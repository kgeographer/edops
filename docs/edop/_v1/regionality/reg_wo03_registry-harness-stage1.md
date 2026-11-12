# WO-03 (regionality): registry harness, stage 1

Draft of 2026-11-12, revised after CC's notes (`reg_wo03_cc_notes.md`).

## Goal

Prepare the engine for regional datasets by building a source registry: one place that records, for every data source the signature reads, what it covers and how it is described. This stage builds and fills the registry and captures a regression baseline. Nothing reads the registry yet, and no signature changes.

## Context

- GEDA is stored locally (`temporal.geda_climate`, WO-02) and is the first regional dataset. LBDA may follow.
- What a signature returns will depend on parameters (place, scope, time span) and on which sources cover that place and time. The registry is where that is recorded, for all sources the signature reads.
- Staged plan: (1) registry built and filled, baseline captured (this WO); (2) the engine and the Sandbox's span checks read the registry, signatures unchanged; (3) GEDA joins through the registry, payload changes by addition only; (4) display, decided later with the Dashboard design.
- Branching: cut `registry` from `regionality`; merge back to `regionality` only. `dashboard` is fast-forwarded from `regionality` when Karl chooses. Nothing reaches `main` before v1; hotfixes to v0.4.2 on `main` are merged forward into the v1 line.

## Part A: regression baseline

1. Capture complete signature payloads, through the real routes using FastAPI's test client (no running server), as reference files in the repo (compressed where large):
   - Timbuktu, single basin L6, and 100 km buffer L6 (the primary fixture).
   - The two-fixture pair for lens validation: Tbilisi and the flat city, named as in the repo's fixture documentation or tests (if it is not recorded, ask Karl).
   - One polity request (Northern Song 961, as in the existing examples).
   - Band T requests for Timbuktu and Kyiv's basin, 1236–1240 and 1300–1400.
2. A comparison script, run as a pytest: new fields are allowed; any changed or removed field fails, reported field by field. Fields that legitimately vary (timestamps, timings) are ignored; list them. Reference files are re-captured only at a stage boundary, with Karl's approval.

## Part B: where source knowledge lives now

3. For each source the signature reads (BasinATLAS, ecoregions and biomes, Cliopatria, LMR, HYDE, eVolv2k, and GEDA once added), record where the engine, routes and Sandbox hold: extent, years covered, years recommended or shown, grain, units, citation and licence, caveat text, span or extent checks, and year-specific rules. Name file and line, or table. CC's preliminary list (`_LMR_RANGE`, the HYDE 1950 epoch rule, low-resolution thresholds, `CAVEAT_TEXTS`, the LMR description and "0-1998" text in `routes_common.py`, the 700 CE floor in `routes_sandbox.py` and `sandbox.html`) is the starting point.
4. Where the same fact is held in more than one place, list each place and whether they agree. Do not resolve disagreements.
5. Record that `meta.signature_version` is hard-coded "0.4" in three places; consolidating it is a stage-2 item, outside the registry.

## Part C: registry

6. Propose a schema, drawn from Part B. Source of truth: a YAML file in the repo, loaded into a table (as the variable catalog is a repo file). Per source, at least:
   - identifier, name, version, kind (field, network, polygon set, gridded time series, events), the table it lives in;
   - footprint: global, or a simplified geometry used only to decide whether the source can touch a request at all (exact coverage is computed from the source table's own cell geometry, as in WO-02);
   - years covered, and years recommended or shown where they differ (LMR: covered 0–1998, recommended from 700), with the reason and its origin (for LMR's 700 floor: EDOPS's own EDA, F10.1 and F10.3);
   - year flags: a list of {years, flag, note} (GEDA: 1990–2020 observed; HYDE: the 1950 epoch rule);
   - grain, units, citation, licence, caveat text;
   - the variables the source supplies, by catalog identifier. Derived variables list each source they draw on. The variable catalog TSV is not changed.
7. Stop here for Karl's approval of the schema.
8. After approval: the YAML file, the loader, the table, and a row for every source in scope, GEDA included.
9. A pytest that every source the signature reads has a registry row, every row names a table that exists, and every catalog variable is claimed by at least one source.

## Provisos

- No change to engine, API or Sandbox behaviour. The baseline test passes at the end of this WO.
- New tables only; no existing table or file the engine reads is altered. The live `cedop` database is shared with v0.4; additive tables are harmless to it.
- Report what is found; where something is unclear or held inconsistently, list it rather than resolve it.

## Deliverables

- Reference files and the baseline test (Part A).
- `reg_wo03_results.md` and `reg_wo03_summary.md`: Parts B and C, with the schema proposal.
- After approval: registry YAML, loader, table and test (items 8 and 9).

## Acceptance gate

The baseline test passes; every source in scope has a registry row; the registry test passes; engine output is unchanged.