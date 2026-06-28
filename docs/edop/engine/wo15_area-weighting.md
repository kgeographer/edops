# WO15 — Area-weighted grid-cell intersection (Band T)

**Phase:** Areas · **Sub-phase:** engine · **Date:** 2026-06-27
**Depends on:** WO14 (single-basin run; HYDE 80-vs-45 finding).
**Branch:** continue `engine_v0.4b`.

---

## Why

WO14 surfaced that the Band T grid path selects cells by **boolean `ST_Intersects`** — any cell touching the query polygon is included whole, at full weight. v0.3 used **centroid-in-polygon** (the source of its 45 vs v0.4's 80 cells at Timbuktu). Both are wrong in opposite directions: boolean inclusion over-counts (a cell 5% inside the basin contributes 100% of its value), centroid under-counts (a cell 45% inside contributes nothing). The basin path already weights partial units by area; the grid path should do the same.

At Timbuktu the 35 extra edge cells resemble the interior, so the bias is a ~7–8% wobble in grazing mean/sd and the distribution shape (p10/p90) survives. The bias is **fixture-dependent and worst exactly where HYDE is most interesting** — a basin straddling a sharp land-use front (the desert/sown margin), where edge cells differ sharply from interior. So this is a real bias on the headline path, quiet here, not deferrable for any HYDE-bearing areal result we'd put on a dashboard.

**The target is area-weighted overlap, not "match v0.3's 45."** v0.3's centroid rule was also wrong; reproducing it is not the goal. Frame and test the fix against fractional overlap, not against the v0.3 count.

---

## The fix

In the Band T grid aggregation, weight each grid cell by its **fractional area of overlap** with the query geometry, rather than including intersecting cells at weight 1.0.

- Compute per-cell weight `w_i = area(cell_i ∩ query_geom) / area(cell_i)` (PostGIS `ST_Intersection` → `ST_Area`, geography or an equal-area projection so the ratio is honest at 16°N).
- Apply `w_i` everywhere the grid path currently treats cells as unit-weight: the areal mean/total, and the cross-cell distribution stats (`p10`/`p90`/`std`) — these become **weighted** quantiles/moments. (Weighted p10/p90: the basin path's weighted-quantile helper should be reusable; confirm it is, rather than writing a second one.)
- `n_units` should keep reporting the count of contributing cells, but note that cells now contribute fractionally — a `w`-sum (effective cell count) in `&detail` would be more honest than the raw count. CC's call on whether to add it; flag if it's awkward.

This applies to **HYDE** (5 arc-min, many cells per basin — where it bites) and, for consistency, to the **LMR** collapse path (the 3-cell Timbuktu collapse is already area-weighted per WO14 — confirm the same helper is used, so there aren't two weighting implementations).

---

## Scope guards

- **Engine internals only.** No contract change: the payload shape, the `distribution` flag, the ECC collapse logic are untouched. This changes *how cells are weighted within* the grid path, not what the path emits.
- **Not a v0.3 reconciliation.** Do not tune toward 45 cells. The acceptance check is correctness of the weighting, not the count.
- **No threshold.** Don't add a minimum-overlap cutoff to "clean up" tiny-overlap cells — area-weighting already handles them (a 1%-overlap cell contributes 1%). A cutoff would reintroduce the centroid-style discontinuity.

---

## Validation

1. **Regression:** the 51 prior Band T tests still pass. The buffer fixture's Band T values *will* shift slightly (buffer edges now weight partial cells) — re-freeze with sign-off if so, as a blessed correction (same pattern as the WO4/5/7 blessed deviations), noting it's the area-weighting fix.
2. **Single-basin re-run:** re-run WO14's HYDE check. Expect the grazing mean/sd divergence from the v0.3 reference to *change* — not necessarily shrink to zero (v0.3's centroid rule was also wrong), but the v0.4 values should now be defensible as fractional-overlap-correct. Report the new per-epoch numbers and the new effective cell weight-sum.
3. **Sanity:** a cell fully inside → w=1; a cell fully outside → excluded (w=0, never selected); a half-overlapping cell → w≈0.5. Assert on a couple of known edge cells.

---

## Deliverables

- Engine edit (the weighting change), with the reused weighted-quantile helper identified.
- Regression result (51 tests; any re-frozen Band T values flagged).
- Single-basin HYDE re-check: new per-epoch mean/sd, new effective weight-sum, vs the WO14 numbers.
- One-line findings note: boolean→area-weighted, the bias it removes, why it matters at land-use boundaries.

---

## Acceptance

- Per-cell area weights computed and applied to HYDE mean/total and the weighted distribution stats.
- Single weighting/quantile implementation shared with the basin and LMR paths (no second copy).
- 51 Band T tests pass; any shifted buffer values re-frozen with sign-off.
- Edge-cell sanity assertions pass.
- No contract/payload-shape change.
- 