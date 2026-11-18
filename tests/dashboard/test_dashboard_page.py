"""Dashboard page (a clone of the Sandbox, WO-03): renders, noindex, GA tag, its own nav, Profile tab, shared examples."""
import json
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
EXAMPLES = json.loads((ROOT / "app" / "web" / "dashboard_examples.json").read_text(encoding="utf-8"))


def _get(path):
    from app.main import app
    r = TestClient(app).get(path)
    assert r.status_code == 200
    return r.text


def test_dashboard_page_renders():
    html = _get("/dashboard")
    assert "EDOPS Dashboard" in html
    assert "gtag/js?id=G-5K56B8BCD9" in html
    assert '<meta name="robots" content="noindex">' in html


def test_dashboard_header_has_its_own_navigation():
    html = _get("/dashboard")
    for href in ('href="/edops"', 'href="/dashboard"', 'href="/using"', 'href="/explorer"'):
        assert href in html
    assert 'href="/sandbox"' not in html and 'href="/workbench"' not in html


def test_dashboard_has_a_profile_tab_after_the_map_and_keeps_the_sandbox_ids():
    html = _get("/dashboard")
    assert html.index('id="v3-tab-map-btn"') < html.index('id="v3-tab-profile-btn"') < html.index('id="v3-tab-sig-btn"')
    for id_ in ("v3-tab-map-btn", "v3-tab-sig-btn", "v3-sig-btn", "v3-scope-select", "v3-level", "v3-polity-sig-btn", "v3-slice-slider"):
        assert f'id="{id_}"' in html


def test_dashboard_dropdowns_use_the_shared_examples():
    html = _get("/dashboard")
    for e in EXAMPLES["settlements"] + EXAMPLES["polities"]:
        assert e["label"] in html
    assert "San Francisco" not in html and "Tristan" not in html


def test_using_page_renders_with_the_same_navigation():
    html = _get("/using")
    assert "Using EDOPS" in html and 'href="/dashboard"' in html and 'href="/sandbox"' not in html


def test_sandbox_and_workbench_keep_their_navigation():
    for path in ("/sandbox", "/workbench"):
        html = _get(path)
        assert 'href="/sandbox"' in html and 'href="/workbench"' in html and 'href="/using"' not in html


def test_the_explorer_has_the_dashboard_navigation():
    html = _get("/explorer")
    assert 'href="/dashboard"' in html and 'href="/using"' in html and 'href="/sandbox"' not in html and 'href="/workbench"' not in html
