# WO18 Findings — HYDE pre-aggregation + route swap

**Branch:** `surf_wo18`
**Date:** 2026-07-07
**Notebook:** `notebooks/edop/surface/wo18_hyde_preaggregate.ipynb`

---

## Accept gate verdict

**GO. Both gates passed.** Table built; per-request 0.033s (80× faster than WO17 baseline);
route swapped; 364/364 tests pass.

| Item | Result |
|---|---|
| Build time | 592s (9.9 min) — longer than ~6 min estimate; commit + index overhead accounted for |
| Total rows | 2,083,968 = 16,281 × 128 exactly |
| Per-request query time | **0.033s** (threshold: <200ms; WO17 baseline: 2.67s; speedup: 80×) |
| Value agreement with WO17 | max \|delta\| = 7.94e-08 (float32 noise floor) |
| Unit guard | See F18.4 |
| Tests | **364 passed, 14 skipped** (Playwright); 0 failures |

---

## F18.1 — Build time: 9.9 min

The 128-step insert loop took ~590s; indexes added ~2s. Longer than the ~6 min estimate
(128 × 2.67s = 342s) due to Python loop overhead, 16-step commit batching, and index build.
Acceptable — one-time cost.

Table schema:
```sql
temporal.hyde_basin06_steps (
    hybas_id       bigint   NOT NULL,
    step_idx       smallint NOT NULL,
    cropland_frac  real,
    grazing_frac   real,
    pasture_frac   real,
    rangeland_frac real
)
```
Fractions are `frac_full` (÷ `sub_area`) per WO17 denominator decision.
Indexes: `(step_idx)` for route queries; `(hybas_id, step_idx)` for future per-basin lookups.

## F18.2 — Null representation: 116 basins absent, not NULL

The 116 no-land basins (absent from `temporal.hyde_basin06_weights`) are simply not inserted
into the steps table — they produce no rows. The route query returns no row for these basins;
they are absent from the values dict; the frontend treats absence as null → transparent paint.
This is equivalent to the centroid route's behaviour for its 357 missing basins.

The notebook's expected null count (116 × 128 = 14,848) was wrong — the correct expectation
is 0 NULL rows and 116 absent basins.

## F18.3 — Per-request timing: 0.033s — GO

Three timed runs (warmed): 0.032s, 0.033s, 0.034s. Mean 0.033s.

The query is `SELECT hybas_id, cropland_frac FROM temporal.hyde_basin06_steps WHERE step_idx = N`
— an indexed scan returning 16,281 rows with no joins, no spatial operations, no array access.
80× faster than the WO17 crosswalk baseline (2.67s). Comfortably within the <200ms threshold
and comparable to the WO16a centroid baseline (0.31s); faster, in fact.

## F18.4 — Unit guard: one basin exceeds 1.0; clamped in route

Cell 7 found `grazing_frac` and `rangeland_frac` max = 1.0016 for `hybas_id 5060271430`.
Confirmed via SQL: only this one basin across all 128 steps; both vars equal at every step
(constant ratio). Cause: HydroSHEDS `sub_area` for this basin is 0.16% smaller than the
HYDE-cell covered area — two independently-sourced area measurements that don't agree exactly.
The basin is fully grazed/ranged, so any fraction-of-1 discrepancy maps directly to both vars.

**Fix:** `min(round(float(r[1]), 6), 1.0)` in the route dict comprehension. Table values are
unchanged (records the honest arithmetic); the physical constraint is enforced at the display
layer. One line added to `app/api/routes.py`.

## F18.5 — Value agreement: float32 noise floor

Cell 6 compared 500 basins at step_idx=20 (1000 CE) between the pre-aggregated table and the
WO17 on-the-fly crosswalk query. Max |delta| = 7.94e-08, mean = 1.54e-09. Both are within
float32 precision (~1.2e-7). The pre-aggregated values are numerically identical to the WO17
crosswalk.

## F18.6 — Route swap: transparent to frontend

`/api/hyde/values` response shape is unchanged: `{var, year, actual_year, values: {hybas_id: fraction}}`.
The `applyHydeChoropleth` function in `sandbox_v2.html` requires no change. Slice-reactive
repaint (added in WO16a) continues to work. Coverage improves from 16,040 (centroid) to 16,281
(area-weighted) — 241 additional basins now paint with values.

---

## Summary of HYDE choropleth arc (WO16a → WO17 → WO18)

| WO | What | Coverage | r vs BasinATLAS | Per-request |
|---|---|---|---|---|
| WO16a | Centroid lookup (shipped) | 16,040 / 16,397 | 0.689 | 0.31s |
| WO17 | Area-weighted crosswalk (proof) | 16,281 / 16,397 | 0.902 | 2.67s (NO-GO) |
| WO18 | Pre-aggregated steps table (live) | 16,281 / 16,397 | 0.902 | **0.033s (GO)** |
