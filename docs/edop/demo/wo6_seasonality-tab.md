# WO6 — Seasonality tab: chart display

**Branch:** `demo_wo6` off `demo`
**Track:** 3 (Sandbox UI)
**Depends on:** WO5 closed — `pre_mm_monthly`, `tmp_dc_monthly`, and six derived scalars
are in the top-level `out` payload.

---

## Goal

Add a **Seasonality** tab to the Explorer sandbox, populated automatically when a signature
is retrieved. The tab renders the monthly precip and temp arrays for the containing basin
as one or more charts, and displays the six derived scalar indices in a readable form.

No interaction (buttons, queries) in this WO — display only. Interaction layers are WO7.

---

## Step 1 — Tab scaffold

Add "Seasonality" as a fourth tab alongside Map / Signature / Analysis. Tab becomes active
and populated on signature load; shows a placeholder state ("click a location to load
seasonality") before first retrieval. No changes to existing tabs.

---

## Step 2 — Chart(s)

The payload provides `pre_mm_monthly` (float[12], mm) and `tmp_dc_monthly` (float[12], °C).
CC should propose and implement one or more chart forms from the following candidates —
the goal is to find what's visually informative, not to produce a finished design:

**Candidate A — Dual-axis bar+line (Walter-Lieth style)**
Precip as bars (left axis, mm), temp as line (right axis, °C), months Jan–Dec on x-axis.
The standard climatological display; immediately readable to any physical geographer.
Phase relationship is visible as the offset between bar peak and line peak.

**Candidate B — Polar/radial plot**
Months arranged around a circle (Jan at top or right, clockwise). Precip as one ring,
temp as another, or overlaid. Makes concentration and phase offset *geometric* — a
concentrated monsoon profile looks like a spike; a maritime profile looks like a nearly
uniform ring; anti-phase is visible as opposite-side peaks. Less conventional but
potentially more revealing for the index values.

**Candidate C — Both**
Small multiples or toggled views — Walter-Lieth for readability, polar for analytical
geometry. Not required; only if CC finds it low-cost to offer both.

CC should implement whichever form(s) seem most informative and note what was tried.
The chart need not be styled beyond legibility at this stage.

---

## Step 3 — Scalar index display

Below or alongside the chart, display the six derived scalars in a simple readable form.
Suggested layout: a small table or label set with friendly names and values rounded to
2 decimal places. Include the [0–6] range gloss for `seas_phase_offset` and [0–1] for
concentration fields so the values are self-interpreting without a legend.

No percentile positions or provenance badges at this stage — those belong to the Band C
accordion, not here.

---

## Step 4 — Location label

The tab should display the basin ID and level (e.g. "L08 basin 4120842") so it's clear
whose profile is being shown. Consistent with how other tabs identify the active location.

---

## Provisos

- CC should note any library constraints in the existing sandbox stack that bear on chart
  form — if a polar plot requires a library not already present, that's worth flagging
  before implementing.
- The monthly arrays are on top-level `out`, not inside `profile_groups` (WO5 locked
  decision). CC should fetch from there.
- No similarity queries, no regional heterogeneity, no additional buttons — those are WO7.

---

## Acceptance

- Clicking any map location loads the Seasonality tab with a chart and scalar readout.
- Chart correctly reflects the known profile shapes: London near-flat bars, Delhi spike
  July–August, Rome moderate winter bias.
- Tab shows placeholder state before first click.
- All existing tests pass.

