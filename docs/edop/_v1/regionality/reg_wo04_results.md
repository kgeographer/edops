# WO-04 results: registry harness, stage 2

Spec: `reg_wo04_registry-harness-refactor.md`. Branch `registry`. In progress; this file is extended as parts complete.

## Done so far

**Part 0 (complete)**
- LMR years 0-1998 to 0-2000 in the engine clamp (`_LMR_RANGE`), `temporal.py`, the API parameter text, the generated API guide, the data-sources page, the project summary, the LMR quality-border rubric and the Sandbox cheat sheet. Test `tests/regionality/test_lmr_range.py`: a span to 2000 returns rows for 1999 and 2000; a span past 2000 stops at 2000. Commit 334f645. Engine, API and regionality partitions: 419 passed.
- One constant, `SIGNATURE_VERSION = "0.4"` in `routes_common.py`, in place of three hard-coded strings. Output unchanged (baseline passes). Commit c4c21dd. The value moves to "0.5" when the `sources` block lands.

**Part A (items 3 to 5)**
- Final registry YAML: `documentation/EDOPS_source_registry.yaml` (from the WO-03 draft; header rewritten, stale remarks and the drafting-questions block removed). Commit a82b43e.
- Loader `scripts/edop/regionality/load_source_registry.py` into `public.source_registry` (moved from `temporal`: sources are not all temporal). Local database only. Commit 2aaf5a1.
- Registry test `tests/regionality/test_registry.py` (5 tests): entries for every source, named tables exist, every catalog variable claimed by a source, one owner each except `elevation_point`, and the YAML agrees with the loaded table.

## Needs attention going forward

1. **The catalog must be the single truth of every variable EDOPS can deliver (top item; the work order after WO-04).** Everything that describes a signature (docs, UI labels, caveats, a future prose layer) should ask the catalog, so every variable returnable from the UI or either API needs a row and a complete, documented key. Scope for that work order: give every returnable variable a row (including the elevation fields); make the join key complete; move the catalog from a file read in four places to one loader; add a test over the saved payloads that fails when a returned variable has no row. The registry also holds variable facts today (payload name, catalog key, column and units for the temporal sources), a second copy of what the catalog should own, put there because the pairing had nowhere else to live. Once the key is complete, the registry should keep source-level facts and point to catalog keys. Findings so far: the catalog is not yet a complete key to what a signature returns. Checked against the ten baseline payloads (80 distinct variable names): 74 match a catalog row on `api_key_s` or `api_key_u` (30 of them also on `schema_key`); 6 match nothing.
   - `lmr_air`, `lmr_prate`, `evolv2k_vssi`: the catalog rows exist (`lmr_temp_anomaly`, `lmr_precip_anomaly`, `evolv2k_vssi_per_event`) but their `api_key_s` is a different name (for example `air_series`), so the key does not join. The registry pairs them by hand. Decision for the crosswalk work order: fix the catalog's key or rename the payload field (which changes the baseline).
   - `elev_source`, `elev_dataset`, `elev_resolution_m` (public signature, beside `elevation_point`): no catalog rows. Decision: give them rows, or treat them as attributes of `elevation_point`.
   - Limits: only what the ten payloads return (other levels, bands and options may return more); the check shows names exist, not that each points at the right row. The registry test checks the other direction (every catalog row is claimed by a source), not this one. Principle for the crosswalk: the catalog is the truth of EDOPS variables, so every variable a signature can return, from the UI or either API, needs a row.
2. **HYDE 3.4 to 3.5 rename** is deferred to the pre-v1 docs check. 45 tracked files say "HYDE 3.4" (about 15 live, about 30 frozen records). Three baseline payloads contain the string (the 1236-1240 caveat for Timbuktu and Kyiv, and `meta.data_sources` in the public signature), so the rename needs a deliberate re-capture of those three. The registry says 3.5, so the new `sources` block will say 3.5 while the older text says 3.4.
3. **`routes_common.py:51` still says LMR "0-1998 CE"** (`meta.data_sources`). The string is in the public-signature reference, so changing it needs a re-capture. Its copies in `documentation/edops_schema_area.json`, `edops_schema_basin.json` and the cheat-sheet example `07_public_signature...json` stay in step with it. Deferred to the pre-v1 docs check with item 2.
4. **`public.source_registry` exists in the local database only.** A deploy needs the loader run on the server first. The table-exists and YAML-versus-table tests need the local database with the loader run.
5. **The HYDE entry names only `temporal.hyde_cells`**, but the code also reads `temporal.hyde_times` and the per-basin step tables (`hyde_basin06_steps`, `hyde_basin08_steps`). The registry test passes either way and cannot catch the omission.
6. **The registry test claims whole catalog sources by name** (BasinATLAS, Derived), not variable by variable. A BasinATLAS variable the code reads but the catalog omits would not be flagged.
7. **`lmr_status` with the permitted-sources option:** if LMR is excluded, `lmr_status` may still say `out_of_range`, which is not quite true. To check when the Band T extraction is done.
8. The closed WO-03 files still say the registry table is `temporal.source_registry`; it is `public.source_registry`.
