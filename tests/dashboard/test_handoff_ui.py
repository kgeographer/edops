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


def _arrive(page, base, url, expect_tab):
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto(base + url, wait_until="load")
    page.wait_for_function(
        f"document.getElementById('{expect_tab}').classList.contains('active') && "
        "!document.getElementById('v3-sig-content').innerText.includes('Loading')", timeout=60000)
    return errors


@pytest.mark.parametrize("kind,name,url", _urls(), ids=[u[1] for u in _urls()])
def test_each_example_arrives_without_error(dashboard_server, page, kind, name, url):
    tab = "v3-tab-profile-btn" if kind == "settlement" else "v3-tab-sig-btn"
    errors = _arrive(page, dashboard_server, url, tab)
    assert errors == []
    assert "d-none" in page.get_attribute("#v3-handoff-alert", "class")          # no message shown
    assert page.inner_text("#v3-sig-content").strip() != ""
    if kind == "settlement":
        assert not page.evaluate("document.getElementById('v3-tab-analysis-btn').classList.contains('disabled')")
        assert f"Containing basin for {name}" in page.inner_text("#v3-profile-content")
        assert page.locator("#v3-profile-content .pf-sec").count() > 0              # the stored profile is shown
    else:
        assert "Profiles are written for settlements" in page.inner_text("#v3-profile-content")


def test_a_polity_link_with_a_year_opens_that_slice(dashboard_server, page):
    errors = _arrive(page, dashboard_server, "/dashboard?scope=polity&polity=Northern%20Song&year=1000&v=1", "v3-tab-sig-btn")
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
    assert r[0]["name"] == "x y" and r[0]["bands"] == "ABCDE" and r[0]["view"] == "profile" and r[0]["level"] == 6
    assert r[1] is None and r[2] is None and r[3] == 1
