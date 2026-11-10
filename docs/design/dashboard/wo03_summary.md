# WO-03 summary (draft, Q1 to Q6 done; Q4 reframed)

Read this first. Evidence and tables: `wo03_results.md` (issue numbers I-n refer to it). Measured on the local database at L6, on 9 test places and the WO-02 sample of 306 random basins (not settlements, which sit on coasts and rivers more often).

## Q1. The ring as it stands

- **Size.** A ring (the basin plus the basins that touch it) has a median of 5 neighbours; 80% of sample rings have 3 to 9; the largest has 18. 8 of 306 sample basins have none (all coastal; 7 look like islands by their coordinates, not checked). Neighbour areas run from a tiny fraction of the core's to thousands of times larger; the extremes come from cores under 60 km².
- **Cost today.** The existing ring call takes about 1.25 s per basin: 5 to 17 s for the test places, and 89 to 290 KB of JSON (without detail). A compact neighbour row is about 7.6 KB (20 KB in full); a whole compact ring is 43 to 114 KB, 3 to 6 KB gzipped.
- **Faster is possible, not yet shown.** The scores for all basins in a ring can be computed in one call (about 1.2 s however many basins) and are identical to the one-at-a-time values (8,296 cells compared, none differ). Whether the rest of the pipeline can then build a row set per basin from that call was not tested; my rough estimate is 2 to 3 s for a ring, not a measurement.
- **Who counts as a neighbour.** Contact only. 1.5% of neighbours (in 7.5% of basins, nearly all coastal) touch the core at a single point, with no border; 11% have under 10 km of border (I-1). Coastal basins often have few or no neighbours; one island basin has another basin 173 m away that does not touch it (I-5).
- **Directions.** The ring's bearings are measured from the core basin's centroid, not from the place. Measured from the place instead, the compass word changes for about 1 neighbour in 5 in the sample (1 in 10 with 4 points) and, at the test places, the four ways of computing a direction agree for only 19% of neighbours (I-4).
- **Zeros and gaps.** Where a variable is zero differs between the core and its neighbours for 34 of 59 test-place neighbours. 7 values are missing (source NoData); one internal table keeps the NoData code as if it were a class (I-3).

## Q2. Flow relation of neighbours

- **It can be labelled, with no unknowns,** from the source's `next_down`. Sinks sometimes carry a "virtual" link that is not flow (source documentation); those were cut and made no difference to up or down labels (I-8).
- **Only about a quarter of neighbours are on the core's stream:** 12% upstream, 12% downstream, 76% across a divide (28% within the same river system, 48% in another). 30% of rings have an upstream neighbour, 58% a downstream one, 27% both, 38% neither.
- **Ring completeness.** Every basin that drains into a core is in its ring. A core's downstream basin is in the ring except for sinks.
- **Upstream-catchment values.** Flow neighbours differ from the core by about half as much as off-stream ones (3.5 against 7.5 to 9.1 percentile points), but mostly because their catchments overlap: a neighbour whose catchment is within 10% of the core's (10% of flow neighbours) is the same place on these variables.

## Q3. Ecoregions

- **A basin has one or two ecoregions of any size, a ring two or three.** At 5% of the area: 146 of 298 sample basins have one, 111 two, 41 three or more; rings have a median of 2 (90% have 4 or fewer). Basin and ecoregion boundaries are drawn independently, so this is expected.
- **The place's own ecoregion is the basin's largest in 94% of sample basins** (280 of 297); in the rest the place is in a smaller one. At the test places, Alexandria, Timbuktu and Tbilisi are in the smaller.
- **Gaps.** Coastal and lake basins are partly outside every ecoregion polygon (median full coverage, worst 71%); one sample point, in a lake, falls in none. 26 of 847 ecoregions have no Wikipedia text; they matter for 3 to 4 of 306 sample places.

## Q4. River names (reframed; Natural Earth supplied by Karl, not in the database)

- **The layer names the main stem near a place in about 60% of World Heritage Cities** (156 of 258 within 10 km of the nearest river above 10,000 km²), and 38% of random basins (115 of 306), which bracket settlements in general. It is better in Europe (87 of 115 cities) than for Arab states (5 of 21); desert and polar basins have almost none.
- **When it matches, the match is tight** (on the line or far from it), but the named river may be far from the place: in a 30-city check, 9 of 22 matched cities had the main stem more than 50 km away, and a few names are branches (Lek, not Rhine).
- **No name does not mean no river.** The river network says a river is there (Berlin: a 12,700 km² stem 12 km away, with no line in the layer). Names would be added only for close, confident matches.

## Q5. Nearest main stem

- **The basin's own upstream area can be far from the river a place sits near:** Kaifeng's nearest river above 1,000 km² is 11.5 km away and drains 48 times the basin's own area. Timbuktu and Tbilisi sit on the big river (ratio about 1).
- **In 306 random basins, a river 10 or more times larger than the basin lies within reach for 4% at 1,000 km² (median 10 km away), 15% at 10,000 km² (median 62 km) and 64% at 100,000 km² (median 369 km).** At the top threshold the figure mostly reflects distance. None of the rivers that touch the core exceed the basin's area tenfold.
- **Median distance to the nearest river above 10,000 km² is 49 km;** above 1,000 km², 9 km.
- Limit: upstream area is size at that point; a major river near its source reads small.

## Q6. Where the point sits

- **WH Cities sit near a basin edge more often than a basin's middle point does:** the median distance to the core's outline is 7.6 km, 7.6% of the core's size (equivalent side); the nearest neighbouring basin is within 5 km for 19% and within 25 km for 69%.
- **For a third of cities (84 of 254) the nearest edge is the coast, not a divide;** Alexandria is 1.5 km from the coast and 47 km from the nearest neighbouring basin.
- **A settlement has an L6 basin in nearly every case:** 2,994 of 3,000 GeoNames cities. The 6 without are 5 islands the basin data does not cover (570 to 7,196 km from the nearest basin) and Akureyri, whose point is 0.2 km outside a basin's edge; Levuka (Fiji) among the WH Cities is under 5 m outside. Snapping would fix the edge cases and nothing else. Points just offshore of a coast were not measured.

## Decisions these numbers raise (for Karl and Opus)

1. Keep every touching basin as a neighbour, or drop point contacts and very short borders? What cutoff?
2. Use compass directions at all? If so, from the place, and say nothing where the methods disagree. Or describe neighbours by flow (upstream, downstream, across a divide) instead.
3. Which meaning of "coastal" for the profile: the coast flag, the Sandbox's "Coastal terminal" (which differs for 45% of those basins), or outlet type (I-7)?
4. What to show when a place has no neighbours or only coastal ones (islands, offshore points)?
5. How to treat a neighbour whose catchment is almost the core's, and ties or zeros, in "where the core ranks" statements.
6. Whether the ring should be built from one score call (faster, needs a code change to verify).
7. Which ecoregions to name for a place or a ring: any area, 1% or 5%; and what to say about the part outside every ecoregion (coast, lakes) and about the 26 ecoregions with no text.
8. Whether to name rivers at all, and if so the rule: name only for a close named line and a close stem ("on the Danube"), generic wording otherwise (I-9: `gaz.hydrorivers` is incomplete; `gaz.rivers` was used).
9. What distance and size count as a river "near" a place, given the distances above.
10. Whether to snap a point outside every basin to the nearest one, and the tolerance: a snap of about 1 km would fix Akureyri and Levuka and nothing else; the other points with no basin are islands 570 km or more away.
11. How to word "near the edge of its basin" when the nearest edge is the coast, and whether the cutoff is a distance or a share of the core's size (1 km, 5 km, 10 km and 25 km are 5%, 19%, 34% and 69% of WH Cities).

## Still to do

Nothing in WO-03 beyond review by Karl and Opus. Not done: Q4 as the work order wrote it (matching names along main stems; share of cores and rings with a named river).
