# WO11 — Containing basin on the map (first scope geometry through the shell)

**Branch:** `surf_wo11` → merge to `surface` at accept gate.
**Type:** Build — map render only. No signature / Band T change.

## Goal

Render the **containing basin polygon** for the single-basin scope on the v2 map, through the
WO8 layer shell. WO8 proved the shell with a polity *outline*; this is the first geometry driven
by a *resolved query* — the map begins doing its job as the onramp for point-rooted scopes.

Just the basin. No neighbors, no proximity shading (the old sandbox's 50 km shading stays
retired — neighbor geometry belongs to basin-ring, a later scope that carries actual per-neighbor
data; keeping single-basin = the basin alone preserves that distinction).

## Why now

WO10 made single-basin resolve live (signature). Its map tab is still untouched — single-basin
currently shows only the base substrate. WO11 draws the resolved basin.

## Build

**1. Geometry source — reuse `/api/basin-preview`, take only the containing basin.**
`/api/basin-preview?lat=&lon=&level=6` at `currentLat`/`currentLon` returns the containing basin
+ neighbors + river lines. Select **only the containing-basin feature**; discard neighbors and
rivers. Prefer selecting it by matching the **hybas_id the single-basin signature already
resolved** (see the honesty check below) rather than by basin-preview's own marker — that makes
geometry-selection and the map/signature agreement one operation. Report which selection path
held.

**2. Draw through the shell.**
`shell.add('single-basin', <geojson source>, [<fill spec>, <line spec>])` — one source, two layer
specs (fill + outline). Rely on shell idempotency for re-draws when coordinates change (same as
`drawPolityBoundary`). Fit-bounds via the existing `geojsonBbox` helper with padding; a single L6
basin is small, so bound tightly.

**3. Trigger + tab.**
Draw on single-basin resolve (example load / Get signature). Switch to the Map tab on resolve,
mirroring the polity behavior locked in WO7. (One small UX choice — veto if you'd rather
single-basin land on the Signature tab; I mirrored polity for consistency.)

**4. Style.**
Outline + light fill, as a **selection highlight** — a neutral attention color, deliberately
*not* drawn from the Explorer value palette (warm/dry=red, cold/wet=blue), so the basin never
reads as a value encoding. Keep it coherent with the polity-boundary visual language. Propose exact
values for review.

## Map must match the signature (honesty check — part of the accept gate)

The basin on the map must be the basin the signature describes. The signature's containing basin
comes from the engine's `resolve_single_basin`; basin-preview resolves its own containing basin
from lat/lon. If those ever disagree, the map would silently describe a different basin than the
panel — the exact class of landmine we don't ship.

- Confirm the single-basin signature payload exposes the resolved containing-basin `hybas_id`
  (neighborhood block or resolver block — check where). Report where it lives, or that it's absent.
- Assert the drawn basin's `hybas_id` **equals** the signature's resolved `hybas_id`. If
  basin-preview has no feature with that id, or the ids differ, **stop and report** — that's a
  finding, not a paper-over.
- If the id is not exposed anywhere in the signature payload, say so: the map can't be
  cross-checked against the signature, which is itself worth surfacing.

## Out of scope (explicit)

Rivers / any "setting" beyond the base hillshade; neighbor basins; proximity shading; any change
to the signature, Band T, or the buffer/polity map paths.

## Accept gate

- Timbuktu single-basin example → the containing basin draws through the shell (fill + outline),
  fit-bounds to it, **no neighbor basins**, on the Map tab.
- Drawn basin `hybas_id` == signature's resolved `hybas_id` (honesty check above).
- Polity boundary path unchanged; `sandbox.html` untouched.

## Tests

- Structural: a `'single-basin'` layer is added to the shell; source is a polygon GeoJSON; a
  single feature (not the neighbor set).
- Playwright: select the Timbuktu example → Map tab shows the basin; assert the shell layer is
  present. Extend the WO10 `load_timbuktu_single()` pattern.
- The id-match assertion, wherever it fits best (route/integration or Playwright — your call).
- Full suite green — zero FAILs, zero unexplained warnings. Note the new count.

## Constraints

- Review before write — Karl signs off each write.
- Shell API only — no direct `map.addSource` / `map.addLayer` in scope code.
- `sandbox.html` and the buffer/polity paths untouched.

## Findings

`docs/edop/surface/wo11_findings.md`. Report: geometry-selection path used; where the resolved
`hybas_id` lives (and the match result); the tab/UX choice as shipped; the chosen style values.