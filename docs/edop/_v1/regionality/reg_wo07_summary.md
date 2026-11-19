# reg WO-07 summary: LBDA v3 through the registry

2026-11-19 to 20. Spec `reg_wo07_lbda.md`; record `reg_wo07_results.md`. Branch `lbda`, cut from `v1`. Nothing deployed; nothing pushed.

- **The data.** The Living Blended Drought Atlas v3 (June to August PMDI, contiguous US, 0 to 2025 CE, 0.5 degree) is loaded locally as `temporal.lbda_climate` (3,277 cells; NULL before each cell's first year) by `scripts/edop/regionality/load_lbda.py`, and checked value for value against the netCDF. Unlike GEDA the grid is not complete in early years: cells with data grow from 722 in year 0 to all by 1473 (the Four Corners, Chaco and Albuquerque from year 0; Santa Fe and Taos from 210). The characterization is `data/lbda_v3/LBDA-v3_characterization.md`.
- **Registry and coverage.** Registry entry `lbda_v3` (served), catalog row, two caveat texts (placeholder). Coverage is judged year by year: only cells that have a value that year count, the span is clipped to the years that meet the floor, and earlier years get no rows. The `sources` block gains a clipped-span flag (`years: {requested, returned}`). `_band_t_lbda` returns one row per year with its own coverage and status.
- **Dashboard.** An LBDA block after LMR on the Signature tab (histogram, slider, mean line, instrumental years from 1900 shaded, labelled PMDI and not standardized), and LBDA in the sources line. Placeholder wording; the spread band needs at least 5 cells (placeholder).
- **Tests.** `pytest -m lbda` runs 32 LBDA tests alone (about 25 s). The regression baseline now allows added sources, matched by id, with no re-capture; older exact-list tests ignore sources added since (`tests/regionality/sources.py`).
- **Year 0.** LMR (0 to 2000, 2,001 values), LBDA and HYDE all use 0 as 0 CE; CLAUDE.md's "1 to 2001" for LMR was wrong and is corrected.
- **The public basin route** does not serve LBDA (report only; what it would take is in the results).

Needs Karl: the placeholder wording, the two thresholds (band 5 cells; coverage 0.5 and 0.1; at 0.5 a single basin with early gaps, such as Santa Fe, is not flagged, a buffer is), whether to serve LBDA on the public basin route, and the server load before any deploy.
