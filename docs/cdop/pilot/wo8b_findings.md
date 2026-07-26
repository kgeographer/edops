# WO8b findings — Environment↔culture correspondence: the first test (settlement fixity)

**Work order:** `docs/cdop/pilot/wo8b_fixity-test.md`
**Branch:** `cdop_wo8b` (cut from `cdop_pilot`). **Type:** statistical-test notebook, no engine / API / UI.
**Notebook:** `notebooks/cdop/wo8b_fixity_test.ipynb` (10 cells + gate). **Engine:**
`scripts/cdop/dbperm.py` (hand-rolled PERMANOVA / db-RDA / Freedman–Lane partial / PERMDISP;
`tests/cdop/test_dbperm.py`, 10 green). **Data:** `output/cdop/wo8b_substrate.parquet`.
**Status:** complete — accept gate **PASSED**. Exec summary: `wo8b_exec_summary.md`.

All statistics are **family-restricted** (permutation within language family — the Galton control) on the
**drop-to-representative** metric. p = 0.0005 is the permutation floor (1 / 2000): "nothing in 1,999
shuffles beat the observed."

---

## Headline — settlement concentrates in a favorable band

Settlement fixity tracks environment: sedentary societies **concentrate in a narrow, favorable climatic band** (wet, warm, low-seasonality — good farming country), while mobile societies **spread widely across the dry, cold, seasonal margins the band excludes**. Climate (chiefly water) *gates the agriculture option*: where it is open people farm and settle; where it is closed they cannot, and mobility is the wide fallback. So climate acts as a **target, not a floor** — it concentrates settlement in the favorable band rather than merely forbidding it at the extremes. About **84%** of the fixity↔environment link is the bundled *farm-and-settle* decision (subsistence); net of economy the residual (R² ≈ 0.01–0.03) is best read as **no interpretable independent effect** — the near-total collapse under the economy control *is* the result, not the sliver that survives it. This is the difference between a truism ("settled people are where you can farm") and a measured one — the rigorous test earned the plain reading over a determinist over-claim, and did so on observed per-group breadth (Cell 10), not asserted.

---

## Part A — substrate (Cells 2–4)

Extended `wo8a_substrate.parquet` with **EA030 fixity** (ordinal 1–8, via the CLDF codebook's own `ord`
column) and the **language-family crosswalk** reconstructed by the WO4 method — 85 Glottolog family trees
(`data/dplace/cldf/trees/*.trees`, glottocode-named; 29 Phlorest study phylogenies excluded), leaf
glottocodes → family, societies resolved via `Language_Level_Glottocodes` (fallback `Glottocode`).

- EA030 coded **1,044 / 1,133**; family resolved **1,049 / 1,133 = 92.6%** (exactly the WO4 figure).
- **Eligible (fixity + family + subsistence all present): 918.** 79 families, 14 singletons, **904
  societies in permutable (≥2-member) families** — a healthy structure for the restricted null.
- **Scope note (documentation-completeness filter, disclosed not corrected):** the 918 excludes 89
  fixity-uncoded societies (including **all 75 "Agriculture, type unknown"** — correlated missingness: the
  thinly-documented lack both codes), 55 with missing subsistence (the "None" bucket was NaN, not a real
  category — a correction to the WO8a reading), and the family-unresolved. Mild skew toward
  better-recorded (state-ward) societies; not an environmental filter.
- **Pre-test cell-count gate:** the 8-level fixity × subsistence grid is **near block-diagonal** — 15 of
  48 cells empty, min 1 (nomads ≈ no agriculture; towns ≈ all agriculture). That sparsity is itself the
  fixity↔subsistence tautology the WO anticipated. Resolution: **factor tests on a declared 8→4 collapse**
  (mobile / semi / sedentary / complex = 223 / 80 / 591 / 24), **ordinal trend on the full 1–8** (a
  monotonic test pays no sparsity tax — it stays maximally faithful to the "environment marches up the
  ladder" hypothesis).

## Part B — the metric decision (Cell 5)

The WO8a composite-distance hazard, resolved with a sensitivity line. Marginal fixity(4-level),
family-restricted:

| metric | k | R² | F | p |
|---|---|---|---|---|
| keep-all-5 | 5 | 0.177 | 65.5 | 0.0005 |
| **drop-to-representative** | 3 | **0.213** | 82.5 | 0.0005 |

Dropping the redundant water axes (aridity/precip/runoff r = 0.66–0.83) **sharpens** the signal rather
than weakening it — the over-counted water block was diluting fixity's R². Carried forward:
**drop-to-representative** (`ari_log`, `temperature_annual`, `tmp_seas_amp`); aridity embeds P/PET and
stands for the water block, every axis stays nameable.

## Part C — the test (Cells 6–7)

**Marginal** (does fixity track environment):

| test | R² | p | note |
|---|---|---|---|
| factor (4-level) | 0.213 | 0.0005 | strong |
| ordinal trend (1–8) | 0.164 | 0.0005 | environment climbs the ladder |
| **PERMDISP** | — | 0.0005 (F=49.8) | **dispersions differ** |

**PERMDISP is a finding, not just a nuisance.** The fixity groups differ in environmental *breadth*, not
only centre: **mobile societies span the wider environmental range** (breadth 1.76) across dry/cold/seasonal margins, while **sedentary societies cluster in the narrow favorable band** (breadth 1.06). Direction confirmed on the Cell 10 per-group means. So the marginal factor
number mixes a location shift with a spread difference; the ordinal-trend and nested reads are cleaner.
(Group imbalance 591 vs 24 also inflates PERMDISP; a 3-level `complex→sedentary` merge is a cheap
robustness option, not run.)

**Nested** (fixity net of subsistence, Freedman–Lane residual permutation within family):

| test | nested R² | p | marginal was | gap |
|---|---|---|---|---|
| factor (4-level) | 0.033 | 0.0005 | 0.213 | **0.180 ≈ 84%** |
| ordinal trend (1–8) | 0.011 | 0.0005 | 0.164 | 0.153 ≈ 93% |

**The gap is the headline output:** ~84% of fixity's environmental signal is subsistence in disguise.
Net of economy the residual is R² ≈ 0.01–0.03 — it clears the permutation floor only because n = 918
makes trivial effects detectable, and at that magnitude it is reported as **no interpretable independent
effect**, not as a "small real" one. The near-total collapse is the finding; the surviving sliver is not
worth interpreting.

**Collinearity caveat.** Fixity and subsistence are near-collinear (the block-diagonal grid — 15 of 48
cells empty), so the nested estimate rests on very little fixity-variation-at-fixed-subsistence. The 84%
is therefore partly a statement about that *overlap*, not a pure claim about nature: attributing shared
variance to one of two near-identical variables is inherently unstable. Carry this into 8c, where
political complexity is also subsistence-collinear and will show the same shape partly for the same
mechanical reason.

## Part D — seasonality reactivation (Cell 8)

Does adding rainfall *timing* (raw 12-value curve, WO6b backbone) change fixity's result where it did not
change subsistence's? **No — refuted.** env R²=0.217 → env+season R²=0.133, **dR²=−0.084**: the timing
channel adds a fixity-orthogonal dimension that *dilutes* rather than sharpens. Fixity tracks *amount and
warmth*, not *when* the rain falls — the same channel subsistence left idle stays idle for fixity.
(The env-only 0.217 is the same marginal-fixity quantity as Part C's 0.213, on the 916 societies with a
defined rainfall curve — 2 flat-curve dropped; the distance rescaling doesn't affect R².)

## The prediction — confirmed (Cell 9)

Stated up front: aridity survives the family null better than the temperature/continentality axis, because
part of any forager↔cold signal is that foragers cluster at high latitudes (phylogeny), which the
within-family null removes.

| axis | R² | family-restricted p |
|---|---|---|
| aridity (water) | 0.134 | 0.0005 |
| temperature (level) | 0.217 | **0.020** |
| seasonal amplitude | 0.288 | 0.0005 |

**Confirmed, and precisely:** temperature *level* has the higher raw R² but its family-restricted p
collapses to 0.020 — the signature of phylogenetic inflation (latitude is shared within families). Aridity
— the axis that actually gates agriculture — is robust. Seasonal amplitude is a strong, robust third axis.
The family control demonstrably bites: direct evidence the instrument separates real signal from ancestry.

**This — not the fixity substance — is the result that matters, and it is a claim about the *instrument*,
not about settlements.** A named axis was predicted in advance, for a stated mechanistic reason, to
deflate under ancestry control; it did, while the predicted-robust axis held. That is the transferable
credibility asset for every contested test that follows (and the strongest short-form story for an
external audience), because it is defensible on method grounds alone — no anthropology required. The
fixity finding is the calibration; the differential deflation is the proof the calibration means
something.

---

## Accept gate — PASSED

A defensible, reported effect size for fixity — marginal and nested — with the family-restricted null and
PERMDISP, interpretable whichever way it came out. Not a null, not a slam-dunk: a large subsistence share
absorbing almost all of the marginal signal, a negligible independent residual, and — the result that
earns the gate — a demonstrated phylogeny effect (the predicted differential deflation). The gate
deliberately reads effect size, not "is it significant."

## Carried forward / notes for WO8c

- **Bet = Climate envelope, drop-to-representative metric** carried; the metric only had to be honest about
  magnitude, and the sensitivity line shows the headline is not a water-over-counting artifact.
- **The nested design is even more essential for 8c** (EA033 political complexity), which routes through
  subsistence/surplus too. Decide the covariate set (subsistence alone, or + fixity) before drafting.
  Note the collinearity caveat travels with it: complexity is subsistence-collinear, so its confound
  share will be partly an overlap artifact, not a pure nature claim — state it.
- **Reporting stance (decided, set before 8c's number is seen):** the headline is the *share explained by
  the confound*; residuals below a pre-set effect-size floor are reported as *no interpretable independent
  effect*, never as "small real" findings. Pick the floor before running 8c so it cannot be motivated by
  the result. This is what keeps a three-rung methods probe from accreting slivers into an overclaim.
- **3-level `complex→sedentary` robustness** for the factor/PERMDISP imbalance — cheap, not run.
- **Held Bet 4 (soil)** unopened; opens only if a rung's nested structure asks for a soil axis.