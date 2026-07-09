# WO21 findings — Sequenced state management: forward-or-reset

**Branch:** `surf_wo21`
**Date:** 2026-07-09
**Status:** Complete — accept gate passed.

---

## Reveal/gate lifecycle as implemented

**Settlements path — resolve:**
1. User types → Resolve button / Enter → `resolveSettlement()` → WHG suggest → candidate list rendered on map + left column
2. User clicks candidate → `setResolvedPoint(lat, lon, name)`:
   - `_pointMarker` placed at resolved point (blue pin, survives scope switches)
   - WHG chip appears; example row (`#v3-example-row`) hidden — alternate entry removed
   - Scope wrap (`#v3-scope-wrap`) revealed; scope defaulted to `single`
   - `_drawScopePreview('single')` fires async (single basin polygon drawn on map)
   - Lower panel choropleth div revealed; intro text hidden
3. X chip button → `clearResolvedPoint()`: reverses all of the above except lower panel (choropleth stays revealed if it was already opened)

**Settlements path — example:**
1. User picks from example dropdown → resolve field + button locked (disabled)
2. `_pointMarker` placed at example coordinates
3. Scope set from example value; `_drawScopePreview(scope)` fires
4. Lower panel revealed

**Reset (full cold start):**
`resetSettlements()` = `clearResolvedPoint()` + choropleth clear + band reset + `map.flyTo({center:[10,20], zoom:1})`

---

## Polities path — as implemented

**Cold start:** search input enabled; slice select disabled; all band checkboxes (A–E + T) disabled; sig button disabled; T year row hidden.

**Resolve path (search):**
1. User types ≥2 chars → debounced fetch → `/api/polity/search` → dropdown
2. Dropdown click → `polityInput.disabled = false` (locks example), `selectPolity(name)`

**Resolve path (example):**
1. User picks from dropdown → `polityInput.disabled = true` (locks search), `selectPolity(name, targetYear)`

**`selectPolity(name, targetYear)`:**
- Fetches `/api/polity/slices` → populates + enables slice select
- Enables all band checkboxes
- Auto-fills Band T: `min(fromyear)/max(toyear)` across all slices (full lifespan, not single slice)
- Auto-checks Band T; reveals T year row
- Auto-selects slice containing `targetYear` (or first slice); calls `applySlice`

**`applySlice(idx, resolverYear)`:**
- Sets `#v3-resolver-year`
- Fetches `/api/polity/geom` → `shell.add('polity-boundary', ...)` → `_fitMap`
- Enables sig button; reveals lower panel

**Reset:** `resetPolities()` = all of the above reversed + `shell.clear()` + choropleth clear + `map.flyTo(world)`

---

## How scope-switch redraw is handled

`_drawScopePreview(scope)` is the single dispatch function:
- Clears all scope shell layers first
- `single` → `drawSingleBasin` → fitBounds
- `buffer` → `geodesicCircle` → shell.add('buffer-circle') → fetch `/api/basin/buffer` → shell.add('buffer-basins') → fitBounds to basins
- `ring` → fetch `/api/basin/ring` → `drawRingGeometry` → fitBounds

Called from: `setResolvedPoint`, example handler, scope-select change listener.

---

## Point marker

`_pointMarker` (MapLibre Marker, `color: '#2c5f8a'`) placed at `[lon, lat]` in `setResolvedPoint` and in the example handler. Survives scope switches because it is a bare marker, not a shell layer — `_drawScopePreview` clears only shell layers. Cleared in `clearResolvedPoint` and `resetSettlements`.

---

## Tab-switch hard reset

Implemented via `hide.bs.tab` (fires before animation, not after) on both fork-tab buttons:
- `v3-tab-settlements-btn` hide → `resetSettlements()`
- `v3-tab-polities-btn` hide → `resetPolities()`

`shown.bs.tab` was tried first but caused a timing bug: the new tab's content could render before the old tab's layers were cleared. `hide.bs.tab` fires synchronously before the animation, ensuring cleanup precedes any new content.

---

## Settlements vs Polities T asymmetry as wired

**Settlements:** Band T unchecked by default; `updateSigButton` gates on `hasPoint && scope` only — year fields are not required to enable Get Sig. T with empty years simply omits `from_year`/`to_year` from the request. Year fields filled by user or example selection.

**Polities:** T pre-checked and all bands disabled at cold start. On polity resolve, bands enable and T year row auto-fills from full polity lifespan. T is mandatory for polity — a polity has a temporal span by definition.

---

## Choropleth variable paint

Ported from `sandbox_v2.html` with v3-prefixed IDs. Three paths:

- **BasinATLAS** (`aridity_index`, `precipitation_annual`, `temperature_annual`, `cropland_pct`) — lazy-load PMTiles vector source; feature-state + RDBU legend.
- **LMR** (`lmr_temp_anomaly`, `lmr_precip_anomaly`) — reads from active tab's year inputs via `_activeBandTYears()` (Settlements: `v3-from-year`/`v3-to-year`; Polities: `v3-polity-from-year`/`v3-polity-to-year`).
- **HYDE** (`hyde_cropland`, `hyde_grazing`, `hyde_pasture`, `hyde_rangeland`) — `fromYr || 1000` as year; feature-state on basin-choropleth layer.

Paint layer is independent of the resolved query — "rides alongside" per WO21 spec.

---

## Buffer basin preview

`/api/basin/buffer?lat&lon&radius_km&level` (new endpoint) — PostGIS `ST_Intersects` geodesic buffer query returning GeoJSON FeatureCollection. `_drawScopePreview('buffer')` draws the dashed circle immediately, then fetches basins async and overlays them with `fitBounds` to the basin FC. Get Sig later replaces preview basins with the engine's `member_ids` set via `drawBufferGeometry` (shell idempotency handles the swap).

---

## Bugs caught / fixed during implementation

**F21.1 — Bootstrap d-flex + inline display:none conflict**
`#v3-buffer-extra` had both `class="d-flex"` and `style="display:none;"`. Bootstrap's `d-flex` is `display: flex !important`, overrides inline styles — element was always visible. Fix: removed `d-flex` from the class; JS uses `style.display = 'flex'` explicitly.

**F21.2 — T checkbox blocks Get Sig with empty years**
Initial `updateSigButton` gated on `!tChecked || (fromYear && toYear)`. Fix: simplified gate to `hasPoint && scope` only.

**F21.3 — Map not clearing on Settlements → Polities tab switch**
`shown.bs.tab` fired after animation; during the transition the reset had not yet run. Fix: switched to `hide.bs.tab` which fires before animation.

**F21.4 — `_basinLayerLoaded` not reset after `shell.clear()`**
After a tab switch called `shell.clear()`, the `basin-choropleth` source was removed but `_basinLayerLoaded` stayed `true`. Subsequent `loadBasinLayer()` calls were no-ops; `applyBasinVar` then crashed on `_layers['basin-choropleth'].sourceId` (undefined). Fix: reset `_basinLayerLoaded = false` in `clearResolvedPoint` and `resetPolities` after `shell.clear()`.

**F21.5 — LMR choropleth read wrong year inputs on Polities tab**
Choropleth listener read `v3-from-year`/`v3-to-year` (Settlements inputs) regardless of active tab; those fields are empty on Polities tab → LMR showed "Set Band T span" error. Fix: `_activeBandTYears()` helper reads from active tab's year fields.

**F21.6 — Example handler did not place point marker**
WHG resolve path placed `_pointMarker`; example path did not. Fix: added `Marker()` placement in example handler after coordinates are set.

---

## F15.10 skips

The F15.10 skip classes (`TestBasinChoropleth`, `TestLMRUI`, `TestHydeUI`) in `test_sandbox_v2_ui.py` target `sandbox_v2`'s unresolved state-model chaos. WO21 solves this on `sandbox_v3`, not by patching v2. The v2 skips remain; `test_sandbox_v3_ui.py` is the WO21 Playwright suite — 45 tests, all pass.

---

## State-management possibilities raised

None required Karl's input — the simple forward-or-reset model from the spec was sufficient. `hide.bs.tab` over `shown.bs.tab` for tab-switch reset was a CC judgment call (timing bug, not a design question).

---

## Tests

- 83 structural tests: `tests/surface/test_sandbox_v3.py`
- 45 Playwright tests: `tests/surface/test_sandbox_v3_ui.py`
- 7 route tests: `TestBasinBufferGeomRoute` in `tests/test_areas.py`
- **551 total tests pass, 50 skipped.**
