# CC work order — Engine assembly WO5: B2 dominant_basin

**Date:** 2026-06-23
**Branch:** new git branch, engine02 after merging engine01 back to main
**Pace:** one agg branch, stop for review.

---

## Why B2 first

It's the simplest branch — three discharge variables, all reading from a single dominant basin, no distribution, no coherence, no modality, no zero-inflation. WO4 already proved `make_row` is contract-faithful; WO5 proves the *other* risk for the first time — lifting a procedural step3 block correctly — on the easiest possible ground. It's also the first work to chain the whole promoted foundation end to end: `resolve_buffer` (WO1) → `attach_values` (WO2) → the branch → `make_row` (WO4). So a clean B2 also confirms the foundation feeds a branch correctly.

**Locked B2 behavior to preserve (regress, don't redesign):** the dominant river is the basin with the highest `discharge_yr` in the buffer set; `discharge_annual`, `discharge_min`, `discharge_max` all read from that one basin; `discharge_min > 0` → perennial, `= 0` → seasonal/intermittent; all discharge units are m³/s. Second-river/confluence detection stays **deferred** (register; needs upstream traversal) — B2 reports only the dominant river.

**Standing rule:** one-directional extraction; the step3 notebook stays frozen; the engine reproduces the frozen TSV.

## Before you start

Read contract §4 (lean envelope) and the WO4 `make_row` signature. Source: the procedural B2 cell(s) in step3. Regression target: the 3 B2 rows in `step3_results.tsv`. Acceptance values from the tracker — dominant basin `hybas_id 1060564960` (Niger main-stem): annual 567.6, min 301.8, max 1089.2 m³/s; min > 0 → perennial.

## Scope — one function

Lift the B2 logic into an engine function (`aggregate_b2` or your naming), fed by the resolved basin set and the attached values (raw discharge from `attach_values`'s raw frame, score from the matrix if B2 carries one). It selects the dominant basin and emits each of the three discharge variables through `make_row` with `method='dominant_basin'`, `unit_type='basin'`, `detail={'dominant_hybas_id': …}`.

Three things to **determine from the frozen output and flag for Karl**, rather than assume:

1. **Score or raw-only** — does a B2 row carry `representative_score` (the dominant basin's discharge percentile) or is it `representative_raw` only with `representative_score=None`? Reproduce whatever the TSV holds; report which.
2. **Perennial/seasonal** — where the `discharge_min > 0` determination currently lives in the B2 output and how it maps into the envelope (a `detail` field, or a flag). Preserve it; report its home.
3. **`n_units` for a single-basin method** — `dominant_basin` reads from one basin out of the set. Report what `n_basins` the frozen TSV carries for B2 (1, the dominant? or 9, the set?), and whether that matches the contract's `n_units` = "units contributing to the headline" semantic. If the TSV says 9 but the value rests on 1, that's a contract refinement — propose and flag, don't silently pick. (This is the first place a non-averaging method stresses `n_units`/`coverage`; better surfaced now than at B3/B4.)

## Acceptance

`aggregate_b2` on the Timbuktu fixture reproduces the 3 B2 rows in `step3_results.tsv` via `diff_output` at **strict** tolerance, now in the `make_row` envelope (`method='dominant_basin'`, `unit_type='basin'`, `dominant_hybas_id` in `detail`, the dominant basin and the three discharge values matching the tracker figures above). Show the lean and full projection of one B2 row.

## Out of scope

- B1, B3, B4, B5, B6 — later WOs.
- second-river/confluence detection — deferred (register).
- the edge-sensitivity and attestation-cloud items — logged in the register, not this WO.
- final engine assembly — after all seven branches emit through `make_row`.

## On completion

Report the regression result, the three flagged determinations (score, perennial, `n_units`), the `aggregate_b2` signature, and confirmation that the procedural lift matched the frozen output exactly. Update the tracker (WO5 done; B2 emits through `make_row`). Stop for Karl's review.
