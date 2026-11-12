# WO-03 (regionality): registry harness, stage 1

Draft of 2026-11-12.

## Goal

Prepare the engine for regional datasets by building a source registry: one place that records, for every data source in a signature, what it covers and how it is described. This stage builds and fills the registry and captures a regression baseline. Nothing reads the registry yet, and no signature changes.

## Context

- GEDA is stored locally (`temporal.geda_climate`, WO-02) and is the first regional dataset. More may follow (LBDA next).
- What a signature returns will depend on parameters (place, scope, time span) and on which sources cover that place and time. A registry makes that decision in one place, for all sources, global and regional, temporal or not.
- Staged plan: (1) registry built and filled, baseline captured (this WO); (2) the engine and the Sandbox's span checks read the registry, with signatures unchanged; (3) GEDA joins through the registry; (4) display, decided later with the Dashboard design.
- Branching: work on a branch from `dashboard`; merge back to `dashboard` only, never to `main`.

## Part A: regression baseline

1. Save complete signature payloads (as returned by Get signature) for a fixed set of requests, as golden files in the repo:
   - Timbuktu, single basin L6, and 100 km buffer L6 (the primary fixture).
   - The two-fixture pair used for lens validation (Tbilisi and the flat city).
   - One polity request (Northern Song 961, as in the existing examples).
   - Band T requests for Timbuktu and Kyiv's basin, 1236–1240 and 1300–1400.
2. A script that re-runs the set and reports any difference from the golden files, field by field. Ignore only fields that legitimately vary (timestamps, timings); list which.

## Part B: where source knowledge lives now

3. For every source the engine uses (BasinATLAS and its attributes, the ecoregion and biome sources, Cliopatria, LMR, HYDE, eVolv2k, any others), record where the engine and the Sandbox get each of: spatial extent, years covered, grain or resolution, units, citation and licence, caveat text, and any span or extent checks. Name the file and function or table for each.
4. How the variable catalog (`EDOPS_variable_catalog_v0.4.tsv` and its database form, if any) relates to sources: which columns describe the source rather than the variable.

## Part C: registry

5. Propose a schema for one row per source, drawn from Part B: identifier, name and version, kind (field, network, polygon set, gridded time series, events), footprint (geometry, or global), years (or none), grain, units, citation, licence, caveat text, observed-years rule where relevant, the table it lives in. Keep it to what Part B shows is needed, plus what GEDA needs.
6. After Karl approves the schema: create the table and fill a row for every source, GEDA included. Link the variable catalog to it (catalog rows point to a source row), without changing what the catalog already holds.
7. A check that every source the engine uses has a registry row and every registry row names a table that exists.

## Provisos

- No change to the engine, API or Sandbox behaviour. The baseline script (Part A) must report no differences at the end of this WO.
- Only new tables; no existing table is altered. Note whether the review deploy for `dashboard` would share a database with the live site.
- Part C stops after item 5 until Karl approves the schema.
- Report what is found; where something is unclear (for example, a source described in two places that disagree), list it rather than resolve it.

## Deliverables

- Golden files and the baseline script (Part A).
- `reg_wo03_results.md` and `reg_wo03_summary.md`: Parts B and C, with the schema proposal.
- After approval: the registry table, its rows, and the check (items 6 and 7).

## Acceptance gate

The baseline script reports no differences; every source has a registry row; the engine's output is unchanged.