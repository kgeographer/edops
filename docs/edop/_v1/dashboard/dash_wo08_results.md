# dash WO-08 results: HYDE as line graphs, a server time limit, lighter slice steps

2026-11-18. Spec `dash_wo08_HYDE-line-graphs.md`; summary `dash_wo08_summary.md`. Branch `dashboard`. Commits: `b159515` (item 1), `a15f770` (item 3), `d28dacb` (item 2), `cf36043` (item 4). Nothing deployed. Row values the engine returns are unchanged; the only change to a payload is on request (`members_only`, `skip_hyde_distribution`, both off by default).

## Item 1: HYDE as line graphs

- Three options were drawn from the real Lviv 1900-2000 rows (56 steps) and screenshotted: A one chart, B small charts side by side, C three charts stacked at full width. Page and picture: `output/edop/dashboard/wo08/hyde_line_options.html` and `.png` (gitignored). Karl chose **A**. In A a variable far below the others (Lviv's pasture, against cropland) is a flatter line, but nothing hides behind anything else once grazing is dropped; with grazing, pasture drew over it because the two are nearly equal.
- **Grazing is not drawn.** Karl's reading: grazing conceptually covers pasture and rangeland, and where they do not add up it is incidental. In Lviv grazing is 2 to 33 km² above pasture plus rangeland; across the polity epochs WO-02 checked it is equal in 68 of 75 and larger in 7 (by up to 56,911 km²); it is never smaller. I did not check HYDE's own documentation for the definition, so "grazing is the total of pasture and rangeland" is Karl's and my recollection, not a verified source statement. The payload, the API, the map's variable dropdown and the catalog still carry grazing.
- Built: `renderHydeChart` in `dashboard.html` (a polyline and a dot per step on a true year axis; dots 3.4 px where steps are at least 6 px apart and 2 px where annual steps crowd; a hover title gives year and km²). Colours were changed once: blue and green were too close on a high-resolution screen, so pasture is purple (`#7b3294`). A span with no HYDE step (or one step) keeps the text table with the "~ nearest available HYDE epoch" note.
- The single-basin and ring 12-step warning is removed (`edops_span_gate.js` keeps only the buffer limit, 9 steps, which is about delivery time and still untested beyond the arithmetic).
- Tests: `tests/dashboard/test_hyde_lines_ui.py` (a short span, a span crossing 1950, a 56-step span as one narrow chart, a span with no step) and the span-gate tests changed to the new rule.

## Item 2: server time limit

- **Proposed and built: 20 s** for the HYDE query and the reduction, `EDOPS_BAND_T_TIME_LIMIT_S` (default 20), read when the engine is first imported (a `.env` line is loaded before that). The page's 5 s ceiling is unchanged. 20 s leaves room for the estimate being off by about three times (Argentina took three times Northern Song's time on the old query) and lets China 2000-2023 (10 s) finish through the API.
- How: a database `statement_timeout` on the HYDE query, a clock check between fetched chunks and before each step's reduction (the Python work after the fetch can also run long), one `BandTTimeLimit` error. Routes: `/api/areas` and the public `scope=buffer` and `scope=area` return 504 with the detail "Band T stopped at the server's time limit (20 s). Untick T, or choose a smaller area or a shorter span." The Dashboard's error panes show it in yellow (placeholder wording, for Karl's wording).
- Tests (`test_band_t_time_limit.py`, 5): the engine stops HYDE, `/api/areas` and the public buffer answer 504, a query inside the limit is unaffected, and the page shows the message. The test server runs in the test process, so the tests lower the limit and force a real timeout. Karl also forced it in his own browser: 0.05 s did not trigger on Kaifeng 800-1200 (a single basin's HYDE is quicker than 50 ms; the request returned 200 in 1.4 s); 0.001 s did.
- The public `scope=buffer` and `scope=area` take one year, so the limit guards them only for a very large single-year area. The public `scope=basin` path runs HYDE on the older code (`app/db/hyde.py`) and has no limit.

## Item 3: lighter slice steps

- A slice step used to send `/api/areas?scope=polity&detail=true` with the bands as ticked, only for the member ids. Now it sends `members_only=true`: the route does the polity lookup and reads the ids from `temporal.polity_basin08_crosswalk`, with no signature.
- Timing (local): 33 ms for both Northern Song and China; the leanest signature request (band A, no detail) was 1.8 to 1.9 s for Northern Song and 3.3 s for China, and the full request 2.5 s and 15 s. Most of the old floor was not Band T: it was the signature itself (basin resolution and aggregation). Member ids are identical to the full request's (2,847 and 3,426).
- The halted-slice rule (Get signature disabled when the estimate is over 5 s) is unchanged; the background request no longer needs to leave Band T out, because it carries no bands.
- Tests (`test_slice_step_ui.py`, 3): same ids without a signature, the signature unchanged without the option, and a slice step sends `members_only` with no bands or detail.

## Item 4: HYDE histograms

- **Does anything use them? No.** The HYDE display reads `representative_raw` (the totals) only; the only reads of `detail.distribution` on the page are for LMR and GEDA; the baseline payloads hold HYDE's bins and weights but nothing asserts on them except as fields.
- **Share of time** (HYDE function alone, histograms patched out): Northern Song 1000-1999 7.0 s with, 4.6 s without (34%); China 2000-2023 10.1 s with, 7.8 s without (23%). Each run twice. I had expected most of the time; it is a quarter to a third.
- **Karl's rules:** HYDE's histograms are never drawn; the public API's `detail` payload does not change. So the engine and `/api/areas` gained one off-by-default option, `hyde_distribution` / `skip_hyde_distribution`, that the Dashboard sends on every signature request (single basin, buffer, polity, ring members). The 16 baseline payloads and every other caller are unchanged; dropping HYDE's histograms altogether is not proposed.
- Tests (`test_hyde_distribution_skip.py`, 6): by default HYDE rows keep bins and weights; skipping drops only the histogram (other numbers equal within 1e-9: cell order moves the last digit between calls); LMR's histograms stay; the Dashboard sends the option.

## Needs attention

1. **The biggest slices are still over 5 s**: Canada-sized (135,000 cells, 74 steps) was about 26 s estimated, about 19 s with item 4; only the 20 s limit stops them, and a real large slice has not been run to the limit.
2. The page's estimate was fitted with the histograms included, so after item 4 it runs about a quarter high (conservative); not recalibrated.
3. The polity page times in the WO-07 edge table are still from the old query; stepping, loading and a Canada run are untimed on the new code.
4. Placeholder wording to settle: the time-limit message and the buffer warning.
5. Whether bands and timespan changes should disable the result tabs (UX review, open since WO-05).
6. Grazing's definition in HYDE 3.5 is unchecked; it matters for the crosswalk meaning summaries.
