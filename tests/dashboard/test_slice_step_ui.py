"""Slice steps ask only for what the map needs (WO-08 item 3): members_only on /api/areas, scope=polity."""
import json
import urllib.parse
import urllib.request

import pytest

from .test_handoff_ui import _arrive

pytestmark = pytest.mark.dashboard

SONG = "/dashboard?scope=polity&polity=Northern%20Song&v=1"


def _get(base, **q):
    with urllib.request.urlopen(f"{base}/api/areas?{urllib.parse.urlencode(q)}", timeout=120) as r:
        return json.load(r)


def test_members_only_returns_the_same_ids_without_a_signature(dashboard_server):
    q = dict(scope="polity", polity="Northern Song", year=1000, level=8)
    lean = _get(dashboard_server, members_only="true", **q)
    full = _get(dashboard_server, bands="A", **q)
    assert set(lean) == {"member_ids", "resolver"}
    assert sorted(lean["member_ids"]) == sorted(full["member_ids"]) and lean["member_ids"]
    assert lean["resolver"] == full["resolver"]


def test_without_the_option_the_signature_is_unchanged(dashboard_server):
    full = _get(dashboard_server, scope="polity", polity="Northern Song", year=1000, level=8, bands="A")
    assert full["rows"] and "scope" in full and "member_ids" in full


def test_a_slice_step_sends_members_only_and_no_bands(dashboard_server, page):
    seen = []
    page.on("request", lambda r: seen.append(r.url) if "/api/areas" in r.url else None)
    _arrive(page, dashboard_server, SONG, "v3-tab-map-btn")
    seen.clear()
    page.click("#v3-btn-next")
    page.wait_for_timeout(1500)
    queries = [dict(p.split("=", 1) for p in u.split("?", 1)[1].split("&")) for u in seen]
    assert queries, "a slice step should still ask for the member ids"
    assert all(q.get("members_only") == "true" and "bands" not in q and "detail" not in q for q in queries)
