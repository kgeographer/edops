"""
test_live_server.py
-------------------
Smoke tests against the live production server.

Skipped entirely unless EDOPS_LIVE_URL is set. Run after each deployment:

    EDOPS_LIVE_URL=https://edops.computingplace.org python -m pytest tests/test_live_server.py -v

Tests a minimal but meaningful subset: health, signature structure, version,
flat mode, Band T, a 404 for an ocean point, and the two areal endpoints
(/area by polity, /areas by scope). Does not depend on the local database.

The areal tests assume the v0.4 surface (/areas takes scope=, not the old
type=); run against edops04 pre-cutover, against edops.computingplace.org after.
"""

import os
import pytest
import httpx

BASE = os.getenv("EDOPS_LIVE_URL", "").rstrip("/")
TIMBUKTU = {"lat": 16.76618535, "lon": -3.00777252}


def _skip_if_no_url():
    if not BASE:
        pytest.skip("EDOPS_LIVE_URL not set — skipping live server tests")


@pytest.fixture(scope="module")
def live():
    """httpx client pointed at the live server."""
    _skip_if_no_url()
    with httpx.Client(base_url=BASE, timeout=15.0) as client:
        yield client


@pytest.fixture(scope="module")
def sig(live):
    r = live.get("/api/signature", params={**TIMBUKTU, "bands": "ABCDE"})
    assert r.status_code == 200, f"signature returned {r.status_code}"
    return r.json()


@pytest.fixture(scope="module")
def sig_flat(live):
    r = live.get("/api/signature", params={**TIMBUKTU, "bands": "ABCDE", "flat": "true"})
    assert r.status_code == 200, f"flat signature returned {r.status_code}"
    return r.json()


@pytest.fixture(scope="module")
def sig_t(live):
    r = live.get("/api/signature", params={
        **TIMBUKTU, "bands": "T", "from_year": 1200, "to_year": 1400
    })
    assert r.status_code == 200, f"Band T returned {r.status_code}"
    return r.json()


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

def test_health(live):
    r = live.get("/api/health")
    assert r.status_code == 200
    assert r.json().get("status") == "ok"


# ---------------------------------------------------------------------------
# Signature — structure and version
# ---------------------------------------------------------------------------

def test_signature_200(sig):
    pass  # fixture already asserts 200


def test_signature_version(sig):
    assert sig["meta"]["signature_version"] == "0.4"


def test_signature_has_profile_groups(sig):
    assert "profile_groups" in sig
    for band in "ABCDE":
        assert band in sig["profile_groups"], f"Band {band} missing from profile_groups"


def test_signature_no_flat_mirror(sig):
    """Default response must not duplicate fields as flat top-level keys."""
    flat_sentinel = "aridity"  # always in Band C
    assert flat_sentinel not in sig, (
        f"'{flat_sentinel}' found at top level — flat mirror should not appear in default response"
    )


def test_signature_meta_fields(sig):
    meta = sig["meta"]
    for key in ("signature_version", "generated", "query", "scope", "data_sources"):
        assert key in meta, f"meta missing '{key}'"


def test_signature_timbuktu_values(sig):
    """Spot-check a few known values for Timbuktu."""
    items = {it["key"]: it["value"] for band in sig["profile_groups"].values()
             for it in band.get("items", [])}
    assert items.get("temp_yr") == pytest.approx(28.2, abs=1.0), "temp_yr out of expected range"
    assert items.get("aridity") is not None
    assert items.get("ecoregion") == "Sahelian Acacia savanna"


# ---------------------------------------------------------------------------
# Flat mode
# ---------------------------------------------------------------------------

def test_flat_no_profile_groups(sig_flat):
    assert "profile_groups" not in sig_flat


def test_flat_has_field_values(sig_flat):
    for key in ("aridity", "temp_yr", "precip_yr", "dist_sink"):
        assert key in sig_flat, f"flat response missing '{key}'"


def test_flat_has_meta(sig_flat):
    assert "meta" in sig_flat
    assert sig_flat["meta"]["signature_version"] == "0.4"


# ---------------------------------------------------------------------------
# Band T
# ---------------------------------------------------------------------------

def test_band_t_present(sig_t):
    assert "T" in sig_t.get("profile_groups", {}), "Band T missing from profile_groups"


def test_band_t_status_ok(sig_t):
    assert sig_t["profile_groups"]["T"].get("_status") == "ok"


def test_band_t_has_pdsi_series(sig_t):
    t = sig_t["profile_groups"]["T"]
    assert "pdsi_series" in t
    assert len(t["pdsi_series"]) > 0


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------

def test_ocean_point_404(live):
    """Mid-Pacific point should return 404 — no basin covers open ocean."""
    r = live.get("/api/signature", params={"lat": 0.0, "lon": -140.0})
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# /area — areal signature for a named polity
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def area_polity(live):
    r = live.get("/api/area", params={"polity": "Northern Song", "year": 1000, "bands": "ABCDE"})
    assert r.status_code == 200, f"/api/area returned {r.status_code}: {r.text[:300]}"
    return r.json()


def test_area_resolver_block(area_polity):
    res = area_polity["resolver"]
    assert res["type"] == "polity"
    assert res["polity"] == "Northern Song"
    assert res["year"] == 1000


def test_area_has_member_basins(area_polity):
    assert len(area_polity.get("member_ids", [])) > 0


def test_area_row_envelope(area_polity):
    assert set(area_polity.get("bands", [])) == set("ABCDE"), "bands list should echo the request"
    rows = area_polity.get("rows")
    assert isinstance(rows, list) and len(rows) > 0, "no variable rows in /api/area response"
    seen = {row["band"] for row in rows}
    assert seen and seen <= set("ABCDE"), f"unexpected band label(s) on rows: {seen}"


def test_area_unknown_polity_404(live):
    r = live.get("/api/area", params={"polity": "Nowhere Empire", "year": 1000})
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# /areas — scope-dispatched areal signature
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def areas_buffer(live):
    r = live.get("/api/areas", params={**TIMBUKTU, "scope": "buffer", "radius_km": 100, "bands": "ABCDE"})
    assert r.status_code == 200, f"/api/areas returned {r.status_code}: {r.text[:300]}"
    return r.json()


def test_areas_scope_block(areas_buffer):
    nb = areas_buffer["scope"]
    assert nb["type"] == "buffer"
    assert nb["n_units"] > 0


def test_areas_row_envelope(areas_buffer):
    assert set(areas_buffer.get("bands", [])) == set("ABCDE"), "bands list should echo the request"
    rows = areas_buffer.get("rows")
    assert isinstance(rows, list) and len(rows) > 0, "no variable rows in /api/areas response"
    seen = {row["band"] for row in rows}
    assert seen and seen <= set("ABCDE"), f"unexpected band label(s) on rows: {seen}"


def test_areas_missing_param_422(live):
    """scope=buffer without radius_km must be rejected, not 500."""
    r = live.get("/api/areas", params={**TIMBUKTU, "scope": "buffer"})
    assert r.status_code == 422
    assert "radius_km" in r.text
