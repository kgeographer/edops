"""WO-04c: throwaway script that fills the dummy into a filled_profile. No LLM.

Fills every 'yes' unit of modal_dummy_annotated.md from real data for a point; leaves each 'maybe' and
'no' unit as a visible placeholder naming what is missing. Read-only: GETs on the local server, SELECTs
on the local database, and the saved WO-03 ring and flow tables. Used by notebooks/edop/whg/wo04c_fill.ipynb.
"""
import csv
import json
import re
import subprocess
import urllib.error
import urllib.parse
import urllib.request

from pathlib import Path

import numpy as np

BASE = 'http://localhost:8000'
ROOT = Path(__file__).resolve().parents[3]
TEMPLATES_PATH = ROOT / 'docs' / 'design' / 'dashboard' / 'profile_templates.md'
MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
          'November', 'December']
SECTIONS = ['S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8', 'S9']

# units that are 'maybe' or 'no' in wo04a_results.md, with what each needs
NEED = {
    'S1.1b': 'live point elevation, or WHG\'s own',
    'S1.1c': 'terrain scheme or cutoff (wo04b)',
    'S1.2b': 'stored one-line ecoregion gist',
    'S1.3': 'distance from the point to the next ecoregion',
    'S1.4': 'share cutoff for further ecoregions',
    'S2.1b': 'rule for "mostly in {months}"',
    'S2.3': 'ring rank rules',
    'S3.1': 'nearest-river layer: distance, name',
    'S3.3': 'cutoffs for a much larger river nearby',
    'S3.4': 'lake share, not in the payloads',
    'S4.1a': 'terrain scheme or cutoff (wo04b)',
    'S4.1b': 'a texture class word',
    'S4.3': 'cutoffs for karst and permafrost words',
    'S5.1c': 'wording',
    'S5.2': 'ring comparison rules',
    'S6.2c': 'description of a neighbouring basin (ring rules)',
    'S6.3': 'contrast counts (ring rules); no compass words',
    'S6.5': 'ring "furthest from the set" rule',
    'S7.1a': 'coastline data (no distance-to-coast field)',
    'S7.3': 'edge kind from the point (live layer)',
    'S8.1b': 'glossary of dataset years',
    'S8.3': 'snap (not built)',
    'S9.1': 'URL scheme from WHG into EDOPS',
}


_TPL = {}

# Every key the generator reads. A template file with a key outside these sets, or without a required one, is refused,
# so a misspelt or stray line cannot silently switch wording off. New wording the script learns to use goes in here.
_UNITS = [f'S{i}' for i in range(1, 10)]
KEYS_ALWAYS = {f'{s}.{p}' for s in _UNITS for p in ('title', 'frame')} | {
    'S2.2bc', 'S3.2b.wetter', 'S3.5.sea', 'S3.5.inland', 'S3.5.closed', 'S5.1a.some', 'S5.1a.none', 'S5.1b.some',
    'S5.1b.none', 'S7.2', 'S8.2', 'S8.2.zero', 'S8.2.other', 'nobasin.text', 'nobasin.frame'}
KEYS_FLOW_PLAIN = {'S6.2'}   # the one-line flow counts of templates v4 and earlier; replaced by the S6.2.* lines (ring rules)
KEYS_PLAIN = {'S3.2'}   # the single water sentence of templates v1 (no framing A)
KEYS_FRAMING_A = {'S1.2c', 'S3.2.exogenous', 'S3.2.uniform', 'S3.2.local', 'S3.2.coastal', 'S3.2.endorheic',
                  'S3.2.undetermined'}   # required once S1.2c is present
KEYS_OPTIONAL = {'S3.2.headwater', 'S3.2.coastal_large', 'S3.5.sea_zero', 'label.upstream',
                 'status.outside_active_domain', 'status.no_data', 'status.low_coverage', 'status.not_areal'}


def check_keys(text):
    """Refuse a template file whose keys the generator does not recognise, or that lacks a required one."""
    framing_a = 'S1.2c' in text
    required = KEYS_ALWAYS | (KEYS_FRAMING_A if framing_a else KEYS_PLAIN)
    if 'S6.2.in_none' in text:   # ring comparison rules (WO-06): the template must carry every line they read
        from scripts.edop.whg import wo06_rings
        required |= wo06_rings.ring_keys()
    else:
        required |= KEYS_FLOW_PLAIN
    known = required | KEYS_OPTIONAL
    if 'S6.2.in_none' in text:
        known |= wo06_rings.ring_optional()
    if 'S3.1.named' in text:   # nearest-river wording (WO-07): the template must carry every line it reads
        from scripts.edop.whg import wo07_rivers
        required |= wo07_rivers.river_keys()
        known |= wo07_rivers.river_keys()
    if 'S4.1a' in text:   # class words (WO-07 part B)
        from scripts.edop.whg import wo07_classes
        required |= wo07_classes.class_keys()
        known |= wo07_classes.class_keys()
    unknown, missing = sorted(set(text) - known), sorted(required - set(text))
    if unknown or missing:
        raise ValueError(f'{TEMPLATES_PATH.name}: ' + '; '.join(
            ([f'keys the generator does not recognise (misspelt, or not supported yet): {", ".join(unknown)}'] if unknown else [])
            + ([f'required keys missing: {", ".join(missing)}'] if missing else [])))


def templates():
    """The wording in profile_templates.md; re-read whenever the file changes. Refuses a version with no Changes line."""
    mtime = (str(TEMPLATES_PATH), TEMPLATES_PATH.stat().st_mtime)
    if _TPL.get('mtime') == mtime:
        return _TPL['data']
    text, version, changes, section = {}, None, [], None
    for line in TEMPLATES_PATH.read_text().splitlines():
        line = line.rstrip()
        if line.startswith('## '):
            section = line[3:].strip().lower()
        elif line.startswith('Version:'):
            version = int(line.split(':', 1)[1])
        elif section == 'changes' and line.startswith('- v'):
            changes.append(line)
        else:
            m = re.match(r'([A-Za-z0-9_.]+):\s*(.*)$', line)
            if m and section != 'changes':
                text[m.group(1)] = m.group(2)
    newest = max((int(re.match(r'- v(\d+) ', c).group(1)) for c in changes), default=None)
    if version is None or newest != version:
        raise ValueError(f'{TEMPLATES_PATH.name}: Version is {version} but the newest Changes line is v{newest}; '
                         'raise Version and add a Changes line (- vN | date | who | what and why)')
    check_keys(text)
    _TPL.update(mtime=mtime, data=dict(text=text, version=version, changes=changes))
    return _TPL['data']


_SLOT = re.compile(r'\{([A-Za-z0-9_.]+)\}')


def fmt(key, vals):
    """Fill template `key` from profile_templates.md; a slot the code does not supply stops the run."""
    tpl = templates()['text'].get(key)
    if tpl is None:
        raise KeyError(f'{TEMPLATES_PATH.name} has no line "{key}:"')

    def sub(m):
        if m.group(1) not in vals:
            raise KeyError(f'{TEMPLATES_PATH.name}, "{key}": the slot {{{m.group(1)}}} is not one the generator supplies')
        return str(vals[m.group(1)])
    return _SLOT.sub(sub, tpl)


def has(key):
    """True when the template file has a line for `key`: how a newer template switches a newer behaviour on."""
    return key in templates()['text']


def tidy(text):
    """Close the gaps left by empty phrases."""
    return re.sub(r' {2,}', ' ', text).strip()


_NUMWORDS = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten']


def numword(n):
    """A whole number as a word up to ten, else digits."""
    return _NUMWORDS[n] if 0 <= n <= 10 else f'{n:,}'


def join_and(items):
    """'a', 'a and b', 'a, b and c'"""
    return items[0] if len(items) == 1 else ', '.join(items[:-1]) + ' and ' + items[-1]


_LABELS = {}


def catalog_labels():
    """{variable key: (readable name, is_upstream)} from the variable catalog."""
    if not _LABELS:
        path = ROOT / 'documentation' / 'EDOPS_variable_catalog_v0.4.tsv'
        with open(path, newline='') as fh:
            for r in csv.DictReader(fh, delimiter='\t'):
                if r['api_key_s']:
                    _LABELS.setdefault(r['api_key_s'], (r['friendly_name'], False))
                if r['api_key_u']:
                    _LABELS.setdefault(r['api_key_u'], (r['friendly_name'], True))
    return _LABELS


def label(key):
    """Readable name for a variable key, from the catalog; the key itself when the catalog has none or the template has no label.upstream."""
    name, up = catalog_labels().get(key, (None, False))
    if name is None or not has('label.upstream'):
        return key
    return fmt('label.upstream', {'label': name}) if up else name


def templates_stamp():
    """Which wording and which rules made a generated file: template version, and last commit and edited-since for the template file, this script, wo06_rings.py, wo07_rivers.py and wo07_classes.py."""
    git = lambda *a: subprocess.run(['git', '-C', str(ROOT), *a], capture_output=True, text=True).stdout.strip()

    def state(path):
        rel = str(path.relative_to(ROOT))
        return f'last commit {git("log", "-1", "--format=%h", "--", rel) or "none yet"}; edited since: {"yes" if git("status", "--porcelain", "--", rel) else "no"}'
    return (f'{TEMPLATES_PATH.name} v{templates()["version"]} ({state(TEMPLATES_PATH)}); '
            f'script {Path(__file__).name} ({state(Path(__file__).resolve())}); '
            f'script wo06_rings.py ({state(Path(__file__).resolve().parent / "wo06_rings.py")}); '
            f'script wo07_rivers.py ({state(Path(__file__).resolve().parent / "wo07_rivers.py")}); '
            f'script wo07_classes.py ({state(Path(__file__).resolve().parent / "wo07_classes.py")})')


def PH(uid, extra=''):
    return f'⟦{uid} maybe: needs {NEED[uid]}{"; " + extra if extra else ""}⟧'


def get_json(path, **params):
    """GET a local endpoint; returns the parsed JSON, or None on a 404 (a point in no basin)."""
    url = f'{BASE}{path}?{urllib.parse.urlencode(params)}'
    try:
        with urllib.request.urlopen(url, timeout=120) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def fetch_point(lat, lon):
    pub = get_json('/api/signature', scope='basin', lat=lat, lon=lon, bands='ABCDE', level=6)
    ar = get_json('/api/areas', scope='single_basin', lat=lat, lon=lon, level=6, bands='ABCDE', detail='false')
    return pub, ar


def sigval(pub, key):
    for band in pub['signature_bands'].values():
        for it in band['items']:
            if it['key'] == key:
                return it['value']
    return None


def build_facts(lat, lon, conn, pairs, flow, ring=None, rivers=None):
    """Everything the units read, for one point. pairs and flow are the saved WO-03 ring and flow tables; ring is
    wo06_rings.load_table() ({core hybas_id: rows}), needed only once the template carries the ring comparison lines."""
    pub, ar = fetch_point(lat, lon)
    F = dict(lat=lat, lon=lon, pub=pub, areas=ar, hid=None)
    if rivers is not None:
        from scripts.edop.whg import wo07_rivers
        F['river'] = rivers.get(wo07_rivers.key(lat, lon))
    pe = conn.execute('SELECT eco_id, eco_name FROM gaz."Ecoregions2017" WHERE ST_Intersects(geom, ST_SetSRID(ST_MakePoint(%s, %s), 4326)) LIMIT 1',
                      (lon, lat)).fetchone()
    F['pt_eco_id'], F['pt_eco_name'] = (int(pe[0]), pe[1]) if pe else (None, None)
    if pub is None or ar is None:
        return F
    hid = int(ar['scope']['hybas_id'])
    F['hid'] = hid
    F['rows'] = {r['variable']: r for r in ar['rows']}
    sub = conn.execute('SELECT sub_area::float8, up_area::float8 FROM public.basin06 WHERE hybas_id = %s', (hid,)).fetchone()
    F['sub_area'], F['up_area'] = sub
    p = pairs[pairs['core_id'] == hid].drop_duplicates('nb_id')
    F['n_nb'] = int((p['shared_km'] > 0).sum())
    F['n_point_contacts'] = int((p['shared_km'] == 0).sum())
    f = flow[flow['core_id'] == hid].drop_duplicates('nb_id')['flow_real'].value_counts().to_dict()
    F['flow'] = {k: int(f.get(k, 0)) for k in ('up1', 'upN', 'dn1', 'dnN', 'same', 'other')}
    fl = flow[flow['core_id'] == hid].drop_duplicates('nb_id')
    F['flow_nb'] = {int(a): b for a, b in zip(fl['nb_id'], fl['flow_real'])}
    F['ring'] = ring.get(hid) if ring is not None else None
    eco_id = sigval(pub, 'eco_id')
    w = conn.execute('SELECT wiki_url FROM public.eco_wikitext WHERE eco_id = %s', (int(eco_id),)).fetchone() if eco_id is not None else None
    F['wiki_url'] = w[0] if w and w[0] else None
    from scripts.edop.whg import wo07_classes
    F['glc'] = wo07_classes.glc_shares(conn, hid)
    wp = conn.execute('SELECT wiki_url FROM public.eco_wikitext WHERE eco_id = %s', (F['pt_eco_id'],)).fetchone() if F['pt_eco_id'] is not None else None
    F['wiki_url_pt'] = wp[0] if wp and wp[0] else None
    return F


def provenance(F):
    """The Analysis tab's water provenance class (sandbox.html renderAnalysis), ported as is."""
    pub = F['pub']
    up = F['up_area']
    dist, coast, endo = sigval(pub, 'dist_sink'), sigval(pub, 'coast_flag'), sigval(pub, 'endorheic')
    ratio = lambda a, b: (a / b) if (a and b) else None
    pr = ratio(sigval(pub, 'precip_yr_upstream'), sigval(pub, 'precip_yr'))
    ar = ratio(sigval(pub, 'aridity_upstream'), sigval(pub, 'aridity'))
    tr = ratio(sigval(pub, 'temp_yr_upstream'), sigval(pub, 'temp_yr'))
    small = up is not None and up < 500
    if endo:
        return 'Endorheic', pr, ar, tr
    if coast and dist is not None and dist < 10:
        return 'Coastal terminal', pr, ar, tr
    if not small and pr is not None and pr > 1.5:
        return 'Exogenous water supply', pr, ar, tr
    if not small and ar is not None and ar > 1.5:
        return 'Exogenous water supply', pr, ar, tr
    if small:
        return 'Undetermined', pr, ar, tr
    near = lambda r: r is None or 0.9 <= r <= 1.1
    return ('Catchment-uniform' if near(pr) and near(ar) and near(tr) else 'Local-dominant'), pr, ar, tr


def fill_units(F):
    """One entry per yes unit: dict(ok, text, why). ok False means it could not be filled (why says why)."""
    U = {}
    pub = F['pub']
    if pub is None:
        for uid in ('S1.2a', 'S2.1a', 'S2.2a', 'S2.2bc', 'S3.2a', 'S3.2b', 'S3.5', 'S4.2', 'S5.1a', 'S5.1b', 'S6.1a',
                    'S6.2', 'S7.2', 'S8.1a', 'S8.2', 'S9.2'):
            U[uid] = dict(ok=False, text=None, why='no basin')
        return U
    rows = F['rows']
    ok = lambda text, note=None: dict(ok=True, text=text, why=None, note=note)
    no = lambda why, na=False: dict(ok=False, text=None, why=why, na=na)

    A = has('S1.2c')   # framing A: the Setting speaks about the place (templates v2 and later)
    eco = sigval(pub, 'ecoregion')
    if not A:
        U['S1.2a'] = ok(eco, "the basin's majority ecoregion; the template means the point's") if eco else no('no ecoregion')
    else:
        peco = F['pt_eco_name']
        if peco:
            U['S1.2a'] = ok(peco, 'the ecoregion at the point')
        else:
            U['S1.2a'] = ok(eco, "no ecoregion polygon at the point; the basin's majority used") if eco else no('no ecoregion')
        differs = bool(peco) and F['pt_eco_id'] != sigval(pub, 'eco_id')
        U['S1.2c'] = ok(fmt('S1.2c', {'eco': eco})) if differs else ok('', 'point and basin ecoregions agree')
        el = sigval(pub, 'elev_point')
        U['S1.1b'] = ok(f'{el:,.0f}', f"{pub.get('elev_dataset')}, {pub.get('elev_resolution_m')} m, via {pub.get('elev_source')}") if el is not None else no('no elevation from the live service')
        for uid, key in (('S1.5a', 'elev_min'), ('S1.5b', 'elev_max')):
            ev = sigval(pub, key)
            U[uid] = ok(f'{ev:,.0f}') if ev is not None else no('no value')

    v = sigval(pub, 'precip_yr')
    U['S2.1a'] = ok(f'{v:.0f}') if v is not None else no('no value')
    v = sigval(pub, 'temp_yr')
    U['S2.2a'] = ok(f'{v:.1f}') if v is not None else no('no value')
    m = sigval(pub, 'tmp_dc_monthly')
    if m and len(m) == 12:
        lo, hi = int(np.argmin(m)), int(np.argmax(m))
        U['S2.2bc'] = ok(fmt('S2.2bc', dict(lo_temp=f'{m[lo]:.1f}', lo_month=MONTHS[lo], hi_temp=f'{m[hi]:.1f}', hi_month=MONTHS[hi])))
    else:
        U['S2.2bc'] = no('no monthly temperature')

    if F['sub_area'] and F['up_area']:
        r = F['up_area'] / F['sub_area']
        U['S3.2a'] = ok(f'{r:.0f}' if r >= 10 else f'{r:.1f}')
    else:
        U['S3.2a'] = no('no area')
    cls, pr, ar, tr = provenance(F)
    if cls == 'Exogenous water supply':
        U['S3.2b'] = ok(fmt('S3.2b.wetter', {}), f'class {cls}; precipitation ratio {pr:.2f}' + (f', moisture ratio {ar:.2f}' if ar else ''))
    else:
        U['S3.2b'] = no(f'class is {cls}: the built rule has no "drier" or "cooler" statement, only "wetter" for exogenous water', na=True)
    U['S3.2b']['class'] = cls
    if A:
        slug = {'Exogenous water supply': 'exogenous', 'Catchment-uniform': 'uniform', 'Local-dominant': 'local',
                'Coastal terminal': 'coastal', 'Endorheic': 'endorheic', 'Undetermined': 'undetermined'}[cls]
        ratio = F['up_area'] / F['sub_area'] if F['sub_area'] and F['up_area'] else None
        if ratio is not None and ratio <= 1.05 and slug in ('uniform', 'local') and has('S3.2.headwater'):
            slug = 'headwater'
        elif ratio is not None and ratio > 2 and slug == 'coastal' and has('S3.2.coastal_large'):
            slug = 'coastal_large'
        t32 = lambda uid: U[uid]['text'] if U[uid]['ok'] else f'⟦{uid}: {U[uid]["why"]}⟧'
        U['S3.2'] = ok(fmt('S3.2.' + slug, {'S3.2a': t32('S3.2a'), 'S3.2b': t32('S3.2b')}), f'class {cls}')

    endo, dist, coast = sigval(pub, 'endorheic'), sigval(pub, 'dist_sink'), sigval(pub, 'coast_flag')
    if dist is None:
        U['S3.5'] = no('no distance to the sink')
    elif endo == 2:
        U['S3.5'] = ok(fmt('S3.5.closed', {}), f'endo=2; dist_sink {dist:,.0f} km')
    elif endo == 1:
        U['S3.5'] = ok(fmt('S3.5.inland', dict(km=f'{dist:,.0f}')), 'endo=1')
    elif has('S3.5.sea_zero') and round(dist) == 0:
        U['S3.5'] = ok(fmt('S3.5.sea_zero', {}), 'endo=0; dist_sink rounds to 0 km')
    else:
        U['S3.5'] = ok(fmt('S3.5.sea', dict(km=f'{dist:,.0f}')), 'endo=0')

    lith = sigval(pub, 'lith_class')
    U['S4.2'] = ok(re.sub(r'\s*\([A-Z]{2}\)$', '', lith).lower()) if lith else no('no lithology')   # GLiM label in lower case (WO-07)

    for uid, var, key, word in (('S5.1a', 'cropland_extent', 'cropland_extent', 'cropland'), ('S5.1b', 'pasture_extent', 'pasture_extent', 'pasture')):
        val, st = sigval(pub, key), rows.get(var, {}).get('status')
        if st == 'outside_active_domain':
            U[uid] = ok(fmt(uid + '.none', {}), 'zero here (outside active domain)')
        elif val is None or st == 'no_data':
            U[uid] = no('no data')
        else:
            U[uid] = ok(fmt(uid + '.some', dict(value=f'{val:.0f}%')))

    if has('S3.1.named'):   # nearest river and a much larger one nearby (WO-07 part C)
        from scripts.edop.whg import wo07_rivers
        U.update(wo07_rivers.fill_river_units(F, ok, no))

    if has('S4.1a'):   # class words (WO-07 part B)
        from scripts.edop.whg import wo07_classes
        U.update(wo07_classes.fill_class_units(F, ok, no, sigval, fmt, tidy))

    n = F['n_nb']
    rings = has('S6.2.in_none')   # ring comparison rules (templates v5 and later)
    U['S6.1a'] = ok(numword(n + 1) if rings else f'{n + 1}', 'empty ring: needs its own wording' if n == 0 else None)
    f = F['flow']
    if rings:
        from scripts.edop.whg import wo06_rings
        U.update(wo06_rings.fill_ring_units(F, ok, no))
    elif f['up1'] + f['upN'] + f['dn1'] + f['dnN'] == 0:
        U['S6.2'] = no('no upstream or downstream neighbour in the ring', na=True)
    else:
        U['S6.2'] = ok(fmt('S6.2', f))
    U['S7.2'] = ok(fmt('S7.2', {})) if coast == 1 else no('basin does not touch the sea (optional part not stated)', na=True)
    U['S8.1a'] = ok(f"{F['sub_area']:,.0f}") if F['sub_area'] else no('no area')

    bad = [(r['variable'], r['status']) for r in F['areas']['rows'] if r['status'] != 'ok']
    zero = [v for v, st in bad if st == 'outside_active_domain']
    other = [(v, st) for v, st in bad if st != 'outside_active_domain']
    if bad:
        txt = []
        if zero:
            txt.append(fmt('S8.2.zero', dict(n=len(zero), list=', '.join(label(v) for v in zero))))
        if other:
            txt.append(fmt('S8.2.other', dict(n=len(other), list='; '.join(f'{label(v)} ({templates()["text"].get("status." + st, st)})' for v, st in other))))
        U['S8.2'] = ok(fmt('S8.2', dict(parts='. '.join(txt))))
    else:
        U['S8.2'] = no('every measure has a value (optional part not stated)', na=True)
    wiki = (F['wiki_url_pt'] or F['wiki_url']) if A and F['pt_eco_id'] is not None else F['wiki_url']
    U['S9.2'] = ok(wiki) if wiki else no('no Wikipedia text for this ecoregion')
    return U


def render_filled_profile(name, F, U):
    """The filled_profile as markdown: yes units filled, maybe units as visible placeholders. Wording: profile_templates.md."""
    L = [f'## {name}: environmental profile', '']
    if F['pub'] is None:
        stub = {uid: PH(uid) for uid in ('S1.1b', 'S1.3', 'S9.1')}
        L += [fmt('nobasin.text', {}), '', fmt('nobasin.frame', stub), '']
        return '\n'.join(L)
    t = lambda uid: U[uid]['text'] if U[uid]['ok'] else f'⟦{uid}: {U[uid]["why"]}⟧'
    s = F['pub']
    pct = lambda v: 'n/a' if v is None else f'{v}%'
    sand, silt, clay = sigval(s, 'pct_sand'), sigval(s, 'pct_silt'), sigval(s, 'pct_clay')
    comp = f'{sand:.0f}% sand, {silt:.0f}% silt, {clay:.0f}% clay' if None not in (sand, silt, clay) else 'composition missing'
    lc = F['rows'].get('land_cover_name', {}).get('representative_raw')
    extra = {'S4.1b': f'composition: {comp}',
             'S4.3': f'karst {pct(sigval(s, "karst"))}, permafrost {pct(sigval(s, "permafrost_extent"))}',
             'S5.1c': f'GLC2000 majority: {lc}',
             'S5.2': 'population density ' + '{:,.1f}'.format(sigval(s, 'pop_density')) + ' per km²'}
    vals = {'name': name}
    for uid in NEED:
        vals[uid] = PH(uid, extra.get(uid, ''))
    ring_silent = ({'S2.3', 'S5.2', 'S6.2', 'S6.3', 'S6.5'} if has('S6.2.in_none') else set()) | ({'S3.1', 'S3.3'} if has('S3.1.named') else set()) | ({'S4.3', 'S5.1c'} if has('S4.1a') else set())
    for uid in U:
        if U[uid]['ok'] or uid not in NEED:
            vals[uid] = t(uid) if (U[uid]['ok'] or not (uid in ring_silent and U[uid].get('na'))) else ''
        elif uid in ring_silent and U[uid].get('na'):
            vals[uid] = ''
    if 'S3.2' in U:
        vals['S3.2'] = t('S3.2')
    elif U['S3.2b']['ok']:
        vals['S3.2'] = fmt('S3.2', {'S3.2a': t('S3.2a'), 'S3.2b': t('S3.2b')})
    else:
        vals['S3.2'] = f'⟦S3.2: not stated; {U["S3.2b"]["why"]}; area ratio {t("S3.2a")}⟧'
    for k_, v_ in list(vals.items()):
        if k_ != 'name' and isinstance(v_, str) and '{name}' in v_:
            vals[k_] = v_.replace('{name}', name)      # units that open with the place's name (S3.1)
    for sec in SECTIONS:
        L += [f'### {fmt(sec + ".title", {})}', tidy(fmt(sec + '.frame', vals)), '']
    notes = [f'- {k}: {v["note"]}' for k, v in U.items() if v.get('note')]
    notes += [f'- {k}: {"not applicable" if v.get("na") else "not filled"} ({v["why"]})' for k, v in U.items()
              if not v['ok'] and not (k == 'S3.2b' and 'S3.2' in U)]
    L += ['**Fill notes**', *notes, '']
    return '\n'.join(L)
