"""Dashboard URL handoff (WO-03 item 5): every example arrives, bad links say why, the codec parses and builds."""
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
EXAMPLES = json.loads((ROOT / "app" / "web" / "dashboard_examples.json").read_text(encoding="utf-8"))
CODEC = ROOT / "app" / "static" / "js" / "edops_permalink.js"


def _urls():
    from app.web.pages import _dashboard_examples
    d = _dashboard_examples()
    return [("settlement", e["name"], e["url"]) for e in d["settlements"]] + [("polity", e["name"], e["url"]) for e in d["polities"]]


# The run has finished when the Signature tab has its content and, for settlements, the Profile tab is enabled and
# so is the Seasonality tab (which follows the second request).
SETTLED = """(() => {
  const on = id => !document.getElementById(id).classList.contains('disabled');
  const pol = document.getElementById('v3-tab-polities-btn').classList.contains('active');
  const sig = document.getElementById('v3-sig-content').innerText.trim();
  return on('v3-tab-sig-btn') && sig !== '' && !sig.includes('Loading') && (pol || (on('v3-tab-profile-btn') && on('v3-tab-seasonality-btn')));
})()"""
RECORD_TABS = "window.__tabs = []; document.addEventListener('shown.bs.tab', e => window.__tabs.push(e.target.id));"
RESULT_TABS = {"v3-tab-profile-btn", "v3-tab-sig-btn", "v3-tab-analysis-btn", "v3-tab-seasonality-btn",
               "v3-tab-context-btn", "v3-tab-similarity-btn"}


def _arrive(page, base, url, expect_tab, record=False):
    """Open a link and wait for the result. record=True logs every tab the page shows, in window.__tabs (use on a
    fresh page, one arrival)."""
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    if record:
        page.add_init_script(RECORD_TABS)
    page.goto(base + url, wait_until="load")
    page.wait_for_function(f"document.getElementById('{expect_tab}').classList.contains('active') && {SETTLED}", timeout=60000)
    return errors


def _profile_tab_display(page):
    return page.evaluate("getComputedStyle(document.getElementById('v3-tab-profile-li')).display")


@pytest.mark.parametrize("kind,name,url", _urls(), ids=[u[1] for u in _urls()])
def test_each_example_arrives_without_error(dashboard_server, page, kind, name, url):
    errors = _arrive(page, dashboard_server, url, "v3-tab-map-btn", record=True)
    assert errors == []
    assert not (set(page.evaluate("window.__tabs")) & RESULT_TABS)               # the reader stays on the map
    assert "d-none" in page.get_attribute("#v3-handoff-alert", "class")          # no message shown
    assert page.inner_text("#v3-sig-content").strip() != ""
    if kind == "settlement":
        assert _profile_tab_display(page) != "none"
        assert not page.evaluate("document.getElementById('v3-tab-analysis-btn').classList.contains('disabled')")
        assert f"Containing basin for {name}" in page.inner_text("#v3-profile-content")
        assert page.locator("#v3-profile-content .pf-sec").count() > 0              # the stored profile is shown
    else:
        assert _profile_tab_display(page) == "none"                                  # polities have no Profile tab


def test_a_polity_link_with_a_year_opens_that_slice(dashboard_server, page):
    errors = _arrive(page, dashboard_server, "/dashboard?scope=polity&polity=Northern%20Song&year=1000&view=signature&v=1", "v3-tab-sig-btn")
    assert errors == []
    assert page.input_value("#v3-resolver-year") == "1000"
    assert page.evaluate("document.getElementById('v3-slice-select').options.length") > 1


def test_a_link_with_a_ring_member_and_buffer_and_level_8_arrives(dashboard_server, page):
    for url in ("/dashboard?lat=41.6938&lon=44.8015&name=Tbilisi&scope=basin_ring&view=signature&v=1",
                "/dashboard?lat=41.6938&lon=44.8015&name=Tbilisi&scope=buffer&radius_km=50&view=signature&v=1",
                "/dashboard?lat=41.6938&lon=44.8015&name=Tbilisi&level=8&view=signature&v=1"):
        errors = _arrive(page, dashboard_server, url, "v3-tab-sig-btn")
        assert errors == [] and "d-none" in page.get_attribute("#v3-handoff-alert", "class")
    # a single-basin Level 06 profile exists only for single_basin at level 6: the Profile tab says so
    page.click("#v3-tab-profile-btn")
    assert "Profiles cover single-basin queries at Level 06" in page.inner_text("#v3-profile-content")


@pytest.mark.parametrize("query,fragment", [
    ("lat=999&lon=0", "lat is required"),
    ("lat=10", "lon is required"),
    ("lat=10&lon=10&level=7", "level must be 6 or 8"),
    ("lat=10&lon=10&bands=ABCT", "Band T needs from_year and to_year"),
    ("lat=10&lon=10&view=nonsense", "view must be one of"),
    ("scope=polity", "polity is required"),
    ("scope=polity&polity=No%20Such%20Polity%20Xyz&v=1", "Polity not found"),
])
def test_a_bad_link_says_why(dashboard_server, page, query, fragment):
    page.goto(f"{dashboard_server}/dashboard?{query}", wait_until="load")
    page.wait_for_function("!document.getElementById('v3-handoff-alert').classList.contains('d-none')", timeout=30000)
    assert fragment in page.inner_text("#v3-handoff-msg")


def test_unknown_parameters_and_plain_visits_are_quiet(dashboard_server, page):
    page.goto(f"{dashboard_server}/dashboard", wait_until="load")
    page.wait_for_timeout(500)
    assert "d-none" in page.get_attribute("#v3-handoff-alert", "class")
    page.goto(f"{dashboard_server}/dashboard?foo=bar", wait_until="load")
    page.wait_for_timeout(500)
    assert "d-none" in page.get_attribute("#v3-handoff-alert", "class")


def test_arrivals_are_logged_as_link():
    from app.db.connection import db_connect
    with db_connect() as conn:
        n = conn.execute("SELECT count(*) FROM public.query_log WHERE src = 'link'").fetchone()[0]
    assert n > 0   # the arrivals above (run first, in file order) were logged with src=link


def test_the_codec_round_trips_and_validates(page):
    page.set_content("<html></html>")
    page.add_script_tag(path=str(CODEC))
    ok = page.evaluate("""() => {
      const P = EdopsPermalink, bad = [];
      const cases = [
        {kind:'settlement', scope:'single_basin', level:6, bands:'ABCDE', view:'profile', lat:41.6938, lon:44.8015, name:'Tbilisi'},
        {kind:'settlement', scope:'buffer', level:8, bands:'ABCDET', view:'signature', lat:-37.068, lon:-12.312, name:'A & B, C', radiusKm:250, fromYear:-500, toYear:200},
        {kind:'settlement', scope:'basin_ring', level:6, bands:'ABCDE', view:'signature', lat:1, lon:2, name:'', member:2060616700},
        {kind:'polity', scope:'polity', level:6, bands:'ABCDET', view:'signature', polity:'Northern Song', year:1000},
        {kind:'polity', scope:'polity', level:6, bands:'ABCDE', view:'signature', polity:'Qin', year:null},
      ];
      for (const c of cases) {
        const r = P.parse('?' + P.build(c));
        if (r.errors.length || JSON.stringify(r.state) !== JSON.stringify(Object.assign({}, c))) bad.push([c, r]);
      }
      return bad.length ? JSON.stringify(bad).slice(0, 600) : 'ok';
    }""")
    assert ok == "ok", ok
    # defaults, unknown keys, sanitising, and a plain visit
    r = page.evaluate("""() => { const P = EdopsPermalink;
      return [P.parse('?lat=1&lon=2&foo=bar&name=%0Ax%0A%20%20y').state, P.parse('?foo=bar').state, P.parse('').state, P.parse('?v=2&lat=1&lon=2').warnings.length]; }""")
    assert r[0]["name"] == "x y" and r[0]["bands"] == "ABCDE" and r[0]["view"] == "map" and r[0]["level"] == 6
    assert r[1] is None and r[2] is None and r[3] == 1


def test_a_link_naming_a_tab_selects_it_once_and_early(dashboard_server, page):
    _arrive(page, dashboard_server, "/dashboard?lat=41.6938&lon=44.8015&name=Tbilisi&view=profile&v=1", "v3-tab-profile-btn", record=True)
    assert page.evaluate("window.__tabs") == ["v3-tab-profile-btn"]
    assert page.locator("#v3-profile-content .pf-sec").count() > 0


def test_a_link_naming_the_signature_tab_selects_it_once(dashboard_server, page):
    _arrive(page, dashboard_server, "/dashboard?lat=41.6938&lon=44.8015&name=Tbilisi&view=signature&v=1", "v3-tab-sig-btn", record=True)
    assert page.evaluate("window.__tabs") == ["v3-tab-sig-btn"]


def test_a_resolved_place_fills_the_tabs_and_stays_on_the_map(dashboard_server, page):
    page.add_init_script(RECORD_TABS)
    page.goto(f"{dashboard_server}/dashboard", wait_until="load")
    page.fill("#v3-place-input", "41.6938, 44.8015")
    page.click("#v3-resolve-btn")
    page.wait_for_function(SETTLED, timeout=60000)
    assert "active" in page.get_attribute("#v3-tab-map-btn", "class")
    assert not (set(page.evaluate("window.__tabs")) & RESULT_TABS)
    assert page.locator("#v3-profile-content .pf-sec").count() > 0
    assert page.inner_text("#v3-sig-content").strip() != ""


def test_a_chosen_polity_runs_and_stays_on_the_map(dashboard_server, page):
    page.add_init_script(RECORD_TABS)
    page.goto(f"{dashboard_server}/dashboard", wait_until="load")
    page.click("#v3-tab-polities-btn")
    page.fill("#v3-polity-input", "Northern Song")
    page.locator(".v3-polity-item", has_text="Northern Song").first.click()
    page.wait_for_function(SETTLED, timeout=60000)
    assert "active" in page.get_attribute("#v3-tab-map-btn", "class")
    assert not (set(page.evaluate("window.__tabs")) & RESULT_TABS)
    assert page.inner_text("#v3-sig-content").strip() != ""


def test_the_profile_tab_follows_the_left_tab(dashboard_server, page):
    _arrive(page, dashboard_server, "/dashboard?lat=41.6938&lon=44.8015&name=Tbilisi&v=1", "v3-tab-map-btn")
    assert _profile_tab_display(page) != "none"
    page.click("#v3-tab-polities-btn")
    assert _profile_tab_display(page) == "none"
    page.click("#v3-tab-settlements-btn")
    assert _profile_tab_display(page) != "none"


def test_a_polity_chosen_from_the_dashboard_has_no_profile_tab(dashboard_server, page):
    page.goto(f"{dashboard_server}/dashboard", wait_until="load")
    page.click("#v3-tab-polities-btn")
    page.select_option("#v3-polity-example", label="Northern Song (961–1027 CE)")   # the Dashboard's own dropdown
    page.wait_for_url("**/dashboard?scope=polity*")
    page.wait_for_function(SETTLED, timeout=60000)
    assert _profile_tab_display(page) == "none"


def test_the_polity_example_dropdown_stays_usable_after_a_polity_search(dashboard_server, page):
    page.goto(f"{dashboard_server}/dashboard", wait_until="load")
    page.click("#v3-tab-polities-btn")
    page.fill("#v3-polity-input", "Northern Song")
    page.locator(".v3-polity-item", has_text="Northern Song").first.click()
    page.wait_for_function(SETTLED, timeout=60000)
    assert page.is_enabled("#v3-polity-example")
    page.select_option("#v3-polity-example", label="Inca Empire (1440–1571 CE)")
    page.wait_for_url("**polity=Inca*")


def test_a_polity_link_that_names_profile_just_opens_the_map(dashboard_server, page):
    page.goto(f"{dashboard_server}/dashboard?scope=polity&polity=Northern%20Song&view=profile&v=1", wait_until="load")
    page.wait_for_function(SETTLED, timeout=60000)
    assert "active" in page.get_attribute("#v3-tab-map-btn", "class")
    assert "d-none" in page.get_attribute("#v3-handoff-alert", "class")                # and says nothing about it


def test_the_signature_tab_shows_a_spinner_while_a_run_is_in_progress(dashboard_server, page):
    import time

    def slow(route):
        time.sleep(1.5)          # a big polity takes seconds; make that deterministic
        route.continue_()

    page.route("**/api/areas*", slow)
    page.goto(f"{dashboard_server}/dashboard?scope=polity&polity=Northern%20Song&v=1", wait_until="load")
    page.wait_for_selector("#v3-tab-sig-spin:not(.d-none)", timeout=30000)        # visible while the query runs
    assert "active" in page.get_attribute("#v3-tab-map-btn", "class")              # the reader is still on the map
    page.wait_for_function(SETTLED, timeout=60000)
    page.wait_for_selector("#v3-tab-sig-spin.d-none", state="attached", timeout=10000)   # and gone when it ends


def test_load_an_example_stays_available_after_a_place_is_resolved(dashboard_server, page):
    page.goto(f"{dashboard_server}/dashboard", wait_until="load")
    page.fill("#v3-place-input", "41.6938, 44.8015")
    page.click("#v3-resolve-btn")
    page.wait_for_function(SETTLED, timeout=60000)
    assert page.is_visible("#v3-example-select") and page.is_enabled("#v3-example-select")
    page.select_option("#v3-example-select", label="Timbuktu, Mali")                 # the reader can switch examples
    page.wait_for_url("**/dashboard?lat=16.8167*")


def test_load_an_example_stays_available_after_an_example_arrival(dashboard_server, page):
    _arrive(page, dashboard_server, "/dashboard?lat=41.6938&lon=44.8015&name=Tbilisi&v=1", "v3-tab-map-btn")
    assert page.is_visible("#v3-example-select") and page.is_enabled("#v3-example-select")


def test_a_place_in_a_profiled_basin_but_far_from_its_point_shows_the_plain_line(dashboard_server, page):
    # about 26 km from the Tbilisi profile's point
    _arrive(page, dashboard_server, "/dashboard?lat=41.55&lon=45.0&name=Rustavi&v=1", "v3-tab-map-btn")
    page.click("#v3-tab-profile-btn")
    assert "Profiles cover single-basin queries at Level 06" in page.inner_text("#v3-profile-content")
    assert page.locator("#v3-profile-content .pf-sec").count() == 0
