"""
test_explorer.py
----------------
Tests for the /api/explorer/* endpoints added for the Explorer choropleth page.

Four endpoints covered:
  /api/explorer/variables    — variable metadata for the accordion
  /api/explorer/values      — flat {hybas_id: value} dict + stats (s / u / delta modes)
  /api/explorer/categorical — flat {hybas_id: cat_id} dict + category legend
  /api/explorer/lisa        — LISA class assignments (no geometry)

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
def codebook(client):
    r = client.get("/api/explorer/variables")
    assert r.status_code == 200
    return r.json()


# ---------------------------------------------------------------------------
# /api/explorer/variables
# ---------------------------------------------------------------------------

def test_codebook_returns_list(codebook):
    assert isinstance(codebook, list)
    assert len(codebook) > 50, "Expected at least 50 codebook entries"


def test_codebook_required_fields(codebook):
    required = {"schema_key", "friendly_name", "band", "dimension", "type", "queryable"}
    for rec in codebook:
        missing = required - rec.keys()
        assert not missing, f"{rec['schema_key']} missing fields: {missing}"


def test_codebook_queryable_flag(codebook):
    # queryable must be a bool and consistent with the data
    for rec in codebook:
        assert isinstance(rec["queryable"], bool), f"{rec['schema_key']}: queryable not bool"
    # At least some variables must be queryable
    assert any(r["queryable"] for r in codebook), "No queryable variables found"


def test_codebook_range_notation_not_queryable(codebook):
    # Variables with '..' range notation must be non-queryable UNLESS they are
    # monthly_series (s01..s12 pattern), which resolve per month
    for rec in codebook:
        col_s = rec.get("basin08_col_s") or ""
        if ".." in col_s and not rec.get("monthly_series"):
            assert not rec["queryable"], (
                f"{rec['schema_key']}: has range notation '{col_s}' but queryable=True"
            )


def test_codebook_excludes_output_band(codebook):
    bands = {r["band"] for r in codebook}
    assert "output" not in bands, "Output-band rows must be excluded from codebook API"


def test_codebook_no_duplicate_schema_keys(codebook):
    keys = [r["schema_key"] for r in codebook]
    assert len(keys) == len(set(keys)), "Duplicate schema_key entries in codebook"


# ---------------------------------------------------------------------------
# /api/explorer/values
# ---------------------------------------------------------------------------

def test_values_aridity_l6(client):
    r = client.get("/api/explorer/values", params={"var": "aridity_index", "level": 6, "su": "s"})
    assert r.status_code == 200
    data = r.json()
    assert "meta" in data and "values" in data
    assert "geojson" not in data, "values endpoint must not return GeoJSON geometry"
    meta = data["meta"]
    assert meta["n_valid"] > 0
    assert meta["min"] is not None and meta["max"] is not None


def test_values_flat_dict_structure(client):
    r = client.get("/api/explorer/values", params={"var": "aridity_index", "level": 6})
    assert r.status_code == 200
    vals = r.json()["values"]
    assert isinstance(vals, dict), "values must be a dict"
    assert len(vals) > 1000, "Expected thousands of L6 basin entries"


def test_values_keys_are_integers(client):
    # MapLibre setFeatureState requires numeric IDs — keys must parse as integers, not floats
    r = client.get("/api/explorer/values", params={"var": "aridity_index", "level": 6})
    assert r.status_code == 200
    sample = list(r.json()["values"].keys())[:20]
    for k in sample:
        assert "." not in k, f"hybas_id key looks like a float: '{k}' — must be integer string"


def test_values_no_nodata_sentinel(client):
    # -9999 sentinel values must be masked to null, never appear as a raw value
    r = client.get("/api/explorer/values", params={"var": "aridity_index", "level": 6})
    assert r.status_code == 200
    vals = list(r.json()["values"].values())
    assert -9999 not in vals, "-9999 NoData sentinel must be masked to null"


@pytest.mark.parametrize("var_key", [
    "precipitation_annual",
    "temperature_annual",
    "cropland_pct",
])
def test_values_wo14_vars_have_p10_p90(client, var_key):
    # WO14 applyBasinVar() uses p10/p90 from meta for domain — confirm all three vars return them.
    r = client.get("/api/explorer/values", params={"var": var_key, "level": 6, "su": "s"})
    assert r.status_code == 200, f"{var_key} returned {r.status_code}"
    meta = r.json()["meta"]
    assert meta["n_valid"] > 0, f"{var_key}: n_valid=0"
    assert "p10" in meta and meta["p10"] is not None, f"{var_key}: missing p10"
    assert "p90" in meta and meta["p90"] is not None, f"{var_key}: missing p90"
    assert meta["p10"] < meta["p90"], f"{var_key}: p10 >= p90"


def test_values_temperature_divide_by_10(client):
    # tmp_dc_smn stored as °C×10 — displayed values should be in plausible °C range
    r = client.get("/api/explorer/values", params={"var": "temperature_min", "level": 6, "su": "s"})
    assert r.status_code == 200
    vals = [v for v in r.json()["values"].values() if v is not None]
    assert vals, "No non-null temperature values"
    assert max(vals) < 200, f"temperature_min looks like it's still in °C×10 (max={max(vals)})"
    assert min(vals) > -200, f"temperature_min out of plausible range (min={min(vals)})"


def test_values_delta_mode(client):
    r = client.get("/api/explorer/values", params={"var": "aridity_index", "level": 6, "su": "delta"})
    assert r.status_code == 200
    meta = r.json()["meta"]
    # Delta should have values spanning both positive and negative (s vs u divergence)
    assert meta["min"] is not None and meta["max"] is not None


def test_values_upstream_mode(client):
    r = client.get("/api/explorer/values", params={"var": "aridity_index", "level": 6, "su": "u"})
    assert r.status_code == 200
    data = r.json()
    assert data["meta"]["n_valid"] > 0


def test_values_invalid_var(client):
    r = client.get("/api/explorer/values", params={"var": "nonexistent_var", "level": 6})
    assert r.status_code == 404


def test_values_invalid_level(client):
    r = client.get("/api/explorer/values", params={"var": "aridity_index", "level": 7})
    assert r.status_code == 400


def test_values_stats_fields(client):
    r = client.get("/api/explorer/values", params={"var": "aridity_index", "level": 6})
    assert r.status_code == 200
    meta = r.json()["meta"]
    for stat in ("min", "max", "mean", "median", "p10", "p90"):
        assert stat in meta, f"Missing stat field: {stat}"


# ---------------------------------------------------------------------------
# bbox filter (WO03) — /explorer/values + /explorer/categorical
# bbox trims the returned values payload only; stats / category ranking stay global.
# ---------------------------------------------------------------------------

AFRICA_BBOX = "-20,-36,55,38"


def test_values_bbox_trims_payload_not_stats(client):
    """bbox returns a strict subset of values; meta (ramp domain) stays global."""
    full = client.get("/api/explorer/values",
                      params={"var": "elevation_max", "level": 8, "su": "s"}).json()
    sub = client.get("/api/explorer/values",
                     params={"var": "elevation_max", "level": 8, "su": "s", "bbox": AFRICA_BBOX}).json()
    assert 0 < len(sub["values"]) < len(full["values"])
    assert set(sub["values"]).issubset(set(full["values"]))
    # stats are global regardless of bbox — Explorer parity
    assert sub["meta"]["n_valid"] == full["meta"]["n_valid"]
    assert sub["meta"]["p10"] == full["meta"]["p10"]
    assert sub["meta"]["p90"] == full["meta"]["p90"]
    assert sub["meta"]["min"] == full["meta"]["min"]
    assert sub["meta"]["max"] == full["meta"]["max"]


def test_values_no_bbox_unchanged(client):
    """Omitting bbox is the pre-WO03 global behaviour."""
    r = client.get("/api/explorer/values", params={"var": "aridity_index", "level": 6, "su": "s"})
    assert r.status_code == 200
    assert r.json()["meta"]["n_valid"] > 15000  # ~all L6 basins


@pytest.mark.parametrize("bad", ["1,2,3", "200,0,210,10", "0,0,10,100", "10,0,5,20", "a,b,c,d"])
def test_values_bbox_malformed_400(client, bad):
    r = client.get("/api/explorer/values",
                   params={"var": "elevation_max", "level": 8, "bbox": bad})
    assert r.status_code == 400


def test_categorical_bbox_trims_payload_not_ranking(client):
    full = client.get("/api/explorer/categorical",
                      params={"var": "pnv_majority_name", "level": 8}).json()
    sub = client.get("/api/explorer/categorical",
                     params={"var": "pnv_majority_name", "level": 8, "bbox": AFRICA_BBOX}).json()
    assert 0 < len(sub["values"]) < len(full["values"])
    assert set(sub["values"]).issubset(set(full["values"]))
    # category ranking / counts / colours are global — same class → same colour as Explorer
    assert sub["categories"] == full["categories"]


def test_categorical_bbox_malformed_400(client):
    r = client.get("/api/explorer/categorical",
                   params={"var": "pnv_majority_name", "level": 8, "bbox": "1,2,3"})
    assert r.status_code == 400


# ---------------------------------------------------------------------------
# /api/explorer/categorical
# ---------------------------------------------------------------------------

def test_categorical_lithology_l6(client):
    r = client.get("/api/explorer/categorical", params={"var": "lithology_name", "level": 6})
    assert r.status_code == 200
    data = r.json()
    assert "categories" in data and "values" in data
    assert "geojson" not in data, "categorical endpoint must not return GeoJSON geometry"
    cats = data["categories"]
    assert len(cats) > 0, "Expected lithology categories"


def test_categorical_top_n_limit(client):
    # climate_stratum_code has 125 classes — exercises top-20 + Other collapse
    r = client.get("/api/explorer/categorical", params={"var": "climate_stratum_code", "level": 6})
    assert r.status_code == 200
    cats = r.json()["categories"]
    named   = [c for c in cats if c["id"] != -1]
    other_e = [c for c in cats if c["id"] == -1]
    assert len(named) <= 20, f"Too many named categories: {len(named)}"
    assert len(other_e) <= 1, "At most one 'Other' entry expected"


def test_categorical_colors_unique(client):
    r = client.get("/api/explorer/categorical", params={"var": "lithology_name", "level": 6})
    assert r.status_code == 200
    cats = r.json()["categories"]
    named_colors = [c["color"] for c in cats if c["id"] != -1]
    assert len(named_colors) == len(set(named_colors)), "Named categories should have unique colors"


def test_categorical_pct_sums_to_100(client):
    r = client.get("/api/explorer/categorical", params={"var": "lithology_name", "level": 6})
    assert r.status_code == 200
    total = sum(c["pct"] for c in r.json()["categories"])
    assert abs(total - 100.0) < 1.0, f"Category percentages should sum to ~100, got {total}"


def test_categorical_values_dict(client):
    r = client.get("/api/explorer/categorical", params={"var": "lithology_name", "level": 6})
    assert r.status_code == 200
    vals = r.json()["values"]
    assert isinstance(vals, dict), "values must be a dict"
    assert len(vals) > 1000, "Expected thousands of L6 basin entries"
    # Values should be cat_id integers (or -1 for Other)
    sample = list(vals.values())[:20]
    for v in sample:
        assert isinstance(v, int), f"cat_id value should be int, got {type(v)}: {v}"


def test_categorical_invalid_var(client):
    r = client.get("/api/explorer/categorical", params={"var": "nonexistent_var", "level": 6})
    assert r.status_code == 404


def test_categorical_numeric_var_rejected(client):
    # aridity_index is numeric, not in _CAT_LOOKUP — should 400
    r = client.get("/api/explorer/categorical", params={"var": "aridity_index", "level": 6})
    assert r.status_code == 400


# ---------------------------------------------------------------------------
# /api/explorer/lisa
# ---------------------------------------------------------------------------

def test_lisa_aridity_l8(client):
    r = client.get("/api/explorer/lisa", params={"var": "aridity_index", "level": 8})
    assert r.status_code == 200
    data = r.json()
    assert "meta" in data and "classes" in data
    meta = data["meta"]
    assert meta["n"] > 0
    assert "counts" in meta


def test_lisa_counts_structure(client):
    r = client.get("/api/explorer/lisa", params={"var": "aridity_index", "level": 8})
    assert r.status_code == 200
    counts = r.json()["meta"]["counts"]
    valid_classes = {"HH", "HL", "LH", "LL", "NS"}
    assert set(counts.keys()).issubset(valid_classes), f"Unexpected LISA classes: {set(counts.keys()) - valid_classes}"


def test_lisa_classes_values(client):
    r = client.get("/api/explorer/lisa", params={"var": "aridity_index", "level": 8})
    assert r.status_code == 200
    classes = r.json()["classes"]
    assert len(classes) > 0, "classes dict must not be empty"
    valid = {"HH", "HL", "LH", "LL", "NS"}
    bad = {v for v in classes.values() if v not in valid}
    assert not bad, f"Invalid LISA class values: {bad}"


def test_lisa_classes_keys_are_strings(client):
    # JS looks up by String(hybas_id) — API must return string keys
    r = client.get("/api/explorer/lisa", params={"var": "aridity_index", "level": 8})
    assert r.status_code == 200
    classes = r.json()["classes"]
    sample_keys = list(classes.keys())[:10]
    for k in sample_keys:
        assert isinstance(k, str), f"hybas_id key should be string, got {type(k)}: {k}"


def test_lisa_counts_sum_equals_n(client):
    r = client.get("/api/explorer/lisa", params={"var": "aridity_index", "level": 8})
    assert r.status_code == 200
    data = r.json()
    n       = data["meta"]["n"]
    total   = sum(data["meta"]["counts"].values())
    assert total == n, f"counts sum {total} != meta.n {n}"


def test_lisa_no_data_returns_404(client):
    # Categorical variables have no LISA data (join-count only) — should always 404
    r = client.get("/api/explorer/lisa", params={"var": "lithology_name", "level": 8})
    assert r.status_code == 404


def test_lisa_invalid_var(client):
    r = client.get("/api/explorer/lisa", params={"var": "nonexistent_var", "level": 8})
    assert r.status_code == 404


def test_lisa_no_geometry_in_response(client):
    # LISA endpoint must NOT return geometry — client reuses the choropleth layer
    r = client.get("/api/explorer/lisa", params={"var": "aridity_index", "level": 8})
    assert r.status_code == 200
    data = r.json()
    assert "geojson" not in data, "LISA endpoint must not return GeoJSON geometry"
    assert "features" not in data


# ---------------------------------------------------------------------------
# /api/explorer/scatter
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def scatter_data(client):
    r = client.get("/api/explorer/scatter",
                   params={"x": "temperature_annual", "y": "precipitation_annual", "level": 6})
    assert r.status_code == 200
    return r.json()


def test_scatter_response_shape(scatter_data):
    for key in ("x_meta", "y_meta", "n_paired", "values"):
        assert key in scatter_data, f"Missing top-level key: {key}"
    for meta_key in ("var", "col", "label", "units", "n_total", "n_valid"):
        assert meta_key in scatter_data["x_meta"], f"x_meta missing field: {meta_key}"
        assert meta_key in scatter_data["y_meta"], f"y_meta missing field: {meta_key}"


def test_scatter_n_paired_matches_values(scatter_data):
    assert scatter_data["n_paired"] == len(scatter_data["values"]), (
        "n_paired must equal len(values)"
    )


def test_scatter_values_are_triples(scatter_data):
    sample = scatter_data["values"][:20]
    for triple in sample:
        assert len(triple) == 3, f"Expected [hybas_id, x, y] triple, got len={len(triple)}"
        hybas_id, xv, yv = triple
        assert isinstance(hybas_id, int), f"hybas_id must be int, got {type(hybas_id)}"
        assert isinstance(xv, (int, float)), f"x value must be numeric, got {type(xv)}"
        assert isinstance(yv, (int, float)), f"y value must be numeric, got {type(yv)}"


def test_scatter_substantial_coverage(scatter_data):
    assert scatter_data["n_paired"] > 5000, (
        f"Expected >5000 paired values for temperature×precip, got {scatter_data['n_paired']}"
    )


def test_scatter_temperature_divided_by_10(client):
    # temperature_annual → tmp_dc_syr stored as °C×10; endpoint divides by 10
    r = client.get("/api/explorer/scatter",
                   params={"x": "temperature_annual", "y": "aridity_index", "level": 6})
    assert r.status_code == 200
    x_vals = [v[1] for v in r.json()["values"] if v[1] is not None]
    assert x_vals, "No temperature_annual x values"
    assert max(x_vals) < 100, f"temperature_annual looks undivided (max={max(x_vals):.1f})"
    assert min(x_vals) > -100, f"temperature_annual out of plausible range (min={min(x_vals):.1f})"


def test_scatter_no_nodata_sentinel(scatter_data):
    for hybas_id, xv, yv in scatter_data["values"]:
        assert xv != -9999, f"x=-9999 NoData sentinel in output (hybas_id={hybas_id})"
        assert yv != -9999, f"y=-9999 NoData sentinel in output (hybas_id={hybas_id})"


def test_scatter_meta_var_names(scatter_data):
    assert scatter_data["x_meta"]["var"] == "temperature_annual"
    assert scatter_data["y_meta"]["var"] == "precipitation_annual"


def test_scatter_invalid_x_var_returns_404(client):
    r = client.get("/api/explorer/scatter",
                   params={"x": "nonexistent_var", "y": "precipitation_annual", "level": 6})
    assert r.status_code == 404


def test_scatter_invalid_y_var_returns_404(client):
    r = client.get("/api/explorer/scatter",
                   params={"x": "temperature_annual", "y": "nonexistent_var", "level": 6})
    assert r.status_code == 404


def test_scatter_invalid_level_returns_400(client):
    r = client.get("/api/explorer/scatter",
                   params={"x": "temperature_annual", "y": "precipitation_annual", "level": 7})
    assert r.status_code == 400
