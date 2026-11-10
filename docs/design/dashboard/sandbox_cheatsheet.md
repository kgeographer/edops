# Sandbox cheat sheet

Last verified against v0.4.2 (`a673660`; in `dashboard` since the merge `3156342`), 2026-10-29, after the WO-01 reconciliation pass and the v0.4.2 housekeeping pass. Function and symbol names cited were checked against this tree; `file:line` citations were not all re-counted and may be off by a few lines where v0.4.2 edited the file (`sandbox.html`, `engine.py`, `routes_sandbox.py`, `routes_common.py`, `climate_classes.py`). **Draft complete: contents, at-a-glance, glossary and sections 0 to 9. Reconciled against the docs and the app as of v0.4.2; awaiting Opus's consistency pass.**

**Changes in v0.4.2 (2026-10-29)**: the app changed under this document and it was brought back into line. Band checkboxes now filter A–E rows (2.1). Empty values name their cause: *not present here*, *largely absent*, *no data*, "no single percentile…", and an italic *(low coverage)* (2.6, 4.2, 4.7). Buffer and polity headings name the place, radius and BCE years (4.1, 5.5). `from_year > to_year` is a 422 (5.5). Year inputs run to 2025 (5.5). The HYDE map follows the signature's epoch rule (6.4, 6.6). Atlas: zero-precipitation basins are Arid, so L6 paints 16,397 (6.3). A query that resolves to no basins is a 404, not a 500 (7.1). `/api/area` was removed (7.4). Status vocabulary is settled at five values (2.6). The Sandbox falls back to a modern basemap if the AWMC tiles are unreachable (6.4). Defects table (7.2) updated to fixed or decided.

**Changes in the 2026-10-27 reconciliation pass** (code was authoritative; docs errors were logged in `main_changes_log.md`, not fixed here): 4.2 now has the full state-to-display table (a single-basin `outside_active_domain` or `no_data` row shows "—"); 4.7.9 and 4.8 note that Analysis, Seasonality, Context and Similarity are headed "Containing basin for {place}"; 4.2 and 2.7: histogram ends are the minimum and maximum of the member-basin percentiles, not p10/p90; 2.9 (new) maps catalog variable counts to what each payload returns; 5.3 gives the HYDE cadence as non-overlapping ranges and states the LMR reference period (Tardif et al. 2019, 850-1850 CE simulation mean; the map layer re-centres on its own 850-1850 mean); 5.5 adds the year convention (signed years, labels use no year zero) and the 2023 input cap; 4 intro and 7.1.4: Polities shows Map, Signature and Atlas; 6.3: the Atlas omits 59 zero-precipitation L6 basins; 9 (new) lists every fixed interpretive threshold; 8: example 05 uses the polity's whole span, not one slice.

Verification status: every function, constant and test cited was checked to exist (re-checked 2026-10-29); line numbers were checked on 2026-10-27 and may have drifted since (see the note above); live figures come from the local server. Not verified: (1) that upstream (`*_upstream`) variables are aggregated like any other (inferred from the dispatch rule, section 3.1); (2) payload size for very long Band T spans (section 5.3, by construction, not run). Checked since: the BCE polity heading in a browser with the Qin example (2026-10-28), and the public `/api/signature` for `from_year > to_year`, which returns a 422 (2026-10-29). Symbol names are the stable reference.
Tags: `[code]` read in source · `[doc]` from docs · `[inferred]` not directly verified.
`[doc …]` tags name pages of the EDOPS documentation site; a PDF of that site will accompany this file. The cheat sheet is written to stand on its own where that is cheap, and points to the docs for concepts and rationale.
Scope: what the Sandbox UI offers, does and produces. Workbench excluded.

## Contents

Each section can be read on its own; the "Assumes" line under each heading says what else it leans on. Terms are defined once, in the glossary below.

| § | Title | What it answers |
|---|---|---|
| 0 | Parameter space | Which calls the Sandbox makes, with which parameters, and what comes back |
| 1 | Query types | What a user can ask for (single basin, ring, buffer, polity), what each resolves to and what the signature then describes |
| 2 | Signature structure | The bands, the fields on every row, the aggregation methods, the percentile, and every reason a value can be missing |
| 3 | Aggregation by scope | What is area-weighted, dominant-basin or not areal, scope by scope, and how Band T differs |
| 4 | What the UI shows | Exactly what the Signature, Analysis and Seasonality tabs render, and which computed fields are never surfaced |
| 5 | Date handling | What a date does and does not select; Band T coverage by source |
| 6 | Other results | Context, Similarity, Atlas, the map and choropleth layers, and every companion endpoint |
| 7 | Gaps and quirks | What would surprise a newcomer; open defects and decisions; what exists in code but is unreachable or deliberately absent |
| 8 | Captured examples | Nine real, trimmed responses (JSON files supplied alongside this document) |
| 9 | Fixed interpretive thresholds | Every fixed cutoff that changes what the UI shows or says, with location and whether the user can set it |

## At a glance

**The four queries** (Settlements tab: first resolve a place; Polities tab: pick a polity and time slice)

| Query | Resolves to | Signature tab shows | Other tabs describe |
|---|---|---|---|
| Single basin | the basin containing the point | that basin's value and global percentile per variable | that basin |
| Basin ring | the same basin plus its first-order neighbours | the **centre basin only**; each neighbour only after being selected; **no ring-level summary** | the centre, or the selected neighbour |
| Buffer (radius 1 to 2000 km, default 100) | basins intersecting the circle, weighted by their share of it | a **distribution** over those basins (percentile, spread badge, histogram) | **only the basin containing the point** |
| Polity at a date | basins intersecting the slice polygon, weighted by their share of it | a distribution over those basins | nothing: the other tabs are hidden |

**The bands.** A–E are undated and return 52 rows at L6 (A physiographic 8, B hydro-climatic 18, C bioclimatic 15, D Anthropocene 8, E coastality 3). T (temporal) is the only band a date selects: HYDE land use, LMR paleoclimate, eVolv2k volcanic events, computed on the query's own geometry, with no percentile.

**Why a number can be missing** (six states, each named on screen; details in §2.6):
1. **By design:** categoricals and flags have no percentile (they show a class label or a fraction).
2. **Score suppressed:** the member basins form two separate populations, so one number would mislead. The row says "no single percentile: the area has two distinct groups of values".
3. **Outside active range:** the variable is about zero across the area. One basin shows *not present here*; several basins show *largely absent* (under 10% of the area has any).
4. **Not areal:** river discharge for a polity is withheld; the row says "river-network measure, not defined for an area".
5. **No data:** nothing to aggregate; shown as *no data*.
6. **Low coverage:** a categorical row where under half of the area has data shows its value followed by an italic *(low coverage)*.

**Three numbers worth knowing.** The percentile ranks a basin against **all basins on Earth at the same level** (L6 or L8). Multi-basin rows show a percentile but **no native-unit value**; a single basin shows both. `n_units` counts the basins that had data **for that variable**, so it varies by row.

**Dates.** Two inputs only: the polity **resolver year** (picks the boundary) and the **Band T span**. Neither changes A–E. Not gating bands by date is deliberate.

**Defects.** The four bugs found in the 2026-10-26 reading (band checkboxes, buffer heading, reversed date span, HYDE map epoch rule) were fixed in v0.4.2, along with the polity heading, the dash wording and the no-basin 500s. What remains are design questions, not defects: §7.2 items 11 to 13.

**Companion files.** The nine JSON examples listed in §8, supplied alongside this document. Code citations name `sandbox.html`, `engine.py`, `routes_sandbox.py` and `routes_common.py` as provenance; those files are not supplied.

## Terms

- **Basin**: a BasinATLAS sub-basin polygon. **Level (L6 / L8)**: scale; L6 has 16,397 basins averaging about 8,232 km², L8 has 190,675 averaging about 708 km².
- **Signature**: all the environmental variables for one query, grouped into **bands**. **Row**: one variable's result in a signature.
- **Scope**: how the query's area is defined (single basin, ring, buffer, polity). **Member set**: the basins the scope resolves to.
- **Method**: how a variable is aggregated over the member set (`area_weighted`, `dominant_basin`, `class_mixture`, `flag_fraction`, `distribution_only`; §2.4).
- **Percentile**: a basin's rank, 0 to 100, among all basins at that level (§2.5). **Coherence**: a badge saying whether the member basins agree (`concentrated`, `spread`, `split`; categoricals `concentrated` or `mixed`).
- **Local / upstream**: a variable measured on the basin itself, or on everything draining into it (`*_upstream`).
- **Band T span**: the years entered for Band T. **Resolver year**: the year that selects a polity's boundary.
- **Persistence bands**: the grouping idea behind A–E: properties that persist over long periods, which is why bands are not gated by date.

## 0. Parameter space

*Assumes: the glossary only.*

### 0.1 What a signature query calls
- **`/api/areas`** (internal GUI dispatcher) carries the main signature. Scopes the Sandbox sends: `single_basin | buffer | polity`. (`basin_ring` exists on the route and in the engine but the Sandbox never sends it; the ring is assembled client-side, see section 1.) [code routes_sandbox.py:areas; sandbox.html:buildSingleBasinUrl, buildBufferUrl, polity branch ~926]
- **`/api/signature?scope=basin&bands=ABCE`** (public) is the second request fired by "Get signature" on the Settlements tab, alongside the main `/api/areas` call. It targets the basin containing the query point, whatever the scope (single, ring, buffer). It populates the **Analysis** and **Seasonality** tabs, which need raw values. [code sandbox.html ~3004; comments at 3002, 3075; `renderAnalysis`/`renderSeasonality` at 2926-2927; `_pointSig` not yet traced to the fetch]
  - The Sandbox hardcodes `bands=ABCE` on this call whatever boxes are ticked, so it never carries Band T. This is the Sandbox's choice: the API accepts T, and its default is `ABCDE`.
  - It fires again with the clicked member's coordinates when a ring member is selected. [code sandbox.html ~2891]
  - Never fired on the Polities tab: the polity handler fetches only `/api/areas?scope=polity`, and the Analysis, Seasonality, Context and Similarity tabs are hidden there. [code sandbox.html comment ~3987, `_setPolitiesTabVisibility`]
- `/api/areas` returns scores, not raw values; the raw values come from this call. [code comment sandbox.html:3002]
- Companion calls (maps, context, similarity, basin-ring geometry) are section 6.

### 0.2 UI control → request
| UI | Request |
|---|---|
| Settlements tab, scope "Single basin" | `/api/areas?scope=single_basin&lat&lon&level&bands&detail=true[&from_year&to_year][&place_links]` |
| Settlements tab, scope "Basin ring" | The same `single_basin` request for the centre basin, plus `/api/basin/ring?lat&lon&level` (geometry and neighbour coordinates only, no signature). Clicking a ring member sends another `single_basin` request at that member's `neighbor_lat/lon`. [code sandbox.html:~3045, commitRingMember:2859; routes_sandbox.py:basin_ring_geom] |
| Settlements tab, scope "Buffer" | `/api/areas?scope=buffer&lat&lon&level&radius_km&bands&detail=true[&from_year&to_year]` |
| Polities tab | `/api/areas?scope=polity&polity&year&level&bands&detail=true[&from_year&to_year]` |

`bands` comes from the band checkboxes; `from_year`/`to_year` are sent only when T is checked. User-initiated "Get signature" calls are tagged `src=ui` and carry `place_name`; background calls are `src=ui_aux`. [code sandbox.html:_qlog]

### 0.3 Parameters (as the Sandbox uses them)
| Param | Used by | Notes |
|---|---|---|
| `scope` | all | `single_basin`, `buffer`, `polity` (the UI's "Basin ring" also sends `single_basin`; see 0.2) |
| `lat`,`lon` | single_basin, buffer | from the resolved place; range-validated |
| `radius_km` | buffer | required |
| `polity`,`year` | polity | `year` is the **resolver year** (selects the boundary); exact name; 404 with `available_periods` if the polity isn't active that year |
| `level` | all | 6 or 8, else 400 |
| `bands` | all | letters from A–E and T |
| `from_year`,`to_year` | when T in bands | Band T span; **independent of the resolver `year`**; both required, else 422 |
| `detail` | all (always `true`) | adds per-variable histogram/distribution objects |
| `place_links` | single_basin, ring centre, public basin call | gazetteer identifiers echoed back, not validated |

### 0.4 Validity rules (as hit by the Sandbox)
- `level ∉ {6,8}` → 400. Missing scope params → 422. [code routes_sandbox.py:areas]
- Band T needs both `from_year` and `to_year` → 422; there is no single-year restriction on `/api/areas`. [code routes_sandbox.py:1528]
- Polity not active at `year` → 404 with the polity's available periods. [code routes_sandbox.py:1582]
- Public basin call: no basin at the point → 404. [code routes_common.py:379]

### 0.5 Response envelopes
| Call | Shape |
|---|---|
| `/api/areas` (all scopes) | `rows[]` (one per variable) + `scope{}` (fields vary by scope) + `bands` + `temporal` + `caveats` + `shortfall`; polity adds `resolver{}`, `member_ids`, `band_t_span`; single_basin/ring add `place_links` if sent [code routes_sandbox.py:areas; engine.py:assemble_payload] |
| `/api/signature` basin | basin identity/geometry + `signature_bands{A..E}.items[{key,label,value}]` + `meta` [code routes_common.py:signature] |

### 0.6 Not yet covered
What each scope's signature *describes* (esp. the ring), row fields, the charts and tables, the companion calls: sections 1, 2, 4, 6.

### Open questions for Karl (section 0)
- None open. (`src` is not a parameter of either route: a logging middleware reads it from the query string, defaulting to `api`, and does not log `src=ui_aux`. [code app/query_log.py:install])

---

## 1. Query types

*Assumes: §0 for the endpoints named.*

Two tabs, four things a user can ask for. Each: what the user does → what is resolved → what the signature describes.
Common to all Settlements queries: the user first **resolves a place** (below), which unlocks the scope, level and band controls.

### 1.0 Resolving a place (Settlements tab)
- Input box accepts a place name (+ optional ", Country"), a prefixed gazetteer ID (`wd:`, `pl:`, `gn:`, `tgn:`, `whg:`), or `lat, lon`. A name returns a candidate list to pick from. [code sandbox.html:~80-98]
- Or "Load an example" (5 places: Timbuktu, Kaifeng, Tbilisi, Santa Fe, San Francisco). An example sets scope = single, level = 6, ticks Band T and fills its year span. [code sandbox.html:123-127, 2492-2530]
- The result is one point (`currentLat/currentLon`) plus a place name; everything below is computed from that **point**, never from the place's own extent.
- Defaults after resolve: scope **Single basin**, level **06**, bands **A–E ticked, T off** (except examples). Level is disabled until a place is resolved. [code sandbox.html:132-200, 2524]

### 1.1 Single basin  (Settlements, scope "Single basin")
- **Resolves to:** the one basin (at the chosen level) whose polygon contains the point. Weight 1.0, shortfall 0. [code engine.py:resolve_single_basin, single_basin_signature]
- **Signature describes:** that basin only (n_units = 1). Rows carry the basin's own raw value and global percentile; the multi-basin dispersion badge and histogram do not apply. [code engine.py:single_basin_signature; sandbox.html:renderSingleBasinContinuousLeaf]
- Band T, if ticked, is computed over the basin polygon for the user-entered year span. [code engine.py:single_basin_signature docstring]
- At L08 the page also fetches the ring neighbours, for choropleth context only. [code sandbox.html:~3012-3040]

### 1.2 Basin ring  (Settlements, scope "Basin ring")
- **Resolves to:** the centre basin (as 1.1) **plus** its first-order adjacent basins (those that touch it), with each neighbour's shared border length, area and bearing. [code engine.py:resolve_basin_ring; routes_sandbox.py:basin_ring_geom]
- **Signature describes:** on "Get signature", the **centre basin's single-basin signature**, exactly as 1.1. **There is no aggregate across the ring.** The neighbours are a comparison set: clicking a neighbour (map or glyph) only **previews** it (a highlight and a popup with a "Get signature" link); following that link replaces the Signature, Analysis, Seasonality, Context and Similarity content with that neighbour's own single-basin signature. Clicking the centre dot restores the centre immediately (its payload is cached). [code sandbox.html:~3045-3060, commitRingMember:2859, renderCenterSig:2919; engine.py:basin_ring_signature docstring "no meaningful aggregate across the ring"]
- A ring glyph shows neighbours by bearing. [code sandbox.html:_renderRingGlyph, `#v3-ring-info`]
- Neighbour lookup point is `ST_PointOnSurface` of the neighbour, so it resolves back to that same basin. [code engine.py:resolve_basin_ring]

### 1.3 Buffer  (Settlements, scope "Buffer")
- **User sets:** radius in km, default 100, clamped to 1–2000 on Enter or blur. [code sandbox.html:145, _applyRadius:1090]
- **Resolves to:** a geodesic circle of that radius around the point, and every basin (at the level) that intersects it. Weight = share of the **circle's** area lying in that basin; slivers under 0.1% of the circle are dropped. Shortfall = 1 − Σ weights (circle area not covered by any basin, e.g. open water). [code engine.py:resolve_buffer, areal_signature]
- **Signature describes:** a **distribution over the member basins**, area-weighted (headline percentile, concentrated/spread/split badge, histogram), not a single place's value. `scope` returns `member_ids` and `n_units`. [code engine.py:areal_signature; sandbox.html:renderLeaf]
- Band T, if ticked, is computed for the buffer over the entered year span. [code engine.py:areal_signature]

### 1.4 Polity at a date  (Polities tab)
- **User does:** searches Cliopatria/Seshat polities by name (or loads one of 8 examples); a polity has several **time slices** (one boundary per slice). A slider and VCR buttons (first, prev, play, next) step through them; the map shows the slice boundary. Level and bands as before (A–E and T all ticked once a polity is chosen). [code sandbox.html:238-355, selectPolity:3645, initSliceControl]
- **Two independent dates:**
  - **Resolver year** (`year`): picks which boundary. Always the current slice's `fromyear`: the slider snaps to the nearest slice and no caller passes another year. [code sandbox.html:applySlice:3806, slider handlers 3909-3920]
  - **Band T span** (`from_year`/`to_year`): **not user-editable on this tab**; the year row is hidden and filled with the slice's own `fromyear`–`toyear`. [code sandbox.html:applySlice:3811, comment 3669]
- **Resolves to:** the slice polygon, and every basin intersecting it. Weight = share of the **polity's** area in that basin; nothing dropped (epsilon 0). At L08 a pre-built crosswalk table is used instead of a live intersection, with a live fallback for island/oceanic polities. [code engine.py:resolve_polygon, resolve_crosswalk, areal_signature_polygon]
- **Signature describes:** a distribution over the member basins, as in 1.3, plus `scope.marginal_exposure` {lt_50pct, lt_20pct}: the weight carried by basins less than 50% / 20% inside the polity (edge basins). `resolver{}` echoes polity name, id, slice span and year. [code engine.py:areal_signature_polygon; routes_sandbox.py:areas polity branch]
- Stepping the slice re-runs a background polity request to refresh member basins and the choropleth; the Signature tab itself updates only on "Get signature". [code sandbox.html:_silentResig:917, applySlice:3808]
- Polities earlier than 700 CE have no LMR coverage; the UI flags this. [code sandbox.html:selectPolity:3655]

### 1.5 Behaviour common to all
- Changing **scope** or **buffer radius** clears the right-hand results ("run Get signature to populate"). Changing **level** after a signature has been fetched only re-draws the basin geometry and choropleth at the new level (and refreshes Context/Similarity if visible); the Signature tab is not recomputed. A signature at the new level needs another **Get signature** click (Karl, confirmed). [code sandbox.html:1075, _applyRadius:1090, _onLevelChange:878]
- Switching between the Settlements and Polities tabs hard-resets the other. [code sandbox.html:~4003]
- Selecting a scope draws a geometry preview on the map before any signature is requested. [code sandbox.html:_drawScopePreview:1028]

### Open questions for Karl (section 1)
- None open. (`scope=basin_ring` on `/api/areas` stays, unused by the Sandbox, for the dashboard: decided by Karl, 2026-10-28.)

---

## 2. Signature structure

*Assumes: the glossary only.*

Verified live (local server) on Timbuktu 16.8167, −2.9833, L6, `bands=ABCDE&detail=true`: `single_basin` and `buffer` r=100 km both return **52 rows**. Row counts below are from that run; they change with level and with the catalog.

### 2.1 Bands
| Band | UI label | Rows (L6) | Source |
|---|---|---|---|
| A | Physiographic bedrock: elevation, slope, relief, lithology, karst | 8 | BasinATLAS |
| B | Hydro-climatic baselines: discharge, runoff, groundwater, soils, wetlands (full upstream catchment) | 18 | BasinATLAS |
| C | Bioclimatic proxies: temperature, precipitation, aridity, biome, ecoregion (contemporary baseline) | 15 | BasinATLAS |
| D | Anthropocene markers: population, cropland, human footprint (present-day only) | 8 | BasinATLAS |
| E | Coastality: distance to sink, endorheic flag, outlet type | 3 | BasinATLAS |
| T | Temporal context: HYDE 3.4 land use, LMR v2.1 climate reconstruction, eVolv2k volcanic forcing. Needs a year span | separate | see 2.4, section 5 |

[code sandbox.html:204-209 (labels), `BAND_LABELS`; catalog `documentation/EDOPS_variable_catalog_v0.4.tsv`; live counts]
- The Signature tab groups rows **only by band** (accordion, default-open band is T if present, else C). The catalog's finer `dimension` (elevation, discharge, …) is not used for grouping. Within a band, order is engine block order (B1, B2, B3, B4, B5), not alphabetical or by dimension. [code sandbox.html:renderSignature:3374-3410; engine.py:_areal_signature_from_basin_set `basin_rows = b1+b2+b3+b4+b5`]
- Only catalog rows with `status = implemented` are emitted; `planned` rows (26 in A–E, per the catalog) never appear. `gdp_avg`, `human_dev_idx`, `river_area_upstream`, `strata_code` and the multi-column `pnv_shares` are excluded. [code engine.py:load_catalog, `_SKIP_API_KEYS`, `_B1_EXCLUDE`]
- **The A–E checkboxes filter the rows.** `bands=A` returns the 8 Band A rows (checked live); an unticked band's rows are dropped, and `bands=None` keeps all. Fixed in v0.4.2, in the engine, so it also holds for the public `/api/signature` `scope=buffer` and `scope=area`. [code engine.py:_areal_signature_from_basin_set; live `bands=A` test]

### 2.2 Local vs upstream pairing
- The catalog gives each variable up to two API keys: `api_key_s` (the basin itself, "local") and `api_key_u` (everything draining into it, "upstream"). Upstream keys end `_upstream`; the display name gets " (upstream)". Many variables have only one. [code engine.py:load_catalog `_emit`; live names: `aridity`/`aridity_upstream`, `pct_clay`/`pct_clay_upstream`, …]
- If a variable has an upstream column but no local one, the upstream column is used under the local key. [code engine.py:load_catalog ~476-480]
- The pair is two independent rows; nothing links them in the payload except the name suffix.

### 2.3 Row fields (every row, `make_row`)
| Field | Meaning |
|---|---|
| `variable`, `friendly_name`, `db_col` | key, display name, raw DB column |
| `band`, `method`, `unit_type`, `n_units` | band; aggregation method (2.4); what is aggregated (`basin`, `hyde_cell`, `lmr_cell`, `global`); count of units |
| `representative_score` | global percentile 0–100 (2.5), or null |
| `representative_raw` | native-unit value (number, or the class label for class_mixture), or null |
| `units` | native unit label |
| `score_suppressed` | true only when the score is null because B6 found two separate populations |
| `status` | see 2.6 |
| `coverage` | share of the query's weight that had data |
| `coherence` | `concentrated` / `spread` / `split` (continuous), `concentrated` / `mixed` (categorical), else null |
| `modality` | `unimodal` / `two_regime` / null (B6) |
| `weight_at_zero` | share of weight at percentile 0 (zero-inflated variables) |
| `caveat` | list of caveat keys; texts once at top level in `caveats` |
| `year`, `epoch_year` | Band T rows only |
| `detail` | method-specific sub-block; present only with `detail=true` (the Sandbox always sends it) |
[code engine.py:make_row, project_row]

Payload top level: `scope`, `shortfall`, `bands`, `temporal`, `caveats`, `rows`. Caveat keys: `lmr_caveat`, `hyde_caveat`, `hyde_nearest_year`. [code engine.py:assemble_payload, CAVEAT_TEXTS]

### 2.4 Methods: how a variable is aggregated
Routing is by the catalog's `kind` and `typology_cluster`: categorical → B3; flag → B4; continuous with cluster `continental-gradient | scale-dependent | local-anomaly` → B1; `network-topology` → B2; continuous with no cluster → B5. [code engine.py:dispatch_variable, `_BLOCK1_CLUSTERS`]

| `method` | Block | Variables (Timbuktu L6) | Score | Raw | Coherence | Detail keys |
|---|---|---|---|---|---|---|
| `area_weighted` | B1 | 35 continuous (aridity, elevation, soils, wetlands, cropland …) | area-weighted mean of member basins' percentiles | null for multi-basin; present for one basin | concentrated / spread / split | `core_share, window_lo/hi, iqr, p10/p25/p75/p90, spread, unit, distribution{bins, weights, min, max, mean, n_units, …}` |
| `dominant_basin` | B2 | 3 discharge (`discharge_yr/max/min`) | percentile of the **one basin with the highest annual discharge** in the set | that basin's value | null | `dominant_hybas_id` |
| `class_mixture` | B3 (+ `outlet_type` from B4) | 10 categorical (biome, zone, ecoregions, land cover, lithology, wetland class, outlet type …) | **none** (no percentile) | modal class label | concentrated if modal share ≥ 0.85, else mixed | `mixture[{class_id, class_label, weight}], modal_class_id, modal_share, n_classes, concentration` |
| `flag_fraction` | B4 | `coast_fraction` | none | area-weighted fraction of basins flagged coastal | null | none |
| `distribution_only` | B5 | 3 untyped continuous (`temp_max`, `temp_min`, `reservoir_vol`) | as area_weighted | null for multi-basin | as area_weighted | as area_weighted, plus `regimes, suppressed_score` when suppressed |
| `extreme` | B5 | none (the set is empty) | n/a | n/a | n/a | never emitted today |
| `grid_areal_distribution`, `global_forcing` | B7 / Band T | HYDE, LMR, eVolv2k | n/a (Band T has no global percentile) | yes | n/a | section 5 |

[code engine.py:aggregate_b1…b5, aggregate_band_t; live `method` counts: area_weighted 35, class_mixture 10, distribution_only 3, dominant_basin 3, flag_fraction 1]
- **B6 modality** is a post-pass on B1 and B5 rows: tags `unimodal` / `two_regime`; for a two-regime row the single score is nulled and `score_suppressed = true`. Live buffer: 13 rows `two_regime`, 13 suppressed. [code engine.py:apply_modality; live]
- **B6 is deliberately skipped for polities** (`run_modality=False`; payload carries `modality_post_pass: "skipped — not calibrated for polygon scale"`, pinned by `test_modality_post_pass_skipped`), so polity rows have `modality` null and no suppression. [code engine.py:2781-2784; tests/engine/test_engine_contract.py:715] See section 3.
- **B2 on a polity:** status `not_areal`, no score or raw ("discharge isn't an area-representative quantity"). [code engine.py:_mark_b2_not_areal, `_B2_NOT_AREAL_SCOPES`]

### 2.5 The percentile (what `representative_score` is)
- Each basin's value is ranked against **every basin in the world at the same level** (L6 ranks against L6 basins, L8 against L8), as `PERCENT_RANK() × 100`. Nodata (`-9999`/NULL) basins are excluded from the ranking so they don't compress it. [code engine.py:rank_expr, two_pass_sql]
- Per-variable variants from the catalog's `position_method`: `percentile` (plain rank), `log_percentile` (rank of ln(1 + x); catalog assigns it to discharge, surface water, moisture balance, human presence, water management), `rarity_rank` (categoricals), `dominance_class`, `class_mixture`, `flag_fraction`. [code engine.py:_val_expr; catalog `position_method`]
- **Zero-aware variant:** when a variable is zero in ≥ 20% of basins, exact zeros get percentile 0 and the remaining positive values are ranked among themselves, so the zeros don't flatten the scale. [code engine.py:rank_expr `zero_fraction_threshold=0.20`]
- For a set of basins the headline is the **area-weighted mean of the member basins' percentiles**. The reference set is still the global one, not the buffer or polity. [code engine.py:aggregate_b1; doc docsite/sandbox/reading-a-signature.md:49]
- The Sandbox UI says "percentile" and the help text says "global percentile"; neither names the level. The docs page does. [code sandbox.html:434; doc reading-a-signature.md:32]

### 2.6 Status values and empty cells
Status vocabulary: five values, `ok`, `outside_active_domain`, `no_data`, `low_coverage` (categorical) and `not_areal` (B2, polity), all listed in the `make_row` docstring since v0.4.2. [code engine.py:make_row, aggregate_b3, _mark_b2_not_areal]

Observed combinations, Timbuktu L6 (counts are rows):

| Method | status | score | raw | suppressed | Buffer r=100 | Single basin | Meaning |
|---|---|---|---|---|---|---|---|
| area_weighted | ok | yes | no | no | 20 | — | normal multi-basin row |
| area_weighted | ok | yes | yes | no | — | 31 | normal one-basin row |
| area_weighted | ok | **no** | no | **yes** | 12 | 0 | two separate populations; one number withheld |
| area_weighted | outside_active_domain | no | no | no | 3 | 4 | variable ≈ zero across ≥ 90% of the area (karst, permafrost, cropland …); percentile would mislead |
| distribution_only | ok | yes/no | no | yes/no | 2 + 1 suppressed | 3 | as area_weighted |
| dominant_basin | ok | yes | yes | no | 3 | 3 | the dominant basin's values |
| class_mixture | ok | no (by design) | label | no | 10 | 10 | categorical has no percentile |
| flag_fraction | ok | no (by design) | fraction | no | 1 | 1 | |

[live `/api/areas`; code engine.py:aggregate_b1 `outside_active_domain` guard (zero-fraction ≥ threshold and weight-at-zero ≥ 0.90)]
- A number can be missing for **six** reasons: four non-ok statuses, `outside_active_domain`, `no_data`, `not_areal` and `low_coverage` (the last still carries a value), plus two that carry status `ok`: by design (categorical or flag, no percentile) and suppressed (`score_suppressed`, two regimes). The status vocabulary is the five values `ok`, `outside_active_domain`, `no_data`, `low_coverage` and `not_areal`; `score_suppressed` is a separate flag. Band T has no percentile at all.

Statuses not seen in the Timbuktu runs above:

| status | when | example |
|---|---|---|
| `no_data` | nothing to aggregate for the variable across the area | `slope_avg`, `slope_upstream`, `stream_gradient`, Greenland 300 km (72.0, −40.0) |
| `low_coverage` | a categorical row where under half of the query area has a valid class (coverage below 0.50) | `wetland_class`, Greenland 300 km (coverage 0.01); a 150 km buffer at 43.0, 51.0 on the Caspian shore (coverage about 0.25, nine rows) |
| `not_areal` | B2 river discharge on a polity: not an area-representative quantity | any polity signature |
- How each shows on screen (the cause of an empty cell is named; a bare "—" is the exception) is section 4.

### 2.7 Coherence and modality definitions
- **Continuous (B1/B5):** `core_share` = the largest share of weight falling inside any window ±15 percentile points wide on the global axis. `concentrated` if ≥ 0.65; `split` if a single tied score holds ≥ 50% of the weight **and** ≥ 10% sits outside the core window; otherwise `spread`. The 0.65 cutoff is provisional. [code engine.py:classify_dispersion, `_CORE_SHARE_*`, `_SPLIT_*`]
- **Fewer than 5 basins:** coherence is cleared (core share is pinned near 1.0 at small n). **One basin:** coherence cleared and raw value back-filled. [code engine.py:`_MIN_COHERENT_BASINS`, _suppress_low_n_coherence, _backfill_single_basin_raw]
- **Categorical (B3):** `concentrated` if the modal class holds ≥ 85% of weight, else `mixed`. [code engine.py:aggregate_b3, `plurality_threshold=0.85`]
- **The badge does not read the p10-p90 span.** A row can span 33 percentile points (min to max) and still be `concentrated` if enough weight sits in one ±15-point window (e.g. Pct Clay, Timbuktu buffer, 18.6 to 51.5).

### 2.8 Scope fields that qualify every row
`shortfall` (share of the query area with no basin, e.g. open water), `scope.n_units`, and for polities `scope.marginal_exposure`. Per-scope detail in section 1; aggregation by scope in section 3.

### 2.9 How the catalog's variable counts map to what a payload returns
The docs use "variables" for several different counts. Measured 2026-10-27 at Timbuktu, L6, bands A-E, against `documentation/EDOPS_variable_catalog_v0.4.tsv` (parsed with `csv`; line 94 has an extra field).

| Count | Number | Notes |
|---|---|---|
| Catalog rows | 102 | 74 implemented, 28 planned. Band T has 13 implemented, 1 planned, plus 1 planned "output" row. This is the "around 100 variables" in the docs. |
| Catalog A-E | 87 | 61 implemented (A 9, B 14, C 26, D 7, E 5) and 26 planned. Local and upstream versions share one entry, so the 61 entries have 75 keys. |
| Public `/api/signature?scope=basin&bands=ABCDE` | 66 variables | A 11, B 20, C 22, D 10, E 3 |
| Sandbox Signature tab (`/api/areas`) | 52 rows | local and upstream counted as separate rows (A 8, B 18, C 15, D 8, E 3) |

Where the 61 implemented A-E entries appear:

| Where | Entries | Which |
|---|---|---|
| Signature tab, all keys | 38 | most of A-E |
| Signature tab, local only | 1 | `river_area` (upstream excluded by `_B1_EXCLUDE`) |
| Public `/api/signature` only, not in the Signature tab | 17 | Seasonality scalars and monthly arrays (`pre_concentration`, `pre_peak_month`, `tmp_concentration`, `tmp_peak_month`, `seas_phase_offset`, `tmp_seas_amp`, `pre_mm_monthly`, `tmp_dc_monthly`), `endorheic`, `coast_flag`, `ecoregion`, `elev_point`, `relief_range_m`, `relief_position`, `pnv_shares`, `gdp_avg`, `human_dev_idx` |
| In neither payload | 5 | `strata_code` (opaque codes; excluded in B3 via `_B3_EXCLUDE`), `climate_class`, `modality`, `phase`, `pt_corr` (derived at startup) |

- `/api/areas` also emits four rows the public payload does not carry: `zone_name`, `land_cover_name`, `outlet_type`, `coast_fraction`.
- `gdp_avg` and `human_dev_idx` are skipped by the engine (`_SKIP_API_KEYS`) but present in the public payload.
- UI use confirmed: Seasonality shows the six scalars and both monthly arrays; the Similarity result shows `relief_range_m`; the Atlas uses `modality` and `phase`. **UI use not checked:** `elev_point`, `relief_position`, `gdp_avg`, `human_dev_idx`, `ecoregion`, `pnv_shares`, `climate_class`, `pt_corr`.
- The catalog has two entries titled "Outlet type": `endorheic` (the raw flag) and `outlet_type` (the derived class).
[code engine.py:load_catalog, _SKIP_API_KEYS:393, _B1_EXCLUDE:1194, _B3_EXCLUDE:1345; live `/api/signature`]

### Open questions for Karl (section 2)
- None open. (Status vocabulary settled in v0.4.2: five values.)

---

## 3. Aggregation by scope

*Assumes: §1 (the four scopes) and §2.4 (the methods).*

All numbers below are from live runs on Timbuktu (single_basin, buffer r=100 km) and Northern Song 961 CE (polity), L6, `bands=ABCDET`, `detail=true`. Ring members are `single_basin` queries (section 1), so they follow the single_basin column.

### 3.1 Basin-path bands (A–E): one table
| | single_basin (and each ring member) | buffer | polity |
|---|---|---|---|
| Member set | the one containing basin | basins intersecting the circle (9 at Timbuktu) | basins intersecting the slice polygon (156 at Northern Song, L6) |
| Weight | 1.0 | share of the **circle's** area in the basin; slivers < 0.1% dropped | share of the **polity's** area in the basin; none dropped |
| `shortfall` | 0 | 1 − Σ weights (circle area outside any basin) | 1 − Σ weights (0.011 at Northern Song) |
| `n_units` on a row | 1 | basins **with data for that variable** (8 or 9) | basins with data for that variable (134, 154 or 156) |
| Continuous (`area_weighted`, `distribution_only`) | the basin's own percentile **and raw value**; coherence cleared | area-weighted mean of member percentiles; **no raw value** (0 of 35 rows); coherence, histogram | same as buffer |
| Discharge (`dominant_basin`) | the basin itself | the member with the highest annual discharge (`detail.dominant_hybas_id`); its percentile and raw | **`not_areal`**, no number (3 rows) |
| Categorical (`class_mixture`) | that basin's class | area-weighted class shares; modal class label; coherence concentrated (modal ≥ 0.85) or mixed | same as buffer |
| `coast_fraction` (`flag_fraction`) | 0 or 1 | area-weighted fraction of coastal basins | same |
| B6 modality (`two_regime`) | runs, always `unimodal` (38 rows) | runs: 13 `two_regime`, 13 scores suppressed | **skipped by design**: `modality` null on all 52 rows |
| `outside_active_domain` rows | 4 | 3 | 1 |
| Extra payload | `scope.hybas_id` | `scope.member_ids`, `radius_km` | top level: `resolver{}`, `member_ids`, `band_t_span`, `modality_post_pass`; `scope.marginal_exposure` |

[code engine.py:resolve_single_basin / resolve_buffer / resolve_polygon / resolve_crosswalk, aggregate_b1…b5, apply_modality, areal_signature_polygon, _mark_b2_not_areal; live runs]
- **Weights are renormalised per variable** over the member basins that have data for it; `coverage` reports the share of total weight that did. [code engine.py:aggregate_b1 `wts_norm = wts / coverage`]
- **Why raw is missing on multi-basin continuous rows:** native-unit means are not implemented, only the mean percentile. Single basins are back-filled because there is nothing to aggregate. [code engine.py:_backfill_single_basin_raw; deferred register "Native-unit means"]
- **Fewer than 5 basins** (e.g. a small buffer): coherence is cleared on continuous rows. [code engine.py:_suppress_low_n_coherence]
- **Why polity discharge is withheld:** the biggest river touching a boundary is a membership fact, not a regional statistic. Buffers and single basins are point-anchored, so the dominant basin is meaningful. [code engine.py comment at `_B2_NOT_AREAL_SCOPES`]
- **L8 polity:** member basins come from a pre-built crosswalk (weights ≥ 0.0001), with a live intersection as fallback. L6 always intersects live. [code engine.py:areal_signature_polygon]
- **Local vs upstream variables** (`*_upstream`) are aggregated exactly like any other variable in their block; I found nothing that treats the upstream catchment spatially differently. [inferred from dispatch_variable, which routes on `kind`/`typology_cluster` only]

### 3.2 Band T: a different geometry
Band T does **not** use the basin set. It is computed directly on the query's own geometry: the buffer circle, the single basin's polygon, or the polity polygon. [code engine.py:aggregate_band_t `geom_wkt` vs lat/lon/radius_km]

| Source | Rows | Aggregation over the footprint | Notes |
|---|---|---|---|
| HYDE 3.4 (`hyde_cropland`, `hyde_grazing`, `hyde_pasture`, `hyde_rangeland`) | one per variable per HYDE epoch inside the span (1 epoch → 4 rows in all three runs) | **overlap-weighted sum** of cell areas in km² (an extensive quantity); distribution of per-cell values in `detail` | If no epoch falls in the span, the **nearest** epoch is used and tagged `hyde_nearest_year`; 1950 is tagged `hyde_caveat` |
| LMR v2.1 (`lmr_pdsi`, `lmr_air`, `lmr_prate`) | one per variable per **year** in the span (51 years → 153 rows; 67 → 201) | area-weighted mean over 2°×2° footprints intersecting the area; footprint count in `n_units` | CE 0–1998 only; every row carries `lmr_caveat`; absent for BCE spans |
| eVolv2k (`evolv2k_vssi`) | one per volcanic event year in the span (7 and 8 in these runs) | none: a global forcing series, not spatial (`unit_type = global`) | −491 to 1890 CE |

- No percentile or score for any Band T row (`representative_score` is null, not suppressed). [code engine.py:aggregate_band_t]
- Row count scales with span length (164 rows for a 51-year span on one basin, 213 for 67 years on a polity). [live]
- The Band T span is user-entered on Settlements and is the slice span on Polities (section 1). [code sandbox.html]
- Public-API limit (Band T single year for buffer/area) does not apply to `/api/areas`; the Sandbox is not restricted. See section 0.

### 3.3 What changes the answer for the same place
- Same point, `single_basin` vs `buffer`: the point's own basin vs a distribution over a circle; only the first has raw values and the position track.
- Same polity, different slice: different boundary, different member basins, different Band T span.
- Level 6 vs 8: different basin set and a different percentile reference set (section 2.5).

### Open questions for Karl (section 3)
- None new. (Polity B6 skip is intentional; the earlier log row was withdrawn.)

---

## 4. What the Sandbox shows, and where it collapses information

*Assumes: §2.3 to §2.6 (row fields, methods, empty states) and §1.*

Scope of this section: the **Signature**, **Analysis** and **Seasonality** tabs, plus the ring glyph. Context, Similarity, Atlas, the map and choropleth layers are section 6.
Which tabs exist: Settlements shows Map, Signature, Analysis, Seasonality, Context, Similarity and Atlas. **Polities shows Map, Signature and Atlas**; the four single-basin tabs (Analysis, Seasonality, Context, Similarity) are hidden. The Atlas is global and is not tied to a query. [code sandbox.html:_setPolitiesTabVisibility]

### 4.1 Signature tab: frame
- Heading depends on the query. Single basin: "Containing basin for *place* (Level 06)". Ring member: "Ring basin #N for *place* (Level 06)". Buffer: "*place*, *R* km buffer" with an italic "*N basins at Level 06*" ("*R* km buffer" when there is no place name). Polity: "*Name* (*from* – *to*)" with an italic "*N basins at Level 06*"; the years are BCE-aware ("750 BCE – 222 BCE"). [code sandbox.html:renderSignature]
- One accordion section per band present in the rows (A–E, T), headed "Band X — *label*" with a row-count badge. Band T opens by default when present, otherwise C. [code sandbox.html:3374-3410]
- Each row: variable name, raw DB column in parentheses, optional "as of *year* CE" (polity resolver year), then the value cell. The name is `humanizeKey(variable)` (underscores to spaces, title case), **not** the payload's `friendly_name`. [code sandbox.html:renderRow:3414, humanizeKey:998]
- A "How to read this" link opens the docs page. [code sandbox.html:3383]

### 4.2 Signature tab: what each row type shows
All of this is `renderLeaf`. Text in quotes is the literal UI text. [code sandbox.html:renderLeaf:3460, widgets 3111-3185]

| Method / state | Shown | Chart |
|---|---|---|
| `area_weighted` / `distribution_only`, **one basin**, ok | "*raw* *units* · *N.N* percentile" | percentile track: a dot on a plain 0-100 line (90 px) |
| same, one basin, `outside_active_domain` | *not present here* (italic) | none |
| same, one basin, `no_data` | *no data* (italic) | none |
| `area_weighted`, several basins, score present | "*N.N* percentile" + badge **concentrated** (green) / **spread** (amber) / **split** (blue); no badge for other coherence values | histogram (160 × 36 px) of member-basin percentiles; the two axis ends are labelled with the **minimum and maximum** of those percentiles (not p10/p90); the pale band is the ±15-point core window [code sandbox.html:renderHistogram:3141, engine.py:_weighted_histogram] |
| `area_weighted`, several, `outside_active_domain` | *largely absent* (italic; tooltip "Under 10% of this area has any") + the histogram if the payload has one | histogram |
| `area_weighted`, several, score suppressed (two regimes) | "—" + "no single percentile: the area has two distinct groups of values" under the histogram | histogram |
| `area_weighted`, several, `no_data` or any other null score | *no data* for `no_data`; "—" for any other null score | empty histogram |
| `distribution_only`, several basins | "*N.N* percentile" (omitted if suppressed) + "no single percentile: the area has two distinct groups of values" when suppressed | **range bar**: p10-p90 span with both end values (unlike the histogram, whose ends are min and max); dark ticks mark each regime when suppressed |
| `dominant_basin`, ok | "*raw* *units* · *N.N* percentile" + "basin *id*" (hidden for one basin) | none |
| `dominant_basin`, `no_data` | *no data* | none |
| `dominant_basin`, `not_areal` (polity) | "river-network measure, not defined for an area" | none |
| `class_mixture`, ok | the modal class label | **modal-share bar**: one filled bar labelled with the modal share as a percent |
| `class_mixture`, `no_data` | *no data* | empty bar |
| `class_mixture`, `low_coverage` | the modal class label followed by an italic *(low coverage)* (tooltip "Under half of this area has data") | modal-share bar |
| `flag_fraction` | "*N.N*%", or the empty-cause text if null | none |
| any other `method` | "[*method*]" (fallback) | none; `extreme` is handled but never emitted |

- The cause is stated on screen (v0.4.2): `outside_active_domain` reads *not present here* (one basin) or *largely absent* (several), `no_data` reads *no data*. A bare "—" remains only for a null score with no status cause. The wording comes from one helper, `emptyCause`. See 2.6 for the payload side. [code sandbox.html:emptyCause, renderLeaf]

### 4.3 Band T display
[code sandbox.html:renderTBand:3225, renderTimeMarginal:3194, wireTSliders:3311]
- **LMR climate** (header "LMR climate — *N* cells · *from–to* CE"): for each of PDSI, temperature anomaly and precipitation, a histogram of footprint values for the **middle year**, a **Year slider** that swaps the histogram to any year in the span, and a small **time series** (mean line with a p10–p90 band, min/max and first/last year labelled).
- **HYDE land use:** a table, rows Cropland / Grazing / Pasture / Rangeland, one column per epoch ("~" prefix and a footnote when the epoch is the nearest one rather than inside the span); values are km² sums.
- **eVolv2k volcanic events:** a table of year and VSSI (Tg S). Events ≥ 5 Tg S are shown; a "show all N" link reveals the rest. If none reach 5, all are shown.
- Band T rows never show a percentile.

### 4.4 Analysis tab (Settlements only)
Built from the **public `/api/signature` basin response** (`bands=ABCE`), so it describes **the one basin containing the query point (or the selected ring member), whatever the scope**. For a buffer it does not describe the buffer. [code sandbox.html:renderAnalysis:2283, parallel fetch ~3004]
- *Basin context* table: upstream catchment area (km²), distance to ocean outlet (km), and a drainage badge: **Endorheic**, **Coastal terminal**, or **Exorheic interior**.
- *Local–upstream divergence* table: precipitation, moisture index (P/PET) and temperature, each as local value, upstream value and a ratio (colour-coded by distance from 1×).
- *Water provenance* classification with a one-sentence note: **Endorheic**, **Coastal terminal**, **Exogenous water supply** (upstream precipitation or moisture > 1.5× local), **Undetermined** (small catchment: upstream area < 500 km² at L6, < 5000 km² at L8), **Catchment-uniform**, or **Local-dominant**.
- A level note: the local/upstream contrast is most informative at L06.

### 4.5 Seasonality tab (Settlements only)
Also from the public basin response, with the same single-basin basis. [code sandbox.html:renderSeasonality:1432]
- **Walter-Lieth chart**: 12 precipitation bars (mm, left axis) with a temperature line (°C, right axis).
- **Polar chart**: the same 12 months as radial precipitation sectors with a temperature ring.
- A **generated sentence** built from fixed thresholds on three derived indices: precipitation concentration (< 0.15 year-round, < 0.35 moderately seasonal, < 0.60 clearly seasonal, else strongly concentrated); precip–temp phase offset (> 3.5 months "Mediterranean-type anti-phase", < 1.5 "monsoon and continental", else moderate); temperature amplitude (< 10 °C tropical/oceanic, < 18 moderate, else continental/high-latitude). [code sandbox.html:1537-1553]
- A **scalar table**: precip concentration, precip peak month, temp concentration, temp peak month, phase offset, temperature amplitude.
- Subtitle "L0*N* basin · monthly climatology (BasinATLAS)". Nothing renders if the monthly arrays are missing.

### 4.6 Ring glyph
A 112 px circle with a dot per neighbour placed by `border_bearing` (north up) and numbered **clockwise from north**, plus a centre dot; the selected dot turns orange; tooltip "Ring *n* · ~*deg*°". Shared border length and neighbour area are in the payload but not shown. [code sandbox.html:_renderRingGlyph, `#v3-ring-info`; routes_sandbox.py:basin_ring_geom]

### 4.7 Where information is collapsed or never shown
Payload fields the Sandbox does not display anywhere (grep of `sandbox.html`): `shortfall`, `coverage`, `weight_at_zero`, `modality` (only its effect, via suppression), `scope.marginal_exposure`, `friendly_name`, `iqr`/`p25`/`p75`/`spread`, `core_share` (only the window is drawn), `band_t_span`, and **the caveat texts** (`lmr_caveat`, `hyde_caveat`). The only caveat handled is the nearest-epoch footnote, with hard-coded wording.

Display collapses:
1. **The cause of an empty cell is named, with one exception.** *not present here*, *largely absent*, *no data*, "no single percentile…" and *(low coverage)* are stated; a bare "—" appears only for a null score with no status cause. What the UI still does not say is *why* coverage is low (section 4 open questions). (Status causes: section 2.6.)
2. **Class mixtures show only the leading class**: the label and a modal-share bar. The full class list (`mixture`), `n_classes` and the `mixed` coherence tag are not shown.
3. **Categorical rows have no coherence badge**, though the engine tags them concentrated / mixed.
4. **No percentile context in the row.** It says "*N.N* percentile" with no level and no statement of what it is ranked against, and no ordinal ("11th") in this tab, though the Context table uses one. [code sandbox.html:2102]
5. **Multi-basin continuous rows show no native-unit value** because the engine does not compute one (section 3).
6. **Histogram axes** carry only the low and high values: no title, no y-axis, no on-chart explanation of the shaded window.
7. **Shortfall and coverage are silent**: a buffer over open water, or a polity with 1% outside the basin layer, looks the same as a complete one.
8. **The polity heading omits the resolver year** (it appears per row only when the row carries one).
9. **Analysis and Seasonality ignore the scope**: they always describe the single containing basin. They are labelled: Analysis, Seasonality, Context and Similarity each carry a "Containing basin for {place}" heading ("Ring basin #N for {place}" once a ring member is selected). The Signature tab's buffer heading, by contrast, names the place and radius ("*place*, *R* km buffer"); see 4.1 and 4.8. [code sandbox.html:_basinTitleHtml, used by renderAnalysis, renderSeasonality, renderContext, renderConjunction]

### 4.8 Single-basin instruments vs multi-basin queries (a gap, stated plainly)
Several outputs are built for **one basin**. Only the Signature tab has a way to summarise a **set** of basins, and only for buffer and polity. [code sandbox.html:renderLeaf, renderAnalysis, renderSeasonality; engine.py:basin_ring_signature]

| Scope | Signature tab | Analysis (local vs upstream) | Seasonality |
|---|---|---|---|
| Single basin | the basin's values | that basin | that basin |
| Basin ring | the **centre** basin's values; each neighbour's values only after selecting it; **no summary of the ring as a set** | centre, or the selected neighbour | centre, or the selected neighbour |
| Buffer | distribution over the member basins (percentile, badge, histogram) | **the one basin containing the point, not the buffer** | **the one basin containing the point, not the buffer** |
| Polity | distribution over the member basins | not available (tab hidden) | not available (tab hidden) |

- The four single-basin tabs (Analysis, Seasonality, Context, Similarity) are headed "Containing basin for {place}" (or "Ring basin #N for {place}"), so the UI does say they describe one basin, whatever the scope.
- Nothing in the code summarises a *small set* of basins for local-vs-upstream divergence or seasonality. The ring is where this shows most, since its signature is a comparison set with no set-level statement (engine docstring: "no meaningful aggregate across the ring").
- Karl's notes (2026-10-26): the buffer is an arbitrary bound whose meaning is unclear and may be retired. How to summarise a small set of basins (ring, and any buffer that stays) is an open question for the dashboard, not a v0.4.x fix.

### Open questions for Karl (section 4)
- None open. (Buffer heading: fixed in v0.4.2. Analysis/Seasonality single-basin basis: recorded as a gap in 4.8.)
- **Explaining partial coverage (dashboard).** `low_coverage` (class-mixture rows) fires when under half of the query area has a valid class value. Two causes, neither surfaced: (1) part of the area is in no basin, i.e. open water or ground outside the dataset (Rome 200 km: 50% sea, 9 of 52 rows; Caspian shore 150 km at 43.0, 51.0: 75% outside, coverage about 0.25); (2) basins in the area with NoData for that variable, e.g. ice sheets (Greenland 300 km: shortfall 0, `wetland_class` coverage 0.01, three slope variables `no_data`). The Sandbox shows only *(low coverage)* with the tooltip "Under half of this area has data" (Karl, 2026-10-28: leave the reader to work out why). The payload has what a fuller explanation needs: per-row `coverage` and the response's `shortfall`. How, or whether, to say why is a design question for the dashboard; a prose generator could use both.

---

## 5. Date handling

*Assumes: §1.4 (polity dates) and §3.2 (Band T).*

Verified live (local server, Rome 41.7, 12.5, `single_basin`, L6) plus the database. Short version: **a date selects only Band T rows. Bands A–E are the same whatever date you ask for, and nothing in the payload or the Signature tab flags that.**

### 5.1 Two date inputs
| Input | Where it exists | What it does |
|---|---|---|
| `year` (resolver year) | polity queries only | picks which Cliopatria boundary is used (section 1.4). The engine otherwise only **stamps** it on histograms (`resolver_year`), which the UI prints as "as of *year* CE" under the row name. It changes no values. [code engine.py:253, 1068, 1145, 2142; sandbox.html:renderRow] |
| `from_year`, `to_year` (Band T span) | any query with T ticked | selects the Band T rows (5.3). Nothing else reads them. [code engine.py:_areal_signature_from_basin_set `run_t`] |

A–E rows take no date input. A point query has no resolver year at all.

### 5.2 Bands A–E are undated; the catalog says which are valid when
- Every A–E value is a contemporary or fixed dataset. They are returned identically for any `from_year`/`to_year`/`year`. [code engine.py:attach_values; live: same 52 A–E rows for 300 BCE, 1500 BCE and 2000 CE spans]
- The variable catalog carries a per-variable **`historical_validity`** flag. Counts for implemented A–E variables: **A** full-record 9; **B** full-record 5, pre-1500 valid 9; **C** pre-1500 valid 25, modern-only 1; **D** modern-only 7; **E** full-record 5. [catalog `documentation/EDOPS_variable_catalog_v0.4.tsv`, column `historical_validity`]
- **That flag is not used by the engine or the Sandbox.** The only code that touches it lists it among the catalog columns exposed to the Explorer API. [code routes_common.py:457; grep of `app/`, `scripts/edop/areas/`, `sandbox.html`]
- **No date-based gating of bands exists, by design.** Bands reflect "persistence" (long-lived properties of a place), so the system deliberately does not restrict band selection by the entered date range (Karl, 2026-10-26). An "admissibility rule" that would do so was an idea floated in design discussion and is not implemented or planned; nothing in the code or docs matches it (grepped for "admissib").

### 5.3 Band T: what a span selects
| Source | Covers | Cadence | What a span returns |
|---|---|---|---|
| HYDE 3.4 | −10000 to 2025 CE (128 steps) | millennial −10000 to −1000 (10 steps); centennial 0 to 1700 (18); decadal 1710 to 1950 (25); annual 1951 to 2025 (75) | all epochs inside the span, 4 rows each. **If none falls inside, the single nearest epoch to the span's midpoint**, tagged `hyde_nearest_year` |
| LMR v2.1 | 0 to 1998 CE (arrays hold 2001 values; the engine clamps to 0–1998; the API parameter text also says 0–1998 but does not validate it) | annual | one row per year per variable (PDSI, air, precipitation); **none** if the span is entirely before 0 or after 1998; partial overlap is clipped |
| eVolv2k v4 | −491 to 1890 CE (256 events) | event years only | one row per eruption year inside the span; none if no events |

[code engine.py:_LMR_RANGE, _EVOLV_RANGE, aggregate_band_t; DB `temporal.hyde_times`, `evolv2k_v4`, `lmr_climate`]

**LMR reference period.** LMR values are anomalies. Per Tardif et al. 2019 (section 2.3) the reanalysis fields are deviations from the mean over the CCSM4 last-millennium simulation, which covers 850 to 1850 CE (not a 20th-century period). The Signature tab's Band T rows show the stored values unchanged. The Polities map layer re-baselines each cell to the mean of the stored values over 850 to 1850 CE. Measured 2026-10-27: that mean is not exactly zero. For air temperature it averages about -0.21 K across the 16,380 cells (range -1.8 to +0.3 K); for PDSI about +0.02; for precipitation rate about -0.014 mm/day (range roughly -0.36 to +0.47). For the Timbuktu cell and 1475-1525 CE, the table shows -0.17 K and the map -0.02 K. So the two displays are close for most cells but not identical, and nothing on screen says which baseline applies. [code engine.py:aggregate_band_t, routes_sandbox.py:lmr_values, `_LMR_BASELINE`; Tardif et al. 2019, Clim. Past 15, 1251]

Live examples:
| Span | HYDE | LMR | eVolv2k |
|---|---|---|---|
| 300–200 BCE | 1 row set at **0 CE** (nearest; 200+ yr away), `hyde_nearest_year` | none | 7 events |
| 1500–1400 BCE | 1 row set at **−1000** (nearest; 400+ yr away), `hyde_nearest_year` | none | none |
| 1475–1525 CE | 1500 | 51 years | 7 events |
| 1990–2010 CE | 21 annual epochs | 9 years (1990–1998) | none |

- A span that has no HYDE epoch always gets one anyway, so HYDE rows are never empty. The Signature tab marks it with "~" before the epoch year and the footnote "nearest available HYDE epoch; no step falls within this span." It does **not** say how far away that epoch is. [code sandbox.html:renderTBand:3262-3280]
- The 1950 HYDE epoch carries `hyde_caveat` (cadence changes there); LMR rows carry `lmr_caveat`. Their texts are in the payload; the UI does not show them (section 4.7).
- Row count grows with span length. LMR is 3 rows per year, so a 2000-year span is about 6000 LMR rows. Not tested at that size. [inferred from aggregate_band_t]

### 5.4 What is excluded or superseded
**Nothing is, in the data returned.** For a 300 BCE query the Signature tab still shows, unflagged:
- Band C contemporary climate and ecoregions, beside the Band T paleoclimate;
- Band D modern-only variables (population density, cropland and pasture extent, human footprint, reservoir volume).

The only date guidance a user gets is static text in the band legend: C "contemporary baseline; Band T supersedes for period-specific queries"; D "present-day only — exclude for pre-modern analyses". [code sandbox.html:204-209]

The public `/api/signature` basin scope does add a `_note` to Bands C and D when `from_year < 0` ("these values describe present-day conditions…"). The Sandbox never sees it: its parallel call sends no `from_year`, and `/api/areas` has no such note. [code routes_common.py:409; sandbox.html:3005]

### 5.5 How the UI sets dates
- **Settlements:** tick T, then type From and To (numeric, −10000 to 2025, free entry; the visible inputs carry the tooltip "Years CE; negative = BCE"). The five examples prefill 25–100-year spans. **`from > to` is rejected**: `/api/areas` and the public `/api/signature` return a 422, "Band T: from_year must not be after to_year" (only when T is requested; equal years are valid), and the Sandbox shows it as "Error: …" (v0.4.2). [code routes_sandbox.py:areas, routes_common.py:signature; sandbox.html]
- **Polities:** no date entry. The slider and VCR step through the polity's time slices; resolver year = the slice start, Band T span = the slice's own `fromyear`–`toyear` (section 1.4). Slider, slice list and map overlay labels are BCE-aware ("750 BCE – 222 BCE"); the Signature tab heading is too since v0.4.2 (`formatYear`). [code sandbox.html:formatYear, renderSignature]
- **Wording to be aware of:** the Polities tab shows "The LMR map layer starts at 700 CE; this polity predates it. The Signature tab still reports LMR from 0 CE." and disables the LMR **choropleth** variables. That 700 CE floor is the map layer's (`/api/lmr/values`), not the signature's: signature LMR rows exist from 0 CE. [code routes_sandbox.py:lmr_values; sandbox.html:selectPolity]

- **Year convention.** Years are signed integers throughout; negative means BCE; the inputs say so (tooltip). Labels (`formatYear`) use no year zero (−44 shows as 44 BCE); the docs (`caveats.md`) say HYDE and eVolv2k use astronomical numbering, a one-year difference that is immaterial for these datasets and is stated there. [code sandbox.html:formatYear, year inputs]

| Where | What it uses |
|---|---|
| From / To inputs (Settlements) | signed integers, passed to the API unchanged; the visible Settlements inputs carry the tooltip "Years CE; negative = BCE" |
| Polity slice years | Cliopatria `fromyear` / `toyear`, signed integers, passed unchanged as the Band T span (Cliopatria's numbering was not checked) |
| Slider, map overlay, slice dropdown | `formatYear`: -N shows as "N BCE", 0 as "0 CE" |
| Polity Signature heading | `formatYear`, like the slider and overlay (e.g. "750 BCE – 222 BCE"); fixed in v0.4.2 (7.2 item 5) |
| Docs (`caveats.md`) | HYDE and eVolv2k use astronomical numbering (year 0 = 1 BCE, -1 = 2 BCE) |

  The labels count -1 as 1 BCE while the dataset convention counts it as 2 BCE: a one-year disagreement that nothing on screen reconciles. `caveats.md` calls this immaterial for annually resolved reconstructions.

### 5.6 Gaps, as stated facts
- Variable-level historical validity is recorded in the catalog but not applied anywhere a user can see it. (Not applying it as a gate is deliberate; surfacing it as information is a separate, open question.)
- A dated query returns the same A–E block as an undated one; only the Band T accordion changes.
- The Signature tab does not say how far a "nearest" HYDE epoch is from the requested span.

### Open questions for Karl (section 5)
- None open. (Admissibility gating: deliberately not done. `from > to`: fixed in v0.4.2, a 422.)

---

## 6. Other results of a signature call: Context, Similarity, Atlas, and the map

*Assumes: §1; independent of §2 to §5.*

Everything below is produced by the Sandbox but is **not** the signature. Settlements shows all of it; Polities shows only the map layers and polity boundary (Context, Similarity and Analysis/Seasonality tabs are hidden there, section 4). Live shapes were captured for Timbuktu, L6. [code sandbox.html; routes_sandbox.py]

### 6.1 Context tab (Settlements only)
"Where does this basin sit, globally and regionally?" Seven fixed variables, each reported independently, never combined into a score. [code sandbox.html:renderContext:1982; routes_sandbox.py:context:323]
- **Trigger:** opening the tab after Get signature, then again whenever the radius, level or selected ring member changes. The basin described is the **active** one (the containing basin, or the selected ring neighbour), not the buffer. [code sandbox.html:1983-1996]
- **Controls:** "Within" radius, 250 / 500 (default) / 1000 / 2500 km; **2500 is unavailable at L8** (render budget). [code sandbox.html:848, routes_sandbox.py:313-336]
- **Table (7 rows):** variable and its value, "vs. all basins" and "vs. within *R* km", each an **ordinal percentile** (e.g. "98th"). Variables: mean annual precipitation (mm/yr), mean annual temperature (°C), seasonal temperature range (°C), mean elevation (m), mean slope (°), aridity index (P/PET ×100), annual runoff (mm/yr). Timbuktu: temperature 98th globally, 43rd within 500 km; elevation 39th globally, 5th within 500 km. [live `/api/context`]
- **Map (420 px):** every basin within the radius, filled by the variable chosen by **clicking a table row** (a sequential ramp per variable), the query basin outlined dark, a marker at the point, hover tooltip with the value, and a min–max legend bar. Count line: "*N* surrounding basins within *R* km". [code sandbox.html:_repaintContextMap:2224; live `/api/context/population`: 109 basins at 500 km]
- **Generated paragraph** (left column, "Regional context"), rule-based: always opens with "This describes the Level *N* basin *place* sits in, not *place* itself" (ring neighbours get their own sentence). Then a sentence only for a variable that is (1) at a **regional** extreme (radius percentile ≤ 15 or ≥ 85) but not a global one: "The basin is *drier/colder/…* than *N*% of basins within *R* km", adding "though close to the global median" when the global percentile is 25–75; (2) at a **global** extreme (≤ 10 or ≥ 90): "*Label* is in the top/bottom 10% worldwide"; or (3) neither, but global and regional percentiles differ by ≥ 25: "*Label* is unremarkable globally but *wetter/…* for its region". Otherwise "Nothing here stands out — the basin looks broadly typical…". [code sandbox.html:_buildContextBlurb:2153-2220, thresholds 2144-2151]
- **Not shown:** the individual neighbours' values (only on the map by hover), anything for a buffer or polity.

### 6.2 Similarity tab (Settlements only)
"Which other basins match this one?", as a **membership test, not a ranking**: a basin is in the set only if it clears **every** threshold of the chosen lens. An empty set is a valid answer. [code sandbox.html:renderConjunction:1666, blurb 465-478; routes_sandbox.py:similarity/conjunction]
- **Lenses (4):** Precipitation (shape, magnitude, amplitude), Temperature (level, range), Climate = precipitation + temperature (5 conditions), Terrain (elevation, relief range). [live `/api/similarity/conjunction/lenses`; code sandbox.html:823-829]
- **Thresholds**, each a three-way selector with the default marked: precipitation **shape** (monthly-pattern correlation ≥ 0.85 / **0.90** / 0.95), **magnitude** (annual total within a ratio 1.25 / **1.5** / 2.0), **amplitude** (seasonality CV within 0.10 / **0.15** / 0.25), **temperature level** (± 2 / **3** / 4 °C), **temperature range** (± 2 / **4** / 6 °C), **elevation** (± 25 / **50** / 100 m), **relief range** (± 50 / **100** / 200 m). Only the conditions of the active lens are shown. [code sandbox.html:645-716]
- **Output:**
  - A readout: "Your query matches *N* basins under *lens*" plus a reach clause ("all within 400 km", "spanning 10,487 km", or "reaching … km out"); with zero matches, "No basins match … honest scarcity, not an error."
  - A **map (420 px)** painting the matching basins, shaded by shape agreement for the precipitation and climate lenses (light to dark purple above the correlation cutoff) and flat blue for temperature and terrain; unmatched basins are unpainted. The query basin is added back as a perfect match, since the search excludes it from its own candidates. Hover tooltip: place name, country codes, and shape r with annual mm (or elevation and relief for terrain).
  - A footnote saying the result describes the **basin**, not the place; for terrain it adds that this is overall elevation and relief, "not fine-grained ruggedness".
  [code sandbox.html:_cjRenderReadout:1626, _cjRenderLegend:1647, 1684-1850]
- **Timbuktu, defaults, Precipitation lens:** 119 matching basins, reaching 9,307 km from the query (diameter 10,487 km); terrain lens: 252. [live]
- The response carries more detail than the tab shows (per-condition counts, the query basin's values, member coordinates). How the thresholds combine internally is deliberately not described; what the tab offers and shows is described above. [live `/api/similarity/conjunction`]
- The older composite-distance panel was retired; this is the only Similarity panel in the Sandbox. [code sandbox.html:627-628]

### 6.3 Atlas tab (not tied to a place)
A global view, available without any query. The left column's place controls are replaced by an explanatory note. [code sandbox.html:renderAtlas:1926, 486-496]
- **Controls:** a view (4) and a level (L6 / L8).
- **Views:** **Modality** (every basin by how its rainfall is spread: Arid, Even year-round, One wet season, Two wet seasons, Undetermined); **Phase** (when rain falls relative to warmth: Warm-season rain, Cool-season rain, Weak coupling, No temperature cycle); **Two wet seasons** (highlight one class); **One wet season, cool-season rain** (highlight, the Mediterranean-type family).
- **Output:** a world map of basins coloured by class, a legend with basin counts, and a text block with a blurb and the declared conventions ("arid < 100 mm/yr · even year-round cv < 0.2 · no temperature cycle < 5 °C seasonal amplitude · warm/cool-season |precip×temp r| ≥ 0.5"). L6 modality counts: Arid 1,493; Even 1,259; One wet season 12,652; Two wet seasons 899; Undetermined 94 (16,397 basins, all painted). The 59 basins with zero precipitation in all twelve months, which were dropped before v0.4.2, are now classed Arid, with phase "weak coupling". L6 phase: 8,272 / 2,017 / 3,208 / 2,900. [live `/api/explorer/climate-class`; code climate_classes.py:build_level, `pre_total >= 0`]
- Highlight views show the matching count and grey out everything else.

### 6.4 Map tab
One map, shared by Settlements and Polities. [code sandbox.html; doc CLAUDE.md "The sandbox pages"]
- **Base:** AWMC historical terrain basemap, with a fallback: the map starts on the local Protomaps style, probes one AWMC tile after page load, and shows the terrain only if it loads (an unreachable tile server otherwise gives a blank map with no error). A corner note reads "Historical terrain basemap unavailable; showing a modern basemap" while the fallback shows. HydroRIVERS rivers (toggle, on by default); basin outlines (charcoal, white-cased). [code sandbox.html; doc CLAUDE.md]
- **After a place is resolved:** a point marker and a **scope preview** drawn before any signature is requested: the containing basin (single), a dashed geodesic circle plus its member basins (buffer), or the centre basin and its numbered neighbours (ring). Selecting a ring neighbour highlights it and opens a popup. [code sandbox.html:_drawScopePreview:1028]
- **After "Get signature":** the member-basin set is recorded and any selected choropleth is repainted (at L8 the set is what limits the paint, see below). [code sandbox.html:_sigMemberIds, _repaintChoropleth:981-988]
- **Polities:** the slice boundary, a large year overlay (top-left), the slider and VCR (play, step, jump) redraw the boundary per slice. Two extra layer toggles, **Cities (modern)** (27,699 GeoNames places) and **Countries**. [code sandbox.html:541, 3996, _setPolitiesTabVisibility; live `/api/sandbox/cities`]
- **"Render variable" choropleth** (one select in the left column, shared by the Settlements and Polities tabs, shown after the first scope render): paints basins by one variable, independent of the signature rows. **At L6 it paints every basin worldwide; at L8 it paints only the basins in the current signature's member set (plus ring neighbours for the single-basin scope).** This is deliberate (Karl, 2026-10-28: nothing in the Sandbox needs a world paint at L8; the L08 aridity values take about 3.5 s to load for the globe). The member set is derived without the user asking: toggling the level silently re-requests the signature (`_silentResig`, tagged `ui_aux`, not logged) to rebuild it, so the message "Get a signature first to use L08 choropleth" appears only if that request fails. [code sandbox.html:applyBasinVar:4126-4150, 4319-4322]

| Group | Options | Source and rule |
|---|---|---|
| BasinATLAS (modern) | aridity index, annual precipitation, mean annual temperature, cropland extent %, slope | `/api/explorer/values`; flat `{hybas_id: value}` per level, painted from PMTiles; cropland uses a fixed 0–~80% domain |
| Paleoclimate, LMR v2.1 | temperature anomaly, precipitation anomaly | `/api/lmr/values`; 2° grid cells, **anomaly vs the cell's own 850–1850 CE mean of the stored values** (the signature rows use the stored values unchanged; see 5.3), averaged over the Band T span; **spans before 700 CE return nothing** (quality floor) |
| Historical land use, HYDE 3.4 | cropland, grazing, pasture, rangeland fraction | `/api/hyde/values`; per-basin fraction of the basin covered, by the signature's epoch rule (v0.4.2): the first epoch inside the Band T span, else the epoch nearest the span's midpoint (a tie goes to the earlier); with only a `from` year, floor-snapped to the epoch at or before it; **1000 CE** if no Band T year is set |

[code sandbox.html:BASIN_VARS:4078, _repaintChoropleth:4162, applyLMRChoropleth/applyHydeChoropleth; routes_sandbox.py:hyde_values, lmr_values]
- A legend bar with low/high labels (or "dry/wet", "cold/warm", "flat/steep") and a status line ("Loading…", "LMR data begins 700 CE…"). The level selectors are disabled while an LMR or HYDE variable is selected. [code sandbox.html:renderBasinLegend:4162, 4379-4380]

### 6.5 Companion endpoints (all internal, GUI-only)
| Endpoint | Trigger | Returns |
|---|---|---|
| `/api/whg/suggest`, `/api/whg/entity` | typing a place name; pasting an identifier | candidate places; a resolved entity's coordinates |
| `/api/basin-preview` | scope preview at a point | point, containing basin, adjacent basins, rivers (GeoJSON, ~218 KB) |
| `/api/basin/buffer` | buffer preview | member basins as GeoJSON (9 features at 100 km) |
| `/api/basin/ring` | ring scope | centre + neighbour geometry, bearings, interior points (section 1.2) |
| `/api/basin/geom`, `/api/basin-geom` (POST) | drawing member basins | geometry by `hybas_id` list |
| `/api/context`, `/api/context/population` | Context tab | 7 rows with percentiles; all basins in the radius with their 7 values (18 KB, 109 basins at 500 km) |
| `/api/similarity/conjunction` (+ `/lenses`) | Similarity tab | member set, per-condition counts, attrition, spatial reach, query values |
| `/api/explorer/climate-class` | Atlas | categories with counts and colours, plus `{hybas_id: class}` for the level (~280 KB) |
| `/api/explorer/values`, `/api/hyde/values`, `/api/lmr/values` | choropleth | flat value dicts (330 KB for one L6 variable) |
| `/api/polity/search`, `/slices`, `/geom` | Polities tab | name matches with slice counts; the slices (id, years, area, geometry hash); a slice boundary |
| `/api/sandbox/cities`, `/api/sandbox/countries` | Polities layer toggles | 27,699 cities as compact arrays (1.6 MB); country polygons |

[live captures; routes_sandbox.py, routes_common.py] (`/api/narrative` and `/api/similar` exist but `sandbox.html` does not call them.)

### 6.6 Quirks specific to this section
- **One epoch rule for HYDE** (v0.4.2): the map layer and the Band T signature now use the same rule (first epoch inside the span, else nearest the span's midpoint), so the same years show the same epoch in the table and on the map. [code routes_sandbox.py:hyde_values; engine.py:aggregate_band_t]
- **The HYDE map default.** With no Band T year entered it paints **1000 CE** regardless of the query (kept by decision, Karl 2026-10-28). [code sandbox.html:hydeMapYears]
- **LMR floors differ:** map 700 CE, signature rows from 0 CE (section 5.5).
- **Context and Similarity describe one basin.** For a buffer they follow the containing basin of the point; for a ring they follow the selected neighbour; for a polity they do not exist. (Same gap as 4.8.)
- **Several tabs share one slow path:** the choropleth, Context, Similarity and Atlas each fetch their own per-basin dictionaries (tens to hundreds of KB) on demand; switching level re-fetches them. [live sizes above; code sandbox.html]

### Open questions for Karl (section 6)
- **L8 choropleth limited to the signature's basins.** Decided (Karl, 2026-10-28): kept.
- **Atlas** is Explorer-adjacent and not part of the Sandbox signature story. The dashboard is expected to carry that material as an option, tab or alternate screen (Karl, 2026-10-26), so it is documented here but not treated as a signature output.

---

## 7. Known gaps and quirks

*Assumes: nothing; each item names the section that explains it.*

Consolidated from sections 0 to 6. Items 7.1 are things that would surprise a newcomer reading the UI or the API. Items 7.2 are defects and open questions, with their status as of 2026-10-26. 7.3 notes two patterns across them. 7.4 lists what exists in the code but is unreachable, or is deliberately absent. The `main` fixes are also tracked in `main_changes_log.md` (a separate file, not part of this cheat sheet).

### 7.1 What would surprise a newcomer
1. **The Sandbox's main call is not the public API.** It uses an internal dispatcher, `/api/areas`, and adds a second, public `/api/signature?scope=basin&bands=ABCE` call per query whose only job is to feed the Analysis and Seasonality tabs. (0.1)
2. **"Basin ring" returns one basin's signature.** The centre basin only; neighbours are previewed on the map and glyph and each has its own single-basin signature if selected. There is no signature of the ring as a set. (1.2)
3. **The same point can be queried as three different things** (single basin, ring, buffer) and the Signature tab, Analysis, Seasonality, Context and Similarity do not all follow the choice. Only the Signature tab summarises a set (buffer, polity); the rest always describe one basin. (4.8, 6.1, 6.2)
4. **Polities show far less.** Only the Signature tab, the map and the global Atlas; no Analysis, Seasonality, Context or Similarity. (4, 6)
5. **The percentile is global at the queried level** (all L6, or all L8, basins on Earth, nodata excluded), not relative to the region or the query. The UI says "percentile" without saying so. (2.5)
6. **Multi-basin continuous rows have no native-unit value**, only a mean percentile; a single basin shows both. (3.1)
7. **A missing number means one of several things:** by design (categoricals, flags), two separate populations (score suppressed), variable absent across the area (`outside_active_domain`), network quantity for a polity (`not_areal`), or no data. The Signature tab names the cause (*not present here*, *largely absent*, *no data*, "no single percentile…", *(low coverage)*); a bare "—" appears only for a null score with no status cause. (2.6, 4.7)
8. **`n_units` varies row to row** in a multi-basin query: it counts the basins that had data for that variable. (3.1)
9. **Band T uses its own geometry**, the query's circle or polygon, not the basin set; its rows are per year (LMR), per epoch (HYDE) or per eruption (eVolv2k). Row counts grow with span length. (3.2, 5.3)
10. **A date selects only Band T.** Bands A to E return identically for any date, and the tab does not flag that Band D is modern-only or that Band C is contemporary. This is deliberate (bands reflect persistence), but nothing says so in the UI. (5.2, 5.4)
11. **Polities have two independent dates.** The resolver year (always the slice start) picks the boundary; the Band T span is the slice's own years and cannot be edited there. (1.4, 5.1)
12. **A "nearest" HYDE epoch can be hundreds of years away,** shown with a "~" but not the distance. (5.3)
13. **Changing the level after a signature only redraws the map.** A signature at the new level needs another Get signature. (1.5)
14. **Most computed fields are never shown** (coverage, shortfall, modality, caveat texts, class mixtures beyond the leading class, similarity detail). (4.7, 6.2)
15. **Several Settlements results are one click and a fetch away from stale.** Changing scope or buffer radius clears results; changing level does not. (1.5)
16. **A query that resolves to no basins is an error, not an empty result** (v0.4.2). A point on open water, an oceanic island with no basin at that level, or a buffer or polygon that meets none returns HTTP 404: "No basin covers the given point location" (single basin, ring), "No basins fall within this buffer", "No basins intersect this area"; the public `/api/signature?scope=basin` says "No basin covers this point" (older wording, same 404). Before v0.4.2 most of these were 500s. In the Sandbox the buffer preview shows no basins first, so the user sees it before asking for a signature. [code engine.py:NoBasinsError; routes_sandbox.py:areas; routes_common.py:signature]

### 7.2 Defects and open items
| # | Item | Status (who decided) | Where |
|---|---|---|---|
| 1 | A–E band checkboxes did not filter the rows returned | **fixed v0.4.2** (engine filter; also public buffer and area scopes) | 2.1 |
| 2 | Buffer heading omitted place name and radius | **fixed v0.4.2** | 4.1 |
| 3 | `from_year > to_year` accepted silently, in UI and API | **fixed v0.4.2** (422 in `/api/areas` and public `/api/signature`) | 5.5 |
| 4 | HYDE epoch chosen by two different rules (signature vs map) | **fixed v0.4.2** (map follows the signature rule); default map year 1000 CE kept (Karl) | 6.4 |
| 5 | Polity Signature heading not BCE-aware | **fixed v0.4.2** | 5.5 |
| 6 | "LMR data begins 700 CE" message concerned the map layer, not the signature | **fixed v0.4.2** (wording names the map layer); the 700 CE floor itself is unchanged | 5.5 |
| 7 | Row `status` vocabulary inconsistent across docstring, code, tests, UI | **decided v0.4.2**: five values, all listed; `low_coverage` shown as an italic parenthetical (Karl) | 2.6 |
| 8 | Docs described the old coherence rule (p10-p90 under 20) | **fixed v0.4.2** (`reading-a-signature.md` rewritten) | 2.7 |
| 9 | L8 choropleth only paints the signature's basins | **decided** (Karl, 2026-10-28): kept; the world paint takes about 3.5 s and nothing needs it | 6.4 |
| 10 | `/api/area` superseded; `scope=basin_ring` never sent by the Sandbox; `/areas` misnamed (takes a point) | **done/decided v0.4.2**: `/api/area` removed; `/api/areas` name and `scope=basin_ring` kept for the dashboard (Karl) | 0.1 |
| 11 | How to summarise a small set of basins (ring, any buffer that stays) for divergence, seasonality, similarity | open design question for the dashboard, not a v0.4.x fix (Karl) | 4.8 |
| 12 | The buffer scope is an arbitrary bound and may be retired. Karl (2026-10-30): a buffer has no conceptual basis for a terrestrial service, and near a coast it includes sea that belongs to no basin (`shortfall`), so the label "R km buffer" promises a full circle while the numbers describe only its land part. A coastality measure exists but is deferred pending more data (bathymetry); how to decide that a place is coastal, and what follows, is tied to this question | open (Karl) | 1.3, 4.8 |
| 13 | Variable-level `historical_validity` is recorded in the catalog but unused; not gating by date is deliberate | decided (Karl); surfacing it as information is separate and open | 5.2 |
| 14 | Atlas is Explorer-adjacent, to appear in the dashboard as an option, tab or alternate screen | decided (Karl) | 6.3 |
| 15 | B6 modality is skipped for polities ("not calibrated for polygon scale") | intentional, pinned by a test | 3.1 |

### 7.3 What this implies for design (stated, not recommended)
- Items 7.1.2, 7.1.3, 7.1.4 and 7.2.11 are one issue seen four ways: the Sandbox has rich single-basin instruments and a thinner set-level story.
- Items 7.1.5, 7.1.7, 7.1.10 and 7.1.12 are cases where a number is displayed without the context needed to read it; the context exists in the payload or the catalog.

- LMR anomalies in the Signature tab and on the Polities map use slightly different baselines (stored values vs re-based to the cell's 850-1850 mean; typically a few tenths of a kelvin, up to about 1.8 K in a few cells), and neither display says which. See 5.3.

### 7.4 Present in the code but unreachable, or deliberately absent
Things a reader of the code or the API might assume the Sandbox does, and does not.

- **`scope=basin_ring` on `/api/areas`** and the engine's `basin_ring_signature` (a full signature for every ring member) exist, but the Sandbox never sends that scope; it builds the ring itself (§1.2). [code routes_sandbox.py:areas; engine.py:basin_ring_signature]
- **`/api/area`** (polity by name) was removed in v0.4.2; `/api/areas?scope=polity` replaced it. [code routes_sandbox.py]
- **The public `/api/signature` scopes `buffer` and `area`** (arbitrary polygon via `geom_wkt`) are not used by the Sandbox, which calls only `scope=basin` on the public endpoint. [code routes_common.py:signature]
- **The `extreme` aggregation method** is implemented but its variable set is empty, so no row ever has it. [code engine.py:`_B5_EXTREME_VARS`]
- **Excluded from the signature:** `river_area_upstream`, `strata_code`, `gdp_avg`, `human_dev_idx`; `pnv_shares` (a multi-column composition) is not emitted. Catalog rows marked `planned` are never emitted either (§2.1). [code engine.py:`_B1_EXCLUDE`, `_SKIP_API_KEYS`, load_catalog]
- **Native-unit values for multi-basin rows** are not computed; only a mean percentile is (§3.1). [doc deferred_items_register "Native-unit means"]
- **Two-regime (modality) detection is skipped for polities** ("not calibrated for polygon scale"), and **discharge is withheld for polities** as not meaningful for an area. [code engine.py:areal_signature_polygon, `_B2_NOT_AREAL_SCOPES`]
- **Similarity, Context, Analysis and Seasonality are single-basin instruments**: no version summarises a set of basins (§4.8, §6.1, §6.2).
- **Bands are not gated by date range**, on purpose: they reflect persistence. The catalog's per-variable `historical_validity` flag exists but nothing reads it (§5.2).
- **The Workbench** (societies, ecoregions, WH Cities, African regions) is a separate page and is not described here.

---

## 8. Appendix: captured example responses

*Assumes: §0 to §3 for how to read the fields.*

Real responses from the local server on 2026-10-26, trimmed, and supplied as separate JSON files alongside this document. All are Timbuktu (16.8167, −2.9833) at L6 unless noted, so the same place can be compared across scopes. Each file starts with `_note`, `_query` (the exact request), `_captured` and `_trimmed` (what was cut). Geometry is omitted everywhere; histogram arrays are capped at 12 entries.

| File | Request | What it demonstrates |
|---|---|---|
| `01_single_basin_timbuktu_L6.json` | `/api/areas?scope=single_basin&…&bands=ABCDE&detail=true` | one basin: 52 rows, raw value **and** percentile on continuous rows, no coherence badge, 4 `outside_active_domain` rows |
| `02_buffer_100km_timbuktu_L6.json` | `/api/areas?scope=buffer&radius_km=100&…` | 9 basins: percentile only (no raw) on continuous rows, coherence tags, 13 `two_regime` rows with the score suppressed, `scope.member_ids` |
| `03_polity_northern_song_961_L6.json` | `/api/areas?scope=polity&polity=Northern Song&year=961&…` | 156 basins: `not_areal` discharge rows, modality skipped, `resolver{}`, `member_ids`, `modality_post_pass`, `marginal_exposure` |
| `04_band_t_timbuktu_1475_1525.json` | single basin with `bands=ABCDET&from_year=1475&to_year=1525` | Band T only: 1 HYDE epoch × 4 variables, 51 LMR years × 3, 7 eVolv2k events; first/middle/last row per variable |
| `05_band_t_polity_northern_song.json` | polity with `bands=T&from_year=961&to_year=1027` (the polity's whole span, not one slice; the Sandbox sends a slice's own years) | Band T on a polygon: 67 LMR years, 8 events. (With `bands=T` only Band T rows come back; before v0.4.2 this request also returned all 52 A–E rows.) |
| `06_ring_topology_timbuktu_L6.json` | `/api/basin/ring` | the ring as the UI gets it: 5 neighbours with interior point and bearing (no signature) |
| `07_public_signature_basin_timbuktu_L6.json` | `/api/signature?scope=basin&bands=ABCE` | the parallel call behind Analysis and Seasonality: raw values per variable, no percentiles, monthly arrays kept |
| `08_context_timbuktu_500km.json` | `/api/context` | the Context table's seven rows with global and radius percentiles |
| `09_similarity_precip_timbuktu.json` | `/api/similarity/conjunction` | the Precipitation lens at default thresholds: 119 matching basins (5 shown), reach, query values |

How to read an areal file (01 to 05): `rows_summary_all_A_to_E` is one compact line for **every** A–E row; `representative_rows_full` is the complete row, `detail` included, for one example of each distinct combination of method, status and score state; `row_counts` tallies the full set; `band_t_rows_selected` and `band_t_counts_by_variable` appear where Band T was requested.

Not captured: a buffer or polity with Band T over a long span (very large), the Atlas and choropleth value dictionaries (hundreds of KB each; shapes are in section 6.5), and the polity-search and slice listings.

---

## 9. Appendix: fixed interpretive thresholds

*Assumes: §2.6, §2.7 (statuses, coherence), §4 (what the UI shows), §6 (Context, Similarity).*

Cutoffs that decide what label, badge, sentence or withheld value a user sees. Values are as of v0.4.2 (`a673660`); v0.4.2 changed no threshold named here (it did change which basins `climate_classes.py` paints, section 6.3). "Set by" is who chooses the value: **fixed** (in code, not adjustable), or **user** (a control, within a range the interface pre-sets). Items marked *provisional* are described that way in the code comments.

**Engine** (`scripts/edop/areas/engine.py`)

| Governs | Value | Where | Set by |
|---|---|---|---|
| Dispersion badge: **concentrated** if core share ≥ cutoff, else spread | 0.65 (*provisional*) | `_CORE_SHARE_CUTOFF` | fixed |
| Core window: half-width of the window that holds the core share | ±15 percentile points | `_CORE_SHARE_DELTA` | fixed |
| Badge **split**: one tied score holds at least this share of the weight | 0.50 | `_SPLIT_TIE_MIN_WEIGHT` | fixed |
| ...and at least this share lies outside the core window | 0.10 | `_SPLIT_MIN_RESIDUAL` | fixed |
| Badge withheld below this many basins (core share is pinned near 1.0 at small n) | 5 | `_MIN_COHERENT_BASINS` | fixed |
| Categorical **concentrated** if the modal class holds at least this share, else mixed | 0.85 | `aggregate_b3(plurality_threshold)` | fixed |
| Categorical row marked `low_coverage` if surviving weight is below this | 0.50 | `aggregate_b3(low_coverage_floor)` | fixed |
| Zero-aware percentile used when a variable's global zero fraction is at least this | 0.20 | `rank_expr`, `compute_global_scores` (`zero_fraction_threshold`) | fixed |
| `outside_active_domain` (percentile withheld): zero fraction at least the catalog threshold **and** weight at zero at least this | 0.20 and 0.90 | `aggregate_b1(zero_fraction_threshold, zero_coverage_threshold)` | fixed |
| Two-regime (bimodal) score suppression: gap as a fraction of spread | 0.50 (*provisional*) | `_MODALITY_GAP` | fixed |
| ...and minimum weight on each side to count as a regime | 0.20 | `_MIN_REGIME_WEIGHT` | fixed |
| Histogram flagged `low_resolution` | fewer than 3 basins (basin units), or effective weight under 5 (cell units) | `_LOW_RES_BASIN_THRESHOLD`, `_LOW_RES_CELL_THRESHOLD` | fixed (flag only; no visible UI use found) |
| Band T span limits | LMR 0 to 1998 CE; eVolv2k -491 to 1890 CE | `_LMR_RANGE`, `_EVOLV_RANGE` | fixed (data coverage, not interpretation) |

**Sandbox UI** (`app/templates/sandbox.html`)

| Governs | Value | Where | Set by |
|---|---|---|---|
| Analysis: small catchment, provenance "Undetermined" | upstream area under 500 km² at L6, under 5,000 km² at L8 | `renderAnalysis` (`smallBasinThreshold`) | fixed |
| Analysis: "Exogenous water supply" | upstream/local ratio of precipitation or moisture index above 1.5 (not applied to small catchments) | `renderAnalysis` | fixed |
| Analysis: "Coastal terminal" | coastal flag and distance to sink under 10 km (the drainage badge in the Basin context table uses under 1 km, or coastal and under 10 km) | `renderAnalysis` | fixed |
| Analysis: "Catchment-uniform" vs "Local-dominant" | all three ratios (precipitation, moisture, temperature) within 0.9 to 1.1 | `renderAnalysis` (`nearUnity`) | fixed |
| Analysis: ratio colouring | muted under 0.1 from 1×; amber under 0.3; red-bold otherwise | `renderAnalysis` (`ratioClass`) | fixed |
| Seasonality sentence: precipitation concentration | under 0.15 very little; under 0.35 moderate; under 0.60 clear; else strong | `renderSeasonality` (blurb) | fixed |
| Seasonality sentence: peak offset (months) | over 3.5 anti-phase (Mediterranean-type); under 1.5 near co-incident (monsoon, continental); else moderate | `renderSeasonality` | fixed |
| Seasonality sentence: temperature range | under 10 °C small; under 18 °C moderate; else large | `renderSeasonality` | fixed |
| Context sentence: extreme at global scale | percentile ≤ 10 or ≥ 90 | `CTX_EXTREME_PCTL_GLOBAL` | fixed |
| Context sentence: extreme within the radius | percentile ≤ 15 or ≥ 85 | `CTX_EXTREME_PCTL_LOCAL` | fixed |
| Context sentence: difference between global and in-radius percentile worth a sentence | 25 points or more | `CTX_MATERIAL_GAP` | fixed |
| Context sentence: "close to the global median" | global percentile 25 to 75 | `CTX_NEAR_MEDIAN` | fixed |
| Band T eVolv2k table: events shown by default | VSSI ≥ 5 Tg S (all shown if none reach 5; "show all" link) | `VSSI_THRESHOLD` | fixed |
| Context radius | 250, 500, 1000, 2500 km | radio buttons | user, four preset values |
| Similarity tolerances (six) | Magnitude 1.25 / **1.5** / 2.0 (ratio); Amplitude 0.10 / **0.15** / 0.25; Shape 0.85 / **0.90** / 0.95 (correlation); Temp level 2 / **3** / 4 (°C); Temp range 2 / **4** / 6; Elevation 25 / **50** / 100 (m); Relief 50 / **100** / 200 (m). Defaults in bold. | `v3-cj-*` selects | user, three preset values each |
| Buffer radius | default 100 km | Scope controls | user |

- **What is not a threshold:** the binning and axis windows of histograms, the ±0.5 fallback window for a single value, and colour ramps are presentation, not interpretation, and are omitted.
- **What is user-set:** only Similarity tolerances, the Context radius, buffer radius, level and the date span. Every interpretive label above is fixed, and the user cannot see the cutoff without reading code or docs.
- **Decision (Karl, 2026-10-27):** the "no thresholds" wording in the docs is to be softened, not the thresholds exposed or retired; these rules are reading aids. A rule-based prose layer may use them. Several are marked provisional in the code.
- **Open design problem:** no single cutoff for dispersion suits all distributions, so the badge rules may change; prose built on them inherits that.
