# WO — Public API reshape

Multi-section WO, sections added one at a time. **Write the next section only after the
current one is built and tested** — deliberate, per Karl (2026-09-13): this touches the live
public API and the Polities tab's signature-fetch path, both real breakage risk.

Grew out of `docs/edop/lod/note_to_opus_lod_compatibility.md` and
`docs/edop/lod/WO_lod-prep_opus.md` — the `place_links` passthrough work surfaced that
`/api/signature`, `/api/areas`, and `/api/area` have three different, undocumented response
shapes. This WO is the resulting reshape, not itself an LOD deliverable.

## Destination shape (context for every section below — not built yet, most of it)

- Two request cases, matching how a user actually supplies a location: **point** (single
  basin / buffer / basin-touching-ring) and **geometry** (a set of basins within a region).
- `/api/signature` (currently the scope-dispatched `/api/areas`) becomes the one public,
  general, `scope`-parameterized endpoint for both cases. The *current* `/api/signature`
  (point/raw-value, `profile_groups`/flat shape) becomes internal-only
  (`include_in_schema=False`) — every internal caller (`sandbox.html` ×2, `workbench.html`,
  the research script) keeps working unchanged; only its public visibility changes.
- `/api/area` (singular) retires — its concept (arbitrary-geometry signature,
  `areal_signature_polygon()`) survives generalized as `scope=area`, not as a Cliopatria-only
  parameter interface.
- `scope=polity` (name+year, Cliopatria-specific) is **not** a public parameter shape — no
  numeric/alphanumeric PK, name-keyed lookup, a Sandbox/Dashboard convenience, not a
  general-purpose input. Resolving a named polity to a geometry becomes an internal step
  (this WO's `/clio`) that feeds the same general geometry-in engine primitive `scope=area`
  will use — bbox and country-code-list are the realistic *public* ways to supply an area,
  raw geometry the edge case.
- `basin_ring`'s response shape gets brought in line with its `single_basin`/`buffer`/`polity`
  siblings (`scope`/`rows`/`bands`/`caveats`/`shortfall`/`temporal`) — currently the one
  outlier (`type`/`lat`/`lon`/`center`/`ring`).

None of the above is scoped as an implementation yet except Section 1. Recorded here so the
destination doesn't get lost across sections, not as a commitment to build it in this order.

---

## Section 1 — `/clio`: search, slices, resolve-to-geometry (build + verify in isolation)

**Status: done, 2026-09-13.** `app/api/routes_common.py` — `/api/clio/search`,
`/api/clio/slices`, `/api/clio/geom` (each delegates directly to its `/polity/*`
counterpart, not a reimplementation) + `_clio_resolve_geom_wkt(slice_id)` (new, not yet
called by anything). Tests: `tests/test_polity.py`, 10 new (equivalence checks for all
three routes, the WKT helper, a 404 case, and a dormancy guard). All three acceptance
criteria verified, live and in pytest: `/clio/geom` output byte-identical to
`/polity/geom` for a real slice (Northern Song, id 4352); `grep` confirms no template or
`areas()` reference to `/clio`. Full suite green before commit. Branch `lod-prep`.

### Why

Traced the live Polities-tab call path in full (2026-09-13, session log). Two findings:

1. Cliopatria-specific logic is spread across three routes (`/api/polity/search`,
   `/api/polity/slices`, `/api/polity/geom`, all in `routes_common.py`) plus a fourth,
   independent copy of the same `gaz.clio_polities` lookup SQL inside `areas()`'s polity
   branch (`routes_sandbox.py`) — four places touching the same table.
2. Map-drawing and signature computation resolve **the same slice's geometry two different
   ways**: `drawPolityBoundary()` fetches it by the slice's own `id`
   (`GET /api/polity/geom?id=`); `_silentResig()` and the `[Get Signature]` click handler
   re-derive it independently by name+year (`GET /api/areas?scope=polity&polity=...&year=...`).
   They agree today but nothing enforces that they always will.

`/clio` consolidates the Cliopatria-specific resolution into one place, and makes "resolve a
chosen slice to a geometry" a single operation both consumers can eventually share.

### What stays untouched (this section)

Everything currently live: `/api/polity/search`, `/api/polity/slices`, `/api/polity/geom`,
`areas()`'s polity branch, the Polities tab's actual behavior (search, slice slider, Play,
`[Get Signature]`). `/clio` is purely additive in this section — nothing existing is modified,
removed, or depended upon by anything live yet.

### What gets built

A new route family (exact URL/param shape a build-time decision, not prescribed here) covering
three responsibilities, mirroring what `/api/polity/*` already does:

1. **Search** — name substring → candidate polities + slice counts.
2. **Slices** — name → ordered slice metadata (id, fromyear, toyear, area, seshatid, geom_hash,
   geom_group; no geometry — matches `/api/polity/slices` today).
3. **Resolve** — a slice's own `id` → its geometry (WKT, for feeding an engine call; GeoJSON,
   for map drawing) — the one place a slice's geometry gets derived, replacing both of today's
   independent paths once wired (not in this section).

### Acceptance criteria for "works independent of anything else"

- New routes exist and are tested (pytest — DB-backed where a real lookup is needed, following
  this week's established pattern: `client`/`buf_client` fixtures, `db_available` skip-gate).
- **Direct equivalence test**: for a real polity + slice id, `/clio`'s resolve step returns the
  same geometry `GET /api/polity/geom?id=` already returns today. This is the actual gate —
  it proves the consolidation preserves correctness before anything is allowed to depend on it.
- `grep` confirms nothing live (templates, `areas()`, `/api/polity/*`) references `/clio` yet —
  dormant until Section 2.

### Explicitly not in this section

Wiring `_silentResig()` or the `[Get Signature]` click handler to use `/clio`'s resolve step.
Retiring `/api/polity/*` or the duplicated SQL in `areas()`. Any change to the render loop
(`applySlice`/`drawPolityBoundary`/Play/abort logic) — confirmed 2026-09-13 that loop is
already correct and doesn't need to change; this section doesn't touch it.

---

## Section 2 — wire the polity signature-fetch path to `/clio`

**Status: written, not built.** Written 2026-09-14 now that Section 1's acceptance criteria
are verified (see above) — per Karl, still its own explicit go/no-go before building, not an
automatic continuation of Section 1's "auto mode."

### Goal

Replace `areas()`'s independent name+year `gaz.clio_polities` lookup, for the polity scope,
with the same by-`id` resolution the map-drawing path (`/api/polity/geom?id=`, and now
`/clio`) already uses correctly — using the slice's own `id`
(`_politySlices[_polityCurrentIdx].id`), already known client-side, no new fetch required to
get it.

### The one real design gap Section 1 left open

`_clio_resolve_geom_wkt(slice_id)` (Section 1) returns **only** a WKT string. `areas()`'s
polity branch needs more than geometry — it builds a `resolver` block
(`polity`/`polity_id`/`fromyear`/`toyear`/`year`) from the same SQL row it looks up today.
Using the WKT-only helper alone would lose those fields and force a second query anyway,
which only half-solves the "two independent lookups" problem this WO exists to fix.

**Resolution:** add a new helper, `_clio_resolve_slice(slice_id)`, returning the full row (id,
name, fromyear, toyear, seshatid, geom_wkt) in one query — everything `areas()`'s polity
branch needs, derived from a single lookup by id. `_clio_resolve_geom_wkt` (Section 1) stays
as-is for callers that only need the WKT.

### What changes

- **`routes_common.py`** — new `_clio_resolve_slice(slice_id)` helper (id/name/fromyear/toyear/
  seshatid/geom_wkt, one query). Additive; `_clio_resolve_geom_wkt` untouched.
- **`areas()`'s polity branch (`routes_sandbox.py`)** — gains a new optional `slice_id` param.
  When present: resolve via `_clio_resolve_slice(slice_id)`, build the `resolver` block from
  its fields. When absent: **exactly today's behavior, untouched** — the existing name+year
  SQL lookup stays the fallback, so every other caller (anything not yet sending `slice_id`,
  and `/api/area`, which is being retired separately and isn't worth touching here) keeps
  working with zero behavior change.
- **`sandbox.html`** — `_silentResig()`'s polity branch and the `[Get Signature]` click
  handler add `slice_id: _politySlices[_polityCurrentIdx].id` to their existing params
  (`polity`/`year` stay too — harmless once `slice_id` takes precedence server-side, and
  keeps the request self-describing). This is the only change that touches live user-facing
  behavior in this whole WO so far.

### Build order (same incremental discipline as Section 1 vs. this section)

- **2a — backend only.** Add the helper + the optional `slice_id` param. Verify standalone:
  a request with `slice_id` returns the identical `rows`/`scope`/`resolver` payload as the
  equivalent name+year request for the same slice (new equivalence test, same pattern as
  Section 1's). Existing `TestPolityPayload`/`TestPolityFixtureEquivalence` (11 tests, exercise
  the unchanged name+year path) must stay green untouched — proves backward compatibility.
  Frontend not touched yet at this point.
- **2b — frontend wiring.** Switch `_silentResig()` and the click handler to send `slice_id`.
  This is the step that changes what a real user's click actually does — per Karl's standing
  habit, wants a browser look before commit, not just green tests.

### Acceptance criteria

- 2a: new equivalence test passes (slice_id-resolved payload == name+year-resolved payload
  for the same real slice); existing 11 polity tests unaffected; full suite green.
- 2b: live-verified in browser against a real polity (Northern Song or similar) — signature
  content identical before/after the frontend change, across at least one slider move and one
  `[Get Signature]` click.

### Explicitly not in this section

Retiring the name+year path itself (kept as the fallback/default — `/api/area` and any other
caller not yet sending `slice_id` still needs it). Retiring `/api/polity/*` or `/api/area`.
Any part of the destination shape beyond this one path (the `/signature` rename, `scope=area`
generalization, `basin_ring`'s shape fix) — separate, later sections.

---

## Section 3 — not written yet
