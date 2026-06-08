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
earlier exploratory scripts are archived in the `cedop` repo.

Research framing: `docs/edop/prospectus_20260505.md` and `docs/edop/project_summary_20260606.md`.

---

## Research phases

### Phase 1 — Signature development (complete)
**Goal**: Design and implement EDOPS signature v0.1 → v0.2.

**Products**:
- EDOPS API (`/api/signature`) delivering Bands A–T for any lat/lon
- Codebook `metadata/edops_codebook_v03.tsv`
- **Lookup page** (`sandbox.html`) — point lookup, neighborhood map, full signature

### Phase 2 — Characterization / CHAR (complete)
**Goal**: Systematic characterization of the EDOPS signature dataset — distributions,
spatial structure, bivariate relationships — before any correspondence testing or modeling.
Comprised two strands: EDA (statistical) and ESDA (spatial).

**Products**:
- EDA findings `logs/exploration_log.md` (F1.1–F11.6); ESDA findings `logs/esda_findings.md`
- Codebook `metadata/edops_codebook_v03.tsv` (7 CHAR columns added)
- CHAR report `docs/char/CHAR_report_draft02.docx` (35 pp; gitignored)
- **Explorer page** (`explorer.html`) — visual CHAR product

### Phase 3 — Aggregation (not started)
**Goal**: Enable EDOPS signature delivery for *areal* locations — user-defined study areas
and existing polygon datasets (historical polities, ecoregions, etc.). Requires spatial
aggregation methods (area-weighted vs. flow-weighted for hydrological variables).

### Phase 4 — Correspondence testing (not started)
**Goal**: Test the degree to which environmental signatures predict or correlate with
cultural patterns — using D-PLACE, Seshat, and Cliopatria as external datasets.

---

## Current work

Explorer Compare tab — **provisionally complete** as of 2026-06-04.

- Canvas scatter, region-highlight-on-pill-click, callout annotation, regional Spearman strip
- `/api/explorer/scatter` endpoint; `basin_regions.json` static lookup (gitignored — rsync)
- OLS regression fit on displayed subset only (p99 x-clip, p97 y-clip) — avoids leverage distortion
- Default pair: `temperature_annual × precipitation_annual` (Mediterranean sign reversal)
- Quick-buttons: T×P (sign reversal) | Ele×Slope (plateau) | Ele×Precip (orographic) | Temp×Snow (cold-arid)
- To swap default pair: `explorer.html` lines 399 (active button), 1964–1965 (`_compareX`/`_compareY`)

Design: `docs/design/EDOPS_explorer_prompt_compare.md`.
Detail: `logs/session_log_20260604.md` §"Compare tab".

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
docs/                    # Working docs — gitignored
scripts/edop/            # Data pipelines, ESDA, Explorer asset generation
notebooks/edop/spatial/  # ESDA + CHAR notebooks
logs/                    # session_log_YYYYMMDD.md, exploration_log.md, esda_findings.md
metadata/                # edops_codebook_v03.tsv and prior versions
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
/api/signature?lat=X&lon=Y[&bands=ABCDET&from_year=N&to_year=N&level=6|8]
    Returns profile_groups A–T. Band T requires from_year+to_year (0–1998 CE).
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
- `public.basin06`: 16,397 L6 sub-basins; `hybas_id`, `geom`, signature fields
- `public.basin08`: 190,675 L8 sub-basins; same schema
- `gaz.clio_polities`: Cliopatria polities — columns lowercase (`fromyear`, `toyear`, `name`, `geom`)
- Temperature fields (`tmp_dc_*`): stored as °C × 10 — always divide by 10 for display
- PostGIS geometries: pass as WKT via `ST_GeomFromText()`, not EWKB hex (psycopg3 endian issue)
- BasinATLAS NoData sentinel: `−9999` — mask before any analysis

---

## Deployment

- **URLs**: `edops.kgeographer.org` (and `cedop.kgeographer.org`) — same Hetzner CPX32 server (Nuremberg, 46.225.125.25)
- **Stack**: Nginx → Gunicorn (port 8001) → FastAPI; `cedop.service` systemd unit
- **Virtualenv**: `/home/karlg/envs/cedop/`; **Working dir**: `/var/www/cedop`
- **Note**: Server still pulls from `kgeographer/cedop`. Migration to `kgeographer/edops` is pending.
- **Deploy sequence** (current — against cedop):
  ```
  git push origin main                  # push edops repo
  rsync <gitignored assets> server:...  # PMTiles, parquet, tiles
  ssh kgeographer-1
    cd /var/www/cedop && git pull        # TODO: migrate to /var/www/edops
    sudo systemctl restart cedop        # requires password — manual step
  ```

---

## Testing

```bash
curl http://localhost:8000/api/health
curl "http://localhost:8000/api/signature?lat=16.76618535&lon=-3.00777252"  # Timbuktu
python -m pytest tests/
```

---

## Key design documents

| Doc | Purpose |
|-----|---------|
| `docs/edop/project_summary_20260606.md` | Current project summary |
| `docs/edop/prospectus_20260505.md` | Research direction (superseded by project summary) |
| `docs/design/scenarios.md` | User profiles + scenarios — read before Lookup UI work |
| `docs/design/EDOPS_explorer_prompt_compare.md` | Compare tab agreed design |
| `metadata/edops_codebook_v03.tsv` | Variable reference; loaded at startup by `signature.py` |
| `docs/edop/edops_schema.json` | Signature schema with Timbuktu example values |
| `logs/esda_findings.md` | Accreting ESDA findings (BV.1–BVR.7, CAT.1–8, etc.) |
| `logs/exploration_log.md` | EDA findings (F1.1–F11.6) |

---

## Open / deferred items

- **Explorer Compare tab** — provisionally complete; open exploration welcome, no known blockers
- **Explorer L8 choropleth** — deferred until after 8 June demo
- **Lookup neighborhood types** — single basin / neighbors / buffer; polygon aggregation
  is methodologically thorny; deferred to Phase 3 (Aggregation)
- **Cliopatria viewer** (`/polities`) — live but eyes-only for ISHI; social diff, basin06
  overlay, and nav link are open threads; code is Phase 4 Correspondence precursor
- **Server migration** — move working dir from `cedop` → `edops` repo; pending
- **Dead API routes** — `/wh-sites`, `/similar`, `/whc-*` in `routes.py` are orphaned
  (workbench retired); remove in a cleanup pass
- **CHAR open design questions** (F8.5, F8.6, F9.6, F11.4, F11.6): Band C silent error
  for BCE queries; population density in signature; EarthStat/HYDE divergence; LMR proxy
  bias disclosure — held for October 2026 expert meeting
