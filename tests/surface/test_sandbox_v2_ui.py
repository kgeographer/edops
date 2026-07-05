"""
tests/surface/test_sandbox_v2_ui.py
-------------------------------------
Playwright browser tests for sandbox_v2.html JS behaviour.

These tests verify runtime state changes that TestClient + BeautifulSoup
cannot reach: scope gate show/hide, Band T toggle, example pre-fill, and
the renderer output in the DOM after Get signature is clicked.

All tests navigate to /sandbox/lookup2 on the session-scoped live server.
The `page` fixture is provided by pytest-playwright (function-scoped: a
fresh browser page per test).
"""

import re
import pytest
from pathlib import Path
from playwright.sync_api import Page, expect

PAGE_PATH = "/sandbox/lookup2"
EXEMPLAR_PATH = Path("output/edop/surface/exemplars/01_single_basin_detail.json")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def goto(page: Page, base_url: str) -> None:
    page.goto(f"{base_url}{PAGE_PATH}")


def select_scope(page: Page, value: str) -> None:
    page.select_option("#v2-scope-select", value)


# ---------------------------------------------------------------------------
# Initial state
# ---------------------------------------------------------------------------

class TestInitialStateUI:
    """On load, before any interaction."""

    def test_page_title(self, page: Page, live_server_url):
        goto(page, live_server_url)
        assert "EDOPS" in page.title()

    def test_scope_extras_hidden(self, page: Page, live_server_url):
        goto(page, live_server_url)
        for el_id in ("scope-extra-buffer", "scope-extra-polity", "scope-extra-draw"):
            expect(page.locator(f"#{el_id}")).to_be_hidden()

    def test_t_year_row_hidden(self, page: Page, live_server_url):
        goto(page, live_server_url)
        expect(page.locator("#v2-t-year-row")).to_be_hidden()

    def test_sig_button_disabled(self, page: Page, live_server_url):
        goto(page, live_server_url)
        expect(page.locator("#v2-sig-btn")).to_be_disabled()

    def test_point_section_visible(self, page: Page, live_server_url):
        goto(page, live_server_url)
        expect(page.locator("#v2-point-section")).to_be_visible()

    def test_signature_tab_disabled(self, page: Page, live_server_url):
        goto(page, live_server_url)
        expect(page.locator("#v2-tab-sig-btn")).to_have_class(re.compile(r"\bdisabled\b"))


# ---------------------------------------------------------------------------
# Scope gate
# ---------------------------------------------------------------------------

class TestScopeGate:

    def test_single_basin(self, page: Page, live_server_url):
        goto(page, live_server_url)
        select_scope(page, "single")
        expect(page.locator("#v2-point-section")).to_be_visible()
        expect(page.locator("#scope-extra-buffer")).to_be_hidden()
        expect(page.locator("#scope-extra-polity")).to_be_hidden()
        expect(page.locator("#scope-extra-draw")).to_be_hidden()
        expect(page.locator("#v2-sig-btn")).to_be_enabled()

    def test_buffer(self, page: Page, live_server_url):
        goto(page, live_server_url)
        select_scope(page, "buffer")
        expect(page.locator("#v2-point-section")).to_be_visible()
        expect(page.locator("#scope-extra-buffer")).to_be_visible()
        expect(page.locator("#scope-extra-polity")).to_be_hidden()
        expect(page.locator("#scope-extra-draw")).to_be_hidden()

    def test_ring(self, page: Page, live_server_url):
        goto(page, live_server_url)
        select_scope(page, "ring")
        expect(page.locator("#v2-point-section")).to_be_visible()
        expect(page.locator("#scope-extra-buffer")).to_be_hidden()
        expect(page.locator("#scope-extra-polity")).to_be_hidden()
        expect(page.locator("#scope-extra-draw")).to_be_hidden()

    def test_polity_hides_point_section(self, page: Page, live_server_url):
        goto(page, live_server_url)
        select_scope(page, "polity")
        expect(page.locator("#v2-point-section")).to_be_hidden()
        expect(page.locator("#scope-extra-polity")).to_be_visible()
        expect(page.locator("#scope-extra-buffer")).to_be_hidden()
        expect(page.locator("#scope-extra-draw")).to_be_hidden()

    def test_draw_hides_point_section(self, page: Page, live_server_url):
        goto(page, live_server_url)
        select_scope(page, "draw")
        expect(page.locator("#v2-point-section")).to_be_hidden()
        expect(page.locator("#scope-extra-draw")).to_be_visible()
        expect(page.locator("#scope-extra-buffer")).to_be_hidden()
        expect(page.locator("#scope-extra-polity")).to_be_hidden()

    def test_switching_scope_clears_previous_extra(self, page: Page, live_server_url):
        """Buffer extra shown, then switching to ring must hide it."""
        goto(page, live_server_url)
        select_scope(page, "buffer")
        expect(page.locator("#scope-extra-buffer")).to_be_visible()
        select_scope(page, "ring")
        expect(page.locator("#scope-extra-buffer")).to_be_hidden()


# ---------------------------------------------------------------------------
# Band T toggle
# ---------------------------------------------------------------------------

class TestBandTToggle:

    def test_check_shows_year_row(self, page: Page, live_server_url):
        goto(page, live_server_url)
        expect(page.locator("#v2-t-year-row")).to_be_hidden()
        page.check("#v2-band-T")
        expect(page.locator("#v2-t-year-row")).to_be_visible()

    def test_uncheck_hides_year_row(self, page: Page, live_server_url):
        goto(page, live_server_url)
        page.check("#v2-band-T")
        expect(page.locator("#v2-t-year-row")).to_be_visible()
        page.uncheck("#v2-band-T")
        expect(page.locator("#v2-t-year-row")).to_be_hidden()


# ---------------------------------------------------------------------------
# Example pre-fill
# ---------------------------------------------------------------------------

class TestExamplePrefill:

    def test_timbuktu_single(self, page: Page, live_server_url):
        goto(page, live_server_url)
        page.select_option("#v2-example-select", "single|16.8167,-2.9833|Timbuktu")
        expect(page.locator("#v2-scope-select")).to_have_value("single")
        expect(page.locator("#v2-place-input")).to_have_value("Timbuktu")

    def test_timbuktu_buffer(self, page: Page, live_server_url):
        goto(page, live_server_url)
        page.select_option("#v2-example-select", "buffer|16.8167,-2.9833|Timbuktu|100")
        expect(page.locator("#v2-scope-select")).to_have_value("buffer")
        expect(page.locator("#v2-radius")).to_have_value("100")

    def test_nsong_polity(self, page: Page, live_server_url):
        goto(page, live_server_url)
        page.select_option("#v2-example-select", "polity|Northern Song|1000|1000|1100")
        expect(page.locator("#v2-scope-select")).to_have_value("polity")
        expect(page.locator("#v2-polity-input")).to_have_value("Northern Song")
        expect(page.locator("#v2-resolver-year")).to_have_value("1000")
        expect(page.locator("#v2-band-T")).to_be_checked()
        expect(page.locator("#v2-from-year")).to_have_value("1000")
        expect(page.locator("#v2-to-year")).to_have_value("1100")
        expect(page.locator("#v2-t-year-row")).to_be_visible()

    def test_example_resets_dropdown(self, page: Page, live_server_url):
        """Dropdown resets to empty after selection so it can be re-used."""
        goto(page, live_server_url)
        page.select_option("#v2-example-select", "single|16.8167,-2.9833|Timbuktu")
        expect(page.locator("#v2-example-select")).to_have_value("")


# ---------------------------------------------------------------------------
# Renderer — requires exemplar fixture served at /dev/exemplars/
# ---------------------------------------------------------------------------

def load_timbuktu_single(page: Page, base_url: str) -> None:
    """Select the Timbuktu single-basin example (sets lat/lon) and click Get signature."""
    goto(page, base_url)
    page.select_option("#v2-example-select", "single|16.8167,-2.9833|Timbuktu")
    page.click("#v2-sig-btn")
    # After WO12 Map-first landing, the accordion is rendered but in a hidden tab pane.
    page.wait_for_selector("#v2-sig-accordion", state="attached", timeout=15000)


class TestRenderer:

    @pytest.fixture(autouse=True)
    def require_db(self, live_server_url):
        import httpx
        r = httpx.get(
            f"{live_server_url}/api/areas?type=single_basin&lat=16.8167&lon=-2.9833&bands=A",
            timeout=10,
        )
        if r.status_code != 200:
            pytest.skip("Single-basin live endpoint not available")

    def test_get_signature_enables_sig_tab(self, page: Page, live_server_url):
        load_timbuktu_single(page, live_server_url)
        expect(page.locator("#v2-tab-sig-btn")).not_to_have_class(re.compile(r"\bdisabled\b"))

    def test_accordion_bands_rendered(self, page: Page, live_server_url):
        """A–E are collapsed by default (present in DOM, not visible); T absent without span."""
        load_timbuktu_single(page, live_server_url)
        for band in ("A", "B", "C", "D", "E"):
            expect(page.locator(f"#v2-acc-{band}")).to_be_hidden()

    def test_intro_hidden_after_render(self, page: Page, live_server_url):
        load_timbuktu_single(page, live_server_url)
        expect(page.locator("#v2-intro")).to_be_hidden()

    def test_histogram_widget_present(self, page: Page, live_server_url):
        """area_weighted rows should render SVG histogram widgets."""
        load_timbuktu_single(page, live_server_url)
        assert page.locator("#v2-sig-accordion svg").count() > 0


# ---------------------------------------------------------------------------
# WO11 — single-basin map layer
# ---------------------------------------------------------------------------

class TestSingleBasinMapLayer:

    @pytest.fixture(autouse=True)
    def require_db(self, live_server_url):
        import httpx
        r = httpx.get(
            f"{live_server_url}/api/areas?type=single_basin&lat=16.8167&lon=-2.9833&bands=A",
            timeout=10,
        )
        if r.status_code != 200:
            pytest.skip("Single-basin live endpoint not available")

    def test_single_basin_shell_layer_present(self, page: Page, live_server_url):
        """After loading Timbuktu single-basin, the shell source should be registered."""
        load_timbuktu_single(page, live_server_url)
        sources = page.evaluate("() => Object.keys(window.v2map.getStyle().sources)")
        assert "src-single-basin" in sources, f"src-single-basin not in map sources: {sources}"

    def test_single_basin_layer_is_polygon(self, page: Page, live_server_url):
        """The single-basin source must be a polygon-type GeoJSON feature (not a point or line)."""
        load_timbuktu_single(page, live_server_url)
        geom_type = page.evaluate(
            "() => window.v2map.getSource('src-single-basin')._data.geometry.type"
        )
        assert geom_type in ("Polygon", "MultiPolygon"), f"Expected polygon type, got {geom_type}"


# ---------------------------------------------------------------------------
# WO12 — Map-first landing, buffer geometry, ring placeholder
# ---------------------------------------------------------------------------

def load_timbuktu_buffer(page: Page, base_url: str) -> None:
    """Select the Timbuktu buffer example and click Get signature."""
    goto(page, base_url)
    page.select_option("#v2-example-select", "buffer|16.8167,-2.9833|Timbuktu|100")
    page.click("#v2-sig-btn")
    page.wait_for_selector("#v2-sig-accordion", state="attached", timeout=15000)


class TestMapFirstLanding:

    @pytest.fixture(autouse=True)
    def require_db(self, live_server_url):
        import httpx
        r = httpx.get(
            f"{live_server_url}/api/areas?type=single_basin&lat=16.8167&lon=-2.9833&bands=A",
            timeout=10,
        )
        if r.status_code != 200:
            pytest.skip("Live endpoint not available")

    def test_single_lands_on_map_tab(self, page: Page, live_server_url):
        """After Get signature (single), Map tab should be active."""
        load_timbuktu_single(page, live_server_url)
        active = page.evaluate(
            "() => document.getElementById('v2-tab-map-btn').classList.contains('active')"
        )
        assert active, "Map tab not active after single-basin sig load"

    def test_buffer_lands_on_map_tab(self, page: Page, live_server_url):
        """After Get signature (buffer), Map tab should be active."""
        load_timbuktu_buffer(page, live_server_url)
        active = page.evaluate(
            "() => document.getElementById('v2-tab-map-btn').classList.contains('active')"
        )
        assert active, "Map tab not active after buffer sig load"

    def test_sig_accordion_still_reachable(self, page: Page, live_server_url):
        """Signature tab must be reachable and populated after Map-first landing."""
        load_timbuktu_single(page, live_server_url)
        page.click("#v2-tab-sig-btn")
        expect(page.locator("#v2-sig-accordion")).to_be_visible()


class TestBufferMapLayers:

    @pytest.fixture(autouse=True)
    def require_db(self, live_server_url):
        import httpx
        r = httpx.get(
            f"{live_server_url}/api/areas?type=buffer&lat=16.8167&lon=-2.9833&radius_km=100&bands=A",
            timeout=10,
        )
        if r.status_code != 200:
            pytest.skip("Buffer live endpoint not available")

    def test_buffer_basins_source_present(self, page: Page, live_server_url):
        load_timbuktu_buffer(page, live_server_url)
        sources = page.evaluate("() => Object.keys(window.v2map.getStyle().sources)")
        assert "src-buffer-basins" in sources, f"src-buffer-basins not in sources: {sources}"

    def test_buffer_circle_source_present(self, page: Page, live_server_url):
        load_timbuktu_buffer(page, live_server_url)
        sources = page.evaluate("() => Object.keys(window.v2map.getStyle().sources)")
        assert "src-buffer-circle" in sources, f"src-buffer-circle not in sources: {sources}"

    def test_buffer_basins_is_feature_collection(self, page: Page, live_server_url):
        load_timbuktu_buffer(page, live_server_url)
        fc_type = page.evaluate(
            "() => window.v2map.getSource('src-buffer-basins')._data.type"
        )
        assert fc_type == "FeatureCollection", f"Expected FeatureCollection, got {fc_type}"

    def test_buffer_member_count_matches_sig(self, page: Page, live_server_url):
        """Basin count on the map must equal n_units from the signature payload."""
        load_timbuktu_buffer(page, live_server_url)
        result = page.evaluate("""() => {
            const fc = window.v2map.getSource('src-buffer-basins')._data;
            return fc.features.length;
        }""")
        assert result == 9, f"Expected 9 buffer basins (Timbuktu 100 km), got {result}"


class TestRingParksCleanly:

    def test_ring_sig_btn_enabled(self, page: Page, live_server_url):
        """Selecting ring scope must enable the Get signature button."""
        goto(page, live_server_url)
        select_scope(page, "ring")
        expect(page.locator("#v2-sig-btn")).to_be_enabled()

    def test_ring_click_shows_placeholder(self, page: Page, live_server_url):
        """Clicking Get signature with ring scope must show a placeholder, not an error."""
        goto(page, live_server_url)
        page.select_option("#v2-example-select", "single|16.8167,-2.9833|Timbuktu")
        select_scope(page, "ring")
        page.click("#v2-sig-btn")
        pane = page.locator("#v2-pane-sig")
        pane.wait_for(state="visible", timeout=5000)
        text = pane.inner_text()
        assert "WO13" in text, f"Expected WO13 placeholder in ring pane, got: {text!r}"
        assert "Error" not in text, "Ring click should not produce an error"
