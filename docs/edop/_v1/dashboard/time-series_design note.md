# Time series: a design note

Draft of 17 Nov 2026, from Karl's thoughts, Opus's and CC's review. A preliminary plan, ahead of any work orders. Not decisions until Karl marks them so; section 10 lists what he has decided.

## 1. Why

- People will ask EDOPS how something changed at a place over centuries: "how did drought and cropland change over 300 years?" Ruth has raised it; the worked examples will need it.
- Band T on the Signature tab can't serve long spans well. WO-05 measured it: about 3.5 KB a year; a single basin stays fast (3 s at 1,000 years), but a polity reaches 66 s at 1,000; HYDE's table runs one column per year after 1950.
- The Signature tab answers "everything about a place for a span" (breadth). A time series answers "a few variables over a long span" (depth). Different jobs, so different tools.

## 2. What it is

A **Time series** tab on the Dashboard. Choose variables and a span for the current place; see them as aligned charts; download what is shown. Optionally add a second place for comparison. That is where it stops.

## 3. Variables

Only time-varying variables, which are Band T's. Spans and resolutions are to be read from the source registry before this note is final (the LMR span in the database is 1–2001 CE).

| Source | Variables | Span | Resolution |
| --- | --- | --- | --- |
| LMR v2.1 | PDSI, temperature anomaly, precipitation anomaly | per registry | annual |
| GEDA | summer scPDSI (standard score) | 1000–2020 CE, Eurasia | annual; observed from 1990 |
| HYDE 3.5 | cropland, grazing, pasture, rangeland | -10000–2025 | steps: millennial, centennial, decadal, then annual from 1950 |
| eVolv2k v4 | volcanic events | per registry | events |

The tab says in a line why other variables (aridity, for example) are absent: they describe the present, from BasinATLAS.

## 4. Layout

[ Time series ]
Place: Tbilisi (Level 06 basin) [+ Add the place in the left panel]
Variables: [x] PDSI (LMR) [x] Summer drought (GEDA) [x] Cropland (HYDE) [ ] ...
Span: [ 1500 ] – [ 1800 ] Smoothing: [ none | 10 yr | 30 yr ]
Coverage: LMR ██████████ GEDA ██████████ HYDE ▪ ▪ ▪ ▪ (from the sources block)
PDSI (LMR) ~~~~/~~~/~~~~~/~~~~ (mean; spread across cells when enough cells)
Summer drought (GEDA) ~~~/~~~~/~~~~~/~~~~
Cropland (HYDE) ____/‾‾‾‾‾‾/‾‾‾‾‾‾‾‾‾ (steps)
Volcanic events | | | | (markers, carried across panels)
                  1500        1650        1800

[ Download CSV ] [ Download JSON ] [ Copy link ]



- The picker and the tab's own span input sit above the charts. The tab does not use the left column's Band T years, which belong to the Signature tab; its span may start from them.
- One panel per variable, its own y-axis, all on one time axis. LMR and GEDA are never on a shared axis.
- **The series line is the mean across cells**, with every cell's value available (section 6). **The band is the spread across cells in space, not uncertainty over time**, and is labelled "spread across cells". It shows only above a minimum cell count, set from the data, not from example places. For a single basin, LMR often has one or two cells and no band; GEDA's band is real for large basins.
- Comparison: the same variable for two places shares a panel (same units), two lines, labelled. The second place is added through the left panel's existing lookup ("add this place to the chart"), not a second picker.
- The coverage strip reads the `sources` block, so `sources` must report a clipped span first.
- The left column's explanatory paragraph changes with the tab, as it does now.

## 5. Behaviour

- **Availability:** the tab works as soon as a place exists, with its own fetch; it does not depend on a signature run. A change of place, scope or level clears its charts (no stale view), in line with the Dashboard's reset rule. A permalink naming the tab runs its own fetch on arrival.
- **Smoothing:** fixed 10- and 30-year running means, display only. Not offered for HYDE (step data). For GEDA, no window spans the 1990 boundary between reconstructed and observed years. The rule at the ends of a series is stated on the page (for example, shortened windows, marked).
- Settlements and single basins first.
- Show and download only: no rule-written statement about patterns (the standing decision on time-varying values). Plain descriptive figures (driest decade, largest HYDE change) are possible later.
- A permalink carries place(s), variables, span and smoothing.

## 6. What it asks of the back end

- A request for chosen variables over a span. By default it returns per year the mean, the spread across cells and the cell count, without histograms, so it stays small and fast (to measure). **Per-cell values are available on request**, in the API and as a download option with a size warning, so that every value can travel with the payload.
- The engine path (`/api/areas`), not the public basin route, so the tab matches the Signature tab (the public route still mixes methods for LMR, HYDE and GEDA; unifying them is a roadmap item).
- The same call exposed in the public API, for scripted users and possibly WHG.
- The `sources` block reporting a clipped span (WO-05 found it doesn't).
- **Downloads:** a long CSV, one row per place, variable and year, with units, cell count, coverage flags and a flag marking HYDE steps; source citations and licences from the registry in a header or companion file. JSON carries the same.

## 7. Changes elsewhere that go with it

- **Signature tab, span threshold** by scope: barely needed for a single basin, needed for polities (about 400 years by WO-05's numbers). The warning sits inline under the year inputs (not a tooltip, which fails on touch). It appears on leaving the field or pressing Enter, as the radius field does, and re-checks when scope or level changes. It offers a shorter span and a link to the Time series tab. Warn, don't block.
- **Signature tab, HYDE** drawn as lines (one chart or small multiples) when it has more than a few steps; whole km², no decimals.
- **Atlas** leaves the Dashboard's tab bar, probably for a tab on the Data Explorer, which is also not place-specific. That makes room for Time series.

## 8. Deferred

- **Polities and buffers.** Beyond cost, a polity series uses one boundary year (the engine treats the Band T span and the resolver year as independent), which misleads when the polity's extent changed over the span. Polities need a design for changing boundaries before they come in.
- More than two places; rule-written prose about patterns; statistics beyond display smoothing; non-Band T sources such as LBDA, until they are ingested.

## 9. Before any work order

1. CC: the cost of a variables-only, no-histogram Band T request over 1,000 years, single basin and polity. Linked to item 2.
2. CC: why a polity's cost jumps between 800 and 1,000 years (4× for 1.25× the span); may need a notebook. Items 1 and 2 decide whether polities are viable at all.
3. CC: whether the engine path can already return chosen variables (Band T functions are one per source, so a filter looks plausible). Code reading.
4. Answered (CC, 17 Nov): the warning's placement and timing, as in section 7. The span threshold by scope is to be confirmed against items 1 and 2.

## 10. Decided (Karl, 17 Nov)

- Comparison: two places, added through the left panel's lookup.
- Smoothing: fixed 10 and 30 years for now.
- Picker and span above the charts.
- The mean across cells is the series line, as long as all values travel with the payload; subject to review. The February meeting may bring environmental scientists, and a thorough review of EDOPS is expected (Ruth may lead it).
- Atlas leaves the Dashboard's tab bar.

## 11. Still open

1. The minimum cell count for showing the spread band (from the data).
2. The rule at the ends of a smoothed series.
3. Tab bar layout with Time series added (UX review).

