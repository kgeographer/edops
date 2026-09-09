# EDOPS — Environmental Dimensions of Place Service

**EDOPS** is a FastAPI service that delivers structured environmental *signatures* for any terrestrial location on Earth. A signature summarizes the environmental character of one or more drainage basins — those containing a given point, or those falling within a given area (polity, region, neighborhood). Signature variables are drawn from the [HydroATLAS datasets](https://www.hydrosheds.org/hydroatlas), together with temporal layers for paleoclimate, land-use history, and volcanic forcing.

The service is designed to be generally useful for spatial humanities research: signature-based comparisons across historical places, environmental context for gazetteers, and exploratory analysis of environment–culture relationships.

EDOPS is a work in progress. A preliminary v0.4 of the platform is live at **[edops.computingplace.org](https://edops.computingplace.org)**.

---

## What a signature may contain

Signatures can include variables from any requested combination of *persistence bands* — groupings that give some temporal scoping apart from the explicitly temporal reconstructions in Band T.

| Band | Content                                                                                                                                                |
|------|--------------------------------------------------------------------------------------------------------------------------------------------------------|
| A | **Physiographic bedrock**: elevation, slope, relief, lithology, karst. Stable over geological time.                                                    |
| B | **Hydro-climatic baselines**: river discharge, runoff, groundwater, soils, wetlands (full upstream catchment).                                         |
| C | **Bioclimatic proxies**: temperature, precipitation, aridity, biome, ecoregion (contemporary baseline; Band T supersedes for period-specific queries). |
| D | **Anthropocene markers**: population density, cropland, human footprint, GDP (present-day only — exclude for pre-modern analyses).                     |
| E | **Coastality**: distance to marine outlet, endorheic flag, outlet type.                                                                                |
| T | **Temporal**: LMR v2.1 paleoclimate · HYDE 3.4 land-use · eVolv2k v4 volcanic forcing.                                                                 |

---

## Using it

- **Web** — [edops.computingplace.org](https://edops.computingplace.org): three interactive pages — Sandbox, Workbench, Data Explorer.
- **Documentation** — [edops.computingplace.org/docs](https://edops.computingplace.org/docs): page guides, a generated variable Codebook, the API Guide, and data-source notes. The single source of truth for what the pages and variables do — not duplicated here.
- **API** — `GET /api/signature?lat=…&lon=…` with optional `bands=ABCDET`, `from_year`/`to_year` (0–1998 CE, required with Band T), `level=6|8`. Areal queries at `GET /api/area` and `GET /api/areas`. Interactive schema at `/api/schema`; full reference at [/docs/api](https://edops.computingplace.org/docs/api/).

---

## What's new in v0.4

**Areal signatures** — signatures now compute over regions, not just points. Circular buffers, basin-ring neighborhoods, and arbitrary polygons (historical polities, custom study areas) all aggregate to the same signature shape, with area-weighted scoring and coherence diagnostics (concentrated/spread/split). New endpoints: `GET /api/area`, `GET /api/areas`.

**Sandbox, rebuilt** — a two-tab interface replaces the original Lookup page: **Settlements** (place search → basin signature) and **Polities** (search → historical boundary with a time-slice slider), both backed by an environmental similarity instrument.

**Workbench** (new) — a page for testing correspondence between environment and culture: 1,291 D-PLACE societies (subsistence, religion, isolates analysis), an exploration of one regionalization (see African Regions below), 258 World Heritage Cities with both environmental and text-based (Wikipedia) similarity search, and an OneEarth ecoregion browser.

**African Regions** (new) — a dedicated map tab for pre-colonial African subregions (Lovejoy et al. 2021), with environmental variable painting, a D-PLACE society overlay, and a per-region signature with an automated environmental-distinctiveness summary.

**Documentation site** — a full MkDocs site at `/docs`, with a variable Codebook and API Guide generated directly from the live catalog and route definitions, plus an interactive API explorer at `/api/schema`.

**Everywhere else** — unified navigation across all pages and a broad legibility/UX pass.

---

## Stack

- **Backend**: Python 3.12 · FastAPI · PostgreSQL 17 + PostGIS · psycopg3
- **Frontend**: MapLibre GL JS · PMTiles · Bootstrap 5 · Vanilla JS
- **Data**: HydroATLAS / BasinATLAS · LMR v2.1 · HYDE 3.4 · eVolv2k v4 · OneEarth ecoregions

---

## Research context

EDOPS is the environmental component of **Computing Place** (CEDOP), a spatial-humanities initiative exploring the environmental and cultural dimensions of place. v0.4 completes the areal-signature work — points, buffers, basin rings, and polity/region boundaries all resolve to the same signature. Current work explores correspondence between environmental signatures and cultural patterns (D-PLACE, Seshat, Cliopatria), a pilot feature on the Workbench page.

---

## Author

Karl Grossner · [kgeographer.org](https://kgeographer.org)
