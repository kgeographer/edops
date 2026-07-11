# WO19 — Scaled transition-character run (50 cities): anchoring, stability, first cultural probe

**Phase:** Areas · **Sub-phase:** neighborhoods → pattern experiment · **Date:** 2026-06-27
**Depends on:** WO18 (comparator validated; gate PASS; ST_PointOnSurface centroid fix; 29-var universal intersection; transition space confirmed orthogonal to signature PCA).
**Branch:** continue the ring branch.

---

## Goal

Scale the transition-character comparator from 10 to **~50 WH cities** and ask the three questions that decide whether this branch earns its keep — not whether the instrument works (WO18 settled that), but whether the structure it finds is **real** and whether it **touches anything historical**:

- **(a) Anchoring** — does any emergent clustering line up with external covariates it wasn't built from?
- **(b) Stability** — does the clustering survive perturbation of the sample and the representation, or is it a method artifact?
- **(c) Cultural probe** — does transition-cluster membership correlate with *any* attribute of the cities as historical places?

These run **together, in one pass**, before any cluster is interpreted — so the tests are honest checks, not things we hope to pass after falling for a pretty clustering. (Same discipline as the threshold check: don't let the story author the finding.)

---

## Framing — what this run can and cannot conclude

A clustering algorithm will **always** return groups from 50 points in 58-dim space, and a geographer will **always** be able to tell a story about them. So a legible clustering is not evidence of anything. The verdict comes from (a)+(b)+(c), not from how interpretable the clusters look. Build accordingly.

This run is **L06, single first-order ring, bands A–E (no T)**. A null on any test means "not here, at this resolution, statically" — **not** "the thesis fails." The signal may live at L08 (the city/hinterland contrast AF.18 found only at fine resolution), in T (transitions over time), or in the deferred ring-expansion distance object. Scope conclusions to L06-static-single-ring.

---

## Part 1 — Select ~50 cities

Extend WO18's spanning logic to ~50 of the 258 OWHC members. Goal is **even coverage of the covariate space**, not random draw — span biome, drainage type (endo/exorheic/coastal), aridity/Köppen class, continent/region, and basin size, so the anchoring test (a) has range to detect alignment against. Keep WO18's 10 in the set (continuity). If the workbench max-dispersion selector from WO18 was usable, use it to fill toward even coverage; otherwise hand-pick for spread. Record why the 50 were chosen (which covariate cells they fill).

**Capture per city** (these are the anchoring + probe inputs — the clustering does **not** see them):
- Environmental covariates: biome, aridity/Köppen class, drainage type, basin size, region/continent.
- Cultural/historical attributes available in-db: whatever the Societies / WH-cities records carry — founding era, settlement function if recorded (entrepôt / agrarian core / frontier / port / capital), any D-PLACE/Seshat-adjacent linkage. Use what exists; note what's missing. This is the (c) probe's raw material; thin is fine.

---

## Part 2 — Build the comparator + cluster

- Build the WO18 transition vector (per-variable `mean_abs` + `max_abs`, threshold-free) for all ~50, L06, on the 29-var universal intersection (re-derive the intersection at n=50 — it may shift; report if it does).
- Cluster on the **threshold-free continuous vector**. Use **≥3 PCA components** (WO18: 44.4% in 2 PCs — 2-D is a slice). Report the components used and variance captured.
- Produce the clustering, but **do not interpret it yet** — Parts 3–5 gate interpretation.

---

## Part 3 — (a) Anchoring test

For each external covariate the clustering never saw (biome, drainage, aridity, region, basin size), test whether cluster membership aligns with it:

- Cross-tabulate cluster × covariate; report whether clusters concentrate on covariate values (e.g. cluster 1 mostly endorheic) or cut across them.
- A simple association measure per covariate (Cramér's V or adjusted Rand vs the covariate partition — CC's choice, report which).

**Read:** which covariates, if any, the transition clustering tracks. Alignment with a physical covariate it wasn't told about = the structure is anchored to the world. Alignment with **nothing** external = a partition only the instrument sees (either novel discovery or artifact — undecidable without more, flag as such, don't resolve).

---

## Part 4 — (b) Stability test

Two perturbations:

- **Sample:** drop a random ~20% of cities, re-cluster, repeat many times (CC sets N). Measure how often the same city-pairs stay co-clustered (co-assignment frequency / bootstrap cluster stability). Report which cities/groups are stable and which reshuffle.
- **Representation:** re-cluster using the `sign_pattern`-derived vector instead of the threshold-free one. Report whether the clustering is broadly preserved or depends on the representation choice.

**Read:** stable across both = real density structure. Reshuffles under sample perturbation = method artifact, the specific groups were luck. Differs sharply by representation = depends on a setup coin-flip, not the cities.

---

## Part 5 — (c) Cultural probe (thin, first look)

Using the historical/cultural attributes from Part 1: does transition-cluster membership relate to **any** of them? E.g. do transition-boundary cities (high-sharpness, mixed-sign) skew toward frontier/entrepôt/contact functions, and transition-interior cities toward agrarian-core/capital functions?

- Cross-tab cluster (or the boundary-vs-interior sharpness axis directly, if cleaner than discrete clusters) × cultural attribute. Report any association, with the **n and the gaps** (many cities will lack a recorded function — report coverage honestly; a probe on 20 of 50 is a probe on 20).

**Read:** even a weak non-null = first evidence the instrument touches the humanistic layer. A null = the finding CC named (transition character may not predict cultural pattern better than signature does) — found early and cheap. Either is a real result. **Do not over-read** a weak signal on thin coverage; state it as suggestive-at-best.

---

## Scope guards

- **No archetype taxonomy.** WO17's three "archetypes" (boundary-location / interior-dominant / alluvial-outlier) and WO18's "deep-stable / wide-shallow" are n≤10 observations; n=50 either grows them into something or dissolves them. Report what the data does; do not carry the labels in as bins.
- **Tests before interpretation.** Run Parts 3–5 before telling any cluster's story.
- **L06 / single-ring / no-T**; conclusions scoped accordingly; nulls are "not here," not "not anywhere."
- **Clustering is the algorithm's; meaning is the tests'.** Legibility ≠ validity.

---

## Deliverables

1. The ~50-city set + selection rationale (covariate cells filled) + the captured covariate/cultural table.
2. Comparator vectors (n≈50, L06); re-derived universal-variable intersection (report if it shifted from 29).
3. Clustering (≥3 PCs, variance reported) — held uninterpreted until 4–6 below.
4. (a) Anchoring: cluster × covariate alignment, association measures, which covariates the structure tracks.
5. (b) Stability: bootstrap co-assignment + representation-swap result; stable vs artifactual groups.
6. (c) Cultural probe: cluster × cultural-attribute association with honest coverage/n.
7. Findings (AF.n), explicitly L06-static-single-ring.

---

## Acceptance

- ~50 cities run; covariate + cultural attributes captured (coverage reported, gaps named).
- Clustering produced on ≥3 components.
- All three tests (a/b/c) run **and reported before interpretation**.
- Findings state, plainly: is the structure **anchored** (a), **stable** (b), and does it **touch the cultural layer** (c) — each yes/no/weak with evidence, scoped to L06.

---

## Back to Opus / the verdict this run returns

This is the run that says whether the branch earns its keep. The three reads combine:

- **Anchored + stable + cultural touch** → the transition instrument is real and humanistically live; design the response object and plan its Phase-4 role.
- **Anchored + stable + cultural null** → a real, robust environmental instrument with no demonstrated cultural signal *at L06-static* — worth keeping, but the next question is whether L08 / T / ring-expansion is where the cultural signal lives, not more L06 cities.
- **Unstable or unanchored** → the structure is method-dependent or free-floating; the comparator needs rethinking before any humanistic claim, and the branch's keep is unproven.

Round-trip on which of these the data returns, with the (c) coverage honestly stated, before anything is built on top. Your synthetic interpretation after the run is the input I'll reason from.
