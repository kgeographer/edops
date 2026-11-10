# WO-06 results: comparing a place's basin with the basins around it

2026-11-07. Summary: `wo06_summary.md`. Profiles: `wo06_filled_profiles.md`. Notebook: `notebooks/edop/whg/wo06_rings.ipynb`. Rules: `scripts/edop/whg/wo06_rings.py` (plus ring hooks in `wo04_fill.py`). Wording: `profile_templates.md` Version 5.

Figures below are from the notebook runs Karl pasted. Place checks (Timbuktu, Utqiagvik, Chaco Canyon and so on) are plausibility reads, not verification; Karl is to flag any that look wrong.

## The ring table

`output/edop/whg/wo06_ring_values.csv`: long table (core, member, role, shared_km, area_km2, variable, value, status) for 315 basins: the 306 sample basins and nine of the ten test places (Tristan da Cunha has no basin). 311 were fetched in the first full run (2,374 s, about 7.6 s each); resumable.

- Neighbour counts (border only) match the saved WO-03 pair table at all 315 basins.
- Counts per basin: 0 (8), 1 (2), 2 (18), 3 (31), 4 (55), 5 (64), 6 (50), 7 (37), 8 (17), 9 (16), 10 (7), 11 (1), 12 (5), 14 (1), 15 (2), 18 (1). 28 basins have fewer than three; 23 have a point-only neighbour (excluded, as the WO says).
- 45 variables per basin. The fetch keeps numeric rows only, so the payload's class-valued rows are dropped, and adds `elev_mean` and `forest_extent` from `public.basin06` (`ele_mt_sav`, `for_pc_sse`; -9999 is NoData), which the ring payload does not carry. `outside_active_domain` rows are treated as 0.

## Rules as built

- **Neighbours:** basins sharing a border (`shared_km > 0`). At least three neighbours with a value (`MIN_NB`), else the comparison is silent. Ties are never ranked; if the core equals every neighbour there is no sentence.
- **Extreme:** the core is the highest or lowest of the set. **Count:** otherwise the measure with the most one-sided count ("more than k of the m"). Extremes take priority; up to two are stated in S2.3 and S5.2, three in S6.5. Extremes over the same set of basins and the same frame are joined into one sentence.
- **S6.2:** counts of neighbours that drain into the core and that the core drains into (WO-03 flow table). Speaks whenever there is a neighbour; one added key, `S6.2.out_some`, for a basin that drains into several.
- **S6.3:** a measure on which every neighbour across a divide (flow `same` or `other`) lies on the same side of the core; first in list order.
- **S6.4:** among the 25 numeric local measures, the count where the core lies outside the neighbours' min to max; speaks when at least one. Silent if within on all.
- **S6.5:** extremes among terrain, forest, karst and soil shares, up to three.
- **Wording:** precipitation has its own frames ("receives the least precipitation of the eight basins that meet here"); other measures use "is". Numbers up to ten are words.
- **Fill note `S6.ring`:** neighbour count, core and neighbour areas, and whether the core is the smallest or largest (the WO asked for area in the notes; no area sentence).

## Measure lists as used (editorial, to be adjusted after the sample page)

| Unit | Measures, in the order tried |
|---|---|
| S2.3 | precipitation, temperature, aridity |
| S5.2 | cropland, pasture, population density |
| S6.3 | elevation, precipitation, temperature, aridity (measures with a natural adjective) |
| S6.5 | mean elevation, relief, slope, forest, karst, sand, silt, clay |
| S6.4 (counted) | `precip_yr`, `temp_yr`, `temp_min`, `temp_max`, `aridity`, `runoff`, `cropland_extent`, `pasture_extent`, `pop_density`, `human_footprint_09`, `elev_min`, `elev_max`, `elev_mean`, `relief`, `slope_avg`, `stream_gradient`, `wet_pct_grp1`, `wet_pct_grp2`, `forest_extent`, `karst`, `permafrost_extent`, `pct_sand`, `pct_silt`, `pct_clay`, `gw_table_depth` |

Departures from the WO's list: "roughness" is `slope_avg` (the catalog has no roughness; nearest are `slope_avg` and `stream_gradient`); wetland is left out of S6.5 (the catalog defines no wetland groups); S6.3 omits measures without an adjective.

## Firing rates over 306 sample basins

Speaks / silent: S2.3 278 / 28; S5.2 232 / 74; S6.2 298 / 8; S6.3 70 / 236; S6.4 208 / 98; S6.5 144 / 162. No unit failed to fill anywhere.

- S2.3: 59 extreme, 219 count. Extremes found per basin 0:247, 1:35, 2:15, 3:9; the cap of two bites at 9.
- S5.2: 80 extreme, 152 count, 46 with nothing to say. Extremes 0:226, 1:62, 2:14, 3:4; cap bites at 4.
- S6.5: extremes per basin 0:162, 1:69, 2:34, 3:18, 4:13, 5:7, 6:2, 7:1; cap of three bites at 23 of the 144 that speak.
- S6.3: 70 speak; first measure elevation (38: 21 lower, 17 higher), precipitation (16), temperature (12), aridity (4). Elevation leads partly because of list order.
- S6.4: measures compared per basin 10 / 22 / 25 (min / median / max). Within the range on all (silent) at 70 of 278 eligible. Where it speaks, outside on 1 / 3 / 16 measures (min / median / max); distribution 1:46, 2:42, 3:36, 4:19, 5:15, 6:10, 7:6, 8:8, 9:6, 10:6, 11:1, 12:3, 13:4, 14:5, 16:1.

By neighbour count (share with an extreme in S2.3 / S5.2; share speaking S6.5 / S6.3): 3 to 4 neighbours (84 basins) 0.43 / 0.44; 0.74 / 0.38. 5 to 6 (112) 0.16 / 0.30; 0.54 / 0.20. 7 to 8 (51) 0.04 / 0.14; 0.33 / 0.22. 9 or more (31) 0.10 / 0.06; 0.16 / 0.16.

By core size among its ring (51 smallest, 26 largest, 201 neither; 278 with three or more neighbours): at least one extreme 0.92 / 0.50 / 0.61; S6.4 silent 0.04 / 0.42 / 0.28.

## The ten places

Sentences are in `wo06_filled_profiles.md`. Ring sentences per place, counting the flow sentence S6.2: Timbuktu 5 (lowest elevation, least relief and gentlest slopes of six; seven of 22 measures outside range); Tbilisi 3 (S2.3, S5.2, S6.2; S6.3, S6.4 and S6.5 silent, since its basin is the largest in its ring and sits inside its neighbours' range on all 23 measures); Santa Fe 5; Kaifeng 5; Lviv 3; Poltava 4; Chaco Canyon 6; Alexandria 4; Utqiagvik 6 (smallest in its ring; outside the range on 12 of 21 measures); Tristan da Cunha has no basin.

The WO expected Santa Fe to be sparse and Timbuktu and Tbilisi to have several. Santa Fe has five, as many as Timbuktu, and Tbilisi has three. The count form speaks for any basin with three or more neighbours.

## Issues found

1. **Size effect.** A large core's averages sit among its small neighbours (Tbilisi's basin is the largest of its ring, 23,251 km² against 2,976 to 22,012). The first S6.4 said "23 of 23 within the range" for such basins, which says nothing; fixed by reversing it. Extremes still depend on size and ring count (see above). No sentence about area was added.
2. **Thin S6.4 sentences.** 46 basins are outside on one measure and 42 on two; the sentence does not say which. A floor, or naming the measures, is a choice for Karl or Opus. Not set.
3. **Wording of dryness.** "Driest" for precipitation was misleading, since aridity is precipitation over PET; fixed in S2.3 and S6.3. `S3.2b.wetter` in the Water section has the same word; not changed (WO-05 wording).
4. **Number words.** "ten of the 12", "nine of 21 measures": the rule stops at ten.
5. **Flow sentences at small rings.** S6.2 speaks for 20 basins with one or two neighbours, where no comparison does. Intended; counts need no minimum.
6. **Ring payload gaps (for the endpoint).** No mean elevation, no forest share; read from `public.basin06` here.
7. **Open-items file name.** The WO cites `profile_open_items.md`; the file is `WHG-profile_open-tems-post-WO7.md`.

## Housekeeping items: untouched, and why

- **I-3 (the -9999 class):** not needed, since no class comparison was built (numeric measures only); do before WO-07 class words.
- **R1 (temperature by difference):** the ring sentences compare temperature by order and never take a ratio. The Analysis/provenance rule's temperature ratio is untouched; it needs a threshold decision.
- **R2 (the "no percentile" list):** parked; the S8.2 list still repeats upstream versions (Tbilisi: 7 measures, karst, permafrost and wetland groups with their upstream twins).
- **E3 (the 36 garbled ecoregion names):** needs Karl's yes to write to the database.

## Process notes

- The template stamp now also tracks `wo06_rings.py` (last commit and edited-since).
- A markdown cell of the notebook was edited through a script, not NotebookEdit; the code cells were edited with NotebookEdit.
- Commits: `fd6050d` (WIP build); the closing commit follows this file.
