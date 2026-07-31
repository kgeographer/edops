"""Factored distance core for WO8d (environment-culture correspondence, exploratory look).

Not declared a shared "core" for the near-future CITYKIN/TRACE phases -- that would be
speculative infrastructure built toward imagined consumers. WO8d's exploratory look is this
module's first real consumer; if a second consumer later validates the shape, extraction to a
named shared module is a lift-and-name, not a rewrite.

**CITYKIN WO4 (2026-07-30) is the second consumer** -- generalizes WO8d's hardcoded EA034 group
into a `(trait_col, value)`-parameterized scan, reused for the Societies-tab PCA-cluster
replacement. Two additions over the WO8d-only functions above:

    displacement(Xz_subset)     -- distance from the subset's own centroid to the backdrop
                                    centroid (= the origin, since Xz is backdrop-standardized).
                                    Cohesion alone is blind to *where* a group sits, only how
                                    tightly it holds together there -- a group uniformly
                                    displaced toward one climate extreme, but with ordinary
                                    internal spread, reads as an unremarkable cohesion number.
    top_families(family_ids)    -- descriptive composition note (top-3 language families by
                                    count/share in the filtered group), NOT a family-restricted
                                    percentile. Karl's correction (2026-07-30, settled with
                                    Opus): "environmental similarity net family" is an
                                    analytical move that belongs to TRACE, not to this
                                    descriptive screen -- a plain composition fact ("14 of 40
                                    are Bantu") is better description than an inferential
                                    statistic most readers can't interpret unaided, same
                                    direction as the project's own 0.70-redundancy-bar critique
                                    (an inferential guard misapplied to a description job
                                    displaces the thing the surface exists to show).
                                    `family_restricted_draw_cohesions` above is UNCHANGED and
                                    UNUSED by WO4's scan -- it stays here for TRACE, which will
                                    need it properly.

WO8d's original functions (`cohesion`, `random_draw_cohesions`, `family_restricted_draw_cohesions`)
are left byte-for-byte unchanged so WO8d's own notebook numbers keep reproducing exactly; WO4's
`random_draw_stats` below duplicates `random_draw_cohesions`'s RNG draw sequence rather than
refactoring it, specifically so its cohesion column is provably identical to the original
function's output at the same seed (see `notebooks/cdop/citykin/wo4_whc_grouping.ipynb` Cell for
the reproduction check).

Three lenses, one whole-signature metric (drop-to-representative, carried from WO8b/8c):

    water    = ['ari_log']
    thermal  = ['temperature_annual', 'tmp_seas_amp']
    overall  = water + thermal (the drop-to-representative Climate-envelope metric)
    terrain  = ['relief_range_m', 'landform_position']   -- a separate physical question,
               never folded into `overall` (WO8c Part D precedent). Both facets are point-window
               (`dplace.society_terrain`, `persist_dplace_terrain.py`: a +-2km/1km grid sample
               around each society's own coordinate, relief = grid max-min, landform = (mean-
               min)/relief) -- NOT the basin-aggregate `ele_mt_smx - ele_mt_smn` WO2a found an
               area confound in. The substrate carries both under different names
               (`relief_range_m` here vs. `basin_relief_range_m`), confirming this lens reads the
               point-window column, not the confounded one (WO4 Step 1 provenance check).
               Caveat, not a defect: this grid is WO8c's original +-2km/1km box, never updated to
               CITYKIN WO1a's later-corrected +-10km/5km box for the WH Cities corpus -- the two
               corpora's terrain facets are not on the same sampling window. Immaterial here (the
               scan never compares a society to a WH City directly), but do not assume the two
               `terrain` lenses are interchangeable if a future WO ever wants to.

Standardization is fit ONCE on the whole-sample backdrop (not refit per subgroup) so that
cohesion numbers for the focus group, for random draws, and for any other subset are all on
the same z-scored footing and genuinely comparable to each other.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple

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


# ---------------------------------------------------------------------------
# WO4 additions (2026-07-30): displacement, composition note, and the
# (trait_col, value) -> per-lens scan that generalizes WO8d's hardcoded EA034
# analysis. See module docstring for why these are new functions rather than
# edits to the WO8d functions above.
# ---------------------------------------------------------------------------

def displacement(Xz_subset: np.ndarray) -> float:
    """Distance from the subset's centroid to the backdrop centroid, in the same standardized
    space `cohesion` uses. `Xz_subset` must be a row-subset of a `backdrop_z` output (same
    precondition as `cohesion`) -- the backdrop's own centroid is then exactly the origin by
    construction (z-scoring subtracts the backdrop mean), so displacement reduces to the norm of
    the subset's own centroid. Where the group sits, as against `cohesion`'s how tightly it holds
    together there."""
    c = Xz_subset.mean(axis=0)
    return float(np.sqrt((c ** 2).sum()))


def random_draw_stats(Xz_backdrop: np.ndarray, k: int, n_draws: int = 2000,
                       seed: int = 0) -> Tuple[np.ndarray, np.ndarray]:
    """Cohesion AND displacement distributions for `n_draws` fully-random size-k draws, computed
    in one resampling loop (the expensive part -- generating the draws -- already has to happen
    for cohesion; this adds one more quantity per iteration, not a second pass).

    Reproducibility note: this function's `idx` draw sequence (`rng.choice(n, size=k,
    replace=False)`, once per iteration, nothing else consuming the RNG stream first) is
    identical to `random_draw_cohesions`'s at the same `seed`/`k`/`n_draws` -- so `coh` here is
    provably the same array `random_draw_cohesions` would return. That equivalence is asserted in
    the WO4 notebook's reproduction check rather than assumed.
    """
    rng = np.random.default_rng(seed)
    n = Xz_backdrop.shape[0]
    coh = np.empty(n_draws)
    disp = np.empty(n_draws)
    for i in range(n_draws):
        idx = rng.choice(n, size=k, replace=False)
        sub = Xz_backdrop[idx]
        coh[i] = cohesion(sub)
        disp[i] = displacement(sub)
    return coh, disp


def displacement_percentile_rank(value: float, distribution: np.ndarray) -> float:
    """Mirrors `percentile_rank`'s convention (high = unusual) for displacement, where the
    direction is reversed from cohesion: a LARGE displacement is the unusual/interesting case
    (the group sits far from the backdrop center), so this returns the fraction of `distribution`
    AT OR BELOW `value` -- 'the real group is more displaced than this fraction of random draws.'
    """
    return float((distribution <= value).mean())


def top_families(family_ids: pd.Series, top_n: int = 3) -> Dict[str, object]:
    """Descriptive composition note: the top `top_n` language families in a filtered group by
    raw count, with each one's share of the group. Always returns up to `top_n` entries -- no
    dominance threshold, because a threshold ("how big a share counts as dominant?") is exactly
    the kind of provisional, set-by-eye cutoff this project keeps having to revisit. A fixed
    top-N-by-count rule reads correctly whichever shape the group takes: one dominant family
    (WO8d's Atlantic-Congo, 15/40) or several small ones with none dominant (WO8d's Siberian
    trio -- three unrelated families, no single one nameable as "the" family, and the single
    tightest sub-group in the whole set: exactly the pattern a single-dominant-family note would
    have missed). NaN/unresolved `family_id` is excluded from the ranking; its count is reported
    separately, never silently folded into a "family."
    """
    n_total = int(len(family_ids))
    resolved = family_ids.dropna()
    counts = resolved.value_counts().head(top_n)
    return {
        "n_total": n_total,
        "n_unresolved": int(n_total - len(resolved)),
        "top_families": [
            {"family_id": str(fam), "n": int(n), "share": float(n) / n_total if n_total else 0.0}
            for fam, n in counts.items()
        ],
    }


def scan(sub: pd.DataFrame, trait_col: str, value: str, family_col: str = "family_id",
         top_n_families: int = 3, n_draws: int = 2000, seed: int = 0) -> Dict[str, object]:
    """The WO4 engine entry point: `(trait_col, value)` -> per-lens cohesion + displacement
    against a random-draw baseline, a composition note, and per-society lens distances (for the
    map). No family-restricted resampling -- that stays a TRACE question (module docstring).

    `sub` is the shared society-basin-signature substrate (`output/cdop/wo8c_substrate.parquet`
    or equivalent), expected to carry every `LENSES` column plus `ari_ix_sav` (from which
    `ari_log` is derived here if not already present, matching WO8d Cell 3) and `family_col`.
    Rows where `trait_col` is null are excluded from the filtered set, never imputed (standing
    rule).
    """
    sub = sub.copy()
    if "ari_log" not in sub.columns and "ari_ix_sav" in sub.columns:
        sub["ari_log"] = np.log1p(sub["ari_ix_sav"])

    is_focus_input = sub[trait_col].notna() & (sub[trait_col] == value)
    n_focus_input = int(is_focus_input.sum())

    lens_results: Dict[str, Dict[str, object]] = {}
    for lens in LENSES:
        ok, Xz = backdrop_z(sub, lens)
        # NB: recompute the focus condition directly against `ok`, never against a mask built on
        # `sub`'s original index and reindexed onto `ok.index`. `backdrop_z` resets `ok`'s index to
        # a fresh 0..N-1 RangeIndex after dropping incomplete rows for THIS lens -- for a lens that
        # drops zero rows that reindex happens to line up by coincidence (nothing shifted), but for
        # any lens that drops rows (e.g. `terrain`, on `landform_position` NaNs) it silently
        # selects the wrong rows once the misalignment starts. Caught in Step 1 validation
        # (wo4_whc_grouping.ipynb Cell 3): terrain's obs_cohesion came out wrong (1.233 vs WO8d's
        # 1.207) while water/thermal/overall -- which drop nothing -- matched exactly.
        fmask = (ok[trait_col].notna() & (ok[trait_col] == value)).to_numpy()
        k = int(fmask.sum())
        if k == 0:
            lens_results[lens] = {"n_backdrop": len(ok), "n_focus": 0, "note": "no complete-case rows"}
            continue

        Xz_focus = Xz[fmask]
        obs_coh = cohesion(Xz_focus)
        obs_disp = displacement(Xz_focus)
        null_coh, null_disp = random_draw_stats(Xz, k=k, n_draws=n_draws, seed=seed)

        lens_results[lens] = {
            "n_backdrop": len(ok),
            "n_focus": k,
            "obs_cohesion": obs_coh,
            "obs_displacement": obs_disp,
            "pct_tighter_than_random": 100 * percentile_rank(obs_coh, null_coh),
            "random_cohesion_mean": float(null_coh.mean()),
            "random_displacement_mean": float(null_disp.mean()),
            "displacement_pct_rank": 100 * displacement_percentile_rank(obs_disp, null_disp),
            "society_distances": {
                str(soc_id): float(d) for soc_id, d in zip(
                    ok.loc[fmask, "soc_id"], np.sqrt(((Xz_focus - Xz_focus.mean(axis=0)) ** 2).sum(axis=1))
                )
            } if "soc_id" in ok.columns else None,
        }

    composition = top_families(sub.loc[is_focus_input, family_col], top_n=top_n_families) \
        if family_col in sub.columns else None

    return {
        "trait_col": trait_col,
        "value": value,
        "n_focus_input": n_focus_input,
        "composition": composition,
        "lenses": lens_results,
    }
