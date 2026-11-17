# dash WO-07: conservative span gate, and a look at the edge

Draft of 17 Nov 2026, for Karl's review. A small build plus a look, on the `dashboard` branch. Follows `dash_wo06_results.md`.

## Goal

Warn when a Band T span is likely to be slow or unreadable on the Signature tab, then run spans just inside the gate and see how the page handles them, HYDE above all. The results set up the next step: redesigning HYDE's display.

## Background

- Two limits govern a span: **delivery** (how long the payload takes) and **legibility** (what the page can show readably). The gate uses the lower of the two, by scope.
- WO-06: cost depends on which years are asked for, not just how many. HYDE's steps are centennial to 1700, decadal to 1950 and annual from 1951 (128 in all, in `temporal.hyde_times`). Polity cost is HYDE cells times HYDE steps.
- Delivery: a single basin has no practical limit (about 3 s at 1,000 years). A large polity reaches about 5 s at about 9 HYDE steps as built.
- Legibility: HYDE's table has one column per step and overflows the pane well before delivery becomes a problem for a single basin (56 columns were 3,242 px in an 827 px pane).
- Warning UI settled in the time series design note: inline under the year inputs, not a tooltip; appears on leaving a field or pressing Enter; re-checks when scope or level changes; warns, does not block.

## Items

1. **Gate.** On the Settlements and Polities sides, count the HYDE steps inside the entered span (from the step years) and the span's length in years. Limits, conservative:
   - Polity: about 9 HYDE steps (delivery).
   - Single basin and ring: a HYDE step count that fits the pane readably (legibility). Propose the number from the current column width.
   - Buffer: as polity until measured.
   Keep the limits in one place, easy to change.

2. **Warning.** When the span exceeds the limit, a short inline message under the year inputs naming the reason (slow, or too wide to read) and suggesting a shorter span. Placeholder wording, marked for Karl. No link to a Time series tab yet.

3. **A look at the edge.** Run spans just inside each limit and just over it: Lviv and Santa Fe (single basin), Lviv (ring), Kingdom of Croatia and Northern Song (polity). Include spans that cross 1950. For each, record the time to a filled Signature tab and take a screenshot of Band T, HYDE's table in particular. Note anything else that reads badly (LMR and GEDA sliders, the sources line).

## Provisos

- No changes to the engine, the API or the payload. The `MATERIALIZED` fix and the HYDE query reshape stay out of this work order.
- HYDE's display is not changed here; it is looked at.
- The Sandbox is unchanged.

## Out of scope

The HYDE display redesign (next); the Time series tab; server timings.

## Deliverables and gate

- `dash_wo07_summary.md`, one page; `dash_wo07_results.md`, with the limits chosen, the timings and the screenshots (or paths to them).
- Tests: the warning appears above the limit and not below, for each scope, and re-checks on a scope or level change.

Gate: Karl looks at the screenshots and the page, and decides what the HYDE redesign must handle.
