# LBDA v3: what the file holds

**For Opus.** This note is from Claude Code (CC), for Karl to pass to you. Context: the v1 plan (19 Nov, `docs/edop/_v1/EDOPS v1 plan 19Nov.md`) lists "LBDA ingested through the registry, for the Pueblo example" as a Must item. Karl's immediate use is the Four Corners and the Chaco-to-Rio Grande example (`rubrics/Pueblo_notes.md`). He asked CC for a characterization of the downloaded file first, as was done for GEDA. This is that, with a draft registry entry (last section) and CC's observations for you (the section after it). The expected next step is a work order from you, which CC will review and comment on. Nothing has been loaded to a database, added to the registry or committed.

19 Nov 2026. A first look at `LBDA-v3.nc` (89 MB) against two text files saved beside it: the NOAA readme for the dataset (on the NCEI server as `LBDA-v3-readme.txt`; saved here as `README.txt`) and the text of the study page (saved here as `README2.txt`). Read-only; nothing in the file was changed. Numbers were computed from the file; statements about method and versions are NOAA's.

## Source (from the two NOAA texts)

- **Living Blended Drought Atlas, version 3**, Continental United States, June-August Palmer Modified Drought Index (PMDI), years 0 to 2025 CE. Investigators Gille, Morrill, Wahl, Vose, Cook. Dataset DOI 10.25921/7xm8-jn36; file last modified 2026-02-25. Study page: https://www.ncei.noaa.gov/access/paleo-search/study/22454. Distributor NCEI (paleo@noaa.gov).
- The reconstruction is Cook et al. 2010 (*J. Quaternary Science* 25(1): 48-61, doi 10.1002/jqs.1303): tree-ring based, half-degree grid. It is extended to the present with instrumental PMDI calculated from NClimGrid (5 km temperature and precipitation aggregated to half a degree).
- **What v3 changes from v2:** no recalibration of the reconstruction when blending; **the blend is at 1900** (1899 and earlier are reconstructed, 1900 and later instrumental; v2 blended at 1979); extended from 2017 to 2025. NCEI will extend it every year after the latest summer values, so **the file will change; pin the version and date.**
- **Use constraints (study page):** cite the original publication, the online resource, the dataset and publication DOIs, and the date accessed. A disclaimer says NOAA does not endorse external sites linked from the page. No licence beyond the citation request is stated.
- The two texts carry the same description and abstract. The readme adds the investigators, the DOI, the variable definitions and the download links; the page adds the use constraints, the distributor and the metadata links (DIF and ISO XML for study 22454; its JSON link uses `xmlId=20650`, not 22454, and was not followed).
- **Bounds differ between the two.** The readme gives 25 to 49 N and -124.5 to -67 E, which are the file's cell edges; the page rounds outward to 24 to 50 N and -124 to -68. The page's years line, "1950 cal yr BP (0 CE)" to "-75 cal yr BP (2025 CE)", shows that year 0 is NOAA's own label for the first year.

## What Cook et al. 2010 says (`articles/sources/Megadroughts_in_North_America_placing_IP.pdf`)

The paper describes the original Living Blended Drought Atlas (version 1), which v3 builds on; v3's pre-1900 values are v1's reconstruction (the readme: no recalibration). Read from the text; the figures (including the skill maps, Fig. 6) were not read.

- **Method.** Summer (June-August) reconstructions by "point-by-point regression" (Cook et al. 1999) on a tree-ring chronology network, half-degree grid. Calibration 1928 to 1978, verification 1895 to 1927. **The reconstructions are rescaled to recover the variance lost to regression**, so they have the instrumental spread: this is consistent with the matching SD either side of 1900 in the Four Corners cells.
- **Skill is modest and varies by place.** Over the whole North American grid, 95% of grid points have a positive calibration CVRE (median 0.29); verification statistics are positive at 59% (VRSQ, median 0.23), 53% (VRE, median 0.21) and 39% (VCE, median 0.20) of points. In the 30 to 50 N band they rise to medians of 0.43 (CVRE), 0.33 (VRSQ), 0.31 (VRE) and 0.27 (VCE), comparable to Cook et al. 1999 for the coterminous US. The paper's box means fit well (California-Nevada, 253 grid points: calibration R2 0.79, verification r2 0.52; Mississippi Valley: calibration R2 0.88).
- **Cells that failed verification are kept in the product.** The paper: "all reconstructions are left in the LBDA with the belief that the quality of some may be higher than their verification statistics indicate". **The netCDF carries no per-cell skill or verification flag**; the only place it appears is Fig. 6 of the paper.
- **Fig. 6, read by eye (`articles/sources/LBDA_fig-6.png`; not measured, the cells are too small to pick out at that size).** Calibration skill (CVRE) is strongest across the interior West and Plains (mostly about 0.5 to 0.7) and weak in the east, Mexico and Canada. The verification maps (VRSQ, VRE, VCE) are patchier: strongest over Texas and Oklahoma; in the Southwest and Great Basin patches of about 0.4 to 0.6 alternate with patches of 0 to 0.2, with a few white holes (failed verification). The Four Corners cells therefore sit in a region of reasonable but uneven skill; a per-cell value would need the data behind the figure, which is not in the netCDF.
- **Instrumental side (v1):** gridded monthly temperature and precipitation from station records (thin-plate-spline normals, inverse-distance anomalies), PDSI computed with soil-capacity estimates; v1 switched to instrumental data after 1978 (v3: 1900, with NClimGrid).
- **Naming.** The paper calls the quantity the summer PDSI; the NOAA files call it the Palmer Modified Drought Index (PMDI). I have not resolved whether this is a different calculation or a label.
- **Not in the paper:** how far a cell's reconstruction reaches for chronologies (so no explanation of the 0.98 pairwise correlation before 1900), why coverage grows through time (that follows the chronology network), or the zeros.
- **The Colorado Plateau.** The paper cites a 24-year drought, 1276 to 1299 CE, as a likely cause of the abandonment of the Anasazi cliff dwellings. In the 48 Four Corners cells, 22 of those 24 years are below zero and the box mean is -1.22 (mean of all years 0.03). Among all 2,003 24-year windows in the record it ranks 88th driest, so in the driest 5% but not the driest: the driest are around 127 to 165 CE (about -3.3), where the data comes from the thinnest part of the network, so I would treat those as a caution, not a finding.

## Structure

| | |
| --- | --- |
| Variable | one: `PMDI`, float64, `long_name` "JJA PMDI", units "dimensionless" |
| Dimensions | `lon` 115, `lat` 48, `time` 2,026 (dimension order lon, lat, time) |
| Grid | 0.5 degree, cell centres at .25 and .75: lon -124.25 to -67.25, lat 25.25 to 48.75 (5,520 cells) |
| Time | annual, 0 to 2025 (one value per year, June-August) |
| Missing values | `NaN`; no fill-value attribute, no sentinel numbers (-999, -9999 and others: none present) |
| Other metadata | the only global attribute is a description ("Living Blended Drought Product version 3"); no CRS, no `_FillValue`, no history |

## Coverage: not a complete grid

- **3,277 of the 5,520 cells ever have data** (59%): the contiguous US; every cell outside it is empty (Mexico, Canada, ocean). 56% of all cell-year values are `NaN`.
- **The set of cells with data grows through time and never shrinks**, because the tree-ring network thins into the past:

| Year (CE) | Cells with data | Share of 3,277 |
| --- | --- | --- |
| 0 to 299 | 722 | 22% |
| 400 | 1,620 | 49% |
| 700 | 2,047 | 62% |
| 1000 | 2,983 | 91% |
| 1300 | 3,196 | 98% |
| 1473 onward | 3,277 | 100% |

- In the earliest centuries the 722 cells lie only between 32 and 44 degrees N and west of 106 degrees W. By 500 CE the data reaches 74 degrees W; by 1500 the whole country is covered.
- Only **722 cells have a value in every one of the 2,026 years**; the per-cell count of years runs from 553 to 2,026.
- A query for any place in the eastern US before about 500 CE therefore has no data, and a query anywhere before 1473 may have data for only some of the cells it covers.

## Four Corners and the Rio Grande (window 31 to 42 N, 113 to 104 W)

The Four Corners monument is at about 37.0 N, 109.05 W. Checked cell by cell for the window around it (396 cells; 385 ever have data; the other 11 lie on its northwest and southern edges):

| Place (point used) | Cell centre | First year with data | Years with data |
| --- | --- | --- | --- |
| Four Corners monument (37.0, -109.05) | 36.75, -109.25 | 0 | 2,026 |
| Mesa Verde (37.18, -108.49) | 37.25, -108.25 | 0 | 2,026 |
| Chaco Canyon (36.06, -107.96) | 36.25, -107.75 | 0 | 2,026 |
| Zuni (35.07, -108.85) | 35.25, -108.75 | 0 | 2,026 |
| Hopi mesas (35.8, -110.6) | 35.75, -110.75 | 0 | 2,026 |
| Albuquerque, Rio Grande (35.08, -106.65) | 35.25, -106.75 | 0 | 2,026 |
| Santa Fe (35.69, -105.94) | 35.75, -105.75 | 210 | 1,816 |
| Taos, Rio Grande (36.41, -105.57) | 36.25, -105.75 | 210 | 1,816 |

- **The Four Corners, Chaco and the Rio Grande at Albuquerque have a value in every year from 0 CE.** The early footprint here is a solid block, not a scatter: 254 of the window's 385 cells have data from year 0, all west of about 106 W, and the rest fill in as solid blocks too (the east of the window, from 106 W to 104 W, from about 200 CE; its southern rows, 31.25 to 33.75 N, from about 300 CE). From 300 CE all 385 cells have data.
- **The edge matters for the Rio Grande.** Cells centred at -105.75 (Santa Fe, Taos) start at 210 CE, so a Chaco-to-Rio-Grande example that goes as far as the northern Rio Grande pueblos has no data there for its first two centuries. A span from 500 CE on is fully covered everywhere in the window.
- The window map was read at half-degree cells, so a point is matched to the cell that contains it; the monument itself falls in the cell centred at 36.75 N, -109.25 E.

## The 1900 blend in the Four Corners cells (48 cells, 35 to 38 N, 111 to 107 W; all have every year)

- **No visible seam in the size of the values.** The SD of a cell's series is about the same either side of 1900 (median ratio of 1900-2025 to 1600-1899: 1.01, range 0.88 to 1.34); the change from 1899 to 1900 averages 1.35, smaller than the typical year-to-year change before 1900 (2.44). Pooled mean and SD: 1800-1899 0.24 and 2.61; 1900-1949 0.63 and 2.68; 1950-1999 -0.18 and 2.46; 2000-2025 -2.05 and 2.25.
- **The cells agree with each other far more before 1900 than after.** The average correlation between pairs of the 48 cells is **0.98 in 1600-1899 and 0.79 in 1900-2025.** Before 1900 the box behaves almost as one series. My reading (not checked against the paper): neighbouring cells draw on the same tree-ring chronologies, so their reconstructed values move together, while the instrumental values carry real local differences. The consequence for EDOPS is that a distribution across cells in a Four Corners-sized area before 1900 will be narrow, and its width says little about how much the climate varied from place to place.
- **Persistence differs:** mean lag-1 autocorrelation 0.32 in 1600-1899 and 0.18 in 1900-2025 (the reconstruction is smoother from year to year).
- **A step in the mean cannot be separated from climate.** The box mean is -0.49 for 1870-1899 and 0.70 for 1900-1929. This could be the blend or a wetter early 20th century; with no overlap period in v3 (it switches at 1900, with no years in both) the file cannot say.
- **Extremes:** the share of cell-years below -4 is 5.2% before 1900 and 7.6% after; above 4, 7.3% and 6.1%. The driest 5-year box mean in the whole record is 143 to 147 CE (-5.64); in 1100-1200 it is 1147 to 1151 (-3.84); in 1250-1300, 1250 to 1254 (-2.85); since 1900, 2000 to 2004 (-3.38).
- 12 of the box's values are exactly 0 (ordinary rounded values; see Values).

## Values

- Pooled over all cell-years: mean -0.08, SD 2.30, range -26.07 to 19.37. Quantiles: 0.1% -7.9, 1% -5.6, 5% -3.8, 25% -1.6, median -0.1, 75% 1.4, 95% 3.7, 99% 5.6, 99.9% 8.0.
- **Reconstructed (0 to 1899) and instrumental (1900 to 2025) periods differ in their tails:** SD 2.29 against 2.40; minimum -16.8 against -26.1 (the instrumental minimum is a south Texas cell, lon -99.25, lat 26.75, in 2009); maximum 19.4 (reconstructed, lon -100.25, lat 35.75, year 598) against 14.6. The domain-mean series has a similar SD in the last century before and after 1900 (1.04 and 1.00). I did not test for a step in the mean at 1900.
- Per-cell SD before 1900 runs from 1.1 to 3.7 (median 2.2). Year-to-year persistence is weak: lag-1 autocorrelation about 0.2 (a sample of the 722 full-record cells).
- **The 844 exact zeros are ordinary values, not a fill.** 93% of the values are stored to three decimals, so anything within 0.0005 of zero is stored as 0.000. The counts of values by 0.001 step around zero are flat: -0.003 to 0.003 gives 948, 913, 935, **914 (zero)**, 872, 882, 906; zero is no more common than its neighbours. The zeros are 0.02% of values, spread over 747 cells and 642 years (never in adjacent years in the same cell, at most 3 in a cell, at most 5 in a year), 840 of them before 1900, none in a cell's first valid year, and their neighbouring years look normal. There is no negative zero and no other repeated sentinel. (From the file alone; the paper or NCEI could confirm the rounding.)

## Against GEDA

| | LBDA v3 | GEDA (`data/geda/geda_trim.nc`) |
| --- | --- | --- |
| Index | PMDI (Palmer Modified Drought Index) | scPDSI (self-calibrating PDSI) |
| Units | dimensionless, not standardized | "sigma"; mean 0.0, SD 1.0, range -4.99 to 5.8 |
| Season | June-August | June-August |
| Years | 0 to 2025 (2,026) | 1000 to 2020 (1,021) |
| Grid | 0.5 degree, 115 x 48 | 0.5 degree, 404 x 158 |
| Footprint | contiguous US | Eurasia |
| Complete grid? | no: cells with data grow from 722 (year 0) to 3,277 (1473) | yes within its footprint (EDOPS stores 28,970 cells and tests footprint only) |
| Recent years | instrumental from 1900 | observed years 1990 to 2020 (as shown in the Dashboard) |
| Values in this file | mean -0.08, SD 2.30, -26 to 19 | mean 0.0, SD 1.0, -5 to 5.8 |

The two are the same kind of thing (a summer Palmer-family drought index reconstructed from tree rings on a half-degree grid) but **not the same measurement**: the index variant differs, and LBDA is not standardized, so a value of -4 in one is not a value of -4 in the other. They should be served side by side with their own labels, never pooled or compared by number. The footprints do not overlap.

## What this means for the registry and the engine

1. **The coverage rule has to be per year, not only per footprint.** GEDA's registry check judges years and a fixed footprint; LBDA's footprint changes by year. A request for a place and span needs the count of covered cells per year, and low coverage should be reported as the sources line does today.
2. **The blend at 1900 needs a caveat in the payload,** as GEDA's observed years have: reconstruction to 1899, instrumental from 1900, with the wider instrumental tails.
3. **The data is a living file** (annual extensions). The registry entry should record the version, the last year and the access date; a loader should read the last year from the file.
4. **Storage** would follow GEDA's shape (a table of cells with an array of years): 3,277 cells, 2,026 years, about 26 MB as `real[]`, a small load.
5. **Citation** follows NOAA's request (publication, online resource, DOIs, access date); the registry has fields for it.

## Open points

- Why neighbouring cells agree so closely before 1900 (0.98): not explained in the paper; the 1999 method paper or NCEI would say.
- Mapping year 0 to the other sources' year axes (HYDE and LMR) before any combined query.
- Not done: no maps or plots, no comparison with v2 or v1, no check of how the instrumental blend compares with the reconstruction in an overlap period, no check of a cell against the paper.

## Draft registry entry: LBDA v3

Draft only; nothing has been added to `documentation/EDOPS_source_registry.yaml`. It follows the GEDA entry. The lines marked NEW or proposed are where LBDA needs something GEDA did not.

```yaml
  - id: lbda_v3
    selects:
      kind: gridded_time_series
      status: proposed                             # not loaded; a table and a loader come first (see below)
      table: temporal.lbda_climate                 # proposed: 3,277 cells; 2,026 values each (real[], NULL before a cell's first year)
      footprint:
        type: cells
        test: temporal.lbda_climate.cell_geom      # gate = the query geometry intersects these cells
        cells: 3277
        varies_by_year: true                       # NEW: the cells with data grow from 722 (year 0) to 3,277 (1473); coverage is counted per year
      time:
        step: annual
        years_covered: [0, 2025]                   # the loader reads the last year from the file; NCEI extends it every year
        year_to_array_position: "year + 1"
        step_rule: "every year in the span, clipped to years_covered"
      spatial:
        method: cell_overlap_weighted
        cell: {size_deg: 0.5, geometry_column: temporal.lbda_climate.cell_geom}
        lon_convention: "-180..180"
      coverage_rule: {ok_from: 0.5, low_coverage_from: 0.1, per_year: true}   # GEDA's starting values; coverage = the share of the query area covered by cells that have a value in that year
      years_recommended: null
      year_flags:
        - {years: [1900, 2025], flag: instrumental, caveat: lbda_instrumental, note: "instrumental PMDI (NClimGrid), not reconstructed; 0-1899 is reconstructed"}
      caveats:
        - {key: lbda_caveat, when: "every LBDA row"}
        - {key: lbda_instrumental, when: "year in 1900-2025 (the instrumental year flag)"}
      variables:
        - {payload: lbda_pmdi, catalog: lbda_pmdi, column: pmdi, units: "PMDI (dimensionless)"}
      columns: {pmdi: "JJA Palmer Modified Drought Index, not standardized (SD about 2.3, range -26 to 19 over the file)"}
    describes:
      name: Living Blended Drought Atlas, version 3 (Continental United States, June-August PMDI)
      version: "3 (NOAA NCEI study 22454; file last modified 2026-02-25; extended each year)"
      grain: "0.5 degrees"
      citation: "Cook et al. 2010, Journal of Quaternary Science 25(1): 48-61; data by Gille, Morrill, Wahl, Vose and Cook, NOAA NCEI"
      doi: 10.1002/jqs.1303
      dataset_doi: 10.25921/7xm8-jn36
      licence: "NOAA NCEI use constraints: cite the publication, the online resource, the DOIs and the date accessed"
      licence_url: https://www.ncei.noaa.gov/access/paleo-search/study/22454
      licence_note: "No licence other than the citation request is stated on the study page or in the readme."
      legacy_notes: []
      notes: "Continental US only. Reconstruction 0-1899 CE, instrumental 1900-2025 CE."
```

**What is different from GEDA, and needs a decision:**

1. **Footprint varies by year (new field `varies_by_year`, and `per_year: true` on the coverage rule).** GEDA's gate tests the query geometry against a fixed set of cells. For LBDA a place may be inside the footprint but have no data in an early year (eastern US before about 500 CE). The coverage fraction has to count only cells that have a value in that year, and the `sources` block should say so when a span is only partly covered. This is a change to the engine's coverage code, not only to the registry.
2. **Storage of missing years.** Proposed: `temporal.lbda_climate`, one row per cell with data, `pmdi real[2026]` holding NULL before the cell's first year, plus a `first_year` column, `geom`, `cell_geom` and `area_km2`, with the same two spatial indexes as GEDA; loader `scripts/edop/regionality/load_lbda.py` reading `data/lbda_v3/LBDA-v3.nc` (about 26 MB of arrays). Whether NULL inside an array is handled by the existing numpy reduction needs checking.
3. **Coverage thresholds.** The 0.5 and 0.1 values are GEDA's starting values, copied. With a per-year rule, a span that crosses the early centuries can change status from one year to the next.
4. **Caveat texts (to write; placeholders in the entry):** `lbda_caveat` (a Palmer index that is not standardized, so its numbers cannot be compared with GEDA's; the reconstruction is spatially smoothed before 1900, so the spread across cells is small; skill is modest and uneven, see Cook et al. 2010 Fig. 6; the file has no per-cell skill flag) and `lbda_instrumental` (the 1900 blend).
5. **Catalog.** Every returnable variable needs a catalog row and key: `lbda_pmdi` is new. NOAA's name is PMDI; the 2010 paper calls the quantity the summer PDSI. I used NOAA's.
6. **Year axis.** Array position `year + 1` puts year 0 at position 1. The NOAA label for the first year is 0 CE (1950 cal yr BP); check how HYDE and LMR treat year 0 before a combined query.
7. **A living file.** `years_covered` must be set from the file at load time, and the entry's version and access date updated when NCEI extends it.
8. **Licence** is the citation request only (no CC or other licence named); confirm with NCEI if a licence line is needed for the docs.

## Observations for Opus

What CC would want a work order to take into account, in rough order of importance. CC's readings are marked as such; none has been tested beyond what is stated above.

1. **For the Four Corners example the coverage problem does not bite; for the general case it does.** Every cell around the Four Corners, Chaco, Zuni, Hopi and Albuquerque has a value in every year from 0 CE; only the northern Rio Grande (Santa Fe, Taos) starts at 210 CE. A span from 500 CE on is fully covered across the whole window. The per-year coverage rule (draft entry, decision 1) matters for places elsewhere in the US and for early spans, and without it Band T would quietly return partial results there. The work order could stage it: load and serve with the per-year rule built from the start (CC's preference, since an unflagged partial result would be misleading and the engine's coverage code is the right place), or serve first with a plain footprint test and add the rule before the public API serves LBDA. Either way, the example does not depend on it.
2. **The reconstruction is spatially smooth before 1900, which affects how Band T should show it.** In 48 Four Corners cells the average pairwise correlation is 0.98 before 1900 and 0.79 after. CC's reading, not confirmed (the 2010 paper does not say): neighbouring cells share the same tree-ring chronologies. If so, the Band T histogram across cells (as built for GEDA and LMR) will be narrow for a Four Corners-sized area and says little about real spatial variation. A time-series line of an area mean, or a histogram with a caveat, may suit LBDA better. Worth measuring the same pairwise correlation in GEDA before deciding whether this is a property of drought atlases in general or of LBDA's method; CC has not done that.
3. **Skill is modest, uneven and not in the file.** Median verification skill is 0.23 over the whole North American grid and 0.33 for 30 to 50 N (VRSQ); Fig. 6 shows the Southwest and Great Basin as patchy, strongest over Texas and Oklahoma. The netCDF has no per-cell skill, and the paper keeps cells that failed verification in the product. A caveat can state this in words; a per-cell number would need the authors' or NCEI's calibration and verification grids (CC cannot load the NCEI page; Karl may be able to find them).
4. **The 1900 blend cannot be tested from this file.** There are no overlap years, so a step at 1900 cannot be separated from a wetter early 20th century (box mean -0.49 for 1870-1899, 0.70 for 1900-1929). The two periods also differ in persistence (lag-1 autocorrelation 0.32 against 0.18) and in the tails (minimum -16.8 reconstructed, -26.1 instrumental). The Pueblo span (about 500 to 1300 CE) is entirely reconstructed, so this matters only for comparisons with the modern period.
5. **The 1276 to 1299 drought is present but not exceptional here.** The 2010 paper ties it to the abandonment of the Colorado Plateau cliff dwellings. In the Four Corners box 22 of the 24 years are below zero (mean -1.22) and it ranks 88th driest of 2,003 24-year windows; the driest windows are around 127 to 165 CE (about -3.3), where the data is thinnest. If the example is presented as a known-answer test, it should not claim the 13th century as the driest period in the record, and any claim about the earliest centuries needs the coverage caveat.
6. **The index is not GEDA's index.** PMDI against scPDSI, unstandardized (SD 2.3, range -26 to 19) against z-scores (SD 1, range -5 to 5.8). A Dashboard that shows them side by side must label them separately; no pooling, no comparison by number. The 2010 paper calls the quantity the summer PDSI and NOAA calls it PMDI; CC does not know whether this is a different calculation or a label.
7. **Year 0.** NOAA labels the first year 0 CE (1950 cal yr BP). CLAUDE.md records LMR's array as "1 to 2001 CE, 0-indexed" and the registry maps `year + 1`; the registry entry uses `year + 1` for LBDA too. The offsets should be checked against HYDE and LMR before any combined query.
8. **A living dataset.** NCEI extends it every year. The registry entry, the loader and the docs should record the version and access date, and take `years_covered` from the file; the readme's guidance is to cite the access date.
9. **Practical points from earlier regional work (GEDA).** A new source needs: the table loaded to the server database before code that serves it runs (the v1 alpha shares the live database, so this is an additive step, as for GEDA); the public basin path has its own Band T code (`band_t_geda_for_point` for GEDA), so serving LBDA on `/api/signature?scope=basin` is a second piece of work; the data-sources lists must be complete (`_data_sources_block`, both schema JSONs and the registry); the regression baseline allows added fields; the Dashboard's GEDA block (own histogram and slider, observed years shaded) is the pattern, with the instrumental years from 1900 in the place of the observed years 1990 to 2020.
10. **Verification of a loaded table.** CC would check the loaded cells against the netCDF for the Four Corners cells and a few others (value for value), and test the per-year coverage on a point in the east for an early year (should report not applied) and on Chaco (should report full coverage).

**Limits of this note.** Read from the file, the two NOAA texts and the paper's text (the PDF's page renderer is not installed here; the text was extracted, with the columns run together, and Fig. 6 was read by eye from the PNG). The paper describes version 1; version 3's differences are from the NOAA readme. No maps or plots were made; no comparison with v1 or v2; the reconstruction was not compared with the instrumental data (no overlap exists in the file); a few cells were looked at, not all.
