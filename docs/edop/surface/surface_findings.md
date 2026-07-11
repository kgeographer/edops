# Surface phase — findings

Coded SF.n. Session-by-session detail in `logs/session_log_YYYYMMDD.md`.

---

## SF.1 — Sandbox capability-gap analysis (2026-07-01)

### What the engine offers

**Resolvers in engine.py (all five):**
- `resolve_buffer` — point + radius → weighted basin set (fractional overlap)
- `resolve_single_basin` — point → exact containing basin (weight=1.0)
- `resolve_basin_ring` — point → (center_df, ring_gdf); centre + first-order adjacents with `border_bearing`, `centroid_bearing`, `shared_km` (WO17; promoted to engine.py 2026-07-01)
- `resolve_polygon` — WKT polygon → weighted basin set (overlap/polity_area)
- `resolve_polity` — Cliopatria name + year → WKT → delegates to `resolve_polygon`

**Public entry points in engine.py (four):**
- `areal_signature(lat, lon, radius_km, conn, ...)` — buffer path; runs B1–B6 + Band T
- `single_basin_signature(lat, lon, conn, ...)` — exact basin path; runs B1–B6, Band T deferred
- `basin_ring_signature(lat, lon, conn, ...)` — centre + first-order adjacents; **distinct payload shape** (see below)
- `areal_signature_polygon(geom_wkt, conn, ...)` — polygon/polity path; same aggregation as buffer

**Payload shape (buffer, single-basin, polygon/polity):**
```json
{
  "neighborhood": { "type", "level", "n_units", "unit_type", ...resolver-specific... },
  "shortfall":    float,
  "bands":        ["A","B","C","D","E","T"],
  "temporal":     { "from_year", "to_year" } | null,
  "caveats":      { "lmr_caveat": "...", "hyde_caveat": "..." },
  "rows":         [ make_row dicts ]
}
```

**Payload shape (basin-ring — structurally different; no aggregate rows[]):**
```json
{
  "type":   "basin_ring",
  "lat":    float, "lon": float, "level": int,
  "center": { <single_basin_signature payload> },
  "ring": [
    {
      "hybas_id": int, "sub_area_km2": float, "shared_km": float,
      "border_bearing": float, "centroid_bearing": float,
      "neighbor_lat": float, "neighbor_lon": float,
      "signature": { <single_basin_signature payload> }
    }
  ]
}
```
The ring path exposes per-neighbour comparison, not an aggregate. The surface must render
centre vs. each ring member individually — no single representative score for the ring as a whole.

**make_row fields per variable:**
`variable`, `band`, `method`, `unit_type`, `n_units`, `representative_score`,
`representative_raw`, `score_suppressed`, `coverage`, `status`, `coherence`,
`modality`, `distribution`, `weight_at_zero`, `caveat`, `year`, `epoch_year`, `units`,
`detail` (lean vs full: `project_row(include_detail=True)` adds histogram objects)

**Methods routing determines rendering:**
- `area_weighted` — B1; yields coherence (concentrated/spread), modality (unimodal/two_regime), p10/p90/spread in detail
- `dominant_basin` — B2; network-topology variable; score + raw from dominant basin
- `class_mixture` — B3/B4; modal class label + mixture breakdown in detail
- `flag_fraction` — B4; coast fraction scalar
- `distribution_only` — B5 fallback; mean percentile + spread
- `extreme` — B5; carrier basin score
- `grid_areal_distribution` — Band T (HYDE per epoch, LMR per year); per-year rows
- `global_forcing` — Band T eVolv2k; per-event rows

**Histogram object** (in `detail['distribution']`, with `include_detail=True`):
```json
{
  "bins": [...21 floats...], "weights": [...20 floats...],
  "n_units": int, "unit_type": "basin|hyde_cell|lmr_cell",
  "low_resolution": bool, "min": float, "max": float,
  "p10": float, "p90": float, "mean": float,
  "resolver_year": int|null, "band_t_from": int|null, "band_t_to": int|null
}
```

**Two temporal axes in polity path:**
- `resolver_year` — selects which year's Cliopatria boundary to use; stamped on histograms
- `from_year`/`to_year` — Band T aggregation window; independent of boundary year

**Wired HTTP endpoints (as of WO22):**
- `GET /api/area?polity=&year=&[level=6]&[bands=ABCDET]&[from_year=]&[to_year=]&[detail=true]`
  → calls `areal_signature_polygon`; only polity-by-name input supported
- `GET /api/signature?lat=&lon=` → calls `get_signature` from `app.db.signature` (v0.3 path, NOT the engine)

**Not wired to any endpoint:**
- `areal_signature` (buffer path)
- `single_basin_signature` (exact basin path)
- `basin_ring_signature` (basin-ring path)

---

### What sandbox.html currently exposes

**Input:**
- WHG place lookup → lat/lon (single-point); reconcile+extend pipeline
- Direct lat/lon coordinate entry
- Example presets (6 presets; Timbuktu, Rome, Kaifeng, Ur)
- Level 6/8 toggle

**Always calls `/api/signature`** (v0.3 point-containing-basin, NOT the engine's areal path).
Accesses: `sig.profile_groups`, `sig.profile_summary`, `sig.eco_id`, `sig.up_area`, `sig.id`.

**Signature rendering:**
- Accordion per band, iterates `['A','B','C','D','E']` hardcoded
- Items rendered as `{label, value}` flat pairs from `group.items`
- Band T via `buildTemporalBody()`: expects v0.3 blob `{pdsi_series, air_series, prate_series, grid_cell, lmr_status, pdsi_mean, hyde_land_use, volcanic_events}`
- SVG bar charts for PDSI/temp/precip (annual), cropland (epochs), grazing stacked (epochs)
- Volcano event table

**Analysis α tab:** basin context, s/u divergence (precip/aridity/temp ratios), water provenance badge

**Map:** Leaflet; hillshade + OSM tiles; neighborhood preview (containing basin orange, adjacent choropleth by up_area, rivers)

**Other:** Ecoregion → Wikipedia modal, LLM narrative button, API Guide iframe

---

### The gap

| Dimension | Engine offers | sandbox.html exposes | Gap |
|---|---|---|---|
| Resolvers | buffer, single-basin, basin-ring, polygon/polity | single-basin point (v0.3 path, bypasses engine) | All four engine paths invisible |
| Input type | polity-by-name+year | lat/lon only | Polity input entirely absent |
| Payload schema | `{rows, neighborhood, shortfall, caveats}` | `{profile_groups, profile_summary}` | Structurally incompatible; different renderer required |
| Quality metadata | coherence, modality, score_suppressed, coverage, weight_at_zero | None | Never displayed anywhere |
| Histogram objects | `{bins, weights, …}` via `&detail=true` | None | Never displayed anywhere |
| `resolver_year` axis | Yes — stamps polity boundary year | No | Entirely missing from any UI |
| Band T axis (`from_year`/`to_year`) | Yes (engine and v0.3) | Yes (v0.3 format) | Present but in incompatible format |
| Band T engine format | per-year `make_row` rows in `rows[]` | `{pdsi_series, …}` nested blob | `buildTemporalBody()` cannot consume engine Band T |
| Neighborhood metadata | `{type, n_units, unit_type, marginal_exposure}` | Partial (adjacent basins on map) | `marginal_exposure`, `shortfall`, `n_units` never shown |
| Polity boundary | `/api/polity/geom` available | Not consumed | Map overlay absent |
| Caveats | Top-level `caveats` dict with text | Not displayed | Never surfaced |
| Basin-ring resolver | `resolve_basin_ring` + `basin_ring_signature` in engine.py (2026-07-01) | N/A | Not yet HTTP-wired; distinct payload shape needs its own rendering path |

---

### Extensibility verdict on sandbox.html

**Cannot absorb the new elements.** The rendering model is deeply coupled to the v0.3
envelope shape (`profile_groups`, `profile_summary`, `group.items`). The engine's `rows[]`
payload requires an entirely different rendering pass — per-row method dispatch rather than
per-band accordion. Band T alone is a structural incompatibility: `buildTemporalBody()` would
need a full rewrite to handle `grid_areal_distribution` and `global_forcing` rows. Extending
in-place would amount to rewriting all rendering functions while keeping the v0.3 Lookup path
intact in the same file — against the locked constraint that `sandbox.html` stays untouched.

New page is unambiguously correct. The two pages share: Bootstrap 5.3, Leaflet (map),
the SVG chart patterns (reusable primitives), and the site header/nav structure. Nothing in
the rendering logic transfers directly.

---

### Decisions the gap analysis drives

**Needs confirmation before page spec:**

1. **Buffer-path endpoint** — the new page will want buffer query input (lat/lon + radius).
   Currently `areal_signature` is not wired. Either add `GET /api/area-buffer?lat=&lon=&radius_km=`
   (simplest), or overload `/api/area` with an alternative input path. The tracker defers
   `/area` input types beyond polity to surface-driven need — this is the first pull.

2. **Map library for new page** — Leaflet is adequate for polity boundary overlay on
   `/api/polity/geom` GeoJSON (no PMTiles choropleth needed). MapLibre adds complexity
   without a clear payoff for this page's use case. Recommend Leaflet to match sandbox.html's
   pattern; revisit if a choropleth layer becomes a requirement.

3. **Band T rendering model** — the engine's Band T is `rows` entries with `method=grid_areal_distribution`
   or `global_forcing`, each with a `year` field. These are NOT summaries; they are one row
   per year per variable. Displaying them requires collating by variable then year to reconstruct
   a time series — the engine does not pre-collapse. The sandbox page must do this collation
   client-side. This is a new rendering task with no sandbox.html analogue.

4. **Histogram widget** — `detail['distribution']` exists in B1, B5, and Band T rows. No
   current UI renders it. The new page is the first consumer. Widget needs: bin-edge array +
   weight array → SVG histogram. Reusable across basin-path variables (percentile x-axis)
   and Band T variables (native-unit x-axis). The temporal stamp fields (`resolver_year`,
   `band_t_from`, `band_t_to`) should be displayed in a caption.

5. **Basin-ring endpoint** — `resolve_basin_ring` and `basin_ring_signature` are now in
   engine.py (promoted 2026-07-01, 77/77 engine tests pass). HTTP wiring is the remaining
   step. The basin-ring payload shape is structurally distinct from the other three entry points
   (`{center, ring[]}` rather than `{rows[], neighborhood}`), so it needs its own endpoint and
   its own rendering path on the new page.
