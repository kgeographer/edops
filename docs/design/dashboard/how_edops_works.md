# How EDOPS produces a signature

Quick overview for a developer new to EDOPS. First draft 2026-11-13, a working document to be revised as the service changes. For detail, see `sandbox_cheatsheet.md` (what the Sandbox does, code-cited), `docsite/` (user docs) and `documentation/` (the variable catalog and source registry).

**What a signature is.** For a place or area on Earth, EDOPS returns a table of environmental variables (terrain, hydrology, climate, ecoregion, land use, and so on). Each variable is aggregated over the drainage basins the query covers, with a global percentile. Optionally it also returns time-specific context for a span of years.

## 1. What the user sets (Sandbox, Settlements tab)

- **Place.** A name, a gazetteer ID or lat/lon, resolved to one point (WHG gazetteer lookup).
- **Scope.** Single basin, basin ring or buffer (radius 1 to 2000 km). A separate Polities tab takes a polity and a date.
- **Level.** 6 or 8, the BasinATLAS scale.
- **Bands.** A to E are undated (physiographic, hydro-climatic, bioclimatic, Anthropocene, coastal). T is temporal.
- **Year span.** Used only when T is ticked.

## 2. What happens on "Get signature"

- **Browser** (`sandbox.html`)
  - Builds the request and calls `GET /api/areas` (the internal route, `routes_sandbox.py`).
  - Also fires `/api/signature?scope=basin&bands=ABCE` for the Analysis and Seasonality tabs, which need raw values.
- **Route**
  - Validates the parameters (level, years, polity active at that date) and dispatches by scope to the engine.
- **Engine** (`scripts/edop/areas/engine.py`), in three steps:
  - **Resolve** the geometry to a member set of basins, each with a weight.
    - Single basin: the basin containing the point.
    - Buffer: a geodesic circle intersected with basins, weighted by share of the circle.
    - Polity: the Cliopatria polygon for that date intersected with basins. At level 8, a precomputed crosswalk table does the intersection.
    - The ring is assembled client-side in the Sandbox, from the centre basin plus its neighbours.
  - **Aggregate bands A to E.**
    - The variable catalog (`documentation/EDOPS_variable_catalog_v0.4.tsv`) decides which variables exist.
    - For each variable the engine reads BasinATLAS values from PostGIS, applies the variable's aggregation method (area-weighted, dominant basin, class mixture, and so on), and ranks the result against all basins on Earth at that level.
    - Seasonality variables are derived from the monthly arrays.
  - **Band T, if asked.**
    - HYDE land use, LMR paleoclimate and eVolv2k volcanic events are computed on the query's own geometry.
    - Each source first asks the **source registry** (`documentation/EDOPS_source_registry.yaml`, read by `scripts/edop/areas/source_registry.py`) whether the span and place are covered.
    - A source outside its years is skipped and reported.
- **Assemble** one JSON payload.
- **Browser** draws the map, the signature accordion, the charts and the caveats.

## 3. Data sources, by what triggers them

- **Always:** BasinATLAS (HydroATLAS), plus values derived from it.
- **Polity scope:** Cliopatria polygons.
- **Band T:** HYDE 3.5 (-10000 to 2025), LMR v2.1 (0 to 2000 CE) and eVolv2k v4 (volcanic forcing). Each is span-limited.
- **Public basin call (`/api/signature`):** also an elevation service (OpenTopoData, falling back to Open-Meteo).
- **Place lookup:** the WHG gazetteer (it finds the point and is not part of the signature).
- **Planned:** GEDA, a regional data set (WO-05).

## 4. What comes back (`/api/areas`, one JSON object)

- `rows`: one object per variable.
  - Each carries its band, variable name and friendly name, units, method, and score (the global percentile).
  - It also has the raw value for a single basin, the coherence and modality badges, `n_units`, a status, optional `detail` (histogram), and a caveat key.
  - Band T rows live here too.
- `bands`: the list of bands included.
- `scope`: what was resolved (basin id or member ids, level, radius, unit count).
- `shortfall`: the share of the area covered by no basin (open water, for example).
- `temporal`: the Band T span.
- `caveats`: caveat texts keyed by name.
- `sources`: `used` and `not_applied`, each source with its name, version, citation, licence, and a reason when not applied.
- Polity scope adds `resolver` (polity name and slice), `member_ids` and `modality_post_pass`.

**The public API's shape differs.** `/api/signature?scope=basin` returns `id`, `up_area`, `geom_geojson`, the elevation fields, `profile_summary`, `signature_bands` (A to E, each a list of `{key, label, value}`), `meta` and `sources`. Its `scope=buffer` and `scope=area` return the engine's payload, with `rows` renamed to `variables` and a `meta` block added.

## Not yet covered

- The Analysis and Seasonality tabs (what they compute from the second request).
- Context, Similarity and the other tabs.
- The public API's request parameters in full (see `docsite/api.md`).
