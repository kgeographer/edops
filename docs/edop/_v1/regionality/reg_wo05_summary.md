# WO-05 summary: GEDA served through the registry (stage 3)

Spec: `reg_wo05_geda_through_registry.md`. Record: `reg_wo05_results.md` (parts, timings, 10 "needs attention" items). Branch `geda`, cut from `registry` (pushed to origin). Nothing merged, nothing deployed.

## What was built

GEDA, the first regional (non-global) source, is served in Band T on the engine path (the Sandbox's `/api/areas`, and the public `scope=buffer` and `scope=area` routes), through the registry. The registry's `check()` now judges a regional source: years, whether any of GEDA's cells lie under the query geometry, and a coverage rule (under 10% not applied; 10 to 50% applied with a `low_coverage` status). GEDA rows read like LMR rows: one per year (1000-2020), a weighted mean with the distribution of the cells' values in `detail`. The `sources` block lists GEDA as `used` (with a coverage note when low) or `not_applied` with a reason (`outside_span`, `outside_footprint`, `below_coverage_floor`).

## What changed in behaviour

- Band T on the engine path gains `geda_scpdsi` rows for places in Eurasia; elsewhere GEDA is `not_applied`. Existing rows (HYDE, LMR, eVolv2k, A-E) are unchanged.
- `geda_scpdsi` has a catalog row; `geda_caveat` and `geda_observed` (1990 onward) are in `CAVEAT_TEXTS`.
- `signature_version` stays "0.5": GEDA lands within the registry-era signature.
- Not changed: the public basin path (`/api/signature?scope=basin`), the Sandbox display (GEDA rows are ignored; the Band T badge counts them), HYDE, LMR and eVolv2k.

## Test state

- Regression anchors from WO-02 reproduce (Kyiv basin 1350: mean -0.408, p10 -0.567, p90 -0.261, 27 cells, effective 14.25).
- New tests: footprint and coverage rules (13), the GEDA block (12), the `sources` block through the real routes (7), plus year-caveat unit tests. Existing tests were updated for a fourth source.
- Baseline: pre-re-capture diff showed only the `sources` lists, GEDA rows and the GEDA caveat; re-captured once (13 references updated, 3 added).
- **Full suite after the re-capture (2026-11-14): 755 passed, 21 skipped, no failures.**
- Timings: 0.01 to 0.05 s for a basin or a 100 km buffer; up to 0.8 s for a 1000 km buffer over the full 1000-2020 span (results file).

## Open items

See the results file. Most relevant:

- What the Band T headline should be (item 1): a display decision, changing LMR, HYDE and GEDA together.
- Deploy: load `temporal.geda_climate` to the server database first (item 2).
- SQL built from polygon text in the existing Band T blocks and the public `scope=area` route (item 4).
- GEDA on the public basin path waits for the path unification (item 5).
- Pre-v1 docs check: HYDE 3.4 mentions, `sources` in the schemas and API guide (item 9).

## Registry status

With GEDA through the registry, the harness is implemented on the engine path: availability by span and footprint, a coverage rule, the permitted-sources option and the `sources` block. Still ahead: the catalog-completeness work order, unifying the public basin path with the engine path, GEDA's display, and the 1.0 deploy.
