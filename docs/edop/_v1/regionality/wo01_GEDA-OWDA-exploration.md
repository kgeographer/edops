# WO-01 (regional data): GEDA and OWDA exploration

Draft of 2026-11-11.

## Goal

Find out what the two drought-atlas files actually contain, beyond what the documentation says, so that the ingest design for GEDA (the first regional dataset) rests on facts. Exploratory only: a notebook and a results file. No ingest, no database writes, no app changes.

## Inputs

- `geda_trim.nc`: Great Eurasian Drought Atlas, Zenodo 10.5281/zenodo.11059894 (CC BY 4.0). Documented as JJA scPDSI, 0.5° grid, 37,774 points, 1000–2020 CE; tree-ring values 1000–1989, instrumental 1990–2020. "Trim" is unexplained.
- `owda.nc`: Old World Drought Atlas, NCEI study 19419. Documented as JJA scPDSI, 0.5° grid, 5,414 points, 27.25–70.75 N, -11.75 to 44.75 E, 0–2012 CE; tree-ring values to 1978, instrumental 1979–2012.
- L6 and L8 basins from the EDOPS database (read only).
- A Ukraine boundary: use whatever admin boundaries the repo already has; otherwise Natural Earth admin-0. Report which.

## Context

GEDA is the planned pilot. OWDA is background: it was considered for Ukraine 700–1000 CE and set aside because its Ukraine coverage before 1000 is thin (from the OWDA animation: none before about 700, the north only until about 1000). This WO confirms that from the data and compares the two where they overlap.

## Questions

### Both files
1. Structure: dimensions, coordinate names and order, variable names, dtypes, units and other attributes, fill values, time axis (calendar years or otherwise), grid registration (cell centres at .25 or .0).
2. Extras: any variables or attributes beyond the main field, such as skill statistics (calibration or validation R², RE, CE), ensemble members, masks, or a flag marking tree-ring and instrumental years.
3. Do the two grids coincide cell for cell where they overlap?

### GEDA
4. Extent: bounding box and count of cells with any valid value. Does "trim" remove sub-Saharan Africa or the area south of the equator? Are Ukraine, Tbilisi and Timbuktu inside?
5. Units: raw scPDSI or restandardized? Report per-cell mean and standard deviation over the full record; values near 0 and 1 everywhere would indicate z-scores.
6. Missing values through time: count of valid cells per year; any cell with gaps inside its record.
7. The 1989/1990 join: for Ukraine cells, mean and variance for 1960–1989 against 1990–2020.
8. Ukraine by century: per-cell variance by century, 1000–2020. Look for a drop in early centuries (values pulled toward the mean).

### OWDA
9. Ukraine coverage through time: first year with a valid value for each Ukraine cell. Map or table; confirm or correct the reading of the animation.
10. Overlap with GEDA, Ukraine cells, 1000–1978: correlation and mean difference by century. The two share chronologies, so this measures consistency, not independent skill.

### Grid to basins (GEDA)
11. For L6 and L8 basins within the GEDA footprint: distribution of the number of grid cells overlapping each basin, and the number of basins whose area contains no cell centre. This informs whether area-weighted overlap (as in `grid_areal_distribution` for LMR) is required.
12. Same counts for the L6 basins intersecting Ukraine, listed by basin.

## Provisos

- Report numbers and observations. Do not set thresholds or reach verdicts on what is good enough; Karl decides from the results.
- Where a question can't be answered from the file, say so and say what would answer it.
- Keep scripts in the notebook; nothing goes into the engine.

## Deliverables

- Notebook: `wo01_geda_owda_exploration.ipynb`.
- `wo01_results.md`: one section per question, numbered as above; tables where they help; maps only where a table won't do (Q9).
- A short list of open issues for the ingest design.

## Acceptance gate

Every question has an answer or a stated reason why it can't be answered from the files.
