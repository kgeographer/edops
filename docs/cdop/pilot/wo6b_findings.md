# WO6b findings — Compare the curve, not its summaries

**Work order:** `docs/cdop/pilot/wo6b_compare-curves.md`
**Branch:** `cdop_wo6`. **Notebook:** `notebooks/cdop/wo6b_compare_curves.ipynb`.
**Papers (on disk, `articles/`):** Knoben, Woods & Freer (2019); Berghuijs & Woods (2016).
**Date:** 2026-07-22. **Status:** Parts A–E all run and read. Notebook complete.

Thesis under test: every prior similarity attempt compressed twelve monthly values into 2–5
scalars and compared those, and the failures were in the *compression*. WO6b compares the
twelve-value curve directly (Pearson correlation on mean-centred monthly precipitation) and rebuilds
the conjunctive instrument on top of it.

Two additions to the WO, made in the notebook: an amplitude condition for Part D (Part A's own text
promised one; the WO's Part D omitted it), and B&W's `s_d` (precipitation–temperature phase
difference) for Part E. Both flagged inline.

---

## Part A — Does profile correlation discriminate? — YES

The kill condition (distribution massed near 1.0, no usable spread) is not met. Pairwise
correlations over a 4,000-basin sample are U-shaped (modes ≈ −0.78 and +0.90, trough at 0, sd
0.66) — the mass at the ends is the hemisphere split (cross-hemisphere mean −0.325, same-hemisphere
+0.309), but neither lobe saturates and 86% of same-hemisphere pairs sit below 0.9.

The decisive per-probe measure is rank-decay (`spread_r1_r1000`). It splits cleanly **by modality**:
bimodal/aseasonal probes discriminate strongly (Somalia 0.51, George Town 0.48, Mombasa 0.44,
Tennessee 0.42, Nairobi 0.35); single-peaked probes barely rank (Yakutsk 0.04, Timbuktu 0.06,
Kaifeng 0.06). Mechanism is shape-space density — single-peaked-summer-max is the commonest shape on
Earth (WO2: 7,923 of 16,397 basins), so a single-peaked query lands in a dense near-tie
neighbourhood and a distinctive-shape query does not. This is WO4 Part 1's "autocorrelation not
analogy" restated in shape-space.

**Ranks 1–10 are near-ties for every probe** (Cell 8): a "top-5" list is an arbitrary slice of a
larger tied set. The instrument's real signal is at the scale of "these ~100 vs those ~1000", not
"here is your single best match" — the same conclusion the WO5 Context tab reached from a different
direction.

## Part B — Probe behaviour — passes the known-answer cases

Correlation-ranked neighbours (Cells 9, 10, 10b), every result drawn:

- **Timbuktu → single-monsoon Sahel basins**, not the two-peaked basins `R_dbl` grouped it with. ✓
- **George Town → twin-peaked basins** (Congo Basin, Colombia) despite its high baseline — the
  case `R_dbl` called "aseasonal" and missed. ✓
- **Somalia → the Ethiopian/Somali two-rains highlands** despite its modest second peak. ✓
- **Tennessee → coherent local matches** — a case no harmonic-ratio measure can detect in principle. ✓
- **Mombasa → the Kenyan/Tanzanian coast**, not Guitri/Abidjan — WO4 found those only *with* a
  geographic exclusion radius, which this configuration has none of. Not a failure, a scope note.

**Modality is emergent, not classified (Cell 11) — the WO's strongest claim, confirmed.** With
modality nowhere in the metric, correlation returns same-modality neighbours anyway: top-50
same-class share is 100% (Somalia), 98% (Nairobi), 92% (George Town) against a 17.4% bimodal base
rate — 5–6× enrichment. So the prominence-threshold problem WO6a Part A could not solve is here
**dissolved** for the bimodal cases. Mombasa is the informative exception: peak-counting labels it
unimodal, yet 82% of its correlation neighbours are bimodal — making the peak-counter the lone
dissenter against three independent methods (correlation here, Knoben in Part C, WO2a's original
`R_dbl` validation) on the canonical validated bimodal case.

**Scale-free is a real hazard, not a footnote (Cell 10b).** A given correlation value is not equally
demanding across queries (r=0.90 is rank 61 for Nairobi, rank 2,149 for Timbuktu), and high
correlation admits climatically absurd magnitudes: Augsburg (1006 mm/yr) matches a 107 mm/yr basin
at **r=0.95** — same annual shape, one-tenth the water. This is the definitional behaviour of a
shape measure and it settles that correlation cannot be the instrument alone; the magnitude band is
mandatory, not a refinement.

## Part C — Knoben ΔE as an independent modality check

Faithful implementation (validated on synthetic curves of known modality, Cell 12, including the
paper's own asymmetric-bimodal failure case). Verdict made three-way rather than binary: **BIMODAL /
unimodal / UNDETERMINED** (both sine models fit badly, |ΔE|≈0 — the paper's "no clear improvement",
i.e. the method abstains) **/ ASEASONAL** (no cycle to have a modality).

- **Knoben agrees with peak-counting on 9 of 11 probes.** Both disagreements are informative:
  Mombasa (Knoben BIMODAL, peak-count unimodal — see above) and Tennessee (Knoben ASEASONAL,
  peak-count 3).
- **The WO's Part C predictions were wrong, and the synthetics said so before the probes did.** WO6b
  predicted Knoben would fail Mombasa and George Town for asymmetry. It doesn't: both come out
  BIMODAL. The equal-amplitude breakdown lands between 2:1 and 4:1 peak-height asymmetry; Mombasa
  (2.1:1) and George Town (1.35:1) sit on the good side.
- **Knoben's ΔX degrades gracefully** — as asymmetry grows, ΔE collapses toward zero with both
  errors rising, rather than flipping sign. UNDETERMINED catches that state.

## Part D — The conjunctive instrument on shape correlation

Five conditions, none may compensate for another (Cell 16): shape (correlation cut, declared),
magnitude (annual-total ratio band), amplitude (see below), temperature level, temperature range.
Coarsened Exact Matching (Iacus, King & Porro) is the named literature.

**The instrument does not starve.** Result-set sizes at corr≥0.90 run 1 (Santiago) to 102
(Timbuktu); only Nairobi at the strictest cut (0.95) empties. Confirms WO6a's non-starvation finding
on a new basis.

**Headline: the load-bearing condition rotates by query — every condition is decisive for some
probe, none for all.** Tightest standalone condition per probe: shape for 7 of 11 (the distinctive
shapes — Mombasa, George Town, Nairobi, Tbilisi, Somalia, Tennessee, Santiago); temperature level
for Augsburg and Kaifeng; temperature range for Yakutsk (its 59.6 °C annual range is matched by
almost nothing); amplitude for Timbuktu. Distinctive-shape queries are nearly finished by
correlation alone (Mombasa corr-alone 15 → final 6); generic-shape queries where correlation is
useless (Yakutsk corr-alone 3,761) are pinned by whatever axis they *are* unusual on. **No query
relies on all five; each is nailed down by the subset it is distinctive on** — the anti-fragile
property a non-compensatory conjunction is supposed to have, and the strongest single argument that
this design is right.

**The amplitude condition: two scalars tried, both flawed as global measures, `cv` retained because
the band usage is sound.**

- `delta_P` (τ=12 fit amplitude) **collapses on bimodal profiles** — the 12-month sine cannot track
  two peaks, so its amplitude measures a failed model. George Town (bimodal) scores 0.088 vs flat
  Tennessee's 0.140, backwards. Visible in the Cell 14 fitted curves. `rel_amp` (first harmonic /
  mean) fails identically, confirmed corpus-wide (2-peak class rel_amp_med 0.32 vs cv_med 0.36).
- `cv` (sd/mean) **explodes on dry-season zeros** as a global ranking (Timbuktu 1.56, Somalia 1.14
  top it on aridity, not seasonality) — **but Cell 16 uses cv as a ±0.15 band around each query's
  own value, which is self-protecting**: a low-cv query cannot reach into high-cv arid territory, so
  the pathology never fires. And cv is **not redundant with the magnitude band** — it cuts hard
  *after* ratio has applied (Timbuktu 645→119, Kaifeng 605→252, Yakutsk 994→576), removing basins of
  similar total and similar shape but different peakiness. That is precisely the amplitude case Part
  A specified. cv earns its place as a band; it is unusable as a global amplitude scalar. No single
  scalar was found that means "how seasonal" across both a Congo double-peak and a Sahel monsoon —
  a `delta_P`-vs-`cv` mirror-image failure, the recurring "no clean scalar" result one level down.

**Caveats.**
- **The magnitude ratio is broadly useful but never the single tightest condition for any probe** —
  the earlier "ratio dominates" expectation was right cumulatively (it is the largest cut once
  correlation has run) and wrong as a standalone claim.
- **Tennessee is pure autocorrelation** — corr-alone 20, and every subsequent condition changes
  nothing (20→20→20→20), because its correlation neighbours are its adjacent basins, which share
  everything. For such queries the conjunction adds nothing over correlation, and result-set size
  measures geography, not analogy.
- **A single global correlation cut is a defensible declared parameter but not a uniform quality
  guarantee** (Cell 10b): the same r-value is a demanding bar for distinctive shapes and a lax one
  for generic shapes.

## Part E — Hemisphere, three ways: `s_d` wins, the shift trick is dead weight

Three candidate hemisphere/phase measures compared per probe (Cell 17): calendar-locked
correlation, correlation maximised over the 12 circular shifts, and B&W's `s_d`
(precipitation–temperature phase difference).

**The circular-shift trick contributes nothing.** `gain` (best shifted correlation minus
calendar-locked) is 0.000 for 9 of 11 probes and 0.002 for the other two — every best match is
already at shift 0. This is structural, not incidental: for a 6-month shift to help, a probe's best
shape-twin would have to be calendar-*opposed*, but such a twin correlates *negatively* at shift 0
and so never tops a correlation-maximising ranking in the first place. The WO framed the maximising
shift as "itself informative"; it is not, because the maximiser is always 0. **Drop it.**

**`s_d` is the hemisphere instrument, and validates where it should.** Santiago = **5.20**, nearest
the ±6 Mediterranean pole of any probe — austral-winter rain, rain *against* warmth, read correctly
with no shift search. Timbuktu (1.04) and Yakutsk (0.69) sit near 0 — rain with warmth
(monsoon/continental summer). `s_d` is hemisphere-blind by construction, so it separates the
Santiago/Kaifeng conflation Cell 6 exposed (both peak in boreal-calendar summer) that neither
correlation variant can, since their best shift is 0.

**But `s_d` is defined only for single-cycle basins — the real limitation.** It is the phase of a
τ=12 sinusoid, so it inherits the same fit-validity gate as `delta_P`: five probes return `s_d`
NaN (Mombasa, Kaifeng, Nairobi, Somalia — τ=12 fit poor, E>0.25), and George Town's 3.69 / Tennessee's
−4.43 are the phases of a badly-fitting and a flat curve respectively — noise. So the phase-of-rain
question is well-answered for unimodal climates and **not answerable at all for bimodal ones**,
because "when does the rain fall relative to warmth" is not single-valued when there are two rainy
seasons. Same shape as the rest of the notebook: single-cycle tools work on single-cycle climates
and degrade on the multi-peak cases — which is precisely why correlation on the raw twelve-value
curve (no cycle assumption) was the right backbone.

---

## Modality as an emergent class — and the aseasonal class recovered

Cross-cutting result from Parts B–C and the Cell 18/18b retrospective, relevant to WO6a:

- **Peak count is not an ordinal ladder.** `cv` by peak-count class is V-shaped: 0 peaks low-cv
  (0.16), 1 peak highest (0.64), 2 peaks moderate (0.36), 3+ peaks low again (0.15–0.19). Both
  *ends* mean aseasonal — `0/1/2/3+` reads `aseasonal / unimodal / bimodal / aseasonal-with-noise`.
  The 3+ class is wet, flat basins whose noise resolves into several bumps (total_med rises
  monotonically 180→578→793→1107→1275 mm/yr with peak count).
- **Karl's hypothesis (>2 peaks ⇒ aseasonal) holds as sufficient-not-necessary.** 60–87% of 3+peak
  basins are low-cv, but only ~14% of low-cv basins have 3+ peaks — most aseasonal basins resolve
  into 1–2 noise peaks and are missed by the peak route. So 3+ peaks corroborates aseasonality;
  it cannot detect it. A dimensionless-amplitude gate (`cv`) catches the rest.
- **`cv` has no natural aseasonal threshold** (Cell 18): the corpus histogram is a flat plateau from
  ≈0.15 to ≈0.65, no trough. `CV_FLAT = 0.20` is a declared convention with no data-driven support —
  the same "no natural cut" result as WO6a Part A, one method over. It still separates the probes
  correctly (Tennessee 0.144 below, George Town 0.296 above); a convention can be defensible without
  being natural, and this must be stated as such rather than as a discovered boundary.

## Correction owed to `wo6a_findings.md`

Cell 18 relocates the cause of WO6a Part A's "no correct floor value" conclusion. The conclusion
**stands**, but:

- **The flagship example (Somalia) was wrong** — its L06 basin is 87 mm/yr, arid-gated by the
  well-evidenced `THRESH_ARID`, so it should never have been classified for modality at all. It was
  described in WO6a as "a textbook two-monsoon climate" without checking the basin's annual total.
- **The binding condition is low seasonal *range*, not aridity.** The floor binds when
  `range < abs_floor / frac`. Of the 1,543 basins that flip class between the 10 mm and 20 mm floors,
  median range is 29 mm but **37.8% are wetter than 500 mm/yr** — wet, low-range basins (the
  Tennessee type). `THRESH_ARID` gates on total and cannot screen these. So the tension is real and
  general, but its cause is seasonal range, and the correct in-corpus example is Tennessee, not
  Somalia.
- **Mombasa is a separate correction:** its second peak fails peak-counting at *both* floors because
  `0.20 × range = 43.4 mm` dominates both, so the floor is irrelevant — the miss is driven by the
  0.20 *fraction* being too high, not by the floor. Neither of WO6a's two knobs is right for it.

(Amendment to `wo6a_findings.md` itself deferred to the WO6a-close step, per the agreement to wait
for the Nairobi/Tennessee evidence — now in hand.)

## Open for WO6c / decision

- Whether the amplitude condition ships as `cv`-band (works, but conflates aridity into the axis for
  arid queries) or is dropped in favour of a purpose-built concentration measure (Gini / PCI /
  wettest-months fraction), none yet tested.
- `s_d` (Part E) is the hemisphere instrument; the shift-max trick is dead weight (drop). Open:
  how to answer the phase-of-rain question for *bimodal* basins, where `s_d` is undefined — likely
  the two harmonic phases separately, or left unanswered as genuinely not single-valued.
- Whether the modality trichotomy (aseasonal / unimodal / bimodal) enters the instrument as an
  explicit gate or is left emergent in the correlation, given Part B showed it emergent for the
  cases that matter.
