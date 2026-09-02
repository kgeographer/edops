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
| WO03 | Environmental variable painting on `#afr-map` (L8 default, L6/L8 pill, 8 vars) | **spec ready** — 4 commits, awaiting go |

---

## You are here

WO01 / WO02 / WO02.5 done. `#afr-map` renders the 34 Lovejoy regions; a region click highlights
its outline and writes the verbatim article rationale + page cite into `#afr-region`, above a
persistent About / citation block. **WO03 spec is written** (below, "Build spec" section) — 4 commits:
(1) YlOrBr terrain ramp for elevation+slope in `explorer.html`; (2) optional `bbox=` on
`/explorer/{values,categorical}` + tests; (3) `#afr-right` flex restructure + `#afr-var` select +
L6/L8 pill + citation flush-bottom; (4) the paint module (`_afrBasinSource` / `_afrPaint` /
legend, ported from `explorer.html`'s `makeColorFn`, basin layers `beforeId:'lovejoy-fill'`).
Awaiting Karl's go. D-PLACE society layer + region-vs-basin click-mode toggle are still later WOs.

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

---

## WO03 — Environmental variable painting on `#afr-map`

**State: outline approved (2026-09-02), not started.** Karl's answers to the 5 [Q] are folded in
below (see *Decisions*). One new side-item: the slope ramp.

### Decisions (Karl, 2026-09-02)

1. `dist_sink_km` — show under **Band E** (my catalog error, now fixed in the table).
2. **Africa-bounds fetch:** add `?bbox=` to `/api/explorer/values` (option a). Africa bbox pulls
   the Arabian peninsula too — accepted for now; go to a static id allowlist only if that reads
   badly later.
3. **PNV:** in scope. Categorical branch + a legend **below the panel content**, styled like
   Explorer's category meter-bars (swatch + label + proportional bar); long tail is fine, users
   scroll.
4. **`lovejoy-fill` wash:** stays on page load, **hides when a variable is painted**, returns when
   the selector is back on "Paint a variable…".
5. **Discharge ramp:** ~~bbox fixes it for free~~ — **reversed 2026-09-02.** Karl: every var on
   this page reads against the **global** distribution, exactly like Explorer — "wet in Africa" is
   not the same question as "wet vs. everywhere," and the Africa-only question is a different,
   narrower one we're not asking here. So `bbox` trims the returned `values` payload **only**;
   `meta` (and categorical ranking/colours) are always global. Discharge therefore still needs a
   real fix (log transform) — tracked as a follow-up tweak, not blocking.

### Side-item — terrain ramp (done in commit 1)

`makeColorFn` had no terrain path — `elevation_{max,min,mean}` and `slope_deg` all fell through
to VIRIDIS (purple→yellow). Commit 1 adds a hypsometric branch for **all four** —
`elevation_max`, `elevation_min`, `elevation_mean`, `slope_deg` → `TERRAIN_PAL` = ColorBrewer
**YlOrBr-7** (matches Sandbox). Karl reviewed: purple is out for both; elevation and slope on the
same brown family is fine (they still differ by domain). The workbench port carries the identical
four-key branch.

### Goal

Paint one BasinATLAS variable at a time as a choropleth over the African basins on `#afr-map`,
**L8 by default** with an **L6/L8 pill**. A variable `<select>` (grouped by band) sits below the
intro paragraph; the article citation moves to the bottom of the right column. The Lovejoy region
outlines and click→rationale behaviour (WO02.5) stay on top and unchanged. This is the
"within-polygon" instrument from the prospectus — overlay the regions on a painted surface and
read whether each one's interior coheres.

### The 8 variables (initial offering)

Grouped as Karl wants them shown (talk grouping, not strictly the catalog band):

| group | label in UI | `schema_key` (→ `/api/explorer/values?var=`) | col / type | ramp |
|---|---|---|---|---|
| **A** | Elevation maximum | `elevation_max` | `ele_mt_smx` float m | sequential |
| **A** | Slope | `slope_deg` | `slp_dg_sav` float ° (API ÷10) | sequential |
| **B** | Discharge, annual mean | `discharge_annual` | `dis_m3_pyr` float m³/s | **log / hard percentile clip** — range is 0 → >200 000 |
| **B** | Potential natural vegetation | `pnv_majority_name` | `pnv_cl_smj` **string** | **categorical** — different endpoint + swatch legend |
| **E** | Flow distance to marine outlet | `dist_sink_km` | `dist_sink` float km | sequential |
| **B** | Clay content | `pct_clay` | `cly_pc_sav` float % | sequential |
| **C** | Aridity index (P/PET) | `aridity_index` | `ari_ix_sav` float ×100 | RDBU, low = red (dry) |
| **C** | Precipitation, annual | `precipitation_annual` | `pre_mm_syr` float mm/yr | RDBU, low = red (dry) |

### Data path (reuse Explorer's, not Sandbox's)

- **Geometry:** `pmtiles:///static/explorer/basin0{6,8}.pmtiles`, source-layer `basin0{6,8}` —
  already served, gitignored, on the rsync/deploy list. New vector source + fill + hairline layer
  on `#afr-map`, inserted **below** `lovejoy-fill` / `lovejoy-line` (so region outlines + the
  click target stay on top).
- **Values:** `GET /api/explorer/values?var=<schema_key>&level=8&su=s` → `{meta:{min,max,p10,p90,
  zero_fraction,var_type,…}, values:{hybas_id: value|null}}`. Loop `setFeatureState({source,
  sourceLayer, id:Number(hybas_id)}, {fc: colorFn(value)})`; `fill-color` =
  `['coalesce',['feature-state','fc'],'transparent']`.
- **PNV only:** `GET /api/explorer/categorical?var=pnv_majority_name&level=8` →
  `{categories:[{id,name,count,color}], values:{hybas_id:cat_id}}`; swatch legend, no ramp.
- **Ramp:** port `makeColorFn(meta, 's', schemaKey)` + `interpPalette` / `RDBU` / `VIRIDIS` from
  `explorer.html` (universal rubric: warm/dry = red, cold/wet = blue; aridity + precip special-cased
  low = red; diverging when min < 0; else VIRIDIS sequential; terrain branch YlOrBr). **Ramp domain
  = global `meta`**, same as Explorer — `bbox` never scopes the domain.
- **s only.** No s/u toggle in this WO (all 8 are surface columns).

### Africa-bounds fetch  — `?bbox=` on `/api/explorer/values` (+ `/categorical`)

Optional `bbox=w,s,e,n`. It trims the returned **`values` payload only** — one query selects all
basins plus a `geom && ST_MakeEnvelope(…)` boolean; `meta` (min/max/p10/p90/n_valid) is computed
over **all** rows, `values` is emitted only for in-envelope rows. `/categorical` likewise: the
count/ranking/colour pass is global, only the per-basin `values` pass is bbox-filtered. So a
bbox call is byte-identical to Explorer on `meta`/`categories`, just fewer `values`. Purely
additive — Explorer passes no `bbox`
and are unaffected; add one route test. Africa bbox ≈ `[-20, -36, 55, 38]` (also catches the
Arabian peninsula — accepted). Payload for L8 drops from ~190 k basins to the Africa subset.

### UI / layout changes (`workbench.html`, `workbench.css`)

- **`#afr-right` → flex column.** Children top→bottom: `#afr-region` (WO02.5 dynamic block),
  `#afr-about` (heading + `web site` link + intro paragraph + **new controls**), then a pulled-out
  `#afr-cite` sibling with `margin-top:auto` so the citation sits flush at the bottom. (Citation
  markup moves out of `#afr-about`.)
- **Controls** under the intro paragraph: a `<select id="afr-var">` with `<optgroup label="A —
  Terrain">` / `B — Hydrology & soils` / `C — Climate`, default option "Paint a variable…"
  (nothing painted on load — tab still opens as the plain regions map); an L6/L8 segmented pill
  (`btn-group`, radio-style, L8 checked) next to it.
- **Legend** goes in `#afr-readouts` (the strip below the map — WO01 reserved it for "painted
  variable · legend · cell count"): variable name + units, the painted-basin count, and:
  - *numeric vars* — the ramp gradient with min / p10 / p90 / max ticks (global `meta`).
  - *PNV* — a **category meter-bar list** ported from Explorer's `renderCategoryBars` (swatch +
    class name + proportional bar, count/pct). Long tail is expected; it scrolls. If the strip is
    too short, the PNV legend can render into a panel-side block instead — executor's call.
- **`lovejoy-fill`** — wash stays as-is on load; when a variable is painted set `fill-opacity` to
  0 (keeps it as the invisible click target); restore the wash when the selector returns to
  "Paint a variable…".

### Interaction

- Region click: unchanged — highlight outline + rationale into `#afr-region`. Basin values are
  backdrop only; **no** basin-value readout or region-vs-basin click-mode toggle in this WO.
- Level pill or variable change → refetch values for the new (var, level), repaint, redraw legend.
  Debounce/guard against overlapping fetches.

### Out of scope (later WOs)

- Clipping / summarising the painted surface *within* a selected region (the actual "does the
  interior cohere" read — needs a spatial join, own WO).
- Basin hover/click value readout; region-vs-society click-mode toggle.
- D-PLACE society marker layer.
- Band T / temporal layers, s/u, month sliders.

### Acceptance (draft)

- African Regions tab: variable `<select>` (optgroups A / B / E / C, 8 options) + L6/L8 pill
  below the intro; article citation flush to the bottom of the right column.
- Pick a numeric variable → Africa basins paint at L8; legend in `#afr-readouts` shows variable +
  units + global ramp (min/p10/p90/max) + painted-basin count. Reads identically to Explorer.
- Pick PNV → categorical paint + a meter-bar legend (swatch / name / proportional bar), scrollable.
- `lovejoy-fill` wash shows on load, hides while a variable is painted, returns on "Paint a
  variable…". Region outlines + click→rationale work throughout, on top of the choropleth.
- L6/L8 pill switches level and repaints; no overlapping-fetch races.
- `/api/explorer/values?bbox=…` returns only in-envelope `values` with **global** `meta`; no-`bbox`
  behaviour unchanged (route test).
- Elevation + slope render YlOrBr (browns), not purple→yellow.
- No console errors; other Workbench tabs and Explorer unaffected; `pytest tests/` green.

---

## WO03 — Build spec (2026-09-02)

Executable. Four commits, in order. Karl reviews the UI in-browser before commit 4.
Africa bbox constant: **`-20,-36,55,38`** (W,S,E,N). Africa basin counts: **L8 ≈ 48,002**,
**L6 ≈ 4,187** (both `geom` GiST-indexed).

### Commit 1 — `feat(explorer): YlOrBr terrain ramp for elevation + slope`

`app/templates/explorer.html`, `makeColorFn` (~L451). Add the palette next to `VIRIDIS`/`RDBU`:

```js
// ColorBrewer YlOrBr-7 — matches sandbox.html TERRAIN_PAL (hypsometric)
const TERRAIN_PAL = ['#ffffd4','#fee391','#fec44f','#fe9929','#ec7014','#cc4c02','#8c2d04'];
```

In `makeColorFn`, **after** the `aridity_index`/`precipitation_annual` block and **before** the
final `VIRIDIS` return:

```js
if (['elevation_max','elevation_min','elevation_mean','slope_deg'].includes(schemaKey)) {
  const range = (hi - lo) || 1;
  return v => v == null ? '#d3d3d3'
    : interpPalette(TERRAIN_PAL, Math.max(0, Math.min(1, (v - lo) / range)));
}
```

All four keys go in the `.includes` list. `makeColorFn` had no terrain path — all four fell to
VIRIDIS. Karl reviewed the browns in-browser and OK'd them (purple out for both elevation and
slope). The numeric legend gradient samples `currentColorFn`, so it follows automatically.

Regression check: cycle every A–E numeric var in Explorer, no console errors, ramps sane.

### Commit 2 — `feat(api): optional bbox on /explorer/{values,categorical}`

`app/api/routes_common.py :: explorer_values` and `app/api/routes_explorer.py :: explorer_categorical`.

Add `bbox: Optional[str] = None` to both signatures. Shared parse helper (put in
`routes_common.py`, import into `routes_explorer.py`):

```python
def _parse_bbox(bbox: Optional[str]):
    if not bbox:
        return None
    try:
        w, s, e, n = (float(x) for x in bbox.split(","))
    except ValueError:
        raise HTTPException(status_code=400, detail="bbox must be 'w,s,e,n'")
    if not (-180 <= w < e <= 180 and -90 <= s < n <= 90):
        raise HTTPException(status_code=400, detail="bbox out of range or degenerate")
    return w, s, e, n
```

In each route, when `_parse_bbox` returns coords, add
`WHERE geom && ST_MakeEnvelope(w, s, e, n, 4326)` to **every** SELECT against `public.basin0{6,8}`
in that handler (values: one query; categorical: the top-N count pass **and** the per-basin
`cat_id` pass — both, so counts/pcts match the painted subset). Params passed positionally via
psycopg (`cur.execute(sql, (w, s, e, n))`), not f-string-interpolated. `meta` needs no change —
it's already derived from the filtered rows.

Test — `tests/` (wherever explorer routes are covered; else `tests/test_areas.py`):
- `values?var=elevation_max&level=8&bbox=-20,-36,55,38` → `len(values)` ≈ 48000, `< ` the no-bbox
  count; `meta.p10/p90/n_valid` stay equal to the no-bbox call (global).
- a hybas_id known to be outside Africa is absent from the bbox response.
- `bbox=1,2,3` → 400; `bbox=200,0,210,10` → 400.
- no `bbox` → byte-identical behaviour to before (count == global).

### Commit 3 — `workbench(africa): WO03 panel restructure + controls`

`app/templates/workbench.html`. **`#afr-right`** (currently the WO02.5 block) → flex column;
citation pulled out as a flush-bottom sibling; controls added under the intro. New inner markup:

```html
<div id="afr-right" style="display:none;flex-direction:column;height:460px;overflow-y:auto;background:#fff;border:1px solid #ddd;padding:.85rem 1rem;font-size:.9rem;line-height:1.4;">
  <div id="afr-region"></div>
  <div id="afr-about">
    <div class="d-flex justify-content-between align-items-baseline">
      <h6 class="mb-1">African Regions in Historical Perspective</h6>
      <a href="https://africanregions.org/about.php" target="_blank" rel="noopener" class="small">web site</a>
    </div>
    <p class="mb-2">This tab overlays the 34 pre-colonial African subregions proposed by
      Lovejoy et&nbsp;al. (2021) as a controlled vocabulary for linking open-source historical
      data. Select a region to read the article's rationale for its extent and the peoples
      associated with it. The regions were drawn for organising data rather than for
      environmental analysis; the Workbench places them over EDOPS basin signatures to ask how
      far each one holds together as an environmental unit.</p>
    <div id="afr-controls" class="d-flex align-items-center gap-2 mt-2 mb-1 flex-wrap">
      <select id="afr-var" class="form-select form-select-sm" style="width:auto;">
        <option value="">Paint a variable…</option>
        <optgroup label="A — Terrain">
          <option value="elevation_max">Elevation maximum</option>
          <option value="slope_deg">Slope</option>
        </optgroup>
        <optgroup label="B — Hydrology &amp; soils">
          <option value="discharge_annual">Discharge, annual mean</option>
          <option value="pnv_majority_name">Potential natural vegetation</option>
          <option value="pct_clay">Clay content</option>
        </optgroup>
        <optgroup label="E — Coastality">
          <option value="dist_sink_km">Flow distance to marine outlet</option>
        </optgroup>
        <optgroup label="C — Climate">
          <option value="aridity_index">Aridity index (P/PET)</option>
          <option value="precipitation_annual">Precipitation, annual</option>
        </optgroup>
      </select>
      <div class="btn-group btn-group-sm" role="group" aria-label="Basin level">
        <input type="radio" class="btn-check" name="afr-level" id="afr-lvl-6" value="6" autocomplete="off">
        <label class="btn btn-outline-secondary" for="afr-lvl-6">L6</label>
        <input type="radio" class="btn-check" name="afr-level" id="afr-lvl-8" value="8" autocomplete="off" checked>
        <label class="btn btn-outline-secondary" for="afr-lvl-8">L8</label>
      </div>
    </div>
  </div>
  <div id="afr-cite" style="margin-top:auto;padding-top:.5rem;">
    <hr class="my-2">
    <p class="mb-0" style="font-size:.78rem;color:#666;">
      Henry B. Lovejoy, Paul E. Lovejoy, Walter Hawthorne, Edward A. Alpers, Mariana Candido,
      Matthew S. Hopper, Ghislaine Lydon, Colleen Kriger, and John Thornton,
      &ldquo;<b>Defining Regions of Pre-Colonial Africa: A Controlled Vocabulary for Linking
      Open-Source Data for Digital History Projects</b>,&rdquo; <i>History in Africa</i> 48
      (2021): 1&ndash;26,
      <a href="https://doi.org/10.1017/hia.2020.17" target="_blank" rel="noopener">https://doi.org/10.1017/hia.2020.17</a>.
    </p>
  </div>
</div>
```

(Only changes vs WO02.5: `display:none` → keeps, add `flex-direction:column`; `#afr-controls`
added; citation `<p>` + its `<hr>` moved from inside `#afr-about` into new `#afr-cite` with
`margin-top:auto`. `renderAfrRegion` already targets `#afr-region` and appends its own trailing
`<hr>` — unchanged.)

**`#afr-readouts`** — becomes the legend host:

```html
<div id="afr-readouts" style="margin-top:.5rem;padding:.5rem .75rem;background:#f6f4ee;border:1px solid #ddd;font-size:.8rem;min-height:2.6rem;">
  <span class="text-secondary">Pick a variable to paint the basins.</span>
</div>
```

No `workbench.css` changes — all inline, matching the existing afr style.

### Commit 4 — `workbench(africa): WO03 variable painting on #afr-map`

`app/templates/workbench.html` `<script>`. State vars by `_afrSelected` (~L441):

```js
let _afrVarKey = '';          // selected schema_key ('' = none painted)
let _afrLevel = 8;            // 6 | 8
let _afrBasinLevel = null;    // pmtiles level currently on the map
let _afrPaintSeq = 0;         // stale-fetch guard
const AFR_BBOX = '-20,-36,55,38';
const AFR_VAR_LABEL = {
  elevation_max:'Elevation maximum', slope_deg:'Slope',
  discharge_annual:'Discharge, annual mean', pnv_majority_name:'Potential natural vegetation',
  pct_clay:'Clay content', dist_sink_km:'Flow distance to marine outlet',
  aridity_index:'Aridity index (P/PET)', precipitation_annual:'Precipitation, annual',
};
```

Port verbatim from `explorer.html` into the workbench `<script>` (one-line provenance comment,
no shared file this WO): `VIRIDIS`, `RDBU`, `TERRAIN_PAL`, `lerpColor`, `interpPalette`,
`makeColorFn` — **including the Commit-1 terrain block** so the two copies stay in step.

**`_afrBasinSource(level)`** — model on `sandbox.html :: _atlasBasinLayer`:

```js
function _afrBasinSource(level) {
  const sl = 'basin0' + level;
  if (_afrBasinLevel === level && _afrMap.getSource('afr-basins')) return sl;
  ['afr-basin-fill','afr-basin-line'].forEach(id => { if (_afrMap.getLayer(id)) _afrMap.removeLayer(id); });
  if (_afrMap.getSource('afr-basins')) _afrMap.removeSource('afr-basins');
  _afrMap.addSource('afr-basins', { type:'vector', url:`pmtiles:///static/explorer/${sl}.pmtiles` });
  _afrMap.addLayer({ id:'afr-basin-fill', type:'fill', source:'afr-basins', 'source-layer':sl,
    paint:{ 'fill-color':['coalesce',['feature-state','fc'],'transparent'], 'fill-opacity':0.82 } }, 'lovejoy-fill');
  _afrMap.addLayer({ id:'afr-basin-line', type:'line', source:'afr-basins', 'source-layer':sl,
    paint:{ 'line-color':'rgba(90,90,90,0.10)', 'line-width':0.3 } }, 'lovejoy-fill');
  _afrBasinLevel = level;
  return sl;
}
```

`beforeId:'lovejoy-fill'` puts basins **under** the region fill (invisible click target) and
`lovejoy-line` (outlines) — regions and their click→rationale stay on top.

**`async _afrPaint()`** — the only paint entry; called on `<select>` change and level change:

```
seq = ++_afrPaintSeq
if !_afrMap || !_afrMap.getLayer('lovejoy-fill'): return          // map/tab not ready; user re-picks
key = _afrVarKey
if !key:
  _afrClearPaint(); _afrMap.setPaintProperty('lovejoy-fill','fill-opacity', <wash>)   // wash = current literal, e.g. 0.10
  #afr-readouts -> '<span class="text-secondary">Pick a variable to paint the basins.</span>'
  return
_afrMap.setPaintProperty('lovejoy-fill','fill-opacity', 0)
#afr-readouts -> 'Loading…'
isCat = key === 'pnv_majority_name'
url = isCat
  ? `/api/explorer/categorical?var=${key}&level=${_afrLevel}&bbox=${AFR_BBOX}`
  : `/api/explorer/values?var=${key}&level=${_afrLevel}&su=s&bbox=${AFR_BBOX}`
data = await fetch(url).then(r => r.ok ? r.json() : r.json().then(e => { throw new Error(e.detail) }))
if seq !== _afrPaintSeq: return                                  // superseded
sl = _afrBasinSource(_afrLevel)
_afrMap.removeFeatureState({ source:'afr-basins', sourceLayer:sl })
if isCat:
  idToColor = Object.fromEntries(data.categories.map(c => [c.id, c.color]))
  for [id,cat] of data.values: setFeatureState({source:'afr-basins',sourceLayer:sl,id:Number(id)}, {fc: idToColor[cat] ?? '#ccc'})
  _afrLegendCategorical(key, data.categories, Object.keys(data.values).length)
else:
  fn = makeColorFn(data.meta, 's', key)
  for [id,v] of data.values: setFeatureState({source:'afr-basins',sourceLayer:sl,id:Number(id)}, {fc: fn(v)})
  _afrLegendNumeric(key, data.meta, fn, Object.keys(data.values).length)
catch -> #afr-readouts shows `<span class="text-danger">${msg}</span>`, restore lovejoy-fill wash
```

**`_afrClearPaint()`** — `if (_afrMap.getSource('afr-basins')) _afrMap.removeFeatureState({ source:'afr-basins', sourceLayer:'basin0'+_afrBasinLevel });` (keep source/layers; just drop states).

**`_afrLegendNumeric(key, meta, fn, n)`** — into `#afr-readouts`. Port explorer's numeric legend
SVG (explorer.html ~L1066–1085): `lo = meta.p10 ?? meta.min`, `hi = meta.p90 ?? meta.max`; ~40
`<rect>` sampling `fn(lo + t*(hi-lo))`; labels `lo`/`mid`/`hi` with `meta.units`; caption
`${AFR_VAR_LABEL[key]} · ${n.toLocaleString()} basins`.

**`_afrLegendCategorical(key, categories, n)`** — into `#afr-readouts`. Port explorer's
`renderCategoryBars` table (swatch / name / proportional bar / pct) filtered to `count > 0`;
wrap in `<div style="max-height:120px;overflow-y:auto;">`; caption
`${AFR_VAR_LABEL[key]} · ${n.toLocaleString()} basins`.

**Wiring** — in the DOMContentLoaded init near the other afr setup:

```js
document.getElementById('afr-var').addEventListener('change', e => { _afrVarKey = e.target.value; _afrPaint(); });
document.querySelectorAll('input[name="afr-level"]').forEach(r => r.addEventListener('change', e => {
  if (!e.target.checked) return;
  _afrLevel = Number(e.target.value);
  _afrPaint();          // _afrPaint -> _afrBasinSource swaps the pmtiles level
}));
```

No auto-paint on `ensureAfrMap` load (`_afrVarKey` starts `''`). No teardown on tab-away
(feature-state persists harmlessly). Keep the `TEMP (dev eyeball)` default-tab line for now.

**Intro-text visibility.** The About intro (`#afr-about-text` = heading + `web site` link +
paragraph) is wrapped separately from `#afr-controls`. `renderAfrRegion()` sets
`#afr-about-text` `display:none` on first region click — once a rationale is up the intro is
noise. Painting a variable never calls `renderAfrRegion`, so "paint first" keeps the intro
visible. It does not come back (there is no region-deselect). `#afr-controls` and `#afr-cite`
are unaffected. `_afrLegendNumeric` renders the ramp SVG at `width="100%"` + `viewBox` /
`preserveAspectRatio="none"` so it fills `#afr-readouts`.

### Deploy

No new static assets — `basin0{6,8}.pmtiles` already on the `MAINTAIN_DEPLOY.md` rsync list and
on `edops04` (Explorer uses them). Commits 1–2 ship with the branch merge.

### Acceptance — as the outline's *Acceptance (draft)*, plus:

- Explorer: `elevation_{max,min,mean}` + `slope_deg` render YlOrBr browns (not purple→yellow);
  every other A–E var unchanged; numeric legend gradient matches the map.
- `values` / `categorical` with `bbox=-20,-36,55,38&level=8` → ~48 k `values`, `meta`/`categories` global;
  malformed `bbox` → 400; no-`bbox` calls unchanged (route tests).
- Workbench: picking each of the 8 paints Africa at L8; discharge shows real contrast; PNV shows
  the scrollable meter-bar legend; L6/L8 swaps and repaints; `lovejoy-fill` wash toggles; region
  click→rationale still works over the choropleth; no console errors; `pytest tests/` green.
