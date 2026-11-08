# WO-08 results (running file)

2026-11-08. One section per numbered item of `wo08_wo07-decisions-new-units-coastline.md`, added as each closes. Template: `profile_templates.md` (version 11 so far). Code: `scripts/edop/whg/` (`missing.py` and `wo08_units.py` new; notebook `notebooks/edop/whg/wo08_new_units.ipynb`; `wo04_fill.py`, `wo06_rings.py`, `wo07_classes.py` changed). Items still to do are listed at the end.

## Decisions taken in discussion before the build (Karl, 8 Nov)

- **A2** is a gate only (no new wording). Zone choice: see A2.
- **A5**: Wikidata coordinates are meaningless for rivers, so they are not tested; OpenStreetMap is explored as a last attempt, time-boxed.
- **B1**: the sentence states the Seasonality tab's concentration class and the peak month, with no new "between July and September" window rule. The payload for WHG should carry the twelve monthly precipitation and temperature values so WHG can draw its own chart (the Sandbox chart reads `pre_mm_monthly` and `tmp_dc_monthly`); noted for the `/whgmodal` payload design.

## A1. Date the land cover

- **Cropland and pasture:** EarthStat, Ramankutty et al. 2008, "circa 2000" and "in the year 2000" (BasinATLAS provider pages L08 and L09, `app/static/basinatlas_pages/`). **Land cover classes:** GLC2000 (satellite year 2000; `wo04_schemes.md`). All three sources are about 2000, so one date serves them and none needs to be stated separately.
- Template: `S5.title: Land cover around 2000`; `S5.frame: Around 2000, {S5.1a} and {S5.1b}; {S5.1c}. {S5.2}`.

## A2. No UNEP aridity sentence in cold climate zones

- **First reading of the WO did not work.** Utqiagvik's GEnS zone is 6, "Extremely cold and mesic", not Arctic 1 or 2, so a rule on the Arctic zones alone would not have silenced it.
- **First build used zones 1 to 7 and was wrong:** zone 7 is "Cold and mesic", which includes Tbilisi (a hot summer; its "0.93, humid" is true and harmless). Karl: the threshold was off.
- **Final rule:** silent in zones **1, 2, 3, 4 and 6** (Arctic 1 and 2, Extremely cold and wet 1 and 2, Extremely cold and mesic: the zones the GEnS itself names Arctic or Extremely cold). Zones 5 ("Cold and wet") and 7 are left alone. The rule is in `wo07_classes.COLD_ZONES`; no wording change.
- **UNEP class by zone, all basins with an index** (what the sentence would have said):

| GEnS zone | Basins | humid | other classes |
|---|---|---|---|
| 1 Arctic 1 | 57 | 57 | none |
| 2 Arctic 2 | 95 | 95 | none |
| 3 Extremely cold and wet 1 | 47 | 47 | none |
| 4 Extremely cold and wet 2 | 127 | 127 | none |
| 5 Cold and wet | 131 | 131 | none |
| 6 Extremely cold and mesic | 1,953 | 1,507 | 47 arid, 174 semi-arid, 225 dry sub-humid |
| 7 Cold and mesic | 1,983 | 1,551 | 2 hyper-arid, 18 arid, 99 semi-arid, 313 dry sub-humid |

- **Affected:** 2,279 of 16,397 basins (14%). Of the 306 sample basins, 85 (17 in each of zones 1 to 4 and 6; the sample takes 17 per climate zone, so its share overstates the world's); 83 of them would have said "humid", 2 "semi-arid". **Of the ten places only Utqiagvik** is silenced.
- **Observation:** zones 1 to 5 are humid throughout, so the gate removes true, harmless sentences there; the misleading classes are in zones 6 and 7 (zone 7 left alone: its dry classes include genuine steppe).

## A3. Slopes under 0.1%

New key `S4.1a.under`: "level on average (a mean slope under 0.1%)" where the slope is under 0.1% (only a stored slope of 0.0 degrees; storage is 0.1 degree, about 0.17%). Kaifeng reads this way.

## A4. Missing values

**Finding.** The engine marks a source -9999 as a `no_data` status on the row. The public signature, which the profile scripts mostly read through `sigval`, passes the marker through, sometimes scaled (slope -999.9). A negative number cannot be treated as missing in general: temperatures are legitimately negative.

**Rule, now in `scripts/edop/whg/missing.py` (one place):** a signature value is missing when the engine's row for it says `no_data` (`W.val`); a value read straight from `public.basin06` is missing at -9999 (`missing.clean`, `is_missing`); a class code is missing at the marker (`class_label`). Four unit tests (`tests/test_whg_missing.py`).

**Audit.**

- **`basin06`:** 27 of 298 numeric columns carry -9999 somewhere. Those the profile reads or could read: slope (302 basins, local and upstream), stream gradient (412), sand, silt, clay and soil carbon (757 local, 668 upstream), wetland class (2,623), climate moisture index (7), snow cover (5 columns, 5 basins).
- **Direct reads in the scripts:** `wo06_rings.py` (`ele_mt_sav`, `for_pc_sse`: already tested, now through the helper); `wo07_classes.py` (`glc_pc_s*`, now cleaned; my first Part B draft used a "negative means missing" test, replaced by the engine's status); `wo04_fill.py` (`sub_area`, `up_area`: no sentinel in those columns); `wo07_rivers.py` (reads no basin values).
- **Ring table (`wo06_ring_values.csv`):** 72,913 ok, 14,344 outside active domain, 3,649 no_data rows; the no_data rows carry no value and no value is below -900. The ring sentences were never affected.
- **Units that have shown a missing value as data in committed output: none.** The only leak was my first, uncommitted draft of Part B on the Greenland ice basins ("very steep (573%)", an invented soil mix), caught on a test before the commit.

**Verification.** All 103 sample basins that carry the marker in a used or neighbouring column were filled and rendered: no rendered profile contains -9999, -999.9 or -99.99, and nothing errored. S4.1a: placeholder at 60 (exactly the basins with no slope), text at 43. S4.1b: placeholder at 53 (exactly those with no soil), text at 50. S4.3: silent at 33, speaks at 70. S2.4 and S5.1c: text at all 103. The ten places regenerate **identically** (351 lines, no difference).

**I-3 (the marker stored as a class).** The class-id frame that carried it is in the WO-03 Q1 research notebook (frozen as a record). No live profile script builds such a frame; the wetland class is not read. The fix for any use from here is `missing.class_label`, tested.

**Not covered:** the check ran over the 103 sample basins, not over all 16,397; columns with the marker that the profile does not read (stream gradient, soil carbon, moisture index, snow cover) are not guarded and will need the helper when a unit first reads them.

## A6. Counts for every measure that qualifies

**Design.** After the extremes sentence (unchanged), every other measure that stands out is stated: "all but one" of the neighbours, or more than half (Karl's floor, `2k > m`). One such measure alone keeps its own sentence (`S2.3.count`, `S2.3.allbutone` and the like, as approved). **Two or more** go in one sentence, `S2.3.counts` or `S5.2.counts`: "Compared with the nine basins around it, its basin receives more precipitation than six, is cooler than seven and is more humid than six." "All but one" appears in the list as "all but one". An extreme is never repeated in the list. Removing the `counts` lines returns S2.3 and S5.2 to one measure per sentence. A measure that is not more than half is kept in the fill note as `not stated`.

**Forest moves from S6.5 to S5.2** (the WO lists forest in S5.2's counts; keeping it in S6.5 as well would state it twice). New `cmp.forest.more` and `cmp.forest.less`. The S6.5 rates over the sample have not been re-measured.

**Rates, over the 287 basins in the ring table with three or more neighbours:**

| Unit | Speaks | one measure | extreme only | extreme + another | counts list (two or more) | silent |
|---|---|---|---|---|---|---|
| S2.3 | 271 | 26 (25 count, 1 all but one) | 21 | 17 | 207 (184 + 23 after an extreme) | 16 (not more than half) |
| S5.2 | 198 | 46 (32 count, 14 all but one) | 31 | 21 | 100 (85 + 15 after an extreme) | 89 (18 not more than half, 71 no measure with data distinguishes the basin) |

The "extreme + another" column counts basins that have an extreme and also a single other measure; those that have an extreme and a counts list are in the counts column.

**Observation.** Precipitation and aridity often qualify together ("receives less precipitation than five … and is more arid than five"); they are different facts, but a reader may find the pair repetitive. For the stakeholders.

## B1. S2.1b, when the rain falls

**Rule.** The Seasonality tab's four classes on precipitation concentration, with its own cutoffs (0.15, 0.35, 0.60; `sandbox.html`, `renderSeasonality`), reused unchanged: **even** (under 0.15), **moderate**, **clear**, **strong** (0.60 and over). The three uneven classes name the **wettest month**; "even" names none. Wording (template v10, slot in "rainfall averages about {S2.1a} mm a year, {S2.1b}"): "spread fairly evenly through the year"; "moderately seasonal, with {month} the wettest month"; "clearly seasonal, ..."; "strongly concentrated, ...". No new cutoff and no new rule.

**Differences from the WO (Karl's decisions, 8 Nov).** No "between {m1} and {m2}" window and no two-season class (`S2.1b.season`, `.spread`, `.two` are not used); the payload for WHG should carry the twelve monthly precipitation and temperature values so WHG can draw its own chart.

**Wettest month, not the tab's "peak month".** The tab's peak month is the direction of the circular mean of the monthly weights, not the wettest month. Over the 306 sample basins, where a month would be named (202 basins), the two differ by one month or more at 44 of 81 moderate, 44 of 75 clear and 20 of 46 strong basins, and by two months or more at 26 of 202 (for example circular peak July, wettest month September). A sentence "peaking in July" beside a WHG chart whose tallest bar is September would read as a contradiction, so the sentence uses the wettest month (a plain fact; the first month where two tie). **This departs from the Sandbox tab, which says "peaks in" the circular month;** switching is one line in `wo08_units.fill_season_unit`.

**Rates over the 306 sample basins:** even 103, moderate 81, clear 75, strong 46, no monthly precipitation 1 (placeholder).

**At the ten places:** Timbuktu "strongly concentrated, with August the wettest month" (the WO expected July to September); Tbilisi moderately seasonal, May; Santa Fe moderately seasonal, August; Kaifeng clearly seasonal, July (198 mm, as in the Sandbox chart); Lviv moderately seasonal, July; Poltava even; Chaco Canyon moderately seasonal, August; Alexandria strongly concentrated, December; Utqiagvik clearly seasonal, August.

**Observation.** The concentration class and the wettest month describe one rainy season; a basin with two (a bimodal regime) reads as "moderately seasonal" with one month named. The monthly values in the payload would show the second.

## B2. S3.4, lakes and wetlands

**Sources, from the provider's own pages** (`app/static/basinatlas_pages/H04.pdf`, `L06.pdf`):

- **Lakes:** `lka_pc_sse`, HydroLAKES limnicity (Messager et al. 2016; lakes and reservoirs of at least 10 ha). **Stored multiplied by 10** (a stored 10 means 1%), so the script divides by 10. In `basin06` but in no payload, so it is read directly (through the missing-value rule).
- **Wetlands:** the GLWD (Lehner and Döll 2004) groupings in the payload. Group 1 is all classes 1 to 12 *including lakes, reservoirs and rivers*; **group 2 is classes 4 to 12, excluding lakes, reservoirs and rivers**. Group 2 is used (`wet_pct_grp2`, the source's own grouping, not relabelled), because group 1 would count lakes a second time beside the HydroLAKES figure (group 1 minus group 2, the lake, reservoir and river part, correlates at 0.85 with the HydroLAKES share across all basins, so they largely measure the same water).

**Rule.** Each part is stated when its share is above zero, **judged by its value** (see the issue below: the engine's `outside_active_domain` flag is about percentiles, not about the value being zero); silent when both are zero. Lake shares show one decimal below 10% (stored to 0.1%), whole numbers above. Wording: `S3.4` (both), `S3.4.lakes`, `S3.4.wetlands` (template v9). The wetland share is stored as a whole percent, so its smallest stated value is 1%.

**At the ten places.** Timbuktu "Lakes cover about 0.4% of the basin and wetlands about 37%"; Tbilisi, Kaifeng, Lviv, Poltava lakes only (0.5%, 0.1%, 0.6%, 0.5%); Santa Fe and Chaco Canyon "Lakes cover about 0.1% of the basin and wetlands about 1%"; Alexandria 1% and 2%; Utqiagvik "Lakes cover about 14% of the basin and wetlands about 67%".

**Rates over the 306 sample basins:** lakes only 93, wetlands only 50, both 56, silent (both zero) 107 (35%). Lakes are under 1% at 98 basins (so many sentences say "about 0.1%" to "about 0.9%"); wetlands are 50% or more at 4; lakes 10% or more at 4. Over all 16,397 basins: lakes above zero at 9,151, wetlands above zero at 7,886 (none below 1%), both zero at 4,195 (26%).

**Not done, by the WO's instruction:** wetland classes are not grouped or relabelled; "seasonal wetlands" (S3.X1) needs the class legend and is not attempted.

## B3. S1.3 the next ecoregion: tried, DROPPED (Karl, 8 Nov)

**Decision.** S1.3 ("The {eco} ecoregion begins about {d} km away.") is not in the profile. Karl's reasoning: the profile says which ecoregion the place sits in and which others its basin takes in (S1.2, S1.4); an ecoregion that lies beyond the basin, within some number of kilometres, describes neither the place nor its basin, and the WO gave no purpose for it. Template v12 removes `S1.3`, `S1.3.near` and the `{S1.3}` slot from `S1.frame` and `nobasin.frame`; the code no longer computes it.

**What was tried (kept as the record).** Distance from the point to the nearest polygon of another ecoregion, geodesic, over the ten places and the 306 sample basins (Cells 3 and 4 of `wo08_new_units.ipynb`, which still run; `next_ecoregion` stays in `wo08_units.py` for them). 304 of 306 have an ecoregion to measure from; 284 have another within the 4-degree search window. Distance, km: median 34, mean 59, 25th percentile 10, 75th 86, 90th 144, max 396.

| Limit | Speaks (of 306) | Of the ten places |
|---|---|---|
| 25 km | 123 (40%) | Timbuktu, Tbilisi, Santa Fe |
| 50 km | 167 (55%) | + Lviv, Alexandria, Poltava |
| 100 km | 226 (74%) | + Kaifeng, Chaco Canyon |

Utqiagvik (137 km) is silent at all three. At 50 km the sentence fires for over half of all basins, so it says little that is particular to the place. The nearest other ecoregion is also the basin's largest-share ecoregion (already named by S1.2c) at only 13 of 306 basins.

## B4. S1.4 the basin's other ecoregions (done; share limit 10%, Karl's choice, 8 Nov)

**Built (template v11, key `S1.4.one` now the trigger).** `S1.4.one` / `S1.4.many`: "Its basin also takes in parts of the {eco} ecoregion[s]." Ecoregions other than the point's, the signature's and the basin's largest by area, covering at least a share of the basin. Shares are the WO-03 Q3 method (intersection area with `basin06`, invalid geometries through `ST_MakeValid`). Code: `wo08_units.py` (`eco_shares`, `fill_ecoregion_units`); computed live per point. **Limit: 10% (`OTHER_ECO_SHARE`), chosen by Karl after the results below.**

**Evidence (Cell 5).** 298 of the 306 sample basins have ecoregion shares (the other 8 are silent). Other ecoregions per basin (0 / 1 / 2 / 3 or more), and how many basins the sentence speaks for:

| Share limit | 0 / 1 / 2 / 3+ | Speaks (of 298) |
|---|---|---|
| 5% | 153 / 113 / 27 / 5 | 145 (49%) |
| 10% | 177 / 99 / 20 / 2 | 121 (41%) |
| 20% | 211 / 81 / 6 / 0 | 87 (29%) |

Most basins that speak name one ecoregion; three or more is rare. At the ten places the limit matters little: Tbilisi (16%) and Alexandria (11%) speak at 5% and 10% and not at 20%; Santa Fe names 3, 2 and 1 ecoregions at 5, 10 and 20%; Chaco Canyon's Arizona Mountains forests sits at 10%. 5% would name minor slivers; 20% would drop Tbilisi and Alexandria.

**At the ten places (10%):** Tbilisi, Eastern Anatolian montane steppe; Santa Fe, Colorado Rockies forests and Arizona Mountains forests; Chaco Canyon, Arizona Mountains forests; Alexandria, Nile Delta flooded savanna; silent at Timbuktu, Kaifeng, Lviv, Poltava, Utqiagvik. Tristan da Cunha has no basin.

## B5. S8.3 the snap (done)

**Built (template v13).** `S8.3`: "The point lies just outside the basin data and was moved {d} m to the nearest basin." Speaks only when a move happened. Rule (`wo08_units.snap_point`, profile scripts only; the engine and the public API still answer `no_basin`): a point inside no basin but within 1 km of one (`SNAP_M`) is moved to just inside the nearest basin's edge (3 m inside, widening to 30 or 300 m only if the point still falls outside the polygon). The move is used only to find the basin; the ecoregion at the point, the river and the elevation stay with the original point. After the move the API must return the aimed-for basin, otherwise the point stays `no_basin`.

**Edge cases (database and API probe, then the full profile in Cell 6).**

| Point | Nearest basin | Moved | Result |
|---|---|---|---|
| Akureyri | 2060058000 | 195 m | S8.3 "moved 195 m"; elevation 7 m; basin 6,554 km² |
| Levuka | 5060081550 | 4 m | S8.3 "moved 4 m"; elevation 31 m; basin 175,335 km² |
| Tristan da Cunha | none within range | none | stays `no_basin` |
| Timbuktu (control) | inside its basin | none | S8.3 silent |

S8.3 is silent at all ten test places in the regenerated profiles.

**Issues found (not fixed; we report sources).**
- **Coastal points with no ecoregion polygon at the point** (both moved points). The "lies in the {eco} ecoregion" sentence then falls back to the basin's majority ecoregion, as for any such point; the fill note records it but the reader is not told. Not caused by the snap.
- **Levuka's basin is 131 separate pieces totalling 175,335 km²**, far above Fiji's land area (about 18,000 km², from memory), so "the basin of about 175,335 km²" would read wrongly for an island place. Cause not looked at (how BasinATLAS groups island basins, or ocean area). Any island basin may show the same. For Opus: a caveat, or silence on S8.1a for multi-part basins.

## Issues found along the way

- **S5.1a and S5.1b (WO-04) read the engine's `outside_active_domain` flag as "none recorded"; it is a percentile guard, not a zero. FIXED (Karl, 8 Nov).** The flag hides a value of at most 1%: of 1,589 flagged basin-by-variable rows in the ring table, 1,396 are 0 and 193 are 1% (122 cropland, 71 pasture), read from `basin06`. Of the 258 flagged core basins, 32 have a positive share, so "no cropland is recorded" was false for them. Now both units state the value when it is above zero, whatever the status ("about 1% of the basin is cropland" at Chaco Canyon, the only one of the ten places that changes), and say "no ... recorded" only at zero; the fill note records the flag. Sample-wide rate of the old error: about 32 of 258 core basins in the ring table.
- **Related, not fixed: the ring table treats the same flagged rows as 0** (WO-06 chose to), so in S5.2's cropland and pasture comparisons a basin with 1% ties with one at 0%. It affects ties only, and only in those two measures (193 of 3,486 member rows). Correcting it means reading the raw values for flagged rows from `basin06`, either at load or by rebuilding the ring table (about 40 minutes). Decision for Karl; and the same flag may hide a 1% elsewhere (karst, permafrost, wetland groups), where it is unmeasured.

## Still to do

A5 (the river-name gate); B6 (the coastline, with the Caspian question). Then the ten filled_profiles, the summary and the commit.
