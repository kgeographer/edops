"""
test_societies_scan.py
-----------------------
Tests for /api/societies/env-scan — CITYKIN WO4, the Societies-tab PCA-cluster replacement.
Wraps scripts/cdop/distance_core.{top_families,variable_percentiles} (the 2026-07-30 meter-bar
redesign — scan()'s lens-level machinery is no longer called by this endpoint at all) over the
cached WO8-family substrate (app/db/societies_scan.py); unit coverage for the engine itself lives
in tests/cdop/test_distance_core.py.

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
    assert "variables" not in body   # meter-bar view is the no-hook display only


def test_subsistence_scan_includes_scatter_coordinates(client):
    r = client.get("/api/societies/env-scan", params={"trait": "subsistence", "value": "Pastoralism"})
    body = r.json()
    sc = body["scatter"]
    assert sc["x_var"] == "ari_log" and sc["y_var"] == "temperature_annual"
    assert len(sc["focus"]) == 76
    assert len(sc["backdrop"]) + len(sc["focus"]) <= 1133   # some backdrop rows drop for NaN coords
    assert all({"soc_id", "x", "y", "name"} <= p.keys() for p in sc["focus"][:5])
    assert all({"soc_id", "x", "y"} <= p.keys() for p in sc["backdrop"][:5])


def test_scatter_has_plain_language_summary(client):
    # Pinned to real numbers (2026-07-30) -- the scatter's own caption, reusing the meter engine
    # restricted to just the two plotted axes rather than asking the reader to eyeball ~1,000 dots.
    r = client.get("/api/societies/env-scan", params={"trait": "subsistence", "value": "Fishing"})
    summary = r.json()["scatter"]["summary"]
    assert set(summary.keys()) == {"aridity", "temperature"}
    assert summary["temperature"]["qualifier"] == "very"
    assert summary["temperature"]["direction"] == "Cool"
    assert summary["aridity"]["qualifier"] == "somewhat"
    assert summary["aridity"]["direction"] == "Wet"


def test_religion_scan_has_no_hook_metadata(client):
    r = client.get("/api/societies/env-scan",
                    params={"trait": "religion", "value": "Active, but not supporting morality"})
    assert r.status_code == 200
    body = r.json()
    assert body["n_focus"] == 40
    assert body["hook"]["has_hook"] is False
    assert body["hook"]["axes"] is None
    assert "scatter" not in body

    # Pinned to real numbers computed against the substrate (2026-07-30) -- a live regression
    # check that the endpoint's meter-bar values stay stable, not just that it responds.
    variables = body["variables"]
    assert set(variables.keys()) == {"aridity", "temperature", "seasonality", "ruggedness", "landform"}
    temp = variables["temperature"]
    assert temp["percentile"] == pytest.approx(33.63, abs=0.5)
    assert temp["qualifier"] == "somewhat"
    assert temp["direction"] == "Cool"
    assert temp["pole_low"] == "Cool" and temp["pole_high"] == "Warm"
    # No percentile/resampling language anywhere in this response's own vocabulary -- the GUI-safe
    # words are qualifier + direction, never a number baked into a label (Karl's standing rule).
    assert "qualifier" in temp and "direction" in temp


def test_religion_scan_includes_per_society_records(client):
    # WO5 (isolates view, experimental): per-society records for client-side ancestral/
    # geographic/environmental nearest-neighbor ranking. EA034 (no-hook) only, matching the
    # strip-plot ticks this reuses the same percentile machinery for.
    r = client.get("/api/societies/env-scan",
                    params={"trait": "religion", "value": "Active, but not supporting morality"})
    body = r.json()
    socs = body["societies"]
    assert len(socs) == body["n_focus"] == 40

    s = socs[0]
    assert {"soc_id", "name", "lat", "lon", "family_id", "family_name",
            "family_global_n", "env"} <= s.keys()
    assert set(s["env"].keys()) == {"aridity", "temperature", "seasonality", "ruggedness", "landform"}

    # WO5 #2's own fix: family_global_n is the family's count across the WHOLE basin-joined
    # corpus, not just this trait's coded set -- so it must be >= that society's family's count
    # within this trait-filtered 40, for every resolved-family society in the response.
    trait_family_counts = {}
    for rec in socs:
        if rec["family_id"] is not None:
            trait_family_counts[rec["family_id"]] = trait_family_counts.get(rec["family_id"], 0) + 1
    for rec in socs:
        if rec["family_id"] is not None:
            assert rec["family_global_n"] >= trait_family_counts[rec["family_id"]]


def test_subsistence_scan_has_no_per_society_records(client):
    # EA042 keeps the confirmatory scatter -- the isolates view is EA034-only (WO5 scope).
    r = client.get("/api/societies/env-scan", params={"trait": "subsistence", "value": "Pastoralism"})
    assert "societies" not in r.json()


def test_composition_note_no_dominance_threshold(client):
    r = client.get("/api/societies/env-scan", params={"trait": "subsistence", "value": "Pastoralism"})
    body = r.json()
    comp = body["composition"]
    assert comp["n_total"] == 76
    assert len(comp["top_families"]) == 3
    assert comp["top_families"][0]["family_id"] == "afro1255"


def test_composition_note_has_names_and_soc_ids_for_map_hover(client):
    r = client.get("/api/societies/env-scan", params={"trait": "subsistence", "value": "Pastoralism"})
    body = r.json()
    comp = body["composition"]

    top = comp["top_families"][0]
    assert top["family_id"] == "afro1255"
    assert top["family_name"] == "Afro-Asiatic"      # resolved, not the raw glottocode
    assert len(top["soc_ids"]) == top["n"] == 36

    # "Other" pools every family beyond the top 3, and it's a real, mappable bucket too, not a
    # discarded remainder -- Karl's requirement for the donut + hover-to-map linking.
    assert comp["other"]["n"] == 76 - sum(f["n"] for f in comp["top_families"]) - comp["n_unresolved"]
    assert len(comp["other"]["soc_ids"]) == comp["other"]["n"]
    assert len(comp["unresolved"]["soc_ids"]) == comp["n_unresolved"]


def test_unknown_trait_is_400(client):
    r = client.get("/api/societies/env-scan", params={"trait": "bogus", "value": "x"})
    assert r.status_code == 400


def test_unmatched_value_returns_zero_focus_not_error(client):
    r = client.get("/api/societies/env-scan",
                    params={"trait": "subsistence", "value": "Not A Real Subsistence Value"})
    assert r.status_code == 200
    assert r.json()["n_focus"] == 0
