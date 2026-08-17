# CLAUDE.md — EDOPS

Read this at the start of every session. It describes current project state, not history.
Session-by-session detail lives in `logs/session_log_YYYYMMDD.md`.

**Session startup:** read this file for orientation, then the tracker for the active phase.
- `CLAUDE.md` (this file) — phase overview, architecture, conventions, pointers
- **v0.4 docs** — active phase, no tracker yet; goto `logs/session_log_YYYYMMDD.md` for latest state
- `docs/cdop/citykin/CITYKIN_tracker.md` — frozen reference (CDOP2/CITYKIN closed 2026-07-30)
- `docs/cdop/pilot/CDOP_PILOT_tracker.md` — frozen reference (CDOP Pilot closed 2026-07-27)
- `docs/edop/demo/DEMO_tracker.md` — frozen reference (DEMO closed 2026-07-18)
- `docs/design/deferred_items_register.md` — cross-phase parked items
- `logs/session_log_YYYYMMDD.md` — daily detail; `docs/cdop/citykin/wo{nn}_findings.md` — per-WO findings

**Logging convention (all phases).** The detailed, technical record of a work order lives in its
`wo{nn}_findings.md`. Trackers and session logs carry **top-level summary + a pointer to the findings
file**, not a re-derivation of it. When closing a WO: update the phase tracker's roadmap row, add/replace
a short WO subsection, reset the one-line "Last updated" stamp, and fold any settled forward-looking note
into the tracker's *Locked decisions* / *Deferred* **in the same edit** — never leave a resolved question
live elsewhere. Keep each tracker's "You are here" to the current WO only. (Older tracker sections that
predate this convention are grandfathered; new WOs get summary + `findings:` link.)

---

## What this project is

**EDOPS** (Environmental Dimensions of Place Service) is a FastAPI service that delivers
structured environmental "signatures" for any location on Earth. Signatures characterize a
drainage basin — or a set of basins, for areal queries like a basin ring, buffer neighborhood,
or historical polity — using BasinATLAS variables covering hydrology, climate baselines,
terrain, and ecoregion, plus temporal enrichment layers: LMR v2.1 paleoclimate, HYDE 3.4
land-use history, and eVolv2k v4 volcanic forcing.

EDOPS is the active component of **Computing Place** (CEDOP), a spatial humanities research
platform. The companion CDOP (Cultural Dimensions of Place) component is deferred; its
earlier exploratory scripts are archived in the `cedop`.

Research framing: `documentation/EDOP_summary_v04.md`

---

## Research phases

| Phase | Status | Key product |
|---|---|---|
| 1 — Signature development | complete | `/api/signature`, `sandbox.html`, variable catalog v0.3 |
| 2 — Characterization / CHAR | complete | `explorer.html`, EDA/ESDA findings |
| 3 — Areas | complete 2026-06-30 | `engine.py` — resolver → aggregator → payload; `AREAS_tracker.md` (frozen ref) |
| Surface | complete 2026-07-10 | `sandbox_v3.html` at `/sandbox/lookup3`; see `SURFACE_tracker.md` (frozen ref) |
| Demo | complete 2026-07-18 | `sandbox_v3.html` polish; similarity instrument; see `DEMO_tracker.md` (frozen ref) |
| CDOP1 — pilot | complete 2026-07-27 | `cdop_pilot.html`; L08 lens index; WO1–WO8d environment↔culture arc; frozen ref, see `CDOP_PILOT_tracker.md` |
| CDOP2 — CITYKIN | complete 2026-07-30 | WH Cities retrieval head (3 lenses: precip/temp/terrain regime), a 4th sandbox Similarity-panel lens (basin-scale Terrain regime), and the Societies-tab PCA-cluster replacement (meter-bar + donut environment display, WO4); frozen ref, see `CITYKIN_tracker.md` |
| Reorg (housekeeping) | complete 2026-08-03 | CDOP merged to `main` for the first time (local only, not deployed); new canonical routes (`/sandbox`, `/explorer`, `/cdop_tests`); unified EDOPS header; `sandbox.html` retired |
| **v0.4 docs** | **active** | Site documentation/legibility pass ahead of v0.4 replacing v0.3 in production; no tracker yet |
| 4 — Correspondence testing | not started | D-PLACE / Seshat / Cliopatria |

---

## Current work

**v0.4 docs is the active track.** v0.4 (CDOP2/CITYKIN's product work plus the 2026-08-03 reorg) is
feature-complete. What remains before it replaces v0.3 in production is a documentation/legibility
pass — the site is about to get wider visibility as a public-facing WIP. No tracker exists yet for
this phase; goto the latest `logs/session_log_YYYYMMDD.md` until one is set up. **Milestone: Braga
(2026-09-20) — UNED Digital Humanities conference.**

**Branching, current shape:** `cdop` and `edop` are the two component trunks off `main`; real coding
work is cut as phase-trunk branches off one of those (`cdop_citykin` was the last one, now closed),
with WO-child branches under each, merged back to the trunk on accept. Cross-cutting housekeeping that
isn't component-specific coding — like the 2026-08-03 site/routing reorg — is instead cut directly off
`main` (the `reorg` branch) and merged straight back to `main`, bypassing `cdop`/`edop` entirely.
**v0.4 docs follows the same shape as the component trunks, off `main`:** `docsv4` is the phase-trunk
branch; WO-scale work is cut as child branches off `docsv4` and merged straight back into it on accept
(`basinring` — the basin-ring rebuild below — was the first, merged 2026-08-06). `docsv4` itself stays
un-merged into `main` until the whole docs pass is ready to replace v0.3 in production.

**State as of 2026-08-16 (branch `varnaming_routes`, cut off `docsv4`, not yet merged back —
nothing deployed):** MkDocs is live in-repo (`docsite/` source, `mkdocs.yml`, `site/` build output
gitignored) with a generated Codebook (`scripts/edop/docsite/generate_codebook.py`, TSV →
compact markdown) and a full "About EDOPS" specificity ladder (in-app modal → `docsite/project.md`
→ `docsite/data-sources.md` → `documentation/EDOP_summary_v04.md`, each linking out rather than
duplicating). `main` has its first tag/release, `v0.3`, matching what's deployed. The Sandbox
template naming collision is resolved (`sandbox.html` is the live one, old Lookup is
`sandbox_v03.html`). **`app/api/routes.py` (formerly ~4000 lines) no longer exists** — split into
`routes_common.py`, `routes_cliopatria.py`, `routes_explorer.py`, `routes_workbench.py`, and
`routes_sandbox.py` (the renamed remainder), using `docs/edop/routes_audit.txt` as the map;
`main.py` and the two external module-path dependents (`tests/test_areas.py`,
`scripts/cdop/wo5_part_b_context_probe.py`) updated to match. Seven confirmed-dead/superseded API
routes removed across the two days (`/basin-clusters(+cities)`, `/similar-text`, `/wh-sites`,
`/whg-place`, `/similarity/climate-class`, `/temporal`); route count now 77. Two working-reference
docs exist in `docs/edop/` that later sessions should consult rather than re-derive:
`pageload_explorer.txt` (on-load + variable-selection pseudocode, more pages planned) and
`routes_audit.txt` (kept current through the split — re-run after any future route change). Two
real UI bugs surfaced and fixed via browser review during the split, unrelated to the routes work
itself: Cliopatria's basin-variable select didn't clear the map on reset (`clearBasinVar()`), and
Explorer's preview variables triggered a doomed LISA fetch that caused a visible repaint-then-revert
(LISA now disabled up front for preview variables, matching the existing categorical/monthly
guard). Full history: `logs/session_log_20260804.md` through `logs/session_log_20260816.md`.

**Same day, continued:** public API surface narrowed to `/health`, `/signature`, `/area`,
`/areas` (everything else marked `include_in_schema=False`); `docsite/api.md` is now generated
(`scripts/edop/docsite/generate_api_guide.py`, same pattern as the Codebook) from the live
route set + docstrings — retired the old hand-maintained `documentation/API_guide.md` and
`app/static/api_guide.html`; `documentation/edops_schema.json` regenerated against live output
(real Band T shape drift found); Codebook rows now link to their own
`BasinATLAS_Catalog_v10.pdf` page (`scripts/edop/docsite/split_basinatlas_catalog.py`), which
surfaced and fixed 14 scrambled `atlas_id` values in the variable catalog TSV. `app/static/
basinatlas_pages/` (gitignored, split-PDF output) still needs adding to the rsync deploy step.
Full detail: `logs/session_log_20260816.md` Part 2.


**Engine** (`scripts/edop/areas/engine.py`) — stable; four public entry points:
- `areal_signature(lat, lon, radius_km, conn, ...)` — buffer
- `areal_signature_polygon(geom_wkt, conn, ...)` — polygon/polity; served on `GET /api/area`
- `single_basin_signature(lat, lon, conn, ...)` — HTTP-wired via `type=single_basin`
- `basin_ring_signature(lat, lon, conn, ...)` — HTTP-wired via `type=basin_ring`

Two independent temporal axes: `resolver_year` (polity boundary) and Band T span (`from_year`/`to_year`).

**`db_utils.read_areas_tsv(path, **kwargs)`** — always use instead of bare `pd.read_csv` for any
TSV with `hybas_id` or `dominant_hybas_id`; forces Int64.

---

## Architecture

```
app/
├── main.py              # FastAPI app
├── api/routes_{sandbox,common,cliopatria,explorer,workbench}.py  # All REST endpoints,
│   #   split by page 2026-08-16 (routes.py no longer exists) — common.py holds routes/helpers
│   #   shared across ≥2 pages; see docs/edop/routes_audit.txt for the classification
├── db/
│   ├── connection.py    # db_connect()
│   └── signature.py     # Core signature query; loads codebook at startup
├── web/pages.py         # Jinja2 page routes
├── templates/
│   ├── sandbox.html     # Sandbox page — Demo phase product; current focus (renamed from
│   │                     #   sandbox_v3.html 2026-08-15; old retired Lookup page is
│   │                     #   sandbox_v03.html, unreferenced by any route)
│   ├── explorer.html    # Explorer page — Phase 2 product
│   ├── workbench.html   # Workbench page — standalone doc like the other two (2026-08-07;
│   │                     #   formerly base.html-extending, base.html deleted, nothing else used it)
│   ├── cliopatria.html  # Cliopatria polity viewer — eyes-only for ISHI; Phase 4 precursor
│   └── ...
└── static/
    ├── css/site.css      # cross-page shared rules (nav pills, tiles, help-tooltip harness)
    ├── css/{explorer,sandbox,workbench}.css  # page-scoped (2026-08-07 CSS reorg; ex-inline <style> blocks)
    ├── js/edops_help.js  # shared help-tooltip harness (2026-08-07) — see State as of, above
    ├── explorer/        # PMTiles, GeoJSON, HYDE tiles (gitignored — rsync only)
    └── ...

mkdocs_hooks.py           # MkDocs post-build hook (2026-08-07) — overrides Material's hardcoded
                          #   sidebar-dock breakpoint via regex on the compiled CSS; see State as of
mkdocs.yml               # MkDocs config — docs_dir: docsite/, site_dir: site/ (v0.4 docs, 2026-08-05)
docsite/                 # MkDocs source (tracked) — one page per DOCSv4 TODO §5 section, nav in
                          #   per-surface subtrees (Sandbox/Data Explorer/Workbench); similarity.md
                          #   is a new top-level page (2026-08-08); javascripts/{embed,external-links}.js
                          #   codebook.md is generated (scripts/edop/docsite/generate_codebook.py
                          #   from the variable catalog TSV) — do not hand-edit it, edit the script
site/                    # `mkdocs build` output (gitignored) — served at /docs via a StaticFiles
                          #   mount in main.py. `mkdocs serve` (live preview) and this are two
                          #   separate things reading from different places — see Key endpoints.
documentation/           # Public-facing docs (tracked)
docs/                    # Design docs and WIP — gitignored with exceptions:
docs/edop/areas/         #   Areas tracker (frozen ref) + findings (tracked)
docs/edop/engine/        #   Work-order specs (tracked)
docs/edop/surface/       #   Surface tracker + findings (tracked; frozen ref)
docs/edop/demo/          #   Demo tracker + findings (tracked) ← active
docs/design/             #   deferred_items_register.md, scenarios.md (gitignored)
docs/design/demo/        #   sandbox_v3 line specs + demo design notes (gitignored)
docs/edop/pageload_explorer.txt  # per-page pseudocode reference (gitignored) — Explorer done,
                          #   Sandbox/Workbench to follow; consult before re-deriving page behavior
docs/edop/routes_audit.txt       # every app/api/routes.py route classified live/shared/orphaned
                          #   (gitignored) — re-run the audit after any route add/remove/rename
scripts/edop/            # Data pipelines, ESDA, Explorer asset generation
scripts/edop/areas/      # Areas engine — engine.py is the primary artifact
notebooks/edop/explore/  # CHAR phase EDA notebooks
notebooks/edop/spatial/  # CHAR phase ESDA notebooks
notebooks/edop/areas/    # Areas phase notebooks (research record; frozen)
notebooks/edop/surface/  # Surface phase notebooks (frozen)
notebooks/edop/demo/     # Demo phase notebooks ← active
output/edop/areas/       # Areas output (gitignored)
output/edop/surface/     # Surface output (gitignored)
output/edop/demo/        # Demo output (gitignored)
logs/                    # session_log_YYYYMMDD.md, exploration_log.md, esda_findings.md
logs/2026_jan-may/       # Archived earlier session logs
metadata/                # gitignored
```

---

## The sandbox pages

**Routing note (local `main`/`docsv4`, not yet deployed — see Current work above):** as of the
2026-08-03 reorg, `/sandbox` is the new canonical route for `sandbox.html` (old
`/sandbox/lookup3` still works too); `/explorer` is the new canonical route for `explorer.html`
(old `/sandbox/explorer` still works too); `/sandbox/lookup` now 301-redirects to `/sandbox`, and
the old Phase 1 Lookup page (renamed `sandbox_v03.html` on 2026-08-15, described below) is fully
retired — no route renders it on `main`. `/workbench` is the third canonical route
(`workbench.html`, formerly `cdop_pilot.html` — renamed 2026-08-05, see Open/deferred items below);
`/cdop` and `/cdop_tests`, which used to serve it, were dropped outright rather than redirected,
since nothing's deployed yet. **In production today none of this has happened:** `/sandbox/lookup`
still serves the old Lookup page live (under its old production filename, `sandbox.html` — the
rename only exists on `docsv4`), and the old `cdop_pilot.html`/`/cdop`/`/cdop_tests` naming is
still what's actually deployed, until this branch ships.

### `/sandbox` (canonical) / `/sandbox/lookup3` — Demo surface (active)
`app/templates/sandbox.html` — Demo phase product; current focus. (Renamed from
`sandbox_v3.html` on 2026-08-15 — the `_v3` distinction stopped meaning anything once the old
Phase 1 page was renamed out of the way; see the Lookup entry below.)

Two-tab surface: **Settlements** (WHG place lookup → scope → BasinATLAS/LMR/HYDE choropleth + signature)
and **Polities** (search → slice slider + VCR → choropleth + signature).

- AWMC historical terrain basemap; HydroRIVERS PMTiles base layer (`app/static/sandbox/`; gitignored)
- Layer control (top-right over map); rivers toggleable
- L06/L08 level toggle; basin fill transparent (choropleth shows through)
- White-cased charcoal basin outlines; polity slice year overlay (top-left map corner)
- 4 placed settlement examples (Timbuktu, Rome, Kaifeng, Santa Fe) + 6 polity examples
- Line spec reference: `docs/design/demo/sandbox_v3_line_specs.md`

### `/sandbox/lookup` — Lookup (retired on `main`, still live in production)
`app/templates/sandbox_v03.html` (renamed from `sandbox.html` on 2026-08-15) — Phase 1 product; was
the primary researcher tool, superseded by `sandbox.html` (formerly `sandbox_v3.html`). File remains
in the repo, unreferenced by any route once deployed.

WHG place lookup → basin assignment → neighborhood map → Band A–T signature.
- Level 08/06 toggle; s/u/Δ toggle; Band T temporal charts (PDSI/Temp/Precip + eVolv2k)
- Analysis α tab: water provenance, s/u divergence, scale mismatch alert
- Ecoregion → Wikipedia modal; LLM narrative button
- Examples: Timbuktu 1100–1200, Rome 0–300, Kaifeng 1000–1100

Key design doc: `docs/design/scenarios.md` — historical reference for this retired page.

### `/explorer` (canonical) / `/sandbox/explorer` — Explorer
`app/templates/explorer.html` — Phase 2 product; visual CHAR exhibit.

MapLibre GL JS choropleth. L6/L8 Level toggle wired 2026-08-07 (`basin06.pmtiles`, 16,397 basins /
`basin08.pmtiles`, 190,675 basins — both registered on the Global map and all 6 Regions sub-maps);
previously a dead control, values API already supported `level=8` but paint was hardcoded to L6.
Three tabs:

**Global** — world choropleth; Bands A–T accordion; histogram; LISA;
Band T (LMR 5-period / HYDE 4-var 3-view / eVolv2k timeline).

**Regions** — 6-panel synchronized choropleth: East Asia, South Asia, Southwest Asia,
Mediterranean & N. Africa, Mesoamerica, Pacific Northwest. Band T fully supported
(LMR with country overlay, HYDE raster). Controls strip persists across tabs.

**Compare** — provisionally complete.

### Explorer architecture decisions (do not revisit)
- **PMTiles + flat values API**: geometry served once per level from `basin06.pmtiles`/`basin08.pmtiles`;
  `/api/explorer/values` returns `{hybas_id: value}` dict only (~0.3 MB L6 / ~3 MB L8, no geometry).
  Sub-second variable loads. Do not suggest GeoJSON caching — explicitly rejected.
- **Color scheme**: warm/dry = red, cold/wet = blue throughout. Temperature diverging
  uses `1 - t`; aridity + precipitation RDBU sequential (low = red); LMR PDSI/precip
  use `t`; LMR temperature anomaly uses `1 - t`.
- **Gitignored static assets** (must rsync to server, never git):
  `basin06.pmtiles`, `basin08.pmtiles`, `lmr_notches.geojson`, `countries_110m.geojson`,
  `hyde_tiles/`, `lisa_classifications.parquet`

### `/workbench` (canonical) — Workbench
`app/templates/workbench.html` — formerly `cdop_pilot.html` (CDOP Pilot/CITYKIN product; renamed
2026-08-05, see Open/deferred items below). Third full peer of Sandbox/Explorer in the app's
header nav; EDOP↔CDOP environment/culture correspondence testing. A map and environmental-profile
panel stay visible on the right across all three tabs; results are necessary-not-sufficient
evidence, not causal claims. Three tabs:

**Societies** — 1,291 D-PLACE societies. Two queries, deliberately asymmetric: **Dominant
subsistence (EA042)** offers a confirmatory **Climate envelope** scatter (has a named theoretical
hook, default view as of 2026-08-10) or *Ecoregions by realm*; **High gods (EA034)** offers an
exploratory **Environment scan** (no hook to confirm against; default view as of 2026-08-10) or
*Ecoregions by realm*. Environment scan is per-society **strip plots** as of 2026-08-10 (WO4
EA045) — one tick per society at its own percentile position, not the earlier mean-position meter
bars. Composition donut (Glottolog-resolved family names), hover-linked to map, scatter, and the
strip plots.

**Experimental, unmerged (`isolates` branch off `docsv4` as of 2026-08-10, not yet reviewed):** a
third EA034 result type, **Isolates** — named societies with no close ancestral/geographic/
environmental neighbor sharing the same trait value, ranked three ways (plus an opt-in
worst-of-three) rather than characterized in aggregate. See `logs/session_log_20260810.md` for
the full design discussion and Karl's evaluation is still pending — do not describe this as live
on `docsv4` until it's merged.

**Ecoregions** — OneEarth Bioregions drill-down (14 realms → 53 subrealms → 185 bioregions → 847
ecoregions), Wikipedia summary + OneEarth link per ecoregion. Mostly a reference browser feeding
the Societies tab's "Ecoregions by realm" view, not a correspondence test of its own — whether it
belongs on this page at all is still an open question (Karl's own note, `docs/_TODO.md`).

**WH Cities** — 258 World Heritage Cities (OVPM), 254 basin-assigned. Two dropdowns, three actually
different mechanisms (not one shared method — see `docsite/similarity.md`): **Similar (env)** —
Precipitation/Temperature "regime" (older composite-distance, not conjunction like Sandbox) and
Terrain regime (gate+rank hybrid, live external elevation-grid fetch); **Similar (semantic)** —
Wikipedia-discourse text similarity by band (Composite/Environment/History/Culture/Modern).

Full mechanics for all three tabs (verified against the live templates, not just described):
`docsite/workbench/overview.md`.

---

## Key endpoints

```
NOTE: see docsite/api.md (master, public; generated by
scripts/edop/docsite/generate_api_guide.py from live route signatures + docstrings —
edit those, not the .md directly; served at /docs/api/)

/api/schema
    FastAPI's interactive Swagger UI — moved here from /docs 2026-08-04 to free that route for
    MkDocs. If you're looking for the old Swagger URL, this is it now.

/docs
    MkDocs site (v0.4 docs). Served by a StaticFiles mount over site/ (main.py), NOT by
    `mkdocs serve`. Those are two different things reading from two different places —
    `mkdocs build` updates what this route serves; `mkdocs serve` (live preview, different port)
    never writes to site/ at all. Edited docsite/ content needs `mkdocs build` before it shows up
    here or in the app's Documentation modal (which iframes this route's built pages).

/api/signature?lat=X&lon=Y[&bands=ABCDET&from_year=N&to_year=N&level=6|8]
    Returns profile_groups A–T. Band T requires from_year+to_year.
    Source ranges: LMR 1–2000 CE · HYDE 10,000 BCE–2023 CE · eVolv2k 500 BCE–1900 CE.
    API currently accepts 0–1998 CE; BCE queries and full HYDE range are not yet handled.
    Temperature fields (tmp_dc_*) stored ×10 in DB — signature.py divides by 10.

/api/basin-preview?lat=X&lon=Y[&level=6|8]
    Containing basin + neighbors + river lines for neighborhood map.

/api/whg-reconcile?q=X[&size=N&bounds=GeoJSON]
    WHG reconcile+extend; requires viewport bounds (zoom ≥ 4).

/api/explorer/values?var=X&level=6&su=s
    Flat {hybas_id: value} dict for Explorer choropleth.

/api/explorer/categorical?var=X&level=6
    Flat {hybas_id: cat_id} dict + category list.

/api/explorer/regions
    Six region bounding boxes for Regions tab.

/api/explorer/scatter?x=VAR&y=VAR&level=6
    Paired values for bivariate scatter: {x_meta, y_meta, n_paired, values: [[id,x,y],…]}

/api/area?polity=<name>&year=<int>[&level=6|8][&bands=ABCDET][&from_year=N&to_year=N][&detail=true]
    Areal signature for a Cliopatria polity. Two independent temporal axes: year moves the
    polity boundary; from_year/to_year moves the Band T aggregation window. detail=true adds
    histogram objects (detail['distribution']) across basin/HYDE/LMR substrates.

/api/polity/search, /api/polity/slices, /api/polity/period, /api/polity/geom
    Cliopatria polity queries — used by cliopatria.html.
```

---

## Database

- **Host**: local dev on `.env` (PGPORT 5432); production PostgreSQL 17/PostGIS on server
- Three active schemas: public, gaz, and temporal
- `public.basin06`: 16,397 L6 sub-basins — **verbatim BasinATLAS extraction**: `hybas_id`, `geom`, raw monthly scalars (`pre_mm_s01`–`pre_mm_s12`, `tmp_dc_s01`–`tmp_dc_s12`), annual summaries, and all other BasinATLAS fields. **Derived variables (`pre_concentration`, `seas_phase_offset`, `pre_peak_month`, etc.) are NOT stored here** — they are computed on-the-fly by `seasonality.py:_compute_derived()` from monthly arrays.
- `public.basin08`: 190,675 L8 sub-basins — same verbatim BasinATLAS structure as `basin06`
- `public.v_basin06_persist_rev2`, `public.v_basin08_persist_rev2`: views used by the similarity index at startup; expose `hybas_id`, `pre_mm_monthly` (array), `tmp_dc_monthly` (array, already °C — not ×10). All derived similarity variables are computed from these arrays at index-load time.
- `gaz.clio_polities`: Cliopatria polities — columns lowercase (`fromyear`, `toyear`, `name`, `geom`)
- `gaz.rivers`: HydroRIVERS v1.0 global river network — 8.5M rows; `hyriv_id`, `geom` (MultiLineString), `ord_clas` (Strahler order class 1–9); tiled to `app/static/sandbox/rivers.pmtiles` (gitignored)
- `temporal.hyde_cells`: 2,215,829 HYDE 3.4 grid cells (~5 arc-min); PostGIS polygon `geom`, `area_km2`, and four variable columns (`cropland`, `grazing`, `pasture`, `rangeland`) each stored as `real[]` arrays indexed by `step_idx`
- `temporal.hyde_times`: 128 rows mapping `step_idx` → `year_ce` (−10000 to 2025); join to get year-specific HYDE values
- `temporal.lmr_climate`: 16,380 LMR v2.1 grid points at 2°×2°; PostGIS point `geom`; `pdsi`, `air`, `prate` stored as `real[]` arrays of length 2001 (1–2001 CE, 0-indexed)
- `temporal.evolv2k_v4`: eVolv2k v4 volcanic forcing rows by `year_ad`; columns `vssi_tg`, `so4_grl`, `so4_ant`, `lat`, `location`
- Temperature fields (`tmp_dc_*`): stored as °C × 10 — always divide by 10 for display
- PostGIS geometries: pass as WKT via `ST_GeomFromText()`, not EWKB hex (psycopg3 endian issue)
- BasinATLAS NoData sentinel: `−9999` — mask before any analysis

### How runtime data reaches the app (source map)

| Source | Serves | Read by |
|---|---|---|
| **Base tables** `basin06`/`basin08` (direct SQL) | raw stored BasinATLAS columns + `geom` + point resolution | `routes.py` only — Explorer choropleths (`/explorer/values`, `/explorer/categorical`), `_resolve_basin`, basin-preview |
| **Persist views** `v_basin0{6,8}_persist_rev2` | monthly **arrays** `pre_mm_monthly`/`tmp_dc_monthly` (°C, not ×10) — the **only** path to the twelve-month curves; base tables have only the 12 separate `×10` scalar columns | `signature.py`, `seasonality.py`, `context.py`, `climate_classes.py` |
| **In-memory indices** built at startup (`main.py` lifespan) from the persist views | similarity + conjunction + context instruments; numpy per request | `seasonality.py`, `context.py` |
| **Parquet** (read once → cached in a module global) | large precomputed analysis **cubes** only | LISA (`output/edop/esda/lisa_classifications.parquet`, 107 MB) via `routes.py` |
| **PMTiles** (static, client-rendered) | geometry | templates (`basin06/08.pmtiles`, `rivers.pmtiles`) |

**Rule of thumb:** anything needing the monthly curves or a derived field goes through the **persist views** (never the base tables). Base tables give raw columns + geometry. Parquet is reserved for large cubes (LISA); small per-basin derived results belong in an **in-memory startup index** (the similarity/context family) or a DB table, not a loose parquet.

---

## Deployment

- **Local dev server**: `uvicorn app.main:app --reload` (runs on http://localhost:8000)
- **URLs**: `edops.computingplace.org` — Hetzner CPX32 server (Nuremberg, 46.225.125.25)
- **Stack**: Nginx → Gunicorn (port 8001) → FastAPI; `edops.service` systemd unit
- **Virtualenv**: `/home/karlg/envs/cedop/`; **Working dir**: `/var/www/edops`
- **Deploy sequence**:
  ```
  git push origin main                  # push edops repo
  rsync <gitignored assets> server:...  # Explorer: PMTiles, parquet, tiles, hyde_epoch_maxes.json
                                        # Sandbox: app/static/sandbox/rivers.pmtiles (365 MB)
  ssh kgeographer-1
    cd /var/www/edops && git pull
    sudo systemctl restart edops        # requires password — manual step
  ```

---

## Notebook conventions

These are standing rules for every notebook. Consult before writing or editing any cell.

**Tooling**
- Edit notebooks with `NotebookEdit`, not the plain `Edit` tool.
- Karl runs notebooks cell by cell in PyCharm/Jupyter and reports back results. Never run notebook code via Bash to verify. Never assume a cell ran — wait for Karl to share output.

**Cell authoring**
- Every code cell must have `# Cell N` as its first line — no exceptions. Karl discusses cells by number.
- `%matplotlib inline` must be the first line of Cell 1; no rcParams or style overrides needed.
- Suppress SQLAlchemy pandas warnings at the top of any cell that makes DB calls:
  ```python
  import warnings; warnings.filterwarnings("ignore", message="pandas only supports SQLAlchemy")
  ```
  These proliferate with multiple DB calls and clutter output.

**Tabular output**
- Never output a bare DataFrame as the last expression in a cell — PyCharm renders it as an interactive table that cannot be cmd-c copied.
- Always use `print(df.to_string())` for any tabular output.

**DB and queries**
- **Connection**: `from scripts.shared.db_utils import db_connect` then `conn = db_connect()`. Default database is `cedop`.
- **Spatial queries**: `gpd.read_postgis(sql, conn, geom_col='geom').rename_geometry('geometry')` — always rename so column is `geometry` not `geom`.
- **World basemap**: `gpd.datasets` removed in geopandas 1.0; `geodatasets` not installed. Use pyogrio test fixtures: `import pyogrio; gpd.read_file(Path(pyogrio.__file__).parent / 'tests/fixtures/naturalearth_lowres/naturalearth_lowres.shp')`
- **Non-spatial queries**: `pd.read_sql(sql, conn)` — f-string SQL with values interpolated directly (no SQLAlchemy, no named params).
- **Inspect before hardcoding**: before writing city names, column names, enum values, or IDs into a cell, query the source table via `psql` to confirm exact values. Do not guess.
- `basin06` and `basin08` are verbatim BasinATLAS extractions. Derived seasonality variables (`pre_concentration`, `seas_phase_offset`, `pre_peak_month`, etc.) are NOT stored in those tables — they are computed on-the-fly by `seasonality.py:_compute_derived()` from monthly array columns. The persist views (`v_basin06_persist_rev2`, `v_basin08_persist_rev2`) expose `hybas_id`, `pre_mm_monthly`, `tmp_dc_monthly` for index-build use.

**Output path**
- Derive from module location, not relative path: `ROOT = Path(db_utils.__file__).parent.parent.parent; OUT = ROOT / 'output' / 'edop'`

**Map figure rendering**
- Do NOT rely on `plt.style.use('default')`, rcParams, or object-level helpers — PyCharm overrides them.
- Pattern: `fig.patch.set_facecolor('white')`, `ax.set_facecolor('white')`, `color='black'` on all text, `fig.savefig(..., facecolor='white')`, `plt.close(fig)`, then `display(IPImage(str(outpath)))`. This saves a PNG and displays it, bypassing PyCharm's inline renderer entirely.
- Always `print("drawing <name>...")` immediately before the `fig, axes = plt.subplots(...)` line. Figure output overwrites text output in PyCharm — an exception inside the figure-drawing block will be invisible if no text was printed before the figure rendered. The print anchors the text output above the figure.

**Extraction rule**
- Notebooks are a research record. Logic extracted to `engine.py` or other modules stays there; notebooks are never modified to call engine code. Extraction is one-directional.

---

## Testing

```bash
curl http://localhost:8000/api/health
curl "http://localhost:8000/api/signature?lat=16.76618535&lon=-3.00777252"  # Timbuktu
python -m pytest tests/                        # full suite (app + engine)
python -m pytest tests/engine/                 # engine contract tests only
python -m pytest tests/ --ignore=tests/engine/ # app tests only
```

**Zero-tolerance rule: no FAILs, no unexplained warnings, ever.**
- A failing test is either fixed immediately or deleted with an explanation of why it no longer applies.
- A warning is either resolved or explicitly suppressed with a comment explaining why it is safe to ignore.
- Never explain away a failure and move on — the longer a known failure rides, the harder it is to unravel.
- Engine tests go in `tests/engine/test_engine_contract.py`. They test contracts and invariants, never frozen notebook TSV values. When an algorithmic improvement changes output, update the contract (or confirm it still holds) in the same commit.

`tests/test_live_server.py` runs smoke tests against the production server — skipped unless
`EDOPS_LIVE_URL` is set. Run after each deployment:

```bash (run as ./smoke_test.sh)
EDOPS_LIVE_URL=https://edops.computingplace.org python -m pytest tests/test_live_server.py -v
```

---

## Key design documents
documentation/ folder holds current master versions of project docs (public on repo)
docs/ hold old drafts and works-in-progress (gitignored)

| Doc                                             | Purpose                                                                                                          |
|-------------------------------------------------|------------------------------------------------------------------------------------------------------------------|
| `documentation/EDOP_summary_20260608.pdf`       | Current project summary                                                                                          |
| `documentation/EDOPS_variable_catalog_v0.4.tsv` | Variable reference; loaded at startup by `signature.py` and `routes.py` — canonical copy, single source of truth. `EDOPS_variable_catalog_v0.3.tsv` is a frozen snapshot of what's actually deployed in production (recovered from the live server 2026-08-06); not read by any code. |
| `documentation/EDOPS_esda_findings.md`          | ESDA findings (BV.1–BVR.7, CAT.1–8, etc.)                                                                        |
| `documentation/EDOPS_eda_findings.md`           | EDA findings (F1.1–F11.6)                                                                                        |
| `docs/edop/prospectus_20260505.md`              | Initial research direction doc (superseded by project summary)                                                   |
| `docs/design/scenarios.md`                      | User profiles + scenarios — read before Lookup UI work                                                           |
| `docs/edop/edops_schema.json`                   | Signature schema with Timbuktu example values                                                                    |

---

## Open / deferred items

Demo-specific items → `DEMO_tracker.md` roadmap.
Cross-phase deferred items → `docs/design/deferred_items_register.md`.

Standing cross-phase notes:
- **Cliopatria viewer** (`/polities`) — live but eyes-only for ISHI; Phase 4 precursor
- **`/wh-sites` and `/similar` are now orphaned** (2026-08-05) — previously "not dead" because
  `workbench.html` called them, but that page has been archived to `xarchive/` (gitignored, not
  deleted) as part of the Workbench-name untangling below. Nothing live calls them now; worth a
  removal pass when convenient, not urgent.
- **The two-things-named-Workbench collision is resolved** (2026-08-05) — the old `workbench.html`
  (dev/test harness: Main lookup, Basins, Ecoregions, Societies, WH Cities, WH Sites tabs) is
  archived to `xarchive/workbench.html`. `cdop_pilot.html` was renamed to `workbench.html` and now
  owns the `/workbench` route and the `active_page = "workbench"` identifier; `/cdop` and
  `/cdop_tests` were dropped outright (v0.4 isn't deployed, no compat redirects needed). The
  nav pill now reads **Workbench** (settled 2026-08-05 — Karl's reasoning: the page keeps the
  Ecoregions drill-down, which isn't strictly a CDOP integration, so a generic name fits better
  than "EDOP <> CDOP"). The page `<h4>` title (`page_title`, currently `"EDOP <> CDOP workbench"`)
  wasn't part of this ask and is still open. The `workbench.computingplace.org` subdomain still
  needs an nginx-level redirect
  to `edops.computingplace.org/workbench` at deploy time — that's a manual step Karl runs on the
  server, not tracked in this repo.
- **`/whc-*` routes are not orphaned** — `/api/whc-similar-terrain` is live (CITYKIN WO1a). Resolved
  2026-08-08 (was previously an open question here): `/api/whc-similar-env-lens` was never replaced —
  it's still the live path behind WH Cities' precip/temp "regime" dropdown, and is a genuinely
  different, older mechanism (composite-distance `LENS_REGISTRY`) than Sandbox's conjunction-based
  regime lenses despite the shared naming. Full breakdown: `docsite/similarity.md`.
- **Deprecated route** — `/api/seasonality/similar` is a backward-compat wrapper for `climate.phase`; marked `# DEPRECATED` in routes.py. Permanently pinned to `mode='topn'` (WO7b). New callers use `/api/similarity?lens=climate.phase`. No active callers in sandbox.html; remove when convenient.
- **CHAR open design questions** (F8.5, F8.6, F9.6, F11.4, F11.6) — held pending expert review
