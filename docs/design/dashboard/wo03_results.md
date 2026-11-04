# WO-03 results: exploratory notebooks for the WHG environmental profile

Working file, started 2026-11-02. Spec: `WO-03_exploratory-notebooks-WHG-profile.md`. Code at commit `d0bb073` (local database, local timings). Notebooks in `notebooks/edop/whg/`, helpers in `scripts/edop/whg/wo03_common.py`, outputs in `output/edop/whg/` (gitignored). Sections are filled as cells are run; "pending" marks what has not been seen yet.

## Test places

Ten places; each resolved with one `ST_Contains` on `public.basin06` (L6). Coordinates are the WO's approximate pair; the Tristan da Cunha point is my choice for the island case (WO leaves it to CC).

| Place | `hybas_id` | `main_bas` | `next_down` | `sub_area` km² | `up_area` km² |
|---|---|---|---|---|---|
| Timbuktu | 1060551560 | 1060022420 | 1060550540 | 3,826.4 | 382,644.3 |
| Tbilisi | 2060616700 | 2060070050 | 2060624230 | 23,250.8 | 23,251.9 |
| Santa Fe | 7060674070 | 7060049270 | 7060675990 | 14,659.0 | 49,334.1 |
| Kaifeng | 4060675920 | 4060009880 | 4060670500 | 15,266.6 | 15,266.9 |
| Lviv | 2060376210 | 2060026550 | 2060374710 | 16,335.7 | 16,336.0 |
| Poltava | 2060459130 | 2060007930 | 2060469820 | 14,511.5 | 14,511.5 |
| Chaco Canyon | 7060618200 | 7060008710 | 7060607440 | 11,887.9 | 11,888.0 |
| Alexandria | 1060034170 | 1060034170 (own id) | 0 | 16,374.7 | 16,374.7 |
| Utqiagvik | 8060007840 | 8060007840 (own id) | 0 | 4,661.6 | 4,661.6 |
| Tristan da Cunha | none (0 matches) | | | | |

(Exact ids from a direct query on 2026-11-02; cell 2 showed them only as floats.)

- Every place has exactly one match except Tristan da Cunha, which has none (`NoBasinsError`, as expected for an oceanic island).
- Santa Fe and Chaco Canyon are in different L6 basins and different `main_bas` (checked 2026-11-01 and again in cell 2).
- Timbuktu: `up_area` is 100 times `sub_area`. Kaifeng: `up_area` equals `sub_area` (the Yellow River at Kaifeng drains hundreds of thousands of km²; this is the perched-river gap, to be measured in Q5). Alexandria and Utqiagvik: `main_bas` equals the basin's own id and `next_down` is 0 (outlet basins). Alexandria's `up_area` (16,375 km²) is far below the Nile's; the basin is a small coastal one (Q5).

## Q1. The ring as it stands

### 1a. `resolve_basin_ring` (cells 3 and 4)

| Place | Neighbours | Largest / core | Smallest / core | Corner-only (`shared_km` = 0) | Shared border total km | Resolve s |
|---|---|---|---|---|---|---|
| Timbuktu | 5 | 6.52 | 0.241 | 0 | 544.9 | 0.151* |
| Tbilisi | 9 | 0.95 | 0.128 | 0 | 1,277.9 | 0.028 |
| Santa Fe | 7 | 1.50 | 0.016 | 0 | 775.4 | 0.017 |
| Kaifeng | 7 | 1.15 | 0.205 | 0 | 1,085.0 | 0.027 |
| Lviv | 12 | 1.25 | 0.009 | 0 | 1,071.5 | 0.031 |
| Poltava | 4 | 1.59 | 0.168 | 0 | 931.9 | 0.025 |
| Chaco Canyon | 7 | 1.59 | 0.127 | 0 | 584.5 | 0.022 |
| Alexandria | 5 | 1.55 | 0.523 | 0 | 773.7 | 0.022 |
| Utqiagvik | 3 | 2.79 | 1.403 | 0 | 389.0 | 0.013 |
| Tristan da Cunha | error: `NoBasinsError: No basin covers the given point location` | | | | | |

\* first call of the session (includes connection and warm-up).

Neighbour count 3 to 12. Area ratios range from 0.009 to 6.52 of the core.

### 1b. Observations from the neighbour tables (cell 4)

1. **Short shared borders.** No neighbour at these nine places has a zero border, but three have under 6 km, next to neighbours with 200 to 430 km: Alexandria 1060034270 (3.1 km; neighbour 20,936 km², 1.3 times the core), Tbilisi 2060624070 (4.7 km; 11,836 km²), Utqiagvik 8060008030 (5.2 km; 6,539 km², 1.4 times the core). The ring treats all neighbours alike. Frequency over the sample: 1i.
2. **`border_bearing` versus `centroid_bearing`.** Largest gap: Kaifeng 4060694190, 344.5 degrees against 100.3 degrees (124 degrees apart) with a 110.6 km border. Other gaps: Alexandria 1060034270 (3.1 km border) 70 degrees; Utqiagvik 8060008030 37 degrees; Tbilisi 2060624070 32 degrees. `border_mid` is `ST_Centroid` of the intersection; for a border in several segments that point need not lie on the border. Checked in 1i and 1j: `border_mid` is often off the border, but that offset does not explain the large bearing gaps.
3. **The core's `next_down` basin is a ring neighbour, and is the smallest neighbour at four of seven places that have one.** Santa Fe 7060675990 (233.5 km², 0.016 of the core, 36.4 km border); Timbuktu 1060550540 (921.4 km²); Lviv 2060374710 (146.6 km²); Kaifeng 4060670500 (3,124.5 km²). Not the smallest at Tbilisi (2060624230, 17,660 km²), Chaco Canyon (7060607440, 14,517.5 km²) or Poltava (2060469820, 12,970 km²). Alexandria and Utqiagvik have no `next_down`. Seven places only; Q2 counts it over the sample.
4. **Neighbours shared between places.** 7060674060 (18,885 km²) is a neighbour of both Santa Fe and Chaco Canyon. Relevant to per-basin caching (ring spec).
5. **Smallest neighbours** (ratio under 0.02): Lviv 2060374710 (146.6 km², 19.8 km border) and Santa Fe 7060675990; both are the core's `next_down` (item 3).

### 1c. `basin_ring_signature` time and payload size (cell 5)

L6, bands A to E, no Band T; local timings. Each ring is the centre plus N neighbours, one `single_basin_signature` call each. "Per basin" = total / (N + 1).

| Place | Neighbours | s (detail off) | s per basin | KB | gzip KB | s (detail on) | s per basin | KB | gzip KB |
|---|---|---|---|---|---|---|---|---|---|
| Timbuktu | 5 | 7.82 | 1.30 | 133.7 | 5.2 | 7.27 | 1.21 | 289.4 | 29.2 |
| Tbilisi | 9 | 12.61 | 1.26 | 223.2 | 7.8 | 13.02 | 1.30 | 482.6 | 47.8 |
| Santa Fe | 7 | 10.44 | 1.31 | 178.1 | 6.6 | 10.64 | 1.33 | 388.0 | 40.3 |
| Kaifeng | 7 | 9.65 | 1.21 | 178.1 | 6.1 | 10.01 | 1.25 | 386.2 | 39.8 |
| Lviv | 12 | 16.51 | 1.27 | 290.2 | 8.8 | 15.96 | 1.23 | 626.7 | 61.0 |
| Poltava | 4 | 6.31 | 1.26 | 111.2 | 4.4 | 6.52 | 1.30 | 241.3 | 25.0 |
| Chaco Canyon | 7 | 10.85 | 1.36 | 178.5 | 6.0 | 10.53 | 1.32 | 386.6 | 38.4 |
| Alexandria | 5 | 7.82 | 1.30 | 133.4 | 5.2 | 6.91 | 1.15 | 286.2 | 28.4 |
| Utqiagvik | 3 | 4.66 | 1.17 | 88.9 | 3.8 | 4.67 | 1.17 | 191.8 | 18.8 |

- **Time:** 1.15 to 1.36 s per basin, the same at 3 and at 12 neighbours, so a ring costs about 1.25 s times (N + 1): 4.7 to 16.5 s over these places. Detail on or off does not change the time. The per-call cost is consistent with a full-table `PERCENT_RANK` at each L6 call (read from `attach_values`); not separately measured.
- **Size, detail off:** 89 to 290 KB raw, about 22 KB per basin. The ring spec estimated 100 to 150 KB for a typical ring. **Detail on:** 192 to 627 KB, about 48 KB per basin (consistent with WO-02's 36 to 84 KB single-basin payloads).
- **gzip:** 3.8 to 8.8 KB with detail off (about 26:1) and 18.8 to 61 KB with detail on (about 10:1). The detail-off ratio is high; plausible given repeated keys across near-identical rows, but a second figure comes from cell 8 (projected compact payload, gzipped).
- The warm-up line (first call, catalog load) was not captured.

### 1d. Payload structure and row statuses (cell 6)

- Top level: `type`, `lat`, `lon`, `level`, `center`, `ring`. `center` is a full single-basin payload (`scope`, `shortfall`, `bands`, `temporal`, `caveats`, `rows`). Each ring member carries `hybas_id`, `sub_area_km2`, `shared_km`, `border_bearing`, `centroid_bearing`, `neighbor_lat`, `neighbor_lon` and a **full** `signature` payload of its own, so `scope`, `bands`, `temporal` and `caveats` repeat per neighbour.
- Every signature, centre and neighbour, has 52 rows at all nine places (min = max = 52).
- Statuses seen: `ok`, `outside_active_domain`, `no_data`; no other values.

| Place | Centre `ok` / `outside_active_domain` | Neighbour rows by status (all neighbours) | Mean `ok` rows per neighbour |
|---|---|---|---|
| Timbuktu | 48 / 4 | ok 232, outside 28 | 46.4 |
| Tbilisi | 45 / 7 | ok 412, outside 56 | 45.8 |
| Santa Fe | 49 / 3 | ok 338, outside 26 | 48.3 |
| Kaifeng | 47 / 5 | ok 335, outside 29 | 47.9 |
| Lviv | 45 / 7 | ok 540, outside 82, no_data 2 | 45.0 |
| Poltava | 45 / 7 | ok 193, outside 15 | 48.3 |
| Chaco Canyon | 45 / 7 | ok 323, outside 40, no_data 1 | 46.1 |
| Alexandria | 48 / 4 | ok 225, outside 31, no_data 4 | 45.0 |
| Utqiagvik | 45 / 7 | ok 135, outside 21 | 45.0 |

- `no_data` appears only in neighbours (Lviv 2, Chaco Canyon 1, Alexandria 4 rows), never in a centre. Which variables, and in which neighbours, is not yet looked at.
- Not yet looked at: whether the set of `outside_active_domain` variables is the same in the centre and in its neighbours (the table gives counts only).

### 1e. Position scores computed once for the set (cell 7)

`engine.attach_values` (the step that reads raw values and computes the position scores) called once over centre + neighbours, versus once per basin. Local timings; read-only.

| Place | Basins | One call for the set (s) | One call per basin (s) | Numeric cells compared | Differ | Text cells differ |
|---|---|---|---|---|---|---|
| Timbuktu | 6 | 1.55 | 8.17 | 270 | 0 | 0 |
| Tbilisi | 10 | 1.36 | 11.64 | 450 | 0 | 0 |
| Santa Fe | 8 | 1.19 | 10.12 | 360 | 0 | 0 |
| Kaifeng | 8 | 1.30 | 10.22 | 360 | 0 | 0 |
| Lviv | 13 | 1.29 | 15.93 | 585 | 0 | 0 |
| Poltava | 5 | 1.15 | 5.73 | 225 | 0 | 0 |
| Chaco Canyon | 8 | 1.16 | 9.20 | 360 | 0 | 0 |
| Alexandria | 6 | 1.15 | 6.88 | 270 | 0 | 0 |
| Utqiagvik | 4 | 1.20 | 4.59 | 180 | 0 | 0 |

- **Yes, it runs over a set.** The scores from the set call and from the per-basin calls agree in every compared cell (0 of 3,060 numeric cells differ at tolerance 1e-9; 0 text cells differ).
- **The set call costs about 1.2 to 1.5 s whatever the number of basins (4 to 13); the per-basin route costs about 1.15 to 1.4 s per basin.** The per-basin route accounts for essentially all of the per-basin time seen in cell 5 (about 1.25 s). So on these measurements the time of a ring is the cost of one `attach_values` call plus the rest of the pipeline per basin, which these tables do not time.
- **Cell 7 raised a pandas `FutureWarning`** (concatenation with all-NA columns, at `pd.concat(parts)`). It was repeated as cell 11 without the concat, comparing each basin's single-call row with its row in the set result, over all three frames `attach_values` returns. **Result: 8,296 cells compared (3,740 scores, 748 class ids, 3,808 raw values; 68 single-basin calls), 0 differ, 0 column-set mismatches.** Scores frame 55 columns, class-id frame 11, raw frame 56 (cell 7 had compared 45 of the 55 score columns as numbers and the rest as text). Set call 1.16 to 1.62 s; per-basin route 5.79 to 17.74 s. The columns that are all-NA in a single-basin frame are `wetland_class` (4 basin-calls) and `pct_clay_upstream`, `pct_sand_upstream`, `pct_silt_upstream` (1 each) in the scores and raw frames: exactly the seven `no_data` rows of 1h, and the source of the warning. The earlier result stands.
- **What this does not show.** Only the score matrix (`matrix_df`) was compared, not `class_id_df` or `raw_df`. No aggregation across basins is planned (ring spec: distributions, not aggregates), so the open question is structural: the row-building steps (`aggregate_b1` to `b5`, backfill, `assemble_payload`) are written for a basin set of any size and would combine several basins. Using the set route would mean one `attach_values` call and then those steps once per basin, each on that basin's slice of the shared frames. Whether they run from the shared frames and give the same rows as the single-basin path was not tested. A rough estimate, not a measurement: cell 5 gives about 1.25 s per basin end to end and this cell about 1.15 s for `attach_values` alone, leaving about 0.1 s per basin for everything else. L8 reads precomputed scores (`basin08_scores`) and was not measured.

### 1f. Weight of a compact neighbour row (cell 8)

Compact row keys: `variable`, `method`, `status`, `representative_score`, `representative_raw`, `weight_at_zero` (no detail, no histograms, no units or names). Sizes are minified JSON (no spaces), so they are a little below cell 5's figures. Projected total = full centre payload + compact neighbour rows + per-neighbour metadata (id, area, shared_km, bearing).

| Place | Neighbours | Centre KB | Full neighbour KB (mean) | Compact neighbour KB (mean) | Projected total KB | Projected gzip KB |
|---|---|---|---|---|---|---|
| Timbuktu | 5 | 20.1 | 20.2 | 7.7 | 59.0 | 4.4 |
| Tbilisi | 9 | 20.1 | 20.2 | 7.7 | 90.3 | 5.9 |
| Santa Fe | 7 | 20.1 | 20.1 | 7.7 | 74.3 | 5.3 |
| Kaifeng | 7 | 20.1 | 20.1 | 7.7 | 74.3 | 4.9 |
| Lviv | 12 | 20.2 | 20.2 | 7.7 | 113.7 | 6.4 |
| Poltava | 4 | 20.1 | 20.1 | 7.6 | 51.0 | 3.9 |
| Chaco Canyon | 7 | 20.2 | 20.2 | 7.7 | 74.7 | 4.8 |
| Alexandria | 5 | 20.0 | 20.1 | 7.6 | 58.6 | 4.2 |
| Utqiagvik | 3 | 20.1 | 20.1 | 7.6 | 43.2 | 3.4 |

- A compact neighbour (52 rows) weighs 7.6 to 7.7 KB, about 148 bytes per row, against 20.1 to 20.2 KB for a full detail-off signature (62% smaller). Basin payloads are the same size to within 0.2 KB at every place (52 rows each).
- Projected ring payloads: 43 to 114 KB uncompressed (full detail-off rings: 89 to 290 KB in cell 5), 3.4 to 6.4 KB gzipped (full detail-off: 3.8 to 8.8 KB). Compacting cuts the uncompressed size by 51 to 61% and the gzipped size by 11 to 27%. (The comparison is against cell 5, which used JSON with spaces, so both cuts are slightly overstated.)
- This is the second gzip figure asked for in 1c: the projected payload compresses about 13 to 18 to 1, the full payload 23 to 33 to 1 (cell 5). The high ratio there is consistent with the repeated structure across neighbour signatures; the compact payload has less of it to exploit.
- The projection uses the same row-per-variable layout as today (key names repeated in every row); other layouts were not tried.

### 1g. Population sample: ring counts, area spread, corner-only contacts (cell 9)

`resolve_basin_ring` at L6 for the 306 distinct L6 basins of the WO-02 sample (stratified by climate zone; **unweighted** here, so not a world rate). 0 errors; whole run 4.7 s (median 11 ms per resolve, maximum 73 ms). Per-basin results in `output/edop/whg/q1_population_ring.csv`.

| Neighbours | Cores | | Neighbours | Cores |
|---|---|---|---|---|
| 0 | 8 | | 8 | 16 |
| 1 | 2 | | 9 | 16 |
| 2 | 8 | | 10 | 7 |
| 3 | 34 | | 11 | 1 |
| 4 | 54 | | 12 | 4 |
| 5 | 66 | | 14 | 1 |
| 6 | 51 | | 15 | 2 |
| 7 | 35 | | 18 | 1 |

- Mean 5.49, median 5, 10th to 90th percentile 3 to 9, maximum 18. 8 cores (2.6%) have no neighbour, 18 (5.9%) have two or fewer, 16 (5.2%) have ten or more.
- Area ratios (neighbour area / core area, 298 cores with at least one neighbour): largest neighbour median 3.64, 10th percentile 1.03, 90th percentile 27.6, maximum 2,904; smallest neighbour median 0.256, 10th percentile 0.013, 90th percentile 2.55, maximum 1,023.9 (a core whose smallest neighbour is 1,000 times its size). Heavy right tail (mean 24.3 and 6.7).
- **Corner-only contacts: 23 of 306 cores (7.5%) have at least one neighbour with `shared_km` = 0**, against none of the nine test places. How many neighbours in total, and whether the zero is a point contact or a border under 5 m (the SQL rounds the length in km to 2 decimals, so a 4 m border also reads 0.0), is not known from this cell.
- Not yet looked at: where the 8 cores with no neighbour are, and what the extreme area ratios are (the 2,904 and 1,023.9 rows).

### 1h. Which rows are `outside_active_domain` or `no_data`, centre versus neighbours (cell 10)

**What the status means (read from `engine.py`, B1 guard at about lines 2055 and 2134):** a zero-heavy variable (global zero fraction at or above a threshold) whose basin weight at zero is at least 0.90 gets status `outside_active_domain` and no score. For a single basin that is the basin's own value being zero. It is the "zero here" case of WO-02's Position family, not an inapplicable variable.

Variables that appear as `outside_active_domain` in these rings: `cropland_extent`, `pasture_extent`, `karst`, `permafrost_extent`, `wet_pct_grp1`, `wet_pct_grp2`, their `_upstream` pairs, and `dist_sink`.

| Place | Centre outside | Neighbours with the same set as the centre |
|---|---|---|
| Timbuktu | 4 | 2 of 5 |
| Tbilisi | 7 | 4 of 9 |
| Santa Fe | 3 | 0 of 7 |
| Kaifeng | 5 | 2 of 7 |
| Lviv | 7 | 11 of 12 |
| Poltava | 7 | 1 of 4 |
| Chaco Canyon | 7 | 2 of 7 |
| Alexandria | 4 | 0 of 5 |
| Utqiagvik | 7 | 3 of 3 |
| All | | 25 of 59 |

- **34 of 59 neighbours differ from the centre in which variables are at zero.** Typical case: a variable at zero in the centre and non-zero in some neighbours (Santa Fe `wet_pct_grp1` and `wet_pct_grp2`: outside in the centre, active in 4 of 7 neighbours), or the reverse (Alexandria neighbour 1060044570: `cropland_extent`, `pasture_extent`, `wet_pct_grp1`, `wet_pct_grp1_upstream`, `wet_pct_grp2` and `wet_pct_grp2_upstream` outside there; not outside in the centre).
- **`dist_sink` is outside wherever `dist_sink` = 0, which includes every outlet basin.** Over all 16,397 L6 basins: `next_down` = 0 and `dist_sink` = 0 in 5,149; `dist_sink` = 0 with `next_down` not 0 in 319 (two examples checked, 7060074010 and 7060074140, both `endo` = 2); `next_down` = 0 with `dist_sink` not 0 in none. So 5,468 basins (33%) have `dist_sink` = 0. Alexandria and Utqiagvik (outlets) and the three Tbilisi neighbours 2060005120, 2060005130, 2060005270 (`next_down` = 0) show it.
- **`no_data` rows (7, all in neighbours, coverage 0.0, empty caveat):** `wetland_class` at Lviv 2060374800 and 2060374710, Chaco Canyon 7060618130 and Alexandria 1060044570; Alexandria 1060044570 also `pct_clay_upstream`, `pct_sand_upstream`, `pct_silt_upstream`. The centre has no `no_data` row at any place. Why: in `basin06` the raw `wet_cl_smj` is -9999 (the source NoData value) for all four basins, and Alexandria 1060044570 also has -9999 in `cly_pc_uav`, `snd_pc_uav` and `slt_pc_uav`; the other three basins have real soil values (checked 2026-11-02). The `class_id_df` frame returned by `attach_values` is read straight from the raw table, so it holds the integer -9999 for these four basins, whereas the score and raw-label frames hold None. The result row is correct (`no_data`, coverage 0.0) because the categorical row-builder counts a basin only if its class id is in the label map, and -9999 has no label (`engine.py` around lines 1405 to 1420). See I-3.
- For the later "core and surroundings" rules, the descriptive fact is that for the zero-heavy variables a ring is a mix of basins at zero and basins with a score, and which basins are at zero varies by variable; counts per variable would be needed.

### 1i. Border facts per neighbour (cell 12)

1,739 (core, neighbour) pairs: 59 at the nine test places and 1,680 in the 306-basin sample (the 8 sample cores with no neighbour contribute none); 0 resolver errors, 0 pairs without an SQL row. One SQL pass for the intersection of each pair (`ST_Intersection`, length on the geography). Pair table: `output/edop/whg/q1_pairs.csv`.

**Intersection type:** MultiLineString 1,700; Point 26; LineString 9; GeometryCollection 4 (a border plus a point contact).

**Border length (metres):**

| Length | Pairs |
|---|---|
| 0 (point contact) | 26 |
| 0 to 5 m | 0 |
| 5 to 50 m | 0 |
| 50 to 500 m | 9 |
| 0.5 to 5 km | 82 |
| 5 to 10 km | 79 |
| over 10 km | 1,543 |

- **Corner-only contacts are point contacts.** The 26 pairs (1.5%) with engine `shared_km` = 0, in 23 of the 306 sample cores (7.5%, as counted in cell 9), are all `ST_Point` intersections of exactly 0 m, not short borders rounded to zero. There is no pair with a border between 0 and 50 m. The engine's `shared_km` equals the length in metres rounded to 2 decimals in all 1,739 pairs (0 differ by more than 0.01 km).
- **Short real borders (I-1):** 170 pairs (9.8%) have a border from 50 m to 10 km; with the point contacts, 196 of 1,739 (11.3%) have under 10 km of border; 88.7% have more than 10 km. As a share of the core's perimeter (1,713 pairs with a line border): median 0.134, mean 0.164, 5th percentile 0.0083, 10th 0.0183, 90th 0.350, minimum 0.0001, maximum 1.0000. A maximum of 1.0000 means a neighbour whose shared border is the core's whole perimeter to four decimals; not looked at.
- **Bearing gap (`border_bearing` versus `centroid_bearing`, degrees):** mean 20.0, median 12.7, 90th percentile 46.7, 99th 120.0, maximum 174.6; 38 pairs (2.2%) above 90 degrees. Ten largest: core 9060039120 appears three times (with 9060050190, 174.6; 9060050220, 163.5; 9060039150, 135.0), then 2060961520/2060953770 (166.6), 9060017070/9060017060 (156.9), 9060082790/9060083650 (156.0), 9060040100/9060041690 (147.9), 9060124670/9060005760 (147.6), 8060038790/8060036730 (146.6), 4060464220/4060465510 (133.1).
- **Distance from `border_mid` to the shared border:** mean 2,457 m, median 1,313 m, 90th percentile 6,276 m, 99th 15,020 m, maximum 36,285 m (core 5060276150 with neighbour 5060087780, a 142.8 km border). More than 1 km in 994 pairs (57%), more than 10 km in 77 (4.4%). **The offset does not account for the large bearing gaps:** for the 38 pairs with a gap over 90 degrees the median offset is 1,217 m, against 1,315 m for the other pairs.

### 1j. Bearing origin (notebook `wo03_q1b_bearing_origin.ipynb`)

The resolver measures `border_bearing` (to the shared-border midpoint) and `centroid_bearing` (to the neighbour's interior point) from the **centroid of the core basin** (`ST_Centroid`), not from the place's point. Recomputed from the place point, over the same 1,739 pairs. Test places use their real coordinates; sample cores use the point the WO-02 harvest queried (`ST_PointOnSurface` of the core), which is inside the basin but not at the centroid, so the sample is a stand-in for a settlement and probably understates the shift for real places. Compass words: 8-point (45 degree sectors centred on N, NE, ...) and 4-point (90 degree sectors). Table: `output/edop/whg/q1_bearing_origin.csv`.

**Origin shift** (307 cores: 298 sample cores with at least one neighbour plus the 9 test cores): the core centroid lies outside its own core for 10 cores (3.3%). Distance from the place point to the core centroid: median 8.3 km, 10th to 90th percentile 2.1 to 33.1 km, mean 14.7 km, maximum 127.5 km. As a share of the square root of the core area: median 0.112, 90th percentile 0.375, maximum 1.615.

**Circular difference between bearings (degrees):**

| Comparison | Median | 90th percentile | 99th percentile | Maximum |
|---|---|---|---|---|
| engine `border_bearing` vs place to the same `border_mid` (origin changed only) | 5.3 | 22.2 | 98.1 | 177.3 |
| engine `border_bearing` vs place to the nearest point of the shared border | 13.5 | 51.0 | 95.5 | 142.3 |
| engine `centroid_bearing` vs place to the nearest point of the shared border | 17.3 | 60.5 | 120.5 | 177.0 |

**Share of pairs whose compass word differs:**

| Comparison | Pairs | n | 8-point | 4-point |
|---|---|---|---|---|
| engine border vs place to `border_mid` | all | 1,739 | 20.4% | 11.4% |
| | test | 59 | 61.0% | 47.5% |
| | sample | 1,680 | 19.0% | 10.1% |
| | centroid outside core | 55 | 41.8% | 18.2% |
| engine border vs place to nearest border point | all | 1,739 | 40.3% | 23.9% |
| | test | 59 | 59.3% | 40.7% |
| | sample | 1,680 | 39.6% | 23.3% |
| | centroid outside core | 55 | 41.8% | 25.5% |
| engine centroid vs place to nearest border point | all | 1,739 | 45.3% | 26.5% |
| | test | 59 | 54.2% | 25.4% |
| | sample | 1,680 | 45.0% | 26.5% |
| | centroid outside core | 55 | 47.3% | 32.7% |
| engine border vs engine centroid | all | 1,739 | 37.3% | 20.8% |
| | test | 59 | 39.0% | 18.6% |
| | sample | 1,680 | 37.2% | 20.9% |
| | centroid outside core | 55 | 40.0% | 30.9% |

- The first comparison changes only the origin. The second and third also change the target (nearest point of the border rather than its midpoint), which is a different question, so they are not errors of the engine's choice. The test-place rows rest on 59 pairs from 9 places (not independent); the 55 "centroid outside core" pairs are from 10 cores.
- Distance from the place point to the shared border (per pair): median 43.1 km, 10th to 90th percentile 9.8 to 122.7 km, minimum 0.04 km, maximum 383.4 km.
- **Compass words at the nine test places (59 neighbours):** all four methods give the same 8-point word for 11 (19%): Chaco Canyon 3 of 7, Timbuktu 2 of 5, Lviv 2 of 12, Kaifeng 1 of 7, Poltava 1 of 4, Santa Fe 1 of 7, Tbilisi 1 of 9, Alexandria 0 of 5, Utqiagvik 0 of 3. Examples where words are 90 degrees or more apart: Utqiagvik 8060008020 (272 km border: engine NE, place to midpoint SW, nearest border point S, centroid SE), Tbilisi 2060616770 (SE, W, S, SE), Kaifeng 4060694190 (N, E, E, E), Lviv 2060444020 (S, NW, W, S), Lviv 2060464310 (S, E, SE, S), Kaifeng 4060676710 (W, S, S, SW). Not counted exactly how many of the 59 have words 90 degrees or more apart.
- Not established: whether border length or neighbour shape predicts disagreement. The examples go both ways (Alexandria 1060034270 with a 3.1 km border splits four ways; Chaco Canyon 7060674060 with a 119 km border agrees in all four).

### 1k. Few-neighbour cores, extreme area ratios, coast and endorheic flags (cell 13)

The 306 sample cores, from `basin06` flags. Coast flag: 53 cores with `coast` = 1, 253 with 0. `endo`: 0 in 250, 2 in 39, 1 in 17 (meaning of 1 versus 2 not looked up).

**Core area (km²):** minimum 0.1, 5th percentile 248.7, 10th 538.3, median 5,259, mean 8,429, 90th 21,111, maximum 55,897. 8 cores under 100 km² (2.6%), 47 under 1,000 km² (15%).

**Neighbour count by coast flag:**

| `coast` | 0 neighbours | 1 to 2 | 3 to 5 | 6 or more |
|---|---|---|---|---|
| 0 (253) | 0 | 5 | 121 | 127 |
| 1 (53) | 8 | 5 | 33 | 7 |

**Cores with a point-contact neighbour (`shared_km` = 0), by coast flag:** `coast` = 0: 1 of 253 (0.4%); `coast` = 1: 22 of 53 (41.5%). 22 of the 23 such cores are coastal. The sample is 17% coastal, and WO-02 rates are for random basins, not settlements, which sit on coasts more often.

**The 18 cores with 2 or fewer neighbours** (nearest = the nearest other L6 basin at any distance):

| Core | Neighbours | Lat, lon | Core km² | `coast` | `endo` | Nearest basin (km²) | Distance m |
|---|---|---|---|---|---|---|---|
| 2060056060 | 0 | 57.597, -13.688 | 0.3 | 1 | 0 | 2060054790 (15,785) | 430,839 |
| 2060059370 | 0 | 60.242, -1.544 | 1,668 | 1 | 0 | 2060054140 (1,254) | 42,317 |
| 2060062160 | 0 | 80.612, 60.733 | 16,036 | 1 | 0 | 2060063930 (46,143) | 375,354 |
| 2060063930 | 0 | 75.112, 58.729 | 46,143 | 1 | 0 | 2060062920 (33,515) | 173 |
| 2060085480 | 0 | 20.429, 58.797 | 717 | 1 | 0 | 2060077480 (3,645) | 13,657 |
| 3060020950 | 0 | 75.342, 81.956 | 498 | 1 | 0 | 3060005240 (5,204) | 104,886 |
| 4060039440 | 0 | 41.003, 139.002 | 0.1 | 1 | 0 | 4060037060 (78,656) | 61,060 |
| 7060057510 | 0 | 53.156, -131.917 | 10,868 | 1 | 0 | 7060057980 (16,412) | 47,722 |
| 1060064750 | 1 | 22.481, 29.931 | 247 | 0 | 2 | 1060040670 (30,516) | 0 |
| 6060037950 | 1 | -54.110, -71.438 | 3,919 | 1 | 0 | 6060038060 (7,384) | 0 |
| 1060058290 | 2 | 28.316, -6.922 | 868 | 0 | 2 | 1060040580 (43,927) | 0 |
| 2060089820 | 2 | 29.855, 63.185 | 1,376 | 0 | 2 | 2060085820 (28,101) | 0 |
| 3060003750 | 2 | 71.179, 76.223 | 3.8 | 1 | 0 | 3060003740 (3,891) | 0 |
| 4060064770 | 2 | 43.095, 105.389 | 234 | 0 | 2 | 4060378180 (11,778) | 0 |
| 5060070680 | 2 | -29.151, 153.402 | 223 | 1 | 0 | 5060070700 (22,150) | 0 |
| 5060087600 | 2 | -18.712, 133.092 | 26.7 | 0 | 2 | 5060282340 (6,208) | 0 |
| 9060001030 | 2 | 75.367, -22.473 | 24,823 | 1 | 0 | 9060001020 (13,015) | 0 |
| 9060017070 | 2 | 81.879, -33.569 | 926 | 1 | 0 | 9060017060 (9,206) | 0 |

- **All 8 cores with no neighbour are coastal** (`coast` = 1, `endo` = 0, `next_down` = 0). Seven have another basin 13.7 to 430.8 km away; by their coordinates several look like islands (not checked). **One, 2060063930, has another basin 173 m away** yet no touching neighbour, so its ring is empty; the ring is by contact only (bears on snap tolerance, ring spec question 1). Of coastal cores, 13 of 53 (25%) have two or fewer neighbours; of inland cores, 5 of 253 (2%).
- **The extreme area ratios belong to tiny cores.** The five largest `max_ratio` are cores of 3.8, 11.4, 16.7, 26.7 and 58.8 km² (ratios 2,904, 271, 657, 232, 241); the 3.8 km² core (3060003750, 2 neighbours, coastal) is both the largest `max_ratio` (2,904) and the largest `min_ratio` (1,024). The five largest `min_ratio` are 1,024, 232, 189, 123 and 70.
- **Core 5060087600:** 26.7 km² but `up_area` 78,249.7 km² (inland, `endo` = 2, `next_down` = 0). Not looked at further.
- Whether signature values for cores of a few km² (or 0.1 km²) are reliable was not examined.

### 1l. Which variable says "coastal" (notes, 2026-11-02)

- **Flag used above:** `basin06.coast` (BasinATLAS `coast`, "Basin touches coast"), the source of the signature rows `coast_fraction` (0 or 1 for a single basin) and, with `endo`, `outlet_type` (exorheic non-coastal 0, exorheic coastal 1, endorheic inland 10, terminal sink 20, per the catalog's own description; the catalog notes it is an areal-engine output and not emitted by the point signature). `endo` is a raw column of `basin06`/`basin08`; it is not in the BasinATLAS catalog. Definition supplied by Karl 2026-11-02 (source document not named): "Indicator for endorheic (inland) basins without surface flow connection to the ocean: 0 = not part of an endorheic basin; 1 = part of an endorheic basin; 2 = sink (i.e. most downstream polygon) of an endorheic basin." This matches the catalog's `outlet_type` description (1 endorheic inland, 2 terminal sink). Checked against `next_down` over all 16,397 L6 basins: `endo` = 1 (1,570 basins): none points to an `endo` = 0 basin (1,337 point to another `endo` = 1 basin, 233 to an `endo` = 2 sink). `endo` = 2 (1,686 basins): 1,367 have `next_down` = 0; 319 (19%) have a `next_down`, all with `dist_sink` = 0 (136 point at their own `main_bas`, 183 elsewhere), and 267 of those 319 point at an `endo` = 0 basin (52 at an `endo` = 1 basin). See I-8. The coast counts in 1k use this flag, not an estimate.
- **`dist_sink` is not a coast flag.** Over all 16,397 L6 basins: `coast` = 1 in 2,094, and every one has `dist_sink` = 0 and `next_down` = 0; `dist_sink` = 0 in 5,468 basins, of which 2,094 (38%) are coastal. The other 3,374 are outlets that do not touch the coast (3,055) or sinks that are not outlets (319). No basin with `coast` = 1 has `endo` other than 0.
- **The Sandbox (`sandbox.html` about lines 2292 to 2311)** labels `dist_sink` "Distance to ocean outlet" and shows a Drainage type badge: Endorheic if `endo` is not 0; Coastal terminal if `dist_sink` < 1 km, or `coast` set and `dist_sink` < 10 km; otherwise Exorheic interior. Over all L6 basins that gives:

| `endo` | `coast` | Sandbox badge | Basins |
|---|---|---|---|
| 0 | 1 | Coastal terminal | 2,094 |
| 0 | 0 | Coastal terminal | 1,690 |
| 0 | 0 | Exorheic interior | 9,357 |
| 1 or 2 | 0 | Endorheic | 3,256 (1,570 with `endo` 1; 1,686 with 2) |

  1,690 of the 3,784 basins labelled Coastal terminal (45%) have the coast flag at 0. They have `dist_sink` under 1 km. Not examined further: what these basins are. The row is labelled "ocean outlet" for endorheic basins too, where `dist_sink` is the distance to an inland sink.
- **"Island":** there is no island flag; "looks like an island" in 1k is from coordinates and an empty ring, not checked.
- **Offshore points** have no basin, so no flag exists for them (WO-02 issue 1; Tristan da Cunha here).

## Issues found

Open, from the above (none is a verdict):
- **I-1** Neighbours with no or a short shared border (1i): 26 of 1,739 pairs are point contacts (shared border 0, in 23 of 306 cores) and 170 have a border from 50 m to 10 km. The ring includes all of them with the same standing as neighbours with hundreds of km of border.
- **I-2** `border_bearing` and `centroid_bearing` disagree by more than 90 degrees in 38 of 1,739 pairs (1i). `border_mid` lying off the border does not explain it (1i). Cause not established; the shared origin (core centroid, outside the core for 10 of 307 cores) is untested as a cause for the largest gaps.
- **I-3** The class-id frame carries the source NoData value -9999 as an ordinary integer (1h). Correct results today because the label map excludes it; any use of the frame that does not go through the label map (for example counting neighbours that share the core's class) would treat -9999 as a class and match any two basins that both have it. Frequency over the sample not measured.
- **I-4** Bearings are measured from the core's centroid, not from the place's point (1j). The compass word changes in 19% of sample pairs (8-point) and 10% (4-point) when only the origin is moved to the place; 61% and 47.5% at the nine test places (59 pairs). Across four ways of computing a bearing, all four give the same 8-point word for 11 of 59 test-place neighbours.
- **I-5** Rings are by contact only (1k): 8 of 306 sample cores (all coastal) have no neighbour, one of them with another basin 173 m away; 25% of coastal sample cores have two or fewer neighbours, against 2% of inland ones. Point-contact neighbours are 22 of 23 coastal cases (41.5% of coastal cores, 0.4% of inland ones).
- **I-6** Area ratios are unbounded for tiny cores (1k): the largest `max_ratio` is 2,904 and the largest `min_ratio` 1,024, both from cores under 60 km²; 8 of 306 sample cores are under 100 km².
- **I-7** Three notions of "coastal" coexist (1l): the `coast` flag, the Sandbox badge "Coastal terminal" (`dist_sink` under 1 km), and the engine's `outlet_type`. The Sandbox badge and the flag disagree for 1,690 of 3,784 L6 basins labelled Coastal terminal (45%). Whether the Sandbox rule is intentional was not established.
- **I-8** Resolved by the source documentation (supplied by Karl 2026-11-02; document not named): a sink (`endo` = 2) with `next_down` > 0 carries a "virtual" connection, a topological link to an appropriate downstream polygon so that routing queries work in larger basins, not surface flow; "users can decide whether or not to terminate the routing at endorheic sinks". So the 319 of 1,686 L6 sinks with a `next_down` (267 pointing at an `endo` = 0 basin) are by design, and the 5 sample cores whose `next_down` basin is 29 to 432 km away and not a neighbour are such links. Consequence: Q2's first classification (Cell 2) followed virtual links as if they were flow; Q2 Cell 6 re-classes with them cut.

## Q2. Flow relation of neighbours (notebook `wo03_q2_flow.ipynb`)

**Answer:** yes. Each neighbour can be classed upstream, downstream or off the core's stream from `next_down`, with no unknowns. Virtual links (sinks with `endo` = 2 and `next_down` > 0, source documentation) are not surface flow and were cut; no up or down class rested on one. Pair table: `output/edop/whg/q2_flow_pairs.csv`.

- **Classes (sample, 1,680 neighbours):** upstream 208 (12.4%), downstream 200 (11.9%), off-stream 1,272 (75.7%). Indirect ones (reached through 2 or more links) are 3%. With virtual links cut, 30 of 491 pairs once labelled "same main_bas" become "other system".
- **Rings (298 sample rings):** at least one upstream neighbour 91 (30.5%); at least one downstream 173 (58.1%); both 80 (26.8%); neither 114 (38.3%). Test places: Alexandria and Utqiagvik (outlets) have none of either.
- **Completeness:** all 186 basins that drain directly into a core (93 cores) are in its ring. Every core with a real downstream basin has it in its ring; the 5 sample cores whose `next_down` basin is not a neighbour are sinks with a virtual link (319 of 1,686 L6 sinks have one; I-8).
- **`_upstream` values by class** (median over 14 variables of |core score - neighbour score|, percentile points; 1,470 pairs, 269 dropped for having under 5 variables not both zero): upstream 3.5, downstream 3.4, off-stream same system 7.5, off-stream other system 9.1. The ranges overlap (quartiles upstream 1.4 to 7.0, same system 4.3 to 11.7).
- **The class effect is mostly a catchment-size effect.** Upstream neighbours: ratio under 0.5, 5.6; 0.5 to 0.9, 1.8; 0.9 to 1.1, 0.0 (19 pairs). Downstream: 0.9 to 1.1, 0.0 (15 pairs); 1.1 to 2, 1.9; 2 to 10, 4.1; over 10, 7.8 (30 pairs). Off-stream neighbours are flat across ratios (4.6 to 11.2). 34 of 341 flow pairs (10%) have a catchment within 10% of the core's and are the same place on these variables.
- **Three places** (19 pairs): consistent with the above; Santa Fe flow neighbours 3.4 to 5.4 against off-stream 14.4 to 22.2; Timbuktu's near-equal neighbours 0.5 and 0.6; at Kaifeng same-system off-stream neighbours (1.5 to 6.2) are as close as the downstream ones (5.0 and 5.5).
- **Ranks:** the first measure (does the core's rank change when flow neighbours are dropped) was uninformative (14 of 14 at all three places because the denominator changes) and is not used. Ranking by "1 + number above" gives "1st of 6" when every basin is tied at 0 (Timbuktu `karst_upstream`, Kaifeng `wet_pct_grp2_upstream`): a rank rule needs tie handling.
- Limits: 14 `_upstream` variables; percentile points; sample is random basins, not settlements; the 3-place table is 19 pairs.

## Q3. Ecoregions (notebook `wo03_q3_ecoregions.ipynb`)

**Answer:** a basin usually has one or two ecoregions of any size, a ring two or three. Pair table of areas: `output/edop/whg/q3_basin_eco.csv` (3,387 rows, 1,735 basins); per-core summary `q3_core_ring_eco.csv` (307 cores = 298 sample cores with neighbours + 9 test places). Areas are geography areas of basin-ecoregion intersections; 69 invalid ecoregion geometries were repaired with `ST_MakeValid`. The 1,735-basin run took 801 s (the first 200 took 122 s; one stretch, 200 to 400, took 473 s).

- **Ecoregions per core (298 sample cores):** any area: median 2, 90th percentile 3, max 7. At 1% of the core: mean 1.8; at 5%: mean 1.7. At 5%, 146 cores have 1, 111 have 2, 35 have 3, 5 have 4, 1 has 5.
- **Per ring (core plus neighbours):** any area: median 3, 90th percentile 5, max 9; at 5% of the ring: median 2, 90th percentile 4, max 7. 76 rings have 1, 113 have 2, 58 have 3, 31 have 4, 20 have 5 to 7.
- **Largest ecoregion's share of the core:** median 0.92, 10th percentile 0.52, min 0.28.
- **The place's own ecoregion** (sample point = interior point of the basin): exactly one in 297 of 298; it is the core's largest-share ecoregion in 280 of 297 (94.3%). In the 17 others the point is in a smaller ecoregion. Test places: 6 of 9 are in the largest; Alexandria (largest share 0.69), Timbuktu (0.69), Tbilisi (0.79) are not.
- **Test places, ring versus core:** core 1 to 5 ecoregions, ring 2 to 7 (Alexandria 3 to 5, Tbilisi 3 to 7); at 5% the ring is 2 to 4 (Alexandria 2, Tbilisi 3). Timbuktu's neighbours add none.
- **Coverage gaps (share of core or ring inside any ecoregion polygon):** median 1.0, mean 0.991, minimum 0.709 (core) and 0.713 (ring). 9 sample cores are under 90% covered: 8 have the coast flag (uncovered 10% to 28%, probably sea beyond the polygons; shapes not inspected), and 1 (7060400750, centre 45.0, -80.0, coordinates in Georgian Bay; not checked on a map) has 29% uncovered and is the one sample point that falls in no ecoregion (nearest polygon 6.8 km away). Sample points are interior points of basins, so one can land on a lake; a settlement would not.
- **Wikipedia text:** 821 of 847 ecoregions have a link and a summary; 26 have neither (Nearctic 10, Afrotropic 6, Antarctica 5, Palearctic 3, Neotropic 1, Australasia 1; e.g. Renosterveld, Cross-Timbers, Gariep Karoo, five Antarctic tundras, Queen Charlotte Islands conifer forests). Every `eco_wikitext` row matches an ecoregion. The point's ecoregion lacks text in 3 of 306 cores, the core's largest in 4 of 307.
- Limits: sample is random basins, not settlements; ecoregion shares are by area only (position not measured); no Wikipedia summaries were read.

Notes for the algorithm stage (not measured here):
- Basins and ecoregions are drawn independently, so a basin often spans several ecoregions (median 2 in the sample). The count, each piece's compass position within the basin, and what each ecoregion is look useful as setting context for a place. Position was not measured in Q3 (EDA only); if built, measure bearings from the place (see 1j).
- Karl's hypothesis for the 26 ecoregions without Wikipedia text (not checked): articles may exist under changed names, since the ecoregion-to-article mapping was not done exhaustively; and OneEarth may have added or renamed ecoregions when it took over from WWF stewardship. A check would compare these 26 names with Wikipedia titles and with the WWF 2001 ecoregion list.
- A description rule needs a cutoff (any, 1%, 5%) and a way to handle the uncovered share (coastal and lake basins).

## Q4 to Q6

Not started (Q4 on hold).