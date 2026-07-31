"""
test_societies_scan.py
-----------------------
Tests for /api/societies/env-scan — CITYKIN WO4 Step 2, the Societies-tab PCA-cluster
replacement. Wraps scripts/cdop/distance_core.scan() over the cached WO8-family substrate
(app/db/societies_scan.py); unit coverage for the engine itself lives in
tests/cdop/test_distance_core.py.

All DB-hitting tests are skipped if the DB is unavailable (the app's other startup indices
still need a connection even though this endpoint's own data source is a parquet).
"""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client(db_available):
    if not db_available:
        pytest.skip("DB not available")
    from app.main import app
    # `with` is required, not just `TestClient(app)` -- only entering the context manager runs
    # the ASGI lifespan startup (which loads this endpoint's substrate cache). Other test files
    # in this suite get away with a bare TestClient(app) only because module-level caches are
    # process-global and something upstream (test_api_examples.py) already ran the `with` form
    # first in the same pytest session -- an implicit ordering dependency this file doesn't rely on.
    with TestClient(app) as c:
        yield c


def test_subsistence_scan_has_hook_metadata(client):
    r = client.get("/api/societies/env-scan", params={"trait": "subsistence", "value": "Pastoralism"})
    assert r.status_code == 200
    body = r.json()
    assert body["trait"] == "subsistence"
    assert body["value"] == "Pastoralism"
    assert body["n_focus"] == 76
    assert body["hook"]["has_hook"] is True
    assert body["hook"]["axes"] == ["water", "thermal"]
    assert set(body["lenses"].keys()) == {"water", "thermal", "overall", "terrain"}


def test_subsistence_scan_includes_scatter_coordinates(client):
    r = client.get("/api/societies/env-scan", params={"trait": "subsistence", "value": "Pastoralism"})
    body = r.json()
    sc = body["scatter"]
    assert sc["x_var"] == "ari_log" and sc["y_var"] == "temperature_annual"
    assert len(sc["focus"]) == 76
    assert len(sc["backdrop"]) + len(sc["focus"]) <= 1133   # some backdrop rows drop for NaN coords
    assert all({"soc_id", "x", "y", "name"} <= p.keys() for p in sc["focus"][:5])
    assert all({"soc_id", "x", "y"} <= p.keys() for p in sc["backdrop"][:5])


def test_religion_scan_has_no_hook_metadata(client):
    r = client.get("/api/societies/env-scan",
                    params={"trait": "religion", "value": "Active, but not supporting morality"})
    assert r.status_code == 200
    body = r.json()
    assert body["n_focus"] == 40
    assert body["hook"]["has_hook"] is False
    assert body["hook"]["axes"] is None
    assert "scatter" not in body
    # Reproduces WO8d's Part C table exactly (wo4_findings.md) -- a live regression check that
    # the endpoint's numbers stay pinned to the validated reference, not just that it responds.
    terrain = body["lenses"]["terrain"]
    assert terrain["n_backdrop"] == 1124
    assert terrain["obs_cohesion"] == pytest.approx(1.207, abs=1e-3)
    assert terrain["pct_tighter_than_random"] == pytest.approx(44.10, abs=0.5)


def test_composition_note_no_dominance_threshold(client):
    r = client.get("/api/societies/env-scan", params={"trait": "subsistence", "value": "Pastoralism"})
    body = r.json()
    comp = body["composition"]
    assert comp["n_total"] == 76
    assert len(comp["top_families"]) == 3
    assert comp["top_families"][0]["family_id"] == "afro1255"


def test_unknown_trait_is_400(client):
    r = client.get("/api/societies/env-scan", params={"trait": "bogus", "value": "x"})
    assert r.status_code == 400


def test_unmatched_value_returns_zero_focus_not_error(client):
    r = client.get("/api/societies/env-scan",
                    params={"trait": "subsistence", "value": "Not A Real Subsistence Value"})
    assert r.status_code == 200
    assert r.json()["n_focus"] == 0
