# WO17 — Basin-ring resolver + per-neighbor transition diagnostic

**Phase:** Areas · **Sub-phase:** neighborhoods · **Date:** 2026-06-27
**Depends on:** WO16 (adjacency confirmed clean — `ST_Touches`, no slivers, no vertex-only contacts; `shared_km` per neighbor already computed). WO14 (single-basin signature, validated).
**Branch:** continue `engine_v0.4b` (or a `ring` branch off it — CC's call).

---

## Goal

Build `resolve_basin_ring` and produce the **per-neighbor transition diagnostic**: for a center basin, compute the center signature and each adjacent basin's signature, then the per-variable signed divergence center↔neighbor, with a geometric **bearing** to each neighbor so the result is directional. The diagnostic answers one question — **do these rings read as coherent surroundings or as directional transitions, and what does an honest boundary reading need to carry** — which decides everything downstream.

This is description, not analysis. We are building the faithful description of the transition field (which variables change, which direction, how sharply); declaring a divergence "a boundary" is later, surface-side, and threshold-calibrated. (Quality of analysis ∝ quality of description.)

---

## Architecture (settled)

- **The center is held separate, never pooled into the ring.** The center is what the ring is compared against.
- **The ring is never collapsed into a single signature.** Collapsing is information loss; we don't, unless something later forces it. There is therefore **no ring weight policy** — equal/area/border-length all existed only to collapse, and are dropped.
- **The object is the per-neighbor set of comparisons** — directional, governed by the lean/full projection for volume, not by averaging.
- **No engine change.** Each signature is a single-basin run (WO14-validated). WO17 adds the resolver and a diagnostic layer that consumes N+1 signatures; the engine resolves and serves, the diagnostic describes the relationship.

---

## Part 1 — `resolve_basin_ring`

First-order adjacency via `ST_Touches`, returning the center basin and its ring as **separate** structures (center carried distinctly; ring = the adjacent basins, excluding the center). For each ring neighbor, carry from WO16: `hybas_id`, `sub_area_km2`, `shared_km`, and the shared-border geometry.

**Bearing (primary = border-bearing):** compute each neighbor's bearing from the center as the bearing to the **shared-border midpoint** (or normal to the shared edge) — the border is where the transition physically happens, so it's the honest direction of crossing. Also carry the **centroid-to-centroid bearing** alongside, as a diagnostic only. The run then shows whether the two diverge enough to matter (most at L6, where neighbors are large and a big neighbor's centroid can sit far from its shared border). Measured, not presumed.

**Semantics:**
- Shortfall structurally 0 (the ring is whole basins; meaningful boundary).
- First-order only (multi-order = ring-expansion, deferred).
- Coastal/open-water adjacency: `ST_Touches` returns no neighbor across water → a coastal center simply has fewer land neighbors. Note, don't special-case.

---

## Part 2 — Per-neighbor transition diagnostic (notebook, cell by cell)

For the center and each ring neighbor, run the single-basin signature (bands **A–E only** — Band T deferred, see below). Then compute, **per variable**, the signed divergence center↔neighbor:

- **Continuous vars:** signed `center − neighbor` in global percentile points (the shared frame both already use). Start simplest; refine only if it under-describes.
- **Categorical vars:** match / mismatch (and which class on each side).

Assemble the **directional transition table**: rows = (neighbor, bearing, per-variable divergences), so each neighbor is a direction off the center with a divergence profile. This is the wombling-on-the-basin-graph object — per-variable rate of change across each adjacency.

**The read this must produce** (the point of the WO):
1. **Per-variable transition character** — for each variable, is the divergence sharp in some directions and null in others (a boundary), uniform (an interior), or uniformly large (center is an outlier)? Timbuktu's expected shape — moisture/drainage sharp toward the Sahara, null toward the Niger — is a hypothesis the table tests, not an assumption.
2. **Coherence of the ring as a whole** — do the neighbors agree (coherent surroundings) or split (directional transition)? This is the engine's coherence question one level up; it is what would have decided any collapse, and it confirms why we don't collapse.
3. **Variable-group structure** — do variables transition *together* (moisture + drainage co-vary across the same adjacency) or independently? Co-transitioning variable groups are the substance of an ecotone reading.

---

## Fixtures

Three boundary characters, each at **L06 and L08** — the L6/L8 difference is **observed, not presumed** (whether L6's wider reach and L8's tighter collar produce different transition reads is a result of this WO):

- **Timbuktu** — desert / river seam.
- **Rome** — Mediterranean / montane (Apennine).
- **Kaifeng** — North China Plain alluvial / loess (Yellow River setting); also the Pitt-stakeholder fixture.

Ring sizes from WO16: Timbuktu L06=5 / L08=7, Rome L06=7. Kaifeng sizes to be found.

---

## Band T — deferred, with reason

Bands A–E only in WO17. Band T adds a temporal axis on top of the spatial transition; "does the boundary move over the millennium" is a real and interesting question, but stacking it on before the spatial transition object's shape is settled is premature. Band T re-enters as its own step once the directional object is settled. (Register note, not a silent drop.)

---

## Deliverables

1. `resolve_basin_ring` (center separate; ring neighbors with `sub_area_km2`, `shared_km`, border geometry, border-bearing + centroid-bearing).
2. Diagnostic notebook (`basin_ring_transition.ipynb` or per convention), cell by cell.
3. **Directional transition table** per fixture per level: (neighbor, border-bearing, centroid-bearing, per-variable signed divergence).
4. Findings (AF.n): per-variable transition character; ring-coherence read; any variable-group co-transition; whether border-bearing and centroid-bearing diverge materially (and at which level); the observed L6↔L8 difference per fixture.

---

## Acceptance

- `resolve_basin_ring` returns center + first-order ring, center held separate, both bearings carried; shortfall=0.
- Per-neighbor signatures run (A–E) for all three fixtures × both levels; no engine change.
- Directional transition table produced for each.
- Findings answer the three reads in Part 2 (per-variable character, ring coherence, variable-group structure), and report the bearing-divergence and L6↔L8 observations as data, not assumption.

---

## Back to Opus

Round-trip on: whether the rings read **directional or coherent** (this is the result that shapes the response object — directional confirms the per-neighbor primitive is the right one); the **variable-group co-transition** structure (the substance of the ecotone reading, and input to how the directional object should be organized); whether **border-bearing vs centroid-bearing** matters enough at L6 to standardize on border-bearing; and the **L6↔L8** transition-read difference per fixture. These collectively are the first real evidence on what an honest areal-transition response object has to carry.
