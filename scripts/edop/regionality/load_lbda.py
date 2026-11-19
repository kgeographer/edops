"""Load the LBDA v3 grid into temporal.lbda_climate (the local database; loading the server is a separate step).

Source: data/lbda_v3/LBDA-v3.nc, the Living Blended Drought Atlas version 3 (NOAA NCEI study 22454; Cook et al. 2010,
doi 10.1002/jqs.1303; dataset doi 10.25921/7xm8-jn36): June-August Palmer Modified Drought Index for the contiguous US on a
0.5 degree grid, year 0 to the latest year in the file (NCEI extends it every year, so the years are read from the file).
Shape follows temporal.geda_climate: one row per cell with data, the annual series as a real[] (position k is year k-1),
a point geom, the cell box and its area. Unlike GEDA the grid is not complete in early years: the cells with data grow
from 722 in year 0 to 3,277 by 1473. The array holds NULL before a cell's first year, and first_year records it. Notes:
data/lbda_v3/LBDA-v3_characterization.md.

    python scripts/edop/regionality/load_lbda.py --dry-run     # checks the file, writes nothing
    python scripts/edop/regionality/load_lbda.py               # creates the table (refuses if it already has rows)
    python scripts/edop/regionality/load_lbda.py --replace     # drops and reloads the table
"""
import argparse
import hashlib
import sys
from pathlib import Path

import numpy as np
import xarray as xr
from psycopg import sql

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from scripts.shared.db_utils import db_connect  # noqa: E402

NC = ROOT / 'data' / 'lbda_v3' / 'LBDA-v3.nc'
TABLE = 'temporal.lbda_climate'


def read_grid():
    """Return (lat, lon, years, G, md5) with G (years, lat, lon) float64, NaN where the file has no value."""
    md5 = hashlib.md5(NC.read_bytes()).hexdigest()
    ds = xr.open_dataset(NC, decode_times=False)
    years = ds['time'].values.astype(int)
    assert years[0] == 0 and (np.diff(years) == 1).all(), 'unexpected year axis (expected annual from 0)'
    G = ds['PMDI'].transpose('time', 'lat', 'lon').values.astype('float64')
    return ds['lat'].values, ds['lon'].values, years, G, md5


def cells(lat, lon, G):
    """Rows for cells with data: (lat, lon, first_year, series). Each cell's values must run without a gap from its first year to the last."""
    fin = np.isfinite(G)
    valid = fin.any(axis=0)
    first = np.where(valid, fin.argmax(axis=0), -1)
    ii, jj = np.nonzero(valid)
    for i, j in zip(ii, jj):
        f = first[i, j]
        assert fin[f:, i, j].all() and not fin[:f, i, j].any(), f'cell ({lat[i]}, {lon[j]}) has a gap after its first year'
    order = np.lexsort((lon[jj], lat[ii]))
    return [(float(lat[ii[k]]), float(lon[jj[k]]), int(first[ii[k], jj[k]]), G[:, ii[k], jj[k]]) for k in order]


def array_text(series):
    return '{' + ','.join('NULL' if np.isnan(v) else f'{v:.7g}' for v in series) + '}'


def comment(n_cells, years, md5):
    return (f"LBDA (Living Blended Drought Atlas) version 3, LBDA-v3.nc: JJA Palmer Modified Drought Index (PMDI), not "
            f"standardized, contiguous US, 0.5 degree grid, {n_cells:,} cells with data. pmdi[k] is year k-1 (k=1 is year "
            f"{years[0]}, {len(years):,} values to {years[-1]}); NULL before a cell's first_year (cells with data grow from "
            f"722 in year 0 to all by 1473). Reconstructed 0-1899, instrumental (NClimGrid) 1900 onward. lon is -180..180. "
            f"cell_geom is the 0.5 degree box. Cook et al. 2010, doi 10.1002/jqs.1303; Gille, Morrill, Wahl, Vose, Cook, NOAA "
            f"NCEI, dataset doi 10.25921/7xm8-jn36; cite with the access date. File md5 {md5}. "
            f"Loaded by scripts/edop/regionality/load_lbda.py.")


def load(rows, years, md5, replace):
    conn = db_connect()
    cur = conn.cursor()
    cur.execute("select to_regclass(%s)", (TABLE,))
    if cur.fetchone()[0] is not None:
        cur.execute(f'select count(*) from {TABLE}')
        n = cur.fetchone()[0]
        if n and not replace:
            sys.exit(f'{TABLE} already has {n:,} rows; use --replace to drop and reload')
        cur.execute(f'drop table {TABLE}')
    cur.execute(f"""create table {TABLE} (
        id          serial primary key,
        lat         real not null,
        lon         real not null,
        first_year  integer not null,
        pmdi        real[] not null,
        geom        geometry(Point, 4326),
        cell_geom   geometry(Polygon, 4326),
        area_km2    real)""")
    with cur.copy(f'copy {TABLE} (lat, lon, first_year, pmdi) from stdin') as cp:
        for la, lo, f, s in rows:
            cp.write_row((la, lo, f, array_text(s)))
    cur.execute(f"""update {TABLE} set
        geom = ST_SetSRID(ST_MakePoint(lon, lat), 4326),
        cell_geom = ST_MakeEnvelope(lon - 0.25, lat - 0.25, lon + 0.25, lat + 0.25, 4326)""")
    cur.execute(f'update {TABLE} set area_km2 = ST_Area(cell_geom::geography) / 1e6')
    cur.execute(f'create index lbda_climate_geom_idx on {TABLE} using gist (geom)')
    cur.execute(f'create index lbda_climate_cell_geom_idx on {TABLE} using gist (cell_geom)')
    cur.execute(f'create index lbda_climate_latlon_idx on {TABLE} (lat, lon)')
    cur.execute(sql.SQL('comment on table {} is {}').format(sql.SQL(TABLE), sql.Literal(comment(len(rows), years, md5))))
    conn.commit()
    cur.execute(f'analyze {TABLE}')
    conn.commit()
    return conn


def _cell(lat, lon, la, lo):
    return int(np.argmin(np.abs(lat - la))), int(np.argmin(np.abs(lon - lo)))


def check(conn, lat, lon, years, G):
    """Cell count, series length, first years, value counts and range, spot cells and 300 random cells against the file, the per-year cell counts."""
    cur = conn.cursor()
    cur.execute(f'select count(*), min(array_length(pmdi, 1)), max(array_length(pmdi, 1)), min(first_year), max(first_year), '
                f'min(lat), max(lat), min(lon), max(lon), pg_size_pretty(pg_total_relation_size(%s)) from {TABLE}', (TABLE,))
    n, a0, a1, f0, f1, la0, la1, lo0, lo1, size = cur.fetchone()
    fin = np.isfinite(G)
    out = [f'{TABLE}: {n:,} cells (file: {int(fin.any(axis=0).sum()):,}); series length {a0} to {a1} (years {years[0]} to {years[-1]}, '
           f'file {len(years)}); first_year {f0} to {f1}; lat {la0} to {la1}, lon {lo0} to {lo1}; size {size}']
    cur.execute(f'select count(v), min(v), max(v), avg(v), stddev_pop(v), count(*) filter (where v = 0) '
                f'from (select unnest(pmdi) v from {TABLE}) t')
    c, vmin, vmax, vavg, vsd, zeros = cur.fetchone()
    out.append(f'non-NULL values {c:,} (file {int(fin.sum()):,}); min {vmin:.3f}, max {vmax:.3f}, mean {vavg:.4f}, SD {vsd:.4f} '
               f'(file: min {np.nanmin(G):.3f}, max {np.nanmax(G):.3f}, mean {np.nanmean(G):.4f}, SD {np.nanstd(G):.4f}); exact zeros {zeros}')
    spots = {'Four Corners cell (37.0, -109.05)': (37.0, -109.05), 'Chaco (36.06, -107.96)': (36.06, -107.96),
             'Albuquerque (35.08, -106.65)': (35.08, -106.65), 'Santa Fe (35.69, -105.94)': (35.69, -105.94),
             'Cahokia (38.65, -90.06)': (38.65, -90.06), 'Boston (42.36, -71.06)': (42.36, -71.06)}
    for name, (y, x) in spots.items():
        cur.execute(f'select lat, lon, first_year, pmdi from {TABLE} order by '
                    f'ST_Distance(geom::geography, ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography) limit 1', (x, y))
        la, lo, fy, s = cur.fetchone()
        i, j = _cell(lat, lon, la, lo)
        ref = G[:, i, j]
        s = np.array([np.nan if v is None else v for v in s], dtype=float)
        ok = np.allclose(s, ref, atol=1e-5, equal_nan=True)
        out.append(f'{name}: cell ({la}, {lo}); first_year {fy}; stored equals file within 1e-5 (NULL = no value): {ok}; '
                   f'year {fy}: stored {s[fy]:.3f}, file {ref[fy]:.3f}' + (f'; year {fy - 1}: stored NULL: {np.isnan(s[fy - 1])}' if fy else ''))
    cur.execute(f'select lat, lon, pmdi from {TABLE} order by random() limit 300')
    bad = 0
    for la, lo, s in cur.fetchall():
        i, j = _cell(lat, lon, la, lo)
        s = np.array([np.nan if v is None else v for v in s], dtype=float)
        bad += not np.allclose(s, G[:, i, j], atol=1e-5, equal_nan=True)
    out.append(f'300 random cells compared with the file: {bad} differ')
    pairs = []
    for y in (0, 299, 300, 500, 1000, 1473, int(years[-1])):
        cur.execute(f'select count(*) from {TABLE} where first_year <= %s', (y,))
        pairs.append((y, cur.fetchone()[0], int(fin[y].sum())))
    out.append('cells with data by year, table vs file: ' + '; '.join(f'{y}: {a} vs {b}' for y, a, b in pairs))
    cur.execute('select obj_description(%s::regclass, %s)', (TABLE, 'pg_class'))
    out.append(f'table comment set: {cur.fetchone()[0] is not None}')
    return '\n'.join(out)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--replace', action='store_true')
    a = ap.parse_args()
    lat, lon, years, G, md5 = read_grid()
    rows = cells(lat, lon, G)
    print(f'file ok; md5 {md5}; {len(rows):,} cells with data, {len(years)} years {years[0]} to {years[-1]}; every cell is gap-free from its first year')
    if a.dry_run:
        print('dry run: nothing written')
    else:
        conn = load(rows, years, md5, a.replace)
        print(check(conn, lat, lon, years, G))
