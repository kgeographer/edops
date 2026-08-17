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
  8. Band T shape   — contract tests for the 2026-08 restructuring (lmr_status,
                       hyde_land_use.epochs, per-source availability notes); the
                       tripwire for the next time this shape changes

(The old WO7a /api/similarity + /api/similarity/lenses examples — items 8/9 — were retired
CITYKIN WO1: the pre-WO6 climate.precip/climate.temp lenses and their vestigial sandbox
fallback panel are gone, superseded by the WO6c conjunction panel at /api/similarity/conjunction.)
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
    assert t.get("lmr_status") == "available"


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
    # HYDE land use should be present for this medieval window. hyde_land_use is a
    # dict ({epochs, n_epochs, _note}), not a list, since the 2026-08 restructuring --
    # check the epochs list itself, not len() of the dict's own keys.
    hyde = t.get("hyde_land_use", {})
    epochs = hyde.get("epochs", [])
    assert len(epochs) > 0, "Expected HYDE land-use epochs for Kaifeng 960–1127"
    assert "cropland_pct" in epochs[0] and "cropland_std" in epochs[0], (
        "hyde_land_use epochs missing expected stats fields (cropland_pct/cropland_std)"
    )


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
# 8. Band T shape contract — pins the 2026-08-16 restructuring so the next shape
#    change fails a test instead of silently going stale in the docs for months.
# ---------------------------------------------------------------------------

def test_band_t_out_of_range_status_stays_ok(client):
    """_status stays "ok" even when a source has no data for the period -- LMR,
    eVolv2k, and HYDE each have independent coverage windows, and availability is
    now signaled per-source (lmr_status, the *_note fields), not via _status itself.
    Confirmed against live output 2026-08-16; update this test in the same commit
    as any future Band T shape change, and re-run generate_api_guide.py + refresh
    documentation/edops_schema.json alongside it.
    """
    r = client.get("/api/signature", params={
        "lat": 16.8167, "lon": -2.9833,
        "bands": "T", "from_year": -2100, "to_year": -1800,
    })
    assert r.status_code == 200
    t = r.json()["profile_groups"]["T"]

    assert t.get("_status") == "ok", (
        "_status should stay 'ok' once years are supplied, even when LMR/eVolv2k "
        "have no coverage for the period -- unavailability is per-source, not all-or-nothing"
    )
    assert t.get("lmr_status") == "out_of_range"
    assert t.get("pdsi_series") == []
    assert t.get("lmr_out_of_range_note"), "Expected a note explaining LMR has no coverage here"
    assert t.get("volcanic_events_note"), "Expected a note explaining eVolv2k has no coverage here"

    # HYDE still has coverage this far back even though LMR/eVolv2k don't
    hyde = t.get("hyde_land_use", {})
    assert len(hyde.get("epochs", [])) > 0, "HYDE should still return epochs for -2100..-1800 CE"


def test_band_t_available_shape(client):
    """Full-availability Band T response has the current field set -- lmr_status,
    the four *_note fields (null when nothing to report), and hyde_land_use's
    {epochs, n_epochs, _note} structure. Same tripwire purpose as the test above.
    """
    r = client.get("/api/signature", params={
        "lat": 16.8167, "lon": -2.9833,
        "bands": "T", "from_year": 1350, "to_year": 1600,
    })
    assert r.status_code == 200
    t = r.json()["profile_groups"]["T"]

    assert t.get("_status") == "ok"
    assert t.get("lmr_status") == "available"
    for note_field in ("volcanic_events_note", "lmr_out_of_range_note", "lmr_fidelity_note",
                        "lmr_proxy_bias_note"):
        assert note_field in t, f"Missing {note_field} -- per-source availability fields changed shape"

    hyde = t.get("hyde_land_use", {})
    assert set(hyde.keys()) >= {"epochs", "n_epochs", "_note"}, (
        f"hyde_land_use shape changed -- got keys {list(hyde.keys())}"
    )
