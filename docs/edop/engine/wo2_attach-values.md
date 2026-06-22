# CC work order — Engine assembly WO2: attach_values

**Date:** 2026-06-21
**Branch:** new branch off the WO1 result (`engine02` or your naming)
**Pace:** one unit, stop for review.

---

## Why this is next

Attachment is the **last contract-independent piece**. It produces the basin values matrix that *feeds* the branches; it does not emit response-envelope rows. So it can be promoted before the response-shape contract is settled — same firewall as WO1. WO2 touches nothing about the envelope, `n_basins`/`n_units`, coverage labels, or the shaper; those wait for the contract.

**Standing rule (already in memory/tracker, restated so we never re-litigate):** extraction is one-directional. Logic moves *out* of the notebooks into `engine.py`; the step2 notebook is **left frozen** as the research record. Any inline duplicate left behind is provenance, not debt. The harness diffs the engine against the frozen TSVs, not against edited notebooks.

## Before you start

Read the step0 inventory and the step2 attachment cells. The source is procedural across **step2 Cells 4–7** — the pass that assembles the score frame (`pos_df`), the class labels and ids (`class_label_df`, `class_id_df`), the raw values, and the flags (`flag_df`). The existing functions to promote alongside it: `_val_expr`, `rank_expr`, `two_pass_sql` (the SQL builders — call this sub-slot **attachment — score SQL builder**), and the small catalog-coercion helpers `_val` / `_zf` if the pass needs them.

## Scope — one function (plus its helpers)

Promote the attachment pass into one importable function in `engine.py`. Inventory's suggested shape, to finalize against the actual code:

`attach_values(basin_set, meta_df, conn, level, table, view) -> (matrix_df, class_id_df, raw_df)`

Return the full attachment bundle the branches will need — position scores, class labels, class ids, raw values, flags — in whatever structure cleanly serves them. **Propose the exact return signature and flag it for Karl**; the three-frame suggestion above is a starting point, not a mandate.

Promote the SQL builders (`_val_expr`, `rank_expr`, `two_pass_sql`) into `engine.py` as the supporting layer and have `attach_values` call them.

### The hazard to surface (this is the real work)

The pass reads state assembled several cells upstream — this is the `detect_modality`-style implicit-input risk, and attachment is where it's most likely to bite. As you extract, **enumerate exactly what the Cells 4–7 code consumes from notebook scope** and make each an explicit parameter or an internal computation. Anything that turns out to be hidden coupling — a frame or constant the pass quietly depended on — call it out in the report rather than absorbing it silently.

### Locked behaviors to preserve (regress, don't redesign)

PERCENT_RANK population hygiene (two-pass SQL excludes −9999/NULL from the ranked population); the zero-aware PARTITION variant for zero-inflated vars; percentiles computed over each variable's defined domain; flags raw (`coast_flag` boolean, `endorheic` 0/1/2); categoricals carried as labels/ids; `gdp_avg`/`human_dev_idx` excluded; scores in global-percentile 0–100 space. `hybas_id` always int64.

## Acceptance

Run `attach_values` on the Timbuktu fixture basin set (from WO1's `resolve_buffer`) and regress with `diff_output` against the step2 attachment-matrix TSV(s) for that fixture — you identify which of the step2 outputs hold the scores/labels/ids/flags. Pass = same rows, same columns, values within float tolerance.

## Out of scope (explicit)

- dispatch — next, and it's still pre-contract.
- the seven branches — post-contract.
- anything about the response shape, envelope fields, `n_units`/`unit_type`, coverage labels, or `make_row`.

## On completion

Report the diff result, your proposed `attach_values` return signature, and any implicit-input surprises the extraction surfaced. Update the tracker (WO2 done) and stop for Karl's review.