"""
test_polity.py
--------------
Tests for /api/polity/* endpoints.

Endpoints covered:
  /api/polity/search          — debounced autocomplete
  /api/polity/slices          — time-slice list for a named polity
  /api/polity/geom            — GeoJSON Feature for a single slice
  /api/polity/period          — GeoJSON FeatureCollection at a given year  [new]
  /api/polity/period/years    — sorted distinct fromyear list              [new]
  /api/polity/seshat          — Seshat general + social variables

All DB-hitting tests are skipped if the DB is unavailable.
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
def northern_song_slices(client):
    r = client.get("/api/polity/slices?name=Northern+Song")
    assert r.status_code == 200
    return r.json()


@pytest.fixture(scope="module")
def period_1000(client):
    r = client.get("/api/polity/period?year=1000")
    assert r.status_code == 200
    return r.json()


@pytest.fixture(scope="module")
def period_years(client):
    r = client.get("/api/polity/period/years")
    assert r.status_code == 200
    return r.json()


# ---------------------------------------------------------------------------
# /api/polity/search
# ---------------------------------------------------------------------------

def test_search_returns_list(client):
    r = client.get("/api/polity/search?q=song")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_search_finds_northern_song(client):
    r = client.get("/api/polity/search?q=northern+song")
    names = [item["name"] for item in r.json()]
    assert "Northern Song" in names


def test_search_result_fields(client):
    r = client.get("/api/polity/search?q=rome")
    assert r.status_code == 200
    for item in r.json():
        assert "name"   in item
        assert "first"  in item
        assert "last"   in item
        assert "slices" in item
        assert item["slices"] >= 1


def test_search_max_40_results(client):
    r = client.get("/api/polity/search?q=empire")
    assert len(r.json()) <= 40


def test_search_short_query_rejected(client):
    r = client.get("/api/polity/search?q=x")
    # Endpoint requires >= 2 chars; returns empty list
    assert r.status_code == 200
    assert r.json() == []


# ---------------------------------------------------------------------------
# /api/polity/slices
# ---------------------------------------------------------------------------

def test_slices_northern_song_count(northern_song_slices):
    assert len(northern_song_slices) == 6


def test_slices_required_fields(northern_song_slices):
    required = {"id", "fromyear", "toyear", "geom_group"}
    for s in northern_song_slices:
        missing = required - s.keys()
        assert not missing, f"Slice missing fields: {missing}"


def test_slices_ordered_by_fromyear(northern_song_slices):
    years = [s["fromyear"] for s in northern_song_slices]
    assert years == sorted(years)


def test_slices_geom_groups_monotone(northern_song_slices):
    groups = [s["geom_group"] for s in northern_song_slices]
    assert groups == sorted(groups)


def test_slices_seshatid_present(northern_song_slices):
    for s in northern_song_slices:
        assert s.get("seshatid") == "cn_northern_song_dyn"


# ---------------------------------------------------------------------------
# /api/polity/geom
# ---------------------------------------------------------------------------

def test_geom_returns_feature(northern_song_slices, client):
    first_id = northern_song_slices[0]["id"]
    r = client.get(f"/api/polity/geom?id={first_id}")
    assert r.status_code == 200
    gj = r.json()
    assert gj["type"] == "Feature"
    assert "geometry" in gj
    assert gj["geometry"]["type"] in {"Polygon", "MultiPolygon"}


def test_geom_properties_present(northern_song_slices, client):
    first_id = northern_song_slices[0]["id"]
    r = client.get(f"/api/polity/geom?id={first_id}")
    props = r.json()["properties"]
    assert "name"     in props
    assert "fromyear" in props
    assert "toyear"   in props


# ---------------------------------------------------------------------------
# /api/polity/period  (new)
# ---------------------------------------------------------------------------

def test_period_1000_is_feature_collection(period_1000):
    assert period_1000["type"] == "FeatureCollection"
    assert "features" in period_1000


def test_period_1000_has_polities(period_1000):
    # Historically rich year — well over 50 active polities expected
    assert len(period_1000["features"]) > 50


def test_period_feature_required_properties(period_1000):
    required = {"id", "name", "fromyear", "toyear"}
    for f in period_1000["features"]:
        missing = required - f["properties"].keys()
        assert not missing, f"Feature missing properties: {missing}"


def test_period_feature_geometry_valid(period_1000):
    valid_types = {"Polygon", "MultiPolygon"}
    for f in period_1000["features"]:
        assert f["type"] == "Feature"
        assert f["geometry"]["type"] in valid_types


def test_period_all_active_at_year(period_1000):
    for f in period_1000["features"]:
        p = f["properties"]
        assert p["fromyear"] <= 1000 <= p["toyear"], (
            f"{p['name']} fromyear={p['fromyear']} toyear={p['toyear']} not active at 1000"
        )


def test_period_no_components(period_1000):
    # is_component polities are excluded; every result should be a leaf polity
    # We can't check the flag directly from the response, but no name should
    # contain a leading '(' (Cliopatria's component naming convention)
    for f in period_1000["features"]:
        name = f["properties"]["name"]
        assert not name.startswith("("), f"Component polity leaked: {name}"


def test_period_pre_history_empty(client):
    # Before the earliest recorded polity (~3400 BCE) there should be nothing
    r = client.get("/api/polity/period?year=-5000")
    assert r.status_code == 200
    assert r.json()["features"] == []


def test_period_modern_has_polities(client):
    r = client.get("/api/polity/period?year=2000")
    assert r.status_code == 200
    assert len(r.json()["features"]) > 10


def test_period_northern_song_present_at_1000(period_1000):
    names = {f["properties"]["name"] for f in period_1000["features"]}
    assert "Northern Song" in names


# ---------------------------------------------------------------------------
# /api/polity/period/years  (new)
# ---------------------------------------------------------------------------

def test_period_years_returns_list(period_years):
    assert isinstance(period_years, list)


def test_period_years_not_empty(period_years):
    assert len(period_years) > 400, "Expected hundreds of distinct fromyear values"


def test_period_years_sorted(period_years):
    assert period_years == sorted(period_years)


def test_period_years_all_integers(period_years):
    for y in period_years:
        assert isinstance(y, int), f"Expected int, got {type(y)}: {y}"


def test_period_years_plausible_range(period_years):
    assert period_years[0]  >= -3500, "Earliest year unexpectedly ancient"
    assert period_years[-1] <= 2024,  "Latest year beyond dataset range"


def test_period_years_contains_1000(period_years):
    assert 1000 in period_years


# ---------------------------------------------------------------------------
# /api/polity/seshat
# ---------------------------------------------------------------------------

def test_seshat_general_fields_present(client):
    r = client.get("/api/polity/seshat?seshatid=cn_northern_song_dyn")
    assert r.status_code == 200
    data = r.json()
    assert "general" in data
    gen = data["general"]
    assert "capital"  in gen
    assert "language" in gen


def test_seshat_social_present(client):
    r = client.get("/api/polity/seshat?seshatid=cn_northern_song_dyn")
    data = r.json()
    assert "social" in data
    # social is a dict keyed by subsection name (e.g. "Bureaucracy Characteristics")
    assert isinstance(data["social"], dict)
    assert len(data["social"]) > 0


def test_seshat_unknown_id_returns_404(client):
    r = client.get("/api/polity/seshat?seshatid=xx_does_not_exist")
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# /api/clio/* -- Section 1 of docs/edop/api_shape/WO_public-api-reshape.md.
# Additive-only consolidation: /clio/search, /clio/slices, /clio/geom delegate
# directly to the /polity/* functions above (not reimplementations), so these
# tests are equivalence checks against the routes tested above, plus coverage
# for the one genuinely new piece (_clio_resolve_geom_wkt). Nothing live calls
# /clio yet -- verified at the bottom of this section.
# ---------------------------------------------------------------------------

def test_clio_search_matches_polity_search(client):
    a = client.get("/api/polity/search?q=song").json()
    b = client.get("/api/clio/search?q=song").json()
    assert a == b


def test_clio_slices_matches_polity_slices(client, northern_song_slices):
    b = client.get("/api/clio/slices?name=Northern+Song").json()
    assert northern_song_slices == b


def test_clio_geom_matches_polity_geom(client, northern_song_slices):
    first_id = northern_song_slices[0]["id"]
    a = client.get(f"/api/polity/geom?id={first_id}").json()
    b = client.get(f"/api/clio/geom?id={first_id}").json()
    assert a == b


def test_clio_geom_404_for_unknown_id(client):
    r = client.get("/api/clio/geom?id=99999999")
    assert r.status_code == 404


def test_clio_resolve_geom_wkt_matches_geojson_type(client, northern_song_slices):
    """The new WKT helper isn't exposed over HTTP yet (Section 2 will call it
    server-side) -- call it directly, and sanity-check it's deriving from the
    same geom column as /polity/geom's GeoJSON (same slice, compatible type)."""
    from app.api.routes_common import _clio_resolve_geom_wkt

    first_id = northern_song_slices[0]["id"]
    wkt = _clio_resolve_geom_wkt(first_id)
    assert wkt is not None
    assert wkt.startswith("POLYGON") or wkt.startswith("MULTIPOLYGON")

    gj_type = client.get(f"/api/polity/geom?id={first_id}").json()["geometry"]["type"]
    assert gj_type.upper() in wkt[:len(gj_type)].upper()


def test_clio_resolve_geom_wkt_none_for_unknown_id():
    from app.api.routes_common import _clio_resolve_geom_wkt
    assert _clio_resolve_geom_wkt(99999999) is None


def test_nothing_live_references_clio():
    """Section 1 acceptance criterion: /clio is dormant -- built and tested in
    isolation, not yet wired into any template or the areas() polity branch."""
    import re
    from pathlib import Path

    root = Path(__file__).parent.parent
    hits = []
    for pattern in ("app/templates/*.html", "app/api/routes_sandbox.py"):
        for path in root.glob(pattern):
            text = path.read_text(encoding="utf-8")
            if re.search(r"/clio\b", text):
                hits.append(str(path.relative_to(root)))
    assert not hits, f"/clio referenced outside its own definition: {hits}"
