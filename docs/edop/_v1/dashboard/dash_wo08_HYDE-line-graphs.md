# dash WO-08: HYDE as line graphs, a server time limit, lighter slice steps

Draft of 17 Nov 2026, for Karl's review. A build, on the `dashboard` branch. Follows `dash_wo07_results.md`.

## Goal

HYDE on the Signature tab reads at any span. No query runs unbounded. Stepping through a polity's slices is quick.

## Background

- HYDE's table has one column per step and overflows the pane past about 13 steps. The settlements warning (12 steps) is a stopgap for that width.
- After the WO-07 reshape, the largest polity slices are still over 5 s (Canada-sized, about 26 s estimated). The page's estimate cannot promise the 5 s ceiling, because cost also depends on the polygon's outline.
- Every manual slice step sends a full `/api/areas` request, Band T included, only to repaint the map from the member basin ids.
- The engine builds a histogram per HYDE step and variable (`_agg_hyde_b7`). It is unclear whether anything uses HYDE's histograms, and for the largest slices they are a large share of the remaining cost.

## Items

1. **HYDE as line graphs.** Replace the table with line graphs for cropland, grazing, pasture and rangeland, in km², whole numbers. Values exist only at HYDE's step years: mark the points and join them, so it is clear where the data is. Propose one chart or four small ones (rangeland is often far smaller than the others) and show both in screenshots before settling. When a span has no step, show the nearest step's values as text, as now. Then remove the 12-step legibility warning for single basin and ring; the buffer limit stays.

2. **Server time limit.** A time limit on Band T queries in the database, so no request runs unbounded, the public API included. When it is hit, the page says so plainly (placeholder wording, marked for Karl) and suggests unticking T or choosing a smaller area; the API returns a clear error. Propose the limit; the 5 s ceiling remains the page's own gate.

3. **Lighter slice steps.** A slice step (Next, Prev, First, slider, choosing a polity) asks only for what the map needs (the member basin ids), not a full signature.

4. **HYDE histograms.** First answer: does the page, the API documentation or anything else use HYDE's histograms, and what share of a large slice's time do they take? Then:
   - if nothing on the page uses them, compute them only when `detail` is requested;
   - report whether they could be dropped for HYDE altogether; Karl decides that.

## Provisos

- Keep it short. One check of each limit, not a sweep. List anything worth looking into in one line under "Needs attention" and stop there.
- LMR, GEDA and eVolv2k displays are unchanged. The Sandbox is unchanged.
- Rows the engine returns must be identical, apart from histograms omitted under item 4.

## Out of scope

The Time series tab; size-aware gates for buffers; server timings.

## Deliverables and gate

- `dash_wo08_summary.md`, one page; `dash_wo08_results.md`, with screenshots of the HYDE options.
- Tests: HYDE lines at a short span, a span crossing 1950, and a no-step span; the time limit's message; a slice step without Band T.

Gate: Karl checks in a browser. Lviv 1900–2000: HYDE readable as lines. Northern Song: stepping through slices is quick. A query forced past the time limit shows the message.
