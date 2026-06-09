# EDOPS Codebook v03

Variable-by-variable documentation for the EDOPS signature, aligned with API v03.
Machine-readable catalog: `edops_variable_catalog_v03.tsv`.
BasinATLAS source variables: see `BasinATLAS_Catalog_v10_optimized.pdf`.

---

## How to read this document

Each entry covers one signature variable. For BasinATLAS-sourced variables, a summary
is given here and the full technical specification (derivation, resolution, aggregation
method, known limitations) is in the PDF catalog under the cited atlas ID.

EDOPS-native variables (derived fields, temporal bands) are documented in full here.

Fields per entry:
- **Schema key** — identifier used in the API and variable catalog
- **Band** — A (physiographic) · B (hydro-climatic) · C (bioclimatic) · D (anthropocene) · E (coastality) · T (temporal)
- **Units** — as returned in the API
- **What it measures** — plain-language description
- **Interpretation notes** — how to read high/low values; known spatial patterns; caveats
- **Historical validity** — whether the variable is meaningful for pre-modern queries
- **Atlas ref** — BasinATLAS catalog ID (BasinATLAS-sourced variables only)

---

## Band A — Physiographic bedrock

### elevation_min
*Basin minimum elevation · m · Atlas ref: P01*

### elevation_max
*Basin maximum elevation · m · Atlas ref: P01*

### elevation_point
*Point elevation at query location · m · Derived (OpenTopoData / Open-Meteo fallback)*

### relief_range_m
*Vertical relief within basin · m · Derived: elevation_max − elevation_min*

### relief_position
*Query point's position within basin relief · 0–1 · Derived: (elev_point − elev_min) / relief_range*

### slope_deg
*Mean basin slope · degrees · Atlas ref: P02*

### stream_gradient
*Mean stream gradient · m/km · Atlas ref: P03*

### lithology_name
*Dominant lithology class · categorical · Atlas ref (lu_lit lookup)*

### karst_pct
*Karst area as share of basin · % · Atlas ref: S07*

---

## Band B — Hydro-climatic baselines

### discharge_annual
*Mean annual river discharge · m³/s · Atlas ref: H01*

### discharge_min
*Mean monthly minimum discharge · m³/s · Atlas ref: H01*

### discharge_max
*Mean monthly maximum discharge · m³/s · Atlas ref: H01*

### runoff
*Mean annual runoff · mm/yr · Atlas ref: H02*

### groundwater_depth
*Mean depth to groundwater table · cm · Atlas ref: H10*

### river_area
*River and lake area within basin · km² · Atlas ref*

### wetland\_pct\_g1
*Wetland area group 1 · % · Atlas ref*

### wetland\_pct\_g2
*Wetland area group 2 · % · Atlas ref*

### wetland\_class\_id
*Dominant wetland class · categorical*

### pct\_clay / pct\_silt / pct\_sand
*Soil texture fractions · % · Atlas ref: S01–S03*

### pnv\_majority\_name
*Potential natural vegetation majority class · categorical · Atlas ref (lu_pnv lookup)*

### pnv_shares
*PNV class shares within basin · compositional array*

---

## Band C — Bioclimatic proxies

### temperature_annual
*Mean annual temperature · °C · Atlas ref: C01*

### temperature_min
*Mean monthly minimum temperature · °C · Atlas ref: C01*

### temperature_max
*Mean monthly maximum temperature · °C · Atlas ref: C01*

### precipitation_annual
*Mean annual precipitation · mm/yr · Atlas ref: C02*

### aridity_index
*Aridity index (P/PET × 100) · dimensionless · Atlas ref: C03*
Higher = wetter; arid/humid boundary at 100; global median ~68.

### permafrost_pct
*Permafrost extent · % · Atlas ref: L09*

### biome_name
*Dominant biome · categorical · Atlas ref (lu_tbi lookup)*

### ecoregion\_terrestrial\_name
*Terrestrial ecoregion · categorical · Atlas ref (lu_tec lookup)*

### freshwater\_habitat\_name
*Freshwater habitat type · categorical · Atlas ref (lu_fmh lookup)*

### freshwater\_ecoregion\_name
*Freshwater ecoregion · categorical · Atlas ref (lu_fec lookup)*

---

## Band D — Anthropocene markers

### reservoir_vol
*Upstream reservoir volume · km³ · Atlas ref*

### cropland_pct
*Cropland area · % · Atlas ref*

### pasture_pct
*Pasture area · % · Atlas ref*

### pop_density
*Population density · persons/km² · Atlas ref*

### human\_footprint\_2009
*Human footprint index (2009) · 0–50 · Atlas ref*

### gdp_mean
*Mean GDP per capita · USD · Atlas ref*

### hdi
*Human Development Index · 0–1 · Atlas ref*

---

## Band E — Coastality

### dist\_sink\_km
*Distance from basin outlet to ocean sink · km · Atlas ref*

### outlet_type
*Basin outlet type — exorheic / endorheic / coastal · categorical*

### coast_flag
*Whether basin drains directly to coast · boolean*

---

## Band T — Temporal enrichment

Band T variables are query-window dependent (from\_year / to\_year). Each source has a
different temporal extent; the API and sandbox must handle requests accordingly:

| Source | Temporal extent | Notes |
|---|---|---|
| LMR v2.1 | 1–2000 CE | Paleoclimate reconstruction |
| HYDE 3.4 | 10,000 BCE–2023 CE | Land-use history |
| eVolv2k v4 | 500 BCE–1900 CE | Volcanic stratospheric forcing |

Each returns a time series and/or period aggregate. Full documentation pending.

### LMR v2.1 — paleoclimate reconstruction

All three variables are anomalies relative to the 850–1850 CE temporal mean (Tardif et al. 2019).

- `lmr_pdsi` — Palmer Drought Severity Index anomaly
- `lmr_temperature` — 2m air temperature anomaly (K)
- `lmr_precipitation` — precipitation rate anomaly (kg/m²/s)

### HYDE 3.4 — land-use history
- `hyde_cropland` — cropland area (km²)
- `hyde_grazing` — grazing area (km²)
- `hyde_population` — population estimate
- `hyde_popdens` — population density

### eVolv2k v4 — volcanic forcing
- `evolv2k_vssi` — volcanic stratospheric sulfur injection (Tg S)

---

## Derived and context fields

| Field | Description |
|---|---|
| `elev_point` | Point elevation from external API (OpenTopoData → Open-Meteo fallback) |
| `relief_range_m` | Basin vertical relief (elev_max − elev_min) |
| `relief_position` | Query point position within relief, clamped 0–1 |
| `up_area` | Upstream drainage area (scale context, not a signature variable) |
| `eco_id` | WWF ecoregion integer ID (cross-reference to external datasets) |
