# LMR quality border (for rubrics and worked examples)

2026-11-11. Decision by Karl: the worked examples and the rubrics expose the data-quality border we already found in LMR, instead of hiding it behind the app's gate. The app does not change.

## The border

LMR is not equally reliable across its 0–1998 CE window. Before about 700 CE the proxy networks are sparse, so the reconstruction regresses toward its model prior: variance is suppressed and the mean stays near zero. The effect grows smaller as proxy density rises.

- **Finding:** `documentation/EDOPS_eda_findings.md`, F10.1 (lines 864–872): the "expanding funnel" in all three variables, 0–500 CE flattest, widening from about 1200 CE. A data-quality signature, not a climate signature. 0–700 CE is the least trustworthy window; 700–1900 CE the most productive.
- **Spread alone does not flag it:** F10.3 (lines 906–910): within-run spread is only about 13% higher early (1.55 vs 1.36 for PDSI), so an explicit epoch caveat is needed beside the spread value.
- **Overlap with HYDE:** F10.1 notes that reliable LMR and meaningful HYDE s/u divergence overlap at roughly 700–1000 CE.

The border is our own EDA result. It is not a cutoff published by the LMR authors.

## How the app treats it today (unchanged)

- Sandbox map layer: starts at 700 CE; below that the UI says so (`sandbox.html:3676`, `:4285`). Set as a quality threshold in the route, not a data boundary (`docs/edop/demo/wo2_findings.md`, D2).
- Signature: reports LMR from 0 CE (`app/db/temporal.py:27`, `LMR_MIN, LMR_MAX = 0, 1998`), with `lmr_fidelity_note` when `year_start < 700` (`temporal.py:200–204`): "Climate reconstructions before 700 CE carry greater uncertainty due to sparser proxy records for this period; treat values as indicative."
- Reconciliation of the two floors: `docs/design/dashboard/sandbox_cheatsheet.md` §5.5 (line 617).

## Plan

- **Worked examples** (starting with Ukraine): pull LMR from 0 CE, and also run a version limited to 700 CE onward. The analysis uses the difference and cites F10.1 and F10.3 as the reason for caution before 700.
- **Rubrics:** state the border as a data-quality condition the rubric can refer to, in the same terms.
- **App:** no change. The map gate and the fidelity note stay as they are.

## Related

- Regional data WO-01 (`docs/edop/_v1/regionality/reg_wo01_GEDA-OWDA-exploration.md`), Q8, looks for the same funnel in GEDA (variance by century, Ukraine and reference cells). Its result can be compared with F10.1.
- Scope: GEDA starts at 1000 CE; Ukraine 700–1000 CE is covered by LMR alone (above the map floor, below GEDA).
