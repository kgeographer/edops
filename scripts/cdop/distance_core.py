"""Factored distance core for WO8d (environment-culture correspondence, exploratory look).

Not declared a shared "core" for the near-future CITYKIN/TRACE phases -- that would be
speculative infrastructure built toward imagined consumers. WO8d's exploratory look is this
module's first real consumer; if a second consumer later validates the shape, extraction to a
named shared module is a lift-and-name, not a rewrite.

Three lenses, one whole-signature metric (drop-to-representative, carried from WO8b/8c):

    water    = ['ari_log']
    thermal  = ['temperature_annual', 'tmp_seas_amp']
    overall  = water + thermal (the drop-to-representative Climate-envelope metric)
    terrain  = ['relief_range_m', 'landform_position']   -- a separate physical question,
               never folded into `overall` (WO8c Part D precedent).

Standardization is fit ONCE on the whole-sample backdrop (not refit per subgroup) so that
cohesion numbers for the focus group, for random draws, and for any other subset are all on
the same z-scored footing and genuinely comparable to each other.
"""
from __future__ import annotations

from typing import Dict, Optional, Tuple

import numpy as np
import pandas as pd

LENSES: Dict[str, list] = {
    "water": ["ari_log"],
    "thermal": ["temperature_annual", "tmp_seas_amp"],
    "overall": ["ari_log", "temperature_annual", "tmp_seas_amp"],
    "terrain": ["relief_range_m", "landform_position"],
}


def backdrop_z(df: pd.DataFrame, lens: str) -> Tuple[pd.DataFrame, np.ndarray]:
    """Standardize `df` on lens `lens`, fit on this same (backdrop) population.

    Returns (backdrop_rows, Xz) where backdrop_rows is df restricted to complete cases for
    this lens (index reset) and Xz is the z-scored coordinate matrix, row-aligned to it.
    """
    cols = LENSES[lens]
    ok = df.dropna(subset=cols).reset_index(drop=True)
    X = ok[cols].to_numpy(float)
    mu, sd = X.mean(0), X.std(0)
    Xz = (X - mu) / sd
    return ok, Xz


def pairwise_distance(Xz: np.ndarray) -> np.ndarray:
    """Euclidean distance matrix from an already-standardized coordinate matrix."""
    G = Xz @ Xz.T
    d2 = np.diag(G)[:, None] + np.diag(G)[None, :] - 2 * G
    return np.sqrt(np.clip(d2, 0, None))


def cohesion(Xz_subset: np.ndarray) -> float:
    """Mean distance to centroid -- lower = tighter. Computed in the SAME standardized
    coordinate space as the backdrop (Xz_subset must be a row-subset of a `backdrop_z` output,
    never re-standardized on its own subset -- that would make cohesion numbers incomparable
    across different subsets)."""
    c = Xz_subset.mean(axis=0)
    d = np.sqrt(((Xz_subset - c) ** 2).sum(axis=1))
    return float(d.mean())


def random_draw_cohesions(Xz_backdrop: np.ndarray, k: int, n_draws: int = 2000,
                          seed: int = 0) -> np.ndarray:
    """Cohesion distribution for `n_draws` fully-random size-k draws from the backdrop
    (the WO's looser, primary baseline: 'tighter than any random k')."""
    rng = np.random.default_rng(seed)
    n = Xz_backdrop.shape[0]
    out = np.empty(n_draws)
    for i in range(n_draws):
        idx = rng.choice(n, size=k, replace=False)
        out[i] = cohesion(Xz_backdrop[idx])
    return out


def family_restricted_draw_cohesions(Xz_backdrop: np.ndarray, backdrop_family_id: np.ndarray,
                                     focus_family_id: np.ndarray, n_draws: int = 2000,
                                     seed: int = 0) -> np.ndarray:
    """Cohesion distribution for the WO's stricter baseline: 'tighter than random cousins'.

    Each draw keeps the REAL focus group's family composition fixed and swaps each member for
    a random OTHER backdrop society of the SAME family (a family-restricted permutation, same
    logic as dbperm.py's blocked shuffle). A focus member whose family is unresolved (NaN) or
    who has no other backdrop society sharing that family_id falls back to a fully-random
    backdrop draw for that slot (noted, not silently identical every time -- it's still redrawn
    per iteration from the full backdrop).
    """
    rng = np.random.default_rng(seed)
    n = Xz_backdrop.shape[0]
    by_family: Dict[object, np.ndarray] = {}
    for fam in pd.unique(backdrop_family_id):
        by_family[fam] = np.where(backdrop_family_id == fam)[0]

    k = len(focus_family_id)
    out = np.empty(n_draws)
    for i in range(n_draws):
        idx = np.empty(k, dtype=int)
        for j, fam in enumerate(focus_family_id):
            pool = by_family.get(fam) if pd.notna(fam) else None
            if pool is None or len(pool) == 0:
                idx[j] = rng.integers(0, n)          # unresolved/no-cousins fallback
            else:
                idx[j] = pool[rng.integers(0, len(pool))]
        out[i] = cohesion(Xz_backdrop[idx])
    return out


def percentile_rank(value: float, distribution: np.ndarray) -> float:
    """% of `distribution` at or above `value` -- for cohesion (lower=tighter), a LOW
    percentile-rank-of-value-among-distribution means the real group is tighter than most
    random draws. Returns the fraction of the random distribution >= value (i.e. 'tighter than
    this fraction of random draws')."""
    return float((distribution >= value).mean())
