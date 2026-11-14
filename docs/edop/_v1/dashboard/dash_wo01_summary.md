# dash WO-01 summary: the summary at Level 08

2026-11-14. Spec `dash_wo01_summary-Level08.md`; record `dash_wo01_results.md`. Branch `dashboard` (from `v1`). Nothing in the app changed. Items 3 and 4 not started; item 2 partly done.

- **Item 1, cost of Level 08 profiles.** As the generator works today, all 190,675 Level 08 basins would take about 93 days on one local process (42 s per basin). Two causes: an ecoregion query that takes 35 s per Level 08 basin because there is no index on `hybas_id` (with the basin picked first it takes about 0.1 s and gives the same result on the two basins compared), and the ring call, which recomputes every basin's signature about 6 times. With both dealt with, about 3.6 days (1.6 s per basin); about 3 days with an index. Template fill is negligible (1 to 4 ms).
- **Level 06 for comparison:** 16,397 basins take about 2 days as built, about 13 hours with signature reuse.
- **Ring, pair and flow tables** exist only for about 310 test basins; they would be built for every basin at either level.
- **Item 2, point and basin units.** Confirmed for the opening sentence: elevation at the point and the point's ecoregion are place facts; the basin's elevation range and majority ecoregion are basin facts; "also takes in parts of …" depends on the point (it skips the point's own ecoregion). So stored basin profiles hold ingredients (values, basin sentences, the basin's ecoregion shares) and the paragraph is assembled when a place is asked about.
- **Ecoregions per basin (300 sampled basins):** Level 08 has mean 1.3 (Level 06: 2.2); 80% of Level 08 basins have one ecoregion at 10% or more (50% at Level 06); "also takes in parts of …" would speak in about 18% of Level 08 basins (37% at Level 06).
- **Not measured:** storage size, production-server speed, parallel workers, the point lookups at request time, the generator's wording at Level 08, how often the levels disagree.

**Gate.** Karl and Fable choose the Level 08 behaviour and whether Level 08 profiles are stored. The cost figures say storing them is a matter of days, not months, if the ecoregion query and the signature reuse are done; items 3 and 4 would show what the summary says at Level 08 and how often the two levels disagree.
