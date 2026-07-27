# WO8c findings — Environment↔culture correspondence: political complexity (EA033)

**Work order:** `docs/cdop/pilot/wo8c_political complexity-EA033.md`
**Branch:** `cdop_wo8c` (cut from `cdop_pilot`). **Type:** statistical-test notebook, no engine / API / UI.
**Notebook:** `notebooks/cdop/wo8c_political_complexity.ipynb` (12 cells + gate). **Engine:**
`scripts/cdop/dbperm.py`, extended this WO with `return_null=True` (exposes the permutation-null R²
distribution — the machinery the effect-size floor runs on; `tests/cdop/test_dbperm.py`, 14 green).
**Data:** `output/cdop/wo8c_substrate.parquet`; new infra persisted this WO: `dplace.society_elevation`
(point elevation, all 6,408 coordinate-bearing `dplace.societies`), `dplace.society_terrain`
(point-window local relief, the 1,133 EA societies). **Status:** complete — accept gate **PASSED**.

All statistics are **family-restricted** (permutation within language family — the Galton control) on the
**drop-to-representative** metric carried from WO8b (`ari_log`, `temperature_annual`, `tmp_seas_amp`).
Verdicts are read against the **committed effect-size floor** — the 95th percentile of each test's own
family-restricted permutation-null R² distribution, not a p-value and not eyeballed — and every
near-margin verdict was re-run at a second seed and 5× the permutations before being trusted.

---

## Headline — a weak raw link, and what survives control clears noise but not interpretability

Complexity's raw, uncontrolled link to climate is weak — itself the real surprise, given how strongly
both subsistence (WO8a) and settlement fixity (WO8b) tracked climate. What survives controlling for
subsistence (and for subsistence+fixity together) is small (R² ≈ 0.017–0.018 for the group contrast,
≈ 0.010 for the ordinal trend), sits at the edge of its own permutation-noise floor, and — the crux — is
estimated on very little independent variation: the state end of the ladder is ~92% concentrated in a
single subsistence category and ~92% in a single settlement category (Part A), so there is almost no
complexity-variation left at fixed subsistence/fixity for a "net of" test to actually measure. **Clearing
the noise floor is a necessary condition for a result to be worth reading, not a sufficient one** — it
says a number probably isn't pure chance; it says nothing about whether it is big enough, or clean enough
of the collinearity documented in Part A, to interpret as an independent effect. Read through that lens,
the honest verdict is: **no strong independent environmental signal — a small residual that clears noise
but not interpretability.** Settlement fixity is not the mechanism absorbing that residual either way —
adding it as a covariate barely moves the number, so the WO's concern that fixity might be a
confound-eating mediator turns out to be moot for this trait; there is simply little room left for any
covariate to move. Ruggedness (terrain) shows no signal on either formulation once checked at a second
seed. A cross-check applying the same floor logic to WO8b's fixity residual (Cell 12) shows it also
clears its own floor by a wide margin — but the same necessary-not-sufficient reading applies there too,
so this is **not** read as reversing WO8b; that record stands unchanged (see below).

---

## Part A — substrate (Cells 2–4)

Extended `wo8b_substrate.parquet` with **EA033 jurisdictional hierarchy** (ordinal 1–5: Acephalous / One
level / Two levels / Three levels / Four levels, via the CLDF codebook's own `ord` column) and joined the
new terrain lens (`dplace.society_terrain`, point-window; `dplace.society_terrain`/basin `smx−smn` also
joined as the WO's named fallback comparison, not needed in practice — point-window resolved 1133/1133).

- EA033 coded **1,012 / 1,133** (drop 121 uncoded). Distribution: Acephalous 464, One level 295, Two
  levels 137, Three levels 75, Four levels 41 — heavily right-skewed toward low complexity, typical for
  an EA-style cross-cultural sample.
- Point-window terrain (5×5 grid, 1km spacing, ±2km box, `persist_dplace_terrain.py`) resolved **1,133 /
  1,133**. Basin-level `smx−smn` fallback also resolved 1,133/1,133 but runs **4–7× larger** on average
  (point-window mean 211m / median 83m vs basin mean 928m / median 620m) — the container effect this
  project has hit before (Tbilisi, San Francisco), now confirmed a third time: a basin polygon's full
  elevation range picks up terrain the society never touched. Point-window is materially the right choice,
  not a technicality.
- **Eligible (complexity + fixity + family + subsistence all present): 891 / 1,133.** 78 families, 13
  singletons, 878 in permutable (≥2-member) families — structurally healthy.
- **Pre-test cell-count gate — the predicted collinearity hazard, concentrated at the top.** Complexity ×
  subsistence: 9/30 empty cells; complexity × fixity: 6/40 empty. The state end (Three+Four levels,
  n=114) is **92% concentrated** in Intensive agriculture (subsistence) and 92% in
  Villages/towns+Complex permanent (fixity) — in this sample, state-level societies are almost never
  anything else. Acephalous and One-level societies are well-spread across every category. This is exactly
  the hazard the WO named going in (complexity, subsistence, and fixity are three near-collinear cultural
  variables), now with real numbers: the residual that survives the nested tests below rests on whatever
  independent variation remains once the near-monolithic state tail is accounted for.

## Part B — metric confirmation (Cell 5)

No re-litigation needed: this sample's correlation structure matches WO8a/8b closely (water block
`ari_log`/`pre_mm_syr`/`run_mm_syr` = 0.647–0.826 vs WO8a's 0.66–0.83; thermal pair
`temperature_annual`/`tmp_seas_amp` = −0.837 vs WO8a's −0.83). **Drop-to-representative (REP3)** carries
forward unchanged.

Declared collapses (both stated as conventions before results were seen, not fit to this sample):
5-level EA033 → 3-level **complexity3** (acephalous 393 / intermediate 389 / state 109, a standard
political-evolution trichotomy); WO8b's own 8-level fixity → **fixity4** recomputed here (it was never
persisted to the WO8b parquet) — sedentary 569 / mobile 220 / semi 79 / complex 23.

## Part C — the test (Cells 6–9, robustness-checked in Cell 11)

**Marginal — weaker than the WO predicted.** The WO expected the marginal to "light up strongly." It
didn't:

| test | R² | p | note |
|---|---|---|---|
| factor (3-level) | 0.050 | 0.068 | not even conventionally significant |
| ordinal trend (1–5) | 0.006 | 0.382 | essentially flat |
| PERMDISP | — | 0.0005 (F=40.8) | dispersions differ (state 1.57, acephalous 1.72, intermediate 1.23) |

Compare WO8a/8b's marginal reads (fixity R²=0.213, unambiguous): complexity's raw association with the
measured climate envelope is much weaker than either subsistence or fixity turned out to be — a real,
specific finding about the trait, not just a preamble to the nested test.

**Nested SPEC 1 — net of subsistence only:**

| test | R² | p | marginal was | gap |
|---|---|---|---|---|
| factor (3-level) | 0.017 | 0.032 | 0.050 | 0.033 (66% collapse) |
| ordinal trend | 0.009 | 0.227 | 0.006 | −0.003 (noise, not a real suppression effect) |

**Nested SPEC 2 — net of subsistence + fixity** (Freedman–Lane, two covariates via `adonis_term`'s
`covars=list`):

| test | R² | p |
|---|---|---|
| factor (3-level) | 0.018 | 0.0095 |
| ordinal trend | 0.010 | 0.0210 |

**Fixity absorbs essentially nothing** (factor: −0.0011; ordinal: −0.0017) — SPEC 1 and SPEC 2 tell the
same story to two decimal places. The WO's own methodological concern (fixity might be a *mediator*,
removing real signal, not just noise) turns out not to bite for this trait: whatever complexity's
residual environmental signal is, fixity doesn't touch it.

**The effect-size floor (Cell 9, stability-checked in Cell 11 at a second seed + 5× permutations).**
Clearing this floor is a *necessary* condition for a result to be worth reading — it means the number is
not indistinguishable from pure permutation noise. It is **not sufficient** to call the result a clean
independent finding; that additionally requires the residual not to be an artifact of the collinearity
documented in Part A. The table below reports the floor read the notebook computed (its "interpretable" /
"sub-floor" labels mean exactly "clears / doesn't clear the noise floor" — nothing stronger); the
paragraph after it is the actual reading, once the second bar is applied.

| test | R² | floor (orig) | verdict (orig) | floor (stability check) | verdict (stability check) |
|---|---|---|---|---|---|
| SPEC1 factor | 0.0169 | 0.0157 | interpretable (7.6% clear) | 0.0156 | **interpretable — holds** |
| SPEC1 ordinal | 0.0085 | 0.0100 | sub-floor | 0.0100 | **sub-floor — holds** |
| SPEC2 factor | 0.0181 | 0.0153 | interpretable (18.3% clear) | 0.0153 | **interpretable — holds** |
| SPEC2 ordinal | 0.0102 | 0.0090 | interpretable (13.3% clear) | 0.0091 | **interpretable — holds (12.1%)** |

Three of four nested verdicts clear their own noise floor — a real, stability-confirmed statement that
these numbers are not chance. **That is where the floor rule's authority ends.** The state tail's 92%
concentration in a single subsistence category and a single fixity category (Part A) means there is very
little independent complexity-variation for these tests to have measured in the first place — the
surviving R²≈0.018 is close to what a residual would look like whether or not a genuine independent
effect exists. The collinearity caveat is not a footnote to this result; **it is the frame the result has
to be read through.** Best read: distinguishable from noise, not separable from confound.

## Part D — the cheap terrain lens (Cell 10, stability-checked in Cell 11)

Point-window ruggedness (`relief_range_m`, `landform_position`) available for 886/891 (5 missing; the
basin fallback was not needed). Tests *ruggedness* (a fragmentation proxy), not *enclosure*
(circumscription's actual, unbuilt containment variable) — no directional prediction, by design.

| test | R² | p | floor (orig) | verdict (orig) | floor (stability check) | verdict (stability check) |
|---|---|---|---|---|---|---|
| factor (3-level) | 0.0119 | 0.239 | 0.0151 | sub-floor | 0.0153 | **sub-floor — holds** |
| ordinal trend | 0.0078 | 0.049 | 0.0077 | interpretable (1.3% clear) | 0.0079 | **sub-floor — FLIPPED** |

The ordinal result was the thinnest margin in the whole notebook (a 0.0001 R² clearance) and did not
survive the stability check — confirmed noise, not signal, once checked properly. **Both terrain
formulations are clean nulls.** PERMDISP shows a modest dispersion difference (F=5.33, p=0.03; state and
intermediate tighter at 1.11, acephalous wider at 1.28) — noted, doesn't change the reading.

**What the terrain null does and does not rule out:** it narrows the terrain channel — rough/broken
country shows no measurable association with complexity level, one way or the other. It does **not** test
circumscription. Carneiro's hypothesis is about the *boundedness* of arable land (a relational,
basin-neighborhood property), not local ruggedness (a fragmentation property with the opposite expected
sign) — that variable is unbuilt (see Forward, WO text). A null here leaves circumscription exactly as
untested as it was going in.

## Cross-check on WO8b's fixity residual (Cell 12) — no change to WO8b's record

Building this WO's floor machinery made it cheap to check something that couldn't be checked when WO8b
closed: does WO8b's fixity residual (net of subsistence, R²=0.0334 factor / 0.0108 ordinal) clear *its
own* permutation-null floor? `return_null` didn't exist at the time, so this was never actually computed.

Reconstructing WO8b's exact design (its own 918-society universe, same REP3 metric, same fixity4 collapse,
same seed/n_perm) from the untouched `wo8b_substrate.parquet` confirms the reconstruction is faithful
(R²=0.0334 / 0.0108, matching WO8b's reported numbers exactly) and then applies the floor:

| test | R² | floor (WO8b's own null) | clears floor by |
|---|---|---|---|
| factor | 0.0334 | 0.0104 | 3.2× |
| ordinal | 0.0108 | 0.0030 | 3.6× |

WO8b's fixity residual clears its own floor comfortably — more comfortably than any of WO8c's own
residuals, in fact. **But the same necessary-not-sufficient logic that governs WO8c's own reading above
applies here too**: clearing the floor confirms the number isn't chance; it says nothing about whether it
survives the same heavy cultural collinearity WO8b's own findings already documented (fixity × subsistence
is a near-block-diagonal grid — WO8b Part A, 15/48 empty cells). So the correct reading is not "WO8b's
verdict was wrong" — it is: **fixity's residual, like complexity's, is distinguishable from noise but
small and confounded; neither upgrades to an interpretable independent effect.** WO8b's original instinct
to characterize the residual as not independently meaningful was closer to right than a
floor-clears-therefore-real reading would be. **No change to WO8b's record** — `wo8b_findings.md`,
`wo8b_exec_summary.md`, and the tracker's WO8b subsection all stand as written. The ~84% subsistence-share
arithmetic there (marginal R²=0.213 → nested R²=0.033/0.011) was always correct and is untouched by any of
this; this section is recorded as a cross-check confirming the floor rule works as intended (WO8b's larger,
more collinear residual clears its floor by a wider margin than WO8c's — internally consistent), not as a
correction owed anywhere.

---

## Accept gate — PASSED

Per the WO's own framing, the gate is not "is it significant" — it is a defensible, reported effect size
across marginal / nested×2 / terrain, interpretable whichever way it comes out, with the procedural
requirements met: pre-test cell counts reported (Part A); the residual read against the committed floor
with the fixity cross-check reported alongside (Part C, and the WO8b cross-check above); the
collinearity caveat stated with the confound-share, and read as the frame the result requires, not a
footnote beside it (Part C); SPEC 1 and SPEC 2 reported side by side, never SPEC 2 alone (Part C); the
terrain-lens result reported and interpretable (Part D); and an explicit statement of what the terrain
null does and does not rule out (Part D). All met. **The substantive answer is close to the modal null
the WO predicted, not a departure from it**: the raw link is weak, and what survives the subsistence(+
fixity) control clears its own noise floor but not the collinearity bar — read as no strong independent
environmental signal, not as the small positive finding a floor-clears-therefore-real reading would
suggest.

## Carried forward / notes for WO8d

- **Calibration scale, softened, not inflated:** subsistence is strong and clean (WO8a). Fixity and
  complexity are both small once properly controlled — each clears its own noise floor (WO8b R²≈0.033/
  0.011, WO8c R²≈0.018/0.010) but neither clears the collinearity bar, so neither is an independent
  finding in the strong sense. Carry **"subsistence strong; fixity and complexity both weak and confounded
  net of it"** into 8d — not a "strong > moderate > small-but-real" gradient a floor-only reading would
  suggest.
- **The stability-check discipline (second seed, 5× permutations) is now standard practice for any
  near-margin floor verdict** — it caught the one result (terrain ordinal) that needed catching. Recommend
  carrying it into 8d as a required step, not an optional add-on.
- **The floor-vs-collinearity discipline (Cell 12's real lesson) applies to any future residual, not just
  this WO's:** clearing the floor is a necessary-not-sufficient check — cheap to run on any prior WO's
  residual (worth a one-line confirmation on WO8a too, though it was descriptive-only and likely moot),
  but it never substitutes for reading the collinearity structure documented in Part A of whichever WO.
- **Collinearity gets worse, not better, at 8d.** High-gods (EA034) is tightly coupled to complexity in the
  literature (the big-gods debate) — expect a fourth near-collinear cultural variable, and the same
  concentration-at-the-extreme pattern this WO found at the state tail.
- **Enclosure/circumscription remains the real open terrain question**, unbuilt. The WO's named trigger for
  building it is "an ambiguous 8c null (climate null + ruggedness null) plus reason to believe
  circumscription specifically." Ruggedness is a clean null; the climate-envelope result, under the
  corrected reading above, is itself ambiguous (clears its noise floor, doesn't clear collinearity) rather
  than cleanly positive or cleanly null — so whether this WO's result actually satisfies the named trigger
  is a live question for Karl/Opus, not resolved here.
