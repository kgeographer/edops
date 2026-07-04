# WO7 — Polity search: live lookup against clio_polities

**Branch:** Surface / sandbox v2 (new branch off WO6)
**Phase:** Surface · **Step:** 4 (polity scope — arbitrary input)
**Depends on:** WO6 (polity live, example-hardwired) — done.
**Type:** frontend wiring only. No backend, no engine, no new routes. The `/api/polity/*`
routes already exist and are live (they power `cliopatria.html`); the signature call is proven
(WO6). WO7 connects proven pieces to a new bit of v2 UI.

## Goal

Replace the hardwired Northern Song example with **arbitrary polity search**: search
`clio_polities` by name → pick a result → pick a slice → the existing proven signature call
(`/api/areas?type=polity`) renders it. This is the polity analog of buffer's "generalize from
the example to real input" step.

## Existing routes to wire (already live)

- `/api/polity/search` — name search → matching polities.
- `/api/polity/slices` — a polity's available slices (geometries + timespans).
- `/api/polity/period` — (available; used as needed for labeling).
- `/api/polity/geom` — slice geometry (for the boundary outline on the Map tab).

WO7 creates none of these. It calls them from the v2 page.

## Flow

1. **Search** — polity search field (visible when scope = Polity, per WO4's scope gate) →
   `/api/polity/search`. **Reuse cliopatria.html's existing search interaction pattern**
   (typeahead or type-and-submit — whichever it does) so the two pages stay consistent; do not
   invent new search behavior.
2. **Pick a result** — user selects a matched polity → fetch its slices via
   `/api/polity/slices`.
3. **Slice picker — plain dropdown this WO.** Present the polity's slices as a dropdown,
   labeled by timespan (e.g. "960–979 CE", "980–999 CE", …). Selecting one sets
   `resolver_year` (the boundary). **Not the Cliopatria slider** — the slider is the map's
   scrubbing interaction and arrives with the map; on a signature-only page it would prove the
   wrong thing. Dropdown is the honest minimal control for WO7.
4. **Boundary outline** — the selected slice's geometry (`/api/polity/geom`) renders to the
   Map tab as an outline (boundary only, no paint — same as WO5). Optional-but-cheap; include
   if it falls out of the existing geom route trivially, else note as a tiny follow-up.
5. **Signature call** — the existing `buildPolityUrl()` + signature button handler takes the
   chosen name + `resolver_year` from here. **Unchanged** — this is the WO6-proven path. Band T
   span (`from_year`/`to_year`) and the client-side T-without-span guard (WO4) apply as before.

## Constraints

- **Live Lookup (`sandbox.html`) untouched.**
- **No change to the signature call path** — `buildPolityUrl()` and the handler are proven
  (WO6); WO7 only changes how the name + slice reach them (search/dropdown instead of hardwired
  example).
- The Northern Song **example** can remain as a preset that pre-fills search + slice (a
  convenience shortcut into the same flow), or be retired — implementer/Karl's call. If kept, it
  must route through the same flow, not a separate hardwired path.

## Accept gate

- Searching an arbitrary polity name returns matches from `clio_polities`.
- Selecting a result populates the slice dropdown from `/api/polity/slices`.
- Selecting a slice + Get signature fires the proven `/api/areas?type=polity` call and renders
  A–E + Band T exactly as WO5/WO6 established.
- A polity other than N Song renders correctly (confirms nothing was N-Song-specific).
- T-without-span guard still fires (WO4 behavior intact).
- Existing suites green (structural + Playwright + engine); live Lookup untouched.
- Karl reviews each write before it lands.

## Out of scope

- Cliopatria-style **slider** — arrives with the map.
- **Map paint** / per-unit endpoint (F5.4) — its own arc; log to deferred register with
  Areas-phase lineage when the map step opens.
- Search result ranking/refinement beyond what `/api/polity/search` already returns.
- Ring / polygon / draw scopes.

## Forward note

With WO7, every point-rooted and polity signature scope is live from real input. The remaining
polity arc is the **map** — boundary paint + per-unit choropleth + the slice slider — which is
the Clio "money shot" and a larger build. The signature side being fully proven first is the
slow-and-steady payoff: the map is designed against a known-good signature pipeline, not
simultaneously with it.
