# WO6 — Polity live: `/api/areas?type=polity` end-to-end

**Branch:** Surface / sandbox v2 (new branch off WO5)
**Phase:** Surface · **Step:** 4 (polity scope — live path)
**Depends on:** WO5 (polity A–E + Band T render, fixture-backed) — done; WO4 (`/api/areas`
route with polity type folded in) — done.
**Type:** wiring + equivalence check. No new render logic, no engine change (F5.1 confirmed the
engine already returns the span). No new widgets.

## Goal

Make the **polity example selection** perform a live DB read via `/api/areas?type=polity`,
replacing the fixture load, and confirm the live response renders identically to
`03_polity_nsong_detail.json`. This is the polity analog of WO4's buffer equivalence step: the
renderer and widgets are already proven against the fixture (WO5), so this WO tests the
**live path and serialization**, not the display.

## Scope — incremental, one thing

Wire the Northern Song **example** to a live call. Not arbitrary polity search yet — the
example is the known-input/known-fixture pair, which is what makes the equivalence check
meaningful. Generalizing to arbitrary polity search + slice selection is a following step.

## Constraints

- **Serialize, do not transform.** The route returns `areal_signature_polygon`'s payload
  **unmodified**. This is what the equivalence check tests, and what keeps the WO5 fixture a
  valid proxy.
- **Live Lookup (`sandbox.html`) untouched.**
- **`/api/areas?type=polity` already exists** (WO4 migration). WO6 does not create the route —
  it points the page's polity example at it and confirms the round trip.

## The call

The Northern Song example carries the fixture's parameters (confirm against
`03_polity_nsong_detail.json`):
```
GET /api/areas?type=polity&polity=<N Song name>&year=<resolver_year>&level=6&bands=ABCDET&from_year=1000&to_year=1100&detail=true
```
- `year` = `resolver_year` = the boundary slice (the fixture's slice — confirm exact value).
- Band T span `from_year=1000&to_year=1100` (the fixture's span).
- `detail=true` (the sandbox consumes detail).

## Build

- Swap the polity example's data source from the WO5 fixture load to the live
  `/api/areas?type=polity` fetch, using the fixture's exact parameters.
- Response renders through the existing WO5 path: A–E via `renderSignature` + widgets, Band T
  via the time-marginal/value-marginal/HYDE-table/eVolv2k-list built in WO5. No render changes.
- Keep the fixture-load path available behind a dev flag if trivial (offline UI work); not required.

## Accept gate — equivalence

- Live N Song call renders **identically** to the WO5 fixture render. Structure, row count
  (372: 52 A–E + 320 T), methods, A–E widgets, and the Band T marginals/slider/table all match
  what the fixture produced.
- Byte-identity of payload not required (float formatting may differ); **structural and rendered
  equivalence** is the gate. Any structural divergence = a serialize-transform bug or a stale
  fixture — caught here, on the known pair, before arbitrary polity input can obscure the cause.
- `marginal_exposure` present in the live neighborhood block as in the fixture
  (`{lt_50pct: 0.030, lt_20pct: 0.008}`) — not rendered, just confirmed present (F5.2).
- Band T validation: the call includes a span, so no T-without-span error; confirm the WO4
  band-conditional validation passes for this well-formed call.
- Existing suites green (structural + Playwright + engine); live Lookup untouched.
- Karl reviews each write before it lands.

## Out of scope

- Arbitrary polity search + slice picker (following step — this WO is the known example only).
- Map paint / per-unit endpoint (F5.4 — its own arc; add to deferred register with Areas-phase
  lineage when the map step opens).
- Any render or widget change.
- Ring / polygon / draw scopes.

## Forward note

Once the example round-trips live and matches the fixture, the next polity step is generalizing
input: polity search → resolve → slice picker (constrained to the polity's actual slices,
setting `resolver_year`) → live call for arbitrary polity + slice. That step exercises the
input machinery WO5's finding and the slice-picker design assume; WO6 proves the pipe first on
the known pair.
