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
| WO02 | Load Lovejoy regions onto the map + region rationale | **complete** (B superseded by WO02.5) |
| WO02.5 | Subregion rationale extraction — verbatim spans + page numbers | **complete** |

---

## You are here

WO01 / WO02 / WO02.5 done. `#afr-map` renders the 34 Lovejoy regions; a region click highlights
its outline and writes the verbatim article rationale + page cite into `#afr-region` (top of the
right column), above a persistent About / citation block. Next: **WO03** — scope with Karl
(variable painting over L6/L8 basins, D-PLACE society layer, click-mode toggle; prospectus §4 +
the prerequisite checks below).

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

**Follow-ups → folded into WO02.5.** The three Part B follow-ups (blurb/rationale redundancy,
extraction cruft, the 7 `needs_review` entries) are all subsumed by the systematic re-extraction
in WO02.5. Do not hand-patch the 7 here.

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

---

## WO02.5 — Subregion rationale extraction (verbatim spans + page numbers)

**State: complete (2026-09-01).** Interjected between WO02 and WO03. Superseded the WO02 Part B
follow-ups (blurb/rationale redundancy, extraction cruft, 7 `needs_review` entries) and the whole
`lovejoy_region_notes.json` / `_afrNotes` path — both deleted. Source draft:
`docs/edop/workbench/WO- Subregion Rationale Extraction (Lovejoy et al. 2021).md`.

**Why.** WO02's Part B `rationale` field was an ad-hoc `DEF` regex per region plus heuristic
trimming — 27/34 auto, 7 flagged, and the 27 carry ligature/footnote/hyphenation cruft and
inconsistent span boundaries. This is talk-facing copy for Braga. Redone on one deterministic rule.

**Architecture (settled with Karl 2026-09-01):**
- **One runtime source** — `app/static/workbench/lovejoy_regions.geojson`. `rationale` + `page` +
  `ethnonyms` become feature `properties`. `lovejoy_region_notes.json` and the `_afrNotes` fetch/
  global are removed.
- **One curated master** — `data/lovejoy/lovejoy_rationales.md`, git-tracked (force-added; `data/`
  is gitignored), reviewed and edited by Karl. Durable source of the rationale prose, page
  numbers, and ethnonym lists.
- **`whg_staging`** — untouched (read-only, geometry + `src_id`). No DB field for any of this.
- **Build** — `build_lovejoy_geojson.py` merges three inputs per feature: geometry from
  `whg_staging.lovejoy.regions`, `name`/`macro` from LPF dataset 1155, `rationale`/`page`/
  `ethnonyms` parsed from the curated master.

### Goal

For each of the 34 subregions, extract the **verbatim** article text presenting that subregion's
rationale, with page numbers, suitable for quoting in `#afr-right`. No rewriting, summarising, or
interpretation — quotable source text with provenance. Karl reviews all 34 by hand; the job is to
make that review fast, not to remove it.

### Source

`articles/Lovejoy_etal_defining-regions-of-pre-colonial-africa.pdf`, region-description section
**pp. 8–22** ("North Africa / Northwest" … "Kalahari", ends at "Conclusion"). Subregion and
broad-region names are **set bold** in the PDF (subsetted font, `.B` fontname suffix) — the
extractor reads bold runs to get the ordered anchor list + each anchor's page. Body prose is
**10 pt**; footnote blocks (9 pt), the Table 1 controlled-vocabulary page (8 pt) and superscript
markers (6 pt) are excluded by size filter, which removes header/footer/footnote contamination in
one pass. Names match WHG dataset 1155 (Table 1).

### Extraction rules

1. **Span start** — the full sentence containing the first bold occurrence of the subregion name
   under its parent broad-region heading (not just from the bold token).
2. **Span end** — immediately before the next subregion's span start, or the next broad-region
   heading, whichever comes first.
3. **Keep everything in the span** — ethnonym lists, trade/polity narrative included. Do not trim
   to "the environmental part"; the mix of claim types is the point.
4. **Broad-region lead-in** — capture the text between a broad-region heading and its first
   subregion span **once**, on the parent record. Do not duplicate into children. (Most likely
   point of disagreement — the West Africa lead-in runs over a page before Central Savanna.)
5. **Page numbers** — record `page_start` and `page_end`; if a span crosses pages, both.
6. **Mechanical cleanup only:**
   - Strip flattened footnote-reference markers (trailing `.51`, `.22` superscripts).
   - Repair line-break hyphenation (`north- ern` → `northern`); preserve genuine hyphens.
   - Normalise whitespace; remove running headers/footers (`History in Africa`,
     `Defining Regions of Pre-Colonial Africa`, the `https://doi.org/…Cambridge University Press`
     line).
   - Preserve diacritics and non-Latin transliterations as they appear.
7. **Footnote body text** is out of scope. Record footnote numbers that occurred within the span
   if cheap, for later citation-chasing.

### Output — Part A (done)

New extractor `scripts/edop/workbench/build_lovejoy_rationale.py` → **`data/lovejoy/lovejoy_rationales.md`**
(the curated master). One `## <src_id> · <name>` section per subregion, a `- macro/page/flags/
ethnonyms` block, then the verbatim rationale as one wrapping paragraph; plus a 6-entry appendix
of broad-region lead-in text (review context, not a feature). Per-entry `hyphen-joins:` line lists
line-wrap joins for eyeball (some are real hyphens the repair fused). Parser contract for step 3
is in the file's header comment.

Result: **34/34 captured, 0 missing, 16 flagged** (SHORT / NO_BOUNDARY_LANGUAGE / CROSS_PAGE /
LONG / one HYPHEN_JOIN) — all with legible reasons, no escalation needed. `ethnonyms` is a
best-effort list from the span's "Ethnonyms included …" sentences; Karl curated the rough spots
(Eastern Savanna, Southeast, Kalahari, WCN/WCS). `build_lovejoy_notes.py` is superseded — delete
at step 3.

### Output — Part B / step 3 (done)

- `build_lovejoy_geojson.py` parses `lovejoy_rationales.md` and folds `rationale` + `page` +
  `ethnonyms` into each feature's `properties` (keyed on `src_id`); `blurb` dropped.
- `renderAfrRegion()` writes into **`#afr-region`** (top of the right column): region name / macro
  / `FROM THE ARTICLE (P. n)` / `(PP. n–m)` header (dash-detect on `page`) / rationale in quotes,
  then an `<hr>`. Below it, a **persistent `#afr-about` block** — heading "African Regions in
  Historical Perspective" + flush-right `web site` link (africanregions.org/about.php), a
  placeholder intro paragraph (Karl to edit), `<hr>`, and the full article citation at `.78rem`
  (title bolded). `properties.ethnonyms` rides along **unrendered** — Karl's later use.
- Feature click **highlights the clicked outline** — `setFeatureState({selected})` +
  `line-*` `['case', ['feature-state','selected'], …]` paint; `promoteId: 'src_id'` on the source;
  prior selection cleared each click.
- `lovejoy_region_notes.json` + `_afrNotes` removed; `build_lovejoy_notes.py` deleted.
- `?v=<mtime>` cache-bust on the geojson URL (`_static_mtime()` in `app/web/pages.py`,
  `lovejoy_v` context on both workbench render paths) — the file changes during rationale review.

### Flagging (assign, don't fix — set Karl's review priority)

`SHORT` / `LONG` (>~2× off median) · `NO_BOUNDARY_LANGUAGE` (no spatial-extent terms) ·
`CROSS_PAGE` (span straddles a page break; `page` shows the range) · `SPAN_UNCERTAIN` (located
page ≠ bold-run page hint) · `HYPHEN_JOIN` (line-wrap repair fused a real hyphen — camelCase
residue, e.g. `EssoukTadmekka`). Escalation ladder (offsets-only model call, degraded-source stop)
was **not needed** — bold anchors + size filter gave a clean deterministic pass.

### Follow-up (WO03+, not this WO)

- `blurb` is dropped, not reconciled — the redundancy question is moot.
- `ethnonyms` — Karl "has in mind to do something further" with these; for now a passenger field.

### Out of scope

- Full "what's here" / "what's claimed" panel redesign.
- D-PLACE / variable-painting work (WO03).

### Acceptance — met 2026-09-01

- `data/lovejoy/lovejoy_rationales.md` — 34 verbatim rationale sections + `page` + `ethnonyms`,
  6 lead-in appendix entries; free of headers/footers, footnote markers, footnote-block citations;
  diacritics preserved. Both extractors re-runnable offline.
- geojson features carry `rationale` / `page` / `ethnonyms`; `renderAfrRegion()` → `#afr-region`
  with quoted rationale + page cite, no blurb, clicked outline highlighted, persistent About /
  citation block below; no console errors. `lovejoy_region_notes.json` + `_afrNotes` +
  `build_lovejoy_notes.py` gone. `pytest tests/` green (519 passed, 14 skipped). Karl reviewed in
  browser.

### Notes

- PDF text-layer quality is the main unknown; WO02's `DEF`-regex success on 27/34 says bold
  anchors are at least partly reliable, but the cruft in those 27 says the text layer has ligature
  and footnote-flattening damage. Expect rule 6 to do real work.
- Keep `data/lovejoy/lovejoy_regions_prose.txt` regen in the script — Karl's review reads it.
