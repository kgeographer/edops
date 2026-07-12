"""
tests/surface/test_sandbox_v3.py
---------------------------------
Structural tests for sandbox_v3.html (/sandbox/lookup3).

Step 1 (WO21): tab structure, cold-start control visibility, initial CSS state.
JS runtime behaviour is verified by Playwright tests (test_sandbox_v3_ui.py — WO21+).
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
    r = client.get("/sandbox/lookup3")
    assert r.status_code == 200
    return BeautifulSoup(r.text, "html.parser")


# ---------------------------------------------------------------------------
# Route
# ---------------------------------------------------------------------------

class TestRoute:
    def test_200(self, client):
        r = client.get("/sandbox/lookup3")
        assert r.status_code == 200
        assert "text/html" in r.headers["content-type"]

    def test_v2_still_200(self, client):
        """Confirm sandbox_v2 is untouched."""
        r = client.get("/sandbox/lookup2")
        assert r.status_code == 200


# ---------------------------------------------------------------------------
# Structure — fork tabs present
# ---------------------------------------------------------------------------

class TestForkTabs:
    def test_settlements_tab_present(self, page):
        el = page.find(id="v3-tab-settlements-btn")
        assert el is not None, "#v3-tab-settlements-btn missing"

    def test_polities_tab_present(self, page):
        el = page.find(id="v3-tab-polities-btn")
        assert el is not None, "#v3-tab-polities-btn missing"

    def test_settlements_tab_active_on_load(self, page):
        el = page.find(id="v3-tab-settlements-btn")
        assert "active" in el.get("class", []), "Settlements tab must be active on load"

    def test_polities_tab_not_active_on_load(self, page):
        el = page.find(id="v3-tab-polities-btn")
        assert "active" not in el.get("class", []), "Polities tab must not be active on load"

    def test_reset_button_present(self, page):
        el = page.find(id="v3-reset-btn")
        assert el is not None, "#v3-reset-btn missing"

    def test_settlements_pane_present(self, page):
        assert page.find(id="v3-pane-settlements") is not None

    def test_polities_pane_present(self, page):
        assert page.find(id="v3-pane-polities") is not None


# ---------------------------------------------------------------------------
# Settlements pane — required elements
# ---------------------------------------------------------------------------

SETTLEMENTS_REQUIRED_IDS = [
    "v3-level",
    "v3-place-input",
    "v3-resolve-btn",
    "v3-whg-status",
    "v3-whg-candidates",
    "v3-whg-chip",
    "v3-whg-name",
    "v3-whg-coords",
    "v3-whg-clear",
    "v3-example-row",
    "v3-example-select",
    "v3-scope-wrap",
    "v3-scope-select",
    "v3-buffer-extra",
    "v3-radius",
    "v3-band-checks",
    "v3-band-A", "v3-band-B", "v3-band-C", "v3-band-D", "v3-band-E", "v3-band-T",
    "v3-t-year-row",
    "v3-from-year",
    "v3-to-year",
    "v3-sig-btn",
]

class TestSettlementsElements:
    @pytest.mark.parametrize("el_id", SETTLEMENTS_REQUIRED_IDS)
    def test_element_present(self, page, el_id):
        assert page.find(id=el_id) is not None, f"#{el_id} not found"


# ---------------------------------------------------------------------------
# Polities pane — required elements
# ---------------------------------------------------------------------------

POLITIES_REQUIRED_IDS = [
    "v3-polity-input",
    "v3-polity-dropdown",
    "v3-polity-example-row",
    "v3-polity-example",
    "v3-slice-control",
    "v3-slice-slider",
    "v3-slice-label",
    "v3-btn-first",
    "v3-btn-prev",
    "v3-btn-play",
    "v3-btn-next",
    "v3-slice-select",
    "v3-resolver-year",
    "v3-polity-band-checks",
    "v3-polity-band-A", "v3-polity-band-B", "v3-polity-band-C",
    "v3-polity-band-D", "v3-polity-band-E", "v3-polity-band-T",
    "v3-polity-t-year-row",
    "v3-polity-from-year",
    "v3-polity-to-year",
    "v3-polity-sig-btn",
]

class TestPolitiesElements:
    @pytest.mark.parametrize("el_id", POLITIES_REQUIRED_IDS)
    def test_element_present(self, page, el_id):
        assert page.find(id=el_id) is not None, f"#{el_id} not found"


# ---------------------------------------------------------------------------
# Right column — required elements
# ---------------------------------------------------------------------------

RIGHT_COL_IDS = [
    "v3-tab-map-btn",
    "v3-tab-sig-btn",
    "v3-tab-analysis-btn",
    "v3-pane-map",
    "v3-pane-sig",
    "v3-pane-analysis",
    "v3-map",
    "v3-sig-content",
]

class TestRightColumn:
    @pytest.mark.parametrize("el_id", RIGHT_COL_IDS)
    def test_element_present(self, page, el_id):
        assert page.find(id=el_id) is not None, f"#{el_id} not found"

    def test_map_tab_active_on_load(self, page):
        el = page.find(id="v3-tab-map-btn")
        assert "active" in el.get("class", [])

    def test_sig_tab_disabled_on_load(self, page):
        el = page.find(id="v3-tab-sig-btn")
        assert "disabled" in el.get("class", [])

    def test_analysis_tab_disabled_on_load(self, page):
        el = page.find(id="v3-tab-analysis-btn")
        assert "disabled" in el.get("class", [])


# ---------------------------------------------------------------------------
# Cold-start CSS state — Settlements
# ---------------------------------------------------------------------------

class TestSettlementsColdStart:
    def test_scope_wrap_hidden(self, page):
        """Scope dropdown hidden at cold start — revealed after resolve."""
        el = page.find(id="v3-scope-wrap")
        assert "none" in (el.get("style") or ""), "#v3-scope-wrap must be display:none on load"

    def test_buffer_extra_hidden(self, page):
        el = page.find(id="v3-buffer-extra")
        assert "none" in (el.get("style") or ""), "#v3-buffer-extra must be display:none on load"

    def test_t_year_row_hidden(self, page):
        el = page.find(id="v3-t-year-row")
        assert "d-none" in el.get("class", []), "#v3-t-year-row must carry d-none on load"

    def test_whg_status_hidden(self, page):
        el = page.find(id="v3-whg-status")
        assert "none" in (el.get("style") or ""), "#v3-whg-status must be display:none on load"

    def test_whg_candidates_hidden(self, page):
        el = page.find(id="v3-whg-candidates")
        assert "none" in (el.get("style") or ""), "#v3-whg-candidates must be display:none on load"

    def test_whg_chip_hidden(self, page):
        el = page.find(id="v3-whg-chip")
        assert "d-none" in el.get("class", []), "#v3-whg-chip must carry d-none on load"

    def test_sig_btn_disabled(self, page):
        el = page.find(id="v3-sig-btn")
        assert el.has_attr("disabled"), "#v3-sig-btn must be disabled on load"

    def test_bands_a_e_checked(self, page):
        for band in ["A", "B", "C", "D", "E"]:
            el = page.find(id=f"v3-band-{band}")
            assert el.has_attr("checked"), f"#v3-band-{band} must be checked on load"

    def test_band_t_unchecked(self, page):
        el = page.find(id="v3-band-T")
        assert not el.has_attr("checked"), "#v3-band-T must be unchecked on load (Settlements)"

    def test_bands_not_disabled(self, page):
        """Settlements bands are interactive from cold start."""
        for band in ["A", "B", "C", "D", "E", "T"]:
            el = page.find(id=f"v3-band-{band}")
            assert not el.has_attr("disabled"), f"#v3-band-{band} must not be disabled on load"


# ---------------------------------------------------------------------------
# Cold-start CSS state — Polities
# ---------------------------------------------------------------------------

class TestPolitiesColdStart:
    def test_slice_select_disabled(self, page):
        """Time slice visible but disabled at cold start."""
        el = page.find(id="v3-slice-select")
        assert el.has_attr("disabled"), "#v3-slice-select must be disabled on load"

    def test_polity_sig_btn_disabled(self, page):
        el = page.find(id="v3-polity-sig-btn")
        assert el.has_attr("disabled"), "#v3-polity-sig-btn must be disabled on load"

    def test_polity_t_year_row_hidden(self, page):
        el = page.find(id="v3-polity-t-year-row")
        assert "d-none" in el.get("class", []), "#v3-polity-t-year-row must carry d-none on load"

    def test_polity_dropdown_hidden(self, page):
        el = page.find(id="v3-polity-dropdown")
        assert "none" in (el.get("style") or ""), "#v3-polity-dropdown must be display:none on load"

    def test_polity_bands_all_checked(self, page):
        """All bands pre-checked in Polities (T included)."""
        for band in ["A", "B", "C", "D", "E", "T"]:
            el = page.find(id=f"v3-polity-band-{band}")
            assert el.has_attr("checked"), f"#v3-polity-band-{band} must be checked on load"

    def test_polity_bands_all_disabled(self, page):
        """All Polities bands disabled at cold start."""
        for band in ["A", "B", "C", "D", "E", "T"]:
            el = page.find(id=f"v3-polity-band-{band}")
            assert el.has_attr("disabled"), f"#v3-polity-band-{band} must be disabled on load"


# ---------------------------------------------------------------------------
# Lower panel — choropleth
# ---------------------------------------------------------------------------

class TestLowerPanel:
    def test_intro_text_present(self, page):
        assert page.find(id="v3-intro-text") is not None

    def test_choropleth_hidden_on_load(self, page):
        """Variable select hidden at cold start — revealed on first scope render."""
        el = page.find(id="v3-choropleth")
        assert el is not None
        assert "none" in (el.get("style") or ""), "#v3-choropleth must be display:none on load"

    def test_basin_var_select_present(self, page):
        assert page.find(id="v3-basin-var") is not None

    def test_ring_info_hidden(self, page):
        el = page.find(id="v3-ring-info")
        assert "none" in (el.get("style") or ""), "#v3-ring-info must be display:none on load"


# ---------------------------------------------------------------------------
# WO22 — Level select (L06/L08)
# ---------------------------------------------------------------------------

class TestLevelSelect:
    """Level select controls are present and have correct cold-start state (WO22)."""

    def test_settlements_level_has_l06_option(self, page):
        el = page.find(id="v3-level")
        assert el is not None
        opts = [o.get("value") for o in el.find_all("option")]
        assert "6" in opts, "#v3-level must have L06 option"

    def test_settlements_level_has_l08_option(self, page):
        el = page.find(id="v3-level")
        opts = [o.get("value") for o in el.find_all("option")]
        assert "8" in opts, "#v3-level must have L08 option"

    def test_settlements_level_disabled_on_load(self, page):
        """Level select disabled until a place is resolved — enables in setResolvedPoint/example handler."""
        el = page.find(id="v3-level")
        assert el.has_attr("disabled"), "#v3-level must be disabled at cold start"

    def test_polity_level_has_l06_option(self, page):
        el = page.find(id="v3-polity-level")
        assert el is not None
        opts = [o.get("value") for o in el.find_all("option")]
        assert "6" in opts, "#v3-polity-level must have L06 option"

    def test_polity_level_has_l08_option(self, page):
        el = page.find(id="v3-polity-level")
        opts = [o.get("value") for o in el.find_all("option")]
        assert "8" in opts, "#v3-polity-level must have L08 option"

    def test_polity_level_disabled_on_load(self, page):
        """Polity level disabled until a polity is resolved (same gate as band checkboxes)."""
        el = page.find(id="v3-polity-level")
        assert el.has_attr("disabled"), "#v3-polity-level must be disabled at cold start"


# ---------------------------------------------------------------------------
# WO22 — /api/hyde/values level parameter (route contract)
# ---------------------------------------------------------------------------

class TestHydeValuesLevel:
    """Route accepts level param and dispatches to correct table (WO22)."""

    def test_l06_returns_200(self, client):
        r = client.get("/api/hyde/values?var=cropland&year=1000&level=6")
        assert r.status_code == 200

    def test_l08_returns_200(self, client):
        r = client.get("/api/hyde/values?var=cropland&year=1000&level=8")
        assert r.status_code == 200

    def test_l08_response_shape(self, client):
        r = client.get("/api/hyde/values?var=cropland&year=1000&level=8")
        body = r.json()
        assert "var" in body and "actual_year" in body and "values" in body

    def test_l08_basin_count(self, client):
        """L08 returns ~189k basins (190,675 total minus ~825 no-land basins)."""
        r = client.get("/api/hyde/values?var=cropland&year=1000&level=8")
        n = len(r.json()["values"])
        assert n > 180_000, f"Expected >180k L08 basins, got {n}"

    def test_l08_values_are_fractions(self, client):
        r = client.get("/api/hyde/values?var=cropland&year=1000&level=8")
        vals = [v for v in r.json()["values"].values() if v is not None]
        assert all(0.0 <= v <= 1.01 for v in vals)

    def test_invalid_level_rejected(self, client):
        r = client.get("/api/hyde/values?var=cropland&year=1000&level=9")
        assert r.status_code == 400
        assert "level" in r.json()["detail"].lower()

    def test_l06_and_l08_key_sets_differ(self, client):
        """L06 and L08 return distinct hybas_id sets — confirms different tables."""
        l06_keys = set(client.get("/api/hyde/values?var=cropland&year=1000&level=6").json()["values"].keys())
        l08_keys = set(client.get("/api/hyde/values?var=cropland&year=1000&level=8").json()["values"].keys())
        assert l06_keys != l08_keys, "L06 and L08 must return different hybas_id sets"
        assert len(l08_keys) > len(l06_keys), "L08 should have more basins than L06"
