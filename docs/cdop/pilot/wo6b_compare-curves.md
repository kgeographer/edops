# WO6b — Compare the curve, not its summaries

**Status:** draft for review.
**Type:** exploratory notebook. No engine writes, no registry changes, no API, no UI.
**Prior:** `wo6a_findings.md`, `wo5_findings.md`, `wo2a_findings.md`.
**New reference:** Knoben, Woods & Freer (2019), *Global bimodal precipitation seasonality: a
systematic overview*, Int. J. Climatology 39(1) 558–567.

Goal-setting with provisos. CC discovers implementation particulars; Karl reviews every write.

---

## Why

Every similarity attempt in this project has compressed twelve monthly values into two to five
derived scalars and compared those. The failures have consistently occurred *in the compression*,
not in the comparison:

- A single concentration scalar cannot distinguish two wet seasons from none (WO2a).
- `R_dbl` is wrong in both directions — false positive on a sharp single peak (Timbuktu, Fourier
  energy at all harmonics), false negative on a high baseline (George Town, verified against the
  chart) — and **structurally cannot detect peaks that aren't ~6 months apart** (Tennessee,
  WO6a).
- Prominence-based peak counting has no data-driven threshold and no absolute floor that avoids
  trading arid noise against real modest second seasons (WO6a Part A).
- Composite distances let shape buy tolerance on level, confirmed in `climate.temp` (WO5 Check 3)
  and in the shipped `climate.precip` (WO6a Part D: Timbuktu admits 0.27×–3.87× its own rainfall
  at loose).

The twelve monthly values *are* the curve. Twelve numbers can be represented exactly by
harmonics; both `R_dbl` and Knoben deliberately discard almost all of that to obtain a
low-dimensional summary. The compression is a choice, and this notebook tests not making it.

**This is a question, not a plan.** Correlation on smooth annual cycles may not discriminate.
Part A is designed to find that out first.

---

## Part A — Does profile correlation discriminate at all? (run this before anything else)

**The instrument:** Pearson correlation between two basins' twelve monthly precipitation values —
cosine similarity on mean-centred vectors, the operation Karl has run on term vectors for fifteen
years. No free parameters, no threshold, no harmonic assumption, no classifier.

**The risk that could sink it immediately:** twelve points, smooth annual cycles, and a dominant
global signal that is essentially *wet in summer* versus *wet in winter*. Most mid-latitude
Northern Hemisphere basins may correlate at 0.9+ with each other, in which case correlation
separates two or three coarse regimes and nothing finer.

Report the **distribution of pairwise correlations** across a large random sample of the L06
corpus before looking at any probe. If it is heavily massed near 1.0 with no useful spread, say so
and stop — the rest of the notebook is then moot and that is a legitimate outcome.

Provisos:

- Mean-centre before correlating. Raw cosine on non-negative vectors compresses everything into a
  narrow high band.
- Correlation is scale-free by construction: it sees shape only. Two basins with summer peaks, one
  strongly seasonal and one barely, correlate near 1.0. That is correct behaviour for a shape
  measure and it is why magnitude and amplitude must be separate conditions (Part D).
- Arid basins have near-flat, noise-dominated profiles whose correlations are meaningless. Apply
  the `THRESH_ARID` gate at 100 mm first — the one threshold in this project sitting in a genuine
  histogram trough, robust to ±25 mm.

## Part B — Probe behaviour

If Part A shows usable spread, run correlation-ranked neighbours for the WO4 probe set (Mombasa,
Augsburg, Tbilisi, Kaifeng, Timbuktu, George Town, Santiago) plus Yakutsk and the Somalia
two-monsoon basin (`hybas 1060006860`).

The questions, all with known right answers:

- Does Mombasa find Guitri and the Kenyan coast? (WO2a and WO4 both found these; a parameter-free
  measure reproducing them is strong evidence.)
- Does George Town find twin-peaked basins despite its high baseline?
- Does Timbuktu find single-monsoon basins rather than the two-peaked ones `R_dbl` grouped it with?
- Does Somalia find other two-monsoon regimes despite its modest second peak?
- Does the Tennessee basin (`hybas 7060610850`, peaks in March and December) find anything
  coherent? This is the case no harmonic-ratio measure can detect in principle.

**Draw every result.** Monthly profiles beside each neighbour, query at top, shared scale. This
rule has now paid off four times and been skipped once — WO2a's validation, George Town's
mischaracterisation, the peak-count detour, and the WO6a `R_dbl` disagreement profiles all used it;
the phase lens went four design rounds without it.

Proviso: **modality should be emergent, not classified.** Two twin-peaked profiles correlate
highly with each other and poorly with a single-peaked one, automatically. If that holds, there is
no gate, no prominence parameter, no `pre_modality` in the metric at all — and WO6a Part A's
unresolved threshold problem is not solved but *dissolved*. Confirm or refute explicitly.

## Part C — Knoben ΔX as an independent modality measure

Implement the Knoben method — fit truncated sine curves at τ=12 and τ=6 with identical degrees of
freedom, compare mean monthly error as a fraction of the mean, take the difference — and run it on
the probes.

It is worth having regardless of Part A's outcome, because it is published, peer-reviewed, and has
**no free parameter in the modality decision**. That is exactly the hole WO6a Part A fell into. A
declared threshold is defensible; a published method with no threshold is better.

Predictions to test, both by construction rather than tuning:

- **Timbuktu should come out unimodal.** A truncated 12-month sine can sit flat at zero through the
  dry season and fits a sharp monsoon well; a 6-month curve fits it badly. The model-comparison
  structure immunises against the Fourier-concentration artifact that fools `R_dbl`.
- **George Town should come out bimodal.** The mean is fitted separately and the seasonality
  parameter is a *fraction of the mean*, so a high baseline is factored out before shape is
  assessed — the dilution that produced `R_dbl`'s false negative.

**The limitation that must be tested, because it is Karl's case.** Knoben forces both peaks to
equal amplitude — stated explicitly as necessary to keep degrees of freedom equal between the two
models, without which the comparison is meaningless. The paper is candid that asymmetric bimodal
regimes therefore fail to register, and its Figure 5 walks a transect across East Africa showing
exactly this at 38.5–39° lon.

Mombasa is 235 mm in May against 110 mm in November — asymmetric bimodal, in the region that
transect covers. **Test Mombasa, Guitri and Somalia before adopting anything.** If Knoben calls
Mombasa unimodal, the method is unusable for the cases that matter most here, whatever its other
virtues.

Note for the record: `(a1, b1, a2, b2)` from WO2a is *strictly more expressive* than Knoben's
formulation — it carries amplitude and timing for both harmonics and represents asymmetric bimodal
natively, because asymmetry is the interaction between first and second harmonics. What went wrong
in WO2a→WO3 was deriving separate scalars (`R_std`, `R_dbl`) from the four-number form, discarding
the interaction and recreating the problem the four numbers had solved. Knoben classifies better;
the existing representation represents better. If Part A succeeds, no classifier is needed and the
trade favours the existing representation.

## Part D — The conjunctive instrument, rebuilt on shape correlation

WO6a established that a non-compensatory rule does not starve: ~111 matches at L06 at the tightest
tolerance, 0.68% of corpus, and k=4 does not collapse. What it could not settle was the modality
condition and the band units.

Re-form the instrument with correlation as the shape condition:

- **shape** — profile correlation above some value
- **magnitude** — annual total within a ratio band (e.g. within 1.5×), which is a band on log:
  physically meaningful, scale-stable, and immune to the right-skew that made both tested rules
  behave badly at the wet end (WO6a Part B: ±5 percentile points spans 98 mm to 4,915 mm)
- **temperature** — mean and seasonal range, in absolute degrees, per-variable rather than one rule
  across all

Every condition must be satisfied; none can compensate for another.

Provisos:

- **Per-variable units, not one rule.** WO6a Part B forced a single choice between absolute and
  percentile bands across all variables and found each fails in mirror image. The transform that
  makes a band meaningful differs by variable; choosing per variable costs nothing. Temperature in
  degrees, precipitation as a ratio, shape as a correlation.
- The correlation cut is a declared parameter, chosen and stated — not fitted to the probes. Report
  results at several values and let Karl pick, in the open.
- Report result-set size per probe. Empty is honest scarcity (WO4 Part 2), not failure.
- **This instrument has a name in the literature.** Non-compensatory matching on coarsened
  variables is *Coarsened Exact Matching* (Iacus, King & Porro) — standard in political science and
  epidemiology, with the same selling point: bin widths chosen on substantive grounds and declared,
  rather than emerging from a fitted metric. Worth citing rather than defending from first
  principles, and it brings known properties, including the honest treatment of empty cells. WO4
  Part 3's matched-set instrument sits in the same literature.

## Part E — Hemisphere, as a by-product

Calendar-locked correlation separates Santiago from Split. Correlation maximised over the twelve
circular shifts is hemisphere-blind. **The shift that maximises it is itself informative** — a
shift of 6 means opposite hemispheres with the same shape.

Report both for the probes. If this works, the question that consumed four design rounds and was
retired in WO3 comes back as a by-product of an instrument built for something else, at no cost.

Proviso: keep both, do not choose. They answer different questions — *same year* versus *same
shape of year* — and which one a user wants depends on what they are asking. That is the WO4
lesson about locality restated: report the measurement rather than pick a winner.

---

## Accept gate

**Part A reports the corpus-wide correlation distribution and states plainly whether profile
correlation discriminates; if it does, Parts B–E run and report, with every probe result drawn as
monthly profiles.**

Not a correctness gate. "Correlation does not discriminate" closes this line cleanly and is a
legitimate outcome — report it and stop rather than tuning toward a result.

---

## Out of scope

- Any engine, registry, API, or UI change
- Changing `pre_modality`'s production computation
- Threshold recalibration for existing lenses
- Fixing `climate.precip`'s confirmed compensation defect (separate, and arguably urgent — WO6a
  Part D shows it live in the sandbox)

---

## Worth obtaining before starting

Berghuijs & Woods (2016), *A simple framework to quantitatively describe monthly precipitation and
temperature climatology*, Int. J. Climatology — the parent framework Knoben builds on. Per its
title it covers **temperature** as well, in three parameters with clear physical meaning: mean,
amplitude as a dimensionless multiple of the mean, and phase in months from January.

Two things there matter directly. The amplitude parameter is **dimensionless by construction** —
the scale-free property WO6a Part B spent a whole notebook failing to find. And phase is handled
cleanly and separately from magnitude, which is the separation WO3 asserted and did not implement.

Caution: Knoben reports the seasonality parameter blowing up in arid regions (12.4% of cells exceed
3, predominantly extremely arid). The `THRESH_ARID` gate stays either way.