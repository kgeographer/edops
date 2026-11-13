# WO-04 summary: registry harness, stage 2

Spec: `reg_wo04_registry-harness-refactor.md`; stage-boundary follow-up (WO-04a items 1 to 5, done here): `reg_wo04a-cleanup-bits.md`. Record: `reg_wo04_results.md` (parts, the stage boundary, and 19 "needs attention" items). Plan for Part B: `reg_wo04_refactor_plan.md`. Branch `registry` (cut from `regionality`). Nothing merged to `regionality` or `main`, nothing deployed.

## What was built

- **Part 0.** LMR range corrected from 0-1998 to 0-2000 (engine, `temporal.py`, API text, docs, cheat sheet), with a test. One `SIGNATURE_VERSION` constant ("0.4") in place of three hard-coded strings.
- **Part A.** The source registry: `documentation/EDOPS_source_registry.yaml` (nine sources), the only copy (a table and loader were built, then removed at the stage boundary, by decision); `tests/regionality/test_registry.py` (4 tests).
- **Part B.** `aggregate_band_t` refactored into one function per source (`_band_t_evolv2k`, `_band_t_lmr`, `_band_t_hyde`) over a shared query object. Output unchanged at every step; three baseline references were added first to cover the buffer branch, the 1950 caveat and polity with Band T.
- **Part C.** The engine asks the registry (`scripts/edop/areas/source_registry.py`, `check()`) whether a source applies, instead of holding its own year ranges. `_LMR_RANGE` and `_EVOLV_RANGE` are gone. An optional `permitted` set lets a caller restrict the sources considered (nothing passes it yet).
- **Part D.** Responses carry a top-level `sources` block (`used` and `not_applied`; each entry has id, name, version, citation, licence, optional note). Engine path and public basin path both emit it; the public buffer and area routes carry the engine's. `meta.data_sources` and `lmr_status` are unchanged.

## What changed in behaviour

- LMR spans now run to 2000 CE.
- Every signature response gains `sources`. This is an additive change, so `signature_version` is now "0.5".
- Response strings: HYDE caveats and `meta.data_sources` say "HYDE 3.5" (were 3.4); `meta.data_sources` says LMR "0-2000 CE" (was 1998).
- Nothing else in any saved baseline payload changed (diff checked before the re-capture: no removed fields, five changed values, one added field).

## Stage boundary (WO-04a items 1 to 5)

The registry became YAML-only (loader and table test removed; HYDE lists all four tables). The response strings and the version were changed together, the new payloads were diffed against the saved references (additions included, reviewed by Karl), and all 13 references were re-captured once. The baseline now includes `sources`, so when WO-05 adds GEDA the only differences will be GEDA's. Details: results, "Stage boundary".

## What did not change

GEDA is not served: it has a registry entry (status `stored`) but no query on either path, so it appears in no response. It joins in stage 3 (WO-05). The public and engine methods are otherwise untouched.

## Test state

- Baseline: 13 payloads through the real routes, compared with additions allowed and changes or removals failing. Through Parts 0 to D the ten original references were never overwritten (three were added); at the stage boundary all 13 were re-captured once, deliberately.
- New tests: `test_lmr_range` (2), `test_registry` (4), `test_source_registry` (18), `test_permitted_sources` (7), `test_sources_block_engine` (8), `test_sources_block_public` (8).
- Full suite before the stage boundary (merge gate, 2026-11-13): 710 passed, 21 skipped (the usual, expected skips), no failures.
- **Full suite after the stage boundary (2026-11-13): 709 passed, 21 skipped, no failures** (one fewer than before: the YAML-versus-table test was removed with the loader).
- A local check against the running server: health 200; the Timbuktu basin signature with `bands=ABCDET` and 1100-1200 returns `sources.used` of BasinATLAS, Mapzen elevation, HYDE 3.5, LMR v2.1 and eVolv2k v4, with `not_applied` empty.

## Open items

See the results file. Those most relevant to the next steps:

- Catalog as the single truth of every variable (item 1): the work order after WO-04.
- GEDA through the registry (item 10): footprint test, zero-cell handling, parameterized SQL.
- Pre-v1 docs check (items 2, 17, 19): the other "HYDE 3.4" mentions; `sources` in the schemas, API guide and cheat sheet (and example 07 refreshed); the "2023" and the citation on the HYDE `data_sources` line.
- The two paths report a span with no HYDE step differently (item 9); for the unification work order.
- Registry schema addition for Opus: the `outside_span: nearest_step` key on HYDE (item 12).
- The local `public.source_registry` table is unused and can be dropped by hand (item 4).

## Next

Opus's review. Work continues on `registry` (WO-05); no merge back to `regionality` until a stage needs it.
