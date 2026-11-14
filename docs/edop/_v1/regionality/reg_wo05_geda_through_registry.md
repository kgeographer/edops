# WO-05 (regionality): GEDA served through the registry (stage 3)

Draft of 2026-11-13.

## Goal

Serve GEDA in Band T on the engine path, as the first regional source, through the registry's location test and coverage rule. The payload changes by addition only. No display work.

## Context

- Stage 2 is closed (WO-04, WO-04a); the reference payloads were re-captured at the boundary.
- GEDA is stored locally (`temporal.geda_climate`, WO-02) and has a registry entry with `status: stored`, a cell-based footprint, years 1000–2020, a coverage rule (ok from 0.5; low_coverage from 0.1; below that not applied) and a year flag for 1990–2020 (observed).
- WO-02 tested the aggregation in a notebook (an adapted copy of the LMR block); its numbers are the regression anchor here.
- Scope: the engine path only (`aggregate_band_t`, reached by `/api/areas` and the public buffer and area routes). The public basin path (`/api/signature`: `signature.py`, `temporal.py`, `hyde.py`) does not get GEDA until the two paths' methods are unified in a later WO.
- Branch: `geda`, cut from `registry`. No merge back is planned in this WO.

## Part 0: confirm the path

1. Confirm which route the Sandbox's Get signature calls, and that it reaches `aggregate_band_t`. If it does not, stop and report before any code.

## Part A: registry and catalog

2. GEDA's registry entry: `status` to `served`; `variables` filled; `caveats` gets the key from item 4.
3. A catalog row for GEDA whose key is the payload name from the start (proposed `geda_scpdsi`), so it joins without a crosswalk. Units: "standard deviations (z-score per cell, 1000–2020 baseline)". Friendly name and description for Karl to word.
4. A caveat in the engine's `CAVEAT_TEXTS` (`geda_caveat`). Draft for Karl to word:
   > Summer (June–August) drought index (scPDSI) from the Great Eurasian Drought Atlas, as standard scores: each 0.5° cell's value relative to its own 1000–2020 record. Values from 1990 are observed, not reconstructed. Reliability is generally lower where and when tree-ring records are sparse.

## Part B: the GEDA function

5. `_band_t_geda(q)`, alongside the other three, called last so existing row order is unchanged. In order:
   - Ask the registry (`check()` in `source_registry.py`), which does the whole judgment, not just the years:
     - Span clipped to 1000–2020; `permitted` respected; outside the span, no query.
     - Location test: the query geometry against `temporal.geda_climate.cell_geom` (replaces the `NotImplementedError` for a `cells` footprint). Zero cells touched: decision `outside_footprint`. Zero cells is a normal case, not an error.
     - Coverage: the share of the query area covered by GEDA cells (as in WO-02), returned on the decision. Apply the registry's coverage rule: below 0.1, `below_coverage_floor`; 0.1 to 0.5, applied and flagged `low_coverage`; 0.5 or more, `ok`.
     - `check()` takes what it needs to run the SQL (a connection and the query geometry); the pure-YAML parts stay testable without the database. Its unit tests (in `test_source_registry.py`) cover the footprint and coverage rules.
   - `_band_t_geda` then only fetches rows for an applied decision; with no rows to fetch it returns the decision alone.
   - Rows, one per year: weighted mean, p10, p90, the weighted histogram (the engine's `_weighted_histogram`), effective cell count and the `low_resolution` flag, as for LMR, plus the coverage share. `unit_type: geda_cell`.
   - Observed years: rows for 1990–2020 carry `observed: true`, read from the registry's year flags, not hard-coded.
   - The caveat key on every row.
6. Parameterized SQL throughout (no values built into the query string).
7. If adding the effective cell count to LMR rows too is a one-line change in the shared histogram path, note it but do not do it here; LMR rows stay as they are.

## Part C: the `sources` block

8. GEDA in `used` when it returns rows (with a note "covers N% of the area" when `low_coverage`), and in `not_applied` with its reason (`outside_span`, `outside_footprint`, `below_coverage_floor`) when the request has Band T and a span but GEDA could not contribute. Not listed when Band T is not requested or GEDA is not permitted.

## Part D: tests

9. Unit tests against the local database:
   - Kyiv basin (2060448220), 1350: values match WO-02 (mean -0.408, p10 -0.567, p90 -0.261; 27 cells, effective 14.25).
   - A place in the Americas (Chaco Canyon): GEDA `not_applied`, `outside_footprint`; no rows.
   - Edge basin 1060044120 (coverage 0.498): rows with `low_coverage`.
   - Basin 1060264990 (coverage 0.067): `not_applied`, `below_coverage_floor`; no rows.
   - Span 500–900: `outside_span`. Span 980–1010: rows for 1000–1010 only.
   - Span 1985–1995: `observed` true from 1990 only.
   - `permitted` excluding GEDA: no rows, GEDA in neither list.
10. Baseline: run the comparison before re-capturing, with additions included (the test's own comparison allows additions, so use a diff that does not). Expected differences, by saved payload:
    - Kyiv Band T 1236–1240 and 1300–1400: GEDA rows added; GEDA in `sources.used`.
    - Timbuktu Band T 1236–1240, 1300–1400, 2010–2020, and the Timbuktu 100 km buffer 1940–1960: GEDA in `sources.not_applied`, expected `outside_footprint` (assumed from WO-02; the diff confirms it).
    - Northern Song Band T 950–970: GEDA in `sources.not_applied`, `outside_span` (the span starts before 1000).
    - No change: the A–E payloads and the public signature (the public basin path does not consult GEDA).
    Anything else: stop and report.
11. New reference payloads: Kyiv 100 km buffer with Band T 1300–1400 (the buffer branch with GEDA); Chaco Canyon single basin with Band T 1300–1400 (outside the footprint); the edge basin with Band T (low coverage).
12. After Karl reviews the diff: re-capture. No `signature_version` change: GEDA lands within "0.5" (the registry-era signature; nothing is deployed at 0.5).

## Part E: docs

13. Docsite GEDA section: from "not yet returned" to served on the engine path (Sandbox and the buffer and area routes), not yet on `/api/signature`. Units, years, the observed years and the coverage rule stated plainly.

## Out of scope

GEDA on the public basin path; display in the Sandbox or Dashboard; loading `geda_climate` on the server; the catalog crosswalk for the existing mismatched keys; any change to LMR, HYDE or eVolv2k rows.

## Deliverables

- Commits by part; the diff for item 12 (for review); new and re-captured references.
- `reg_wo05_results.md` and `reg_wo05_summary.md`, including timings for GEDA queries (single basin, buffer, a polity) and anything odd found.

## Acceptance gate

The tests in Part D pass; the pre-re-capture diff shows only GEDA additions; the full suite passes (zero failures).

## Adjustments after review (2026-11-13, Claude Code, with Karl)

Changed in place above: the branch (`geda` from `registry`, no merge); item 5 (the location test and coverage rule live in `check()`); item 10 (the full list of expected diffs); item 12 (no version bump) and the gate. Also decided:

- Versioning: the earlier "minor bump per additive change" no longer applies before 1.0. 0.5 is the registry-era signature and GEDA is part of it; the number moves to 1.0 at the deploy, when Karl names it.
- Catalog row (item 3): follow the LMR rows' pattern; regenerate the codebook and check the docs' count statements.
- Registry text: `describes.notes` ("Not read by the engine") updated; the GEDA version string changed from "trimmed distribution geda_trim.nc" to wording that cites the Zenodo deposit.
- A test on the public buffer route (single year) that GEDA rows and the `sources` entry come through.
- Check in `sandbox.html` that Band T rows it does not know (GEDA) are ignored; Karl checks the browser.
- Deploy checklist (results): `temporal.geda_climate` is loaded to the server database as the other static datasets are, before code that serves GEDA runs there.
