# CC work order — Engine assembly WO8: B4 flag / structural

**Date:** 2026-06-23 · branch off WO7b (`engine08` or your naming) · one branch, stop for review.

---

## What B4 is

The flag/structural branch. It **synthesizes** two outputs from flag inputs — `endorheic` (0/1/2) and `coast_flag` (0/1) — that are themselves *not* emitted as rows (consumed as inputs, per the WO3 output-identity property; now catalog-resident derived rows after WO7b):

- **`outlet_type`** — a 4-class mixture, `method='class_mixture'`. Derived per basin as `endo*10 + coast`, mapping to four non-overlapping classes: exorheic non-coastal (0,0), exorheic coastal (0,1), inland drainage (1,0), terminal sink (2,0). The exclusivity invariant — `coast=1` never co-occurs with `endo>0` — is asserted live; preserve it.
- **`coast_fraction`** — `method='flag_fraction'`, the weighted fraction of basins with `coast_flag=1`.

**Locked / fixture values (reproduce):** Timbuktu — outlet_type exorheic 53.5% / terminal-sink 46.5%, `coast_fraction=0.0` (uniform, inland). Cross-block consistency: the endorheic fraction (endo>0 classes summed = 0.4654) equals `dist_sink_km`'s `weight_at_zero` from B1 (~0.47) — confirm this still holds, it's a real sanity check across branches.

**Standing rule:** one-directional; notebook frozen; engine reproduces the frozen TSV.

## Before you start

Contract §4, the WO4 `make_row` signature, and WO7b — since `outlet_type` is a `class_mixture`, it follows the WO7b convention (modal class label in `representative_raw`, the rest in `detail`); reuse B3's mixture aggregation if it's factored to allow it. Source: the B4 cell(s) in step3. Target: the 2 B4 rows in `step3_results.tsv` plus the B4 (outlet_type 4-class) portion of `step3_block3_mixture.tsv`.

## Scope — one function

`aggregate_b4` (your naming), fed by the basin set and the raw `endorheic`/`coast_flag` values from `attach_values`:

- synthesize the per-basin outlet class, assert exclusivity, tally the weighted 4-class mixture, emit `outlet_type` via `make_row` (`method='class_mixture'`, `unit_type='basin'`, `representative_raw` = modal class label per WO7b, `coherence`, `detail` = modal summary + 4-class mixture);
- compute `coast_fraction`, emit via `make_row` (`method='flag_fraction'`, `unit_type='basin'`);
- `endorheic` and `coast_flag` are **not** emitted standalone.

Confirm and flag: whether `coast_fraction` carries a `coherence` flag or `coherence=None` (its old status was `uniform` → `ok`), and what its `representative_raw`/`representative_score` hold.

## Acceptance

`aggregate_b4` on the Timbuktu fixture reproduces the 2 B4 rows and the outlet_type 4-class mixture at **strict** tolerance: outlet_type modal label in `representative_raw`, `coherence='mixed'` (modal_share 0.535 < 0.85), 4-class mixture in `detail`; `coast_fraction=0.0`; exclusivity assertion holds; endorheic-fraction = dist_sink `weight_at_zero` confirmed. Show lean + full projection for both rows.

## Out of scope

B5, B6, final assembly. `endorheic`/`coast_flag` standalone emission (deliberately none).

## On completion

Report the regression, the `coast_fraction` determination, the cross-block consistency check, and the `aggregate_b4` signature. Update the tracker (WO8 done; B4 emits through `make_row`; synthetics now catalog-resident and emitting). Stop for review. WO9 (B5) next.
