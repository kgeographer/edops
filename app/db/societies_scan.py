"""CITYKIN WO4 — the Societies-tab PCA-cluster replacement's data path.

Loads the shared society-basin-signature substrate once at startup (not per-request) and wraps
`scripts.cdop.distance_core` with the two wired D-PLACE traits' hook metadata.

**2026-07-30 meter-bar redesign**: no longer calls `distance_core.scan()` (the lens-level
cohesion/displacement machinery) at all — Karl's review of the four-lens scan found
"tighter than X% of random draws" language cannot appear on a GUI page, and two of the four
lenses bundle two physical variables into one number, so no plain-language gloss could give a
single variable + direction either way. The no-hook display now uses `variable_percentiles()`
(a single deterministic percentile per raw physical variable, no resampling) instead. This also
means `run_societies_env_scan()` no longer pays for `scan()`'s 2000-draw resampling loop across
four lenses on every request — a real performance win, not just a display change, since that
output was going unused everywhere once the meter redesign landed.

**Data source, and the trade-off it makes explicit.** The substrate is
`output/cdop/wo8c_substrate.parquet` — a real, already-validated artifact (WO8a's base society-
basin-climate join, extended by WO8b with the Glottolog family-crosswalk, by WO8c with the
point-window terrain columns), not a throwaway notebook export. It is NOT re-derived from the DB
here: the family-crosswalk step in particular parses local Glottolog CLDF `.trees` files (WO8b
Cell 3), a research-data dependency this module deliberately does not repeat at request time or
even at every app startup. Loading it once into memory at startup (this module) rather than
re-reading it per request follows the project's standing "small per-basin derived results belong
in an in-memory startup index, not a loose parquet read repeatedly" rule for the *access pattern*;
the source file itself stays a parquet (like LISA's, `output/edop/esda/lisa_classifications.parquet`)
rather than a new DB table, to keep this WO's scope to a few days. **Deploy note:** this parquet
needs the same rsync treatment as other gitignored static assets (PMTiles, LISA) — it is not
pushed by `git push`. If any WO8-family notebook ever regenerates the substrate, the server needs
a restart (to reload this module's cache) as well as a fresh rsync.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, Optional

import numpy as np
import pandas as pd

from scripts.cdop.distance_core import top_families, variable_percentiles, VARIABLES
from scripts.cdop.glottolog_family_names import family_name

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SUBSTRATE_PATH = ROOT / "output" / "cdop" / "wo8c_substrate.parquet"

# The two traits currently wired on the Societies tab. EA042 has a named theoretical hook (WO8a
# Part B validated aridity x temperature as the cleanest subsistence separator) -> confirmatory
# display; EA034 has none (WO8d could not test a predicted axis) -> exploratory scan. Hand-flagged
# per Karl's review (2026-07-30): a boolean carries neither what the hook is nor which axes it
# needs, so this records both. Two traits wired -- deliberately not a general rule; see
# `wo4_whc-grouping.md` Step 3 proviso before adding a third trait here.
TRAIT_CONFIG: Dict[str, Dict[str, object]] = {
    "subsistence": {
        "column": "ea042_subsistence",
        "has_hook": True,
        "hook_axes": ["water", "thermal"],
        "hook_source": "WO8a Part B — Climate envelope (aridity x temperature)",
        # The confirmatory scatter's two literal plotted variables -- deliberately raw aridity and
        # temperature, not a PCoA/PCA rotation of the 'overall' lens. A page built to retire a
        # PCA-based display shouldn't replace it with another composite projection; two named,
        # directly-interpretable physical quantities are what "confirmatory illustration" means
        # here. `tmp_seas_amp` (thermal's second variable) still informs the engine's cohesion/
        # displacement stats but isn't a plotted axis.
        "scatter_x": "ari_log", "scatter_x_label": "Aridity index (log)",
        "scatter_y": "temperature_annual", "scatter_y_label": "Mean annual temperature (°C)",
    },
    "religion": {
        "column": "ea034_religion",
        "has_hook": False,
        "hook_axes": None,
        "hook_source": None,
        "scatter_x": None, "scatter_x_label": None,
        "scatter_y": None, "scatter_y_label": None,
    },
}

_substrate: Optional[pd.DataFrame] = None


def load_societies_scan_substrate(path: Optional[Path] = None) -> None:
    """Load and cache the substrate. Call once at app startup (see `app/main.py` lifespan)."""
    global _substrate
    p = path or DEFAULT_SUBSTRATE_PATH
    if not p.exists():
        logger.warning("societies_scan: substrate not found at %s -- /api/societies/env-scan will 503", p)
        _substrate = None
        return
    df = pd.read_parquet(p)
    if "ari_log" not in df.columns and "ari_ix_sav" in df.columns:
        df["ari_log"] = np.log1p(df["ari_ix_sav"])
    _substrate = df
    logger.info("societies_scan: loaded %s (%d rows, %d columns)", p.name, len(df), len(df.columns))


def get_societies_scan_substrate() -> pd.DataFrame:
    if _substrate is None:
        raise RuntimeError(
            "societies_scan substrate not loaded -- call load_societies_scan_substrate() at "
            "startup, or the source parquet is missing from this deployment"
        )
    return _substrate


def run_societies_env_scan(trait: str, value: str) -> Dict[str, object]:
    """`(trait, value)` -> the WO4 payload: composition note (family names + soc_ids, for the
    donut and its map-hover linking) + trait hook metadata, plus either the confirmatory scatter
    (hook traits) or the meter-bar variable percentiles (no-hook traits). `trait` is
    `'subsistence'` (EA042) or `'religion'` (EA034) -- the tab's two wired traits, not a raw
    column name."""
    if trait not in TRAIT_CONFIG:
        raise ValueError(f"unknown trait '{trait}' -- expected one of {sorted(TRAIT_CONFIG)}")

    cfg = TRAIT_CONFIG[trait]
    sub = get_societies_scan_substrate()
    trait_col = cfg["column"]
    is_focus = sub[trait_col].notna() & (sub[trait_col] == value)

    composition = top_families(
        sub.loc[is_focus, "family_id"], soc_ids=sub.loc[is_focus, "soc_id"],
    )
    for entry in composition["top_families"]:
        entry["family_name"] = family_name(entry["family_id"])

    payload: Dict[str, object] = {
        "trait": trait,
        "value": value,
        "n_focus": int(is_focus.sum()),
        "hook": {
            "has_hook": cfg["has_hook"],
            "axes": cfg["hook_axes"],
            "source": cfg["hook_source"],
        },
        "composition": composition,
    }

    if cfg["has_hook"]:
        payload["scatter"] = _build_scatter(sub, trait_col, value, cfg)
        # A plain-language read of the same two axes the scatter plots -- reuses the meter-bar
        # engine (variable_percentiles) rather than asking the reader to eyeball ~1,000 dots
        # unaided (Karl, 2026-07-30: "can we do better?" after the scatter alone read as an
        # inscrutable cloud for a trait -- Fishing -- whose real driver isn't on either axis).
        payload["scatter"]["summary"] = variable_percentiles(
            sub, trait_col=trait_col, value=value,
            variables={"aridity": VARIABLES["aridity"], "temperature": VARIABLES["temperature"]},
        )["variables"]
    else:
        payload["variables"] = variable_percentiles(sub, trait_col=trait_col, value=value)["variables"]
        # WO4 strip-plot redesign (2026-08-10): one tick per focus society, not just its group
        # mean -- see _per_society_ticks() below for why this is a separate pass rather than an
        # addition inside variable_percentiles() itself.
        ticks_by_var = _per_society_ticks(sub, is_focus)
        for key, ticks in ticks_by_var.items():
            if key in payload["variables"]:
                payload["variables"][key]["ticks"] = ticks

    return payload


def _per_society_ticks(sub: pd.DataFrame, is_focus: pd.Series,
                        variables: Optional[Dict[str, Dict[str, str]]] = None) -> Dict[str, list]:
    """Per-society percentile position for the strip plot -- one tick per focus-group society
    per variable, each against the FULL basin-joined backdrop (`sub`, not the focus subset),
    matching the WO's own caption rule ("positions are always against all basin-joined
    societies"). Separate from `variable_percentiles()` rather than folded into it: that
    function reports one percentile per (trait, value) -- the group MEAN's position -- and nine
    lines of module docstring already explain why that single-number, no-resampling design is
    deliberate; this is a different shape of output (an array per variable) for a different
    consumer (the strip plot's ticks), not a variant of the same computation.

    `rank(pct=True)` (default `na_option='keep'`) excludes NaNs from both the ranking and the
    denominator, so a focus row's tick position is its percentile among backdrop rows that have
    a non-null value for that column -- same complete-case convention `variable_percentiles()`
    uses via `.dropna()`.
    """
    variables = variables or VARIABLES
    out: Dict[str, list] = {}
    for key, cfg in variables.items():
        col = cfg["column"]
        pct = sub[col].rank(pct=True) * 100
        rows = pd.DataFrame({
            "soc_id": sub["soc_id"], "family_id": sub["family_id"], "percentile": pct,
        })[is_focus].dropna(subset=["percentile"])
        out[key] = [
            {
                "soc_id": str(r.soc_id),
                "family_id": str(r.family_id) if pd.notna(r.family_id) else None,
                "percentile": float(r.percentile),
            }
            for r in rows.itertuples(index=False)
        ]
    return out


def _build_scatter(sub: pd.DataFrame, trait_col: str, value: str, cfg: Dict[str, object]) -> Dict[str, object]:
    """Raw (x, y) coordinates for the confirmatory scatter -- distinct from `scan()`'s standardized
    lens space, which isn't meant for direct plotting (z-scores, not the named physical units a
    reader expects on a labeled axis). Every backdrop row with both coordinates present is
    included (small dataset, ~1,133 rows -- no sampling needed); NaNs dropped, never imputed."""
    x_col, y_col = cfg["scatter_x"], cfg["scatter_y"]
    ok = sub.dropna(subset=[x_col, y_col])
    is_focus = ok[trait_col].notna() & (ok[trait_col] == value)

    def _points(df: pd.DataFrame, with_name: bool) -> list:
        cols = ["soc_id", x_col, y_col] + (["name"] if with_name and "name" in df.columns else [])
        out = []
        for row in df[cols].itertuples(index=False):
            d = {"soc_id": str(row[0]), "x": float(row[1]), "y": float(row[2])}
            if with_name:
                d["name"] = str(row[3]) if len(row) > 3 else None
            out.append(d)
        return out

    return {
        "x_var": x_col, "x_label": cfg["scatter_x_label"],
        "y_var": y_col, "y_label": cfg["scatter_y_label"],
        "backdrop": _points(ok[~is_focus], with_name=False),
        "focus": _points(ok[is_focus], with_name=True),
    }
