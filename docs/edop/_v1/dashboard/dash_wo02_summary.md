# dash WO-02 summary: permalink, an estimate

2026-11-15. Spec `dash_wo02_permalink-estimate.md`; record `dash_wo02_results.md`. Branch `dashboard`. Nothing in the app or the Sandbox changed.

- **Item 1, state today.** The Sandbox reads only `?tab=` from the URL. Place, scope, level, bands, years, radius, the active tab, Context radius and the Similarity controls can all be set from code. The ring member, polity slice and Band T panel state are harder. The page script is a closure, so a loader must live inside the clone's script. The Sandbox keeps no record of the last run, and after a level change its tabs can disagree with its controls.
- **Item 2, minimal handoff.** Identify the place by `lat`, `lon` and `name` (the S9.1 decision); no WHG call is needed. Order: validate, set place, set parameters, run, wait, select tab. Measured load: Tbilisi 1.8 s to a filled Signature tab, Northern Song 2.5 s. It needs the run pulled into a function that returns a promise, polity year handling, and visible errors. Examples are hard-coded in the HTML (5 settlements, 8 polities); a shared list is easy. **10 to 18 hours (settlements only: 5 to 9).**
- **Item 3, full permalink.** A button that captures the displayed state on click needs a last-run snapshot, `getState()` and `applyState()`: **19 to 31 hours more**; a URL kept current as the user acts is 6 to 12 more. About 30 to 50 hours in all with item 2. It is also most of the cost of the "Show me" guides. Build the minimal version with this structure from the start to avoid rework.
- **Item 4, routing.** `/dashboard` and its query string work as they are. One unverified point: the trailing-slash redirect's `Location` behind nginx. The page has `noindex`. Which host WHG links to is a decision.
- **Decisions for Karl:** tag permalink arrivals in the query log; the host for WHG links; noindex or canonical at launch; capture on click only, or keep-current as well.

**Gate.** Karl chooses whether dash_wo03 builds the minimal handoff only or the full permalink. My recommendation: the minimal handoff, built on `applyState` and `getState` so the button is an increment; settlements first, polities and the extra panels after.
