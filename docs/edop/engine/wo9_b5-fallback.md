# CC work order — Engine assembly WO9: B5 fallback + extreme

**Date:** 2026-06-23 · branch off WO8 (`engine09` or your naming) · one branch, two sub-paths. Stop for review.

---

## What B5 is

The fallback branch, with two sub-paths:

- **`distribution_only`** — for continuous variables not yet typed, surface the distribution (spread, p10, p90) rather than a typed verdict. At Timbuktu: `temp_min`, `temp_max` (band C).
- **`extreme`** — for the local-anomaly variable `river_area`, report the max value and the basin carrying it. This is a **third method shape**: not an average (B1), not a mixture (B3/B4), not cumulation-selection (B2 discharge). It selects one basin by extremum, so it follows B2's settled `n_units` convention — `n_units` = the set, the carrier basin id in `detail`.

**Locked B5 behavior (reproduce, don't redesign):** `EXTREME_VARS = ['river_area']` only — `river_area_upstream` is **deferred within B5** and not emitted (register). The four untyped-continuous vars not yet attached in step2 (`elev_point`, `relief_range_m`, `relief_position`, `reservoir_vol`) are **not** handled here — they're unattached (register), so only `temp_min`/`temp_max` take the fallback. Timbuktu `river_area` extreme: carrier basin `1060582960`, 4273 km² — which **differs** from B2's discharge dominant (`1060564960`); that's the Inner Niger Delta splitting biggest-discharge from biggest-river-area, and it's a real finding worth an AF entry if not already logged.

**Standing rule:** one-directional; notebook frozen; engine reproduces the frozen TSV.

## Before you start

Contract §4, the WO4 `make_row` signature, and B2 (the extreme reporter inherits B2's `n_units`/carrier-in-detail convention). Source: the B5 cell(s) in step3 (including Cell 21, `EXTREME_VARS`). Target: the B5 rows in `step3_results.tsv` (`temp_min`, `temp_max`, `river_area`) plus `step3_block5_distribution.tsv`.

## Scope — one function

`aggregate_b5` (your naming), fed by the basin set and `attach_values` output, handling both sub-paths:

- **distribution_only:** emit each untyped continuous var via `make_row` with `method='distribution_only'`, `unit_type='basin'`, `detail={'spread':…, 'p10':…, 'p90':…, 'unit':'percentile'}`.
- **extreme:** emit `river_area` via `make_row` with `method='extreme'`, `unit_type='basin'`, the max value in `representative_raw`, the carrier basin id in `detail`.

Reproduce `EXTREME_VARS=['river_area']` exactly (no `river_area_upstream`); do not handle the four unattached untyped vars.

Confirm and flag:
1. **distribution_only** — does it carry a `coherence` flag, or `coherence=None` (the point of the untyped fallback being that we surface the distribution without rendering a typed verdict)? And is `representative_score` the area-weighted percentile mean or null? Reproduce the frozen behavior; report which.
2. **extreme envelope** — confirm the mapping: `representative_raw` = max value, `representative_score` = carrier's percentile or null, carrier basin id in `detail`, `coherence=None`.

## Acceptance

`aggregate_b5` on the Timbuktu fixture reproduces the B5 rows in `step3_results.tsv` and `step3_block5_distribution.tsv` at **strict** tolerance: the distribution_only vars with their spreads; `river_area` extreme with carrier `1060582960` at 4273 km²; the carrier confirmed distinct from the B2 discharge dominant. Show lean + full projection for one distribution_only row and the extreme row.

## Out of scope

- B6 — WO10 (the post-pass, and where its two deferred decisions come due: preserving the suppressed score value in detail; the modality/score_suppressed fields).
- `river_area_upstream` and the four unattached untyped vars — deferred (register).
- final engine assembly.

## On completion

Report the regression, the two flagged determinations (distribution_only coherence/score; extreme envelope), the `aggregate_b5` signature, and confirmation the extreme/discharge dominant split is preserved. Update the tracker (WO9 done; B5 emits through `make_row`; all primary branches B1–B5 + B7 now through `make_row`, B6 post-pass remaining). Stop for review.
