"""The Atlas moved from the Dashboard to the Data Explorer (WO-09): a fourth Explorer tab, gone from the Dashboard."""
import pytest

pytestmark = pytest.mark.dashboard


def test_the_dashboard_no_longer_has_an_atlas(dashboard_server, page):
    page.goto(dashboard_server + "/dashboard", wait_until="load")
    assert page.locator("#v3-tab-atlas-btn, #v3-pane-atlas, #v3-left-atlas").count() == 0
    parsed = page.evaluate("EdopsPermalink.parse('?lat=10&lon=20&view=atlas')")      # a link to the old tab is no longer a valid view
    assert any("view must be one of" in e for e in parsed["errors"])


def test_the_explorer_has_an_atlas_tab_that_swaps_the_left_column(dashboard_server, page):
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto(dashboard_server + "/explorer", wait_until="load")
    assert page.locator("#ex-tabs .nav-link").all_inner_texts() == ["Global", "Regions", "Compare", "Atlas"]
    assert page.is_visible("#ex-search-box") and page.is_visible("#ex-controls")
    page.click("#ex-tab-atlas")
    page.wait_for_selector("#ex-pane-atlas.active")
    assert page.is_visible("#ex-left-atlas") and not page.is_visible("#ex-search-box") and not page.is_visible("#ex-controls")
    page.wait_for_selector("#ex-atlas-legend span", timeout=60000)           # the classes were painted and the legend drawn
    assert page.inner_text("#ex-atlas-title") == "Modality — all classes"
    assert "Every basin coloured by how its rainfall is spread" in page.inner_text("#ex-atlas-info")
    page.click("#ex-tab-global")
    page.wait_for_selector("#ex-pane-global.active")
    assert page.is_visible("#ex-search-box") and page.is_visible("#ex-controls") and not page.is_visible("#ex-left-atlas")
    assert errors == []


def test_the_atlas_views_change_the_title_and_legend(dashboard_server, page):
    page.goto(dashboard_server + "/explorer", wait_until="load")
    page.click("#ex-tab-atlas")
    page.wait_for_selector("#ex-atlas-legend span", timeout=60000)
    page.select_option("#ex-atlas-view", "twin")
    page.wait_for_function("document.getElementById('ex-atlas-title').textContent === 'Two wet seasons'", timeout=60000)
    page.wait_for_function("document.getElementById('ex-atlas-legend').innerText.includes('basins')", timeout=60000)


def test_inactive_explorer_panes_take_no_space_so_the_atlas_map_sits_under_its_controls(dashboard_server, page):
    page.goto(dashboard_server + "/explorer", wait_until="load")
    page.click("#ex-tab-atlas")
    page.wait_for_selector("#ex-atlas-legend span", timeout=60000)
    assert page.evaluate("getComputedStyle(document.getElementById('ex-pane-compare')).display") == "none"
    tabs = page.locator("#ex-tabs").bounding_box()
    atlas_map = page.locator("#ex-atlas-map").bounding_box()
    assert atlas_map["y"] - (tabs["y"] + tabs["height"]) < 200            # the title and legend, not a 500 px gap


def test_the_compare_tab_still_lays_out_when_opened(dashboard_server, page):
    page.goto(dashboard_server + "/explorer", wait_until="load")
    assert page.evaluate("getComputedStyle(document.getElementById('ex-pane-compare')).display") == "none"
    page.click("#ex-tab-compare")
    page.wait_for_selector("#ex-pane-compare.active")
    box = page.locator("#ex-scatter-wrap").bounding_box()
    assert box["height"] >= 350 and box["width"] > 300
