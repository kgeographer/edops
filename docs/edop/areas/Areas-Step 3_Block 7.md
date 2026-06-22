# CC work order — Step 3 Block 7: Band T gridded areal path

**Date:** 2026-06-20
**Notebook:** new `notebooks/edop/areas/step3b_band_t.ipynb` (split from `step3_` for length)
**Branch:** `areas_step3`
**Pace:** sequenced for review at each step. Stop after each numbered step and report; do not run ahead. Steps 7.1–7.3 are exploratory/confirmatory — they establish ground truth and validate the routing premise, and commit to nothing. 7.4–7.6 build.

---

## Before you start

Read `AREAS_tracker.md`, `deferred_items_register.md`, and `CLAUDE.md` first; they are the source of truth on current state and locked decisions. Three existing pieces are reference implementations — reuse them, do not reinvent:

- `app/db/signature.py` — the point/basin Band T retrieval. It already pulls HYDE cells, indexes the `real[]` arrays by time, joins `hyde_times`, aggregates HYDE cells *within the containing basin* (returns mean plus per-cell sd / p10 / p90), and returns LMR and eVolv2k for a query span. Block 7 generalizes the HYDE cell aggregation from "cells in one basin" to "cells in the query polygon," and keeps the same temporal-retrieval and unit handling. Confirm units from this file rather than assuming — in particular whether LMR `air` carries a scale factor, and the array indexing convention for each source.
- `notebooks/edop/areas/step1_buffer_resolver.ipynb` — buffer construction (point + radius → polygon, using `geog` directly) and the figure styling. Rebuild the buffer with step1's exact construction so the geometry is identical, and match step1's figure look for the diagnostic figure in 7.2.
- The Explorer (`explorer.html` + `/api/explorer` routes) — already handles LMR as five periods and HYDE as epochs; reference for temporal handling.

---

## The settled design (so you have it without the design thread)

- **Pathway: cells → query polygon, direct.** No basins on this path. Clip grid cells straight to the buffer geometry. Block 7 is a parallel resolver branch that shares the query geometry with Blocks 1–6 but not the weighted-basin-set spine. Double aggregation (cells → basin → basin-set) is explicitly out — it would destroy the within-area distribution before the areal step ran.
- **Honesty diagnostic = clipped-cell-count, computed, dataset-blind.** Count the grid cells the polygon clips, weighted by overlap area; from that, an effective-cell-count (Herfindahl form, `1 / Σ wᵢ²` on overlap-area weights normalized to the covered area). Above a threshold, report the cross-cell distribution; at or below it, collapse to the area-weighted value. HYDE and LMR are *not* hardcoded — they land on opposite sides only because their cells differ by ~three orders of magnitude in area. Threshold is **provisional → multi-fixture calibration** (register).
- **Time: scoping in, scoring parked.** The areal product is a *time series of areal aggregates* — collapse space at each resolved time step, keep the time axis whole. Span width is the snapshot-vs-history selector; no mode flag, and **no within-span temporal collapse** (a temporal mean lies the way a spatial mean lies). Temporal *position scoring* (what reference window a value is scored against) stays deferred; so `representative_score` is **null** for every Band T variable and `representative_raw` carries the headline.
- **eVolv2k:** global forcing series, **no areal step** — return the in-range events exactly as the point signature does, regardless of geometry.
- **LMR caveat mandatory** on every LMR output row: values are anomalies against the 850–1850 CE CCSM4 reference frame, and the spatial structure reflects the reanalysis prior, not raw past climate. This bites hardest here because at buffer scale the single collapsed value *is* essentially the prior at that location.
- **Modality (Block 6 two-regime) is NOT extended to the grid path.** Report mean + spread per epoch; let the spread speak.
- **Envelope:** same top-level fields as Blocks 1–6 (`variable, method, status, representative_score, representative_raw, n_basins, coverage_weight`), with two consequences Block 7 surfaces rather than solves: `n_basins` is the wrong unit here (units are grid cells) → carry `n_units` + a `unit_type` tag instead; and `coverage_weight` here means the fraction of the query area covered by data-bearing cells, a different notion from the basin-renormalized coverage of Blocks 1–6. Flag both to the register as engine-assembly items.

---

## Working query (the fixture)

Point (lon −2.9833, lat 16.8167), radius 100 km, level L06 — the same buffer as step1 (9 basins, weight sum 1, shortfall 0). Primary span **1100–1200 CE** (the documented Timbuktu example; safe for all three sources). In 7.5 also run a wide span (e.g. 1000–2000 CE) to show the history shape against the snapshot.

---

## Data reference (confirm against `signature.py`)

- `temporal.hyde_cells` — ~2.22M cells, polygon `geom`, `area_km2`, and `cropland`, `grazing`, `pasture`, `rangeland` each `real[]` indexed by `step_idx`. Join `temporal.hyde_times` (`step_idx → year_ce`) for the time slice. HYDE cells exist over land only: an absent cell (ocean) is *not* a zero, and a zero land-use value (e.g. desert cropland) is a real zero — keep them distinct.
- `temporal.lmr_climate` — 16,380 grid **points** at 2°×2°, point `geom`; `pdsi`, `air`, `prate` each `real[]` length 2001 (1–2001 CE, 0-indexed). The 2° footprint per point comes straight from the LMR footprint precompute script (CC's reference implementation) — the centre/corner registration is settled there, so no reconstruction or estimation is needed.
- `temporal.evolv2k_v4` — rows by `year_ad`; `vssi_tg`, `so4_grl`, `so4_ant`, `lat`, `location`.
- Conventions: `# Cell N` first line of every cell; `from scripts.shared.db_utils import db_connect` (db `cedop`); spatial via `gpd.read_postgis(..., geom_col='geom').rename_geometry('geometry')`; non-spatial via `pd.read_sql` with f-string SQL; PostGIS geometries passed as WKT via `ST_GeomFromText()`; output path derived from module location.

---

## Steps

### 7.1 — Grid reconnaissance (confirmatory, no writes)

Rebuild the Timbuktu buffer (step1 construction). For HYDE, find every `hyde_cells` polygon intersecting the buffer and its overlap area with the buffer; report the count and the overlap-fraction distribution. For LMR, take the 2° footprint formula from the precompute script (registration is settled there — no estimation), run the PostGIS intersection of those footprints against the buffer, and report each one's overlap area; while there, verify the tiling is gapless. For both, compute the effective-cell-count (`1 / Σ wᵢ²`, weights = overlap area normalized to covered area) and the data-bearing coverage (covered area ÷ buffer area). The expected result, to be confirmed not assumed: HYDE in the hundreds of cells with coverage ≈ 1 (inland), LMR effectively ~1 cell with the buffer sitting inside a single footprint. Print a small table; write nothing. This step alone validates the routing premise.

### 7.2 — The diagnostic figure (confirmatory)

In the style of the step1_ buffer-resolver figure (reuse its code), produce the resolution-contrast picture: one panel of the buffer with the clipped HYDE cells (the dense swarm), one of the buffer with the LMR footprint(s) it touches (the buffer dwarfed by one 2° cell). This is the visual statement of why the diagnostic routes them oppositely, and the confirmatory centrepiece. Save the PNG to the areas output folder.

### 7.3 — Confirm the diagnostic and record the threshold (confirmatory)

From 7.1's numbers, state HYDE's and LMR's effective-cell-counts, propose a provisional effective-cell-count threshold, and show that at Timbuktu HYDE lands "report distribution" and LMR lands "collapse." Record the threshold as provisional and add a register row pointing it at the multi-fixture calibration step (alongside T=20, the modality gaps, the zero-inflation threshold). No production commitment — this is the decision rule written down with one fixture behind it.

### 7.4 — The spatial collapse primitive, single time step (build)

For one year (use 1150; resolve to the overlapping HYDE epoch via `hyde_times`, and the LMR index), compute the areal aggregate of each variable over the buffer. HYDE (4 vars): area-weighted mean across clipped cells (weight = overlap area, normalized over data-bearing cells — do not treat absent cells as zero), plus the distribution summary (area-weighted p10/p90 and sd) since the diagnostic says report. LMR (3 vars): area-weighted mean across the overlapping footprint(s), distribution suppressed, LMR caveat string attached. eVolv2k: the year's forcing value(s), no spatial operation. Emit one row per variable in the shared envelope — `representative_score` null, `representative_raw` = the area-weighted value, `n_units` + `unit_type`, `coverage_weight` = data-bearing fraction, and a `method` that names the path (`grid_areal_distribution` for HYDE, `grid_areal_collapsed` for LMR, `global_forcing` for eVolv2k). Review carefully — this is the core.

### 7.5 — Map the primitive over the time axis (build)

Given from/to, resolve the time steps — HYDE as every overlapping epoch (do not interpolate; expose the irregular cadence), LMR as annual fields in range, eVolv2k as in-range events — and run 7.4's primitive at each, assembling the time series of areal aggregates. Run the primary span (1100–1200) and a wide span (1000–2000) and show that snapshot (narrow → one step) and history (wide → many steps) fall out of the same code with no mode flag. Note the payload asymmetry in the report: HYDE = few epochs each carrying a distribution; LMR = many years each a single value. Watch the HYDE distribution change shape across epochs — the areal analogue of the Kaifeng intensification signal.

### 7.6 — Envelope, caveats, housekeeping (build)

Write the Block 7 results in the shared envelope (Blocks 1–6 columns plus `n_units`/`unit_type` and the grid-coverage notion), the LMR caveat on every LMR row, and a companion distribution table for the HYDE per-epoch spreads. Do not solve the two engine-assembly consequences here — add register rows for them: the `n_basins` → unit-tagged-field generalization, and the second coverage notion (data-bearing-cell fraction vs basin-renormalized coverage). Record any new provisional constant against the multi-fixture calibration item. Any mutation of an existing file or the catalog follows propose-then-confirm-then-write-with-backup; Block 7 should mostly produce new outputs, not mutate.

---

## On completion

Update the tracker (Block 7 status, output filenames, new locked decisions if any), move resolved register items to Closed, and leave the engine-assembly consequences as open register rows for the assembly step.

---

## postscript

The following items were requested by Opus after reviewing the areas_findings.md file and other status docs.

CC — three quick checks on the Block 7 outputs, while it's fresh.

- AF.3, the 1950 HYDE spike — source or seam? Read the raw 1950 grazing value directly from the hyde_cells array for two or three Timbuktu buffer cells and compare against HYDE's published 1950 grazing for those cells. Match → artifact is in the source, hyde_caveat stands. Mismatch → it's a step_idx → year misalignment at the decadal-to-annual seam: fix the indexing instead of caveating, and check whether any other seam years are hit.
- AF.4 confidence split. Qualify the entry: the floodplain-intensification half (p90, large absolute values) is robust; the fringe-decline half (p10, 0.225 → 0.138, all sub-0.25 km²/cell) sits where HYDE's downscaling allocation can move cells with no real signal. Mark the p10/abandonment reading low-confidence pending Phase-4 provenance review.
- Spread-unit collision. AF.4 reports HYDE spread as "pp," but it should be native km²/cell. Confirm the Block 7 HYDE spread column isn't sharing a name and unit with the percentile-point spread from Blocks 1 and 6 — if it is, rename or unit-tag it now, before engine assembly merges them in the shared envelope.