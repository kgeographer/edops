# WO3 — Continuous precipitation lens; retire the phase lens; scalar hygiene

**Status:** draft for review.
**Prior:** `wo1_findings.md`, `wo2_findings.md`, `wo2a_findings.md`.
**Supersedes:** WO2 Part B4 (Option B) in full.

Goal-setting with provisos. CC discovers implementation particulars; Karl reviews every write.

---

## Why this shape

WO2a Part B established that the continuous four-component representation of monthly rainfall
separates Mombasa from the European temperate cluster with no classifier, no threshold inside
feature construction, and no candidate filter. Its five nearest neighbours are four Kenyan
coastal basins plus the Ghana coast, twin peaks visible in every profile. That is the WO1
failure, closed.

The seasonal phase lens is a different matter. Four designs have now been tried — the original
scalar, the branching `_v2`, the `(cross, dot)` reduction, the 4D absolute form — and each
exposed a new defect rather than closing the previous one. The diagnosis is that the lens was
never one question. It bundled three:

1. **How many wet seasons?** — broke the original scalar, and has now migrated into the
   precipitation lens where it belongs.
2. **Do rain and heat coincide?** — answerable, but *hemisphere-blind*. Keeping only this
   matches Santiago to Split correctly and Mombasa to Split incorrectly.
3. **When in the calendar does the year turn?** — answerable, but *hemisphere-aware*. Keeping
   only this separates Mombasa from Split correctly and destroys the Santiago/Split match.

(2) and (3) cannot share a lens: each fix breaks what the other repairs. That is a fork
requiring a research decision, not a math problem requiring a fifth design.

And (2) — the only sub-question that survives decomposition intact — is **undefined precisely
where it is most needed**. Mombasa's temperature range is 1.87 °C; there is no thermal year for
rainfall to be in or out of phase with. The same holds across most of the equatorial belt, which
is where the D-PLACE correspondence work is concentrated.

The lens is therefore retired rather than redesigned. Nothing currently asks for it.

---

## Part A — Precipitation lens: continuous features

Replace `climate.precip` features with the four harmonic components computed in WO2a, plus
annual total.

Provisos:

- **Retire `same_modality` entirely.** It was proposed as a safety net; WO2a Part B shows no net
  is needed. Modality does not enter the engine.
- **No threshold appears anywhere in feature construction.** If a formula branches, the metric
  built on it is lying somewhere.
- `pre_concentration` and `R_dbl` are *exactly* the magnitudes of the two component pairs
  (verified to machine epsilon in WO2a A2). Including them alongside the components would be
  perfectly redundant. Do not.
- Annual total is a magnitude and the components are shape. Keep that separation explicit and
  independently weightable — *how much* and *when* are different questions. Logging the total is
  likely; confirm against the distribution rather than assuming.
- Correlation structure in the new feature set determines Euclidean vs Mahalanobis dispatch.
  Check it; do not inherit the previous lens's choice.
- Radii require recalibration against L06 CDFs in the new space. L08 uses topN and is unaffected
  (`wo_l08_findings.md` Part D).
- Both the L06 and L08 indices rebuild. Startup cost is negligible (vectorised over already-loaded
  arrays), but confirm rather than assert.

## Part B — Retire `climate.phase`

Remove the seasonal phase sub-lens from the lens registry, from the sandbox Similarity tab, and
from the WH Cities dropdown on `cdop_pilot.html`.

Provisos:

- Removal, not deferral-with-a-plan. If a use case asks for hemisphere-blind phase relation or
  hemisphere-aware seasonal timing, either can be built then, as its own lens, with its own
  question. Record the fork in the deferred register so the analysis isn't repeated; do not
  record an intention to build.
- `seas_phase_offset` stays in the signature as a display variable. It is not wrong as a
  *description* of a basin with two well-defined cycles; it was wrong as a *distance feature*
  applied to basins that don't have them.
- Climate lens group goes from three sub-lenses to two. That is a reduction in controls to
  explain, not a gap to fill.

## Part C — Scalar hygiene

The monthly arrays and the charts drawn from them are the truthful representation. The derived
scalars are lossy summaries, and three of them are currently misleading on the surface.

**`pre_peak_month`** — currently derived from the summed-vector direction, which is why Mombasa
reads June against a May maximum. Derive from the monthly maximum instead. Where a basin has two
comparable peaks, a single peak month is a category error: report both (`phi_dbl` predicts them,
validated in WO2 A7) or report none. Do not report one.

**`pre_concentration`** — the name asserts more than the quantity delivers. It is the strength of
the annual cycle, and it is only readable as "seasonality" when the second harmonic is small.
Mombasa's 0.21 alongside Augsburg's 0.21 is the whole failure in one number. Either rename it to
what it measures and never display it without its companion, or drop it from the displayed
signature. Recommend one; the Explorer choropleth is a consideration on the keep side, and
`R_dbl` or a modality layer would serve there instead.

**The `aseasonal` class label** — currently covers relentlessly wet equatorial, temperate
distributed, and genuinely seasonal Mediterranean, at 48% of basins, and it reaches users as
generated prose. Rename and split. This does not wait on anything else in this WO.

**The narrative generator** — Mombasa currently receives *a Mediterranean-type anti-phase pattern
where the wet season is the cool season*. That sentence is confidently wrong, in prose, on a
deployed surface. It should be repaired in this WO, and its claims gated on whether the
underlying cycles are strong enough to support them.

Proviso: `pre_modality` survives as a display variable only — Explorer categorical layer,
narrative vocabulary, population description in writing. But its thresholds are now doubly
suspect (see below), so revisit them before it is displayed anywhere.

## Part D — The glyph

Ship the monthly-profile visual with the precipitation lens: twelve bars per result, query at
top, shared scale, two-harmonic fit overlaid.

Provisos:

- Show **raw bars and fit together**, not the fit alone. Mombasa's 235 mm May against its 110 mm
  November, versus a smoother reconstruction, is the honest picture of what the metric can and
  cannot see. That divergence is information.
- The rule this arc actually established is diagnostic, not decorative: **when a similarity
  result looks wrong, draw the compared dimension before theorising about the metric.** In WO2a
  the glyph was used to confirm a success and never pointed at a failure. Some of the four-design
  cycle on the phase lens was probably avoidable.
- Generalises to future lenses: a lens definition has three parts — variables, metric, glyph.
  Terrain would want a hypsometric or elevation profile. Not built here; noted as the pattern.

---

## A finding that arrived with the George Town chart

WO2 justified `THRESH_DBL = 0.30` partly on George Town being "correctly excluded" — described
there as high baseline with no true dry season and only a mild secondary peak.

The Walter-Lieth plot shows otherwise: an October–November maximum (365 mm) and a clear April
secondary (275 mm), roughly six months apart, with June and January–February troughs. That is
twin-peak structure on a high baseline, which is exactly the dilution case WO2 flagged as a
limitation elsewhere in the same document. `R_dbl = 0.187` because the ratio is suppressed by a
~150 mm/month floor, not because the structure is absent.

Consequences:

- The threshold's empirical justification rested on a mischaracterised case. Immaterial for
  similarity — thresholds are gone from feature construction — but material for `pre_modality`
  as a display variable, which still depends on them.
- It is further evidence for the diagnostic rule in Part D: the chart contradicted the prose, and
  nobody had drawn it.
- The SE Asia held-out cases in WO2a Part C were assessed by distance to two anchors and read as
  "correctly unimodal." Given George Town, that reading is not safe. Cheap check, worth doing
  inside this WO: pull the monthly profiles for Bangkok, Ho Chi Minh, and Manila, and their own
  top-5 neighbours rather than their distance to Mombasa and Augsburg. Two visible peaks with the
  metric reading unimodal is a miss; one peak with a shoulder vindicates the reading.

---

## Accept gate

**The WH Cities precipitation lens returns bimodal East African neighbours for Mombasa, Lamu, and
Zanzibar City, with monthly profiles rendered beside each result; the phase lens is absent from
both surfaces; and no deployed surface asserts a Mediterranean anti-phase description for a
bimodal basin.**

Supporting: test suite green; L06 and L08 indices rebuild within existing startup budget;
`pre_peak_month` returns May for Mombasa.

This closes the WO1 accept gate.

---

## Out of scope

- Rebuilding phase similarity in any form
- Two-harmonic extension beyond the second harmonic
- Terrain or Hydrology lens groups
- Modality-based correspondence analysis against D-PLACE (Phase 4; the more valuable thread, and
  it needs its own frame rather than a slot in a remediation WO)

---

## For the deferred register

- **The phase fork.** Hemisphere-blind relation and hemisphere-aware timing are two distinct
  lenses. Analysis is done; trigger is a use case asking for either. Not a prediction that one
  will arrive.
- **Support sensitivity in probe selection.** Rome was dropped from WO2a because its L06 basin
  mixes Apennine terrain; Kerala-N and Kerala-S resolved to one basin. Both are
  container-constitutes-the-place instances, and they belong recorded as support findings rather
  than as probe-selection footnotes.
- **High-baseline dilution in `R_dbl`.** Normalising by annual total suppresses the ratio where
  the monthly floor is high. Affects the modality classifier, not the continuous features.