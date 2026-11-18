"""Time series stub (WO-09 item 3): a tab in the Dashboard after the signature tabs, before Atlas, with "coming soon" and an outline."""
import pytest

pytestmark = pytest.mark.dashboard

ORDER = ["v3-tab-map-btn", "v3-tab-profile-btn", "v3-tab-sig-btn", "v3-tab-analysis-btn", "v3-tab-seasonality-btn",
         "v3-tab-context-btn", "v3-tab-similarity-btn", "v3-tab-timeseries-btn", "v3-tab-atlas-btn"]


def test_the_tab_follows_similarity_and_precedes_atlas(dashboard_server, page):
    page.goto(dashboard_server + "/dashboard", wait_until="load")
    ids = page.evaluate("[...document.querySelectorAll('button.nav-link[id^=\"v3-tab-\"]')].map(b => b.id)")
    assert [i for i in ids if i in ORDER] == ORDER


def test_it_opens_without_a_result_and_says_coming_soon(dashboard_server, page):
    page.goto(dashboard_server + "/dashboard", wait_until="load")
    assert "disabled" not in page.get_attribute("#v3-tab-timeseries-btn", "class")
    page.click("#v3-tab-timeseries-btn")
    page.wait_for_selector("#v3-pane-timeseries.active")
    text = page.inner_text("#v3-pane-timeseries")
    assert "Coming soon" in text and "download of the raw numbers" in text and "will point here" in text
