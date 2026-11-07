"""WO-06: the persisted ring-values table and the neighbour comparison rules.

Fetches, once per basin, the local values of the core and of every basin that meets it (the /api/areas basin_ring
call, plus mean elevation and forest share from public.basin06, which the ring payload does not carry), and saves
them to output/edop/whg/wo06_ring_values.csv. The rules then run on that table alone, with no live calls.

A comparison states only what is true without a cutoff: being the highest or lowest of the set, counts of the
basins a basin is more or less than, "all of them". Ties are never ranked. Wording is in profile_templates.md
(the `cmp.*`, `S2.3.*`, `S5.2.*`, `S6.2.*`, `S6.3.all`, `S6.4`, `S6.5` lines). Read-only.
"""
import pandas as pd

from scripts.edop.whg import wo04_fill as W

RING_CSV = W.ROOT / 'output' / 'edop' / 'whg' / 'wo06_ring_values.csv'

MIN_NB = 3                             # fewest neighbours with a value for any comparison
CAP = dict(S2_3=2, S5_2=2, S6_5=3)     # most extremes stated in one sentence

# measure slug -> variable name in the ring rows (elev_mean and forest_extent come from basin06; relief is derived)
MEAS = {'precip': 'precip_yr', 'temp': 'temp_yr', 'aridity': 'aridity', 'elev': 'elev_mean', 'relief': 'relief',
        'slope': 'slope_avg', 'cropland': 'cropland_extent', 'pasture': 'pasture_extent', 'popdens': 'pop_density',
        'forest': 'forest_extent', 'karst': 'karst', 'sand': 'pct_sand', 'silt': 'pct_silt', 'clay': 'pct_clay'}
# which measures each sentence draws on, in the order they are tried (an editorial choice, to be adjusted)
L_S23 = ['precip', 'temp', 'aridity']
L_S52 = ['cropland', 'pasture', 'popdens']
L_S63 = ['elev', 'precip', 'temp', 'aridity']      # only measures with an adjective ("all drier")
L_S65 = ['elev', 'relief', 'slope', 'forest', 'karst', 'sand', 'silt', 'clay']
# numeric local measures counted by S6.4 (flow-position measures such as discharge and river area are left out)
NUMERIC_LOCAL = ['precip_yr', 'temp_yr', 'temp_min', 'temp_max', 'aridity', 'runoff', 'cropland_extent',
                 'pasture_extent', 'pop_density', 'human_footprint_09', 'elev_min', 'elev_max', 'elev_mean', 'relief',
                 'slope_avg', 'stream_gradient', 'wet_pct_grp1', 'wet_pct_grp2', 'forest_extent', 'karst',
                 'permafrost_extent', 'pct_sand', 'pct_silt', 'pct_clay', 'gw_table_depth']


def ring_keys():
    """Every template key the ring rules read; check_keys requires them once the template has S6.2.in_none."""
    keys = {f'S6.2.{k}' for k in ('in_none', 'in_one', 'in_some', 'out_one', 'out_some', 'out_none')}
    keys |= {'S2.3.extreme', 'S2.3.count', 'S5.2.extreme', 'S5.2.count', 'S6.3.all', 'S6.4', 'S6.5'}
    keys |= {'S2.3.extreme.precip', 'S2.3.count.precip', 'S6.3.all.precip'}     # precipitation has its own frames ("receives ... precipitation")
    for s in set(L_S23) | set(L_S52) | set(L_S63):
        keys |= {f'cmp.{s}.{d}' for d in ('top', 'bottom', 'more', 'less')}
    for s in L_S65:
        keys |= {f'cmp.{s}.{d}' for d in ('top', 'bottom')}
    return keys


# ---- the persisted table -------------------------------------------------------------------------------------

def _num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def fetch_ring_rows(lat, lon, conn):
    """Long rows (core, member, role, shared_km, area_km2, variable, value, status) for one basin and its ring."""
    r = W.get_json('/api/areas', scope='basin_ring', lat=lat, lon=lon, level=6, bands='ABCDE', detail='false')
    if r is None:
        return []
    core = int(r['center']['scope']['hybas_id'])
    members = [(core, 'core', None, None, r['center']['rows'])]
    members += [(int(m['hybas_id']), 'neighbour', m['shared_km'], m['sub_area_km2'], m['signature']['rows']) for m in r['ring']]
    ex = {int(h): (e, f, a) for h, e, f, a in conn.execute(
        'SELECT hybas_id, ele_mt_sav, for_pc_sse, sub_area::float8 FROM public.basin06 WHERE hybas_id = ANY(%s)',
        ([m[0] for m in members],)).fetchall()}
    out = []
    for hid, role, shared, area, rows in members:
        base = dict(core=core, member=hid, role=role, shared_km=shared, area_km2=area if role == 'neighbour' else ex[hid][2])
        for x in rows:
            raw = x.get('representative_raw')
            if _num(raw) or (raw is None and x['status'] != 'ok'):
                out.append({**base, 'variable': x['variable'], 'value': raw if _num(raw) else None, 'status': x['status']})
        e, f, _ = ex[hid]
        for var, v in (('elev_mean', e), ('forest_extent', f)):
            good = v is not None and v >= 0     # -9999 is the source's NoData
            out.append({**base, 'variable': var, 'value': float(v) if good else None, 'status': 'ok' if good else 'no_data'})
    return out


def fetch_table(points, conn, path=RING_CSV, every=25, log=print):
    """Append the ring of each point's basin to the CSV; a basin already in the file is skipped (resumable)."""
    import time
    done = set(pd.read_csv(path, usecols=['core'])['core'].unique()) if path.exists() else set()
    t0, new = time.perf_counter(), 0
    for k, (lat, lon) in enumerate(points, 1):
        row = conn.execute('SELECT hybas_id FROM public.basin06 WHERE ST_Intersects(geom, ST_SetSRID(ST_MakePoint(%s, %s), 4326)) LIMIT 1', (lon, lat)).fetchone()
        if row is not None and int(row[0]) not in done:
            rows = fetch_ring_rows(lat, lon, conn)
            if rows:
                pd.DataFrame(rows).to_csv(path, mode='a', header=not path.exists(), index=False)
                done.add(int(row[0]))
                new += 1
        if k % every == 0:
            log(f'  {k} points | {new} new basins | {time.perf_counter() - t0:.0f}s')
    return len(done), new


def load_table(path=RING_CSV):
    """{core hybas_id: that basin's rows}"""
    t = pd.read_csv(path)
    return {int(c): g for c, g in t.groupby('core')}


# ---- the rules -----------------------------------------------------------------------------------------------

def member_values(df):
    """{variable: {member: float}}. Zero extents (outside_active_domain) count as 0; no data or low coverage is left out."""
    v = {}
    for r in df.itertuples(index=False):
        x = r.value
        if r.status == 'outside_active_domain':
            x = 0.0
        elif r.status != 'ok' or pd.isna(x):
            continue
        v.setdefault(r.variable, {})[int(r.member)] = float(x)
    lo, hi = v.get('elev_min', {}), v.get('elev_max', {})
    v['relief'] = {m: hi[m] - lo[m] for m in lo if m in hi}
    return v


def compare(core_val, nb_vals):
    """How the core stands among its neighbours; None when there is nothing to say (too few neighbours, or all equal)."""
    m = len(nb_vals)
    if core_val is None or m < MIN_NB:
        return None
    c = round(core_val, 6)
    less = sum(round(x, 6) < c for x in nb_vals)
    more = sum(round(x, 6) > c for x in nb_vals)
    if less == 0 and more == 0:
        return None
    side, k = ('more', less) if less >= more else ('less', more)
    return dict(m=m, less=less, more=more, top=(less == m), bottom=(more == m), side=side, k=k)


def _frame(key, slug):
    """The measure's own frame (`key.slug`) when the template has one, else the shared one."""
    return f'{key}.{slug}' if f'{key}.{slug}' in W.templates()['text'] else key


def _cmps(slugs, V, core, nbs):
    out = {}
    for s in slugs:
        d = V.get(MEAS[s], {})
        out[s] = compare(d.get(core), [d[m] for m in nbs if m in d])
    return out


def _stated(slugs, cap, key_ext, key_cnt, V, core, nbs):
    """The sentence for S2.3 or S5.2: the extremes (up to cap), else the most one-sided count; plus a trace."""
    cm = _cmps(slugs, V, core, nbs)
    ext = [(s, 'top' if c['top'] else 'bottom') for s, c in cm.items() if c and (c['top'] or c['bottom'])]
    if ext:
        used = ext[:cap]
        groups = {}          # extremes over the same set of basins and the same frame share one sentence
        for s, d in used:
            groups.setdefault((cm[s]['m'] + 1, _frame(key_ext, s)), []).append(W.fmt(f'cmp.{s}.{d}', {}))
        text = ' '.join(W.fmt(k, dict(cmp=W.join_and(ws), n=W.numword(n))) for (n, k), ws in groups.items())
        return text, dict(kind='extreme', ext=ext, used=used)
    live = [(s, c) for s, c in cm.items() if c]
    if not live:
        return None, dict(kind='none', ext=[], used=[])
    s, c = max(live, key=lambda sc: abs(sc[1]['less'] - sc[1]['more']))   # first of equals, in list order
    text = W.fmt(_frame(key_cnt, s), dict(cmp=W.fmt(f'cmp.{s}.{c["side"]}', {}), k=W.numword(c['k']), m=W.numword(c['m'])))
    return text, dict(kind='count', ext=[], used=[(s, c['side'])])


def fill_ring_units(F, ok, no):
    """S6.2, S2.3, S5.2, S6.3, S6.4, S6.5 and a ring note, for one basin. ok and no are fill_units' own constructors."""
    U = {}
    f = F['flow']
    n_in, n_out = f['up1'] + f['upN'], f['dn1'] + f['dnN']
    if F['n_nb'] == 0:
        U['S6.2'] = no('no neighbouring basin', na=True)
    else:
        a = 'in_none' if n_in == 0 else 'in_one' if n_in == 1 else 'in_some'
        b = 'out_none' if n_out == 0 else 'out_one' if n_out == 1 else 'out_some'
        first = W.fmt('S6.2.' + a, dict(n=W.numword(n_in)))
        U['S6.2'] = ok(first[:1].upper() + first[1:] + ' ' + W.fmt('S6.2.' + b, dict(n=W.numword(n_out))),
                       f'in {n_in}, out {n_out}')
    df = F.get('ring')
    others = ('S2.3', 'S5.2', 'S6.3', 'S6.4', 'S6.5')
    if df is None:
        for uid in others:
            U[uid] = no('no ring values for this basin')
        return U
    core = F['hid']
    nbs = [int(m) for m in df[(df['role'] == 'neighbour') & (df['shared_km'] > 0)]['member'].unique()]
    V = member_values(df)
    areas = df.drop_duplicates('member').set_index('member')['area_km2'].to_dict()
    nb_areas = [areas[m] for m in nbs]
    if len(nbs) < MIN_NB:
        for uid in others:
            U[uid] = no(f'only {len(nbs)} neighbouring basin(s) (fewer than {MIN_NB})', na=True)
        U['S6.ring'] = ok('', f'{len(nbs)} neighbours; ring rules silent')
        return U

    for uid, slugs, ck, kx, kc in (('S2.3', L_S23, 'S2_3', 'S2.3.extreme', 'S2.3.count'),
                                   ('S5.2', L_S52, 'S5_2', 'S5.2.extreme', 'S5.2.count')):
        text, tr = _stated(slugs, CAP[ck], kx, kc, V, core, nbs)
        U[uid] = ok(text, f'{tr["kind"]}: ' + ', '.join(f'{s} {d}' for s, d in tr['used'])) if text else no('no measure with data distinguishes the basin', na=True)
        U[uid]['trace'] = tr

    across = [m for m in nbs if F['flow_nb'].get(m) in ('same', 'other')]
    hit = []
    for s in L_S63:
        d = V.get(MEAS[s], {})
        c, xs = d.get(core), [d[m] for m in across if m in d]
        if c is not None and len(xs) >= MIN_NB:
            if all(round(x, 6) > round(c, 6) for x in xs):
                hit.append((s, 'more'))
            elif all(round(x, 6) < round(c, 6) for x in xs):
                hit.append((s, 'less'))
    if hit:
        s, d = hit[0]
        U['S6.3'] = ok(W.fmt(_frame('S6.3.all', s), dict(cmp=W.fmt(f'cmp.{s}.{d}', {}))), f'{s} {d}; {len(across)} across a divide')
    else:
        U['S6.3'] = no(f'no measure on which all {len(across)} basins across its divides lie on one side', na=True)
    U['S6.3']['trace'] = dict(across=len(across), hit=hit)

    out = []     # measures on which the core lies outside the range of its neighbours
    m = 0
    for var in NUMERIC_LOCAL:
        d = V.get(var, {})
        c, xs = d.get(core), [d[x] for x in nbs if x in d]
        if c is None or len(xs) < MIN_NB or all(round(x, 6) == round(c, 6) for x in xs):
            continue
        m += 1
        if not min(xs) <= c <= max(xs):
            out.append(var)
    k = len(out)
    if k:
        U['S6.4'] = ok(W.fmt('S6.4', dict(k=W.numword(k), m=W.numword(m))), f'outside on {k} of {m}: ' + ', '.join(out))
    elif m:
        U['S6.4'] = no(f'within the range of its neighbours on all {m} measures (nothing to say)', na=True)
    else:
        U['S6.4'] = no('no measure to compare', na=True)
    U['S6.4']['trace'] = dict(k=k, m=m, out=out)

    cm = _cmps(L_S65, V, core, nbs)
    ext = [(s, 'top' if c['top'] else 'bottom') for s, c in cm.items() if c and (c['top'] or c['bottom'])]
    if ext:
        used = ext[:CAP['S6_5']]
        U['S6.5'] = ok(W.fmt('S6.5', dict(n=W.numword(len(nbs) + 1), list=W.join_and([W.fmt(f'cmp.{s}.{d}', {}) for s, d in used]))),
                       ', '.join(f'{s} {d}' for s, d in used))
    else:
        U['S6.5'] = no('the basin is the highest or lowest of the set on none of the terrain, forest, karst or soil measures', na=True)
    U['S6.5']['trace'] = dict(ext=ext, used=ext[:CAP['S6_5']])

    rank = 'the smallest' if areas[core] < min(nb_areas) else 'the largest' if areas[core] > max(nb_areas) else 'neither the smallest nor the largest'
    U['S6.ring'] = ok('', f'{len(nbs)} neighbours; areas km2 core {areas[core]:,.0f}, neighbours {min(nb_areas):,.0f} to {max(nb_areas):,.0f}; the core is {rank} by area')
    U['S6.ring']['trace'] = dict(n_nb=len(nbs), smallest=areas[core] < min(nb_areas), largest=areas[core] > max(nb_areas))
    return U
