# WO8 — MapLibre stack + layer-management shell

**Branch:** Surface / sandbox v2 (new branch off WO7)
**Phase:** Surface · **Step:** 5 (map — foundation)
**Depends on:** WO7 (polity search live) — done.
**Type:** frontend map foundation. No engine, no new signature routes. Establishes the map
substrate the subsequent map WOs (single-basin, basin-ring, polity choropleth) build on.

## Goal

Shift the v2 Map tab from Leaflet to **MapLibre**, and stand up a **layer-management shell** —
the map thinks in named, add/remove/restyle-able layers from the start, so each later scope
*adds a layer type* rather than rewriting the map. This WO renders no new scope data; it
proves the substrate and the shell, with the current behavior (polity slice outline on slice
selection, from WO7) reproduced on the new stack as the proof.

## Why now, why a shell

MapLibre is the substrate everything downstream needs: the polity choropleth (F5.4, ~16k–38k
units) requires vector-tile performance Leaflet-GeoJSON can't give. Standardizing now avoids a
mid-stream Leaflet→MapLibre migration. Building it as a layer shell — not a hardcoded
single-geometry render — is the one structural choice that makes the remaining map sequence
(single-basin → ring → polity) *additive*: each is "add these geometries with this styling as a
named layer," not a map rewrite.

Perfect shared-code efficiency is NOT the goal; refactoring later is acceptable. The one
forethought that pays off: the shell manages layers generically so b/d/e slot in.

## Rendering substrate — CC's call

Whether basin geometries render as **GeoJSON sources** (fine at low cardinality — single basin,
a ring of adjacents) or via **tilesets/PMTiles** (the Cliopatria stack, necessary at polity
scale) is left to CC's judgment, weighed on **harness clarity**:
- Does adopting the full tileset stack now simplify or complicate the map harness for the
  low-cardinality scopes (single-basin, ring)?
- Does mixing GeoJSON (small scopes) + tilesets (polity) later make the code harder to read, or
  is the split clean because the scopes are genuinely different?
- Is a single substrate (all tiles, or GeoJSON-now-tiles-later) more code-readable end to end?

CC decides. The **constraint** the decision must satisfy: the layer shell extends to the polity
choropleth (many units, one-variable paint, per-slice) without a rewrite of the shell itself.
If GeoJSON-now means the shell needs restructuring when tilesets arrive for polity, that cost
counts against it. If pulling the Cliopatria tileset setup now is cleaner long-term, that counts
for it. Document the choice and its reasoning briefly in the WO8 findings.

## Build

- Replace Leaflet with MapLibre on the **v2 page only** (`sandbox_v2.html` / its JS). Base
  layers: hillshade + OSM equivalent (match the current look closely enough that the page
  doesn't visually regress).
- **Layer-management shell:** a small API for named layers — add(name, source, style),
  remove(name), restyle(name, …), clear. The scopes downstream call this; the shell doesn't
  know about scopes.
- **Reproduce current behavior as the proof:** polity slice selection (WO7) renders the slice
  boundary outline via the shell (add a "polity-boundary" layer; changing slice removes/re-adds
  it). This is the existing behavior on the new stack — the acceptance that the substrate + shell
  work.
- Map controls (zoom, etc.) and the tab structure carry forward.

## Constraints

- **Live Lookup (`sandbox.html`) untouched** — it keeps Leaflet; WO8 touches only v2.
- **No signature-path change** — the Signature/Analysis tabs and all WO2–WO7 rendering are
  untouched. WO8 is the Map tab's substrate only.
- **No new scope data on the map yet** — single-basin geometry, basin-ring, choropleth are
  later WOs (b/d/e). WO8 stops at "MapLibre + shell + polity outline reproduced."

## Accept gate

- Map tab renders on MapLibre; base map visually comparable to the prior Leaflet view.
- Polity slice selection draws the slice boundary via the layer shell; changing the slice in the
  dropdown updates the boundary (current WO7 behavior, now on MapLibre).
- Layer shell API exists and is what the boundary render uses (not a one-off hardcode) — so the
  next WO can add a "single-basin" layer through the same API.
- WO8 findings note the GeoJSON-vs-tileset decision and its harness-clarity reasoning.
- Existing suites green; Playwright UI tests updated for MapLibre where they asserted
  Leaflet-specific DOM. Live Lookup untouched.
- Karl reviews each write before it lands.

## Out of scope (the sequence after this)

- b) single-basin on the map — just the containing basin, no neighbors (next WO).
- c) wire basin-ring data to the frontend.
- d) basin-ring on the map — containing basin + adjacent ring, neighbors clickable to surface
  their signatures, principled encoding (shared-border / sub-area, not up_area proximity).
- e) polity choropleth — per-unit endpoint (F5.4) + one-variable paint + slice slider.

## Design notes carried forward (for the sequence, not WO8)

- **Single-basin map shows one basin, not a proximity neighborhood.** The v1 sandbox
  50km-proximity shading is retired: now that basin-ring is an explicit data-bearing scope, the
  proximity display would blur two different geographic claims (radius-proximity vs
  first-order-adjacency). Single-basin = the basin; basin-ring = the adjacency neighborhood with
  data. Keep them distinct.
- **Slice slider** (Cliopatria-style) arrives with the polity choropleth (e), where it scrubs a
  paint — not before, where it would only re-fetch a static signature.
- **Per-unit values endpoint** (F5.4) is the polity choropleth's prerequisite; log to the
  deferred register with its Areas-phase lineage when e is planned.
  