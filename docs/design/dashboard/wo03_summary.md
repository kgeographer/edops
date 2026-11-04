# WO-03 summary (draft, Q1 to Q3 done; Q5, Q6 not started; Q4 on hold)

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

## Decisions these numbers raise (for Karl and Opus)

1. Keep every touching basin as a neighbour, or drop point contacts and very short borders? What cutoff?
2. Use compass directions at all? If so, from the place, and say nothing where the methods disagree. Or describe neighbours by flow (upstream, downstream, across a divide) instead.
3. Which meaning of "coastal" for the profile: the coast flag, the Sandbox's "Coastal terminal" (which differs for 45% of those basins), or outlet type (I-7)?
4. What to show when a place has no neighbours or only coastal ones (islands, offshore points)?
5. How to treat a neighbour whose catchment is almost the core's, and ties or zeros, in "where the core ranks" statements.
6. Whether the ring should be built from one score call (faster, needs a code change to verify).
7. Which ecoregions to name for a place or a ring: any area, 1% or 5%; and what to say about the part outside every ecoregion (coast, lakes) and about the 26 ecoregions with no text.

## Still to do

Q5 nearest main stem; Q6 where the point sits. Q4 (river names) needs a named-rivers source, which the database does not have.
