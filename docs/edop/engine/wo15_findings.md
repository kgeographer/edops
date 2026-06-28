# WO15 — Area-weighted grid-cell intersection: findings

**Fixture:** 16.8167, −2.9833 (Timbuktu), L06, 1100–1200 CE
**Notebook:** `notebooks/edop/areas/single_basin_comparison.ipynb` (cell 12, WO15 section)
**Branch:** engine_v0.4b
**Date:** 2026-06-27

---

## What was changed

`_agg_hyde_b7` and the LMR aggregation path in `aggregate_band_t` previously weighted
cells by `overlap_m2 / sum(overlap_m2)` — each cell's share of the total intersection
area. This over-weights large cells when cells have unequal sizes: two cells both 10%
inside the query area receive equal fractional coverage but unequal weight if one is
larger in absolute area.

**Fix:** weight by `overlap_m2 / cell_area_m2` (fractional coverage of each cell's own
area), normalized across the cell set. A cell 10% inside contributes weight 0.1
regardless of absolute size. Applied to HYDE and LMR paths for consistency.

- **HYDE**: `area_km2` was already present in the SQL SELECT; no SQL change required.
  Weight computed as `frac = overlap_m2 / (area_km2 * 1e6)`. Detail block gains
  `w_eff` (sum of fractional coverages — honest effective cell count, distinct from the
  raw `n_units` count which still reflects how many cells contributed).
- **LMR**: `ST_Area(f.fp::geography) AS cell_area_m2` added to footprints SELECT.
  Weight computed as `frac_l = ov / ca; w_lmr = frac_l / frac_l.sum()`. For cells at
  the same latitude (equal area) this is numerically identical to the prior
  normalization.

Engine test suite: all 58 engine tests pass post-fix (including the 7 DB-fixture tests
that had been failing due to missing `scripts/edop/areas/conftest.py` — added as part
of this work order; those failures were pre-existing, not introduced by WO15).

---

## Correction to WO14 framing

WO14's deferred register entry described the current engine as doing "boolean inclusion
at weight 1.0" for HYDE boundary cells. This was wrong. The engine already computed
`ST_Area(ST_Intersection(...))` and used it as the weight — the 80-vs-45 cell count
divergence from v0.3 was the correct result of including boundary cells at their true
fractional overlap weight, not a weighting defect. The 7–8% grazing mean divergence
from v0.3 was caused by the extra 35 boundary cells carrying higher grazing values than
the interior — a legitimate signal, not a bias artifact.

WO15 is a principled normalization refinement (removes size-bias across unequal cells),
not a fix for the problem WO14 actually identified. The deferred register entry was
updated to reflect this.

---

## Validation result

**WO15 PASS.** Automated check in cell 12 (WO15 section):

- **LMR**: shift from WO14 baseline ≈ 0 across all three variables (pdsi, air, prate).
  3 cells at same latitude → equal areas → frac-normalized weights equal old weights.
  All Δ < 0.001.
- **HYDE**: `w_eff` present in detail block on all 8 HYDE rows (4 vars × 2 epochs),
  confirming the fix ran. All stat shifts (mean, p10, p90, sd) < 5% relative vs WO14
  baseline — as expected at 16°N where 5 arc-min cells are nearly equal in area. The
  wo11b Band T regression test (float_tol=0.01 vs `step3b_block7_primary.tsv`) also
  passes; no re-freeze of reference TSVs required.
- **Volcanic**: unchanged (eVolv2k path untouched).

The fix matters most at high latitudes or queries spanning large latitude ranges, where
cell area varies significantly with cos(latitude). Its impact at this equatorial fixture
is correctly minimal.

---

## Deferred register update

The entry "HYDE cell-selection: ST_Intersects vs area-weighted intersection" was updated
to accurately describe the prior state (overlap-area normalization, not boolean weight-1)
and to frame the fix as fractional-coverage normalization that removes latitude-dependent
size bias.
