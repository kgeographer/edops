# EDOPS — Environmental Dimensions of Place Service

**EDOPS** is a FastAPI service that delivers structured environmental *signatures* for any terrestrial location on Earth. A signature summarizes the environmental character of the drainage basin containing a given point, drawing on HydroATLAS (16,000+ Level 6 sub-basins), climate baselines, terrain, and ecoregion data — plus temporal layers for paleoclimate, land-use history, and volcanic forcing reaching back two millennia.

The service is designed for spatial humanities research: signature-based comparisons across historical places, environmental context for gazetteers, and exploratory analysis of environment–culture relationships.

Live at [edops.computingplace.org](https://edops.computingplace.org)

---

## What a signature contains

| Band | Content |
|------|---------|
| A | Basin geometry and topology (area, perimeter, elevation range, order) |
| B | Hydrological regime (discharge, runoff, soil moisture, water table) |
| C | Climate baselines (temperature, precipitation, aridity, PET) |
| D | Terrain (slope, aspect, roughness) |
| E | Land cover and soil properties |
| T | Temporal: LMR v2.1 paleoclimate · HYDE 3.4 land-use · eVolv2k v4 volcanic forcing |

---

## Tools

### Lookup (`/sandbox/lookup`)
Place-name search via World Historical Gazetteer → basin assignment → full Band A–T signature with neighborhood map. Band T delivers 200-year temporal charts for PDSI, temperature, precipitation anomalies, and volcanic sulfur injection. Supports L6 and L8 basin resolution.

### Explorer (`/sandbox/explorer`)
MapLibre GL JS choropleth across all 16,397 Level-6 sub-basins worldwide. Three tabs:
- **Global** — single-variable choropleth with histogram and LISA cluster map
- **Regions** — six synchronized regional panels (East Asia, South Asia, Southwest Asia, Mediterranean, Mesoamerica, Pacific Northwest)
- **Compare** — bivariate scatter with OLS fit, regional Spearman correlations, and region-highlight interaction

---

## API

The core endpoint:

```
GET /api/signature?lat=LATITUDE&lon=LONGITUDE
    [&bands=ABCDET] [&from_year=N] [&to_year=N] [&level=6|8]
```

Returns `profile_groups` for each requested band. Band T requires `from_year` and `to_year` (0–1998 CE).

See `documentation/` for schema details and use cases.

---

## Stack

- **Backend**: Python 3.12 · FastAPI · PostgreSQL 17 + PostGIS · psycopg3
- **Frontend**: MapLibre GL JS · PMTiles · Bootstrap 5 · Vanilla JS
- **Data**: HydroATLAS / BasinATLAS · LMR v2.1 · HYDE 3.4 · eVolv2k v4 · OneEarth ecoregions

---

## Research context

EDOPS is part of **Computing Place** (CEDOP), a spatial humanities initiative exploring environmental and cultural dimensions of place. Phase 3 will add signature aggregation for areal study regions (historical polities, ecoregion zones). Phase 4 will test correspondence between environmental signatures and cultural patterns using D-PLACE, Seshat, and Cliopatria.

---

## Author

Karl Grossner · [kgeographer.org](https://kgeographer.org)
