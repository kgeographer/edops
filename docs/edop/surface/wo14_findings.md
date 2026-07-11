# WO14 findings — Basin choropleth

**Date:** 2026-07-05
**Branch:** `surf_wo14`

---

## F14.1 — Shell works as-claimed for PMTiles; one extension (before param)

The WO8 shell claim was correct: `shell.add` passes the source spec directly to
`map.addSource`, which handles vector/PMTiles sources without modification. No restructuring
was required. The only extension: a `{ before }` option was added to `shell.add` (and
`map.addLayer`) to support insertion below existing layers. The shell API is otherwise
unchanged (`add`, `remove`, `restyle`, `clear`). This extension was triggered by lazy-load
ordering, not by PMTiles itself.

## F14.2 — Lazy load with `before`-insertion for layer ordering

The basin choropleth is loaded lazily on first variable select (not at `map.on('load')`).
Eager loading at map init caused PMTiles tile-fetch requests to contend with the ring sig
API call in concurrent tests, producing intermittent 20-second timeouts.

To ensure scope geometry (polity boundary, single basin, ring, buffer) always draws on top:
`loadBasinLayer()` reads `_layers` at call time and passes the first existing scope layer ID
as `before` to the shell's `add`. If no scope layers exist (user selects variable before
Get Signature), `before` is undefined and choropleth lands naturally below future scope layers
— because scope layers are always added after the choropleth once it's in `_layers`.

## F14.3 — All four static-path variables live; LMR/HYDE inert-present

BASIN_VARS (direct port from cliopatria): `aridity_index`, `precipitation_annual`,
`temperature_annual` (reverse=true), `cropland_pct` (green palette, fixed domain [0, 79.72]).
LMR and HYDE entries are present in the selector as `disabled` options so WO15 can enable
them without restructuring the menu. No error on select (disabled options are not selectable).

## F14.4 — Color ramp: RDBU per-variable, shared implementation

All four variables use the same `RDBU_PAL` + `interpRdbu(t)` / `interpTwo()` functions,
direct port from cliopatria. `reverse: true` for temperature (low=cold=blue). Cropland uses
a custom green ramp (`#e5f5e0 → #006d2c`, fixed domain). No per-variable ramp.
Cliopatria uses `su='s'` for all four (standardized); WO14 matches.

## F14.5 — `#v2-intro` restructured as reusable lower panel

`#v2-intro` is now a container (`class="px-1 mt-1"`) with two residents:
- `#v2-intro-text` — original intro paragraphs, hidden on sig load
- `#v2-choropleth` — basin variable selector + legend, always visible

All `getElementById('v2-intro').style.display = 'none'` calls updated to
`getElementById('v2-intro-text')` (2 locations: draw placeholder + main sig tail).
The choropleth controls remain visible regardless of signature state.

## F14.6 — Lazy-load `sourceId` bug caught by console-error test

First implementation captured `sourceId = _layers['basin-choropleth']?.sourceId` before
calling `loadBasinLayer()`, so the first call got `undefined`. Fixed by restructuring
`applyBasinVar` to call `loadBasinLayer()` first and read `sourceId` afterward. The
`test_no_console_errors_on_repaint` Playwright test caught this on the first run.

## F14.7 — Variable repaint is clean; `removeFeatureState` clears stale paint

On variable change, `map.removeFeatureState({ source, sourceLayer })` clears all prior
feature-state before the new paint loop. Selecting "— none —" also clears state and hides
the legend. No stale paint between variable switches.

## F14.8 — Test count

- BS tests (`test_sandbox_v2.py`): 71 (+4 from WO14 REQUIRED_IDS: `v2-intro-text`,
  `v2-choropleth`, `v2-basin-var`, `v2-basin-legend`)
- Playwright (`test_sandbox_v2_ui.py`): 53 (+11 from `TestBasinChoropleth`,
  and `test_intro_hidden_after_render` updated to `#v2-intro-text`)
- Explorer route (`test_explorer.py`): 3 new parametrized `test_values_wo14_vars_have_p10_p90`
  for `precipitation_annual`, `temperature_annual`, `cropland_pct`
- **Full suite: 395 pass, 14 DB-skipped.** Zero FAILs, zero unexplained warnings.
