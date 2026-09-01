# African Regions — Workplan

Living doc. WO sections are added as they're designed, tackled one at a time, and marked
**complete** when done. Design that naturally forms several WOs can be dropped in ahead of
execution; we still take them one at a time.

- **Source:** `docs/design/_workbench/prospectus_AfricanRegions.md` (draft — nothing in stone).
- **Branch:** `wb_africa` (off `v04`).
- **Ships within v0.4 or not at all.** Target: Braga talk, 2026-09-23. v0.4 cutover is **not**
  reopened for this.
- **Workflow:** WOs drafted here (Claude or Karl), Karl approves, Claude Code executes,
  Karl reviews each change in the browser before commit.

---

## Status

| WO | Title | State |
|----|-------|-------|
| WO01 | African Regions tab scaffold + left map | **complete** |

---

## Prerequisite checks

Short investigations, done before the WOs that depend on them (prospectus §4). Not WOs themselves.

1. **Lovejoy polygon detail.** Pull the *Pre-Colonial African Subregions* geometry from
   `whg_staging` (`lovejoy` schema) and eyeball vertex density against L6/L8 basin edges. If
   heavily generalized, the boundary-coincidence framing is out and only within-polygon framing
   remains. ~10 min. **Do before WO that adds the polygon layer.**
2. **Tiling vs. overlap.** Do the 34 subregions partition Africa or overlap? Overlaps complicate
   click resolution. Quick spatial check in the same pull.
3. **Lovejoy prose.** Does the `whg_staging.lovejoy` record carry per-feature descriptions (for
   the right panel's "what's claimed" tab), or must the 34 blurbs be transcribed from the paper?
4. **D-PLACE African field survey.** `cedop.dplace.*` is local + prod (confirmed). Survey the EA
   variables; pick ~6 (subsistence-first) rather than dumping the set. Also decides how thin the
   society layer is over the Sahara / deep rainforest / North Africa.

---

## WO01 — African Regions tab scaffold + left map

**State: complete.** `d5da6d0` (grey-box layout: tab, nav moved above the row, map-left /
info-right, tab-switch show/hide + Leaflet `invalidateSize` fix). `<next>` (real MapLibre map:
`pmLightStyle()` extracted to shared `app/static/js/pm_basemap.js`; workbench loads MapLibre +
pmtiles; `ensureAfrMap()` lazy-inits the map, Protomaps light basemap, `bounds` fit to Africa,
nav control; `resize()` on re-show). `#afr-right` / `#afr-readouts` remain placeholders.

**Goal.** A new **African Regions** tab in `workbench.html` that lays out as *map on the left,
info panel on the right* (inverting the other three tabs, which are controls-left / map-right),
within the existing 6/6 row. Left column is a real, empty MapLibre map with the light Protomaps
basemap. Everything else is a labelled coloured placeholder `<div>`. No data, no polygons, no
societies, no painting, no wiring.

**Layout (option 1 — 6/6, inverted for this tab).**

- New tab: nav button `#tab-afr` ("African Regions") + pane `#panel-afr`, added to `#edopTabs` /
  `#edopTabContent` (Bootstrap 5, same as the other three). `#panel-afr` lives in the **left**
  `col-lg-6`, like the other panes.
- `#panel-afr` content = `<div id="afr-map">` (fills the column; give it a fixed height like the
  shared `#map`'s 340px, or taller — Karl to eyeball) + a `<div id="afr-readouts">` strip below
  it: coloured background, one sentence ("dynamic readouts — later WO").
- On `shown.bs.tab` → `#tab-afr`: hide the shared right-column Leaflet map `#map`, show a
  `<div id="afr-right">` in that same right `col-lg-6` — coloured background, one sentence
  ("info panel: *what's here* / *what's claimed* — later WO").
- On `shown.bs.tab` → any other tab: reverse (show `#map`, hide `#afr-right`); the handler
  already calls `map.invalidateSize()`, which covers the Leaflet redraw.
- Net effect on this tab: left col = MapLibre map, right col = info-panel placeholder. Physically
  still 6/6; no `col-12` breakout, no width juggling.

**Left map.**

- Own MapLibre GL instance (MapLibre + pmtiles are not yet loaded on `workbench.html` — add the
  CDN `<script>`s and CSS, matching `sandbox.html`'s versions).
- Basemap = the self-hosted Protomaps light style built for Sandbox (`pmLightStyle()` in
  `sandbox.html` — `pmtiles:///static/basemaps/protomaps-light.pmtiles`, 8-layer minimal
  land/water/bounds/sparse-labels). **Extract that builder into a shared file**
  (`app/static/js/pm_basemap.js`) and use it from both pages rather than copy-pasting.
- Lazy-init on first `shown.bs.tab` for `#tab-afr`; `map.resize()` on every subsequent show
  (container was `display:none`). Model on `sandbox.html`'s `_atlasEnsureMap`.
- Initial view: fit Africa (~`[-20, -36]` to `[52, 38]`).
- Page-scoped CSS in `app/static/css/workbench.css`; placeholder backgrounds any obvious colour.

**Out of scope (later WOs).**

- Lovejoy subregion polygons, click resolution, region prose.
- Variable-painting `<select>`s and choropleth paint over L6/L8 basins.
- D-PLACE society marker layer; regions-vs-societies click-mode toggle.
- Real content in `#afr-right` or `#afr-readouts`.
- Full Leaflet → MapLibre port of the rest of `workbench.html` — deferred; this tab keeps its own
  map instance (two map libs on the page is acceptable).

**Acceptance.**

- African Regions tab appears in the Workbench nav, activates with no console errors.
- On activation: left col shows a light-grey Protomaps basemap fit to Africa, MapLibre
  attribution present; right col shows the `#afr-right` placeholder; shared Leaflet `#map` hidden.
- Switch away → Leaflet `#map` visible and correctly sized again; switch back → MapLibre map
  re-renders sized correctly (no zero-height grey box).
- Other three tabs unchanged — layout, map, behaviour.
- `pytest tests/` green; any Workbench Playwright selectors still pass or updated in the same change.

**Notes / open.**

- `pm_basemap.js` extraction: keep it a plain function returning the style object; Sandbox's
  three call sites switch to it in the same change (small, low-risk) or a follow-up — executor's call.
- `docs/edop/workbench/` may need adding to `.gitignore` exceptions if this workplan should be
  tracked (the other `docs/edop/*` WO folders are). Karl's call.
