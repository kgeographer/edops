# WO8 findings

**WO:** wo8_maplibre  
**Phase:** Surface  
**Branch:** surf_wo8

---

## F8.1 — GeoJSON sources for low-cardinality scopes; PMTiles deferred to polity choropleth

**Decision (CC's call per spec):** GeoJSON sources for all scopes through WO-d (single basin,
basin ring, polity boundary outline). PMTiles/vector tiles only when the polity choropleth
(WO-e) arrives.

**Reasoning:** The split is clean because the two cases are genuinely different in character:

- Single basin, ring, polity boundary: 1–10 features, fetched per-query, rendered as context
  geometry. GeoJSON trivially sufficient; no tileset infrastructure needed.
- Polity choropleth: 16k–38k basin units, one-variable paint, needs vector-tile performance.
  That's a qualitatively different problem.

The layer shell abstracts over source type — `shell.add(name, sourceSpec, layerSpecs)` takes
any MapLibre source spec. A GeoJSON source and a vector tile source are both just `{ type:
'geojson', data: ... }` vs `{ type: 'vector', url: 'pmtiles://...' }` at the call site. The
shell doesn't branch on them. So adopting GeoJSON now does not require restructuring the shell
when PMTiles arrives for WO-e; the choropleth just passes a different `sourceSpec`.

Pulling the PMTiles worker + style-layer `source-layer` references into WO8 would have added
real complexity for zero benefit at this stage.

---

## F8.2 — Layer shell works; accept gate clean on first run

The shell (`add`, `remove`, `restyle`, `clear`) was built to the pseudocode spec and proved
against the polity boundary use case:

- `shell.add('polity-boundary', { type: 'geojson', data: feature }, [line layer spec])` draws
  the outline.
- Re-calling `shell.add('polity-boundary', ...)` on slice change removes the old source +
  layers before adding the new ones — idempotent from the caller's side.
- `geojsonBbox(feature)` extracts `[west, south, east, north]` from any GeoJSON
  geometry/feature for `map.fitBounds`.

No Playwright tests needed updating — none were asserting on Leaflet internals.
313/313 tests pass.

---

## F8.3 — MapLibre migration notes (for reference on later WOs)

- **CDN**: `unpkg.com/maplibre-gl@4` for both CSS and JS.
- **Base map**: two raster sources (hillshade + OSM at 0.5 opacity) defined in the initial
  style object, matching the prior Leaflet visual closely.
- **Center/zoom**: MapLibre uses `[lng, lat]` (not Leaflet's `[lat, lng]`).
- **OSM subdomains**: `{s}` template not supported; specify tile URLs as an array
  (`['https://a.tile...', 'https://b.tile...', 'https://c.tile...']`).
- **Tab resize**: `map.invalidateSize()` (Leaflet) → `map.resize()` (MapLibre).
- **`sandbox.html` untouched** — the live Lookup page keeps Leaflet throughout.
