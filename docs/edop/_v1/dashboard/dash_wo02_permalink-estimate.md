# dash WO-02: permalink, an estimate

Draft of 15 Nov 2026, for Karl's review. Reading code and small experiments only; nothing in the app changes.

## Goal

Find out what it takes for a URL to open a place in the Dashboard with a result showing. The splash examples depend on it: choosing an example hands the place to the Dashboard by URL. The results decide how much permalink capability goes into the build work order (dash_wo03: new splash, Sandbox cloned as Dashboard, example navigation).

## Background

- The Dashboard will be a clone of `sandbox.html` on the empty `/dashboard` page. The Sandbox stays untouched, live and out of the navigation.
- Entry order: choose a place; arrive with the default query run (single basin, Level 06, bands A to E), the Profile tab showing for a settlement, the Signature tab for a polity, and the other tabs filled. A left panel adjusts parameters.
- The splash has two example dropdowns, settlements and polities. Examples only; typed lookup on the splash is later.
- "Load an example" in the Sandbox sets scope, level, Band T and years but does not run the query.
- Later consumers of a permalink: a link from WHG place pages, and any "Show me" guide on the Using EDOPS page. Neither is in v1 scope here; note anything that bears on them.

## Items

1. **State today.** List everything that makes up what the Sandbox shows: Settlements/Polities tab, place (WHG id, name, lat/lon), scope, buffer radius, ring member, level, bands, Band T years, polity and slice, active result tab, Context radius, Similarity lens and thresholds. For each, say whether it can be set from code without a user action, and whether the Sandbox reads any of it from the URL now.

2. **Minimal handoff.** What the splash examples need: a URL that names the place, the Dashboard reads it on load, runs the default query and opens the right tab. Say:
   - what identifies the place in the URL (example key, WHG id, lat/lon), and which choice also serves a later WHG link;
   - whether loading needs an external call (WHG lookup) and what happens if it fails;
   - the load order (resolve place, run query, fill tabs, select tab) and anything asynchronous that makes it fragile;
   - where examples are defined now and whether splash and Dashboard can share one list;
   - hours to build.

3. **Full permalink.** What it would take for the URL to carry the parameters and active tab as well, kept current as the user changes things and restored on load. Say which state is easy, which is hard (ring member, polity slice, Band T years likely), and hours to build. Note anything to keep in mind at item 2 so item 3 doesn't require rework.

4. **Routing.** Anything in nginx or the app's routes that the `/dashboard` path and its query string need.

## Provisos

- No changes to the Sandbox, the app, the engine or the server configuration.
- A throwaway test page in scratch, to confirm the load order, is allowed; name it as scratch.
- Karl and CC choose the branch.

## Out of scope

The splash, the clone, the Profile tab's content, `/whgmodal`, the profile store.

## Deliverables and gate

- `dash_wo02_summary.md`, one page: each item answered in a sentence or two, with hours.
- `dash_wo02_results.md`: the state inventory as a table, the findings per item, anything that needs attention.

Gate: Karl reads the summary and chooses whether dash_wo03 builds the minimal handoff only or the full permalink.

