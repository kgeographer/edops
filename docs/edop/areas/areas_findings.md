# AREAS phase — findings

Coded observations from the aggregation work. Short entries: observation + implication.
Tags: **[method]** aggregation behavior · **[signal]** substantive place content · **[data]** source data properties.

Numbering: AF.n, sequential. Add at the bottom; no retroactive renumbering.

---

## AF.1 [method] — ECC diagnostic routes HYDE and LMR oppositely without hardcoding

At Timbuktu 100 km / L06, HYDE has ECC=393 (426 cells, ~9 km each) and LMR has ECC=3.75 (4 cells, ~222 km each). A single threshold of ECC=10 routes them correctly — HYDE to distribution, LMR to area-weighted collapse — with ~39× headroom above the threshold for HYDE and ~2.7× below for LMR. The routing emerges from the data geometry, not from dataset identity. This matters for future grid sources (e.g. a finer paleoclimate reanalysis) that might fall on the HYDE side even if they are "climate" data.

*Implication:* ECC_THRESHOLD should be calibrated against multiple fixtures and buffer radii before being hardened. Provisional at 10.

---

## AF.2 [method] — LMR at buffer scale is essentially the reanalysis prior

Four 2° cells cover the 100 km Timbuktu buffer; the area-weighted collapse produces a single value whose spatial variation across the cells is small (e.g. PDSI range 0.13–0.28 at year 1150). The caveat that LMR values "reflect the reanalysis prior" bites hardest here: unlike the point signature (which at least picks the nearest cell), the areal collapse averages the prior over the query area, adding no information the reanalysis didn't already have. The result is still useful as a temporal index at that location, but the spatial step adds essentially nothing.

*Implication:* LMR rows in the Band T output carry a mandatory `lmr_caveat` string. The display layer should surface this prominently, especially for queries where the buffer is smaller than a single 2° cell.

---

## AF.3 [data] — HYDE 3.4 has a cadence-transition artifact at the 1950 epoch

The 1950 epoch is the last point in HYDE's centennial/decadal historical reconstruction series before annual data takes over. At Timbuktu, the 1950 grazing mean (27.88 km²/cell) spikes to roughly 1.7× the 1900 value (16.67) then reverts immediately in 1951 (17.03). The artifact is consistent across the four HYDE variables (grazing and rangeland most visible; cropland and pasture near-zero so the spike is proportionally large but tiny in absolute terms). It is not a real land-use signal.

*Implication:* The 1950 epoch row is tagged `hyde_caveat` in the Band T output. Any temporal display of HYDE data should either suppress 1950 or flag it visually. Do not use the 1950 epoch as a baseline reference year.

---

## AF.4 [signal] — HYDE grazing at Timbuktu shows spatial inequality growth, not just expansion

From 1000–1700 CE the area-weighted mean grazing rises ~2× (5.83 → 11.65 km²/cell) while the spread nearly doubles (24.0 → 49.3 km²/cell). **Confidence is split by tail.** The high end (p90 rising from 24.2 → 49.5 km²/cell, absolute values large enough that HYDE's downscaling allocation is well-constrained) is **robust**. The low end (p10 falling from 0.225 → 0.138, all values below 0.25 km²/cell) is **low confidence**: at sub-cell scales HYDE's allocation method can move small fractional values with no real signal, so the apparent fringe-decline reading should not be interpreted without Phase-4 provenance review.

*Implication:* Report the intensification signal (p90, mean) with confidence; treat the abandonment signal (p10) as suggestive only. The spread signal here is societal not environmental — LMR PDSI is flat over the same period. This remains a prototype case for what areal distributions add over a single representative value, but qualified.

---

## AF.5 [signal] — HYDE cropland at Timbuktu shows a late-medieval acceleration

Cropland mean stays near-zero from 1000–1500 CE (0.016–0.023 km²/cell), then roughly doubles by 1600 (0.053) and again by 1700 (0.090), reaching ~1.12 by 2000 — a 70× increase from the medieval baseline. The p10 is permanently zero (many cells, especially in the Saharan fringe, never acquire cropland), so the entire signal is carried by the upper tail (p90 grows from 0.067 to 4.376 km²). The distribution is not diffusing; it is intensifying in an already-active subset of cells.

*Implication:* The 1600 CE uptick coincides broadly with Atlantic trade reorganization in West Africa; whether HYDE is capturing that signal or simply backfilling from later census data is a HYDE provenance question worth raising with domain experts in Phase 4. The pattern (late medieval acceleration, upper-tail-only growth) distinguishes this buffer from one where cropland diffuses uniformly.

---

## AF.6 [method] — Band T and shortfall are not strictly level-invariant

Band T rows (321) are identical at L6 and L8 (max score delta=0): the grid path aggregates over the buffer geometry directly, with no basin resolution involved. Level does not leak into Band T. Shortfall, however, is not invariant: L6=0.0, L8=0.002459 (0.25%). L8 sub-basin polygons leave tiny slivers at their boundaries that fall below the sliver-exclusion threshold; this is a geometry-precision artifact, not geographic absence. The gap is small but systematic.

*Implication:* Band T can be treated as level-invariant by design. Shortfall should be compared across levels with a tolerance of ~0.5%, not as an exact invariant. The shortfall difference can also be used as a diagnostic: if it exceeds ~1% the resolver may have a level-threading bug.

---

## AF.7 [method] — Modality on continuous variables is support-relative; gap magnitude is not evidence of genuine bimodality

At Timbuktu 100 km, 11 of 11 meaningful modality flips go two_regime (L6) → unimodal (L8). Zero reversals. Only dist_sink survives as two_regime at both levels. The seam-alignment check (WO12/WO13) showed 6 of the 11 flippers had perfect or near-perfect endorheic-partition alignment — yet they still dissolved. Gap magnitude also fails as a discriminator: wet_pct_grp1 has an 80.54 pp center-gap (nearly equal to dist_sink's 82.51 pp) and still dissolves, making any absolute floor fit in a 1.97 pp window — not a useful instrument.

The reason dist_sink survives is not that its gap is large or its partition is seam-aligned: it is that its valley is structurally unfillable (a basin either drains to the ocean or it doesn't; no sub-basin takes a middle value). The 11 flippers have large center-gaps because at 9 basins, two piles of an under-sampled gradient can look like two regimes; at 74 basins, the intermediate sub-basins fill the valley and the gap test fails. No L6-computable quantity tested — gap, relative gap, seam-alignment — distinguishes a structural discontinuity from a fillable gradient.

*Closure:* Modality on continuous variables is a support-relative verdict, computed at the queried support and not corrected from coarse data. Coarse-support two_regime is inherently low-confidence and may dissolve at finer support; this is disclosed in the detail field, not fixed. An absolute gap floor is retired as a broken proxy. A proper bimodality statistic (gap normalized by within-regime spread, or a dip test) is the candidate single-level instrument — deferred to multi-fixture calibration (Egypt, Song).

---

## AF.8 [method] — Coherence flips at L8 show no systematic direction

4 coherence flips at Timbuktu L6→L8 (all area_weighted): aridity_upstream and precip_yr_upstream go spread→concentrated; cropland_extent and slope_avg go concentrated→spread. No consistent direction. All other methods (dominant_basin, class_mixture, flag_fraction, extreme, distribution_only) show zero coherence flips.

*Implication:* Coherence is MAUP-sensitive but not MAUP-biased at this fixture: finer support can resolve either more or less spread depending on the variable. L6 coherence verdicts carry uncertainty proportional to their distance from the spread threshold. The non-area_weighted methods are stable across levels.

---

## AF.9 [signal] — Outlet type sub-class structure is only visible at L8

At L6 (9 basins), the Timbuktu buffer shows two outlet classes: exorheic non-coastal (0, 53.5%) and terminal sink (20, 46.5%). At L8 (74 basins), the endorheic fraction splits: endorheic inland (class_id=10, endo=1, 32.3%) + terminal sink (class_id=20, endo=2, 14.3%). Total endorheic weight is stable (~46.6% at both levels). Cross-block consistency holds: endorheic classes sum (0.4659) ≈ dist_sink low-regime weight (0.4671) at both levels.

*Implication:* The internal composition of the endorheic fraction — whether basins drain to a defined inland body (endo=1) or simply terminate (endo=2) — is a geographically meaningful distinction that requires L8 resolution to surface. For the Niger/Sahara seam at Timbuktu, the L6 outlet_type summary is accurate in total but coarse in character.

---

## AF.10 [method] — B2 discharge scores rise at L8; raw values are stable

At L8 the dominant discharge basin has a different hybas_id (finer polygon) but similar raw values (discharge_yr: 567→601 m³/s; discharge_max: 1089→1085; discharge_min: 301→361). Scores increase substantially (discharge_yr: 86→95; discharge_min: 89→96) because the L8 dominant sub-basin aligns more closely with the Niger main stem and ranks higher in the finer L8 percentile population. The perennial verdict (True for discharge_min only) is stable. The Inner Niger Delta / main-stem carrier split (B5 vs B2) persists at L8.

*Implication:* B2 raw values are the reliable cross-level signal; scores reflect the level-specific rank population and should not be compared directly across levels.
