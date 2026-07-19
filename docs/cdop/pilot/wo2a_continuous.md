# WO2a addendum — Continuous harmonic representation: test before commit

**Status:** draft for review. Notebook-only. No registry writes, no API changes, no UI changes.
**Prior:** `wo2_findings.md` (Parts A–C complete; Part B4 recommends Option B).
**Purpose:** test whether the continuous form of Option C makes the classifier unnecessary for
similarity, before WO3 commits to Option B.

This addendum does not dispute WO2's empirical work. The separation is real, the geography is
physically motivated, and `THRESH_ARID` is well-evidenced. What it questions is the decision to
*discretize* that structure before feeding it to a distance metric.

---

## Why reopen

Three objections to Option B, which are one objection at three levels.

**1. It puts a discontinuity inside a distance metric.** `seas_phase_offset_v2` branches on
`R_dbl ≥ 0.30`: basins at 0.299 and 0.301 get different formulas and can land months apart.
Distance metrics assume small changes in the world produce small changes in the number. This
breaks that at a line with no physical meaning — and breaks it invisibly, as noise near the
boundary rather than as a conspicuous wrong answer.

**2. `same_modality` makes modality a filter rather than a dimension.** The engine would be
deciding what counts as comparable. That conflicts with the locked principle that the engine
resolves and serves rather than interprets, and it cannot be labelled honestly: "5 most similar"
would silently mean "5 most similar among the 386 we classed as like you."

**3. Two of the three thresholds are not supported the way the third is.** `THRESH_ARID` sits in
a genuine trough — move it ±25 mm and nothing changes. `THRESH_DBL = 0.30` was set so that the
probe cities that motivated the investigation land on the expected side, and WO2 already records
that it misses Vietnam, Thailand, the Philippines, and northern Australia. `THRESH_STD = 0.40`
is "retained for continuity" — inherited rather than justified — and is what places Split and
Rome in the `aseasonal` bin that WO2 concedes is wrong in spirit.

**The observation that changes the cost estimate:** `R_std` and `R_dbl` *are already* the first
and second harmonic amplitudes, normalized by the mean. `phi_std` and `phi_dbl` are their
phases. The notebook has already computed every component of the two-harmonic model. Option C is
not a redesign of what Option B builds — it is the same quantities kept whole instead of
thresholded. WO2's "2–3 sessions" estimate prices a rebuild that does not need to happen.

---

## The correction Option C needs

WO2 B3 specifies Option C as four features `(A₁, φ₁, A₂, φ₂)`. Raw phase angles cannot enter a
Euclidean or Mahalanobis distance: month 11.9 and month 0.1 are adjacent in the world and
maximally distant in the number. Use the Cartesian components instead:

```
denom = Σ p_m                       (annual total)
θ_m   = 2π·m/12                     (m = 0..11)

a1 = Σ p_m·cos(θ_m)  / denom        b1 = Σ p_m·sin(θ_m)  / denom
a2 = Σ p_m·cos(2θ_m) / denom        b2 = Σ p_m·sin(2θ_m) / denom
```

Identities worth asserting in the notebook as a correctness check:
`R_std = √(a1² + b1²)` and `R_dbl = √(a2² + b2²)`. If those don't hold to floating-point
tolerance, something is wrong before anything else is tested.

Distance in `(a1,b1)` combines cycle strength and cycle timing in one continuous quantity: same
amplitude with opposite phase reads far apart; same phase with different amplitude reads
moderately apart. No wraparound, no threshold, no class.

---

## Parts

### Part A — Compute and verify

Compute `a1, b1, a2, b2` and `log(annual total)` for all 16,397 L06 basins (and L08 if the index
makes it cheap). Verify the identities above against the existing `R_std` / `R_dbl` columns.

Proviso: the shape features are already normalized by total, so magnitude enters only through the
separate total feature. Keep that separation explicit — *how much* and *when* are different
questions and should be separately weightable.

### Part B — Does separation survive without classification?

Reproduce WO2's probe result using distance in the continuous space alone, with no modality
step anywhere:

- Mombasa's nearest neighbours should be bimodal-tropical, not European temperate
- Augsburg's should be temperate distributed
- Timbuktu's should be single-peak monsoon
- Split and Rome should find each other rather than dissolving into a 7,885-basin `aseasonal`
  cloud

The Split/Rome case is the sharper test. It is not a bimodal problem at all — it is the
`THRESH_STD` problem — and it is the one where the continuous representation should visibly
outperform the classifier rather than merely tie it.

### Part C — Held-out validation

WO2's thresholds were tuned on the cases that prompted the investigation. This part uses cases
that were not.

Assemble a held-out set from independent climatology — known ITCZ double-passage and
double-monsoon regions (Vietnam, Thailand, the Philippines, northern Australia, Kerala, the
Guinea coast, Pacific-coast Mexico) — chosen and written down *before* looking at the numbers.
Then ask: does the continuous representation place them near Mombasa and near each other,
without any threshold being adjusted?

WO2 records that the thresholded version misses several of these because their peaks are not
exactly six months apart or their baseline rainfall is high. The continuous form has no such
tuning point, so this is a genuine discriminating test rather than a confirmation exercise.

Proviso: write the expected set down first, in the notebook, before computing. If the list gets
edited after seeing results, the validation is worthless and the notebook should say so.

### Part D — Phase relation, continuously

Replace the scalar precipitation-minus-temperature offset with a continuous representation of
the relation between the two annual harmonics. Requirement: defined for every basin, no branch,
no wraparound.

Provisos:

- Where either cycle is weak the relation is genuinely unstable. The aim is not to hide that but
  to make it *visible as small amplitude* rather than buried inside a threshold — basins with
  weak cycles should cluster together on that basis rather than being assigned arbitrary angles.
- Whether amplitude belongs in the phase lens or stays in the precipitation lens is a
  one-physical-question call. Recommend one; don't assume.
- Confirm the Mediterranean contamination path documented in WO2 A7 is actually closed, not
  merely moved.

### Part E — The compared dimension, drawn

Prototype the display that would have caught this in one second.

For a similarity result under a precipitation lens, render a twelve-bar monthly profile beside
each neighbour, query at the top, shared scale. Mombasa's twin peaks against Augsburg's flat
profile is the whole WO1 failure, legible without numbers or caveats. When the fix works, five
profiles that all show twin peaks are self-evidently right.

Notebook prototype only — small multiples, static. UI implementation is out of scope.

Proviso worth testing here rather than asserting: whether the glyph should show the raw monthly
values or the reconstructed two-harmonic fit. Raw is honest about the data; the fit is honest
about what the metric actually compared. They differ, and the difference is informative.

**If this works, it generalizes.** A lens definition would then have three parts rather than two
— variables, metric, and glyph — so that every lens ships with a visual signature of what it
compares. That is the structural answer to a surface that drew the truth on one screen while a
scalar lied on another.

---

## Accept gate

**The continuous representation reproduces WO2's probe separation with no classification step,
and additionally recovers held-out cases the thresholded version misses.**

If it reproduces but does not improve, Option B is vindicated and WO3 proceeds as written — that
is a real possible outcome and should be reported plainly, not argued around.

If it improves, WO3 changes: `climate.precip` takes the continuous features, `climate.phase`
takes the continuous relation, `same_modality` is dropped, and `pre_modality` survives as a
display variable only.

---

## What `pre_modality` is for either way

Keep it. It is genuinely useful as an Explorer categorical layer, as vocabulary for the
narrative generator ("rainfall peaks in May and November"), and for describing the population in
writing. The claim here is only that it should not enter a metric or filter a candidate pool.

The general form, which is the existing architecture applied one level down: **compute continuous
in the engine, classify at the surface.** A class assigned in the engine is irreversible and
propagates silently. A class assigned at the surface is reversible, labelled, and available to be
doubted by the person looking at it — which is where the doubt belongs, since the lines are ours
and the ground does not honour them.

---

## Carried forward regardless of outcome

- **No threshold inside feature construction.** Thresholds are display-layer objects. A branching
  feature formula means the metric built on it is lying somewhere.
- **Circular quantities enter as sine/cosine pairs, never as angles.** This recurs immediately:
  slope aspect is circular and is a Terrain lens candidate.
- **Distinguish natural boundaries from imposed ones.** Test by stability — move the line 10% and
  see whether the counts move. `THRESH_ARID` passes; `THRESH_DBL` does not. A threshold at a real
  gap is a finding; a threshold in a continuum is a decision, and decisions need a named decider.
- **Population share is the wrong exposure metric.** "2.4% of basins, 3 of 254 cities" reads as
  negligible, but those basins are East Africa, the Sahel margin, and South Asia — where D-PLACE
  societies concentrate. Exposure should be counted in units of use, not units of inventory.
- **The `aseasonal` label needs renaming whatever happens.** It currently holds relentlessly wet
  equatorial, temperate distributed, and genuinely seasonal Mediterranean. It appears in
  generated prose. WO2 already flags this; it should not wait on the harmonic question.

---

## Out of scope

Registry changes, threshold recalibration, narrative-generator repair, UI work, L08 rebuild.
All belong to WO3, whose shape this addendum exists to determine.
