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

## Section 2 — calve the polity signature path off `/api/areas` entirely

**Status: written, not built.** Written 2026-09-14 (revised same day — first draft kept a
`scope=polity`/`scope=area` value inside `areas()`'s dispatch; Karl's call: go further,
`/api/areas` should end up with no Cliopatria-awareness at all, not even a generic
geometry-accepting scope value it delegates to). Still its own explicit go/no-go before
building.

### Goal

A new, fully self-contained endpoint, `GET /api/clio/signature`, owns the whole Cliopatria
signature computation — resolve a slice, compute over its geometry, return the result.
`/api/areas`'s `scope=polity` branch keeps running exactly as it does today, untouched, for
the duration of this section — it becomes deletable only once nothing calls it anymore
(Section 3, after 2b is confirmed working). End state this section moves toward: no
`scope=polity` on `/api/areas` at all.

### Why a full endpoint, not a scope value

A resolved polity boundary as WKT can be tens of KB — too large to hand back to the client
and then re-submit on a GET querystring, so resolution has to happen server-side, in one hop,
from an id. Given that, the question was just *where* that hop lives. Putting it inside
`areas()` (even as a generically-named `scope=area`) still leaves the dispatcher holding a
`slice_id`-shaped, `/clio`-calling branch — Cliopatria-awareness by another name. A separate
endpoint means `/api/areas` genuinely never has to know Cliopatria exists.

### What gets built (additive — nothing existing touched)

- **`routes_common.py`** — new `_clio_resolve_slice(slice_id)` helper: one query returning
  id/name/fromyear/toyear/seshatid/geom_wkt. (`_clio_resolve_geom_wkt`, Section 1, stays
  as-is for anything that only needs WKT.)
- **New route, `GET /api/clio/signature`** (file TBD at build time — `routes_common.py`
  alongside the rest of `/clio`, or its own `routes_clio.py` if it grows) — params:
  `slice_id`, `level`, `bands`, `from_year`, `to_year`, `detail` (same shape `areas()` already
  takes, minus `scope`/`polity`/`year`, which this endpoint has no use for). Body: resolve via
  `_clio_resolve_slice`, call `areal_signature_polygon(geom_wkt, conn, ...)` directly — the
  same engine primitive `areas()`'s polity branch already calls — then assemble the **same
  response shape** that branch produces today (`rows`/`scope`/`bands`/`caveats`/`shortfall`/
  `temporal`/`resolver`/`member_ids`), so nothing about how the frontend *renders* a signature
  needs to change, only which URL it fetches from.
- **`sandbox.html`** — `_silentResig()`'s polity branch and the `[Get Signature]` click
  handler switch from `GET /api/areas?scope=polity&polity=...&year=...` to
  `GET /api/clio/signature?slice_id=...&...` (the slice id is already in hand,
  `_politySlices[_polityCurrentIdx].id`, no new fetch to get it).

### Build order

- **2a — backend only.** Build `_clio_resolve_slice` + `/api/clio/signature`. Verify
  standalone: for a real slice, its payload matches `areas()?scope=polity&polity=...&year=...`
  for the same slice's own fromyear (equivalence test, same pattern as Section 1's). Existing
  `TestPolityPayload`/`TestPolityFixtureEquivalence` (11 tests, exercise `areas()`'s untouched
  polity branch) must stay green, unmodified — proves nothing existing moved. Frontend not
  touched at this point.
- **2b — frontend wiring.** Switch `_silentResig()` and the click handler to
  `/api/clio/signature`. The one step that changes what a real click does — browser-verified,
  not just green tests, per Karl's standing habit.

### Acceptance criteria

- 2a: new equivalence test passes; existing 11 polity tests on `areas()` unaffected; full
  suite green; `/api/clio/signature` confirmed live via direct curl against a real polity.
- 2b: live-verified in browser (Northern Song or similar) — signature content identical
  before/after, across a slider move and a `[Get Signature]` click.

### Explicitly not in this section

Removing `scope=polity` from `areas()` — stays live as-is throughout this section, deletable
only in a later section once 2b is confirmed and nothing calls it. Retiring `/api/polity/*` or
`/api/area`. Any part of the destination shape beyond this one path (the `/signature` rename,
`scope=area` generalization for non-Cliopatria geometry sources, `basin_ring`'s shape fix).

---

## Section 3 — not written yet
