"""Load the GEDA grid into temporal.geda_climate (the local database; loading the server is a separate step).

Source: data/geda/geda_trim.nc, the authors' trimmed distribution of the Great Eurasian Drought Atlas
(Cook et al. 2024; Zenodo 10.5281/zenodo.11059894; CC BY 4.0). Shape follows temporal.lmr_climate: one row per
0.5 degree cell, the annual series as a real[] (here scpdsi, position k is the year 999 + k), a point geom, plus the
cell box and its area as in temporal.hyde_cells. The file stores the netCDF default fill value (9.969e+36) as data;
it is masked here, and only cells with values are stored.

    python scripts/edop/regionality/load_geda.py --dry-run     # checks the file, writes nothing
    python scripts/edop/regionality/load_geda.py               # creates the table (refuses if it already has rows)
    python scripts/edop/regionality/load_geda.py --replace     # drops and reloads the table
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

NC = ROOT / 'data' / 'geda' / 'geda_trim.nc'
MD5 = 'b05338614a43627b43acb878d860fb6a'           # the md5 Zenodo publishes for geda_trim.nc
TABLE = 'temporal.geda_climate'
EXPECTED_CELLS, N_YEARS, YEAR0 = 28970, 1021, 1000
COMMENT = ("GEDA (Great Eurasian Drought Atlas), trimmed distribution geda_trim.nc: JJA scPDSI as z-scores (mean 0, SD 1 per "
           "cell over 1000-2020 CE), 0.5 degree grid, 28,970 cells with values (sub-Saharan Africa and everything south of "
           "the equator removed). scpdsi[k] is year 999+k (k=1 is 1000 CE, 1021 values); 1990-2020 are observed CRU TS 4.06, "
           "not reconstructed. lon is -180..180 (lmr_climate uses 0..360). cell_geom is the 0.5 degree box. "
           "Cook et al. 2024, doi 10.1175/JCLI-D-23-0773.1; data doi 10.5281/zenodo.11059894; CC BY 4.0. "
           "Loaded by scripts/edop/regionality/load_geda.py.")


def read_grid():
    """Return (lat, lon, years, G) with the fill value masked; G is (years, lat, lon) float64."""
    md5 = hashlib.md5(NC.read_bytes()).hexdigest()
    if md5 != MD5:
        sys.exit(f'md5 mismatch for {NC.name}: {md5} (expected {MD5})')
    ds = xr.open_dataset(NC, decode_times=False, mask_and_scale=False)
    G = ds['scPDSI'].values.astype('float64')
    G[G > 1e30] = np.nan
    years = ds['yr'].values.astype(int)
    assert years[0] == YEAR0 and len(years) == N_YEARS and (np.diff(years) == 1).all(), 'unexpected year axis'
    return ds['lat'].values, ds['lon'].values, years, G


def cells(lat, lon, G):
    """Rows for cells with values: (lat, lon, series). Every valid cell must have a value in every year."""
    fin = np.isfinite(G)
    valid = fin.any(axis=0)
    assert (fin[:, valid]).all(), 'a cell has values in some years only'
    ii, jj = np.nonzero(valid)
    order = np.lexsort((lon[jj], lat[ii]))
    return [(float(lat[ii[k]]), float(lon[jj[k]]), G[:, ii[k], jj[k]]) for k in order]


def array_text(series):
    return '{' + ','.join(f'{v:.7g}' for v in series) + '}'


def load(rows, replace):
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
        id         serial primary key,
        lat        real not null,
        lon        real not null,
        scpdsi     real[] not null,
        geom       geometry(Point, 4326),
        cell_geom  geometry(Polygon, 4326),
        area_km2   real)""")
    with cur.copy(f'copy {TABLE} (lat, lon, scpdsi) from stdin') as cp:
        for la, lo, s in rows:
            cp.write_row((la, lo, array_text(s)))
    cur.execute(f"""update {TABLE} set
        geom = ST_SetSRID(ST_MakePoint(lon, lat), 4326),
        cell_geom = ST_MakeEnvelope(lon - 0.25, lat - 0.25, lon + 0.25, lat + 0.25, 4326)""")
    cur.execute(f'update {TABLE} set area_km2 = ST_Area(cell_geom::geography) / 1e6')
    cur.execute(f'create index geda_climate_geom_idx on {TABLE} using gist (geom)')
    cur.execute(f'create index geda_climate_cell_geom_idx on {TABLE} using gist (cell_geom)')
    cur.execute(f'create index geda_climate_latlon_idx on {TABLE} (lat, lon)')
    cur.execute(sql.SQL('comment on table {} is {}').format(sql.SQL(TABLE), sql.Literal(COMMENT)))
    conn.commit()
    cur.execute(f'analyze {TABLE}')
    conn.commit()
    return conn


def check(conn, lat, lon, G):
    """Part A item 4: cell count, year range, value range, spot values for the Kyiv and Tbilisi cells."""
    cur = conn.cursor()
    cur.execute(f'select count(*), min(array_length(scpdsi, 1)), max(array_length(scpdsi, 1)), '
                f'min(lat), max(lat), min(lon), max(lon), pg_size_pretty(pg_total_relation_size(%s)) from {TABLE}', (TABLE,))
    n, a0, a1, la0, la1, lo0, lo1, size = cur.fetchone()
    cur.execute(f'select min(v), max(v), avg(v), stddev_pop(v) from (select unnest(scpdsi) v from {TABLE}) t')
    vmin, vmax, vavg, vsd = cur.fetchone()
    out = [f'{TABLE}: {n:,} cells (file: {EXPECTED_CELLS:,}); series length {a0} to {a1} (years {YEAR0} to {YEAR0 + a1 - 1}); '
           f'lat {la0} to {la1}, lon {lo0} to {lo1}; size {size}',
           f'values over all cells and years: min {vmin:.3f}, max {vmax:.3f}, mean {vavg:.4f}, SD {vsd:.4f} (file after masking: '
           f'min {np.nanmin(G):.3f}, max {np.nanmax(G):.3f})']
    for name, (y, x) in {'Kyiv': (50.4547, 30.5238), 'Tbilisi': (41.7151, 44.8271)}.items():
        cur.execute(f'select lat, lon, scpdsi from {TABLE} order by '
                    f'ST_Distance(geom::geography, ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography) limit 1', (x, y))
        la, lo, s = cur.fetchone()
        i, j = int(np.argmin(np.abs(lat - la))), int(np.argmin(np.abs(lon - lo)))
        ref = G[:, i, j]
        ok = np.allclose(np.array(s, dtype=float), ref, atol=1e-5)
        out.append(f'{name}: cell ({la}, {lo}); stored equals file within 1e-5: {ok}; first values {[round(v, 3) for v in s[:3]]} '
                   f'vs file {[round(v, 3) for v in ref[:3]]}; 2010: stored {s[2010 - YEAR0]:.3f}, file {ref[2010 - YEAR0]:.3f}')
    rng = np.random.default_rng(0)
    cur.execute(f'select lat, lon, scpdsi from {TABLE} order by random() limit 300')
    bad = 0
    for la, lo, s in cur.fetchall():
        i, j = int(np.argmin(np.abs(lat - la))), int(np.argmin(np.abs(lon - lo)))
        bad += not np.allclose(np.array(s, dtype=float), G[:, i, j], atol=1e-5)
    out.append(f'300 random cells compared with the file: {bad} differ')
    cur.execute('select obj_description(%s::regclass, %s)', (TABLE, 'pg_class'))
    out.append(f'table comment set: {cur.fetchone()[0] is not None}')
    return '\n'.join(out)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--replace', action='store_true')
    a = ap.parse_args()
    lat, lon, years, G = read_grid()
    rows = cells(lat, lon, G)
    print(f'file ok (md5 matches); {len(rows):,} cells with values, {len(years)} years {years[0]} to {years[-1]}')
    if len(rows) != EXPECTED_CELLS:
        sys.exit(f'expected {EXPECTED_CELLS:,} cells')
    if a.dry_run:
        print('dry run: nothing written')
    else:
        conn = load(rows, a.replace)
        print(check(conn, lat, lon, G))
