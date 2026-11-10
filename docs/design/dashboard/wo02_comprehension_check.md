# WO-02 comprehension check (for Karl; use only if Opus struggles or issues arise)

How to use. Give Opus `wo02_summary.md`, `wo02_master_table.csv` and `wo02_results.md`. Ask the ten questions in a fresh message, with no key. Compare with the key below. Questions 9 and 10 cannot be answered from the files; an honest answer says so.

## Questions (paste these)

1. How many statement types does WO-02 define, and in how many families?
2. Which statement types fell back to stating a number alone because their wording changed under a cutoff sweep, and which of them changed most?
3. When a variable is zero almost everywhere, which statement says that no percentile is given and why, and what does it need from outside the payload?
4. Which variables are left out of the cross-band statements, and why?
5. How does the Sandbox show a variable and its upstream version today, and what does the local-and-upstream family add?
6. A span runs past the end of the LMR record. What does the payload return for it, and which statement covers it?
7. What does a `no_data` status mean for `wetland_class`, and what does it mean for `slope_avg`? What evidence supports each reading?
8. HYDE grazing land does not equal pasture plus rangeland in some Band T payloads. How was it established whether the source or EDOPS's aggregation causes this?
9. What does HYDE's grazing layer contain beyond pasture and rangeland?
10. Why do about 110 basins outside Greenland have a missing stream gradient?

## Answer key (do not paste)

1. **54 statement types in 9 families** (Position 7, Empty cells 6, Local and upstream 5, Coverage and shortfall 4, Distribution 6, Categorical 4, Within-band 8, Cross-band 4, Band T 10). Summary, "What was done".
2. **Five fell back to the number alone:** POS-06 (the "Most of" share; wording changes for 37% of rows across the grid), LU-01 and LU-02 ("agree or differ"; 31% of single-basin pairs and 19.5% of area pairs), DIS-06 (concentrated label for continuous spreads; 13%), and CAT-04 (concentrated label for categorical mixtures; **66%, the most**). Two more could not be swept: DIS-04 (the tied weight is not in the payload) and BT-03 (`low_resolution`: the effective weight is not in the LMR rows). Summary, "What is unstable"; results, each family's sweep paragraph.
3. **EMP-01 (one basin) and EMP-02 (an area).** Example: "Cropland extent is zero in this basin. No percentile is given: 43% of all L6 basins are zero for this variable." They need the **catalog zero fraction** (`zero_fraction_s/u_L6/L8`), which is not in the payload. The Sandbox shows "not present here" or "largely absent" without the reason. Master table; results, Empty cells and issue 6a.
4. **Zero-aware variables** (catalog zero fraction of 0.20 or more: karst, wetland extents, cropland, pasture, permafrost and others), because their percentile 0 means "zero here" and their other values rank only the non-zero basins; and **variables with no catalog zero fraction**, which is `reservoir_vol` (77% of basins score exactly 0 on it; left in, it was the furthest from the median in 57% of single-basin queries). Band E has too few eligible variables. Also `dist_sink` is zero-aware at L6 and not at L8. Results, Cross-band.
5. **The Sandbox lists them as two separate rows and nothing links or compares them.** The family adds LU-01 and LU-02 (both percentiles and the gap in percentile points, with which side is higher), LU-03 (both raw values), LU-04 (one side has no usable percentile, saying what each side is) and LU-05 (no separate upstream value). It states no "agree or differ" label because that flips under the sweep. Master table (LU rows); results, Local and upstream.
6. **Only the covered years, with no placeholder rows and nothing marking the gap.** **BT-04** states it ("LMR covers 1980 to 1998 of the span 1980 to 2020; the record runs 0 to 1998 CE"). Examples: F41 (ends at 1998) and F42 (starts at year 0, so 50 BCE to 1 BCE are missing). Results, Band T (cell 8).
7. **`wetland_class`:** no wetlands ("absent", not missing). The provider's page says −9999 "indicates spatial units that contain no wetland areas"; confirmed in the data: in all 136 single-basin cases where `wetland_class` is `no_data`, both wetland extents read zero. **`slope_avg`:** missing, deliberately: the provider assigned −9999 to all of Greenland (302 L6 basins) because the elevation data over the ice sheet gave unreasonable slopes. Results, issue 5 and Within-band (cell 8).
8. **From the cells.** A check across all 2,215,829 HYDE cells (no missing values) found grazing larger than pasture plus rangeland in 225,394 cells at 0 CE, 254,579 at 1000 CE and 336,113 at 1950, and never smaller. The engine computes each total as the sum of cell value times the fraction of the cell inside the query area, the same fractions for every variable, so it is linear and cannot create the mismatch: it is in the source. Results, issue 8.
9. **Not established.** The files say the HYDE documentation was not checked and record it as an open question for the crosswalk. Any specific claim is unsupported. (Results, issue 8.)
10. **Not established.** The provider's page explains −9999 for stream gradient only for Greenland; why 110 non-Greenland basins also have it is recorded as an open question. (Results, issue 5.)

Optional third "cannot be answered" question: "What share of settlement queries have buffers that take in sea?" Not measured: the files give about 19% of 100 km buffers on random basins with a shortfall of at least 1%, and say settlements sit on coasts more often, probably higher, unmeasured.
