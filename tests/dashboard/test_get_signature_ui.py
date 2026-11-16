"""Get signature (WO-04 item 2): enabled only when the controls differ from the last successful run."""
from .test_handoff_ui import SETTLED, _arrive

TBILISI = "/dashboard?lat=41.6938&lon=44.8015&name=Tbilisi&v=1"
SONG = "/dashboard?scope=polity&polity=Northern%20Song&v=1"


def _disabled(page, id_):
    return page.evaluate(f"document.getElementById('{id_}').disabled")


def _run_and_wait(page, button):
    page.click(button)
    page.wait_for_selector("#v3-tab-sig-spin.d-none", state="attached", timeout=60000)   # the run has ended
    page.wait_for_function(SETTLED, timeout=60000)


def test_it_is_disabled_after_an_automatic_run(dashboard_server, page):
    _arrive(page, dashboard_server, TBILISI, "v3-tab-map-btn")
    assert _disabled(page, "v3-sig-btn")


def test_a_changed_parameter_enables_it_and_changing_back_disables_it(dashboard_server, page):
    _arrive(page, dashboard_server, TBILISI, "v3-tab-map-btn")
    page.uncheck("#v3-band-C")
    assert not _disabled(page, "v3-sig-btn")
    page.check("#v3-band-C")
    assert _disabled(page, "v3-sig-btn")


def test_applying_a_level_change_runs_once_and_disables_it_again(dashboard_server, page):
    _arrive(page, dashboard_server, TBILISI, "v3-tab-map-btn")
    before = page.inner_text("#v3-sig-content")
    page.select_option("#v3-level", "8")
    assert not _disabled(page, "v3-sig-btn")
    _run_and_wait(page, "#v3-sig-btn")
    assert _disabled(page, "v3-sig-btn")
    assert page.inner_text("#v3-sig-content") != before                      # the Signature tab now shows Level 08
    page.click("#v3-permalink-btn")
    assert "level=8" in page.input_value("#v3-permalink-url")                 # and the link follows the last run
    assert "active" in page.get_attribute("#v3-tab-sig-btn", "class")          # and the reader is shown what was asked for


def test_band_t_years_count_as_a_parameter(dashboard_server, page):
    _arrive(page, dashboard_server, TBILISI + "&bands=ABCDET&from_year=1150&to_year=1250", "v3-tab-map-btn")
    assert _disabled(page, "v3-sig-btn")
    page.fill("#v3-to-year", "1260")
    assert not _disabled(page, "v3-sig-btn")
    page.fill("#v3-to-year", "1250")
    assert _disabled(page, "v3-sig-btn")


def test_a_scope_change_clears_the_results_and_enables_it(dashboard_server, page):
    _arrive(page, dashboard_server, TBILISI, "v3-tab-map-btn")
    page.select_option("#v3-scope-select", "ring")
    assert not _disabled(page, "v3-sig-btn")
    assert page.evaluate("document.getElementById('v3-tab-profile-btn').classList.contains('disabled')")


def test_a_failed_first_run_leaves_it_enabled_for_a_retry(dashboard_server, page):
    page.route("**/api/areas*", lambda route: route.abort())
    page.goto(f"{dashboard_server}{TBILISI}", wait_until="load")
    page.wait_for_function("!document.getElementById('v3-handoff-alert').classList.contains('d-none')", timeout=30000)
    assert not _disabled(page, "v3-sig-btn")
    page.unroute("**/api/areas*")
    _run_and_wait(page, "#v3-sig-btn")
    assert _disabled(page, "v3-sig-btn")


def test_the_polity_button_follows_the_same_rule(dashboard_server, page):
    _arrive(page, dashboard_server, SONG, "v3-tab-map-btn")
    assert _disabled(page, "v3-polity-sig-btn")
    page.select_option("#v3-polity-level", "8")
    assert not _disabled(page, "v3-polity-sig-btn")
    page.select_option("#v3-polity-level", "6")
    assert _disabled(page, "v3-polity-sig-btn")
    page.click("#v3-btn-next")                                                # a later slice
    assert not _disabled(page, "v3-polity-sig-btn")
    _run_and_wait(page, "#v3-polity-sig-btn")
    assert _disabled(page, "v3-polity-sig-btn")


def _active(page, tab):
    return "active" in page.get_attribute(f"#v3-tab-{tab}-btn", "class")


def test_pressing_get_signature_from_the_map_shows_the_signature_tab(dashboard_server, page):
    _arrive(page, dashboard_server, TBILISI, "v3-tab-map-btn")
    page.select_option("#v3-level", "8")
    page.click("#v3-sig-btn")
    page.wait_for_selector("#v3-tab-sig-btn.active", timeout=10000)
    page.wait_for_function(SETTLED, timeout=60000)
    assert _active(page, "sig") and not _active(page, "map")


def test_pressing_get_signature_from_another_tab_shows_the_signature_tab(dashboard_server, page):
    _arrive(page, dashboard_server, TBILISI, "v3-tab-map-btn")
    page.click("#v3-tab-profile-btn")
    page.select_option("#v3-level", "8")
    page.click("#v3-sig-btn")
    page.wait_for_selector("#v3-tab-sig-btn.active", timeout=10000)
    page.wait_for_function(SETTLED, timeout=60000)
    assert not _active(page, "profile")


def test_a_failed_press_shows_the_signature_tab_and_leaves_the_button_enabled(dashboard_server, page):
    _arrive(page, dashboard_server, TBILISI, "v3-tab-map-btn")
    page.select_option("#v3-level", "8")
    page.route("**/api/areas*", lambda route: route.abort())
    page.click("#v3-sig-btn")
    page.wait_for_selector("#v3-tab-sig-btn.active", timeout=10000)
    page.wait_for_selector("#v3-tab-sig-spin.d-none", state="attached", timeout=30000)
    assert not _disabled(page, "v3-sig-btn")


def test_a_polity_press_after_a_slice_step_shows_the_signature_tab(dashboard_server, page):
    _arrive(page, dashboard_server, SONG, "v3-tab-map-btn")
    page.click("#v3-btn-next")
    assert not _disabled(page, "v3-polity-sig-btn")
    page.click("#v3-polity-sig-btn")
    page.wait_for_selector("#v3-tab-sig-btn.active", timeout=10000)
    page.wait_for_selector("#v3-tab-sig-spin.d-none", state="attached", timeout=90000)
    assert not _active(page, "map")
