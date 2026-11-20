# reg WO-08 summary: LBDA, finishing items

2026-11-20. Spec `reg_wo08_lbda-finish.md`; record `reg_wo08_results.md`. Branch `lbda`. Nothing deployed or pushed.

- **Early gaps are named.** A year is flagged when its coverage is more than 5 points below the span's final year. The `sources` note and the Dashboard block now say, for the Santa Fe Level 6 basin, 150 to 300: "early years cover less of the area: 150-209 at 77%, against 100% from 210 on". Chaco is not flagged. The 0.1 and 0.5 thresholds are unchanged; the Dashboard shows the engine's note, so the wording has one source.
- **Data for the band threshold.** Cells under each contiguous-US basin: at Level 6 (932 basins) 22% have under 5 cells, 63% under 10, 92% under 20 (median 8); at Level 8 (10,933 basins) 90% have under 5, 99.9% under 10 (median 2). `MIN_CELLS_FOR_BAND` stays 5; Karl sets it. At 5, about 78% of Level 6 basins get a spread band and about 10% of Level 8.
- **Documentation.** LBDA section in `docsite/data-sources.md`; Codebook regenerated; the catalog row is `implemented`.
- **Baseline.** Three US cases added (Chaco, Santa Fe buffer, Cahokia clipped) with no existing reference re-captured; the capture script now keeps the original manifest date and records additions.
- **Tests.** `pytest -m lbda` 40 passed; regionality, codebook and API tests 152 passed.

Needs Karl: the Santa Fe gate in the Dashboard, then `lbda` can merge into `v1`; `MIN_CELLS_FOR_BAND` from the table; the WO-07 items still open (wording, `scope=basin`, sources line).
