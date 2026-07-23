# WO6a — Non-compensatory similarity: notebook

**Status:** draft for review.
**Type:** exploratory notebook. No engine writes, no registry changes, no API, no UI.
**Prior:** `wo5_findings.md` (Part A Check 3; the modality detour), `wo4_findings.md`.
**Follows to:** WO6b, whose shape this notebook determines. Report back before 6b is drafted.

Goal-setting with provisos. CC discovers implementation particulars; Karl reviews every write.

---

## Why

WO5 Part A Check 3 found that `climate.temp` bundles absolute level (`tmp_dc_syr`) with shape
(`tmp_seas_amp`, `tmp_concentration`) in one composite distance, so favourable shape agreement
buys tolerance on level: ±3 °C at strict, ±10 °C at moderate. A lens labelled *Temperature
regime* admits basins nearly 10 °C off. This is the same failure shape WO3 found in
`climate.phase` — one label bundling questions that don't share an answer — recurring.

The proposal under test is **non-compensatory matching**: a basin qualifies only if it is close
on *every* condition, with no trading off between them. Its metric form is Chebyshev distance —
score is the worst dimension, not the sum — which preserves ranking while making compensation
impossible by construction.

Merits, to be confirmed or refuted here rather than assumed:

- **No calibration anywhere.** Percentiles are uniform by construction and absolute bands are
  stated in physical units. The strict/moderate/loose problem — uncalibrated for temp,
  geometrically incoherent at 1×/3×/6×, non-transferable between L06 and L08 — does not arise.
- **Every result explains itself.** *Within 8 percentile points on mean temperature, 5 on seasonal
  range, same number of wet seasons* is simultaneously the result and its caveat. Given that no
  one reads caveats, an output that is its own justification is worth a great deal.
- **Nearly free to build.** The percentile index shipped in WO5 and cross-validated against WO4
  Part 5 to within 1.6 points.

**This is a question, not a plan.** A result showing non-compensatory matching returns unusable
sets, or no better sets than the existing lenses, is a legitimate outcome and should be reported
plainly.

---

## Instrument under test

Three continuous conditions plus one class gate:

- mean annual temperature
- seasonal temperature range
- annual precipitation total
- **modality as a gate** — a basin qualifies only if its wet-season count matches the query's

Modality is a discrete class, not a graded quantity, so it cannot be a weighted axis without
either being diluted against the continuous terms or degenerating into a near-constant percentile
axis. Gating sidesteps both.

The gate runs on **peak count**, not `R_dbl`. WO5's detour found `R_dbl` wrong in both directions
across the probe set — a false positive on Timbuktu (Fourier artifact of a sharp single peak) and
a false negative on George Town (verified against the Seasonality chart) — while prominence-based
peak counting was correct on all four probes tested.

---

## Part A — Prominence threshold: a defensible default

Peak counting requires a prominence threshold, expressed as a fraction of each basin's own annual
range. WO5's detour swept 10/20/30/40% on four probes; Mombasa flips from two peaks to one between
10% and 20%.

Counting modes in a distribution is genuinely ill-posed without a scale parameter — Silverman's
mode-testing work formalised this; the mode count is monotonic in the smoothing bandwidth, so
choosing the bandwidth is choosing the answer. There is no view from nowhere. The task is
therefore not to find the true threshold but to pick a defensible one and state it.

**Sweep prominence across all L06 basins** (and L08 if cheap) and look for stability: is the
bimodal count flat across some band and then moving sharply outside it? A plateau is
`THRESH_ARID`-grade evidence — a real feature of the data, robust to small changes in the line.
No plateau anywhere is also a finding, and would mean the number has to be justified some other
way before it goes into prose.

Provisos:

- Report the geography of the bimodal class at the recommended threshold and at the sweep
  endpoints. The equatorial double-ITCZ belt, monsoon Asia, the Sahel margin should appear; if
  they don't, the measure is wrong regardless of what the count curve looks like.
- Compare against `R_dbl`'s class assignments. Where they disagree, draw the monthly profile.
  **Draw the compared dimension before theorising about the measure** — this rule has now paid off
  three times (WO2a's validation, George Town's mischaracterisation, the peak-count detour).
- The threshold will be **declared, not exposed as a control**. A control implies the choice is
  the user's when it is Karl's. The blurb states it: *two rainy seasons (second peak at least N%
  of the annual range)*. Deferred register entry for exposing it as a control; trigger is a user
  actually disputing the default.

---

## Part B — Absolute bands or percentile bands (the decision this notebook exists to make)

The two options fail in mirror-image ways:

- **Absolute bands** hold physical meaning constant and let the result count swing. Basins are
  densely packed at 20–30 °C (~7,000 in two bins) and sparse below −10 °C (718), so ±2 °C returns
  a crowd in the tropics and almost nothing in the arctic.
- **Percentile bands** hold the count roughly constant and let physical meaning swing. Five
  percentile points is a fraction of a degree in the tropics and several degrees at the cold end.

**The diagnostic is one table.** Run both rules on probes spanning dense and sparse regions, and
report per probe: the result count, *and* the physical width of what came back (the actual °C and
mm spread of the qualifying set).

Then the choice is between *unpredictable N with stable meaning* and *stable N with unstable
meaning* — a judgment Karl can make by looking, rather than by argument.

Proviso, and the thing most likely to dissolve the question: the marginal widths look alarming,
but **the conjunction determines N**. Four simultaneous conditions cut a crowd down fast. The
tropical over-return under absolute bands may not survive the other three conditions, in which
case absolute wins on both criteria and there is nothing to trade off.

Probes: the WO4 set (Mombasa, Augsburg, Tbilisi, Kaifeng, Timbuktu, George Town, Santiago), plus
at least one high-latitude basin to exercise the sparse end.

---

## Part C — Variable budget, measured

For *k* independent conditions at tolerance *t* percentile points, the expected population share
is roughly `(2t/100)^k` before correlation. Three at ±10 → ~0.8%: about 130 basins at L06, ~1,500
at L08.

Measure it rather than deriving it — the variables are correlated (WO5 Check 2 found
corr(`tmp_dc_syr`, `tmp_seas_amp`) = −0.84), so the real counts will differ, probably upward.

Report result-set size as a function of *k* and *t*, at both levels. The output is a table
answering: **how many conditions can this instrument carry before it returns nothing?**

Provisos:

- Empty results are honest scarcity, not a failure mode (WO4 Part 2). But the point at which
  *most* queries return empty is a structural limit worth knowing before the instrument ships.
- This is a small-*k* instrument by construction. It will never grow into "similarity across many
  dimensions." Confirm that in numbers so it isn't discovered later.
- Note the L06/L08 asymmetry: the finer support makes this instrument *more* comfortable, not
  less — the opposite of the pattern everywhere else in this project.

---

## Part D — Precipitation lens compensation check (cheap, independent)

`climate.precip` is `(log_pre_mm_syr, a1, b1, a2, b2)` — level plus shape in one composite
distance, the same construction Check 3 found in `climate.temp`. It has only ever been validated
at top-N, where the radius is too tight for compensation to surface.

Run the Check 3 diagnostic on it: at strict, moderate, and loose, what is the admitted range of
`pre_mm_syr` itself? If a basin at a third or triple the query's annual rainfall qualifies at
moderate because its harmonic shape agrees, the precipitation lens has the same defect.

Relevant to WO4's George Town result, where the *opposite* failure appeared — two ~17,500 km
phantom matches from comparing shape with no magnitude at all. That was fixed by adding magnitude
into the same distance, which is precisely what opens the compensation channel.

Diagnostic only. No changes to the lens in this WO.

---

## Accept gate

**Parts A–D run and report, with a recommended prominence threshold and its stability evidence, a
recommendation on absolute versus percentile bands supported by the count-and-width table, a
measured variable budget, and the precipitation lens compensation result.**

Not a correctness gate. Any of these may come back negative.

Report to Karl before WO6b is drafted — Part B's answer determines what 6b builds.

---

## Out of scope

- Any engine, registry, API, or UI change
- Building the instrument
- Changing `pre_modality`'s production computation
- Threshold recalibration for existing lenses
- Removing or altering the existing Similarity tab

---

## Noted for WO6b, not decided here

**The instrument fits the existing structure as a third dispatch case.** The registry already does
per-lens metric dispatch — Euclidean for near-independent variables, Mahalanobis for correlated
ones. A non-compensatory rule is a third case, added as a sub-lens and evaluated side by side with
the existing ones on the same anchor. Nothing gets ripped out, and the comparison is the point.

**One friction to settle in 6b:** strict/moderate/loose would mean something different for this
lens — a tolerance, not a radius. Either the control takes lens-specific semantics with the meaning
shown, or this lens ignores it and states its own.

**What this instrument gives up:** the harmonic shape representation. `(a1, b1, a2, b2)` do not
percentile meaningfully — the percentile of `a1` mixes amplitude and phase. So it uses
interpretable scalars, with the collapse problem that killed the *original* scalars handled by the
modality gate rather than by the embedding. Coherent, but WO2a's harmonic work does not carry over
into this design, and that should be stated rather than assumed.

