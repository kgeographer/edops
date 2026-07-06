# WO14 — BasinATLAS choropleth: global basin paint in sandbox_v2

**Branch:** `surf_wo14` → merge to `surface` at accept gate.
**Type:** Build — first choropleth. New rendering mechanism (PMTiles vector source +
feature-state paint) on the v2 map. BasinATLAS/physiographic variables only; gridded datasets
are WO15.

## Goal

Port cliopatria.html's global basin choropleth into sandbox_v2: paint all L6 basins by a chosen
BasinATLAS-path variable, coloured from the variable's p10–p90 domain, with a variable selector
and legend. Global paint (all basins), polity boundary drawn over it as context — the same
figure the tiles bought on the pilot: the polity reads against a painted surrounding field, and
zooming out gives a global view.

cliopatria.html is the reference implementation. How much is a direct port vs. adapted to the
WO8 shell is yours to judge (see the shell question below) — port what ports cleanly, adapt what
doesn't, and report which was which.

## Scope this WO — the four static-path variables only

The cliopatria variable menu spans four groups across two rendering mechanisms. This WO takes the
**feature-state-on-basin-tiles** mechanism only:

- Aridity index
- Annual precipitation
- Mean annual temperature
- Cropland extent % (BasinATLAS)

All four paint through `/api/explorer/values` → `{hybas_id: value}` + p10/p90 meta →
`setFeatureState` on the basin vector source. This is one rendering path, end to end.

**Explicitly WO15, not this WO:** the gridded groups — Paleoclimate/LMR (temperature anomaly,
precipitation anomaly; static GeoJSON) and HYDE (cropland fraction, grazing fraction; raster
tiles). They're a different rendering mechanism and carry a temporal dimension + a year control
that only makes sense once a time-indexed layer exists. Splitting at the mechanism seam keeps
this WO to one paint path. The variable selector should be built so the gridded groups can be
added in WO15 without restructuring — but they render nothing in WO14.

## First task — verify the shell holds a PMTiles feature-state source

Everything drawn on the v2 map so far (single, buffer, ring, polity outline) has been GeoJSON
through `shell.add`. This is the first PMTiles vector source with a feature-state paint loop. The
WO8 findings claimed the shell "accepts either source type; no restructuring required when
PMTiles arrives" — but that was written before any PMTiles layer existed, and forward claims in
this project have not always held (single-basin-live, the fixtures). So verify it against reality
before wiring the paint:

- Register the PMTiles protocol and add `basin06.pmtiles` as a **shell-managed source** with a
  fill layer whose paint reads `['coalesce', ['feature-state', 'fc'], 'transparent']`.
- Confirm the WO8 shell either handles a PMTiles vector source cleanly, or needs a documented
  extension to do so. If it needs extending (e.g. the shell's source/layer model assumes GeoJSON,
  or feature-state layers need lifecycle handling the shell doesn't provide), that extension is
  legitimate WO14 work — do it, keep the shell's named add/remove/restyle contract intact, and
  report what changed. If the choropleth layer genuinely can't sit inside the shell's API, say so
  and report how it's managed instead rather than forcing it.

Report the outcome as F14.x either way — this is the one part of the WO with real unknowns; the
rest is a faithful port of working cliopatria code.

## Build (after the shell question is settled)

1. **Paint loop.** On variable select: call `/api/explorer/values?var=X&level=6&su=s` (match
   cliopatria's params — confirm the `su` default it uses), iterate `{hybas_id: value}`, compute
   colour `t` from the p10–p90 domain in the `meta`, `setFeatureState({source, sourceLayer,
   id: Number(id)}, {fc})`. Clear prior feature-state on variable change so stale paint doesn't
   linger. Port cliopatria's colour ramp; report which ramp and whether it's per-variable or
   shared.

2. **Variable selector.** The grouped menu shown in the pilot (group headers as disabled
   options). WO14 wires only the four static-path variables live; the gridded group entries may be
   present-but-inert or omitted — your call, but if present they must not error on select. Report
   which you did.

3. **Legend.** The p10–p90 domain with the colour ramp and the variable's units. Whatever
   cliopatria shows, ported.

4. **Polity boundary over paint.** When a polity is resolved, its boundary draws over the
   choropleth as context (the existing polity boundary layer, on top). The choropleth is global
   and scope-independent — it does not filter to the polity. Painting is available whenever the
   map is shown; it does not require a polity.

## Where the selector lives / when paint is available

Global paint is scope-independent — it's a property of the map, not of a resolved signature. Put
the variable selector on the Map tab (or wherever it reads most naturally as a map control), live
whenever the map is shown. It does not gate on Get-signature and does not depend on scope. A user
can paint a variable, then resolve any scope to draw its geometry over the painted field. Confirm
the selector's placement and report it.

## Deliberately not in this WO

- Gridded datasets (LMR, HYDE) — WO15.
- Year / time control — WO15, with the gridded temporal layers.
- Caveat rendering — the caveat is a field on the signature payload; it renders wherever the
  variable renders as a trivial later step (relevant mainly to LMR in WO15). Not WO14.
- Member-only paint / `member_ids` on the polity neighborhood — not needed; paint is global, so
  there's no member set to match and no id-match honesty check here.
- L8 — L6 only, as everywhere so far.

## Accept gate

- All four static-path variables paint the global basin field from `/api/explorer/values`,
  coloured p10–p90, with a legend.
- Variable change repaints cleanly (no stale feature-state).
- Polity boundary draws over the paint as context; painting works with no scope resolved.
- The PMTiles source is shell-managed (or the documented exception is reported).
- Single/buffer/ring/polity geometry paths and `sandbox.html` untouched.

## Tests

- The paint path is hard to assert in unit tests (it's WebGL feature-state); lean on Playwright
  for what's observable — selector present and populated, `/api/explorer/values` called with the
  right params on select, legend renders and updates per variable, no console errors on repaint.
- A route-level test that `/api/explorer/values` returns the expected shape for each of the four
  variables (if not already covered by Explorer's own tests — check before adding).
- Full suite green — zero FAILs, zero unexplained warnings. Note the new count and correct any
  stale count in CLAUDE.md (per F13.8, the surface count needed correcting once already).

## Constraints

- Review before write — Karl signs off each write.
- Keep the WO8 shell's named add/remove/restyle contract intact; extend it if PMTiles needs it,
  don't fork around it silently.
- Reuse `/api/explorer/values` read-only — it's Explorer's route, shared; do not modify it.
- `sandbox.html` untouched.

## Findings

`docs/edop/surface/wo14_findings.md`. Report: the shell/PMTiles outcome (handled as-is vs.
extended vs. exception) — this is the key finding; the `su` param and colour ramp ported from
cliopatria; the selector placement; whether gridded entries are inert-present or omitted; how much
was direct port vs. adapted.

## Open questions I'd have flagged (answer in findings if they surface)

- Does the WO8 shell hold a feature-state-painted PMTiles source as-claimed, or need extending?
  (The one real unknown.)
- Does cliopatria paint with a fixed `su=s`, or expose the s/u choice? WO14 can default to one
  and leave s/u exposure for later — report what cliopatria does and what you defaulted to.
- Is `basin06.pmtiles` already served/available to sandbox_v2's origin, or does the tile source
  need wiring into the static path first? If the tiles aren't reachable, that's a blocker to
  surface immediately, not work around.

