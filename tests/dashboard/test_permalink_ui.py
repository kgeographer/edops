"""Dashboard permalink button (WO-03 item 6): it appears after a run, and the link it gives reproduces the result."""
from urllib.parse import parse_qs, urlparse

import httpx
import pytest

from .test_handoff_ui import _arrive

TBILISI = "/dashboard?lat=41.6938&lon=44.8015&name=Tbilisi&v=1"


def _link(page):
    page.click("#v3-permalink-btn")
    url = page.input_value("#v3-permalink-url")
    assert url.startswith("http")
    return url, parse_qs(urlparse(url).query)


def _open_link(page, base, url, tab):
    """Open a permalink in a new page of the same browser, wait for the result, return the page."""
    other = page.context.new_page()
    path = url[url.index("/dashboard"):]
    errors = _arrive(other, base, path, tab)
    assert errors == []
    return other


def test_the_button_is_hidden_until_a_run_and_after_a_reset(dashboard_server, page):
    page.goto(f"{dashboard_server}/dashboard", wait_until="load")
    assert page.evaluate("getComputedStyle(document.getElementById('v3-permalink-row')).display") == "none"
    _arrive(page, dashboard_server, TBILISI, "v3-tab-profile-btn")
    assert page.evaluate("getComputedStyle(document.getElementById('v3-permalink-row')).display") == "flex"
    assert "lat=41.6938" in page.url
    page.click("#v3-reset-btn")
    assert page.evaluate("getComputedStyle(document.getElementById('v3-permalink-row')).display") == "none"
    assert page.url == f"{dashboard_server}/dashboard"   # the old link is gone from the address bar


def test_reset_also_clears_a_polity_link_and_its_message(dashboard_server, page):
    _arrive(page, dashboard_server, "/dashboard?scope=polity&polity=Northern%20Song&v=1", "v3-tab-sig-btn")
    assert "polity=Northern" in page.url
    page.click("#v3-reset-btn")
    assert page.url == f"{dashboard_server}/dashboard"
    assert "d-none" in page.get_attribute("#v3-handoff-alert", "class")


def test_a_failed_link_gives_no_button(dashboard_server, page):
    page.goto(f"{dashboard_server}/dashboard?scope=polity&polity=No%20Such%20Polity%20Xyz&v=1", wait_until="load")
    page.wait_for_function("!document.getElementById('v3-handoff-alert').classList.contains('d-none')", timeout=30000)
    assert page.evaluate("getComputedStyle(document.getElementById('v3-permalink-row')).display") == "none"


def test_single_basin_round_trip_keeps_the_tab_and_the_result(dashboard_server, page):
    _arrive(page, dashboard_server, TBILISI, "v3-tab-profile-btn")
    page.click("#v3-tab-sig-btn")
    url, q = _link(page)
    assert q["view"] == ["signature"] and q["scope"] == ["single_basin"] and q["level"] == ["6"] and q["lat"] == ["41.6938"]
    other = _open_link(page, dashboard_server, url, "v3-tab-sig-btn")
    assert other.inner_text("#v3-sig-content") == page.inner_text("#v3-sig-content")
    assert other.inner_text("#v3-profile-content") == page.inner_text("#v3-profile-content")


def test_the_active_tab_is_part_of_the_link(dashboard_server, page):
    _arrive(page, dashboard_server, TBILISI, "v3-tab-profile-btn")
    page.click("#v3-tab-seasonality-btn")
    url, q = _link(page)
    assert q["view"] == ["seasonality"]
    _open_link(page, dashboard_server, url, "v3-tab-seasonality-btn")


def test_band_t_years_and_buffer_radius_are_carried(dashboard_server, page):
    _arrive(page, dashboard_server, TBILISI + "&bands=ABCDET&from_year=1150&to_year=1250&view=signature", "v3-tab-sig-btn")
    url, q = _link(page)
    assert q["bands"] == ["ABCDET"] and q["from_year"] == ["1150"] and q["to_year"] == ["1250"]
    other = _open_link(page, dashboard_server, url, "v3-tab-sig-btn")
    assert other.inner_text("#v3-sig-content") == page.inner_text("#v3-sig-content")

    _arrive(page, dashboard_server, TBILISI + "&scope=buffer&radius_km=50&view=signature", "v3-tab-sig-btn")
    url, q = _link(page)
    assert q["scope"] == ["buffer"] and q["radius_km"] == ["50"]
    other = _open_link(page, dashboard_server, url, "v3-tab-sig-btn")
    assert other.inner_text("#v3-sig-content") == page.inner_text("#v3-sig-content")


def test_a_ring_member_round_trips(dashboard_server, page):
    ring = httpx.get(f"{dashboard_server}/api/basin/ring", params={"lat": 41.6938, "lon": 44.8015, "level": 6}, timeout=60).json()
    member = int(ring["ring"][0]["hybas_id"])
    _arrive(page, dashboard_server, f"{TBILISI}&scope=basin_ring&member={member}&view=signature", "v3-tab-sig-btn")
    page.wait_for_function("document.getElementById('v3-sig-content').innerText.includes('Ring basin #')", timeout=60000)
    url, q = _link(page)
    assert q["scope"] == ["basin_ring"] and q["member"] == [str(member)]
    other = _open_link(page, dashboard_server, url, "v3-tab-sig-btn")
    other.wait_for_function("document.getElementById('v3-sig-content').innerText.includes('Ring basin #')", timeout=60000)
    assert other.inner_text("#v3-sig-content") == page.inner_text("#v3-sig-content")


def test_a_polity_slice_round_trips(dashboard_server, page):
    _arrive(page, dashboard_server, "/dashboard?scope=polity&polity=Northern%20Song&year=1000&v=1", "v3-tab-sig-btn")
    url, q = _link(page)
    assert q["scope"] == ["polity"] and q["polity"] == ["Northern Song"] and q["year"] == ["1000"] and "lat" not in q
    other = _open_link(page, dashboard_server, url, "v3-tab-sig-btn")
    assert other.input_value("#v3-resolver-year") == "1000"
    assert other.inner_text("#v3-sig-content") == page.inner_text("#v3-sig-content")
