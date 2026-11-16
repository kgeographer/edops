# dash WO-04: arrival on the map, Get signature, small fixes

Draft of 16 Nov 2026, for Karl's review. A build, on the `dashboard` branch. Follows `dash_wo03_results.md`.

## Goal

Every way of choosing a place lands the same way: on the Map tab, zoomed to the basin the signature is about, with the query run and the other tabs filling. Get signature behaves consistently with that. Implement and evaluate; Karl judges the feel in a browser.

## Background

- WO-03 arrival: an example runs the query and selects the Profile tab after the result returns, so the Map tab shows first and then switches. A WHG lookup instead stops at the map, the user confirms, and clicks Get signature. These two behaviours are to be reconciled.
- Karl's direction: the first thing a reader sees after choosing a place is the map and the basin, the unit the signature describes. The Profile and other tabs are there when they turn to them.
- The Dashboard is moving toward a configurator: result first, controls adjust it. WO-03 added a last-run snapshot.

## Items

1. **Arrival on the map.** For a splash example, a Dashboard example and a confirmed WHG lookup, settlements and polities alike: select the Map tab, zoom to the basin (or the polity's basins), run the query, fill the other tabs. The Map tab becomes the default `view`. A permalink that names a `view` still opens that tab; select it before the query returns, with a short loading line, so there is no switch.

2. **Get signature.** The problem: after an automatic run the button is still live, and clicking it runs the same query again. With item 1, a confirmed lookup also runs on its own, so the button no longer starts a first run. Its remaining job is applying changed parameters (scope, level, bands, years, radius, polity slice), and the last-run snapshot tells whether the controls differ from what is displayed. Settle one behaviour for settlements and polities alike, and say why: for example, enabled only when the controls differ from the last run, or a re-run on change with the button removed. Then list what each control does afterwards (the table in `dash_predesign_note_01.md` §3, updated).

3. **"Load an example" stays visible** after a place is resolved, so the reader can switch examples. Remove the code that tries to hide it (`setResolvedPoint`).

4. **Profile route and the point.** `/api/profile` is keyed by level and `hybas_id`. Profile text also depends on the point (WO-01 item 2: point elevation, the point's ecoregion, river distances), so a future store serving any place will need it. Consider adding `lat` and `lon` to the route's contract now, while it is internal, and say what you decided.

5. **Small fixes.** The query-log docstring lists `link`. The splash and Dashboard version badges read from one setting (the value is Karl's). Re-run the full dashboard test folder.

## Provisos

- No changes to the Sandbox, the engine, the public API, `/profiles` or the stored profiles.
- No keep-current URL; no panel state.
- Example coordinates stay as they are.

## Out of scope

The sources statement and long-span caution; the Using EDOPS page; typed lookup on the splash; the profile store; Level 08 profiles.

## Deliverables and gate

- `dash_wo04_summary.md`, one page; `dash_wo04_results.md`, with anything that needs attention.
- Tests for each arrival path and for the chosen Get signature behaviour.

Gate: Karl checks in a browser. Choose Tbilisi on the splash: the Map tab shows the basin, the tabs fill, and Get signature does not re-run the same query. Change the level and apply it by the chosen behaviour. Look up a place in WHG and confirm it: the same arrival.

