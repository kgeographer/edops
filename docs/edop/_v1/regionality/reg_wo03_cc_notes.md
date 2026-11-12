# WO-03: Claude Code's assessment (before any work)

2026-11-12. On `reg_wo03_registry-harness-stage1.md`. Nothing has been built.

## Branching

1. `dashboard` is an ancestor of `regionality` (0 commits ahead, 75 behind), and `regionality` already holds the WHG work. The WO's "branch from `dashboard`, merge back to `dashboard` only" can be met by cutting `registry` off `regionality` and merging back there. `dashboard` can be fast-forwarded to `regionality` whenever Karl chooses. Please revise that line.
2. Nothing reaches `main` before v1. Hotfixes to v0.4.2, including the profiles page already on `main`, will need merging forward into the v1 line.

## Part A (baseline)

3. Stage 1 changes no engine behaviour, so the baseline equals today's `main`, which is v0.4.2.
4. At stage 3 the payload changes on purpose, so "no differences" cannot hold. Suggest the script allow additive fields and fail on any changed or removed field, with the golden files re-captured at each stage.
5. "The flat city" in the lens pair is not named in the WO. Needs the name.
6. Capture over HTTP (needs the local server) or by calling the engine in-process? Full payloads for Kyiv 1300 to 1400 will be large.

## Part B (where source knowledge lives)

7. Source knowledge is scattered, and some of it is duplicated.
   - `engine.py`: `_LMR_RANGE (0, 1998)`, the HYDE 1950 epoch rule, the low-resolution thresholds, `CAVEAT_TEXTS`.
   - `routes_common.py`: a hard-coded LMR description (line 51); "0-1998" in the Query descriptions (lines 215-216).
   - The 700 CE floor: `routes_sandbox.py:1291-1299`; `sandbox.html:3674` and `:4284`.
   - The variable catalog's `source` column holds only a label (BasinATLAS 71, Derived 17, eVolv2k 6, LMR 4, HYDE 4), with no extent, citation or caveat.
8. `meta.signature_version` is hard-coded `"0.4"` in three places (`routes_common.py:324`, `:366`, `:442`). Karl's plan is to tie release numbers to a signature version, with 1.0 for February. The registry could hold it.

## Part C (registry schema)

9. LMR has two year ranges: coverage 0 to 1998, and a map-layer quality floor of 700. The schema should separate years covered from years recommended or shown, or the registry cannot replace the Sandbox's checks in stage 2.
10. GEDA's footprint is irregular (28,970 valid cells), and WO-02 found partial coverage matters (0.498 and 6.7% cases). The registry needs a real footprint geometry, or a pointer to the table that computes coverage. A simplified polygon would give inexact fractions.
11. GEDA's observed years (1990 to 2020) and HYDE's 1950 epoch artefact are both year-specific flags. A generic flags field would fit better than a bespoke observed-years column.
12. Linking the catalog (item 6) means adding a `source_id` column to the TSV. `signature.py`, `test_codebook_alignment` and the generated codebook all read that file; not yet checked that they tolerate an extra column. Not yet checked whether the catalog has a database form. The `Derived` rows have no single source.
13. For the source of truth, suggest following the catalog pattern: a repo file loaded into the table, rather than a hand-filled table. Design call for Opus.
14. Suggest limiting "every source" to what the signature reads: BasinATLAS, ecoregions and biomes, Cliopatria, LMR, HYDE, eVolv2k and GEDA.

## Provisos

15. The live `cedop` database is shared with v0.4, so new tables are additive and harmless to prod. A v1beta would need `geda_climate` and the registry loaded on the server, plus its own service and nginx `/api/` cache.
16. Item 7 (the registry check) should be a pytest, so it falls under the zero-failure rule.
