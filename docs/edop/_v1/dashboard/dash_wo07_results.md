# dash WO-07 results: conservative span gate, and a look at the edge

2026-11-17. Spec `dash_wo07_conservative-span-gate.md`; summary `dash_wo07_summary.md`. Branch `dashboard`. Commit `5369ca6` (gate, tests, spec, edge script); this record is uncommitted. Nothing deployed. No change to the engine, API, payload or the Sandbox. Following Karl's steer in the session, the Settlements side was built first; **the Polities side was not built**, for the reason under Item 3.

## Items 1 and 2: the gate and its warning (Settlements side)

- `app/static/js/edops_span_gate.js`: the step table by rule (millennial -10000 to -1000, centennial 0 to 1700, decadal 1710 to 1950, annual 1951 to 2025: 128), `stepsIn`, `check(scope, from, to)` and one `LIMITS` object. A test compares the table with `temporal.hyde_times`.
- **Limits (conservative):** single basin 12 and ring 12 steps (legibility: the HYDE table is about 58 px a column and the pane about 907 px); buffer 9 (delivery, as a polity until measured). HYDE only; no year limit (Karl, 17 Nov). Karl's reading after looking: 13 steps is right at the display limit.
- **Warning:** inline under the Band T year inputs (`#v3-t-span-warn`), yellow placeholder wording ("This span has 13 HYDE steps; the HYDE table gets too wide to read past 12. Try a shorter span."), shown on leaving a year field or pressing Enter, re-checked when scope or level changes and when Band T is ticked. It does not block: Get signature stays available, and automatic runs (links, examples) proceed, so the edge can be poked at.
- **Tests** (`tests/dashboard/test_span_gate_ui.py`, 8): the table equals the database's; the single-basin limit (12 no warning, 13 warning); ring; buffer (9 and 10); a scope change re-checks the same span; the warning does not block the button; no warning without Band T or with a reversed span; the cost follows the years asked for (400 years from 1000 has 5 steps and does not warn; 400 years from 1700 does). Dashboard folder: **112 passed** (5 min 3 s).

## Item 3: a look at the edge

Script `scripts/edop/dashboard/dash_wo07_edge_look.py` (Playwright, local server, bands ABCDET, viewport 1400 x 1000): opens each case by link, times the load until Band T is drawn, records the HYDE table's columns and width against the pane, and screenshots the Band T accordion. Data `output/edop/dashboard/wo07_edge/wo07_edge_look.csv` and `wo07_edge_look_polity.csv`; screenshots `output/edop/dashboard/wo07_edge/*.png` (gitignored).

### Settlements (valid: spans set in the link)

| Case | Span | HYDE steps | Seconds to Band T | HYDE table (pane 907 px) | Warned |
| --- | --- | --- | --- | --- | --- |
| Lviv single | 0-1100 | 12 | 13.8 (first load of the run, cold) | 12 columns, 891 px | no |
| Lviv single | 0-1200 | 13 | 2.6 | 13 columns, 891 px | yes |
| Lviv single | 1940-1960 (crosses 1950) | 12 | 2.1 | 12 columns, 891 px | no |
| Lviv single | 1900-2000 | 56 | 3.0 | 56 columns, **3,242 px** | yes |
| Santa Fe single | 0-1100 / 0-1200 / 1900-2000 | 12 / 13 / 56 | 2.2 / 2.2 / 2.6 | 891 / 891 / **3,245** px | no / yes / yes |
| Lviv ring | 0-1100 / 0-1200 / 1900-2000 | 12 / 13 / 56 | 2.2 / 2.5 / 2.9 | 891 / 891 / **3,242** px | no / yes / yes |

- **Delivery is not the limit for a single basin or a ring:** 2 to 3 s at 12 and at 56 steps. **Legibility is:** the table compresses (values wrap, "km2" drops to a second line) to about 13 columns and then overflows. The screenshot for Lviv 0-1200 shows 13 columns fitting.
- Everything else on the tab read acceptably at the limit: the LMR and GEDA histograms, sliders and line charts (200 to 1,200 years drawn without trouble), the sources line, the eVolv2k list ("22 >= 5 Tg S, show all 132"). Spans that cross 1950 are as slow or fast as any other for a single basin.

### Polities: the span is not typed, so I opened real slices

The Polities side's Band T year inputs (`#v3-polity-from-year`, `-to-year`) sit in a row that is never revealed (the Sandbox is the same); `applySlice` writes the slice's own dates into them. So a user cannot enter a polity span, and a link's `from_year` and `to_year` are ignored for polities (my first polity cases loaded 990-1017 instead of the spans I asked for, and were discarded). A polity's span is its slice's span.

Cliopatria slices (15,690): median length 6 years, p90 37, p99 163, maximum 967. **330 (2.1%) have more than 9 HYDE steps; 280 more than 12.** The 8 example polities have 0 or 1 step in every slice. The exposed ones are modern states (annual HYDE steps, large areas); by steps times area: Canada 1949-2023 (74 steps, 9.9 million km2), Commonwealth of Australia, USSR 1953-1968, Brazil, China 2000-2023, Argentina 1936-2023.

| Slice | HYDE steps | Area | Seconds to a filled Signature tab (bands ABCDET) | HYDE table |
| --- | --- | --- | --- | --- |
| Northern Song 990-1017 | 1 | 2.76 million km2 | 15.0 (4.8 s in an earlier load; varies) | 891 px |
| China 2000-2023 | 24 | 9.4 million km2 | 104.1 | 1,963 px |
| Brazil 1987-2023 | 37 | 8.5 million km2 | 205.5 | 2,931 px |
| Argentina 1936-2023 | 75 | 2.8 million km2 | 192.7 | 5,690 px |
| USSR 1953-1968 | 16 | 22.0 million km2 | **over 300 (the page run timed out; not completed)** | not drawn |
| Canada 1949-2023 | 74 | 9.9 million km2 | **not run** (about 10 million rows into pandas; risked the running server's memory) | |

- **It is Band T.** China's slice by API: bands A-E 3.3 s; band T alone 101 s. HYDE is the whole cost; the other bands are small. At about 31 microseconds per cell-and-step pair for China (against about 20 for Northern Song) the cost per pair rises with the polity's size.
- **Display:** the HYDE table overflows the pane at 24 columns (1,963 px) and is 5,690 px at 75.
- Timing noise: the same Northern Song slice took 4.8 s and 15 s in two loads, and the first load of a session is cold (13.8 s above). Treat the seconds as order of magnitude.

### What this says about the polity gate

The Settlements gate (a warning when a typed span has too many steps) has no polity counterpart, because nothing is typed. A polity gate would act when a **slice is chosen** (a search result, a slice step, a link), on **steps and area together**: Northern Song-sized polities cost about 5 s at 9 steps, but a 22 million km2 slice is slow at 16 and a 2.8 million km2 slice took 193 s at 75. A flat "9 steps" would flag the 330 slices but miss that the biggest slices are slow with few steps. The HYDE query reshape (WO-06) is now more pressing: anyone who picks a modern state today waits minutes.

## The polity gate and the HYDE query (after the edge look)

Decisions (Karl, 17 Nov): a ceiling of 5 s on any query; halt on the slice, before any request; disable Get signature with the reason; unticking T re-enables it (the other bands take about 3 s); the settlements warning is a stopgap until HYDE is drawn as line graphs (the step limit is about table width; the real turn-down rule is time); fix the query first, keep the stopgap.

- **Why every slice step is expensive today.** `applySlice` calls `_silentResig` on Next, Prev, First, the slider and picking a polity, which sends `/api/areas?scope=polity&detail=true` (bands as ticked, Band T included) only to get the member basin ids for the choropleth. Play ticks skip it and resync once when playback stops. Stepping onto China 2000-2023 started a 100 s request before any button was pressed. A halted slice's request now leaves Band T out.
- **Counting the exposure.** Estimated as built (cells = area / 73 km2, 25 microseconds a pair): of 15,690 slices (1,618 polities), 300 over 5 s (95 polities), 115 over 10 s (53), 29 over 30 s (17), 8 over 60 s (7), 3 over 120 s. All 8 example polities are under 3 s at their worst slice. The estimate ran low for the largest areas (China 77 s estimated, 101 s measured).
- **The estimate is not enough on its own.** China 1950-1952 (3 steps, 8.4 million km2) took 16.4 s against an 11 s estimate; Argentina 1936-2023 took 193 s against Northern Song's 63 s at the same cells and steps. On the old query the cost followed the polygon's outline, not only its area.
- **The reshape** (`9340d31`): `_band_t_hyde` now fetches one row per cell, with each variable's array sliced to the span's steps and the overlap computed once (MATERIALIZED), and reduces per step in numpy with `_agg_hyde_b7` unchanged. Compared with the old function on nine cases (polities, a buffer, the nearest-step fallback with and without a tie, China 1950-1952): all rows identical except one `p90` (Seljuk 1200-1999, 54.46661 against 54.46677, 3 parts per million); shuffling the cell order alone moves `p90` by up to 2.3 parts per million, so that is existing order sensitivity of the weighted percentile. Engine and regionality tests (the 16 baseline payloads): 217 passed.

| HYDE query, seconds | Old | New |
| --- | --- | --- |
| Northern Song 1000-1099 | 0.82 | 0.59 |
| Northern Song 1000-1399 | 3.21 | 0.81 |
| Northern Song 1000-1799 | 13.17 | 1.91 |
| Northern Song 1000-1999 | 63.6 | 7.03 |
| Croatia 1000-1999 | 2.07 | 0.34 |
| Seljuk 1200-1999 | 6.25 | 0.77 |
| China 1950-1952 | 13.52 | 4.66 |
| China 2000-2023 | about 100 | 10.22 |

- **The gate, recalibrated to the new query.** Fitted from those times: cost per HYDE step about 2.1 microseconds a cell (the same for Northern Song and China); cost per cell 13 (Northern Song) to 34 microseconds (China, a complex outline), 35 used. The estimate is within about 1.3 times for the large polities; for a tiny polity it is a fraction of a second under (fixed overhead). Estimates: China 2000-2023 11 s (halted), China 1950-1952 4.8 s (allowed; measured 4.7 s), Canada 1949-2023 about 26 s, Argentina 1936-2023 about 7.4 s.
- **Still over 5 s:** the biggest slices (Canada-sized: 135,000 cells x 74 steps). The remaining cost is Python (a histogram per step and variable) and moving the arrays. Untested: that the estimate holds for other complex outlines; a server time limit would be the only guarantee.
- **Built and tested:** `EdopsSpanGate.estimateSeconds` and `areaCheck`, `_polityHalt` and the halt note under the polity Get signature button (`#v3-polity-halt`, placeholder wording), the halted slice's background request without Band T, and `tests/dashboard/test_polity_gate_ui.py` (6).

## Provisos kept

The spec's provisos (no engine, API or payload change) held while WO-07 ran; the HYDE query reshape was then done at Karl's request, outside the spec, as `9340d31`. The Sandbox page is unchanged (it receives the faster HYDE rows through the engine). HYDE's display is looked at, not changed.

## Needs attention going forward

1. **Whether the polity Band T year inputs should ever be user-enterable** (the Time series tool would cover arbitrary spans). The polity gate itself is built (above).
2. **The biggest slices are still over 5 s** after the reshape (Canada-sized: about 26 s estimated). Options: trim the Python side (histograms only when detail is wanted), and a server time limit as the guarantee. The Sandbox's polity page uses the same query and benefits.
3. **HYDE's display redesign** (lines, not a column per step): the table overflows from about 14 columns; at 24, 37 and 75 steps it is 2 to 6 times the pane.
4. **A polity link ignores `from_year` and `to_year`;** the Copy link for a polity does not carry a span either (WO-03 codec header says it does).
5. **The warning wording** is placeholder (yellow); the buffer limit (9) is untested beyond the arithmetic.
6. **Timings are local and noisy** (cold first load; two loads of one slice differed by 3x); server timings remain to be taken.
7. **The polity page times in the edge-look table were taken on the old query** and not re-measured after the reshape (only the HYDE function was timed on the new one: 7 to 10 s for the large slices). **The USSR page run timed out at 5 minutes** on the old query and no completed time exists for it; Canada was not run on either query.
8. **Not built here:** a link to a Time series tab. The estimate and the area-based gate are not yet used for buffers (the settlements buffer limit is still 9 steps).
