# CLAUDE.md — EDOPS

Read this at the start of every session. It describes current project state, not history.
Session-by-session detail lives in `logs/session_log_YYYYMMDD.md`.

**Three-file planning system** — project status and planning context lives in three files
that must be kept consistent. Always read all three at the start of an active phase session:
- `CLAUDE.md` (this file) — high-level phase status, architecture, conventions
- `docs/edop/areas/AREAS_tracker.md` — authoritative current state, block table, locked decisions
- `docs/design/areas/deferred_items_register.md` — parked items and their triggers

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

**Deferred items register**: `docs/design/areas/deferred_items_register.md` — consult at every step resumption; add rows there, not as loose flags in notebooks or reports.

**Products so far**:
- `notebooks/edop/areas/aggregation_figures.ipynb` — Phase 3 orientation figures (Kingdom of Egypt / discharge heterogeneity, resolution mismatch, aggregation pathways)
- `notebooks/edop/areas/step1_buffer_resolver.ipynb` — buffer resolver: (lat, lon, radius_km, level) → weighted basin set `{hybas_id, weight}`; uses `geog` column directly; tested Timbuktu 100 km → 9 basins, weight sum = 1.0
- `notebooks/edop/areas/step2_value_attachment.ipynb` — value attachment: basin set → raw values (from view) + position scores + categorical class IDs + flags; outputs `step2_raw.tsv`, `step2_matrix.tsv`, `step2_class_ids.tsv`, `step2_meta.tsv`
- `notebooks/edop/areas/step3_aggregation.ipynb` — block 1 aggregation: continental-gradient continuous variables → weighted p10/p90/mean + spread verdict; outputs `step3_block1_results.tsv`

**Step 2 design notes** (do not revisit):
- Continuous scores: PERCENT_RANK over full basin table with outer CASE guard for -9999/NULL → NULL score (without the outer guard, NoData basins rank highest due to NULLS LAST)
- Zero-aware variant: if catalog `zero_fraction` ≥ 0.20, zeros score 0.0 explicitly and non-zeros rank within the positive subpopulation via PARTITION BY — prevents zero pile compressing non-zero range; scores are within-active-domain ranks, not global percentiles
- Categorical rarity: must fetch integer class IDs from raw TABLE using `db_col` for both basin values and global frequency; view returns text labels that don't match integer codes
- Flags (coast_flag, endorheic): emitted as raw integers, not scored
- `v_basin06_persist_rev1` and `v_basin08_persist_rev1` include `hybas_id` as second column (non-breaking additive fix)
- TSV files saved in different row orders — always join on hybas_id, never use positional `.values`

**Step 3 design notes** (do not revisit):
- Block 1 handles continental-gradient + scale-dependent continuous variables (34 vars); network-topology → Block 2; categoricals → Block 3
- Block 3: categorical class mixture; `strata_code` excluded (opaque sub-zone codes, undocumented intra-zone differences; see deferred register)
- Weighted quantiles via sorted cumulative weights + linear interpolation; spread = p90 − p10 (percentile points)
- `SPREAD_THRESHOLD = 20`; `ZERO_FRACTION_THRESHOLD = 0.20`; `ZERO_COVERAGE_THRESHOLD = 0.90` (all provisional)
- Degenerate-at-floor guard: if a variable's catalog `zero_fraction` ≥ 0.20 AND the buffer's `weight_at_zero` ≥ 0.90 → verdict = `outside_active_domain` (variable does not apply at this location)
- Block 1 verdicts are L6-only; they may flip at L8 due to MAUP (see deferred items register)

### Phase 4 — Correspondence testing (not started)
**Goal**: Test the degree to which environmental signatures predict or correlate with
cultural patterns — using D-PLACE, Seshat, and Cliopatria as external datasets.

---

## Current work

**v0.3 public release complete as of 2026-06-10.** No known open blockers.

Phase 3 — Areas is the active work block. **Branch: `engine_v0.4b`.**
Read `docs/edop/areas/AREAS_tracker.md` first — it is the authoritative goto for current
state, block status, locked decisions, and what's next. Consult
`docs/design/areas/deferred_items_register.md` at each step resumption.

**Step 3 aggregator status (as of 2026-06-21):**
- Block 1 — area-weighted coherence (continental-gradient + scale-dependent, 34 vars): **done**
- Block 2 — dominant basin (network-topology: discharge_annual, discharge_min, discharge_max): **done**
- Block 3 — categorical class mixture (9 vars): **done**
- Block 4 — flag/structural path (outlet_type 4-class mixture + coast_fraction flag_fraction): **done**
- Block 5 — untyped fallback (distribution-only) + extreme (river_area): **done**
- Block 6 — modality refinement (12 two_regime vars; seam-aligned with endorheic partition): **done**
- Block 7 — Band T gridded path (HYDE distribution + LMR distribution + eVolv2k global): **done**
- Engine assembly: **done** (WO11b complete; `areal_signature` is the public entry point)

**Engine assembly status (as of 2026-06-30):**
- WO4 — `make_row` / projector / assembler + Band T promotion: **done** (5/5 strict PASS)
- WO4b — Band T regression coordinate diagnosis: **done** (no code change; coordinate fixture corrected)
- WO5 — B2 dominant_basin extraction: **done** (4/4 strict PASS)
- WO6 — B1 area_weighted extraction: **done** (5/5 strict PASS)
- WO7 — B3 class_mixture extraction: **done** (6/6 strict PASS)
- WO8 — B4 flag/structural extraction: **done** (7/7 strict PASS)
- WO9 — B5 distribution_only + extreme extraction: **done** (6/6 strict PASS)
- WO10 — B6 modality post-pass: **done** (6/6 strict PASS)
- WO10b — distribution_only coherence flag: **done** (6/6 strict PASS; contract fully closed)
- WO11a — `load_catalog` + sourced/derived fork: **done** (7/7 strict PASS)
- WO11b — `areal_signature` final assembly: **done** (8/8 capstone PASS; 51 basin + 321 Band T rows)
- WO12 — Buffer L8 validation: **done** (Band T invariant; 11/11 modality flips; shortfall slivers; AF.6–AF.10)
- WO13/WO13a — Modality floor close-out: **done** (floor retired; support-relative posture settled; no engine edit)
- WO14 — Single-basin resolver + v0.3 comparison: **done** (373 rows payload; 0 MISMATCH/UNEXPLAINED; AF.11–AF.12)
- WO15 — Area-weighted cell weighting: **done** (HYDE + LMR `overlap/cell_area` normalization; size-bias removed; AF.13; 58 tests PASS)
- WO16 — Basin-ring resolver exploration: **done** (ST_Touches clean across Timbuktu L06/L08, Rome L06, Baghdad L06; all contacts ST_MultiLineString; no slivers; three weight schemes surfaced but not decided; notebook `basin_ring_exploration.ipynb`)
- WO17 — Basin-ring resolver + transition diagnostic: **done** (`resolve_basin_ring`; `border_bearing`; ST_PointOnSurface fix; 3 L06 fixtures; AF.14–AF.19)
- WO18 — Transition-character comparator: **done** (29-var universal intersection; 58 features; spanning-10 gate PASS; AF.WO18.1–3)
- WO19 — Scaled comparator n=50: **done** (47 WHC cities; k=3 silhouette-optimal clustering; ANCHORED partial; AF.WO19.1–5)
- WO20 — Polity resolver + polygon engine path: **done** (`resolve_polygon`, `resolve_polity`, `areal_signature_polygon`; N Song 376 basins; B6 skipped; 60/60 PASS)
- WO21b — Distribution histograms: **done** (`_weighted_histogram` in `detail` across basin/HYDE/LMR substrates; LMR collapse retired; `grid_areal_collapsed` + sentinels removed; 60/60 PASS)

**Deferred items note (2026-06-24):** Two items added from WO4b "doh moment" — (1) edge-sensitivity
diagnostic (boundary leverage, candidate trust-layer flag); (2) representative-point uncertainty /
WHG attestation cloud (Phase 4 input design). See `docs/design/areas/deferred_items_register.md`.

**Engine contract fully closed (2026-06-24):** `contract_amendments.md` Pending is empty.
Last item settled: distribution_only coherence (WO10b). Branch: `engine_v0.4b`.

**Population hygiene fix (2026-06-18):** step2 scorer now excludes -9999/NULL from PERCENT_RANK window via two-pass SQL; 9 vars corrected (pct_clay/silt/sand ×2, stream_gradient, slope_avg/upstream). No verdict flips at Timbuktu.

Output: `output/edop/areas/step3_results.tsv` — 51 rows + modality column; 12 two_regime scores suppressed; validated on Timbuktu 100 km / L06.
Companion: `output/edop/areas/step3_block3_mixture.tsv` — 22 rows (B3 + B4 outlet_type classes).
Companion: `output/edop/areas/step3_block5_distribution.tsv` — 18 rows (full per-basin distribution for untyped vars).
Companion: `output/edop/areas/step3_block6_regimes.tsv` — 24 rows (12 two_regime vars × 2 regimes).
Band T (separate notebook `step3b_band_t.ipynb`): `step3b_block7_primary.tsv` (321 rows, 1100–1200 CE), `step3b_block7_wide.tsv` (3427 rows, 1000–2000 CE), `step3b_block7_hyde_distributions.tsv` (332 rows, HYDE distribution companion with `spread_native` in km²/cell).

**Shared output envelope** (all blocks): `variable, method, status, representative_score,
representative_raw, n_basins, coverage_weight` + method-specific detail columns.
Block 7 extensions: `n_units`, `unit_type` (replace `n_basins`), `year`, `epoch_year`, `lmr_caveat`, `hyde_caveat`. Note: Block 7 `p10`/`p90`/`sd` are in native units (km²/cell); Blocks 1–6 use percentile points — engine assembly must reconcile (see deferred register).

**Findings**: `docs/edop/areas/areas_findings.md` — coded observations AF.1–AF.13 (method behavior, signal content, data quality). Add new AF.n entries as the phase proceeds.

**`db_utils.read_areas_tsv(path, **kwargs)`** — always use this instead of bare
`pd.read_csv` for any Areas TSV containing `hybas_id` or `dominant_hybas_id`; forces Int64.

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

- **Explorer L8 choropleth** — deferred until after 8 June demo
- **Lookup neighborhood types** — single basin / neighbors / buffer; polygon aggregation
  is methodologically thorny; deferred to Phase 3 (Aggregation)
- **Cliopatria viewer** (`/polities`) — live but eyes-only for ISHI; social diff, basin06
  overlay, and nav link are open threads; code is Phase 4 Correspondence precursor
- **Server migration** — complete as of 2026-06-07; working dir is `/var/www/edops`, service is `edops`
- **Dead API routes** — `/wh-sites`, `/similar`, `/whc-*` in `routes.py` are orphaned
- **CHAR open design questions** (F8.5, F8.6, F9.6, F11.4, F11.6): Band C silent error
  for BCE queries; population density in signature; EarthStat/HYDE divergence; LMR proxy
  bias disclosure — held pending expert review; no fixed date
- **Braga milestone (2026-09-20)** — UNED Digital Humanities conference; demo opportunity with
  Pitt colleagues. Target: v0.4 signature + updated sandbox surfacing areal engine (lean/full,
  new resolver types, endpoint params). ~11 weeks out from 2026-06-25.
