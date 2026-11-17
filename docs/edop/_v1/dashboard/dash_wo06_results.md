# dash WO-06 results: time series, preliminary questions

2026-11-17. Spec `dash_wo06_time-series-prelim-stuff.md`; summary `dash_wo06_summary.md`. Branch `dashboard`. Nothing changed in the app, engine, API or database; nothing deployed. Scripts (scratch, in `scripts/edop/dashboard/`): `dash_wo06_per_source.py`, `dash_wo06_hyde_plan.py`, `dash_wo06_hyde_variant.py`, `dash_wo06_hyde_fixed_total.py`. Data in `output/edop/dashboard/wo06_*.csv` (gitignored). All times are from the local machine and database, one user, medians of 3 for `dash_wo06_per_source.py` and single runs for the others.

## What the measurements are for

Two decisions: (1) the **governor** on the Dashboard's year inputs, by scope (items 2 and 4); (2) the **shape of a Time series tool** and whether polities can have one (items 1 and 3). There are two limits in play: **delivery** (how long the payload takes, measured here) and **display** (what the interface does with a large result; a design question, not measured beyond WO-05's render times).

## Item 3: chosen variables on the engine path (code reading)

- The Band T functions (`_band_t_hyde`, `_band_t_lmr`, `_band_t_evolv2k`, `_band_t_geda`, called by `aggregate_band_t`) take only the query object. There is no variable filter and no lean mode.
- `detail` is a projection at serialization (`project_row`): histograms are always computed (`_weighted_histogram` per row, `_agg_hyde_b7` for HYDE) and dropped from the payload when `detail` is off. `detail=false` saves bytes, not compute.
- A lean row holds the mean (`representative_raw`), `n_units` and `coverage`. The spread (p10, p90) is in `detail` only (inside the distribution for LMR and GEDA; separate fields for HYDE). A series of mean, spread and count needs a new light output.
- Source selection exists: `permitted` is a set of source ids. Variables within a source are computed together (LMR's three, HYDE's four); filtering them saves little except histogram work.
- Per-cell values: LMR and GEDA already build a cells x years matrix and weights in memory; HYDE returns one row per cell per step. Emitting them is straightforward for a single basin and large for a polity.
- Public API: `/api/signature` accepts a span only for `scope=basin` (older path: LMR nearest cell, HYDE centroid rule). For `buffer` and `area` it requires `from_year == to_year`. `/api/areas` takes ranges but is internal. A public series needs a new route or a relaxed rule, and building it on the older basin path would give different numbers from the tab. Whether to expose it is Karl's decision.

## Item 2: the polity jump

**It is HYDE and the number of HYDE steps, not the length of the span.** WO-05's spans all began at 1000 CE, so the 1,000-year span was the first to cross 1950, where HYDE's steps become annual.

Per-source time for Northern Song (resolver year 1000; 37,901 HYDE cells; seconds, medians):

| Span | HYDE steps | HYDE | LMR | GEDA | eVolv2k |
| --- | --- | --- | --- | --- | --- |
| 1000-1099 | 1 | 0.81 | 0.03 | 0.11 | 0.00 |
| 1000-1399 | 4 | 3.01 | 0.10 | 0.30 | 0.00 |
| 1000-1799 | 17 | 12.80 | 0.18 | 0.51 | 0.00 |
| 1000-1949 | 32 | 23.86 | 0.20 | 0.70 | 0.00 |
| 1000-1999 | 82 | 63.23 | 0.21 | 0.71 | 0.00 |
| 1-800 | 8 | 6.02 | 0.17 | 0.00 | 0.00 |
| 1200-1999 | 80 | 61.68 | 0.18 | 0.62 | 0.00 |

Same length (800 years), different cost: 1-800 CE 6.0 s; 1000-1799 12.8 s; 1100-1899 19.6 s; 1200-1999 61.7 s. HYDE's steps are centennial to 1700, decadal from 1710 to 1950 and annual from 1951 (128 in all). Rows HYDE pulls into Python equal cells x steps (644,317 rows for 17 steps; 3,032,080 for 80).

**Query plan** (`EXPLAIN ANALYZE`, 1200-1999): finding the cells takes about 30 ms (the spatial index works; 37,901 cells at every span). The nested loop that joins each cell to each of the 80 steps takes 32 s for 3,032,080 pairs; the rows are then sorted on disk (148 MB). The overlap calculation (`ST_Intersection`, `ST_Area`) is evaluated after the join, once per cell and step pair, not once per cell.

**Test of that reading:** the same query with `cell_overlaps AS MATERIALIZED`: 33.0 s down to 1.1 s in the database (plan only; it sends no rows). End to end, with the rows moved into pandas, the same fix gives:

| Northern Song, HYDE only | As sent | With the fix |
| --- | --- | --- |
| 1000-1099 | 0.80 s | 0.56 s |
| 1000-1799 | 12.76 s | 6.07 s |
| 1200-1999 | 61.12 s | 29.61 s |
| 1000-1999 | 63.64 s | 30.85 s |

The numbers agree with the engine's current output in every case (row count, variables, years, means). About 26 s of the remaining 30 s is moving 3 million rows into pandas; Python grouping and histograms add about 3 s.

**Is it fixable?** Yes. Cheap: the one-word `MATERIALIZED` change (40 to 50% less). Real: fetch one row per cell with each variable's array sliced to the span's steps (about 38,000 rows, not 3 million), as `_band_t_lmr` and `_band_t_geda` do, and average with numpy. Not built or measured, and it is an engine change outside this WO. Expectation (not a measurement): several times faster again.

**Does cost scale with polity size?** Yes, close to linearly in cells (resolver year 1000; span 1000-1999, 82 steps):

| Polity | Area | HYDE cells | As sent | With the fix |
| --- | --- | --- | --- | --- |
| Kingdom of Croatia | 90,000 km2 | 1,596 | 2.05 s | 1.24 s |
| Seljuk Dynasty | 292,000 km2 | 4,825 | 6.11 s | 3.80 s |
| Northern Song | 2,765,000 km2 | 37,901 | 63.64 s | 30.85 s |

As sent: about 15 microseconds per cell-and-step pair for Croatia and the Seljuks and about 20 for Song (the disk sort); with the fix about 10 across all three. Rows agree in every case.

## Item 1: cost of a lean request

Partly answered.

- **Polity:** HYDE is 95% of Band T time (table above). LMR and GEDA together take under 1 s at 1,000 years; eVolv2k nothing. Python time (grouping, histograms, row building) is about 3.3 s of the 30 s (fixed) at 82 steps.
- **Single basin (Lviv, 25 km buffer as proxy; seconds, medians):** HYDE 0.01 (100 years), 0.03 (800), 0.13 (1000-1999); LMR 0.01 to 0.07; GEDA 0.00 to 0.03; eVolv2k 0.00. The four sources together take about 0.25 s at 1,000 years. WO-05's whole API call for Lviv took 1.24 s at 10 years and 3.06 s at 1,000, so **about 1 s is fixed overhead and a further 1 to 1.5 s grows with span and lies outside the Band T functions**. Probably payload assembly and serialization of about 4,400 rows with histograms; not traced.
- **Payload:** about 850 bytes per row, about 3.5 KB per year raw, about 0.45 KB gzip. The design note's assumption that histograms are most of the weight is plausible for bytes (not measured separately).
- **Not measured:** the effect of `detail=false` on time (it shrinks the payload; the histograms are still computed); an engine-level lean request (none exists).

## Item 4: span threshold by scope (proposal)

Conservative first, dynamic:

- **Mechanism.** The Signature tab's year inputs count the HYDE steps inside the span (the 128 step years in `temporal.hyde_times` are a small, known table) and the years for LMR and GEDA, and warn (not block) above the scope's limit. The cost depends on which years are asked for, as much as on how many.
- **Polity:** about 9 HYDE steps or fewer, as built (about 5 s for a large polity such as Northern Song; allows about 1000-1700). Seljuk-sized polities would allow about 68 steps; Croatia-sized needs none. A size-aware gate (budget divided by cell count) is possible later; the conservative one is set by the largest polity.
- **Single basin:** no delivery limit in the measurements (3 s at 1,000 years); the limit comes from display (the HYDE table is 82 columns, 3,242 px at 56, wider than the pane).
- **Ring and buffer:** not measured. A large buffer pulls tens of thousands of HYDE cells and may behave like a polity.
- **Would change if** the HYDE query is reshaped (the polity limit could loosen a lot) or HYDE is drawn as lines (the display limit mostly disappears and delivery becomes the binding one).

## Risks and what would differ on the server

- **Local timings.** One user, local database, warm cache after the first run. The server has its own PostgreSQL tuning (work_mem, shared_buffers, parallel workers, disk), which changes the disk-sort and transfer parts of the cost. nginx caches `/api/` for 6 hours, so repeat requests are fast and a cache miss is the number that matters. A cold first run was not measured.
- **One resolver year.** All polity numbers use the polity's extent at year 1000; the engine treats the resolver year and the Band T span as independent.
- **Estimates in the proposal** (the 5 s budget, the 9-step and 68-step figures) are arithmetic on 15 microseconds per pair, not measured gates.

## Needs attention going forward

1. **Decide whether to reshape the HYDE query** (one row per cell with array slices): it decides whether polities can be in the Time series tool and how loose the polity gate can be. Engine change, outside WO-06.
2. **The 1 to 1.5 s outside the Band T functions** for a single basin (serialization?) and the effect of `detail=false` on time: not traced. Matters for the request shape of a Time series tool.
3. **Ring and buffer** costs by radius and level.
4. **HYDE display redesign** (lines, not a column per step), then look at it; then revisit the gate.
5. **A second resolver year** for a polity (its extent changes; a time series uses one boundary year).
6. **Public API:** a range on the engine path is not exposed; Karl decides whether and how.
7. **Server timings** (cold and warm) before setting final limits.
8. **Scripts:** the four `dash_wo06_*.py` scratch scripts are untracked.
