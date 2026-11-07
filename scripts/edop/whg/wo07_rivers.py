"""WO-07 part C: the nearest river (S3.1) and a much larger river nearby (S3.3).

`gaz.rivers` (HydroRIVERS) gives presence, size and distance; its `ord_flow` is a discharge class (1 the largest, 10 the
smallest; 5 = 10 to 99.99 m3/s, 6 = 1 to 9.99). Natural Earth rivers (data/ne_10m_rivers_lake_centerlines_scale_rank)
give a name only where they have a line near the reach. For every point the table holds what each cutoff would give, so a
cutoff can be chosen (and changed) without querying again: the nearest reach at class 5 and at class 6, the largest class
in the place's own basin, and the nearest reach at least STEP classes larger than that. Read-only.
"""
import numpy as np
import pandas as pd

from scripts.edop.whg import wo04_fill as W

RIVERS_CSV = W.ROOT / 'output' / 'edop' / 'whg' / 'wo07_rivers.csv'
LABELS_CSV = W.ROOT / 'output' / 'edop' / 'whg' / 'wo07_river_labels.csv'
NE_SHP = W.ROOT / 'data' / 'ne_10m_rivers_lake_centerlines_scale_rank' / 'ne_10m_rivers_lake_centerlines_scale_rank.shp'

CLASSES = (4, 5, 6)       # minimum size of the nearest river tried: ord_flow at or below 4 (100 m3/s), 5 (10 m3/s) or 6 (1 m3/s)
STEP = 2                  # "much larger": this many discharge classes (a factor of 10 each) above the largest in the own basin
D_KM = (10, 25, 50)       # distances tried for "nearby"
# the values the sentences use now; the table keeps every value tried, so changing them needs no new query
USE_CLASS, USE_D, NAME_KM = 5, 25, 5.0
NAMED_LIMITS = {'r4': 25.0}   # S3.1 tier 1: only a river of class 4 or larger (100 m3/s and up) is named, out to this distance; smaller rivers are never named (see wo07_results.md, river names)
ON_KM = 1.5               # ... and within this distance the place is 'on' it
NEAR_KM = 3.0             # S3.1: no named river, but a river of class 5 or larger within this distance is mentioned (tier 2); beyond, silence
# S3.1 ignores anything smaller than class 5 (10 m3/s): the class 6 values stay in the table but are not used
OWN_MIN_KM = 1.0          # a reach counts as "in the own basin" only with more than this much length inside it (not a boundary clip)

REACH_SQL = """
WITH p AS (SELECT ST_SetSRID(ST_MakePoint(%s, %s), 4326) AS geom)
SELECT r.hyriv_id::bigint, r.ord_flow::int, r.dis_av_cms::float8, ST_Distance(r.geog, p.geom::geography) / 1000.0,
       ST_X(ST_ClosestPoint(r.geom, p.geom)), ST_Y(ST_ClosestPoint(r.geom, p.geom))
FROM gaz.rivers r, p WHERE r.ord_flow <= %s ORDER BY r.geog <-> p.geom::geography LIMIT 1
"""
BIG_SQL = """
WITH p AS (SELECT ST_SetSRID(ST_MakePoint(%s, %s), 4326) AS geom)
SELECT r.hyriv_id::bigint, r.ord_flow::int, r.dis_av_cms::float8, ST_Distance(r.geog, p.geom::geography) / 1000.0,
       ST_X(ST_ClosestPoint(r.geom, p.geom)), ST_Y(ST_ClosestPoint(r.geom, p.geom))
FROM gaz.rivers r, p WHERE r.ord_flow <= %s AND ST_DWithin(r.geog, p.geom::geography, %s) ORDER BY r.geog <-> p.geom::geography LIMIT 1
"""
OWN_SQL = """
SELECT min(r.ord_flow)::int FROM gaz.rivers r JOIN public.basin06 b ON ST_Intersects(r.geom, b.geom)
WHERE b.hybas_id = %s AND ST_Length(ST_Intersection(r.geom, b.geom)::geography) / 1000.0 > %s
"""

_NE = {}
_PARTS = ('reach', 'ord', 'dis', 'km', 'cx', 'cy', 'name', 'name_km', 'qid', 'name2', 'name2_km', 'qid2')
FIELDS = ['key', 'label', 'group', 'lat', 'lon', 'hid', 'own_min'] + [f'{p}_{x}' for p in ('r4', 'r5', 'r6', 'big') for x in _PARTS]


def river_keys():
    return {'S3.1.on', 'S3.1.named', 'S3.1.unnamed', 'S3.1.unnamed_on', 'S3.3.named', 'S3.3.unnamed', 'S3.3.same', 'S3.3.same.named'}


def key(lat, lon):
    return f'{lat:.5f},{lon:.5f}'


def _ne():
    if not _NE:
        import geopandas as gpd
        G = gpd.read_file(NE_SHP)
        G['label_name'] = G['name_en'].where(G['name_en'].notna(), G['name'])
        ok = G['featurecla'].isin(['River', 'River (Intermittent)']) & G['label_name'].notna()
        NE = G[ok].reset_index(drop=True)
        NE['qid'] = NE['wikidataid'].where(NE['wikidataid'].notna(), '')
        _NE.update(df=NE, sindex=NE.geometry.sindex)
    return _NE


def ne_nearest(lat, lon, n_keep=2):
    """Distinct nearest Natural Earth river lines to a point: [(name, km, wikidata id), ...], nearest first (as in WO-03 Q4).
    Two lines are the same river when they share an id (or, without one, a name)."""
    from pyproj import CRS, Transformer
    from shapely.geometry import Point
    from shapely.ops import transform
    NE, sindex = _ne()['df'], _ne()['sindex']
    pt = Point(lon, lat)
    tr = Transformer.from_crs(CRS.from_epsg(4326), CRS.from_proj4(f'+proj=aeqd +lat_0={lat} +lon_0={lon} +datum=WGS84 +units=m'), always_xy=True)
    inscribed = lambda r: r * 111.0 * max(np.cos(np.radians(abs(lat))), 0.05)
    best = []
    for r in (0.25, 0.5, 1, 2, 4, 8, 16, 32, 64):
        ids = sindex.query(pt.buffer(r))
        if len(ids) == 0:
            continue
        rows = sorted(((NE['label_name'].iloc[i], transform(tr.transform, NE.geometry.iloc[i]).distance(Point(0, 0)) / 1000.0, NE['qid'].iloc[i]) for i in ids), key=lambda x: x[1])
        best = rows
        if rows[0][1] <= inscribed(r):
            break
    out, seen = [], set()
    for nm, km, qid in best:
        ident = qid or nm
        if ident not in seen:
            seen.add(ident); out.append((nm, km, qid))
        if len(out) == n_keep:
            break
    return out


def _reach(conn, lat, lon, max_class, prefix, within_km=None):
    """The nearest reach at or below a class (within within_km, if given), its distance and the Natural Earth names near its closest point."""
    if max_class < 1:
        return {}
    r = (conn.execute(BIG_SQL, (lon, lat, max_class, within_km * 1000.0)).fetchone() if within_km
         else conn.execute(REACH_SQL, (lon, lat, max_class)).fetchone())
    if r is None:
        return {}
    nn = ne_nearest(r[5], r[4], 2)
    d = {f'{prefix}_reach': r[0], f'{prefix}_ord': r[1], f'{prefix}_dis': r[2], f'{prefix}_km': r[3], f'{prefix}_cx': r[4], f'{prefix}_cy': r[5],
         f'{prefix}_name': nn[0][0] if nn else '', f'{prefix}_name_km': nn[0][1] if nn else np.nan, f'{prefix}_qid': nn[0][2] if nn else '',
         f'{prefix}_name2': nn[1][0] if len(nn) > 1 else '', f'{prefix}_name2_km': nn[1][1] if len(nn) > 1 else np.nan, f'{prefix}_qid2': nn[1][2] if len(nn) > 1 else ''}
    return d


def point_row(conn, lat, lon, label='', group=''):
    """Everything the river sentences can need for one point, for every cutoff tried."""
    b = conn.execute('SELECT hybas_id FROM public.basin06 WHERE ST_Intersects(geom, ST_SetSRID(ST_MakePoint(%s, %s), 4326)) LIMIT 1', (lon, lat)).fetchone()
    hid = int(b[0]) if b else None
    own_min = conn.execute(OWN_SQL, (hid, OWN_MIN_KM)).fetchone()[0] if hid else None
    d = dict(key=key(lat, lon), label=label, group=group, lat=lat, lon=lon, hid=hid, own_min=own_min)
    for c in CLASSES:
        d.update(_reach(conn, lat, lon, c, f'r{c}'))
    if own_min is not None:
        d.update(_reach(conn, lat, lon, own_min - STEP, 'big', within_km=max(D_KM)))
    return {f: d.get(f) for f in FIELDS}


def fetch_table(points, conn, path=RIVERS_CSV, every=25, log=print):
    """points: [(label, group, lat, lon)]. Appends a row per point not already in the file (resumable). A point that fails is
    logged and skipped, never stopping the run; returns (rows in the file, new rows, [(label, error), ...])."""
    import time
    conn.execute('SET statement_timeout = 120000')
    done = set(pd.read_csv(path, usecols=['key'])['key']) if path.exists() else set()
    t0, new, failed = time.perf_counter(), 0, []
    for k, (label, group, lat, lon) in enumerate(points, 1):
        try:
            if key(lat, lon) not in done:
                row = point_row(conn, lat, lon, label, group)
                pd.DataFrame([row], columns=FIELDS).to_csv(path, mode='a', header=not path.exists(), index=False)
                done.add(row['key']); new += 1
        except Exception as e:
            failed.append((label, f'{type(e).__name__}: {e}'[:200]))
            try:
                conn.rollback(); conn.execute('SET statement_timeout = 120000')
            except Exception:
                pass
        if k % every == 0:
            log(f'  {k} of {len(points)} points | {new} new | {len(failed)} failed | {time.perf_counter() - t0:.0f}s')
    return len(done), new, failed


def load_table(path=RIVERS_CSV):
    """{key: row dict}; a repeated key keeps its last row."""
    t = pd.read_csv(path, low_memory=False)
    return {r['key']: r for r in t.drop_duplicates('key', keep='last').to_dict('records')}


def _val(row, k):
    v = row.get(k)
    return None if v is None or (isinstance(v, float) and np.isnan(v)) else v


_LABELS = {}
_GENERIC = {'river', 'rio', 'rio', 'the', 'of', 'de', 'del', 'la', 'le', 'les', 'fleuve', 'riviere', 'branch', 'canal'}


def _tokens(x):
    import re, unicodedata
    t = re.sub(r'[^a-z0-9 ]', ' ', unicodedata.normalize('NFKD', str(x)).encode('ascii', 'ignore').decode().lower()).split()
    return {w for w in t if len(w) >= 3 and w not in _GENERIC}


def agrees(ne_name, label):
    """The Wikidata label and the Natural Earth line's own name share a word (an id attached to the wrong river does not)."""
    return bool(_tokens(ne_name) & _tokens(label))


def labels():
    """{wikidata id: English label} from the one-time lookup (fetch_labels); empty if it has not been run."""
    if not _LABELS and LABELS_CSV.exists():
        t = pd.read_csv(LABELS_CSV).fillna('')
        _LABELS.update({q: l for q, l in zip(t['qid'], t['label_en']) if l})
    return _LABELS


def _name(row, prefix):
    """The river's name (its Wikidata label) only when a Natural Earth line with an id and a label lies within NAME_KM of
    the reach and no line of a different river does (two close rivers are ambiguous, so the sentence says 'a river')."""
    nm, km, q, nm2, km2, q2 = (_val(row, f'{prefix}_{x}') for x in ('name', 'name_km', 'qid', 'name2', 'name2_km', 'qid2'))
    if not isinstance(q, str) or not q or km is None or not (km <= NAME_KM) or q not in labels():
        return ''
    if km2 is not None and km2 <= NAME_KM and (nm2 or q2) and q2 != q:
        return ''
    if not agrees(nm, labels()[q]):
        return ''
    return labels()[q]


def _km(km):
    """A distance in figures, to the nearest km (not less than 1)."""
    return f'{max(1, int(round(km))):,}'


def fill_river_units(F, ok, no):
    """S3.1 (nearest river) and S3.3 (a much larger river nearby; silent when there is none)."""
    row = F.get('river')
    if row is None:
        return {'S3.1': no('no river row for this point'), 'S3.3': no('no river row for this point', na=True)}
    U = {}
    used = None             # the reach S3.1 spoke about
    nm_ = '{name}'          # the place's name is put in by the renderer
    named = [(row[f'{p}_km'], p, _name(row, p)) for p in NAMED_LIMITS if _val(row, f'{p}_km') is not None and _name(row, p)]
    named = [t for t in named if t[0] <= NAMED_LIMITS[t[1]]]
    k6 = _val(row, 'r5_km')
    if named:                                   # tier 1: a named river is close
        km, p, nm = min(named)
        used = int(row[f'{p}_reach'])
        text = W.fmt('S3.1.on' if km <= ON_KM else 'S3.1.named', dict(name=nm_, d=_km(km), river=nm))
        U['S3.1'] = ok(text, f'tier 1: class {int(row[p + "_ord"])} reach {int(row[p + "_reach"])}, {km:.1f} km, {row[p + "_dis"]:.1f} m3/s; named {nm} (line {row[p + "_name_km"]:.1f} km from the reach)')
    elif k6 is not None and k6 <= NEAR_KM:      # tier 2: an unnamed river is truly close
        used = int(row['r5_reach'])
        text = W.fmt('S3.1.unnamed_on' if k6 <= ON_KM else 'S3.1.unnamed', dict(name=nm_, d=_km(k6)))
        U['S3.1'] = ok(text, f'tier 2: class {int(row["r5_ord"])} reach {int(row["r5_reach"])}, {k6:.1f} km, {row["r5_dis"]:.1f} m3/s; no name (nearest line: {row.get("r5_name") or "none"}' + (f', {row["r5_name_km"]:.1f} km' if _val(row, 'r5_name_km') is not None else '') + ')')
    else:                                       # tier 3: silence
        k5 = _val(row, 'r5_km')
        U['S3.1'] = no('no river of class 5 or larger within ' + f'{NEAR_KM:g} km, and no named river within its limit (nearest class 5: ' + (f'{k5:.0f} km)' if k5 is not None else 'none)'), na=True)
    big_km = _val(row, 'big_km')
    if big_km is None:
        own = _val(row, 'own_min')
        U['S3.3'] = no('no reach within ' + str(max(D_KM)) + f' km that is {STEP} classes above the largest in the own basin' + (f' (class {int(own)})' if own is not None else ' (no basin)'), na=True)
    elif big_km > USE_D:
        U['S3.3'] = no(f'the nearest much larger river is {big_km:.0f} km away (more than {USE_D})', na=True)
    else:
        nm = _name(row, 'big')
        same = used is not None and used == int(row['big_reach'])   # S3.1 already spoke of this river
        if same:
            text = W.fmt('S3.3.same.named', dict(river=nm)) if nm else W.fmt('S3.3.same', {})
        else:
            text = W.fmt('S3.3.named', dict(d=_km(big_km), river=nm)) if nm else W.fmt('S3.3.unnamed', dict(d=_km(big_km)))
        U['S3.3'] = ok(text, f'own basin largest class {int(row["own_min"])}; class {int(row["big_ord"])} reach {int(row["big_reach"])}, {big_km:.1f} km, {row["big_dis"]:.0f} m3/s; '
                       + ('the same reach as S3.1; ' if same else '') + (f'named {nm}' if nm else 'unnamed'))
    return U


# ---- proper river names: Wikidata labels for the Natural Earth lines' wikidataid ---------------------------------------

WD_API = 'https://www.wikidata.org/w/api.php'
WD_AGENT = 'EDOPS-research/0.4 (https://edops.computingplace.org; karl.geog@gmail.com) river-label lookup'


def ne_ids():
    """The distinct Wikidata ids on Natural Earth's named river lines, with the Natural Earth names that carry each."""
    import geopandas as gpd
    G = gpd.read_file(NE_SHP)
    R = G[G['featurecla'].isin(['River', 'River (Intermittent)']) & G['wikidataid'].notna()]
    return R.groupby('wikidataid').agg(ne_names=('name_en', lambda s: '; '.join(sorted({x for x in s if isinstance(x, str)}))),
                                       lines=('name_en', 'size')).reset_index()


def fetch_labels(path=LABELS_CSV, batch=50, pause=0.6, log=print):
    """One-time lookup: English label and description for every id, saved to a CSV (an id already in the file is skipped)."""
    import json, ssl, time, urllib.parse, urllib.request
    import certifi
    ctx = ssl.create_default_context(cafile=certifi.where())      # this Python has no system certificate bundle
    ids = ne_ids()
    have = set(pd.read_csv(path)['qid']) if path.exists() else set()
    todo = [q for q in ids['wikidataid'] if q not in have]
    new = []
    for i in range(0, len(todo), batch):
        chunk = todo[i:i + batch]
        url = WD_API + '?' + urllib.parse.urlencode(dict(action='wbgetentities', ids='|'.join(chunk), props='labels|descriptions', languages='en', format='json'))
        with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': WD_AGENT}), timeout=60, context=ctx) as r:
            ents = json.loads(r.read()).get('entities', {})
        for q in chunk:
            e = ents.get(q, {})
            new.append(dict(qid=q, label_en=e.get('labels', {}).get('en', {}).get('value', ''),
                            description_en=e.get('descriptions', {}).get('en', {}).get('value', ''), missing='missing' in e))
        log(f'  {min(i + batch, len(todo))} of {len(todo)}')
        time.sleep(pause)
    if new:
        pd.DataFrame(new).to_csv(path, mode='a', header=not path.exists(), index=False)
    return len(have) + len(new), len(new)


# ---- is a name solid? the along-the-course check ----------------------------------------------------------------------

CHAIN_SQL = "SELECT next_down::bigint, length_km::float8, ST_AsText(geom) FROM gaz.rivers WHERE hyriv_id = %s"


def course_check(conn, reach, qid, max_reaches=15, max_km=40.0, step_km=1.0, tol_km=2.0):
    """How well a Natural Earth river (all its lines with this Wikidata id) follows the matched reach: the share of points
    sampled every step_km along the reach (first_frac) and along it plus the reaches downstream, up to max_km (chain_frac),
    that lie within tol_km of the river's lines. A real match follows the course; a wrong one touches it at a point."""
    from pyproj import CRS, Transformer
    from shapely import wkt
    from shapely.geometry import Point
    from shapely.ops import linemerge, transform, unary_union
    lines, rid, km = [], int(reach), 0.0
    for _ in range(max_reaches):
        r = conn.execute(CHAIN_SQL, (rid,)).fetchone()
        if r is None:
            break
        g = linemerge(wkt.loads(r[2]))
        lines.append(g if g.geom_type == 'LineString' else max(g.geoms, key=lambda x: x.length)); km += r[1] or 0.0
        if not r[0] or km >= max_km:
            break
        rid = int(r[0])
    if not lines or not isinstance(qid, str) or not qid:
        return {}
    NE = _ne()['df']
    same = NE[NE['qid'] == qid]
    if same.empty:
        return {}
    c = lines[0].coords[0]
    tr = Transformer.from_crs(CRS.from_epsg(4326), CRS.from_proj4(f'+proj=aeqd +lat_0={c[1]} +lon_0={c[0]} +datum=WGS84 +units=m'), always_xy=True)
    near = same[same.geometry.distance(Point(c[0], c[1])) < 3.0]       # about 300 km, in degrees
    if near.empty:
        return dict(first_frac=0.0, chain_frac=0.0, n_pts=0, rank=int(same['scalerank'].min()), reaches=len(lines), km=round(km, 1))
    ne = unary_union([transform(tr.transform, g) for g in near.geometry])
    pts = []
    for ln in lines:
        L = transform(tr.transform, ln)
        n = max(1, int(L.length / (step_km * 1000.0)))
        pts.append([L.interpolate(k / n, normalized=True) for k in range(n + 1)] if L.length > 0 else [])
    ok = lambda p: ne.distance(p) <= tol_km * 1000.0
    first = [ok(p) for p in pts[0]] or [False]
    allp = [ok(p) for ps in pts for p in ps] or [False]
    return dict(first_frac=round(sum(first) / len(first), 2), chain_frac=round(sum(allp) / len(allp), 2), n_pts=len(allp),
                rank=int(near['scalerank'].min()), reaches=len(lines), km=round(km, 1))
