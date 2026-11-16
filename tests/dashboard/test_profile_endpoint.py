"""/api/profile: the stored profile of a basin, keyed by (level, hybas_id); the Dashboard's Profile tab reads it."""
import json
from pathlib import Path

from fastapi.testclient import TestClient

PROFILES = Path(__file__).resolve().parents[2] / "app" / "static" / "profiles"


def _client():
    from app.main import app
    return TestClient(app)


def _records():
    index = json.loads((PROFILES / "index.json").read_text())
    return [json.loads((PROFILES / f"{p['slug']}.json").read_text()) for p in index]


def test_each_stored_basin_returns_its_own_record():
    c = _client()
    recs = [r for r in _records() if not r["no_basin"]]
    assert len(recs) == 9
    for r in recs:
        resp = c.get("/api/profile", params={"level": 6, "hybas_id": r["hybas_id"]})
        assert resp.status_code == 200
        body = resp.json()
        assert body["place"] == r["place"] and body["hybas_id"] == r["hybas_id"] and body["sections"]


def test_a_basin_without_a_stored_profile_is_404():
    r = _client().get("/api/profile", params={"level": 6, "hybas_id": 1})
    assert r.status_code == 404


def test_level_8_has_no_stored_profiles():
    rec = next(r for r in _records() if not r["no_basin"])
    r = _client().get("/api/profile", params={"level": 8, "hybas_id": rec["hybas_id"]})
    assert r.status_code == 404


def test_missing_or_bad_parameters_are_422():
    c = _client()
    assert c.get("/api/profile").status_code == 422
    assert c.get("/api/profile", params={"level": 6, "hybas_id": "x"}).status_code == 422


def test_the_route_is_internal():
    from app.main import app
    assert "/api/profile" not in _client().get("/openapi.json").json()["paths"]
