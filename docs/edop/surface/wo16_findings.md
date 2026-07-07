# WO16 findings — HYDE land-use raster overlay

**Date:** 2026-07-06
**Branch:** `surf_wo16a` → merge to `surface` when UI verification complete

---

## Status

WO16 split into two sub-steps after a design review:

- **WO16 (initial)** — implemented the pre-baked raster tile approach inherited from the
  Explorer (`applyHydeRaster`, `HYDE_EPOCHS`, `yearToHydeEpoch`). Proved functionally
  correct but architecturally wrong for EDOPS (see F16.1).
- **WO16a** — establishes the correct architecture (values-API + feature-state) via
  notebook feasibility study. UI implementation pending; will merge to `surface` when
  verified in browser.

---

## F16.1 — Architecture: values-API over pre-baked raster tiles

The Explorer's HYDE choropleth uses pre-baked PNG raster tiles (`epoch_N/{z}/{x}/{y}.png`)
averaging multiple DB time steps into 7 coarse bins. This is wrong for EDOPS because:

1. Epoch 4 (100–1000 CE) averages 10 DB steps (every 100 years) — the mean of 100–1000 CE
   is not a valid characterisation of any specific historical query window.
2. The 7 bins are a storage decision, not a historical one; they have no interpretive standing.

The correct architecture — confirmed in prior Explorer work and re-established here — is:
- Geometry: existing `basin06.pmtiles` (already loaded, 18.2 MB, never changes)
- Values: `/api/hyde/values?var=cropland&year=N` route returning `{hybas_id: fraction}` dict
- Paint: `setFeatureState` on `basin06` source — same path as the BasinATLAS choropleth

This gives full temporal precision: any of 118 CE-era steps (plus 10 BCE steps) on demand.

## F16.2 — HYDE temporal structure

`temporal.hyde_times` has 128 steps total:

- Steps 0–10: 10,000 BCE – 0 CE (1,000-year intervals)
- Steps 11–20: 100–1,000 CE (100-year intervals)
- Steps 21–112: 1,100–2,010 CE (100-year intervals, coarsening post-1700 TBD)
- Steps 113–127: 2,011–2,025 CE (annual)

118 CE-era steps (0–2025 CE). Year → step_idx: floor-snap via
`WHERE year_ce <= target ORDER BY year_ce DESC LIMIT 1`.

The 7-epoch Explorer tile bins each average 10–30 of these actual steps. The notebook
(Cell 2) confirms what the precompute script obscured: the underlying data has full
100-year resolution through the CE era.

## F16.3 — HYDE storage units: km² per cell, not fraction

`temporal.hyde_cells.cropland[step_idx+1]` returns **km² of cropland within the cell**,
not a fraction. To obtain cropland fraction: `cropland[step] / area_km2`. This was
discovered in Cell 4/11 when validation produced values >100%.

The `area_km2` column is available on every row. All value route queries must apply
this division.

## F16.4 — Centroid lookup: 0.31s for 16,040 basins

Three approaches were tested in `notebooks/edop/surface/wo16a_hyde_basin_values.ipynb`:

| Approach | Time | Coverage | Verdict |
|---|---|---|---|
| A — PostGIS spatial join | ~140s (extrapolated) | ~100% | Too slow |
| B — Centroid lookup | 0.31s | 16,040 / 16,397 | Viable |
| C — Pre-computed crosswalk | not built | ~100% | Future improvement |

Centroid lookup: for each L6 basin, `ST_Contains(hyde_cell.geom, ST_Centroid(basin.geom))`.
Exploits PostGIS spatial index; returns all 16,040 reachable basins in 0.31s.

357 basins have no containing HYDE cell (small island and coastal basins whose centroid
falls outside land coverage). The route returns null for these; the frontend treats null
as no-paint (transparent).

## F16.5 — Validation: r=0.689 vs BasinATLAS crp_pc_sse

HYDE 2000 CE cropland fraction (centroid lookup) vs BasinATLAS `crp_pc_sse` on a
500-basin sample: Pearson r=0.689. HYDE reads ~40% higher on average (different source
datasets; centroid picks a single cell rather than a weighted-area mean). The correlation
is directionally correct and the scale is sensible (0–99% range). Fit for choropleth
purposes: the paint shows spatial pattern and temporal change, not precise attribution.

Scatter plot saved: `output/edop/surface/wo16a_cropland_validation.png`.

## F16.6 — Output format: 354 KB, matches /api/explorer/values

Sample output dict (1000 CE, cropland): 16,040 entries, 354 KB JSON.
The `/api/explorer/values` route returns ~0.3 MB — identical shape and size.
The frontend can use exactly the same feature-state paint loop.

Saved: `output/edop/surface/wo16a_hyde_sample_1000ce.json`.

## F16.7 — Raster implementation in sandbox_v2 is superseded

The WO16 raster block (`HYDE_EPOCHS`, `HYDE_VAR_PATHS`, `HYDE_RAMPS`, `yearToHydeEpoch`,
`applyHydeRaster`, `renderHydeLegend`, `clearHydePaint`) added to `sandbox_v2.html`
during the initial WO16 pass is the wrong architecture and will be replaced. It remains
in the file on `surf_wo16a` but is not the implementation path forward.

## F16.8 — Deferred: pre-computed crosswalk

A materialized `temporal.hyde_basin06_weights(hybas_id, cell_id, area_frac)` table
(build script in Cell 9 of the notebook) would replace the centroid lookup with a
proper area-weighted aggregation and cover all 16,397 basins. Build time ~30–90 min.
Not required for the Braga milestone; recorded as a future accuracy improvement.

## F16.9 — Next step: UI implementation

WO16a has established feasibility. The implementation path:

1. Add `/api/hyde/values` route to `app/api/routes.py` (centroid lookup, var + year params)
2. Remove raster block from `sandbox_v2.html`; wire HYDE variables through `applyBasinVar`
   (or thin wrapper) with year parameter from Band T span
3. Verify in browser; update tests
4. Merge `surf_wo16a` → `surface`

## F16.10 — Test count

Structural tests: 83 pass (unchanged from WO15 — no new structural coverage added this
sub-step; HYDE Playwright tests remain skipped per F15.10 trigger).
Engine + app suite: 395 pass. Zero FAILs, zero unexplained warnings.
