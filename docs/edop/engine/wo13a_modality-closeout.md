# WO13a — Modality floor: close-out

**Phase:** Areas · **Sub-phase:** engine · **Date:** 2026-06-26
**Amends:** WO13 (supersedes Part 2) · **Depends on:** WO13 Part 1 result.

---

## What Part 1 settled

A single floor *technically* separates the 12 — but only in a **1.97 pp window** (any `A` in 80.5–82.5 pp), because `wet_pct_grp1` (a flipper that dissolves at L8) has an 80.54 pp center-gap, nearly equal to `dist_sink`'s 82.51 pp. A floor that high is no longer a noise filter: it would also kill `precip_yr_upstream` (58), `pasture_extent_upstream` (66), `wet_pct_grp1_upstream` (69) — large gaps that aren't noise.

The lesson: **gap magnitude is not evidence of genuine bimodality.** An 80 pp gap that dissolves at L8 is two piles of an under-sampled gradient, not two regimes. `dist_sink` survives not because its gap is large but because its valley is *unfillable* (a basin drains to the ocean or it doesn't; no sub-basin takes a middle value). No L6-computable quantity we have tested separates an unfillable discontinuity from a fillable gradient: **gap** fails (knife-edge), and **seam-alignment** already failed in WO12 (`human_footprint_09` and `pasture_extent_upstream` share `dist_sink`'s exact partition and still dissolved).

---

## Decision (closure)

1. **Do not build the gap floor.** WO13 Part 2 is retired. The floor is a broken proxy.
2. **Modality on continuous variables is a support-relative verdict.** It is computed and reported at the queried support; it is **not** corrected from coarse data. Coarse-support `two_regime` is inherently low-confidence and may dissolve at finer support — this is disclosed, not fixed. Same posture as MAUP generally.
3. **No engine edit** beyond a one-line clarification, if useful, that the `modality` flag's meaning is support-relative. No new threshold, no seam prior, no floor.

This closes the L6↔L8 modality thread. The verdicts stand as computed; their support-relativity is documented.

---

## Register (consolidate three items into one, then close the rest)

- **Retire** "absolute-separation floor for modality detector" — proven a broken proxy (1.97 pp window; `wet_pct_grp1` the binding case). Move to Closed with this reason.
- **Retire** "support-relative vs structural-seam prior" — resolved to **support-relative**. Move to Closed.
- **One new deferred item** replacing both: *"Single-level bimodality instrument."* A proper bimodality statistic — gap normalized by within-regime spread (two tight modes vs. two diffuse tails of a stretched gradient), or a dip test — is the only untried candidate for an L6 predictor of genuine bimodality. It is a larger change than a threshold and unvalidated on one fixture. **Trigger:** multi-fixture calibration (Egypt, Song), developed together with the open question of whether `dist_sink`'s near-discrete behavior is intrinsic to the variable or specific to Timbuktu's drainage.

---

## AF.7 — final form

Fold in: 11/11 directional flips (`two_regime`→`unimodal` at L8); only `dist_sink` survives. The floor is a broken proxy — 1.97 pp separating window, `wet_pct_grp1` at 80.54 pp the binding constraint; gap magnitude does not indicate genuine bimodality. No L6-computable quantity tested (gap, seam-alignment) distinguishes a structural discontinuity from an under-sampled gradient. **Closure:** modality on continuous variables is support-relative — reported at the queried support, coarse-support `two_regime` flagged low-confidence, not corrected. A proper bimodality statistic is the candidate single-level instrument, deferred to multi-fixture.

---

## Acceptance

- WO13 Part 2 marked retired (no floor code).
- Register: two items closed, one consolidated item added with the multi-fixture trigger.
- AF.7 in final form.
- Modality verdicts unchanged in the engine; support-relativity documented.
-