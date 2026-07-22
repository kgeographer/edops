# WO6a findings — Non-compensatory similarity: notebook

**Work order:** `docs/cdop/pilot/wo6a_notebook.md`
**Branch:** `cdop_wo6` (cut from `cdop_pilot`, after merging `cdop_wo5`)
**Notebook:** `notebooks/cdop/wo6a_noncompensatory.ipynb`
**Date:** 2026-07-22
**Status:** All parts (A–D) run and closed.

---

## Instrument under test

Non-compensatory (Chebyshev-style) matching: a basin qualifies only if it is close on *every*
condition, with no trading off between them — three continuous conditions (mean annual
temperature, seasonal temperature range, annual precipitation total) plus modality (rainy-season
count) as a hard gate rather than a weighted axis. Full rationale in the WO.

## Notebook structure

| Part | Cells | What it does |
|---|---|---|
| Setup / probes | 1–5 | Standard boilerplate; WO4's 7-probe set + Yakutsk (high-latitude sparse-end check); corpus-wide load of monthly arrays + BasinATLAS scalars + `ST_PointOnSurface` points, L06 and L08 |
| A — prominence threshold | 7–12 | Vectorized reimplementation of `scripts/cdop/wo5_modality_peak_count_probe.py`'s prominence-filtered peak-counting, validated cell-by-cell against that script's scalar version before running corpus-wide; sweep 5–50% in 5-point steps looking for a stability plateau; geography check (zone_name breakdown, world map) at the recommended threshold and sweep endpoints; confusion matrix + drawn monthly profiles comparing against the retired `R_dbl` measure |
| B — absolute vs percentile bands | 14–15 | Marginal (single-variable) result-count-and-width diagnostic on all 8 probes; conjunction proviso check (does combining all three variables make the marginal tension moot) |
| C — variable budget | 17–18 | Measured population share for nested variable sets (k=1..3) × tolerance (5/10/15/20 pctl points) × level, against the `(2t/100)^k` theoretical prediction; modality gate added as a 4th, discrete condition |
| D — precip lens compensation check | 20 | Live-API Check-3-style diagnostic on `climate.precip` (admitted `pre_mm_syr` range at strict/moderate/loose) — does it have the same compensation defect WO5 Part A found in `climate.temp`? |

## Design choices made while drafting (not in the WO text, decided here)

- **Vectorization.** The WO5 probe script's peak-counting is a per-basin Python loop; running it
  corpus-wide (16,397 L06 basins, 190,675 L08) needed a vectorized form. Rewritten so the walk
  step is batched across all basins at once (only 12 fixed index-arithmetic steps per direction,
  independent of N) rather than looping in Python per basin. Validated cell-by-cell (Cell 7)
  against a direct port of the original scalar function before trusting any corpus-wide number —
  confirmed exact match on all 4 WO5 probes × 4 thresholds.
- **High-latitude probe.** Yakutsk added to WO4's 7-probe set for Part B's sparse-end
  requirement (Tromsø tried first, hit a basin-coverage gap on its fragmented fjord coastline —
  swapped for continental Siberia instead).
- **Absolute band widths (Part B).** `ABS_TOL` = {tmp_dc_syr: ±2°C, tmp_seas_amp: ±2°C,
  pre_mm_syr: ±100 mm/yr}. Only the temperature figure is stated in the WO text; the other two are
  illustrative first-pass choices, not calibrated against any distribution fit. Expect these to
  move once Karl sees the count/width table.
- **Percentile band tolerance.** 5 percentile points for Part B's marginal diagnostic; Part C
  sweeps 5/10/15/20 explicitly as its own variable.
- **Part D probes.** George Town (WO4's opposite-failure case), Mombasa, Timbuktu — reusing
  probes already characterized rather than introducing new ones, so any compensation finding
  connects directly to prior findings.

## Results

### Part A — Prominence threshold for peak-counting modality

**No stability plateau exists, with or without an absolute floor.** The corpus-wide sweep
(5–50% prominence, both levels) is a smooth, monotonic decline throughout — no flat stretch
anywhere. `RECOMMENDED_FRAC = 0.20` is justified only by precedent (WO5's Mombasa 2→1 flip point),
not by anything the corpus-wide curve itself shows. This holds before and after the floor fix
below — the floor changed *which* basins get classified, not the shape of count-vs-threshold.

**Relative-only (fraction-of-own-range) prominence is unsound on its own.** Without an absolute
floor, the "bimodal" class geography *inverted* at strict thresholds: cold/dry/xeric zones
dominated the top-10 at 50% prominence instead of thinning out, because ordinary noise in a
near-flat arid/cold basin's curve trivially clears a threshold defined only relative to that
basin's own (tiny) range. Confirmed via zone_name breakdown and world map at L06/L08.

**A 20mm absolute floor** (`thresh = max(frac*range, 20mm)`) restored sane geography —
"Extremely hot and moist" (the genuine equatorial/ITCZ zone) now dominates consistently across
all three checked thresholds, and cold/arid zones stay in the tail rather than taking over. But
the floor **introduced the opposite failure**, demonstrated concretely rather than assumed: the
Horn of Africa (Somalia, hybas 1060006860) is a textbook two-monsoon climate (Gu rains Apr–May,
Deyr rains Oct–Nov) — peak-counting correctly identifies October as a local maximum, but its
prominence (~13mm) fell just under the 20mm floor, so the real second season was missed.

**Lowering the floor to 10mm confirmed this is a genuine two-sided trade-off, not a tuning
error.** At 10mm, Somalia is fixed (October's ~13mm prominence now clears it, peak count 1→2).
But the arid-noise problem partially returns: at the strict end (frac=50%) "Extremely hot and
xeric" retakes the #1 zone at L06 (192 vs. 138 for "Extremely hot and moist") and is
statistically tied with it at L08 (1,726 vs. 1,752) — the same inversion the floor was built to
fix, just less severe than with no floor at all. The loose end also moved a lot: frac=5% bimodal
share rose from 15.9%/16.6% (20mm floor) to 26.1%/27.1% (10mm floor) at L06/L08 — a large,
real sensitivity to one scalar parameter. And a second, independent symptom of the same problem
showed up on the Tennessee pinned basin: it picked up a third "peak" (July, ~11mm prominence)
that only clears the *lower* floor — a much weaker case for a genuine third rainy season than its
March (53mm) and December (32mm) peaks, and the kind of marginal wobble the floor exists to
exclude.

**Conclusion: no single absolute-floor value is simply correct.** 20mm is too strict for Somalia;
10mm is loose enough to partially reopen arid-zone noise and admit marginal peaks like
Tennessee's July bump. This is the same shape of result as the missing plateau one level down —
the corpus data does not pick a floor value for us, because the two things a floor is asked to do
(reject noise in flat/arid curves, accept real modest-magnitude second seasons) pull in opposite
directions on the same knob. Closing Part A here rather than continuing to search for a value that
satisfies both. A **relative-to-annual-total floor** (e.g., a peak's prominence must clear some
fraction of the basin's own annual precipitation total, not a fixed mm figure) is a candidate
worth raising for WO6b — untested here — since a fixed mm number can't scale between Somalia's
~250mm/yr regime and a much wetter one's noise floor.

**Vs. `R_dbl`:** 73.8% agreement at L06 (`RECOMMENDED_FRAC=0.20`, 20mm floor — run once, before
the 10mm retry above; not re-run at 10mm). Peak-counting is
markedly more conservative overall (1,951 basins flagged vs. `R_dbl`'s 2,953). Drawn disagreement
profiles (2 pinned + 6 random) reconfirmed both R_dbl failure modes WO5 already found, now at
corpus scale — false positives on a sharp single monsoon peak (India, NW Australia, plus two more
drawn examples all showing one dramatic peak against near-zero rest-of-year) and a likely false
negative from high-baseline dilution (Congo Basin — real-looking deep mid-year troughs that
`R_dbl` under-reads). A new structural finding: `R_dbl` cannot detect bimodality whose two peaks
aren't roughly 6 months apart, because it measures a specifically *semi-annual* harmonic
component by construction. A Tennessee basin (hybas 7060610850) has two genuine, well-separated
local maxima (March and December, ~9 months apart) with prominences of 32–53mm — comfortably real
by any measure — that `R_dbl` reads as essentially zero (0.03) purely because they're phase-offset
from a clean 6-month split. Peak-counting has no such phase assumption and catches it correctly.

**Net assessment:** peak-counting is more reliable than `R_dbl` on both of R_dbl's originally
diagnosed failure modes (sharp-peak false positive, high-baseline false negative), and catches
phase-asymmetric bimodality R_dbl structurally cannot. It is not a clean drop-in replacement,
though — its correctness depends on an absolute-floor value that trades two failure modes against
each other, and no plateau in the corpus data picks that value for us.

### Part B — Absolute bands or percentile bands

**Both halves of the predicted mirror-image tension are confirmed, with numbers.** Marginal
(single-variable) diagnostic, 8 probes, L06:

- **Absolute bands: stable meaning, unpredictable count.** Width sits at the design tolerance
  everywhere (temp ~3.9–4.0°C, precip ~197–200mm — the corpus is large enough that band edges are
  always populated). But count swings hugely for the same fixed width: temperature `abs_n` ranges
  572 (Yakutsk) to 4,173 (Mombasa), a **~7× spread**; precipitation is worse, 154 (George Town,
  2656mm/yr) to 3,249 (Yakutsk, 261mm/yr), **~21×**.
- **Percentile bands: roughly stable count, unstable meaning.** Count clusters near ~1,600–1,650
  in the interior (sensible truncation near the tails — e.g. Yakutsk's `tmp_seas_amp` sits at the
  99.9th percentile, so the ±5-point window clips at 100 and only returns 840). But the *physical
  width* of "±5 percentile points" ranges from 1.3°C (George Town) to 10.7°C (Yakutsk) for
  temperature — and for precipitation, **98mm to 4,915mm**, a **50× swing**. Precipitation's
  instability is far worse than temperature's, consistent with its known right-skew (the same
  property that motivated the log-transform used elsewhere in `climate.precip`).

**Conjunction proviso — the WO's own hoped-for resolution did not happen.** The WO floated that
combining all three variables might shrink absolute bands' "tropical over-return" enough that
"absolute wins on both criteria and there is nothing to trade off." It didn't: Mombasa's
abs-conjunction count (202) remains the largest across all 8 probes even after all three
conditions apply together — the underlying bias (common climates are just common) survives
conjunction rather than dissolving into parity. Percentile is the more generous rule in 6 of 8
probes, sometimes by a lot (Yakutsk 244 vs. 27, 9×; George Town 338 vs. 98, 3.4×; Augsburg 29 vs.
9, 3.2×) — absolute only wins for Mombasa and Timbuktu, both fairly typical tropical/monsoon
profiles sitting in dense climate clusters. Santiago returns 2–3 matches either way — honest
scarcity (WO4 Part 2 precedent), not a failure of either rule.

**Decision: percentile bands.** Percentile is more often the more generous rule, and specifically
more generous exactly where the query point is unusual (Yakutsk, George Town) — the opposite of
what absolute bands do, and arguably the more useful property for an instrument meant to
characterize unusual places. Absolute's one real advantage (fixed physical meaning) never
translated into a stable count anywhere, including under conjunction, so there was nothing to
trade it against.

### Part C — Variable budget, measured

**No collapse to empty, even at k=3 with the tightest tested tolerance.** At tol=5 (±5 percentile
points on all three continuous variables simultaneously), L06 returns ~111 matches on average
across probes (0.68% of corpus) and L08 ~1,230 (0.65%) — small, but a genuinely workable result
set, not the "returns nothing" failure mode the WO flagged as the thing to watch for. Measured
counts run 1.7×–6.8× above the naive independence prediction `(2t/100)^k` throughout, confirming
real variable correlation is doing substantial work (consistent with WO5's −0.84
`tmp_dc_syr`/`tmp_seas_amp` correlation).

**The L06/L08 "asymmetry" is about absolute count, not selectivity.** The WO expected L08's finer
support to make the instrument "more comfortable." Measured: the *percentage* of corpus matching
is essentially level-invariant at every k/tol combination (e.g. k=3/tol=20: 11.02% at L06 vs.
10.87% at L08). L08 does return far more matches in absolute terms (20,651 vs. 1,800 at
k=3/tol=20) simply because it has ~11.6× more basins total — but the instrument's actual
selectivity doesn't change with level. Worth stating this precisely rather than the looser
"L08 is more comfortable" framing.

**Adding the modality gate (k=4, the actual proposed WO6b instrument, L06 only) still doesn't
collapse to zero** — the sparsest case is Santiago at tol=5 with n=3 (0.018%), consistent with
Part B's finding that Santiago is a genuinely rare global combination.

**But the gate's bite is highly asymmetric and class-dependent, which matters for how WO6b should
read this number.** At `RECOMMENDED_FRAC=0.20`/10mm floor, 7 of the 8 probes have
`query_peak_count=1` — the common, roughly-82%-of-the-globe unimodal class — so the modality gate
barely restricts them beyond the three continuous conditions alone. George Town is the one probe
with `query_peak_count=2` (the rarer ~18% bimodal class), and it shows real additional
restriction: its k=4/tol=20 share (2.77%) sits far below the group's k=3/tol=20 average (11.02%),
while the other 7 probes' reductions are much smaller. The apparent ~30% drop in average share
from k=3 to k=4 (11.02%→7.67% at tol=20) is mostly George Town pulling the average down, not a
uniform effect — **a query that happens to be bimodal gets gated much harder than one that
doesn't**, an asymmetry inherent to gating on a skewed class distribution that WO6b's design
should account for explicitly rather than treating the gate as a uniform k+1 condition.

### Part D — Precipitation lens compensation check

**Confirmed: `climate.precip` has the same compensation defect WO5 Part A found in
`climate.temp`.** Three probes (George Town 2655mm/yr, Mombasa 1101mm/yr, Timbuktu 190mm/yr) at
strict/moderate/loose stringency:

- **Strict returns zero for the two wetter probes** (George Town, Mombasa) — consistent with the
  already-known "threshold mode returns zero peers for 36–39% of cities at strict" finding
  (`wo_l08_findings.md`), not a new result.
- **Moderate already shows real compensation.** Timbuktu (query 190mm) admits basins from 111mm to
  351mm — a basin at little more than half Timbuktu's rainfall and one at nearly double both
  register as "moderately similar precipitation regime." George Town's moderate set spans
  1,646–3,641mm against a 2,655mm query (0.62×–1.37×).
- **Loose is dramatic.** Timbuktu's admitted range widens to 51–736mm — **0.27× to 3.87× the
  query value**, a basin at roughly a quarter and one at nearly four times Timbuktu's actual
  rainfall both qualifying because harmonic shape (`a1,b1,a2,b2`) agrees. George Town's loose set
  spans 719–6,872mm (0.27×–2.59×); Mombasa's spans 388–1,665mm (0.35×–1.51×).

Same mechanism as Check 3: level (`log_pre_mm_syr`) and shape are bundled into one composite
Euclidean distance, so favorable shape agreement buys tolerance on absolute magnitude. Diagnostic
only, per the WO's own scope — no lens change made here.

## Recommendation for WO6b

**Percentile bands, not absolute** (Part B). The instrument as specified — 3 continuous conditions
+ modality gate — does not collapse to an unusable empty set even at its tightest tested tolerance
(Part C), but two design points need to carry into WO6b explicitly rather than being smoothed
over:

1. **No single scalar controls this instrument cleanly.** Part A found no data-driven prominence
   threshold and no absolute-floor value that avoids trading arid-noise false positives against
   real-modest-signal false negatives. A relative-to-annual-total floor (untested here) is the
   most promising unexplored fix.
2. **The modality gate's restrictiveness depends on which class the query falls into**, not a
   uniform k+1 tightening — WO6b should decide how to present/calibrate this rather than assume
   it behaves like the three continuous conditions.

Part D confirms `climate.precip` carries the same composite-distance compensation defect Part A
had already flagged indirectly via `R_dbl` (which is computed from the same `a2,b2` components
`climate.precip` uses). It doesn't bear on the two points above — it's a separate, independent
diagnostic of the currently-shipped lens — but it's a second, independently-confirmed instance of
the exact failure mode this whole WO is a response to (WO5 Part A Check 3), now shown in the lens
that's actually live in production, not just `climate.temp`. Worth carrying into whatever the
Karl/Opus similarity-architecture conversation does with the existing Similarity tab.
