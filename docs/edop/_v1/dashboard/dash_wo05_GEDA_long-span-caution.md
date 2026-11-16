# dash WO-05: GEDA in Band T, sources statement, long-span caution

Draft of 16 Nov 2026, for Karl's review. A build, on the `dashboard` branch. Follows `dash_wo04_results.md`.

## Goal

GEDA appears on the Dashboard's Signature tab wherever the payload carries it, with a statement heading Band T that says which sources apply to this place and span and which do not. Long spans get a caution at the year inputs. Two carry-overs from WO-04 settle how results behave when controls change.

## Background

- GEDA has been served since the regionality phase: `geda_scpdsi` rows on the engine path (`/api/areas`, which the Dashboard uses) and on the public basin route. The Sandbox page ignores the rows; its Band T badge counts them.
- Display decisions already made (`pre-design_notes_cc.md`, "Decisions already made that bear on display"):
  - GEDA is shown like LMR: the same panel type (histogram of cell values with a year slider, a small line with its p10–p90 band), in its own block, never on a shared axis with LMR. Each block is fully labelled: product, season, grain, units.
  - Values are standard scores (how unusual a summer was for that place, relative to 1000–2020), not Palmer drought categories; wording must say so.
  - Observed years (1990–2020) are shaded differently from the p10–p90 band, with a legend or tooltip naming both.
  - Notes appear for `low_coverage` and `low_resolution`; no new chart types.
  - Where GEDA and LMR both appear, the UI says they are independent reconstructions, not a conflict to resolve.
  - HYDE's display and LMR's handling are not touched.
- The `sources` block lists each Band T source as `used` (with a coverage note when low) or `not_applied` with a reason: `outside_span`, `outside_footprint`, `below_coverage_floor`.
- Regression anchor: Kyiv basin, 1350: mean -0.408, p10 -0.567, p90 -0.261, 27 cells.
- Payload size grows with span: about three rows per year for LMR; 1,049 KB for 401 years in the earlier measurements (`_xfer/dashboard/wo02_results.md`), before GEDA.

## Items

1. **GEDA block.** Draw the `geda_scpdsi` rows on the Signature tab's Band T as decided above, using the existing `geda_caveat` and `geda_observed` texts. Settlements and polities alike. Label and caveat wording is placeholder, marked for Karl.

2. **Sources statement.** A short block heading Band T: fixed sentences with slots, read from the `sources` block. One sentence per Band T source (HYDE, LMR, eVolv2k, GEDA): used, used with low coverage, or not applied with its reason, for this place and span. List every state the block can take and show each in a test. Wording is placeholder, marked for Karl.

3. **Long-span caution.** Measure payload size and response time against span length, for a single basin and a polity, with GEDA included. Propose a span length for a caution from those measurements, and show the caution at the year inputs when a span exceeds it. Karl sets the number; the caution warns and does not block.

4. **Out-of-date results (from WO-04).** When the controls differ from the last run, keep the results visible, dim them, and show one line above the tabs naming what they are for (for example, "These results are for Level 06, single basin. Press Get signature to update."). The line goes when the controls match again. Scope and radius changes no longer clear results; Context and Similarity wait for the button like the other result tabs. The Map tab still previews the controls.

5. **Polity example dropdown (from WO-04).** It stays usable after a polity search, as the settlement one now does.

## Provisos

- Display only: no changes to the engine, the public API or the payload. If a display needs something the payload lacks, report it and do not change it.
- The Sandbox, HYDE's display and LMR's handling are unchanged.
- The Band T headline value stays as it is (weighted mean for LMR and GEDA); that decision is still open.
- Thresholds come from measurement, not from inspecting the example places.

## Risks to watch

- Two blocks with year sliders on one tab: whether they move together or apart.
- Out-of-date state across tabs that render lazily (Context, Similarity).
- Polity spans that cross GEDA's 1000 CE start, so GEDA applies to part of the span only.

## Out of scope

The Band T headline value; switching sources off; GEDA in the Sandbox or the profile; the Using EDOPS page.

## Deliverables and gate

- `dash_wo05_summary.md`, one page; `dash_wo05_results.md`, with the measurements for item 3 and anything that needs attention.
- Tests for each `sources` state, the Kyiv anchor shown in the block, and the out-of-date marking.

Gate: Karl checks in a browser. Lviv, Band T 1300–1400: the GEDA block beside LMR, the statement saying GEDA applies. Santa Fe, same span: the statement saying GEDA does not apply, outside its footprint. A long span shows the caution. Changing the level dims the results with the line, and changing it back clears it.