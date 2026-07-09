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
