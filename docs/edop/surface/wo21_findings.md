# WO21 findings — Sequenced state management: forward-or-reset

**Branch:** `surf_wo21`
**Date:** 2026-07-09
**Status:** Settlements track complete; Polities tab next.

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
1. User picks from example dropdown → resolve field locked (disabled)
2. Scope set from example value; `_drawScopePreview(scope)` fires
3. Lower panel revealed

**Reset (full cold start):**
`resetSettlements()` = `clearResolvedPoint()` + choropleth clear + band reset + `map.flyTo({center:[10,20], zoom:1})`

---

## How scope-switch redraw is handled

`_drawScopePreview(scope)` is the single dispatch function:
- Clears all scope shell layers first
- `single` → `drawSingleBasin` → fitBounds
- `buffer` → `geodesicCircle` → shell.add('buffer-circle') → fitBounds (basin polygons come on Get Sig)
- `ring` → fetch `/api/basin/ring` → `drawRingGeometry` → fitBounds

Called from: `setResolvedPoint`, example handler, scope-select change listener. Prior to this refactor, all three duplicated the draw logic independently.

---

## Point marker

`_pointMarker` (MapLibre Marker, `color: '#2c5f8a'`) placed at `[lon, lat]` in `setResolvedPoint`. Survives scope switches because it is a bare marker, not a shell layer — `_drawScopePreview` clears only shell layers. Cleared in `clearResolvedPoint` and `resetSettlements`.

---

## Tab-switch hard reset

Not yet wired (next step in WO21). Settlements tab resets on `v3-reset-btn` click only.

---

## Settlements vs Polities T asymmetry as wired

Settlements tab: Band T unchecked by default; `updateSigButton` gates on `hasPoint && scope` only — year fields are not required for Get Sig to enable. When T is checked with empty years, the request omits `from_year`/`to_year` (handled in `buildSingleBasinUrl`). Year fields are filled by the user or by example selection.

Polities tab: T pre-checked and all bands disabled at cold start (not yet wired beyond HTML structure).

---

## Choropleth variable paint

Ported directly from `sandbox_v2.html` with v3-prefixed IDs. Three paths:

- **BasinATLAS** (`aridity_index`, `precipitation_annual`, `temperature_annual`, `cropland_pct`) — `loadBasinLayer()` lazy-loads PMTiles vector source on first use; `applyBasinVar()` fetches `/api/explorer/values`, sets feature-state for each basin, renders RDBU legend.
- **LMR** (`lmr_temp_anomaly`, `lmr_precip_anomaly`) — `applyLMRChoropleth()` reads `v3-from-year`/`v3-to-year`; shows "Set Band T span" message if empty. Bakes `fc` color into `lmr_notches.geojson` feature properties, calls `setData`. Requires `from_year`/`to_year` to be set.
- **HYDE** (`hyde_cropland`, `hyde_grazing`, `hyde_pasture`, `hyde_rangeland`) — `applyHydeChoropleth()` reads `v3-from-year || 1000` as the year parameter, fetches `/api/hyde/values`, feature-state paint on basin-choropleth layer.

Paint layer is independent of the resolved query — "rides alongside" per WO21 spec.

---

## Bugs caught / fixed during implementation

**F21.1 — Bootstrap d-flex + inline display:none conflict**
`#v3-buffer-extra` had both `class="d-flex"` and `style="display:none;"`. Bootstrap's `d-flex` is `display: flex !important`, which overrides inline styles — element was always visible. Fix: removed `d-flex` from the class; `applyScope('buffer')` sets `style.display = 'flex'` explicitly.

**F21.2 — T checkbox blocks Get Sig with empty years**
Initial `updateSigButton` gated on `!tChecked || (fromYear && toYear)`. Since year fields start empty, checking T immediately disabled Get Sig with no way to re-enable short of filling years. Fix: simplified gate to `hasPoint && scope` only — year fields are not a prerequisite for the button.

---

## F15.10 skips

The Playwright skip suite (`test_sandbox_v2_ui.py` `F15.10` class) targets `sandbox_v2` state. WO21 is building `sandbox_v3` — a new page, not a patch to v2. The F15.10 skips remain skipped pending a dedicated `test_sandbox_v3_ui.py` Playwright suite (later step in WO21 or a dedicated WO).

---

## State-management possibilities raised

None required Karl's input — the simple forward-or-reset model from the spec was sufficient and no alternative was tempting enough to flag.

---

## Tests

83 structural tests in `tests/surface/test_sandbox_v3.py`. All passing. No Playwright suite yet for v3.
499 total tests pass, 50 skipped.
