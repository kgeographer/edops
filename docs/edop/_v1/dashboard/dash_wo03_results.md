# dash WO-03 results: splash, Dashboard clone, example handoff

2026-11-16. Spec `dash_wo03_splash-dashboard-clone.md` (Fable) with its "Adjustments after review". Branch `dashboard`. Commits: item 1 `2f9b949`, item 2 `623ca26`, item 3 `c1c6dee`, item 4 `edcaae5`, item 5 `fa257f4`; item 6 and the Reset fix not yet committed. Nothing is deployed or on `main`. The Sandbox, Explorer and Workbench render byte-for-byte as before (compared with copies saved before the work).

## Item 1: examples list

`app/web/dashboard_examples.json`: 9 settlements in WO-10 order (Timbuktu, Tbilisi, Santa Fe, Kaifeng, Lviv, Poltava, Chaco Canyon, Alexandria, Utqiagvik) and the Sandbox's 8 polities. Timbuktu, Tbilisi, Santa Fe and Kaifeng use the Sandbox's coordinates, which fall in the same Level 06 basin as the stored profiles (0.4 to 5.9 km from the profile points); the other five use the WO-09 coordinates. San Francisco (no profile) and Tristan da Cunha (no basin; it was only a proof of the no-basin message) are not examples. Labels are placeholder wording. `scripts/edop/dashboard/dash_wo03_check_examples.py` runs every example against the local server: all 17 return results at Level 06 (settlements 52 rows each, with the returned basin equal to the stored profile's; polities 59 to 89 rows at their first slice).

## Item 2: splash

`app/templates/edops.html` is the new splash (served at `/edops`, and at `/` when the host contains "edops"): header with the EDOPS logo, About EDOPS and Documentation (the existing modals, GA tag and runtime contact link kept); a "what it is" block; a "See a place" row with two dropdowns; three tiles (Dashboard, Using EDOPS, Data Explorer, with the two new tile images); a Computing Place line. Text is placeholder, marked with a yellow bar or highlight (search the templates for `ph` and `ph-inline`). Each example's Dashboard URL is built once in `app/web/pages.py` (`_dashboard_examples()`): `/dashboard?lat=…&lon=…&name=…&v=1` for settlements, `/dashboard?scope=polity&polity=…&v=1` for polities (defaults left out). Choosing an example navigates. Five tests in `tests/dashboard/test_splash.py`.

## Item 3: Dashboard clone

`app/templates/dashboard.html` is a copy of `sandbox.html` (4,590 lines against 4,631), keeping every element id, with the GA tag, `noindex` and the title "EDOPS Dashboard". A Profile tab is leftmost, disabled until a result. Both dropdowns are drawn from the shared list and navigate to the example's URL. The shared header partial gains a Dashboard and Using EDOPS variant (Home, Dashboard, Using EDOPS, Data Explorer); every other page's header output is unchanged. `/using` is a placeholder page; `_guide_dashboard.html` and `_guide_using.html` show the documentation home until real guides exist.

## Item 4: Profile tab

An internal route, `/api/profile?level=6&hybas_id=…` (`app/api/routes_dashboard.py`), returns the stored record for a basin or 404; it reads the ten sample records now (nine with a basin) and is the contract a later store will keep. The tab asks it with the `hybas_id` the query returned and shows the profile when the record's own place is within 10 km of the displayed place (the stored text names that place and its point); otherwise it says "Profiles cover single-basin queries at Level 06 for a few places so far", plus marked placeholder text. After a polity run it says profiles are for settlements. Rendering is `app/static/js/edops_profile.js`, extracted from the `/profiles` page's own functions without its template view, draft captions and portal buttons; `/profiles` is unchanged. Styles are in a new `app/static/css/dashboard.css`.

## Item 5: handoff

`app/static/js/edops_permalink.js` is the codec (parse, validate, build). Parameters mirror the API's names (`lat`, `lon`, `name`, `scope` as `single_basin`, `basin_ring`, `buffer` or `polity`, `level`, `bands`, `from_year`, `to_year`, `radius_km`, `polity`, `year`) plus `v`, `member` (a ring member's `hybas_id`) and `view` (the tab). It sanitises the name, range-checks numbers and ignores unknown parameters. `applyState(state)` in the page sets the controls, runs the query, waits for it and selects the tab. The two Get signature handlers are now functions that return promises (the buttons call them as before). A polity link with a `year` opens the nearest slice through the loader; `selectPolity` is unchanged. Arrivals log as `src=link`. Visible messages cover bad parameters, an unknown polity, a ring member not in the ring, an unavailable tab and a failed query. 29 browser tests: every example arrives without error (each settlement shows its stored profile, each polity lands on the Signature tab); a polity link with a year, and ring, buffer and Level 08 links, arrive; seven kinds of bad link each say why; unknown parameters and plain visits are quiet; arrivals reach the query log as `link`; the codec round-trips.

## Item 6: permalink button

A "Copy link" button above the tabs appears after a successful run and hides on Reset or a failed link. The page records the parameters of the last successful run; `getState()` combines them with the ring member shown and the active tab, and the codec builds the URL, which is copied to the clipboard and also shown in a box as a fallback. On the public hosts (`computingplace.org`, `www.computingplace.org`) the link carries `edops.computingplace.org`; local and test hosts keep their own. Panel controls (sliders, thresholds, Context radius, Similarity, map variable, accordions) are not captured. Reset now also clears the link from the address bar and any message. Eight browser tests (`tests/dashboard/test_permalink_ui.py`): hidden before a run, after Reset and after a failed link; round trips for a single basin keeping its tab and result, the Seasonality tab, Band T years, a buffer radius, a ring member and a polity slice.

## Tests

All 52 dashboard tests passed in one run (about 3 minutes) before the Reset fix; after it, the two Reset tests pass and the full folder has not been re-run. The 38 related existing tests I ran (public API surface, profiles page, WHG profile tests, API examples) pass. The full suite was not run (it is for a merge gate). The browser tests are marked `ui`, start the app on port 8766 and add rows to the local `public.query_log`.

## Needs attention going forward

1. **UX of arrival from the splash (for Opus).** Choosing an example on the splash opens the Dashboard on its Map tab first and, within about a second or so, switches to the Profile tab. The cause as far as the code shows: the page renders with the Map tab active (its markup default), and `applyState` selects the target tab only after the query has run and the result is in (the query takes about two seconds in my timings). The link already names the target tab (`view`) before the page loads. No fix was made; Karl has ideas to put to Opus.
2. **Profile text describes the sample point.** For Timbuktu, Tbilisi, Santa Fe and Kaifeng the examples use the Sandbox's coordinates, 0.4 to 5.9 km from the points the stored profiles describe (same basin). Basin statements are right; the elevation and point-ecoregion lines are for the profile's point.
3. **Profile store.** The tab reads `/api/profile`, which reads the ten sample files in `app/static/profiles/`. A database table of per-basin profiles, keyed by level and `hybas_id`, replaces only that route's reader (one function). The table design (finished records or facts assembled per request) is open. Adding the route lifted this WO's "no API changes" proviso, with Karl's agreement.
4. **Local dev server needs a restart** before `/api/profile` works there (it returned 404 until restarted).
5. **Dashboard dropdown after a place is resolved.** In the clone, "Load an example" stays visible beside the place chip, although `setResolvedPoint` sets it to `display: none`. Bootstrap's `d-flex` is `!important`, which probably overrides the inline style; I have not checked whether the Sandbox behaves the same. Choosing an example there navigates to that place.
6. **The link records the last run, not the current controls.** After a level change without re-running, the link carries the old level (the same displayed-versus-control mix found in WO-02). Keep-current URLs (refresh and back button) were not built.
7. **Query log.** Arrivals log as `src=link`; the docstring in `app/query_log.py` still lists only `ui`, `ui_aux`, `workbench`, `api`. The GA event does not distinguish arrivals.
8. **Names I chose:** the `member` and `view` parameters (the legacy `?tab=settlements|polities` still works and is not the same thing); the `profile` field in the examples list now only documents the fixtures.
9. **Header and splash.** The splash header badge still reads "v0.4 Sep 2026". Workbench and the Sandbox are not in the Dashboard's navigation; the Sandbox is reachable by URL only. The Dashboard and Using EDOPS pages are `noindex`; the canonical host and the trailing-slash redirect behind nginx (WO-02) are still to confirm on the server.
10. **The clone duplicates 4,590 lines.** Sandbox wording remains in its help text and comments; extraction of shared code waits until the design settles.
11. **Out of scope, as the WO says:** configurator control behaviour, the sources statement and long-span caution, the Using EDOPS page itself, typed lookup on the splash, the profile store, Level 08 profiles.
12. **Hours.** WO-02's hour estimates were far too high; the six items were built in one working session.

## Gate (for Karl's browser check)

Choose Tbilisi on the splash and arrive on the Dashboard with its stored profile on the Profile tab and the other tabs filled; press Copy link, open the URL in a new window, and see the same result. The tests cover this; the check in a real browser is still Karl's.
