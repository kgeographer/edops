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
