"""
test_areas.py
-------------
Tests for GET /api/areas — type-dispatched areal signature (v2 sandbox).

Validation tests run without a DB.  DB-dependent tests are skipped if unavailable.

Accept-gate fixture coordinates (buffer): lat=16.8167, lon=-2.9833, radius_km=100
matches the exemplar at output/edop/surface/exemplars/02_buffer_detail.json.
"""

import json
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

FIXTURE_PATH        = Path(__file__).parent.parent / "output/edop/surface/exemplars/02_buffer_detail.json"
POLITY_FIXTURE_PATH = Path(__file__).parent.parent / "output/edop/surface/exemplars/03_polity_nsong_detail.json"
SB_FIXTURE_PATH     = Path(__file__).parent.parent / "output/edop/surface/exemplars/01_single_basin_detail.json"

# ---------------------------------------------------------------------------
# Shared app client (no DB required for validation tests)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def client():
    from app.main import app
    return TestClient(app)


# ---------------------------------------------------------------------------
# DB-backed fixtures (Timbuktu buffer, accept-gate coords)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def buf_client(db_available):
    if not db_available:
        pytest.skip("DB not available")
    from app.main import app
    return TestClient(app)


@pytest.fixture(scope="module")
def timbuktu_buffer(buf_client):
    """Lean Timbuktu buffer — accept-gate coordinates, bands A–E, detail=true."""
    r = buf_client.get(
        "/api/areas?type=buffer&lat=16.8167&lon=-2.9833&radius_km=100&bands=ABCDE&detail=true"
    )
    assert r.status_code == 200, r.text
    return r.json()


# ---------------------------------------------------------------------------
# Validation — no DB needed
# ---------------------------------------------------------------------------

class TestValidation:
    def test_missing_type(self, client):
        r = client.get("/api/areas?lat=16.8&lon=-2.9&radius_km=100")
        assert r.status_code == 422

    def test_unsupported_type(self, client):
        r = client.get("/api/areas?type=ring&lat=16.8&lon=-2.9&radius_km=100")
        assert r.status_code == 422
        assert "Unsupported type" in r.json()["detail"]

    def test_single_basin_missing_lat(self, client):
        r = client.get("/api/areas?type=single_basin&lon=-2.9")
        assert r.status_code == 422
        assert "lat" in r.json()["detail"]

    def test_single_basin_missing_lon(self, client):
        r = client.get("/api/areas?type=single_basin&lat=16.8")
        assert r.status_code == 422
        assert "lon" in r.json()["detail"]

    def test_polity_missing_polity(self, client):
        r = client.get("/api/areas?type=polity&year=1000")
        assert r.status_code == 422
        assert "polity" in r.json()["detail"]

    def test_polity_missing_year(self, client):
        r = client.get("/api/areas?type=polity&polity=Northern+Song")
        assert r.status_code == 422
        assert "year" in r.json()["detail"]

    def test_polity_not_found(self, client):
        r = client.get("/api/areas?type=polity&polity=Atlantis&year=500")
        assert r.status_code == 404

    def test_polity_wrong_year(self, client):
        r = client.get("/api/areas?type=polity&polity=Northern+Song&year=500")
        assert r.status_code == 404
        body = r.json()["detail"]
        assert "available_periods" in body

    def test_buffer_missing_lat(self, client):
        r = client.get("/api/areas?type=buffer&lon=-2.9&radius_km=100")
        assert r.status_code == 422
        assert "lat" in r.json()["detail"]

    def test_buffer_missing_lon(self, client):
        r = client.get("/api/areas?type=buffer&lat=16.8&radius_km=100")
        assert r.status_code == 422
        assert "lon" in r.json()["detail"]

    def test_buffer_missing_radius(self, client):
        r = client.get("/api/areas?type=buffer&lat=16.8&lon=-2.9")
        assert r.status_code == 422
        assert "radius_km" in r.json()["detail"]

    def test_band_t_missing_from_year(self, client):
        r = client.get(
            "/api/areas?type=buffer&lat=16.8&lon=-2.9&radius_km=100&bands=ABCDET&to_year=1100"
        )
        assert r.status_code == 422
        assert "Band T" in r.json()["detail"]

    def test_band_t_missing_to_year(self, client):
        r = client.get(
            "/api/areas?type=buffer&lat=16.8&lon=-2.9&radius_km=100&bands=ABCDET&from_year=900"
        )
        assert r.status_code == 422
        assert "Band T" in r.json()["detail"]

    def test_invalid_level(self, client):
        r = client.get(
            "/api/areas?type=buffer&lat=16.8&lon=-2.9&radius_km=100&level=4"
        )
        assert r.status_code == 400


# ---------------------------------------------------------------------------
# Payload structure — DB required
# ---------------------------------------------------------------------------

class TestBufferPayload:
    def test_top_level_keys(self, timbuktu_buffer):
        required = {"rows", "neighborhood", "shortfall", "bands", "caveats"}
        missing = required - timbuktu_buffer.keys()
        assert not missing, f"Missing top-level keys: {missing}"

    def test_neighborhood_block(self, timbuktu_buffer):
        nb = timbuktu_buffer["neighborhood"]
        assert nb["type"] == "buffer"
        assert abs(nb["lat"] - 16.8167) < 0.001
        assert abs(nb["lon"] - (-2.9833)) < 0.001
        assert nb["radius_km"] == 100
        assert nb["n_units"] > 0

    def test_row_count(self, timbuktu_buffer):
        # Accept-gate: must match the fixture (52 rows)
        assert len(timbuktu_buffer["rows"]) == 52

    def test_all_methods_present(self, timbuktu_buffer):
        methods = {r["method"] for r in timbuktu_buffer["rows"]}
        expected = {"area_weighted", "dominant_basin", "class_mixture",
                    "flag_fraction", "distribution_only", "extreme"}
        assert expected == methods

    def test_detail_distributions_present(self, timbuktu_buffer):
        aw_rows = [r for r in timbuktu_buffer["rows"] if r["method"] == "area_weighted"]
        for row in aw_rows:
            assert "detail" in row, f"Missing detail on {row['variable']}"
            assert "distribution" in row["detail"], f"Missing distribution on {row['variable']}"

    def test_no_band_t_rows_without_span(self, timbuktu_buffer):
        t_rows = [r for r in timbuktu_buffer["rows"] if r.get("band") == "T"]
        assert t_rows == [], "T rows present without Band T span — unexpected"

    def test_bands_field(self, timbuktu_buffer):
        # bands=ABCDE requested → T should not be included
        assert "T" not in timbuktu_buffer["bands"]
        for letter in "ABCDE":
            assert letter in timbuktu_buffer["bands"]


# ---------------------------------------------------------------------------
# Accept-gate equivalence — live response vs captured fixture
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def fixture_data():
    if not FIXTURE_PATH.exists():
        pytest.skip(f"Fixture not found: {FIXTURE_PATH}")
    return json.loads(FIXTURE_PATH.read_text())


class TestFixtureEquivalence:
    """Live /api/areas response must match the structure of 02_buffer_detail.json."""

    def test_same_row_count(self, timbuktu_buffer, fixture_data):
        assert len(timbuktu_buffer["rows"]) == len(fixture_data["rows"])

    def test_same_variable_list(self, timbuktu_buffer, fixture_data):
        live_vars    = [r["variable"] for r in timbuktu_buffer["rows"]]
        fixture_vars = [r["variable"] for r in fixture_data["rows"]]
        assert live_vars == fixture_vars

    def test_same_method_per_variable(self, timbuktu_buffer, fixture_data):
        live    = {r["variable"]: r["method"] for r in timbuktu_buffer["rows"]}
        fixture = {r["variable"]: r["method"] for r in fixture_data["rows"]}
        assert live == fixture

    def test_same_band_per_variable(self, timbuktu_buffer, fixture_data):
        live    = {r["variable"]: r["band"] for r in timbuktu_buffer["rows"]}
        fixture = {r["variable"]: r["band"] for r in fixture_data["rows"]}
        assert live == fixture

    def test_scores_within_tolerance(self, timbuktu_buffer, fixture_data):
        live_map    = {r["variable"]: r["representative_score"] for r in timbuktu_buffer["rows"]}
        fixture_map = {r["variable"]: r["representative_score"] for r in fixture_data["rows"]}
        mismatches = []
        for var, fix_score in fixture_map.items():
            live_score = live_map.get(var)
            if fix_score is None and live_score is None:
                continue
            if fix_score is None or live_score is None:
                mismatches.append(f"{var}: fixture={fix_score} live={live_score}")
                continue
            if abs(live_score - fix_score) > 0.5:
                mismatches.append(f"{var}: fixture={fix_score:.2f} live={live_score:.2f}")
        assert not mismatches, "Score divergence exceeds tolerance:\n" + "\n".join(mismatches)

    def test_neighborhood_matches_fixture(self, timbuktu_buffer, fixture_data):
        live_nb = timbuktu_buffer["neighborhood"]
        fix_nb  = fixture_data["neighborhood"]
        assert live_nb["type"]      == fix_nb["type"]
        assert live_nb["n_units"]   == fix_nb["n_units"]
        assert live_nb["unit_type"] == fix_nb["unit_type"]


# ---------------------------------------------------------------------------
# Polity payload — DB required
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def nsong_live(buf_client):
    """Live Northern Song polity response — accept-gate parameters."""
    r = buf_client.get(
        "/api/areas?type=polity&polity=Northern+Song&year=1000"
        "&level=6&bands=ABCDET&from_year=1000&to_year=1100&detail=true"
    )
    assert r.status_code == 200, r.text
    return r.json()


class TestPolityPayload:
    def test_top_level_keys(self, nsong_live):
        required = {"rows", "neighborhood", "shortfall", "bands", "resolver"}
        missing = required - nsong_live.keys()
        assert not missing, f"Missing top-level keys: {missing}"

    def test_resolver_block(self, nsong_live):
        res = nsong_live["resolver"]
        assert res["type"]   == "polity"
        assert res["polity"] == "Northern Song"
        assert res["year"]   == 1000

    def test_total_row_count(self, nsong_live):
        assert len(nsong_live["rows"]) == 372

    def test_band_t_row_count(self, nsong_live):
        t_rows = [r for r in nsong_live["rows"] if r.get("band") == "T"]
        assert len(t_rows) == 320

    def test_neighborhood_block(self, nsong_live):
        nb = nsong_live["neighborhood"]
        assert nb["type"]      == "polygon"
        assert nb["n_units"]   == 376
        assert nb["unit_type"] == "basin"
        assert "marginal_exposure" in nb

    def test_band_t_span_present(self, nsong_live):
        assert nsong_live.get("band_t_span") == {"from_year": 1000, "to_year": 1100}


# ---------------------------------------------------------------------------
# Polity equivalence — live vs captured fixture
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def polity_fixture_data():
    if not POLITY_FIXTURE_PATH.exists():
        pytest.skip(f"Polity fixture not found: {POLITY_FIXTURE_PATH}")
    return json.loads(POLITY_FIXTURE_PATH.read_text())


class TestPolityFixtureEquivalence:
    """Live /api/areas?type=polity must match structure of 03_polity_nsong_detail.json."""

    def test_same_row_count(self, nsong_live, polity_fixture_data):
        assert len(nsong_live["rows"]) == len(polity_fixture_data["rows"])

    def test_same_variable_list(self, nsong_live, polity_fixture_data):
        live_vars    = [r["variable"] for r in nsong_live["rows"]]
        fixture_vars = [r["variable"] for r in polity_fixture_data["rows"]]
        assert live_vars == fixture_vars

    def test_same_method_per_variable(self, nsong_live, polity_fixture_data):
        live    = {r["variable"]: r["method"] for r in nsong_live["rows"]}
        fixture = {r["variable"]: r["method"] for r in polity_fixture_data["rows"]}
        assert live == fixture

    def test_same_band_per_variable(self, nsong_live, polity_fixture_data):
        live    = {r["variable"]: r["band"] for r in nsong_live["rows"]}
        fixture = {r["variable"]: r["band"] for r in polity_fixture_data["rows"]}
        assert live == fixture

    def test_neighborhood_matches_fixture(self, nsong_live, polity_fixture_data):
        live_nb = nsong_live["neighborhood"]
        fix_nb  = polity_fixture_data["neighborhood"]
        assert live_nb["type"]      == fix_nb["type"]
        assert live_nb["n_units"]   == fix_nb["n_units"]
        assert live_nb["unit_type"] == fix_nb["unit_type"]


# ---------------------------------------------------------------------------
# Single-basin payload — DB required
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def timbuktu_single(buf_client):
    """Live single-basin Timbuktu response — accept-gate coordinates, bands A–E, detail=true."""
    r = buf_client.get(
        "/api/areas?type=single_basin&lat=16.8167&lon=-2.9833&bands=ABCDE&detail=true"
    )
    assert r.status_code == 200, r.text
    return r.json()


class TestSingleBasinPayload:
    def test_top_level_keys(self, timbuktu_single):
        required = {"rows", "neighborhood", "shortfall", "bands", "caveats"}
        missing = required - timbuktu_single.keys()
        assert not missing, f"Missing top-level keys: {missing}"

    def test_neighborhood_block(self, timbuktu_single):
        nb = timbuktu_single["neighborhood"]
        assert nb["type"]      == "basin"
        assert nb["n_units"]   == 1
        assert nb["unit_type"] == "basin"
        assert "hybas_id" in nb
        assert abs(nb["lat"] - 16.8167) < 0.001
        assert abs(nb["lon"] - (-2.9833)) < 0.001

    def test_row_count(self, timbuktu_single):
        # n=1 basin → same 52 rows as the single-basin fixture
        assert len(timbuktu_single["rows"]) == 52

    def test_shortfall_zero(self, timbuktu_single):
        assert timbuktu_single["shortfall"] == 0.0

    def test_no_band_t_rows_without_span(self, timbuktu_single):
        t_rows = [r for r in timbuktu_single["rows"] if r.get("band") == "T"]
        assert t_rows == []


# ---------------------------------------------------------------------------
# Single-basin equivalence — live vs captured fixture
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def sb_fixture_data():
    if not SB_FIXTURE_PATH.exists():
        pytest.skip(f"Single-basin fixture not found: {SB_FIXTURE_PATH}")
    return json.loads(SB_FIXTURE_PATH.read_text())


class TestSingleBasinFixtureEquivalence:
    """Live /api/areas?type=single_basin must match structure of 01_single_basin_detail.json."""

    def test_same_row_count(self, timbuktu_single, sb_fixture_data):
        assert len(timbuktu_single["rows"]) == len(sb_fixture_data["rows"])

    def test_same_variable_list(self, timbuktu_single, sb_fixture_data):
        live_vars    = [r["variable"] for r in timbuktu_single["rows"]]
        fixture_vars = [r["variable"] for r in sb_fixture_data["rows"]]
        assert live_vars == fixture_vars

    def test_same_method_per_variable(self, timbuktu_single, sb_fixture_data):
        live    = {r["variable"]: r["method"] for r in timbuktu_single["rows"]}
        fixture = {r["variable"]: r["method"] for r in sb_fixture_data["rows"]}
        assert live == fixture

    def test_same_band_per_variable(self, timbuktu_single, sb_fixture_data):
        live    = {r["variable"]: r["band"] for r in timbuktu_single["rows"]}
        fixture = {r["variable"]: r["band"] for r in sb_fixture_data["rows"]}
        assert live == fixture

    def test_scores_within_tolerance(self, timbuktu_single, sb_fixture_data):
        live_map    = {r["variable"]: r["representative_score"] for r in timbuktu_single["rows"]}
        fixture_map = {r["variable"]: r["representative_score"] for r in sb_fixture_data["rows"]}
        mismatches = []
        for var, fix_score in fixture_map.items():
            live_score = live_map.get(var)
            if fix_score is None and live_score is None:
                continue
            if fix_score is None or live_score is None:
                mismatches.append(f"{var}: fixture={fix_score} live={live_score}")
                continue
            if abs(live_score - fix_score) > 0.5:
                mismatches.append(f"{var}: fixture={fix_score:.2f} live={live_score:.2f}")
        assert not mismatches, "Score divergence exceeds tolerance:\n" + "\n".join(mismatches)

    def test_neighborhood_matches_fixture(self, timbuktu_single, sb_fixture_data):
        live_nb = timbuktu_single["neighborhood"]
        fix_nb  = sb_fixture_data["neighborhood"]
        assert live_nb["type"]      == fix_nb["type"]
        assert live_nb["n_units"]   == fix_nb["n_units"]
        assert live_nb["unit_type"] == fix_nb["unit_type"]
        assert live_nb["hybas_id"]  == fix_nb["hybas_id"]


# ---------------------------------------------------------------------------
# Single-basin Band T live smoke — verifies the polygon Band T path
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def timbuktu_single_band_t(buf_client):
    """Single-basin Timbuktu with Band T 1000–1100 CE."""
    r = buf_client.get(
        "/api/areas?type=single_basin&lat=16.8167&lon=-2.9833"
        "&bands=ABCDET&from_year=1000&to_year=1100&detail=true"
    )
    assert r.status_code == 200, r.text
    return r.json()


class TestSingleBasinBandT:
    def test_t_rows_present(self, timbuktu_single_band_t):
        t_rows = [r for r in timbuktu_single_band_t["rows"] if r.get("band") == "T"]
        assert len(t_rows) > 0, "No Band T rows returned"

    def test_lmr_rows_present(self, timbuktu_single_band_t):
        lmr_vars = {"lmr_pdsi", "lmr_air", "lmr_prate"}
        t_vars = {r["variable"] for r in timbuktu_single_band_t["rows"] if r.get("band") == "T"}
        assert lmr_vars <= t_vars, f"Missing LMR variables: {lmr_vars - t_vars}"

    def test_hyde_rows_present(self, timbuktu_single_band_t):
        hyde_vars = {"hyde_cropland", "hyde_grazing", "hyde_pasture", "hyde_rangeland"}
        t_vars = {r["variable"] for r in timbuktu_single_band_t["rows"] if r.get("band") == "T"}
        assert hyde_vars <= t_vars, f"Missing HYDE variables: {hyde_vars - t_vars}"

    def test_evolv2k_rows_present(self, timbuktu_single_band_t):
        t_vars = {r["variable"] for r in timbuktu_single_band_t["rows"] if r.get("band") == "T"}
        assert "evolv2k_vssi" in t_vars

    def test_lmr_rows_have_year(self, timbuktu_single_band_t):
        lmr_rows = [r for r in timbuktu_single_band_t["rows"]
                    if r.get("band") == "T" and r["variable"].startswith("lmr_")]
        for row in lmr_rows:
            assert "year" in row, f"LMR row missing year: {row['variable']}"
            assert row["year"] is not None

    def test_lmr_rows_have_distribution(self, timbuktu_single_band_t):
        lmr_rows = [r for r in timbuktu_single_band_t["rows"]
                    if r.get("band") == "T" and r["variable"].startswith("lmr_")]
        for row in lmr_rows:
            det = row.get("detail") or {}
            assert "distribution" in det, f"LMR row missing detail.distribution: {row['variable']} y={row.get('year')}"


# ---------------------------------------------------------------------------
# WO11 honesty check — signature hybas_id matches basin-preview containing basin
# ---------------------------------------------------------------------------

class TestSingleBasinMapHonestyCheck:
    """The basin drawn on the map must be the basin the signature describes."""

    def test_hybas_id_in_neighborhood(self, timbuktu_single):
        nb = timbuktu_single["neighborhood"]
        assert "hybas_id" in nb, "neighborhood block missing hybas_id"
        assert nb["hybas_id"] is not None

    def test_signature_id_matches_basin_preview(self, buf_client, timbuktu_single):
        sig_id = timbuktu_single["neighborhood"]["hybas_id"]
        r = buf_client.get("/api/basin-preview?lat=16.8167&lon=-2.9833&level=6")
        assert r.status_code == 200, r.text
        data = r.json()
        preview_id = data["containing_basin"]["properties"]["hybas_id"]
        assert sig_id == preview_id, (
            f"Signature resolved basin {sig_id} but basin-preview resolved {preview_id} "
            "— map and signature would describe different basins"
        )
