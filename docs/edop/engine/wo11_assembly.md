# CC work order — Engine assembly WO11: final assembly

**Date:** 2026-06-24 · branch off WO10b (`engine11` or your naming) · the capstone. Stop for review.

---

## What this is

Every piece exists and is regressed in isolation. Assembly chains them into one callable that takes a query and returns the complete areal signature across all bands. **No new aggregation logic, no new contract decisions** — this is threading tested functions and proving the seam-up changed no numbers. It's the "pull it all together for Timbuktu" step.

**Pieces to wire (all in `engine.py`):** `resolve_buffer` (WO1) · `attach_values` (WO2) · `dispatch_variable` (WO3) · `aggregate_b1`/`b2`/`b3`/`b4`/`b5` (WO5–9) · `aggregate_band_t` (B7, WO4) · `apply_modality` (B6, WO10) · `make_row`/`project_row`/`assemble_payload` (WO4) · `load_catalog`, `weighted_quantile`, `diff_output`, `CAVEAT_TEXTS`.

**Standing rule:** one-directional; notebooks frozen; engine reproduces the frozen TSVs.

## The pipeline to wire

**Build-once (startup, per the WO2 seam):** `load_catalog` → the catalog (`meta_df`). Query-independent; built once, not per call.

**Per-query callable** — one public entry point (`signature` / `areal_signature`, your naming), taking the query (lat, lon, radius_km, level, bands, optional `from_year`/`to_year`) and a projection switch (`include_detail`):

1. `resolve_buffer` → weighted basin set.
2. `attach_values` → the basin matrix (scores, labels/ids, raw, flags).
3. dispatch each catalog variable via `dispatch_variable` and run it through its branch (B1–B5) on the matrix; collect rows.
4. **Parallel grid path:** if Band T is requested *and* a span is given, `aggregate_band_t` on the query geometry directly (it does not use the basin matrix); collect its rows. (Band T gate: no T without a span.)
5. `apply_modality` post-pass over the distribution-bearing rows (B1 `area_weighted` + B5 `distribution_only`).
6. `assemble_payload` → the contract-shaped object (neighborhood echo, `shortfall`, `caveats`, the projected rows).

This callable is the engine's public entry point — the thing the future routes (buffer on `/signature`, polygon on `/area`) will wrap as thin front doors.

## Integration risks to surface (not patch silently)

The branches were each tested on hand-fed inputs; wiring is where their interfaces meet for the first time. Surface, don't paper over:

- **Input threading** — confirm each branch's required inputs are satisfied by the `resolve_buffer` + `attach_values` outputs; flag any branch needing something upstream doesn't produce.
- **Dispatch → branch routing** — the dispatch label maps to the right `aggregate_bN`; the 5 non-emitters (`strata_code`, `ecoregion`, `river_area_upstream`, `endorheic`, `coast_flag`) are excluded/deduped/consumed; the emitted row count comes out to **51** (basin bands), plus Band T rows when requested.
- **Order** — `apply_modality` after B1+B5 and before `assemble_payload`; B4 synthesizes from the consumed flags; Band T gated on the span.
- **Build-once/per-query seam** — decide and flag where `load_catalog` sits (engine init vs passed in).

## Acceptance — the capstone regression (contract §9)

The full callable on the Timbuktu fixture (lat 16.8167, lon −2.9833, r=100 km, L06; Band T span 1100–1200), full detail, reproduces **all 13 frozen TSVs at once** at strict tolerance — honoring the blessed deviations already re-frozen (LMR caveat, perennial flag, modal label, distribution_only coherence). You may validate incrementally (basin path against its TSVs, then add Band T, then the full set) — your call. Show the complete Timbuktu signature in both lean and full projection. Confirm no number changed versus the per-branch regressions: assembly is a seam-up, not a recomputation.

## Out of scope

- future resolvers — upstream, adjacency/ring-expansion, polygon `/area` (v0.4).
- the routes themselves — thin wrappers, a later step.
- edge/context features and the coastal-fixture deferrals (v0.4 / register).

## On completion

Report the public callable signature, the build-once/per-query split, the all-13-TSV regression result, and any integration mismatch surfaced. Update the tracker: **engine assembled and whole; the v0.3 areal signature is complete end to end.** Stop for Karl's review.
