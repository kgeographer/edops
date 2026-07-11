# WO12 findings — example-select standard + buffer on the map

**WO:** wo12_example-select
**Phase:** Surface
**Date:** 2026-07-05
**Branch:** surf_wo12 → merged to surface

---

## F12.1 — Buffer member_ids not in payload (pre-WO12)

The buffer neighborhood block did not expose member hybas_ids — only
`type/lat/lon/radius_km/level/n_units/unit_type`. The `basin_set` DataFrame
(which holds the ids) was internal to `areal_signature`. Added `member_ids:
basin_set['hybas_id'].tolist()` to the neighborhood block. One-line engine
change; existing tests unaffected (fixture equivalence test checks only three
specific keys).

## F12.2 — No existing route serves basin geometry by id list

No existing route accepts a hybas_id list and returns geometries. `/api/basin-preview`
resolves by point (ST_Covers) and is shared with sandbox v1 — untouched.
Added new read-only route `GET /api/basin/geom?ids=<csv>&level=6` returning a
GeoJSON FeatureCollection. hybas_ids are cast to `int` in the route; the DB column
returns floats but `member_ids` in the payload are Python ints — cast ensures the
honesty check set comparison works correctly.

## F12.3 — Honesty check passes for Timbuktu buffer

The set of hybas_ids returned by `/api/basin/geom` for the full Timbuktu 100 km
member list equals `neighborhood.member_ids` exactly. `TestBasinGeomRoute::test_full_member_set_honesty_check` confirms this.

## F12.4 — Buffer map: what the display reveals

Timbuktu sits at the intersection of multiple L06 basins — the unclipped fill +
dashed circle makes visually legible exactly what an arbitrary-boundary scope does:
the circle cuts across natural basin boundaries, including basins it only partially
contains. The display is not a deficiency of the buffer scope; it is the honest
depiction the spec intended.

## F12.5 — fitBounds must fire after map.resize(), not before

Draw functions initially called `map.fitBounds(bbox)` directly before the Map tab
was shown. With Map-first landing (WO12), the tab switch happens after the draw,
meaning `fitBounds` fired while the map container had zero dimensions — geometry
was drawn but rendered off-centre. Fix: draw functions return the bbox (not void);
sig handler registers `map.once('resize', () => map.fitBounds(bbox, {padding:40}))`
before calling `bootstrap.Tab...show()`. The `shown.bs.tab` listener calls
`map.resize()`, which fires the resize event, and fitBounds applies to a correctly
sized container.

## F12.6 — geojsonBbox extended for FeatureCollections

`geojsonBbox` only handled Feature/geometry. Passing a FeatureCollection produced
`undefined.coordinates` (silently caught), leaving fitBounds unregistered. Extended
to handle `type === 'FeatureCollection'` by collecting coordinates from all features.

## F12.7 — FIXTURE_URLS cleaned up; draw and ring get placeholders

All three fixture entries (`single`, `buffer`, `polity`) were dead code — each scope
has an explicit live handler branch. Removed all entries; `FIXTURE_URLS` is now
empty. The `loadFixture` function and its `else` fallthrough are retained but
unreachable by any current scope. `ring` and `draw` both have explicit placeholder
branches in the sig handler ("not yet wired") so neither errors silently.

## F12.8 — Test counts

- 11 new tests in `tests/test_areas.py` (4 `TestBufferMemberIds` + 7 `TestBasinGeomRoute`)
- 13 new Playwright tests in `tests/surface/test_sandbox_v2_ui.py`
  (3 `TestMapFirstLanding` + 4 `TestBufferMapLayers` + 2 `TestRingParksCleanly` + `load_timbuktu_buffer` helper)
- `wait_for_selector` in both load helpers updated to `state="attached"` (accordion is in hidden tab after Map-first landing)
- **355/355 tests pass; 14 skipped**
