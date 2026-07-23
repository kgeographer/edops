# WO6c — Similarity panel, rebuilt on the conjunction

**Status:** draft for review.
**Prior:** `wo6b_findings.md` (Parts A, B, D), `wo6a_findings.md`, `wo5_findings.md`.
**Type:** engine + UI. Notebook only where a value has to be chosen.

Goal-setting with provisos. CC discovers implementation particulars; Karl reviews every write.

---

## Why

WO6b settled the backbone. Correlation on the raw twelve monthly values discriminates (Part A),
returns right-looking neighbours on every known-answer probe (Part B), and produces modality
without classifying it — 5–6× enrichment over base rate with nothing about peak count in the
metric. The non-compensatory conjunction built on it does not starve, and its load-bearing
condition rotates by query: shape pins the distinctive-shape basins, temperature range pins
Yakutsk, amplitude pins Timbuktu. No query needs all five conditions; each is nailed down by the
subset it is distinctive on.

The shipped panel is a composite-distance instrument with an uncalibrated threshold ladder. WO6a
Part D confirmed it admits basins from 0.27× to 3.87× Timbuktu's own rainfall at loose, because
shape agreement buys tolerance on magnitude. That is live now.

This WO replaces the engine behind the panel, and changes the output from a ranked list to a
painted set.

**Purpose, stated plainly so scope stays honest:** answer *what other basins are like this basin*,
on a map, per lens. Not classification, not naming, not a typology. The D-PLACE correspondence
question is a separate instrument and a later WO.

---

## Part A — Output shape: sets, not rankings

WO6b Part A found ranks 1–10 are near-ties for every probe. A top-5 was always an arbitrary slice
of a tied set, and the tie is a property of shape-space density rather than of the query.

Membership becomes binary: a basin satisfies every condition or it does not. Paint the set.

Provisos:

- Shade within the set by shape correlation if texture is wanted, but the ramp must not imply
  continuous membership. The Tbilisi map's pale outer wash — the 852nd-ranked basins painted at
  nearly the tone of real matches — is the failure this change exists to prevent.
- Report set size on the panel. *Your query matches 47 basins* is a substantive statement about
  the place; so is *3*, and so is *0*.
- Empty is honest scarcity (WO4 Part 2, WO6b Part D: Nairobi empties at the strictest cut). Say so
  plainly; do not widen bands automatically to avoid it.
- Report the spatial spread of the set alongside size — the measurement Karl established is a
  property of the place rather than a verdict on the instrument. *All 47 within 300 km* and
  *spanning 11,000 km* are both findings.

## Part B — Controls: declared bands, no ladder

Retire strict/moderate/loose for this panel. The replacement control is band width in stated
units.

- magnitude — annual total within a ratio band (1.25× / 1.5× / 2×)
- shape — correlation cut (0.85 / 0.90 / 0.95)
- temperature level and range — absolute degrees

Provisos:

- **Per-variable units, not one rule.** WO6a Part B found absolute and percentile bands fail in
  mirror image; the transform that makes a band meaningful differs by variable. Temperature in
  degrees, precipitation as a ratio (a band on log, scale-stable and immune to the right-skew that
  broke both tested rules at the wet end), shape as a correlation.
- The correlation cut is a **declared parameter**, chosen and stated, not fitted to probes. WO6b
  Part D notes a single global cut is not a uniform quality bar — r=0.90 is rank 61 for Nairobi and
  rank 2,149 for Timbuktu. That is a real limitation and it should be visible in the panel copy,
  not smoothed over.
- No calibration anywhere. The L06/L08 transfer problem does not arise: a ratio band and a
  correlation cut mean the same thing at any level.
- One or two presets are fine as a default; the point is that the label names what the band does
  rather than characterising the result.

## Part C — Lens composition

The conjunction composes by adding conditions. This is the property that makes the union Karl asked
for free — no weighting, no metric design, no compensation.

- **Precipitation** — shape correlation, magnitude ratio band, amplitude band
- **Temperature** — level and range bands; shape term pending Part D below
- **Climate (union)** — precipitation conditions **and** temperature conditions
- **Terrain** — scalar bands only (elevation, slope, relief); no monthly curve, so no shape term

Provisos:

- The amplitude condition ships as the `cv` band, per WO6b Part D. It is unusable as a global
  amplitude scalar — it explodes on dry-season zeros — but as a ±band around each query's own value
  it is self-protecting, and it cuts hard *after* the magnitude ratio has applied (Timbuktu
  645→119). It earns its place as a band and must not be exposed as a standalone score.
- Terrain is a variable-selection question, not a design question. Recommend a small set; do not
  build a Terrain lens group beyond what the conjunction needs.
- Do not add lenses beyond these in this WO.

## Part D — Does temperature get a shape term? (notebook, decide before building the temp lens)

Temperature has monthly arrays, so shape correlation is available. But temperature cycles are far
more uniformly sinusoidal than rainfall, and every Northern Hemisphere basin peaks in July. That is
precisely the kill condition precipitation escaped in WO6b Part A, and temperature may not escape
it.

Run the Part A distribution check on temperature profiles: pairwise correlations across a large
random sample, plus per-probe rank decay. If the distribution saturates near 1.0 within hemisphere,
the temperature lens is level-band plus range-band only, and that is the finding.

Cheap, decisive, and it determines the lens definition rather than being discovered mid-build.

## Part E — Container disclosure

The Similarity panel carries the same line the Context tab already carries: *this describes the
Level 8 basin the settlement sits in, not the settlement itself.*

Nothing here fixes the container problem — 13.4% of settlements above a 2 °C implied gap even at
L08 (WO5 Part 0B) — and this WO should not try. Saying so on screen is the honest available move
and it is already established practice on the adjacent tab.

---

## What comes out and what stays

Largely CC's call. Guidance rather than instruction:

- The percentile index (WO5) and the monthly array loading are unaffected and stay.
- `find_similar()` gains a conjunction path; the existing composite-distance path can remain for
  comparison during development.
- **Keep the old panel reachable until the new one is judged good.** The cdop_pilot tab removal was
  a long, dicey process; a parallel route or a feature flag is cheaper than a revert.
- `climate.phase` remains retired (WO3). Do not resurrect it.
- The circular-shift trick is dead — WO6b Part E measured its gain at 0.000 on 9 of 11 probes,
  because a calendar-opposed twin correlates negatively at shift 0 and never tops the ranking.
  Do not build it.

---

## Accept gate

**Timbuktu's precipitation set contains no basin outside the declared magnitude band, and the
WO6b probe set returns the same basins through the panel as the notebook produced.**

The first clause retires the confirmed defect by construction. The second confirms the engine swap
preserved the validated result rather than approximating it.

Supporting: set size and spatial spread reported; controls state their units; Part D's answer
determines the temperature lens definition; container line present; tests green.

---

## Out of scope

- The D-PLACE correspondence instrument (separate WO)
- Naming or classifying climate profiles
- Any fix to the container problem
- Hydrology lens group
- Phase-of-rain for bimodal basins (WO6b Part E: genuinely not single-valued; leave unanswered)
- The seasonal/aseasonal cut. WO6b found `cv` has no natural threshold — a flat plateau from 0.15
  to 0.65, no trough. It is not needed here, since the conjunction uses bands rather than classes.
  
  