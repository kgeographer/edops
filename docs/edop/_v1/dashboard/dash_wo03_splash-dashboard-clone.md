# dash WO-03: splash, Dashboard clone, example handoff

Draft of 15 Nov 2026, for Karl's review. A build, on the `dashboard` branch.

## Goal

A visitor chooses an example on a new splash page and arrives on the Dashboard with a result showing: the Profile tab for a settlement, the Signature tab for a polity, the other tabs filled. A permalink button on the Dashboard copies a URL that reproduces what is displayed.

## Background

- `dash_wo02_results.md` is the basis for items 4 and 5; follow its "to avoid rework" list.
- The Dashboard starts as a clone of `sandbox.html` on the empty `/dashboard` page. The Sandbox stays untouched, live and out of the navigation.
- The Dashboard will become a configurator (result first, controls adjust it). Rebuilding the left panel and making every control behave one way is a later work order; this one adds the last-run snapshot that work will need.
- Profiles: nothing is generated or stored in this work order. The Profile tab shows the stored profiles of the ten WO-09 places (as `/profiles` reads them) and placeholder text otherwise.
- Decisions from WO-02: place in the URL as `lat`, `lon`, `name`; the API's parameter names plus `v`; arrivals tagged in the query log; host `edops.computingplace.org`; `noindex` stays. A polity arrives at its first slice; `selectPolity` ignoring its year is left as it is.

## Items

1. **Examples list.** One small file rendered into both the splash and the Dashboard. Settlements: the nine WO-09 places that have a basin, in WO-10 order (Timbuktu, Tbilisi, Santa Fe, Kaifeng, Lviv, Poltava, Chaco Canyon, Alexandria, Utqiagvik). Tristan da Cunha, which has no basin, is not an example. Polities: the Sandbox's eight. Check each runs at single basin, Level 06, without error; report any that fail rather than swapping them.

2. **Splash.** Replace the current splash with the layout in `dash_fable-opus-handoff.md` §2: header (logo, EDOPS, About, Documentation); a "what it is" block; a "See a place" row with the two example dropdowns; three tiles (Dashboard, Using EDOPS, Data Explorer); a line linking Computing Place. All text is placeholder, marked for Karl to write. Choosing an example navigates to the Dashboard by permalink.

3. **Dashboard clone.** Copy `sandbox.html` to the Dashboard page. Keep element ids, so existing tests and helpers still apply; include the GA tag. Add a Profile tab, first among the result tabs. Header navigation: splash, Dashboard, Using EDOPS, Data Explorer.

4. **Profile tab.** Headed "Containing basin for {place}", as the other tabs are. For one of the ten places at single basin, Level 06: its stored profile. Otherwise: one line saying what profiles cover at present, plus placeholder text so the tab is not empty. For polities the tab says profiles are for settlements.

5. **Handoff.** On load, the Dashboard reads the URL and applies it: validate and sanitise; set the place, scope, level, bands, years, radius, polity; run; wait; set the ring member if given (one extra request); select the tab. Build it as `applyState(state)` with the URL codec outside it, the run pulled into a function that returns a promise, and visible errors (bad parameters, failed run, polity slices not found). Unknown parameters are ignored. Arrivals log as `src=link`.

6. **Permalink button.** After a run, a button copies a URL built from the last-run snapshot by `getState()`: place, scope, level, bands, years, radius, polity and slice, ring member when one is displayed, and the active tab. Panel controls (sliders, thresholds, Context radius, Similarity lens, map variable, accordions) are not captured; they open at their defaults.

## Provisos

- No changes to the Sandbox, the engine, the API, `/profiles`, the stored profiles or `/whgmodal`.
- No keep-current URL; no panel state.
- The left panel stays as cloned, apart from what items 3 to 6 need.
- Placeholder prose is marked as such; Karl writes the text.

## Out of scope

Configurator control behaviour; the sources statement and the long-span caution; the Using EDOPS page itself; typed lookup on the splash; the profile store; Level 08 profiles.

## Deliverables and gate

- `dash_wo03_summary.md`, one page; `dash_wo03_results.md`, with anything that needs attention.
- Playwright tests: each example arrives without error; a permalink round trip for a single basin, a ring member and a polity.

Gate: choose Tbilisi on the splash and arrive on the Dashboard with its stored profile on the Profile tab and the other tabs filled; press the permalink button, open the URL in a new window, and see the same result.

## Adjustments after review (Karl and CC, 16 Nov)

- **Polity year.** `selectPolity` stays as it is. The handoff loader honours a `year` parameter when present: after the slices arrive it applies `nearestPolitySlice(year)` and `applySlice(idx, year, skipResig)`. With no `year` a polity arrives at its first slice (the splash). The permalink button includes the year, so a later slice round-trips.
- **One examples list, two dropdowns.** The splash and the Dashboard draw on the same file, so a place has the same coordinates in both. Timbuktu, Tbilisi, Santa Fe and Kaifeng use the Sandbox's coordinates (the same Level 06 basin as the stored profiles, 0.4 to 5.9 km from the profile points); the other five use the WO-09 coordinates. San Francisco is dropped (no profile), and Tristan da Cunha is not an example (it was only a proof of the no-basin message). Choosing an example in the Dashboard behaves like the splash: it runs the default query and opens the Profile tab.
- **Profile tab matching.** The list carries each place's profile slug; the tab shows a stored profile when the slug matches and the stored `hybas_id` equals the basin the query returned. Otherwise the one-line "profiles cover only some places" text.
- **Header.** The shared header partial may be edited to carry the Dashboard (nothing is pushed to `main` until the v1 deploy; test deploys come from `v1`, as with v0.4). "Using EDOPS" gets a placeholder page so its link resolves.
- **`noindex`** is added to the clone. `src=link` needs a mode in the clone's `_qlog`; the server needs no change.
- **Item 1 wording.** Settlements are checked at single basin, Level 06; polities at polity scope, Level 06, at the first slice, with the bands the Sandbox sets by default. Failures are reported, not swapped.
- **Steps.** The WO runs one item at a time. WO-02's hour figures are not a plan; there is no split unless it becomes necessary.
