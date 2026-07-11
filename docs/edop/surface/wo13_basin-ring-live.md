# WO13 — Basin-ring live: center signature + adjacency ring on the map

**Branch:** `surf_wo13` → merge to `surface` at accept gate.
**Type:** Build — the ring scope, end to end. First multi-member meaningful-boundary
neighborhood; first clickable map features.

## Goal

Bring `basin_ring` live: the **center** basin's full signature in the accordions, the **center +
first-order adjacent ring** drawn on the map (categorically colored), and each ring member
clickable to fetch and show its own signature. This closes the long-standing gap the old sandbox
left open — it drew neighbors but surfaced no neighbor data.

Ring drops into the WO12 standard (example-select behavior, Map-first landing); that frame is
already built and green.

## Payload (established)

`GET /api/areas?type=basin_ring` returns `{center, ring[]}`. Each ring member carries its own
`hybas_id`, `neighbor_lat`/`neighbor_lon`, and a **complete signature sub-payload**. `center`
carries its signature plus `center.neighborhood.hybas_id`. **No GeoJSON in the payload** —
geometry is fetched by id via `/api/basin/geom` (built in WO12), the same as buffer.

## Build

**1. Route — `type=basin_ring` on `/api/areas`.**
Add the dispatch branch (alongside buffer, single_basin, polity). Live DB pull of `{center,
ring[]}` from lat/lon. Two-pass validation and unmodified serialization, as every prior scope.
`/api/area` and the other branches untouched.

**2. Frontend — dispatch the `{center, ring[]}` shape.**
This is not the flat `rows[]` every other scope returns. Route it to a ring path. The initial
Get-signature:
- renders the **center's full signature** in the Signature tab via the existing single-basin
  rows-renderer (DN8 delegation — no new leaf widgets), Band T on the center when ticked;
- fetches **center + ring geometry** via `/api/basin/geom` using `center.neighborhood.hybas_id`
  and every `ring[i].hybas_id`;
- lands on **Map** (WO12 standard).

The ring members' signature sub-payloads arrive in the initial `{center, ring[]}` response but
are **not rendered up front** — each renders on demand when its member is clicked (Build 4). Hold
them client-side from the initial response; do not re-fetch per member unless the payload doesn't
already carry them at full detail (report which held).

**3. Map — center + ring, categorically colored.**
Through the shell: center as one highlight, ring as a second, distinct highlight — **categorical,
not value-painted** (center-vs-ring is the only distinction this WO encodes). Two named layers or
one source with a center/ring property driving a paint match — CC's call; report it.
- Fit-bounds to the full center∪ring extent (the WO12 `geojsonBbox` FeatureCollection path +
  the F12.5 resize-ordering fix both apply — reuse them, don't re-derive).
- **Honesty check:** the drawn basin set equals `{center.neighborhood.hybas_id} ∪ {ring[i].hybas_id}`
  exactly, by id — same discipline as WO11/WO12. Divergence stops the WO.

**4. Clickable ring members — the new interaction.**
Ring member features are clickable, surfaced by a **hover affordance carrying a bare "view
signature" link** — its only job is to signal *there is data here*. The tooltip carries **no
summary content**: no hybas_id (a DB key, not user-facing information), no distance/centroid
figure (adjacent basins share a border — centroid distance is a fabricated precision that
misrepresents adjacency as proximity, the same error as the retired 50 km shading). Link only.

On click: render that member's signature (from its held sub-payload) through the single-basin
renderer, and switch to the **Signature tab**. The center is the default render; a clicked member
replaces it. Provide a way back to the center (re-click center, or a "center" control — CC's
call; report it).

**5. Info div — explain the ring case.**
The left-column info `<div>` (lower half) carries a short, factual orientation for this scope: the
map shows the containing basin (center) and its first-order adjacent ring; ring members are
clickable for their own signatures; the accordions currently show whichever basin is selected
(center by default). This is the affordance label for a genuinely new interaction, not a caveat —
keep it short. Shown for ring scope only.

## One investigation to report, not assume

**Does the ring engine path produce Band T per member, or center-only?** It governs whether a
clicked member's signature can show a Band T accordion at all, or whether T is a center-only
affordance for this scope. Check the engine ring path and the member sub-payload shape; report
what's there. Do not fabricate a member T panel if the data isn't produced — if T is center-only,
a clicked member simply shows A–E and the T accordion is absent/disabled for members.

## Out of scope (explicit)

Per-member value encoding on the map (ring color stays categorical); ring-expansion beyond
first-order adjacency; user-drawn scope; any weight/aggregation across ring members (settled: no
cross-ring aggregation — each member carries its own signature).

## Accept gate

- `type=basin_ring` returns `{center, ring[]}` live for Timbuktu; center full signature renders in
  the accordions (T on center when ticked).
- Center + ring draw on the map, categorically colored, fit-bounds to full extent, land on Map.
- Drawn set == `{center ∪ ring}` by hybas_id.
- Hovering a ring member shows the "view signature" link (no summary content); clicking it renders
  that member's signature and switches to the Signature tab; return-to-center works.
- Info div explains the ring case, ring scope only.
- Buffer/single/polity paths and `sandbox.html` untouched.

## Tests

- Route: `type=basin_ring` validation + payload shape; center∪ring id-match honesty check.
- Playwright: ring example → Get signature → center sig in accordions, Map landing, center+ring
  layers present; hover shows link; click member → member sig renders + Signature tab active;
  return-to-center.
- Extend the WO12 example-standard tests to cover ring's now-live behavior (it parked in WO12;
  update the `TestRingParksCleanly` expectations to live behavior).
- Full suite green — zero FAILs, zero unexplained warnings. Note the new count.

## Constraints

- Review before write — Karl signs off each write.
- Shell API only — no direct `map.addSource` / `map.addLayer` in scope code.
- No modification to any route already in use elsewhere (incl. `/api/basin-preview`,
  `/api/basin/geom` — reuse read-only); `sandbox.html` untouched.

## Findings

`docs/edop/surface/wo13_findings.md`. Report: whether member sub-payloads carried full detail in
the initial response (or needed per-member fetch); the Band T per-member investigation result; the
map layer structure (two layers vs property-driven paint); the return-to-center mechanism; the
id-match result.
