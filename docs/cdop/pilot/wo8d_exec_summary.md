# WO8d — executive summary, plain-English (the high-gods look / EA034)

*(Companion detail with every number and test name: `wo8d_findings.md`. This is an exploratory "look,"
not a confirmatory test — there was no predicted result and no significance gate going in; the goal was
to see what's there and report it honestly, whichever way it came out.)*

**One line:** Of the 40 societies coded as having "active, but not supporting morality" high gods, most
of whatever environmental similarity they share traces back to two large, related lineages sitting in
consistent climates. Outside that story: a strong cross-family exception (three unrelated Siberian
peoples, the tightest group in the whole set) worth a closer look, and — the more interesting open
question — roughly a third of the 40 are explained by neither ancestry, climate, nor proximity to each
other at all.

## A few terms, quickly

- **Cohesion** — how tightly packed a group is in "climate space" (aridity, temperature, seasonal swing).
  Lower number = tighter group.
- **Backdrop** — the whole comparison population (~1,133 societies), used to answer "tight *compared to
  what*." Without it, "these 40 are tight" is meaningless.
- **The "random cousins" check** — a stricter comparison: instead of comparing the real group to any
  random 40 societies from anywhere, this version only swaps each society for another member of its *own*
  language family. If a group looks tight against a random draw but stops looking tight against this
  stricter check, that means the tightness is basically explained by which families happen to be in the
  group, not by anything beyond that.
- **Ordination (PCoA)** — a 2D map of "climate space," built so you can see at a glance who's near whom
  environmentally.

## What we did

Took the 40 basin-linked societies coded with this specific high-gods trait, mapped them in climate
space alongside all ~1,133 comparison societies, colored them by language family (not removed as a
confound — the whole point was to see transmission and independent recurrence side by side), and asked:
are these 40 environmentally distinctive as a group, on which specific climate dimensions, and does any
apparent pattern trace back to shared ancestry or hold up independent of it?

## What we found

1. **One family is over a third of the whole group.** Fifteen of the 40 societies — more than a third —
   belong to a single African language family (Atlantic-Congo, broadly Bantu-related). That's not a small
   detail; it's the single biggest fact for reading everything else.

2. **That family really is environmentally tight — genuinely, not just numerically.** Those 15 societies
   are tighter in climate space than essentially any random draw of 15 societies from anywhere in the
   world. A second, smaller family (4 East African Nilotic societies) shows the same pattern.

3. **But a third family shows the opposite — shared ancestry proved nothing there.** Three Sino-Tibetan-
   language societies (from the Northeast India/Myanmar region) are genealogically related to each other
   but sit no closer together in climate space than three random strangers would. Family membership alone
   doesn't guarantee environmental similarity — it depends on the specific lineage.

4. **Once you account for those big families, nothing else holds up.** Testing the whole group of 40
   against climate variables one at a time (rainfall/aridity, temperature, seasonal swing, terrain
   roughness), there's a real-looking signal on the rainfall/aridity dimension — but it disappears almost
   entirely once you control for which families are in the group. In other words: the "these 40 share an
   environment" impression is mostly "one big family shares an environment," not something broader.

5. **A strong exception: three unrelated peoples across Arctic Siberia form the single tightest group in
   the whole dataset.** Chukchi, Yakut, and Yurak-Samoyeds speak three completely different languages with
   no shared ancestry, yet they're closer together environmentally than any other group in the set —
   tighter even than the two large related African families above. This is either cultural contact across
   a shared harsh environment, or independent adaptation to the same conditions — the data can't
   distinguish those two, and with only 3 societies the statistical confidence is limited. But the raw
   phenomenon — three unrelated peoples, same environment, same trait, tightest cluster in the set — is
   exactly the "similar culture despite no shared ancestry" pattern this look was built to catch, and it's
   the strongest lead worth following up.

6. **The best evidence the method is measuring something real: a validation check we didn't plan for.** As
   a sanity check (not part of the group being tested), we located the Hopi in the same climate-space map
   and looked at their nearest neighbors. Most were, as expected, other closely related Uto-Aztecan-
   speaking peoples of the American Southwest — but two of the ten nearest neighbors were Hano (a
   Tewa-speaking village that historically settled *among* the Hopi villages) and Navajo (whose land
   surrounds the Hopi reservation today) — both well-documented real cases of cultural contact between
   unrelated languages sharing the same place. Neither fact was fed into the analysis; they emerged purely
   from climate data lining up with known geography and history. This is the strongest single piece of
   evidence in the whole look that the method is doing what it claims — it doesn't need any of the
   religion/culture findings above to be true to stand on its own, and it's what makes the rest of this
   summary worth trusting.

## What it means

- **The headline isn't "no environmental thread" — it's "we explained what's explainable, and what's left
  over is the more interesting question."** Two big families account for most of the whole-group
  environmental impression; one strong cross-family exception (the Siberian trio) stands out as a real
  convergence case; and about a third of the 40 — roughly 14 societies — share the trait but aren't
  explained by family, by climate as a whole group, or by being near each other. That unexplained group is
  not a loose end to file away — it's the natural target for the next question (see below).
- **A map of where these 40 societies actually sit in the world** (built earlier, independent of this
  analysis) shows real geographic clusters — dense in Sub-Saharan/Central Africa, a thin line along
  Arctic Siberia, scattered through the Americas — matching what the statistics found. The dispersion
  itself, across quite different climate zones, is a documented, real pattern worth keeping regardless of
  which explanation (or combination of explanations) eventually accounts for it.
- **Not every "same family" pairing means "same environment"** — the Sino-Tibetan case is a useful
  reminder not to over-read family coloring as automatically meaningful.

## Open items for the next step

1. **The unexplained ~14 societies are the real next question, and the most important item here.** This
   look was built to find what environment (and language-family ancestry) *does* explain; the flip side —
   what it *can't* explain — turned out to be a well-defined, nameable group of societies (Wayuu, Mapuche,
   Bribri, Aztec, !Kung, Semang, Bhil, and others), not scattered noise. The natural follow-up is a
   different kind of question than this WO asked: does this specific set of societies share *anything* —
   a different environmental measure, some other cultural trait, or genuinely nothing at all (which would
   itself be a real and informative answer)?

   One honest limit on this, worth keeping in mind: our best ancestry check (language family) only sees
   back a few thousand years. A group "unexplained by environment and language family" could still share
   deeper ancestry or undocumented historical contact that this project simply has no way to detect yet.
   So the right way to describe this group is "unexplained by the environment and shallow-ancestry checks
   we have" — not "unexplained by everything ordinary that could account for it."

2. **The Siberian trio is the strongest lead worth a domain-expert look** (independently documented contact
   between Chukchi, Yakut, and Yurak-Samoyeds peoples?) before treating it as anything more than a
   suggestive pattern.
3. A bug was caught mid-analysis where a family-lookup accidentally queried the *entire* worldwide
   database instead of just the 40 being studied — caught quickly because the numbers didn't match a
   cross-check, fixed, and re-verified, then double-checked a second way (plotting where each group
   actually sits, not just counting how many members it has). Noted for the record, not because it
   affects any number in this summary (all final numbers above are post-fix and position-verified).
4. A more rigorous version of an older, now-retired "climate zone tally" view (the kind that shows "10 in
   Boreal, 9 in Steppe," etc., using proper current climate-classification machinery instead of the
   retired one) was discussed as a possible follow-up visualization but not built this round.
