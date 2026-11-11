# WO-02 (regionality) results: GEDA stored; what a basin query returns on the fly

2026-11-11. Spec: `wo02_store_GEDA.md`. Notebook: `notebooks/edop/regionality/wo02_geda_store_and_aggregate.ipynb` (Cells 1 to 15, with 4a; outputs saved in it). Load script: `scripts/edop/regionality/load_geda.py`. The database is the local dev instance (Postgres.app); the server load is a separate step. Numbers are from notebook output Karl ran. No thresholds or verdicts. A plain-language summary is in `wo02_summary.md`. Figures (gitignored, `output/edop/regionality/`): `wo02_item6_distribution.png`, `wo02_item7_8_lines.png`, `wo02_item11_geda_vs_lmr.png`.

## Read first

1. **GEDA is stored** as `temporal.geda_climate`: 28,970 cells, 1,021 annual values each, checked against the file. Loading the table was done through the loader; no engine, API or app change was made.
2. **A basin query through the LMR path works for GEDA.** The same overlap weights, weighted mean and histogram give a line with a p10 to p90 band for 1000 to 2020, and spans clip as they do for LMR. It is fast (0.01 s for the whole record).
3. **Cells inside a basin are highly correlated** (mean correlation 0.64 to 0.97), so the weighted-mean line is only 1% to 15% narrower than a single cell's series. Re-standardizing the line against the basin's own record changes it by at most 17%.
4. **The mean hides real within-basin spread.** In a typical year the p10 to p90 width is 0.6 to 1.2 standard-score units; for Tbilisi's basin it is wider than the whole series' SD. This supports delivering the distribution, not only a mean.
5. **Basins with few cells or partial coverage return numbers that mean less than they look.** One cell gives a single-point "distribution"; a basin 6.7% covered by GEDA still returns a value. The block would need a coverage status and a flag for observed years (see "What a GEDA block would need").
6. **GEDA and LMR do not track each other** on the same basin (Kyiv, 1300 to 1400: r = -0.39; SD 1.04 against 0.31).

## Part A: store

**Provenance.** `data/geda/geda_trim.nc` has md5 `b05338614a43627b43acb878d860fb6a`, which equals the value given in the WO for the Zenodo record (10.5281/zenodo.11059894, CC BY 4.0, deposit by the authors). The Zenodo page itself was not consulted.

**Table `temporal.geda_climate`** (following `lmr_climate`, with `hyde_cells` additions):

| Column | Type | Notes |
|---|---|---|
| `id` | serial primary key | as `lmr_climate` |
| `lat`, `lon` | real | cell centres; `lon` is -180 to 180 (LMR stores 0 to 360), so no wrap is needed |
| `scpdsi` | real[] | 1,021 values; position k is year 999 + k (k = 1 is 1000 CE). LMR's arrays are indexed by year + 1 |
| `geom` | geometry(Point, 4326) | GiST index; btree on (`lat`, `lon`) as for LMR |
| `cell_geom` | geometry(Polygon, 4326) | the 0.5 degree box, GiST index; avoids building an envelope for every cell on each query (LMR builds ±1 degree envelopes at query time) |
| `area_km2` | real | geography area of the box, as in `hyde_cells` |

The fill value (9.969209968386869e+36, stored as data in the file) and NaN are masked; only the 28,970 cells with values are stored. Values are as distributed: z-scores per cell against 1000 to 2020. Total size 176 MB (LMR's table is 321 MB).

**Checks after loading:** 28,970 cells (file: 28,970); series length 1,021 for every cell (years 1000 to 2020); lat 0.25 to 78.25, lon -21.75 to 179.75; values min -4.990, max 5.803, mean 0.0000, SD 1.0000, equal to the file after masking; the Kyiv cell (50.25, 30.75) and the Tbilisi cell (41.75, 44.75) equal the file within 1e-5, including 2010 (0.139 and 2.721); 300 random cells compared with the file: 0 differ.

**Metadata.** A table comment on `temporal.geda_climate` records product, units, grid, years, the observed 1990 to 2020 note, the position-to-year rule, and citations (Karl chose to add it to this table only; no other table in `temporal` or `gaz` has one, and 17 of 55 in `public` do). A GEDA section was added to `docsite/data-sources.md` (commit 4f8d0f0), marked "stored in the EDOPS database; not yet returned by the API or the Sandbox". Catalog rows and a caveat text belong to the WO that adds the Band T block.

**The first load failed** on the `COMMENT ON TABLE` statement (it cannot take a bind parameter) before committing; the loader was fixed and rerun.

## Part B: what is delivered now

### 5. LMR and HYDE for a basin (the Kyiv basin 2060448220, 28,495 km², three LMR cells, 500 to 600 CE)

`engine.aggregate_band_t` called with the basin polygon as `geom_wkt` (the path a single-basin signature uses):

- **323 rows:** 101 years × 3 LMR variables (PDSI, air, precipitation), 12 eVolv2k events, and 2 HYDE epochs (500, 600) × 4 land-use variables.
- **The line:** the value for each year is the weighted mean of the cells. For 550 the engine's 0.8361 equals the mean rebuilt from the cells (0.8361). Weights are overlap area divided by the cell's own area, normalized to sum to 1.
- **The cells for 550:** three LMR cells overlap; weights 0.504, 0.488 and 0.008 (the third has 0.7% of its area in the basin), so "three cells" is effectively two. Effective cells (the sum of the overlap fractions) 0.893. The engine does not report this number for LMR.
- **The band and the distribution:** p10, p90, min, max, mean and a `low_resolution` flag are held in `detail['distribution']` for LMR rows (for HYDE rows p10, p90, SD and effective cells are also at the top of `detail`). For 550: p10 0.808, p90 0.852, min 0.808, max 0.999. `low_resolution` is True in all 101 years (effective cells below the engine's threshold of 5). The histogram's min and max are unweighted: a cell with 0.8% weight set the maximum.
- **Coverage** 1.000; status "ok" and the `lmr_caveat` on every LMR row; the LMR block always sets status "ok".
- **HYDE** for the same basin: 600 cells, effective cells 507.1, coverage 0.989; cropland 441 km² (500) and 471 km² (600).
- **The display** (from `sandbox_cheatsheet.md` §4.3): a histogram of footprint values for a chosen year, a year slider and a small time series (mean line with a p10 to p90 band). No percentile for any Band T row.

Ukraine's 99 L6 basins by number of LMR cells overlapping: 1 cell: 22, 2: 34, 3: 13, 4: 22, 5: 5, 6: 3. So 56 of 99 have one or two LMR cells.

### 5a. Cliopatria over Ukraine

`gaz.clio_polities` has one row per polity slice (15,690 slices, 1,618 polities). Against the Ukraine outline (`gaz.admin0`, a modern border used as a study-area outline for earlier periods): 1,401 slices and 111 distinct polities overlap (slivers included); 20 polities cover 50% or more of Ukraine in at least one slice, 27 cover 25% or more, 48 cover 10% or more, 79 cover 1% or more. Parents and components both appear, so shares overlap (the sum of shares is 2.07 at 1400).

| Year | Largest single slice over Ukraine | Share |
|---|---|---|
| 0 | Greek City-States | 0.009 |
| 300 | Gothia | 0.630 |
| 400 | Huns | 0.804 |
| 500 | Eastern Roman Empire | 0.001 |
| 600 | Avar Khaganate | 0.794 |
| 700 and 800 | Khazaria | 0.195 and 0.194 |
| 900 | Kievan Rus' | 0.320 |
| 1000 | Kievan Rus' | 0.427 |
| 1100 and 1200 | Halych-Volhynia occupation | 0.420 |
| 1300 | Golden Horde | 0.832 |
| 1400 | (Polish-Lithuania Kingdom) | 0.744 |
| 1500 | House of Jagiellon | 0.597 |
| 1600 and 1700 | Polish-Lithuanian Commonwealth | 0.452 and 0.361 |
| 1800 and 1900 | Russian Empire | 0.849 and 0.876 |
| 2000 | Ukraine | 0.980 |

At 0, 100, 200 and 500 CE no polity covers more than about 1% of Ukraine. From the 13th century one polity usually dominates, but its polygon is a large area that includes much more than Ukraine, and the polity changes from slice to slice. So the polity path gives areas that overlap Ukraine, not Ukraine itself.

**Aside (Cell 4a, not in the WO): is the count ordinary for Europe?** For the 48 European countries with an overlapping slice, counting polities (names merged for parent and component) that cover at least 1% of the country: Ukraine 73 (60 within 1000 to 2000 CE), fifth of 48, behind Germany 114, France 112, Italy 95 and Poland 76; per 100,000 km² it ranks 34th of 38 (12.8; median 48.7). Among countries of 250,000 to 1,000,000 km²: Germany 114, France 112, Italy 95, Poland 76, Ukraine 73, Spain 69, Sweden 20, Norway 17, Finland 13. Ordinary for a large continental country. No query needed the fallback and no slice was skipped after `ST_MakeValid`.

## Part C: notebook experiments

Test basins: Kyiv 2060448220 (28,495 km², the WO's "large Ukraine basin" is the same basin); Tbilisi 2060616700 (23,285 km²); a second large Ukraine basin 2060469830 (22,802 km², entirely inside Ukraine; added because the WO's two examples coincided); the small Ukraine basin 2060467040 (1,667 km²); the edge basin 1060044120 (9,184 km², Libyan Sahara at 28.82 N, 20.02 E, coverage 0.498). The GEDA block is an adapted copy of the LMR block in `aggregate_band_t` (Cell 6) that uses the engine's own `_weighted_histogram`.

| Basin | Cells overlapping | Cell centres inside | Effective cells | Coverage | Top three weights |
|---|---|---|---|---|---|
| Kyiv | 27 | 13 | 14.25 | 1.000 | 0.070, 0.070, 0.070 |
| Tbilisi | 25 | 12 | 10.08 | 1.000 | 0.099, 0.094, 0.090 |
| Large Ukraine 2 | 22 | 11 | 11.04 | 1.000 | 0.091, 0.091, 0.091 |
| Small Ukraine | 6 | 0 | 0.82 | 1.000 | 0.460, 0.245, 0.153 |
| Edge | 5 | 2 | 1.70 | 0.498 | 0.478, 0.249, 0.249 |

These agree with WO-01's counts for the Ukraine basins, found by a different query. Footprint edge: of 6,630 L6 basins overlapping GEDA cells, coverage (share of the basin inside GEDA cells with values) is below 0.99 for 473, below 0.9 for 295, below 0.7 for 205, below 0.5 for 150, below 0.3 for 94 and below 0.1 for 46.

### 6. The distribution per year

| Basin | 1350: weighted mean | p10 to p90 | min to max | low_resolution |
|---|---|---|---|---|
| Kyiv | -0.408 | -0.567 to -0.261 | -0.994 to -0.174 | False |
| Tbilisi | 0.110 | -1.279 to 1.038 | -1.675 to 1.606 | False |
| Large Ukraine 2 | -0.440 | -1.175 to 0.215 | -1.421 to 0.360 | False |
| Small Ukraine | -0.582 | -0.649 to -0.426 | -0.649 to -0.352 | True |
| Edge | 0.834 | 0.671 to 0.907 | 0.657 to 1.009 | True |

For 2010 (observed): Kyiv 0.224 (-0.070 to 0.654), Tbilisi 2.602 (2.287 to 2.820; all 25 cells positive, 1.96 to 2.91), Large Ukraine 2 0.181 (-0.328 to 0.787), Small Ukraine 1.419 (1.380 to 1.433), Edge -2.001 (-2.157 to -1.924). In Tbilisi's basin in 1350 the mean of 0.11 conceals cells from -1.7 to +1.6; Kyiv's cells sit in a narrow peak with one stray low-weight cell (the figure `wo02_item6_distribution.png`). For few-cell basins the weighted mean falls in an empty gap between histogram bars. The min and max are unweighted extremes: in the edge basin a cell of weight 0.000 sets the minimum, and in Kyiv's basin the minimum (-0.994) comes from a low-weight cell, so a panel should show p10 to p90, not min and max.

### 7. The summary line and its spread; 8. The re-standardized alternative

| Basin | Cells | Effective | SD of the weighted-mean line | Ratio to the cells' SD (1.0) | Times to reach SD 1 | Mean correlation between cells | Median p10 to p90 width | Years flagged low-resolution |
|---|---|---|---|---|---|---|---|---|
| Kyiv | 27 | 14.25 | 0.951 | 0.951 | 1.05 | 0.882 | 0.605 | 0% |
| Tbilisi | 25 | 10.08 | 0.854 | 0.854 | 1.17 | 0.640 | 1.177 | 0% |
| Large Ukraine 2 | 22 | 11.04 | 0.948 | 0.948 | 1.05 | 0.863 | 0.717 | 0% |
| Small Ukraine | 6 | 0.82 | 0.993 | 0.993 | 1.01 | 0.970 | 0.192 | 100% |
| Edge | 5 | 1.70 | 0.982 | 0.982 | 1.02 | 0.918 | 0.349 | 100% |

The weighted mean of zero-mean cells has mean zero, so the re-standardized line is the same shape stretched by the "times" factor, not shifted. Selected years, raw and re-standardized: Kyiv 1350 -0.408 / -0.429, 2010 0.224 / 0.236; Tbilisi 1350 0.110 / 0.128, 2010 2.602 / 3.046; Large Ukraine 2 1350 -0.440 / -0.463; Small Ukraine 1816 1.734 / 1.746; Edge 2010 -2.001 / -2.036. The two lines nearly coincide (`wo02_item7_8_lines.png`); the difference is largest where the cells disagree (Tbilisi). The p10 to p90 band varies year to year (wide around 1965 to 1975 in Kyiv's basin) and is nearly a line for the small and edge basins.

### 9. Small and edge basins

| Case | Basin (km²) | Cells | Cell centres | Effective cells | Coverage | 1350: mean (p10, p90; min, max) | low_resolution |
|---|---|---|---|---|---|---|---|
| One cell | 4060029310 (986) | 1 | 1 | 0.324 | 1.000 | -0.865 (all five statistics equal) | True |
| Two cells | 2060693490 (1,754) | 2 | 1 | 0.717 | 1.000 | 1.020 (0.996, 1.032; 0.996, 1.040) | True |
| Coverage below 10% | 1060264990 (37,000) | 3 | 0 | 0.886 | 0.067 | 1.226 (-0.146, 1.633; -0.146, 1.770) | True |
| Outside the footprint | 1061132570 (55,432) | 0 | none | none | none | no rows returned (absent, not zero) | none |

For the one-cell basin the "distribution" is a single point. For the basin 6.7% covered the block returns a value that describes under a tenth of the basin; the LMR block would label it status "ok" (status `low_coverage`, which exists, is not used by it).

### 10. Year ranges

Spans for the Kyiv basin, GEDA against the engine's LMR rows:

| Span asked | GEDA rows (years) | LMR rows (years) |
|---|---|---|
| 1300 to 1400 | 101 (1300 to 1400) | 101 |
| 1350 to 1350 | 1 | 1 |
| 900 to 1100 | 101 (1000 to 1100) | 201 (900 to 1100) |
| 990 to 1010 | 11 (1000 to 1010) | 21 (990 to 1010) |
| 2000 to 2100 | 21 (2000 to 2020) | 0 |
| 2015 to 2025 | 6 (2015 to 2020) | 0 |
| 500 to 600 | 0 | 101 |
| 2030 to 2040 | 0 | 0 |

A span that partly overlaps the data is clipped; one entirely outside returns nothing, as for LMR. A span reaching 1990 or later mixes reconstructed and observed years, and a row does not say which. Timings, best of three, for Kyiv and Tbilisi respectively: the block's query for 1000 to 2020 0.01 s and 0.01 s; the per-year rows (one run) 0.03 s and 0.03 s; the block plus rows for 1300 to 1400 0.01 s and 0.01 s; the engine's whole Band T call (LMR, HYDE and eVolv2k, so an upper bound for LMR alone) 0.08 s and 0.07 s.

### 11. Next to LMR (Kyiv basin, 1300 to 1400)

GEDA: 27 cells (effective 14.25), `low_resolution` in 0% of years; LMR: 3 cells, in 100% of years. SD over the span: GEDA 1.036, LMR 0.306. Pearson r between the two lines: -0.394. Median p10 to p90 width: GEDA 0.493, LMR 0.040. Every tenth year, GEDA against LMR: 1300 -1.195 / 0.218; 1330 1.118 / 0.158; 1350 -0.408 / 0.688; 1360 -0.980 / 0.754; 1380 1.379 / -0.418; 1400 1.555 / -0.003. GEDA is a standard score and LMR an anomaly in PDSI units, so the scales differ. LMR's three cells are nearly identical, so its band is almost a line; its histogram is two bars and a sliver, with the mean in the gap between them (`wo02_item11_geda_vs_lmr.png`). WO-01 found the two uncorrelated over Ukraine as a whole.

### 12. The 1990 check

The 68 L6 basins at least half inside Ukraine; 34 windows of 30 years (1000 to 1029 ... 1960 to 1989, then 1990 to 2020), 33 adjacent pairs.

- The difference of means, 1990 to 2020 minus 1960 to 1989, across basins: minimum -0.683, median -0.456, maximum +0.081 (negative in all but one basin).
- The other adjacent pairs: median absolute difference 0.281 across basins; the largest anywhere 1.296.
- Rank of the 1990 pair among the 33 pairs by absolute difference (1 = largest): top three in 1 basin, ranks 4 to 10 in 18, rank 11 or lower in 49.
- Ukraine-wide average of these basins: the 1990 pair difference -0.396 against a median absolute difference of 0.178 for the other pairs; rank 11 of 33.
- Between-cell spread (median p10 to p90 width), from 1990 against before: ratio across basins 0.55 (10th percentile), 0.86 (median), 1.29 (90th). Of the ten largest basins, three narrow sharply (ratios 0.41, 0.41, 0.47), four widen (1.03 to 1.39), Kyiv's is unchanged (1.00). This was not in the WO; it was added because Tbilisi's figure looked narrower after about 2000. Tbilisi itself was not tested.

## What a GEDA block would need (changes described, none made)

1. **A GEDA block in the Band T aggregator**, beside LMR's: footprints from `temporal.geda_climate.cell_geom` (not envelopes built from lat/lon), array position year - 999, years 1000 to 2020 clipped as LMR's are, one variable, a new unit type (`geda_cell`; the engine's histogram already treats any non-basin unit type as cells), longitudes need no wrap. Tested here as an adapted copy; it runs in 0.01 s.
2. **A `low_coverage` status** when coverage is low. The LMR block always sets "ok", which suits a global dataset; GEDA has a footprint edge. The coverage level to use is not set here (473 footprint basins have coverage below 0.99, 150 below 0.5, 46 below 0.1).
3. **A flag for observed years.** 1990 to 2020 are observed CRU TS 4.06 values; rows do not say so. A caveat on the rows, or a per-year flag from 1990.
4. **A GEDA caveat text** in `CAVEAT_TEXTS` (z-scores per cell against 1000 to 2020, summer only, observed 1990 to 2020, reliability follows tree-ring density).
5. **The effective cell count in the payload.** The engine's histogram computes it only to set `low_resolution`; for LMR it is not reported. The panel and the flag both depend on it.
6. **Panels should use p10 to p90**, not min and max, which are unweighted and set by low-weight cells.
7. **Catalog and docs:** a variable catalog row and the docsite entry (the latter already drafted).
8. **Delivery:** the block works for any polygon (basin, buffer, polity); whether to deliver at L6 only is a product choice (an L8 basin is a fraction of a cell: in Ukraine a typical L8 basin holds about a quarter of a GEDA cell, WO-01 Q11).

## Deviations from the WO

- The WO's "one large Ukraine basin (2060448220)" is the Kyiv basin, so a second large basin (2060469830) was used for the fifth test.
- The edge basin was chosen by rule (area at least 5,000 km², coverage nearest 0.5): 1060044120 in the Libyan Sahara.
- Item 9 added cases the WO did not name (one cell, two cells, coverage below 10%, outside the footprint).
- Item 12 added the between-cell spread comparison. Cell 4a (Europe) is an aside.
- Part B item 5 used the engine as a library from the notebook; nothing in the engine was edited.
