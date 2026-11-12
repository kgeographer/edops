# WO-02 summary: GEDA stored, and what a basin query returns

2026-11-11. Spec: `reg_wo02_store_GEDA.md`. Full numbers by item: `reg_wo02_results.md`. Notebook: `notebooks/edop/regionality/wo02_geda_store_and_aggregate.ipynb`. Loader: `scripts/edop/regionality/load_geda.py`. Branch `regionality`. The engine, API and app were not changed. The GEDA table exists only in the local database; putting it on the server is a later step.

## The short version

GEDA is now in the database, laid out like LMR, and running it through the same machinery LMR uses works and is fast. What it returns for a basin is a line with a band, as for LMR. The new finding is that the single average hides a lot: within a basin the cells often disagree, so the distribution is worth delivering. A few small changes would be needed before it is shown to users.

## What was done

- **Stored:** `temporal.geda_climate`: 28,970 cells, one row each with 1,021 annual values (1000 to 2020), checked cell by cell against the file. The file's checksum matches the one the WO gives for Zenodo. The table carries a short comment with its source and units, and the docsite has a GEDA section marked "not yet returned by the API or the Sandbox".
- **What a basin query returns today for LMR:** a weighted average of the 2° cells over the basin for each year, with a p10 to p90 band and a histogram of the cell values. For the Kyiv basin LMR has only 3 cells (really 2), and it is flagged low-resolution in every year.
- **GEDA through the same path** gives 27 cells for that basin, not flagged low-resolution, and takes 0.01 s.

## What we found

1. **Averaging barely smooths the line.** Neighbouring cells within a basin are strongly correlated (0.64 to 0.97), so the basin's line is only 1% to 15% narrower than one cell's. Re-standardizing it against the basin's own record changes it by at most 17%, so the two lines are almost the same.
2. **The average hides real spread.** In a typical year the gap between the cells (p10 to p90) is 0.6 to 1.2 standard-score units. In Tbilisi's mountainous basin it is wider than the whole 1000 to 2020 line varies. The WO's principle, delivering the distribution as well as a number, is supported.
3. **Few-cell and partial basins return numbers that mean less than they look.** A one-cell basin has a "distribution" that is a single point. A 37,000 km² basin that GEDA covers only 6.7% of still returns a value. A basin wholly outside the footprint returns nothing, which is right.
4. **Year ranges behave like LMR's:** spans are clipped where they overlap the data and return nothing where they do not.
5. **Next to LMR the two do not agree.** On the Kyiv basin over 1300 to 1400 the correlation is -0.39, GEDA swings about three times as widely, and LMR's band is almost a line. Shown side by side, they would look like unrelated series.
6. **The 1990 shift in Ukraine** (mean of 1990 to 2020 minus 1960 to 1989) is negative in nearly every basin and larger than a typical adjacent-window change (0.46 against 0.28), but not extreme: for the Ukraine-wide average it ranks 11th of 33 adjacent pairs.

## What a GEDA delivery would need (none of it made)

A GEDA block beside LMR's (cell boxes, year 1000 to 2020, one variable); a `low_coverage` status for partly covered basins; a flag or caveat for the observed years from 1990; a GEDA caveat text (z-scores, summer only, reliability follows tree-ring density); the effective cell count in the payload (the engine computes it but does not report it for LMR); and p10 to p90, not min and max, in any panel, because min and max are set by low-weight cells.

## Asides

- **Cliopatria over Ukraine** (item 5a): from the 13th century one polity usually covers 40% to 98% of Ukraine, but its polygon is much larger than Ukraine and changes from slice to slice; before about 1000 coverage is patchy, with no polity covering more than about 1% at 0, 100, 200 and 500 CE. So the polity path gives Ukraine-ish areas, not Ukraine.
- **Is Ukraine's polity count unusual?** No: 73 polities cover at least 1% of it, fifth in Europe behind Germany, France, Italy and Poland, and typical for a large continental country.

## Decisions for you and Opus

1. **Coverage rule:** the level below which a basin returns `low_coverage` or no value (150 of 6,630 footprint basins are under 50% covered, 46 under 10%).
2. **What the panel shows for low-resolution basins:** the band, a note, or only the cell list.
3. **Whether the re-standardized line is worth offering** given that it differs from the plain line by at most 17%.
4. **How to mark the observed years** (1990 to 2020).
5. **Whether GEDA and LMR appear in the same panel**, given that they disagree.
6. **When to load the table on the server** and add the Band T block.
