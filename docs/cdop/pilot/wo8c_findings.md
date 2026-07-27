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

## Headline — a small, real signal survives, net of both subsistence and settlement fixity

Contrary to the WO's own stated expectation (the modal predicted outcome was a null), **political
complexity shows a small but robustly-above-floor independent environmental signal**, net of subsistence
*and* net of subsistence+fixity together. It is real by the pre-committed rule and confirmed stable under
a second permutation run — but it is small in absolute terms (R² ≈ 0.017–0.018 for the group contrast,
≈ 0.010 for the ordinal trend, roughly 1–2% of environmental variance), smaller than settlement fixity's
own residual once that number is corrected (see below). Settlement **fixity turns out not to matter at
all** as a covariate here — adding it barely moves the residual either direction, so the WO's concern that
fixity might be a confound-eating mediator turned out to be moot for this trait. **Ruggedness (terrain)
shows no interpretable signal**, on either formulation, once checked at a second seed — narrowing the
terrain channel, not the different, unbuilt "enclosure" (circumscription) variable, which remains
untested. A secondary, unplanned result of building this WO's floor machinery: **retroactively applying
the same rule to WO8b's fixity residual reverses that WO's original verdict** — flagged below, not yet
applied to WO8b's closed record.

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

**The effect-size floor (Cell 9, stability-checked in Cell 11 at a second seed + 5× permutations):**

| test | R² | floor (orig) | verdict (orig) | floor (stability check) | verdict (stability check) |
|---|---|---|---|---|---|
| SPEC1 factor | 0.0169 | 0.0157 | interpretable (7.6% clear) | 0.0156 | **interpretable — holds** |
| SPEC1 ordinal | 0.0085 | 0.0100 | sub-floor | 0.0100 | **sub-floor — holds** |
| SPEC2 factor | 0.0181 | 0.0153 | interpretable (18.3% clear) | 0.0153 | **interpretable — holds** |
| SPEC2 ordinal | 0.0102 | 0.0090 | interpretable (13.3% clear) | 0.0091 | **interpretable — holds (12.1%)** |

Three of four nested verdicts are robustly interpretable; SPEC1's ordinal trend alone is a clean null.
**Collinearity caveat stands alongside every one of these numbers**: with the state tail 92% concentrated
in one subsistence/fixity combination, the surviving residual is real by the floor rule but is not immune
to the overlap problem the WO named — it should be read as "a small signal survives the near-total
overlap," not as clean independent evidence.

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

## Retroactive check on WO8b's fixity residual (Cell 12) — flagged, not yet applied

Building this WO's floor machinery made it cheap to check something that couldn't be checked when WO8b
closed: was WO8b's own "no interpretable independent effect" call (fixity net of subsistence, R²=0.0334
factor / 0.0108 ordinal) actually checked against *its own* permutation-null floor? It wasn't —
`return_null` didn't exist yet, so WO8b's verdict was a judgment call, not a floor-rule read.

Reconstructing WO8b's exact design (its own 918-society universe, same REP3 metric, same fixity4 collapse,
same seed/n_perm) from the untouched `wo8b_substrate.parquet` confirms the reconstruction is faithful
(R²=0.0334 / 0.0108, matching WO8b's reported numbers exactly) and then applies the floor:

| test | R² | floor (WO8b's own null) | verdict |
|---|---|---|---|
| factor | 0.0334 | 0.0104 | **interpretable — clears by 3.2×** |
| ordinal | 0.0108 | 0.0030 | **interpretable — clears by 3.6×** |

Neither result is close — this is not a borderline case like terrain-ordinal above. **Under the rule
WO8c committed to, WO8b's own fixity residual was a real, interpretable independent effect, not "no
interpretable independent effect."** This does not change WO8b's confound-share arithmetic (marginal
R²=0.213 → nested R²=0.033/0.011 is still an ~84% collapse — subsistence still absorbs the great majority
of fixity's raw environmental correlation); it changes the characterization of what is left over. WO8b's
`wo8b_findings.md`, `wo8b_exec_summary.md`, and the tracker's WO8b subsection all currently assert the
now-contradicted framing and need a coordinated amendment — **held pending Karl's decision on when/how to
apply it**, not made unilaterally here.

---

## Accept gate — PASSED

Per the WO's own framing, the gate is not "is it significant" — it is a defensible, reported effect size
across marginal / nested×2 / terrain, interpretable whichever way it comes out, with the procedural
requirements met: pre-test cell counts reported (Part A); the residual read against the committed floor
with the fixity cross-check reported alongside (Part C, and the retroactive correction above); the
collinearity caveat stated with the confound-share (Part C); SPEC 1 and SPEC 2 reported side by side,
never SPEC 2 alone (Part C); the terrain-lens result reported and interpretable (Part D); and an explicit
statement of what the terrain null does and does not rule out (Part D). All met. **The substantive answer
is not the modal null the WO predicted** — a small, robustness-confirmed independent effect survives — but
that is a legitimate outcome under the WO's own stated logic (a null was the expected result, not a
requirement).

## Carried forward / notes for WO8d

- **Three-point calibration scale, corrected:** subsistence (strong, WO8a) > fixity (moderate, R²≈0.033/
  0.011, **now confirmed real** pending the WO8b amendment) > complexity (smaller but real, R²≈0.018/
  0.010). A coherent gradient, not the flat "everything collapses to nothing" picture the pre-WO8c
  expectation implied.
- **The stability-check discipline (second seed, 5× permutations) is now standard practice for any
  near-margin floor verdict** — it caught the one result (terrain ordinal) that needed catching. Recommend
  carrying it into 8d as a required step, not an optional add-on.
- **The retroactive-floor-check technique (Cell 12) is now cheap for any prior WO's residual** — worth a
  pass over WO8a's numbers too if WO8a ever computed a nested residual near a floor (it didn't; WO8a was
  descriptive only, so likely moot, but worth a one-line confirmation before 8d).
- **Collinearity gets worse, not better, at 8d.** High-gods (EA034) is tightly coupled to complexity in the
  literature (the big-gods debate) — expect a fourth near-collinear cultural variable, and the same
  concentration-at-the-extreme pattern this WO found at the state tail.
- **Enclosure/circumscription remains the real open terrain question**, unbuilt. This WO's null (on
  ruggedness) plus WO's own named trigger (an ambiguous complexity null, which did *not* happen here) means
  the enclosure build is not urgently triggered by this result — the climate-envelope test came back
  positive, so there's no "ambiguous null" calling for it yet.
