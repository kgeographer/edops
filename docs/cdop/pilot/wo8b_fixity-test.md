# WO8b — Environment–culture correspondence: the first test (settlement fixity)

**Status:** draft for review.
**Prior:** `wo8a_findings.md` (Climate-envelope bet selected; composite-distance hazard surfaced;
container caveat disclosed; substrate parquet), `wo4_findings.md` (L08 join; language-family
crosswalk 92.6%), `wo6b_findings.md` (raw-curve backbone; `pre_concentration` scalar carries the
two-peaks-cancel bug), `EDOPS_variable_catalog_v0.3.tsv`.
**Type:** notebook, statistical test — no engine / API / UI. CC authors; Karl runs cell by cell.

Goal-setting with provisos. CC discovers implementation particulars; Karl reviews every write.

---

## Why

WO8a calibrated the instrument on the positive control (EA042 subsistence separates, most cleanly
in the Climate-envelope bet) and, in passing, established the honest baseline: environment sets
bounds it does not determine, and even a near-tautologically-environmental trait separates only
partially. WO8b is the **first real test** — the first trait we do not already know the answer for,
and the first to run the two controls WO8a deferred: the **phylogenetic null** (restricted
permutation within language family, the Galton control) and the **metric decision** (the
composite-distance hazard, now with a real question attached).

The trait is **EA030 settlement fixity** — an 8-step ordinal gradient from fully nomadic to complex
permanent settlement, 1,044/1,133 coded. It is the "middle rung" of a deliberately staged scale:
calibrate the *strong-hypothesis* middle (fixity) before the *contested* rungs (EA033 political
complexity, then EA034 high-gods). Its a priori environmental hypothesis is the strongest available
among the middles — resource predictability in time predicts sedentism — which is why a null here
would be genuinely surprising and a positive would calibrate the middle of the coupling scale.

**The tautology and its resolution — the reason this WO has two tests, not one.** Fixity is partly
a restatement of subsistence (nomadic↔forager/pastoralist, sedentary↔farmer). A *marginal* test of
fixity against environment would therefore largely re-measure EA042 and prove little. The value is
in the **nested** test — does fixity track environment *within* subsistence class, beyond what
being-a-farmer-vs-forager already forces. So WO8b runs **both, together**: the marginal (the
legible headline — "does settlement permanence track climate") and the nested (the rigorous version
that answers the skeptic — "and it is not just subsistence in disguise"). **The gap between them is
itself a headline output**, not a diagnostic: it quantifies how much of fixity's environmental
signal is subsistence in disguise versus genuinely additional.

## Predictor eligibility — unchanged

Climate-envelope bet, locked from WO8a: `aridity_index` (log), `precipitation_annual`, `runoff`,
`temperature_annual`, `tmp_seas_amp`. All `pre-1500 valid` / `full-record`. Modern-only and
temporal bands excluded (WO8a § Predictor eligibility).

---

## Part A — substrate extension

Extend `output/cdop/wo8a_substrate.parquet` with **EA030 fixity** (ordinal, from
`dplace.data`/`dplace.codes`) and the **WO4 language-family crosswalk** keyed to `society_id` — the
latter is the stratum for restricted permutation and was not in the WO8a parquet.

Provisos:

- **EA030 coverage is 1,044/1,133; the 89 uncoded societies drop** — a named scope limit, stated in
  the notebook. Confirm the family crosswalk's coverage (WO4 recorded 92.6%) and that societies
  lacking a family assignment are handled explicitly (they cannot be permuted-within-family and
  must be either dropped or pooled — declare which; do not let them silently anchor an unrestricted
  swap).
- **Report the cell counts before any test runs** — fixity × subsistence, and fixity × family. Thin
  cells are the nested test's failure mode: within-family permutation with sparse strata weakens the
  very null that is the point. This is a look-first gate on the test's own validity.

## Part B — the metric decision (the hazard WO8a surfaced, resolved with the question attached)

WO8a made the composite-distance hazard visible and did not resolve it: the water variables
inter-correlate 0.66–0.83, temperature↔amplitude −0.83 — all < 0.90, so no catalog guard fires, but
z-scored Euclidean over-counts these blocks (a 3-member water block outweighing a 2-member thermal
block). WO8b decides the metric. Three options, with the reasoning, not a diktat:

- **Drop-to-representative** — aridity as the sole water axis (WO8a: the three-way "water from
  above / flowing nearby" split *bought little independence*, so aridity, the balance term that
  already embeds P/PET, can stand for the block at little loss). Keeps every axis nameable.
- **Mahalanobis** — whitens the correlated blocks. Statistically tidy, but the resulting axes are
  not nameable, and attribution is the entire deliverable of 8c.
- **Keep-and-declare** — accept the over-counting, state it.

Recommended lean: **drop-to-representative for the water block; decide the thermal pair with the
question in front of you**, because level and seasonality are conceptually distinct claims even at
−0.83 collinearity, and collapsing them may erase a distinction fixity cares about.

Provisos:

- **The test metric and the attribution method are separable.** Run the omnibus on the chosen
  distance; do attribution afterward (envfit / db-RDA on the *raw named* variables). So the metric
  choice only has to be honest about *magnitude*; naming which dimension carries the effect is a
  separate, later step and is not constrained by it.
- **Report the effect size under more than one metric choice where they diverge materially** — a
  sensitivity line, so the headline R² is not revealed to be an artifact of over-counted water.
  Declare the choice carried forward and why.

## Part C — the test (marginal + nested, together)

Both PERMANOVAs, restricted permutation within language family, **PERMDISP run alongside each** so a
dispersion difference is never misread as a location shift (WO8a's Part D showed how much the
class structure can hide).

- **Marginal:** environment-distance ~ fixity. R², family-restricted p, PERMDISP. The legible
  headline.
- **Nested:** environment-distance ~ subsistence + fixity, with the **fixity term assessed after
  subsistence**. Its R² is fixity's environmental signal *net of* subsistence. The marginal − nested
  R² gap is reported as a finding.
- **Ordinal structure — do not throw the order away.** Fixity is an *ordered* 8-step gradient;
  PERMANOVA-as-factor tests only "do the 8 centroids differ," ignoring the ordering. Add a
  **db-RDA / ordered-predictor test for the monotonic component** — "does environment march along
  the fixity axis as fixity increases" — which is closer to the actual hypothesis than "the centroids
  differ somewhere." Report both: factor (any difference) and ordered (monotonic trend).

Provisos:

- **The nested null needs the right permutation scheme, not naive full-label shuffling.** Testing
  fixity *net of* subsistence under a within-family restriction requires reduced-model residual
  permutation (Freedman–Lane or equivalent) so the subsistence effect is held while fixity labels
  are permuted within family strata. Naive permutation of the raw fixity labels gives the wrong
  nested null. CC to implement the correct restricted-partial scheme; flag if the library in use
  cannot express it.
- **Thin-cell guard.** If the nested cells are too sparse to permute honestly, collapse the 8-step
  fixity to a declared coarser ordinal (e.g. nomadic / semi / sedentary / complex) and state the
  collapse as a convention in the notebook — do not fit thresholds to make cells work.
- **State the prediction before running it** (below), so the result confirms or refutes a named
  expectation rather than being narrated after the fact.

## Part D — the seasonality-reactivation probe

WO8a found rainfall seasonality *orthogonal to subsistence* — but fixity's a priori hypothesis
(resource predictability *in time*) points specifically at seasonality, the one channel subsistence
left idle. So this is a trait-specific probe, not a repeat: does **adding the raw-curve seasonality
channel** to the Climate-envelope distance change fixity's result where it did not change
subsistence's?

Provisos:

- **Raw 12-value precipitation curve** (WO6b backbone, bug-free), never the `pre_concentration`
  scalar (Mombasa two-peaks-cancel, WO8a Part C confirmed).
- This is a **comparison** — envelope vs envelope+seasonality — and the *increment* attributable to
  seasonality is the quantity of interest. Keep it a separate probe; do not fold the seasonality
  channel into the Part C headline metric.
- **A positive here is the publishable result of the WO**: seasonality non-load-bearing for
  subsistence but load-bearing for fixity is a clean dissociation. A null is also informative — it
  says fixity, like subsistence, tracks *amount and warmth*, not *timing*.

---

## The prediction (stated up front)

The **aridity constraint survives within-family permutation better than the temperature /
continentality separation**, because water availability varies within language families more than
latitude band does — part of any forager↔cold signal is that foragers cluster at high latitudes,
which is phylogeny, not independent evidence, and the family-restricted null is precisely what
removes it. Confirm or refute; either direction is informative.

## Anthropology claims to verify — the offloading guard

Not folded in as fact; flagged for confirmation (Ruth is the domain expert and the natural check)
before any of it is load-bearing in a presentation:

- **Binford, *Constructing Frames of Reference* (2001); Testart on storage and sedentism** —
  settlement fixity is predicted by resource predictability in time. This is the a priori
  hypothesis motivating EA030 as the middle rung. A worth-a-sentence check with Ruth before Braga.

---

## Accept gate

WO8a's gate was visual (*does it separate*). WO8b's is not, and deliberately **not "is it
significant"** — a significance gate incentivizes p-hunting and would corrupt the instrument's
credibility, which is the asset WO8a built. The gate is:

**A defensible, reported effect size for fixity — marginal and nested — with the family-restricted
null and PERMDISP, interpretable whichever way it comes out.** A null or dispersion-confounded
result PASSES the gate; it is a real finding, not a failure (WO8a set exactly this expectation).
What the gate requires is that the number is *honest and legible*: the pre-test cell counts
reported, the metric choice declared with a sensitivity line, the marginal−nested gap quantified,
the seasonality increment measured, and the stated prediction confirmed or refuted.

Supporting: container caveat handled per the conservative-bias argument — the basin-site gap is
non-differential (uncorrelated with the trait), so it biases toward the null; a positive that
survives it is conservative. **Not corrected up front.** A robustness rerun excluding the high-gap
(>2 °C) societies runs *only if* a result comes back borderline, guarding against differential
error via terrain (mountain basins carry the largest gaps and mountain societies may be
trait-distinctive).

---

## Forward (8c, 8d) — sketch, not drafted

The staged scale, each rung's result setting the reading of the next:

- **8c — EA033 jurisdictional hierarchy** (political complexity). The contested rung — circumscription
  theory (Carneiro) vs surplus/institutional accounts that route through subsistence. Also the
  natural rehearsal for high-gods, since complexity and moralizing-gods are tightly linked in the
  big-gods debate. Anthropology claims to be flagged for Ruth, per the guard above.
- **8d — EA034 high-gods** — the contested finale, read against a now three-point calibrated scale
  (subsistence strong / fixity middle / complexity contested), framed around an honest effect size
  and a clean family-controlled null, not a hunt for separation.

## Out of scope

- **8c / 8d traits** — sketched above, not specified until 8b's result lands (WO6/WO7 rhythm).
- **Held Bet 4 — Agriculture suitability** — opens only if 8b's nested subsistence structure asks
  for a soil axis.
- **Enrichment beyond EA** — demand-driven; the modest-effect finding argues for cleaner traits, not
  more (WO8a). Not now.
- **Container correction** — disclosed, conditional robustness rerun only (above); never corrected
  up front.
- **Any engine / API / UI.** 8b is a notebook.
- 