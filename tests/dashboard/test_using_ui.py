"""Using EDOPS (WO-09 item 2): five tabs with the Overview first, a tile per example, the Workbench tabs shown inside, the sample profiles."""
import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.dashboard

TABS = ["Overview", "Societies", "African Regions", "Pueblo", "WHG"]


def test_the_five_tabs_with_the_overview_first_and_active(dashboard_server, page):
    page.goto(dashboard_server + "/using", wait_until="load")
    assert page.locator("#useTabs .nav-link").all_inner_texts() == TABS
    assert "active" in page.get_attribute("#tab-overview", "class")
    assert page.is_visible("#pane-overview")


def test_each_tile_opens_its_tab(dashboard_server, page):
    page.goto(dashboard_server + "/using", wait_until="load")
    tiles = page.locator(".use-tile")
    assert tiles.count() == 4
    for name in ("societies", "africa", "pueblo", "whg"):
        page.click(f".use-tile[data-tab='{name}']")
        page.wait_for_selector(f"#pane-{name}.active")
        page.click("#tab-overview")
        page.wait_for_selector("#pane-overview.active")


@pytest.mark.parametrize("name", ["overview", "societies", "africa", "pueblo", "whg"])
def test_tab_links_land_on_their_tab(dashboard_server, page, name):
    page.goto(f"{dashboard_server}/using?tab={name}", wait_until="load")
    page.wait_for_selector(f"#pane-{name}.active")
    assert f"tab={name}" in page.url or name == "overview"


def test_the_workbench_tabs_load_inside_without_their_own_header_or_tab_bar(dashboard_server, page):
    page.goto(dashboard_server + "/using?tab=societies", wait_until="load")
    frame = page.frame_locator("#frame-societies")
    frame.locator("#panel-soc.active").wait_for(timeout=60000)
    assert frame.locator("#edopTabs").is_hidden()
    assert frame.locator(".edops-page-pills").count() == 0
    page.click("#tab-africa")
    afr = page.frame_locator("#frame-africa")
    afr.locator("#panel-afr.active").wait_for(timeout=60000)
    afr.locator("#afr-right").wait_for(state="visible", timeout=30000)      # the African Regions info panel replaces the shared map
    assert afr.locator("#map").is_hidden()
    afr.locator("#afr-map canvas").first.wait_for(state="attached", timeout=60000)   # the African Regions map was drawn


def test_the_whg_tab_lists_the_ten_sample_places(dashboard_server, page):
    page.goto(dashboard_server + "/using?tab=whg", wait_until="load")
    page.wait_for_selector("#pf-places .nav-link", timeout=30000)
    assert page.locator("#pf-places .nav-link").count() == 10
    page.click("#pf-places .nav-link >> nth=1")
    page.wait_for_function("new URLSearchParams(location.search).get('tab') === 'whg' && new URLSearchParams(location.search).has('place')")


def test_the_old_profiles_address_redirects_to_the_whg_tab():
    from app.main import app
    r = TestClient(app, follow_redirects=False).get("/profiles?place=tbilisi&view=template")
    assert r.status_code == 307 and r.headers["location"] == "/using?tab=whg&place=tbilisi&view=template"
