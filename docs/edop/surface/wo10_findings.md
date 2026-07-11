# WO10 findings

**WO:** wo10_single-basin-live
**Phase:** Surface
**Branch:** surf_wo10

---

## F10.1 — Coordinate inputs: place input already present; no new input group needed

The WO spec asked to confirm whether single-basin had coordinate inputs or whether new ones
were needed. The `v2-point-section` (shared place input + Resolve button) is already shown
for all `POINT_SCOPES` including `single`. No new input group was added.

Current state: coordinates are set via the "Load an example" dropdown (example handler writes
`currentLat`/`currentLon` from the option value). The Resolve button has no handler yet —
manual place-name lookup is future scope. For WO10, single-basin is seeded by the Timbuktu
example. Typing a raw lat,lon into the place input does not work yet (not in scope for this WO).

---

## F10.2 — Band T verified live; polygon path confirmed

The `single_basin_signature` docstring said "Band T not yet supported." Code inspection (WO9
audit A4.2) found this stale — the function already passes `basin_geom_wkt` + `from_year`/
`to_year` through `_areal_signature_from_basin_set` to `aggregate_band_t(geom_wkt=...)`.

Confirmed live: a call with `bands=ABCDET&from_year=1000&to_year=1100` returns well-formed T
rows — LMR time marginals (3 variables × 101 years), HYDE epoch table (4 variables), eVolv2k
event list. The existing WO5 Band T renderer handles them without modification. Docstring
corrected in this commit.

---

## F10.3 — Playwright TestRenderer updated

The four `TestRenderer` Playwright tests were written against the fixture path. With single-basin
now live, they needed two changes:
1. `require_fixture` (checked for the static exemplar file) replaced by `require_db` (hits
   `/api/areas?type=single_basin` and skips if non-200).
2. Each test now calls `load_timbuktu_single()` — selects the Timbuktu example (sets
   `currentLat`/`currentLon`) then clicks Get signature — instead of `select_scope("single")`
   alone. This is an interim pattern; once the Resolve button is wired, tests should use a
   resolved place instead of the example dropdown.

---

## Accept gate

- **A–E equivalence:** `TestSingleBasinFixtureEquivalence` passes — variable list, methods,
  bands, and scores within 0.5 pct all match `01_single_basin_detail.json`.
- **Band T live smoke:** `TestSingleBasinBandT` passes — LMR, HYDE, and eVolv2k variables all
  present with correct structure. Visually confirmed in browser.
- **332 tests pass, 14 skipped, 0 failures.**
