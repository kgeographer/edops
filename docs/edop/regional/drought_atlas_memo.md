# Tree-ring drought atlases as regional specializations of EDOPS

**Status:** speculative design memo, pre-WO. Nothing implemented except
`scripts/edop/drought_atlas_inspect.py`. Written 2026-09-26 in a remote session against `main` @ `4d06e04`.

---

## 0. Caveat on sources

This session's network policy blocked NOAA NCEI, the UCAR Climate Data Guide and the Memphis
drought portal, so **no atlas file was opened**. The format and inventory below come from
NOAA metadata records and paper abstracts seen through web search, plus prior knowledge of
these products. Items marked **[verify]** should be checked with
`scripts/edop/drought_atlas_inspect.py` before any loader is written.

---

## 1. What the atlases are

All the major tree-ring drought atlases share one design:

- **Method.** Point-by-point regression (PPR; Cook et al. 1999): a separate regression for
  each grid point, fed by tree-ring chronologies within a search radius. Recent atlases
  (OWDA, ERDA) use an *ensemble* PPR, then smooth or infill spatially.
- **Target.** Warm-season soil-moisture balance: PDSI, scPDSI or PMDI, calibrated against
  an instrumental grid (typically the 20th century).
  - Boreal atlases target June–August (JJA).
  - Southern-hemisphere atlases target the austral summer (DJF) **[verify per atlas]**.
- **Output.** Annual maps on a regular lat/lon grid, land cells only.
- **Nesting.** Chronologies drop out going back in time, so each cell is reconstructed by a
  sequence of nested models, with skill declining in earlier nests. Cells begin at different
  years: "0–2012 CE" for an atlas means that *some* cells reach year 0, not all.
- **Per-cell skill.** Calibration and verification statistics (r², RE, CE) are published per
  cell, sometimes per nest **[verify which atlases ship these inside the netCDF and which as
  separate ASCII]**.

### Inventory

| Atlas | Region | Grid | Span (CE) | Target | Source |
|---|---|---|---|---|---|
| NADA v2a | N. America ≤ ~63°N | 2.5° (286 pts) | 0–2006 | JJA PDSI | Cook et al. 2008 (NOAA study 6319) |
| LBDA | N. America incl. Alaska | 0.5° (11,396 pts; 1,845 chronologies) | 0–2005 | JJA PMDI | Cook et al. 2010 |
| LBDA v2 | Contiguous US | 0.5° | 0–2017 | JJA PMDI (recalibrated) | Gille et al. 2017 (study 22454) |
| MXDA | Mexico, 14–34°N 75–120°W | 0.5° (252 chronologies) | 1400–2012 | JJA scPDSI | Stahle et al. 2016 |
| OWDA | Europe, Mediterranean, N. Africa, Middle East | 0.5° (5,414 pts) | 0–2012 | JJA scPDSI | Cook et al. 2015 |
| ERDA | East European Plain to Urals | 0.5° | 1400–2016 | JJA scPDSI (smoothed, infilled) | Cook et al. 2020 |
| MADA v1 | Monsoon Asia | 2.5° (534 pts) | 1300–2005 | JJA PDSI | Cook et al. 2010 **[verify]** |
| MADA v2 | Monsoon Asia | 1.0° (453 chronologies) | ~1000–2012 | JJA scPDSI | Cook et al. (MADAv2) |
| ANZDA | E. Australia + NZ | 0.5° (176 chronologies + 1 coral) | 1500–2012 | austral-summer scPDSI | Palmer et al. 2015 |
| SADA | S. America south of 12°S | 0.5° **[verify]** (286 chronologies) | 1400–2000 | austral-summer scPDSI | Morales et al. 2020 |
| *PHYDA* | *Global* | *~2°* | *1–2000* | *PDSI + SPEI; annual / JJA / DJF* | *Steiger et al. 2018. Data assimilation, not PPR* |

PHYDA is not an atlas. Like LMR it is a global data-assimilation product, but it is
hydroclimate-focused and seasonally resolved. It belongs in this memo only as a candidate
*global floor* for drought that matches the atlases' JJA target better than LMR's annual
PDSI (see §8).

### Expected file shape [verify]

- **netCDF.** One variable (`pdsi` or similar) over `(time, lat, lon)`. Values are NaN
  outside the domain, over ocean, and before a cell's first nest. Time may be plain integer
  years or BP-coded: NOAA metadata gives OWDA as "1950 to −62 BP". For that reason the
  inspection script opens with `decode_times=False` and prints the raw time values.
- **ASCII.** A grid-point list (e.g. `cook2020-erda-gridpts.txt`: id, lat, lon), a year ×
  grid-point matrix, and often a separate calibration/verification-statistics file.

### Scale relative to EDOPS basins

- A 0.5° cell is about 2,400 km² at 40°N.
- A mean L6 basin is about 8,000 km², i.e. roughly three atlas cells per basin.
- A mean L8 basin is about 700 km². At L8 the atlas is effectively one cell per basin,
  which is how LMR's 2° grid already behaves at both levels.
- Storage is trivial. OWDA as `real[]` per cell (≈5,400 × 2,013 × 4 B) is about 44 MB,
  far below `hyde_cells`.

---

## 2. Framing: global floor, regional ceiling

EDOPS today returns the *same kinds* of signature everywhere. Regional products break that
symmetry: at Santa Fe or Tbilisi a query can get a 0.5°, annual, summer-specific drought
record from local trees, while at Timbuktu it cannot. The goal is to be richer where the
data allow without becoming inconsistent or misleading.

Principles:

1. **Global floor, regional ceiling.** LMR (and possibly PHYDA later) stays everywhere.
   Atlases are *added alongside* it, never substituted silently.
2. **Provenance travels with the value.** Every atlas row carries atlas id and version,
   season, variable, resolution, contributing cells, and skill for the requested span.
3. **No cross-atlas blending.** Where atlases overlap (LBDA/NADA/MXDA; OWDA/ERDA; MADA
   margins), return each atlas as its own row set, marked by a declared precedence.
   Averaging PPR products with different targets and calibrations would manufacture a
   dataset nobody published.
4. **Absence is a status, not a gap to fill.** The engine's Pin 1 vocabulary already covers
   both cases:
   - `outside_active_domain`: no atlas footprint at this place.
   - `no_data`: inside a footprint, but before the cell's first year. Kaifeng 965–990 is the
     live example (§5).
5. **Skill is time-varying.** A 1450 value and an 1850 value from the same cell are
   different epistemic objects; the caveat and detail blocks must say so.

The same pattern will carry other regional products later: documentary indices (REACHES
for China, Euro-Climhist), regional temperature reconstructions, lake and speleothem
syntheses. So build the atlases as the **first instance of a regional-layer registry**, not
as a one-off.

---

## 3. How it fits the current engine

`scripts/edop/areas/engine.py::aggregate_band_t` already runs three temporal sources through
one mechanism:

- HYDE (`grid_areal_distribution`, `hyde_cell`)
- LMR (`grid_areal_distribution`, `lmr_cell`, 2° envelopes intersected with the query
  geometry, weights `overlap_m2 / cell_area_m2` per WO15)
- eVolv2k (`global_forcing`)

The atlases are a **fourth block of the same shape as LMR**, differing only in resolution
and domain. No new aggregation machinery is needed:

- **One cell query per atlas.** Intersect the atlas cells with `buf_geom`, then compute
  `overlap_m2`, `cell_area_m2`, and fractional weights exactly as in the LMR block.
- **Rows via `make_row`:**
  - `variable='tda_scpdsi'` (or per-variable names if the atlas targets differ)
  - `band='T'`, `method='grid_areal_distribution'`, `unit_type='tda_cell'`
  - `year=…`, `units='scPDSI'`
  - `detail={'layer_id', 'season', 'resolution_deg', 'first_year', 'skill', 'distribution'}`
- **`_weighted_histogram`.** Accepts `unit_type='tda_cell'` unchanged: the low-resolution
  test already takes the cell path for any non-`basin` type. Only its docstring changes.
- **Status.**
  - `outside_active_domain`: the query geometry misses every footprint.
  - `no_data`: inside a footprint, but every intersecting cell is NaN for that year.
  - `ok` otherwise, with `coverage` = covered fraction of the query area, so a buffer
    straddling the OWDA edge reads partial coverage honestly.
- **Caveats** (`CAVEAT_TEXTS`, keys only on rows, per Pin 2):
  - `tda_season`: warm-season soil moisture, not annual; not directly comparable to the LMR
    annual PDSI anomaly.
  - `tda_early_skill`: the year falls before the contributing cells' reliable nest.
  - `tda_overlap`: another atlas also covers this area; see its rows.

**Scope paths:**

- **`scope=buffer` and `scope=area`.** Inherit this immediately. The single-year Band T
  restriction on `/signature` for these scopes (the `from_year == to_year` guard in
  `routes_common.py`) keeps the payload bounded.
- **`scope=basin`.** Band T currently comes from `app/db/temporal.py::get_temporal_context`
  (nearest 2° LMR cell). For atlases, nearest-cell is wrong at L6, where about three cells
  fall inside one basin. Two options:
  - **(a)** Route basin-scope atlas values through the same intersection, using the basin
    polygon as `geom_wkt`. This gives one aggregation semantics for all scopes.
  - **(b)** Precompute `temporal.tda_basin0{6,8}_series`, analogous to
    `hyde_basin0{6,8}_steps`. This is needed anyway for choropleths (§5).

  Recommendation: build (b) for the maps, and have `temporal.py` read (b) for scope=basin.
  That keeps the point path a cheap lookup, like HYDE's.

### Storage sketch

```
temporal.tda_layer                   -- registry; one row per atlas/version
  layer_id text PK                   -- 'owda_v1', 'mada_v2', 'lbda_v1', …
  family text                        -- 'tree_ring_drought_atlas' (registry is family-agnostic)
  variable text, season text, resolution_deg real
  year_min int, year_max int, calib_period int4range
  footprint geometry(MultiPolygon,4326)   -- union of valid cells; drives outside_active_domain
  precedence int, citation text, doi text, notes text

temporal.tda_cells
  layer_id text, cell_id int
  geom geometry(Polygon,4326)        -- stored cell envelope (GIST); avoids per-query ST_MakeEnvelope
  first_year int                     -- earliest non-null year
  values real[]                      -- index 1 = tda_layer.year_min (not year 0)
  skill jsonb                        -- {cal_r2, ver_re, ver_ce, nests:[{from, to, r2}, …]}

temporal.tda_basin0{6,8}_series      -- precomputed area-weighted basin series (built like hyde_basin*_steps)
  hybas_id, layer_id, coverage_frac real, values real[]
```

Anchoring arrays at each layer's `year_min` avoids 1,400-element leading NaN runs for the
1400-start atlases. Note that this departs from `lmr_climate`'s year-0 anchoring. Say so in
the loader docstring.

### Catalog, docs and tests

- **Variable catalog.** Add rows in `documentation/EDOPS_variable_catalog_v0.4.tsv`
  (`band=T`, `status=planned` → `implemented`), with `historical_validity` stating the
  per-atlas span. The generated Codebook and API Guide then pick them up
  (`generate_codebook.py`, `generate_api_guide.py`).
- **Data sources.** Add an entry to `docsite/data-sources.md`. The "About EDOPS" ladder
  links to it.
- **Engine contract tests** (`tests/engine/test_engine_contract.py`). Test invariants, not
  values:
  - a Timbuktu buffer gives `outside_active_domain`
  - Kaifeng 965 gives `no_data` if MADA v2 starts after 965 **[verify]**
  - Santa Fe 950 gives `ok` with `coverage == 1.0`
  - every `tda_*` row has a non-empty `caveat` list

---

## 4. Payload sketch (scope=basin)

Scope=basin Band T is a compact per-basin time series, so atlases sit beside the existing
LMR series:

```jsonc
"regional_hydroclimate": {
  "status": "ok",                         // ok | outside_active_domain | no_data
  "coverage": ["lbda_v1", "nada_v2a"],     // every layer whose footprint meets this basin
  "preferred": "lbda_v1",
  "layers": [{
    "layer_id": "lbda_v1", "name": "Living Blended Drought Atlas",
    "variable": "PMDI", "season": "JJA", "resolution_deg": 0.5,
    "coverage_frac": 1.0, "n_cells": 3,
    "series": [{"year": 900, "value": -1.21}, …],
    "summary": {"mean": …, "min": …, "max": …,
                "dry_years_lt_minus3": 11, "longest_dry_run": 7,
                "pctile_vs_own_record": 38},
    "skill": {"reliable_from": 1150, "span_cal_r2": 0.46},
    "agreement_with_lmr": {"r": 0.31, "n": 101},
    "caveat": ["tda_season"]
  }]
}
```

Two derived fields are the real value added:

- **`pctile_vs_own_record`** ranks the span mean within the cell's (or basin's) full
  record. This is the atlas analogue of the 850–1850 re-baselining the Sandbox already
  applies to LMR (`_LMR_BASELINE` in `routes_sandbox.py`). It answers "was this span dry
  *for this place*?" without pretending PDSI, scPDSI and PMDI share units.
- **`agreement_with_lmr`** is the correlation between the atlas series and the LMR series
  over the same span and place. It is empirical input to the held CHAR question on LMR
  proxy bias (F11.x). EDA already documents the Samalas signal as sharp at Central Europe and
  blurred at Kaifeng. Where a dense-network atlas and LMR disagree, that disagreement is a
  finding to show, not an error to suppress.

---

## 5. Surface presentation

### Sandbox — Settlements

The five current examples make an unusually good teaching set **[all verify]**:

| Example | Span | Atlas | What it demonstrates |
|---|---|---|---|
| Santa Fe | 900–1000 | LBDA (0.5°), NADA | Showcase: dense Southwest chronology network; Ancestral Puebloan context. Two overlapping atlases, so `preferred` and `tda_overlap` are visible. |
| San Francisco | 1825–1875 | LBDA, NADA | Late span, high skill; the atlas and the instrumental era meet. |
| Tbilisi | 1150–1250 | OWDA edge (~45°E) or none | Edge case: `coverage_frac` < 1 in a buffer, or nearest cells empty. |
| Kaifeng | 965–990 | MADA v2 footprint, before its ~1000 start | Inside the footprint but before the record: `no_data`, the most instructive null. |
| Timbuktu | 1475–1525 | none | `outside_active_domain`: "no regional drought atlas covers this place; LMR only." |

In the Band T panel:

- **Coverage line.** One sentence above the charts, e.g. "Regional record: Living Blended
  Drought Atlas · 0.5° · JJA PMDI · 3 cells", or the honest null.
- **PDSI chart.** The atlas is the primary series and LMR PDSI a thin secondary line, with a
  legend stating season and source. A shared axis is defensible for PDSI-family indices; the
  labels must still prevent reading them as one measurement.
- **Skill shading.** Hatch years before `reliable_from`, with a tooltip giving the nest r².
  This matches the Sandbox's existing LMR 700 CE quality floor (`actual_from`), made
  per-cell.
- **eVolv2k markers on the same timeline.** A volcanic summer set against *summer* soil
  moisture is the juxtaposition the atlases newly make meaningful.
- **Map.** A `/tda/values` endpoint shaped like `/lmr/values` (flat `{"lat,lon": value}`
  over the span) lets the existing cell-choropleth code draw 0.5° atlas cells under the
  basin outline. That shows the aggregation rather than describing it; it matters most at
  L8, where one cell is larger than the basin.

### Sandbox — Polities

This is the strongest research use. A Cliopatria slice runs through `scope=area`, so polity
queries get atlas coverage from the engine block in §3 at no extra cost. Examples:

- Northern Song: MADA
- Byzantine and Ottoman slices: OWDA
- Aztec and colonial New Spain: MXDA, from 1400

`coverage` then reports what share of the polity the atlas actually sees.

### Explorer

- **Global tab: a regional-specializations overlay.** Atlas footprints outlined, overlaps
  visible. It answers "where does EDOPS know more?" at a glance, and is the honest
  counterpart to LMR's proxy-bias note. One small footprints GeoJSON, gitignored and rsynced
  like `lmr_notches.geojson`.
- **Band T accordion: a "Drought atlases" entry.** An L6/L8 basin choropleth from
  `tda_basin0{6,8}_series`, served through the flat values pattern (the settled PMTiles +
  values-API architecture, not GeoJSON). Periods follow the existing LMR notches (Early /
  MCA / Trans. / LIA / Indust.). Outside the footprints stays neutral grey: the global map
  visibly becomes a patchwork, and that is the point. Color: dry = red, wet = blue, the same
  `t` convention as LMR PDSI.
- **Regions tab: a natural home.** Five of the six regions sit inside atlas domains:
  - Mediterranean & N. Africa, Southwest Asia: OWDA
  - East Asia, South Asia: MADA
  - Mesoamerica: MXDA
  - Pacific Northwest: LBDA

  A synchronized six-panel view of, say, 1630–1645 shows the late-Ming drought (MADA)
  beside the same years in OWDA and LBDA. Regional drought synchrony is a well-studied use
  of the combined atlases (Baek et al. 2017).

### Workbench — African Regions

There is no gridded tree-ring atlas for sub-Saharan Africa; only OWDA's North African margin
touches the tab's domain. The footprint overlay makes that gap explicit, which is useful in
itself for the kind of audience the tab was built for (Braga).

---

## 6. Methodological issues

1. **Season.**
   - The atlases are warm-season; LMR is annual mean.
   - Southern-hemisphere year labelling (DJF 1600/01) needs checking per atlas.
   - Mediterranean winter-rain regimes are only partly captured by summer PDSI.
2. **Variable drift.** PDSI, scPDSI and PMDI are related but not identical. The percentile
   framing (§4) avoids unit pretence.
3. **Built-in spatial autocorrelation.** PPR search radii and ERDA-style smoothing make
   neighbouring cells share predictors. Any ESDA/LISA on atlas-derived basin values inherits
   that dependence.
4. **Variance loss back in time.** Early nests under-state extremes, so "longest dry run" is
   a lower bound in early spans.
5. **Tree-ring network bias.** Networks favour mid-latitude, montane, moisture-limited sites;
   lowland irrigated basins may be poorly sampled even inside a footprint. `coverage_frac`
   measures grid coverage, not proxy proximity. A per-cell "distance to nearest chronology"
   is a worthwhile extra field if the releases include chronology locations.
6. **Overlap disagreement.** NADA vs. LBDA vs. MXDA, and OWDA vs. ERDA (ERDA's authors report
   higher skill where the two overlap). Precedence is an editorial decision and should be
   documented as one.
7. **Environmental determinism (Phase 4).** Annual, local drought series make polity × megadrought
   juxtapositions very tempting in the Workbench and Cliopatria contexts. EDOPS should make them
   possible and well-documented. It should not frame them causally, consistent with the
   Workbench's "necessary-not-sufficient" stance.

---

## 7. Suggested work orders (a REGIONAL phase)

| WO | Scope |
|---|---|
| 0 | **Inspect.** Download OWDA, MADA v2 and LBDA; run `drought_atlas_inspect.py`. Confirm variable names, time encoding, NaN convention, skill files, and first year at the five example cells. Findings go in `wo0_findings.md`. |
| 1 | **Registry + loader.** `temporal.tda_layer`, `temporal.tda_cells`; load the three atlases (mirror `load_temporal.py`: batched inserts, `real[]`). |
| 2 | **Engine block.** Add a `tda` block to `aggregate_band_t`, plus caveat keys, `_weighted_histogram` unit type, and contract tests. `scope=buffer`/`area` are then live. |
| 3 | **Basin series.** Build `tda_basin0{6,8}_series` (notebook, like HYDE's). Read it from `temporal.py` for `scope=basin`. Add catalog rows, then regenerate the Codebook and API Guide. |
| 4 | **Sandbox.** Coverage line, two-series PDSI chart with skill hatching, `/tda/values` cell choropleth. |
| 5 | **Explorer.** Footprint overlay, Band T atlas choropleth, Regions-tab synchrony view. |
| 6 | **Breadth.** MXDA, ERDA, ANZDA, SADA. Evaluate PHYDA as a seasonal global floor. |

Nothing touches `/signature`'s public contract until WO3. The new block appears as
additional Band T rows or keys, so it is additive for existing clients.

---

## 8. Open questions for Karl

1. **Placement.** Inside Band T (as sketched, since atlases are temporal), or a distinct
   `specializations` block that makes the global/regional asymmetry explicit in the schema?
2. **Precedence.** Newest-and-finest wins, or best skill at this cell wins? The second is
   more defensible but harder to explain.
3. **PHYDA.** Evaluate now as a seasonal global drought floor alongside LMR?
4. **Held CHAR questions.** Does the LMR-agreement metric belong with the LMR proxy-bias
   disclosure question held for expert review?
5. **Registry scope.** Tree-ring atlases only, or design `tda_layer` → `regional_layer`
   from the start so documentary and other syntheses can join?

---

### Sources (search results; primary pages were blocked in-session)

- NOAA/WDS OWDA — https://www.ncei.noaa.gov/access/metadata/landing-page/bin/iso?id=noaa-recon-19419
- Cook et al. 2015, Sci. Adv. — https://www.science.org/doi/10.1126/sciadv.1500561
- NOAA/WDS MADA — https://www.ncei.noaa.gov/access/metadata/landing-page/bin/iso?id=noaa-recon-10435
- NOAA/WDS LBDA — https://www.ncei.noaa.gov/access/metadata/landing-page/bin/iso?id=noaa-recon-19119 · LBDA v2 — id=noaa-recon-22454
- NOAA/WDS NADA v2a — https://www.ncei.noaa.gov/access/paleo-search/study/6319
- NOAA/WDS MXDA — https://www.ncei.noaa.gov/access/metadata/landing-page/bin/iso?id=noaa-recon-20353
- NOAA/WDS ANZDA — https://www.ncei.noaa.gov/access/metadata/landing-page/bin/iso?id=noaa-recon-20245
- NOAA/WDS SADA — https://www.ncei.noaa.gov/access/metadata/landing-page/bin/iso?id=noaa-recon-30612
- Cook et al. 2020, ERDA, Clim. Dyn. — https://link.springer.com/article/10.1007/s00382-019-05115-2
- Steiger et al. 2018, PHYDA, Sci. Data — https://www.nature.com/articles/sdata201886
- Tree-Ring Drought Atlas Portal, BAMS 2021 — https://journals.ametsoc.org/view/journals/bams/102/10/BAMS-D-20-0142.1.xml
- Baek et al. 2017, J. Climate — https://journals.ametsoc.org/view/journals/clim/30/18/jcli-d-16-0766.1.xml
