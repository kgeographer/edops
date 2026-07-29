"""CITYKIN terrain lens — query-relative tolerance core (WO1a).

Factored separately from any presentation head (WO1a Part B proviso), same "factor the distance from
the head" discipline as WO8d's `distance_core.py`. This WO wires it to a ranked-retrieval head
(`docs/cdop/citykin/wo1a_terrain-lens.md` Part C); a later WO wires the same core to a paint-a-set head
on the sandbox Similarity tab (Forward).

Supersedes WO1's `ELEV_HIGH_THRESHOLD >= 400m` global eligibility gate (`wo1_findings.md`), which
passed the Tbilisi fixture but was a Tbilisi-specific artifact: it hard-coded "high" as a global
constant, so a flat query city would be excluded by its own gate. Fix: elevation, relief, and landform
position are each a query-relative tolerance band, anchored to the *selected* city's own facet values
-- the same pattern already validated for the sandbox's climate-regime lenses (query-relative bands
with user knobs, e.g. temp level +-3C, temp range +-4C).

Ranking distance within the tolerance band normalizes each facet's deviation by its OWN tolerance
(not a corpus-wide z-score, which was WO1's original failure mode -- see `wo1_findings.md`), so widening
or tightening a knob rescales that facet's contribution to the ranking automatically, no separate
weight to keep in sync. Elevation's contribution is scaled by `elev_weight` (an internal parameter,
not a user knob -- WO1a Part B: "elevation's weight ... is an internal parameter set once against the
fixtures, not a raw z-score and not a user knob"), set empirically against both Part D fixtures
(Tbilisi + a flat city), not assumed.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

import numpy as np
import pandas as pd

FACETS = ["grid_elev_mean", "relief_range_m", "landform_position"]

# Starting defaults -- informed by the corpus's own spread (post negative-elevation-filter fix,
# wo1_findings.md follow-up), NOT asserted: elev std ~698m, relief std ~404m, position std ~0.115.
# Set once against both Part D fixtures jointly (WO1a validation order step 2), not fit to either alone.
DEFAULT_TOLERANCES: Dict[str, float] = {
    "grid_elev_mean": 300.0,      # +-300m
    "relief_range_m": 200.0,      # +-200m
    "landform_position": 0.10,    # +-0.10 (0-1 scale)
}
DEFAULT_ELEV_WEIGHT = 1.0   # internal parameter -- see module docstring; tuned against the fixtures


def in_tolerance(query: Dict[str, float], corpus: pd.DataFrame,
                  tolerances: Optional[Dict[str, float]] = None) -> pd.Series:
    """Boolean mask: which corpus rows fall within `tolerances` of `query` on every facet."""
    tol = tolerances or DEFAULT_TOLERANCES
    mask = pd.Series(True, index=corpus.index)
    for f in FACETS:
        mask &= (corpus[f] - query[f]).abs() <= tol[f]
    return mask & corpus[FACETS].notna().all(axis=1)


def rank_by_terrain(query: Dict[str, float], corpus: pd.DataFrame,
                     tolerances: Optional[Dict[str, float]] = None,
                     elev_weight: float = DEFAULT_ELEV_WEIGHT,
                     exclude_index: Optional[Any] = None) -> pd.DataFrame:
    """Cities within `tolerances` of `query`, ranked by a tolerance-normalized distance.

    Distance = sqrt(elev_weight*(d_elev/tol_elev)^2 + (d_relief/tol_relief)^2 + (d_pos/tol_pos)^2) --
    each facet's deviation is normalized by ITS OWN tolerance (not a corpus-wide z-score), so the
    distance is always in units of "how much of the allowed band was used," comparable across facets
    with very different physical units and comparable across different knob settings.

    Returns a copy of the in-tolerance rows of `corpus`, with a `terrain_dist` column, sorted
    ascending, self excluded if `exclude_index` names a row to drop (e.g. the query's own corpus row).
    """
    tol = tolerances or DEFAULT_TOLERANCES
    mask = in_tolerance(query, corpus, tol)
    eligible = corpus[mask].copy()
    if exclude_index is not None and exclude_index in eligible.index:
        eligible = eligible.drop(index=exclude_index)

    d_elev = (eligible["grid_elev_mean"] - query["grid_elev_mean"]) / tol["grid_elev_mean"]
    d_relief = (eligible["relief_range_m"] - query["relief_range_m"]) / tol["relief_range_m"]
    d_pos = (eligible["landform_position"] - query["landform_position"]) / tol["landform_position"]
    eligible["terrain_dist"] = np.sqrt(elev_weight * d_elev**2 + d_relief**2 + d_pos**2)

    return eligible.sort_values("terrain_dist").reset_index(drop=True)
