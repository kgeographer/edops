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
NE_SHP = W.ROOT / 'data' / 'ne_10m_rivers_lake_centerlines_scale_rank' / 'ne_10m_rivers_lake_centerlines_scale_rank.shp'

CLASSES = (5, 6)          # minimum size of the nearest river tried: ord_flow at or below 5 (10 m3/s) or 6 (1 m3/s)
STEP = 2                  # "much larger": this many discharge classes (a factor of 10 each) above the largest in the own basin
D_KM = (10, 25, 50)       # distances tried for "nearby"
# the values the sentences use now; the table keeps every value tried, so changing them needs no new query
USE_CLASS, USE_D, NAME_KM = 5, 25, 5.0
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
_PARTS = ('reach', 'ord', 'dis', 'km', 'name', 'name_km', 'name2', 'name2_km')
FIELDS = ['key', 'label', 'group', 'lat', 'lon', 'hid', 'own_min'] + [f'{p}_{x}' for p in ('r5', 'r6', 'big') for x in _PARTS]


def river_keys():
    return {'S3.1.named', 'S3.1.unnamed', 'S3.3.named', 'S3.3.unnamed', 'S3.3.same'}


def key(lat, lon):
    return f'{lat:.5f},{lon:.5f}'


def _ne():
    if not _NE:
        import geopandas as gpd
        G = gpd.read_file(NE_SHP)
        G['label_name'] = G['name_en'].where(G['name_en'].notna(), G['name'])
        ok = G['featurecla'].isin(['River', 'River (Intermittent)']) & G['label_name'].notna()
        NE = G[ok].reset_index(drop=True)
        _NE.update(df=NE, sindex=NE.geometry.sindex)
    return _NE


def ne_nearest(lat, lon, n_keep=2):
    """Distinct-name nearest Natural Earth river lines to a point: [(name, km), ...], nearest first (as in WO-03 Q4)."""
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
        rows = sorted(((NE['label_name'].iloc[i], transform(tr.transform, NE.geometry.iloc[i]).distance(Point(0, 0)) / 1000.0) for i in ids), key=lambda x: x[1])
        best = rows
        if rows[0][1] <= inscribed(r):
            break
    out, seen = [], set()
    for nm, km in best:
        if nm not in seen:
            seen.add(nm); out.append((nm, km))
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
    d = {f'{prefix}_reach': r[0], f'{prefix}_ord': r[1], f'{prefix}_dis': r[2], f'{prefix}_km': r[3],
         f'{prefix}_name': nn[0][0] if nn else '', f'{prefix}_name_km': nn[0][1] if nn else np.nan,
         f'{prefix}_name2': nn[1][0] if len(nn) > 1 else '', f'{prefix}_name2_km': nn[1][1] if len(nn) > 1 else np.nan}
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


def _name(row, prefix):
    """The river's name only when a Natural Earth line lies within NAME_KM of the reach and no second differently
    named line does (two close names are ambiguous, so the sentence says 'a river'); else ''."""
    nm, km, nm2, km2 = (_val(row, f'{prefix}_{x}') for x in ('name', 'name_km', 'name2', 'name2_km'))
    if not isinstance(nm, str) or not nm or km is None or not (km <= NAME_KM):
        return ''
    if isinstance(nm2, str) and nm2 and km2 is not None and km2 <= NAME_KM:
        return ''
    return nm


def _km(km):
    """A distance in figures, to the nearest km (not less than 1)."""
    return f'{max(1, int(round(km))):,}'


def fill_river_units(F, ok, no):
    """S3.1 (nearest river) and S3.3 (a much larger river nearby; silent when there is none)."""
    row = F.get('river')
    if row is None:
        return {'S3.1': no('no river row for this point'), 'S3.3': no('no river row for this point', na=True)}
    p = f'r{USE_CLASS}'
    U = {}
    if _val(row, f'{p}_km') is None:
        U['S3.1'] = no('no river of this size in gaz.rivers')
    else:
        nm = _name(row, p)
        text = W.fmt('S3.1.named', dict(d=_km(row[f'{p}_km']), river=nm)) if nm else W.fmt('S3.1.unnamed', dict(d=_km(row[f'{p}_km'])))
        U['S3.1'] = ok(text, f'class {int(row[p + "_ord"])} reach {int(row[p + "_reach"])}, {row[p + "_km"]:.1f} km, {row[p + "_dis"]:.1f} m3/s; '
                       + (f'named {nm} (line {row[p + "_name_km"]:.1f} km from the reach)' if nm else
                          f'unnamed (nearest line: {row.get(p + "_name") or "none"}'
                          + (f', {row[p + "_name_km"]:.1f} km' if isinstance(row.get(p + "_name"), str) and row.get(p + "_name") else '') + ')'))
    big_km = _val(row, 'big_km')
    if big_km is None:
        own = _val(row, 'own_min')
        U['S3.3'] = no('no reach within ' + str(max(D_KM)) + f' km that is {STEP} classes above the largest in the own basin' + (f' (class {int(own)})' if own is not None else ' (no basin)'), na=True)
    elif big_km > USE_D:
        U['S3.3'] = no(f'the nearest much larger river is {big_km:.0f} km away (more than {USE_D})', na=True)
    else:
        nm = _name(row, 'big')
        same = _val(row, f'{p}_reach') is not None and int(row[f'{p}_reach']) == int(row['big_reach'])   # S3.1 already named this river
        if same:
            text = W.fmt('S3.3.same', {})
        else:
            text = W.fmt('S3.3.named', dict(d=_km(big_km), river=nm)) if nm else W.fmt('S3.3.unnamed', dict(d=_km(big_km)))
        U['S3.3'] = ok(text, f'own basin largest class {int(row["own_min"])}; class {int(row["big_ord"])} reach {int(row["big_reach"])}, {big_km:.1f} km, {row["big_dis"]:.0f} m3/s; '
                       + ('the same reach as S3.1; ' if same else '') + (f'named {nm}' if nm else 'unnamed'))
    return U
