# WO5 — Context tab; temperature lens diagnostic; hide Similarity

**Status:** draft for review.
**Branch:** `cdop_pilot` structure; sandbox v3 surface.
**Prior:** `wo4_findings.md`, `wo3_findings.md`.

Goal-setting with provisos. CC discovers implementation particulars; Karl reviews every write.

---

## Why

The Similarity tab currently paints coastal Norway (maritime, 8–12 °C annual range) as similar to
the Tbilisi basin while its own blurb states the criteria as *5.3 °C mean, 21.7 °C range,
continental*. The panel contradicts itself on screen. Two properties are named; the results share
one.

Two problems sit behind that, and they are separable:

- **The cut point.** `climate.temp`'s strict/moderate/loose radii were set empirically in WO7 and
  have never been calibrated. The ladder is 0.25 / 0.75 / 1.50 — a 1× / 3× / 6× radius ratio,
  which in three dimensions is a volume ratio near 1 / 27 / 216. Those are not three settings of
  one control.
- **The container.** The Tbilisi L06 basin reports 5.3 °C against a city at ~13.8 °C. WO4 Part 0
  measured this corpus-wide: even at L08, 13.4–14.6% of D-PLACE and WH Cities sites show a >2 °C
  implied gap. Tightening the threshold would produce a tidier map that still answers the wrong
  question — and would stop signalling the defect.

WO4 also established that the sturdiest similarity products are the ones that **rank nothing**.
Typological position and local anomaly need no threshold, no candidate pool, no calibration, and
no assumption that the container suits the site. They ran clean on first pass and produced real
findings — Timbuktu's inland delta caught twice by independent methods, Tbilisi's regional cold
anomaly triangulating the container problem from a third direction.

This WO ships those, hides the instrument that isn't ready, and runs the one diagnostic that
determines what happens to it.

**Part A and Parts B–E are independent.** The Context tab uses no lens distance and no threshold,
so its design does not depend on the diagnostic's outcome. They are in one WO because they concern
one surface; either can proceed without the other. The single narrow dependency is noted in Part B.

---

## Part A — Temperature lens diagnostic (first, standalone)

One query against an index already in memory.

For the 852 basins inside `climate.temp` moderate for Tbilisi, bin by distance rank into quartiles
and report the distribution of `tmp_seas_amp` (and `tmp_dc_syr`) in each. Repeat for Kaifeng, whose
map reads as coherent, as a control.

Two outcomes, both actionable:

- Amplitude tracks rank cleanly — Q1 at roughly 18–25 °C, Q4 at 8–14 °C. The ranking is sound and
  `moderate` is simply too wide. A threshold problem.
- Low-amplitude basins scattered through Q1 and Q2. The metric is admitting them, and
  `tmp_concentration` is the suspect — it is the only one of the three variables that is not
  self-evidently interpretable and it has never been examined.

Provisos:

- **Write the expectation down before running.** Standing hazard: three times in this project a
  cut point or interpretation has been set by checking whether the result matched a prior.
- Norway's presence needs explaining even if it ranks last. A 13 °C amplitude gap ought to exceed
  any radius called *moderate*; if it doesn't, that is a fact about the metric, not the label.
- Report `tmp_concentration` values for the query and for a sample of the admitted maritime basins.
  If that variable turns out to be doing the admitting, it affects Part B (below) as well.
- Diagnostic only. No threshold changes, no metric changes, no recalibration in this WO.

---

## Part B — Context data path

A basin's position against a stated population. Two comparisons per variable: **all basins**, and
**basins within a chosen radius**.

Endpoint returning, for a given basin and radius: per-variable value, global percentile,
within-radius percentile, and the count of basins in the radius.

Provisos:

- Global percentiles are static per level and can be precomputed. Within-radius percentiles are
  request-time — a spatial query plus a percentile. Confirm the cost; if slow, consider precomputed
  percentiles at the fixed radius set rather than an arbitrary radius.
- **Variable set is a design decision, not a dump.** Six to eight rows that a historian can read
  without a glossary. Candidates: mean annual precipitation, mean annual temperature, seasonal
  temperature range, mean elevation, relief or roughness, aridity, runoff or discharge. Recommend
  a set; do not include derived statistics that need explaining.
- **The one dependency on Part A:** if `tmp_concentration` is implicated there, it does not appear
  as a Context row either. Nothing else in Context depends on Part A's outcome.
- Level: Context should honour the Level dropdown properly. Note that this control is currently
  inert on the Similarity tab — a control that silently does nothing. Do not reproduce that.
  Report neighbourhood counts at both L06 and L08 before deciding whether both are offered; L08 is
  11.6× the basins and the radius populations grow accordingly.
- The reference population for "all basins" is all land basins at the level, which includes
  Greenland and the Sahara. That is defensible but should be stated in the UI, not assumed.

---

## Part C — Context tab UI

New tab, label **`Context`**, beside Seasonality on sandbox v3.

**Table** — two comparison columns, no ranking, no candidate list:

| | vs. all basins | vs. within 500 km |
|---|---|---|
| Mean annual precipitation | 64th | 92nd |
| Mean annual temperature | 30th | **3rd** |
| Seasonal temperature range | 59th | 71st |
| Mean elevation | 93rd | 88th |

**One control:** comparison radius — `250 / 500 / 1000 / 2500 km`, segmented. Show the count
alongside: *344 basins within 500 km*.

**Map.** Numbers changing under a slider need visual accompaniment, and this comparison has a
spatial dimension, so it gets one.

The map renders the comparison population itself: all basins within the selected radius,
choroplethed on the selected variable, with the query basin outlined. Tbilisi's *colder than 97%
within 500 km* becomes visible directly — the query sits at the dark end of a field that is mostly
warmer. Moving the radius grows or shrinks the painted region, and the query's position within the
distribution visibly shifts.

Provisos:

- Selecting a table row sets the map variable. That is the interaction; no separate variable
  selector.
- Colour ramp is the variable's own distribution *within the shown population*, not a global ramp —
  otherwise the local comparison is invisible, which is the entire point.
- Confirm basin counts at 2500 km before committing to that radius. WebGL is comfortable to ~5,000;
  if 2500 km at L08 exceeds it, cap the radius set rather than degrading the render.
- Do not reuse the strict/moderate/loose widget semantics or vocabulary. The radius control names a
  population; those named a calibrated distance that was never calibrated.

**Labelling discipline.** Avoid `Local` and `Anomaly` in the interface. Say `within 500 km`. Both
`strict/moderate/loose` and `seasonal phase` failed by promising an interpretation the computation
did not deliver; the label should name the population, not characterise the result.

---

## Part D — Blurb

Rule-based, no API call, same pattern as the Seasonality narrative:

> This basin is colder than 97% of basins within 500 km, though close to the global median.
> Elevation is in the top 10% worldwide. Precipitation is unremarkable globally but high for its
> region.

Provisos:

- Report only where the two comparisons disagree materially, or where a global percentile is
  extreme. A sentence per row would be unreadable and would bury the finding.
- Rule-based wherever the data supports it. The Seasonality blurb established this; it also
  established that a confidently wrong sentence in prose is worse than a wrong number, so the rules
  should assert only what the percentiles directly support.

---

## Part E — Hide Similarity

Hide the Similarity tab on sandbox v3. Hide, not delete: route, index, and code remain, and
`cdop_pilot`'s WH Cities lens dropdown is unaffected — that surface uses topN over a 254-city
corpus and no threshold, so it is not implicated.

Record in the tracker what would unhide it: the Part A outcome resolved, the threshold question
settled, and the container argument declared. Not a date.

---

## Deferred to a second increment

**Radius sweep.** Percentile plotted against comparison radius — a small chart answering *at what
scale does this place stop being typical?* Tbilisi would read near-median at 100 km and collapse
toward the 3rd percentile by 500 km. This is the one output here not available anywhere else, and
it generalises the ESDA local-heterogeneity finding to the point query. Held back only so the first
increment ships boring and correct.

---

## Accept gate

**The Context tab renders for the WO4 probe set, and Tbilisi shows near-median global temperature
against bottom-few-percent within 500 km — with the map making that visible without reading the
numbers.**

Supporting: Timbuktu shows the documented precipitation inversion (17th globally, ~47th locally);
radius control updates table, map, and blurb together; counts reported; Similarity hidden; tests
green.

Part A reports its result whichever way it falls, and its expectation is recorded before the run.

---

## Out of scope

- Threshold recalibration or the quantile proposal
- Any change to `climate.temp` variables or metric
- Deciding whether similarity moves to L08
- Restoring or redesigning the Similarity tab
- Matched sets (Phase 4 notebook instrument; dedup unresolved)
- The radius sweep chart
- 