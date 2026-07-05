# WO10 — Single-basin live (signature-first)

**Branch:** `surf_wo10` → merge to `surface` at accept gate.
**Type:** Build — live DB wiring for the single-basin scope. No map work.

## Goal

Make single-basin resolve live off the DB: `type=single_basin` on `/api/areas`, the frontend
wired to a live call, Band T verified live. Single-basin joins buffer and polity as a real
scope before it goes on the map. `01_single_basin_detail.json` becomes the equivalence
baseline, not the runtime path.

## Why now

The WO9 audit established single-basin is fixture-only: no route branch, `single_basin_signature`
wired to no HTTP route, example served from `01_single_basin_detail.json`. Every other scope went
signature-first; single-basin skipped it. This WO closes that. The map render is the following WO
and depends on this.

## Build

**1. Route — add `type=single_basin` to `/api/areas`.**
`app/api/routes.py` (the type dispatch ~line 3032 that branches buffer / polity, else 422). Add a
single-basin branch calling engine `single_basin_signature(lat, lon, conn, ...)`. Inputs: lat,
lon (no radius), bands, from_year/to_year (Band T span), detail. Two-pass validation like buffer:
type-params (lat/lon present and in range) first, Band T span second. Serialize the engine payload
**unmodified** — fixtures must not go stale. `/api/area` and the buffer/polity branches untouched.

**2. Frontend — single-basin runs live, not fixture.**
In `sandbox_v2.html`, the sig-button handler's dispatch (buffer→live, polity→live,
else→`loadFixture`) currently drops single-basin into the fixture branch. Add a single-basin live
branch with a `buildSingleBasinUrl()` (mirror `buildBufferUrl`, drop radius) reading the scope's
lat/lon inputs + Band T from/to. The **example** handler should pre-fill the single-basin lat/lon
inputs from the fixture's coordinates and run the live call — so example-then-run reproduces the
fixture live, the way polity's example does (WO6/WO7), rather than loading the fixture.
- If the single-basin scope has no coordinate inputs today (the fixture example never needed them),
  add a lat/lon input group for the scope, mirroring buffer's minus radius. Confirm which case
  held and report it.

**3. Docstring — correct the stale claim.**
`single_basin_signature` in `engine.py` documents Band T as "not yet supported"; the audit (A4.2)
found the code already threads `basin_geom_wkt` + `from_year/to_year` through
`_areal_signature_from_basin_set → aggregate_band_t`. The code is true; the docstring is the lie.
Fix the docstring in this commit. No behavior change.

## Band T — verify live, do not inherit

A4.2 is a code-read, not a live confirmation. Do not take "should work" on trust. As part of the
accept gate, issue a live single-basin call **with a Band T span** and confirm:
- T rows return well-formed — LMR span rows, HYDE epoch rows, eVolv2k events, in the shapes the
  WO5 renderer expects;
- they render through the existing WO5 Band T renderer without modification;
- the currently-inert Band T toggle now threads from_year/to_year into the single-basin live URL.

If any of these fails, it is a finding, not a silent gap — stop and report.

## Accept gate

Two parts:

- **A–E equivalence** — `TestSingleBasinFixtureEquivalence` in `tests/test_areas.py`: load
  `01_single_basin_detail.json`, issue the live call at the fixture's coordinates + same bands +
  `detail=true`, diff variable list, method per variable, band per variable, scores within
  tolerance (0.5 pct, as buffer/polity), neighborhood n_units/unit_type/shape. Single-basin is the
  **n_units = 1** case — expected; the n=1 cross-unit widget suppression is separate deferred
  polish, not in scope here. Route-added metadata keys absent from the fixture are allowed (as with
  polity's `resolver` / `band_t_span`).
- **Band T live smoke** — a live call with a span returns renderable T rows (per the section above).

## Tests

New tests in `tests/test_areas.py`, mirroring WO4 (buffer, 21) / WO6 (polity, 15) scaled to
single-basin: validation (missing / out-of-range lat or lon → 422), payload shape, the equivalence
test, the Band T live check. No changes to buffer/polity tests. Full suite green — zero FAILs, zero
unexplained warnings.

## Constraints

- Review before write — Karl signs off each write.
- `/api/area`, `sandbox.html`, and the buffer/polity paths untouched.
- Engine payload serialized unmodified through the new route.

## Findings

`docs/edop/surface/wo10_findings.md`. Report: which frontend case held (inputs existed vs added);
the Band T live-verification result; the docstring correction.

---

*Numbering assumes the audit took the WO9 slot; adjust the branch / findings names if not.*