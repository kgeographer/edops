# WO18 — Transition-character comparator + spanning-10 validation

**Phase:** Areas · **Sub-phase:** neighborhoods → pattern experiment · **Date:** 2026-06-27
**Depends on:** WO17 (per-neighbor divergence result; border-bearing; sign-pattern + mean_abs/max_abs per variable). WH Cities table in-db (258 OWHC members).
**Branch:** continue the ring branch.

---

## Goal

Build a fixed-width, threshold-stable, **non-directional** per-city **transition-character vector** from the WO17 per-neighbor result, and validate it on **10 deliberately maximally-spanning** WH cities: does the vector cleanly separate places of known-different environmental setting? This is the comparator-validation gate before scaling to 20/50/100, where the actual pattern hunt happens.

The aim is a hunt for classes **without presuming any exist** — let structure emerge from the sample (the ontology discipline: classes come from the source, not imposed). WO18 does not cluster or name anything; it confirms the instrument can tell diverse places apart and captures the covariates a later clustering will need.

---

## Part 1 — Select the spanning-10

The 10 must span environmental settings as widely as possible (the point is to stress whether the comparator separates known-different places — if it can't separate a desert seam from a boreal river, the approach needs rethinking before any M5 time is spent on 50).

**Route A (preferred if simple):** Inspect `workbench.html` (and whatever serves its similarity data) to determine whether the existing **signature PCA space** supports a max-dispersion / farthest-point query — i.e., pick ~10 cities that are maximally distant from each other in that space. If it does and it's straightforward, use it to draw the 10. *(Selecting by signature distance is just a diversity sampler — it gets spread-out inputs; it is **not** part of the transition analysis, which uses the transition vector. Selection space ≠ analysis space, and that's fine.)*

**Route B (fallback):** if the space doesn't expose this cleanly, use this candidate geographic spanning set, **reconciled against the 258 in-db** — substitute within the same biome/hydro cell for any non-member:

| City | Setting (biome / hydro) | Continent |
|---|---|---|
| Timbuktu, Mali | hot desert / Niger floodplain–desert seam (exorheic) | Africa [WO17] |
| Harar, Ethiopia | semi-arid tropical highland / Acacia bushland | Africa |
| Rome, Italy | Mediterranean / Tiber valley, montane-adjacent | Europe [WO17] |
| Edinburgh, UK | cool oceanic temperate / volcanic crag, estuarine | Europe |
| Kaifeng, China | temperate / Yellow River alluvial plain, loess | Asia [WO17] |
| Yazd, Iran | hot arid **endorheic** plateau / desert oasis | Asia |
| Luang Prabang, Laos | tropical monsoon / Mekong montane confluence | Asia |
| Cusco, Peru | high Andes (~3400 m) / Amazon headwaters | S. America |
| Cartagena, Colombia | tropical coastal lowland / Caribbean | S. America |
| Québec City, Canada | cold temperate–boreal / St. Lawrence, maritime-continental | N. America |

This set deliberately pairs near-neighbors-in-one-axis-but-far-in-another (Timbuktu lowland-arid vs Harar highland-arid; Timbuktu exorheic vs Yazd endorheic; Rome Mediterranean vs Edinburgh oceanic) so the comparator is tested on subtle as well as gross differences. Keep the three WO17 fixtures in the set for continuity — we already know their transition character, so they're a known-answer check.

---

## Part 2 — The transition-character comparator vector

Per city, collapse the variable-cardinality WO17 per-neighbor result into a **fixed-width** vector that is identical in shape across cities regardless of ring size. Per continuous variable, carry:

- `mean_abs` and `max_abs` of the signed center↔neighbor divergence (continuous, **threshold-free**);
- `sign_pattern` (all+ / all− / mixed) as a **derived label** for interpretation.

**Threshold discipline (important):** the `sign_pattern` / `n_sharp` notion rests on the provisional 10 pp threshold, never multi-fixture-calibrated. Across diverse cities that line could manufacture or erase structure. So: **cluster/compare on the continuous `mean_abs`/`max_abs`** (threshold-free); treat `sign_pattern` as an interpretive label, not a clustering input. If `sign_pattern` is used in any separation claim, verify it at 2–3 thresholds and report whether the separation is threshold-stable. Don't let a 10 pp line drawn at Timbuktu author the finding.

Directionality is **out** (agreed) — bearings stay in the WO17 result for later, not in the comparator.

---

## Part 3 — Run + validate

- Run `resolve_basin_ring` + the per-neighbor diagnostic (WO17 machinery, **bands A–E, L06 only**) for the 10.
- Build the comparator vectors.
- **First-look separation:** do the 10 vectors distinguish the deliberately-diverse places sensibly? A simple distance matrix / 2-D projection is enough — this is a *does-it-separate* check, **not** a clustering claim and **not** an archetype claim.
- **Capture covariates per city** for the later cluster-attribution question (is emergent structure environmental, biogeographic, or regional?): UNESCO region / continent, biome, aridity or Köppen class, drainage type (endo/exorheic), basin size, level (L06). These ride alongside the vectors; not used in WO18's separation check, recorded for the 20/50 run.

---

## Scope guards

- **No clustering, no classes, no archetypes** in WO18. The word "archetype" is earned (or not) at n=50–100, never at 10. WO18 validates the instrument and stages the data.
- **L06 only**; all findings explicitly "at L06." (AF.18 showed sign-patterns shift L06→L08; cluster structure found at L06 may reorganize at L08 — a later question, not assumed.)
- **Cluster shape left open** — when the hunt runs, the result may be discrete types *or* a continuous space with dense regions (the latter is a real and arguably more interesting finding, and the honest response object if it holds). Don't pre-decide.

---

## Deliverables

1. The spanning-10 (route A or B), with the workbench-space finding (does it support max-dispersion selection?).
2. Comparator builder: WO17 per-neighbor result → fixed-width threshold-free transition vector.
3. The 10 vectors + covariate table.
4. First-look separation (distance matrix / 2-D projection) and a plain read: does the comparator separate the diverse 10, yes/no.
5. Findings (AF.n), explicitly at L06: comparator behavior, separation result, any threshold-sensitivity seen.

---

## Acceptance / gate

- Spanning-10 selected (and reconciled against the 258 if route B).
- Fixed-width comparator builds for all 10 regardless of ring size.
- Separation check done on the threshold-free vector; threshold-sensitivity of any `sign_pattern`-based statement reported.
- Covariates captured.
- **Gate:** does the comparator separate the deliberately-diverse 10? **Yes →** proceed to the 20/50 hunt (next WO). **No →** the comparator (or the transition representation) needs rethinking before scaling. Either outcome is a result.

---

## Back to Opus

Round-trip on: the separation result (does the transition vector tell diverse places apart — and do the three WO17 fixtures land where their known character predicts?); any threshold-sensitivity in `sign_pattern`; and whether the workbench space gave a clean max-dispersion selector (useful infrastructure if so). The 20/50 scale-up — clustering, spatial-organization attribution, discrete-vs-continuous — is the next WO, gated on this one passing.
