# WO-08 results (running file)

2026-11-08. One section per numbered item of `wo08_wo07-decisions-new-units-coastline.md`, added as each closes. Template: `profile_templates.md` (version 8 so far). Code: `scripts/edop/whg/` (`missing.py` new; `wo04_fill.py`, `wo06_rings.py`, `wo07_classes.py` changed). Items still to do are listed at the end.

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

## Still to do

A5 (the river-name gate); B1 (when the rain falls); B2 (lakes and wetlands); B3 and B4 (the next ecoregion and the basin's other ecoregions, with cutoff results at 25, 50, 100 km and 5, 10, 20%); B5 (the snap); B6 (the coastline, with the Caspian question). Then the ten filled_profiles, the summary and the commit.
