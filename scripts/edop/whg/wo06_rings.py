"""WO-06: the persisted ring-values table and the neighbour comparison rules.

Fetches, once per basin, the local values of the core and of every basin that meets it (the /api/areas basin_ring
call, plus mean elevation and forest share from public.basin06, which the ring payload does not carry), and saves
them to output/edop/whg/wo06_ring_values.csv. The rules then run on that table alone, with no live calls.

A comparison states only what is true without a cutoff: being the highest or lowest of the set, counts of the
basins a basin is more or less than, "all of them". Ties are never ranked. Wording is in profile_templates.md
(the `cmp.*`, `S2.3.*`, `S5.2.*`, `S6.2.*`, `S6.3.*` and `S6.5` lines). Read-only.
"""
import pandas as pd

from scripts.edop.whg import missing
from scripts.edop.whg import wo04_fill as W

RING_CSV = W.ROOT / 'output' / 'edop' / 'whg' / 'wo06_ring_values.csv'

MIN_NB = 3                             # fewest neighbours with a value for any comparison
MIN_ABO = 5                            # fewest for "all but one" (in a ring of three or four it is only "second highest")
CAP = dict(S2_3=2, S5_2=2, S6_5=3)     # most extremes stated in one sentence

# measure slug -> variable name in the ring rows (elev_mean and forest_extent come from basin06; relief is derived)
MEAS = {'precip': 'precip_yr', 'temp': 'temp_yr', 'aridity': 'aridity', 'elev': 'elev_mean', 'relief': 'relief',
        'slope': 'slope_avg', 'cropland': 'cropland_extent', 'pasture': 'pasture_extent', 'popdens': 'pop_density',
        'footprint': 'human_footprint_09', 'forest': 'forest_extent', 'karst': 'karst', 'sand': 'pct_sand',
        'silt': 'pct_silt', 'clay': 'pct_clay', 'runoff': 'runoff', 'permafrost': 'permafrost_extent',
        'gwdepth': 'gw_table_depth'}
# which measures each sentence draws on, in the order they are tried (an editorial choice, to be adjusted)
L_S23 = ['precip', 'temp', 'aridity']
L_S52 = ['cropland', 'pasture', 'forest']           # population density and human footprint are left out: places are where people are
L_S63 = ['elev', 'precip', 'temp', 'aridity']      # only measures with an adjective ("all higher")
L_S65 = ['elev', 'relief', 'slope', 'karst', 'sand', 'silt', 'clay', 'runoff', 'permafrost', 'gwdepth']
L_UNSTATED = {'popdens': 'population density', 'footprint': 'human footprint'}   # compared, kept in the fill notes only


def ring_keys():
    """Every template key the ring rules read; check_keys requires them once the template has S6.2.in_none."""
    keys = {f'S6.2.{k}' for k in ('in_none', 'in_one', 'in_some', 'out_one', 'out_some', 'out_chain', 'out_none')}
    keys |= {'S2.3.extreme', 'S2.3.allbutone', 'S2.3.allbutone.precip', 'S5.2.extreme', 'S5.2.allbutone',
             'S6.3.all', 'S6.3.all.precip', 'S6.3.allbutone', 'S6.3.allbutone.precip', 'S6.5'}
    for s in set(L_S23) | set(L_S52) | set(L_S63):
        keys |= {f'cmp.{s}.{d}' for d in ('top', 'bottom', 'more', 'less')}
    for s in L_S65:
        keys |= {f'cmp.{s}.{d}' for d in ('top', 'bottom')}
    return keys


def ring_optional():
    """Middle counts ("less than three of the five"): they speak only while the template carries these lines."""
    return {'S2.3.count', 'S2.3.count.precip', 'S5.2.count', 'S2.3.counts', 'S2.3.counts.item', 'S2.3.counts.item.precip',
            'S5.2.counts', 'S5.2.counts.item', 'S2.3.extreme.counts', 'S5.2.extreme.counts'}



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
            good = not missing.is_missing(v)     # -9999 is the source's NoData
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
    """{variable: {member: float}}. Flagged extents (outside_active_domain) count at their stored value, 0 if empty; no data or low coverage is left out."""
    v = {}
    for r in df.itertuples(index=False):
        x = r.value
        if r.status == 'outside_active_domain':
            x = 0.0 if pd.isna(x) else x     # the table carries the 0 or 1 of basin06 (wo09_patch_ring); 0 if a table was never patched
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
    return dict(m=m, less=less, more=more, top=(less == m), bottom=(more == m), side=side, k=k,
                abo=(m >= MIN_ABO and k == m - 1))


def _frame(key, slug):
    """The measure's own frame (`key.slug`) when the template has one, else the shared one."""
    return f'{key}.{slug}' if f'{key}.{slug}' in W.templates()['text'] else key


def _has(key):
    return key in W.templates()['text']


def _nums(*ns):
    """Numbers as words up to ten; figures for all of them as soon as one is above ten ("10 of the 12")."""
    return tuple(W.numword(n) for n in ns) if max(ns) <= 10 else tuple(f'{n:,}' for n in ns)


def _join_phrases(ws):
    """'receives the least precipitation and is the most arid'; a run of 'is ...' phrases shares its verb."""
    out = [w[3:] if i and w.startswith('is ') and ws[i - 1].startswith('is ') else w for i, w in enumerate(ws)]
    return W.join_and(out)


def _cmps(slugs, V, core, nbs):
    out = {}
    for s in slugs:
        d = V.get(MEAS[s], {})
        out[s] = compare(d.get(core), [d[m] for m in nbs if m in d])
    return out


def _one(slugs_cm, key_abo, key_cnt):
    """A single measure standing among the neighbours, as one sentence of its own (the earlier wording)."""
    s, c = slugs_cm
    if c['abo']:
        return W.fmt(_frame(key_abo, s), dict(cmp=W.fmt(f'cmp.{s}.{c["side"]}', {}), m=_nums(c['m'])[0])), 'allbutone'
    k, m = _nums(c['k'], c['m'])
    return W.fmt(_frame(key_cnt, s), dict(cmp=W.fmt(f'cmp.{s}.{c["side"]}', {}), k=k, m=m)), 'count'


def _stated(slugs, cap, key_ext, key_abo, key_cnt, key_cnts, V, core, nbs):
    """The sentences for S2.3 or S5.2, plus a trace: the extremes (up to cap) in one sentence; then every other measure
    that stands out (all but one, or more than half the set) -- alone in its own sentence (key_abo, key_cnt), or, when
    there are two or more and the template has key_cnts, together in one sentence. A count not stated (the template has
    no line for it, or it is not more than half) is kept in `unstated`."""
    cm = _cmps(slugs, V, core, nbs)
    ext = [(s, 'top' if c['top'] else 'bottom') for s, c in cm.items() if c and (c['top'] or c['bottom'])]
    used, texts, kinds, unstated = ext[:cap], [], [], []
    isext = {s for s, _ in ext}
    live = [(s, c) for s, c in cm.items() if c and s not in isext]
    firm = [(s, c) for s, c in live if c['abo'] or 2 * c['k'] > c['m']]     # a count is stated only when more than half the set
    for s, c in live:
        if (s, c) not in firm:
            k, m = _nums(c['k'], c['m'])
            unstated.append(f'{s} {c["side"]} than {k} of {m}, not more than half')
    stated = []
    item = lambda s, c: W.fmt(_frame(key_cnts + '.item', s), dict(cmp=W.fmt(f'cmp.{s}.{c["side"]}', {}),
                                                                 k='all but one' if c['abo'] else _nums(c['k'], c['m'])[0]))
    ms = {cm[s]['m'] for s, _ in used}
    fold = bool(used) and bool(firm) and _has(key_ext + '.counts') and _has(key_cnts) and len(ms) == 1 and {c['m'] for _, c in firm} == ms
    if used and not fold:   # (formatted only here: a line the fold does not use must not be recorded)
        groups = {}          # extremes over the same set of basins share one sentence
        for s, d in used:
            groups.setdefault(cm[s]['m'] + 1, []).append(W.fmt(f'cmp.{s}.{d}', {}))
        texts.append(' '.join(W.fmt(key_ext, dict(cmp=_join_phrases(ws), n=W.numword(n))) for n, ws in groups.items()))
        kinds.append('extreme')
    if fold:             # the extremes and the counts are about the same basins: one sentence, one count of them
        m = ms.pop()
        texts = [W.fmt(key_ext + '.counts', dict(cmp=_join_phrases([W.fmt(f'cmp.{s}.{d}', {}) for s, d in used]), n=W.numword(m + 1),
                                                m=_nums(m)[0], list=W.join_and([item(s, c) for s, c in firm])))]
        kinds = ['extreme+counts']
        stated = [(s, c['side']) for s, c in firm]
    elif len(firm) >= 2 and _has(key_cnts):
        groups = {}          # measures over the same number of neighbours share the sentence
        for s, c in firm:
            groups.setdefault(c['m'], []).append((s, c))
        for m, items in groups.items():
            texts.append(W.fmt(key_cnts, dict(m=_nums(m)[0], list=W.join_and([item(s, c) for s, c in items]))))
        kinds.append('counts')
        stated = [(s, c['side']) for s, c in firm]
    elif firm:
        abo = [(s, c) for s, c in firm if c['abo']]
        if abo:
            pick = abo[0]
        elif _has(key_cnt):
            pick = max(firm, key=lambda sc: abs(sc[1]['less'] - sc[1]['more']))   # first of equals, in list order
        else:
            pick = None
        for s, c in firm:
            if pick is None or (s, c) != pick:
                k, m = _nums(c['k'], c['m'])
                unstated.append(f'{s} {c["side"]} than {k} of {m}')
        if pick is not None:
            t, kd = _one(pick, key_abo, key_cnt)
            texts.append(t); kinds.append(kd); stated = [(pick[0], pick[1]['side'])]
    if not texts:
        kind = 'count_unstated' if unstated else 'none'
    else:
        kind = '+'.join(kinds)
    return (' '.join(texts) or None), dict(kind=kind, ext=ext, used=used + stated, unstated='; '.join(unstated))


def _standing(slug, c):
    """For the fill notes: where the core stands on a measure the sentences leave out."""
    return f'{slug} ' + ('highest' if c['top'] else 'lowest' if c['bottom'] else f'{c["side"]} than {c["k"]} of {c["m"]}')


def fill_ring_units(F, ok, no):
    """S6.2, S2.3, S5.2, S6.3, S6.5 and a ring note, for one basin. ok and no are fill_units' own constructors."""
    U = {}
    f = F['flow']
    n_in, n_out = f['up1'] + f['upN'], f['dn1'] + f['dnN']
    if F['n_nb'] == 0:
        U['S6.2'] = no('no neighbouring basin', na=True)
    else:
        a = 'in_none' if n_in == 0 else 'in_one' if n_in == 1 else 'in_some'
        chain = f['dn1'] == 1 and f['dnN'] >= 1   # one basin directly downstream and others further on
        b = 'out_none' if n_out == 0 else 'out_one' if n_out == 1 else 'out_chain' if chain else 'out_some'
        first = W.fmt('S6.2.' + a, dict(n=W.numword(n_in)))
        U['S6.2'] = ok(first[:1].upper() + first[1:] + ' ' + W.fmt('S6.2.' + b, dict(n=W.numword(f['dnN'] if chain else n_out))),
                       f'in {n_in}, out {n_out}')
    df = F.get('ring')
    others = ('S2.3', 'S5.2', 'S6.3', 'S6.5')
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

    for uid, slugs, ck, kx, ka, kc, kn in (('S2.3', L_S23, 'S2_3', 'S2.3.extreme', 'S2.3.allbutone', 'S2.3.count', 'S2.3.counts'),
                                           ('S5.2', L_S52, 'S5_2', 'S5.2.extreme', 'S5.2.allbutone', 'S5.2.count', 'S5.2.counts')):
        text, tr = _stated(slugs, CAP[ck], kx, ka, kc, kn, V, core, nbs)
        if text:
            U[uid] = ok(text, f'{tr["kind"]}: ' + ', '.join(f'{s} {d}' for s, d in tr['used']) + (f' | not stated: {tr["unstated"]}' if tr['unstated'] else ''))
        elif tr['unstated']:
            U[uid] = no(f'count not stated: {tr["unstated"]}', na=True)
        else:
            U[uid] = no('no measure with data distinguishes the basin', na=True)
        U[uid]['trace'] = tr

    across = [m for m in nbs if F['flow_nb'].get(m) in ('same', 'other')]
    hit, abo = [], []
    for s in L_S63:
        d = V.get(MEAS[s], {})
        c, xs = d.get(core), [d[m] for m in across if m in d]
        if c is None or len(xs) < MIN_NB:
            continue
        up, dn = sum(round(x, 6) > round(c, 6) for x in xs), sum(round(x, 6) < round(c, 6) for x in xs)
        if up == len(xs):
            hit.append((s, 'more'))
        elif dn == len(xs):
            hit.append((s, 'less'))
        elif len(xs) >= MIN_ABO and up == len(xs) - 1:
            abo.append((s, 'more'))
        elif len(xs) >= MIN_ABO and dn == len(xs) - 1:
            abo.append((s, 'less'))
    if hit:
        s, d = hit[0]
        U['S6.3'] = ok(W.fmt(_frame('S6.3.all', s), dict(cmp=W.fmt(f'cmp.{s}.{d}', {}))), f'all: {s} {d}; {len(across)} across a divide')
    elif abo:
        s, d = abo[0]
        U['S6.3'] = ok(W.fmt(_frame('S6.3.allbutone', s), dict(cmp=W.fmt(f'cmp.{s}.{d}', {}))), f'all but one: {s} {d}; {len(across)} across a divide')
    else:
        U['S6.3'] = no(f'no measure on which all, or all but one of, the {len(across)} basins across its divides lie on one side', na=True)
    U['S6.3']['trace'] = dict(across=len(across), hit=hit, abo=abo)

    cm = _cmps(L_S65, V, core, nbs)
    ext = [(s, 'top' if c['top'] else 'bottom') for s, c in cm.items() if c and (c['top'] or c['bottom'])]
    if ext:
        used = ext[:CAP['S6_5']]
        U['S6.5'] = ok(W.fmt('S6.5', dict(n=W.numword(len(nbs) + 1), list=W.join_and([W.fmt(f'cmp.{s}.{d}', {}) for s, d in used]))),
                       ', '.join(f'{s} {d}' for s, d in used))
    else:
        U['S6.5'] = no('the basin is the highest or lowest of the set on none of the terrain, forest, karst, soil, runoff, permafrost or water-table measures', na=True)
    U['S6.5']['trace'] = dict(ext=ext, used=ext[:CAP['S6_5']])

    left_out = [_standing(L_UNSTATED[s], c) for s, c in _cmps(list(L_UNSTATED), V, core, nbs).items() if c]
    rank = 'the smallest' if areas[core] < min(nb_areas) else 'the largest' if areas[core] > max(nb_areas) else 'neither the smallest nor the largest'
    U['S6.ring'] = ok('', f'{len(nbs)} neighbours; areas km2 core {areas[core]:,.0f}, neighbours {min(nb_areas):,.0f} to {max(nb_areas):,.0f}; the core is {rank} by area'
                      + ('; left out of the sentences: ' + ', '.join(left_out) if left_out else ''))
    U['S6.ring']['trace'] = dict(n_nb=len(nbs), smallest=areas[core] < min(nb_areas), largest=areas[core] > max(nb_areas))
    return U
