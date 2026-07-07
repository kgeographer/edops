# WO17 Findings — Area-weighted HYDE-to-basin aggregation

**Branch:** `surf_wo17`
**Date:** 2026-07-07
**Notebook:** `notebooks/edop/surface/wo17_hyde_area_weighted.ipynb`

---

## Accept gate verdict

**Crosswalk proven correct. Route swap (WO18) blocked by per-request query time.**

| Item | Result |
|---|---|
| Build time (one-off) | 74s (1.2 min) |
| Per-request query time | **2.67s — NO-GO** (centroid baseline: 0.31s) |
| Crosswalk rows | 2,817,246 |
| Mean cells/basin | 173 |
| Basins covered (area-weighted) | 16,281 / 16,397 |
| Basins recovered from centroid-nulls | 241 of 357 |
| Still null (no land overlap) | 116 — paint transparent, never zero |
| r vs BasinATLAS crp_pc_sse (frac_covered) | **0.902** (centroid baseline: 0.689) |
| r vs BasinATLAS crp_pc_sse (frac_full) | **0.901** |
| Denominator decision | `frac_full` (÷ sub_area) |
| Unit guard (no frac > 1.0) | Passed |

---

## F17.1 — Crosswalk build time well within acceptable range

Estimated from Cell 3 sample: 2.7 min. Actual: 74s (1.2 min). GIST index on `temporal.hyde_cells.geom` was confirmed present (Cell 2); this drove the fast `ST_Intersects` candidate lookup. Build time is a one-time cost — acceptable.

Crosswalk schema: `(hybas_id bigint, cell_id integer, overlap_frac real)`.  
`overlap_frac = ST_Area(ST_Intersection(basin.geom, cell.geom)) / ST_Area(cell.geom)` — planar ratio; projection distortion cancels. Denominator choice (full basin vs. covered area) is deferred to query time, not baked into the crosswalk. Two B-tree indexes built: on `hybas_id` and `cell_id`.

## F17.2 — Per-request query time: NO-GO (2.67s vs 0.31s centroid)

The per-request join (Cell 6) touches 2.82M crosswalk rows × 2.21M distinct `hyde_cells` rows for the `cropland[step_idx+1]` array access — essentially the entire `hyde_cells` table on every call. The crosswalk eliminates the live `ST_Intersection` spatial join (which extrapolated to ~140s for Approach A in WO16a) but does not eliminate per-row data access. Per-step array subscript across 2.8M rows costs ~2.67s regardless of indexing.

The WO17 criterion was centroid-comparable (~0.3s). 2.67s fails. Route swap is blocked.

**Path forward (WO18):** Pre-aggregate the crosswalk across all 128 steps × 4 vars into `temporal.hyde_basin06_steps (hybas_id, step_idx, cropland_frac, grazing_frac, ...)`. This is a one-time computation (128 iterations of the 2.67s query = ~6 min). Per-request then becomes `SELECT hybas_id, cropland_frac FROM temporal.hyde_basin06_steps WHERE step_idx = $1` — an indexed point lookup, expected <100ms.

## F17.3 — Crosswalk coverage: 16,281 basins; 241 centroid-nulls recovered

Centroid (WO16a): 16,040 / 16,397 basins (357 null — centroid fell outside land coverage).  
Area-weighted crosswalk: 16,281 / 16,397 (116 null — genuine no-land-overlap basins).  
241 basins recovered: their centroid was in ocean but the basin boundary clips at least one land HYDE cell.  
116 remain null → paint transparent, never coerced to zero (zero is a value, not an absence marker).

## F17.4 — Denominator decision: frac_full (÷ sub_area)

Cell 7 showed that `covered_km2 ≈ sub_area` for the vast majority of basins (coverage ratio histogram peaked sharply at 1.0). Basins where they diverge (cover_ratio < 0.95) are a small coastal/island minority. The validation r values differ by only 0.001 (0.902 vs 0.901). The two denominators are empirically equivalent for a global choropleth.

Use `frac_full` (÷ sub_area) for consistency with how BasinATLAS computes `crp_pc_sse` — it also uses the full HydroSHEDS basin area as denominator.

## F17.5 — r improvement: 0.689 → 0.902 validates area-weighting

Validation at 2000 CE against BasinATLAS `crp_pc_sse` (Cell 10): r jumped from 0.689 (centroid) to 0.902 (area-weighted). BasinATLAS derives `crp_pc_sse` by the same area-weighted aggregation method we now use; recovering their spatial pattern confirms the crosswalk is doing genuine work. r does not approach 1.0 — expected, since HYDE 3.4 and the BasinATLAS cropland source are different datasets (HYDE runs ~40% higher, consistent with WO16a F16.5).

## F17.6 — Shift vs centroid: meaningful for a minority; near-zero for majority

Cell 9 histogram: the distribution of (area-weighted − centroid) is sharply peaked at zero for most basins — the centroid cell was representative. The tail extends ±0.10–0.15 in cropland fraction (10–15 percentage points), with a systematic positive skew: centroid tends to underestimate relative to area-weighted for high-agriculture basins. Mechanism: basin centroids disproportionately sit at low-elevation valley-floor positions, which in agricultural landscapes tend to have more cropland than the basin mean.

## F17.7 — Unit guard: no fraction exceeds 1.0

Cell 11: `frac_covered > 1.0`: 0 basins. `frac_full > 1.0`: 0 basins. The F16.3 unit handling (cropland stored as km²/cell; divide by area_km2 before weighting) carried correctly through the weighted sum.

## F17.8 — Methods note (settled)

HYDE 3.4 cropland values are aggregated to L6 HydroSHEDS basins via `temporal.hyde_basin06_weights`. For each basin–cell pair with non-zero planar intersection area, the crosswalk stores `overlap_frac = area(cellᵢ ∩ basinᵦ) / area(cellᵢ)` (planar ratio; distortion cancels). Basin aggregate: `(Σ cropland_km²ᵢ × overlap_fracᵢ) / sub_area`. Within-cell distribution assumed uniform — the finest structure HYDE 3.4 asserts. Within-basin heterogeneity is not represented; the choropleth shows a basin-level summary, the same epistemic object every other EDOPS band delivers.

---

## Next step

**WO18** — Pre-aggregate crosswalk across all steps × vars → `temporal.hyde_basin06_steps`. Then swap `/api/hyde/values` to use it. Expected per-request time <100ms; build time ~6 min.
