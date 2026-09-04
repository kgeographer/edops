# African Regions — Workplan

Living doc. WO sections are added as they're designed, tackled one at a time, and marked
**complete** when done. Design that naturally forms several WOs can be dropped in ahead of
execution; we still take them one at a time.

- **Source:** `docs/design/_workbench/prospectus_AfricanRegions.md` (draft — nothing in stone).
- **Branch:** `wb_africa` (off `v04`).
- **Ships within v0.4 or not at all.** Target: Braga talk, 2026-09-23. v0.4 cutover is **not**
  reopened for this.
- **Workflow:** WOs drafted here (Claude or Karl), Karl approves, Claude Code executes,
  Karl reviews each change in the browser before commit. **From WO04 on:** each WO is done on
  its own branch cut from `wb_africa`, merged back on accept (`--no-ff`).

---

## Status

| WO | Title | State |
|----|-------|-------|
| WO01 | African Regions tab scaffold + left map | **complete** |
| WO02 | Load Lovejoy regions onto the map + region rationale | **complete** (B superseded by WO02.5) |
| WO02.5 | Subregion rationale extraction — verbatim spans + page numbers | **complete** |
| WO03 | Environmental variable painting on `#afr-map` (L8 default, L6/L8 pill, 8 vars) | **complete** (`38297c0` `2ec5af5` `e39b777`, + `b10b281` `4999a0d`) |
| WO04 | Operationalize D-PLACE societies (+ layer control, rivers) | **complete** — c1–c3 + skunkworks UX track (merged `80fec2c` into `wb_africa`) |
| WO05 | Areal signature per Lovejoy region | **build spec ready** (2026-09-04) — below |
| WO06 | `Societies_refine` (was seeded as WO5) | seed in `D-PLACE_Markers.md` |

---

## You are here

WO01–WO04 done, on branch **`wb_africa_wo04`** (@ `bee0638`). `#afr-map` renders the 34 Lovejoy
regions + a paintable BasinATLAS variable (`#afr-var` select + L6/L8 pill, global ramp domain,
legend in `#afr-readouts`), and a top-right **Layers** box toggling **Regions** / **Societies**
(528 African D-PLACE points) / **Rivers** (34 mainstems). A unified click dispatcher resolves
topmost of {marker, region}; the right panel reflows between region mode (title + collapsible
rationale + paint controls + citation) and society mode (region title, collapsed rationale,
`#soc-vars` D-PLACE card, paint controls dropped to the bottom, citation retired). Society card:
name + `<id> record` link (opens the D-PLACE page in a 90vw modal iframe), EA042 / EA034 with a
magnifier that rings every marker sharing that value + a count.

**Branches:** `wb_africa_wo04` holds WO01–WO04. `wb_africa` (@ `4d91156`) is one commit behind
(the WO04 build spec). The `TEMP (dev eyeball)` line in `workbench.html` still forces the African
Regions tab open — **remove before `wb_africa_wo04` merges up**.

**Next / not yet scoped (own WOs):** society styling by trait (EA042 colour) over a painted
variable; societies-in-a-region list + environmental spread + n (the "does it cohere" read);
society ↔ region cross-highlight; graduate the skunkworks D-PLACE modal / EA magnifier out of
`SKUNKWORKS` tags; discharge log-ramp; rivers `upland_skm` / z-order tuning; the two untracked
reference files (`africaregions.html`, `D-PLACE_Markers.md`) are local-only.

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

---

## WO04 — Operationalize D-PLACE societies (+ layer control, rivers)

**State: outline — 3 questions answered 2026-09-02 (see *Decisions*), ready for a build spec.**
Branch `wb_africa_wo04` off `wb_africa`.
Broad goal: **make the D-PLACE societies usable on the African Regions tab — how, exactly, is
TBD.** This WO stands up the display pieces first; what to *do* with them (click behaviour,
region↔society cross-highlight, filtering, a societies-vs-regions mode) becomes later WO04
elements once we can see them on the map.

### Decisions (Karl, 2026-09-02)

1. **Society set = African continent** — point-in-polygon vs Natural Earth `admin0`
   (`continent='Africa'`), **528** societies. Not the paint bbox.
2. **Layer control = on-map box, top-right** ("a cliché that earned its place") — HTML checkboxes,
   not a row in `#afr-controls`.
3. **Both layers must render at the default (continental) Africa zoom** — no zoom-in required. So
   the `sandbox/rivers.pmtiles` reuse is **out** (its tileset is baked `minzoom 3`). Piece B needs
   a low-zoom source instead — a static Africa **major-rivers GeoJSON** (HydroRIVERS filtered to
   the high Strahler orders + simplified; the mainstems you'd want on a continental map anyway),
   built once from `gaz.rivers`, served from `app/static/workbench/`. Same for societies — a
   GeoJSON source renders at any zoom.

### Context

- Societies tab uses `dplace.societies WHERE contribution_id='dplace-dataset-ea'` — 1,291
  societies, `longitude`/`latitude` on the row. **~528 fall on the African continent**
  (point-in-polygon vs Natural Earth `admin0`, `continent='Africa'`); **551** inside the paint
  bbox `-20,-36,55,38` (the extra ~23 = Arabian-peninsula bleed + a few offshore islands).
- `dplace.*` is local **and** prod (confirmed) — no deploy blocker.
- `#afr-map` currently carries: Protomaps basemap, `lovejoy` (fill + line), `afr-basins`
  (fill + hairline, only when a variable is painted), a `NavigationControl`. No layer control.
- MapLibre has **no built-in layer-control widget**. Sandbox's MapLibre map does it with plain
  HTML checkboxes in an on-map box (`#v3-layer-control` / `#v3-layer-rivers`), toggling
  `setLayoutProperty(id,'visibility',…)` — the pattern to copy.
- `sandbox/rivers.pmtiles` is **not reusable here** — its tileset is baked `minzoom 3` and the
  Africa-fit view sits ~zoom 2.5–3, so nothing would draw. Africa needs its own low-zoom source
  (see Piece B).

### Piece A — African societies as a toggleable layer

- **Data:** a purpose-built GeoJSON — either a static artifact `app/static/workbench/afr_societies.geojson`
  (built once by a script, like `lovejoy_regions.geojson`) or a route `GET /api/workbench/afr-societies`.
  Lean toward the **static artifact** (the set is fixed; no runtime DB hit; `?v=<mtime>` cache-bust
  like the geojson). Point features, props `soc_id` / `name` / `subsistence` / `religion` (enough
  for the later popup; extend when the click WO needs it). 528 features, a few KB. Built from
  `dplace.societies` ⋈ `admin0` (continent = Africa).
- **Layer:** source `afr-societies` + `circle` layer `afr-soc-dots`, added last so it's topmost.
  Neutral styling — small filled circle + white stroke; no data-driven colour, no clustering.
- **Invariant:** toggling Societies must not disturb a painted variable (separate source/layer) —
  assert in the acceptance check.
- **No click behaviour.** Cursor-pointer on hover to signal it's live; no popup / `#afr-region`
  write yet.

### Piece B — rivers as a toggleable layer

- **Data:** static `app/static/workbench/afr_rivers.geojson` — HydroRIVERS (`gaz.rivers`) clipped
  to Africa, filtered to the high Strahler orders (`ord_clas` threshold TBD at build — pick the
  cut that yields the continental mainstems: Nile, Congo, Niger, Zambezi, Orange, Senegal,
  Volta, Shabelle/Jubba, Okavango…), `ST_SimplifyPreserveTopology` for size. Renders at any zoom.
  Build script under `scripts/edop/workbench/`. Size-check at build; keep it well under ~1 MB.
- **Layer:** source `afr-rivers` + `line` layer `afr-rivers-line`, **off by default**, second
  checkbox in the control. Width can key on `ord_clas` (as Sandbox does).
- **Z-order:** provisional — above `afr-basin-line`, below `lovejoy-line`. Revisit once both
  layers are visible together.

### Layer control (both pieces)

- Small HTML box on `#afr-map`, **top-right**, styled like the Leaflet layer controls on the
  other tabs. Two checkboxes — **Societies**, **Rivers** — **both off on load**. Toggle flips
  `setLayoutProperty(<layerId>,'visibility','visible'|'none')`. Build once when the layers are
  added in `_afrMap.on('load')`; a MapLibre `IControl` shim or just a positioned `<div>`.

### Out of scope (this WO / later WO04 elements)

- Any society **click** action (popup, cross-highlight with regions, write to `#afr-region`).
- Region ↔ society cross-filtering / "which societies fall in this Lovejoy region".
- A societies-vs-regions click-mode toggle.
- Society styling by trait (subsistence / religion colour), clustering, legend.
- Final rivers z-order + default-state + zoom affordance.

### Acceptance (draft)

- `afr_societies.geojson` — 528 point features, props `soc_id`/`name`/`subsistence`/`religion`;
  build script re-runnable offline.
- `afr_rivers.geojson` — the African mainstems, simplified, well under ~1 MB; renders at the
  default continental zoom.
- `#afr-map` has a top-right layer-control box with **Societies** and **Rivers** checkboxes, both
  off on load. Ticking each shows its layer at the current zoom (no zoom-in needed).
- A painted variable stays painted through either toggle; region click→rationale still works;
  no console errors; `pytest tests/` green.

### Still open

- rivers size filter — `upland_skm >= 100000` is the starting cut (see spec); eyeball and adjust.
- Rivers z-order vs basins / region outlines — settle once both layers are on screen.

---

## WO04 — Build spec (2026-09-02)

Executable. Branch **`wb_africa_wo04`** off `wb_africa`; 3 commits; Karl eyeballs each map change
before commit. Both data artifacts are **static, committed** (like `lovejoy_regions.geojson`) —
`dplace` + `gaz` are local-and-prod, but the sets are fixed so no runtime route.

### Commit 1 — `afr_societies.geojson` + build script

`scripts/edop/workbench/build_afr_societies.py` → `app/static/workbench/afr_societies.geojson`.

- Query `dplace.societies s` (`WHERE s.contribution_id='dplace-dataset-ea'`), LEFT JOIN
  `dplace.data`/`dplace.codes` for **EA042** (subsistence) and **EA034** (religion) — reuse the
  join + code-name filters from `routes_workbench.py :: societies()` (excludes `'Missing data'`,
  `''`, `'Two or more sources'`, etc.), INNER JOIN
  `gaz.admin0 a ON ST_Contains(a.geom, ST_SetSRID(ST_MakePoint(s.longitude, s.latitude), 4326))
  AND a.continent = 'Africa'`.
- Emit a FeatureCollection: `Point` geoms, props `{ soc_id, name, subsistence, religion }`
  (null where the trait is missing). **Expect 528 features** (~60–90 KB). Print the count.
  Re-runnable offline; commit the geojson.

### Commit 2 — `afr_rivers.geojson` + build script

`scripts/edop/workbench/build_afr_rivers.py` → `app/static/workbench/afr_rivers.geojson`.

- `gaz.rivers` has full HydroRIVERS attrs. Continental mainstems = a **catchment-area** cut, not
  `ord_clas` (which is Strahler-ish: `ord_clas<=1` is still 124k reaches). Measured, Africa bbox:

  | filter | reaches | ~geojson (simplify 0.02°) |
  |---|---|---|
  | `upland_skm >= 150000` | ~9k | ~0.5 MB |
  | **`upland_skm >= 100000`** | **12.9k** | **~0.67 MB** |
  | `upland_skm >= 50000` | 21.5k | ~1.1 MB |

- Query: `SELECT hyriv_id, ord_clas,
  ST_AsGeoJSON(ST_SimplifyPreserveTopology(geom, 0.02)) FROM gaz.rivers
  WHERE geom && ST_MakeEnvelope(-20,-36,55,38,4326) AND upland_skm >= 100000`.
  Props `{ ord_clas }` (kept for line-width). Print feature count + file size. Eyeball on the map;
  drop the threshold to 50000 if too sparse, raise to 150000 if too busy; loosen the simplify
  tolerance if lines look crude. Commit the geojson if ≤ ~1 MB; else gitignore + add to
  `MAINTAIN_DEPLOY.md` rsync list.

### Commit 3 — layer control + both layers on `#afr-map`

`app/web/pages.py` — add `afr_societies_v` + `afr_rivers_v` (via the existing `_static_mtime`)
to **both** workbench render calls, beside `lovejoy_v`.

`app/templates/workbench.html`, in `_afrMap.on('load')` after the lovejoy layers:

- **Rivers:** `addSource('afr-rivers', { type:'geojson', data:'/static/workbench/afr_rivers.geojson?v={{ afr_rivers_v | default("") }}' })`;
  `addLayer({ id:'afr-rivers-line', type:'line', source:'afr-rivers',
  layout:{ visibility:'none' },
  paint:{ 'line-color':'#5a9bd4', 'line-opacity':0.8,
  'line-width':['case', ['<=', ['to-number',['get','ord_clas']], 1], 1.2, 0.6] } }, 'lovejoy-line')` —
  `beforeId:'lovejoy-line'` puts rivers under region outlines, above the (dynamically added)
  `afr-basin-*`.
- **Societies:** `addSource('afr-societies', { type:'geojson', data:'/static/workbench/afr_societies.geojson?v={{ afr_societies_v | default("") }}' })`;
  `addLayer({ id:'afr-soc-dots', type:'circle', source:'afr-societies',
  layout:{ visibility:'none' },
  paint:{ 'circle-radius':3.5, 'circle-color':'#333', 'circle-opacity':0.9,
  'circle-stroke-width':1, 'circle-stroke-color':'#fff' } })` — added last ⇒ topmost.
  `mouseenter`/`mouseleave` set the canvas cursor to `pointer`/`''`. **No click handler.**
- **Control box** — `document.createElement('div')` appended to `#afr-map` (MapLibre's container
  is `position:relative`), styled from Sandbox's `#v3-layer-control`
  (`position:absolute;top:10px;right:10px;z-index:1;background:rgba(255,255,255,.92);border:1px solid #ccc;border-radius:6px;padding:7px 10px;font-size:.78rem;box-shadow:0 1px 4px rgba(0,0,0,.15)`):
  an uppercase "Layers" caption + two `<label><input type="checkbox">…</label>` rows —
  `#afr-lyr-societies`, `#afr-lyr-rivers`, **both unchecked**. Each `change` handler flips its
  layer's `visibility` via `setLayoutProperty`.

Nav control is `top-left` on this map, so `top-right` is clear. `_afrPaint` only ever touches
`afr-basins` + `lovejoy-fill` opacity → the two overlay layers are independent by construction.

### Acceptance

- `build_afr_societies.py` → 528-feature geojson, props `soc_id`/`name`/`subsistence`/`religion`;
  `build_afr_rivers.py` → African mainstems geojson, count + size printed. Both re-runnable offline.
- `#afr-map` top-right **Layers** box: Societies + Rivers, both off on load. Tick Societies → grey
  dots at the default continental zoom (no zoom-in). Tick Rivers → blue lines, same.
- Paint a variable → toggle either overlay → variable stays painted. Toggle an overlay → click a
  region → rationale still renders. No console errors; `pytest tests/` green.

### Still open (build / review)

- `upland_skm` threshold + simplify tolerance — tune by eye.
- rivers z-order once a choropleth is also on — provisional above basins / below region outlines.

---

## WO04 — Close-out (2026-09-03)

**Done.** Stated purpose — *operationalize the D-PLACE societies on the African Regions tab* —
met. What follows are refinements/additions, and they get their own WOs.

### Built to spec (branch `wb_africa_wo04`)

- **c1 `120a3e1`** — `build_afr_societies.py` → `afr_societies.geojson`: 528 continent-clipped EA
  societies (`ST_Contains` vs `admin0`), props `soc_id`/`name`/`subsistence`(EA042)/`religion`(EA034).
- **c2 `f3ddda2`** — `build_afr_rivers.py` → `afr_rivers.geojson`: `gaz.rivers` `upland_skm ≥ 100000`,
  **dissolved by `main_riv`** → 34 river systems, 47 KB (not the 1.8 MB per-reach cut).
- **c3 `a5cdbb3`** — `#afr-map` top-right **Layers** box; `afr-soc-dots` (circle) + `afr-rivers-line`
  layers; `pages.py :: _workbench_ctx()` cache-bust for all three geojson artifacts.

### Diverging track — skunkworks UX/UI (merged `bee0638`, was branch `wb_africa_socpanel_skunk`)

Once the layer was live it was faster to iterate the interaction/panel behaviour freehand than
to spec each nit. Ran on its own branch off `wb_africa_wo04`, merged back `--no-ff`. Five commits:

- **`3c83575`** — marker-click **panel reflow** + **unified click/cursor dispatcher**
  (`queryRenderedFeatures` over `['afr-soc-dots','lovejoy-fill']`, topmost wins; one `mousemove`
  for the cursor — replaces the per-layer region click + four hover handlers). `#afr-right` split
  into `#afr-region-head` / `#afr-region-body`; `#afr-about` → `#var-select`; new `#soc-vars`.
  `.mode-society` / `.cite-retired` classes drive the reflow.
- **`c8886d8`** — rationale is a **caret toggle** (`#afr-rationale-toggle` → `#afr-rationale-text`);
  region mode shows it expanded, society mode collapsed-but-reachable. `text-muted`/`text-secondary`
  stripped from `#afr-right`.
- **`2f78cfb`** — hover **name tooltip** on markers; **selection outline** via `promoteId:'soc_id'`
  + feature-state (`removeFeatureState` then set on click); `#soc-vars` polish (Name row, `<id>`
  linked).
- **`4d44405`** — **EA-value magnifier**: click the glass by an EA042/EA034 value → `afr-soc-match`
  ring layer filters to `['==',['get',field],value]`, `#afr-hl-status` shows the deduped count +
  a `clear` link. Empty-space map click also deselects the region outline.
- **`1cbe0b1`** — **D-PLACE society page in a 90 vw modal iframe** (`#afr-dplace-modal`); d-place.org
  sends no `X-Frame-Options`/CSP so it frames, and its own layout is responsive. `<id> record`
  link replaced the external new-tab link; modal header keeps an "open on d-place.org" escape.
  All tagged `SKUNKWORKS` — the modal + EA magnifier want a deliberate spec + de-tag in a
  follow-up WO.

### Explicitly not in WO04 (later WOs)

- Society dot colour by trait; societies-in-region membership list; environmental spread + n per
  region; society ↔ region cross-highlight; society clustering / a societies legend.
- Graduating the skunkworks modal + magnifier out of `SKUNKWORKS` (spec, a11y, de-tag).
- Discharge log-ramp (WO03 carry-over); rivers `upland_skm` / z-order fine-tune.
- `wb_africa_wo04` still carries the `TEMP (dev eyeball)` default-tab line — pull before it
  merges toward `v04`.
- society dot colour/size — neutral grey now; trait styling is a later WO04 element.

---

## WO05 — Areal signature per Lovejoy region (scope, 2026-09-03)

**Not started.** Scope decisions all settled (50-year Band T window, modal trigger placement/reuse
locked 2026-09-04); coherence-badge prerequisite fix done and merged. **Build spec written
2026-09-04** — see *WO05 — Build spec*, below — ready to execute on branch `wb_africa_wo05`.

### Goal

For each of the 34 Lovejoy regions, a full **areal signature** — the per-variable distribution
over the region's containing basins, with the histogram + summary the polity signature already
renders — surfaced from a **profile modal** on the African Regions tab.

### Why this, and why cheap

- **Prospectus framing.** The prospectus names these subregions as EDOPS study areas going
  forward. Computationally a Lovejoy region is just a polygon — the same shape as a polity time
  slice, and `engine.py` already generates areal signatures for those.
- **Machinery done.** `engine.py :: areal_signature_polygon(geom_wkt, conn, level=6, bands,
  from_year, to_year, include_detail, resolver_year, polity_id)`. HTTP: `/api/areas?scope=polity
  &year=<int>&detail=true` (year is **required** — it's the resolver/extent year). The Sandbox
  Polities renderer consumes `profile_groups`: per row `${score} percentile` + coherence badge +
  `renderHistogram(detail.distribution)`, grouped into A–T band accordions.
- **Sidesteps the D-PLACE problems.** Reads the region's *own* basins, not societies — **no
  coverage gaps**, no ethnographic-present caveat. Wide distributions are the point (the panel's
  copy already says the regions were drawn for data organisation, not environmental analysis).

### Decisions (Karl, 2026-09-03)

1. ~~Precompute, static artifact.~~ **Reversed in the build spec (2026-09-04)** — Karl pointed
   out Sandbox's own Polities tab doesn't precompute either: geometry is loaded for every time
   slice up front, but the areal signature itself is fetched live, on demand, one slice at a
   time (it's ~9s of compute, per `sandbox.html`'s own measurement — too slow to do for all of
   them speculatively). WO05 has the same shape already: all 34 region geometries are always on
   the map; the signature is the expensive per-region step. **Now: a live route,
   `GET /api/lovejoy-signature?src_id=…`**, fetched on modal-open with a client-side cache so a
   repeat open of the same region is instant. See *WO05 — Build spec*, Commit 1, for the reasoning
   and the route itself.
2. **Level L6 only.**
3. **Band T IN**, with a **fixed 50-year window** (not the 400-year LPF `whens`, which smooths
   LMR to nothing) — the first sustained Atlantic-trade surge. **Locked (2026-09-04):
   `from_year=1600, to_year=1650`** (West Central Africa → Brazil; aligns with the SlaveVoyages
   1601–1650 era). HYDE over that window: use one representative epoch (~1650) or the endpoints —
   `detail` handles either; pick at build.
4. **UI: a `profile` modal, triggered from the rationale line.** **Locked (2026-09-04):** the
   trigger is a link **flush-right on the `#afr-rationale-toggle` line** (not a separate control
   in `#afr-controls`) — region-scoped, disabled/hidden until a region is selected. It opens a
   modal whose body is the ported signature renderer, fed live from the Commit-1 route rather
   than a precomputed entry (all bands, the locked 1600–1650 T window). **Reuse the existing
   `#afr-dplace-modal` markup/logic for dual purpose** (society D-PLACE page + region signature)
   rather than building a second modal — share the shell, parameterize header/body/escape-link
   per use; narrow it for the signature case since a signature reads tall, not wide. Exact
   mechanics (shared modal element with swapped content vs. a second modal cloned from the same
   CSS) are an executor call at build-spec time.

### Depends on / must-do-first — the coherence badge

**Done and merged (`59bfcea`, merged to `wb_africa` `1b95cf8`, 2026-09-03/04).** The diagnostic
below is now history — recorded for context on *why* the fix was needed, not a live blocker.

- Original rule: on the area's *weighted percentile scores*, `spread = p90 − p10`; `concentrated`
  if `spread < _SPREAD_THRESHOLD (20.0)` else `spread`. (`aggregate_b1` ~L1985, `aggregate_b5`
  ~L1663.)
- Not stuck — small areas got a mix (Goguryeo@300: 12 conc / 22 spread; Kongo@1550: 9 / 24).
  **Large areas collapsed to `spread`** (Songhai@1497, 113 basins: 2 / 29): a continental-scale
  polygon genuinely spans a wide slice of the global gradient for almost every variable, so
  `p90 − p10 > 20` nearly always. `20` was calibrated for settlement/ring scale.
- Secondary problem: `p90 − p10` is blind to mass-concentration-with-a-tail (a spiked histogram
  with a thin tail still read `spread`).
- **Fix:** switched the coherence test to weighted **IQR (p75−p25) < 20**, tail-robust to the
  thin-tail case; `p90−p10` is still emitted in `detail.spread` (B6 modality + histogram range
  labels still use it unchanged). `detail` gained `iqr`, `p25`, `p75`. Threshold stays 20 —
  live-probe effect: Songhai 2/29 → 14/17, Goguryeo 12/22 → 25/9, Kongo 9/24 → 19/14; genuinely
  broad variables (elev_min, dist_sink, karst) still read `spread`. New contract test
  `test_b1_coherence_is_iqr_driven`; engine + app test suites green.
- **Consequence for WO05:** this was one shared fix — it changes badge output for **both**
  Sandbox polity signatures and whatever WO05 renders for Lovejoy regions. The prior plan to
  **suppress the badge at region scale** (because even a re-tuned p90–p10 threshold would mostly
  say `spread` for continent-scale polygons) needs re-checking against real Lovejoy-region IQR
  output before the WO05 build spec locks that suppression in — it may no longer be necessary,
  or may still be warranted at a different threshold. Check at build time, don't assume either way.
- Shelved alongside: the "as of {resolver_year} CE" stamp rendering on *static* A–E variables
  (Karl's original bug from the same screenshots) — the resolver year describes the region's
  spatial extent, not the vintage of a soil measurement. Fix when the renderer is ported: a
  single area-level "extent as of {year}" caption, or scope the stamp to Band T rows only.

### Renderer port

The Sandbox Polities signature renderer is coupled to Sandbox state; WO05 ports a trimmed copy
into `workbench.html` (band accordions + `renderLeaf` + `renderHistogram`, Band T slider kept —
see the build spec's reversed decision below), fed from the live `/api/lovejoy-signature` route
rather than a precomputed artifact. Main JS cost.

### Caveats to state in the modal

- Distributions are **wide by construction** — big, deliberately heterogeneous areas; that's
  informative, not a defect (hence the badge suppression above).
- Points-stand-for-territories does **not** apply (no society points) — cleaner than the
  society-spread version.
- Band T is one fixed 50-year window, no scrub — a region-character summary, not the interactive
  polity panel.

### Rough cost

Build script ~an afternoon (engine call per region + assemble + size-check). Renderer port +
modal wiring: the bulk, ~a day depending on how tangled the Sandbox renderer is. Coherence
re-tune: deferred, separate.

---

## WO05 — Build spec (2026-09-04, revised same day — precompute dropped for a live route)

**Revision note.** The first pass of this spec (precompute all 34 regions to a static
`lovejoy_signatures.json`) is superseded before any commit landed. Karl's pushback: Sandbox
doesn't do this either — the Polities tab loads geometry for every time slice up front but only
computes/fetches the **areal signature** for one slice at a time, on an explicit "Get Signature"
click, precisely because that computation isn't cheap (`sandbox.html`'s own code comment clocks
`/api/areas?scope=polity&detail=true` at **~9s**). Precomputing all 34 Lovejoy regions would mean
paying that cost ~34 times up front (for regions nobody may look at during the talk) *and* still
juggling a potentially-oversized static JSON (gitignore/rsync dance) for something that doesn't
need to be static at all. WO05 already has the exact analog to "geometry for every slice, sig on
demand": **the map already renders all 34 region geometries** (the `lovejoy` layer, always on) —
signature-on-demand for the one region you click is the natural fit, not a bulk precompute.

Commit 1 below replaces the build script with a live route mirroring `/api/area`'s own
`areal_signature_polygon` call. Commit 2's modal fetches it on open, with a loading state (that
~9s isn't disappearing — it's real per-region compute time, level=6 or not) and a small
client-side cache so re-opening the same region's modal within a session is instant.

Executable. Branch **`wb_africa_wo05`** off `wb_africa`. Three commits; Karl eyeballs the modal
in-browser before commit 3. Modal-sharing mechanics (below) are a CC implementation call — Karl
has no opinion beyond "reuse if it's cheaper than building a second modal."

### Commit 1 — `GET /api/lovejoy-signature` (live route, no precompute)

`app/api/routes_workbench.py`, same file/conventions as the tab's other endpoints
(`@router.get(..., include_in_schema=False)`, `app.db.connection.db_connect` — **not**
`scripts.shared.db_utils.db_connect**, the offline-script one; the two are different functions,
see CLAUDE.md's `db_utils` note). Modeled directly on `routes_sandbox.py :: area()`'s
`areal_signature_polygon` call (~L1105), swapping the polity-name lookup for a Lovejoy `src_id`
lookup.

- **Geometry lookup — lazy module-level cache, not a DB hit.** The app never touches
  `whg_staging` at runtime (standing rule); `app/static/workbench/lovejoy_regions.geojson` is
  already the single served source of truth for these 34 polygons, so read it once, cache in a
  module global, same idiom the LISA parquet cache already uses ("read once → cached in a module
  global" per CLAUDE.md's data-source table):
  ```python
  import shapely.geometry
  _LOVEJOY_GEOMS: Optional[Dict[str, tuple]] = None   # {src_id: (wkt, name, macro)}, lazy

  def _lovejoy_geoms() -> Dict[str, tuple]:
      global _LOVEJOY_GEOMS
      if _LOVEJOY_GEOMS is None:
          path = Path(__file__).resolve().parents[2] / "static" / "workbench" / "lovejoy_regions.geojson"
          data = json.loads(path.read_text())
          _LOVEJOY_GEOMS = {
              f["properties"]["src_id"]: (
                  shapely.geometry.shape(f["geometry"]).wkt,
                  f["properties"]["name"],
                  f["properties"]["macro"],
              )
              for f in data["features"]
          }
      return _LOVEJOY_GEOMS
  ```
- **Route:**
  ```python
  _LOVEJOY_T_FROM, _LOVEJOY_T_TO = 1600, 1650   # locked WO05 decision

  @router.get("/lovejoy-signature", include_in_schema=False)
  def lovejoy_signature(src_id: str):
      geoms = _lovejoy_geoms()
      if src_id not in geoms:
          raise HTTPException(status_code=404, detail=f"Unknown Lovejoy src_id '{src_id}'")
      geom_wkt, name, macro = geoms[src_id]
      try:
          conn = db_connect()
          payload = areal_signature_polygon(
              geom_wkt, conn,
              level=6, bands=None,   # None = A-E + T, since from_year/to_year are given
              from_year=_LOVEJOY_T_FROM, to_year=_LOVEJOY_T_TO,
              include_detail=True,
              resolver_year=None, polity_id=None,
          )
      except Exception as e:
          raise HTTPException(status_code=500, detail=str(e))
      finally:
          conn.close()
      payload["resolver"] = {"type": "lovejoy_region", "src_id": src_id, "name": name, "macro": macro}
      return payload
  ```
  `payload` is exactly `{scope, shortfall, bands, temporal, caveats, rows}` plus the added
  `resolver` block — the same shape `sandbox.html`'s Polities renderer already consumes as
  `payload.rows`/`payload.scope`, so the ported renderer (Commit 3) needs no reshaping.
  `scope.type` will still read `'polity'` (the engine's generic polygon label); use
  `payload.resolver.name`/`.macro` for the modal heading instead, not `scope.type`.
- **Found while testing this commit: 3 of 34 regions have zero L6 basin coverage.** St. Helena
  (`hc_45`), Cabo Verde (`hc_40`), and Mascarenes (`hc_44`) — small offshore island groups —
  resolve to **zero** BasinATLAS L6 basins (`resolve_polygon(...).empty`); `areal_signature_
  polygon` doesn't guard this and blows up with a raw SQL syntax error (`... hybas_id IN ()`) —
  a pre-existing engine gap (never exercised before; every Cliopatria polity is real land), not
  something WO05 introduced, and not touched here. **Fixed at the route level**: `lovejoy_
  signature()` calls `resolve_polygon` itself first and returns a clean `422` with a plain-English
  message (rather than a leaked SQL trace) when the region has no basin coverage, before ever
  calling `areal_signature_polygon`. The other three small island regions in the geometry set —
  Comoros, Gulf Islands, Canarias — do resolve (1–2 basins each) and are unaffected. `Commit 2`'s
  modal error-handling path (the `catch` block that renders `e.message` as `text-danger`) already
  covers this case for free — clicking one of the 3 affected regions' "Signature ↗" link will show
  the 422 message in the modal rather than a scary error.
- **Latency is real, not a defect.** Lovejoy regions are large polygons — plausibly *slower* than
  the ~9s polity baseline for the bigger ones (more L6 basins to aggregate). No caching layer on
  the server side for WO05 (would need an invalidation story this feature doesn't need yet); the
  client-side cache in Commit 2 is what makes repeat opens cheap. If a specific region proves
  unworkably slow in review, that's a build-time signal to revisit, not a spec change.
- No new static asset, no cache-bust var, no `pages.py` change — this commit is app-code only,
  ships and deploys exactly like any other route.

### Commit 2 — panel + modal shell: profile link + dual-purpose `#afr-dplace-modal`

### Commit 2 — panel + modal shell: profile link + dual-purpose `#afr-dplace-modal`

**Rationale-row restructure** (`app/templates/workbench.html`, ~L264–266). Currently
`#afr-rationale-toggle` is a bare `<p>` carrying its own `hidden` attribute (toggled by
`_afrSetRationale()`). Wrap it in a flex row so a flush-right link can sit on the same line,
and move the `hidden` gate to the wrapper — the toggle `<p>` and the new link share one
visibility condition (a region is in scope), which is already exactly what `_afrSetRationale()`
computes from `p.rationale`:

```html
<div id="afr-rationale-row" class="d-flex justify-content-between align-items-baseline mb-1" hidden>
  <p id="afr-rationale-toggle" class="mb-0 small text-uppercase" style="letter-spacing:.04em;cursor:pointer;">
    <span id="afr-rationale-caret">▾</span> <span id="afr-rationale-label">From the article</span>
  </p>
  <a href="#" id="afr-profile-link" class="small text-decoration-none">Signature ↗</a>
</div>
```

`_afrSetRationale(p, expanded)` — swap `toggle.hidden = true/false` for
`document.getElementById('afr-rationale-row').hidden = true/false` at both the early-return and
the success path; no other change to that function's logic. This means the profile link appears
and disappears exactly where the rationale toggle already does today — including in society mode
(`renderAfrSociety` calls `_afrSetRationale(region, false)` for the containing region, so the link
tracks `_afrSelected` there too) and on empty-space deselect.

**Modal reuse — dual-purpose `#afr-dplace-modal`.** Rather than a second modal element, give the
existing one a second body pane and a small set of per-mode swaps (title text, side-link
visibility, dialog width), toggled by which `afrOpen*` function calls `.show()`. This is the
proposed approach for the efficiency Karl asked for; if it turns out fussier in practice than
expected, falling back to a second, near-duplicate modal is an acceptable pivot — call it during
the build, not before.

```html
<!-- was: single-purpose D-PLACE iframe modal. Now dual-purpose: D-PLACE iframe (existing) or
     a region signature (WO05) -- swapped by which afrOpen*Modal() function is called. -->
<div class="modal fade" id="afr-dplace-modal" tabindex="-1" aria-hidden="true">
  <div class="modal-dialog modal-dialog-centered" id="afr-dplace-dialog" style="max-width:90vw;width:90vw;">
    <div class="modal-content" style="height:88vh;">
      <div class="modal-header py-2">
        <h6 class="modal-title mb-0" id="afr-dplace-title">D-PLACE society <span class="text-muted small" id="afr-dplace-subtitle">— CC-BY-NC 4.0</span></h6>
        <a id="afr-dplace-ext" href="#" target="_blank" rel="noopener" class="small ms-auto me-3">open on d-place.org ↗</a>
        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
      </div>
      <div class="modal-body p-0">
        <iframe id="afr-dplace-frame" src="" style="width:100%;height:100%;border:0;" loading="lazy"></iframe>
        <div id="afr-profile-body" style="display:none;width:100%;height:100%;overflow-y:auto;padding:1rem 1.25rem;"></div>
      </div>
    </div>
  </div>
</div>
```

```js
function _afrModalMode(mode) {   // 'dplace' | 'profile' — shared show/hide + sizing
  const isDplace = mode === 'dplace';
  document.getElementById('afr-dplace-frame').style.display = isDplace ? '' : 'none';
  document.getElementById('afr-profile-body').style.display = isDplace ? 'none' : '';
  document.getElementById('afr-dplace-subtitle').style.display = isDplace ? '' : 'none';
  document.getElementById('afr-dplace-ext').style.display = isDplace ? '' : 'none';
  const dlg = document.getElementById('afr-dplace-dialog');
  dlg.style.width = isDplace ? '90vw' : '640px';
  dlg.style.maxWidth = isDplace ? '90vw' : '92vw';   // narrower + not full-bleed -- signature is tall, not wide
}

function afrOpenDplaceModal(sid) {   // unchanged behaviour, now routed through _afrModalMode
  const url = `https://d-place.org/society/${encodeURIComponent(sid)}`;
  document.getElementById('afr-dplace-frame').src = url;
  document.getElementById('afr-dplace-ext').href = url;
  document.getElementById('afr-dplace-title').firstChild.textContent = 'D-PLACE society ';
  _afrModalMode('dplace');
  bootstrap.Modal.getOrCreateInstance(document.getElementById('afr-dplace-modal')).show();
}

// Client-side cache: fetched once per src_id per page load, since the underlying data
// (BasinATLAS/LMR/HYDE/eVolv2k for a fixed 1600-1650 window) doesn't change mid-session.
const _afrSigCache = {};   // {src_id: payload}
let _afrSigSeq = 0;        // stale-fetch guard, same pattern as _afrPaintSeq

async function afrOpenProfileModal() {
  if (!_afrSelected) return;   // link is hidden whenever this would be true; belt-and-suspenders
  const srcId = _afrSelected;
  const body = document.getElementById('afr-profile-body');
  document.getElementById('afr-dplace-title').firstChild.textContent = 'Areal signature ';
  _afrModalMode('profile');
  bootstrap.Modal.getOrCreateInstance(document.getElementById('afr-dplace-modal')).show();

  if (_afrSigCache[srcId]) { body.innerHTML = _afrRenderSigHtml(_afrSigCache[srcId]); return; }

  const seq = ++_afrSigSeq;
  body.innerHTML = '<p class="text-secondary mb-0">Computing areal signature — this can take several seconds for a large region…</p>';
  try {
    const r = await fetch(`/api/lovejoy-signature?src_id=${encodeURIComponent(srcId)}`);
    if (!r.ok) throw new Error((await r.json()).detail || `HTTP ${r.status}`);
    const payload = await r.json();
    if (seq !== _afrSigSeq) return;   // modal reopened for a different region meanwhile
    _afrSigCache[srcId] = payload;
    body.innerHTML = _afrRenderSigHtml(payload);
  } catch (e) {
    if (seq !== _afrSigSeq) return;
    body.innerHTML = `<p class="text-danger mb-0">${_afrEsc(e.message)}</p>`;
  }
}
```

`hidden.bs.modal` handler (existing, ~L1953) already blanks the iframe `src` unconditionally —
harmless to leave as-is; it's a no-op when the profile pane was the one showing. It does **not**
need to touch `_afrSigCache` — a fetched region's data is valid for the rest of the session.

**Wire the link** in the DOMContentLoaded init block, beside the rationale-toggle listener
(~L1938):

```js
const afrProfileLink = document.getElementById('afr-profile-link');
if (afrProfileLink) afrProfileLink.addEventListener('click', e => { e.preventDefault(); afrOpenProfileModal(); });
```

### Commit 3 — ported renderer, namespaced to avoid the existing `renderSignature` collision

`workbench.html` already defines its own `renderSignature(sig)` / `humanizeKey(k)` / `escapeHtml(s)`
for the shared `#map` panel's single-basin signature (`/api/signature`'s `profile_summary`/
`profile_groups` envelope — a different shape entirely from what `areal_signature_polygon`
returns). **Do not overwrite these** — port the Sandbox Polities renderer under a fresh `_afrSig`
prefix instead of reusing the bare names:

- Port verbatim (one-line provenance comment, no shared file this WO — same call WO03 made for
  its ramp helpers): `renderHistogram` → `_afrSigHistogram`, `renderRangeBar` →
  `_afrSigRangeBar`, `renderMixtureBar` → `_afrSigMixtureBar`, `renderPercentileTrack` →
  `_afrSigPercentileTrack`, `renderSingleBasinContinuousLeaf` → `_afrSigSingleLeaf`, `renderLeaf`
  → `_afrSigLeaf`, `renderRow` → `_afrSigRow`, `fmtNum` (workbench has no equivalent — port as-is
  under `_afrFmtNum` or reuse if one already exists; check first), `BAND_ORDER`/`BAND_LABELS` →
  `_AFR_SIG_BAND_ORDER`/`_AFR_SIG_BAND_LABELS`. Reuse workbench's existing `escapeHtml` — it's a
  strict superset (adds quote-escaping) of sandbox's, safe as a drop-in.
- **`_afrRenderSigHtml(payload)`** — the entry point `afrOpenProfileModal()` calls. Trimmed from
  Sandbox's `renderSignature(payload)`: same accordion-per-band structure and `defaultOpenBand`
  logic (T if present, else C), but the heading branch collapses to one case — there's no ring/
  basin/polity-name disambiguation here, just the region name + macro (pass those in as args:
  `_afrRenderSigHtml(payload, name, macro)`) plus `${n_units} L6 basins` from `payload.scope`, and
  no "How to read this" doc-modal link (that doc page is written for the Sandbox Polities flow,
  not this one — leave it out rather than mis-point it; a WO05 follow-up can add a Workbench-side
  explainer if wanted).
- **Band T — keep the slider (reversed 2026-09-04).** The original scope note called this "a
  fixed 50-year window, no scrub" and the first pass of this spec read that as "drop the slider."
  Karl asked why, directly — and there isn't a technical reason. `aggregate_band_t` returns one
  row **per year** across whatever `from_year`–`to_year` span it's given; a "fixed window" only
  fixes *which* 50 years come back, not how many rows — the route in Commit 1 already fetches all
  ~50 annual LMR rows per variable, same shape a Sandbox polity query returns for its span. The
  "no scrub" framing was about *intent* (a region-character summary vs. an interactive research
  tool), not a data constraint, and porting `renderTBand`/`wireTSliders` **as-is** is strictly
  less work than trimming them — no new no-slider variant to build or maintain. **Port
  `renderTBand` → `_afrSigTBand` and `wireTSliders` → `_afrSigWireTSliders` verbatim**, call the
  latter after `_afrRenderSigHtml` injects the HTML (same as Sandbox does after `renderSignature`).
  HYDE and eVolv2k table rendering ports unchanged — those were already static in Sandbox too. If
  scrubbing through 1600–1650 turns out to be a distracting fidget during the actual talk rather
  than a nice demo beat, that's a one-line call to make later (hide the `<input>`, keep the static
  midpoint) — not worth deciding speculatively now.
- **Caveats block.** `payload.caveats` (if non-empty) — Sandbox doesn't currently surface this
  array in `renderSignature`'s own output (check at build time whether it renders elsewhere in
  `sandbox.html`, e.g. inline per-row via `row.caveat`, vs. an unrendered top-level list); if
  `payload.caveats` carries anything WO05-relevant (e.g. the marginal-exposure diagnostic), give
  it one small line under the heading. Don't invent caveat copy — pass through what the engine
  emits.
- **Static-A–E "as of" stamp** (the shelved item from the scope section, above) — while porting
  `_afrSigRow`, drop the per-row `resolverYear`/`asOf` line for A–E rows (`resolver_year` is
  `None` here — `areal_signature_polygon` was called with `resolver_year=None` in Commit 1 — so
  it would render nothing anyway; leave the dead branch out rather than port unreachable code).
  Band T rows keep their own `band_t_from`/`band_t_to` stamp in `_afrSigHistogram` unchanged —
  that one does apply.

### Coherence-badge re-check (do this before finishing Commit 3, not after)

The IQR fix (`59bfcea`) is merged, but WO05's own scope section flagged that the planned
"suppress the badge at region scale" decision needs re-checking against **real Lovejoy-region
IQR output**, not assumed either way. There's no persisted JSON to query now (Commit 1 is a live
route, not a precompute) — do this as a one-off, throwaway loop calling
`areal_signature_polygon` directly for all 34 regions (same geometry-read pattern as Commit 1's
`_lovejoy_geoms()`, just a standalone script under `scripts/edop/workbench/` or even a REPL
session — not committed unless it's genuinely reusable) before finishing Commit 3:

- Pull `coherence` + `detail.iqr` across all 34 regions × their A–E rows and show Karl the
  concentrated/spread mix at region scale now that IQR drives it, the same way the `59bfcea`
  commit message reported Songhai/Goguryeo/Kongo before/after.
- **If it now reads as a reasonable mix** (not near-universally `spread`, per-variable-type
  variation similar to what the IQR fix showed for polities): render the badge as-is via
  `_afrSigLeaf`, no suppression.
- **If it still collapses to `spread` almost everywhere** at Lovejoy-region scale: keep the
  scope-section's fallback — suppress the badge in `_afrSigLeaf`'s `area_weighted`/
  `distribution_only` branches (lead with histogram + `p10`/`p90` + weighted mean percentile,
  same as those branches render today minus the badge span) and note it as a still-open,
  separately-tracked engine item (size-aware `T`, or a different scale-appropriate threshold) —
  not a WO05 blocker either way.
- Whichever way it goes, record the actual numbers Karl was shown in this file's close-out, not
  just the decision — the WO03/WO04 close-outs both did this and it's what makes the badge fix's
  effect traceable later.

### Deploy

No new static asset — Commit 1 is a route (app code), Commit 2/3 are template changes. Nothing
to add to `MAINTAIN_DEPLOY.md`'s rsync list; ships with the normal branch-merge + redeploy like
any other route/template change.

### Out of scope (later WOs)

- A Workbench-side "how to read this" explainer for the modal (Sandbox's doc-modal link is
  Polities-flow-specific, left out per Commit 3 above).
- A server-side cache for `/api/lovejoy-signature` (the client-side `_afrSigCache` covers the
  session; a server cache would need an invalidation story this feature doesn't need yet).
- Re-tuning the coherence threshold itself (as opposed to the suppress/don't-suppress call above)
  — separate engine task if the re-check says it's still needed.
- Hiding the Band T slider in favor of a static midpoint, if it proves distracting live — a
  one-line follow-up, not scoped now (see the reversed decision above).

### Acceptance

- `GET /api/lovejoy-signature?src_id=<id>` returns the `areal_signature_polygon` payload (L6, all
  bands, `from_year=1600, to_year=1650, include_detail=True`) plus a `resolver` block; unknown
  `src_id` → 404; engine errors → 500. No new static asset, no DB hit against `whg_staging`.
- `#afr-rationale-row` shows the rationale toggle **and** a flush-right "Signature ↗" link
  whenever a region is in scope (region click or society click with a containing region); both
  hidden together on empty-space deselect.
- Clicking "Signature ↗" opens `#afr-dplace-modal` in profile mode (narrower dialog, title reads
  "Areal signature", D-PLACE-only chrome hidden) with a loading message, then fetches
  `/api/lovejoy-signature` for the selected region and renders band accordions (T open by
  default, slider live) with `_afrSigLeaf` percentile/coherence/histogram output per row.
  Re-opening the same region's modal within the session renders instantly from
  `_afrSigCache` — no repeat fetch.
- Clicking a D-PLACE society's `<id> record` link still opens the same modal in D-PLACE mode,
  unchanged from WO04 — the two modes don't interfere with each other's state on repeat opens.
- Coherence-badge re-check done and recorded (numbers shown to Karl, suppress/don't-suppress
  decision made and applied in `_afrSigLeaf`).
- No console errors; other Workbench tabs and Sandbox unaffected (no shared function names
  collide); `pytest tests/` green.

### Still open (build-time calls)

- Modal-sharing mechanics as spec'd above (shared shell + mode toggle) vs. a second modal if that
  turns out cleaner in practice — CC's call during the build, not a blocker to starting.
- Real per-region latency, especially for the largest regions (Sahara-scale polygons) — eyeball
  during the build; a server-side cache is the fallback if it's genuinely too slow for the talk,
  but not built preemptively.
- Exact wording/placement of the coherence-suppression fallback copy, if that branch is taken.
- Whether the Band T slider stays interactive through the actual Braga talk or gets pinned to the
  midpoint for a calmer demo — decide after seeing it live, not now.
