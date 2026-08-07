# EDOPS Codebook

*First-draft variable entries generated mechanically from `documentation/EDOPS_variable_catalog_v0.4.tsv` (served live at `/documentation/EDOPS_variable_catalog_v0.4.tsv`). The prose sections below (marked TODO) are hand-written and not yet drafted — see `docs/design/DOCSv4 — TODO.md` §5.4.*

## How to read a signature

The Codebook is a strict per-variable reference — for how the Signature tab's numbers, badges,
histograms, and Band T charts actually work, see
[Reading a signature](sandbox/reading-a-signature.md).

## Local, upstream, and delta

*TODO — extend the existing API Guide paragraph (`documentation/API_guide.md`, “Local vs. upstream” note under Profile Bands).*

## The bands

### Band A — Physiographic

Stable over geological timescales; defensible as a historical baseline for any period.

*12 variables in the catalog (9 implemented, 3 planned). Overview paragraph above is carried over from `API_guide.md`; confirm it still reads right in a codebook context, or replace.*

#### Cryosphere

##### Glacier/permanent snow (`glacier_pct`)
*planned — not yet in the live API · BasinATLAS v1.0 · % · local + upstream*

Not currently in signature

#### Elevation

##### Elevation maximum (`elevation_max`)
*implemented · BasinATLAS v1.0 · m · local only*

Basin maximum elevation

##### Elevation mean (`elevation_mean`)
*planned — not yet in the live API · BasinATLAS v1.0 · m · local + upstream*

Mean basin elevation; u available in basin08

##### Elevation minimum (`elevation_min`)
*implemented · BasinATLAS v1.0 · m · local only*

Basin minimum elevation

##### Point elevation (`elevation_point`)
*implemented · Derived · m · point*

Derived from OpenTopoData/Open-Meteo; not a basin08 field

##### Relief position (`relief_position`)
*implemented · Derived · 0–1 · derived*

Derived: (elev_point - elev_min) / relief_range

##### Relief range (`relief_range_m`)
*implemented · Derived · m · derived*

Derived: elev_max - elev_min

#### Geology

##### Erosion rate (`erosion_rate`)
*planned — not yet in the live API · BasinATLAS v1.0 · t/ha/yr · local + upstream*

Not currently in signature

##### Karst area (`karst_pct`)
*implemented · BasinATLAS v1.0 · % · local + upstream*

u already in view as karst_upstream

##### Lithology class name (`lithology_name`)
*implemented · BasinATLAS v1.0 · — · local only*

Resolved via lu_lit

#### Terrain

##### Slope (`slope_deg`)
*implemented · BasinATLAS v1.0 · degrees · local + upstream*

u already in view as slope_upstream

##### Stream gradient (`stream_gradient`)
*implemented · BasinATLAS v1.0 · m/km · local only*

*No description yet in the catalog — needs a hand-written note.*

### Band B — Hydroclimatic

Hydrological fluxes and soil characteristics integrating the full upstream catchment under the current climatic regime. Discharge and runoff reflect contemporary conditions, including the effects of upstream dams and diversions where present.

*23 variables in the catalog (14 implemented, 9 planned). Overview paragraph above is carried over from `API_guide.md`; confirm it still reads right in a codebook context, or replace.*

#### Discharge

##### Annual runoff (`runoff`)
*implemented · BasinATLAS v1.0 · mm/yr · local only*

*No description yet in the catalog — needs a hand-written note.*

##### Discharge annual mean (`discharge_annual`)
*implemented · BasinATLAS v1.0 · m³/s · local only*

Cumulative; no upstream avg meaningful

##### Discharge monthly maximum (`discharge_max`)
*implemented · BasinATLAS v1.0 · m³/s · local only*

*No description yet in the catalog — needs a hand-written note.*

##### Discharge monthly minimum (`discharge_min`)
*implemented · BasinATLAS v1.0 · m³/s · local only*

*No description yet in the catalog — needs a hand-written note.*

#### Groundwater

##### Groundwater table depth (`groundwater_depth`)
*implemented · BasinATLAS v1.0 · cm · local only*

*No description yet in the catalog — needs a hand-written note.*

##### Soil water content annual (`soil_water_content`)
*planned — not yet in the live API · BasinATLAS v1.0 · % · local + upstream*

Not currently in signature

#### Inundation

##### Inundation extent long-term (`inundation_longterm`)
*planned — not yet in the live API · BasinATLAS v1.0 · % · local + upstream*

Flood signal; not currently in signature

##### Inundation extent maximum (`inundation_max`)
*planned — not yet in the live API · BasinATLAS v1.0 · % · local + upstream*

Flood signal; not currently in signature

##### Inundation extent minimum (`inundation_min`)
*planned — not yet in the live API · BasinATLAS v1.0 · % · local + upstream*

Flood signal; not currently in signature

#### Soils

##### Clay content (`pct_clay`)
*implemented · BasinATLAS v1.0 · % · local + upstream*

s+u both in signature

##### Sand content (`pct_sand`)
*implemented · BasinATLAS v1.0 · % · local + upstream*

s+u both in signature; clay+silt+sand≈100 (compositional): drop pct_sand from classification feature matrices to avoid spurious linear dependency

##### Silt content (`pct_silt`)
*implemented · BasinATLAS v1.0 · % · local + upstream*

s+u both in signature

##### Soil organic carbon (`soil_organic_carbon`)
*planned — not yet in the live API · BasinATLAS v1.0 · t/ha · local + upstream*

Not currently in signature; good agricultural fertility proxy

#### Surface Water

##### Lake area (`lake_area_pct`)
*planned — not yet in the live API · BasinATLAS v1.0 · % · local + upstream*

Not currently in signature

##### Lake volume upstream (`lake_volume_upstream`)
*planned — not yet in the live API · BasinATLAS v1.0 · — · upstream only*

u-only field

##### River area (`river_area`)
*implemented · BasinATLAS v1.0 · ha · local + upstream*

u already in view as river_area_upstream

##### River channel volume (`river_volume`)
*planned — not yet in the live API · BasinATLAS v1.0 · — · local + upstream*

Not currently in signature

#### Vegetation

##### Potential natural vegetation majority name (`pnv_majority_name`)
*implemented · BasinATLAS v1.0 · — · local only*

Resolved via lu_pnv; in Band B in v01 payload

##### Potential natural vegetation shares (`pnv_shares`)
*implemented · BasinATLAS v1.0 · — · local only*

JSON object of {name: pct}; in Band B in v01 payload

#### Water Management

##### Degree of regulation by dams (`degree_of_regulation`)
*planned — not yet in the live API · BasinATLAS v1.0 · % · local only*

Not currently in signature

#### Wetlands

##### Wetland class ID (`wetland_class_id`)
*implemented · BasinATLAS v1.0 · — · local only*

Lookup: lu_wet

##### Wetland extent group 1 (`wetland_pct_g1`)
*implemented · BasinATLAS v1.0 · % · local + upstream*

u available in basin08

##### Wetland extent group 2 (`wetland_pct_g2`)
*implemented · BasinATLAS v1.0 · % · local + upstream*

s+u both in signature

### Band C — Bioclimatic

Contemporary climate baseline from BasinATLAS (WorldClim ~1970–2000 CE). These are long-run averages — for historical temperature and precipitation, Band T provides LMR anomalies relative to a 20th-century reference.

*32 variables in the catalog (26 implemented, 6 planned). Overview paragraph above is carried over from `API_guide.md`; confirm it still reads right in a codebook context, or replace.*

#### Climate Type

##### Biome name (`biome_name`)
*implemented · BasinATLAS v1.0 · — · local only*

Resolved via lu_tbi

##### Climate stratum code (`climate_stratum_code`)
*implemented · BasinATLAS v1.0 · — · local only*

Resolved via lu_cls

##### Climate zone name (`climate_zone_name`)
*implemented · BasinATLAS v1.0 · — · local only*

Resolved via lu_clz

#### Cryosphere

##### Permafrost extent (`permafrost_pct`)
*implemented · BasinATLAS v1.0 · % · local + upstream*

u available in basin08; placed in Band C in v01 payload

##### Snow cover annual (`snow_cover_annual`)
*planned — not yet in the live API · BasinATLAS v1.0 · % · local + upstream*

u available in basin08

##### Snow cover maximum (`snow_cover_max`)
*planned — not yet in the live API · BasinATLAS v1.0 · % · local only*

*No description yet in the catalog — needs a hand-written note.*

#### Freshwater Ecology

##### Freshwater ecoregion name (`freshwater_ecoregion_name`)
*implemented · BasinATLAS v1.0 · — · local only*

Resolved via lu_fec

##### Freshwater habitat type name (`freshwater_habitat_name`)
*implemented · BasinATLAS v1.0 · — · local only*

Resolved via lu_fmh

#### Land Cover

##### Land cover class name (`land_cover_name`)
*implemented · BasinATLAS v1.0 · — · local only*

Resolved via lu_glc; in profile_summary only

#### Moisture Balance

##### Actual evapotranspiration annual (`aet_annual`)
*planned — not yet in the live API · BasinATLAS v1.0 · mm/yr · local + upstream*

u available in basin08

##### Aridity index (P/PET) (`aridity_index`)
*implemented · BasinATLAS v1.0 · P/PET ×100 · local + upstream*

Global Aridity Index: stored as P/PET × 100. Value of 100 = P equals PET (arid/humid boundary). Values >100 = humid (P > PET); wet tropics reach ~1000. Global median ~68 (semi-arid). Higher = wetter. Key s/u divergence variable. u available in basin08

##### Climate moisture index (`climate_moisture_index`)
*planned — not yet in the live API · BasinATLAS v1.0 · — · local + upstream*

u available in basin08

##### Potential evapotranspiration annual (`pet_annual`)
*planned — not yet in the live API · BasinATLAS v1.0 · mm/yr · local + upstream*

u available in basin08

#### Precipitation

##### Precipitation annual (`precipitation_annual`)
*implemented · BasinATLAS v1.0 · mm/yr · local + upstream*

u available in basin08 as pre_mm_uyr

##### Precipitation monthly (`precipitation_monthly`)
*implemented · BasinATLAS v1.0 · mm · local only*

Jan–Dec array (mm); delivered as float[12] via v_basin0{6,8}_persist_rev2

#### Seasonality

##### Climate class (modality × phase cell) (`climate_class`)
*implemented · Derived (WO7) · — · derived*

Composed (modality, phase) cell — the two axes comma-joined, modality-first, with the phase term dropped for aseasonal basins (e.g. "One wet season, cool-season rain"; "Even year-round"). Labels compose from the axis labels only; classic names (Köppen-Mediterranean, monsoon, tropical twin-rains) appear as legend annotation, never as class names (WO7a label lock; a test enforces this). Backing column `cell` in app/db/climate_classes.py; served as the same-class Similarity lens /api/similarity/climate-class, and rendered in the Atlas tab as a client-side compose over the two axis choropleths (not a separate ~20-colour choropleth).

##### Climate rainfall modality class (`climate_modality`)
*implemented · Derived (WO7) · — · derived*

Discrete rainfall-modality class from the 12-month precipitation curve: arid (annual total < 100 mm/yr), aseasonal / even year-round (coefficient of variation < 0.20), one wet season, two wet seasons, or undetermined. Modality is emergent from curve shape via a vectorized Knoben ΔE 6- vs 12-month sinusoid fit (WO6b/WO7), not a peak-count threshold. Computed at startup from the persist-view monthly arrays and held in an in-memory index (app/db/climate_classes.py); served by /api/explorer/climate-class?axis=modality (Atlas tab, sandbox_v3). Köppen, monsoon, and tropical twin-rains types are subsets of these classes, not equivalent to them.

##### Peak precipitation month (`pre_peak_month`)
*implemented · Derived · month (0=Jan) · local only*

*No description yet in the catalog — needs a hand-written note.*

##### Peak temperature month (`tmp_peak_month`)
*implemented · Derived · month (0=Jan) · local only*

*No description yet in the catalog — needs a hand-written note.*

##### Precipitation seasonality concentration (`pre_concentration`)
*implemented · Derived · 0–1 · local only*

*No description yet in the catalog — needs a hand-written note.*

##### Precipitation–temperature correlation (`precip_temp_corr`)
*implemented · Derived (WO7) · r (−1 to 1) · derived*

Pearson correlation between the mean-centred 12-month precipitation and temperature curves. Positive = rain falls with the warm season (monsoon / continental); negative = rain falls in the cool season (Mediterranean). The continuous quantity underlying climate_phase — the warm-wet / cool-dry axis — validated in WO6b (Cell 19: 7/7 sign agreement with the s_d phase index, and defined for the 2,694 bimodal basins s_d cannot handle). Calendar-locked, hence hemisphere-blind on the warm/cool split (deferred register). Backing column `pt_corr` in app/db/climate_classes.py.

##### Precipitation–temperature phase class (`climate_phase`)
*implemented · Derived (WO7) · — · derived*

Discrete phase class from the direct Pearson correlation of the mean-centred 12-month precipitation and temperature curves, with a 5 °C seasonal-amplitude thermal gate: warm-season rain (r ≥ 0.50), cool-season rain (r ≤ −0.50), weak coupling (|r| < 0.50), or no temperature cycle (tmp_seas_amp < 5 °C). This is the warm-wet / cool-dry axis (WO6b Part E); the phase term is dropped for aseasonal basins. Served by /api/explorer/climate-class?axis=phase (Atlas tab). Calendar-locked and therefore hemisphere-blind on the warm/cool split — see deferred register.

##### Precipitation–temperature phase offset (`seas_phase_offset`)
*implemented · Derived · months (0–6) · local only*

*No description yet in the catalog — needs a hand-written note.*

##### Temperature seasonal amplitude (`tmp_seas_amp`)
*implemented · Derived · °C · local only*

*No description yet in the catalog — needs a hand-written note.*

##### Temperature seasonality concentration (`tmp_concentration`)
*implemented · Derived · 0–1 · local only*

*No description yet in the catalog — needs a hand-written note.*

#### Temperature

##### Temperature annual mean (`temperature_annual`)
*implemented · BasinATLAS v1.0 · °C · local + upstream*

Stored ×10 in basin08; divide by 10. u available in basin08 as tmp_dc_uyr

##### Temperature monthly (`temperature_monthly`)
*implemented · BasinATLAS v1.0 · °C · local only*

Jan–Dec array (°C, already ÷10); delivered as float[12] via v_basin0{6,8}_persist_rev2

##### Temperature monthly maximum (`temperature_max`)
*implemented · BasinATLAS v1.0 · °C · local only*

*No description yet in the catalog — needs a hand-written note.*

##### Temperature monthly minimum (`temperature_min`)
*implemented · BasinATLAS v1.0 · °C · local only*

*No description yet in the catalog — needs a hand-written note.*

#### Vegetation

##### Forest cover (`forest_cover_pct`)
*planned — not yet in the live API · BasinATLAS v1.0 · % · local + upstream*

Not currently in signature

##### Terrestrial ecoregion ID (`ecoregion_terrestrial_id`)
*implemented · BasinATLAS v1.0 · — · local only*

Lookup: lu_tec

##### Terrestrial ecoregion name (`ecoregion_terrestrial_name`)
*implemented · BasinATLAS v1.0 · — · local only*

Resolved via lu_tec

### Band D — Anthropocene

Present-day only. Exclude or qualify for pre-modern analyses; useful as a contrast baseline.

*14 variables in the catalog (7 implemented, 7 planned). Overview paragraph above is carried over from `API_guide.md`; confirm it still reads right in a codebook context, or replace.*

#### (Uncategorized)

##### Human Development Index (`hdi`)
*implemented · BasinATLAS v1.0 · — · local only*

*No description yet in the catalog — needs a hand-written note.*

#### Economic

##### GDP mean (`gdp_mean`)
*implemented · BasinATLAS v1.0 · USD/km² · local only*

*No description yet in the catalog — needs a hand-written note.*

#### Human Presence

##### Human footprint 1993 (`human_footprint_1993`)
*planned — not yet in the live API · BasinATLAS v1.0 · — · local + upstream*

Not currently in signature

##### Human footprint 2009 (`human_footprint_2009`)
*implemented · BasinATLAS v1.0 · — · local + upstream*

s+u both in signature

##### Nighttime lights index (`nighttime_lights`)
*planned — not yet in the live API · BasinATLAS v1.0 · — · local + upstream*

Not currently in signature

##### Population count (`pop_count`)
*planned — not yet in the live API · BasinATLAS v1.0 · — · local + upstream*

Not currently in signature

##### Population density (`pop_density`)
*implemented · BasinATLAS v1.0 · pk/km² · local only*

s only in signature; u available in basin08

##### Protected area (`protected_area_pct`)
*planned — not yet in the live API · BasinATLAS v1.0 · % · local + upstream*

Not currently in signature

##### Road density (`road_density`)
*planned — not yet in the live API · BasinATLAS v1.0 · m/km² · local + upstream*

Not currently in signature

#### Land Use

##### Cropland extent (`cropland_pct`)
*implemented · BasinATLAS v1.0 · % · local + upstream*

s+u both in signature; EarthStat ~2000 CE

##### Irrigated area (`irrigated_area_pct`)
*planned — not yet in the live API · BasinATLAS v1.0 · % · local + upstream*

Not currently in signature

##### Pasture extent (`pasture_pct`)
*implemented · BasinATLAS v1.0 · % · local + upstream*

EarthStat ~2000 CE; s+u both in signature

##### Urban area (`urban_area_pct`)
*planned — not yet in the live API · BasinATLAS v1.0 · % · local + upstream*

Not currently in signature

#### Water Management

##### Reservoir volume upstream (`reservoir_vol`)
*implemented · BasinATLAS v1.0 · — · upstream only*

u-only field; in Band D in v01 payload

### Band E — Coastality

Hydrological connectivity to the marine outlet.

*6 variables in the catalog (5 implemented, 1 planned). Overview paragraph above is carried over from `API_guide.md`; confirm it still reads right in a codebook context, or replace.*

#### Coastality

##### Basin touches coast (`coast_flag`)
*implemented · BasinATLAS v1.0 · — · local only*

*No description yet in the catalog — needs a hand-written note.*

##### Coastal fraction (`coast_fraction`)
*implemented · Derived · fraction (0-1) · local only*

Derived from coast_flag (0/1) via area-weighted weight sum. Convenience scalar complement to outlet_type. Areal-engine output only — not emitted by point signature.

##### Flow distance to marine outlet (`dist_sink_km`)
*implemented · BasinATLAS v1.0 · km · local only*

In Band E payload; raw basin08 units (m → divide by 1000 for km)

##### Outlet type (`endorheic`)
*implemented · BasinATLAS v1.0 · — · local only*

Derived from endo flag: exorheic/endorheic/coastal

##### Outlet type (`outlet_type`)
*implemented · Derived · — · local only*

Derived from endorheic (0/1/2) and coast_flag (0/1); exclusivity verified (coast=1 never co-occurs with endo>0). Areal-engine output only — not emitted by point signature.

##### Topological depth from coast (`topo_depth_from_coast`)
*planned — not yet in the live API · Derived · hops · derived*

Computed via next_down DAG traversal

### Band T — Temporal

Period-specific climate enrichment from LMR v2.1, volcanic event annotation from eVolv2k v4, and land-use history from HYDE 3.4. Requires from_year and to_year.

*14 variables in the catalog (13 implemented, 1 planned). Overview paragraph above is carried over from `API_guide.md`; confirm it still reads right in a codebook context, or replace.*

#### Land Use Temporal

##### Cropland extent (HYDE 3.4) (`hyde_cropland`)
*implemented · HYDE 3.4 · km²/pct · local only*

Per-epoch list of {year_ce, cropland_km2, cropland_pct, basin_area_km2, n_cells}; resolution: millennial BCE, centennial 0–1700, decadal 1710–1950, annual 1951–2025; _note discloses temporal resolution

##### Grazing land extent (HYDE 3.4) (`hyde_grazing`)
*implemented · HYDE 3.4 · km²/pct · local only*

Per-epoch list; grazing = pasture + rangeland; same resolution structure as hyde_cropland

##### Pasture extent (HYDE 3.4) (`hyde_pasture`)
*implemented · HYDE 3.4 · km²/pct · local only*

Per-epoch list; managed pasture subset of grazing land

##### Rangeland extent (HYDE 3.4) (`hyde_rangeland`)
*implemented · HYDE 3.4 · km²/pct · local only*

Per-epoch list; unmanaged/extensive grazing subset

#### Temporal Climate

##### PDSI (LMR v2.1) (`lmr_pdsi`)
*implemented · LMR v2.1 · — · series*

Annual series {year, pdsi} + pdsi_mean/min/max; 2°×2° nearest cell

##### Precipitation rate anomaly (LMR v2.1) (`lmr_precip_anomaly`)
*implemented · LMR v2.1 · mm/day · series*

Annual series {year, prate_anom_mm_day} + mean; converted from kg/m²/s

##### Sea-level pressure (LMR v2.1) (`lmr_slp`)
*planned — not yet in the live API · LMR v2.1 · hPa · point*

Not currently stored in temporal.lmr_climate

##### Temperature anomaly (LMR v2.1) (`lmr_temp_anomaly`)
*implemented · LMR v2.1 · K · series*

Annual series {year, air_anom_k} + air_mean_anom_k; anomaly vs. reference period

#### Volcanic Forcing

##### Hemispheric asymmetry per event (`evolv2k_asymmetry`)
*implemented · eVolv2k v4 · 0–1 · event*

asymmetry field within each volcanic_events object; 0=SH, 1=NH, intermediate=bilateral

##### Total VSSI in period (`evolv2k_vssi_sum`)
*implemented · eVolv2k v4 · Tg · derived*

Sum of vssi_tg for all events ≥ vssi_min in the query window

##### Volcanic event count in period (`evolv2k_event_count`)
*implemented · eVolv2k v4 · — · derived*

Count of events ≥ vssi_min (default 5 Tg) in the query window

##### Volcanic events in period (eVolv2k v4) (`evolv2k_events`)
*implemented · eVolv2k v4 · — · event*

List of {year_ad, month, vssi_tg, vssi_1sig, asymmetry, location, tephra}; default vssi_min=5.0 Tg

##### VSSI per event (eVolv2k v4) (`evolv2k_vssi_per_event`)
*implemented · eVolv2k v4 · Tg · event*

vssi_tg field within each volcanic_events object

##### Years since last major eruption (`evolv2k_years_since_major`)
*implemented · eVolv2k v4 · years · derived*

Years between year_end and the most recent event ≥ 10 Tg; null if none in window

## Derived variables

*TODO — rationale and computation for each `source: Derived` row (e.g. `coast_fraction`, `relief_range_m`, `relief_position`, `outlet_type`). Flagged in the TODO as “the one unavoidable hand-written block.”*

## Other / not yet banded

*Rows in the catalog outside the A–E/T band structure — not part of the `/api/signature` response today.*

##### LLM narrative summary (`narrative`)
*planned — not yet in the live API · Derived · — · output*

Claude API; non-specialist natural language summary
