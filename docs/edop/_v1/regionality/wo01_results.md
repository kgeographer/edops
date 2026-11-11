# WO-01 (regional data) results: GEDA and OWDA exploration

2026-11-11. Spec: `wo01_GEDA-OWDA-exploration.md`. Notebook: `notebooks/edop/regionality/wo01_geda_owda_exploration.ipynb` (Cells 1 to 14; the outputs are saved in it). Inputs: `data/geda/geda_trim.nc`, `data/owda/owda.nc`; their documentation (`owda-readme.txt`; Cook et al. 2024 and its supplement for GEDA; Cook et al. 2015 for OWDA); `gaz.admin0`, `public.basin06` and `public.basin08` (read only). The numbers below are from notebook output Karl ran. Nothing here sets a threshold or reaches a verdict. "Cell" means a 0.5° grid cell; "valid" means a finite value after the fill value described under Q3 is masked. A plain-language summary is in `wo01_summary.md`.

## Read first: what changes the WO's premises

1. **OWDA has Ukraine values before 1000 CE.** 55 of the 271 Ukraine cells with OWDA data have values from year 0, 80 by 600 CE, 161 by 800, 174 by 1000, and all by 1120. The WO's context line ("no Ukraine values before about 700, only the north until about 1000") came from reading the animation and is not what the file holds (Q9).
2. **GEDA's file stores a netCDF fill value as data**, with no `_FillValue` declared. Anything that opens it without masking `> 1e30` will read 9.969e+36 as a value (Q3).
3. **GEDA values are z-scores**, not PDSI: every valid cell has mean 0.0000 and SD 1.0000 over 1000 to 2020 (Q5). OWDA values are not rescaled (SD about 1.9).
4. **"37,774 points" is the full GEDA.** The trimmed file has 28,970 cells with values. The authors removed sub-Saharan Africa and everything south of the equator (Q4).
5. **GEDA differs strongly from OWDA in Ukraine**: median per-cell correlation 0.046 over 1000 to 1978, the lowest of any European country with 30 or more cells, against 0.77 at a Paris cell (Q10). OWDA is the older product that GEDA replaces (its web app says so and recommends GEDA), so this shows where the newer network changed the answer; it is not evidence against GEDA. The open question about GEDA itself is its validation over Ukraine: neither file carries skill statistics (Q2) and the papers give none for Ukraine. LMR, which the worked example also uses, correlates at about 0.1 or less with both products at annual resolution (Q10, Cell 15).
6. **The "700 CE" sentence in the WO is wrong about its origin.** The Sandbox's LMR map layer starts at 700 CE, a quality floor set from our own EDA (F10.1, F10.3), not "following the LMR authors". The signature reports LMR from 0 CE (see `docs/edop/_v1/rubrics/lmr_quality_border.md`).

## Q1. Structure of both files

| | GEDA (`geda_trim.nc`, 226 MB) | OWDA (`owda.nc`, 228 MB) |
|---|---|---|
| Dimensions | yr = 1021, lat = 158, lon = 404 | lon = 114, lat = 88, time = 2013 |
| Main variable | `scPDSI` (yr, lat, lon), float64 | `pdsi` (lon, lat, time), float64 |
| Variable attributes | long_name "self-calibrating PDSI", units "sigma" | longname "Palmer Drought Severity Index", units "unitless" |
| Latitude | 0.25 to 78.75, step 0.5 | 27.25 to 70.75, step 0.5 |
| Longitude | -21.75 to 179.75, step 0.5 | -11.75 to 44.75, step 0.5 |
| Grid registration | centres at .25 (offset 0.25 from whole degrees) | centres at .25 |
| Time axis | `yr` 1000 to 2020, step 1, units "unitless" | `time` 0 to 2012, step 1, no units attribute |
| Global attributes | `comment`: "Trimmed and restandardized (zero mean, unit standard deviation; baseline 1000-2020) scPDSI from the Great Eurasian Drought Atlas." | `creation_date` 10-Mar-2015 15:53:08; `Description` "Reconstructed PDSI for Europe-Mediterranean Region (OWDA v1.0)" |
| Compression and packing | zlib; no scale factor, offset or declared fill | none; no declared fill |
| Dimension order | time first | longitude first (the array must be transposed to compare) |

- **Time labels.** Neither file says the years are CE. The OWDA readme declares the time variable as `age_AD, year AD`. The GEDA paper describes the record as 1000 to 2020 CE.
- **Coordinate attributes.** OWDA's use the key `longname` (not `long_name`), apparently a MATLAB export.

## Q2. Extras beyond the main field

None, in either file. No other variable or non-index coordinate, no variable along the time axis (so no flag for tree-ring versus instrumental years), and no attribute mentioning skill, calibration, validation, chronology counts, ensembles or masks. The tree-ring and instrumental split, the skill and the chronology counts all have to come from the papers (see Q7 and the open issues).

## Q3. Do the grids coincide?

**Lattices: yes.** All 88 OWDA latitudes and all 114 OWDA longitudes are found exactly on the GEDA axes, so OWDA's grid is a subset of GEDA's and the cells line up one to one.

**Missing values in GEDA (found while checking Q3).** The raw maximum is `9.969209968386869e+36`, the netCDF default double fill value, stored as data. After masking it:

| GEDA cells | Count |
|---|---|
| Entirely fill value (31,290,587 entries, which is 30,647 cells × 1,021 years) | 30,647 |
| Entirely NaN | 4,215 |
| With values | 28,970 |
| Total | 63,832 |

The fill and NaN cells are all-or-none: no cell is partly fill. The split by region was not retained, because Cell 4 was run twice; only the combined figure ("cells without values") is tabulated under Q4.

**Valid-cell masks inside OWDA's box (10,032 cells)**, after masking the fill value:

| | Cells |
|---|---|
| Valid in both | 5,388 |
| Valid in GEDA only | 966 |
| Valid in OWDA only | 26 |
| Valid in neither | 3,652 |
| GEDA valid cells outside the box | 22,616 |

- **GEDA only (966), by country subregion:** no country 549, Northern Europe 156, Eastern Europe 96, Southern Europe 74, Western Asia 45, Northern Africa 25, Western Europe 21. ("No country" means the cell centre is outside every Natural Earth polygon; probably coast and inland water, not examined.)
- **OWDA only (26):** all in Western Asia, at latitude 27.25 to 31.25 and longitude 40.25 to 44.25 (the northern Arabian desert). Nothing in the file or the GEDA paper explains why GEDA lacks them.

## Q4. GEDA extent

- **Cells with values:** 28,970 of 63,832. Extent of those cells: latitude 0.25 to 78.25, longitude -21.75 to 179.75. The grid has no cells south of the equator (it starts at 0.25 N).
- **Documented 37,774 points:** the file has 8,804 fewer valid cells. The GEDA paper (Cook et al. 2024) explains the trim: the full GEDA "covers the entire Eurasian region and a substantial portion of sub-Saharan Africa", and the authors "do not consider the GEDA domain for sub-Saharan Africa and south of the equator". The paper gives no cell count for what was removed.
- **Cells by Natural Earth subregion** (cells without values are the fill and NaN cells together):

| Subregion | Cells in grid | With values | Without values |
|---|---|---|---|
| Eastern Europe | 12,388 | 12,375 | 13 |
| Eastern Asia | 4,800 | 4,753 | 47 |
| Southern Asia | 2,448 | 2,448 | 0 |
| (no country) | 30,394 | 1,910 | 28,484 |
| Central Asia | 1,850 | 1,850 | 0 |
| Western Asia | 1,684 | 1,489 | 195 |
| Northern Europe | 1,226 | 1,205 | 21 |
| South-Eastern Asia | 1,019 | 1,016 | 3 |
| Northern Africa | 2,753 | 784 | 1,969 |
| Southern Europe | 564 | 564 | 0 |
| Western Europe | 533 | 532 | 1 |
| Northern America | 45 | 43 | 2 |
| Eastern Africa | 996 | 1 | 995 |
| Middle Africa | 1,101 | 0 | 1,101 |
| Western Africa | 2,031 | 0 | 2,031 |

- **Named places** (the GEDA cell holding the point):

| Place | Point | Cell centre | Cell holds |
|---|---|---|---|
| Kyiv | 50.4547, 30.5238 | 50.25, 30.75 | values |
| Tbilisi | 41.7151, 44.8271 | 41.75, 44.75 | values |
| Timbuktu | 16.8167, -2.9833 | 16.75, -2.75 | no values (Western Africa) |

- **Ukraine** (cell centres inside the Natural Earth outline; a modern border used as a study-area outline for earlier periods): 289 GEDA cells, all 289 with values. OWDA has values in 271 of the same 289.

## Q5. GEDA units

Restandardized. Over all 28,970 cells with values the per-cell mean over 1000 to 2020 is 0.0000 (percentiles 0, 1, 50, 99, 100 all print -0.0000 to 0.0000) and the per-cell SD (population) is 1.0000 at every percentile; the Ukraine cells are the same. The value range after masking the fill is -4.99 to 5.803. This agrees with the file's comment and with the GEDA paper ("restandardized PDSI at every grid cell to a mean of zero and unit standard deviation (z scores) using the entire period as the baseline (1000-2020 CE)"). The baseline includes the instrumental years 1990 to 2020. OWDA is not rescaled: over Ukraine its per-cell SD is 1.92 (median) against GEDA's 1.00 (Q10).

## Q6. Missing values through time

- **GEDA:** 28,970 cells have a value in every one of the 1,021 years (minimum and maximum per year are the same; one distinct count). No cell has values in some years and not others. The raw NaN count (4,303,515) is exactly 4,215 cells × 1,021 years, so every NaN sits in an entirely-NaN cell.
- **OWDA:** no cell has a gap inside its own record, and all 5,414 cells with values end at 2012. Coverage grows only by cells starting later. Cells by first year with a value:

| First year | Cells |
|---|---|
| 0 | 3,054 |
| 1 to 300 | 0 |
| 301 to 700 | 645 |
| 701 to 1000 | 750 |
| 1001 to 1500 | 965 |
| 1501 to 2012 | 0 |

  Percentiles (0, 5, 25, 50, 75, 95, 100) of the first year: 0, 0, 0, 0, 967, 1083, 1120.

| Year | OWDA cells with a value | Ukraine cells |
|---|---|---|
| 0 | 3,054 | 55 |
| 300 | 3,054 | 55 |
| 600 | 3,551 | 80 |
| 700 | 3,699 | 80 |
| 800 | 3,819 | 161 |
| 900 | 4,008 | 161 |
| 1000 | 4,449 | 174 |
| 1100 | 5,412 | 270 |
| 1500 to 2012 | 5,414 | 271 |

## Q7. The 1989/1990 join (GEDA, 289 Ukraine cells)

The file has no flag for the join. The GEDA paper states it: "tree-ring reconstructed values spanning 1000-1989 CE and instrumental observations from 1990 to 2020 CE", the instrumental part being the CRU TS 4.06 scPDSI. Across the Ukraine cells:

| | 1960 to 1989 | 1990 to 2020 |
|---|---|---|
| Per-cell mean, median (min, max) | 0.435 (-0.218, 0.777) | -0.054 (-0.577, 0.280) |
| Per-cell variance, median (min, max) | 0.962 (0.659, 1.476) | 0.930 (0.618, 1.945) |
| Cell-average series: mean | 0.373 | -0.037 |
| Cell-average series: variance | 0.566 | 0.649 |

Per-cell variance ratio (1990 to 2020 over 1960 to 1989), percentiles 5, 50, 95: 0.55, 1.06, 1.59. The cell-average series for 1985 to 1995 has no visible step at 1990 (1985 1.10, 1986 -0.29, 1987 -0.70, 1988 0.23, 1989 -0.43, 1990 -0.42, 1991 0.37, 1992 -0.22, 1993 0.30, 1994 -0.34, 1995 0.35). The file alone cannot say whether the mean shift is climate or an artefact of the join. A comparison with shifts between other 30-year windows was not run.

## Q8. Variance by century (GEDA)

Sample variances (ddof = 1) of the annual values within each century. "All" is the median over all 28,970 cells; "Ukr" is over the Ukraine cells (median, 10th and 90th percentile, and the mean value); the last five columns are single cells.

| Years | All median | Ukr median | Ukr p10 | Ukr p90 | Ukr mean | Paris | Ankara | Tashkent | Beijing | Stockholm |
|---|---|---|---|---|---|---|---|---|---|---|
| 1000-1099 | 0.945 | 0.890 | 0.760 | 0.986 | -0.170 | 0.881 | 0.926 | 1.045 | 0.821 | 0.938 |
| 1100-1199 | 0.967 | 0.946 | 0.744 | 1.080 | -0.065 | 1.218 | 1.095 | 0.821 | 1.108 | 0.988 |
| 1200-1299 | 0.999 | 1.009 | 0.874 | 1.249 | -0.045 | 0.861 | 1.152 | 1.160 | 0.918 | 0.947 |
| 1300-1399 | 1.011 | 1.115 | 0.947 | 1.224 | -0.025 | 0.973 | 0.977 | 1.021 | 1.117 | 1.041 |
| 1400-1499 | 0.966 | 0.868 | 0.790 | 0.981 | 0.040 | 0.981 | 0.829 | 1.075 | 0.908 | 0.924 |
| 1500-1599 | 0.948 | 0.999 | 0.934 | 1.062 | 0.035 | 1.027 | 0.928 | 0.928 | 1.008 | 0.867 |
| 1600-1699 | 1.031 | 1.066 | 0.926 | 1.145 | 0.094 | 0.977 | 1.108 | 0.937 | 1.030 | 1.127 |
| 1700-1799 | 0.955 | 0.944 | 0.857 | 1.089 | 0.056 | 0.879 | 0.984 | 0.997 | 0.983 | 0.864 |
| 1800-1899 | 0.937 | 0.947 | 0.858 | 1.072 | 0.143 | 1.048 | 0.952 | 1.040 | 0.933 | 1.139 |
| 1900-1999 | 0.934 | 1.010 | 0.944 | 1.067 | -0.016 | 1.005 | 0.779 | 1.133 | 0.956 | 1.091 |
| 2000-2020 (21 years) | 0.948 | 1.008 | 0.713 | 1.333 | -0.230 | 0.885 | 1.194 | 0.567 | 0.615 | 0.720 |

Reference cells (nearest GEDA cell, all with values): Paris (48.75, 2.25), Ankara (39.75, 32.75), Tashkent (41.25, 69.25), Beijing (39.75, 116.25), Stockholm (59.25, 18.25). No early-century drop in variance is visible, in Ukraine or in the all-cell median; the reference cells scatter around 1 with no consistent direction. This is a different picture from the LMR funnel recorded in EDA F10.1. The GEDA paper states that validation statistics "are generally consistent even as tree-ring availability declines back in time", which is a statement about skill, not variance. The century means in Ukraine drift between -0.17 (1000s) and +0.14 (1800s), and -0.23 for 2000 to 2020.

## Q9. OWDA coverage of Ukraine through time

Ukraine: 289 OWDA grid cells have their centre inside the Natural Earth outline; 271 have values and 18 have none. No Ukraine cell has a gap inside its record. First year with a value, Ukraine cells (year: cells): 0: 55, 559: 16, 584: 9, 727: 77, 730: 4, 967: 12, 970: 1, 1003: 61, 1010: 21, 1020: 13, 1100: 1, 1120: 1.

| First year | Cells | Latitude | Longitude | Mean position |
|---|---|---|---|---|
| 0 | 55 | 48.25 to 51.75 | 22.75 to 29.75 | 50.20 N, 25.23 E |
| 1 to 700 (559, 584) | 25 | 50.75 to 52.25 | 30.25 to 34.75 | 51.41 N, 32.67 E |
| 701 to 1000 | 94 | 45.25 to 51.25 | 25.25 to 38.75 | 49.06 N, 30.34 E |
| 1001 to 1500 | 97 | 46.25 to 50.25 | 27.75 to 39.75 | 48.43 N, 34.82 E |

The pattern is a gradient from west to east: the west and northwest from year 0, a northern block from the 6th century, the broad middle at about 727, and the east and south from about 1003, with the last two cells at 1100 and 1120. The map is `output/edop/regionality/wo01_ukraine_owda_first_year.png` (gitignored). The 18 cells with no value: along the southern coast (46.25 to 46.75 N at 31.25 to 36.75 E, 47.25 N at 32.25, 34.25 and 38.25 E) and three inland, at (49.75, 32.25), (49.25, 33.25) and (47.75, 35.75), which may be Dnipro reservoir cells (not checked against a water layer).

**What marks thin support in the file:** only the start year of each cell. The OWDA paper (Cook et al. 2015) maps chronology start years across a 106-chronology network, "reasonably uniform ... except for Russia", and reconstructs by point-by-point regression with a 1000 km search radius, but gives no per-cell table. That the file's start years follow chronology availability is a plausible reading, not a confirmed one. The earlier desk note (four chronologies in western Ukraine) was not found in this paper.

## Q10. OWDA against GEDA, Ukraine, 1000 to 1978

**How the two products relate.** OWDA (Cook et al. 2015) is the older product that GEDA replaces. The OWDA web app carries this notice (wording supplied by Karl, 2026-11-11): "Legacy Notice: The Old World Drought Atlas (OWDA) has entered legacy mode. This web app will remain available, but will no longer be updated. The Great Eurasian Drought Atlas significantly improves upon the reconstructions available in the OWDA and is recommended." The GEDA paper (Cook et al. 2024) likewise says GEDA "builds, expands, and improves upon previous spatial reconstructions of PDSI, including the Old World Drought Atlas". Inputs and methods differ:

| | OWDA | GEDA |
|---|---|---|
| Tree-ring network | 106 chronologies ("reasonably uniform ... except for Russia") | 1,869 chronologies and one speleothem |
| Method | point-by-point regression, mean of 8 ensemble members | ensemble point-by-point regression, 48 candidate models per cell chosen on validation R2, recalibrated at nine chronology cutoffs (1800 to 1000) and averaged |
| Calibration / validation | 1928 to 1978 / 1901 to 1927 | 1951 to 1990 / 1920 to 1950 |
| Observed target | CRU TS 3.21 scPDSI | CRU TS 4.06 scPDSI |

The two are therefore not expected to agree where OWDA's network was thin, and the agreement figures below fit that: highest in Western Europe, lowest in the east. They show where the newer product differs most from the older one; they do not show which is right in Ukraine. Because OWDA is the product its authors now advise against using, its agreement or disagreement with GEDA is background, not a test of GEDA.

271 Ukraine cells with OWDA values; each cell used only in years where OWDA has a value (264,436 of 265,309 cell-years have both); a cell-century needs 20 years. Per-cell SD over matched years, median: OWDA 1.924, GEDA 1.002. GEDA is rescaled and OWDA is not, so the mean difference mixes scale and baseline with disagreement; correlations are unaffected by scale. The two share chronologies, so agreement shows consistency, not independent skill.

| Years | Cells | r median | r p10 | r p90 | Mean diff (OWDA - GEDA) | SD ratio | Cell-average r | Cell-average diff |
|---|---|---|---|---|---|---|---|---|
| 1000-1099 | 269 | 0.029 | -0.150 | 0.194 | -0.079 | 1.936 | -0.044 | -0.324 |
| 1100-1199 | 271 | -0.067 | -0.240 | 0.250 | -0.411 | 1.951 | -0.132 | -0.471 |
| 1200-1299 | 271 | 0.031 | -0.162 | 0.237 | -0.387 | 1.918 | 0.011 | -0.419 |
| 1300-1399 | 271 | 0.049 | -0.182 | 0.263 | -0.124 | 1.750 | 0.100 | -0.204 |
| 1400-1499 | 271 | -0.012 | -0.355 | 0.279 | -0.589 | 2.020 | -0.106 | -0.637 |
| 1500-1599 | 271 | 0.044 | -0.209 | 0.277 | -0.205 | 1.865 | 0.090 | -0.310 |
| 1600-1699 | 271 | 0.084 | -0.121 | 0.359 | -0.856 | 1.979 | 0.217 | -0.863 |
| 1700-1799 | 271 | 0.063 | -0.085 | 0.246 | -0.305 | 1.717 | 0.182 | -0.325 |
| 1800-1899 | 271 | 0.073 | -0.101 | 0.307 | -0.637 | 1.980 | 0.113 | -0.650 |
| 1900-1978 | 271 | 0.286 | 0.015 | 0.502 | -0.299 | 1.914 | 0.442 | -0.344 |

Median per-cell r by the cell's OWDA first-year group (cells in the group with at least 20 years in the century):

| Years | First 0 (n=55) | First 1-700 (n=25) | First 701-1000 (n=94) | First 1001-1500 (n=95 to 97) |
|---|---|---|---|---|
| 1000-1099 | 0.15 | -0.01 | 0.04 | -0.06 |
| 1100-1199 | 0.18 | 0.18 | -0.09 | -0.13 |
| 1200-1299 | 0.19 | -0.02 | 0.02 | -0.03 |
| 1300-1399 | 0.24 | 0.03 | 0.11 | -0.09 |
| 1400-1499 | 0.20 | 0.06 | 0.05 | -0.20 |
| 1500-1599 | 0.21 | -0.10 | 0.08 | -0.07 |
| 1600-1699 | 0.28 | -0.11 | 0.15 | 0.03 |
| 1700-1799 | 0.15 | -0.01 | 0.05 | 0.07 |
| 1800-1899 | 0.24 | 0.03 | 0.07 | 0.03 |
| 1900-1978 | 0.45 | 0.08 | 0.33 | 0.22 |

**Is the low agreement a pairing error?** No. Cell 11 checked it two ways. By year lag (GEDA year = OWDA year + lag), the single cells peak at lag 0 (Paris r = 0.774, Ankara 0.650, Stockholm 0.531; at lag +1: 0.493, 0.121, 0.447; at -1: 0.055, 0.165, 0.136). The Ukraine median at lag 0 is 0.046 over 1000 to 1978 (0.055 at lag +1) and 0.286 over 1900 to 1978 (0.156 at lag +1). By spatial shift of the GEDA cell (-2 to +2 cells in each direction) the Ukraine median is flat: 0.02 to 0.065 for 1000 to 1978 and 0.22 to 0.32 for 1900 to 1978, with the highest values to the south-west (0.324 at -2, -2) and no sharp centre peak.

**Regional context** (Cell 12: median per-cell r at lag 0 over the 5,388 cells valid in both files; all cells: 0.396 for 1000 to 1978 and 0.530 for 1900 to 1978):

| Subregion | Cells | r 1000-1978 (median) | p10 | p90 | r 1900-1978 (median) |
|---|---|---|---|---|---|
| Western Europe | 511 | 0.671 | 0.299 | 0.825 | 0.760 |
| Northern Europe | 951 | 0.560 | 0.235 | 0.751 | 0.665 |
| Southern Europe | 487 | 0.446 | 0.188 | 0.653 | 0.604 |
| Northern Africa | 736 | 0.311 | 0.066 | 0.582 | 0.402 |
| Eastern Europe | 1,979 | 0.289 | -0.029 | 0.590 | 0.451 |
| Western Asia | 625 | 0.216 | 0.039 | 0.703 | 0.433 |
| (no country) | 94 | 0.429 | 0.098 | 0.681 | 0.540 |
| Southern Asia | 5 | 0.161 | 0.018 | 0.172 | 0.207 |

| Country (30 or more cells) | Cells | r 1000-1978 | r 1900-1978 |
|---|---|---|---|
| Germany | 185 | 0.731 | 0.779 |
| United Kingdom | 109 | 0.713 | 0.772 |
| Ireland | 30 | 0.680 | 0.726 |
| France | 240 | 0.639 | 0.754 |
| Finland | 220 | 0.598 | 0.753 |
| Sweden | 281 | 0.535 | 0.610 |
| Turkey | 299 | 0.523 | 0.682 |
| Norway | 204 | 0.522 | 0.582 |
| Poland | 165 | 0.430 | 0.534 |
| Russia | 1,149 | 0.289 | 0.403 |
| Romania | 108 | 0.272 | 0.561 |
| Belarus | 113 | 0.266 | 0.363 |
| Iraq | 117 | 0.115 | 0.299 |
| Syria | 71 | 0.111 | 0.294 |
| Saudi Arabia | 69 | 0.084 | 0.347 |
| Egypt | 64 | 0.063 | 0.191 |
| **Ukraine** | **271** | **0.046** (p10 -0.104, p90 0.233) | **0.286** |

(Other countries with 30 or more cells are in the Cell 12 output.) Agreement falls from west to east, and Ukraine is the lowest of the European countries listed. The GEDA paper's Supplementary Fig. 3 (validation R² maps for the 1800, 1600 and 1400 chronology cutoffs) shows R² highest, about 0.4 to 0.5, over Western and Central Europe and Scandinavia and lower to the east. At the resolution of the map in the supplement Ukraine cannot be read; this is a visual impression only.

**Observed overlap (Cell 15).** The GEDA paper says its 1990 to 2020 values are instrumental CRU TS 4.06 scPDSI; OWDA was calibrated on CRU TS 3.21 scPDSI, and the NCEI description puts its observed years at 1979 to 2012 (the paper text read does not say so). If both tails are observations, the two files should agree closely there. Per-cell r between OWDA and GEDA by span (Ukraine with 10th and 90th percentile; other columns are medians over the cells with values in both files):

| Years | Ukraine median | Ukraine p10 | Ukraine p90 | All cells | Western Europe | Eastern Europe |
|---|---|---|---|---|---|---|
| 1901-1950 | 0.242 | -0.041 | 0.496 | 0.522 | 0.782 | 0.434 |
| 1951-1978 | 0.284 | 0.034 | 0.528 | 0.575 | 0.749 | 0.493 |
| 1979-1989 (11 years) | 0.458 | 0.094 | 0.746 | 0.551 | 0.575 | 0.570 |
| 1990-2012 | 0.701 | 0.386 | 0.858 | 0.765 | 0.817 | 0.774 |

Agreement rises toward the observed years but reaches only 0.70 over Ukraine in 1990 to 2012 (0.82 over Western Europe). The files cannot say why (the CRU versions the two used differ, or the OWDA tail holds something other than what its description says); since OWDA is not planned for ingest this was not pursued. The earlier expectation of near-identical series over 1990 to 2012 was wrong.

**LMR as a third product (Cell 15).** LMR PDSI is annual, on a 2° grid, an anomaly (a different variable and season from JJA scPDSI); 31 LMR cells cover the Ukraine cells. Per-cell r over the Ukraine cells (median, with 10th and 90th percentile):

| Span | GEDA-OWDA | GEDA-LMR | OWDA-LMR |
|---|---|---|---|
| 1000-1978 | 0.046 (-0.104, 0.233) | -0.030 (-0.068, 0.088) | 0.108 (-0.024, 0.186) |
| 1900-1978 | 0.286 (0.015, 0.502) | 0.123 (-0.014, 0.364) | 0.163 (-0.035, 0.268) |

On the Ukraine cell-average series: 1000 to 1978 GEDA-OWDA 0.085, GEDA-LMR -0.026, OWDA-LMR 0.186; 1900 to 1978 0.442, 0.219, 0.234. Year-lag scan of the cell averages over 1000 to 1978 (LMR year = product year + lag), lags -2 to +2: GEDA against LMR -0.063, -0.019, -0.026, -0.031, 0.003; OWDA against LMR 0.046, 0.099, 0.186, 0.140, 0.136 (no peak for GEDA; a weak peak at lag 0 for OWDA; no sign of a one-year offset in LMR). Single cells over 1000 to 1978:

| Cell | GEDA-OWDA | GEDA-LMR | OWDA-LMR |
|---|---|---|---|
| Paris | 0.774 | 0.094 | 0.096 |
| Ankara | 0.650 | 0.055 | 0.020 |
| Stockholm | 0.531 | 0.057 | -0.108 |

LMR does not side with either product. It does not track either at annual resolution, even where GEDA and OWDA agree strongly. At annual resolution GEDA and LMR are effectively uncorrelated over Ukraine and over Paris, so showing them side by side in the worked example invites an expectation of corroboration that is not there. Agreement on slower changes is in the next paragraph.

**Slow changes (Cells 16 and 17).** Cell averages over two fixed sets of Ukraine cells (so the mix of cells does not change through time), then centred moving averages. Set A: the 55 cells with OWDA values from year 0 (the west), 1000 to 1978. Set B: all 271 cells with OWDA values, 1120 to 1978 (the last cell starts in 1120). r between the cell-average series, by smoothing window ("independent" is about span / window; smoothed values overlap, so few are independent):

| Set | Window (years) | Independent values | GEDA-OWDA | GEDA-LMR | OWDA-LMR |
|---|---|---|---|---|---|
| A (n=55) | 1 | 979 | 0.349 | 0.081 | 0.081 |
| A | 11 | 89 | 0.365 | -0.013 | 0.004 |
| A | 31 | 31 | 0.266 | -0.060 | -0.014 |
| A | 51 | 19 | 0.249 | -0.026 | -0.008 |
| B (n=271) | 1 | 859 | 0.093 | -0.014 | 0.184 |
| B | 11 | 78 | -0.001 | -0.080 | 0.201 |
| B | 31 | 27 | -0.185 | -0.166 | 0.235 |
| B | 51 | 16 | -0.249 | -0.085 | 0.370 |

In the west (set A) GEDA and OWDA agree moderately at every scale (0.25 to 0.37) and LMR sits near zero against both. Over all Ukraine cells (set B) GEDA and OWDA agree weakly unsmoothed (0.09) and become negatively correlated as the series are smoothed (-0.19 at 31 years), with their smoothed values often of opposite sign (around 1885 GEDA +1.76, OWDA -0.67; around 1585 +1.50 against -0.60; around 1135 -0.58 against +1.73; in set A around 1065 OWDA -2.69 against GEDA +0.80). OWDA-LMR rises to 0.37 at 51 years but rests on about 16 independent values. With 16 to 31 roughly independent values, correlations of plus or minus 0.2 to 0.4 can arise by chance; no significance test was run. The figure `output/edop/regionality/wo01_ukraine_lowfreq.png` (gitignored) shows the 31-year series: the three lines move independently over most of the record, converging only late (all three rise near 1815 and fall near 1915 to 1960, the period when the products are fitted to observations). So slow swings are not shared across the products over Ukraine, and the check does not support presenting a centennial drought narrative from a single product there. The eastern cells alone (those starting after 1000 CE) were not separated out.

## Q11. Grid cells per basin

"Footprint" is the 28,970 GEDA cells with values; a basin is in the footprint if it intersects at least one cell box (centre ± 0.25°), so basins at the edge are counted. The weight of a cell in a basin follows `engine.py` (`_agg_hyde_b7`): overlap area divided by the cell's own area, with `w_eff` the sum of those fractions (the engine's effective cell count; it flags low resolution below 5).

**L6:** 6,630 basins in the footprint; 1,045 contain no cell centre.

| Centres per basin | 0 | 1 | 2 | 3 to 4 | 5 to 9 | 10 or more |
|---|---|---|---|---|---|---|
| Basins | 1,045 | 1,166 | 1,104 | 1,288 | 1,307 | 720 |

Cells overlapping by area: 1 for 216 basins, 2 for 335, 3 to 4 for 774, 5 to 9 for 2,286, 10 or more for 3,019; percentiles (0, 5, 25, 50, 75, 95, 100): 1, 2, 5, 9, 14, 27, 106. `w_eff` percentiles: 0, 0.13, 1.08, 2.54, 5.36, 13.04, 70.29; 4,824 basins are below 5 and 1,550 are below 1.

**L8:** 76,086 basins in the footprint; 53,249 contain no cell centre.

| Centres per basin | 0 | 1 | 2 | 3 to 4 | 5 to 9 | 10 or more |
|---|---|---|---|---|---|---|
| Basins | 53,249 | 19,321 | 2,948 | 529 | 38 | 1 |

**L8, area-weighted overlap, basins intersecting Ukraine only:** 930 basins; 636 contain no cell centre (262 contain one, 30 contain two, 2 contain three or four). Cells overlapping by area: 1 for 148 basins, 2 for 265, 3 to 4 for 382, 5 to 9 for 134, 10 or more for 1; percentiles (0, 5, 25, 50, 75, 95, 100): 1, 1, 2, 3, 4, 6, 12. `w_eff` percentiles: 0, 0.01, 0.11, 0.25, 0.49, 1.06, 2.81; 874 basins are below 1 and 701 are below 0.5.

## Q12. L6 basins intersecting Ukraine

99 basins. "Share in Ukraine" is the fraction of the basin inside the Natural Earth outline; the cell counts include every GEDA cell touching the basin, including cells outside Ukraine. 37 basins are entirely inside (1.000). 12 have no cell centre, 68 have `w_eff` below 5 and 16 have it below 1. Four basins entirely inside Ukraine contain no cell centre: 2060480720 (28 km², `w_eff` 0.01), 2060472570 (150 km², 0.07), 2060467040 (1,667 km², 0.82) and 2060481560 (2,464 km², eight cells overlapping, `w_eff` 1.19).

| hybas_id | area km² | share in Ukraine | cell centres | cells overlapping | w_eff |
|---|---|---|---|---|---|
| 2060454840 | 7,169 | 1.000 | 3 | 13 | 3.53 |
| 2060493250 | 3,129 | 1.000 | 2 | 6 | 1.51 |
| 2060388040 | 12,034 | 1.000 | 6 | 16 | 6.10 |
| 2060007010 | 4,711 | 1.000 | 3 | 7 | 2.23 |
| 2060469830 | 22,802 | 1.000 | 11 | 22 | 11.04 |
| 2060416550 | 19,979 | 1.000 | 10 | 21 | 10.11 |
| 2060462840 | 2,830 | 1.000 | 2 | 5 | 1.39 |
| 2060481420 | 7,850 | 1.000 | 3 | 11 | 3.81 |
| 2060480720 | 28 | 1.000 | 0 | 2 | 0.01 |
| 2060480610 | 16,691 | 1.000 | 10 | 16 | 8.17 |
| 2060448220 | 28,495 | 1.000 | 13 | 27 | 14.25 |
| 2060472570 | 150 | 1.000 | 0 | 1 | 0.07 |
| 2060416390 | 8,935 | 1.000 | 5 | 13 | 4.59 |
| 2060006800 | 5,036 | 1.000 | 4 | 8 | 2.41 |
| 2060390810 | 4,127 | 1.000 | 2 | 6 | 2.13 |
| 2060008160 | 5,396 | 1.000 | 4 | 8 | 2.57 |
| 2060448170 | 19,286 | 1.000 | 9 | 22 | 9.76 |
| 2060472640 | 2,811 | 1.000 | 1 | 7 | 1.36 |
| 2060481560 | 2,464 | 1.000 | 0 | 8 | 1.19 |
| 2060461960 | 15,577 | 1.000 | 8 | 16 | 7.65 |
| 2060493390 | 2,897 | 1.000 | 1 | 6 | 1.39 |
| 2060388050 | 13,723 | 1.000 | 8 | 17 | 6.94 |
| 2060495670 | 4,227 | 1.000 | 3 | 7 | 2.04 |
| 2060459250 | 2,439 | 1.000 | 1 | 6 | 1.19 |
| 2060508440 | 9,802 | 1.000 | 4 | 14 | 4.72 |
| 2060444190 | 2,917 | 1.000 | 1 | 7 | 1.44 |
| 2060464310 | 15,774 | 1.000 | 8 | 15 | 7.77 |
| 2060515580 | 8,095 | 1.000 | 3 | 12 | 3.83 |
| 2060462830 | 14,036 | 1.000 | 6 | 17 | 6.94 |
| 2060515460 | 14,529 | 1.000 | 9 | 15 | 7.01 |
| 2060416040 | 3,998 | 1.000 | 2 | 7 | 2.02 |
| 2060416160 | 2,224 | 1.000 | 1 | 7 | 1.12 |
| 2060464320 | 3,927 | 1.000 | 4 | 5 | 1.95 |
| 2060467040 | 1,667 | 1.000 | 0 | 6 | 0.82 |
| 2060466960 | 3,376 | 1.000 | 2 | 7 | 1.67 |
| 2060495760 | 5,992 | 1.000 | 2 | 9 | 2.86 |
| 2060469820 | 13,011 | 1.000 | 6 | 18 | 6.41 |
| 2060465300 | 6,463 | 0.999 | 2 | 10 | 3.15 |
| 2060008170 | 7,233 | 0.995 | 3 | 10 | 3.42 |
| 2060508300 | 9,827 | 0.992 | 4 | 14 | 4.71 |
| 2060397700 | 8,159 | 0.990 | 6 | 11 | 4.19 |
| 2060007020 | 4,714 | 0.987 | 2 | 7 | 2.21 |
| 2060007930 | 3,803 | 0.984 | 1 | 8 | 1.80 |
| 2060006810 | 6,772 | 0.983 | 3 | 9 | 3.19 |
| 2060542170 | 3,286 | 0.978 | 2 | 6 | 1.52 |
| 2060444020 | 5,949 | 0.970 | 3 | 9 | 2.95 |
| 2060008010 | 2,864 | 0.939 | 2 | 5 | 1.35 |
| 2060392620 | 8,206 | 0.932 | 5 | 12 | 4.29 |
| 2060375360 | 6,825 | 0.929 | 3 | 12 | 3.51 |
| 2060008450 | 1,243 | 0.904 | 0 | 4 | 0.57 |
| 2060007940 | 1,096 | 0.899 | 1 | 4 | 0.52 |
| 2060008000 | 234 | 0.884 | 0 | 3 | 0.11 |
| 2060501780 | 20,329 | 0.834 | 9 | 25 | 9.89 |
| 2060459130 | 14,561 | 0.824 | 8 | 19 | 7.31 |
| 2060008360 | 3,056 | 0.819 | 1 | 5 | 1.42 |
| 2060542410 | 344 | 0.747 | 0 | 3 | 0.16 |
| 2060454640 | 22,862 | 0.727 | 12 | 24 | 11.56 |
| 2060452740 | 23,201 | 0.708 | 11 | 22 | 11.63 |
| 2060006680 | 7,079 | 0.682 | 4 | 12 | 3.41 |
| 2060461730 | 7,414 | 0.656 | 2 | 10 | 3.69 |
| 2060465150 | 5,383 | 0.634 | 2 | 8 | 2.65 |
| 2060374270 | 1,403 | 0.609 | 1 | 7 | 0.73 |
| 2060008440 | 5,401 | 0.596 | 3 | 10 | 2.52 |
| 2060006690 | 3,369 | 0.592 | 1 | 5 | 1.61 |
| 2060390710 | 8,298 | 0.589 | 5 | 11 | 4.35 |
| 2060376210 | 16,394 | 0.589 | 8 | 19 | 8.35 |
| 2060375150 | 20,421 | 0.569 | 9 | 23 | 10.65 |
| 2060478820 | 11,724 | 0.566 | 5 | 14 | 5.66 |
| 2060478420 | 14,355 | 0.445 | 8 | 15 | 7.02 |
| 2060007120 | 19,253 | 0.430 | 9 | 23 | 8.86 |
| 2060400110 | 4,240 | 0.375 | 3 | 7 | 2.21 |
| 2060008350 | 11,658 | 0.354 | 7 | 15 | 5.51 |
| 2060541660 | 28,507 | 0.327 | 11 | 33 | 13.64 |
| 2060008490 | 969 | 0.323 | 0 | 5 | 0.44 |
| 2060544450 | 565 | 0.316 | 1 | 2 | 0.26 |
| 2060379760 | 3,775 | 0.307 | 1 | 8 | 1.99 |
| 2060374150 | 23,210 | 0.303 | 11 | 26 | 12.16 |
| 2060452600 | 14,870 | 0.296 | 6 | 20 | 7.54 |
| 2060424690 | 8,472 | 0.293 | 5 | 10 | 4.23 |
| 2060007130 | 22,797 | 0.270 | 12 | 35 | 10.49 |
| 2060544300 | 4,272 | 0.260 | 1 | 8 | 1.98 |
| 2060400100 | 1,221 | 0.255 | 0 | 5 | 0.63 |
| 2060477070 | 7,046 | 0.252 | 5 | 9 | 3.43 |
| 2060392710 | 28,000 | 0.251 | 15 | 29 | 14.54 |
| 2060544810 | 960 | 0.250 | 1 | 5 | 0.44 |
| 2060520280 | 12,428 | 0.173 | 6 | 16 | 5.94 |
| 2060544880 | 565 | 0.159 | 1 | 2 | 0.26 |
| 2060397580 | 11,488 | 0.155 | 5 | 17 | 6.00 |
| 2060376060 | 5,928 | 0.149 | 3 | 10 | 3.11 |
| 2060006590 | 7,592 | 0.054 | 5 | 9 | 3.63 |
| 2060369590 | 6,074 | 0.043 | 2 | 8 | 3.24 |
| 2060491970 | 8,511 | 0.025 | 3 | 13 | 4.11 |
| 2060374580 | 609 | 0.020 | 0 | 3 | 0.32 |
| 2060369600 | 567 | 0.018 | 0 | 4 | 0.30 |
| 2060478430 | 4,024 | 0.016 | 3 | 5 | 1.94 |
| 2060477080 | 10,576 | 0.003 | 6 | 13 | 5.20 |
| 2060541720 | 308 | 0.002 | 0 | 2 | 0.14 |
| 2060439160 | 17,086 | 0.001 | 8 | 18 | 8.58 |
| 2060363170 | 5,394 | 0.001 | 2 | 10 | 2.84 |

## Corrections to the WO text

- **Scope paragraph:** "EDOPS serves LMR from 700 CE, following the LMR authors" should read: the Sandbox LMR map layer starts at 700 CE, a quality floor from our own EDA (F10.1, F10.3); the signature reports LMR from 0 CE with a fidelity note below 700.
- **Scope and context:** "OWDA ... no Ukraine values before about 700 and only the north until about 1000" is not what the file holds (Q9). The decision that GEDA is the only dataset planned for ingest is not affected by this check; its stated reason is.
- **Inputs:** "37,774 points" is the full GEDA; the trimmed file has 28,970 cells with values (Q4). The GEDA data file is distributed by the authors through a Dropbox link in the paper's data availability statement, not (as the WO says) Zenodo; the Zenodo record was not checked.
- **OWDA split:** the "tree-ring to 1978, instrumental 1979 to 2012" split is not stated in the files. The paper gives the calibration period 1928 to 1978 and validation period 1901 to 1927.

## Open issues for the ingest design

1. **Fill value.** The GEDA file stores 9.969209968386869e+36 as data in 30,647 cells and NaN in 4,215 more, with no `_FillValue`. An ingest must mask `> 1e30` and treat both kinds as "no data".
2. **Footprint.** The valid-cell mask (28,970 cells) is the footprint, not the bounding box. The 8,804 cells removed by the authors and the cells outside it must give an absent addendum, never zero. Timbuktu's cell is outside.
3. **Units.** Values are z-scores against each cell's own 1000 to 2020 history, including the instrumental years; the addendum must say so. They are not comparable with OWDA's scPDSI, whose SD over Ukraine is about 1.9.
4. **Instrumental years.** 1990 to 2020 are observed CRU TS 4.06 scPDSI, restandardized, not reconstruction. The join is not flagged in the file. The Ukraine mean differs between 1960 to 1989 and 1990 to 2020 (0.37 against -0.04 for the cell average); whether that is climate was not tested.
5. **Skill.** No skill statistics in either file; no Ukraine figures in either paper. GEDA validation maps exist (Supplementary Fig. 4 was not in our copy of the supplement; the EPPR method is in Smerdon et al. 2023). Whatever the addendum says about reliability in Ukraine needs one of these, or the authors. OWDA's disagreement with GEDA in Ukraine is expected from the change of network and method and is not evidence against GEDA. LMR (annual, 2 degrees, a different variable and season) is uncorrelated with GEDA at annual resolution, so it cannot corroborate it; this matters for how the worked example presents the two.
6. **Resolution.** At L6 the median basin overlaps 9 cells, but 73% of footprint basins are below the engine's `w_eff` threshold of 5; a centre-in-basin rule would lose 16% of them. At L8 a centre rule would lose 70% of footprint basins and 68% in Ukraine; in Ukraine 94% of L8 basins are smaller than one cell (`w_eff` below 1), so neighbouring basins share cells and the value repeats across them. Whether to ingest L8 at all is a decision, not a measurement.
7. **Year labels.** Neither file states that the years are CE; GEDA's `yr` is "unitless". The papers and the OWDA readme say CE/AD.
8. **Variance.** GEDA's variance is flat across centuries in Ukraine and overall (Q8), unlike the LMR funnel. Whether that reflects the reconstruction method (nine-member ensemble, recalibrated at nine chronology cutoffs) or real stability was not tested.
9. **OWDA as a second source.** Not planned for ingest, and its authors now advise using GEDA instead; if it is considered later anyway: coverage and skill vary by cell start year (Q9, Q10), the file marks thin support only by start year, and the 26 northern-Arabian cells that OWDA has and GEDA lacks are unexplained.
10. **Housekeeping.** `data/eurasion_drought_atlas/geda_trim.nc` is a byte-identical copy of `data/geda/geda_trim.nc` (directory name misspelt); `data/` is gitignored. Redistribution terms beyond "cite the source" were not checked.

## What would answer what the files cannot

- GEDA calibration and validation maps and numbers, by cell: Supplementary Fig. 4 of the GEDA paper, Smerdon et al. 2023, or the authors.
- OWDA chronology counts and nest structure per cell: the OWDA supplement (Figs S6 and S11), not in `data/owda/`.
- Which GEDA cells were removed in trimming, and why the 26 Arabian cells are absent: the authors.
- Whether the 1990 shift in Ukraine is unusual: a comparison with other 30-year windows (not run).
- What GEDA's validation looks like over Ukraine: its Supplementary Fig. 4, Smerdon et al. 2023, or the authors (Edward Cook, Lamont-Doherty, is an author of the GEDA paper and led OWDA).
