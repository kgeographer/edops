# CC work order — Engine assembly WO10: B6 modality post-pass

**Date:** 2026-06-24 · branch off WO9 (`engine10` or your naming) · the last branch. Stop for review.

---

## Why B6 is different

It is a **post-pass**, not a primary branch — dispatch never routes to it. It runs over the 36 distribution-bearing rows already emitted by B1 (34 `area_weighted`) and B5 (2 `distribution_only`), and overlays a modality verdict, suppressing the score where a single number would lie. So B6 **closes the three fields WO6 deferred**: `modality`, `score_suppressed`, and the score-nulling on the concentrated-but-bimodal rows.

**Locked B6 behavior (reproduce, don't redesign):** relative-gap test, two_regime when `gap > MODALITY_GAP × spread`, with `MODALITY_GAP = 0.50` and `MIN_REGIME_WEIGHT = 0.20` (provisional — calibration). 12 two_regime across the 36. Sets `modality` on all 36 (`unimodal`/`two_regime`). The 2 that were `concentrated` in B1 (`cropland_extent` 5.29, `temp_yr_upstream` 96.45) get their score nulled; the other 10 two_regime were already `spread`, so B1 already nulled them. Regimes companion: `step3_block6_regimes.tsv`, 24 rows (12 × 2), each regime's id/center/weight. **Reproduce the provisional detection as-is, weak calls included** (`temp_yr_upstream`, `pct_sand`) — do **not** add the absolute-separation floor; that's deferred (register, multi-fixture calibration). The 11/12 seam alignment with B4's endorheic partition is an informative finding, not a computation.

**Standing rule:** one-directional; notebook frozen; engine reproduces the frozen TSV.

## The two register decisions, due now

1. **Suppressed-score value → detail.** This turns out to be faithful reproduction, not a deviation: the frozen TSV already holds the value in its `representative_score_suppressed` column. Map it as — `representative_score` → null; `score_suppressed` (bool, lean) → true where that column is non-null; `detail['suppressed_score']` → the value itself (96.45 / 5.29). The value is preserved (relocated to detail), the boolean is the only additive bit. **No re-freeze needed.** (Resolves the register item; Opus's recommendation.)
2. **The WO6-deferred fields** — `modality`, `score_suppressed`, the score-nulling — are now set by B6, per the mapping above and the amended contract §4.

## The lift hazard — de-closure `detect_modality`

`detect_modality` (step3 Cell 27) is a **closure** — it reads `joined`/`raw_df` from notebook scope and won't port as-is (the inventory flagged this). Parameterize it (the inventory proposed `detect_modality(scores, weights, spread, endorheic_set)`); surface exactly what it consumes from scope, and **confirm whether `endorheic_set` is used in the detection itself or only for the seam-alignment reporting** — report which.

## Before you start

Read the amended contract §4 (`modality ∈ {unimodal, two_regime, null}`, `score_suppressed`, the four null-score reasons) and §6 (regime breakdowns live in `&detail`); WO6 (the deferred fields); and the register (the two decisions, the calibration item, the weak calls). Source: `detect_modality` plus the B6 application logic in step3. Target: the `modality` column across the 36 distribution-bearing rows in `step3_results.tsv`, plus `step3_block6_regimes.tsv` (24 rows).

## Scope — one post-pass function

`apply_modality(rows, …) -> (rows, regimes_companion)` (your naming): take the distribution-bearing rows (B1 `area_weighted` + B5 `distribution_only`), run the de-closured `detect_modality`, and return the rows with `modality` set; on the concentrated-but-bimodal rows, null `representative_score`, set `score_suppressed=True`, and put the withheld value in `detail['suppressed_score']`. Emit each two_regime row's breakdown into `detail['regimes'] = [{id, center, weight}, …]` and as the companion table. It is a post-pass over emitted rows, not a dispatch target.

## Acceptance

Run `aggregate_b1` + `aggregate_b5`, feed their distribution-bearing rows through `apply_modality`, and regress at **strict** tolerance against the frozen final state: `modality` correct on all 36; the 2 concentrated-but-bimodal rows with null score, `score_suppressed=True`, `detail['suppressed_score']` = 96.45 / 5.29; the regimes companion (24 rows) = `step3_block6_regimes.tsv`. This closes the WO6-deferred fields and validates the full B1 → B6 chain. Show lean + full projection for one two_regime row (the preserved suppressed value visible in `detail`).

## Out of scope

- the absolute-separation floor for the detector — deferred (register, calibration).
- modality on the Band T grid path — locked, not extended.
- final engine assembly — next, after WO10.

## On completion

Report the regression, the `detect_modality` de-closure surface (what it consumed from scope), the `endorheic_set` determination, the seam-alignment confirmation (11/12), and the `apply_modality` signature. Update the tracker: **all seven branches now emit/overlay through the unified envelope; the WO6-deferred fields are closed; B6 is the last branch.** Note for the next step: the post-WO10 consistency pass (the one open contract decision — distribution_only coherence, §7) and then final engine assembly. Stop for Karl's review.
