"""temporal.lbda_climate (reg WO-07 item 1): loaded from data/lbda_v3/LBDA-v3.nc; the table matches the file."""
from pathlib import Path

import numpy as np
import pytest
import xarray as xr

from app.db.connection import db_connect

# netCDF4 (1.7.4) is built against an older numpy C header than the numpy 2.4 here; importing it warns "ndarray size changed".
# Harmless: the extension only reads arrays, and the values this file compares against the table match to 1e-5.
pytestmark = [pytest.mark.lbda, pytest.mark.filterwarnings("ignore:numpy.ndarray size changed:RuntimeWarning")]

NC = Path(__file__).resolve().parents[2] / "data" / "lbda_v3" / "LBDA-v3.nc"


@pytest.fixture(scope="module")
def conn():
    c = db_connect()
    yield c
    c.close()


@pytest.fixture(scope="module")
def grid():
    ds = xr.open_dataset(NC, decode_times=False)
    return ds["lat"].values, ds["lon"].values, ds["PMDI"].transpose("time", "lat", "lon").values.astype(float)


def _series(conn, lat, lon):
    r = conn.execute("select first_year, pmdi from temporal.lbda_climate where lat = %s and lon = %s", (lat, lon)).fetchone()
    return r[0], np.array([np.nan if v is None else v for v in r[1]], dtype=float)


def test_cells_and_series_length_match_the_file(conn, grid):
    lat, lon, G = grid
    n, lo, hi = conn.execute("select count(*), min(array_length(pmdi, 1)), max(array_length(pmdi, 1)) from temporal.lbda_climate").fetchone()
    assert n == int(np.isfinite(G).any(axis=0).sum()) and lo == hi == G.shape[0]


def test_values_are_the_files_and_null_before_a_cells_first_year(conn, grid):
    lat, lon, G = grid
    for la, lo in [(36.25, -107.75), (35.75, -105.75), (38.75, -90.25), (42.25, -71.25)]:   # Chaco, Santa Fe, Cahokia, Boston cells
        fy, s = _series(conn, la, lo)
        ref = G[:, int(np.argmin(abs(lat - la))), int(np.argmin(abs(lon - lo)))]
        assert np.allclose(s, ref, atol=1e-5, equal_nan=True)
        assert np.isnan(s[:fy]).all() and np.isfinite(s[fy:]).all()


def test_first_years_of_named_cells(conn):
    assert [_series(conn, la, lo)[0] for la, lo in [(36.25, -107.75), (35.75, -105.75), (38.75, -90.25)]] == [0, 210, 920]


@pytest.mark.parametrize("year,cells", [(0, 722), (300, 1098), (1000, 2983), (1473, 3277)])
def test_cells_with_data_grow_through_time(conn, year, cells):
    assert conn.execute("select count(*) from temporal.lbda_climate where first_year <= %s", (year,)).fetchone()[0] == cells


def test_geometry_columns_and_indexes(conn):
    assert conn.execute("select count(*) from temporal.lbda_climate where geom is null or cell_geom is null or area_km2 is null").fetchone()[0] == 0
    idx = {r[0] for r in conn.execute("select indexname from pg_indexes where schemaname = 'temporal' and tablename = 'lbda_climate'")}
    assert {"lbda_climate_geom_idx", "lbda_climate_cell_geom_idx", "lbda_climate_latlon_idx"} <= idx
