# dash WO-03 summary: splash, Dashboard clone, example handoff

2026-11-16. Spec `dash_wo03_splash-dashboard-clone.md`; record `dash_wo03_results.md`. Branch `dashboard`. Nothing deployed; the Sandbox, Explorer and Workbench render exactly as before.

- **Item 1, examples.** One list (`app/web/dashboard_examples.json`): 9 settlements and the Sandbox's 8 polities. All 17 run at Level 06; each settlement's basin matches its stored profile. San Francisco and Tristan da Cunha are not examples.
- **Item 2, splash.** New `edops.html`: two example dropdowns, three tiles (Dashboard, Using EDOPS, Data Explorer), placeholder text marked for Karl. Choosing an example opens the Dashboard by URL.
- **Item 3, Dashboard.** `dashboard.html`, cloned from the Sandbox with its ids; a Profile tab leftmost; its own header navigation; `/using` placeholder.
- **Item 4, Profile tab.** An internal `/api/profile` keyed by level and `hybas_id` (ten sample records for now) feeds the tab; it shows a stored profile when the basin has one and its own place is within 10 km, otherwise one line and placeholder text.
- **Item 5, handoff.** `/dashboard?lat=…&lon=…&name=…` (parameters named as in the API) opens a place with its result and tab showing; settlements, polities (with a year), rings, buffers and Level 08 work. Bad links say why. Arrivals log as `src=link`.
- **Item 6, permalink button.** After a run, "Copy link" gives a URL built from the last run, the ring member shown and the active tab; opening it reproduces the result. Reset clears the address bar.
- **Tests:** 52 dashboard tests passed in one run, and the Reset tests after the last fix (the full folder not re-run since); related existing tests pass.
- **For Opus:** arriving from the splash shows the Map tab first and switches to Profile about a second later. The cause is that the target tab is selected only after the query returns; not addressed.
- **Not done, by design:** configurator control behaviour, sources statement, the Using EDOPS page, typed lookup on the splash, the profile store, Level 08 profiles.

**Gate.** Karl checks in a browser: Tbilisi on the splash, the stored profile on the Profile tab, Copy link, open it in a new window, same result.
