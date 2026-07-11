# WO13 — Modality detector: absolute separation floor

**Phase:** Areas · **Sub-phase:** engine · **Date:** 2026-06-26
**Depends on:** WO12 (L6↔L8 buffer comparison; AF.7)
**Branch:** continue WO12's branch.

---

## Why now

WO12 showed 11 of 11 L6 modality flips went `two_regime` → `unimodal` at L8, and only `dist_sink` survived. The reading (AF.7): at 9 basins the gap-based detector can't tell a real value discontinuity from an under-sampled steep gradient, so it over-calls `two_regime`. At 74 basins the gradients fill in and dissolve; the one genuine discontinuity (`dist_sink` — a basin drains to the ocean or it doesn't, no halfway) survives.

The fix is to make a gap more expensive to claim: require the two regime centers to be **far enough apart in value** before calling `two_regime`, not just separated relative to the local spread. The hope is that this reproduces the L8 verdicts *from L6 data alone* — i.e. an honest single-level detector that doesn't need an L8 pass to be trusted.

---

## Part 1 — Does a floor exist? (investigatory, one cell)

On the existing L6 regimes companion, for all **12** variables (the 11 flippers + `dist_sink`), compute the **regime-center gap** in the detector's own units (percentile points). Then answer one question:

**Is there a single floor value `A` (pp) such that `dist_sink` clears it and all 11 flippers fall below it?**

Report the 12 gaps, sorted, with `dist_sink` marked, and the yes/no. If yes, name the separating range (the window between the largest flipper gap and `dist_sink`'s gap). If no — if a flipper's gap overlaps `dist_sink`'s — say so plainly; that means a value floor alone won't separate the cases and we rethink before any code change.

This is the whole experiment. It runs on data already on disk.

---

## Part 2 — If clean: propose the edit (gated)

Only if Part 1 separates cleanly: propose the minimal change to `detect_modality` — `two_regime` requires **both** the existing relative test (`gap > MODALITY_GAP × spread`) **and** the new absolute floor (`gap ≥ A` pp). Show which of the 12 the combined rule now calls `two_regime` (should be: `dist_sink` only). **Do not write the engine edit until Karl signs off**, and do not touch the other thresholds.

**Do not** pursue a "feed the endorheic seam in as a prior partition" approach. WO12 already disproved it: `human_footprint_09` and `pasture_extent_upstream` carry `dist_sink`'s *exact* partition (0.4654/0.5346) and still dissolved — forcing them to report two regimes would manufacture structure their L8 values contradict. The floor is the instrument; the seam prior is off the table.

---

## Scope / deferral

- **Settled now (shape):** the fix is an absolute value-separation floor in the detector's score space. No seam prior.
- **Deferred (value):** the floor *number* `A` cannot be set honestly from one fixture. It waits for Egypt + the Song fixture at the multi-fixture calibration step. Part 1 only establishes that such an `A` exists at Timbuktu and its rough range.

**Register:** update the existing "absolute-separation floor for modality detector" item to carry the WO12 evidence (11/11 dissolve, `dist_sink` the lone survivor) and the Part 1 result; mark its *shape* settled, *value* multi-fixture-gated. **Drop** the "support-relative vs structural-seam prior" semantics item in favor of support-relative — the floor resolves it. Separately, note for later that the three climate-upstream vars (`aridity_upstream`, `precip_yr_upstream`, `temp_yr_upstream`) share an identical non-endorheic partition (0.2922/0.7078) — a candidate second partition, not noise; worth a look, not now.

**Findings:** fold the Part 1 result into AF.7.

---

## Acceptance

- The 12 L6 regime-center gaps reported, sorted, `dist_sink` marked.
- A clean yes/no on whether one floor separates `dist_sink` from the 11, with the separating range if yes.
- If yes: the proposed combined-rule call set shown, edit gated on sign-off.
- Register + AF.7 updated; value left deferred.
- 