"""
WO7 climate classes — label-composition rules + engine contract against the notebook.

Two discrete axes (modality, phase) with a composed cell label, served from an in-memory startup
index (app/db/climate_classes.py). Pure-function tests need no DB; the index tests pin corpus
shares, probe cells, and the hemisphere-blind lens to notebooks/cdop/wo7_climate_classes.ipynb.

DB-backed tests skip when the database is unreachable.
"""
import pytest

from app.db import climate_classes as cc

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


# ---------------------------------------------------------------------------
# Label composition — pure functions, no DB (WO7a label lock)
# ---------------------------------------------------------------------------
def test_compose_modality_first():
    assert cc.cell_label("1-season", "cool-wet") == "One wet season, cool-season rain"
    assert cc.cell_label("1-season", "warm-wet") == "One wet season, warm-season rain"
    assert cc.cell_label("1-season", "no thermal cycle") == "One wet season, no temperature cycle"
    assert cc.cell_label("arid", "warm-wet") == "Arid, warm-season rain"


def test_aseasonal_drops_phase_term():
    """Issue 1: flat rainfall -> timing is meaningless, so the phase term is dropped."""
    for ph in cc.PHASE_ORDER:
        assert cc.cell_label("aseasonal", ph) == "Even year-round"
        assert cc.cell_key("aseasonal", ph) == "aseasonal"   # all 4 collapse to one cell


def test_no_koppen_or_knoben_name_in_labels():
    """Accept gate: no class or cell label uses a Köppen or Knoben name."""
    banned = ("mediterran", "monsoon", "twin", "köppen", "koppen", "knoben")
    labels = {cc.cell_label(m, p) for m in cc.MOD_ORDER for p in cc.PHASE_ORDER}
    labels |= set(cc.MOD_LABEL.values()) | set(cc.PHASE_LABEL.values())
    for lab in labels:
        low = lab.lower()
        assert not any(b in low for b in banned), f"banned name in {lab!r}"


# ---------------------------------------------------------------------------
# DB-backed: in-memory index, pinned to the WO7 notebook
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def class_idx(db_available):
    if not db_available:
        pytest.skip("DB not available")
    from scripts.shared.db_utils import db_connect
    conn = db_connect()
    cc.load_class_index(conn, level=6)
    yield conn
    conn.close()


@pytest.fixture(scope="module")
def probe_ids(class_idx):
    ids = {}
    with class_idx.cursor() as cur:
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
    return ids


def test_corpus_shares_match_notebook(class_idx):
    """Cell 5/6 regression: modality + phase counts at L06."""
    mcats, mvals = cc.axis_values(6, "modality")
    pcats, pvals = cc.axis_values(6, "phase")
    assert len(mvals) == 16338 and len(pvals) == 16338
    mcount = {c["key"]: c["count"] for c in mcats}
    pcount = {c["key"]: c["count"] for c in pcats}
    assert mcount == {"arid": 1434, "aseasonal": 1259, "1-season": 12652,
                      "2-season": 899, "undetermined": 94}
    assert pcount == {"warm-wet": 8272, "cool-wet": 2017,
                      "weak coupling": 3149, "no thermal cycle": 2900}


def test_probe_cells(class_idx, probe_ids):
    """Known-answer probe cells (notebook Cell 7)."""
    def lbl(name):
        return cc.class_lens(6, probe_ids[name])["label"]
    assert lbl("Santiago") == "One wet season, cool-season rain"
    assert lbl("Augsburg") == "One wet season, warm-season rain"
    for trop in ("Mombasa", "George Town", "Nairobi"):
        assert lbl(trop) == "Two wet seasons, no temperature cycle"


def test_lens_hemisphere_blind(class_idx, probe_ids):
    """Santiago's cool-season-rain cell spans both hemispheres — the point of the class lens,
    which the calendar-locked conjunction cannot do. set_size pinned to the Cell 7 count."""
    lens = cc.class_lens(6, probe_ids["Santiago"])
    assert lens["cell"] == "1-season|cool-wet"
    assert lens["set_size"] == 1325
    # Hemisphere-blind: members reach both hemispheres -> a very large spread.
    assert lens["spatial"]["max_dist_from_query_km"] > 10000
    idx = cc._INDEX[6]
    lats = idx["lat"][[idx["id_to_pos"][h] for h in lens["members"]]]
    assert (lats > 10).any() and (lats < -10).any()


def test_aseasonal_lens_has_no_phase(class_idx):
    """An even-year-round basin's lens carries no phase term (Issue 1)."""
    idx = cc._INDEX[6]
    pos = next(i for i, m in enumerate(idx["modality"]) if m == "aseasonal")
    lens = cc.class_lens(6, int(idx["hybas_ids"][pos]))
    assert lens["label"] == "Even year-round"
    assert lens["phase"] is None and lens["phase_label"] is None


def test_axis_values_rejects_bad_axis(class_idx):
    with pytest.raises(ValueError):
        cc.axis_values(6, "not_an_axis")
