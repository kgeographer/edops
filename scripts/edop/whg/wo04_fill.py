"""WO-04c: throwaway script that fills the dummy into a filled_profile. No LLM.

Fills every 'yes' unit of modal_dummy_annotated.md from real data for a point; leaves each 'maybe' and
'no' unit as a visible placeholder naming what is missing. Read-only: GETs on the local server, SELECTs
on the local database, and the saved WO-03 ring and flow tables. Used by notebooks/edop/whg/wo04c_fill.ipynb.
"""
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
    'S6.4': 'cutoff for "resembles"',
    'S6.5': 'ring "furthest from the set" rule',
    'S7.1a': 'coastline data (no distance-to-coast field)',
    'S7.3': 'edge kind from the point (live layer)',
    'S8.1b': 'glossary of dataset years',
    'S8.3': 'snap (not built)',
    'S9.1': 'URL scheme from WHG into EDOPS',
}


_TPL = {}


def templates():
    """The wording in profile_templates.md; re-read whenever the file changes. Refuses a version with no Changes line."""
    mtime = TEMPLATES_PATH.stat().st_mtime
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
            m = re.match(r'([A-Za-z0-9_.]+): (.*)$', line)
            if m and section != 'changes':
                text[m.group(1)] = m.group(2)
    newest = max((int(re.match(r'- v(\d+) ', c).group(1)) for c in changes), default=None)
    if version is None or newest != version:
        raise ValueError(f'{TEMPLATES_PATH.name}: Version is {version} but the newest Changes line is v{newest}; '
                         'raise Version and add a Changes line (- vN | date | who | what and why)')
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


def templates_stamp():
    """Which wording made a generated file: version, last commit of the template file, edited since."""
    rel = str(TEMPLATES_PATH.relative_to(ROOT))
    git = lambda *a: subprocess.run(['git', '-C', str(ROOT), *a], capture_output=True, text=True).stdout.strip()
    last = git('log', '-1', '--format=%h', '--', rel)
    edited = bool(git('status', '--porcelain', '--', rel))
    return f'{TEMPLATES_PATH.name} v{templates()["version"]} (last commit {last or "none yet"}; edited since: {"yes" if edited else "no"})'


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


def build_facts(lat, lon, conn, pairs, flow):
    """Everything the units read, for one point. pairs and flow are the saved WO-03 ring and flow tables."""
    pub, ar = fetch_point(lat, lon)
    F = dict(lat=lat, lon=lon, pub=pub, areas=ar, hid=None)
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
    eco_id = sigval(pub, 'eco_id')
    w = conn.execute('SELECT wiki_url FROM public.eco_wikitext WHERE eco_id = %s', (int(eco_id),)).fetchone() if eco_id is not None else None
    F['wiki_url'] = w[0] if w and w[0] else None
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

    eco = sigval(pub, 'ecoregion')
    U['S1.2a'] = ok(eco, "the basin's majority ecoregion; the template means the point's") if eco else no('no ecoregion')

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

    endo, dist, coast = sigval(pub, 'endorheic'), sigval(pub, 'dist_sink'), sigval(pub, 'coast_flag')
    if dist is None:
        U['S3.5'] = no('no distance to the sink')
    elif endo == 2:
        U['S3.5'] = ok(fmt('S3.5.closed', {}), f'endo=2; dist_sink {dist:,.0f} km')
    elif endo == 1:
        U['S3.5'] = ok(fmt('S3.5.inland', dict(km=f'{dist:,.0f}')), 'endo=1')
    else:
        U['S3.5'] = ok(fmt('S3.5.sea', dict(km=f'{dist:,.0f}')), 'endo=0')

    lith = sigval(pub, 'lith_class')
    U['S4.2'] = ok(re.sub(r'\s*\([A-Z]{2}\)$', '', lith)) if lith else no('no lithology')

    for uid, var, key, word in (('S5.1a', 'cropland_extent', 'cropland_extent', 'cropland'), ('S5.1b', 'pasture_extent', 'pasture_extent', 'pasture')):
        val, st = sigval(pub, key), rows.get(var, {}).get('status')
        if st == 'outside_active_domain':
            U[uid] = ok(fmt(uid + '.none', {}), 'zero here (outside active domain)')
        elif val is None or st == 'no_data':
            U[uid] = no('no data')
        else:
            U[uid] = ok(fmt(uid + '.some', dict(value=f'{val:.0f}%')))

    n = F['n_nb']
    U['S6.1a'] = ok(f'{n + 1}', 'empty ring: needs its own wording' if n == 0 else None)
    f = F['flow']
    if f['up1'] + f['upN'] + f['dn1'] + f['dnN'] == 0:
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
            txt.append(fmt('S8.2.zero', dict(n=len(zero), list=', '.join(zero))))
        if other:
            txt.append(fmt('S8.2.other', dict(n=len(other), list='; '.join(f'{v} ({templates()["text"].get("status." + st, st)})' for v, st in other))))
        U['S8.2'] = ok(fmt('S8.2', dict(parts='. '.join(txt))))
    else:
        U['S8.2'] = no('every measure has a value (optional part not stated)', na=True)
    U['S9.2'] = ok(F['wiki_url']) if F['wiki_url'] else no('no Wikipedia text for this ecoregion')
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
    for uid in U:
        if U[uid]['ok'] or uid not in NEED:
            vals[uid] = t(uid)
    if U['S3.2b']['ok']:
        vals['S3.2'] = fmt('S3.2', {'S3.2a': t('S3.2a'), 'S3.2b': t('S3.2b')})
    else:
        vals['S3.2'] = f'⟦S3.2: not stated; {U["S3.2b"]["why"]}; area ratio {t("S3.2a")}⟧'
    for sec in SECTIONS:
        L += [f'### {fmt(sec + ".title", {})}', fmt(sec + '.frame', vals), '']
    notes = [f'- {k}: {v["note"]}' for k, v in U.items() if v.get('note')]
    notes += [f'- {k}: {"not applicable" if v.get("na") else "not filled"} ({v["why"]})' for k, v in U.items() if not v['ok']]
    L += ['**Fill notes**', *notes, '']
    return '\n'.join(L)
