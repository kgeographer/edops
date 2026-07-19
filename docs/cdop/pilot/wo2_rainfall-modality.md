# WO2 — Rainfall seasonality modality: investigation and variable definition

**Status:** draft for review. Notebook-only; no registry writes, no UI changes.
**Scope note:** this is **EDOP** work, not CDOP — it changes shared signature variables and
affects the sandbox Seasonality and Similarity tabs. DEMO is closed, so it needs a phase home.
Flagged for Karl; not decided here.

**Prior:** `wo1_findings.md` (bimodal hypothesis), CDOP1 WO1 accept gate partial fail.

---

## Problem

`pre_concentration` compresses the twelve monthly rainfall values to a single scalar — the
length of the summed monthly vector on a twelve-month circle. That scalar assumes one wet
season. Where a basin has two, the peaks sit roughly opposite each other and largely cancel,
producing a low value indistinguishable from genuinely aseasonal or arid basins.

Three physically distinct regimes therefore collapse to the same reading:

- evenly distributed rainfall (temperate oceanic)
- two wet seasons (equatorial bimodal)
- little rainfall in any month (arid)

Everything downstream inherits the collapse.

### Observed consequences

- **Similarity, L08 corpus (WO1):** Mombasa's precipitation-lens neighbours are Augsburg,
  Salzburg, Kotor, Tinn. Phase-lens neighbours include Split, Ibiza, Vatican City.
- **Similarity, L06 global (deployed sandbox):** Mombasa's neighbours are in Spain, Turkey,
  Turkmenistan, Uzbekistan, Pakistan. No equatorial matches. The global population does not
  compensate — this is live and visibly wrong.
- **Seasonality tab narrative (deployed):** for Mombasa the blurb reports a June precipitation
  peak (the chart shows May at 235 mm) and asserts a *Mediterranean-type anti-phase pattern
  where the wet season is the cool season*. Both are wrong, and they are stated in prose.
- **The same app contradicts itself:** the Walter-Lieth and polar charts draw the two peaks
  correctly. Only the derived scalars erase them.

### Why the metric swap could not have fixed it

The old PCA composite returned Jerusalem; the calibrated lens returns Augsburg. Two different
metrics, two different wrong answers, both drawn from the same collapsed set. Information is
lost upstream of the distance function, so no distance function recovers it.

---

## Approach

Add a second measure computed on **doubled month angles**. Months six apart map to the same
direction and reinforce instead of cancelling. Paired with the existing measure it separates
the collapsed regimes:

| Regime | Standard sum | Doubled-angle sum |
|---|---|---|
| Single wet season | high | low |
| Two wet seasons | low | **high** |
| Aseasonal or arid | low | low |

This restores a dimension the current signature cannot carry — how many wet seasons a place
has — rather than replacing the circular framing, which remains correct for timing.

---

## Parts

### Part A — Population characterisation (the question that shapes everything else)

Compute the doubled-angle measure across all L06 basins (and L08 if cheap), and describe the
population:

- How many basins read low on the standard measure but high on the doubled-angle measure?
  Is Mombasa an outlier or a member of a substantial class?
- Where are they? Expect East Africa, Indonesia, coastal Brazil, Sahel margin, parts of
  monsoon Asia — confirm or refute.
- How many basins are low on both, and can arid be separated from aseasonal-wet using annual
  total?
- Does the modality reading hold between L06 and L08, or is it support-relative like the
  earlier modality findings? Report at both if the L08 index makes this cheap.

**This part gates the rest.** If the bimodal class is small and geographically marginal, a
narrow fix is warranted. If it is a large share of the tropics, the variable set changes and
recalibration follows.

### Part B — Variable definition

Propose the variables to add or amend, with names and definitions:

- the doubled-angle concentration measure
- a derived regime label (single / double / aseasonal / arid) if the population supports clean
  separation — **only if it does**; a label with fuzzy boundaries is worse than two scalars
- disposition of `seas_phase_offset`: its angle is unstable when the standard measure is near
  zero. Options are to mask it as undefined below a threshold, or to define it against the
  doubled-angle direction for bimodal basins. Recommend one.
- disposition of `pre_peak_month`: currently appears to derive from the summed-arrow direction
  (Mombasa reads June against a May maximum). Confirm, and recommend deriving it from the
  monthly maximum instead.

Provisos:

- Temperature is not affected — it is genuinely single-peaked, and the temperature lens passed
  WO1's gate. Do not touch it.
- One physical question per lens still applies. Peak count and peak timing are different
  questions; deciding whether they belong in one lens or two is part of this WO.
- The 719 basins with no monthly rainfall stay NaN. Zero is a value; absence is not.

### Part C — Downstream impact assessment (assessment only, no changes)

Enumerate what a variable change touches, so the implementation WO can be scoped honestly:

- `LENS_REGISTRY` precipitation and phase lens membership; whether Mahalanobis or Euclidean
  dispatch changes given the new correlation structure
- threshold radii — adding a variable invalidates the L06 CDF calibration for affected lenses
- the Seasonality tab narrative generator, including the peak-month bug and the anti-phase
  claim, both of which are wrong independently of the similarity work
- the Explorer, if either variable appears there

---

## Accept gate

**Part A produces a defensible count and map of the bimodal class, and Part B a recommended
variable set with the phase-offset and peak-month dispositions resolved.**

Sanity check on the new measure, in the notebook: Mombasa reads clearly bimodal; Augsburg
reads aseasonal; a known single-wet-season monsoon basin reads single. If those three don't
separate, the approach is wrong and should not proceed to implementation.

No registry writes, no API changes, no UI changes in this WO.

---

## Out of scope — implementation, deferred to a follow-on WO

Registry changes, radius recalibration, narrative-generator repair, and any UI work. Splitting
these out keeps one gate on this increment and lets Part A's population finding shape the
implementation rather than the reverse.

**Interim exposure question, for Karl:** the deployed sandbox currently returns wrong
similarity results and asserts a wrong climate narrative for bimodal basins. Whether to leave
it, quietly narrow it, or wait for the fix is a judgment call that shouldn't be buried in a
notebook WO.

