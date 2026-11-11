# WO-01 (regional data): GEDA and OWDA exploration

Draft of 2026-11-11, revised after CC review.

## Goal

Find out what the two drought-atlas files actually contain, beyond what the documentation says, so that the ingest design for GEDA (the first regional dataset) rests on facts. Exploratory only: a notebook and a results file. No ingest, no database writes, no app changes.

## Decided: scope before 1000 CE

GEDA is the pilot dataset and the only one planned for ingest. It starts at 1000 CE, and Ukraine before 1000 is out of scope for regional data.

- EDOPS serves LMR from 700 CE, following the LMR authors. For Ukraine, 700–1000 is covered by LMR alone.
- OWDA was set aside for that period: from its animation, it has no Ukraine values before about 700 and only the north until about 1000, built on very few distant chronologies.
- Worked example 1 (Ukraine) is now framed around this: it shows what can be said from time-specific data where it exists and from persistent features of the modern signature where it doesn't (see `docs/edop/_v1/rubrics/worked-examples-predesign.md`).

OWDA is examined here to confirm its Ukraine coverage from the data and to compare it with GEDA where they overlap. It is not a candidate for ingest.

## Inputs

- `data/geda/geda_trim.nc`: Great Eurasian Drought Atlas, Zenodo 10.5281/zenodo.11059894 (CC BY 4.0). Documented as JJA scPDSI, 0.5° grid, 37,774 points, 1000–2020 CE; tree-ring values 1000–1989, instrumental 1990–2020. "Trim" is unexplained.
- `data/owda/owda.nc`: Old World Drought Atlas, NCEI study 19419. Documented as JJA scPDSI, 0.5° grid, 5,414 points, 27.25–70.75 N, -11.75 to 44.75 E, 0–2012 CE; tree-ring values to 1978, instrumental 1979–2012.
- L6 and L8 basins from the EDOPS database (read only).
- Ukraine outline: `gaz.admin0` (Natural Earth). It is a modern border used as a study-area outline for earlier periods; the results say so.

## Questions

### Both files
1. Structure: dimensions, coordinate names and order, variable names, dtypes, units and other attributes, fill values, time axis (calendar years or otherwise), grid registration (cell centres at .25 or .0).
2. Extras: any variables or attributes beyond the main field, such as skill statistics (calibration or validation R², RE, CE), chronology counts, ensemble members, masks, or a flag marking tree-ring and instrumental years.
3. Do the two grids coincide cell for cell where they overlap?

### GEDA
4. Extent: bounding box and count of cells with any valid value. Does "trim" remove sub-Saharan Africa or the area south of the equator? Are Ukraine, Tbilisi and Timbuktu inside?
5. Units: raw scPDSI or restandardized? Report per-cell mean and standard deviation over the full record; values near 0 and 1 everywhere would indicate z-scores.
6. Missing values through time: count of valid cells per year; any cell with gaps inside its record.
7. The 1989/1990 join: for Ukraine cells, mean and variance for 1960–1989 against 1990–2020.
8. Variance by century, 1000–2020: per-cell variance for Ukraine cells, and the same table for a few reference cells elsewhere (for example western Europe, Anatolia, central Asia). The reference cells show whether any early-century drop is specific to Ukraine or a property of the whole dataset.

### OWDA
9. Ukraine coverage through time: first year with a valid value for each Ukraine cell. If every cell has values back to 0 CE, the gaps seen in the animation are not missing values in the file; then report what, if anything, in the file marks thin support (Q2), and say whether the readme or paper is needed to locate it.
10. Overlap with GEDA, Ukraine cells, 1000–1978: correlation and mean difference by century. The two share chronologies, so this measures consistency, not independent skill.

### Grid to basins (GEDA)
11. Within the GEDA footprint:
    - All L6 and L8 basins: number of cell centres falling in each basin; number of basins containing none.
    - L6 basins: number of cells overlapping each basin by area, as the Band T aggregator does for LMR (see the LMR rows in `engine.py`).
    - L8 area-weighted overlap for Ukraine basins only.
12. The L6 basins intersecting Ukraine, listed with their cell counts (centre and overlap).

## Provisos

- Report numbers and observations. Do not set thresholds or reach verdicts on what is good enough; Karl decides from the results.
- Where a question can't be answered from the file, say so and say what would answer it.
- Keep scripts in the notebook; nothing goes into the engine.

## Deliverables

- Notebook: `notebooks/edop/regionality/wo01_geda_owda_exploration.ipynb`, following `notebooks/CLAUDE.md`.
- `wo01_results.md`, next to this WO: one section per question, numbered as above; tables where they help; maps only where a table won't do (Q9).
- A short list of open issues for the ingest design.

## Acceptance gate

Every question has an answer or a stated reason why it can't be answered from the files.
