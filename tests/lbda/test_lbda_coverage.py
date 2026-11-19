"""reg WO-07 item 3: LBDA is judged year by year (the cells with data grow through time); the span is clipped to the years
that meet the coverage floor; a fixed-footprint source (GEDA) is judged as before."""
import pytest

from app.db.connection import db_connect
from scripts.edop.areas import engine, source_registry as sr

pytestmark = pytest.mark.lbda

CHACO, SANTA_FE, CAHOKIA, LVIV = (36.06, -107.96), (35.69, -105.94), (38.65, -90.06), (49.84, 24.03)


@pytest.fixture(scope="module")
def conn():
    c = db_connect()
    yield c
    c.close()


def _lbda(conn, place, a, b, radius_km=25):
    r = engine.aggregate_band_t(place[0], place[1], radius_km, a, b, conn)
    d = next(x for x in r.decisions if x.source_id == "lbda_v3")
    return d, [x for x in r.rows if x["variable"] == "lbda_pmdi"], r


def test_a_place_covered_from_year_0_is_covered_in_full(conn):
    d, rows, _ = _lbda(conn, CHACO, 1100, 1200)
    assert d.applied and d.span == (1100, 1200) and len(rows) == 101
    assert {r["status"] for r in rows} == {"ok"} and all(r["coverage"] == pytest.approx(1.0) for r in rows)


def test_a_partly_covered_span_is_flagged_year_by_year(conn):
    d, rows, r = _lbda(conn, SANTA_FE, 100, 300)          # the cells east of 106 W start at 210
    cov = [d.coverage_by_year[y] for y in range(100, 301)]
    assert d.applied and d.span == (100, 300) and len(rows) == 201
    assert cov == sorted(cov) and cov[0] < 0.5 <= cov[-1]       # coverage never falls
    assert rows[0]["status"] == "low_coverage" and rows[-1]["status"] == "ok"
    statuses = [x["status"] for x in rows]
    k = statuses.index("ok")
    assert set(statuses[:k]) == {"low_coverage"} and set(statuses[k:]) == {"ok"}              # low_coverage years come first, then ok
    assert "partly covered" in r.notes["lbda_v3"]


def test_years_below_the_floor_are_dropped_and_the_sources_block_says_so(conn):
    d, rows, r = _lbda(conn, CAHOKIA, 300, 1000)          # first data in the Cahokia cells: 920
    assert d.applied and d.span == (920, 1000) and rows[0]["year"] == 920 and len(rows) == 81
    block = sr.sources_block(decisions=r.decisions)
    lbda = next(e for e in block["used"] if e["id"] == "lbda_v3")
    assert lbda["years"] == {"requested": [300, 1000], "returned": [920, 1000]}


def test_a_span_with_no_covered_year_is_not_applied(conn):
    d, rows, r = _lbda(conn, CAHOKIA, 300, 800)
    assert (d.applied, d.reason, rows) == (False, "below_coverage_floor", [])
    assert any(e["id"] == "lbda_v3" and e["reason"] == "below_coverage_floor" for e in sr.sources_block(decisions=r.decisions)["not_applied"])


def test_outside_the_footprint_and_outside_the_years(conn):
    assert _lbda(conn, LVIV, 1000, 1100)[0].reason == "outside_footprint"
    assert _lbda(conn, CHACO, 2100, 2200)[0].reason == "outside_span"


def test_a_span_before_the_data_is_clipped_to_it(conn):
    d, rows, _ = _lbda(conn, CHACO, -500, 100)
    assert d.span == (0, 100) and rows[0]["year"] == 0 and len(rows) == 101


def test_a_single_cell_area_returns_the_stored_value(conn):
    wkt = "POLYGON((-107.9 36.15,-107.6 36.15,-107.6 36.35,-107.9 36.35,-107.9 36.15))"       # inside the cell centred 36.25, -107.75
    r = engine.aggregate_band_t(None, None, 0, 1100, 1103, conn, geom_wkt=wkt)
    rows = [x for x in r.rows if x["variable"] == "lbda_pmdi"]
    stored = conn.execute("select pmdi from temporal.lbda_climate where lat = 36.25 and lon = -107.75").fetchone()[0]
    assert [x["year"] for x in rows] == [1100, 1101, 1102, 1103] and all(x["n_units"] == 1 for x in rows)
    assert [x["representative_raw"] for x in rows] == pytest.approx([stored[y] for y in range(1100, 1104)], abs=1e-5)   # year y is at index y (array position y + 1)


def test_a_fixed_footprint_source_is_judged_as_before(conn):
    r = engine.aggregate_band_t(LVIV[0], LVIV[1], 25, 1000, 1100, conn)
    d = next(x for x in r.decisions if x.source_id == "geda")
    assert d.applied and d.span == (1000, 1100) and d.coverage_by_year is None and d.requested_span == (1000, 1100)
    assert not any("years" in e for e in sr.sources_block(decisions=r.decisions)["used"])        # nothing was clipped


def test_the_public_value_of_a_year_uses_only_the_cells_that_have_it(conn):
    d, rows, _ = _lbda(conn, SANTA_FE, 150, 150)
    assert rows[0]["n_units"] < 4 and rows[0]["coverage"] < 0.5          # early year: only the cells with data count
