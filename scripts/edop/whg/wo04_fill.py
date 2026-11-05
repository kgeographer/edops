"""WO-04c: throwaway script that fills the dummy into a filled_profile. No LLM.

Fills every 'yes' unit of modal_dummy_annotated.md from real data for a point; leaves each 'maybe' and
'no' unit as a visible placeholder naming what is missing. Read-only: GETs on the local server, SELECTs
on the local database, and the saved WO-03 ring and flow tables. Used by notebooks/edop/whg/wo04c_fill.ipynb.
"""
import json
import re
import urllib.error
import urllib.parse
import urllib.request

import numpy as np

BASE = 'http://localhost:8000'
MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
          'November', 'December']
STATUS_WORDS = {'outside_active_domain': 'zero here, so no percentile', 'no_data': 'no data in the source',
                'low_coverage': 'low coverage', 'not_areal': 'not defined for an area'}

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
    'S4.3': 'cutoffs for karst and permafrost words',
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
        U['S2.2bc'] = ok(f'from {m[lo]:.1f} °C in {MONTHS[lo]} to {m[hi]:.1f} °C in {MONTHS[hi]}')
    else:
        U['S2.2bc'] = no('no monthly temperature')

    if F['sub_area'] and F['up_area']:
        r = F['up_area'] / F['sub_area']
        U['S3.2a'] = ok(f'{r:.0f}' if r >= 10 else f'{r:.1f}')
    else:
        U['S3.2a'] = no('no area')
    cls, pr, ar, tr = provenance(F)
    if cls == 'Exogenous water supply':
        U['S3.2b'] = ok('wetter', f'class {cls}; precipitation ratio {pr:.2f}' + (f', moisture ratio {ar:.2f}' if ar else ''))
    else:
        U['S3.2b'] = no(f'class is {cls}: the built rule has no "drier" or "cooler" statement, only "wetter" for exogenous water', na=True)
    U['S3.2b']['class'] = cls

    endo, dist, coast = sigval(pub, 'endorheic'), sigval(pub, 'dist_sink'), sigval(pub, 'coast_flag')
    if dist is None:
        U['S3.5'] = no('no distance to the sink')
    elif endo == 2:
        U['S3.5'] = ok('nowhere: it is a closed basin, an inland sink', f'endo=2; dist_sink {dist:,.0f} km')
    elif endo == 1:
        U['S3.5'] = ok(f'to an inland sink about {dist:,.0f} km downstream along the river from the basin\'s outlet', 'endo=1')
    else:
        U['S3.5'] = ok(f'to the sea about {dist:,.0f} km downstream along the river from the basin\'s outlet', 'endo=0')

    lith = sigval(pub, 'lith_class')
    U['S4.2'] = ok(re.sub(r'\s*\([A-Z]{2}\)$', '', lith)) if lith else no('no lithology')

    for uid, var, key, word in (('S5.1a', 'cropland_extent', 'cropland_extent', 'cropland'), ('S5.1b', 'pasture_extent', 'pasture_extent', 'pasture')):
        val, st = sigval(pub, key), rows.get(var, {}).get('status')
        if st == 'outside_active_domain':
            U[uid] = ok(f'no {word} is recorded', 'zero here (outside active domain)')
        elif val is None or st == 'no_data':
            U[uid] = no('no data')
        else:
            U[uid] = ok(f'{val:.0f}%')

    n = F['n_nb']
    U['S6.1a'] = ok(f'{n + 1}', 'empty ring: needs its own wording' if n == 0 else None)
    f = F['flow']
    if f['up1'] + f['upN'] + f['dn1'] + f['dnN'] == 0:
        U['S6.2'] = no('no upstream or downstream neighbour in the ring', na=True)
    else:
        U['S6.2'] = ok(f"upstream: {f['up1']} direct, {f['upN']} further; downstream: {f['dn1']} direct, {f['dnN']} further")
    U['S7.2'] = ok('Its basin touches the sea.') if coast == 1 else no('basin does not touch the sea (optional part not stated)', na=True)
    U['S8.1a'] = ok(f"{F['sub_area']:,.0f}") if F['sub_area'] else no('no area')

    bad = [(r['variable'], r['status']) for r in F['areas']['rows'] if r['status'] != 'ok']
    zero = [v for v, st in bad if st == 'outside_active_domain']
    other = [(v, st) for v, st in bad if st != 'outside_active_domain']
    if bad:
        txt = []
        if zero:
            txt.append(f"{len(zero)} measures are zero here and so have no percentile: " + ', '.join(zero))
        if other:
            txt.append(f"{len(other)} have no value: " + '; '.join(f'{v} ({STATUS_WORDS.get(st, st)})' for v, st in other))
        U['S8.2'] = ok('. '.join(txt))
    else:
        U['S8.2'] = no('every measure has a value (optional part not stated)', na=True)
    U['S9.2'] = ok(F['wiki_url']) if F['wiki_url'] else no('no Wikipedia text for this ecoregion')
    return U


def render_filled_profile(name, F, U):
    """The filled_profile as markdown: yes units filled, maybe units as visible placeholders."""
    L = [f'## {name}: environmental profile', '']
    if F['pub'] is None:
        L += ['No basin contains this point (structured response `no_basin`; nearest basin: see WO-03 Q6). Every basin-keyed unit is empty.', '',
              f'{PH("S1.1b")} {PH("S1.3")} {PH("S9.1")}', '']
        return '\n'.join(L)
    t = lambda uid, default='⟦not filled⟧': U[uid]['text'] if U[uid]['ok'] else f'⟦{uid}: {U[uid]["why"]}⟧'
    s = F['pub']
    pct = lambda v: 'n/a' if v is None else f'{v}%'
    km, perm = pct(sigval(s, 'karst')), pct(sigval(s, 'permafrost_extent'))
    sand, silt, clay = sigval(s, 'pct_sand'), sigval(s, 'pct_silt'), sigval(s, 'pct_clay')
    comp = f'{sand:.0f}% sand, {silt:.0f}% silt, {clay:.0f}% clay' if None not in (sand, silt, clay) else 'composition missing'
    L += ['### Setting', f'{name} sits at about {PH("S1.1b")} m above sea level, in {PH("S1.1c")} country. It lies in the {t("S1.2a")} ecoregion, {PH("S1.2b")}. {PH("S1.3")} {PH("S1.4")}', '',
          '### Climate',
          f'Rainfall averages about {t("S2.1a")} mm a year, {PH("S2.1b")}. Temperatures average {t("S2.2a")} °C, {t("S2.2bc")}. {PH("S2.3")}', '']
    s32 = f'Most of the water passing here falls far upstream: the catchment above is {t("S3.2a")} times the size of the local basin, and {t("S3.2b")} than it.' if U['S3.2b']['ok'] else f'⟦S3.2: not stated; {U["S3.2b"]["why"]}; area ratio {t("S3.2a")}⟧'
    L += ['### Water', f'{name} is {PH("S3.1")}. {s32} {PH("S3.3")} {PH("S3.4")} The basin drains {t("S3.5")}.', '',
          '### Land and geology',
          f'The land is {PH("S4.1a")}, with ⟦S4.1b maybe: needs a texture class word; composition: {comp}⟧. The underlying rock is mostly {t("S4.2")}. {PH("S4.3", f"karst {km}, permafrost {perm}")}', '']
    lc = F['rows'].get('land_cover_name', {}).get('representative_raw')
    def part(uid, noun, tail):
        if not U[uid]['ok']:
            return f'⟦{uid}: {U[uid]["why"]}⟧'
        return U[uid]['text'] if U[uid]['text'].startswith('no ') else f'about {U[uid]["text"]} of the basin is {noun}{tail}'
    crop_part, past_part = part('S5.1a', 'cropland', ''), part('S5.1b', 'pasture', '')
    past_part = past_part.replace('about ', '', 1) if past_part.startswith('about ') else past_part
    L += ['### Land cover today',
          f'Today {crop_part} and {past_part}; ⟦S5.1c maybe: needs wording; GLC2000 majority: {lc}⟧ covers most of the rest. {PH("S5.2", "population density " + "{:,.1f}".format(sigval(s, "pop_density"))  + " per km²")}', '']
    L += ['### Surroundings',
          f"{name}'s basin is one of {t('S6.1a')} that meet here. {t('S6.2')} {PH('S6.2c')} {PH('S6.3')} {PH('S6.4')} {PH('S6.5')}", '']
    L += ['### Coast and reach', f'{PH("S7.1a")} {t("S7.2")} {PH("S7.3")}', '']
    dot = '.' if U['S8.2']['ok'] else ''
    L += ['### About these figures',
          f'These figures describe the basin of about {t("S8.1a")} km² that contains {name}, from global datasets of about {PH("S8.1b")}. {t("S8.2")}{dot} {PH("S8.3")}', '']
    L += ['### Buttons', f'{PH("S9.1")} [Ecoregion on Wikipedia: {t("S9.2")}] [Data as JSON: always]', '']
    notes = [f'- {k}: {v["note"]}' for k, v in U.items() if v.get('note')]
    notes += [f'- {k}: {"not applicable" if v.get("na") else "not filled"} ({v["why"]})' for k, v in U.items() if not v['ok']]
    L += ['**Fill notes**', *notes, '']
    return '\n'.join(L)
