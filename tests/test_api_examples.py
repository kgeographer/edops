"""
test_api_examples.py
--------------------
Smoke tests that mirror the example curl requests in app/static/api_guide.html.
One test per example; all are skipped if the DB is unavailable.

Examples tested:
  1. Athens         — bands=AB    (static only, no temporal)
  2. Samarkand      — bands=ABCDE (full baseline, no temporal)
  3. Rome           — bands=ABCT, from_year=1,   to_year=400   (imperial period)
  4. Kaifeng        — bands=ABCT, from_year=960, to_year=1127  (Song dynasty)
  5. Timbuktu       — bands=ABT,  from_year=1200, to_year=1600 (medieval)
  6. Kaifeng L6     — bands=ABC,  level=6         (regional scale)
  7. Seasonality    — WO5 contract tests (pinned values + ordering)
  8. Similarity     — WO7 /api/seasonality/similar (SF validation)
"""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client(db_available):
    if not db_available:
        pytest.skip("DB not available")
    from app.main import app
    with TestClient(app) as client:
        yield client


# ---------------------------------------------------------------------------
# 1. Athens — bands=AB
# ---------------------------------------------------------------------------

def test_athens_bands_ab(client):
    r = client.get("/api/signature", params={"lat": 37.97, "lon": 23.73, "bands": "AB"})
    assert r.status_code == 200
    data = r.json()
    pg = data["profile_groups"]
    assert "A" in pg and "B" in pg
    assert "C" not in pg and "T" not in pg
    assert len(pg["A"]["items"]) > 0


# ---------------------------------------------------------------------------
# 2. Samarkand — bands=ABCDE
# ---------------------------------------------------------------------------

def test_samarkand_bands_abcde(client):
    r = client.get("/api/signature", params={"lat": 39.65, "lon": 66.98, "bands": "ABCDE"})
    assert r.status_code == 200
    pg = r.json()["profile_groups"]
    for band in ("A", "B", "C", "D", "E"):
        assert band in pg, f"Missing band {band}"
    assert "T" not in pg


# ---------------------------------------------------------------------------
# 3. Rome — bands=ABCT, early imperial period
# ---------------------------------------------------------------------------

def test_rome_bands_abct(client):
    r = client.get("/api/signature", params={
        "lat": 41.9, "lon": 12.5,
        "bands": "ABCT", "from_year": 1, "to_year": 400,
    })
    assert r.status_code == 200
    data = r.json()
    pg = data["profile_groups"]
    for band in ("A", "B", "C", "T"):
        assert band in pg, f"Missing band {band}"

    t = pg["T"]
    assert t.get("_status") == "ok", f"Band T status: {t.get('_status')}"
    assert len(t["pdsi_series"]) > 0, "pdsi_series empty for Rome 1–400 CE"
    assert len(t["air_series"]) > 0
    assert len(t["prate_series"]) > 0


# ---------------------------------------------------------------------------
# 4. Kaifeng — bands=ABCT, Song dynasty capital
# ---------------------------------------------------------------------------

def test_kaifeng_bands_abct(client):
    r = client.get("/api/signature", params={
        "lat": 34.8, "lon": 114.3,
        "bands": "ABCT", "from_year": 960, "to_year": 1127,
    })
    assert r.status_code == 200
    data = r.json()
    pg = data["profile_groups"]
    for band in ("A", "B", "C", "T"):
        assert band in pg, f"Missing band {band}"

    t = pg["T"]
    assert t.get("_status") == "ok", f"Band T status: {t.get('_status')}"
    assert len(t["pdsi_series"]) == 1127 - 960 + 1, (
        f"Expected {1127-960+1} PDSI years; got {len(t['pdsi_series'])}"
    )
    # HYDE land use should be present for this medieval window
    hyde = t.get("hyde_land_use", [])
    assert len(hyde) > 0, "Expected HYDE land-use epochs for Kaifeng 960–1127"


# ---------------------------------------------------------------------------
# 5. Timbuktu — bands=ABT, medieval period
# ---------------------------------------------------------------------------

def test_timbuktu_bands_abt(client):
    r = client.get("/api/signature", params={
        "lat": 16.77, "lon": -3.01,
        "bands": "ABT", "from_year": 1200, "to_year": 1600,
    })
    assert r.status_code == 200
    pg = r.json()["profile_groups"]
    assert "A" in pg and "B" in pg and "T" in pg
    assert "C" not in pg

    t = pg["T"]
    assert t.get("_status") == "ok"
    assert len(t["pdsi_series"]) == 1600 - 1200 + 1


# ---------------------------------------------------------------------------
# 6. Kaifeng — bands=ABC, level=6 (regional scale)
# ---------------------------------------------------------------------------

def test_kaifeng_level6(client):
    r = client.get("/api/signature", params={
        "lat": 34.8, "lon": 114.3,
        "bands": "ABC", "level": 6,
    })
    assert r.status_code == 200
    data = r.json()
    assert data["meta"]["query"]["level"] == 6
    pg = data["profile_groups"]
    for band in ("A", "B", "C"):
        assert band in pg
    assert "T" not in pg


# ---------------------------------------------------------------------------
# 7. WO5 Seasonality — array presence, length, pinned scalars, ordering
# ---------------------------------------------------------------------------

def test_seasonality_arrays_rome(client):
    """Monthly arrays present and length-12 for Rome (L08 default)."""
    r = client.get("/api/signature", params={"lat": 41.9, "lon": 12.5, "bands": "C"})
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data.get("pre_mm_monthly"), list), "pre_mm_monthly missing"
    assert len(data["pre_mm_monthly"]) == 12
    assert isinstance(data.get("tmp_dc_monthly"), list), "tmp_dc_monthly missing"
    assert len(data["tmp_dc_monthly"]) == 12


def test_seasonality_scalars_rome(client):
    """Pinned seasonality indices for Rome L08 — tolerance ±0.05."""
    r = client.get("/api/signature", params={"lat": 41.9, "lon": 12.5, "bands": "C"})
    assert r.status_code == 200
    data = r.json()
    pre_conc   = data["pre_concentration"]
    phase_off  = data["seas_phase_offset"]
    tmp_amp    = data["tmp_seas_amp"]
    assert pre_conc  is not None
    assert phase_off is not None
    assert tmp_amp   is not None
    # Pinned from notebook cell 8 (2026-07-14):
    assert abs(pre_conc  - 0.280) < 0.05, f"pre_concentration {pre_conc:.3f} outside ±0.05 of 0.280"
    assert abs(phase_off - 4.486) < 0.05, f"seas_phase_offset {phase_off:.3f} outside ±0.05 of 4.486"
    assert abs(tmp_amp   - 16.4)  < 1.0,  f"tmp_seas_amp {tmp_amp:.1f} outside ±1.0 of 16.4"


def test_seasonality_discrimination(client):
    """Ordering relationships encode the Mediterranean vs monsoon discrimination story."""
    rome   = client.get("/api/signature", params={"lat": 41.9,  "lon": 12.5,  "bands": "C"}).json()
    delhi  = client.get("/api/signature", params={"lat": 28.6,  "lon": 77.2,  "bands": "C"}).json()
    london = client.get("/api/signature", params={"lat": 51.5,  "lon": -0.12, "bands": "C"}).json()

    rome_offset   = rome["seas_phase_offset"]
    delhi_offset  = delhi["seas_phase_offset"]
    london_conc   = london["pre_concentration"]

    # Mediterranean (Rome) has large precip–temp phase offset; monsoon (Delhi) small
    assert rome_offset  is not None
    assert delhi_offset is not None
    assert rome_offset  > 3.5,  f"Rome seas_phase_offset {rome_offset:.3f} — expected > 3.5"
    assert delhi_offset < 1.5,  f"Delhi seas_phase_offset {delhi_offset:.3f} — expected < 1.5"
    assert rome_offset  > delhi_offset, "Rome offset should exceed Delhi offset"

    # London has low precip concentration (year-round rain)
    assert london_conc is not None
    assert london_conc < 0.2, f"London pre_concentration {london_conc:.3f} — expected < 0.2"


# ---------------------------------------------------------------------------
# 8. WO7 Similarity — /api/seasonality/similar SF validation
# ---------------------------------------------------------------------------

def test_seasonality_similar_sf(client):
    """SF query returns Mediterranean-climate analogs (IQ/CL/IR/JO) in top-10 results."""
    r = client.get("/api/seasonality/similar", params={"lat": 37.77, "lon": -122.42, "n": 20})
    assert r.status_code == 200
    data = r.json()

    assert data["metric"] == "normalized_euclidean_2idx"
    assert data["query_basin_id"] is not None
    assert data["query_pre_concentration"] is not None
    assert data["query_seas_phase_offset"] is not None

    results = data["results"]
    assert len(results) > 0, "Expected at least one result"

    # All results must have required fields
    for res in results:
        assert "basin_rank" in res
        assert "basin_id" in res
        assert "distance" in res
        assert "place_name" in res
        assert "ccodes" in res

    # Distances must be non-negative and ascending
    dists = [r["distance"] for r in results]
    assert all(d >= 0 for d in dists)
    assert dists == sorted(dists), "Results must be ordered by distance ascending"

    # Top-10 must include at least one Mediterranean-climate country
    top_ccodes = {cc for r in results[:10] for cc in (r["ccodes"] or [])}
    med_countries = {"IQ", "CL", "IR", "JO", "EG", "MA", "ES", "PT"}
    assert top_ccodes & med_countries, (
        f"Expected Mediterranean analogs in top-10 ccodes, got {top_ccodes}"
    )
