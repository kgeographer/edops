# WO-03 results: registry harness, stage 1

2026-11-12. Spec: `reg_wo03_registry-harness-stage1.md`; assessment before the work: `reg_wo03_cc_notes.md`. Branch `registry` (cut from `regionality`). A plain-language summary is in `reg_wo03_summary.md`. **Status:** Part A done. Part B done, with the limits listed at the end of that part. Part C stops after the schema proposal (item 6), for Karl's approval; items 8 and 9 (YAML file, loader, table, test) are not started. No engine, API or Sandbox behaviour was changed.

## Part A: regression baseline

**What it is.** Ten requests, each captured through the real routes with FastAPI's test client against the local database (GET only, no server needed), stored as gzipped JSON in `tests/regionality/baseline_reference/` (about 120 kB in all, with a `MANIFEST.json` giving the requests, capture date and git head).

| Name | Route and request |
|---|---|
| `timbuktu_single_basin_L6` | `/api/areas`, single basin, L6, bands ABCDE, detail |
| `timbuktu_buffer100_L6` | same, 100 km buffer |
| `tbilisi_single_basin_L6` | single basin, L6 (lens fixture, rugged) |
| `bruges_single_basin_L6` | single basin, L6 (lens fixture, flat; CITYKIN WO1a) |
| `northern_song_961_L6` | polity, Northern Song, 961, L6 |
| `timbuktu_bandT_1236_1240`, `timbuktu_bandT_1300_1400` | single basin, bands T |
| `kyiv_bandT_1236_1240`, `kyiv_bandT_1300_1400` | single basin at Kyiv (L6 basin 2060448220), bands T |
| `timbuktu_public_signature` | `/api/signature`, basin, L6, bands ABCE |

**Comparison rules** (`tests/regionality/baseline.py`, run by `tests/regionality/test_baseline.py`): fields and rows only in the new payload are allowed; a changed or removed field fails, reported by path. Signature rows are matched by (band, variable, year, epoch_year), not by position, so added rows do not shift anything. Numbers match within 1e-6 relative (1e-9 absolute). Reference files are re-captured only at a stage boundary with Karl's approval (`scripts/edop/regionality/capture_baseline.py` refuses to overwrite without `--force`).

**What varies between identical calls** (found by rerunning, not assumed):
- Band T sums differ in the last digits (16 numeric leaves over three reruns of Kyiv 1300 to 1400; none above 1e-9 relative). Handled by the tolerance.
- `meta.generated` (a timestamp, public signature only). Ignored.
- The public signature looks up the point elevation from OpenTopoData, a live external call. The baseline pins that one lookup to the captured value (267.0, mapzen, 30 m) so the test is offline and deterministic.

**Checks that the baseline works.** A perturbed value and a dropped field were both reported; an added GEDA-style row was not. Six unit tests cover these semantics without a database; one more checks that every request has a reference file; ten compare the payloads.

**Test results.** Before any change, the full suite: 643 passed, 21 skipped (all `tests/test_live_server.py`, which needs `EDOPS_LIVE_URL`). After adding Part A: 681 collected; run in parts, 609 passed and 21 skipped with `-m "not ui"`, and 51 passed with `-m ui` (a single run of all 681 was not repeated). The 17 new tests pass.

**Test partitions (added at Karl's request).** `tests/conftest.py` assigns area markers by path: `engine`, `ui` (Playwright), `sandbox`, `cdop`, `regionality`, `dashboard`, `live`, `whg`, `api`. Registered in `pytest.ini`, described in `CLAUDE.md`. Timings: `-m "not ui"` 2 min 20 s; `-m ui` 48 s; `-m engine` 26 s; `-m "whg or regionality or dashboard"` 13 s.

## Part B: where source knowledge lives

Scope, settled with Karl: the registry covers what the signature reads (BasinATLAS, Cliopatria as the polity resolver, LMR, HYDE, eVolv2k, and GEDA once served). Workbench-only data (Ecoregions2017, OneEarth, D-PLACE) is out.

### LMR v2.1 (`temporal.lmr_climate`)

- **Extent and grain.** Global, 16,380 cells at 2 degrees (lat -90 to 90, lon 0 to 358). Arrays of 2,001 values per variable (`pdsi`, `air`, `prate`), position k is year k-1.
- **Years in the data: 0 to 2000.** The raw file's time axis is 2,001 annual steps from year 0 (`days since 0000-01-01`, noleap). All three variables are non-null in all 16,380 cells at years 0, 1997, 1998, 1999 and 2000 (checked in the table).
- **Years as stated: 0 to 1998**, in `engine.py:906` (`_LMR_RANGE`, which clamps Band T at `engine.py:1099-1100`), `app/db/temporal.py:27` (`LMR_MAX`), `:35`, `:42`, `:51`, `:197`, `routes_common.py:51`, `:215-216`, `docsite/data-sources.md:83`, `docsite/api.md:59-60` (generated from `routes_common.py`), `documentation/edops_schema_basin.json:25`, `documentation/edops_schema_area.json:26`, `data/lmr_v2.1/lmr_inventory.md:6` and `documentation/EDOP_summary_v04.md:122`. `EDOP_summary_v04.md:72` says 1-2000. A request for 1995 to 2000 returns LMR years 1995 to 1998.
- **Years recommended or shown: from 700 CE.** The Sandbox map layer cuts off below 700 (`routes_sandbox.py:1291-1299`; `sandbox.html:3674-3676`, `:4284`); the Explorer's "Early reliable" window starts at 700 (`explorer.html:159`, `:529`); `cliopatria.html:933`, `:957`, `:1021`; and the signature carries `lmr_fidelity_note` for spans starting before 700 (`temporal.py:201-203`). Its origin is EDOPS's own EDA (F10.1 and F10.3; see `docs/edop/_v1/rubrics/lmr_quality_border.md`). All agree on 700; each is a separate literal.
- **Units.** Payload: `lmr_pdsi` "dimensionless anomaly", `lmr_air` "K anomaly", `lmr_prate` "mm/day anomaly". Catalog: `lmr_temp_anomaly` K, `lmr_precip_anomaly` mm/day. `lmr_slp` (hPa) is in the catalog as `planned`; the table has no such column.
- **Caveat text.** `CAVEAT_TEXTS['lmr_caveat']` in `engine.py` (anomaly against the 850-1850 CE CCSM4 reference frame; at buffer scale the collapsed value is essentially the prior). In `temporal.py`: `lmr_out_of_range_note`, `lmr_fidelity_note`, `lmr_proxy_bias_note`. Prose in `docsite/data-sources.md:78-95`.
- **Reference frame.** The engine and docsite say 850-1850 CE. Tardif et al. 2019 (in `articles/sources/`) says the CCSM4 simulation used as the prior covers years 850 to 1850 CE; I did not verify that the anomalies are defined against that period's mean. `EDOP_summary_v04.md:72` says deviations from a 1000-1850 CE reference mean, and `:126` describes 1000-1850 as a narrower recommended baseline window set during normalization. Whether these are the same thing is unresolved.
- **Citation and licence.** Tardif et al. 2019, *Climate of the Past* 15, 1251 (doi 10.5194/cp-15-1251-2019), cited in the docsite and `meta.data_sources`. **Licence: not found.** The NOAA study page does not render for a fetch, the data directory states no terms, and the files carry no licence attribute.

### HYDE (`temporal.hyde_cells`, `temporal.hyde_times`)

- **Extent and grain.** Global land, 2,215,829 cells on a 5 arc-minute grid (2160 x 4320; the land mask is identical across the four variables); `cropland`, `grazing`, `pasture`, `rangeland`, km2 per cell.
- **Years: -10000 to 2025**, 128 steps: millennial to 0 (10 intervals), centennial to 1700 (17), decadal to 1950 (25), annual from 1951 to 2025 (75). The 1950 step is the cadence transition the engine flags (`_HYDE_1950_EPOCH_YEAR`, `engine.py:908`; `hyde_caveat`).
- **Years as stated.** 2025 in the table, `docsite/data-sources.md:41`, `docsite/codebook.md:377` and the Sandbox inputs (`min=-10000 max=2025`, `sandbox.html:218-221`, `:345-348`). 2023 in `routes_common.py:53` (`meta.data_sources`) and `EDOP_summary_v04.md:70`.
- **Version: 3.5.** Settled by a byte check. The `urban_area.nc` we hold (101,947,271 bytes, md5 `6450ebdb4669c9930e80b4699662ff5c`) is identical to the file downloaded from the page Karl identified as HYDE 3.5; all seven files share one set of attributes and one creation timestamp, and our source folder is `hyde35_c9_apr2025` (`data/hyde/getcdf.sh`). The files' own attributes say `HYDE3.4` / "HYDE3.4 test netCDF" (created 28 April 2025); that label is stale. Docs, catalog friendly names (for example "Cropland extent (HYDE 3.4)"), `meta.data_sources`, `load_hyde_cells.py` and the codebook all say 3.4.
- **Citation and licence.** The files' `references` attribute cites Klein Goldewijk et al. 2017, *ESSD* 9, 927-953 (the v3.2 paper; in `articles/sources/` as `hyde_Goldewijk-etal_HYDE3.2.pdf`). The 3.5 readme gives: Klein Goldewijk, Beusen, Vander Linden, Doelman 2025, "Holocene anthropogenic land-use reconstructions; HYDE 3.5", *ESSD* (in prep). Licence CC BY 3.0, with the references to be acknowledged (files' `license` attribute; readme). The readme in `data/hyde/` describes the March 2025 release; its cadence text (annual from 2000) and "to 2023" are stale against our files.
- **Caveat text.** `hyde_caveat` and `hyde_nearest_year` in `engine.py`; `HYDE_NOTE` in `app/db/hyde.py`; docsite prose.
- **Grain as stated.** "~10 km" (`routes_common.py:53`); the readme gives about 85 km2 per cell at the equator.

### eVolv2k v4 (`temporal.evolv2k_v4`)

- 256 events, -491 to 1890, global (one value per event year; `unit_type='global'`). Range agrees everywhere it is stated: `engine.py:907` (`_EVOLV_RANGE`), `app/db/temporal.py:26` (`EVOLV2K_MIN/MAX`), `docsite/data-sources.md:129`, the table.
- Units: payload `Tg S` (`engine.py:1186`); catalog `Tg`.
- Citation: Sigl and Toohey 2024, PANGAEA, doi 10.1594/PANGAEA.971968 (the dataset's own title says 500 BCE to 1900 CE). Licence CC BY 4.0, stated in the header of our own `.tab` file.
- Caveat text: `volcanic_events_note` in `temporal.py` (events after 1890 are not in the record).

### Cliopatria (`gaz.clio_polities`)

- 15,690 slices of 1,618 polities, years -3400 to 2024. Used as the polity resolver (`engine.py:163-176`; `routes_cliopatria.py`), not as a band. Polygons are often invalid (use `ST_MakeValid`).
- The docsite lists it under Platform services (`data-sources.md`) with no year range and no licence.
- Citation: Bennett et al. (in `articles/sources/`). Licence: CC BY 4.0 (repo `LICENSE.md`; Zenodo record v0.0.1, August 2024). Which release we hold is not recorded. Seshat's general downloads page says its data is CC BY-NC-SA; that page is about Seshat data generally and conflicts with the Cliopatria licence above.
- Caveat text in code: not traced.

### BasinATLAS (`public.basin06`, `public.basin08`)

- Global, L6 16,397 basins and L8 190,675. Static baseline: "climate normals and contemporary land cover" (`docsite/data-sources.md:21-35`); the Band C note for BCE queries (`routes_common.py:419`) gives WorldClim, about 1970-2000.
- The signature's biome and freshwater-ecoregion variables are BasinATLAS columns. The catalog's `source` is a free label: BasinATLAS v1.0 (71 variables), Derived (13), Derived (WO7) (4), eVolv2k v4 (6), LMR v2.1 (4), HYDE 3.4 (4). Units are per variable in the catalog.
- Nodata sentinel -9999 (masked in analysis). Some attributes are stored scaled by 10 or 100 (the codebook states each).
- Citation: Linke et al. 2019 (doi 10.1038/s41597-019-0300-6), in the docsite. The paper itself is not in `articles/sources/`; the HydroSHEDS and HydroBASINS tech docs are.
- Licence: CC BY 4.0 for the database as a whole; the HydroSHEDS documentation says individual attribute columns may instead be under ODbL 1.0, listed per column in the BasinATLAS catalog. I did not check which of our columns that applies to. Older HydroSHEDS records list other terms (CC BY-NC 3.0 on a Stanford record); the current HydroSHEDS terms govern.

### GEDA (`temporal.geda_climate`, local database only)

- 28,970 cells at 0.5 degrees, 1000 to 2020, JJA scPDSI z-scores; 1990 to 2020 observed (CRU TS 4.06). Not read by the engine. Licence CC BY 4.0; Cook et al. 2024 (doi 10.1175/JCLI-D-23-0773.1), data doi 10.5281/zenodo.11059894. No `meta.data_sources` entry and no caveat text yet. See `reg_wo02_summary.md`.

### The catalog and its relation to sources (item 4 of the revised WO)

- A file only: `documentation/EDOPS_variable_catalog_v0.4.tsv`. No database form exists. It is read independently in `app/db/catalog.py:21`, `app/db/signature.py:32`, `app/api/routes_common.py:474` and `scripts/edop/areas/engine.py:412`, and by the docsite generator.
- Columns that describe the source, not the variable: `source` and, partly, `status`. `friendly_name` is the UI wording; `api_key_s` is the public `/api/signature` key. The `/api/areas` row names (`lmr_air`, `lmr_prate`, `evolv2k_vssi`) are a third set and are not recorded in the catalog; the crosswalk is a separate planned work order.
- Status: 74 `implemented`, 28 `planned`. `lmr_slp` is `planned` ("Not currently stored in temporal.lmr_climate").

### The same fact held in more than one place (item 4 of the revised WO; listed, not resolved)

1. LMR end year: 0-1998 in the places listed above against 0-2000 in the data (and 1-2000 in `EDOP_summary_v04.md:72`).
2. LMR reference baseline: 850-1850 (engine, docsite) against 1000-1850 (`EDOP_summary_v04.md:72`, `:126`); see above.
3. HYDE end year: 2025 against 2023 (`routes_common.py:53`, `EDOP_summary_v04.md:70`). HYDE version: 3.5 in the data against 3.4 everywhere it is stated.
4. eVolv2k units: `Tg S` against `Tg`.
5. Duplicated constants: `_LMR_RANGE` and `LMR_MAX`; `_EVOLV_RANGE` and `EVOLV2K_MIN/MAX`; the 700 CE floor as separate literals in seven places.
6. Two caveat systems: keyed `CAVEAT_TEXTS` in `engine.py` (used by `/api/areas`) and free-text notes in `temporal.py` and `hyde.py` (used by `/api/signature`). The two carry different LMR warnings; the 700 CE fidelity note exists only in the second.
7. `meta.signature_version` is hard-coded `"0.4"` in three places (`routes_common.py:324`, `:366`, `:442`). Consolidating it is a stage-2 item, outside the registry.
8. Licence: stated in the docs only for GEDA.

### Limits of this audit

Not traced: year handling in the JavaScript of the Explorer, Workbench and Cliopatria pages beyond the literals found by search; `app/db/hyde.py` year clamping; per-column units, periods and licences for BasinATLAS; Cliopatria caveat text in code.

## Part C: registry schema proposal (item 6)

The proposal is the draft file `reg_wo03_registry_draft.yaml` (version 2; it parses; nothing reads or loads it). It replaces the field list this section first carried. Stops here for approval (item 7).

**Shape.** A YAML file in the repo, loaded into `temporal.source_registry`, following the variable catalog's pattern. Nine entries: LMR, HYDE, eVolv2k, GEDA, Cliopatria, BasinATLAS, `edops_derived`, OpenTopoData and Open-Meteo (the elevation fallback). Each has two blocks:
- `selects`: read by the code that pulls data. It replaces facts now hard-coded in `engine.py`, `temporal.py`, `hyde.py` and the Sandbox map-layer routes: table, footprint, years covered, how years map to array positions, how time steps are chosen, how cells relate to the query, longitude convention, unit conversions, caveat keys with the condition that triggers them, coverage rule, and the variables the source can supply.
- `describes`: citation, licence, grain, notes. Read by the response's `sources` block, `meta.data_sources`, the docsite and credits text.

**How it was derived: the engine pass.** The code that reads the temporal sources is in four places: `engine.py` (`/api/areas` and the public buffer and area scopes), the public basin path (`temporal.py`, `hyde.py`), the Sandbox map-layer routes (`/hyde/values`, `/lmr/values`), and `routes_cliopatria.py` and `routes_explorer.py`. What it decides about a source:

| Decision | Where today | Registry field |
|---|---|---|
| Clip the span to covered years | engine (LMR, eVolv2k); `temporal.py`; HYDE none | `years_covered` |
| Which time step | HYDE steps in span, else nearest to the midpoint (engine); steps in span only (`hyde.py`); floor-snap (Sandbox layer) | `step_rule` |
| Year to array position | LMR `year+1`, HYDE `step_idx+1`, GEDA `year-999` | `year_to_array_position` |
| How cells relate to the query | engine: area-overlap weights; basin path: nearest cell (LMR), centroid in basin (HYDE) | `spatial` |
| Units and conversions | hard-coded; `prate x 86400` | `variables` |
| Which caveat | LMR always; HYDE at 1950 and when nearest-step is used | `caveats` with `when` |
| Recommended-years floor | 700 CE in the Sandbox layer and the basin-path note; not in the engine's Band T | `years_recommended` |
| Source not covering the request | basin path: `lmr_status: out_of_range` with a note; engine: silent omission | the `sources` block |
| Static data asked about a BCE year | notes for Band C and D in `routes_common.py` | `static_basis_notes` |

Request logic stays in the code: Band T needs a span, buffer and area scopes need a single year, level 6 or 8, scope dispatch. Not read: Explorer routes beyond eVolv2k; `get_signature` for A-E uses no year facts (persist views by level, the live elevation call, seasonality indices).

## Design decisions made with Karl (for Opus)

1. **What the registry judges.** Source availability and handling, identically for the UI and the public API. It does not decide which bands or variables a route returns; that is each route's own specification. Today the two differ: `/api/areas` returns only `coast_fraction` and `outlet_type` among the derived variables; the public basin path returns the seasonality and relief variables and makes the live elevation lookup; the climate-class variables come from the similarity and context endpoints, in neither. A response is the route's specification filtered by the registry's availability decisions, and `variables` in the registry means what a source can supply.
2. **Two blocks per source,** `selects` and `describes`, each with named consumers; no metadata sits in the registry that nothing reads.
3. **Location gate: the source's own cells, no stored shape.** A regional source names its cell geometry (GEDA: `temporal.geda_climate.cell_geom`), and the gate is whether the query geometry (point, buffer or polygon) touches any cell. Measured on GEDA: 0.1 to 0.4 ms for a 100 km buffer (0 cells at Mexico City and Lima, 14 at Reykjavik, 24 at Kyiv). Zero cells means outside the footprint. Global sources are not tested. Measured footprint shapes, for the record: exact union of cells 57.7 million km2 (86 parts); bounding box 111.6; convex hull 109.9; concave hull 71.6 (ratio 0.1). A box or hull was rejected as inaccurate. A display outline, if wanted, is generated from the cells and is not part of the registry.
4. **Coverage rule per source.** GEDA: coverage 0.5 or more is `ok`; 0.1 to 0.5 returns the value flagged `low_coverage`; below 0.1 is `not_applied` with no value. Starting values, tunable. This is a deliberate exception to "serve, don't suppress"; it is defensible because the `sources` block reports it with a reason. Other sources report coverage per row and apply no threshold today. WO-02 context: of 6,630 basins in the footprint, 150 are under 50% covered and 46 under 10%.
5. **A `sources` block in every response,** UI and API alike. `used`: the sources that contributed (BasinATLAS always; Cliopatria when the request resolves a polity; whichever elevation service answered, when the elevation lookup ran; the temporal and regional sources only when Band T is requested and the span and place fall inside what they cover; a source returned at low coverage is `used`, with its rows flagged), each with name, version, citation and licence. `not_applied`: sources the request would have drawn on but could not, with a reason (`outside_span`, `outside_footprint`, `below_coverage_floor`). Sources the request does not ask for appear in neither. The rows are unchanged; the block is additive; the existing `meta.data_sources` and `lmr_status` stay for now. It replaces `meta.data_sources`' habit of listing all five sources whether or not they contributed.
6. **Two sources for the same concept** (GEDA and LMR both give drought indices and disagree): nothing is carried in the signature. The UI explains the meaning and the difference whenever the two appear together.
7. **Derived variables.** BasinATLAS is the default input; only the exceptions are named: `elev_point` (catalog `elevation_point`), `relief_position` and `relief_range_m` also use OpenTopoData.
8. **Scope.** Signature sources only; Workbench-only data stays out.

9. **External services** (OpenTopoData, and Open-Meteo as its fallback) are registry entries only so the `sources` block can credit whichever answered. Their timeouts, caching and fallback logic stay in the route code. The test applied to every field: does the engine, a route or the API need it from the registry?

10. **Payload and catalog names.** The registry keeps both for each variable: the payload name (the `sources` block needs it, because the route reports what it returned) and the catalog key (the registry test and the docs need it). The LMR pairing is inferred from the catalog's `api_key_s`; the real crosswalk is its own work order.

11. **Missing licences.** `licence: null` means "not stated"; the registry never guesses one. The `sources` block passes the null through and the UI shows "licence not stated". A source whose terms are actually "none" says so in words. LMR is the only one today.

**Nothing remains open in the draft.** What is untested is whether these fields are enough for the code to run from the registry; the baseline test is the check (trial plan below).

**For Opus to weigh.** The engine and the public basin path use different spatial methods for the same sources (overlap weights against nearest cell for LMR, against centroid-in-basin for HYDE), different step rules for HYDE, and different not-covered behaviour. The registry does not unify them; stage 2 must decide whether the public basin path moves onto the engine's methods or only consults the registry for availability. The 700 CE recommended floor is applied in the Sandbox layer and the basin-path note, not in the engine's Band T.

## From Opus's review of this draft (2026-11-12)

Opus approves the schema once the small fixes are in; they are applied (the `not_applied` reason `below_coverage_floor`, the elevation services' licences checked, BasinATLAS's table as a list, and the `used` description naming Cliopatria and the elevation service that answered). Opus's decisions, all recorded here:
- GEDA's coverage floor (below 0.1, no value) is a deliberate exception to "serve, don't suppress", defensible because the `sources` block reports it with a reason. Record it in the locked decisions.
- Stage 2: both paths consult the registry for availability only, so the baseline stays identical. Unifying the two spatial methods is a later work order of its own, with a deliberate baseline re-capture. GEDA enters through the engine path first.
- Stage 2 order: pull the inline LMR, HYDE and eVolv2k blocks into their own functions as a pure refactor first, with the baseline passing, before any registry call is wired in.
- The 1998 to 2000 fix goes in as a small standalone change, not inside stage 2.

## Proposed trial (stage 2 shape)

The draft is an educated design: it comes from reading what the code decides (the table in Part C), but nothing has been tried. The baseline test is the check. In Opus's order:

1. The 1998 to 2000 fix, standalone (text and clamp), with the baseline passing.
2. A pure refactor: pull the inline LMR, HYDE and eVolv2k blocks of `aggregate_band_t` into their own functions, baseline passing, no registry yet.
3. A loader for the registry file, and one function that answers, per source, in or out with a reason (span or footprint). Nothing else changes.
4. Call it from the engine to gate the per-source functions, and take the year ranges from the registry in place of `_LMR_RANGE` and `_EVOLV_RANGE`.
5. Add the `sources` block (`used`, `not_applied`) to the payload, additive.
6. The baseline passes at every step; where the registry's answer differs from today's behaviour, a field is missing or wrong.
7. GEDA joins afterwards as a new block (stage 3), through the engine path, with the touch test before its query and the coverage rule after it returns.

The public basin path (`temporal.py`, `hyde.py`) consults the registry for the in-or-out verdict only, later.

## Needs attention going forward

Nothing below was changed in this work order.

**Fixes to make (Karl's decisions so far):**
1. **LMR years 0-1998 to 0-2000 everywhere it is claimed:** `engine.py:906` (the clamp), `app/db/temporal.py` (lines 27, 35, 42, 51, 197), `routes_common.py` (51, 215-216), `docsite/data-sources.md:83`, `docsite/api.md:59-60` (regenerate), `documentation/edops_schema_basin.json:25` and `edops_schema_area.json:26`, `data/lmr_v2.1/lmr_inventory.md:6`, `EDOP_summary_v04.md:122`. Opus: a small standalone change, not part of stage 2. The clamp change makes spans that reach 1999 and 2000 start returning data; no baseline request touches those years. Karl sees no reason for the 1998 clamp. The Explorer's "Industrial (1850-1998)" period (`explorer.html:167`, `:533`; `cliopatria.html:937`, `:957`; `lmr_notches_meta.json:36`) describes a precomputed layer and is a separate question.
2. **HYDE 3.4 to 3.5** in the docsite heading and prose, the catalog friendly names (which the UI shows), `meta.data_sources` (`routes_common.py:53`), the codebook, `load_hyde_cells.py`, and the summary documents. End year 2023 to 2025 (`routes_common.py:53`, `EDOP_summary_v04.md:70`). Cite the in-prep 3.5 paper, with the 2017 paper as lineage. The two HYDE docsite links were already corrected (commit decbccc).
3. **eVolv2k units** `Tg S` against `Tg`.

**To investigate or decide:**
4. **Licences.** LMR: not found. BasinATLAS: which columns, if any, are ODbL 1.0 (share-alike). Cliopatria: which release we hold, and the Seshat NC-SA statement against the CC BY 4.0 in the Cliopatria repo. The elevation services were checked on 2026-11-12: OpenTopoData states no licence (its tiles are a composite of national datasets with per-provider attribution; the public API allows 1 call a second and 1,000 a day); Open-Meteo's data is CC BY 4.0 but its free API is non-commercial only, and its terms page does not name the Elevation API. Whether the live per-signature elevation call stays inside those limits on a public site is worth a look. The docsite states a licence only for GEDA. What the licences mean for downstream use is Karl's judgement.
5. **LMR reference frame:** are 850-1850 (prior period) and 1000-1850 (recommended baseline) the same thing as the anomaly reference?
6. **Missing papers** in `articles/sources/`: eVolv2k (Sigl and Toohey), BasinATLAS (Linke 2019); HYDE 3.5 is in prep.
7. **Cliopatria's docsite entry** has no year range or licence; no entry for GEDA's caveat text or `meta.data_sources` until it is served.

**Structure:**
8. **Two caveat systems** (the engine's keyed texts and `temporal.py`/`hyde.py` free text): GEDA's caveats would have to be written in both, or the two unified.
9. **The catalog is a file read in four places;** a database form is possible if there is a reason.
10. **`meta.signature_version`** hard-coded in three places; Karl's plan ties release numbers to a signature version, 1.0 for February.
11. **At stage 3 the baseline re-captures** because the payload changes on purpose; the comparison already allows additions.
12. **Review deploy of `dashboard`:** the live `cedop` database is shared with v0.4; additive tables are harmless to it, and `geda_climate` and the registry would have to be loaded on the server first.
13. **Catalog vs payload names:** the `/api/areas` row names are not recorded in the catalog; the crosswalk work order is not yet written.

**Done in this work order:** `articles/sources/` created and filled with the signature-source papers (Lovejoy and the Workbench-only papers stay where they were); the two HYDE docsite links corrected and committed.
