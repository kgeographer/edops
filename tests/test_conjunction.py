"""
WO6c conjunction panel — engine contract + regression against the WO6b notebook.

The conjunction path (app/db/seasonality.py: find_conjunction) replaces the composite-distance
Similarity panel with a non-compensatory conjunction on the raw twelve-value precipitation curve.
These tests pin it to the validated notebook result (wo6b_compare_curves.ipynb Cell 16) and to the
WO6c accept gate.

DB-backed tests skip when the database is unreachable. The registry-shape test needs no DB.
"""

import pytest


# Probe set and coordinates — verbatim from wo6b_compare_curves.ipynb Cell 3.
PROBE_POINTS = [
    ("Mombasa",      -4.0435,   39.6682),
    ("Augsburg",     48.3705,   10.8978),
    ("Tbilisi",      41.6938,   44.8015),
    ("Kaifeng",      34.7986,  114.3413),
    ("Timbuktu",     16.8167,   -2.9833),
    ("George Town",   5.4141,  100.3288),
    ("Santiago",    -33.4489,  -70.6693),
    ("Yakutsk",      62.0280,  129.7326),
    ("Nairobi",      -1.2864,   36.8172),
]
PROBE_IDS = [("Somalia", 1060006860), ("Tennessee", 7060610850)]

# climate.union result-set size at corr cut (0.80, 0.90, 0.95), all other bands at Cell 16
# defaults (ratio 1.5, cv 0.15, T level 3, T range 4). Captured from Cell 16 output.
UNION_COUNTS = {
    "Mombasa":     (8,   6,   3),
    "Augsburg":    (40,  35,  18),
    "Tbilisi":     (51,  14,  6),
    "Kaifeng":     (35,  34,  32),
    "Timbuktu":    (108, 102, 92),
    "George Town": (27,  8,   2),
    "Santiago":    (1,   1,   1),
    "Yakutsk":     (47,  47,  47),
    "Nairobi":     (12,  7,   0),
    "Somalia":     (2,   2,   2),
    "Tennessee":   (37,  20,  10),
}


# ---------------------------------------------------------------------------
# Registry shape — no DB required
# ---------------------------------------------------------------------------

def test_conjunction_registry_shape():
    """Three Climate lenses; temperature carries NO shape term (WO6c Part D)."""
    from app.db.seasonality import get_conjunction_registry

    reg = {l["lens_id"]: l for l in get_conjunction_registry()}
    assert set(reg) == {"climate.precip", "climate.temp", "climate.union"}

    precip = [c["condition"] for c in reg["climate.precip"]["conditions"]]
    assert precip == ["precip_shape", "precip_magnitude", "precip_amplitude_cv"]
    assert reg["climate.precip"]["shade_by"] == "precip_shape"

    # Temperature: level + range only, no shape term, no shading correlation.
    temp = [c["condition"] for c in reg["climate.temp"]["conditions"]]
    assert temp == ["temp_level", "temp_range"]
    assert reg["climate.temp"]["shade_by"] is None
    assert "precip_shape" not in temp and "temp_shape" not in temp

    # Union is the five-condition conjunction; precip/temp are subsets of it.
    union = [c["condition"] for c in reg["climate.union"]["conditions"]]
    assert union == precip + temp
    assert reg["climate.union"]["shade_by"] == "precip_shape"


# ---------------------------------------------------------------------------
# DB-backed regression + accept gate
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def conj_conn(db_available):
    if not db_available:
        pytest.skip("DB not available")
    from scripts.shared.db_utils import db_connect
    from app.db.seasonality import load_similarity_index
    conn = db_connect()
    load_similarity_index(conn, level=6)   # builds the L06 conjunction index
    yield conn
    conn.close()


@pytest.fixture(scope="module")
def probe_ids(conj_conn):
    ids = {}
    with conj_conn.cursor() as cur:
        for name, lat, lon in PROBE_POINTS:
            cur.execute(
                "SELECT hybas_id FROM public.basin06 "
                "WHERE ST_Within(ST_SetSRID(ST_MakePoint(%s, %s), 4326), geom) "
                "ORDER BY ST_Area(geom::geography) ASC LIMIT 1",
                (lon, lat),
            )
            row = cur.fetchone()
            assert row is not None, f"{name} did not resolve to a basin"
            ids[name] = int(row[0])
    for name, h in PROBE_IDS:
        ids[name] = h
    return ids


def test_union_counts_match_wo6b_cell16(conj_conn, probe_ids):
    """Engine reproduces the validated Cell 16 result-set sizes for every probe, every cut."""
    from app.db.seasonality import find_conjunction

    mismatches = []
    for name, expected in UNION_COUNTS.items():
        h = probe_ids[name]
        for cut, exp in zip((0.80, 0.90, 0.95), expected):
            meta, _ = find_conjunction(
                h, lens_id="climate.union", bands={"precip_shape": cut}, level=6)
            if meta["set_size"] != exp:
                mismatches.append(f"{name} @corr>={cut}: got {meta['set_size']}, expected {exp}")
    assert not mismatches, "Cell 16 regression mismatches:\n" + "\n".join(mismatches)


def test_timbuktu_cumulative_attrition(conj_conn, probe_ids):
    """Timbuktu's ordered attrition matches Cell 16 exactly (corr 2148 -> ... -> 102)."""
    from app.db.seasonality import find_conjunction

    meta, _ = find_conjunction(
        probe_ids["Timbuktu"], lens_id="climate.union",
        bands={"precip_shape": 0.90}, level=6)
    remaining = [a["remaining"] for a in meta["attrition"]]
    assert remaining == [2148, 645, 119, 113, 102]


def test_accept_gate_timbuktu_precip_within_magnitude_band(conj_conn, probe_ids):
    """WO6c accept gate, clause 1: Timbuktu's precipitation set contains no basin outside the
    declared magnitude band — the confirmed defect (0.27x-3.87x under the old panel) is retired
    by construction. Set size matches the notebook's precip conjunction (119)."""
    from app.db.seasonality import find_conjunction

    meta, members = find_conjunction(
        probe_ids["Timbuktu"], lens_id="climate.precip",
        bands={"precip_shape": 0.90, "precip_magnitude": 1.5}, level=6)
    assert meta["set_size"] == 119
    q = meta["query_values"]["pre_total_mm"]
    lo, hi = q / 1.5, q * 1.5
    outside = [m for m in members if not (lo <= m["pre_total_mm"] <= hi)]
    assert not outside, (
        f"{len(outside)} members outside the 1.5x magnitude band around {q:.0f} mm/yr"
    )


def test_empty_is_honest_not_widened(conj_conn, probe_ids):
    """Nairobi empties at the strictest cut (Cell 16: n=0 at corr 0.95). The engine reports the
    empty set plainly and does not widen bands to avoid it (WO6c Part A)."""
    from app.db.seasonality import find_conjunction

    meta, members = find_conjunction(
        probe_ids["Nairobi"], lens_id="climate.union",
        bands={"precip_shape": 0.95}, level=6)
    assert meta["set_size"] == 0
    assert members == []


def test_spatial_spread_reported(conj_conn, probe_ids):
    """Set size and spatial spread are reported alongside membership (WO6c Part A)."""
    from app.db.seasonality import find_conjunction

    meta, members = find_conjunction(
        probe_ids["Timbuktu"], lens_id="climate.precip",
        bands={"precip_shape": 0.90}, level=6)
    assert meta["set_size"] == len(members)
    assert meta["spatial"]["max_dist_from_query_km"] is not None
    assert meta["spatial"]["diameter_km"] is not None
    # Shape-shaded lens returns a correlation per member, descending.
    corrs = [m["corr"] for m in members]
    assert all(c is not None for c in corrs)
    assert corrs == sorted(corrs, reverse=True)
