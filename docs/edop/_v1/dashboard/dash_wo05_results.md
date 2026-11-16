# dash WO-05 results: GEDA in Band T, sources line, long-span measurements

2026-11-16. Spec `dash_wo05_GEDA_long-span-caution.md` (Fable). Branch `dashboard`. Commits: item 5 `0d7c221`, item 1 `0ad2aed`, a Get signature change outside the WO's list `875ee10`, item 2 `a979f5f`; item 3 measurements and this record in the commit after. Nothing is deployed or on `main`. **Item 4 (out-of-date results) was not started. Item 3 is measurement only: the caution was not built, by Karl's decision (see below).**

## Item 5: polity example dropdown

Choosing a polity from the search no longer disables "Load an example" (one line removed). Test: search Northern Song, the dropdown is enabled, choosing Inca Empire goes there.

## Item 1: GEDA block

`renderGedaBlock` in `dashboard.html`, drawn after the LMR block when the payload has `geda_scpdsi` rows, settlements and polities alike. Its own histogram with its own year slider, the mean line with the p10 to p90 band, never on an axis shared with LMR. Labels: product, season, grain, units, and standard score not Palmer categories (placeholder wording, highlighted). Observed years (1990 to 2020) are an amber strip on the line chart and "· observed" in the histogram's year text; a legend line names the strip and the band. The texts `geda_caveat` and `geda_observed` come from the payload's `caveats`. Notes for low coverage, a coarse histogram (few cells), a span the atlas covers only in part ("GEDA covers 1000–1100 of the 900–1100 requested", derived from the rows because the `sources` block does not say), and, where LMR is shown too, that the two are independent reconstructions.

Added at Karl's request while checking: the slider's year is the text under each Band T histogram (it showed the query span), and a vertical marker on the line chart follows the slider, for LMR and GEDA alike (they share the code). The "observed" text beside the slider was dropped as redundant.

Tests (`tests/dashboard/test_geda_block.py`, 9): Lviv shows GEDA beside LMR with the labels and caveat; independent sliders; observed shading, tag and legend; the clipped-span note; no shading when the span has no observed years; Santa Fe has no block and keeps LMR; the Kyiv anchor (1350: mean -0.408, 27 cells) reaches the page; slider-year stamp and marker. Not tested: the low-coverage and coarse-histogram notes inside the GEDA block (the sources line covers low coverage).

## Item 2: sources line

`renderSourcesLine`, read from the response's `sources` block, at the top of the Band T accordion (Karl's wording idea): "Available for this query: HYDE land use, LMR climate, eVolv2k volcanic events, GEDA drought." then a sentence for each exception: low coverage ("GEDA drought: covers 49.8% of the area"), HYDE with no step in the span (the nearest is shown), and not applied with a reason (outside its footprint; its years do not overlap this span; its cells cover too little of this area). Wording is placeholder. **The states a source can reach differ:** HYDE is never "not applied" (it falls back to the nearest step); LMR and eVolv2k can be outside their years; GEDA has all of used, low coverage and three not-applied reasons. Each state is tested with a real place (`tests/dashboard/test_sources_line.py`, 7): Lviv 1300–1400 (all four), Santa Fe (outside footprint), Lviv 2021–2025 (outside span), Lviv 1301–1302 (HYDE nearest step), the edge basin at 28.82, 20.02 (low coverage, 49.8%), basin 1060264990's interior point (below the floor), and Inca Empire (a polity; GEDA outside footprint). LMR's and eVolv2k's out-of-span states go through the same code as GEDA's and are not separate tests. Northern Song's default Band T span gives GEDA "years do not overlap" (the polity's default span ends before 1000).

## Get signature shows the Signature tab (outside the WO's list, commit `875ee10`)

Karl observed that a pressed Get signature should take the reader to the Signature tab (automatic runs still stay on the Map, as in WO-04). The two button listeners now start the run, then select the tab early. A race turned up and is fixed: a map preview started by a level, scope or radius change used to switch to the Map when it finished, pulling the reader back if they had already pressed the button; a press counter stops that. One WO-04 test that asserted "stays on the map" after a level change now asserts the Signature tab; four tests added (from the Map, from another tab, a failed press, a polity after a slice step).

## Item 3: span measurements (no caution built)

Karl's decision: **no action on these now.** The question is bigger than a warning: how to compute and render large time series needs a time-series UX design (Opus, Karl, then CC). The numbers are kept here. Local server, `/api/areas` as the Dashboard asks (detail=true, Band T only), spans starting at 1000 CE, median of 3 (`scripts/edop/dashboard/dash_wo05_span_timing.py`; CSV in `output/edop/dashboard/wo05_span_timing.csv`, gitignored).

| Span (years) | Lviv rows | Raw KB | Gzip KB | Seconds | Polity seconds (Northern Song) |
| --- | --- | --- | --- | --- | --- |
| 10 | 45 | 40 | 7 | 1.2 | 2.8 |
| 25 | 107 | 91 | 14 | 1.3 | 2.8 |
| 50 | 209 | 178 | 25 | 1.2 | 2.8 |
| 100 | 413 | 349 | 47 | 1.3 | 2.8 |
| 200 | 826 | 697 | 91 | 1.3 | 3.7 |
| 400 | 1,652 | 1,394 | 178 | 1.4 | 5.5 |
| 800 | 3,351 | 2,822 | 358 | 1.8 | 15.7 |
| 1,000 | 4,426 | 3,759 | 481 | 3.1 | 66 |

Santa Fe (no GEDA) is 15 to 30% smaller and takes 1.2 to 2.2 s. A polity's raw payload is about 4 MB at 1,000 years.

- **Size** grows in a straight line, about 3.5 KB per year raw, 0.45 KB gzipped. **Time** for a single basin is flat to 400 years and 3 s at 1,000.
- **Polities** are the binding case: 2.8 s at 100 years, 5.5 s at 400, 15.7 s at 800, 66 s at 1,000, steeper than a straight line. GEDA is part of it: Northern Song 1–800 CE (GEDA not applicable) took 8.4 s, 1000–1799 CE (GEDA for 800 years) 15.6 s. The cause of the 800-to-1,000 jump is not investigated (a notebook may be called for).
- **Browser** (`dash_wo05_span_render.py`, Lviv): 2.7 s to draw at 100 years, 2.4 s at 400, 3.9 s at 1,000; 1,209 page elements at 1,000 years; no render problem.
- **HYDE's table** is a separate display problem: HYDE steps are annual from 1950, so the table has one column per year there: 56 columns (3,242 px in an 827 px pane) for 1900–2000, 82 columns at 1,000 years. The width depends on how much of the span is after 1950, so a limit on span length would not catch it.
- A caution threshold was proposed at 400 years (a polity passes 5 s and starts climbing); not built.

## Item 4: out-of-date results: not started

Spec: keep results visible and dim them when the controls differ from the last run, with a line naming what they are for; scope and radius changes no longer clear results; Context and Similarity wait for the button. Karl expects a methodical state chase (settlement to ring, ring-member clicks, polity slices; one handler for a control change and one for the control-window click), time-consuming, and will decide when to start it. Read first: WO-04 results ("Needs attention" 1 and 2), `_settlementDirty`, `_resetRightColumn`, `_drawScopePreview`.

## Tests

`tests/dashboard/test_geda_block.py` 9, `test_sources_line.py` 7, `test_get_signature_ui.py` 11, `test_handoff_ui.py` 28 with `test_permalink_ui.py` 21 (49 together); the whole dashboard folder at the end of the day: **97 passed** (about 4.5 minutes). The full suite was not run (it is for the merge gate).

## Needs attention going forward

1. **A time-series design** (Karl, Opus, then CC): computing and rendering large or long series; a size gate (large and small); marking a clipped span (done for GEDA only); possibly capping spans; people will want to see change over centuries. This implies a new feature: a "Time series" in the Signature panel (choose a variable and a span, get a line graph), possibly public-API only, and possibly a reorganised request panel. Needs a conversation with Opus.
2. **Polity cost with span** (above): the 66 s at 1,000 years and its cause; also the cost of a polity's Signature re-run per slice with a long span.
3. **HYDE's table** is one column per step: wide with annual steps after 1950.
4. **Observed versus reconstructed:** two shadings and a legend are in; users will not know the difference and deserve to; wording is placeholder and to be written in a UI pass.
5. **The `sources` block does not say a span was clipped;** the page derives it from the rows' first and last year (GEDA only).
6. **Item 4** (above).
7. **Wording** of the GEDA block and the sources line is placeholder (yellow); the "SD (z-score)" units text repeats itself in the GEDA description.
8. **The Band T headline value** (weighted mean for LMR and GEDA) is still an open decision.
9. **Carried from WO-03 and WO-04:** the profile store; Context and Similarity follow the level control at once (item 4 would change it); prose still saying v0.4; the profile text describes the sample point.
10. **Polity default Band T span** can end before GEDA starts, so a polity opened by default may show GEDA as not applied for years.
