# CITYKIN WO1a — terrain lens: query-relative tolerance knobs, retrieval head, factored core

**Status:** draft for review.
**Prior:** `wo1_findings.md` (Tier-1 terrain facets validated; the 400m gate; the Tbilisi fixture
passed *for Tbilisi*), CITYKIN WO1 Part C (staged terrain-lens design), the sandbox Similarity-tab
regime-lens pattern (query-relative bands with user knobs — the precip/temp-level/temp-range controls).
**Type:** lens correction — retire a de-generalizing artifact, rebuild the combination, re-fixture.
Notebook validation first, then wiring. CC authors; Karl reviews every write.

Goal-setting with provisos. CC discovers implementation particulars; Karl reviews every write.

## Why — the 400m gate de-generalized the instrument

WO1's terrain lens passed the Tbilisi fixture, but passing *for Tbilisi* and *generalizing to all 254
cities* turned out to be different things, and the gate optimized the first at the cost of the second.
The `grid_elev_mean >= 400m` eligibility gate hard-codes **one fixed question** — "is this a *high*
contained place" — with "high" baked in as a global constant. The UI offers a dropdown of *all* WH
Cities. Query a flat coastal city (Bruges, ~5 m) and the 400m gate is nonsense: it excludes the city
from its own query, and the contained-valley shape terms are meaningless for a delta city. The gate was
fit to make *Tbilisi* return satisfying results and in doing so baked Tbilisi's *kind of terrain* into
the instrument — the standing project hazard (fitting to the motivating case), one level up: not a
threshold fit to a case, but a whole design fit to a case.

**The fix is the pattern already validated for the climate regimes.** The sandbox temperature-regime
lens does not hard-code "warm" — it anchors to the *query city's own* temperature curve and matches
within user-set tolerances (±°C level, ±°C range). The anchor is the query; the tolerances are knobs.
Bruges asks "what's like Bruges," Tbilisi asks "what's like Tbilisi" — same instrument, no baked-in
constant, generalized by construction. Terrain gets the same treatment: **query-relative tolerance
knobs, anchored to the selected city, not a global gate.**

This also reframes what WO1 actually discovered — correctly diagnosed facets, mis-designed combination:

- **±10km sensing window is the workable radius** (±2km can't see enclosing highlands). *Keep* —
  general finding.
- **Raw z-scored elevation dominates a plain Euclidean sum and swamps the shape facets.** *Keep the
  insight, change the fix.* WO1's fix was "gate elevation out entirely"; the general fix is "give
  elevation its own query-relative tolerance so it informs without dominating and without being
  discarded." Tbilisi's ~600 m elevation is a real, matched dimension of its terrain character — the
  gate *erased* elevation's role; a query-relative band *preserves* it.
- **The three facets are near-independent** (|r| ≤ 0.35). *Keep* — what makes per-facet tolerances
  legitimate.

## Part A — retire the gate

Remove `ELEV_HIGH_THRESHOLD = 400.0` and the eligibility-gate step. It was a Tbilisi-specific artifact.
Elevation returns to the lens as a *query-relative tolerance* (Part B), not a global floor and not a
discarded facet.

## Part B — the terrain tolerance core (factored, head-agnostic)

The lens becomes **three query-relative tolerance knobs**, each anchored to the *selected city's* facet
value:

- **Elevation tolerance** (± m of the query's `grid_elev_mean`) — Tbilisi (673 m) matches ~600 m
  cities; Bruges (5 m) matches near-sea-level cities.
- **Relief tolerance** (± m of the query's `relief_range_m`).
- **Landform-position tolerance** (± of the query's `landform_position`, 0–1).

Provisos:

- **Factor the tolerance computation as a callable core, separate from any presentation head.** WO1a
  wraps it in the *retrieval* head (Part C). The sandbox Similarity tab will later wrap the **same
  core** in a *paint-a-set* head (see Forward). Same "factor the distance from the head" discipline as
  WO8d's `distance_core` — so the later Similarity-tab addition is a new head on a proven core, not a
  reimplementation. The knobs live in the core; the two heads differ only in what they do with the
  in-tolerance set (rank-and-list vs paint).
- **Elevation must inform without dominating.** The WO1 domination problem (elevation swamping shape in
  a plain Euclidean sum) is solved here structurally: as a *tolerance band* it can't dominate a ranking
  — it constrains eligibility query-relatively, and shape does the ranking within the band. If a
  ranked distance is still computed within the tolerances, elevation's weight in it is an internal
  parameter set once against the fixtures (Part D), not a raw z-score and not a user knob.
- **Default knob values** are internal parameters set against the fixtures, exposed as user controls
  with sensible defaults (the sandbox regime lenses' pattern — the dials start somewhere reasonable and
  the user tightens/loosens). Derive defaults, don't assert them.

## Part C — the retrieval head (this WO)

WH Cities stays **retrieval**, not paint-a-set: query city → the cities within the current tolerances,
ranked by terrain distance → **top-N markers on the map + ranked list below** (the cdop_pilot WH Cities
pattern, distances shown — the magnitude-with-rank rule). Knobs above the result; adjusting them
re-queries. A tab in sandbox is a fine home, but it does **not** inherit the Similarity tab's
paint-a-set output just by sharing the sandbox — it is retrieval-with-knobs.

## Part D — two fixtures (the generalization check)

WO1 had one fixture (Tbilisi) and that is exactly how a Tbilisi-shaped instrument slipped through. WO1a
requires **two**, and the second is the one that catches de-generalization:

- **Tbilisi** (contained high valley) → high contained-valley neighbors (Yerevan, Kathmandu-valley
  cities, other intermontane basins), with the query-relative knobs at their defaults. Must still pass.
- **A flat city** (Bruges, or a comparable near-sea-level delta/coastal city in the corpus) → *flat*
  neighbors (other low-relief, floor-position, low-elevation cities). This is the generalization gate:
  the instrument must return terrain-*like* cities for a city that is nothing like Tbilisi, with no
  parameter change.

Acceptance: **both fixtures return terrain-coherent neighbors at default knob settings, with no
city-specific tuning between them.** If the flat-city fixture requires different internal parameters
than Tbilisi, the instrument is still city-shaped and the tolerance core is not yet query-relative
enough — a by-eye gate, in the WO7 tradition.

## Validation order

1. Rebuild the lens as the query-relative tolerance core (Part B), gate removed (Part A).
2. Set default knob values and elevation weighting against **both** fixtures jointly (Part D) — not
   Tbilisi alone.
3. Confirm both fixtures pass at shared defaults; report the neighbor lists for each.
4. Wire the retrieval head (Part C) to the UI.

## Accept gate

**The terrain lens is query-relative (anchored to the selected city, no global elevation constant); the
400m gate is gone; the three tolerance knobs are exposed with derived defaults; the retrieval head
returns ranked markers + list with distances; and both fixtures — Tbilisi and a flat city — return
terrain-coherent neighbors at the same default settings with no per-city tuning.** The tolerance core is
factored separately from the retrieval head.

## Forward — not this WO

- **Terrain regime on the sandbox Similarity tab.** After WH Cities proves the lens, the *same tolerance
  core* gets a **paint-a-set** head (paint all basins/cities within the tolerances, span-in-km, the
  regime-lens output shape) alongside precip/temp regimes. A new head on the proven core — factored for
  in Part B, built in a following WO.
- **Soft elevation down-weight** (Karl's WO1 follow-on) — with elevation now a query-relative tolerance
  rather than a hard gate, the sharp in/out edge is already softened; whether a continuous down-weight
  further improves edge behavior is a refinement to assess in use, not now.
- **Tier-2 enclosure/containment** (`ST_Touches` basin-ring) and **Tier-3 local DEM** remain named, not
  built (WO1 Part C). Kathmandu's mid-pack WO1 rank is the standing candidate trigger for Tier-2.