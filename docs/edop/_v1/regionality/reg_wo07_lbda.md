# reg WO-07: LBDA v3 through the registry

Draft of 19 Nov 2026, for Karl's review. A build. Branch: cut from `v1` once `dashboard` and `v1` are level (Karl and CC).

## Goal

LBDA v3 (Living Blended Drought Atlas, June–August PMDI, contiguous US, 0–2025 CE) served in Band T through the source registry, with coverage judged year by year, and shown on the Dashboard's Signature tab. It is the data for the Pueblo worked example (`rubrics/Pueblo_notes.md`).

## Background

- `data/lbda_v3/LBDA-v3_characterization.md` (CC, 19 Nov) is the basis: structure, coverage, values, the draft registry entry and CC's observations. Read it first.
- Coverage grows through time: 722 cells at year 0, all 3,277 by 1473. The Four Corners, Chaco, Mesa Verde, Zuni, Hopi and Albuquerque have data from 0 CE; Santa Fe and Taos from 210 CE.
- PMDI is not GEDA's scPDSI and is not standardized. The two are never pooled or compared by number. Their footprints do not overlap.
- Before 1900 the values are reconstructed and neighbouring cells move almost together (pairwise correlation 0.98 in the Four Corners box); from 1900 they are instrumental.
- The file is extended by NCEI every year.

## Items

1. **Table and loader.** `temporal.lbda_climate` and `scripts/edop/regionality/load_lbda.py`, as proposed in the characterization (one row per cell with data, an array of years with NULL before the cell's first year, `first_year`, geometry, cell geometry, area, the same indexes as GEDA). Check the loaded values against the netCDF for the Four Corners cells and a few others.

2. **Registry and catalog.** The registry entry as drafted, with the version, file date and access date recorded and `years_covered` read from the file. A catalog row for `lbda_pmdi`. Placeholder caveat texts `lbda_caveat` and `lbda_instrumental`, marked for Karl. Data-sources lists complete.

3. **Coverage by year.** The registry's coverage check counts, for each year, only the cells that have a value in that year. The `sources` block reports a source that applies to only part of the span, and a span clipped to a source's years (the clipped-span flag missing since WO-05). GEDA's results must not change.

4. **Year 0.** Check how LBDA's year 0 lines up with LMR's and HYDE's year axes, and say so.

5. **Dashboard.** An LBDA block in Band T modelled on GEDA's: its own histogram and slider, the mean line, and the spread across cells shown only when there are enough cells (per the time series design note). Years from 1900 are shaded as instrumental, with a legend. Labels say PMDI, June–August, not standardized. Placeholder wording.

6. **The public basin route.** Report only: how `/api/signature?scope=basin` serves regional sources now (GEDA), and what serving LBDA there would take. Do not build it.

## Provisos

- Keep it short. One check per case, not a sweep. List anything else worth looking into in one line under "Needs attention" and stop there.
- No change to how HYDE, LMR, eVolv2k or GEDA are computed or displayed, apart from the shared coverage code in item 3.
- The table load is an additive step on the server database, as for GEDA; note it for the deploy.

## Deliverables and gate

- `reg_wo07_summary.md`, one page; `reg_wo07_results.md`, with the loader check, the year-0 finding, the coverage cases and the item 6 report.
- Tests: Chaco covered in full; a point in the eastern US at 300 CE reported as not applied; Santa Fe 100–300 reported as partly covered; Lviv's GEDA output unchanged.

Gate: Karl checks in a browser. Chaco 1100–1200 shows the LBDA block and the sources line lists LBDA. Santa Fe 150–300 says LBDA covers only part of the span. Lviv still shows GEDA as before.
