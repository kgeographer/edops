# WO8c — executive summary, plain-English (political complexity / EA033)

*(Companion detail with every number and formal test name: `wo8c_findings.md`. This version is written to
be readable without a statistics background — every technical term is explained the first time it's used.)*

**One line:** Does how politically complex a society is (from stateless bands up to states) track the
climate it lives in? Not really. The direct link is weak — itself the interesting finding, given how
strongly the earlier two traits in this series (subsistence, settlement pattern) tracked climate — and the
tiny residual that survives isn't cleanly interpretable as an independent effect: it's estimated on almost
no independent variation once you account for how tightly political complexity, subsistence, and
settlement pattern overlap in this sample.

## A quick glossary, so the rest of this makes sense

- **R² ("R-squared")** — the share of variation in environment that lines up with the trait being tested,
  on a 0-to-1 scale. Think of it as "how much of the environmental picture this trait explains." 0.02
  means 2% — small. 0.20 would be large, for this kind of data.
- **p-value** — roughly, "how likely is a pattern this strong to show up by pure chance?" Small (under
  0.05) is usually read as "probably not chance." We use p less than R² in this arc, on purpose (see
  below).
- **The permutation test** — instead of trusting a textbook formula, we scramble the data thousands of
  times (shuffle which society has which trait, keeping everything else fixed) and see how extreme the
  real, unscrambled result looks compared to all those random shuffles. If the real result beats 1,999
  out of 2,000 random shuffles, that's about as strong as this method can say "not chance."
- **"Net of X" / "nested"** — the test result *after* accounting for X. "Complexity's signal net of
  subsistence" means: once you already know how the society gets its food, how much *more* does knowing
  the environment tell you about its politics? This is the real question — a raw, unadjusted link between
  complexity and climate would mostly just be re-measuring the (well known) link between farming and
  states.
- **The "cousin control" (family-restricted permutation)** — societies that share a language family also
  share ancestry, and often copied ideas and institutions from each other, not just adapted to similar
  ground independently. So the shuffles above are only allowed *within* language families ("shuffle among
  cousins, not across the whole world") — otherwise a pattern caused by shared history could get
  mistaken for a pattern caused by shared environment.
- **The "noise ceiling" (effect-size floor)** — even pure random noise, run through this same shuffle
  test, will occasionally produce a real-looking number just by chance. We compute that noise ceiling for
  each specific test (the top 5% of what 2,000 random shuffles produce) and check whether the real result
  beats it — not an eyeballed cutoff, a number read straight off the data, and set as a rule *before* we
  looked at complexity's actual number, so we couldn't tune it to get the answer we wanted. **Important
  limit on what this proves:** beating the noise ceiling only tells you a number probably isn't pure
  chance. It does *not* by itself tell you the number is big enough, or clean enough of overlap with other
  correlated traits, to trust as a real independent finding — that's a second, separate bar (see
  "collinearity" below), and this WO's headline result clears the first bar but not obviously the second.
- **"Collinearity" / overlap** — when two or more things you're measuring move together so closely that
  it's hard to tell which one is actually doing the work. If, say, every state-level society in the sample
  also happens to be an intensive-agriculture society, then a test asking "does climate predict complexity,
  once you already know subsistence?" has almost no complexity-without-subsistence cases left to learn
  from — whatever small number comes out the other end is as much a description of *how little
  independent information was available* as it is a description of a real effect.
- **The "spread test" (PERMDISP)** — checks whether groups differ in how *spread out* they are
  environmentally (some groups live in a narrow range of climates, others range widely), separately from
  whether they differ in their *average* climate. A group can look "different" on average purely because
  it's more spread out, not because it's centered somewhere else — this test catches that.
- **The three representative climate variables ("drop-to-representative")** — instead of throwing in every
  correlated climate variable (which double-counts anything that moves together, like rainfall and
  runoff), we picked one clean stand-in per underlying physical thing: **aridity** (dry vs. wet, on a
  log scale), **average temperature**, and **how much temperature swings across the year**.
- **The complexity groups ("complexity3")** — EA033 is a 5-step political-complexity ladder (Acephalous →
  One → Two → Three → Four levels of authority above the local community). For the group-comparison test
  we collapsed it to 3 groups: **stateless** (Acephalous), **intermediate** (One/Two levels), and
  **state-level** (Three/Four levels) — a standard grouping in the literature, decided before we looked at
  results.
- **The settlement-mobility groups ("fixity4")** — from fully nomadic to permanent villages, collapsed
  into 4 groups: mobile, semi-settled, sedentary, complex-permanent (carried over unchanged from the prior
  WO on settlement fixity).
- **"Ruggedness" (the terrain lens)** — how bumpy/mountainous the immediate area right around a society's
  location is, measured directly from elevation data sampled in a small (~4km) box around its coordinates
  — not the terrain of the whole surrounding region, just the society's own neighborhood.

## What we tested

Political complexity — a society's ladder of authority above the local community, from
stateless/acephalous up to full states — against the same three-variable climate picture used in the
prior WOs (subsistence, settlement fixity). The open question: is there anything about environment that
predicts political complexity *specifically*, once you already know how the society farms/forages and how
settled it is? The literature's classic environmental theory (Carneiro's "circumscription": states form
where good farmland is boxed in by desert or mountains, so losers in a conflict can't just walk away) is
about a *relational* property — how boxed-in a place is — which we can't measure yet. So this test could
not check that specific theory either way; it checked whether *climate itself* (not boxed-in-ness) predicts
complexity.

## What we found

1. **The raw link is weaker than expected — the real finding here.** Before controlling for anything,
   complexity's link to climate was already weak (5% share, and not even clearly better than chance on its
   own). That's a genuine surprise — both of the earlier traits in this series (how a society gets food;
   how settled it is) had strong, obvious raw links to climate. Political complexity doesn't. This is the
   headline, not a preamble to what follows.

2. **The high-complexity end of the sample is almost one thing, not many.** States (and near-states) in
   this sample are ~92% concentrated in a single subsistence category (intensive agriculture) and ~92% in
   a single settlement category (villages/permanent settlement). That means once you already know a
   society's economy and settlement pattern, there's very little independent variation *in complexity
   itself* left over for climate to explain — almost by construction, whatever number comes out of a "net
   of subsistence" test at the high-complexity end is going to be small, whether or not political
   complexity has any real independent tie to environment at all.

3. **What survives the controls is small and sits right at that limit.** Once you know how a society
   farms/forages *and* how settled it is, there's a small residual environmental signal specifically tied
   to political complexity — about 1.8% of environmental variation for the group comparison, about 1% for
   the ladder-trend version. It clears its own noise ceiling (survived a deliberate re-run with a
   different random shuffle and five times more shuffles, so it's not a fluke of one particular run) —
   but given point 2, clearing the noise ceiling is a low bar here. **Best read: distinguishable from
   random chance, not distinguishable from the subsistence/settlement overlap.** Not a positive finding
   about political complexity's independent effect on environment.

4. **Settlement pattern doesn't change the picture either way.** We worried going in that "how settled a
   society is" might be *part of the causal chain* from environment to complexity — in which case
   controlling for it could accidentally remove real signal, not just noise. That worry turned out not to
   matter here: adding settlement pattern to the control barely moved the number. There simply isn't much
   room left for any covariate to move it.

5. **Ruggedness (mountainous/broken terrain) shows nothing.** We also tested a cheap, different physical
   question — is the society's immediate terrain rough or smooth — as a partial stand-in for
   circumscription (rough terrain could go either way: it might fragment political units into smaller
   ones, or it might box people in, depending on the specific geography). One version of this test looked
   positive at first, but it was the thinnest possible margin — it evaporated the moment we re-checked it
   more carefully. **Terrain roughness shows no relationship to political complexity, one way or the
   other**, once checked properly. This narrows (doesn't disprove) the terrain question; the real
   circumscription measure — how *boxed in* good farmland is — is a different, more complex thing we
   haven't built yet.

6. **A cross-check on the previous trait, with no change to its conclusion.** Building the "noise ceiling"
   tool for this WO let us go back and check the previous trait (settlement fixity) against its own noise
   ceiling for the first time — that check hadn't existed before. Its leftover environmental signal does
   clear its own noise ceiling, by a wide margin. But per point 3's logic, that's still not the same as an
   independent finding: settlement fixity sits under the same kind of collinearity documented here, so its
   residual is best read the same way — distinguishable from chance, not distinguishable from confound.
   **No change to the earlier write-up's conclusion**; this is recorded as confirmation the noise-ceiling
   tool behaves consistently across traits, not as a correction owed anywhere.

## What it means

- **Political complexity does not show a strong, independently interpretable connection to climate.**
  Subsistence has a real, clean one (WO8a). Settlement pattern and political complexity both have small
  residual signals that survive controls in the narrow "not pure chance" sense, but both sit on top of
  heavy overlap with each other and with subsistence — neither clears the higher bar of being a clean,
  independent environmental effect. The pattern across all three traits so far: the more directly a trait
  is about *making a living from the land*, the more climate explains it, cleanly. Nothing tested past
  subsistence itself has cleared that same clean bar yet.
- **This WO's real contribution is a tool, not a discovery.** The useful result isn't "complexity has a
  small environmental effect" — it's the demonstration that a floor-clears result still needs to be read
  against collinearity before it means anything, confirmed on two traits now (complexity here, fixity on
  the cross-check). That's the discipline the next trait needs even more of.
- **The bar for the next trait (moralizing "high gods") should be the same, or higher.** That trait is
  expected to be even more entangled with political complexity in the literature, so the same collinearity
  concern applies, probably worse.

## Open items for the next step

1. **No correction needed to the settlement-fixity write-up — resolved.** The same necessary-not-sufficient
   logic that tempers this WO's own reading applies retroactively: fixity's residual clears its own noise
   ceiling but sits under the same kind of collinearity, so it stays characterized as small and confounded,
   not upgraded to a real independent effect. Full detail in `wo8c_findings.md`.
2. **The double-check step (re-running with a different random shuffle) should become standard**, not
   optional, for any borderline result going forward — it's what caught the one false-positive-looking
   result in this WO.
3. **Circumscription (the "boxed-in farmland" theory) is still untested** — this WO tested a related but
   different thing (local terrain roughness) and found nothing, which narrows but doesn't close that
   question. Whether this WO's overall result (ambiguous climate signal + clean terrain null) actually
   meets the WO's own stated trigger for building the real "boxed-in-ness" measure is a live call for
   Karl/Opus, not resolved here — full detail in `wo8c_findings.md`.
