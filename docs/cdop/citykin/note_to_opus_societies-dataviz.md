# Note to Opus — replacing the Societies-tab PCA cluster option: a hook/no-hook asymmetry

Not a WO. A framing note, drafted at Karl's request, to ground a design conversation before scoping the
next CITYKIN work order: what replaces the legacy PCA "Basin clusters" option in `cdop_pilot.html`'s
`#panel-soc` Societies tab. Background on why that option exists and is currently hidden:
`docs/cdop/pilot/note_societies-tab-vs-wo8.md`. Register entry: `docs/design/deferred_items_register.md`
§ CDOP — Societies tab (pilot legacy). **This stays CITYKIN scope** — Karl's call, 2026-07-30: it isn't a
new phase (`cdop_trace`), it's CITYKIN's next deferred item, so the phase doesn't close yet.

## The core issue: the two wired traits are not symmetric, and that's deliberate

The tab currently treats EA042 (subsistence) and EA034 (high gods) identically — same accordion UI, same
map highlight, same ecoregion breakdown below. That symmetry was fine for a trait-agnostic descriptive
list (ecoregion membership is always computable, regardless of whether a trait has any business
correlating with environment). It stops being fine the moment the replacement is a *targeted* dataviz,
because the two traits differ in a way that matters for what's honest to show:

- **EA042 (subsistence) has a named theoretical hook.** WO8a's own headline: environment sets outer
  bounds on subsistence strategy (water for rain-fed agriculture is a near-hard constraint; temperature a
  soft gradient), it does not determine it. The **Climate envelope** view (aridity × temperature PCoA,
  `wo8a_findings.md` Part B) is the validated, specific axis pair *because there's a prior reason to
  expect those two variables to matter*. Showing that scatter for a subsistence filter is a confirmatory
  illustration of an established relationship.
- **EA034 (high gods) has no such hook.** WO8d didn't test a predicted axis — it explicitly could not,
  because there isn't one. It instance-hunted instead: "is there *any* environmental thread, on *any*
  dimension, more than shared ancestry explains" — no predicted result, no significance floor, by design
  (tracker's Locked decisions: "label family, don't null it; no floor"). That's a different *kind* of
  question than WO8a/8b/8c asked, and it needed a different instrument to ask it.

**Karl's read, which this note adopts:** this isn't a gap to close by finding EA034's hidden theory. Most
D-PLACE traits probably have no a priori environmental hook at all — EA042 and EA034 were chosen, back at
WO8's start, as one of each on purpose (credit where due, if unintentionally prescient at the time). A
good replacement design has to work for **both** kinds of trait, because the tab will likely always be
showing one hook-trait next to one no-hook trait, not because these two happen to be special cases.

## What a "no hook" trait actually gets: refresher on the WO8d cohesion stat

Karl asked for a refresher on this, since it's the one piece of built machinery that already does the
right *kind* of thing for a no-hook trait. It lives in `scripts/cdop/distance_core.py`, built as WO8d's
supporting engine (tests: `tests/cdop/test_distance_core.py`, 10 green).

**The mechanic:**
1. Take the filtered society set (e.g., the 40 EA034 "active-but-not-supporting-morality" societies) and
   a whole-sample **backdrop** (~1,133 basin-linked D-PLACE societies) to answer "compared to what."
2. Standardize (z-score) the backdrop on a chosen **lens** — a named group of environmental variables —
   fitting the mean/std once on the whole backdrop, never refit per subgroup, so every group's number
   lands on the same footing and is comparable across groups.
3. **Cohesion** = mean distance from each society in the (sub)group to that group's own centroid, in the
   lens's z-scored coordinate space. Lower = tighter.
4. Compare the filtered group's cohesion against two baselines, both built by resampling from the same
   standardized backdrop: **fully-random** draws of the same size (loosest bar — "tighter than any random
   k"), and **family-restricted** draws (each society swapped only for another member of its own language
   family — the stricter bar that asks whether tightness survives once you stop letting shared ancestry
   do the work). `percentile_rank()` turns "where does the real group's cohesion fall in that resampled
   distribution" into a single readable number.

**The lenses already defined** (`distance_core.py` `LENSES` dict — this is the part directly relevant to
"the vars we have wired"):

| Lens | Variables | Source |
|---|---|---|
| `water` | `ari_log` (aridity) | — |
| `thermal` | `temperature_annual`, `tmp_seas_amp` | — |
| `overall` | water + thermal together | = the Climate envelope metric, WO8a/8c lineage |
| `terrain` | `relief_range_m`, `landform_position` | WO8c's terrain module, a separate physical question, never folded into `overall` |

WO8d ran this once, hand-scoped to the 40-society EA034 group. **It was never generalized into a
reusable, parameterized instrument** — it's a one-off analysis script, not a live query path.

## What this means for the replacement dataviz: two modes, not one

A single fixed chart is wrong for at least one of the two traits, whichever one you pick:
- Always showing the Climate-envelope scatter over-promises for EA034 — it visually implies a specific
  correspondence exists (aridity/temperature) where none has been established, the same over-promising
  problem the project has already named and corrected elsewhere (Köppen/Knoben naming, the original PCA
  composite this whole effort replaces).
- Always showing a lens-agnostic scan under-serves EA042 — it buries a real, specific, already-validated
  relationship under a "checking everything, nothing predicted" framing built for when nothing is known.

So the design wants (at least) **two display modes, gated by whether the selected trait carries a
declared theoretical hook**:

1. **Hook known → confirmatory view.** Show the specific validated axis pair directly (Climate envelope
   scatter for EA042: each filtered society plotted in aridity × temperature space, same two dimensions
   WO8a validated as the cleanest subsistence separator).
2. **No hook (or not yet established) → exploratory scan.** Karl's phrasing, corrected: **"the dataviz
   that a scan can support"** — not a specific bivariate plot, but a per-lens comparison. For the
   currently-wired lenses (`water`, `thermal`, `overall`/Climate-envelope, `terrain` — i.e., exactly
   climate + terrain, the two families CITYKIN has already built and validated elsewhere), run the
   cohesion-vs-baseline check per lens and show something like a small per-lens bar/dot comparison: one
   row per lens, each showing where the filtered group's actual cohesion falls against its random-draw (and
   optionally family-restricted) baseline distribution — letting the eye spot which lens, if any, shows
   unusual tightness, exactly the reading WO8d did by hand for EA034 (aridity/water looked tight, then
   mostly dissolved once family-restricted). This is the generalization of a one-off notebook script into
   a live, parameterized, any-filter instrument — the actual build item.

**Open design questions this note is surfacing, not resolving:**
- Does EA042 also get run through the scan (as a sanity check — it should light up strongly on
  `overall`/`water`/`thermal`, which would itself validate the scan is measuring something real), or does
  a hook-known trait skip the scan entirely and go straight to its confirmatory view?
- Is the hook/no-hook distinction a per-trait metadata flag someone sets by hand (there are only two
  traits wired right now, so this is cheap), or does it need to generalize to a rule before D-PLACE
  enrichment (the deferred "traits beyond EA042/EA034" item) is ever taken up? Likely answer: hand-flag
  for now, revisit if/when a third trait is wired — don't build a general rule for a two-trait tab.
- `family_restricted_draw_cohesions` needs each society's language family, which D-PLACE already carries
  and WO8d already used — no new data dependency there. Does the scan default to showing both baselines
  (random + family-restricted) per lens, or just random with family-restricted as a drill-down? WO8d's own
  finding (water looked tight against random, dissolved against family-restricted) argues for showing both
  by default — a scan that only checks against random risks reporting exactly the kind of ancestry-
  confounded "signal" WO8d had to correct for.
- Scope for a few days: generalizing `distance_core.py` from "hardcoded WO8d script" to "parameterized by
  (trait, value) → filtered society set" is the actual lift here, not the chart itself — the visualization
  is a straightforward small-multiple bar/dot layout once the per-lens numbers exist.

## What's not in question

This stays CITYKIN scope (Karl, 2026-07-30) — it's the phase's next deferred item, not a reason to close
the phase or open a new one (`cdop_trace` was floated and set aside; the set-first cohesion grammar this
work uses is the same *kind* of thing WO8/TRACE was named after, but scoping it under CITYKIN is Karl's
explicit call, not a grammar-purity argument). The three WH Cities retrieval lenses (precip regime, temp
regime, terrain regime) are complete and not reopened by this note.
