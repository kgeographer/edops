# WO6 status — plain-English summary + Karl's reframe (for the WO author)

**From:** Claude Code (execution session), 2026-07-22
**For:** Opus (WO author), passed along by Karl with `wo6a_findings.md` and `wo6b_findings.md`
**Purpose:** a readable status on where the similarity work actually landed, plus a target
reframe from Karl this session that changes what WO6c should build.

---

## What WO6b did, in plain terms

**The idea.** Every past attempt squashed a basin's twelve monthly rainfall numbers down into two
or three summary numbers and compared those. They kept failing, and the failures were always in the
squashing. So this time we didn't squash — we compared the whole twelve-month curve directly, using
ordinary correlation ("how alike are these two shapes").

**It works.** Ask "what rains like Timbuktu?" and you get Sahel monsoon basins. Ask about George
Town and you get twin-peaked tropical basins — the exact case the old measure had labelled "no
seasons" and completely missed. Every probe returned rainfall shapes that look right when you draw
them. No equivalent of the old Mombasa-returns-Jerusalem failure anywhere.

**The genuinely new result:** modality falls out for free. We never told the correlation anything
about "one rainy season vs two." Yet when you ask what's like a two-season place, ~95%+ of the
answers are also two-season places. The two-vs-one-rainy-season question — which three previous work
orders spent enormous effort trying to classify with a threshold nobody could pin down — simply
dissolves. You don't classify it; it emerges from comparing the shapes.

**What correlation can't do, by design:** it's blind to amount. A place with 1000mm and a place with
100mm can have the identical *shape* of year. So the design is a checklist: to count as similar, two
basins must match on shape **and** total rainfall **and** temperature — every box, no trading one
off against another. Different places lean on different boxes (distinctive rainfall shape pins one
place; a brutal temperature swing pins Yakutsk), and every box earns its keep for some place.

**What was still unsettled at the end of WO6b** (small, relative to the above):
- "How strongly seasonal is this place" as a single continuous number resisted — two ways to
  measure it, each broke in an opposite direction. Works as a checklist band, not as a standalone
  score.
- "Which season is the rainy one relative to the warm season" works cleanly for one-season places
  and is undefined for two-season places.

**It also corrected a mistake in WO6a** — its star example (Somalia) turned out to be near-desert
(87mm/yr) and shouldn't have been in the analysis; the real culprit was a different, well-watered
kind of place. WO6a's conclusion survived, its evidence was wrong, both files now corrected.

---

## Karl's reframe of the target (this session, after reading the above)

Karl's read on the two "unsettled" items — and it dissolves most of them, because it says WO6b was
answering harder questions than EDOPS actually needs:

1. **"How strongly seasonal" is probably not a question EDOPS needs to answer.** What Karl is after
   is the **discrete** version: *is it seasonal or aseasonal, and if seasonal, 1 or 2 rainy
   seasons?* Not a continuous amplitude — a small class label.

2. **Combining precipitation with temperature wants a simple categorical answer:** *is it warm/wet,
   cool/dry, or the reverse* — i.e. does the rain come with the heat or against it.

Both are discrete classifications, not continuous measures.

### What that does to the open items

- **The continuous amplitude scalar that "resisted" is no longer needed.** If the target is
  {aseasonal / 1-season / 2-season}, WO6b already delivers it, three independent ways: the aseasonal
  gate (a flatness cut), and 1-vs-2 emergent from correlation (Part B, strong), independently
  confirmed by Knoben's model-comparison (Part C) and by peak-counting. The hard part (a single
  "how seasonal" number) was never required. **This open item closes.**
  - One honest caveat to hand Opus: the seasonal/aseasonal *boundary* has no natural cut in the data
    (the flatness histogram is a smooth plateau, no trough) — so wherever it's drawn is a declared
    convention. It separates the real cases correctly (Tennessee aseasonal, George Town seasonal),
    but it should be stated as a convention, not a discovered line.

- **The precip-vs-temp phase question is exactly Karl's "warm/wet vs cool/dry."** WO6b's `s_d`
  already answers it for one-season places (rain-with-warmth ≈ warm/wet; rain-against-warmth ≈
  Mediterranean cool-wet/warm-dry). Its only failure was undefined-for-bimodal — and that matters
  less for a coarse warm/wet-vs-cool/dry label than for a precise phase.

### The precip-temp category — verified (Cell 19), not speculative

The precip-temp category is answerable **more simply and without the bimodal failure**, by the same
tool that made WO6b work: **correlate the twelve-month precipitation curve directly against the
twelve-month temperature curve.** One number in [−1, +1]:

- strongly + → rain falls with the heat (**warm/wet**; the dry season is the cool season)
- strongly − → rain falls against the heat (**cool/wet, warm/dry** — the Mediterranean/Santiago case)
- near 0 → no clean coupling

**Verified against `s_d` and against the bimodal cases it exists to cover (Cell 19):**

- **Sign agreement is 7/7** on every probe where `s_d` is also defined — it is the same signal,
  obtained without the sine fit. Santiago −0.894 (Mediterranean, matching `s_d`=+5.20); Augsburg,
  Tbilisi, Yakutsk strongly positive (rain-with-warmth).
- **It is defined for the 2,694 bimodal basins where `s_d` is not**, with a full real spread
  (−0.99…+0.98), not a degenerate collapse. The acid test passed.
- **Corpus shares are sane:** 55% warm/wet, 17% Mediterranean, 28% weak/none.
- **The "weak/none" middle band is correct behaviour, not a gap.** George Town (−0.25), Mombasa
  (−0.16), Somalia (+0.28), Timbuktu (+0.38) land there — and they should: a basin wet year-round,
  or one whose two rainy seasons straddle the temperature peak, genuinely has no "wet season vs warm
  season" relationship to report. The measure abstains exactly where the categorical question is
  ill-posed, rather than inventing an answer.

So for the reframed `{warm-wet / cool-dry / neither}` target this is a single fit-free number,
defined everywhere, agreeing with the principled measure where both exist, and honestly reporting
"no clean answer" where there isn't one — a better fit to a coarse categorical question than `s_d`.
Cell 19 in `wo6b_compare_curves.ipynb`.

**Net for WO6c:** if the target is the two small classifications above — {aseasonal / 1 / 2} and
{warm-wet / cool-dry / neither} — WO6b's machinery already reaches both, and the one genuinely open
piece is whether direct precip×temp correlation is the clean way to the second. That is a much
smaller and more tractable brief than "build a continuous similarity measure."
