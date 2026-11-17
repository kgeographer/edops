"""Polity gate (WO-07 follow-up): a slice whose Band T would take over the ceiling is not run while T is ticked."""
from .test_handoff_ui import _arrive

CHINA = "/dashboard?scope=polity&polity=People%27s%20Republic%20of%20China&year=2010&v=1"      # slice 2000-2023, 24 HYDE steps
SONG = "/dashboard?scope=polity&polity=Northern%20Song&v=1"
HALT = "#v3-polity-halt"


def _halted(page):
    return page.evaluate(f"!document.querySelector('{HALT}').classList.contains('d-none')")


def _open_halted(page, base, requests=None):
    if requests is not None:
        page.on("request", lambda r: requests.append(r.url) if "/api/areas" in r.url else None)
    page.goto(base + CHINA, wait_until="load")
    page.wait_for_selector(f"{HALT}:not(.d-none)", timeout=60000)


def test_the_estimate_follows_the_measured_times(dashboard_server, page):
    """HYDE seconds measured on the one-row-per-cell query: Northern Song 1000-1999 7.0, China 2000-2023 10.2, China 1950-1952 4.7,
    Seljuk 1200-1999 0.77, Croatia 1000-1999 0.34. The estimate is within a factor of about 1.3 and not below for the large ones;
    for a tiny polity it is a fraction of a second under (fixed overhead), which does not matter against a 5 s ceiling."""
    page.goto(dashboard_server + "/dashboard", wait_until="load")
    est = lambda area, a, b: page.evaluate(f"EdopsSpanGate.estimateSeconds({area}, {a}, {b})")
    assert 7.0 <= est(2764506, 1000, 1999) < 9.5
    assert 10.2 <= est(9399800, 2000, 2023) < 13.5
    assert 4.7 <= est(8412878, 1950, 1952) < 6.2
    assert 0.77 <= est(291924, 1200, 1999) < 1.2
    assert 0.2 < est(90475, 1000, 1999) < 0.6


def test_the_estimate_flags_the_slow_modern_slices_and_passes_the_examples(dashboard_server, page):
    page.goto(dashboard_server + "/dashboard", wait_until="load")
    over = lambda area, a, b: page.evaluate(f"EdopsSpanGate.areaCheck({area}, {a}, {b}) !== null")
    assert over(9399800, 2000, 2023)         # China, 10 s measured on the new query (about 100 s on the old)
    assert over(10024490, 1949, 2023)        # Canada
    assert over(2792618, 1936, 2023)         # Argentina, 193 s on the old query
    assert not over(2764275, 990, 1017)      # Northern Song, the example slice
    assert not over(90475, 1000, 1017)       # Croatia
    assert not over(1577069, 947, 959)       # an Abbasid slice


def test_a_halted_slice_disables_get_signature_and_says_why(dashboard_server, page):
    _open_halted(page, dashboard_server)
    assert page.evaluate("document.getElementById('v3-polity-sig-btn').disabled")
    text = page.inner_text(HALT)
    assert "Band T for this slice would take about" in text and "Untick T" in text


def test_unticking_t_brings_the_button_back_and_ticking_halts_again(dashboard_server, page):
    _open_halted(page, dashboard_server)
    page.uncheck("#v3-polity-band-T")
    assert not _halted(page)
    assert not page.evaluate("document.getElementById('v3-polity-sig-btn').disabled")
    page.check("#v3-polity-band-T")
    assert _halted(page)
    assert page.evaluate("document.getElementById('v3-polity-sig-btn').disabled")


def _slice_requests(urls, from_year):
    """The /api/areas requests made for slices from from_year on, as {parameter: value} dicts."""
    out = []
    for u in urls:
        q = dict(p.split("=", 1) for p in u.split("?", 1)[1].split("&"))
        if int(q.get("year", "0")) >= from_year:
            out.append(q)
    return out


def test_stepping_onto_a_halted_slice_sends_no_band_t_request(dashboard_server, page):
    seen = []
    _open_halted(page, dashboard_server, seen)                  # the link lands on 2000-2023
    seen.clear()
    page.click("#v3-btn-prev")                                  # off the halted slice ...
    page.wait_for_timeout(500)
    page.click("#v3-btn-next")                                  # ... and back onto it
    page.wait_for_selector(f"{HALT}:not(.d-none)", timeout=60000)
    page.wait_for_timeout(2000)
    for_slice = _slice_requests(seen, 2000)
    assert for_slice, "the map's background request for the slice should still go out"
    assert all("T" not in q.get("bands", "") for q in for_slice)


def test_an_example_slice_is_not_halted(dashboard_server, page):
    _arrive(page, dashboard_server, SONG, "v3-tab-map-btn")
    assert not _halted(page)
