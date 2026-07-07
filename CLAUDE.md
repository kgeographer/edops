# CLAUDE.md — EDOPS

Read this at the start of every session. It describes current project state, not history.
Session-by-session detail lives in `logs/session_log_YYYYMMDD.md`.

**Three-file planning system** — project status and planning context lives in three files
that must be kept consistent. Always read all three at the start of an active phase session:
- `CLAUDE.md` (this file) — high-level phase status, architecture, conventions
- `docs/edop/surface/SURFACE_tracker.md` — authoritative current state, roadmap, locked decisions
- `docs/design/areas/deferred_items_register.md` — parked items and their triggers (cross-phase; not forked)

---

## What this project is

**EDOPS** (Environmental Dimensions of Place Service) is a FastAPI service that delivers
structured environmental "signatures" for any point on Earth. Signatures characterize the
drainage basin containing a given point using BasinATLAS variables covering hydrology,
climate baselines, terrain, and ecoregion, plus temporal enrichment layers: LMR v2.1
paleoclimate, HYDE 3.4 land-use history, and eVolv2k v4 volcanic forcing.

EDOPS is the active component of **Computing Place** (CEDOP), a spatial humanities research
platform. The companion CDOP (Cultural Dimensions of Place) component is deferred; its
earlier exploratory scripts are archived in the `cedop`.

Research framing: `docs/edop/project_summary_20260606.md`

---

## Research phases

### Phase 1 — Signature development (complete)
**Goal**: Design and implement EDOPS signature v0.1 → v0.3.

**Products**:
- EDOPS API (`/api/signature`) delivering Bands A–T for any lat/lon; v0.3 deployed 2026-06-10
- Codebook `documentation/EDOPS_variable_catalog_v0.3.tsv` (canonical; loaded at startup)
- **Lookup page** (`sandbox.html`) — point lookup, neighborhood map, full signature
- API docs: `documentation/API_guide.md`, `documentation/edops_schema.json`, `app/static/api_guide.html`

### Phase 2 — Characterization / CHAR (complete)
**Goal**: Systematic characterization of the EDOPS signature dataset — distributions,
spatial structure, bivariate relationships — before any correspondence testing or modeling.
Comprised two strands: EDA (statistical) and ESDA (spatial).

**Products**:
- EDA findings `logs/exploration_log.md` (F1.1–F11.6); ESDA findings `logs/esda_findings.md`
- Codebook `documentation/EDOPS_variable_catalog_v0.3.tsv` (7 CHAR columns added)
- CHAR report `docs/char/CHAR_report_draft02.docx` (35 pp; gitignored)
- **Explorer page** (`explorer.html`) — visual CHAR product

### Phase 3 — Areas (complete 2026-06-30)
**Goal**: Expand EDOPS API to deliver signatures for areal locations — weighted basin-set
resolver → variable-aware aggregator → endpoint. Closed with WO22 (`/area` endpoint stub).

**Engine** (`scripts/edop/areas/engine.py`): resolver → aggregator → payload. Resolvers:
buffer, single-basin, basin-ring, polygon/polity. Aggregator: Blocks 1–7 across all
variable types; Band T (HYDE/LMR/eVolv2k); `_weighted_histogram` in `detail['distribution']`
across basin/HYDE/LMR substrates, temporally stamped; no collapse. 185 tests PASS.

**Settled background**: `docs/edop/areas/AREAS_tracker.md` (frozen reference). Design
decisions, WO log, and locked decisions live there — read for background, do not extend.
Deferred items register is cross-phase: `docs/design/areas/deferred_items_register.md`.

### Surface (active — see SURFACE_tracker.md)
**Goal**: Build what a person sees and does with the engine. Areas built the engine;
Surface builds the consumer. First deliverable: a new sandbox page exercising the engine
end to end. Milestone: Braga demo (2026-09-20). Branch: `surface`.

**Work folders**: `notebooks/edop/surface/`, `docs/edop/surface/`, `output/edop/surface/`

### Phase 4 — Correspondence testing (not started)
**Goal**: Test the degree to which environmental signatures predict or correlate with
cultural patterns — using D-PLACE, Seshat, and Cliopatria as external datasets.

---

## Current work

**v0.3 public release complete (2026-06-10).** No known open blockers.

**Surface is the active track. Branch: `surface`.**
Read `docs/edop/surface/SURFACE_tracker.md` — authoritative goto for current state, roadmap,
and locked decisions. Consult `docs/design/areas/deferred_items_register.md` (cross-phase).

**Engine (stable background — Areas complete 2026-06-30):**
`scripts/edop/areas/engine.py` — resolver → aggregator → payload. Four public entry points:
- `areal_signature(lat, lon, radius_km, conn, ...)` — buffer path (not yet HTTP-wired)
- `areal_signature_polygon(geom_wkt, conn, ...)` — polygon/polity path; served on `GET /api/area`
- `single_basin_signature(lat, lon, conn, ...)` — single containing basin; HTTP-wired via `type=single_basin`
- `basin_ring_signature(lat, lon, conn, ...)` — centre + first-order adjacents; HTTP-wired via `type=basin_ring`

Resolvers: `resolve_buffer`, `resolve_single_basin`, `resolve_basin_ring`, `resolve_polygon`, `resolve_polity` — all in engine.py.
Aggregator: Blocks 1–7 across all variable types; Band T (HYDE/LMR/eVolv2k).
`_weighted_histogram` in `detail['distribution']` across basin/HYDE/LMR substrates, temporally stamped.
Two independent temporal axes: `resolver_year` (polity boundary year) and Band T span (`from_year`/`to_year`).
395 tests PASS (80 engine `tests/engine/test_engine_contract.py` + 206 app incl. `tests/test_area.py` + `tests/test_areas.py` + 109 surface `tests/surface/`).

**`db_utils.read_areas_tsv(path, **kwargs)`** — always use this instead of bare
`pd.read_csv` for any Areas TSV containing `hybas_id` or `dominant_hybas_id`; forces Int64.

**Surface — current step:** WO17 complete; next: WO18 (pre-aggregation + route swap).
- SF.1 (sandbox capability-gap analysis) complete — `docs/edop/surface/surface_findings.md`
- WO1 (exemplar payload inspection) complete — F1.1–F1.13 in `docs/edop/surface/wo1_findings.md`;
  design notes DN1–DN10 in `docs/edop/surface/wo1_design-notes.md`; 3 engine TODOs fixed
- Engine row schema: `make_row` no longer emits `row["distribution"]` (was always null; removed)
- **Step 0 (skeleton) complete** — `app/templates/sandbox_v2.html` at `/sandbox/lookup2`;
  scope gate + Band T toggle; Level fixed L06; 5-scope dropdown
- **WO2 (Step 1 rows-renderer) complete** — fixture harness (`/dev/exemplars/` static mount);
  `renderSignature` → band accordion; `renderLeaf` 6-method dispatch; accept gate passed
- Field names in fixture: `representative_score`, `representative_raw`, `score_suppressed`
- **WO3 (Step 2 leaf widgets) complete** — buffer scope live; B1 histogram; B2 coherence badge;
  B3 range-bar + regime marks; B4 mixture bar. Findings F3.1–F3.4 in `wo3_findings.md`.
- **WO4 (`/api/areas` + buffer live) complete** — `GET /api/areas?type=buffer` live; two-pass
  validation; accept-gate equivalence test vs fixture; `tests/test_areas.py` (21 tests).
  `/api/area` untouched.
- **WO5 (polity fixture + Band T charts) complete** — Northern Song wired to fixture; Band T
  accordion: LMR time marginal SVG + slider + value marginal histogram; HYDE epoch table;
  eVolv2k event list. Findings F5.1–F5.5 in `wo5_findings.md`.
- **WO6 (polity scope live) complete** — `type=polity` in `/api/areas`; live DB call; equivalence
  confirmed. Findings F6.1–F6.3 in `wo6_findings.md`.
- **WO7 (arbitrary polity search) complete** — polity search → `/api/polity/search` → slice picker
  → live call. Band T auto-fills from full polity lifespan (not slice dates — F7.2). Resolver year
  threaded through flow. UX: T open/A–E collapsed; map tab on polity change; spinner.
  Findings F7.1–F7.5 in `wo7_findings.md`.
- **WO8 (MapLibre stack + layer shell) complete** — Leaflet → MapLibre GL JS on v2 only; layer
  shell (`add`/`remove`/`restyle`/`clear`) established; polity boundary reproduced via shell.
  GeoJSON for low-cardinality scopes; PMTiles deferred to polity choropleth.
  Findings F8.1–F8.3 in `wo8_findings.md`. **313/313 tests pass** (no changes needed).
- **WO9 (audit) complete** — single-basin confirmed fixture-only; basin-ring weight policy
  register row closed (per-member design, no aggregate). Findings in `wo9_audit_findings.md`.
- **WO10 (single-basin live) complete** — `type=single_basin` in `/api/areas`; live frontend
  branch; Band T via polygon path; stale docstring corrected. 332/332 tests pass.
  Findings in `wo10_findings.md`.
- **WO11 (single-basin map) complete** — `drawSingleBasin()` via shell; honesty check
  (`hybas_id` match before draw); fit-bounds. 336/336 tests pass.
  Findings in `wo11_findings.md`.
- **WO12 (example-select standard + buffer map) complete** — example handler standardised;
  Map-first landing after Get signature; buffer basins + circle via shell; `member_ids`
  in buffer neighborhood; `GET /api/basin/geom` route; `fitBounds` via `map.once('resize')`
  after tab switch. Findings in `wo12_findings.md`.
- **WO13 (basin-ring live) complete** — ring scope end-to-end: center sig + ring on map
  (two shell layers, categorically colored) + clickable members (on-demand single_basin fetch)
  + return-to-center. Parallel fetch: center sig + `/api/basin/ring` topology (~1.1 s total).
  Band T available for all members. Ring info div in left column. 391/391 tests pass.
  Findings in `wo13_findings.md`.
- **WO14 (basin choropleth) complete** — PMTiles basin06 vector source + feature-state paint
  for 4 BasinATLAS vars (aridity, precip, temp, cropland); RDBU ramp; legend; shell extended
  with `{ before }` for lazy-load layer ordering; `#v2-intro-text` sub-div hides on sig load
  while `#v2-choropleth` persists. LMR/HYDE entries inert-present for WO15. 395/395 tests pass.
  Findings in `wo14_findings.md`.
- **WO15 (LMR paint + example-select UX) complete** — LMR temp/precip anomaly live from
  `lmr_notches.geojson` (5 notches, not per-year; quality floor 700 CE); diverging RDBU ramp
  centred on zero; paint-year slider hidden (default 1100 CE / MCA notch); state audit conducted
  (7 conflicts, `wo15_state_audit.md`); scope dropdown sidelined as display-only; preview geometry
  on example select (single/ring fetch topology; buffer circle-only); Get Signature → Signature tab;
  choropleth cleared on example change. 80/80 structural tests pass. Findings in `wo15_findings.md`.
- **WO16a (HYDE basin values — feasibility + implementation) complete** — architecture decision:
  values-API over pre-baked epoch raster tiles; `lmr_notches.geojson`/`basin06.pmtiles` pattern
  extended to HYDE; new `/api/hyde/values?var=X&year=N` route (centroid lookup, 0.31s for 16k
  basins); `applyHydeChoropleth` replaces raster block; slice-change reactive repaint for both
  HYDE and LMR. Feasibility notebook at `notebooks/edop/surface/wo16a_hyde_basin_values.ipynb`.
  93/93 structural tests pass. Findings in `wo16_findings.md`.
- **WO17 (area-weighted HYDE crosswalk) complete** — `temporal.hyde_basin06_weights` materialized
  (2.82M rows, 1.2 min build); area-weighted r=0.902 vs centroid 0.689; route swap blocked by
  2.67s query time. WO18 = pre-aggregation → `temporal.hyde_basin06_steps` → route swap.
  Denominator settled: `frac_full` (÷ sub_area). Notebook: `wo17_hyde_area_weighted.ipynb`.
  Findings in `wo17_findings.md`.
- Per-WO branch pattern: `surf_wo{n}` → merge to `surface` at accept gate
- Build workflow: `docs/edop/surface/surface_workflow_opus.md` — read before each WO
- State/renderer model: `docs/edop/surface/surface_state-analysis.md`

**Milestone:** Braga (2026-09-20) — UNED Digital Humanities conference; new sandbox page
demonstrating the areal engine is the deliverable. ~11 weeks from 2026-07-01.

---

## Architecture

```
app/
├── main.py              # FastAPI app
├── api/routes.py        # All REST endpoints
├── db/
│   ├── connection.py    # db_connect()
│   └── signature.py     # Core signature query; loads codebook at startup
├── web/pages.py         # Jinja2 page routes
├── templates/
│   ├── sandbox.html     # Lookup page — Phase 1 product
│   ├── explorer.html    # Explorer page — Phase 2 product
│   ├── cliopatria.html  # Cliopatria polity viewer — eyes-only for ISHI; Phase 4 precursor
│   └── ...
└── static/
    ├── css/site.css
    ├── explorer/        # PMTiles, GeoJSON, HYDE tiles (gitignored — rsync only)
    └── ...

documentation/           # Public-facing docs (tracked)
docs/                    # Design docs and WIP — gitignored with exceptions:
docs/edop/areas/         #   Areas tracker (frozen ref) + findings (tracked)
docs/edop/engine/        #   Work-order specs (tracked)
docs/edop/surface/       #   Surface tracker + findings (tracked) ← active
docs/design/             #   deferred_items_register.md, scenarios.md (gitignored)
scripts/edop/            # Data pipelines, ESDA, Explorer asset generation
scripts/edop/areas/      # Areas engine — engine.py is the primary artifact
notebooks/edop/explore/  # CHAR phase EDA notebooks
notebooks/edop/spatial/  # CHAR phase ESDA notebooks
notebooks/edop/areas/    # Areas phase notebooks (research record; frozen)
notebooks/edop/surface/  # Surface phase notebooks ← active
output/edop/areas/       # Areas output (gitignored)
output/edop/surface/     # Surface output (gitignored)
logs/                    # session_log_YYYYMMDD.md, exploration_log.md, esda_findings.md
logs/2026_jan-may/       # Archived earlier session logs
metadata/                # gitignored
```

---

## The two sandbox pages

### `/sandbox/lookup` — Lookup
`app/templates/sandbox.html` — Phase 1 product; primary researcher tool.

WHG place lookup → basin assignment → neighborhood map → Band A–T signature.
- Level 08/06 toggle; s/u/Δ toggle; Band T temporal charts (PDSI/Temp/Precip + eVolv2k)
- Analysis α tab: water provenance, s/u divergence, scale mismatch alert
- Ecoregion → Wikipedia modal; LLM narrative button
- Examples: Timbuktu 1100–1200, Rome 0–300, Kaifeng 1000–1100

Key design doc: `docs/design/scenarios.md` — read before any Lookup UI work.

### `/sandbox/explorer` — Explorer
`app/templates/explorer.html` — Phase 2 product; visual CHAR exhibit.

MapLibre GL JS choropleth on `basin06.pmtiles` (L6, 16,397 basins). Three tabs:

**Global** — world choropleth; Bands A–T accordion; histogram; LISA;
Band T (LMR 5-period / HYDE 4-var 3-view / eVolv2k timeline).

**Regions** — 6-panel synchronized choropleth: East Asia, South Asia, Southwest Asia,
Mediterranean & N. Africa, Mesoamerica, Pacific Northwest. Band T fully supported
(LMR with country overlay, HYDE raster). Controls strip persists across tabs.

**Compare** — provisionally complete.

### Explorer architecture decisions (do not revisit)
- **PMTiles + flat values API**: geometry served once from `basin06.pmtiles`;
  `/api/explorer/values` returns `{hybas_id: value}` dict only (~0.3 MB, no geometry).
  Sub-second variable loads. Do not suggest GeoJSON caching — explicitly rejected.
- **Color scheme**: warm/dry = red, cold/wet = blue throughout. Temperature diverging
  uses `1 - t`; aridity + precipitation RDBU sequential (low = red); LMR PDSI/precip
  use `t`; LMR temperature anomaly uses `1 - t`.
- **Gitignored static assets** (must rsync to server, never git):
  `basin06.pmtiles`, `lmr_notches.geojson`, `countries_110m.geojson`,
  `hyde_tiles/`, `lisa_classifications.parquet`

---

## Key endpoints

```
NOTE: see documentation/API_guide.md (master, public)

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
- `public.basin06`: 16,397 L6 sub-basins; `hybas_id`, `geom`, signature fields
- `public.basin08`: 190,675 L8 sub-basins; same schema
- `gaz.clio_polities`: Cliopatria polities — columns lowercase (`fromyear`, `toyear`, `name`, `geom`)
- `temporal.hyde_cells`: 2,215,829 HYDE 3.4 grid cells (~5 arc-min); PostGIS polygon `geom`, `area_km2`, and four variable columns (`cropland`, `grazing`, `pasture`, `rangeland`) each stored as `real[]` arrays indexed by `step_idx`
- `temporal.hyde_times`: 128 rows mapping `step_idx` → `year_ce` (−10000 to 2025); join to get year-specific HYDE values
- `temporal.lmr_climate`: 16,380 LMR v2.1 grid points at 2°×2°; PostGIS point `geom`; `pdsi`, `air`, `prate` stored as `real[]` arrays of length 2001 (1–2001 CE, 0-indexed)
- `temporal.evolv2k_v4`: eVolv2k v4 volcanic forcing rows by `year_ad`; columns `vssi_tg`, `so4_grl`, `so4_ant`, `lat`, `location`
- Temperature fields (`tmp_dc_*`): stored as °C × 10 — always divide by 10 for display
- PostGIS geometries: pass as WKT via `ST_GeomFromText()`, not EWKB hex (psycopg3 endian issue)
- BasinATLAS NoData sentinel: `−9999` — mask before any analysis

---

## Deployment

- **Local dev server**: `uvicorn app.main:app --reload` (runs on http://localhost:8000)
- **URLs**: `edops.computingplace.org` — Hetzner CPX32 server (Nuremberg, 46.225.125.25)
- **Stack**: Nginx → Gunicorn (port 8001) → FastAPI; `edops.service` systemd unit
- **Virtualenv**: `/home/karlg/envs/cedop/`; **Working dir**: `/var/www/edops`
- **Deploy sequence**:
  ```
  git push origin main                  # push edops repo
  rsync <gitignored assets> server:...  # PMTiles, parquet, tiles, hyde_epoch_maxes.json
  ssh kgeographer-1
    cd /var/www/edops && git pull
    sudo systemctl restart edops        # requires password — manual step
  ```

---

## Notebook conventions

- **Cell numbering**: every code cell must have `# Cell N` as its first line.
- **DB connection**: `from scripts.shared.db_utils import db_connect` then `conn = db_connect()`. Default database is `cedop`.
- **Spatial queries**: `gpd.read_postgis(sql, conn, geom_col='geom').rename_geometry('geometry')` — always rename so column is `geometry` not `geom`.
- **Non-spatial queries**: `pd.read_sql(sql, conn)` — f-string SQL with values interpolated directly (no SQLAlchemy, no named params).
- **Output path**: derive from module location, not relative path — `ROOT = Path(db_utils.__file__).parent.parent.parent; OUT = ROOT / 'output' / 'edop'`
- **Map figure rendering**: to get black text on white backgrounds, do NOT rely on `%matplotlib inline`, `plt.style.use('default')`, rcParams, or object-level helpers — PyCharm overrides all of these. Instead: `fig.patch.set_facecolor('white')`, `ax.set_facecolor('white')`, `color='black'` on all text, `fig.savefig(..., facecolor='white')`, `plt.close(fig)`, then `display(IPImage(str(outpath)))`. This displays the saved PNG, bypassing the inline renderer entirely. See `scripts/edop/edops_polity_maps.py` as the reference implementation.

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
| `documentation/EDOPS_variable_catalog_v0.3.tsv` | Variable reference; loaded at startup by `signature.py` and `routes.py` — canonical copy, single source of truth |
| `documentation/EDOPS_esda_findings.md`          | ESDA findings (BV.1–BVR.7, CAT.1–8, etc.)                                                                        |
| `documentation/EDOPS_eda_findings.md`           | EDA findings (F1.1–F11.6)                                                                                        |
| `docs/edop/prospectus_20260505.md`              | Initial research direction doc (superseded by project summary)                                                   |
| `docs/design/scenarios.md`                      | User profiles + scenarios — read before Lookup UI work                                                           |
| `docs/edop/edops_schema.json`                   | Signature schema with Timbuktu example values                                                                    |

---

## Open / deferred items

- **Explorer L8 choropleth** — deferred; no active pull
- **Cliopatria viewer** (`/polities`) — live but eyes-only for ISHI; social diff, basin06
  overlay, and nav link open; code is Phase 4 Correspondence precursor
- **Dead API routes** — `/wh-sites`, `/similar`, `/whc-*` in `routes.py` are orphaned
- **CHAR open design questions** (F8.5, F8.6, F9.6, F11.4, F11.6): Band C silent error
  for BCE queries; population density in signature; EarthStat/HYDE divergence; LMR proxy
  bias disclosure — held pending expert review; no fixed date
- **Areas deferred items** — multi-fixture calibration, `/area` input types beyond polity,
  per-unit polity rendering, upstream resolver — all in `docs/design/areas/deferred_items_register.md`
- **Braga milestone (2026-09-20)** — UNED Digital Humanities conference; demo with Pitt
  colleagues. Deliverable: new sandbox page surfacing the areal engine. ~12 weeks from 2026-06-30.
