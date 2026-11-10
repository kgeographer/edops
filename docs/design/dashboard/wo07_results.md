# WO-07 results (running file)

2026-11-08. One section per part (A, B, C), then issues for Karl and Opus. Read `wo07_summary.md` first.

Template: `profile_templates.md` v6. Code: `scripts/edop/whg/wo07_classes.py` (B), `wo07_rivers.py` (C), `wo06_rings.py` (A), `wo04_fill.py`. Notebook: `notebooks/edop/whg/wo07_adjust_classes_rivers.ipynb`.

## Part A: adjustments to the WO-06 sentences

**Rules now.** A ring sentence states, in this order, an extreme (highest or lowest of the set), "all", "all but one" (needs at least five basins with a value), and only if none of those holds, a count, and only when more than half the set (floor `2k > m`). Counts stay in at Karl's decision (Opus's draft dropped them); removing `S2.3.count`, `S2.3.count.precip` and `S5.2.count` switches them off, the content then staying in the fill notes. Other changes: S6.4 and its slot in the Surroundings frame are removed (a value outside the neighbours' range is being highest or lowest, which S6.5 names); S6.5 draws on 11 measures (elevation, relief, slope, forest, karst, sand, silt, clay, runoff, permafrost, water-table depth) with a cap of three sentences; population density and human footprint are left out of the sentences and recorded in the fill note (people's measures are close to circular for gazetteer places); precipitation is never "driest" (aridity is a different fact; "arid/humid" is used for aridity only); S2.3's extreme is one sentence ("Of the n basins that meet here, it receives the least precipitation and is the most arid"); S5.2 opens "Among the n basins"; S6.2 reads "Its water flows on through n of them"; S3.2 headwater and S5.1b "some" as Opus worded them.

**Rates over the 306-basin sample** (Cell 4; basins with fewer than three neighbours get no comparison): S2.3 speaks at 262, S5.2 at 161, S6.2 at 298, S6.3 at 105, S6.5 at 159; the S6.5 cap bites at 35 of those 159. 98% of basins with three or more neighbours get at least one comparison sentence.

**Kaifeng "Its water flows on through two of them".** A basin whose next basin downstream also has a further one at its border drains into both, but not by two outlets. The sentence is true of the adjacency data and may read as two outlets; reviewers may want it reworded.

## Part B: class words

All six units fill at every place that has a basin (`wo07_classes.py`; wording keys `S4.1a`, `S4.1b`, `S4.1b.texture`, `S4.3.karst`, `S4.3.permafrost`, `S5.1c`, `S2.4`). Rates over the 306 sample basins are from Cells 7 and 8.

| Unit | Rule | Source | Sample result |
|---|---|---|---|
| S4.1a terrain | FAO slope class on the mean slope in percent, "on average", percent shown. Classes under 1% merged as "level". | FAO Guidelines for soil description 2006, Table 7 (primary quoted in `wo04_schemes.md`) | 246 with data: gently sloping 62, sloping 42, level 42, moderately steep 41, very gently sloping 25, strongly sloping 21, steep 13. 10 sit where the 0.1 degree storage could change the class. |
| S4.1b soil | Sand, silt, clay normalised to 100, plus the USDA texture class | USDA Soil Survey Manual ch. 3, pp. 122 to 124 (`bibliography/`; checked: every one of the 5,151 integer triples falls in exactly one class) | 253 with data: loam 119, sandy loam 66, sandy clay loam 44, clay loam 12, silt loam 7, loamy sand 4, clay 1; 20 change class with a half-point change. Totals: 168 sum to 100, 85 to 99 or 101. |
| S4.2 rock | GLiM label, lower case | basin06 | unchanged except case |
| S5.1c land cover | Largest GLC2000 class other than cultivated and managed areas, with its share | basin06 `glc_pc_s*`, `lu_glc` | The second class is under 10% at 7 of 306 and under 5% at 1, so a floor would rarely matter. Commonest other class: snow and ice 66, bare areas 49, sparse herbaceous or shrub 37. |
| S4.3 karst, permafrost | Share, silent at zero; karst "up to" | basin06 | karst speaks at 83 (100% at 7), permafrost at 108 (90% or more at 28) |
| S2.4 aridity | UNEP class on the index (stored x 100), index shown; placed before S2.3 so "most arid" follows the class | bands from Wikipedia (secondary; no primary found) | humid 188, arid 38, semi-arid 38, hyper-arid 26, dry sub-humid 16; 8 of 306 on a boundary within the integer rounding |

The terrain word is removed from Setting (S1.frame).

**Findings and caveats**

- **"Flat", "level", "nearly level" merged** (Karl): near-synonyms, and slope is stored to 0.1 degree (0.17%), so the data cannot separate them. This departs from Table 7. "Mountainous" is not used (no support in the table).
- **NoData leak (found and fixed).** On Greenland ice basins the payload gives slope -999.9 and sand, silt, clay -9999, which my first version turned into "very steep (573%)" and "34% sand, 33% silt, 33% clay (clay loam)". Part B units now treat a negative value as no data and print a placeholder. 60 sample basins have no slope and 53 no soil. The older units may leak the same way: check when open item I-3 is taken up.
- **Alexandria karst "up to about 100%".** All five neighbours and the Nile basin are 92 to 100%; 379 of 16,397 basins worldwide are at 100%; its majority rock is unconsolidated sediments, so the two sentences sit awkwardly together. A data pattern (karst-capable carbonate mapped under cover), not a rule fault. Left as is; open item D1.
- **Utqiagvik is "dry sub-humid"** (index 0.63 on a tundra basin with 97% permafrost). The index is precipitation over potential evapotranspiration, so cold places read humid or sub-humid; correct on the index, odd to a reader. For Opus.
- **Alexandria's aridity index of 0.05** is exactly the hyper-arid and arid boundary and the stored integer cannot separate them.
- **"Today" in Land cover.** GLC2000 is year 2000 and HYDE cropland and pasture belong to another year, so "Today" and the section title "Land cover today" are wrong. Karl prefers a stated date; the wording is for Karl and Opus. The frame is unchanged.
- **Land-cover labels are the source's own** and some are long ("shrub cover, closed-open, deciduous (with or without sparse tree layer)"). Karl: do not shorten.
- **Basin means hide mixed basins.** "Moderately steep on average" for Tbilisi's basin (22%) is true of the mean and not of the city's site.

## Part C: the nearest river (S3.1) and a much larger river nearby (S3.3)

### What is built

S3.1 is a sentence of its own in three tiers, and silent when none applies:

1. **A named river that is close.** Only a river of **class 4 or larger** (HydroRIVERS discharge class `ord_flow` 4 or lower, 100 m3/s and up) is named, within **25 km**. Within 1.5 km: "Tbilisi is on the Kura River." Further: "Timbuktu is about 13 km from the Niger River."
2. **No named river, but a river of class 5 or larger (10 m3/s and up) within 3 km:** "A river runs about 3 km from Poltava." Within 1.5 km: "X is on a river."
3. **Otherwise silence.** Karl's rule: a river 70 km away is not worth saying, and neither is anything smaller than class 5.

S3.3 ("a much larger river nearby") fires when a reach two discharge classes above the largest reach with more than 1 km of its length inside the place's own basin lies within 50 km (reported at 10, 25 and 50 km; the sentence uses 25). When that river is the one S3.1 already names it reads "The Yellow River is much larger than any river within the basin." (Kaifeng). Counting the own-basin maximum only from reaches with more than 1 km inside the basin was needed: Kaifeng's basin touches a class 3 reach (1,012 m3/s) at a corner, 337 km from the city, which hid the Yellow River (1,429 m3/s, 11.5 km away). With the boundary clip excluded the basin's largest is class 5 (64 m3/s).

Names: Natural Earth 1:10m river lines (`data/ne_10m_rivers_lake_centerlines_scale_rank`), each with a Wikidata id on 3,390 of 3,589 named lines (976 distinct ids). The English labels were fetched once from Wikidata (`output/edop/whg/wo07_river_labels.csv`; 966 of 976 have a label) so names read "Rio Grande", "Yellow River", not Natural Earth's bare "Grande", "Yellow". A name is used only if (a) a Natural Earth line with an id and label lies within 5 km of the matched reach, (b) no line of a different river is as close, and (c) the label shares a word with the line's own name (this removed "Rio Sabinas" for a line named "San Juan").

River table: `output/edop/whg/wo07_rivers.csv` (574 points: ten places, 306 sample basins, 258 World Heritage Cities), built by `wo07_rivers.fetch_table` (about 65 s, resumable, a failing point is logged and skipped).

### Evidence (from Cell 6 on the table; nothing changed by later steps unless noted)

- Class 6 is small (1 to 9.99 m3/s) and was dropped: at 3 km it would have produced "a river" sentences for 30% of the sample and 45% of cities.
- With the earlier settings (class 4 or larger named within 25 km, class 5 within 5 km) 16% of the sample and 22% of cities were named, 12% and 17% got an unnamed river, 71% and 61% were silent. The class 5 naming was later removed (below), so the final named share is lower; Cell 6 reports the final settings.
- Cities named under a class 4 or larger rule look right where we know the places (Vienna and Regensburg on the Danube, Paris on the Seine, Prague on the Vltava, Cairo on the Nile, Hamburg on the Elbe).

### Issue needing a hard decision: river names from Natural Earth can be wrong, and nothing automatic detects it

**Known wrong names (both found by Karl from local knowledge):**

- **Oaxaca, "Balsas River".** The Natural Earth line 1.1 km from the matched reach is correctly placed and its own `name` is "Atoyac", but its English-name field says "Balsas" and its Wikidata id (Q1129218) is the Balsas River. Two different rivers are called Atoyac: the upper course of the Balsas (Puebla and Guerrero) and the Atoyac at Oaxaca. The real Balsas lines (scale rank 7) are 220 to 560 km away. The Oaxaca line is scale rank 8. It was a class 5 reach, so the class 4 rule removes it.
- **Dujiangyan, "Tuo River".** Karl: a Min Jiang River bisects the city (Google Maps), and Tuo may be an alternate name for it; not resolved. The reach is class 4 or larger, so the sentence is still produced: "Dujiangyan City is on the Tuo River." The along-the-course check flagged it (the line follows 8 to 17% of the reach), but that check was not used as a filter.

**What the checks can and cannot see.** Distance to the line, a unique name, a label that agrees with the line's name, and the along-the-course score all pass for Oaxaca because the line is where it should be; the label is what is wrong. A rule that distrusts any disagreement between `name` and `name_en` would drop correct names too (the Yellow River's `name` is "Huang"). The course score separated Dujiangyan (0.08) but also scored correct matches low where the 1:10m lines are generalised (Cairo 0.27, Yaroslavl 0.35), so it cannot be a general filter.

**Error rate.** 2 of the 62 named city matches (at the time) are known wrong, found only because Karl knows those places. That is a lower bound. One sentence in thirty or so could be a confident false statement about a place. The WH Cities are on or near big rivers, which is the favourable case; names for ordinary places may be worse or better.

**Options considered**

1. A correction table keyed on Natural Earth line ids (right name, or blank), seeded with these two and grown as reviewers report errors. Karl's view, from a decade with gazetteers: unbounded, a lost cause.
2. A visible caveat on the pilot page ("river names come from Natural Earth and Wikidata and may be misattributed") with a way to report an error. Not decided; a page decision for Karl and Opus.
3. Name only class 4 or larger rivers. **Adopted** (Karl, 7 Nov). It removes the Oaxaca type (small tributaries whose names collide) but not Dujiangyan.
4. A lenient along-the-course filter (leave a river unnamed if its line follows under about 20% of the reach). On the 68 checked cities it catches only Dujiangyan and loses no correct name. Not adopted.
5. No names at all (always "a river runs about N km from X"). True everywhere, much less useful.

**Decision needed:** whether the pilot page should carry river names given that some will be wrong and the rate is unknown, and if so with what safeguard (caveat, error reporting, a list of large rivers vetted by a human, or option 4). Karl's current position: accept the class 4 cutoff, log the rest. To revisit with Opus and the reviewers after the pilot has produced a real error rate.

### Settings, for reference (constants at the top of `wo07_rivers.py`)

`NAMED_LIMITS = {'r4': 25.0}` named class 4 or larger within 25 km; `ON_KM = 1.5`; `NEAR_KM = 3.0` (unnamed class 5 or larger); `NAME_KM = 5.0` (line to reach); `STEP = 2`, `D_KM = (10, 25, 50)`, `USE_D = 25` for S3.3; `OWN_MIN_KM = 1.0`.

### Smaller points found along the way

- **Alexandria** is silent: it sits on the coast at the western edge of the Nile delta, about 52 km from the Rosetta branch, a peculiar case (Karl: not worried).
- **Timbuktu** needed the size-dependent limit: the Niger is 12.6 km away, beyond the first 10 km placeholder.
- **Panama City** is "about 7 km from the Panama Canal" in the wider list (a canal, not a river; accurate).
- **Natural Earth names**: only 20 to 29% of places had any name within 5 km (sample and cities); the Wikidata labels fix the display form but not coverage.
- **A process lesson:** my first reading of the doubtful names (Quebec City "Saint John", Bam "Helmand") was a display fault, not a naming fault. Cell 6 printed the nearest line's name whatever its distance, while the sentence rule required a line within 5 km. Cell 6 now prints the river the sentence uses.
