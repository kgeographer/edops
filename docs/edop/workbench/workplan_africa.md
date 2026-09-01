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
| WO02 | Load Lovejoy regions onto the map + region rationale | **complete** (B has follow-ups) |

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
  tracked (the other `docs/edop/*` WO folders are). Karl's call. *(done — `491e3ae`.)*

---

## WO02 — Load Lovejoy regions onto the map + region rationale

**State:** drafted.

**Reconciliation already done** (2026-08-31, this session — findings below). Data sources are
settled; no "examine" step remains.

### Sources

- **Published WHG dataset 1155** (*Pre-Colonial African Subregions*), downloaded to
  `data/lovejoy/whg_dataset_1155.lpf` and `.tsv` — the citable version. Current names,
  macro-region parents, per-region blurbs, and **32/34 polygons**.
- **`whg_staging.lovejoy.regions`** (dev DB `whg_staging`, schema `lovejoy`, 34 rows) — Karl's
  working copy. Geometry byte-identical to the published export for 32 regions; holds the **real
  multipolygons for the 2 the export is missing** (Western Sahara, Kalahari — see Part C). Older
  `hc_18` name, no blurbs. `regions_take1` (32 rows) is an earlier draft — ignore.
- **The article** `articles/Lovejoy_etal_defining-regions-of-pre-colonial-africa.pdf` — per-region
  *rationale*, fuller than the LPF blurbs.

Reconciliation result: all 34 `src_id`s (`hc_01`…`hc_67`) match both sides; 32 geometries
byte-identical; macro-regions all match. Only real diffs: the 2 point-vs-polygon regions, and
`hc_18` "Eastern" (staging) vs "Eastern Interior" (published — use published).

### Part A — geometry + attributes → artifact + render

- Build `app/static/workbench/lovejoy_regions.geojson` (new dir): 34 features, each with
  `src_id`, `name` (from the published LPF/TSV — current, so `hc_18` = "Eastern Interior"),
  `macro` (parent region), `blurb` (the LPF short description).
  - **All 34 geometries from `whg_staging.lovejoy.regions`** (`geom`) — the 32 that match the
    published export byte-for-byte, plus the real Western Sahara + Kalahari polygons the export
    lost. One source, no per-feature split.
  - Names + blurbs joined on `src_id` from `data/lovejoy/whg_dataset_1155.lpf` (or `.tsv`).
  - Build script `scripts/edop/workbench/build_lovejoy_geojson.py` — queries `whg_staging` +
    reads the LPF, writes the merged GeoJSON. Committed. If the `.geojson` is small (~200–400 KB
    likely) commit it too; else gitignore + add to `MAINTAIN_DEPLOY` rsync list.
- Render on `#afr-map`: GeoJSON source + fill layer (low opacity) + line layer (outline), fetched
  once in `ensureAfrMap()` after style load. Africa bounds unchanged.
- **Click a region → populate `#afr-right`** (name, macro, LPF blurb, and the article rationale
  from `lovejoy_region_notes.json`) via `renderAfrRegion()`. No popups. `#afr-right` is the single
  click-output target for this tab — D-PLACE society-marker clicks will render here too (later WO).
- **Prereq check — DONE (2026-08-31).** Mainland Lovejoy boundaries are schematic: ~15–58 km per
  vertex (median ~27 km), can't trace L8 (~2–10 km) or really L6 (~10–50 km) basin edges. Island
  groups are finer (~1.5–2.2 km/vertex). **Boundary-coincidence framing is out; within-polygon is
  the instrument** (overlay a region → which basins fall inside → paint variables within → does
  the interior cohere). Polygons render fine on a continental map. Karl: precise outer-edge
  alignment doesn't matter for this application.

### Part B — per-region rationale from the article  (DRAFT, 2026-08-31)

- `scripts/edop/workbench/build_lovejoy_notes.py` → `app/static/workbench/lovejoy_region_notes.json`
  (`{src_id: {name, page, blurb, rationale, needs_review}}`) — `blurb` = LPF short form,
  `rationale` = the article's defining paragraph(s), pp. 12–23.
- **27/34 land clean automatically; 7 flagged `needs_review`** — hand-finish against
  `data/lovejoy/lovejoy_regions_prose.txt` (the cleaned section text, written by the same script):
  **Comoros, Horn, Nile Valley, North Coast, Northwest, Southeast, West Central South** (missed
  the defining paragraph — it's in a broad-region intro — or got a short/boundary-bled slice).
  Horn is genuinely short (the article gives it 3 sentences).
- Wired: region click renders `blurb` + `rationale` into `#afr-right` (`renderAfrRegion()`).

**Follow-ups (WO03+, not now):**
- The WHG `blurb` is often just the opening of the article `rationale` — sometimes verbatim,
  sometimes lightly shortened. Showing both is redundant for many regions. Refine: diff them and
  present one (or the blurb as a lead, rationale as expandable).
- Minor extraction cruft in `rationale` for some regions: mid-word hyphen breaks from PDF line
  wraps ("north- ern"), trailing footnote numbers stuck to the last word ("Zombo.51"). Clean in
  the same pass, or in `build_lovejoy_notes.py`.
- Hand-finish the 7 `needs_review` entries.

**"North Coaast" typo** — WHG dataset 1155's title for `hc_10` is misspelled (double-a), in the
published export *and* `whg_staging`. Display-corrected via `NAME_FIX` in both build scripts;
flagged as a secondary item in the WHG issue draft.

### Part C — WHG export-bug issue  (DRAFT written, 2026-08-31)

`docs/edop/workbench/whg_export_bug_issue.md` — dataset export (LPF + TSV) drops contributor polygons
for places with multiple geometries, picking the reconciliation Wikidata point. Dataset 1155:
Western Sahara (wid 7130907, `wd:Q6250`) and Kalahari (wid 7130908, `wd:Q14202768`). Plus the
"North Coaast" typo as a secondary item. **Karl to file against WHG.**

### Out of scope (later WOs)

- Variable-painting `<select>`s / choropleth over L6/L8 basins.
- D-PLACE society marker layer; regions-vs-societies click-mode toggle.
- Full "what's here" / "what's claimed" panel design and wiring (Part A click just shows a name).
- Promoting the GeoJSON to a `gaz` table (only if a later WO needs server-side spatial joins).

### Acceptance

- `lovejoy_regions.geojson`: 34 features, `src_id` + `name` + `macro` + `geom_source`; Western
  Sahara + Kalahari are polygons; `hc_18` is "Eastern Interior".
- Regions render on `#afr-map` (fill + outline); clicking one shows its name; no console errors;
  tab switch-away-and-back still fine.
- Vertex-density prereq result recorded.
- `lovejoy_region_notes.json` with `blurb` + `rationale` per region (or noted gaps).
- `docs/edop/workbench/whg_export_bug_issue.md` drafted.
- `pytest tests/` green (build script is offline).

### Notes

- `whg_staging` is dev-only — build script runs locally, emits a static artifact; nothing at app
  runtime touches `whg_staging` (same as `gaz.geonames_cities`).
- New static dir `app/static/workbench/` — `app/static` is already a StaticFiles mount, no route.
