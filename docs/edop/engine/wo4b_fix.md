# CC work order — Engine assembly WO4b: HYDE grid-cell overlap determinism

**Date:** 2026-06-23
**Branch:** off the WO4 result (`engine04b` or your naming)
**Pace:** diagnose, then fix per the finding, then re-freeze. Stop for review.
**Scope:** Band T grid path only. The basin path is untouched.

---

## Why

WO4 surfaced that a HYDE cell on the geometric edge of the 100 km buffer flickers in and out (`n_units` 426 vs 425) depending on floating-point rounding in `ST_Intersection`/`ST_Area`, and the WO4 HYDE regression had to be loosened (±1 on `n_units`, 15% on the mean) to pass. That loosened tolerance is a temporary patch; this WO resolves the cause so the Band T path can regress strict.

**But the report contains a contradiction that must be resolved before any fix is chosen.** CC reports the edge cell's overlap is "at or near zero," *and* that its in/out status shifts the weighted mean ~11%. Those can't both be true if HYDE cells are weighted by clipped overlap area: a near-zero-overlap cell contributes near-zero to an overlap-weighted mean **regardless of its values**, so it cannot move the mean 11%. So one of two things is true, and which one decides the fix:

- the overlap isn't actually near-zero (it's a real partial overlap), or
- the HYDE mean isn't weighting by clipped overlap (it's using full cell area, or equal weight once a cell passes a presence test) — which would be a correctness bug against the locked area-weighted model.

## Principle (do not violate)

A cell contributes **by its fraction of overlap with the buffer**, weighted — the same model as the buffer resolver's `weight = fraction of buffer covered`. The fix must keep the edge cell and weight it by its true overlap fraction. **Do not add an epsilon that eliminates the cell** — that would cause the error it's meant to prevent. And the edge-leverage effect (at a buffer's edge, area is large but cell count is low, so one high-value cell has outsized influence) is a **real property of small-n areal queries**, surfaced by `n_units`/`coverage`, not something to suppress.

## Step 1 — Diagnose (confirmatory, no fix yet)

Establish, for the Timbuktu 100 km buffer:

1. Exactly how `_agg_hyde` weights cells in the mean — is the weight the **clipped overlap area** (cell ∩ buffer), the full cell `area_km2`, or presence-based once a cell intersects?
2. For the flickering edge cell specifically: its full area, its clipped overlap area, its overlap **fraction**, the weight it actually receives in the mean, and its grazing/rangeland values.
3. Reconcile the contradiction: with those numbers, how does this cell move the mean 11%? State which of the two causes above is real.

Report this before touching any aggregation code.

## Step 2 — Fix per the finding

- **Always:** pin the geometry computation so the same query yields the same overlap every run — consistent projection, precision, and any snapping in the PostGIS intersection — so the cell **set** (`n_units`) is reproducible run to run. The edge cell stays in, carrying its true fractional weight; nothing is dropped.
- **If Step 1 shows the HYDE mean is not weighting by clipped overlap:** correct `_agg_hyde` to weight by clipped overlap area, consistent with the locked area-weighted model. After this, the edge cell contributes in proportion to its real (small) overlap, and the 11% sensitivity collapses to the negligible contribution a near-zero-overlap cell should have.

## Step 3 — Re-freeze the Band T TSVs (scope set by Step 1)

The current Band T TSVs were written with the flicker baked in, and the wide TSV's `lmr_caveat` column is all-NaN (the notebook omission WO4 already corrected in the engine). So the frozen target is wrong in known ways and must be regenerated from the corrected, deterministic engine.

**Guard the regression integrity:** before the regenerated TSVs become the new ground truth, diff them against the old ones and **prove the deltas are confined to the intended corrections** — the edge-cell `n_units`, the HYDE means affected by it (and by any weighting fix), and the `lmr_caveat` column. Every LMR and eVolv2k row must be **unchanged** (strict). Document exactly what changed and why. This is a deliberate shift of the Band T regression target from notebook output to corrected-engine output, justified only by the two known notebook defects — **flag it for Karl's explicit sign-off** before committing the new TSVs.

Re-freeze the Band T outputs: `step3b_block7_primary.tsv`, `step3b_block7_wide.tsv`, and any Band T companion tables.

## Acceptance

- **Determinism:** the same query, run repeatedly, returns identical `n_units` and identical HYDE means (strict, not tolerance).
- **Strict regression:** with the re-frozen TSVs as target, the WO4 Band T regression passes at **strict** tolerance — the loosened HYDE ±1/15% tolerance is retired.
- **No collateral change:** LMR and eVolv2k rows identical to the prior TSVs.

## Out of scope

- the basin path (WO5+); notebooks (frozen — the fix lives in `engine.py`, TSVs regenerated from the engine, not the notebook).

## On completion

Report the Step 1 diagnosis (which cause was real), the fix made, and the Step 3 delta proof (what changed in the re-frozen TSVs and confirmation that LMR/eVolv2k are untouched). Update the tracker (WO4b done; Band T path deterministic; regression strict). Stop for Karl's sign-off on the re-freeze before WO5.
