"""The v1 alpha site mode (WO-09 item 1): the new pages only, a banner, noindex, 0.4 pages answer with a pointer."""
import re

import pytest
from fastapi.testclient import TestClient

from app.site_mode import V04_PAGES, is_v04_page

pytestmark = pytest.mark.dashboard

NEW_PAGES = ["/edops", "/dashboard", "/using", "/explorer", "/profiles"]
OLD_PAGES = list(V04_PAGES) + ["/sandbox/explorer", "/sandbox/lookup3"]
LIVE = "https://edops.computingplace.org"


@pytest.fixture
def alpha(monkeypatch):
    from app.main import app
    from app.settings import settings
    monkeypatch.setattr(settings, "EDOPS_SITE_MODE", "v1alpha")
    return TestClient(app, follow_redirects=False)


@pytest.fixture
def v04():
    from app.main import app
    return TestClient(app, follow_redirects=False)


@pytest.mark.parametrize("path", OLD_PAGES)
def test_0_4_pages_answer_404_with_a_pointer_to_the_live_site(alpha, path):
    r = alpha.get(path)
    assert r.status_code == 404
    assert LIVE in r.text and "/edops" in r.text and "not part of the v1 alpha" in r.text


@pytest.mark.parametrize("path", NEW_PAGES)
def test_new_pages_carry_the_banner_and_noindex(alpha, path):
    r = alpha.get(path)
    assert r.status_code == 200
    assert "work in progress, not for citation" in r.text and "v1.0 alpha" in r.text and LIVE in r.text
    assert r.headers["x-robots-tag"] == "noindex, nofollow"


def test_no_new_page_links_to_a_0_4_page(alpha):
    """Every internal href on the new pages leads to a new page, an API route, a static file or the docs."""
    for path in NEW_PAGES:
        html = alpha.get(path).text
        for m in re.finditer(r"""(?:href|action)=["'](/[^"'#? ]*)""", html):
            assert not is_v04_page(m.group(1)), f"{path} links to {m.group(1)}"


def test_the_dashboard_pills_serve_the_explorer_and_the_profiles_page(alpha):
    for path in ("/explorer", "/profiles", "/using", "/dashboard"):
        html = alpha.get(path).text
        assert 'href="/using"' in html and 'href="/dashboard"' in html and 'href="/explorer"' in html
        assert 'href="/sandbox"' not in html and 'href="/workbench"' not in html
        if path != "/profiles":                       # the sample profiles page has no documentation link
            assert 'Documentation (<span class="v04-tag">v0.4</span>)' in html


def test_robots_txt_disallows_everything(alpha):
    r = alpha.get("/robots.txt")
    assert r.status_code == 200 and "Disallow: /" in r.text


def test_the_root_is_the_splash_whatever_the_host(alpha):
    r = alpha.get("/", headers={"host": "localhost:8000"})
    assert r.status_code == 200 and 'href="/dashboard"' in r.text


def test_without_the_setting_nothing_changes(v04):
    assert v04.get("/sandbox").status_code == 200
    assert v04.get("/robots.txt").status_code == 404
    r = v04.get("/dashboard")
    assert "work in progress" not in r.text and "x-robots-tag" not in r.headers
    assert "v04-tag" not in r.text


def _log_count():
    from app.db.connection import db_connect
    with db_connect() as conn:
        return conn.execute("SELECT count(*) FROM public.query_log").fetchone()[0]


@pytest.mark.parametrize("path", NEW_PAGES)
def test_no_analytics_tag_in_the_alpha(alpha, path):
    assert "googletagmanager" not in alpha.get(path).text


def test_the_analytics_tag_is_still_there_without_the_setting(v04):
    assert "googletagmanager" in v04.get("/dashboard").text


def test_the_alpha_writes_nothing_to_the_query_log(alpha):
    import time
    before = _log_count()
    r = alpha.get("/api/areas", params=dict(scope="single_basin", lat=49.8397, lon=24.0297, level=6, bands="A", src="ui"))
    assert r.status_code == 200
    time.sleep(1)                                   # the write, if there were one, runs in a thread
    assert _log_count() == before


def test_without_the_setting_the_query_log_still_records(v04):
    import time
    before = _log_count()
    r = v04.get("/api/areas", params=dict(scope="single_basin", lat=49.8397, lon=24.0297, level=6, bands="A", src="ui", place_name="site-mode test"))
    assert r.status_code == 200
    time.sleep(1)
    assert _log_count() == before + 1


def test_the_documentation_modal_title_carries_the_v0_4_tag_in_the_alpha(alpha):
    title = 'Environmental Dimensions of Place Service (EDOPS) <span class="v04-tag">v0.4</span></h4>'
    assert title in alpha.get("/explorer").text


def test_the_documentation_modal_title_is_unchanged_without_the_setting(v04):
    assert "v04-tag" not in v04.get("/explorer").text
