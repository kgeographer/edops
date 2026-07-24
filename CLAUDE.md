# CLAUDE.md — EDOPS

Read this at the start of every session. It describes current project state, not history.
Session-by-session detail lives in `logs/session_log_YYYYMMDD.md`.

**Session startup:** read this file for orientation, then the tracker for the active phase.
- `CLAUDE.md` (this file) — phase overview, architecture, conventions, pointers
- `docs/cdop/pilot/CDOP_PILOT_tracker.md` — authoritative current state, roadmap, locked decisions ← active
- `docs/edop/demo/DEMO_tracker.md` — frozen reference (DEMO closed 2026-07-18)
- `docs/design/deferred_items_register.md` — cross-phase parked items
- `logs/session_log_YYYYMMDD.md` — daily detail; `docs/cdop/pilot/wo{nn}_findings.md` — per-WO findings

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

| Phase | Status | Key product |
|---|---|---|
| 1 — Signature development | complete | `/api/signature`, `sandbox.html`, variable catalog v0.3 |
| 2 — Characterization / CHAR | complete | `explorer.html`, EDA/ESDA findings |
| 3 — Areas | complete 2026-06-30 | `engine.py` — resolver → aggregator → payload; `AREAS_tracker.md` (frozen ref) |
| Surface | complete 2026-07-10 | `sandbox_v3.html` at `/sandbox/lookup3`; see `SURFACE_tracker.md` (frozen ref) |
| Demo | complete 2026-07-18 | `sandbox_v3.html` polish; similarity instrument; see `DEMO_tracker.md` (frozen ref) |
| **CDOP1 — pilot** | **active** | `cdop_pilot.html`; L08 lens index; WH Cities lens swap; see `CDOP_PILOT_tracker.md` |
| 4 — Correspondence testing | not started | D-PLACE / Seshat / Cliopatria |

---

## Current work

**CDOP1 is the active track. Branch: `cdop`; cut WO branches off `cdop`, merge back on accept.**

- **Goto:** `docs/cdop/pilot/CDOP_PILOT_tracker.md` — authoritative state, roadmap, locked decisions
- **Deferred items:** `docs/design/deferred_items_register.md` (cross-phase)
- **Current step:** WO6a **and** WO6b complete on `cdop_wo6` (2026-07-22; Opus passed WO6b). Both are exploratory notebooks — no engine/API/UI change yet. **WO6b is the breakthrough:** stop compressing the twelve monthly values into scalars and compare the *raw twelve-value curve directly* (correlation). It discriminates, passes every known-answer probe, and produces **modality emergently** — same-modality neighbours fall out with nothing about peak count in the metric, dissolving the threshold problem WO6a couldn't solve. The conjunction built on it is anti-fragile (load-bearing condition rotates by query). Karl reframed the target: EDOPS needs two *discrete* classes — {aseasonal / 1 / 2} and {warm-wet / cool-dry / neither} — not a continuous score; the second is served by direct precip×temp correlation (verified). Findings: `wo6b_findings.md`; handoff to Opus: `wo6_status_CC.md`. WO6a's floor conclusion amended (Somalia was the wrong flagship; cause is low seasonal *range*, not aridity). **Next: WO6c** (drafted by Opus, `wo6c_similarity-redux.md`) — rebuild the Similarity panel on the correlation-backed conjunction (engine + UI). Prior context (Context tab shipped in WO5; WO3 C+D suspended) in tracker.
- **Tests:** 584 pass, 50 skipped
- **Milestone:** Braga (2026-09-20) — UNED Digital Humanities conference

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
docs/edop/surface/       #   Surface tracker + findings (tracked; frozen ref)
docs/edop/demo/          #   Demo tracker + findings (tracked) ← active
docs/design/             #   deferred_items_register.md, scenarios.md (gitignored)
docs/design/demo/        #   sandbox_v3 line specs + demo design notes (gitignored)
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

### `/sandbox/lookup3` — Demo surface (active)
`app/templates/sandbox_v3.html` — Demo phase product; current focus.

Two-tab surface: **Settlements** (WHG place lookup → scope → BasinATLAS/LMR/HYDE choropleth + signature)
and **Polities** (search → slice slider + VCR → choropleth + signature).

- AWMC historical terrain basemap; HydroRIVERS PMTiles base layer (`app/static/sandbox/`; gitignored)
- Layer control (top-right over map); rivers toggleable
- L06/L08 level toggle; basin fill transparent (choropleth shows through)
- White-cased charcoal basin outlines; polity slice year overlay (top-left map corner)
- 4 placed settlement examples (Timbuktu, Rome, Kaifeng, Santa Fe) + 6 polity examples
- Line spec reference: `docs/design/demo/sandbox_v3_line_specs.md`

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
| `documentation/EDOPS_variable_catalog_v0.3.tsv` | Variable reference; loaded at startup by `signature.py` and `routes.py` — canonical copy, single source of truth |
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
- **Dead API routes** — `/wh-sites`, `/similar`, `/whc-*` in `routes.py` are orphaned
- **Deprecated route** — `/api/seasonality/similar` is a backward-compat wrapper for `climate.phase`; marked `# DEPRECATED` in routes.py. Permanently pinned to `mode='topn'` (WO7b). New callers use `/api/similarity?lens=climate.phase`. No active callers in sandbox_v3; remove when convenient.
- **CHAR open design questions** (F8.5, F8.6, F9.6, F11.4, F11.6) — held pending expert review
