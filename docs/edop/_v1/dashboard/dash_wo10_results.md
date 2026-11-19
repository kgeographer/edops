# dash WO-10 results: edge cases WHG will hit

2026-11-19. Spec `dash_wo10_edge-cases.md`; summary `dash_wo10_summary.md`. Branch `dashboard`.

## Behaviour before (item 1)

Local server, 30 cases, five calls each: `/api/signature?scope=basin` at Levels 6 and 8; `/api/areas` with `scope=single_basin`, `basin_ring` and `buffer` (50 km, Level 8). All sent with `src=ui_aux` (not logged). Script: scratchpad `wo10_check.py` (not kept in the repo).

| Case | Basin (L6, L8), single basin, ring | Buffer 50 km |
| --- | --- | --- |
| Port, point in the port (Alexandria, Rotterdam, Venice, Piraeus, Lisbon, Mumbai, Hong Kong, Istanbul) | 200 | 200 |
| A made-up point just offshore of each port (six tried; coordinates picked by eye, 20 m to 2.2 km from the nearest basin; the ports themselves are the 200 row above) | 404 "No basin covers this point" (areas routes: "No basin covers the given point location") | 200 |
| Open water (Atlantic, Pacific) | 404, same texts | 404 "No basins fall within this buffer" |
| Tristan da Cunha | 404, same texts | 404 |
| Antarctica (-80, 0) | 404 | 404 |
| North Pole, 89.5 N, South Pole | 404 | 404 |
| Antimeridian: lon 180 at Fiji | 404 | 200 (basins within 50 km) |
| Antimeridian: -179.9 and 179.99 (Chukotka, Siberia) | 200 | 200 |
| lat 91, lat -91, lon 181 | 422, the framework's raw validation list (`[{'type': 'less_than_equal', 'loc': ['query', 'lat'], ...}]`) | 422, same |
| Missing lon | 422 "scope=basin requires: lon" (areas routes name their scope) | 422 |
| Non-numeric lat | 422, raw validation list | 422 |
| Swapped latitude and longitude (New York as -74, 40.71) | passes validation, lands in Antarctica: 404 | 404 |

- Three different 404 texts; none says why. No structured body.
- **Moved-point logic.** It lives in the profile scripts only: `scripts/edop/whg/wo08_units.py`, S8.3 "the snap" (`SNAP_M = 1000` m; a point inside no basin and within 1 km of one is moved to it). The engine and the public API do not snap.
- **Dashboard.** It shows the server's `detail` text (`_errorHtml`), so a 404 appears as the bare sentence. Not yet looked at in a browser.

## The distance (item 2)

Measured on the 6,205 WHG populated places that fall in no Level 6 basin (`gaz.whg_gaz`, `hybas_id_l06` null; 8,688 places of all kinds), distance to the nearest basin: under 1 km 59%, under 2 km 69%, under 5 km 74%, under 10 km 75%, under 50 km 78%; the rest are ocean islands hundreds of km away. Past 5 km each band adds 1 to 2%. Karl chose 5 km (about 94% of the places within 50 km of a basin). The profile pages' snap, 1 km until now, uses the same distance.

## Behaviour after

| Case | After |
| --- | --- |
| Point inside a basin | unchanged |
| Point outside every basin, within 5 km of one (WHG places Bulukumba, Arsuz, Pevensey Castle; the six made-up offshore points; Fiji across the antimeridian) | 200. The point is moved just inside the nearest basin; the response has `point_moved` (`hybas_id`, `distance_m`, `max_m`, `from`, `to`). Same on the public basin route, `/api/areas` single basin and basin ring, `/api/basin/ring`, `/api/basin-preview` (the map's outline) and Context and conjunction |
| No basin within 5 km (open water, Tristan da Cunha, Antarctica, the poles, swapped coordinates that land at sea) | 404, one wording on every route: "No basin within 5 km of this point; the nearest is N km away. It may be open water, or outside BasinATLAS coverage (Antarctica, some islands)." Body also has `reason` (`no_basin_nearby`) and `nearest_basin_km` |
| Buffer or area with no basin | 404, `reason` `no_basin_in_buffer` or `no_basin_in_area` |
| Latitude or longitude out of range, or not a number | 422, `detail` a sentence naming the parameter, e.g. "lat: Input should be less than or equal to 90 (got '91.0')"; the framework's list is kept in `errors` |
| Missing parameter | unchanged (already named it) |
| Dashboard | the map draws the nearest basin and zooms to it, with a note in its top-left corner ("This point lies outside the basin data; showing the nearest basin, N km away"); with no basin within 5 km the map keeps its view and the note says "No basin covers this place:" and the server's sentence; the Signature tab shows its own line when `point_moved` is present; errors show the new sentences. All placeholder wording (yellow). `/api/basin-preview` gained `point_moved` and `no_basin` |

Where: `snap_to_basin`, `resolve_point` and `SNAP_M` in `scripts/edop/areas/engine.py`; `NoBasinsError` carries `reason`; two handlers in `app/main.py`; `wo08_units.snap_point` delegates to the engine. The moved point is nudged inside by the nearest point of the basin shrunk by 3, 30 or 300 m (the earlier line-to-interior nudge left the basin on concave coasts).

## Changes to the public API (for the v1 release notes)

- `/api/signature` (scope basin) and `/api/areas` (single basin, basin ring): a point within 5 km of a basin now returns 200 where it returned 404; the response gains `point_moved`.
- 404 bodies for no basin gain `reason` (and `nearest_basin_km` for a point); `detail` stays a string with new wording.
- 422 validation bodies: `detail` is now a string (it was a list); the list is in `errors`. This applies to every route.

## Tests

`tests/dashboard/test_edge_cases.py` (15): inside not moved; three real WHG places moved at both levels; public basin and ring routes; the map's basin preview; the 404 body; bad coordinates; the profile snap equals the engine's. Two older tests changed with the contract: `tests/test_areas.py` (the new 404 wording and `reason`) and `tests/dashboard/test_page_background.py` (it still expected the pale background Karl had reverted; it now follows the CSS variable). Targeted run of the affected suites (public API, areas, band T, WHG, regionality, dashboard, engine, surface): 683 passed; the two changed files and the new one re-run: 172 passed. No full suite (merge gate only).

## Needs attention

1. Swapped latitude and longitude cannot be detected; a swapped point that lands on land is simply a different place.
2. The antimeridian: the snap's index prefilter does not wrap at 180, so a basin whose nearest part is across the line may be missed (Fiji's worked because the basin itself spans the line).
3. Context and conjunction use the snapped basin but measure from the original point.
4. Wording of the Dashboard notes is placeholder; the no-basin note repeats "No basin" (its own lead-in plus the server's sentence).
5. Karl's gate (Alexandria, Arsuz as the offshore point, Tristan da Cunha, a bad coordinate) passed 19 Nov: the API half run by CC, the Dashboard half by Karl.
