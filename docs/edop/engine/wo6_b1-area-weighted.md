# CC work order — Engine assembly WO6: B1 area_weighted

**Date:** 2026-06-23
**Branch:** off the WO5 result (`engine06` or your naming)
**Pace:** one branch, but the meatiest. Stop for review.

---

## Why B1 is the substantial one

It's the workhorse — most continuous variables route here (continental-gradient and scale-dependent both). It's the first branch carrying all of: area-weighted aggregation over the basin set, the coherence verdict, the spread/p10/p90 distribution detail, zero-inflation (the hurdle path, `weight_at_zero`, the `outside_active_domain` guard), and — the part that needs the most care — an interaction with B6, which is extracted *later* (WO10).

**Locked B1 behavior to preserve (reproduce, don't redesign):** aggregation works on global-percentile scores (0–100); coherence is `concentrated` if weighted (p90 − p10) < T, else `spread`, with **T = 20 provisional**; zero-inflated variables are hurdle-scored (that scoring already happened in `attach_values`' PARTITION variant — B1 consumes those scores); `weight_at_zero` is the buffer weight sitting on zero-valued basins, computed at aggregation time; `status = outside_active_domain` when `weight_at_zero ≥ 0.90` (ZERO_COVERAGE_THRESHOLD). Use the deduped `weighted_quantile` (WO1) for p10/p90.

**Standing rule:** one-directional; step3 notebook frozen; engine reproduces the frozen TSV.

## Field ownership — B1 vs B6 (this is the crux)

The frozen `step3_results.tsv` already carries separate `verdict`, `modality`, and `representative_score_suppressed` columns, plus the overloaded `status`. The final state of a two_regime row is the product of **two** branches, and WO6 extracts only the first:

- **B1 owns** (WO6 must reproduce, strict): `representative_score` (area-weighted percentile mean, **un-suppressed**), `representative_raw`, `coherence` (← frozen `verdict` column, Pin 1), `spread`/`p10`/`p90` (detail, `unit:'percentile'`), `weight_at_zero`, `n_units`, `coverage`, `status` (`ok` | `outside_active_domain`).
- **B6 owns** (deferred to WO10, do **not** expect B1-alone to produce): `modality` (← frozen `modality`), `score_suppressed` (← frozen `representative_score_suppressed`), and the **nulling** of `representative_score` on two_regime rows.

So B1-in-isolation produces, for the ~12 variables the frozen TSV marks `modality='two_regime'`, a `concentrated`/`spread` coherence and a **non-null** score — which is exactly the correct *input* to B6's later post-pass. That's not a regression failure; it's B1 doing its job before B6 refines it.

## Before you start

Read contract §4, the WO4 `make_row` signature, and Pin 1 (coherence is a flag, not a status). Source: the B1 cell(s) in step3. Target: the B1 rows in `step3_results.tsv` (the harness already maps old-schema columns to the new envelope, as in WO4/WO5).
NB contract file is 'Engine response contract — Areas signature payload.md'

## Scope — one function

Lift B1 into an engine function (`aggregate_b1` or your naming), fed by the resolved basin set and `attach_values` output (scores from the matrix, raw from the raw frame, `zero_fraction` from `meta_df` for the hurdle/guard logic). Emit each continuous variable through `make_row` with `method='area_weighted'`, `unit_type='basin'`, the `coherence` flag, `weight_at_zero`, and `detail={'spread':…, 'p10':…, 'p90':…, 'unit':'percentile'}`.

Confirm and flag: whether B1 rows carry `representative_raw` (a native-unit mean) or null — native-unit means were deferred (register), so the frozen TSV may show score-only. Reproduce whatever it holds; report which.

## Regression strategy

1. **All B1-owned fields, all B1 rows, strict** — including `coherence` against the frozen `verdict` column, for the two_regime rows too (B1's verdict is preserved there; B6 didn't overwrite it).
2. **`representative_score`** — strict on rows where frozen `modality ≠ two_regime`. On two_regime rows, confirm B1 produced a non-null mean (the correct B6 input) and **do not** compare it to the frozen null.
3. **`modality`, `score_suppressed`, the score-nulling** — not compared in WO6; they're B6's, validated in WO10.

Report the count of two_regime rows deferred this way and confirm their B1-owned fields all matched.

## Acceptance

`aggregate_b1` on the Timbuktu fixture reproduces every B1-owned field of the frozen B1 rows at **strict** tolerance per the strategy above. Show lean + full projection for one `concentrated` row, one `spread` row, and one `outside_active_domain` row if the fixture has one.

## Out of scope

- B3, B4, B5 — later WOs.
- the B6 post-pass and the three fields it owns — WO10.
- final engine assembly.

## On completion

Report the regression (B1-owned strict pass; the two_regime rows listed as B6-deferred with their B1 fields confirmed), the `representative_raw` determination, the `aggregate_b1` signature, and confirmation that B1's output is the correct input for B6's later refinement. Update the tracker (WO6 done; B1 emits through `make_row`). Stop for Karl's review.
