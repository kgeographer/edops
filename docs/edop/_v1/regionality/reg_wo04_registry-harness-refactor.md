# WO-04 (regionality): registry harness, stage 2

Draft of 2026-11-12.

## Goal

Make the registry real and have the engine path consult it for source availability, without changing what any existing request returns, except for two intended changes: LMR years 1999 and 2000 become available, and every response gains a `sources` block. The refactor this needs is delicate, so the work goes in small steps, each with its own commit and a passing baseline.

## Context

- WO-03 delivered the baseline test (ten reference payloads), the source audit, and the approved schema (`reg_wo03_registry_draft.yaml`, with the fixes agreed afterwards).
- Stage plan: (1) done; (2) this WO; (3) GEDA served through the registry; (4) display, with the Dashboard design.
- Decided for this stage: the engine path consults the registry; the public basin path (`temporal.py`, `hyde.py`) keeps its own methods and is not rewired. Unifying the two paths' spatial methods is a later WO with a deliberate baseline re-capture.
- Branch `registry`; merge to `regionality` on acceptance.

## Ground rules

- One step per commit. The baseline test runs after every commit and must pass.
- If the baseline fails, stop and report. Do not edit reference files or loosen the comparison.
- No reference re-capture in this WO. The `sources` block is an addition, which the comparison already allows.
- No logic changes during the refactor, including known oddities, except the LMR range fix in Part 0.

## Part 0: LMR range fix (standalone)

1. Change LMR's covered years from 0–1998 to 0–2000 everywhere WO-03 listed (the engine clamp, `temporal.py`, `routes_common.py`, docsite, schemas, inventory, summary). Add a test that a span reaching 2000 returns LMR rows for 1999 and 2000. The baseline must still pass (no reference request touches those years).
2. Replace the three hard-coded `"0.4"` signature versions with one constant. Output unchanged.

## Part A: the registry made real (WO-03 items 8 and 9)

3. Final registry YAML in the repo, next to the variable catalog, from the approved draft with the agreed fixes.
4. Loader into `temporal.source_registry` (plain columns: id, status, table names; `selects` and `describes` as jsonb).
5. Registry test (pytest): every source the signature reads has an entry; every named table exists; every catalog variable is claimed by a source; the YAML and the loaded table agree.

Nothing reads the registry yet. Baseline passes.

## Part B: refactor the engine's Band T

6. **Plan first.** Before editing code, write a short refactor plan for `aggregate_band_t`: the current blocks for LMR, HYDE and eVolv2k, the state they share (span clipping, weights, histogram, caveats, row assembly), and the functions they will become, with signatures. **Stop for Karl and Opus to review the plan.**
7. After approval, extract one source per commit: eVolv2k (simplest) first, then LMR, then HYDE. Each extraction moves code without changing it. Baseline passes after each.
8. If the extraction exposes behaviour that looks wrong, record it in the results; do not fix it here.

## Part C: the engine path consults the registry

9. A registry module: load once at startup; one function that answers, for a source and a request (geometry, span), in or out with a reason (`outside_span`, `outside_footprint`, `below_coverage_floor`), and the clipped span. For global sources the footprint test is skipped. GEDA is `status: stored` and is never queried in this stage.
10. In the Band T code from Part B: each source's block asks the registry before querying, and takes its covered years from the registry in place of `_LMR_RANGE` and `_EVOLV_RANGE` (now redundant; remove them). HYDE's step rule and the engine's spatial method stay in code.
11. Baseline passes after each source is switched.

## Part D: the `sources` block

12. Add the `sources` block (`used`, `not_applied`) to every signature response, on both the engine path and the public basin path, as specified in the registry YAML. Entries carry name, version, citation and licence from `describes`; `not_applied` entries carry a reason. On the public basin path the block is computed from what the route returned plus the registry; that path's methods are not changed.
13. `meta.data_sources` and `lmr_status` stay as they are.
14. Tests: the block's content for the ten baseline requests (which sources appear, in which list, with which reason), plus one request with Band T outside LMR's years and one polity request.

## Out of scope

Serving GEDA (stage 3); unifying the two paths' spatial methods; applying the 700 CE floor in the engine; merging the two caveat systems; the catalog-to-payload crosswalk; display changes.

## Deliverables

- Commits as above, each with the baseline passing.
- The refactor plan (item 6), for review.
- `reg_wo04_results.md` and `reg_wo04_summary.md`: what changed, the test record per step, anything odd found during the refactor, and what stage 3 will need.

## Acceptance gate

The baseline passes at the end and after every commit; the registry and `sources` tests pass; the full suite passes (zero failures); `_LMR_RANGE` and `_EVOLV_RANGE` are gone and their values come from the registry.