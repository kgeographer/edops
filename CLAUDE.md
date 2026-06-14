# CLAUDE.md — EDOPS

Read this at the start of every session. It describes current project state, not history.
Session-by-session detail lives in `logs/session_log_YYYYMMDD.md`.

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

### Phase 3 — Areas (active)
**Also called**: Aggregation, Neighborhoods (earlier working names; "Areas" is canonical).
**Goal**: Expand EDOPS API to deliver signatures for *areal* locations — new endpoint(s)
accepting polygon features of various kinds: Cliopatria polity geometries, user-defined
study areas (bboxes to start), and neighborhood types TBD (buffer, adjacent basins, etc.).
Core GISci question: area-weighted vs. flow-weighted aggregation for hydrological variables.

**Work folders**: `notebooks/edop/areas/`, `scripts/edop/areas/`, `output/edop/areas/`

**Products so far**:
- `notebooks/edop/areas/aggregation_figures.ipynb` — Phase 3 orientation figures (Kingdom of Egypt / discharge heterogeneity, resolution mismatch, aggregation pathways)
- `notebooks/edop/areas/step1_buffer_resolver.ipynb` — buffer resolver: (lat, lon, radius_km, level) → weighted basin set `{hybas_id, weight}`; uses `geog` column directly; tested Timbuktu 100 km → 9 basins, weight sum = 1.0
- `notebooks/edop/areas/step2_value_attachment.ipynb` — value attachment: basin set → raw values (from view) + position scores (PERCENT_RANK on full basin table, one SQL pass) + categorical rarity ranks (global class frequency from raw TABLE using integer db_col); outputs `step2_raw.tsv`, `step2_scores.tsv`, `step2_meta.tsv`

**Step 2 design notes** (do not revisit):
- Continuous scores: PERCENT_RANK over full basin table with outer CASE guard for -9999/NULL → NULL score (without the outer guard, NoData basins rank highest due to NULLS LAST)
- Categorical rarity: must fetch integer class IDs from raw TABLE using `db_col` for both basin values and global frequency; view returns text labels that don't match integer codes
- `v_basin06_persist_rev1` and `v_basin08_persist_rev1` now include `hybas_id` as second column (was missing; fixed this session; non-breaking additive change)
- TSV files saved in different row orders — always join on hybas_id, never use positional `.values`

### Phase 4 — Correspondence testing (not started)
**Goal**: Test the degree to which environmental signatures predict or correlate with
cultural patterns — using D-PLACE, Seshat, and Cliopatria as external datasets.

---

## Current work

**v0.3 public release complete as of 2026-06-10.** No known open blockers.

Phase 3 — Areas is the active work block. Steps 1 (buffer resolver) and 2 (value attachment) are complete and validated. Next: Step 3 — aggregation (collapse the basin×variable matrix per variable, dispatching on `typology_cluster`).

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
docs/                    # Older draft docs and WIP (partial; remainder in cedop repo)— gitignored
scripts/edop/            # Data pipelines, ESDA, Explorer asset generation
scripts/edop/areas/      # Phase 3 — Areas scripts
notebooks/edop/explore/  # CHAR phase EDA notebooks
notebooks/edop/spatial/  # CHAR phase ESDA notebooks
notebooks/edop/areas/    # Phase 3 — Areas notebooks
output/edop/areas/       # Phase 3 — Areas figures and output (gitignored)
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

**Compare** — provisionally complete. See Current work above.

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
python -m pytest tests/
```

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

- **Explorer L8 choropleth** — deferred until after 8 June demo
- **Lookup neighborhood types** — single basin / neighbors / buffer; polygon aggregation
  is methodologically thorny; deferred to Phase 3 (Aggregation)
- **Cliopatria viewer** (`/polities`) — live but eyes-only for ISHI; social diff, basin06
  overlay, and nav link are open threads; code is Phase 4 Correspondence precursor
- **Server migration** — complete as of 2026-06-07; working dir is `/var/www/edops`, service is `edops`
- **Dead API routes** — `/wh-sites`, `/similar`, `/whc-*` in `routes.py` are orphaned
- **CHAR open design questions** (F8.5, F8.6, F9.6, F11.4, F11.6): Band C silent error
  for BCE queries; population density in signature; EarthStat/HYDE divergence; LMR proxy
  bias disclosure — held for October 2026 expert meeting
