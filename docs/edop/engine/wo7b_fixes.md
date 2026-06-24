# CC work order — WO7b: B3 label fix, derived catalog rows, register line

**Date:** 2026-06-23 · branch off WO7 · three small items, one pass, stop for review.

---

### 1. B3 modal label → lean row
In `aggregate_b3`, move the modal class label from `detail` into `representative_raw` (lean). Keep everything else in `detail` (modal_class_id, modal_share, n_classes, concentration, mixture). Re-regress. This diverges from the frozen NaN deliberately (same pattern as the LMR caveat / perennial flag), so **re-freeze the 9 B3 rows** of `step3_results.tsv` — prove the only delta is `representative_raw` on those 9 rows, nothing else. **Karl signs off the re-freeze before commit.**

### 2. Derived catalog rows
First confirm the catalog already contains `derived`-marked rows and that the step2 attachment pass and WO3 dispatch coverage check already handle them — so two more behave identically. Then add `outlet_type` and `coast_fraction` as derived rows, provenance in `notes` (outlet_type from `endorheic` × `coast_flag`; coast_fraction from `coast_flag`). Karl reviews the exact rows; write with backup. Try to confirm that adding derived rows (any rows really) does not break instancees of row counts in the code

### 3. Register line
In the deferred register's "Multi-fixture calibration" row, append `plurality_threshold = 0.85` (B3 concentrated-vs-mixed cutoff) to the existing provisional-threshold list (T=20, MODALITY_GAP, MIN_REGIME_WEIGHT, ECC=10, L6/L8 policy).

---

On completion: report the B3 re-freeze diff, the derived-rows check result + the two rows as written, and confirm the register line. Update tracker. Stop. WO8 (B4) is next.