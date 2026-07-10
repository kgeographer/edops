# WO22 — L08 viability + Level-select wiring

**Branch:** `surf_wo22` — notebook exploration first; wiring only after viability is proven.
**Type:** Probe → assess → wire. Closes SURFACE's last surfacing gap: the engine and API already
do L08 (`&level=`), v1 has an operable Level select, but v2 is frozen at L06. This exposes the
instrument's actual scale range — the honest close of SURFACE.

Two-stage, gated: **(1) prove L08 viable internally under v2's real load; (2) wire it to the Level
select where viable.** Stage 2 does not begin until Stage 1's findings are reviewed. Goal-setting,
not a spec — the notebook characterizes; the port/wire decision follows the data.

## Why probe-first

L08 is ~4× the basins of L06 (~8M rows where L06 had ~2M in the HYDE steps table). That hits
**every L08 consumer** at once: signature aggregation over a footprint, the choropleth feature-state
paint, and the HYDE pre-aggregated steps table. v1's Level select works *somewhere*, but likely was
never stressed at L08 under the full choropleth load v2 now carries. So characterize before wiring,
same discipline as the WHG and HYDE-crosswalk probes — "it should scale" is not a finding.

## Stage 1 — Notebook: is L08 affordable under v2's load?

`notebooks/edop/surface/wo22_l08_viability.ipynb`. Characterize L08 across the consumers, reporting
actual numbers against the L06 baselines already on record:

1. **Choropleth paint.** Per-request cost of a `level=8` values query for a BasinATLAS variable
   (`/api/explorer/values?...&level=8`) — how many basins returned, query time, payload size, vs.
   L06's ~0.3 MB / fast baseline. This is the one most likely to hurt: ~4× the features to paint via
   feature-state, plus the vector-tile source question below.
2. **HYDE at L08.** The L06 win (WO18) was a pre-aggregated `hyde_basin06_steps` table (2.08M rows,
   0.033s/request). L08 would need its own `hyde_basin08_steps` — ~4× rows, ~4× build time.
   Characterize: build cost, table size, per-request query time. Does the same pre-aggregation
   pattern hold at L08, or does something (build time, index size, query) break? Report; **don't
   build the full table unless the numbers say it's the path** — a sample/extrapolation may answer
   viability without a 40-minute build.
3. **LMR at L08.** LMR is a 2° grid painted independently of basin level — confirm whether L08
   changes anything for it (likely not, but verify rather than assume the grid is level-agnostic).
4. **Signature aggregation.** Cost of an areal signature (polity or buffer) aggregated over L08
   basins vs. L06 — the aggregation touches more units. Time a representative case.
5. **The vector-tile source.** The choropleth paints via feature-state on `basin06.pmtiles`. L08
   needs `basin08.pmtiles` (or equivalent) as a source — does it exist / is it served to v2's origin?
   If the L08 tileset isn't reachable, that's a Stage-1 blocker to surface, not work around.

**Stage 1 deliverable:** a viability verdict per consumer — affordable as-is / affordable with the
pre-aggregation extended / not affordable without further work — with the numbers. This is the
review gate. Karl decides how far Stage 2 goes based on it.

## A Stage 2a was inserted (and completed) after the fact; see SURFACE_tracker.md

## Stage 2b — Wire to the Level select (where Stage 1 says viable)

Only after the Stage 1 review. Then assess and wire:

- **Port assessment.** v1's Level select is operable — read it and report whether it ports cleanly
  to v2, or whether v2's architecture (MapLibre + feature-state paint + the pre-aggregated steps
  tables, none of which v1 has) means a fresh wire is cleaner than a port. Don't assume port; assess.
- **Wire the control.** Make the v2 Level select operable for the scales Stage 1 cleared. Changing
  level re-resolves the active scope's signature and re-paints the active choropleth at the new
  level (the `&level=` param threads through the existing paths). If L08 needs its own HYDE steps
  table / tileset and Stage 1 approved building them, that build is Stage 2 work.
- **Honest gating in the UI.** If a consumer is viable at L08 but slow enough to matter (e.g. a
  multi-second paint), the control should reflect that honestly — not silently hang. How (a spinner,
  a note, disabling the heaviest variable at L08) is a small UX call; surface it rather than ship a
  control that appears instant and isn't.

## The scale story is a demo asset (note, not scope)

L08 vs L06 makes the MAUP finding *visible* — same region, two scales, regime cores holding,
transition zones shifting. That's a DEMO-phase money shot, not WO22's job. WO22 just makes the toggle
real and affordable; the show-and-tell is later. Flagging so the wiring supports a clean L06↔L08
compare, but not building the comparison view here.

## Out of scope

- The MAUP comparison view / scale-compare demo (DEMO phase).
- Analysis and Demo tabs, correspondence (DEMO phase — different work entirely).
- draw-study-area (still deferred, before-Braga).
- `sandbox.html` (v1) untouched — read its Level-select code, don't modify it.

## Accept gate

- Stage 1: viability characterized per consumer (choropleth, HYDE, LMR, signature, tileset) with
  numbers vs. L06 baselines; verdict reviewed before Stage 2.
- Stage 2 (for cleared scales): Level select operable in v2; changing level re-resolves signature +
  re-paints choropleth at that level; any L08 build (steps table / tileset) done only if Stage 1
  approved it; honest UI gating if a path is viable-but-slow.
- Port-vs-fresh-wire decision reported with rationale.
- L06 behavior unchanged; existing scope/choropleth machinery and `sandbox.html` untouched.

## Tests

- Route: `&level=8` value queries return expected shape/coverage for the cleared variables.
- Playwright: Level select changes level and re-resolves/re-paints (for cleared scales); L06 path
  unregressed.
- Engine/app suite green — zero FAILs, zero unexplained warnings. Note counts.

## Findings

`docs/edop/surface/wo22_findings.md`. Report: L08 per-consumer numbers vs L06 (choropleth, HYDE
build/query, LMR, signature aggregation); the tileset reachability answer; the viability verdict;
the port-vs-fresh-wire decision + rationale; what was built in Stage 2 (steps table? tileset?) and
what stayed deferred; the viable-but-slow UI gating if any; whether L08 closes SURFACE's surfacing
gap or leaves a characterized remainder.
