"""
test_live_alpha.py
------------------
Smoke tests against the deployed v1 alpha (EDOPS_SITE_MODE=v1alpha). Skipped unless EDOPS_ALPHA_URL is set. Run after each deploy:

    EDOPS_ALPHA_URL=https://edopsv1a.computingplace.org python -m pytest tests/test_live_alpha.py -v     (or ./smoke_alpha.sh)

Checks the alpha's own surface: the new pages, the alpha mode (banner, noindex, no analytics tag, 0.4 pages answering 404 with a
pointer), the API on the v1 code (signature_version 0.5, GEDA in Band T), HTTPS and the /api/ cache. Does not depend on the local
database. Every request to a logged endpoint carries src=ui_aux, which the query log skips, so running this adds no rows to
public.query_log. (The 0.4 smoke test, test_live_server.py, asserts signature_version 0.4 and is for the live 0.4 site.)
"""
import os

import httpx
import pytest

BASE = os.getenv("EDOPS_ALPHA_URL", "").rstrip("/")
QUIET = {"src": "ui_aux"}                         # not written to the query log
TIMBUKTU = {"lat": 16.8167, "lon": -2.9833}
KYIV = {"lat": 50.4547, "lon": 30.5238}
CUSCO = {"lat": -13.5319, "lon": -71.9675}        # outside GEDA's footprint
PAGES = ["/edops", "/dashboard", "/using", "/explorer"]
EMBEDS = ["/using/societies", "/using/africa"]
V04_PAGES = ["/sandbox", "/sandbox/explorer", "/workbench", "/polities", "/about"]
LIVE_V04 = "https://edops.computingplace.org"


@pytest.fixture(scope="module")
def alpha():
    if not BASE:
        pytest.skip("EDOPS_ALPHA_URL not set: skipping live alpha tests")
    with httpx.Client(base_url=BASE, timeout=30.0, follow_redirects=False) as client:
        yield client


def test_health(alpha):
    r = alpha.get("/api/health")
    assert r.status_code == 200 and r.json() == {"status": "ok"}


@pytest.mark.parametrize("path", PAGES + EMBEDS)
def test_new_pages_answer_200(alpha, path):
    assert alpha.get(path).status_code == 200


@pytest.mark.parametrize("path", ["/static/css/dashboard.css", "/static/js/edops_atlas.js", "/static/js/edops_permalink.js",
                                  "/static/profiles/index.json", "/favicon.ico"])
def test_static_files(alpha, path):
    assert alpha.get(path).status_code == 200


@pytest.mark.parametrize("path", PAGES)
def test_banner_and_live_v04_link(alpha, path):
    t = alpha.get(path).text
    assert "work in progress, not for citation" in t and f'href="{LIVE_V04}"' in t


@pytest.mark.parametrize("path", PAGES)
def test_no_analytics_tag(alpha, path):
    assert "googletagmanager" not in alpha.get(path).text


@pytest.mark.parametrize("path", V04_PAGES)
def test_0_4_pages_answer_404_with_a_pointer(alpha, path):
    r = alpha.get(path)
    assert r.status_code == 404 and "not part of the v1 alpha" in r.text and LIVE_V04 in r.text


def test_noindex_everywhere(alpha):
    assert alpha.get("/robots.txt").text.split() == ["User-agent:", "*", "Disallow:", "/"]
    for path in PAGES + ["/api/health"]:
        assert alpha.get(path).headers["x-robots-tag"] == "noindex, nofollow"


@pytest.mark.skipif(not BASE.startswith("https://"), reason="needs an https URL")
def test_http_redirects_to_https():
    r = httpx.get("http://" + BASE[len("https://"):] + "/edops", follow_redirects=False, timeout=30.0)
    assert r.status_code == 301 and r.headers["location"] == BASE + "/edops"


def test_api_responses_pass_through_the_cache_layer(alpha):
    r = alpha.get("/api/health")
    assert r.headers["x-cache-status"] in ("MISS", "HIT", "UPDATING", "STALE", "BYPASS", "EXPIRED")


def test_signature_version_is_the_v1_code(alpha):
    r = alpha.get("/api/signature", params={**TIMBUKTU, "scope": "basin", "level": 6, "bands": "ABCE", **QUIET})
    assert r.status_code == 200 and r.json()["meta"]["signature_version"] == "0.5"


def test_band_t_serves_geda_inside_its_footprint(alpha):
    r = alpha.get("/api/areas", params={"scope": "single_basin", **KYIV, "level": 6, "bands": "T", "from_year": 1300, "to_year": 1400, **QUIET})
    assert r.status_code == 200
    d = r.json()
    assert "geda_scpdsi" in {row["variable"] for row in d["rows"]}
    assert "geda" in {s["id"] for s in d["sources"]["used"]}


def test_band_t_says_why_geda_is_not_applied_outside_its_footprint(alpha):
    r = alpha.get("/api/areas", params={"scope": "single_basin", **CUSCO, "level": 6, "bands": "T", "from_year": 1438, "to_year": 1470, **QUIET})
    assert r.status_code == 200
    d = r.json()
    assert {s["id"]: s["reason"] for s in d["sources"]["not_applied"]} == {"geda": "outside_footprint"}
    assert any(row["variable"].startswith("hyde_") for row in d["rows"])


def test_a_polity_slice_step_asks_only_for_the_member_ids(alpha):
    r = alpha.get("/api/areas", params={"scope": "polity", "polity": "Northern Song", "year": 961, "level": 8, "members_only": "true", **QUIET})
    assert r.status_code == 200
    d = r.json()
    assert set(d) == {"member_ids", "resolver"} and len(d["member_ids"]) > 100 and d["resolver"]["polity"] == "Northern Song"


def test_the_atlas_data_the_explorer_needs(alpha):
    r = alpha.get("/api/explorer/climate-class", params={"axis": "modality", "level": 6})
    assert r.status_code == 200 and r.json()["categories"]


def test_unknown_polity_is_a_404(alpha):
    r = alpha.get("/api/areas", params={"scope": "polity", "polity": "Nowhere Empire", "year": 1000, **QUIET})
    assert r.status_code == 404
