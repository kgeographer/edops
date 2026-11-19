"""The new pages (splash, Dashboard, Using EDOPS, Data Explorer) share a page background from one CSS variable in dashboard.css;
the Sandbox, Workbench and the Computing Place pages are unchanged."""
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.dashboard

CSS = Path(__file__).resolve().parents[2] / "app" / "static" / "css" / "dashboard.css"
NEW = ["/edops", "/dashboard", "/using", "/explorer"]
UNCHANGED = ["/sandbox", "/workbench", "/", "/about"]


def _client():
    from app.main import app
    return TestClient(app)


def test_the_variable_and_the_rule_live_in_dashboard_css():
    css = CSS.read_text(encoding="utf-8")
    assert ":root { --edops-page-bg:" in css and "body.edops-v1 { background: var(--edops-page-bg); }" in css


@pytest.mark.parametrize("path", NEW)
def test_new_pages_have_the_class_and_load_dashboard_css(path):
    html = _client().get(path).text
    assert '<body class="edops-v1">' in html and "/static/css/dashboard.css" in html


@pytest.mark.parametrize("path", UNCHANGED)
def test_other_pages_do_not(path):
    html = _client().get(path).text
    assert "edops-v1" not in html and "/static/css/dashboard.css" not in html


def test_the_browser_paints_the_page_from_the_variable_and_the_panes_white(dashboard_server, page):
    page.goto(dashboard_server + "/explorer", wait_until="load")
    bg = lambda sel: page.evaluate(f"getComputedStyle(document.querySelector('{sel}')).backgroundColor")
    var = page.evaluate("""() => { const d = document.createElement('div'); d.style.background = 'var(--edops-page-bg)';
        document.body.appendChild(d); const c = getComputedStyle(d).backgroundColor; d.remove(); return c; }""")
    assert bg("body") == var
    assert bg("#ex-right .tab-content") == "rgb(255, 255, 255)"
