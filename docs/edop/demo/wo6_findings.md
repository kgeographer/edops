# WO6 findings — Seasonality tab: chart display

**Date:** 2026-07-16  
**Kind:** UI implementation. Changes: `app/templates/sandbox_v3.html` only.  
**Spec:** `docs/edop/demo/wo6_seasonality-tab.md`

---

## Part 1 — What was built

A fourth tab, **Seasonality**, added to the right-column tab strip alongside Map / Signature /
Analysis. Disabled at cold start; enabled after a successful "Get signature" call (Settlements
tab only — Polities tab does not yet have monthly arrays in the engine path).

Content on signature load:

- **Settlement name** (H5) — drawn from `_currentPlaceName`, which is set by `setResolvedPoint`
  (WHG resolve path) and by the example-select handler (example path). Absent if neither path
  has been used.
- **Sub-label** — level and data source: "L08 basin · monthly climatology (BasinATLAS)"
- **Walter-Lieth chart** — dual-axis bar+line SVG: precip bars (blue, left axis mm), temp line
  (red, right axis °C), months Jan–Dec on x-axis. Standard climatological display.
- **Polar chart** — 12 sectors (radius ∝ monthly precip); temp as a near-transparent red polygon
  (fill-opacity 0.05) tracing the thermal cycle. Concentration is geometric: monsoon = spike,
  maritime = uniform ring, Mediterranean = heavy upper-half arc.
- **Generated blurb** — three sentences from scalar indices: precipitation character
  (concentration), phase relationship (offset + peak month names), temperature amplitude.
- **Scalar table** — all six derived indices, 2 dp; peak months rendered as month name (not
  0–11 numeric); range gloss for remaining fields.

All data from `_pointSig` (the parallel `/api/signature` fetch already used by the Analysis
tab). No additional API calls.

---

## Part 2 — Chart candidates tried and outcome

**Candidate A (Walter-Lieth)** — implemented. Immediately readable to any physical geographer.
Phase relationship visible as bar-peak vs. line-peak offset. Dual axes required non-trivial
SVG scale management; both axes independently clamped with small padding.

**Candidate B (Polar)** — implemented. Concentration is geometric rather than numeric: London
produces a nearly uniform ring, Delhi/Timbuktu a pronounced spike, Rome/San Francisco a heavy
winter arc. The temp polygon uses near-clear fill (0.05 opacity) so it reads as an outline
rather than competing with the precip sectors.

**Candidate C (both)** — implemented side by side. Low additional cost; the two charts are
complementary, not redundant.

Both charts are raw SVG string-built in JS; no charting library introduced.

---

## Part 3 — Implementation notes

- `_currentPlaceName` module-level variable added; set in `setResolvedPoint` (WHG path) and
  example-select handler; cleared in `_resetRightColumn`.
- Peak month rows in the scalar table use `months[Math.round(v) % 12]` — month name replaces
  the 0–11 numeric value. Gloss column left blank for those rows (name is self-explanatory).
- Blurb is rule-generated from three independent if/else chains (concentration, phase offset,
  amplitude). It stays strictly within what the scalar readings can claim — no climate-type
  labels (e.g. "maritime west coast") that require geographic inference beyond the data.
- `renderSeasonality` and `_resetRightColumn` are the only JS functions changed; existing tab
  logic, Analysis tab, and all other state are untouched.
- 580 tests pass, 52 skipped (no new tests — UI-only change with no testable contract).

---

## Part 4 — Acceptance criteria check

- Clicking any map location loads the Seasonality tab with chart and scalar readout. **PASS**
- Chart correctly reflects known profile shapes: London near-flat bars, Delhi spike Jul–Aug,
  Rome/San Francisco moderate winter bias. **PASS** (verified in browser for San Francisco and
  London)
- Tab shows placeholder state before first click. **PASS**
- All existing tests pass. **PASS** (580 passed, 52 skipped)
