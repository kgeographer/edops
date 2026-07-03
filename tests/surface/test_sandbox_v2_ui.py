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

class TestRenderer:

    @pytest.fixture(autouse=True)
    def require_fixture(self, live_server_url):
        import httpx
        r = httpx.get(f"{live_server_url}/dev/exemplars/01_single_basin_detail.json")
        if r.status_code != 200:
            pytest.skip("Exemplar fixture not available via live server")

    def test_get_signature_enables_sig_tab(self, page: Page, live_server_url):
        goto(page, live_server_url)
        select_scope(page, "single")
        page.click("#v2-sig-btn")
        page.wait_for_selector("#v2-sig-accordion")
        expect(page.locator("#v2-tab-sig-btn")).not_to_have_class(re.compile(r"\bdisabled\b"))

    def test_accordion_bands_rendered(self, page: Page, live_server_url):
        goto(page, live_server_url)
        select_scope(page, "single")
        page.click("#v2-sig-btn")
        page.wait_for_selector("#v2-sig-accordion")
        for band in ("A", "B", "C", "D", "E"):
            expect(page.locator(f"#v2-acc-{band}")).to_be_visible()

    def test_intro_hidden_after_render(self, page: Page, live_server_url):
        goto(page, live_server_url)
        select_scope(page, "single")
        page.click("#v2-sig-btn")
        page.wait_for_selector("#v2-sig-accordion")
        expect(page.locator("#v2-intro")).to_be_hidden()

    def test_hist_slot_present(self, page: Page, live_server_url):
        """area_weighted rows should carry the [hist] placeholder slot."""
        goto(page, live_server_url)
        select_scope(page, "single")
        page.click("#v2-sig-btn")
        page.wait_for_selector("#v2-sig-accordion")
        hist_slots = page.locator("text=[hist]")
        assert hist_slots.count() > 0
