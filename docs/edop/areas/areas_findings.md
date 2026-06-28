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

---

## AF.11 [method] — Single-basin is a clean degeneracy limit; the aggregator needs no special-casing at n=1

All six degeneracy properties hold at n=1 without exception: coherence=concentrated on every scored row; modality never two_regime (no regime structure detectable from a single data point); score_suppressed=False everywhere; weight_at_zero∈{0, 1} (binary — the basin is either entirely at zero or it isn't); coverage=1.0 for all ok rows; class_mixture=100%-one-class with modal_share=1.0 and n_classes=1. No special-casing was required — all of these fall out from the general path with n=1 input. The `outside_active_domain` guard fires correctly on `cropland_extent` (zero_fraction≥0.20 and weight_at_zero=1.0 — the whole basin is at the cropland floor); the engine correctly refuses to score it. Minor sequencing artifact: `modality='unimodal'` is still emitted on that row before the domain guard nulls the score — cosmetic, score is correctly null.

*Implication:* The areal engine's n=1 boundary is clean. Single-basin and multi-basin signatures share the same code path; the single-basin is not a degenerate edge case that needs its own handling. This is the intended behavior of the resolver-plus-aggregator architecture.

---

## AF.12 [method] — Zero-aware scorer is a principled improvement over v0.3's naive global percentile; direct score comparison requires accounting for it

For variables with zero_fraction≥0.20 (aridity, dist_sink, pop_density at Timbuktu L06), v0.4 partitions the ranking: zeros score 0.0 explicitly; non-zeros rank within the positive subpopulation via PARTITION BY. v0.3 applied a naive global PERCENT_RANK that included the zero pile, compressing the non-zero range and inflating scores for low-but-positive values. The resulting deltas — aridity 1.48 pp, dist_sink 6.59 pp, pop_density 7.12 pp — are improvements, not regressions. A validation check against the DB must mirror `rank_expr` exactly (with the PARTITION BY and NULLS LAST guard) to serve as a valid oracle; a naive subquery produces these phantom deltas.

*Implication:* Any cross-version comparison of percentile scores for zero-inflated variables must account for the scorer difference. The v0.4 scores are the authoritative ones for these variables. The zero-aware logic is settled and should not be revisited without a principled reason.

---

## AF.13 [method] — HYDE/LMR cell weighting: fractional cell coverage removes latitude-size bias; impact is fixture-dependent

WO14 initially described the engine as doing "boolean inclusion at weight 1.0" for boundary HYDE cells. This was wrong: the engine already computed `ST_Area(ST_Intersection(...))` and used it as the weight; the 80-vs-45 cell count divergence from v0.3 (which used centroid-in-polygon) was correct fractional-overlap inclusion of boundary cells, not a defect. WO15 made a principled refinement: the normalization changed from `overlap_m2/Σoverlap_m2` (weights large cells more even when both are 10% inside) to `overlap_m2/cell_area_m2` (each cell's fractional coverage of its own area), removing a latitude-driven size bias via cos(φ). For equal-size cells at one latitude (LMR at 16°N: Δ<0.001; HYDE at 16°N: <5% relative shifts), the two normalizations are numerically equivalent. The fix matters most at high latitudes or queries spanning large latitude ranges.

*Implication:* HYDE boundary cells carry their true fractional-coverage weight in the distribution (p10/p90/sd); whether that faithfully represents the query area when boundary cells differ sharply from the interior is untested beyond the Timbuktu fixture (see deferred register). `w_eff` (sum of fractional coverages) is now emitted in the HYDE detail block as an honest effective-cell-count.

---

## AF.14 [method] — Border-bearing and centroid-bearing diverge substantially; border-bearing is the honest directional signal

At Timbuktu L06 (5 ring neighbors), the azimuth from the center-basin centroid to the shared-edge midpoint (`border_bearing`) diverges from the azimuth to the neighbor's centroid (`centroid_bearing`) by 0.2°–39.4°, mean 21.0°. Two neighbors differ by more than 30°:

- **1060041510** (24,966 km²): border=5° (nearly due N), centroid=40.7° (NE) — delta 35.7°. The crossing happens along the southern edge of this large basin; its centroid sits far to the NE.
- **1060551770** (10,322 km²): border=91.9° (due E), centroid=131.3° (SE) — delta 39.4°. The basin elongates to the SE, but the shared border is an eastward crossing.

For compact neighbors with small area, centroid and border midpoint nearly coincide (1060550540: delta 0.2°). For large or elongated neighbors the centroid bearing can misclassify the direction of the crossing by a full compass sub-quadrant.

*Implication:* `border_bearing` is the correct directional signal for "in which direction does this variable transition?" The centroid bearing is a convenient proxy only when basin shape is compact; it is retained as a diagnostic column (`centroid_bearing`) but should not drive transition analysis. This validates the design decision in `resolve_basin_ring` to compute bearing to the shared-edge midpoint rather than the neighbor centroid.

---

## AF.15 [signal] — Three distinct transition characters at Timbuktu L06; 29/41 continuous vars cross the sharp threshold

At Timbuktu L06 (5 ring neighbors, border_bearing sorted N→clockwise), the per-variable transition table reveals three structurally distinct patterns:

**All-directional outliers** — center is consistently higher or lower than every ring neighbor regardless of direction:
- `pop_density` all+, n_sharp=4: center basin is a genuine population concentration; all Saharan/Sahelian neighbors rank lower. Interior-city signal, not a boundary.
- `gw_table_depth` all-, n_sharp=4: center has shallower groundwater than all ring neighbors. Niger floodplain proximity makes this basin anomalously accessible; surrounding dryland basins rank higher on depth. Structural, not directional.
- `river_area` all+, n_sharp=2: open water and floodplain area concentrated at center; ring neighbors are drier.

**Directional boundary signals** — mixed sign pattern, high max_abs and moderate-to-high mean_abs: discharge, wetness, aridity, soil texture variables. The center straddles a gradient: crossing eastward (toward the Niger main stem, ~92°) raises discharge and wetness scores; crossing westward or into the Saharan fringe lowers them. `mean_abs` of 20–35 pp confirms real gradients.

**One-direction outliers** — mixed sign, high max_abs but low mean_abs (11–14 pp), n_sharp=1: `wet_pct_*_upstream`, `cropland_extent_upstream`. One neighbor crosses a sharp boundary while the others are similar to the center — likely the large NNE basin (1060041510, 24,966 km²) whose upstream catchment characteristics differ radically from the others.

`reservoir_vol` tops the chart at 89.6 pp max — infrastructure variables have the sharpest spatial gradients because dams are discrete objects, not continuous gradients.

*Implication:* The all-directional outlier pattern (all+/all-) identifies the center as a genuine landscape singularity rather than a boundary location. The mixed pattern is the boundary signature. The two are separable from the sign_pattern and mean_abs columns alone, without knowing geography. This distinction should inform how the basin-ring resolver result is presented: outlier-center signals call for a different narrative than gradient-crossing signals.

---

## AF.16 [signal] — Rome L06 is a hydrological interior-dominant, not a boundary location; contrast with Timbuktu

At Rome L06 (7 ring neighbors), the transition character differs structurally from Timbuktu despite a similar total count of sharp variables (24 vs 29).

**Discharge becomes all-directional:** At Timbuktu, discharge_yr/max/min were mixed (directional gradient toward the Niger, lower toward the Sahara). At Rome all three are **all+, n_sharp=6** — the Tiber basin outranks essentially every ring neighbor on discharge in every direction. Rome sits in the dominant valley; all neighbors are smaller Apennine tributary basins. Not a boundary; the center is a regional hydrological outlier.

**`reservoir_vol` shifts from mixed to all+:** At Timbuktu it was mixed (directional). At Rome it is all+ with mean_abs=74.6 — the highest mean_abs in the table — meaning the Tiber catchment carries substantially more managed water infrastructure than all seven surrounding basins uniformly.

**`karst`/`karst_upstream` appear at Rome and not at Timbuktu:** Geology-specific to the Apennines; Saharan substrates have no karst signal. Both mixed and directional — more toward the limestone Apennines, less toward the coast. A fixture-specific variable surfacing exactly where expected.

**`gw_table_depth` shrinks from structural to marginal:** At Timbuktu: all-, n_sharp=4, mean_abs=22 (strong Niger-floodplain signal). At Rome: mixed, n_sharp=1, mean_abs=5.4 — barely above threshold. Rome's center is not a groundwater singularity.

**`pop_density` drops out entirely:** At Timbuktu it was all+, n_sharp=4 — a city in an uninhabited desert ring. Rome's large basin (17,733 km²) sits among other populous Lazio/Campania basins; no local population outlier signal at L06 scale.

**`river_area` all+ at both fixtures (n_sharp=2):** Both Timbuktu and Rome show the center basin as the highest-floodplain basin in its ring. Candidate generalizable pattern — query points at historically significant settlements tend to land in the water-adjacent basin. To be confirmed at Kaifeng (Yellow River).

*Implication:* The Timbuktu/Rome contrast establishes two named transition archetypes: **boundary location** (mixed gradients in multiple variable groups, center not consistently dominant) vs **interior dominant** (center basin is regional hydrological hub, strong all+ signals in discharge and infrastructure). Both are geographically legible from the transition table without prior knowledge of the fixture. The sign_pattern and mean_abs columns together are sufficient to distinguish them.

---

## AF.17 [signal] — Kaifeng L06 introduces a third archetype (alluvial-plain outlier) and falsifies the river_area all+ hypothesis

At Kaifeng L06 (6 ring neighbors), the transition table reveals a structurally distinct pattern from both Timbuktu and Rome.

**Defining signal — `karst`/`karst_upstream` both all-:** The center scores lower on karst than every single ring neighbor (n_sharp=4 and 6 respectively). Kaifeng sits on the North China Plain alluvial deposit; the ring — Qinling, Taihang, and loess-plateau basins — all have karstified bedrock. The center is geologically the *simplest* basin in its own neighborhood. This is an all-directional structural outlier in the opposite sense from Rome's discharge dominance.

**Discharge is mixed (not all+):** All 6 neighbors differ sharply from center but in both directions. Unlike Rome, Kaifeng's center is not the hydrological dominant — the Yellow River's discharge is distributed across the ring rather than concentrated at center. Rome dominated its neighbors; Kaifeng does not.

**`reservoir_vol` mixed with highest max_abs across all three fixtures (97.0 pp):** Infrastructure is scattered across the ring — major dams sit in the mountain tributary basins upstream; the flat alluvial plain at center has less. The high max_abs reflects extreme ring heterogeneity, not center dominance.

**`river_area` is mixed — falsifies the AF.16 all+ hypothesis:** Both Timbuktu and Rome showed `river_area` all+ (center always the most floodplain-rich in its ring), suggesting a generalizable pattern for historically significant settlements. Kaifeng breaks it. The Yellow River floodplain at L06 is spread across multiple basins; the query point lands in a primarily agricultural-plain basin, not the channel itself. The candidate generalization must be retired or qualified to "some historically significant settlements."

**Sharp variable count: 22 (Kaifeng) vs 24 (Rome) vs 29 (Timbuktu).** The Niger/Sahara seam at Timbuktu is the most environmentally complex neighborhood of the three.

*Implication:* Three archetypes are now distinguishable from the transition table alone:
- **Boundary location** (Timbuktu): mixed gradients in most variable groups; center is not consistently dominant or subordinate; environmental seam sharp in multiple directions.
- **Interior dominant** (Rome): center is the regional hydrological hub; discharge and infrastructure signals are all+ across all or nearly all neighbors.
- **Alluvial-plain outlier** (Kaifeng): center is geologically the simplest basin in its ring (all- karst); discharge is mixed (center neither dominant nor subordinate); infrastructure scattered across upland ring members. The defining signal is substrate, not hydrology.

These archetypes are separable from sign_pattern, mean_abs, and the identity of all+ vs all- variables — no geographic prior knowledge required.

---

## AF.18 [method] — Timbuktu L06→L08 MAUP: 21/29 sharp vars scale-stable; sign patterns shift for pasture, silt, and river_area

Repeating the Timbuktu transition diagnostic at L08 (7 ring neighbors vs 5 at L06) gives the first direct MAUP test for the basin-ring resolver. Sharp-variable threshold = 10 pp throughout.

**Scale-stable core:** 21 of 29 L06 sharp vars remain sharp at L08. Jaccard = 21/30 = 0.70. The boundary-location character of Timbuktu is largely scale-invariant.

**Dissolved at L08 (L06-only, 8 vars):** Local soil texture point vars (`pct_clay`, `pct_sand`, `pct_silt`) and upstream wetness fractions (`wet_pct_grp1/2_upstream`). At L06 the large basin averaged across a soil-heterogeneous area and diverged from neighbors; at L08 the 588 km² center sub-basin is locally homogeneous and the contrast shrinks below threshold. Upstream wetness dissolved because L08 sub-basins have smaller, more similar catchments.

**New at L08 (1 var):** `dist_sink` — the endorheic/exorheic distinction sharpens at fine resolution; the small center sub-basin gets a cleaner drain-path classification than the aggregated L06 basin.

**Sign pattern changes — the substantive MAUP story:**
- `pasture_extent`/`pasture_extent_upstream` → **all-** at L08 (were mixed at L06): the large L06 basin averaged urban and pastoral areas; at L08 the urban Timbuktu core is separated and every ring sub-basin has more pasture. Resolution reveals a settlement/hinterland contrast invisible at L06.
- `pct_silt_upstream` → **all+** at L08 (mixed at L06): the Niger floodplain silt signal concentrates in the center sub-basin at fine resolution; diluted at L06.
- `river_area` → **mixed** at L08 (was all+ at L06): the L06 all+ was an aggregation artifact — the large L06 center basin captured a substantial Niger floodplain slice. At L08 the 588 km² center is one small piece and adjacent sub-basins contain as much channel. This confirms `river_area` all+ is not a reliable property of the center basin; it was a size-of-center-basin effect.
- `pop_density` **strengthens**: all+, n_sharp 4→6. The urban concentration signal gets cleaner at finer resolution, not noisier. Population is not a MAUP artifact at this fixture.
- `gw_table_depth` weakens but remains in sharp list: was all-, n_sharp=4, mean_abs=22 at L06; drops below top-20 at L08 (max_abs ~10–15 pp). Niger floodplain groundwater signal is scale-sensitive.

**Performance:** L08 ring run (center + 7 neighbors) takes ~2.5 minutes. The L08 basin table (190k rows) is ~12× larger than L06 (16k rows); each `single_basin_signature` call is proportionally slower. Any production endpoint using `resolve_basin_ring` at L08 will need query optimization or caching.

---

## AF.19 [method] — Cross-fixture synthesis: 15-variable structural core + extreme bearing divergence at Kaifeng

Cell 20 cross-fixture summary across Timbuktu L06, Rome L06, Kaifeng L06, and Timbuktu L08.

**Kaifeng bearing delta of 119.8° is the extreme case for border_bearing:** One Kaifeng ring neighbor has a shared border in the opposite compass hemisphere from its centroid — likely a highly elongated basin straddling the Qinling or Taihang range, whose centroid sits deep in the mountains while the shared border runs along the piedmont edge with the North China Plain. Using centroid_bearing for that neighbor would assign the transition to the wrong direction by ~120°. This is the strongest single-case argument in the notebook for computing bearing to the shared-edge midpoint rather than the neighbor centroid. All fixtures show non-trivial divergence (mean_delta 13–35°, max_delta 27–120°); Kaifeng's extreme case is not an outlier in kind, only in magnitude.

**15-variable structural core — sharp at all 3 L06 fixtures:**

| Group | Variables |
|---|---|
| Hydrology | discharge_yr, discharge_max, discharge_min, river_area, reservoir_vol |
| Terrain | slope_avg, slope_upstream, elev_max, stream_gradient |
| Water balance | aridity_upstream, gw_table_depth |
| Land use | pasture_extent, pasture_extent_upstream |
| Sediment | pct_silt, pct_silt_upstream |

These 15 variables are heterogeneous at basin boundaries regardless of fixture. They constitute the universal basin-ring diagnostic core — any basin ring will exhibit sharp transitions on most of these regardless of geographic setting.

**10 variables shared by any 2 fixtures** (aridity, cropland_extent_upstream, elev_min, karst, karst_upstream, pct_clay, pct_clay_upstream, pct_sand_upstream, precip_yr_upstream, runoff) are context-modulated: present at basin boundaries in some settings, below threshold in others.

**10 variables appearing at 1 fixture only** encode local environmental character rather than generic basin-boundary heterogeneity: pop_density and wet fractions (Timbuktu — desert-city and Niger Delta); dist_sink (Kaifeng — endorheic/exorheic distinction at fine scale); human_footprint (Timbuktu); pct_sand, cropland_extent (single-fixture). These distinguish *where* you are, not just that you are at a basin boundary.

*Implication:* The structural core (15 vars) is a candidate fixed component of any basin-ring transition report — expected to be informative at any fixture. The fixture-specific group is what makes each location's transition signature distinctive. A transition report that separates "universal boundary heterogeneity" from "local environmental character" variables would be more interpretable than a flat ranked list.
