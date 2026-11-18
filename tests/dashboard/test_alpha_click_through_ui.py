"""WO-09 gate: in the v1 alpha, clicking every nav element, tab, tile and example link on the new pages reaches only new-site pages
(or the one link to live 0.4). The setting is switched on for the in-process test server."""
import json
from pathlib import Path
from urllib.parse import urlparse

import pytest

from app.site_mode import is_v04_page

pytestmark = pytest.mark.dashboard

NEW = {"/edops", "/dashboard", "/using", "/explorer"}
EXAMPLES = json.loads((Path(__file__).resolve().parents[2] / "app" / "web" / "dashboard_examples.json").read_text(encoding="utf-8"))
LIVE = "https://edops.computingplace.org"


@pytest.fixture
def alpha_mode(monkeypatch):
    from app.settings import settings
    monkeypatch.setattr(settings, "EDOPS_SITE_MODE", "v1alpha")


def _path(page):
    return urlparse(page.url).path


def _is_pointer_page(page):
    return "not part of the v1 alpha" in page.content()


@pytest.mark.parametrize("start", sorted(NEW - {"/edops"}))      # the splash has tiles, not pills (tested below)
def test_every_header_pill_leads_to_a_new_page(dashboard_server, page, alpha_mode, start):
    page.goto(dashboard_server + start, wait_until="load")
    labels = page.locator(".edops-page-pills a").all_inner_texts()
    assert labels == ["Home", "Dashboard", "Using EDOPS", "Data Explorer"]
    for label in labels:
        page.goto(dashboard_server + start, wait_until="load")
        page.click(f".edops-page-pills a:text-is('{label}')")
        page.wait_for_load_state("load")
        assert _path(page) in NEW and not _is_pointer_page(page), f"{start}: {label} went to {page.url}"


def test_the_splash_tiles_and_examples_lead_to_the_dashboard_using_and_explorer(dashboard_server, page, alpha_mode):
    for href in ("/dashboard", "/using", "/explorer"):
        page.goto(dashboard_server + "/edops", wait_until="load")
        page.click(f".cp-tile[href='{href}']")
        page.wait_for_load_state("load")
        assert _path(page) == href and not _is_pointer_page(page)
    page.goto(dashboard_server + "/edops", wait_until="load")
    options = page.eval_on_selector_all(".cp-tiles ~ * select option, select option", "els => els.map(e => e.value).filter(v => v)")
    assert len(options) >= len(EXAMPLES["settlements"]) + len(EXAMPLES["polities"])
    assert all(urlparse(v).path == "/dashboard" for v in options)


def test_every_using_tile_and_tab_stays_on_the_using_page(dashboard_server, page, alpha_mode):
    page.goto(dashboard_server + "/using", wait_until="load")
    for name in ("societies", "africa", "pueblo", "whg", "overview"):
        page.click(f"#tab-{name}")
        page.wait_for_selector(f"#pane-{name}.active")
        assert _path(page) == "/using"
    page.click("#tab-whg")
    page.wait_for_selector("#pf-places .nav-link")
    for i in range(page.locator("#pf-places .nav-link").count()):          # every sample place and the template view
        page.locator("#pf-places .nav-link").nth(i).click()
        assert _path(page) == "/using"
    page.click("#pf-toggle")
    assert _path(page) == "/using"


def test_every_internal_link_on_the_new_pages_and_the_embedded_workbench_is_a_new_page(dashboard_server, page, alpha_mode):
    """Crawl: each same-origin link (outside static, api and the 0.4 docs) is a new page that answers 200, and the two embedded
    Workbench pages are checked the same way."""
    seen, todo = set(), ["/edops", "/dashboard", "/using", "/explorer", "/using/societies", "/using/africa"]
    while todo:
        path = todo.pop()
        if path in seen:
            continue
        seen.add(path)
        page.goto(dashboard_server + path, wait_until="load")
        hrefs = page.eval_on_selector_all("a[href], iframe[src], form[action]",
                                          "els => els.map(e => e.getAttribute('href') || e.getAttribute('src') || e.getAttribute('action'))")
        for h in hrefs:
            if not h or h.startswith(("#", "mailto:", "javascript:")):
                continue
            u = urlparse(h)
            if u.scheme and u.netloc:                                        # external: only the live 0.4 site is ours
                continue
            if u.path.startswith(("/static", "/api", "/docs")) or u.path in ("/favicon.ico", ""):    # "" is a link on the same page (?place=...)
                continue
            assert not is_v04_page(u.path), f"{path} links to {h}"
            assert u.path in NEW | {"/using/societies", "/using/africa"}, f"{path} links to an unexpected page {h}"
            todo.append(u.path)
    assert {"/edops", "/dashboard", "/using", "/explorer"} <= seen


def test_a_stale_0_4_link_lands_on_the_pointer_page_which_leads_back(dashboard_server, page, alpha_mode):
    for stale in ("/sandbox", "/workbench", "/polities", "/about", "/sandbox/explorer"):
        response = page.goto(dashboard_server + stale, wait_until="load")
        assert response.status == 404 and _is_pointer_page(page)
        assert page.locator(f"a[href='{LIVE}']").count() == 1
        page.click("a[href='/edops']")
        page.wait_for_load_state("load")
        assert _path(page) == "/edops"


def test_the_banner_is_on_every_new_page_and_links_to_live_0_4(dashboard_server, page, alpha_mode):
    for path in sorted(NEW):
        page.goto(dashboard_server + path, wait_until="load")
        assert "work in progress, not for citation" in page.inner_text(".alpha-banner")
        assert page.locator(f".alpha-banner a[href='{LIVE}']").count() == 1
