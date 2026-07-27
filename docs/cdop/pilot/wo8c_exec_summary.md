# WO8c — executive summary, plain-English (political complexity / EA033)

*(Companion detail with every number and formal test name: `wo8c_findings.md`. This version is written to
be readable without a statistics background — every technical term is explained the first time it's used.)*

**One line:** Does how politically complex a society is (from stateless bands up to states) track the
climate it lives in? Mostly no — but a small, real piece of it does, even after accounting for how the
society makes its living and how settled it is. That's a genuine, if modest, result — the arc's first
"yes" on a trait nobody could pre-check the answer to.

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
  each specific test (the top 5% of what 2,000 random shuffles produce) and only call a result "real" if
  it beats its own noise ceiling — not an eyeballed cutoff, a number read straight off the data. Crucially,
  this ceiling was set as a rule *before* we looked at complexity's actual number, so we couldn't tune it
  to get the answer we wanted.
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

1. **The raw link is weaker than expected.** Before controlling for anything, complexity's link to climate
   was already weak (2% share, and not even clearly better than chance on its own). That's a real surprise
   — both of the earlier traits in this series (how a society gets food; how settled it is) had strong,
   obvious raw links to climate. Political complexity doesn't.

2. **But something small and real survives, net of subsistence and settlement together.** Once you know
   how a society farms/forages *and* how settled it is, there's still a small extra environmental signal
   specifically tied to political complexity — about 1.8% of environmental variation for the group
   comparison, about 1% for the ladder-trend version. Small, but it cleared its own noise ceiling, and
   held up when we deliberately re-ran the test with a different random shuffle and five times more
   shuffles to make sure it wasn't a fluke of one particular run.

3. **Settlement pattern doesn't explain it away.** We worried going in that "how settled a society is"
   might be *part of the causal chain* from environment to complexity (rather than just a confusing extra
   factor) — in which case controlling for it could accidentally remove real signal, not just noise.
   That worry turned out not to matter here: adding settlement pattern to the control barely changed
   anything. Whatever complexity's small environmental signal is, it doesn't run through settlement
   pattern.

4. **Ruggedness (mountainous/broken terrain) shows nothing.** We also tested a cheap, different physical
   question — is the society's immediate terrain rough or smooth — as a partial stand-in for
   circumscription (rough terrain could go either way: it might fragment political units into smaller
   ones, or it might box people in, depending on the specific geography). One version of this test looked
   positive at first, but it was the thinnest possible margin — it evaporated the moment we re-checked it
   more carefully. **Terrain roughness shows no relationship to political complexity, one way or the
   other**, once checked properly. This narrows (doesn't disprove) the terrain question; the real
   circumscription measure — how *boxed in* good farmland is — is a different, more complex thing we
   haven't built yet.

5. **A side discovery: the previous trait's "no effect" call needs revisiting.** Building the "noise
   ceiling" tool for this WO let us go back and properly check the previous trait (settlement fixity)
   against its own noise ceiling for the first time — that check hadn't existed before. It turns out
   settlement fixity's leftover environmental signal, which the earlier write-up called negligible, was
   actually real by a wide margin (3× its own noise ceiling, not close). That's a correction owed to the
   earlier document, held for a deliberate decision on how/when to apply it — not silently changed.

## What it means

- **Political complexity has a real but modest independent connection to climate** — smaller than
  settlement fixity's true signal (once that gets corrected), which is itself smaller than the very strong
  subsistence-climate link found earlier in this project. That's a sensible, coherent picture: the more a
  trait is directly about *making a living from the land*, the more climate explains it; the further a
  trait gets from that (settlement pattern, then political structure), the weaker — but not zero — the
  direct climate connection.
- **This is the arc's first genuinely positive result on a trait nobody could pre-check.** The first two
  traits tested were chosen because we already had a strong hunch about the answer (a "calibration"). This
  one wasn't, and it came back with a real, if small, signal — a legitimate finding, not an artifact,
  because we built the tools to catch artifacts (the noise-ceiling rule, and a second check with different
  random shuffles) before trusting it.
- **The bar for the next trait (moralizing "high gods") should be the same, or higher.** That trait is
  expected to be even more entangled with political complexity in the literature, so the same collinearity
  concern applies, probably worse.

## Open items for the next step

1. **Decide how/when to correct the settlement-fixity write-up** — the earlier "no real independent
   effect" conclusion doesn't survive the same check applied here. Full detail in `wo8c_findings.md`.
2. **The double-check step (re-running with a different random shuffle) should become standard**, not
   optional, for any borderline result going forward — it's what caught the one false-positive-looking
   result in this WO.
3. **Circumscription (the "boxed-in farmland" theory) is still untested** — this WO tested a related but
   different thing (local terrain roughness) and found nothing, which narrows but doesn't close that
   question. Building the real measure is flagged as future infrastructure, not urgent right now since
   nothing here specifically calls for it.
