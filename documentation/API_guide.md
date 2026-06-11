# EDOPS API Guide
**v0.3 · June 2026**

EDOPS — the Environmental Dimensions of Place Service — generates structured environmental signatures for geographic coordinates worldwide. Signatures are derived from global datasets aggregated at the hydrological sub-basin level in [BasinATLAS](https://www.hydrosheds.org/products/hydroatlas), with optional historical climate enrichment from LMR v2.1 (paleoclimate) and eVolv2k v4 (volcanic events).

**Base URL:** `https://edops.computingplace.org/api`  
**Interactive schema:** https://edops.computingplace.org/docs

> **Research prototype — June 2026.** The API is publicly accessible but not under a stability guarantee. Parameters and response fields may change between versions. Fields marked *planned* are in design but not yet in the response.

---

## Endpoints

### GET /api/health

Returns `{"status": "ok"}`. Use to confirm the service is running.

### GET /api/signature

```
GET https://edops.computingplace.org/api/signature
  ?lat={lat}&lon={lon}
  [&bands={bands}]
  [&level={level}]
  [&from_year={from_year}]
  [&to_year={to_year}]
  [&flat={flat}]
```

Returns the environmental signature for the HydroATLAS sub-basin containing the given coordinate.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `lat` | float | required | Latitude in decimal degrees (−90 to 90) |
| `lon` | float | required | Longitude in decimal degrees (−180 to 180) |
| `bands` | string | `ABCDE` | Profile groups to include — any combination of A B C D E T with no separator, e.g. `ABT`. Band T requires `from_year` and `to_year`. |
| `level` | integer | `8` | Basin hierarchy level. `8` = sub-basin (median ~200 km²). `6` = regional (~tens of thousands km²). |
| `from_year` | integer | — | Start year CE for Band T temporal enrichment. Range: 0–1998. |
| `to_year` | integer | — | End year CE for Band T temporal enrichment. Range: 0–1998. |
| `flat` | boolean | `false` | When `true`, returns all band field values as flat top-level keys instead of the nested `profile_groups` structure. Band T temporal data appears at key `temporal` rather than inside `profile_groups`. See *Response modes* below. |

---

## Response Structure

The response is a structured JSON object. By default, environmental variables (Bands A–T) are grouped under `profile_groups`. Pass `&flat=true` to receive all variable values as flat top-level keys instead — useful for ingestion pipelines and vector operations.

### Fields present in both modes

| Key | Description |
|---|---|
| `meta` | Request context: `signature_version`, `generated` (ISO timestamp), `query` (lat, lon, bands, level, from_year, to_year), `neighborhood` (type, basin_level), `data_sources` |
| `id` | Basin identifier (BasinATLAS hybas_id) |
| `eco_id` | OneEarth ecoregion identifier |
| `up_area` | Total upstream contributing area (km²) |
| `geom_geojson` | Basin polygon as GeoJSON MultiPolygon string |
| `elev_point`, `elev_source`, `elev_dataset`, `elev_resolution_m` | Point elevation at query coordinate (OpenTopoData / Open-Meteo fallback) |
| `relief_range_m`, `relief_position` | Derived terrain metrics: elev_max − elev_min; (elev_point − elev_min) / relief_range |
| `profile_summary` | Ordered array of highlight fields: `[{key, label, value}, …]` |

### Default mode (no `&flat`)

| Key | Description |
|---|---|
| `profile_groups` | Dict keyed A–T (filtered to requested bands). Each entry: `{label, items: [{key, label, value}, …]}`. All environmental variables live here — see band tables below. |

### Flat mode (`&flat=true`)

| Key | Description |
|---|---|
| *band field keys* | All band field values returned as top-level keys, e.g. `elev_min`, `aridity`, `pop_density`. `profile_groups` is omitted. |
| `temporal` | Band T temporal data (when requested). Same structure as `profile_groups["T"]` in default mode. |

### Accessing field values

Default mode — walk the items list for the relevant band:

```python
sig = requests.get("https://edops.computingplace.org/api/signature?lat=16.77&lon=-3.01&bands=C").json()
items = sig["profile_groups"]["C"]["items"]
aridity = next(it["value"] for it in items if it["key"] == "aridity")
```

Flat mode — field values are directly at the top level:

```python
sig = requests.get("https://edops.computingplace.org/api/signature?lat=16.77&lon=-3.01&bands=C&flat=true").json()
aridity = sig["aridity"]
```

---

## Profile Bands

> **Local vs. upstream:** Most Band A–C fields appear as pairs — a local value (conditions within the sub-basin only) and an upstream value (area-weighted accumulation across all upstream contributing basins). Upstream keys carry an `_upstream` suffix, e.g. `aridity` / `aridity_upstream`. The divergence between the two is itself environmentally meaningful: a site where local aridity diverges sharply from upstream aridity (e.g. a desert city fed by a distant mountain river) occupies a qualitatively different position than one where they converge.

### Band A — Physiographic `(profile_groups["A"])` ✓ implemented

Stable over geological timescales; defensible as a historical baseline for any period.

| Field | Description | Units |
|---|---|---|
| `elev_min`, `elev_max` | Elevation range of sub-basin | m asl |
| `slope_avg`, `slope_upstream` | Mean slope local / upstream | ° |
| `stream_gradient` | Channel gradient | m/km |
| `lithology`, `lith_class` | Dominant lithology code and name | — |
| `karst`, `karst_upstream` | Karst extent local / upstream | % |
| `relief_range_m`, `relief_position` | Derived terrain relief metrics | m; 0–1 |
| *`elev_mean` (s/u), `erosion_rate`, `glacier_pct`, `permafrost_pct`* | *Planned additions* | *—* |

### Band B — Hydroclimatic `(profile_groups["B"])` ✓ implemented

Hydrological fluxes and soil characteristics integrating the full upstream catchment under the current climatic regime. Discharge and runoff reflect contemporary conditions, including the effects of upstream dams and diversions where present.

| Field | Description | Units |
|---|---|---|
| `discharge_yr`, `discharge_min`, `discharge_max` | River discharge annual mean, min, max | m³/s |
| `runoff` | Annual runoff | mm/yr |
| `river_area`, `river_area_upstream` | River/lake surface area local / upstream | km² |
| `gw_table_depth` | Groundwater table depth | m |
| `pct_clay`, `pct_silt`, `pct_sand` | Soil texture local (+ `_upstream` variants) | % |
| `wet_pct_grp1`, `wet_pct_grp2` | Wetland extent by type local (+ `_upstream` variants) | % |
| `wetland_class` | Dominant wetland class name | — |
| `reservoir_vol` | Reservoir storage volume | 10⁶ m³ |
| `pnv_majority`, `pnv_shares` | Potential natural vegetation — dominant class and share breakdown | —; % |

### Band C — Bioclimatic `(profile_groups["C"])` ✓ implemented

Contemporary climate baseline from BasinATLAS (WorldClim ~1970–2000 CE). These are long-run averages — for historical temperature and precipitation, Band T provides LMR anomalies relative to a 20th-century reference. When `from_year` is a BCE year, a disclosure note is appended indicating that these values reflect present-day conditions, not conditions at the requested epoch.

| Field | Description | Units |
|---|---|---|
| `temp_yr`, `temp_min`, `temp_max` | Annual mean, min month, max month temperature (local) | °C |
| `temp_yr_upstream` | Annual mean temperature upstream | °C |
| `precip_yr`, `precip_yr_upstream` | Annual precipitation local / upstream | mm/yr |
| `aridity`, `aridity_upstream` | Aridity index (P/PET) local / upstream — higher = wetter | dimensionless |
| `permafrost_extent` | Permafrost extent | % |
| `biome_id`, `biome` | OneEarth biome code and name | — |
| `eco_id`, `ecoregion` | OneEarth ecoregion code and name | — |
| `freshwater_type`, `freshwater_ecoregion_class`, `freshwater_ecoregion_name` | Freshwater ecoregion classification | — |

### Band D — Anthropocene `(profile_groups["D"])` ✓ implemented

Present-day only. Exclude or qualify for pre-modern analyses; useful as a contrast baseline. When `from_year` is a BCE year, a disclosure note is appended indicating these values are contemporary and do not represent conditions at the requested epoch.

| Field | Description | Units |
|---|---|---|
| `pop_density` | Contemporary population density | persons/km² |
| `human_footprint_09`, `human_footprint_09_upstream` | Human footprint index local / upstream (2009) | 0–100 |
| `cropland_extent`, `cropland_extent_upstream` | Cropland extent local / upstream (EarthStat ~2000 CE) | % |
| `pasture_extent`, `pasture_extent_upstream` | Pasture extent local / upstream (EarthStat ~2000 CE) | % |
| `reservoir_vol` | Reservoir storage volume | 10⁶ m³ |
| `gdp_avg` | GDP per km² (PPP, ~2015) | USD/km² |
| `human_dev_idx` | Human Development Index | 0–1 |

### Band E — Coastality `(profile_groups["E"])` ✓ implemented

Hydrological connectivity to the marine outlet. Always returned; the `endorheic` flag changes the interpretation of `dist_sink`.

| Field | Description | Units |
|---|---|---|
| `dist_sink` | Flow distance to marine outlet via basin network. **Note:** BasinATLAS records 0 for endorheic (landlocked) basins — this means *no outlet*, not zero distance. Check `endorheic` flag before interpreting. | km |
| `endorheic` | 0 = exorheic (ocean-connected); non-zero = landlocked with no marine outlet | flag |
| `coast_flag` | 1 = basin directly touches the coast | binary |
| *`outlet_type`, `topo_depth_from_coast`* | *Planned additions* | *—* |

### Band T — Temporal `(profile_groups["T"])` ✓ implemented

Period-specific climate enrichment from LMR v2.1 (Tardif et al. 2019), volcanic event annotation from eVolv2k v4 (Sigl & Toohey 2024), and land-use history from HYDE 3.4 (Klein Goldewijk et al. 2017). Requires `from_year` and `to_year`. LMR coverage: 0–1998 CE; HYDE coverage: 10000 BCE–2023 CE.

If the period is outside the LMR range, `profile_groups["T"]` (or `temporal` in flat mode) will contain a `_status: "out_of_range"` message; Bands A–E are unaffected. In flat mode (`&flat=true`), Band T data appears at the top-level key `temporal` rather than inside `profile_groups`.

| Field | Description | Units |
|---|---|---|
| `grid_cell` | LMR grid cell used for extraction `{lat, lon}` — 2°×2° grid snapped to nearest centre | — |
| `year_start`, `year_end` | Requested period echoed back | CE |
| `pdsi_series` | Annual PDSI values: `[{year, pdsi}, …]`. Negative = dry, positive = wet. | dimensionless |
| `pdsi_mean`, `pdsi_min`, `pdsi_max` | Period summary statistics for PDSI | dimensionless |
| `air_series` | Annual temperature anomaly: `[{year, air_anom_k}, …]`. Anomaly relative to 1951–1980 reference period. | K (anomaly) |
| `air_mean_anom_k` | Period mean temperature anomaly | K (anomaly) |
| `prate_series` | Annual precipitation rate anomaly: `[{year, prate_anom_mm_day}, …]`. Anomaly relative to 1951–1980 reference period. | mm/day (anomaly) |
| `prate_mean_anom_mm_day` | Period mean precipitation anomaly | mm/day (anomaly) |
| `volcanic_events` | Eruptions within the period from eVolv2k v4: `[{year_ad, month, vssi_tg, vssi_1sig, asymmetry, location, tephra}, …]` | — |
| `volcanic_event_count`, `volcanic_vssi_sum_tg`, `years_since_last_major` | Period summary statistics for volcanic forcing | —; Tg; years |
| `hyde_land_use` | HYDE 3.4 land-use series: `[{year_ce, cropland_km2, cropland_pct, grazing_km2, grazing_pct, pasture_km2, pasture_pct, rangeland_km2, rangeland_pct, basin_area_km2, n_cells}, …]`. One object per epoch within the requested period. | km²; % |
| `_status` | `"ok"` when data returned; `"out_of_range"` or `"not_requested"` otherwise | — |

> **Temporal values note.** LMR temperature and precipitation values are anomalies relative to a 20th-century reference period (1951–1980), not absolute values. PDSI is a drought severity index in its own right — positive values indicate wetter-than-average conditions for that location, negative values drier. Band C baselines reflect contemporary long-run averages from a different source and reference period; they are not directly comparable to LMR anomalies.

---

## Example Requests

**Bands A and B only — Athens**
```
curl "https://edops.computingplace.org/api/signature?lat=37.97&lon=23.73&bands=AB"
```

**Full baseline signature — Samarkand**
```
curl "https://edops.computingplace.org/api/signature?lat=39.65&lon=66.98&bands=ABCDE"
```

**With historical climate — Rome, early imperial period**
```
curl "https://edops.computingplace.org/api/signature?lat=41.9&lon=12.5&bands=ABCT&from_year=1&to_year=400"
```

**With historical climate — Kaifeng (Song dynasty capital)**
```
curl "https://edops.computingplace.org/api/signature?lat=34.8&lon=114.3&bands=ABCT&from_year=960&to_year=1127"
```

**Bands A, B, T — Timbuktu, medieval period**
```
curl "https://edops.computingplace.org/api/signature?lat=16.77&lon=-3.01&bands=ABT&from_year=1200&to_year=1600"
```

**Regional scale — Level 6**
```
curl "https://edops.computingplace.org/api/signature?lat=34.8&lon=114.3&bands=ABC&level=6"
```

**Flat mode — all fields as top-level keys**
```
curl "https://edops.computingplace.org/api/signature?lat=16.77&lon=-3.01&bands=ABCDE&flat=true"
```

---

## Notes for Application Developers

- **CORS:** Cross-origin requests are allowed. You can call the API directly from browser JavaScript.
- **No basin found:** If the coordinate falls outside all known sub-basins (open ocean, ice sheet), the API returns HTTP 404.
- **Default mode uses `profile_groups`:** Environmental variables are in `profile_groups["A"]` through `profile_groups["T"]`. The `bands` parameter controls which groups are included. Use `&flat=true` to receive all variable values as flat top-level keys instead.
- **Band T anomalies:** LMR temperature and precipitation values are anomalies relative to a 20th-century reference period (1951–1980), not absolute values. PDSI is a drought severity index — not an anomaly relative to a baseline.
- **Endorheic basins:** `dist_sink = 0` in BasinATLAS means *no marine outlet*, not zero distance. Always check the `endorheic` flag.
- **Rate limits:** None enforced currently. Contact us for bulk request needs.

---

*EDOPS is part of the [Computing Place](https://computingplace.org) research initiative.*  
*Contact: karl.geog@gmail.com*  
*Machine-readable schema: [edops_schema.json](edops_schema.json)*
