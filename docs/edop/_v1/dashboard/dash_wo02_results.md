# dash WO-02 results: permalink, an estimate

2026-11-15. Spec `dash_wo02_permalink-estimate.md` (Fable). Branch `dashboard`. Reading code and one scratch experiment; nothing in the app, the Sandbox or the server changed. Line numbers refer to `app/templates/sandbox.html` (4,631 lines) as of this date. The scratch script is `scripts/edop/dashboard/dash_wo02_scratch_loadorder.py` (headless browser against the local server; its run added a few rows to the local `public.query_log`).

## Earlier discussion of permalinks (for the record)

- `docs/design/dashboard/wo10_results.md` §D, `wo10a_profile-page-adjustments.md` §5, `WHG-profile_open-tems-post-WO7.md` (S9.1) and the v1 plan's "Parked ideas": a permalink reads `lat`, `lon`, `name`, `scope` and `level` from the URL and runs Get signature on load. EDOPS defines the URL and WHG builds it from a place's name and coordinates; not blocked on WHG. `logs/session_log_20261110.md` repeats it.
- `dash_predesign_note_01.md` (Fable): 5 to 10 hours for "URL parameters read on load"; "Show me" guides need each panel settable to a named state (not estimated).
- Not covered by any earlier note: polities, and a button that reflects the displayed state.

## Item 1: state today

The Sandbox reads only `?tab=settlements|polities` from the URL (line 4620). Everything else in the table is set by controls or by the page's own state variables. The whole page script is a closure, `(() => { … })()` (line 764), and exposes nothing on `window`.

| State | Where it lives | Settable from code | Notes |
| --- | --- | --- | --- |
| Settlements / Polities tab | `v3-tab-*-btn` | Yes | As `?tab=` does |
| Place: lat, lon, name, gazetteer links | `currentLat`, `currentLon`, `_currentPlaceName`, `_currentPlaceLinks` | Yes | The example handler (2492 to 2532) sets them with no WHG call; the typed lookup (`resolveSettlement`, 1186) calls WHG |
| Scope | `v3-scope-select` (single, ring, buffer) | Yes | Then `applyScope`. UI values differ from the API's (`single` is `single_basin`, `ring` is `basin_ring`) |
| Buffer radius | `v3-radius` | Yes | Applied on Enter (`_applyRadius`) |
| Level 6 or 8 | `v3-level`; `v3-polity-level` on Polities. `_activeLevel()` reads the active one | Yes | Disabled until a place is set, and when the map variable is an LMR or HYDE grid layer |
| Bands | `v3-band-A`…`T`; polities `.v3-polity-band-chk` | Yes | A to E on, T off by default |
| Band T years | `v3-from-year`, `v3-to-year`; polities fill them from the slice span | Yes | |
| Ring member | `_committedRingMemberId` (a `hybas_id`) | Moderate | `commitRingMember` needs `_ringData` loaded. A re-run re-selects by id (2980) |
| Polity, slice, year | `_polityName`, `_politySlices` (fetched), `_polityCurrentIdx`, hidden `v3-resolver-year` | Yes | `nearestPolitySlice(year)` and `applySlice(idx, year, skipResig)` exist; `selectPolity` ignores its `targetYear` and starts at slice 0 |
| Active result tab | Map, Signature, Analysis, Seasonality, Context, Similarity, Atlas | Yes | Analysis to Similarity are disabled until a parallel `/api/signature` returns (3076 to 3091) |
| Context radius | Radios 250, 500 (default), 1000, 2500 | Yes | The level can force 1000 (898 to 911); the panel renders on tab shown |
| Similarity | `v3-cj-lens` plus selects `ratio`, `cv`, `corr`, `tlevel`, `trange`, `elev`, `relief` | Yes | The lens decides which others show (`_cjUpdateBandVisibility`); each change re-runs the panel |
| Map variable and layers | `v3-basin-var`; rivers, cities, countries checkboxes; basemap toggle | Yes | LMR and HYDE choropleths load asynchronously and disable the level control |
| Band T panel | Per-variable sliders `v3-t-sl-<variable>`, built per payload (`wireTSliders`, 3311) | Moderate to hard | DOM state of each payload |
| Open accordions | Bootstrap collapse; Band T open by default when present (3384) | Moderate to hard | The user's own openings |
| Atlas | `v3-atlas-view`, `v3-atlas-level` | Yes | Place-independent |
| Map viewport | MapLibre | Hard | Auto-fits after a result; restoring a view races with it |

Examples are hard-coded `<option>` elements: 5 settlements (`lat,lon|name|from|to`, lines 123 to 127) and 8 polities (`polity|NAME`, lines 252 to 259). "Load an example" sets controls and does not run the query.

**Displayed state versus control state.** The Sandbox keeps no record of the parameters of the last run; each click rebuilds them from the controls. Changing the level repaints the map and refreshes Context and Similarity if visible (878 to 888), but leaves the Signature, Analysis and Seasonality tabs at the old level until Get signature is clicked again. A button reflecting what the user sees needs a last-run snapshot.

## Item 2: minimal handoff

- **Place in the URL:** `lat`, `lon`, `name` (the S9.1 decision). No external call is needed, because the example path sets the place directly; `name` is a label. A WHG place id is a poor fit (WHG does not expose it in its UI, per project notes). An example key is not needed: the splash's links can themselves be the permalinks. Mirror the API's parameter names (`scope`, `level`, `bands`, `from_year`, `to_year`, `radius_km`, `polity`, `year`) and add a version parameter.
- **Load order:** validate and sanitise; set the place (as the example handler does); set scope, level, bands and years; run; wait for the result; select the tab.
- **Measured** (scratch script; one run each, headless Chromium, local server, warm; map tiles not waited for): Tbilisi 1150 to 1250: page load 0.8 s, Get signature enabled 0.19 s after choosing the example, Signature tab filled 1.81 s after the click, Analysis, Seasonality, Context and Similarity tabs enabled 1.82 to 1.83 s. Northern Song: page load 1.4 s, polity button enabled 0.14 s (6 slices, resolver year 961), Signature filled 2.51 s. No page errors.
- **Fragile points:** the closure (the loader must live inside the clone's script, or the clone exposes a hook); the Get signature click handler is async and returns no handle (a "ready" signal is needed; the cleanest fix is to pull the run into a function that returns a promise); `selectPolity` ignores its year and returns silently when `/api/polity/slices` fails; a coastal point can 404 on single-basin (known gap) and the page then shows an error message; Level and Get signature stay disabled until a place is set; URL text is untrusted (length limit, `textContent`, range checks on lat and lon).
- **Examples:** hard-coded in the HTML. A shared list (one small file rendered into both the splash and the Dashboard) is easy.
- **Query log:** a permalink arrival logs as `src=ui` with `place_name`, identical to a user's click. Whether to tag arrivals (for example `src=link`) is a decision for Karl.
- **Hours** (an estimate from reading the code): URL parsing, validation and sanitising 1 to 2; settlements loader with the run-as-promise refactor 3 to 5; polity loader 2 to 4; shared examples list 1 to 2; error display and edge cases 1 to 2; Playwright tests 2 to 4. **Total 10 to 18; settlements only with minimal tests, 5 to 9.** Fable's earlier 5 to 10 appears to have covered settlements without polities or tests.

## Item 3: full permalink

- **Capture on click** needs a `getState()`, the last-run snapshot and a button; it does not touch every control. **Keep-current** (the URL updated as the user acts, so refresh and back work) needs about 25 controls hooked, with debouncing for sliders and the polity play loop; it is the larger piece and optional.
- **Easy:** tab, place, scope, level, bands, years, radius, active result tab, Context radius, Atlas. **Moderate:** polity and year, ring member (set `_committedRingMemberId` before the click, one extra member request), Similarity (set the lens first), map variable and layers. **Moderate to hard:** Band T panel sliders and open accordions. **Hard:** the map viewport (leave out).
- **To avoid rework at item 2:** one `applyState(state)` from a state object, with `getState()` as its inverse and the URL codec outside both; the run as a promise, once; the last-run snapshot; the API's parameter names and a `v` parameter, unknown parameters ignored; stable tab keys, not positions; apply order tab, place, scope, level, bands, years, run, wait, then panel settings (ring member, Context radius, Similarity, tab).
- **Hours, on top of item 2:** last-run snapshot and `getState()` 3 to 5; `applyState` for the extras 8 to 12; codec for the extra parameters with versioning 2 to 3; button, copy action and confirmation 2 to 3; tests for each restorable state 4 to 8. **Extra 19 to 31; keep-current 6 to 12 more.** About 30 to 50 hours in all with item 2. The "Show me" guides would reuse `applyState`, so this also sizes most of them. The least certain figure is the Band T slider and accordion state.

## Item 4: routing

- `/dashboard` is a plain page route (`app/web/pages.py:52`). It returns 200 with or without a query string and ignores unknown parameters. No change needed.
- `/dashboard/` returns 307 to the unslashed path and keeps the query string, but its `Location` is absolute and built from the request host. Behind nginx the scheme and host depend on forwarded-header handling, which is not visible in the repo. **Unverified:** `curl -sI https://edops.computingplace.org/dashboard/` on the server would show it.
- `/sandbox/lookup` returns 301 to `/sandbox` and drops the query string (checked locally). New links should not use legacy paths.
- `dashboard.html` has `<meta name="robots" content="noindex">`. Fine for arrivals; at launch decide on noindex or a canonical URL, since each parameter variant is otherwise indexable.
- nginx (from `MAINTAIN_DEPLOY.md`, not from the server's files): only `/api/` is cached, keyed on the full URI; everything else passes to the app. A page request with a query string needs no nginx change. `edops.computingplace.org`, `computingplace.org` and `edops04` all serve the app; which host WHG links to is a decision (suggest `edops.computingplace.org`).
- The clone needs the GA tag (`_ga.html`); `_qlog` fires a `signature_request` event, so arrivals also appear in GA. Use the query string, not a fragment, so arrivals show in access logs.

## Needs attention going forward

1. **Last-run snapshot** (item 1): displayed and control state can differ now; the button must define what it captures.
2. **Run as a promise** and the ready signal (item 2); the clone's script is a closure.
3. **Polity gaps:** `selectPolity` ignores its year and fails silently; the loader needs the year and visible errors.
4. **Decisions for Karl:** tag permalink arrivals in the query log; which host WHG links to; noindex or canonical at launch; capture on click only, or keep-current as well.
5. **Server check** of the trailing-slash redirect (item 4).
6. **Existing tests** may use the Sandbox's element ids (the code mentions a hidden element "kept for test compat"); not checked. The clone should keep ids or the tests change.
7. **Dashboard layout is undecided** (the Profile tab, the left panel); the state schema should use stable names so the layout can change.
8. **Estimates** are from reading the code, not building; single timings, one run each, local; Band T slider and accordion state is the least certain.
9. **Legacy paths** drop the query string.
