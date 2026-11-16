# dash WO-04 results: arrival on the map, Get signature, small fixes

2026-11-16. Spec `dash_wo04_misc-fixes.md` (Fable). Branch `dashboard`. Commits: items 1 (with the tab order, the Profile tab hidden for polities and the Signature-tab spinner) `4d1de55`, 2 `4f1b571`, 3 `d2f12d3`, 4 `4700c85`, 5 `e4bf4c0`. Nothing is deployed or on `main`. All 76 dashboard tests passed in one run (about 3.5 minutes) after item 5; the only change since is the label default gaining a space ("v1.0 alpha"), whose two tests were re-run.

## Item 1: arrival on the map

- **Cause of the old switching** (and a correction to WO-03's results, which described only a Map to Profile switch): every run handler showed the Signature tab as soon as it started, and the loader selected the target tab only after the result returned, so an arrival went Map, then Signature (loading), then Profile. A scope preview that finished late also pulled the page to the Map after an early tab selection.
- **Changes** (`dashboard.html`): the settlement and polity runs no longer switch tabs. The zoom after a run uses `_fitMap`, because the old code waited for a map `resize` event that only fires when the Map tab has been hidden and shown. A confirmed place (a WHG candidate, a pasted identifier, typed coordinates, a marker click: all go through `setResolvedPoint`) and a polity chosen from the search now run on their own; the URL loader runs its own query. The scope preview takes a `showMap` flag so a URL arrival that names a tab is not pulled to the map.
- **Default `view` is `map`** (codec). A link that names `profile` or `signature` selects that tab once, before the result returns, with a loading line; links naming Analysis, Seasonality, Context or Similarity select the tab after the result (those tabs are disabled until their data arrives).
- **Map tab first** in the tab order (Map, Profile, Signature, Analysis, Seasonality, Context, Similarity, Atlas on the right). **No Profile tab on the Polities side** (the visibility rule that hid four tabs now hides five); a polity link naming `view=profile` opens the map and says nothing.
- **A spinner on the Signature tab label** shows while a run is in progress, for settlements and polities.
- **Left as it was:** clicking a ring member on the map still switches to the Signature tab (an explicit "show me this basin" action).
- **Tests:** every example arrives on the map and the page never shows another result tab; a link naming Profile or Signature selects exactly that tab once; a resolved place and a chosen polity fill the tabs and stay on the map; the spinner appears during a deliberately slow query and clears; the Profile tab follows the left Settlements and Polities tab; a polity chosen from the Dashboard's own dropdown has no Profile tab.

## Item 2: Get signature

**Behaviour.** The button is enabled only when the controls differ from the last successful run (or there is no successful run for this place), and is disabled while a run is in progress. After an automatic run it is disabled; changing a parameter enables it and changing it back disables it again. A failed run leaves it enabled for a retry. Settlements and polities follow the same rule with their own controls (level, bands, slice year for polities; scope, level, bands, Band T years, radius for settlements). **Why:** several changes (bands, years, radius, slice) can be applied in one run; the polity play loop does not fire a query per step; the last-run snapshot already tells whether the display is out of date; re-running on every change would need debouncing for checkboxes and year inputs.

What each control does now (the table in `dash_predesign_note_01.md` §3, updated):

| Control | Effect |
| --- | --- |
| Scope, buffer radius | Clears the results (as before), previews the new basins on the map, enables the button |
| Level | Enables the button. The map and the Context and Similarity tabs still follow the control at once; Signature, Profile, Analysis and Seasonality wait for the button |
| Band checkboxes, Band T years | Enable the button only; nothing else changes until it is pressed |
| Ring member | Unchanged: replaces Signature, Analysis, Seasonality, Context and Similarity with that basin's |
| Polity slice | The map updates; the Signature tab waits for the button, which is enabled |
| Context radius, Similarity lens and thresholds | Unchanged: re-run that tab only |
| Settlements / Polities | Unchanged: hard reset of the other |
| Reset | Clears everything and the address bar |

Seven browser tests (`test_get_signature_ui.py`): disabled after an automatic run; a changed band enables and changing back disables; a level change applied runs once, re-disables, updates the Signature tab and the link, and leaves the map; Band T years count; a scope change clears results and enables; a failed first run stays enabled; the polity button follows the same rule.

## Item 3: "Load an example"

Removed the code in `setResolvedPoint` and `clearResolvedPoint` that hid the row, and six lines that disabled the dropdown while resolving (it stayed disabled once a place was confirmed). Two browser tests: it stays visible and enabled after a typed-coordinates place resolves (choosing Timbuktu then goes to Timbuktu's link) and after an example arrival.

## Item 4: `/api/profile` and the point

**Decision:** `lat` and `lon` are in the contract now, optional, both or neither (422 otherwise, and 422 out of range). With them, the route returns a sample record only when that record's own place is within 10 km of the point asked about (404 "No stored profile for this place." otherwise); without them it returns the basin's record as before. The page passes the point and no longer does its own distance check. **Why:** profile text depends on the point (WO-01 item 2), so a store that serves any place will use `lat` and `lon` to assemble point statements; adding them while the route is internal costs nothing later, and the page does not change when the store arrives. Route tests: a point near the profile's place (including the Sandbox's Tbilisi point, 3 km away) gets the record; a point 26 km away in the same basin gets 404; `lat` alone or `lon` alone, and a latitude of 99, are 422. One page test: Rustavi (Tbilisi's basin, 26 km from the profile's point) shows the plain line.

## Item 5: small fixes

- `app/query_log.py` documents `src='link'`.
- One setting, `EDOPS_VERSION_LABEL` (`app/settings.py`, environment-overridable, default **"v1.0 alpha"**, Karl's value), feeds the splash badge and the shared header's pill on every page. The Sandbox, Explorer and Workbench differ from before by that badge line only (checked against copies saved before WO-03). Two tests.
- The signature version stays "0.5": it has been 0.5 since WO-04a (registry-era signature, held through GEDA) and moves to 1.0 at the v1 deploy.
- Full dashboard folder: 76 passed.

## Needs attention going forward

1. **Context and Similarity follow the level control at once** (as in the Sandbox) while the Signature tab waits for the button, so for a moment the tabs can show different levels. Making them wait means changing how they read the level; not done.
2. **Scope and radius changes still clear the results** (Sandbox behaviour) instead of keeping them until the button is pressed. Whether a configurator should keep the old result visible is a question for Opus.
3. **Polity search locks the polity "Load an example" dropdown** after a choice (existing behaviour; not in this WO). The same small removal as item 3 would change it.
4. **Tabs named by a link:** Analysis, Seasonality, Context and Similarity are selected after the result arrives, so a link naming one of them can still show the map first.
5. **No "ready" cue beyond the Signature spinner and the tabs enabling;** the Profile tab has no spinner of its own. Whether the arrival feels right is Karl's to judge in a browser.
6. **Prose still saying v0.4:** the About modal ("now at v0.4") and the Computing Place page's tile label. Karl writes that text.
7. **The pill changed on the Sandbox, Explorer and Workbench** (text only). The local server needs a restart to read the setting.
8. **Tests** are Playwright browser tests (marked `ui`, port 8766); they add rows to the local `public.query_log`; the folder takes about 3.5 minutes. The full suite was not run.
9. **Still open from WO-03:** the profile text describes the sample point, not always the displayed one; the profile store (files now, a database table later); the trailing-slash redirect and canonical host on the server.

## Gate (for Karl's browser check)

Choose Tbilisi on the splash: the Map tab shows the basin, the tabs fill, and Get signature does not re-run the same query. Change the level and apply it by the button. Look up a place in WHG and confirm it: the same arrival.
