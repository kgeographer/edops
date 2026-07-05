# WO12 — Example-select standard + buffer on the map

**Branch:** `surf_wo12` → merge to `surface` at accept gate.
**Type:** Build — frontend standardization + buffer map geometry. No signature/engine change except (possibly) one read route for buffer member geometry (see Build 4).

## Goal

Set one standard for how `#v2-example-select` behaves across all four scopes, make **Map** the default landing tab, and bring **buffer** geometry to the map. This is the frame ring drops into (WO13); setting it now, before ring, is deliberate.

## The standard (applies to all four example options)

Selecting an example:
- sets `#v2-scope-select` to the matching scope,
- exposes that scope's param inputs **pre-filled**,
- enables **Get signature**,
- renders geometry to the map **only if selecting already yields geometry** — true for polity alone (its slice fetch carries geometry); single, buffer, ring render geometry on the Get-signature click.

On **Get signature** (single, buffer, ring): signature loads into the Signature tab (Band T when ticked), the scope's geometry renders to the map, and the **Map tab is made active**.

Per-example specifics:

- **single** → scope=single, lat/lon pre-filled (Timbuktu). Click → sig (+T), containing-basin
  outline+fill to map (WO11 path), land on Map.
- **buffer** → scope=buffer, radius input exposed preset to 100 (+ lat/lon). Click → sig (+T),
  **buffer geometry to map** (Build 4), land on Map.
- **polity** → scope=polity, fetch N Song slices, render first slice geom immediately, pre-fill
  name + start/end from that slice. Click → full sig (+T), land on Map.
- **ring** → scope=ring, lat/lon pre-filled (Timbuktu), inputs exposed, Get signature enabled.
  **No geometry, no signature wiring yet** — ring is WO13. Selecting ring must not error; it
  parks in the standard's shape awaiting WO13.

## Transitional-state note (state it in findings, don't design around it)

Landing on Map presumes geometry at Get-signature time. Today geometry comes from companion routes fired by the click (single: `/api/basin-preview`; buffer: Build 4; polity: slice geom), **not** from the signature payload — the areal endpoint serves signature + histograms, not paint geometry (locked decision, polity work). When live resolve replaces the example dropdown, geometry will be present at resolve and Map-first will be the natural default. WO12 makes Map the default now, ahead of that. This is a known transitional state, not a payload change — CC should not look for geometry in the sig JSON.

## Build

**1. Standardize `#v2-example-select`.**
Rewrite the example handlers to the standard above — one shared shape, per-scope specifics. Today
each option behaves differently (single sets scope only; polity fetches slices + renders; etc.);
converge them. The polity example keeps its slice-fetch-renders-immediately behavior as the
codified exception, not a special case bolted on.

**2. Map is the default landing tab.**
On Get-signature (and on polity select, which already has geometry), make Map active. Single and
polity already draw; this changes *which tab* is active on resolve. Confirm the Signature tab's
accordions still render correctly when reached by a later click (they're just not the landing).

**3. Buffer param input.**
Radius input exposed on buffer example select, preset 100, feeding the existing `buildBufferUrl`.

**4. Buffer geometry on the map — the real work of this WO.**
Draw, through the shell, **all basins involved in the buffer, unclipped, one flat highlight
color** (the same highlight single uses for its basin — scopes differentiate by the circle, not
by basin color), with a **circle outline layer over them** at the buffer's lat/lon + radius.

The unclipped fill + overlaid circle is the point: it shows the arbitrary boundary cutting through
basins it only partially contains — the honest depiction of an arbitrary-boundary scope, legible
without caveat. Do not clip the basins to the circle; clipping would hide exactly what's worth
seeing.

- **Circle:** construct client-side from lat/lon + radius (a geodesic circle polygon/line);
  `shell.add('buffer-circle', ...)` as an outline layer over the fill. No route needed.
- **Involved-basin geometry:** the buffer signature already computes over its member basins
  server-side, so the member `hybas_id`s are recoverable. Locate where they surface in the buffer
  payload (report it), then fetch their geometry.
  - **Route constraint:** use a route to fetch basin geometry by id. It may be new, or an existing
    one read-only — **but if a route is already in use elsewhere (v1 or otherwise), WO12 must not
    modify it.** No reshaping a shared endpoint. If an existing route serves basin geometry by id
    without modification, reuse it; if none fits, add one. Report which path you took.
  - Draw the member set as `shell.add('buffer-basins', <geojson>, [<fill spec>])` **under** the
    circle layer.
- **Honesty check:** the set of basins drawn must equal the buffer signature's member set by
  `hybas_id` — same discipline as WO11's single-basin id match. If they diverge, stop and report.

## Out of scope (explicit)

Ring signature/geometry/wiring (WO13); user-drawn scope; any per-basin value encoding (buffer fill is flat, not value-painted); any change to a route already in use elsewhere.

## Accept gate

- Each of the four example options behaves to the standard above; ring parks without error.
- Get-signature lands on Map for single, buffer, polity; polity renders geom at select.
- Buffer: all involved basins draw unclipped in flat highlight, circle outline over them, at the
  right center/radius; drawn basin set == signature member set by `hybas_id`.
- Single (WO11) and polity boundary paths unchanged; `sandbox.html` untouched.

## Tests

- Playwright per example option → correct scope set, params pre-filled, correct landing tab.
- Buffer: shell has `buffer-basins` + `buffer-circle` layers; basin set matches signature by id;
  circle geometry at expected center/radius.
- The id-match assertion (route/integration or Playwright — your call).
- Full suite green — zero FAILs, zero unexplained warnings. Note the new count.

## Constraints

- Review before write — Karl signs off each write.
- Shell API only — no direct `map.addSource` / `map.addLayer` in scope code.
- No modification to any route already in use elsewhere; `sandbox.html` untouched.

## Findings

`docs/edop/surface/wo12_findings.md`. Report: where buffer member `hybas_id`s surface in the
payload; the basin-geometry route path taken (new vs reused-read-only) and, if reused, evidence
it went unmodified; the id-match result; confirmation ring parks cleanly.