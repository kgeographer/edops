# WO-01 summary: what the GEDA and OWDA files actually contain

2026-11-11. Spec: `wo01_GEDA-OWDA-exploration.md`. Full numbers, one section per question: `wo01_results.md`. Notebook: `notebooks/edop/regionality/wo01_geda_owda_exploration.ipynb` (Cells 1 to 14). Branch `regionality`. Nothing was ingested, written to the database or changed in the app. All twelve questions are answered.

## The short version

GEDA is usable as the pilot dataset, with care. It covers all of Ukraine for every year from 1000 to 2020 with no gaps. But it is stored in a way that will bite an ingest (a hidden fill value, and z-scores instead of PDSI), its last 31 years are observations and not reconstruction, and in Ukraine it differs strongly from OWDA, the older product it replaces (the OWDA web app is in "legacy mode" and recommends GEDA). That difference shows where the newer network changed the answer; it is not evidence against GEDA. Nobody has published skill figures for Ukraine that we could find.

## What we found

1. **Both files read cleanly and share a grid.** Every OWDA cell sits exactly on a GEDA cell. Neither file carries any extra information: no skill statistics, no chronology counts, no flag for tree-ring versus observed years.
2. **GEDA has a trap.** Cells with no data are not all marked "missing". 30,647 cells hold the number 9.969e+36 (the netCDF default fill value) as if it were data, and the file does not declare it. Another 4,215 cells are empty. Any ingest must mask both.
3. **GEDA values are z-scores.** Every cell has mean 0 and standard deviation 1 over 1000 to 2020. "1.5" means 1.5 standard deviations above that cell's own long-run average, not a PDSI of 1.5. OWDA is not rescaled (its spread is about 1.9 times larger).
4. **What "trim" removed.** The authors cut sub-Saharan Africa and everything south of the equator. That is why the file has 28,970 cells with data, not the 37,774 in the documentation. Timbuktu's cell is outside; Kyiv's and Tbilisi's are inside; all 289 cells inside Ukraine have data.
5. **The join at 1990.** The paper says 1000 to 1989 is reconstruction and 1990 to 2020 is observed CRU data. The file does not mark it. In Ukraine the average sits higher in 1960 to 1989 than in 1990 to 2020 (0.37 against -0.04); we did not test whether that is climate or an artefact.
6. **GEDA's variance is steady across the centuries.** There is no early-century collapse of the kind we found in LMR (EDA F10.1). That is a measurement, not proof the early centuries are reliable.
7. **OWDA does have Ukraine data before 1000 CE.** This corrects the WO. The west and northwest (55 of 271 cells) have values from year 0, 80 cells by 600, 161 by 800, 174 by 1000, and the last by 1120. Coverage spreads from west to east, which is what the animation showed once you allow for its resolution. The map is `output/edop/regionality/wo01_ukraine_owda_first_year.png`.
8. **GEDA and the older OWDA barely agree over Ukraine.** The typical correlation is 0.05 over 1000 to 1978 (0.29 for 1900 to 1978), against 0.77 over Paris and 0.67 across Western Europe, falling steadily eastward; Ukraine is the lowest of any European country measured. We checked that this is not a year or grid misalignment. OWDA is the product GEDA replaces: its web app says it is in legacy mode and recommends GEDA, and the GEDA paper says it improves on OWDA (106 chronologies against 1,869, and a new method). Agreement is highest where OWDA's network was dense, so this maps where the newer network changed the answer; it is not evidence against GEDA. LMR, which the worked example also uses, correlates at about 0.1 or less with both at annual resolution, and smoothing to 31 years does not change that.
9. **Basins are finer than the data.** An L6 basin typically overlaps about 9 GEDA cells, but about three in four have less than the engine's "five cells' worth" cutoff for good resolution. An L8 basin in Ukraine is, for 94% of them, smaller than one GEDA cell, so neighbouring basins would share a value. A rule that uses only the cell centre would lose 16% of L6 basins and 70% of L8 basins; area weighting is needed.

## What the papers say, and what is still missing

GEDA (Cook et al. 2024) is built from 1,869 tree-ring chronologies by an ensemble regression method, calibrated on 1951 to 1990 and validated on 1920 to 1950. It reports validation as maps that look strongest over Western and Central Europe and weaker eastward, which fits finding 8. OWDA (Cook et al. 2015) uses 106 chronologies, "reasonably uniform ... except for Russia". **Neither gives skill numbers for Ukraine.** The GEDA validation maps and the Smerdon et al. 2023 method paper are the places to look next, or the authors.

## Corrections the WO text needs

- "EDOPS serves LMR from 700 CE, following the LMR authors": the 700 CE gate is on the Sandbox map layer only and comes from our own EDA; the signature reports LMR from 0 CE.
- OWDA coverage of Ukraine before 1000 (finding 7).
- "37,774 points" describes the full GEDA, not the trimmed file.
- The GEDA file comes from a Dropbox link in the paper, not Zenodo (the WO says Zenodo).

## Decisions for you and Opus

1. **Is GEDA still the pilot?** The case for: complete coverage and no gaps from 1000. The case for caution: no Ukraine skill figures. (Disagreement with the older OWDA is expected and is not part of the case.)
2. **Which basin levels to ingest.** L6 is workable with area weighting; at L8 the value repeats across neighbouring basins. Whether to offer L8 at all is a product choice.
3. **How to word the units and the instrumental years** in whatever the addendum says (z-scores against 1000 to 2020; 1990 to 2020 are observations).
4. **Whether the Ukraine example needs OWDA** for the early part, now that it has values from year 0 in the west, or stays with LMR alone before 1000.
5. **How to show GEDA and LMR together in the worked example.** At annual resolution they are uncorrelated over Ukraine (and over Paris), and smoothing to 31 years does not change that (figure `output/edop/regionality/wo01_ukraine_lowfreq.png`). With only 16 to 31 independent values, none of these correlations is solid either way.
6. **Whether to run one more check**: compare the 1990 shift with the differences between other 30-year windows.

The full list of open ingest issues is at the end of `wo01_results.md`.
