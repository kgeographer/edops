"""
tests/surface/test_sandbox_v3_ui.py
-------------------------------------
Playwright browser tests for sandbox_v3.html JS state machine.

Covers the WO21 accept gate:
  - Cold-start control visibility (Settlements + Polities tabs)
  - Reveal-on-example: scope gate appears, alternate entry locks
  - Tab-switch hard reset: abandoned tab returns to cold start
  - Reset button: current tab returns to cold start
  - Variable select hidden at cold start, visible after scope render
  - Band T toggle on Settlements tab
  - Polities example reveal (DB-dependent: slices, bands, T auto-tick)

WHG resolve path requires a live WHG API call and is not tested here.
Polities DB-dependent tests are guarded by a require_db fixture.
"""

import re
import pytest
import httpx
from playwright.sync_api import Page, expect

PAGE_PATH = "/sandbox/lookup3"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def goto(page: Page, base_url: str) -> None:
    page.goto(f"{base_url}{PAGE_PATH}")


def click_polities_tab(page: Page) -> None:
    page.click("#v3-tab-polities-btn")
    expect(page.locator("#v3-tab-polities-btn")).to_have_class(re.compile(r"\bactive\b"))


def click_settlements_tab(page: Page) -> None:
    page.click("#v3-tab-settlements-btn")
    expect(page.locator("#v3-tab-settlements-btn")).to_have_class(re.compile(r"\bactive\b"))


def select_settlements_example(page: Page, value: str) -> None:
    click_settlements_tab(page)
    page.select_option("#v3-example-select", value)


# ---------------------------------------------------------------------------
# Settlements cold start
# ---------------------------------------------------------------------------

class TestV3SettlementsColdStart:
    """On load: Polities tab active by default; nothing resolved."""

    def test_polities_tab_active(self, page: Page, live_server_url):
        goto(page, live_server_url)
        expect(page.locator("#v3-tab-polities-btn")).to_have_class(re.compile(r"\bactive\b"))

    def test_scope_wrap_hidden(self, page: Page, live_server_url):
        goto(page, live_server_url)
        expect(page.locator("#v3-scope-wrap")).to_be_hidden()

    def test_sig_btn_disabled(self, page: Page, live_server_url):
        goto(page, live_server_url)
        expect(page.locator("#v3-sig-btn")).to_be_disabled()

    def test_sig_tab_disabled(self, page: Page, live_server_url):
        goto(page, live_server_url)
        expect(page.locator("#v3-tab-sig-btn")).to_have_class(re.compile(r"\bdisabled\b"))

    def test_whg_chip_hidden(self, page: Page, live_server_url):
        goto(page, live_server_url)
        expect(page.locator("#v3-whg-chip")).to_be_hidden()

    def test_choropleth_hidden(self, page: Page, live_server_url):
        goto(page, live_server_url)
        expect(page.locator("#v3-choropleth")).to_be_hidden()

    def test_intro_text_visible(self, page: Page, live_server_url):
        goto(page, live_server_url)
        expect(page.locator("#v3-intro-text")).to_be_visible()

    def test_example_row_visible(self, page: Page, live_server_url):
        goto(page, live_server_url)
        click_settlements_tab(page)
        expect(page.locator("#v3-example-row")).to_be_visible()

    def test_t_year_row_hidden(self, page: Page, live_server_url):
        goto(page, live_server_url)
        expect(page.locator("#v3-t-year-row")).to_be_hidden()

    def test_buffer_extra_hidden(self, page: Page, live_server_url):
        goto(page, live_server_url)
        expect(page.locator("#v3-buffer-extra")).to_be_hidden()


# ---------------------------------------------------------------------------
# Polities cold start
# ---------------------------------------------------------------------------

class TestV3PolitiesColdStart:
    """Polities tab state before any interaction."""

    def test_slice_select_disabled(self, page: Page, live_server_url):
        goto(page, live_server_url)
        click_polities_tab(page)
        expect(page.locator("#v3-slice-select")).to_be_disabled()

    def test_polity_sig_btn_disabled(self, page: Page, live_server_url):
        goto(page, live_server_url)
        click_polities_tab(page)
        expect(page.locator("#v3-polity-sig-btn")).to_be_disabled()

    def test_bands_all_disabled(self, page: Page, live_server_url):
        """All six band checkboxes are disabled at Polities cold start."""
        goto(page, live_server_url)
        click_polities_tab(page)
        for band in ("A", "B", "C", "D", "E", "T"):
            expect(page.locator(f"#v3-polity-band-{band}")).to_be_disabled()

    def test_t_year_row_hidden(self, page: Page, live_server_url):
        goto(page, live_server_url)
        click_polities_tab(page)
        expect(page.locator("#v3-polity-t-year-row")).to_be_hidden()

    def test_polity_input_enabled(self, page: Page, live_server_url):
        """Search input starts enabled — user can type immediately."""
        goto(page, live_server_url)
        click_polities_tab(page)
        expect(page.locator("#v3-polity-input")).to_be_enabled()


# ---------------------------------------------------------------------------
# Settlements example reveal
# ---------------------------------------------------------------------------

class TestV3SettlementsExampleReveal:
    """Selecting an example commits the path and reveals scope controls."""

    def test_scope_wrap_appears(self, page: Page, live_server_url):
        goto(page, live_server_url)
        select_settlements_example(page, "single|16.8167,-2.9833|Timbuktu")
        expect(page.locator("#v3-scope-wrap")).to_be_visible()

    def test_sig_btn_enabled(self, page: Page, live_server_url):
        goto(page, live_server_url)
        select_settlements_example(page, "single|16.8167,-2.9833|Timbuktu")
        expect(page.locator("#v3-sig-btn")).to_be_enabled()

    def test_choropleth_appears(self, page: Page, live_server_url):
        """Variable select is hidden at cold start, visible after scope render."""
        goto(page, live_server_url)
        expect(page.locator("#v3-choropleth")).to_be_hidden()
        select_settlements_example(page, "single|16.8167,-2.9833|Timbuktu")
        expect(page.locator("#v3-choropleth")).to_be_visible()

    def test_intro_text_hidden(self, page: Page, live_server_url):
        goto(page, live_server_url)
        select_settlements_example(page, "single|16.8167,-2.9833|Timbuktu")
        expect(page.locator("#v3-intro-text")).to_be_hidden()

    def test_resolve_field_locked(self, page: Page, live_server_url):
        """Example path removes the alternate entry: resolve input disabled."""
        goto(page, live_server_url)
        select_settlements_example(page, "single|16.8167,-2.9833|Timbuktu")
        expect(page.locator("#v3-place-input")).to_be_disabled()

    def test_resolve_btn_locked(self, page: Page, live_server_url):
        goto(page, live_server_url)
        select_settlements_example(page, "single|16.8167,-2.9833|Timbuktu")
        expect(page.locator("#v3-resolve-btn")).to_be_disabled()

    def test_scope_defaults_to_single(self, page: Page, live_server_url):
        goto(page, live_server_url)
        select_settlements_example(page, "single|16.8167,-2.9833|Timbuktu")
        expect(page.locator("#v3-scope-select")).to_have_value("single")

    def test_buffer_example_shows_radius(self, page: Page, live_server_url):
        goto(page, live_server_url)
        select_settlements_example(page, "buffer|16.8167,-2.9833|Timbuktu|100")
        expect(page.locator("#v3-scope-select")).to_have_value("buffer")
        expect(page.locator("#v3-buffer-extra")).to_be_visible()

    def test_ring_example_checks_band_T(self, page: Page, live_server_url):
        goto(page, live_server_url)
        select_settlements_example(page, "ring|16.8167,-2.9833|Timbuktu|1400|1500")
        expect(page.locator("#v3-band-T")).to_be_checked()
        expect(page.locator("#v3-from-year")).to_have_value("1400")
        expect(page.locator("#v3-to-year")).to_have_value("1500")
        expect(page.locator("#v3-t-year-row")).to_be_visible()


# ---------------------------------------------------------------------------
# Band T toggle (Settlements)
# ---------------------------------------------------------------------------

class TestV3BandTToggle:

    def test_check_shows_year_row(self, page: Page, live_server_url):
        goto(page, live_server_url)
        click_settlements_tab(page)
        expect(page.locator("#v3-t-year-row")).to_be_hidden()
        page.check("#v3-band-T")
        expect(page.locator("#v3-t-year-row")).to_be_visible()

    def test_uncheck_hides_year_row(self, page: Page, live_server_url):
        goto(page, live_server_url)
        click_settlements_tab(page)
        page.check("#v3-band-T")
        page.uncheck("#v3-band-T")
        expect(page.locator("#v3-t-year-row")).to_be_hidden()


# ---------------------------------------------------------------------------
# Tab-switch hard reset
# ---------------------------------------------------------------------------

class TestV3TabSwitchReset:
    """Switching tabs hard-resets the abandoned tab to cold start."""

    def test_polities_tab_resets_settlements_scope(self, page: Page, live_server_url):
        """Settlements with example selected → switch to Polities → scope wrap clears."""
        goto(page, live_server_url)
        select_settlements_example(page, "single|16.8167,-2.9833|Timbuktu")
        expect(page.locator("#v3-scope-wrap")).to_be_visible()
        click_polities_tab(page)
        click_settlements_tab(page)
        expect(page.locator("#v3-scope-wrap")).to_be_hidden()

    def test_polities_tab_resets_settlements_sig_btn(self, page: Page, live_server_url):
        goto(page, live_server_url)
        select_settlements_example(page, "single|16.8167,-2.9833|Timbuktu")
        click_polities_tab(page)
        click_settlements_tab(page)
        expect(page.locator("#v3-sig-btn")).to_be_disabled()

    def test_polities_tab_resets_settlements_choropleth(self, page: Page, live_server_url):
        goto(page, live_server_url)
        select_settlements_example(page, "single|16.8167,-2.9833|Timbuktu")
        expect(page.locator("#v3-choropleth")).to_be_visible()
        click_polities_tab(page)
        click_settlements_tab(page)
        expect(page.locator("#v3-choropleth")).to_be_hidden()

    def test_polities_tab_unlocks_resolve_input(self, page: Page, live_server_url):
        """Resolve input re-enables and empties after tab-switch reset."""
        goto(page, live_server_url)
        select_settlements_example(page, "single|16.8167,-2.9833|Timbuktu")
        expect(page.locator("#v3-place-input")).to_be_disabled()
        click_polities_tab(page)
        click_settlements_tab(page)
        expect(page.locator("#v3-place-input")).to_be_enabled()
        expect(page.locator("#v3-place-input")).to_have_value("")

    def test_settlements_tab_resets_polities_slice_select(self, page: Page, live_server_url):
        """Switch Polities → Settlements → back to Polities: slice-select still disabled."""
        goto(page, live_server_url)
        click_polities_tab(page)
        click_settlements_tab(page)
        click_polities_tab(page)
        expect(page.locator("#v3-slice-select")).to_be_disabled()

    def test_settlements_tab_resets_polities_sig_btn(self, page: Page, live_server_url):
        goto(page, live_server_url)
        click_polities_tab(page)
        click_settlements_tab(page)
        click_polities_tab(page)
        expect(page.locator("#v3-polity-sig-btn")).to_be_disabled()


# ---------------------------------------------------------------------------
# Reset button
# ---------------------------------------------------------------------------

class TestV3ResetButton:

    def test_reset_hides_scope_wrap(self, page: Page, live_server_url):
        goto(page, live_server_url)
        select_settlements_example(page, "single|16.8167,-2.9833|Timbuktu")
        page.click("#v3-reset-btn")
        expect(page.locator("#v3-scope-wrap")).to_be_hidden()

    def test_reset_disables_sig_btn(self, page: Page, live_server_url):
        goto(page, live_server_url)
        select_settlements_example(page, "single|16.8167,-2.9833|Timbuktu")
        page.click("#v3-reset-btn")
        expect(page.locator("#v3-sig-btn")).to_be_disabled()

    def test_reset_hides_choropleth(self, page: Page, live_server_url):
        goto(page, live_server_url)
        select_settlements_example(page, "single|16.8167,-2.9833|Timbuktu")
        page.click("#v3-reset-btn")
        expect(page.locator("#v3-choropleth")).to_be_hidden()

    def test_reset_shows_intro_text(self, page: Page, live_server_url):
        goto(page, live_server_url)
        select_settlements_example(page, "single|16.8167,-2.9833|Timbuktu")
        page.click("#v3-reset-btn")
        expect(page.locator("#v3-intro-text")).to_be_visible()

    def test_reset_unlocks_resolve_input(self, page: Page, live_server_url):
        goto(page, live_server_url)
        select_settlements_example(page, "single|16.8167,-2.9833|Timbuktu")
        page.click("#v3-reset-btn")
        expect(page.locator("#v3-place-input")).to_be_enabled()
        expect(page.locator("#v3-place-input")).to_have_value("")

    def test_reset_re_enables_example_select(self, page: Page, live_server_url):
        goto(page, live_server_url)
        select_settlements_example(page, "single|16.8167,-2.9833|Timbuktu")
        page.click("#v3-reset-btn")
        expect(page.locator("#v3-example-select")).to_be_enabled()

    def test_reset_on_polities_tab_clears_slice_select(self, page: Page, live_server_url):
        """Reset button on Polities tab calls resetPolities."""
        goto(page, live_server_url)
        click_polities_tab(page)
        page.click("#v3-reset-btn")
        expect(page.locator("#v3-slice-select")).to_be_disabled()
        expect(page.locator("#v3-polity-sig-btn")).to_be_disabled()


# ---------------------------------------------------------------------------
# Polities example reveal — requires live DB (/api/polity/slices)
# ---------------------------------------------------------------------------

class TestV3PolitiesExampleReveal:
    """Northern Song example triggers selectPolity → slices loaded → bands enabled."""

    @pytest.fixture(autouse=True)
    def require_db(self, live_server_url):
        r = httpx.get(
            f"{live_server_url}/api/polity/slices?name=Northern+Song", timeout=10
        )
        if r.status_code != 200:
            pytest.skip("Polity slices endpoint not available")

    def _load_nsong(self, page: Page, live_server_url: str) -> None:
        goto(page, live_server_url)
        click_polities_tab(page)
        page.select_option("#v3-polity-example", "polity|Northern Song")
        # Wait for async slices fetch to complete
        page.wait_for_function(
            "document.getElementById('v3-slice-select').options.length > 1",
            timeout=10000,
        )

    def test_slice_select_enabled(self, page: Page, live_server_url):
        self._load_nsong(page, live_server_url)
        expect(page.locator("#v3-slice-select")).to_be_enabled()

    def test_bands_enabled(self, page: Page, live_server_url):
        self._load_nsong(page, live_server_url)
        for band in ("A", "B", "C", "D", "E", "T"):
            expect(page.locator(f"#v3-polity-band-{band}")).to_be_enabled()

    def test_band_T_auto_checked(self, page: Page, live_server_url):
        """T is auto-ticked for polities — a polity has a mandatory span."""
        self._load_nsong(page, live_server_url)
        expect(page.locator("#v3-polity-band-T")).to_be_checked()

    def test_t_year_row_hidden(self, page: Page, live_server_url):
        """Year row stays hidden on Polities tab — span is the slice's own span."""
        self._load_nsong(page, live_server_url)
        expect(page.locator("#v3-polity-t-year-row")).to_be_hidden()

    def test_slice_control_visible(self, page: Page, live_server_url):
        """Slider control div is revealed after polity loads."""
        self._load_nsong(page, live_server_url)
        expect(page.locator("#v3-slice-control")).to_be_visible()

    def test_slice_label_populated(self, page: Page, live_server_url):
        """Slice label shows ordinal and year span after polity loads."""
        self._load_nsong(page, live_server_url)
        label = page.locator("#v3-slice-label").text_content()
        assert "Slice" in label and "of" in label

    def test_t_span_filled_from_polity_lifespan(self, page: Page, live_server_url):
        """Band T span mirrors the active slice (zero-width slices are valid)."""
        self._load_nsong(page, live_server_url)
        from_yr = int(page.locator("#v3-polity-from-year").input_value())
        to_yr   = int(page.locator("#v3-polity-to-year").input_value())
        assert from_yr <= to_yr

    def test_search_input_locked(self, page: Page, live_server_url):
        """Example path removes the alternate entry: search input is disabled."""
        goto(page, live_server_url)
        click_polities_tab(page)
        page.select_option("#v3-polity-example", "polity|Northern Song")
        # Disabled synchronously before the async fetch
        expect(page.locator("#v3-polity-input")).to_be_disabled()

    def test_polity_level_enabled_after_resolve(self, page: Page, live_server_url):
        """Level select is disabled at cold start and enabled after polity resolves (WO22)."""
        goto(page, live_server_url)
        click_polities_tab(page)
        expect(page.locator("#v3-polity-level")).to_be_disabled()
        page.select_option("#v3-polity-example", "polity|Northern Song")
        page.wait_for_function(
            "document.getElementById('v3-slice-select').options.length > 1",
            timeout=10000,
        )
        expect(page.locator("#v3-polity-level")).to_be_enabled()


# ---------------------------------------------------------------------------
# WO22 — Level select (Settlements tab)
# ---------------------------------------------------------------------------

class TestV3LevelSelect:
    """Level select cold-start state and enable/disable lifecycle (WO22)."""

    def test_level_select_disabled_on_load(self, page: Page, live_server_url):
        """Level select disabled at cold start — no place resolved yet."""
        goto(page, live_server_url)
        expect(page.locator("#v3-level")).to_be_disabled()

    def test_level_select_default_l06(self, page: Page, live_server_url):
        goto(page, live_server_url)
        expect(page.locator("#v3-level")).to_have_value("6")

    def test_level_select_enabled_after_example(self, page: Page, live_server_url):
        """Level select becomes interactive and is set to L06 when an example loads."""
        goto(page, live_server_url)
        select_settlements_example(page, "single|16.8167,-2.9833|Timbuktu")
        expect(page.locator("#v3-level")).to_be_enabled()
        expect(page.locator("#v3-level")).to_have_value("6")

    def test_polity_level_disabled_on_load(self, page: Page, live_server_url):
        goto(page, live_server_url)
        click_polities_tab(page)
        expect(page.locator("#v3-polity-level")).to_be_disabled()

    def test_reset_returns_level_to_l06_and_disabled(self, page: Page, live_server_url):
        """Reset restores level to L06 and disables the select."""
        goto(page, live_server_url)
        select_settlements_example(page, "single|16.8167,-2.9833|Timbuktu")
        page.select_option("#v3-level", "8")
        page.click("#v3-reset-btn")
        expect(page.locator("#v3-level")).to_have_value("6")
        expect(page.locator("#v3-level")).to_be_disabled()

    def test_polity_reset_disables_level(self, page: Page, live_server_url):
        """Reset on Polities tab disables and resets polity level select."""
        goto(page, live_server_url)
        click_polities_tab(page)
        page.click("#v3-reset-btn")
        expect(page.locator("#v3-polity-level")).to_be_disabled()
        expect(page.locator("#v3-polity-level")).to_have_value("6")
