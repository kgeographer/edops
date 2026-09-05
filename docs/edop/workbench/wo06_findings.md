# WO06 — Core-share exploration: findings

Notebook: `notebooks/edop/workbench/wo06_core_share.ipynb`. Spec: `docs/design/_workbench/coherence_study_opus.md`.
Run cell-by-cell against the live `cedop` database on 2026-09-05, results reviewed and
discussed at each step. **Notebook-only** — no engine, API, or UI code changed as a result of
this work; the shipped dispersion badge (`coherence_iqr`, `59bfcea`) is untouched.

This document states what was found. It does not propose what to build next — that's a
separate, later decision.

## Setup

- **Scope**: the B1 aggregation path's continuous variables (`aggregate_b1` in `engine.py`) —
  the same set the shipped IQR badge scores today. B1's full continuous set spans bands
  A/B/C/D/E (34 variables); Band D (Anthropocene: cropland/pasture extent, human footprint,
  population density) was excluded as out of scope for an *environmental*-coherence question,
  leaving 27 variables in bands A (terrain), B (hydrology/soils), C (climate), E (coastality).
  `permafrost_extent` (Band C) never returns a valid coherence value in any region (see below),
  so 26 variables actually appear in results.
- **Regions**: all 34 Lovejoy pre-colonial African subregions, minus 3 with zero L6 basin
  coverage (small offshore islands, a known gap from WO05) and 3 more excluded for having
  fewer than 5 basins (Canarias: 2, Gulf Islands: 1, Comoros: 1) — see "Low-basin-count
  regions," below. **28 regions** carried through the full analysis.
- **Level**: L6 basins throughout, matching the shipped Lovejoy-region signature.
- **`permafrost_extent`**: confirmed `outside_active_domain` (the engine's own zero-fraction
  guard) in all 31 resolvable regions — physically sensible, since mainland Africa has
  essentially no permafrost. Not a bug; this variable simply never contributes a score here.

## The statistic tested: core share

**Core share** — the fraction of a region's weighted area falling inside the densest window
of fixed half-width δ on the global percentile (rank) axis, δ ∈ {10, 15, 20}. Computed from
each region's raw per-basin weighted scores (not the API's pre-binned local-range histogram,
which is too coarse for a 1-rank sliding-window scan). Tested against the shipped weighted
IQR (p75−p25), pulled directly from `aggregate_b1`'s own output — not re-derived — so every
comparison is against the actual production number.

## A4 — validity checks (both required before interpreting anything else)

Both passed.

- **Tie-handling**: SQL `PERCENT_RANK()` gives every basin in a tied raw-value group the
  identical score, never spreads them across an interval — confirmed at the most extreme case
  in the dataset (a full 438-basin region, i.e. one entire region, sharing a single raw
  value): zero score-range within that tie block.
- **NaN/NoData**: zero mismatches between raw-NoData basins and NaN scores, across all
  26 variables × 28 regions. A raw `-9999`/`NULL` basin never contributes to either the score
  array or the weight sum.

## A2 — stability across δ

Spearman rank-correlation of each region's variable-by-core-share ordering, compared pairwise
across δ = 10/15/20 (28 regions × 3 delta-pairs = 84 comparisons):

| delta pair | mean ρ | median ρ | min ρ |
|---|---|---|---|
| 10–15 | 0.921 | 0.921 | 0.835 |
| 15–20 | 0.931 | 0.949 | 0.762 |
| 10–20 | 0.842 | 0.864 | 0.673 |

Only 2 of 84 combinations churn (ρ < 0.7), both at the widest delta gap (10 vs. 20): Western
Sahara (0.673) and West Central South (0.674). Ordering is stable enough that δ functions as a
legibility choice, not a source of disagreement; δ=15 (the middle value) was used for all
downstream analysis (A3, Part B).

## A3 — does core share track visual reading? (the acceptance gate)

**Gate result: passed.** Reviewed by Karl directly against the rendered histograms, per the
spec's own acceptance criterion ("Karl's own eye against the disagreement panel, not a
metric").

**The motivating case reproduced.** `pct_sand` (surface) vs. `pct_sand_upstream`, visually
near-identical shapes (one hump with a shoulder trailing right, differing only in how far the
shoulder extends), receive opposite badges in real regions:

| region | variable | core share | IQR | badge |
|---|---|---|---|---|
| Rivers | pct_sand | 0.836 | 12.7 | concentrated |
| Rivers | pct_sand_upstream | 0.716 | 20.9 | spread |
| North Coast | pct_sand | 0.856 | 15.8 | concentrated |
| North Coast | pct_sand_upstream | 0.672 | 29.1 | spread |

Core share tracks the visual similarity between the pair as a smooth gradient; IQR trips a
hard threshold.

**A stronger, unanticipated failure mode: zero-inflation.** The strongest disagreements in
the full dataset (top ~18 of 20, well ahead of the motivating pair) are not skew cases at all
— they share one specific shape: a large point-mass at rank 0 (most basins in the region
genuinely have none of the thing — karst, wetland) plus a real, non-trivial minority of
basins scattered from roughly rank 40 to 100. Examples:

| region | variable | core share | IQR | badge |
|---|---|---|---|---|
| East Coast | karst_upstream | 0.789 | 0.00 | concentrated |
| Kalahari | wet_pct_grp1_upstream | 0.816 | 0.00 | concentrated |
| Kalahari | wet_pct_grp1 | 0.831 | 0.00 | concentrated |
| Central Savanna | karst | 0.846 | 0.00 | concentrated |
| Horn | wet_pct_grp1 | 0.855 | 0.00 | concentrated |

In every one of these, IQR reads exactly **0.00** — not just low, degenerate zero — while
core share reads 79–89%, i.e. "most, not all." The mechanism: once the tied mass at one raw
value (typically zero) exceeds half a region's weight, both the 25th and 75th percentile land
on that same tied value by construction. IQR is then structurally blind to whatever the
remaining minority looks like, however large or real it is. This is a cleaner, more extreme
version of the skew problem than the original motivating example — there, IQR was merely too
generous; here it reports a number (0.00) that actively asserts uniformity a real minority
contradicts.

**Vocabulary note.** Two distinct terms apply to this pattern and are worth keeping separate
in any follow-on discussion: **zero-inflated** is the standard statistical term for the
*mechanism* — a point-mass at one value mixed with a distinct non-zero population.
**Long-tailed** is a closer lay description of *what the residual looks like*, but is
technically imprecise for most of these specific cases: the residual in the histograms is
typically a scattered comb of similarly-sized bars across a wide range, not a smoothly-decaying
tail. The observation from inspecting the panel: **the binary concentrated/spread vocabulary
is missing a category**, not simply misapplying the two categories it has. A big point-mass at
rank 0 is not, on its own, a problem for IQR — see the control-panel counter-examples below;
the problem is specifically a big point-mass *plus* a substantial separate minority.

**Control panel (statistics agreeing).** Genuine agreement examples confirm the above
distinction rather than contradicting it:

- Nile Valley/`aridity` (core 100%, IQR 2.3), Nile Valley/`precip_yr` (core 100%, IQR 2.5),
  Western Sahara/`precip_yr` (core 100%, IQR 3.1) — these also show a large spike at rank 0,
  but with **no substantial residual minority** (Western Sahara's near-total lack of
  precipitation is physically real, not zero-inflation hiding a wetter minority). Both
  statistics correctly read these as tight.
- North Coast/`temp_yr`, `temp_yr_upstream` — a genuine single hump not anchored at zero.
  Both statistics agree cleanly.
- Five genuinely broad cases (Rivers/`wet_pct_grp1_upstream` and `wet_pct_grp2_upstream`,
  Nile Valley/`pct_clay_upstream`, Southeast/`wet_pct_grp2_upstream`, Northwest/`elev_min`) —
  IQR 71–91, core share 40–48%, both statistics agree these regions are genuinely dispersed.

So the mere presence of a point-mass at zero is not diagnostic; it's the *combination* with a
real separate minority population that IQR cannot see and core share can.

## Part B — region-level profile (exploratory, no threshold adopted)

**Provisional cutoff used: core share ≥ 0.5 at δ=15.** This threshold discriminates weakly —
scores across the 28 regions range only 0.769 to 1.000 (20/26 to 26/26 variables clearing it),
with 5 regions at a perfect 26/26 (Madagascar, Southern Grasslands, West Central North,
Central Sahara, Western Sahara) and 2 more at 24/24 with a smaller variable count (East
Central, Forests). At this threshold, nearly every declared Lovejoy region reads as
"environmentally coherent" on nearly everything; the cutoff was not tuned or re-run at a
higher value as part of this study.

**Region-size effect: none found.** Spearman correlation between `n_basins` and coherence
count: ρ = −0.091 (p = 0.65, raw count), ρ = −0.175 (p = 0.37, normalized percentage). Neither
significant; both negligible. The two largest regions in the dataset (Western Sahara, 434
basins; Central Sahara, 438 basins) both score a perfect 26/26; the single worst-scoring
region (Central Savanna, 20/26) is mid-sized at 192 basins. Region size, at the scale present
in this dataset (25–438 basins), does not predict coherence in either direction.

**Which dimension carries the coherence, and which doesn't.** By band, mean share of regions
clearing the cutoff: Climate (C) 98.8%, Terrain (A) 93.1%, Hydrology/soils (B) 89.0%,
Coastality (E, one variable) 88.5%. The four lowest-scoring individual variables are all
wetland-percentage measures: `wet_pct_grp2_upstream` (67.9% of regions coherent),
`wet_pct_grp1_upstream` (71.4%), `wet_pct_grp1` (75.0%), and `karst` (88.0%) — the same
variable family that dominated the A3 zero-inflated disagreement cluster, now independently
confirmed (via the correctly-computed core-share statistic, not the flawed IQR badge) as the
dimension along which these regions most often fail to hold together. The regions×variables
heatmap shows this isn't spread evenly: the weak cells cluster specifically in a group of
savanna/coastal regions (Southern Savanna, Western Bight, East Coast, Western Savanna, Central
Savanna), not scattered at random across the continent.

`karst`, `karst_upstream`, and `dist_sink` are each missing from a handful of regions
(`n_regions` 25 or 26 of 28, rather than 28) — the same `outside_active_domain` mechanism as
`permafrost_extent`, just not total. Not an error; these are cases where a region has too
little variation in that variable to score it at all.

## Two implementation issues found and fixed (notebook-internal, no wider effect)

Neither affects any of the findings above; recorded because they're the kind of thing that
would silently corrupt results if repeated elsewhere.

1. **Pandas Series comparison requires identical indexing.** An early NaN/NoData check
   compared two columns pulled from different DataFrames with bare `==`; pandas raises rather
   than aligning when the indices aren't identically labeled (same values *and* order) — fixed
   by building the pair into one `pd.DataFrame({...})` first, which does align.
2. **PyCharm's cell output can render zero text when a `print()` precedes a matplotlib figure
   in the same cell** — not a scrolling issue, not stale/cached output (confirmed via a fresh,
   fast execution with legitimately no visible text at all). The documented project convention
   ("print immediately before `plt.subplots`") was insufficient on its own in this instance;
   splitting the stats-printing code and the figure-drawing code into two separate cells was
   the fix that actually worked, plus writing the numeric result to a small text file as an
   independent, display-independent record.

## Summary

- Core share passed its acceptance gate: it tracks visual reading of the underlying
  distributions where the shipped IQR-based badge does not, confirmed against both the
  original motivating case and a wider, independently-discovered zero-inflation failure mode.
- That zero-inflation failure mode is arguably a cleaner demonstration of the underlying
  problem than the original motivating example (IQR reports a degenerate 0.00, not merely a
  too-generous number), and it is common in this dataset — 19 of the top 24 disagreements were
  this shape, driven by variables (karst, wetland-percentage) that are also independently the
  weakest-coherence dimension in the Part B region-level profile.
- The binary concentrated/spread vocabulary appears to be missing a category for this shape,
  not simply misapplying the two it has — a big point-mass at one value is not itself a
  problem (see the control-panel counter-examples); it's specifically a big point-mass
  combined with a real separate minority that breaks IQR.
- Low basin-count regions (n=1, n=2 observed here) produce degenerate, uninformative results
  for both statistics — a distinct issue from the disagreement question above, surfaced
  independently twice in this run.
- No significant relationship was found between region size and coherence in this dataset.
- The provisional core-share cutoff (0.5) used for Part B does not discriminate strongly
  between regions; a real threshold, if one is wanted, was not derived here.
