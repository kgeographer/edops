# WO11 findings — single-basin map

**WO:** wo11_single-basin-map
**Phase:** Surface
**Date:** 2026-07-04
**Branch:** surf_wo11_single-basin-map → merged to surface

---

## F11.1 — Polity was already "first through the shell"

The WO spec described the single-basin polygon as "first geometry through the shell."
That was incorrect. `drawPolityBoundary` was wired to `shell.add('polity-boundary', ...)`
in WO8. Single-basin is more precisely the **first point-rooted scope geometry** on the map
— polity is search-rooted (no lat/lon). No functional consequence; noted for accuracy.

## F11.2 — Honesty check: both callers use the same containing basin

`single_basin_signature` (engine) and `/api/basin-preview` (map) both resolve to the
containing L06 basin for a given lat/lon. `drawSingleBasin` fetches the preview, extracts
`containing_basin.properties.hybas_id`, and compares it to `payload.neighborhood.hybas_id`
before drawing. A mismatch logs an error and skips the draw rather than showing a polygon
that disagrees with the signature.

Two tests in `TestSingleBasinMapHonestyCheck` (`tests/test_areas.py`) verify:
- `neighborhood.hybas_id` is present and non-null in the live `/api/areas?type=single_basin` response
- The value equals `containing_basin.properties.hybas_id` from `/api/basin-preview` for the same coordinates

Both pass, confirming there is no mismatch for Timbuktu.

## F11.3 — No tab switch on sig load

The WO spec suggested switching to the Map tab after the single-basin sig loads. Vetoed.
Polity's map-switch happens on **polity selection** (before the sig fetch), so the user
sees the boundary before requesting the sig. Switching to Map after sig load (single-basin)
would be jarring — the user just asked for a signature. Basin polygon is on the Map tab;
user navigates there themselves.

## F11.4 — Timbuktu basin is MultiPolygon

`/api/basin-preview` returns a `MultiPolygon` for the Timbuktu L06 basin. The Playwright
geometry-type test was initially written to assert `"Polygon"`; updated to accept
`("Polygon", "MultiPolygon")`. MapLibre and the shell handle both without modification.

## F11.5 — Test counts

Two new `TestSingleBasinMapHonestyCheck` tests in `tests/test_areas.py` (HTTP layer).
Two new `TestSingleBasinMapLayer` Playwright tests in `tests/surface/test_sandbox_v2_ui.py`.
**336/336 tests pass; 14 skipped** (live-server Playwright skips when DB endpoint absent).
