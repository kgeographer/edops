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

    def test_basin_ring_missing_lat(self, client):
        r = client.get("/api/areas?type=basin_ring&lon=-2.9")
        assert r.status_code == 422
        assert "lat" in r.json()["detail"]

    def test_basin_ring_missing_lon(self, client):
        r = client.get("/api/areas?type=basin_ring&lat=16.8")
        assert r.status_code == 422
        assert "lon" in r.json()["detail"]

    def test_ring_topology_missing_lat(self, client):
        r = client.get("/api/basin/ring?lon=-2.9")
        assert r.status_code == 422

    def test_ring_topology_missing_lon(self, client):
        r = client.get("/api/basin/ring?lat=16.8")
        assert r.status_code == 422


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


# ---------------------------------------------------------------------------
# WO12 — buffer member_ids + /api/basin/geom route
# ---------------------------------------------------------------------------

class TestBufferMemberIds:
    """Buffer neighborhood must expose member_ids for map draw."""

    def test_member_ids_present(self, timbuktu_buffer):
        nb = timbuktu_buffer["neighborhood"]
        assert "member_ids" in nb, "neighborhood missing member_ids"

    def test_member_ids_is_list(self, timbuktu_buffer):
        assert isinstance(timbuktu_buffer["neighborhood"]["member_ids"], list)

    def test_member_ids_count_matches_n_units(self, timbuktu_buffer):
        nb = timbuktu_buffer["neighborhood"]
        assert len(nb["member_ids"]) == nb["n_units"]

    def test_member_ids_are_integers(self, timbuktu_buffer):
        for mid in timbuktu_buffer["neighborhood"]["member_ids"]:
            assert isinstance(mid, int), f"member_id {mid!r} is not int"


class TestBasinGeomRoute:
    """GET /api/basin/geom returns correct GeoJSON for a hybas_id list."""

    def test_returns_feature_collection(self, buf_client, timbuktu_buffer):
        ids = timbuktu_buffer["neighborhood"]["member_ids"][:3]
        r = buf_client.get(f"/api/basin/geom?ids={','.join(str(i) for i in ids)}&level=6")
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["type"] == "FeatureCollection"

    def test_feature_count_matches_request(self, buf_client, timbuktu_buffer):
        ids = timbuktu_buffer["neighborhood"]["member_ids"][:3]
        r = buf_client.get(f"/api/basin/geom?ids={','.join(str(i) for i in ids)}&level=6")
        assert len(r.json()["features"]) == 3

    def test_returned_ids_are_integers(self, buf_client, timbuktu_buffer):
        ids = timbuktu_buffer["neighborhood"]["member_ids"][:3]
        r = buf_client.get(f"/api/basin/geom?ids={','.join(str(i) for i in ids)}&level=6")
        for f in r.json()["features"]:
            assert isinstance(f["properties"]["hybas_id"], int)

    def test_full_member_set_honesty_check(self, buf_client, timbuktu_buffer):
        """Basin set returned by /api/basin/geom must equal the signature member_ids exactly."""
        member_ids = timbuktu_buffer["neighborhood"]["member_ids"]
        r = buf_client.get(f"/api/basin/geom?ids={','.join(str(i) for i in member_ids)}&level=6")
        assert r.status_code == 200, r.text
        returned = {f["properties"]["hybas_id"] for f in r.json()["features"]}
        expected = set(member_ids)
        assert returned == expected, f"Mismatch — expected {expected}, got {returned}"

    def test_empty_ids_returns_422(self, client):
        r = client.get("/api/basin/geom?ids=&level=6")
        assert r.status_code == 422

    def test_non_integer_ids_returns_422(self, client):
        r = client.get("/api/basin/geom?ids=abc,def&level=6")
        assert r.status_code == 422


# ---------------------------------------------------------------------------
# WO13 — /api/basin/ring topology route
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def timbuktu_ring_topology(buf_client):
    """Fast ring topology for Timbuktu — center Feature + ring members with geometry."""
    r = buf_client.get("/api/basin/ring?lat=16.8167&lon=-2.9833&level=6")
    assert r.status_code == 200, r.text
    return r.json()


class TestBasinRingTopologyRoute:

    def test_has_center_key(self, timbuktu_ring_topology):
        assert "center" in timbuktu_ring_topology

    def test_center_is_geojson_feature(self, timbuktu_ring_topology):
        assert timbuktu_ring_topology["center"]["type"] == "Feature"

    def test_center_hybas_id_is_int(self, timbuktu_ring_topology):
        hid = timbuktu_ring_topology["center"]["properties"]["hybas_id"]
        assert isinstance(hid, int), f"Expected int, got {type(hid)}"

    def test_has_ring_key(self, timbuktu_ring_topology):
        assert "ring" in timbuktu_ring_topology

    def test_ring_is_nonempty_list(self, timbuktu_ring_topology):
        ring = timbuktu_ring_topology["ring"]
        assert isinstance(ring, list) and len(ring) > 0

    def test_ring_member_hybas_id_is_int(self, timbuktu_ring_topology):
        member = timbuktu_ring_topology["ring"][0]
        assert isinstance(member["hybas_id"], int)

    def test_ring_member_has_neighbor_coords(self, timbuktu_ring_topology):
        member = timbuktu_ring_topology["ring"][0]
        assert "neighbor_lat" in member and "neighbor_lon" in member
        assert isinstance(member["neighbor_lat"], float)
        assert isinstance(member["neighbor_lon"], float)

    def test_ring_member_feature_is_polygon(self, timbuktu_ring_topology):
        geom = timbuktu_ring_topology["ring"][0]["feature"]["geometry"]
        assert geom["type"] in ("Polygon", "MultiPolygon")

    def test_center_and_ring_ids_are_distinct(self, timbuktu_ring_topology):
        """Center basin must not appear in the ring."""
        center_id = timbuktu_ring_topology["center"]["properties"]["hybas_id"]
        ring_ids  = {m["hybas_id"] for m in timbuktu_ring_topology["ring"]}
        assert center_id not in ring_ids, f"Center {center_id} found in ring {ring_ids}"


# ---------------------------------------------------------------------------
# WO21 — /api/basin/buffer topology route
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def timbuktu_buffer_topology(buf_client):
    """Buffer topology for Timbuktu at 200 km — GeoJSON FeatureCollection."""
    r = buf_client.get("/api/basin/buffer?lat=16.8167&lon=-2.9833&radius_km=200&level=6")
    assert r.status_code == 200, r.text
    return r.json()


class TestBasinBufferGeomRoute:

    def test_is_feature_collection(self, timbuktu_buffer_topology):
        assert timbuktu_buffer_topology["type"] == "FeatureCollection"

    def test_has_features_list(self, timbuktu_buffer_topology):
        assert isinstance(timbuktu_buffer_topology["features"], list)

    def test_returns_multiple_basins(self, timbuktu_buffer_topology):
        assert len(timbuktu_buffer_topology["features"]) > 1

    def test_features_are_geojson(self, timbuktu_buffer_topology):
        f = timbuktu_buffer_topology["features"][0]
        assert f["type"] == "Feature"
        assert f["geometry"]["type"] in ("Polygon", "MultiPolygon")

    def test_hybas_id_is_int(self, timbuktu_buffer_topology):
        hid = timbuktu_buffer_topology["features"][0]["properties"]["hybas_id"]
        assert isinstance(hid, int)

    def test_missing_lat_returns_422(self, client):
        r = client.get("/api/basin/buffer?lon=-2.9&radius_km=100")
        assert r.status_code == 422

    def test_missing_lon_returns_422(self, client):
        r = client.get("/api/basin/buffer?lat=16.8&radius_km=100")
        assert r.status_code == 422


# ---------------------------------------------------------------------------
# WO20 — /api/whg/suggest route: validation tests (no live WHG calls)
# ---------------------------------------------------------------------------

class TestWhgSuggestRouteValidation:
    """Input-validation tests for GET /api/whg/suggest.
    These run without a DB or live WHG connection.
    """

    def test_missing_q_returns_422(self, client):
        r = client.get("/api/whg/suggest")
        assert r.status_code == 422, r.text

    def test_empty_q_returns_empty(self, client):
        r = client.get("/api/whg/suggest?q=")
        assert r.status_code == 200
        assert r.json()["results"] == []

    def test_short_q_returns_empty(self, client):
        r = client.get("/api/whg/suggest?q=a")
        assert r.status_code == 200
        assert r.json()["results"] == []

    def test_response_shape(self, client, monkeypatch):
        """Route returns {results: [{id, name, lat, lon, ccodes, alt_names, cname}]}."""
        fake_suggest = [
            {
                "id": "place:5424806",
                "name": "Tombouctou",
                "repr_point": [-2.9833, 16.8167],
                "ccodes": ["ML"],
                "alt_names": ["Timbuktu", "Timbuctoo"],
            },
            {
                "id": "place:9999999",
                "name": "No coords place",
                "repr_point": None,
                "ccodes": [],
                "alt_names": [],
            },
        ]

        import app.api.routes_sandbox as routes_mod
        monkeypatch.setattr(routes_mod, "_whg_suggest", lambda *a, **kw: fake_suggest)

        r = client.get("/api/whg/suggest?q=Timbuktu")
        assert r.status_code == 200
        data = r.json()
        assert "results" in data
        # Only result with repr_point should appear
        assert len(data["results"]) == 1
        res = data["results"][0]
        assert res["id"]     == "place:5424806"
        assert res["name"]   == "Tombouctou"
        assert res["lat"]    == pytest.approx(16.8167)
        assert res["lon"]    == pytest.approx(-2.9833)
        assert res["ccodes"] == ["ML"]
        assert "Timbuktu" in res["alt_names"]
        assert res["cname"]  == "Mali"   # resolved from _CCODES static dict

    def test_no_repr_point_filtered_out(self, client, monkeypatch):
        """Results without repr_point are excluded from the response."""
        import app.api.routes_sandbox as routes_mod
        monkeypatch.setattr(routes_mod, "_whg_suggest",
                            lambda *a, **kw: [{"id": "x", "name": "X", "repr_point": None}])
        r = client.get("/api/whg/suggest?q=test")
        assert r.status_code == 200
        assert r.json()["results"] == []

    def test_fclasses_passed_to_suggest(self, client, monkeypatch):
        """Route always passes fclasses='P,S' to _whg_suggest."""
        import app.api.routes_sandbox as routes_mod
        captured = {}

        def fake(prefix, limit=8, fclasses=None, countries=None):
            captured["fclasses"] = fclasses
            return []

        monkeypatch.setattr(routes_mod, "_whg_suggest", fake)
        client.get("/api/whg/suggest?q=Rome")
        assert captured.get("fclasses") == "P,S"

    def test_country_hint_resolves_to_ccode(self, client, monkeypatch):
        """A country= param is resolved via gaz.ccodes ILIKE and passed as countries= to WHG."""
        import app.api.routes_sandbox as routes_mod
        captured = {}

        def fake(prefix, limit=8, fclasses=None, countries=None):
            captured["countries"] = countries
            return []

        monkeypatch.setattr(routes_mod, "_whg_suggest", fake)

        # Patch db_connect so we don't need a live DB
        class FakeCur:
            def __enter__(self): return self
            def __exit__(self, *a): pass
            def execute(self, sql, params): self._params = params
            def fetchone(self): return ("ML",)

        class FakeConn:
            def cursor(self): return FakeCur()
            def close(self): pass

        monkeypatch.setattr(routes_mod, "db_connect", lambda: FakeConn())
        client.get("/api/whg/suggest?q=Timbuktu&country=Mali")
        assert captured.get("countries") == "ML"

    def test_country_no_match_proceeds_without_filter(self, client, monkeypatch):
        """Unrecognised country hint does not block the search (countries=None)."""
        import app.api.routes_sandbox as routes_mod
        captured = {}

        def fake(prefix, limit=8, fclasses=None, countries=None):
            captured["countries"] = countries
            return []

        monkeypatch.setattr(routes_mod, "_whg_suggest", fake)

        class FakeCur:
            def __enter__(self): return self
            def __exit__(self, *a): pass
            def execute(self, *a): pass
            def fetchone(self): return None

        class FakeConn:
            def cursor(self): return FakeCur()
            def close(self): pass

        monkeypatch.setattr(routes_mod, "db_connect", lambda: FakeConn())
        client.get("/api/whg/suggest?q=Timbuktu&country=xyzzy")
        assert captured.get("countries") is None
