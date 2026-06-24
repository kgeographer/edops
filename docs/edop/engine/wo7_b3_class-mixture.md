# CC work order — Engine assembly WO7: B3 class_mixture

**Date:** 2026-06-23
**Branch:** 
**Pace:** one branch, stop for review.

---

## Why B3 is different

It's the categorical path — variables that are classes, not numbers (lithology, biome, climate zone, land cover). Three ways it departs from B1/B2: there's no percentile score (`representative_score` is null by nature, like Band T but for a different reason); the headline is the dominant/modal class rather than a number; and it produces a **class mixture** — the percentage breakdown across classes over the weighted basin set. Unlike B2, it aggregates the **whole** set (the mixture tallies every basin), so `n_units` = the full set is honest support, no selection-vs-pool tension here.

This is also where **Pin 1's deferred categorical-coherence value set gets settled**: B3's old `mixed`/`concentrated` status becomes the `coherence` flag, and WO7 confirms the value set is exactly `concentrated` (one class dominates) | `mixed` (no dominant class), plus whatever rule decides between them.

**Locked B3 behavior to preserve (reproduce, don't redesign):** the 9 categorical variables are `lith_class`, `wetland_class`, `zone_name`, `biome`, `eco_id`, `pnv_majority`, `freshwater_ecoregion_class`, `freshwater_ecoregion_name`, `land_cover_name`; `strata_code` is **excluded** (opaque sub-zone codes — register); `ecoregion` is **deduped** into `eco_id` (same db_col). Class percentages are computed across the weighted basin set.

**Standing rule:** one-directional; step3 notebook frozen; engine reproduces the frozen TSV.

## Before you start

Read contract §4, the WO4 `make_row` signature, and Pin 1 (categorical `mixed`/`concentrated` → `coherence` flag; status stays `ok`/`no_data`). Source: the B3 cell(s) in step3. Target: the 9 B3 rows in `step3_results.tsv` plus the B3 portion of `step3_block3_mixture.tsv` (that companion holds both B3 and B4 mixtures — B4's `outlet_type` mixture is WO8, not this one).

## Scope — one function

Lift B3 into an engine function (`aggregate_b3` or your naming), fed by the resolved basin set and the class labels/ids from `attach_values`. Emit each of the 9 categorical variables through `make_row` with `method='class_mixture'`, `unit_type='basin'`, `representative_score=None`, the `coherence` flag, and `detail` carrying the modal summary and the full per-class mixture: `{'modal_class_id':…, 'modal_share':…, 'n_classes':…, 'concentration':…, 'mixture':[{class_id, class_label, weight}, …]}`.

Confirm and flag, rather than assume:

1. **`representative_raw`** — what the frozen TSV puts in the headline for a categorical: the modal class **label**, the `modal_class_id`, or null with the class living only in detail. Reproduce what it holds; report which.
2. **Lean vs detail boundary** — which mixture fields belong in the lean row (likely the modal class + `coherence` + `n_classes`) versus behind `&detail` (the full per-class `mixture`, `modal_share`, `concentration`). Propose and flag.
3. **Categorical coherence rule** — the metric/threshold that decides `concentrated` vs `mixed` (modal-share cutoff? the `concentration` value?), and confirm the value set is exactly `{concentrated, mixed}`, plus whether `no_data` appears for any var in the fixture.

Reproduce the `strata_code` exclusion and `ecoregion`→`eco_id` dedup exactly as the B3 cell does.

## Acceptance

`aggregate_b3` on the Timbuktu fixture reproduces the 9 B3 rows in `step3_results.tsv` and the B3 portion of `step3_block3_mixture.tsv` at **strict** tolerance, in the `make_row` envelope (`method='class_mixture'`, `coherence` ∈ {concentrated, mixed}, the per-class mixture in `detail`). Show lean + full projection for one `concentrated` categorical row and one `mixed` one.

## Out of scope

- **B4 (WO8)** — and note: the synthetics-to-catalog step (`outlet_type`, `coast_fraction` become catalog-resident derived rows) lands **between WO7 and WO8**, per the register, before B4 can key them.
- B5, B6 — later WOs.
- final engine assembly.

## On completion

Report the regression result, the three flagged determinations (`representative_raw`, the lean/detail boundary, the categorical coherence rule and value set), and the `aggregate_b3` signature. Update the tracker (WO7 done; B3 emits through `make_row`; categorical coherence value set settled). Stop for Karl's review.
