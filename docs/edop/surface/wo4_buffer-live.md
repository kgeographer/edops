# WO4 — Buffer live: `/api/areas` route + first live call

**Branch:** Surface / sandbox v2 (new branch off WO3)
**Phase:** Surface · **Step:** 3 (buffer scope — live path)
**Depends on:** WO3 (buffer fixture-backed scope + widgets) — done.
**Type:** full-stack. New backend route + frontend wiring. First live DB-backed call from the v2 page.

## Goal

Make buffer a **live** scope: lat/lon + radius drive a real query through a new `/api/areas`
endpoint over `areal_signature`, and the response renders through the existing (WO2/WO3)
renderer + widgets. The accept gate is **live response renders identically to the fixture** —
because `02_buffer_detail.json` was captured from the same callable, any divergence means the
route is transforming the payload (violating serialize-unmodified) or the fixture is stale.

This is the first WO that can fail for backend reasons (DB, route, serialization), so the gate
isolates that: fixture-vs-live equivalence is the test.

## Constraints

- **Live Lookup (`sandbox.html`) untouched.** New route and v2 wiring only.
- **Serialize, do not transform.** The route returns `areal_signature`'s payload **unmodified** —
  no wrapping, renaming, or added envelope. This is the constraint that keeps the WO3 fixtures
  valid proxies. It is the thing the equivalence gate actually tests.

## Backend — `/api/areas` route

Stand up `GET /api/areas` as a thin front door over the area resolvers, type-dispatched.
Pattern follows WO22's `/api/area` (polity) — thin, no new engine logic.

**Route shape:**
```
GET /api/areas?type=<buffer|polity>&<type-params>&[bands=ABCDET]&[from_year=&to_year=]&[detail=true]
```

**Type dispatch + per-type params:**
| `type` | required params | resolver / callable |
|---|---|---|
| `buffer` | `lat`, `lon`, `radius_km` | `areal_signature` |
| `polity` | `polity`, `year` (resolver_year — the boundary year) | `areal_signature_polygon` via `resolve_polity` |

`polity`'s `year` is `resolver_year` — the boundary year, **always required for polity**
(the boundary is time-dependent; unrelated to Band T). Buffer has no boundary-year.

**Migrate polity in:** fold WO22's `/api/area` (polity-only) into `/api/areas?type=polity`.
Keep `/api/area` as a **deprecated alias** that internally forwards to the polity path (301 or
internal call — implementer's choice), so WO22's tests can be repointed without breaking, and
nothing that referenced the old route 404s. Mark it deprecated in the route docstring; a later
WO removes it once nothing references it.

**Validation — two passes, in order:**
1. **Type-params:** the params required by `type` (table above). Missing → 422 naming the
   missing param and the type.
2. **Band-conditional (cross-cutting, applies to all types):** if `T` ∈ `bands`, then
   `from_year` AND `to_year` are required. Missing → 422 with a clear message
   ("Band T requires a timespan (from_year, to_year)"). **Span-only this WO** — a single-year
   T query is expressed as `from_year == to_year`; no dedicated single-year mode (that's a
   deferred UX question — see forward notes).

Keep the band-conditional rule in **one place**, not duplicated per type — it is orthogonal to
type. `resolver_year` (polity) is a type-param and validates in pass 1; the T span validates in
pass 2. They are separate passes so the two year-inputs never tangle.

## Frontend — buffer wiring

- The buffer input control (radius, from WO3) becomes **functional**: lat/lon (from
  WHG/coord resolve, existing) + radius → the live call.
- On Get signature with scope=buffer: build the `/api/areas?type=buffer&...` URL, fetch,
  render the response through `renderSignature` (unchanged — same payload shape).
- **Client-side band guard (the "you need a timespan for T" message):** if T is ticked and
  from/to are empty, show the message and **do not fire the request**. This is the fast-fail UX;
  the server 422 (pass 2 above) is the backstop for direct API callers, not the primary path.
- Swap the WO3 fixture loader for the live fetch on the buffer path. Keep the fixture-load path
  available behind a dev flag if trivial (useful for offline UI work); not required.

## Accept gate

- **Equivalence (the core test):** a live buffer call on the fixture's coordinates
  (Timbuktu, lat 16.8167, lon -2.9833, radius_km 100, L06, bands A–E, detail=true) returns a
  payload that renders **identically** to `02_buffer_detail.json`. Byte-identity of payload not
  required (float formatting etc. may differ), but structure, row count (52), methods, and
  rendered output must match. Any structural divergence = serialize-transform bug, caught here.
- **Validation:** T-ticked-without-span → client message, no request; direct route call same
  case → 422. Buffer without radius → 422. Polity path still works via `/api/areas?type=polity`.
- **Polity regression:** WO22's polity tests pass, repointed to `/api/areas?type=polity` (or via
  the `/api/area` alias). Nothing 404s.
- **Existing suites green:** full `pytest tests/` (structural + Playwright + engine). Live
  Lookup untouched.
- Karl reviews each write before it lands.

## Out of scope

- Polygon type (`type=polygon`) — geometry transport (GET param vs POST body) undecided;
  documented as "not yet wired," picked up at the polygon scope step.
- Single-year-as-first-class T query — span-only this WO; the year-or-span UX is deferred (see
  forward notes).
- Band T rendering — buffer A–E only here; the Band T panel is a later step.
- Ring / draw-study-area scopes.

## Forward notes / open questions to log

- **Single-year vs span T input** — span-only implemented now (matches existing sandbox). Whether
  a single year should be a first-class T query (its own mode, one field) rather than a
  from==to workaround is deferred. **This is the same fork as the polity/Cliopatria pattern
  question below** — decide them together, not piecemeal.
- **Polity T semantics undecided (log to tracker/register):** the existing-sandbox T pattern
  ("poll an area's cells over a span, show distribution over time") and the Cliopatria pattern
  ("pick a polity slice, paint one variable globally at that slice") are *different operations*.
  Which one — or both, split across Map (Cliopatria paint) and Signature (sandbox distribution)
  tabs — the v2 polity scope implements is **not yet decided**. Not a WO4 concern (buffer has
  neither ambiguity), but it must be settled before the polity live step. Buffer is where the
  underlying single-year-vs-span choice can be made cheaply, ahead of polity forcing it.
- **`/api/area` alias removal** — once nothing references the singular route, a later WO removes it.

