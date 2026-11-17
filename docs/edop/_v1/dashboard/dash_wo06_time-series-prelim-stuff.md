# dash WO-06: time series, preliminary questions

Draft of 17 Nov 2026, for Karl's review. Measurement and code reading only; nothing in the app changes.

## Goal

Answer the three questions in section 9 of the time series design note, so that a build work order can be written. The answers decide what a time series request looks like and whether polities can have one at all.

## Background

- The time series design note (in the repo) describes a Time series tab: chosen variables over a span, a mean line per variable with the spread across cells, settlements and single basins first, polities deferred.
- WO-05 measured Band T as the Dashboard asks for it (`/api/areas`, detail=true, Band T only): a single basin is fast to 1,000 years; Northern Song climbs from 2.8 s (100 years) to 15.7 s (800) and 66 s (1,000). Script: `scripts/edop/dashboard/dash_wo05_span_timing.py`.
- Band T is computed per source (HYDE, LMR, eVolv2k, GEDA), each through the source registry.
- The intended default time series payload is per year: the mean, the spread across cells and the cell count, without histograms; per-cell values on request.

## Items

1. **Cost of a lean request.** Measure Band T over spans of 100 to 1,000 years with no histograms and, as far as can be done without changing the app, only the chosen variables, for a single basin (Lviv, Santa Fe) and a polity (Northern Song, plus one polity of a different size). Report time and payload size beside WO-05's figures, and say how much of the weight was the histograms.

2. **The polity jump.** Find why Northern Song's cost rises 4× between 800 and 1,000 years when the span grows 1.25×. Time each source separately; look at the query plans at both spans; note memory use. A notebook is fine. Say whether the cause is fixable and what the fix would involve. Do not fix it.

3. **Chosen variables on the engine path.** From the code: can the Band T functions already return a subset of variables, and the lean form (mean, spread, cell count) without histograms? If not, what would it take? Also say how per-cell values on request would be served, and whether the public API could expose the same call.

4. **Span threshold.** From items 1 and 2, propose the Signature tab's span threshold by scope (single basin, ring, buffer, polity), or say that a scope needs none.

## Provisos

- No changes to the app, the engine, the API or the database. Scratch scripts and notebooks only, named as such.
- Thresholds come from the measurements, not from the example places.
- Karl and CC choose the branch.

## Risks to watch

- Timings on the local machine may not match the server; say what would differ.
- A polity's cost may depend on its size as much as on the span; the second polity is there to show which.

## Out of scope

Building the Time series tab; the warning UI (already settled in the design note); the `sources` clipped-span flag; polities' changing boundaries.

## Deliverables and gate

- `dash_wo06_summary.md`, one page; `dash_wo06_results.md`, with the tables, the polity diagnosis and anything that needs attention.
- The scripts or notebook.

Gate: Karl reads the summary and decides the shape of the time series request and whether polities stay deferred for v1.
