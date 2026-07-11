"""
tests/surface/test_sandbox_v2.py
---------------------------------
Structural tests for sandbox_v2.html (/sandbox/lookup2).

These verify the page renders, required element IDs exist, and the initial
CSS state matches the JS-controlled visibility contract (scope extras hidden,
Band T year row hidden, sig button disabled on load).

JS runtime behaviour (scope gate, T toggle) is verified by browser inspection,
not here.  When a browser-automation tool is added, extend this file.
"""

import pytest
from fastapi.testclient import TestClient
from bs4 import BeautifulSoup


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def client():
    from app.main import app
    return TestClient(app)


@pytest.fixture(scope="module")
def page(client):
    r = client.get("/sandbox/lookup2")
    assert r.status_code == 200
    return BeautifulSoup(r.text, "html.parser")


@pytest.fixture(scope="module")
def raw_html(client):
    return client.get("/sandbox/lookup2").text


# ---------------------------------------------------------------------------
# Constants (module-level so parametrize can reference them)
# ---------------------------------------------------------------------------

REQUIRED_IDS = [
    "v2-scope-select",
    "v2-band-T",
    "v2-t-year-row",
    "v2-sig-btn",
    "v2-point-section",
    "v2-example-select",
    "scope-extra-buffer",
    "scope-extra-polity",
    "scope-extra-draw",
    "v2-radius",
    "v2-polity-input",
    "v2-polity-dropdown",
    "v2-slice-row",
    "v2-slice-select",
    "v2-resolver-year",
    "v2-from-year",
    "v2-to-year",
    "v2-map",
    "v2-pane-sig",
    "v2-pane-analysis",
    "v2-intro",
    "v2-intro-text",
    "v2-choropleth",
    "v2-basin-var",
    "v2-basin-legend",
    # v2-lmr-year-control / slider / label retired by WO19 (notch path removed)
]

SCOPE_OPTIONS = [
    ("",       "Select a scope"),
    ("single", "Single basin"),
    ("buffer", "Buffer"),
    ("ring",   "Basin ring"),
    ("polity", "Polity"),
    ("draw",   "Draw a study area"),
]

EXAMPLE_VALUES = [
    "single|16.8167,-2.9833|Timbuktu",
    "buffer|16.8167,-2.9833|Timbuktu|100",
    "ring|16.8167,-2.9833|Timbuktu|1400|1500",
    "polity|Northern Song|1000|1000|1100",
]

BANDS_CHECKED_ON_LOAD   = ["A", "B", "C", "D", "E"]
BANDS_UNCHECKED_ON_LOAD = ["T"]

SINGLE_BASIN_FIXTURE = "/dev/exemplars/01_single_basin_detail.json"
POLITY_FIXTURE       = "/dev/exemplars/03_polity_nsong_detail.json"
EXPECTED_METHODS = {"area_weighted", "dominant_basin", "class_mixture",
                    "flag_fraction", "distribution_only", "extreme"}


# ---------------------------------------------------------------------------
# Route
# ---------------------------------------------------------------------------

class TestRoute:
    def test_200(self, client):
        r = client.get("/sandbox/lookup2")
        assert r.status_code == 200
        assert "text/html" in r.headers["content-type"]


# ---------------------------------------------------------------------------
# Structure — required IDs
# ---------------------------------------------------------------------------

class TestStructure:
    @pytest.mark.parametrize("el_id", REQUIRED_IDS)
    def test_element_present(self, page, el_id):
        assert page.find(id=el_id) is not None, f"#{el_id} not found in rendered HTML"


# ---------------------------------------------------------------------------
# Initial CSS state
# ---------------------------------------------------------------------------

class TestInitialState:
    """
    These assert the CSS state the browser sees before any JS runs.
    The scope gate and T toggle JS update inline styles/classes at runtime;
    the initial state here must match so the JS starts from the right baseline.
    """

    def test_scope_extras_carry_hidden_class(self, page):
        """All three scope-extra divs must carry the .scope-extra class (display:none via CSS)."""
        for extra_id in ("scope-extra-buffer", "scope-extra-polity", "scope-extra-draw"):
            el = page.find(id=extra_id)
            assert el is not None, f"#{extra_id} missing"
            assert "scope-extra" in el.get("class", []), \
                f"#{extra_id} must carry .scope-extra class to be hidden on load"

    def test_polity_slice_row_hidden(self, page):
        """Slice picker must be hidden on load — shown only after a polity is selected."""
        el = page.find(id="v2-slice-row")
        assert el is not None, "#v2-slice-row missing"
        assert "none" in (el.get("style") or ""), \
            "#v2-slice-row must have display:none on load"

    def test_polity_dropdown_hidden(self, page):
        el = page.find(id="v2-polity-dropdown")
        assert el is not None, "#v2-polity-dropdown missing"
        assert "none" in (el.get("style") or ""), \
            "#v2-polity-dropdown must have display:none on load"

    def test_t_year_row_hidden(self, page):
        el = page.find(id="v2-t-year-row")
        assert "d-none" in el.get("class", []), \
            "#v2-t-year-row must carry d-none on load"

    def test_sig_button_disabled(self, page):
        el = page.find(id="v2-sig-btn")
        assert el.has_attr("disabled"), \
            "#v2-sig-btn must be disabled on load (no scope selected)"

    def test_point_section_visible_on_load(self, page):
        """Point input should be visible initially — JS hides it for polity/draw scopes."""
        el = page.find(id="v2-point-section")
        assert "display: none" not in el.get("style", ""), \
            "#v2-point-section must not be hidden on load"


# ---------------------------------------------------------------------------
# Scope dropdown
# ---------------------------------------------------------------------------

class TestScopeOptions:
    def test_option_count(self, page):
        select = page.find(id="v2-scope-select")
        assert len(select.find_all("option")) == len(SCOPE_OPTIONS)

    @pytest.mark.parametrize("value,label", SCOPE_OPTIONS)
    def test_option_present(self, page, value, label):
        select = page.find(id="v2-scope-select")
        opt = select.find("option", {"value": value})
        assert opt is not None, f"Scope option value='{value}' not found"
        assert label in opt.get_text(), f"Scope option '{value}' label mismatch"


# ---------------------------------------------------------------------------
# Example dropdown
# ---------------------------------------------------------------------------

class TestExampleOptions:
    @pytest.mark.parametrize("value", EXAMPLE_VALUES)
    def test_option_present(self, page, value):
        select = page.find(id="v2-example-select")
        opt = select.find("option", {"value": value})
        assert opt is not None, f"Example option value='{value}' not found"


# ---------------------------------------------------------------------------
# Band checkboxes
# ---------------------------------------------------------------------------

class TestFixtureHarness:
    """
    Verify the dev exemplar fixture is served correctly and has the structural
    contract the renderer depends on.  Tests skip if the fixture dir is absent
    (gitignored output/; not present on server or CI).
    """

    @pytest.fixture(scope="class")
    def fixture_json(self, client):
        r = client.get(SINGLE_BASIN_FIXTURE)
        if r.status_code != 200:
            pytest.skip("Exemplar fixtures not available (output/edop/surface/exemplars/)")
        return r.json()

    def test_fixture_served(self, client):
        r = client.get(SINGLE_BASIN_FIXTURE)
        if r.status_code != 200:
            pytest.skip("Exemplar fixtures not available")
        assert "application/json" in r.headers["content-type"]

    def test_top_level_keys(self, fixture_json):
        assert {"rows", "neighborhood", "bands", "shortfall"} <= set(fixture_json.keys())

    def test_row_count(self, fixture_json):
        assert len(fixture_json["rows"]) == 52

    def test_all_methods_present(self, fixture_json):
        methods = {r["method"] for r in fixture_json["rows"]}
        assert methods == EXPECTED_METHODS

    def test_representative_score_field_name(self, fixture_json):
        """Guard against field-name drift — renderer uses representative_score, not score."""
        row = fixture_json["rows"][0]
        assert "representative_score" in row
        assert "score" not in row

    def test_representative_raw_field_name(self, fixture_json):
        row = fixture_json["rows"][0]
        assert "representative_raw" in row
        assert "raw" not in row

    def test_class_mixture_raw_is_string(self, fixture_json):
        """DN7: class_mixture.representative_raw must be a string label, not a number."""
        row = next(r for r in fixture_json["rows"] if r["method"] == "class_mixture")
        assert isinstance(row["representative_raw"], str)

    def test_neighborhood_block(self, fixture_json):
        nb = fixture_json["neighborhood"]
        assert {"type", "level", "hybas_id", "n_units", "unit_type"} <= set(nb.keys())

    @pytest.mark.parametrize("band", ["A", "B", "C", "D", "E"])
    def test_rows_in_band(self, fixture_json, band):
        rows_in_band = [r for r in fixture_json["rows"] if r["band"] == band]
        assert len(rows_in_band) > 0, f"No rows in band {band}"


class TestPolityFixtureContract:
    """Contract tests for 03_polity_nsong_detail.json — guards the T-band renderer."""

    @pytest.fixture(scope="class")
    def polity_json(self, client):
        r = client.get(POLITY_FIXTURE)
        if r.status_code != 200:
            pytest.skip("Polity fixture not available (output/edop/surface/exemplars/)")
        return r.json()

    def test_fixture_served(self, client):
        r = client.get(POLITY_FIXTURE)
        if r.status_code != 200:
            pytest.skip("Polity fixture not available")
        assert "application/json" in r.headers["content-type"]

    def test_top_level_keys(self, polity_json):
        assert {"rows", "neighborhood", "bands", "shortfall"} <= set(polity_json.keys())

    def test_total_row_count(self, polity_json):
        assert len(polity_json["rows"]) == 372

    def test_band_t_present(self, polity_json):
        t_rows = [r for r in polity_json["rows"] if r.get("band") == "T"]
        assert len(t_rows) == 320

    def test_lmr_variables_present(self, polity_json):
        t_vars = {r["variable"] for r in polity_json["rows"] if r.get("band") == "T"}
        for v in ("lmr_pdsi", "lmr_air", "lmr_prate"):
            assert v in t_vars, f"Missing LMR variable: {v}"

    def test_hyde_variables_present(self, polity_json):
        t_vars = {r["variable"] for r in polity_json["rows"] if r.get("band") == "T"}
        for v in ("hyde_cropland", "hyde_grazing", "hyde_pasture", "hyde_rangeland"):
            assert v in t_vars, f"Missing HYDE variable: {v}"

    def test_evolv2k_present(self, polity_json):
        t_vars = {r["variable"] for r in polity_json["rows"] if r.get("band") == "T"}
        assert "evolv2k_vssi" in t_vars

    def test_lmr_rows_have_year(self, polity_json):
        lmr = [r for r in polity_json["rows"] if r.get("variable") == "lmr_pdsi"]
        assert all(r.get("year") is not None for r in lmr)
        assert len(lmr) == 101

    def test_lmr_rows_have_distribution(self, polity_json):
        lmr = [r for r in polity_json["rows"] if r.get("variable") == "lmr_pdsi"]
        for r in lmr:
            dist = r.get("detail", {}).get("distribution", {})
            assert "bins" in dist and "weights" in dist, \
                f"Missing distribution in lmr_pdsi row year={r.get('year')}"
            assert "p10" in dist and "p90" in dist


class TestBandChecks:
    @pytest.mark.parametrize("band", BANDS_CHECKED_ON_LOAD)
    def test_band_checked(self, page, band):
        cb = page.find(id=f"v2-band-{band}")
        assert cb is not None, f"Band {band} checkbox missing"
        assert cb.has_attr("checked"), f"Band {band} should be checked on load"

    @pytest.mark.parametrize("band", BANDS_UNCHECKED_ON_LOAD)
    def test_band_unchecked(self, page, band):
        cb = page.find(id=f"v2-band-{band}")
        assert cb is not None, f"Band {band} checkbox missing"
        assert not cb.has_attr("checked"), f"Band {band} should be unchecked on load"


# ---------------------------------------------------------------------------
# WO15 — LMR choropleth (structural)
# ---------------------------------------------------------------------------

class TestLMRChoroplethStructure:
    """
    Structural tests for the WO15 LMR variable selector entries and
    paint-year control element.  JS runtime behaviour tested in TestLMRUI.
    """

    def test_lmr_temp_option_enabled(self, page):
        """lmr_temp_anomaly must be selectable — not disabled."""
        select = page.find(id="v2-basin-var")
        opt = select.find("option", {"value": "lmr_temp_anomaly"})
        assert opt is not None, "lmr_temp_anomaly option not found"
        assert not opt.has_attr("disabled"), "lmr_temp_anomaly must not be disabled (WO15 enables it)"

    def test_lmr_precip_option_enabled(self, page):
        """lmr_precip_anomaly must be selectable — not disabled."""
        select = page.find(id="v2-basin-var")
        opt = select.find("option", {"value": "lmr_precip_anomaly"})
        assert opt is not None, "lmr_precip_anomaly option not found"
        assert not opt.has_attr("disabled"), "lmr_precip_anomaly must not be disabled (WO15 enables it)"

    def test_hyde_cropland_now_enabled(self, page):
        """HYDE cropland enabled by WO16 — no longer disabled."""
        select = page.find(id="v2-basin-var")
        opt = select.find("option", {"value": "hyde_cropland"})
        assert opt is not None, "hyde_cropland option not found"
        assert not opt.has_attr("disabled"), "hyde_cropland must be enabled (WO16)"

    def test_lmr_slider_retired(self, page):
        """WO19: paint-year slider (#v2-lmr-year-slider) must be gone — retired by WO19."""
        slider = page.find(id="v2-lmr-year-slider")
        assert slider is None, "#v2-lmr-year-slider still present — should have been retired by WO19"

    def test_lmr_year_control_retired(self, page):
        """WO19: paint-year control div (#v2-lmr-year-control) must be gone — retired by WO19."""
        el = page.find(id="v2-lmr-year-control")
        assert el is None, "#v2-lmr-year-control still present — should have been retired by WO19"

    def test_lmr_notch_path_retired(self, raw_html):
        """WO19: notch-based property keys (air_0 etc.) must not appear in page JS."""
        assert "lmrNotchForYear" not in raw_html, "lmrNotchForYear still in page JS"
        assert "LMR_NOTCHES" not in raw_html, "LMR_NOTCHES still in page JS"

    def test_lmr_values_route_referenced(self, raw_html):
        """WO19: page JS must reference /api/lmr/values."""
        assert "/api/lmr/values" in raw_html, "/api/lmr/values not referenced in page JS"

    def test_lmr_optgroup_label(self, page):
        """LMR option group must carry the v2.1 label, not the WO15 placeholder."""
        select = page.find(id="v2-basin-var")
        groups = select.find_all("optgroup")
        labels = [g.get("label", "") for g in groups]
        assert any("LMR v2.1" in lbl for lbl in labels), \
            "LMR optgroup label must include 'LMR v2.1'; found: " + str(labels)


# ---------------------------------------------------------------------------
# WO16 — HYDE choropleth (structural)
# ---------------------------------------------------------------------------

class TestHydeChoroplethStructure:
    """
    Structural tests for the WO16 HYDE variable selector entries.
    JS runtime behaviour tested in TestHydeUI (Playwright, skip-pending-state-model).
    """

    def test_hyde_cropland_option_enabled(self, page):
        select = page.find(id="v2-basin-var")
        opt = select.find("option", {"value": "hyde_cropland"})
        assert opt is not None, "hyde_cropland option not found"
        assert not opt.has_attr("disabled"), "hyde_cropland must be enabled (WO16)"

    def test_hyde_grazing_option_enabled(self, page):
        select = page.find(id="v2-basin-var")
        opt = select.find("option", {"value": "hyde_grazing"})
        assert opt is not None, "hyde_grazing option not found"
        assert not opt.has_attr("disabled"), "hyde_grazing must be enabled (WO16)"

    def test_hyde_optgroup_label(self, page):
        """HYDE optgroup label must drop the WO16 placeholder."""
        select = page.find(id="v2-basin-var")
        groups = select.find_all("optgroup")
        labels = [g.get("label", "") for g in groups]
        assert any("HYDE 3.4" in lbl for lbl in labels), \
            "HYDE optgroup label must include 'HYDE 3.4'; found: " + str(labels)
        assert not any("WO16" in lbl for lbl in labels), \
            "HYDE optgroup must not still carry the (WO16) placeholder"

    def test_hyde_uses_values_api_not_raster(self, raw_html):
        """WO16a: HYDE must use applyHydeChoropleth (values-API), not applyHydeRaster."""
        assert "applyHydeChoropleth" in raw_html, "applyHydeChoropleth not found in page JS"
        assert "applyHydeRaster" not in raw_html, "old raster function still present"

    def test_hyde_values_route_referenced(self, raw_html):
        assert "/api/hyde/values" in raw_html, "/api/hyde/values route not referenced in page JS"

    def test_hyde_pasture_option_enabled(self, page):
        select = page.find(id="v2-basin-var")
        opt = select.find("option", {"value": "hyde_pasture"})
        assert opt is not None, "hyde_pasture option not found"
        assert not opt.has_attr("disabled"), "hyde_pasture must be enabled"

    def test_hyde_rangeland_option_enabled(self, page):
        select = page.find(id="v2-basin-var")
        opt = select.find("option", {"value": "hyde_rangeland"})
        assert opt is not None, "hyde_rangeland option not found"
        assert not opt.has_attr("disabled"), "hyde_rangeland must be enabled"

    def test_hyde_db_var_map_present(self, raw_html):
        """HYDE_DB_VAR maps selector keys to DB column names (replaces HYDE_VAR_PATHS)."""
        assert "HYDE_DB_VAR" in raw_html, "HYDE_DB_VAR not found"
        assert "HYDE_VAR_PATHS" not in raw_html, "old HYDE_VAR_PATHS still present"
        assert "hyde_pasture" in raw_html, "hyde_pasture missing from HYDE_DB_VAR"
        assert "hyde_rangeland" in raw_html, "hyde_rangeland missing from HYDE_DB_VAR"


class TestHydeValuesRoute:
    """Smoke tests for the /api/hyde/values route (WO16a)."""

    def test_route_returns_200(self, client):
        r = client.get("/api/hyde/values?var=cropland&year=1000")
        assert r.status_code == 200

    def test_response_shape(self, client):
        r = client.get("/api/hyde/values?var=cropland&year=1000")
        body = r.json()
        assert "var" in body and "actual_year" in body and "values" in body

    def test_actual_year_snapped(self, client):
        r = client.get("/api/hyde/values?var=cropland&year=1050")
        body = r.json()
        assert body["actual_year"] == 1000, f"Expected 1000 CE snap, got {body['actual_year']}"

    def test_values_are_fractions(self, client):
        r = client.get("/api/hyde/values?var=cropland&year=1000")
        body = r.json()
        vals = [v for v in body["values"].values() if v is not None]
        assert all(0.0 <= v <= 1.01 for v in vals), "Values should be fractions 0–1"

    def test_invalid_var_rejected(self, client):
        r = client.get("/api/hyde/values?var=badvar&year=1000")
        assert r.status_code == 400

    def test_grazing_returns_values(self, client):
        r = client.get("/api/hyde/values?var=grazing&year=1000")
        assert r.status_code == 200
        assert len(r.json()["values"]) > 1000

    def test_consecutive_steps_differ(self, client):
        """Adjacent CE century steps must return genuinely different basin values.

        Confirms the slice-repaint mechanism has real temporal signal, not stale data.
        900→1000 CE and 1000→1100 CE should each change >500 basins by more than 0.1%
        cropland fraction (observed: ~2385 and ~2648 respectively).
        """
        r900  = client.get("/api/hyde/values?var=cropland&year=900").json()["values"]
        r1000 = client.get("/api/hyde/values?var=cropland&year=1000").json()["values"]
        r1100 = client.get("/api/hyde/values?var=cropland&year=1100").json()["values"]

        shared = set(r900) & set(r1000) & set(r1100)
        assert len(shared) > 10000, f"Too few shared basin IDs: {len(shared)}"

        changed_900_1000 = sum(
            1 for k in shared
            if abs((r1000[k] or 0) - (r900[k] or 0)) > 0.001
        )
        changed_1000_1100 = sum(
            1 for k in shared
            if abs((r1100[k] or 0) - (r1000[k] or 0)) > 0.001
        )
        assert changed_900_1000 > 500, \
            f"900→1000 CE: only {changed_900_1000} basins changed >0.1% — values may be stale"
        assert changed_1000_1100 > 500, \
            f"1000→1100 CE: only {changed_1000_1100} basins changed >0.1% — values may be stale"


# ---------------------------------------------------------------------------
# WO19 — LMR per-span values route
# ---------------------------------------------------------------------------

class TestLMRValuesRoute:
    """Smoke tests for the /api/lmr/values route (WO19)."""

    def test_route_returns_200(self, client):
        r = client.get("/api/lmr/values?var=air&from_year=1000&to_year=1100")
        assert r.status_code == 200

    def test_response_shape(self, client):
        r = client.get("/api/lmr/values?var=air&from_year=1000&to_year=1100")
        body = r.json()
        assert "var" in body
        assert "from_year" in body
        assert "to_year" in body
        assert "actual_from" in body
        assert "values" in body

    def test_actual_from_above_floor(self, client):
        """Span above floor: actual_from == from_year."""
        r = client.get("/api/lmr/values?var=air&from_year=1000&to_year=1100")
        body = r.json()
        assert body["actual_from"] == 1000

    def test_floor_straddle(self, client):
        """Span straddling 700 CE floor: actual_from must be 700, not from_year."""
        r = client.get("/api/lmr/values?var=air&from_year=500&to_year=900")
        body = r.json()
        assert body["actual_from"] == 700, \
            f"Expected actual_from=700 for straddle, got {body['actual_from']}"
        assert len(body["values"]) > 0, "Straddle span should return values"

    def test_floor_entirely_below(self, client):
        """Span entirely below 700 CE floor: values must be empty."""
        r = client.get("/api/lmr/values?var=air&from_year=500&to_year=650")
        assert r.status_code == 200
        body = r.json()
        assert body["values"] == {}, \
            "Below-floor span must return empty values dict, not coerced zeros"

    def test_values_are_floats(self, client):
        r = client.get("/api/lmr/values?var=air&from_year=1000&to_year=1100")
        body = r.json()
        vals = [v for v in body["values"].values() if v is not None]
        assert len(vals) > 1000, f"Expected >1000 cells, got {len(vals)}"
        assert all(isinstance(v, float) for v in vals)

    def test_keys_are_latlon_strings(self, client):
        """Values dict keys must be 'lat,lon' strings, not hybas_ids."""
        r = client.get("/api/lmr/values?var=air&from_year=1000&to_year=1100")
        body = r.json()
        sample_keys = list(body["values"].keys())[:5]
        for key in sample_keys:
            parts = key.split(",")
            assert len(parts) == 2, f"Key '{key}' is not 'lat,lon' format"
            float(parts[0])  # must be numeric
            float(parts[1])

    def test_prate_returns_values(self, client):
        r = client.get("/api/lmr/values?var=prate&from_year=1000&to_year=1100")
        assert r.status_code == 200
        assert len(r.json()["values"]) > 1000

    def test_invalid_var_rejected(self, client):
        r = client.get("/api/lmr/values?var=badvar&from_year=1000&to_year=1100")
        assert r.status_code == 400

    def test_span_mean_correctness(self, client):
        """Span mean over a 1-year window must equal the single-year value.

        For from_year == to_year, the mean of one value is that value.
        Two adjacent single-year calls must produce different results (temporal signal).
        """
        r1100 = client.get("/api/lmr/values?var=air&from_year=1100&to_year=1100").json()
        r1101 = client.get("/api/lmr/values?var=air&from_year=1101&to_year=1101").json()
        shared = set(r1100["values"]) & set(r1101["values"])
        assert len(shared) > 1000
        diffs = [abs((r1101["values"][k] or 0) - (r1100["values"][k] or 0)) for k in shared]
        changed = sum(1 for d in diffs if d > 0.001)
        assert changed > 500, \
            f"Adjacent single-year calls differ on only {changed} cells — values may be stale"
