"""
test_area.py
------------
Tests for GET /api/area — areal signature for a named Cliopatria polity.

All DB-hitting tests are skipped if the DB is unavailable.

The N Song fixture is module-scoped (engine runs over 376 basins; run once).
Band T tests are separate: they request from_year/to_year and are also module-scoped.
"""

import pytest
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def client(db_available):
    if not db_available:
        pytest.skip("DB not available")
    from app.main import app
    return TestClient(app)


@pytest.fixture(scope="module")
def nsong_lean(client):
    """Lean N Song response (no Band T, no detail)."""
    r = client.get("/api/area?polity=Northern+Song&year=1000&level=6&bands=ABCDE")
    assert r.status_code == 200, r.text
    return r.json()


@pytest.fixture(scope="module")
def nsong_detail(client):
    """N Song with detail=true and Band T 900–1100 CE."""
    r = client.get(
        "/api/area?polity=Northern+Song&year=1000&level=6"
        "&bands=ABCDET&from_year=900&to_year=1100&detail=true"
    )
    assert r.status_code == 200, r.text
    return r.json()


# ---------------------------------------------------------------------------
# Basic payload structure
# ---------------------------------------------------------------------------

def test_lean_top_level_keys(nsong_lean):
    required = {"rows", "neighborhood", "shortfall", "bands", "resolver"}
    missing = required - nsong_lean.keys()
    assert not missing, f"Missing top-level keys: {missing}"


def test_lean_resolver_block(nsong_lean):
    res = nsong_lean["resolver"]
    assert res["type"]   == "polity"
    assert res["polity"] == "Northern Song"
    assert res["year"]   == 1000
    assert res["fromyear"] <= 1000 <= res["toyear"]


def test_lean_neighborhood_type(nsong_lean):
    nb = nsong_lean["neighborhood"]
    assert nb["type"]      == "polygon"
    assert nb["level"]     == 6
    assert nb["unit_type"] == "basin"


def test_lean_basin_count(nsong_lean):
    # WO20 established N Song = 376 basins at L06
    assert nsong_lean["neighborhood"]["n_units"] == 376


def test_lean_shortfall_low(nsong_lean):
    # WO20: shortfall=0.011
    assert nsong_lean["shortfall"] < 0.02


def test_lean_row_count(nsong_lean):
    # 52 basin rows (B1–B5; reservoir_vol is the 52nd, added WO14)
    rows = nsong_lean["rows"]
    assert len(rows) == 52


def test_lean_row_envelope(nsong_lean):
    required = {"variable", "method", "status", "representative_score"}
    for row in nsong_lean["rows"]:
        missing = required - row.keys()
        assert not missing, f"Row {row.get('variable')} missing: {missing}"


# ---------------------------------------------------------------------------
# Dominant basin (B2 — Yangtze should dominate)
# ---------------------------------------------------------------------------

def test_yangtze_dominant(nsong_lean):
    b2_rows = [r for r in nsong_lean["rows"] if r["method"] == "dominant_basin"]
    assert b2_rows, "No B2 dominant_basin rows found"
    # Yangtze main-stem: representative_score ~99.7th pct globally
    scores = [r["representative_score"] for r in b2_rows if r["representative_score"] is not None]
    assert all(s > 95 for s in scores), f"B2 scores unexpectedly low: {scores}"


# ---------------------------------------------------------------------------
# Lean vs detail gating
# ---------------------------------------------------------------------------

def test_lean_no_distribution(nsong_lean):
    for row in nsong_lean["rows"]:
        detail_block = row.get("detail") or {}
        assert "distribution" not in detail_block, (
            f"distribution present in lean row {row['variable']}"
        )


def test_detail_has_distributions(nsong_detail):
    # At least basin rows (B1) should carry distribution objects
    basin_rows = [r for r in nsong_detail["rows"] if r.get("band") != "T"]
    b1_rows = [r for r in basin_rows if r.get("method") == "area_weighted"]
    detail_with_dist = [
        r for r in b1_rows
        if (r.get("detail") or {}).get("distribution") is not None
    ]
    assert len(detail_with_dist) > 0, "No B1 rows carry a distribution in detail mode"


def test_detail_distribution_shape(nsong_detail):
    b1_rows = [r for r in nsong_detail["rows"] if r.get("method") == "area_weighted"]
    for row in b1_rows:
        dist = (row.get("detail") or {}).get("distribution")
        if dist is None:
            continue
        assert "bins"     in dist
        assert "weights"  in dist
        assert "n_units"  in dist
        assert "min"      in dist
        assert "p10"      in dist
        assert "p90"      in dist
        assert dist["unit_type"] == "basin"
        assert dist["low_resolution"] is False   # 376 basins — never low-res


# ---------------------------------------------------------------------------
# Band T presence and temporal stamp
# ---------------------------------------------------------------------------

def test_detail_has_band_t_rows(nsong_detail):
    t_rows = [r for r in nsong_detail["rows"] if r.get("band") == "T"]
    assert len(t_rows) > 0, "No Band T rows in detail response"


def test_detail_band_t_span_in_payload(nsong_detail):
    assert "band_t_span" in nsong_detail
    span = nsong_detail["band_t_span"]
    assert span["from_year"] == 900
    assert span["to_year"]   == 1100


def test_detail_resolver_year_in_histogram_stamp(nsong_detail):
    t_rows = [r for r in nsong_detail["rows"] if r.get("band") == "T"]
    for row in t_rows:
        dist = (row.get("detail") or {}).get("distribution")
        if dist is None:
            continue
        assert dist.get("resolver_year") == 1000
        assert dist.get("band_t_from")   == 900
        assert dist.get("band_t_to")     == 1100


# ---------------------------------------------------------------------------
# Two-axis independence: resolver year ≠ Band T span
# ---------------------------------------------------------------------------

def test_two_axis_independence(client):
    """year=1000 (boundary) with Band T 1200–1300 (different window) should work."""
    r = client.get(
        "/api/area?polity=Northern+Song&year=1000&level=6"
        "&bands=ABCDET&from_year=1200&to_year=1300&detail=true"
    )
    assert r.status_code == 200
    data = r.json()
    assert data["resolver"]["year"] == 1000
    assert data["band_t_span"]["from_year"] == 1200
    assert data["band_t_span"]["to_year"]   == 1300
    # Histogram stamps should reflect the Band T window, not resolver year
    t_rows = [r2 for r2 in data["rows"] if r2.get("band") == "T"]
    for row in t_rows:
        dist = (row.get("detail") or {}).get("distribution")
        if dist is None:
            continue
        assert dist.get("resolver_year") == 1000
        assert dist.get("band_t_from")   == 1200
        assert dist.get("band_t_to")     == 1300


# ---------------------------------------------------------------------------
# 404 paths
# ---------------------------------------------------------------------------

def test_404_unknown_polity(client):
    r = client.get("/api/area?polity=Atlantis&year=500")
    assert r.status_code == 404
    assert "Atlantis" in r.text


def test_404_name_exists_wrong_year(client):
    # Northern Song existed ~960–1127 CE; year 500 should be 404 with available_periods
    r = client.get("/api/area?polity=Northern+Song&year=500")
    assert r.status_code == 404
    data = r.json()
    detail = data.get("detail", {})
    assert "available_periods" in detail, "Expected available_periods in 404 detail"
    periods = detail["available_periods"]
    assert len(periods) > 0
    for p in periods:
        assert "fromyear" in p and "toyear" in p


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def test_bad_level_rejected(client):
    r = client.get("/api/area?polity=Northern+Song&year=1000&level=4")
    assert r.status_code == 400
