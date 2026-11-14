"""GEDA in Band T on the engine path (regionality WO-05): rows, decisions, and the cases of the WO-02 notebook.

Runs engine.aggregate_band_t against the local database (temporal.geda_climate must be loaded).
"""
import pytest

from app.db.connection import db_connect
from scripts.edop.areas.engine import aggregate_band_t

KYIV, EDGE, SPARSE = 2060448220, 1060044120, 1060264990   # L6 basins: fully inside GEDA, coverage 0.498, coverage 0.067


@pytest.fixture(scope='module')
def conn():
    with db_connect() as c:
        yield c


def wkt_of(conn, hybas_id):
    return conn.execute('SELECT ST_AsText(geom) FROM public.basin06 WHERE hybas_id = %s', (hybas_id,)).fetchone()[0]


def band_t(conn, hybas_id, from_year, to_year, **kw):
    return aggregate_band_t(0, 0, 0, from_year, to_year, conn, geom_wkt=wkt_of(conn, hybas_id), **kw)


def geda_rows(result):
    return [r for r in result.rows if r['variable'] == 'geda_scpdsi']


def decision(result, source_id='geda'):
    return next(d for d in result.decisions if d.source_id == source_id)


def test_kyiv_basin_1350_matches_the_wo02_notebook(conn):
    res = band_t(conn, KYIV, 1350, 1350)
    (row,) = geda_rows(res)
    dist = row['detail']['distribution']
    assert row['representative_raw'] == pytest.approx(-0.408, abs=6e-4)
    assert dist['p10'] == pytest.approx(-0.567, abs=6e-4)
    assert dist['p90'] == pytest.approx(-0.261, abs=6e-4)
    assert (row['n_units'], row['detail']['w_eff']) == (27, 14.25)
    assert (row['status'], row['year'], row['unit_type'], row['units']) == ('ok', 1350, 'geda_cell', 'SD (z-score)')
    assert row['coverage'] == pytest.approx(1.0, abs=1e-3)
    assert row['caveat'] == ['geda_caveat']


def test_a_geda_row_reads_like_an_lmr_row(conn):
    res = band_t(conn, KYIV, 1350, 1350)
    (g,) = geda_rows(res)
    lmr = next(r for r in res.rows if r['variable'] == 'lmr_pdsi')
    assert set(g) == set(lmr)
    assert (g['method'], g['band'], g['representative_score']) == (lmr['method'], lmr['band'], None)
    assert set(g['detail']['distribution']) == set(lmr['detail']['distribution'])
    assert set(g['detail']) - set(lmr['detail']) == {'w_eff'}       # the one addition: the effective cell count


def test_geda_rows_come_last_so_existing_row_order_is_unchanged(conn):
    res = band_t(conn, KYIV, 1350, 1350)
    variables = [r['variable'] for r in res.rows]
    first_geda = variables.index('geda_scpdsi')
    assert all(v == 'geda_scpdsi' for v in variables[first_geda:])
    assert [d.source_id for d in res.decisions] == ['hyde_3_5', 'lmr_v2_1', 'evolv2k_v4', 'geda']


def test_a_place_outside_the_footprint_gets_no_rows_and_a_reason(conn):
    res = aggregate_band_t(36.06, -107.96, 10, 1300, 1400, conn)        # Chaco Canyon
    assert geda_rows(res) == []
    d = decision(res)
    assert (d.applied, d.reason) == (False, 'outside_footprint')
    assert any(r['variable'] == 'lmr_pdsi' for r in res.rows)             # the global sources still answer


def test_an_edge_basin_returns_rows_flagged_low_coverage(conn):
    res = band_t(conn, EDGE, 1350, 1350)
    (row,) = geda_rows(res)
    assert row['status'] == 'low_coverage'
    assert row['coverage'] == pytest.approx(0.498, abs=0.005)
    assert res.notes['geda'] == 'covers 49.8% of the area'


def test_a_basin_below_the_coverage_floor_gets_no_rows(conn):
    res = band_t(conn, SPARSE, 1350, 1350)
    assert geda_rows(res) == []
    assert decision(res).reason == 'below_coverage_floor'
    assert 'geda' not in res.notes


def test_a_span_before_the_data_is_outside_span(conn):
    res = band_t(conn, KYIV, 500, 900)
    assert geda_rows(res) == []
    assert decision(res).reason == 'outside_span'


def test_a_span_straddling_the_start_returns_only_the_years_covered(conn):
    res = band_t(conn, KYIV, 980, 1010)
    assert [r['year'] for r in geda_rows(res)] == list(range(1000, 1011))


def test_observed_years_carry_the_observed_caveat_from_1990(conn):
    res = band_t(conn, KYIV, 1985, 1995)
    by_year = {r['year']: r['caveat'] for r in geda_rows(res)}
    assert all('geda_caveat' in c for c in by_year.values())
    assert [y for y, c in by_year.items() if 'geda_observed' in c] == list(range(1990, 1996))


def test_a_span_to_2020_ends_at_2020(conn):
    res = band_t(conn, KYIV, 2015, 2030)
    assert [r['year'] for r in geda_rows(res)] == list(range(2015, 2021))


def test_excluding_geda_from_permitted_leaves_the_other_rows_unchanged(conn):
    everything = band_t(conn, KYIV, 1350, 1350)
    without = band_t(conn, KYIV, 1350, 1350, permitted={'hyde_3_5', 'lmr_v2_1', 'evolv2k_v4'})
    assert geda_rows(without) == []
    assert decision(without).reason == 'not_permitted'
    expected = [r for r in everything.rows if r['variable'] != 'geda_scpdsi']
    # Compared by identity and value to tolerance: the HYDE query does not fix cell order, so sums can differ in the last digits.
    assert [(r['variable'], r['year'], r['n_units'], r['status']) for r in without.rows] == \
           [(r['variable'], r['year'], r['n_units'], r['status']) for r in expected]
    assert [r['representative_raw'] for r in without.rows] == pytest.approx([r['representative_raw'] for r in expected])


def test_a_buffer_runs_the_same_block_as_a_basin(conn):
    res = aggregate_band_t(50.4547, 30.5238, 100, 1300, 1400, conn)      # Kyiv, 100 km buffer
    rows = geda_rows(res)
    assert [r['year'] for r in rows] == list(range(1300, 1401))
    assert rows[0]['n_units'] > 1 and decision(res).applied
