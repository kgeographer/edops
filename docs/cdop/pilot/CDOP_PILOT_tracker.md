# CDOP Pilot — Phase tracker

**This is the living source of truth** for the CDOP Pilot phase: current state, roadmap,
and locked decisions. If any other CDOP document disagrees with this one about *where things
stand*, this one wins — for CDOP Pilot scope only.

**How to keep this current (and the logging convention).** The detailed, technical record of each work
order lives in its `wo{n}_findings.md`. This tracker — and the session logs — carry **top-level summary +
a pointer to that findings file**, not a re-derivation of it. (The WO1–WO8 sections below predate this
convention and are kept as-is; **new** WOs get a short summary paragraph + a `findings:` link, not full
detail.) On each WO close: (1) add/replace that WO's subsection under *Work orders*; (2) update its
*Roadmap* row; (3) reset the one-line *Last updated* stamp; (4) fold any settled forward-looking note into
*Locked decisions* or *Deferred* **in the same edit** — never leave a resolved question live elsewhere.
Keep *You are here* to the current WO only.

- **Location:** `docs/cdop/pilot/CDOP_PILOT_tracker.md`
- **Last updated:** 2026-07-27 — WO8d complete, accept gate PASSED (EA034 high-gods, the arc's first
  **exploratory**, not confirmatory, instrument). Headline: whole-group cohesion is substantially a
  two-lineage story (Atlantic-Congo + Nilo-Saharan, both related and environmentally coherent); outside
  that, a strong cross-family convergence case (three unrelated Siberian peoples, the tightest sub-group
  in the set) and an unexplained singleton residual (~14 societies) that is the arc's real carried-
  forward question. New infra: `scripts/cdop/distance_core.py` (factored distance module, first real
  consumer). Next step undecided — see *You are here*.

**Addendum, 2026-07-28 (post-freeze housekeeping, not a WO close — added from CITYKIN).** Before
revisiting this phase, read `note_societies-tab-vs-wo8.md` first: the Societies tab's EA042/EA034
filter + PCA-based "Basin clusters" coloring is pre-CDOP-Pilot legacy (built in `workbench.html`,
2026-01-18, inherited unchanged when `cdop_pilot.html` was cloned from it) and was never touched by or
connected to WO8a–d's correspondence-testing research, which was scoped notebook-only from WO8a's own
accept gate onward. Two tracks that happen to share variable names, not one stalled feature. The real
open question for a resumed CDOP Pilot — what the Societies tab should actually show now that WO8's
findings exist — is unspec'ed, not answered here.

## Table of contents

- What CDOP Pilot is
- Relationship to DEMO
- Roadmap
- You are here
- Work orders (reverse chronological):
  - WO8 — Environment↔culture correspondence testing (8a, 8b, 8c, 8d)
  - WO7 — Climate classes (instrument + Atlas tab)
  - WO6 — Similarity: non-compensatory → raw-curve backbone (6a, 6b, 6c)
  - WO5 — Context tab; temperature lens diagnostic; hide Similarity
  - WO4 — Four similarity instruments on shared probes
  - WO3 — Continuous precip lens + retire phase lens + scalar hygiene
  - WO1 — CDOP pilot page + L08 lens similarity
  - (WO2 / WO2a are roadmap-only; detail in `wo2*_findings.md`)
- Locked decisions
- Deferred / out of scope

---

## What CDOP Pilot is

CDOP (Cultural Dimensions of Place) is the companion component to EDOP within the
**Computing Place** research platform. EDOP delivers environmental signatures; CDOP delivers
cultural/comparative material. They are two components of one frame — the frame belongs to
Computing Place, not to either component.

The pilot stands up `cdop_pilot.html` as CDOP's own surface, separating it from the
Workbench (which was CDOP work filed under EDOPS by chronology). The first increment
replaces the broken PCA-composite environmental similarity on WH Cities with the
LENS_REGISTRY instrument at L08.

**Why the old similarity is broken:** the PCA composite returns Jerusalem (Arid/Desert) and
Acre (Mediterranean) among the top-5 neighbours of Mombasa (Extremely hot and moist). This
is the WO4d dilution finding displayed live, with the contradicting glosses printed alongside.
The Workbench link is disabled on the EDOPS home page for this reason.

Full rationale: `docs/cdop/CDOP_workplan_v1.md`. Feasibility evidence: `docs/edop/demo/wo_l08_findings.md`.

## Relationship to DEMO

DEMO is **frozen reference** (`docs/edop/demo/DEMO_tracker.md`, closed 2026-07-18).
Do not extend it. The **deferred items register is shared** and cross-phase:
consult at every step resumption, add rows there (`docs/design/deferred_items_register.md`).

---

## Roadmap

| Step | Branch | Status | Notes |
|---|---|---|---|
| WO1 — CDOP pilot page + L08 lens similarity | `cdop_pilot` | **blocked** | Plumbing complete; accept gate partial fail; blocked on WO3 |
| WO2 — Rainfall modality investigation | `cdop_wo2` | **complete** | Bimodal characterization; continuous (a1,b1,a2,b2) representation validated |
| WO2a — Continuous harmonic representation | `cdop_wo2` | **complete** | Part B pass; Part C clean on own-top-5 evidence; phase lens retired |
| WO3 — Continuous precip lens + retire phase lens | `cdop_wo3` | **stasis** | A+B complete (merged); C+D suspended; similarity approach under reconsideration |
| WO4 — Four similarity instruments on shared probes | `cdop_pilot` | **complete** | All six parts run; verdict: four instruments by output shape (ranked analogue w/ exclusion parameter, matched set, global/local typology). Design decision on architecture now pending. |
| WO5 — Context tab; temperature lens diagnostic; hide Similarity | `cdop_wo5` → merged to `cdop_pilot` | **A–D complete, E set aside** | Context tab shipped (percentiles, no ranking, no composite score). Part E waits on further similarity-architecture discussion with Opus, not a technical blocker. |
| WO6a — Non-compensatory similarity: notebook | `cdop_wo6` (cut from `cdop_pilot`) | **complete** | Exploratory only — no engine/API/UI change. All four parts run; verdict: percentile bands over absolute (Part B); instrument doesn't collapse to empty even at k=4 (Part C), but no data-driven prominence threshold or absolute-floor value exists (Part A) and `climate.precip` carries the same composite-distance compensation defect as `climate.temp` (Part D). Full findings: `docs/cdop/pilot/wo6a_findings.md`. |
| WO6b — Compare the curve, not its summaries | `cdop_wo6` | **complete (Opus-passed)** | Exploratory notebook. Compares the raw twelve-value curve directly (correlation) instead of scalars. Backbone found: correlation discriminates (A), modality is emergent not classified (B, the headline), Knoben ΔE agrees independently (C), the conjunction's load-bearing condition rotates by query (D), `s_d`/direct precip×temp correlation handle the phase question (E). No amplitude *scalar* survives; `cv`-band does. Corrected WO6a's Somalia flagship → low-*range* cause. Karl reframed the target to two discrete classes. Findings: `wo6b_findings.md`; handoff: `wo6_status_CC.md`. |
| WO6c — Similarity panel, rebuilt on the conjunction | `cdop_wo6c` (cut from `cdop_wo6`) | **engine + UI built, Karl-reviewed** | Scope: sandbox_v3 Similarity tab only. Part D: temp lens has **no shape term**. **Engine** (`find_conjunction`, separate from untouched `find_similar`; raw-curve index + arid gate; `/api/similarity/conjunction`), pinned to WO6b Cell 16 (`tests/test_conjunction.py`, 6 green). **UI**: painted set (shape-shaded members, unpainted non-members), declared per-variable bands (no ladder), size + spatial-spread readout, honest-empty, container line; respects L06/L08 toggle (feature-flagged `SIM_CONJUNCTION`, old panel kept). Removed dead `sandbox_v2`. Reviewed in browser 2026-07-23 (Tbilisi union, container toggle, SF shape hemisphere-blindness, SF equable-coast temp). **Deferred candidates:** `precip_temp_phase` condition + global climate-class map (both use the precip×temp correlation). WO: `wo6c_similarity-redux.md`; findings: `wo6c_findings.md`. |
| WO7 — Climate classes (class-relative instrument) | `cdop_pilot` (notebook) | **investigation complete** | Notebook `wo7_climate_classes.ipynb` (Cells 1–13). Two discrete axes computed per basin: **modality** (arid gate → cv gate → vectorized Knoben ΔE, validated grid==exact==WO6b on 9/9 synthetics + 11/11 probes) and **phase** (precip×temp correlation + 5 °C thermal gate). Phase map is textbook (equatorial gold, winter-rain belt, summer-rain). Verdict: **sound instrument, over-broad names** — the five Köppen-Med regions all appear (Med cell 63.5% "leak" into the Iran/C-Asia winter-rain belt), twin-rains cores right (Indonesia was L06 aggregation, returns 8× at L08; mid-latitude bimodal is real & scale-stable). Both sharpening dials tested (Cell 12 winter temp, Cell 13 aridity) — neither isolates Köppen-Med cleanly. WO: `wo7_climate-classes.md`; findings: `wo7_findings.md`. |
| WO7a — Label lock + build | `cdop_wo7a` (cut from `cdop_pilot`) | **complete — backend + Atlas UI, Karl-signed-off 2026-07-24** | Scope: sandbox only (`explorer.html` frozen; NOT `cdop_pilot`). **Labels (Option A):** cells compose from axis names (modality-first), aseasonal drops the phase term, classic names annotation-only — a test enforces no Köppen/Knoben name in any label. **Storage:** in-memory startup index (similarity/context family), persist-view sourced, L06 eager (~1.9 s) / L08 lazy (~18 s, never at boot) — CLAUDE.md § "How runtime data reaches the app". **Backend:** `app/db/climate_classes.py` (compute + index + `axis_values`/`class_lens`), `main.py` L06 load, routes `/api/explorer/climate-class` (Atlas) + `/api/similarity/climate-class` (place-anchored, tested, no UI yet), `tests/test_climate_classes.py` (8 green). **UI = the Atlas tab** (`sandbox_v3.html`): a place-independent global-views surface (climate classes first, extensible); flush-right cyan tab, left column swaps to a global-context panel; paints basin PMTiles via feature-state from the flat class dict (Map-tab pattern, no GeoJSON/`basin-geom`); views = Modality / Phase choropleths + Two-wet-seasons / cool-season-rain highlights. **Render decision (Issue 2):** two axis choropleths + client-side compose, NOT a ~20-colour cell choropleth (supersedes the WO's "three variables" wording). Sandbox similarity/climate-class track **closed**; UI/UX polish + example smoke tests deferred to a review pass. WO: `wo7a_label-lock-build.md`; findings: `wo7_findings.md`. |
| WO8a — Environment↔culture correspondence: descriptive probes (Societies) | `cdop_wo8a` (cut from `cdop_pilot`) | **complete — accept gate PASSED** | Descriptive notebook only (no engine/API/UI). Shared substrate (1,133 EA societies→L08 basin→`s`-signature, persisted `output/cdop/wo8a_substrate.parquet`); nested-bet PCoAs (Water⊂Climate envelope⊂Landscape) coloured by EA042 subsistence + WO7 modality. **EA042 separates cleanest in Climate envelope** (temperature opens the 2nd axis; Landscape's terrain smears). Part C: seasonality shape orthogonal to subsistence (refutes the WO's modality-class expectation; raw curve is the faithful rep). Part D crosstab corroborates (pastoralism→25% arid; fishers/gatherers→cool-wet). **Headline: environment sets bounds, not determination.** Decisions: bet=Climate envelope; seasonality=raw curve if any (non-load-bearing); keep Part D via crosstab. Next=WO8b (PERMANOVA/PERMDISP, within-family). WO: `wo8a_culture-probes.md`; findings: `wo8a_findings.md`. |
| WO8b — Environment↔culture correspondence: the first test (EA030 settlement fixity) | `cdop_wo8b` (cut from `cdop_pilot`) | **complete — accept gate PASSED** | Notebook + hand-rolled stats engine `scripts/cdop/dbperm.py` (PERMANOVA / db-RDA / Freedman–Lane partial / PERMDISP; `tests/cdop/test_dbperm.py` 10 green, validated vs closed-form ANOVA/regression F). Marginal fixity R²=0.213 (family-restricted); **nested \| subsistence R²=0.033 — 84% collapse into subsistence** (residual = no interpretable independent effect; fixity↔subsistence near-collinear). PERMDISP flags a breadth difference (mobile wider, breadth 1.76; sedentary narrower, breadth 1.06). Part D: rainfall timing dilutes (dR²=−0.084), not load-bearing. **Prediction confirmed** — temperature phylogeny-inflated (family p→0.020), aridity robust: the instrument-validation carry-forward headline. Substantive: settlement concentrates in a narrow favorable band — a target, not a floor (mobility the wide fallback across the margins it excludes). Reporting stance decided; effect-size floor open (Karl, before 8c) — **now set** (WO8c); a retroactive check confirmed this residual clears its own floor by 3.2–3.6× but reads the same way as WO8c's own numbers (necessary-not-sufficient; collinearity stands) — no change to this row's verdict. WO: `wo8b_fixity-test.md`; findings: `wo8b_findings.md`; exec: `wo8b_exec_summary.md`. |
| WO8c — Environment↔culture correspondence: political complexity (EA033) | `cdop_wo8c` (cut from `cdop_pilot`) | **complete — accept gate PASSED** | Notebook, `dbperm.py` extended with `return_null=True` (permutation-null R² distribution — the machinery behind the effect-size floor; `tests/cdop/test_dbperm.py` 14 green). New infra: `dplace.society_elevation` (point elevation, all 6,408 coordinate-bearing `dplace.societies`), `dplace.society_terrain` (point-window local relief, 1,133 EA societies). **Headline: complexity's raw climate link is weak** (unlike subsistence/fixity) — the real finding. **Nested \| subsistence(+fixity) R²≈0.017–0.018 (factor) / 0.010 (ordinal)** clears its own permutation-null floor (stability-checked at a second seed + 5× perms) but **not the collinearity bar**: the state tail is ~92% concentrated in one subsistence category and ~92% in one fixity category (Part A), so read as *no strong independent environmental signal*, not a positive finding — floor-clearing is necessary, not sufficient. Fixity as a covariate barely moves the residual either way (mediator concern moot for this trait). **Terrain (ruggedness) is a clean null** on both formulations once stability-checked (one apparent positive, R²=0.0078 vs floor=0.0077, flipped to null under the recheck — exactly the guard doing its job). A retroactive floor cross-check on WO8b's fixity residual (Cell 12) got the same necessary-not-sufficient reading — **no change to WO8b's record**. WO: `wo8c_political complexity-EA033.md`; findings: `wo8c_findings.md`; exec: `wo8c_exec_summary.md`. |
| WO8d — Environment↔culture correspondence: the high-gods look (EA034, exploratory) | `cdop_wo8d` (cut from `cdop_pilot`) | **complete — accept gate PASSED** | The arc's first **exploratory, not confirmatory** instrument — no predicted result, no effect-size floor; language family is **labeled, not permuted away** so transmission/convergence read directly, against a whole-sample backdrop. New infra: `scripts/cdop/distance_core.py` (factored distance module — 4 lenses, cohesion statistic, fully-random + family-restricted resampling baselines; `tests/cdop/test_distance_core.py` 10 green), first real consumer, not yet a named shared core. **Headline: substantially a two-lineage story.** Atlantic-Congo (n=15, 37.5% of the 40-society focus set) and Nilo-Saharan (n=4) are both genealogically related *and* environmentally coherent (100%/94% tighter than random); Sino-Tibetan (n=3) is a counter-example — related but not coherent (46%, chance). No per-lens whole-group cohesion clears both the random and family-restricted baselines at once (water: 95.25% vs random, 42.25% vs cousins — the Atlantic-Congo effect). **Two things sit outside that story**: a strong cross-family convergence case (3 unrelated Siberian peoples — Chukchi/Yakut/Yurak-Samoyeds — the tightest sub-group in the whole set) and an **unexplained singleton residual (~14 societies)** explained by neither lineage, whole-group climate, nor proximity — promoted to the primary carried-forward item after Karl/Opus review (framing-only revision, no numbers changed). **Hopi check** (sanity anchor, not a focus-class member) surfaced Hano/Navajo as nearest climate-space neighbors — two independently documented cross-family contact cases, unprompted — the strongest instrument-validation evidence in the WO, paralleled to WO8b's differential-deflation result. One bug caught and fixed mid-session (a family lookup queried the whole backdrop instead of the focus class; caught by row-count mismatch, fixed, verified against actual PCoA positions). WO: `wo8d_env-culture-highgods.md`; findings: `wo8d_findings.md`; exec: `wo8d_exec_summary.md`. |

---

## You are here

Phase opened 2026-07-18. Integration branch `cdop_pilot`; WO branches cut from it, merged back on accept.
**483 app tests pass / 14 skipped / 1 pre-existing fail** (full suite, 2026-07-27 WO8d gate;
`test_codebook_alignment.py::test_implemented_fields_accessible` — confirmed unrelated to CDOP work
across two sessions now, last touched by WO7/7a, not fixed here) plus `tests/cdop/` (24 green:
`test_dbperm.py` 14 + `test_distance_core.py` 10, new this WO).

**WO8, environment↔culture correspondence testing, 8a–8d complete.** 8a (descriptive), 8b (fixity), 8c
(political complexity), and 8d (high-gods — the arc's first **exploratory**, not confirmatory,
instrument) all passed their accept gates. **8d's headline:** whole-group cohesion among the 40
"active-but-not-supporting-morality" societies is substantially a two-lineage story (Atlantic-Congo +
Nilo-Saharan, both related and environmentally coherent; Sino-Tibetan a counter-example). Outside that: a
strong cross-family convergence case (3 unrelated Siberian peoples, tightest sub-group in the whole set)
and — the arc's real carried-forward question, per Karl's own framing after review — an **unexplained
singleton residual (~14 societies)** explained by neither lineage, whole-group climate, nor proximity,
with an explicit epistemic boundary (unexplained by environment and *shallow* — language-family —
ancestry; deep descent and undocumented diffusion remain un-subtracted). The Hopi check surfaced Hano/
Navajo as nearest neighbors — two independently documented cross-family contact cases, unprompted — the
strongest instrument-validation evidence in the WO. New infra: `scripts/cdop/distance_core.py` (factored
distance module, first real consumer, not yet a named shared core). Full detail: `wo8d_findings.md`;
plain-English: `wo8d_exec_summary.md`.

**Next step undecided.** No WO8e drafted; options on the table include a residual-characterization
follow-up on the singleton group (per 8d's own carried-forward item), a further EA034 sub-question, or a
pivot to a different phase. Prior arcs are complete: the similarity instruments (WO1–WO6c) and the
climate-class instrument (WO7/7a; Atlas tab shipped) — see their sections below.

---

## WO8 — Environment↔culture correspondence testing

The correspondence-testing arc asks: does a cultural trait covary with environmental setting, net of
shared ancestry and diffusion? WO8a calibrated the instrument on a positive control; WO8b ran the first
real test. Detailed technical record in the per-WO findings files.

### WO8a — descriptive probes (Societies) · `cdop_wo8a`, gate passed

**WO8a (2026-07-25, `cdop_wo8a`) opened the correspondence-testing arc** — the first environment↔culture
probe, and the first CDOP work to touch the D-PLACE societies since WO4. A descriptive notebook only
(no engine/API/UI): the shared society→basin→signature substrate + nested-bet PCoAs of EA042
subsistence. **Accept gate PASSED** (EA042 separates cleanest in the Climate envelope bet); the
instrument is calibrated. Standout finding — **environment sets outer bounds on culture, it does not
determine it**: one near-hard constraint (water for rain-fed agriculture), one soft gradient
(temperature), broad adaptability otherwise; rainfall seasonality is orthogonal to subsistence. Three
decisions locked (bet = Climate envelope; seasonality = raw curve if any, non-load-bearing; keep the
modality-standalone bet as a crosstab corroborator). Findings: `wo8a_findings.md`; exec summary for Opus:
`wo8a_exec_summary.md`.

### WO8b — first test: EA030 settlement fixity · `cdop_wo8b`, gate passed

**WO8b (2026-07-25, `cdop_wo8b`) is the first real test** — EA030 settlement fixity — and the first to run
the two controls WO8a deferred: the phylogenetic null (restricted permutation within language family) and
the metric decision. Built the hand-rolled, unit-tested distance-based stats engine `scripts/cdop/dbperm.py`
(PERMANOVA / db-RDA / Freedman–Lane partial / PERMDISP; `tests/cdop/test_dbperm.py`, 10 green) *before* the
notebook, validating pseudo-F against closed-form ANOVA/regression F. **Accept gate PASSED.** The
carry-forward headline is the **instrument validation** — the family control demonstrably bit, deflating
exactly the predicted axis (temperature's family-restricted p → 0.020, aridity holds); a method claim,
defensible with no anthropology. The substantive finding: settlement **concentrates in a narrow favorable band** — sedentary societies
cluster in wet/warm/low-seasonality country (breadth 1.06), while mobile societies range widely (breadth
1.76) across the dry/cold/seasonal margins the band excludes; a target, not a floor. ~84% of fixity↔environment is subsistence; the nested
residual is **no interpretable independent effect** (fixity↔subsistence near-collinear, so the 84% is partly
an overlap artifact — recurs in 8c). Decided reporting stance: confound-share is the headline, sub-floor
residuals are not "small real"; the effect-size floor is Karl's to set **before** 8c's number is seen.
Findings: `wo8b_findings.md`; exec: `wo8b_exec_summary.md`. **Next: 8c — EA033 political complexity**, WO
arriving 2026-07-26.

> **Note (2026-07-25):** an earlier draft of the WO8b write-ups asserted the *reversed* dispersion
> direction ("sedentary catholic / floor not target") from a per-group breadth number that had not been
> looked at; it propagated into findings, exec, and this tracker before Karl's cell run caught it. The
> direction above is the corrected, verified one (Cell 10 per-group means). Process lesson logged: no
> value is stated as a finding until read off actual output.

### WO8c — political complexity: EA033 · `cdop_wo8c`, gate passed

**WO8c (2026-07-26, `cdop_wo8c`) is the arc's first genuinely speculative test** — EA033 jurisdictional
hierarchy — the first trait with no pre-checkable answer (8a/8b were calibration). Built the effect-size
floor WO8b deferred to Karl: `dbperm.py` extended with `return_null=True` (the permutation-null R²
distribution), so the pre-committed rule (95th-percentile of that distribution) could actually be
computed, not eyeballed. Also built, on Karl's go-ahead mid-WO: `dplace.society_elevation` (point
elevation for all 6,408 coordinate-bearing `dplace.societies`) and `dplace.society_terrain` (point-window
local relief for the 1,133 EA societies), after confirming no local DEM raster exists but OpenTopoData's
batch API makes a grid sample cheap. **Accept gate PASSED.**

**Headline, after a language correction from Opus (WO author) on the first draft:** complexity's raw,
uncontrolled climate link is weak (R²=0.050, not even conventionally significant) — itself the real
finding, given how strongly subsistence and fixity tracked climate. What survives controlling for
subsistence (R²=0.017) and subsistence+fixity together (R²=0.018 factor / 0.010 ordinal) clears its own
permutation-null floor — stability-checked at a second seed and 5× the permutations, which is exactly
what caught the one false positive in this WO (terrain's ordinal trend, a 1.3% floor margin that flipped
to null on recheck) — but **clearing the floor is necessary, not sufficient**. The state tail is ~92%
concentrated in a single subsistence category and ~92% in a single fixity category, so there is almost no
independent complexity-variation left for a "net of" test to measure; the surviving residual should be
read as *distinguishable from noise, not separable from confound* — **no strong independent
environmental signal**, not a small positive finding. Fixity as a covariate barely moves the residual
either direction (the WO's mediator-vs-confound concern turned out moot for this trait). **Terrain
(ruggedness) is a clean null** on both formulations once stability-checked — narrows the terrain channel,
does not test circumscription (a different, unbuilt, relational variable).

**A cross-check, not a correction:** building the floor machinery made it cheap to retroactively apply
the same rule to WO8b's fixity residual (R²=0.0334/0.0108) — it clears its own floor by 3.2–3.6×, a wider
margin than WO8c's own numbers. Applying the identical necessary-not-sufficient logic, this does **not**
upgrade WO8b's residual to an interpretable independent effect either — WO8b's original characterization
stands, unchanged. **No edits to `wo8b_findings.md`, `wo8b_exec_summary.md`, or this tracker's WO8b
section or row.**

Findings: `wo8c_findings.md`; exec: `wo8c_exec_summary.md`. WO: `wo8c_political complexity-EA033.md`.
**Next: 8d — EA034 high-gods**, reframed exploratory rather than confirmatory (Karl + Opus).

### WO8d — the high-gods look: EA034, exploratory · `cdop_wo8d`, gate passed

**WO8d (2026-07-27, `cdop_wo8d`) is the arc's first genuinely exploratory instrument.** Karl pushed back
on continuing the confirmatory-PERMANOVA pattern for EA034 and, with Opus, reframed the WO around
instance-hunting: "is there an environmental thread among these societies, and is it more than shared
ancestry" — no predicted result, no effect-size floor. Two corrections to the confirmatory frame:
language family is **labeled, not permuted away** (transmission and convergence read directly, not
inferred from a residual), and a whole-sample backdrop makes "tight"/"distinctive" measurable. New infra:
`scripts/cdop/distance_core.py` (factored distance module — 4 lenses, whole-sample-fit standardization, a
cohesion statistic, fully-random + family-restricted resampling baselines; `tests/cdop/
test_distance_core.py`, 10 green) — the module's first real consumer, not yet promoted to a named shared
core (CITYKIN/TRACE remain forward references only). **Accept gate PASSED.**

**Headline: substantially a two-lineage story.** Of the 40 basin-joined focus-class societies (EA034
"active, but not supporting morality"), one lineage — Atlantic-Congo — is 37.5% of the entire set (15/40)
and is both genealogically related *and* environmentally coherent (100% tighter than random draws of the
same size); a second, smaller lineage (Nilo-Saharan, n=4) shows the same pattern (94%). A third
(Sino-Tibetan, n=3) is a useful counter-example — related but **not** environmentally coherent (46%,
chance) — shared descent does not uniformly predict shared environment. No per-lens whole-group cohesion
clears both the fully-random and family-restricted baselines at once (water: 95.25% vs random collapses
to 42.25% vs cousins — the Atlantic-Congo effect, same Galton-control logic as WO8b/8c applied without a
formal floor).

**Two things sit outside the two-lineage story, and matter more than a flat verdict would suggest.** A
strong cross-family convergence case: three genealogically unrelated peoples across Arctic Siberia
(Chukchi, Yakut, Yurak-Samoyeds — three different families, no shared ancestry) form the **single
tightest sub-group in the entire 40-society set** — real convergence or areal contact, not confirmed
which, a candidate for a domain-expert (Ruth) follow-up. And — per Karl's own reframing during review,
now the arc's primary carried-forward item — an **unexplained singleton residual**: ~14 societies sharing
the trait but explained by neither the dominant lineages, whole-group climate, nor proximity to each
other. **Epistemic boundary, stated explicitly in both docs:** "unexplained by environment and *shallow*
(language-family, ~6–10k yr) ancestry," never "unexplained by everything mundane" — deep descent and
undocumented diffusion remain un-subtracted candidates. Same scoping discipline as WO8c's circumscription
boundary.

**The Hopi check (a sanity anchor, not a focus-class member) produced the strongest instrument-validation
evidence in the WO.** Hopi's nearest non-family climate-space neighbors are Hano and Navajo — two real,
independently documented cases of cross-family cultural contact driven by shared geography — with no
history or contact information fed into the metric. Paralleled to WO8b's differential-deflation result as
the credibility asset licensing trust in the rest of the WO's spatial reads.

**One real bug, caught and fixed mid-session:** a named-family cohesion lookup first queried the whole
~1,133-society backdrop instead of the 40 focus-class members (Atlantic-Congo alone has 289 members
corpus-wide). Caught via row-count mismatch against the named cluster membership, fixed, and verified a
second way per Opus's review request — actual PCoA positions plotted per group, confirming the cohesion
numbers reflect real visual clustering/scatter, not just a corrected count.

Findings: `wo8d_findings.md`; exec: `wo8d_exec_summary.md`. WO: `wo8d_env-culture-highgods.md`.
**Next step undecided** — options include a residual-characterization follow-up on the singleton group
(8d's own primary carried-forward item), a further EA034 sub-question, or a phase pivot; see *You are
here*.

---

## WO7 — Climate classes (instrument + Atlas tab)

**WO6c merged to `cdop_pilot`.** Then **WO7** (`wo7_climate-classes.md`) built the class-relative
climate-class instrument and **WO7a** (`wo7a_label-lock-build.md`) locked labels + built the backend,
both on `cdop_pilot` (WO7 notebook-first, then `cdop_wo7a` cut for the build). **WO7a shipped the `Atlas`
tab (2026-07-24, Karl-signed-off)** — a place-independent global-views surface in `sandbox_v3.html`,
climate classes first. **The sandbox similarity / climate-class track is closed.** `cdop_pilot` similarity
(WH Cities) is a separate future thread Karl will take up with Opus. Findings: `wo7_findings.md`; the
Roadmap rows carry the full build detail.

### Corrections to the original (WO6c-review) proposal — recorded so the stale version is not re-derived

- The negative phase pole is **`cool-wet`** (Mediterranean), not "cool-dry" (that names the *warm-wet*
  pole). Med vs monsoon is separated by phase *sign*; the one-wet-season condition separates both from
  twin-rains.
- Rendering is **not** the `/explorer/categorical` DB pattern and **not** at index-load. The classes
  are a derived per-basin quantity from the persist-view curves; they live in an **in-memory startup
  index** (the similarity/context family), served by `/api/explorer/climate-class` +
  `/api/similarity/climate-class`. The Knoben grid is ~18 s at L08, so L08 loads lazily, not at boot.
- The cell is **not** a 20-color choropleth. Two axis choropleths + a client-side compose picker
  (WO7a Issue 2).

**`precip_temp_phase` as a conjunction condition** stays deferred — WO7 validated the precip×temp
quantity as a *map*; wiring it as a WO6c lens condition is a separate decision (`wo6c_findings.md`).

---

## WO6 — Similarity: non-compensatory bands → the raw-curve backbone

### WO6a — non-compensatory instrument (notebook) · `cdop_wo6`, complete

**WO6a took up the gated percentile-vector idea directly, and is complete.** `cdop_wo5` merged
back to `cdop_pilot`; `cdop_wo6` cut for this step. `notebooks/cdop/wo6a_noncompensatory.ipynb`
ran all four parts from `wo6a_notebook.md`. Headline results (full detail:
`docs/cdop/pilot/wo6a_findings.md`):

- **Part A** — corpus-wide prominence-sweep peak-counting (vectorized reimplementation of WO5's
  4-probe script, validated exact-match before scaling up) beats `R_dbl` on every mechanism
  checked, including a new one (`R_dbl` can't see bimodality whose two peaks aren't ~6 months
  apart — a real Tennessee case it misses that peak-counting catches). But there is no
  data-driven prominence threshold (the corpus-wide sweep never plateaus) and no absolute-floor
  value that avoids trading arid-noise false positives (a 20mm floor fixes desert-noise
  false-bimodal calls) against real-modest-signal false negatives (that same 20mm floor misses
  Somalia's genuine Gu/Deyr two-monsoon pattern; loosening to 10mm fixes Somalia but partially
  reopens the arid-noise problem). Open candidate for WO6b: a relative-to-annual-total floor
  instead of a fixed mm value.
- **Part B** — percentile bands beat absolute bands. Both predicted failure modes were confirmed
  with real numbers (absolute: ~7–21× count swings at fixed physical width; percentile: 8–50×
  swings in physical width at roughly fixed count, worst for precipitation's right-skew). The
  WO's hoped-for resolution — that conjoining all three variables might let absolute "win
  outright" — didn't happen.
- **Part C** — the proposed instrument (3 percentile conditions + modality gate) does not
  collapse to an empty result set even at its tightest tested tolerance (sparsest case: 3
  matches). But the modality gate's restrictiveness is highly asymmetric — it barely restricts a
  query in the common ~82%-of-globe unimodal class, and restricts a rare bimodal query (George
  Town) hard — not a uniform k+1 tightening, and WO6b needs to account for that explicitly.
- **Part D** — `climate.precip` has the same composite-distance compensation defect WO5 Part A
  found in `climate.temp` (loose stringency admits basins at 0.27×–3.87× the query's actual
  rainfall because harmonic shape agrees). Locked as a decision below — this is now confirmed on
  both active Climate lenses, not just `climate.temp`.

### WO6b — compare the curve, not its summaries · `cdop_wo6`, complete (Opus-passed)

**WO6b took a different tack and it is the one that worked** — the first thing in the whole
similarity arc that mostly did. Rather than tune the non-compensatory instrument's parameters, WO6b
stopped compressing the twelve monthly values into scalars and compared the **raw twelve-value curve
directly** (Pearson correlation on mean-centred monthly precipitation). `cdop_wo6` continued;
notebook `notebooks/cdop/wo6b_compare_curves.ipynb`, all five parts run. Full findings:
`docs/cdop/pilot/wo6b_findings.md`. Opus reviewed and passed WO6b complete. Headlines:

- **Part A — profile correlation discriminates.** U-shaped pairwise distribution (not massed near
  1.0); rank-decay splits cleanly by modality — distinctive-shape queries rank strongly, generic
  single-peaked queries land in dense near-tie neighbourhoods (shape-space autocorrelation, WO4
  Part 1 restated). Ranks 1–10 are near-ties for every probe: the signal is "~100 vs ~1000", not "a
  single best match" — same conclusion Context reached from the other direction.
- **Part B — modality is emergent, not classified. The strongest result.** With nothing about peak
  count in the metric, correlation returns same-modality neighbours anyway (top-50 same-class share
  92–100% vs a 17.4% base rate). The prominence-threshold problem WO6a Part A could not solve is here
  **dissolved** for the cases that matter. All known-answer probes pass (Timbuktu→single-monsoon,
  George Town→twin-peaked, Somalia→two-rains highlands, Tennessee→coherent local).
- **Part C — Knoben ΔE (published, threshold-free) agrees with peak-counting on 9/11 probes**,
  independently. Faithful implementation, validated on synthetics. Made three-way (adds ASEASONAL /
  UNDETERMINED). The WO's own predictions that Mombasa/George Town would fail were wrong — both come
  out bimodal; the equal-amplitude breakdown lands past 2:1 asymmetry.
- **Part D — the conjunction's load-bearing condition rotates by query.** Every condition (shape,
  magnitude, temperature level/range, amplitude) is the tightest one for some probe and none for
  all — the anti-fragile property a non-compensatory checklist should have, and the strongest single
  argument the design is right. No amplitude *scalar* survived (`cv` explodes on dry zeros,
  `delta_P`/`rel_amp` collapse on bimodal), but `cv` as a per-query *band* is sound and non-redundant
  with magnitude.
- **Part E — `s_d` (precip–temp phase) is the hemisphere instrument; the shift-max trick is dead
  weight** (best shift is always 0). And Karl's session reframe: the target EDOPS needs is two small
  *discrete* classifications, not a continuous similarity score — {aseasonal / 1-season / 2-season}
  and {warm-wet / cool-dry / neither}. WO6b already reaches both; the second is served cleanly by
  **direct precip×temp correlation** (verified Cell 19: 7/7 sign agreement with `s_d`, and defined
  for the 2,694 bimodal basins where `s_d` is not). Handoff to Opus: `docs/cdop/pilot/wo6_status_CC.md`.

WO6b also **corrected `wo6a_findings.md`**: Part A's "no correct floor value" conclusion stands, but
Somalia was the wrong flagship (its L06 basin is 87 mm/yr, arid-gated), the binding condition is low
seasonal *range* not aridity (Tennessee is the right example), and Mombasa's miss is a *fraction*
problem not a floor one. Amendment applied to `wo6a_findings.md`.

### WO6c — similarity panel, rebuilt on the conjunction · `cdop_wo6c`, engine + UI built

Rebuilt the sandbox_v3 Similarity tab on the WO6b conjunction (engine `find_conjunction` + UI), Karl-
reviewed in browser 2026-07-23. Full detail in the Roadmap row and `wo6c_findings.md`. Deferred
candidates from the review: a `precip_temp_phase` condition and a global climate-class map (both use the
precip×temp correlation) — the latter became WO7.

---

## WO5 — Context tab; temperature lens diagnostic; hide Similarity

**Work order:** `docs/cdop/pilot/wo5_context-panel.md`. **Branch:** `cdop_wo5` (cut from
`cdop_pilot`). Findings: `docs/cdop/pilot/wo5_findings.md`.

### Part A — Temperature lens diagnostic

Neither of the WO's own two predicted outcomes held. `climate.temp`'s Mahalanobis metric is
uniformly looser at Tbilisi's position in variable space than at the Kaifeng control, not
selectively broken on `tmp_concentration` as hypothesized — and that looseness reflects real,
substantial, globally-consistent climatic diversity at any fixed mean temperature (std of seasonal
amplitude is 6–9°C at every 5°C temperature band, corpus-wide), not a Tbilisi-specific anomaly.
The mechanism that actually explains the WO1 false-match complaint: the composite "regime"
distance lets shape variables (`tmp_seas_amp`, `tmp_concentration`) compensate for a mismatch on
absolute level (`tmp_dc_syr`) — at `moderate` threshold, Tbilisi's admitted set spans −3.9°C to
+14.9°C, nearly 10°C off in either direction, all under one "Temperature regime" label. At
`strict` the same lens behaves exactly as labeled (±3°C both dimensions) — the threshold, not the
metric or the variables, determines how much compensation is tolerated. Not a bug: the arithmetic
is correctly computed against the real covariance structure; the label promises more than the
composite distance delivers at wide thresholds.

### Part B — Context data path

New module `app/db/context.py`, routes `GET /api/context` and `GET /api/context/population`. Same
architecture as the similarity index (in-memory, loaded at startup) but reports each of 7
variables independently — global percentile, within-radius percentile, no composite distance, no
ranking. Cross-validated against WO4 Part 5's independently-computed numbers (agreement within
~1.6 percentage points). Basin representative point is `ST_PointOnSurface`, not `ST_Centroid`
(the WO17/18 centroid-outside-polygon precedent). Radius/level combination for the UI settled by
a 258-city density check, not the initial 4-probe guess that looked like an L08-wide problem: it
isn't — L06 stays under the ~5,000-basin WebGL budget at every radius; L08 does too through
1000km, but 99.2% of a geographically diverse sample exceeds budget at L08/2500km specifically.
**Locked:** both levels offered at 250/500/1000km; 2500km available at L06 only, enforced
server-side.

### Part C — Context tab UI

Table (value + two percentiles per row) + radius control + MapLibre choropleth of the radius
population, colored by whichever row is selected. Color ramps aligned with the existing Map tab's
`applyBasinVar` convention after Karl caught a real inversion (moisture variables were backwards —
dry mapped to blue, should be red) and requested dedicated ramps for non-climate axes: a terrain
(hypsometric) palette for elevation/slope, a light-grey-to-purple sequential scale for seasonal
temperature range (a magnitude of swing, not a warm/cold axis). Left-column Map-tab legend now
hidden while any other right-column tab is active — previously stayed visible regardless of tab,
a state-management gap Karl caught by inspection.

Plausibility-checked against San Francisco: confirmed a second, independent container-problem
instance (11,378 km² L06 basin, elevation range −14m to 1,588m, nothing like the city itself).
**Karl's correction, worth keeping over the WO4-era framing of this same effect:** the
container/basin-size effect is not a measurement problem — a basin-scale average is a correct,
direct read of the source data; there is nothing to fix, because there is nothing wrong. Context's
design (no ranking, no composite score) is the right instrument for surfacing that fact honestly.
Verdict: Context "does its advertised job more effectively than Similarity."

### Part D — Blurb

Rule-based, no API call, computed client-side from data the table already fetched. Selection rule
reverse-engineered from the WO's own worked example (three distinct cases, not one template —
local-extreme gets exact numbers, global-extreme gets a rounded bucket, a material-but-not-extreme
gap gets a directional clause with no number; everything else drops rather than burying the
finding under a sentence per row). Two real bugs found via Karl's live testing and fixed: (1) the
flagship Tbilisi finding silently missing at the tab's own default radius (500km) because the
local percentile sat a hair above the strict extreme cutoff — fixed by splitting the threshold,
global stays strict at 10 (matches the WO's literal wording), local loosened to 15; (2) the
basin-naming/disambiguation sentence only fired from the one template that happened to trigger it,
so L08 blurbs (whose percentiles rarely reach either extreme bar) never said what they were
describing — defeating the entire point of naming the basin. Fixed by making the disambiguating
lead sentence unconditional, independent of which findings follow.

### Part E — not blocked, deliberately set aside

Karl wants further discussion with Opus before deciding what happens to the Similarity tab —
WO5 answered the WO4 reconsideration one way (Context, a structurally different instrument), but
a parallel thread is still open: a percentile-vector instrument with modality as a hard
eligibility gate rather than a weighted axis, discussed mid-WO5 and logged as a detour in
`wo5_findings.md`, not built. Similarity stays live, unhidden, exactly as before. Revisit once
that conversation lands.

---

## WO4 — Four similarity instruments on shared probes

**Work order:** `docs/cdop/pilot/wo4_similarity-studies.md` (approved 2026-07-20)
**Branch:** `cdop_pilot`. Notebook: `notebooks/cdop/wo4_similarity-studies.ipynb` (complete, all
six parts run). Full findings: `docs/cdop/pilot/wo4_findings.md`.

Tests whether "similarity" is one instrument or four (analogue / analogue net of geography /
matched control set / typological position) on seven probe basins (the WO's six plus Santiago,
added for Southern Hemisphere coverage), plus a Part 0 measuring how often the L06/L08
basin-container mean diverges from actual site elevation across historically significant
settlements.

### Prerequisite — D-PLACE schema audit (complete 2026-07-20)

Part 3 (matched control set, addressing Galton's problem for the eventual D-PLACE
correspondence test) needs a trustworthy society↔basin join and a phylogenetic proxy. Full
findings: `data/dplace/dplace_audit_findings.md` (gitignored — data-adjacent working doc).
Follow-up EDA: `notebooks/cdop/dplace_eda.ipynb`.

Headline: the core CLDF tables (`societies`, `data`, `variables`, `codes`, `contributions`)
are a complete, exact, current import of D-PLACE CLDF v3.1.1 — not the stale hodgepodge
suspected going in. `dplace.societies` (6,684 rows) holds 4,085 `languoid` scaffold rows plus
2,599 real `society` rows across **seven** independent ethnographic samples (EA 1,291; ccmc
410; binford 339; sccs 186; wnai 172; carneiro4 127; carneiro6 74) — `cdop_pilot`/workbench
currently surfaces only the EA slice (via `contribution_id='dplace-dataset-ea'`), which is why
the app shows 1,291 against the table's 6,684.

**Locked decisions:**

- **EA-only for WO4 Part 3.** `xd_id`/`glottocode` cross-checks (`dplace_eda.ipynb`) show 41.8%
  of EA's 1,291 societies (540) have a same-culture match in another sample — 395 via `xd_id`
  to Binford/SCCS/WNAI, 281 via `glottocode` to ccmc/carneiro4/6 — and carneiro4/6 mostly
  duplicate EA outright (83–86% overlap; two editions of the same source). Pooling would
  overcount and needs real dedup work. EA is the one sample with existing basin/bioregion
  linkage (`society_basin`, `society_spatial`) and no internal duplication problem of its own.
- **`society_basin` L06 backfill: still held.** Only L08 rows exist (1,133 of 1,291 EA
  societies, 87.8% — matches Part 3's own cited figure). Not needed — Part 3 runs at L08 only.
- **Family crosswalk: built in Part 3, not held anymore.** 85 Glottolog family tree files on
  disk parsed by regex (leaf glottocodes only, no tree-topology parsing) → 1,245-glottocode
  crosswalk. Matching on raw `glottocode` alone only resolved 74.3% of EA societies to a
  family; CLDF's `language_level_glottocodes` field exists specifically for this and raised it
  to 92.6% (1,049/1,133). Detail in `wo4_findings.md` Part 3.
- **D-PLACE enrichment (pooling variables from the other six samples onto EA societies via
  `xd_id`/`glottocode`, not adding new society rows) logged as deferred**, not built now:
  `docs/design/deferred_items_register.md` § CDOP — D-PLACE data.
- **Two dead scripts deleted**: `scripts/edop/dplace_env_correlations_{signature,exploratory}.py`
  referenced a `dplace.societies.basin_id` column that doesn't exist in the current schema and
  would error if run. Superseded by `app/api/routes.py`'s `/societies` route.
- **Deferred items register relocated**: `docs/design/areas/deferred_items_register.md` →
  `docs/design/deferred_items_register.md` — it was never Areas-specific, just nested there.
  All full-path references repo-wide updated in the same edit.

### Notebook setup decisions (resolved)

- **Part 0's "WHG settlement corpus" scope**: full `gaz.whg_gaz` (1.5M rows) was infeasible
  against the free elevation API. Resolved to two corpora, matching the WO's own proviso to
  count exposure in units of use — WH Cities (254/258) **and** D-PLACE EA (1,133/1,291) — run
  side by side, not either alone.
- **A real bug found and fixed early**: the notebook's first pass used only the 4 shape
  features `(a1,b1,a2,b2)` with raw Euclidean distance. Production `climate.precip`
  (`app/db/seasonality.py` — the WO text's `app/db/similarity.py` doesn't exist) actually uses
  5 features including `log_pre_mm_syr`, Euclidean on **z-scored** variables. Fixed; surfaced
  by spurious ~17,500 km "matches" for George Town before the fix. Full detail in
  `wo4_findings.md`.

### Results (Parts 0–6) — full detail in `wo4_findings.md`

- **Part 0**: L08 basin nested in (or, for Mombasa, exactly equal to — HydroBASINS' hierarchy
  terminates early for some basins) its L06 parent, confirmed for all 7 probes directly against
  geometry. Corpus-wide exposure (Part 0B): container mismatch is **a substantial share, not a
  thin tail**, even at L08 — 13.4% (EA) to 14.6% (WH Cities) still show a >2°C implied
  temperature gap at the better level.
- **Part 1**: 6 of 7 probes are entirely local in their unrestricted top-10 (autocorrelation,
  not analogy). Santiago's exception (Western Australia wheatbelt matches) is a genuine,
  textbook Mediterranean-climate teleconnection.
- **Part 2**: Mombasa → Guitri, Ivory Coast replicates WO2a's own validated Abidjan finding.
  Tbilisi and George Town show single distant matches that don't change across any exclusion
  radius from 250–5000 km — an unexplained pattern, noted for follow-up.
- **Part 3**: matched-control-set construction (Galton's problem instrument, `EA042` as a
  smoke test) works — 37 matched pairs found (997 usable societies). Known limitation, not
  fixed: some pairs share a "b" partner from the same real-world cluster counted more than once
  (~30–32 genuinely distinct once collapsed).
- **Part 4**: `pre_modality`'s distance-to-boundary confidence measure is actively misleading —
  Timbuktu's known-artifact "bimodal" reading (WO2a) shows the *largest* margin of any probe,
  while Mombasa's validated real bimodal case shows the *thinnest*. Mombasa and George Town land
  in the identical bioclimate bucket despite meaningfully different continuous-lens values —
  categorical typology is coarser than the continuous lens, concretely.
- **Part 5**: local-anomaly percentiles independently reconfirm the container problem for
  Tbilisi and Augsburg (both collapse to the bottom ~3% of their own 1000 km region on
  temperature despite unremarkable global percentiles) — a third, unrelated method landing on
  the same fact Part 0 and the original visual review already established.
- **Part 6**: Jaccard(Part 1, Part 2) = 0.00 for 6 of 7 probes (mechanically guaranteed once
  Part 1 showed those probes were all-local) and 0.25 for Santiago (real convergence — Part 2
  independently rediscovers the same distant Western Australia matches Part 1 found
  unprompted).

**Overall verdict**: four instruments distinguished by output shape, not by whether geography is
excluded — ranked analogue (Parts 1–2 unified; exclusion radius is a parameter of this one
instrument), matched control set (Part 3), global-typological position (Part 4),
local-typological position (Part 5). Six of seven probes returning all-local top-10s at L08 is a
measurement of those places, not a failure of the instrument; Part 6's six zero-Jaccard cells
follow mechanically from Part 1's own results and aren't independent evidence for anything
(Santiago's 0.25 is the one informative cell). Geography exclusion answers a second question a
user may ask — worth a control, default off — not a precondition for the first question to mean
anything. **Next step is a design decision** on what this means for the lens registry /
similarity architecture (e.g. whether a lens needs a declared geography-inclusion argument, not
just a variable set) — not further investigation. Not made here; needs Karl/Opus review.

---

## WO3 — Continuous precip lens + retire phase lens + scalar hygiene

**Work order:** `docs/cdop/pilot/wo3_retire-phase.md`
**Branch:** `cdop_wo3` (merged to `cdop_pilot` 2026-07-20)

### Parts A+B — Complete

**Part A** — `climate.precip` feature set replaced: `(pre_mm_syr, pre_concentration)` →
`(log_pre_mm_syr, a1, b1, a2, b2)`. Continuous harmonic form; no threshold in feature
construction; log total keeps magnitude independent of shape. `_compute_derived()` rewritten.
Provisional L06 thresholds set (strict: 0.25, moderate: 0.60, loose: 1.20); CDF
recalibration deferred.

**Part B** — `climate.phase` retired from `LENS_REGISTRY` (status → `"retired"`).
Deprecated `/api/seasonality/similar` route removed. Dropdown removed from `cdop_pilot.html`.
Phase blurb block removed from `sandbox_v3.html`. All defaults updated to `climate.precip`.

### Parts C+D — Suspended

Scalar hygiene (`pre_peak_month`, `pre_concentration` rename, narrative fix) and the
monthly-profile glyph are suspended. Reason: similarity approach is under reconsideration
before further investment.

### Problems discovered during map review (2026-07-20)

Two distinct problems with the **temperature lens** found during visual review:

**1. `climate.temp` Mahalanobis distortion.** At moderate threshold (0.75), Tbilisi returns
852 basins including coastal Norway — wrong, as coastal Scandinavian basins have amplitude
8–12 °C vs Tbilisi's 21.7 °C. The global covariance matrix is dominated by the
mean-temperature/latitude correlation, tilting the Mahalanobis ellipse so that amplitude
differences become secondary. The strict threshold (0.25) produces geographically coherent
results. The moderate-to-strict jump (3×) is too large and crosses a distortion boundary.
`climate.temp` thresholds were never CDF-calibrated; carried over from WO7 without review.

**2. L06 container-constitutes-the-place.** Tbilisi city mean annual temperature ~13.8 °C;
L06 basin reports 5.3 °C. The 8.5 °C gap is because the basin extends into the Greater
Caucasus at 3,000–5,000 m. The similarity query answers "what is similar to the upper Kura
headwaters?" not "what is similar to Tbilisi?" This is inherent to L06 for mountain-valley
cities; L08 would give a smaller, more representative basin. The sandbox similarity tab is
hardwired to L06 (two lines) regardless of the level toggle — an oversight noted but not yet
fixed.

Problem statement for Opus drafted (session_log_20260720.md).

---

## WO1 — CDOP pilot page + L08 lens similarity

**Work order:** `docs/cdop/pilot/wo1_cdop-pilot.md`
**Branch:** `cdop_pilot` (cut from `cdop`)

### Parts

**Part A — Phase scaffolding:** ✓ Phase folders exist (`docs/cdop/`, `notebooks/cdop/`,
`scripts/cdop/`, `output/cdop/`, `sql/cdop/`). This tracker created. DEMO_tracker.md header
scope-qualified.

**Part B — `cdop_pilot.html`:** in progress
- Cloned from `workbench.html`
- Tabs retained: Societies (active default), Ecoregions, WH Cities
- Tabs dropped: Main, Basins, WH Sites
- Route added: `GET /cdop` → `cdop_pilot.html`
- Old `/workbench` route and page untouched

**Part C — L08 lens index:** in progress
- `load_similarity_index(conn, level)` parameterized; level selects view + scalars table
- `_INDEX` dict keyed by level holds both L06 and L08 state at runtime
- Legacy L06 globals (`_HYBAS_IDS`, `_LENS_STATE`) kept in sync — existing callers unaffected
- `find_similar()` gains `level` (default 6) and `filter_hybas_ids` parameters
- `main.py` lifespan loads L06 then L08 at startup (~4 s, ~17 MB for L08)
- Level tables: L06 → `v_basin06_persist_rev2` + `basin06`; L08 → `v_basin08_persist_rev2` + `basin08`

**Part D — Wire `#whc-similar-env-btn`:** in progress
- New route `GET /api/whc-similar-env-lens?city_id&lens_id&limit=5`
- Uses L08 index, `mode='topn'`, corpus-restricted via `filter_hybas_ids`
- FK path: `gaz.wh_cities.basin_id → basin08.id → basin08.hybas_id`
- Dropdown items: Seasonal phase / Precipitation regime / Temperature regime (replaces A/B/C/D bands)
- Heading: "5 most similar cities in this collection" (corpus-relative; honest scope)
- Semantic similarity heading updated to same corpus-relative label
- 254/258 count shown in panel subhead

### Accept gate: partially met

Checked 2026-07-18. Results by lens:

- **Temperature regime — PASS**: Trinidad (Cuba), Camagüey (Cuba), Mompox (Colombia),
  Galle (Sri Lanka), Santa Ana de Coro (Venezuela). All tropical. ✓
- **Seasonal phase — FAIL**: Split (Croatia), Ibiza (Spain), Vatican City appear in top 5.
  Three of five are Mediterranean. ✗
- **Precipitation regime — FAIL**: Augsburg, Salzburg, Kotor, Tinn dominate. Clearly wrong. ✗

Root-cause hypothesis: Mombasa has bimodal rainfall (Apr–May + Oct–Nov peaks). Unimodal
circular statistics (`pre_concentration`, `seas_phase_offset`) can't represent bimodal
patterns — the two peaks nearly cancel, making Mombasa look like a city with even year-round
rainfall. European cities with distributed rainfall score as nearest neighbours.

Jerusalem is absent from all three lenses — the specific PCA failure is fixed. The bimodal
limitation is a different problem. See `wo1_findings.md` for full analysis.

**Decision deferred to Opus review session.**

### Open / pending

- [ ] Similarity approach reconsideration — problem statement drafted; Opus review pending
- [x] Test suite green (584 pass, 50 skipped, 0 failed — 2026-07-20)
- [ ] Merge `cdop_pilot → cdop` on WO1 accept gate met

---

## Locked decisions

| Decision | Rationale |
|---|---|
| topN=5 for WH Cities | Threshold mode returns zero peers for 36–39% of cities at strict; loose temp returns median 148/254. topN=5 approximates empirical moderate scale for precip/phase. From `wo_l08_findings.md` Part D. |
| L06 thresholds not used at L08 | Counts inflate ~10×; `climate.temp/loose` returns 46% of all L08 basins. Recalibration deferred and not needed for this use case. |
| Corpus-relative label | "5 most similar cities in this collection" — scope is the 258-city corpus, not a global neighbourhood. Distinguishes from sandbox Similarity tab. |
| Old Workbench stays live | Rollback path; retire/redirect decision deferred. |
| Basins tab dropped but recoverable | Passed the inverted-query test; dropped as EDOP-side classification. Clone makes it recoverable. Not rediscovered as a new idea. |
| `climate.precip` features: continuous (a1,b1,a2,b2) | Identities verified to machine epsilon; Mombasa top-5 all East African with no modality filter; Abidjan recovered (R_dbl=0.246 < 0.30 threshold, continuous correct). No threshold inside feature construction. `pre_concentration` and `R_dbl` are redundant once components included — do not add. `same_modality` dropped. From WO2a Part B. |
| `climate.phase` lens retired | The lens was never one question: it bundled how-many-wet-seasons (now in precip lens), hemisphere-blind phase relation, and hemisphere-aware seasonal timing. Questions 2 and 3 cannot share a lens — each fix breaks the other's repair. Undefined across the equatorial belt where D-PLACE work is concentrated. Retired, not redesigned. Phase fork recorded in deferred register. From WO3 spec. |
| Phase fork recorded, not planned | Hemisphere-blind relation and hemisphere-aware timing are two distinct lenses. Neither is built until a use case asks for it. Analysis is done; do not re-derive. From `wo3_retire-phase.md` deferred register. |
| `climate.temp` composite distance lets shape compensate for level | At `moderate` threshold Tbilisi's admitted set spans −3.9°C to +14.9°C — a basin can be ~10°C off in either direction and still register as "moderately similar" if `tmp_seas_amp`/`tmp_concentration` agree. Not a bad threshold or bad variable; a Mahalanobis composite over a genuinely-correlated-but-noisy variable pair admits this at wide radii by construction. From WO5 Part A. |
| Context ships as a second instrument, not a Similarity fix | Context (percentiles, no ranking, no composite score) answers the WO4 four-instruments reconsideration one way; it does not replace, recalibrate, or redesign `climate.temp`/`climate.precip`. Similarity stays live, unhidden. From WO5 Parts A–D. |
| Context radius set: L06 all four, L08 capped at 1000km | 258-city geographically diverse density check (not the initial 4-probe guess, which looked like a general L08 problem and wasn't): L06 stays under the ~5,000-basin WebGL budget at every radius including 2500km; L08 does too through 1000km (worst case 4,579/5,000), but 99.2% of the same sample exceeds budget at L08/2500km specifically. From WO5 Part B. |
| Basin representative point: `ST_PointOnSurface`, not `ST_Centroid` | A plain centroid can fall outside a concave/crescent-shaped basin polygon — the exact WO17/18 failure mode (centroid-outside-polygon silently resolving to the wrong basin). Raised by Karl during WO5 Part B design review. |
| The container/basin-size effect is not a measurement problem | A basin-scale average is a correct, direct read of the source data — there is nothing to fix, because there is nothing wrong. Confirmed on a second, independent case (San Francisco, 11,378 km² L06 basin) beyond Tbilisi. Same shape of correction as WO4's locality reframe, applied to a different topic. Karl's correction, WO5 Part C. |
| `climate.precip` has the same compensation defect as `climate.temp` | At `loose` stringency Timbuktu's admitted set spans 51–736 mm/yr against a 190 mm/yr query (0.27×–3.87×); George Town and Mombasa show the same pattern. Same mechanism as `climate.temp` (Locked decisions, above): level (`log_pre_mm_syr`) and shape (`a1,b1,a2,b2`) bundled into one composite Euclidean distance, so shape agreement buys tolerance on magnitude. Confirms the composite-distance problem is not `climate.temp`-specific. From WO6a Part D. |
| Percentile bands over absolute bands for a non-compensatory instrument | Both predicted failure modes confirmed with real numbers: absolute bands hold physical width fixed (~7–21× count swings across 8 probes); percentile bands hold count roughly fixed (8–50× swings in physical width, worst for precipitation's right-skew). Conjunction across all three variables did not resolve in absolute's favor as hypothesized — percentile is the more generous rule in 6/8 probes, and specifically more generous where the query point is unusual. From WO6a Part B. |
| No data-driven prominence threshold or absolute-floor value for peak-counting modality | Corpus-wide sweep (5–50% prominence, both levels) never plateaus — `RECOMMENDED_FRAC=0.20` is precedent-only. A fixed absolute floor cannot both reject arid-noise false-bimodal calls and accept real modest-magnitude bimodal signal (20mm floor fixes noise, misses Somalia's Gu/Deyr pattern; 10mm floor fixes Somalia, partially reopens noise). Untested candidate: a relative-to-annual-total floor instead of a fixed mm value. From WO6a Part A. |
| Compare the raw twelve-value curve, do not compress to scalars | Every prior similarity attempt compressed 12 monthly values to 2–5 scalars and failed *in the compression*. Correlation on the mean-centred twelve-value curve discriminates (Part A), passes every known-answer probe (Part B), and produces modality emergently — 92–100% same-modality neighbours vs a 17.4% base rate, with nothing about peak count in the metric (Part B). This is the backbone WO6c builds on. From WO6b Parts A–B. |
| Modality is emergent from shape, not classified by a threshold | The prominence-threshold problem WO6a Part A could not solve is dissolved: correlation returns same-modality neighbours without any modality term. WO6c may leave modality emergent rather than gate on it. Independently corroborated by Knoben ΔE agreeing with peak-counting on 9/11 probes (Part C). From WO6b Parts B–C. |
| No amplitude *scalar* works; `cv` as a per-query *band* does | Two dimensionless amplitude scalars both fail as global measures: `delta_P`/`rel_amp` collapse on bimodal curves (harmonic underfit), `cv` explodes on dry-season zeros. But `cv` as a ±band around the query's own value is self-protecting and non-redundant with the magnitude band (cuts hard *after* ratio). No single scalar means "how seasonal" across a Congo double-peak and a Sahel monsoon. From WO6b Part D. |
| Temperature lens has no shape term | WO6c Part D: temperature-curve correlation saturates within hemisphere (same-hemi pairwise median 0.963; 55% of pairs > 0.95; per-probe rank-decay spread ~0.003 extratropically, a 0.95 cut admitting ~9,000 basins). Where the seasonal swing is large the curve is the same July/January sinusoid everywhere — redundant with `temp_range` (amplitude) + hemisphere (phase). Where the swing is small (tropics, ~11% under 3 °C) the curve is noise (2–5 °C amplitude band: mean r 0.02, median −0.027). No amplitude regime is both meaningful and discriminating. Temperature lens = `temp_level` + `temp_range`. Contrast precipitation, whose curve genuinely varies in shape (WO6b). From WO6c Part D. |
| Target is two discrete classifications, not a continuous similarity score | Karl's WO6b reframe: EDOPS needs {aseasonal / 1-season / 2-season} and {warm-wet / cool-dry / neither}, not a continuous "how similar / how seasonal" number. WO6b already reaches both. The precip–temp phase axis is served cleanly by **direct precip×temp correlation** (verified, Cell 19: 7/7 sign agreement with `s_d`, and defined for the 2,694 bimodal basins `s_d` cannot handle). From WO6b Part E + Karl reframe. |
| Climate-class instrument is sound; the Köppen/Knoben names over-promise → Option A | The two axes produce climatologically-coherent classes, but *broader* than the named types: the five Köppen-Med regions all appear inside a bigger cool-season-rain belt (63.5% "leak" to Iran/C-Asia), the twin-rains cores inside a real mid-latitude-bimodal superset. Both sharpening dials tested — winter temp (Cell 12) and aridity (Cell 13) — and neither isolates Köppen-Med without discarding too much of the genuine article. Rename honestly, keep the two minimal axes. From WO7 Parts A–D + Diagnostics 1–3. |
| Class labels compose from the axes; classic names are annotation only | Cells get no prose name of their own — they comma-join the axis labels, modality-first (`One wet season, cool-season rain`); the phase term is dropped for `aseasonal` (flat rain → timing meaningless → `Even year-round`). Köppen-Mediterranean / monsoon / twin-rains appear only in the legend note as *subsets*, never as class names — a composed name cannot over-promise by construction. A test enforces no Köppen/Knoben name in any label. From WO7a label lock. |
| Climate classes live in an in-memory startup index, not parquet/table | They are a derived per-basin quantity from the persist-view curves (like the similarity/context/conjunction indices), so they join that family: computed at startup from `v_basin0{6,8}_persist_rev2`, held in RAM, served fast. L06 eager (~1.9 s); L08 lazy on first use (~18 s Knoben never at boot). Not parquet (that's for big cubes, e.g. LISA 107 MB) and not a DB table. Source map recorded in CLAUDE.md § "How runtime data reaches the app". From the WO7a data-source review. |
| Cell rendered as two axis choropleths + a compose picker, not a 20-color map | 5 modality × 4 phase ≈ 17 populated cells overflows a qualitative palette and is unreadable. The two axes each render as a clean choropleth (5- and 4-class); the combined cell is a client-side picker ("pick a modality + a phase, highlight it") — the same shape as the same-cell lens. Supersedes WO7a's "three variables (modality, phase, cell)" wording (Issue 2, Karl-approved). From WO7a build. |
| Global class distributions live on their own `Atlas` tab, not the Similarity tab | A class distribution is **not place-specific** — unlike every other sandbox feature — so it cannot sit in the place-centric Similarity dropdown (which means "similar to *this* place"). `explorer.html` is frozen and off-limits for new work. Resolution: a new place-independent `Atlas` tab in `sandbox_v3.html` — a global-views surface (climate classes first, extensible to other global paintings; a friendlier home than the Explorer). On entry the left column swaps from place controls to a global-context panel; no Resolve/signature needed. Rendered via the Map-tab tile + feature-state pattern (not the Similarity panel's GeoJSON/`basin-geom` path, which is place-specific and caps at 6000 ids). From WO7a UI, Karl 2026-07-24. |
| Effect-size floor rule, set and built (WO8c) | The floor = the 95th percentile of each test's own family-restricted permutation-null R² distribution (`dbperm.py`'s `return_null=True`), committed before 8c's number was seen. **Clearing it is necessary, not sufficient** — it means a result is distinguishable from noise, not that it is big enough or clean enough of collinearity to interpret as an independent effect (Opus correction, WO8c review, 2026-07-26). Any near-margin verdict gets a stability check (second seed + 5× permutations) before being trusted — it caught one real false positive in WO8c (terrain's ordinal trend). A collinearity read (cell counts, concentration at trait extremes) is required alongside every floor verdict, not optional. From WO8b (the deferred item) + WO8c (the build + the correction). |
| Exploratory instrument for instance-hunting traits: label family, don't null it; no floor (WO8d) | Confirmatory PERMANOVA (WO8a–c) permutes language family away and reports only the residual — correct for testing whether a trait generalizes, wrong for hunting *instances* of environment↔culture coupling. WO8d's instrument instead **labels** family (colors by it, tests each named lineage's own cohesion) so transmission and convergence are read directly rather than inferred from what a null hides, and reports cohesion **descriptively** against a whole-sample backdrop — no effect-size floor, no significance verdict, by design. Use this instrument (not the confirmatory PERMANOVA one) whenever the question is "is there a lead worth chasing," not "does this generalize." From WO8d, Karl + Opus reframe. |

---

## Deferred / out of scope

- Overall instrument validity — **answered by WO4** (four instruments by output shape; see WO4
  section above). WO5 answered part of the implementation question (Context ships as a second
  instrument). **What happens to Similarity itself is still open** — Part E deliberately set
  aside pending further Karl/Opus discussion, not a technical blocker; see WO5 section.
- Mahalanobis vs Euclidean for climate.temp; threshold CDF calibration for all active lenses —
  WO5 Part A found a real, evidenced mechanism (composite-distance compensation, see Locked
  decisions) but recalibrating or redesigning the metric was explicitly out of WO5's scope
- Wiring level toggle into the sandbox **Similarity** tab specifically (2-line fix, held) —
  Context's own level toggle was built correctly from the start (WO5 Part C), this bullet is
  about Similarity's still-inert one
- WO3 Parts C+D — scalar hygiene + monthly profile glyph (suspended pending approach decision)
- L08 threshold recalibration
- Semantic-similarity calibration
- Ecoregion IDs in the signature
- Retiring or redirecting the old Workbench page
- Terrain lens group (open; decide after WO1)
- Any new tab, dataset, or UI restructuring
- Building the non-compensatory instrument itself (WO6b) — WO6a (raised by Karl mid-WO5, logged as
  a detour in `wo5_findings.md`) tested the idea exploratory-only in a notebook and closed with a
  recommendation (percentile bands) plus two open design points (no clean prominence/floor value;
  the modality gate's asymmetric bite); building it as an actual lens is WO6b, not done here
- CDOP — D-PLACE enrichment (pool the other six samples onto EA societies), and CDOP — similarity
  (`precip_temp_phase` lens condition): both parked in `docs/design/deferred_items_register.md`.
- **WO8d's singleton-residual follow-up** — a residual-characterization query (distinct in kind from the
  cohesion look done in WO8d) on the ~14 EA034 focus-class societies unexplained by lineage, whole-group
  climate, or proximity: does that specific set cohere on anything else (a different environmental
  dimension, another EA variable, or nothing)? Not started; Karl's own framing names this as the arc's
  real next question (`wo8d_findings.md` § Carried forward).
- **WO8d's Siberian-trio lead** — three unrelated peoples (Chukchi, Yakut, Yurak-Samoyeds), tightest
  cross-family sub-group in the WO8d set; candidate for a domain-expert (Ruth) check on independently
  documented areal contact before any confirmatory follow-up. Not started.
