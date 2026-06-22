# CC Work Order — Areas Step 3, Block 6: Modality refinement (general; suppress two-regime)

Branch: areas_step3. Fixture: Timbuktu 100 km / L06. A terminal pass that refines the
coherence verdict for every distribution-bearing row by detecting distribution *shape*, and
suppresses the representative mean where the area is two-regime.

## Scope + ordering
- Runs AFTER Blocks 1 and 5. Block 6 is the **last word on coherence** for distribution-bearing
  rows — it may overwrite representative_score/verdict that those blocks set.
- Applies to rows with method in {area_weighted (Block 1), distribution_only (Block 5)}.
  Excludes Block 2 (single value), Block 3 / Block 4 (class mixtures — "modality" there is
  n_classes, a different sense), and river_area (extreme, single basin).
- No early-cell impact: reads per-basin weighted scores from the Cell-2 matrix (already
  loaded) and the existing step3_results rows. No new attachment, no dispatch change, Cells
  1–4 untouched.
- Note on legitimacy for untyped vars: modality is a *descriptive* property of the value
  distribution ("do the scores cluster into two groups"), not a spatial-model assumption — so
  running it on Block 5's untyped rows is sound. If an untyped variable is two-regime,
  suppressing its provisional flagged mean only tightens the honesty already intended there.

## Safety (Block 6 is the first mutating block)
Cell A — PROPOSE (no writes): detect modality from the Cell-2 matrix; print the change diff —
per affected row: current verdict / representative_score → proposed modality / null, with
evidence (gap, regime weights, regime centers) — plus a summary count. Re-runnable: tune
MODALITY_GAP / MIN_REGIME_WEIGHT and rerun until calls are right. Detection is from the matrix,
so reruns don't compound.

Cell B — WRITE (gated, only after the diff is reviewed):
  1. snapshot step3_results.tsv → step3_results.<date>.bak
  2. add `modality` column to the table (null on non-distribution rows)
  3. two_regime rows: set representative_score = null AND preserve the original mean
     (representative_score_suppressed column, or in step3_block6_regimes.tsv) — reversible,
     not destroyed
  4. write step3_results.tsv + step3_block6_regimes.tsv
Recovery: restore the .bak.


## Detector
Per variable, on the sorted weighted per-basin scores (score space; native deferred):
- **two_regime** iff there is an internal gap > `MODALITY_GAP` (provisional — start relative,
  e.g. gap > 0.5 × (p90 − p10); set by eye like T) AND each side carries ≥ `MIN_REGIME_WEIGHT`
  (provisional, e.g. 0.20) so a lone outlier basin can't manufacture a regime.
- otherwise **unimodal**, sub-labelled `concentrated` (was Block-1 concentrated / tight) or
  `broad` (spread but single-humped).
- Start with this gap heuristic (fine for ~9-basin buffers). Note Hartigan's dip test as the
  scale-up path for many-basin polities, and >2-regime splitting as deferred — split at the
  single qualifying gap for now.
- `MODALITY_GAP` and `MIN_REGIME_WEIGHT` are provisional, calibrate against Egypt + Song
  alongside T.


## Refinement (suppress)
- unimodal → leave representative_score unchanged; set `modality` = `concentrated` | `broad`.
- two_regime → set `representative_score = null`; set `modality` = `two_regime`; emit the
  regimes to a companion. representative_raw stays null. This is the "don't report a mean that
  names the empty gap" rule, and Block 6 owns the overwrite for these rows.

## Output
- step3_results.tsv: add `modality` detail column to distribution-bearing rows; null
  representative_score for two_regime; status reflects two_regime where applicable.
- companion step3_block6_regimes.tsv: `(variable, regime_id, regime_center, regime_weight,
  n_basins)` for two_regime variables — regime_center = weighted mean of member scores;
  regime_weight sums (with the variable's coverage) to 1.0. Parallel to the mixture /
  distribution companions.

## Validate (print, no writes)
- Timbuktu is a known two-regime fixture (Niger corridor vs desert), so expect at least some
  distribution-bearing vars flagged two_regime. The strong cross-check: a two_regime
  variable's regime membership should fall along the same seam as the Block-4 endorheic split
  (the 0.4654 / 0.5346 partition) — if the basins sort the same way, that's the Niger/desert
  boundary detected yet again, now in a continuous variable's shape. Note matches; don't force.
- Concentrated vars (e.g. zone-driven) must come back unimodal.
- representative_score is null on every two_regime row; `modality` present on every
  distribution-bearing row; regimes + coverage reconcile.
- Block 2 / 3 / 4 rows unchanged.

## Write (gated)
Update step3_results.tsv; write step3_block6_regimes.tsv.

## Done =
Every distribution-bearing row carries a modality label; two_regime rows suppress the mean and
carry their regimes in the companion; Timbuktu's duality surfaces where expected and ideally
along the known seam; nothing upstream of the verdict moved.
