"""WO-10: the stored profile record for one place, and the files the sample page reads.

One selection (the units the rules filled, and the template lines they chose) gives both renderings: `filled` text and `template`
segments. The page swaps them and does no parsing of its own. A unit not built yet is left out of both. Wording is
profile_templates.md; the rules are wo04_fill.py and its companions. Records are written to app/static/profiles/<slug>.json.
"""
import json
import re
import unicodedata

from scripts.edop.whg import wo04_fill as W

PROFILES_DIR = W.ROOT / 'app' / 'static' / 'profiles'

# Units that speak about the place's point, not its basin. A profile stored for a basin carries only the basin units; these are
# added for a place. (S9.3 is both: the JSON of the record itself.)
POINT_UNITS = {'S1.1b', 'S1.2a', 'S1.2c', 'S3.1', 'S3.3', 'S8.3', 'S8.point', 'S8.osm', 'S9.2', 'S9.4'}

_PLACEHOLDER = re.compile(r'⟦[^⟧]*⟧')


def slugify(name):
    """'Utqiaġvik' -> 'utqiagvik'; 'Chaco Canyon' -> 'chaco-canyon'"""
    ascii_ = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-z0-9]+', '-', ascii_.lower()).strip('-')


def _clean(line):
    """A recorded template line, without the filled output."""
    return dict(key=line['key'], raw=line['raw'], vals=line['vals'], parts=[_clean(p) for p in line['parts']])


def _segments(raw, U, vals):
    """The frame's template: literal text, a slot left unfilled ({name}, or a unit that is only a value), or the template lines
    the rules chose for a unit that is a sentence. Units not built, and units that are silent, are left out."""
    segs, pos = [], 0
    for m in W._SLOT.finditer(raw):
        if m.start() > pos:
            segs.append(dict(type='text', text=raw[pos:m.start()]))
        pos = m.end()
        slot = m.group(1)
        if slot == 'name':
            segs.append(dict(type='slot', slot='name'))
            continue
        u = U.get(slot)
        if u is None or not u['ok'] or vals.get(slot, '') == '':
            continue
        if u.get('lines'):
            segs += [dict(type='line', unit=slot, **_clean(ln)) for ln in u['lines']]
        else:
            segs.append(dict(type='slot', slot=slot))
    if pos < len(raw):
        segs.append(dict(type='text', text=raw[pos:]))
    return segs


def frame_key(sec, U):
    """The frame of a section. A unit not built is hidden, so Setting and About these figures use the frames without the gist (S1.2b)
    and the dataset years (S8.1b) until those are built."""
    text = W.templates()['text']
    if sec == 'S5' and U.get('S5.both_none', {}).get('ok'):
        return 'S5.frame.both_none'
    if sec == 'S1' and not U.get('S1.2b', {}).get('ok') and 'S1.frame.nogist' in text:
        return 'S1.frame.nogist'
    if sec == 'S8' and not U.get('S8.1b', {}).get('ok') and 'S8.frame.noyears' in text:
        return 'S8.frame.noyears'
    return sec + '.frame'


def _eco_links(F):
    """{ecoregion name: its OneEarth page}, for the basin's majority ecoregion, the point's, and the others that cover part of the basin (S1.4). Names with no page are left out."""
    base = 'https://www.oneearth.org/ecoregions/'
    out = {}
    if F.get('oe_slug') and W.val(F, 'ecoregion'):
        out[W.val(F, 'ecoregion')] = base + F['oe_slug'] + '/'
    for name, slug in F.get('oe_slug_by_name', {}).items():
        if slug:
            out[name] = base + slug + '/'
    if F.get('oe_slug_pt') and F.get('pt_eco_name'):
        out[F['pt_eco_name']] = base + F['oe_slug_pt'] + '/'
    return out


def _runs(text, links):
    """The filled text as pieces: {t} for text, {t, href} for an ecoregion name, which the page opens in a new tab."""
    if not links:
        return [dict(t=text)]
    pat = re.compile('|'.join(re.escape(n) for n in sorted(links, key=len, reverse=True)))
    runs, pos = [], 0
    for m in pat.finditer(text):
        if m.start() > pos:
            runs.append(dict(t=text[pos:m.start()]))
        runs.append(dict(t=m.group(0), href=links[m.group(0)]))
        pos = m.end()
    if pos < len(text):
        runs.append(dict(t=text[pos:]))
    return runs


def _buttons(slug, U, lat, lon):
    """The stored record, the full signature of the basin (the public API, relative to the site), and Wikipedia where present.
    (The OneEarth page is linked from the ecoregion name; S9.1, the link into EDOPS, is not built.)"""
    out = [dict(id='S9.3', label='Profile as JSON', url=f'/static/profiles/{slug}.json', target='_blank'),
           dict(id='signature', label='Full signature (JSON)', url=f'/api/signature?scope=basin&level=6&lat={lat}&lon={lon}', target='_blank')]
    if U.get('S9.2', {}).get('ok'):
        out.append(dict(id='S9.2', label='Ecoregion on Wikipedia', url=U['S9.2']['text'], target='_blank'))
    return out


def _monthly(F):
    """Monthly precipitation (mm) and temperature (deg C) of the basin, 12 values each, for the climate figure; None if either is missing."""
    pre, tmp = W.val(F, 'pre_mm_monthly'), W.val(F, 'tmp_dc_monthly')
    if not pre or not tmp or len(pre) != 12 or len(tmp) != 12:
        return None
    return dict(scope='basin', level=6, source='BasinATLAS monthly climatology', precip_mm=[float(v) for v in pre], temp_c=[float(v) for v in tmp])


def build_record(name, F, U, generated):
    """The stored record: both renderings, the section structure, the buttons, provenance and the fill notes."""
    slug = slugify(name)
    rec = dict(place=name, slug=slug, lat=F['lat'], lon=F['lon'], hybas_id=F.get('hid'), generated=generated,
               template_version=W.templates()['version'], provenance=W.templates_stamp(), no_basin=F['pub'] is None)
    if F['pub'] is None:
        rec.update(message=W.fmt('nobasin.text', {}), sections=[], monthly=None, buttons_title=None, buttons=[], units={}, notes=[])
        return rec
    vals = W.profile_vals(name, F, U)
    text = W.templates()['text']
    links = _eco_links(F)
    sections = []
    for sec in W.SECTIONS:
        if sec == 'S9':
            continue            # the buttons
        frame = frame_key(sec, U)
        filled = W.tidy(_PLACEHOLDER.sub('', W.fmt(frame, vals)))
        if filled.strip():      # a section with nothing true to say has no heading either
            sections.append(dict(id=sec, title=W.fmt(sec + '.title', {}), filled=filled, runs=_runs(filled, links),
                                 template=_segments(text[frame], U, vals)))
    rec['sections'] = sections
    rec['monthly'] = _monthly(F)
    rec['buttons_title'] = W.fmt('S9.title', {})
    rec['buttons'] = _buttons(slug, U, F['lat'], F['lon'])
    rec['units'] = {uid: dict(scope='point' if uid in POINT_UNITS else 'basin', ok=u['ok'], text=u['text'], why=u['why'],
                              na=bool(u.get('na')), note=u.get('note'), lines=[_clean(ln) for ln in u.get('lines', [])])
                    for uid, u in U.items()}
    rec['notes'] = [f'{k}: {v["note"]}' for k, v in U.items() if v.get('note')] + \
                   [f'{k}: {"not applicable" if v.get("na") else "not filled"} ({v["why"]})' for k, v in U.items()
                    if not v['ok'] and not (k == 'S3.2b' and 'S3.2' in U)]
    return rec


def write_records(records, directory=PROFILES_DIR):
    """One <slug>.json per record, and index.json listing them in order. Returns the paths written."""
    directory.mkdir(parents=True, exist_ok=True)
    paths = []
    for r in records:
        p = directory / f'{r["slug"]}.json'
        p.write_text(json.dumps(r, ensure_ascii=False, indent=1) + '\n')
        paths.append(p)
    idx = directory / 'index.json'
    idx.write_text(json.dumps([dict(place=r['place'], slug=r['slug'], no_basin=r['no_basin']) for r in records],
                              ensure_ascii=False, indent=1) + '\n')
    return paths + [idx]
