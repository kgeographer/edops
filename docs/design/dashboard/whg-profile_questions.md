# Profile questions: what the WHG environmental profile answers

Draft 2026-11-04 by Opus, for Karl to carve. Bridges the ring spec (`whg_ring_profile_spec_prelim.md`) and WO-03 (`wo03_summary.md`, `wo03_results.md`) to the payload proposal for Stephen Gadd and Ruth Mostern. Recommendations are marked **Rec.** and are options, not decisions. Decision numbers D1 to D11 are those in `wo03_summary.md`.

## The modal in one paragraph

A WHG place page has an [Environmental Profile] button. The modal answers a short set of questions about the place at three scales: its own L6 basin (the core), the basins that touch it (the ring), and its ecoregion; plus the river network that connects them. The answers are prose with optional visual elements that WHG draws. The prose mostly does not recite numbers. The numbers travel in the payload and are a click away: a link to the full signature in EDOPS, and a link to the same query as JSON for researchers who want the data.

## Three kinds of fact

The rule layer stays deterministic and emits facts; a prose layer words them. To keep the locked decision (numbers only, no verdict words) consistent with prose that speaks plainly, every fact is one of three kinds:

| Kind | What it is | Example | Condition |
|---|---|---|---|
| **T** topological or categorical | a relation or class read directly from the data | the neighbour drains into the core; the nearest edge is the coast; the place is in ecoregion X | none; safe to state |
| **H** threshold | a word that depends on a cutoff | near the edge; a second ecoregion of note; a much larger river nearby | the cutoff is documented and swept (WO-02 method) before the fact is emitted |
| **N** numeric | a value, count, rank, distance or share | 2nd highest of 7; 11.5 km; 48 times the area | carried in the payload; spoken only where the prose needs it |

The prose layer words what it receives and never applies a threshold of its own.

## Cross-cutting decisions

**Who counts as a neighbour (D1).** WO-03: 1.5% of neighbours touch at a single point, all coastal; 11% share under 10 km of border.
**Rec.** Keep every touching basin in the payload with its `shared_km`. Exclude point contacts (shared border exactly 0) from neighbour statements: this is T, not H, since a point contact is a distinct geometry, not a short border. Keep short borders as neighbours in v1; no cutoff.

**Snap and no-basin points (D10).** WO-03: a 1 km snap fixes Akureyri and Levuka and nothing else; the remaining no-basin points are islands 570 km or more from any basin.
**Rec.** Snap within 1 km and report that a snap happened and its distance. Otherwise return a structured `no_basin` response with the distance to the nearest basin. The point's ecoregion is a point-in-polygon lookup that does not need a basin, so return it in the no-basin response if the island has one (to check in WO-04).

**Speed (D6).** WO-03: the ring takes 5 to 17 s today, too slow for a modal. One score call for the set gives identical scores; the rest of the pipeline over a set was not tested.
**Rec.** The data is static, so test precomputing compact signatures for all 16,397 L6 basins (about 7.6 KB each, roughly 125 MB) plus the ecoregion intersections. A ring then becomes lookups. The one-pass route is the fallback.

**The -9999 class (I-3).** Harmless today; breaks the "how many neighbours share the core's class" fact.
**Rec.** Fix in the edge-case work, before any ring rule is built.

**Glossary.** What high means, what zero means, units, area covered (WO-02 7a to 7d). A dependency for every question; Karl's data-source docs.

## The questions

Proposed tiers are a starting point for the hours, not a decision.

### Q1. What is it like here?

The core basin, plus named context.

- **Draws on:** core rows (A to E); the point's ecoregion with name, Wikipedia link and summary; ecoregion shares in the core; named rivers (see Q6).
- **Rule families:** WO-02 Position, Distribution, Categorical, Within-band, Cross-band (core unchanged); new **Named context**.
- **WO-03:** the point's ecoregion is the core's largest in 94% of sample basins; a basin has one or two ecoregions above 5% of its area. 26 of 847 ecoregions have no text.
- **Facts:** the point's ecoregion (T); other ecoregions above a share (H, D7); the share outside every ecoregion polygon (N).
- **Rec.** Always name the point's ecoregion. Name others only above a swept share (sweep 1% to 10%). Name an ecoregion without text by name alone, and check Karl's renaming hypothesis for the 26 as housekeeping. Generated ecoregion summaries are marked as generated, like the paragraph.
- **Tier:** Must.

### Q2. How does here differ from around here?

- **Draws on:** core rows; compact neighbour rows (variable, status, score, raw, weight at zero, class); neighbour `flow_relation`.
- **Rule family:** new **Core and surroundings** (ring spec): rank among N+1, counts above, below and equal, neighbour range as values, class agreement, how many neighbours have a value and how many are at zero.
- **WO-03:** median 5 neighbours (3 to 9); which variables are at zero differs between core and neighbours for 34 of 59 test-place neighbours; tied zeros give "1st of 6" under a naive rank. For `_upstream` variables, flow neighbours differ from the core about half as much as others, mostly because their catchments overlap.
- **Facts:** ranks and counts (N); class agreement (N, after the I-3 fix).
- **D5. Rec.** Rank wording reports above, below and equal, never a bare ordinal with ties. For `_upstream` variables, compare the core only with off-stream neighbours; flow neighbours get the Q6 relation instead. That avoids a catchment-ratio cutoff. Exclude variables with unknown zero fraction (`reservoir_vol`), as the ring spec says.
- **Which facts reach the prose** is the editorial rule and the hardest part: probably the variables where the core is at or near an extreme of the set. "Near" is H and goes to WO-04.
- **Tier:** Must.

### Q3. Is the surround uniform or varied, and in which direction?

- **Draws on:** compact neighbour rows; neighbour positions relative to the place; ecoregions in the ring.
- **Rule family:** Core and surroundings (spread); a new fitted-direction rule.
- **WO-03:** per-neighbour compass words are unreliable: measured from the place, the 8-point word changes for 1 neighbour in 5, and the four methods agree for 19% of test-place neighbours. The ring has two or three ecoregions of note.
- **D2. Rec.** No per-neighbour compass words. For direction, fit across the ring: for each variable, the bearing from the place along which values change most, emitted only when the fit is strong (H; test in WO-04 on Tbilisi, Santa Fe and the sample). Spread across neighbours as values (N). Ecoregion count in the ring above the D7 share (H).
- **Tier:** spread Must; fitted direction Should, pending WO-04.

### Q4. Where does the place sit within its basin?

- **Draws on:** distance from the point to the core's outline; distance to the nearest neighbouring basin; which kind of edge is nearest.
- **Rule family:** new **Point position**.
- **WO-03:** World Heritage Cities sit a median 7.6 km from the core's outline; for a third the nearest edge is the coast.
- **D11. Rec.** Edge kind, coast or divide (T). Distances (N). "Near the edge" (H) swept on a share of the core's size measure, with distance alongside.
- **Tier:** Should.

### Q5. What does the record cover?

- **Draws on:** row statuses for core and neighbours; coverage; ecoregion coverage; whether named rivers exist nearby; snap information.
- **Rule families:** WO-02 Empty cells and Coverage; additions for the ring and named context.
- **WO-03:** `no_data` rows occur only in neighbours (seven rows; source NoData); coastal and lake basins are partly outside every ecoregion polygon; the Natural Earth layer names a nearby main stem for about 60% of World Heritage Cities and much less in deserts and polar regions.
- **Facts:** counts of neighbours with a value (N); why a value is missing (T, existing Empty-cells wording).
- **Rec.** Absence of a name never becomes absence of a river: the prose says a river runs nearby without naming it.
- **Tier:** Must.

### Q6. What arrives here?

- **Draws on:** core local and upstream pairs; upstream area; neighbour `flow_relation`; nearest reach above 1,000, 10,000 and 100,000 km² of upstream area, with distance, upstream area and name where matched.
- **Rule families:** WO-02 Local and upstream (rewording the Analysis tab's verdicts as ratios); new **Network**.
- **WO-03:** flow relation is clean, with no unknowns: 12% of neighbours upstream, 12% downstream, 76% across a divide. Kaifeng's nearest large river is 11.5 km away and drains 48 times the core's area; in random basins a river ten times larger lies near 4% of cores at 1,000 km². Upstream area measures size at that point, not a river's size overall.
- **Facts:** drains into, receives from, across a divide (T); nearest reach per size class with distance (N); "a much larger river runs nearby" (H, D9: ratio and distance swept together); river named (H, D8).
- **D8. Rec.** Name a river only when a named line lies close to a close reach; both distances are swept. Otherwise generic wording.
- **D9. Rec.** Repeat the Kaifeng-type rate on the World Heritage Cities before choosing cutoffs; random basins understate it.
- **Tier:** flow relation and local-upstream Must; nearest main stem Must (fast, and it is the Kaifeng case); names Should.

### Q7. What is reachable from here?

- **Draws on:** `coast`, `outlet_type`, `dist_sink`; edge kind from Q4.
- **Rule family:** Network.
- **WO-03:** three meanings of "coastal" coexist. The Sandbox's "Coastal terminal" badge disagrees with the `coast` flag for 45% of the basins it labels. `dist_sink` is labelled "Distance to ocean outlet" even for endorheic basins, where it is the distance to an inland sink.
- **D3. Rec.** The basin touches the coast from the `coast` flag (T); drainage from `outlet_type`: to the sea, interior, or to an inland sink (T); distance to the outlet or sink (N), with the label naming which. Align or retire the Sandbox badge and fix its label separately; that is a Sandbox issue, not a profile one.
- **Tier:** Must.

## Ring spec open questions, after WO-03

1. Snap tolerance: D10 above.
2. Default bands for the modal: open; Band D question unchanged.
3. Band T: the v1 plan keeps Band T statements out of the endpoint. Core-only Band T values can travel in the payload for WHG to draw, with no statements; open.
4. L8 as a second profile: not in v1 (WO-03 measured L6 only).
5. Compact neighbour fields: WO-03 1f's set (`variable`, `method`, `status`, score, raw, `weight_at_zero`) plus class label, `flow_relation`, `shared_km`, point-contact flag, catchment ratio.
6. Rules server-side: yes; facts travel in the payload, so WHG renders and does not compute.
7. Identifier and cache key: the point (lat, lon) for the request, so cases like Kaifeng stay reproducible; the basin id for the cache.

## Payload sections, sketch

`place` (point, snapped point and distance, or `no_basin`); `core` (full rows); `neighbours[]` (compact rows and the fields in item 5 above); `ecoregions` (the point's, with link and summary flag; shares in core and ring); `network` (flow relations, local and upstream pairs, nearest reaches by size class, names where matched); `position` (edge kind and distances); `coastality`; `facts[]` (id, kind T, H or N, stat, the inputs it read); `links` (EDOPS view, JSON); `caveats`; `versions` (engine, data). Size is not a target until the sections are agreed.

## What goes to WO-04

- Sweeps for every H fact: ecoregion share (D7), near the edge (D11), a much larger river nearby (D9), river naming distances (D8), which core-and-surroundings facts reach the prose (Q2).
- The fitted-direction test (Q3).
- The Kaifeng-type rate on World Heritage Cities (D9).
- Whether the point's ecoregion is returned for no-basin islands (D10).
- Precompute scoping (D6): time for all L6 basins, storage, a lookup-built ring checked against `basin_ring_signature`.

Separately, as edge-case work: the I-3 fix, the snap, and the structured no-basin response.

## Decisions for Karl

Each **Rec.** above; the tiers; whether the fitted direction is worth a WO-04 test; Band T values in the payload without statements; whether WO-04 includes the precompute scoping or it goes with the edge-case work.