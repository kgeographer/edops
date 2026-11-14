# Summary 02: GEDA on the public basin route

Follows WO-06 (`reg_wo06_summary.md`). Record: `reg_wo06_results02.md`. Branch `geda`, pushed (b5759cd, 76c1197, 49ff07e). Nothing merged, nothing deployed.

## What was built

Adding `T` to the bands of `/api/signature?scope=basin` now returns GEDA where the place and years fit what the source provides, as the buffer and area scopes already did. The basin route runs the engine's GEDA block on the containing basin's polygon (the same numbers as the Sandbox's `/api/areas` single-basin call) and returns `signature_bands.T.geda_scpdsi`: a compact year-by-year series (`scpdsi`, `p10`, `p90`, `observed` from 1990) with the status, cell count and coverage, or `{status: "not_applied", reason}` when the place (`outside_footprint`), the span (`outside_span`) or the coverage (`below_coverage_floor`) is outside what GEDA can give. The `sources` block now says the same, instead of staying silent about GEDA. This is the "own GEDA block" option from WO-06; the broader refactor stays on the roadmap.

## What changed in behaviour

- A basin Band T request in Eurasia gains `geda_scpdsi`; elsewhere it reads `not_applied`. A span is accepted (clipped to 1000-2020); no single-year rule.
- `sources` lists GEDA as `used` (with a coverage note when low) or `not_applied`.
- Nothing else changed in the basin response; `signature_version` stays "0.5".

## Test state

Full suite: 768 passed, 21 skipped, no failures. Eleven new route tests (including a year-by-year match with the engine's numbers), three existing `sources` tests updated, two new baseline references for the public basin route's Band T (additions only).

## Open items

- LMR, HYDE and GEDA use different methods in the same basin response (nearest cell, centroid rule, overlap-weighted); unifying Band T on the engine's blocks is a roadmap item.
- Deploy: load `temporal.geda_climate` first; the public basin route now depends on it too.
- `meta.data_sources` does not list GEDA; the Band T guide pages and the area schema JSON do not mention it yet (pre-v1 docs check).
