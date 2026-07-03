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
    "v2-resolver-year",
    "v2-from-year",
    "v2-to-year",
    "v2-map",
    "v2-pane-sig",
    "v2-pane-analysis",
    "v2-intro",
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
    "ring|16.8167,-2.9833|Timbuktu",
    "polity|Northern Song|1000|1000|1100",
]

BANDS_CHECKED_ON_LOAD   = ["A", "B", "C", "D", "E"]
BANDS_UNCHECKED_ON_LOAD = ["T"]

SINGLE_BASIN_FIXTURE = "/dev/exemplars/01_single_basin_detail.json"
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
