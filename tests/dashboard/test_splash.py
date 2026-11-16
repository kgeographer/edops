"""Splash (/edops): two example dropdowns drawn from the shared list, three tiles, GA tag."""
import json
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
EXAMPLES = json.loads((ROOT / "app" / "web" / "dashboard_examples.json").read_text(encoding="utf-8"))


def _page():
    from app.main import app
    r = TestClient(app).get("/edops")
    assert r.status_code == 200
    return r.text


def test_splash_renders_with_ga_and_tiles():
    html = _page()
    assert "gtag/js?id=G-5K56B8BCD9" in html
    for href in ('href="/dashboard"', 'href="/using"', 'href="/explorer"'):
        assert href in html


def test_splash_dropdowns_list_every_example():
    html = _page()
    assert html.count("<option") == 2 + len(EXAMPLES["settlements"]) + len(EXAMPLES["polities"])
    for e in EXAMPLES["settlements"] + EXAMPLES["polities"]:
        assert e["label"] in html


def test_example_urls_open_the_dashboard_with_versioned_parameters():
    from app.web.pages import _dashboard_examples
    d = _dashboard_examples()
    for s in d["settlements"]:
        u = urlparse(s["url"]); q = parse_qs(u.query)
        assert u.path == "/dashboard"
        assert (float(q["lat"][0]), float(q["lon"][0]), q["name"][0], q["v"][0]) == (s["lat"], s["lon"], s["name"], "1")
    for p in d["polities"]:
        u = urlparse(p["url"]); q = parse_qs(u.query)
        assert u.path == "/dashboard" and q["scope"] == ["polity"] and q["polity"] == [p["name"]] and q["v"] == ["1"]


def test_every_settlement_example_has_a_stored_profile_for_its_basin():
    index = {p["slug"]: p for p in json.loads((ROOT / "app" / "static" / "profiles" / "index.json").read_text())}
    for s in EXAMPLES["settlements"]:
        assert s["profile"] in index
        rec = json.loads((ROOT / "app" / "static" / "profiles" / f"{s['profile']}.json").read_text())
        assert not rec["no_basin"]


def test_examples_are_unique_and_tristan_is_not_an_example():
    ids = [e["id"] for e in EXAMPLES["settlements"] + EXAMPLES["polities"]]
    assert len(ids) == len(set(ids))
    assert "tristan-da-cunha" not in ids
