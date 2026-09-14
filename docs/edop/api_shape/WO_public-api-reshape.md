# WO — Public API reshape

Multi-section WO, sections added one at a time. **Write the next section only after the
current one is built and tested** — deliberate, per Karl (2026-09-13): this touches the live
public API and the Polities tab's signature-fetch path, both real breakage risk.

Grew out of `docs/edop/lod/note_to_opus_lod_compatibility.md` and
`docs/edop/lod/WO_lod-prep_opus.md` — the `place_links` passthrough work surfaced that
`/api/signature`, `/api/areas`, and `/api/area` have three different, undocumented response
shapes. This WO is the resulting reshape, not itself an LOD deliverable.

## Destination shape — locked 2026-09-14 (superseded the 2026-09-13 version below it verbatim;
kept for the record, not deleted)

Locked in direct conversation with Karl, point by point, 2026-09-14. This is the model now —
not a proposal.

- **"Areas" (plural) does not exist, internal or external, anywhere.** Not a route, not a
  function name, not a concept. Every request resolves to exactly **one** signature — whether
  it aggregates over one basin or many. This is the starting assumption everything else follows
  from, not a naming preference.
- **One public endpoint: `/api/signature`.** One parameter, `scope`, flat, three values, no
  nesting: `basin` | `buffer` | `area`. (`basin-ring` was in this list briefly, 2026-09-14 —
  pulled back out the same day, see below.)
- **Input shape per scope:**
  - `basin` — a point (`lat`/`lon`).
  - `buffer` — a point + `radius_km`.
  - `area` — a WKT geometry string (`POLYGON`/`MULTIPOLYGON` only). First build target: a
    **bbox-constructed** example (short, trivial to round-trip) — not arbitrary or large WKT,
    kept simple deliberately.
- **Two response shapes, both already built and working today, no reshaping between them:**
  - `basin` (one basin) → raw values + a few derived values, mostly straight DB columns and
    category labels. Band T, if requested, requires `from_year`/`to_year` — "Band T is
    irrelevant without a year or timespan — it is not computable, can't be returned" (Karl,
    2026-09-14) — includes HYDE land-use summed across the grid cells within the one basin, and
    an LMR pdsi/temp/precip distribution across the grid cells overlapping it (both already
    within-basin aggregations `get_signature()` already does correctly — not the same kind of
    aggregation `buffer`/`area` do across a *set of basins*). Existing machinery:
    `get_signature()` — today's `/api/signature`, unchanged, reused directly.
  - `buffer` / `area` (many basins, aggregated across the set) → distribution constructs driving
    histograms. Existing machinery: `areal_signature()`, `areal_signature_polygon()`
    respectively. Should read like what the GUI already shows for these cases (buffer:
    confirmed byte-identical to the GUI's own buffer query, 2026-09-14; area: no direct GUI
    analog yet, but reuses the same envelope shape the GUI's polity queries already produce).
  - **`basin-ring` is not a `scope` of its own.** Karl, 2026-09-14: "all basin-ring ever does is
    pull a sig for the central basin — the rest is a GUI feature, rendering the surrounding
    basins... allowing separate calls for their signatures." It decomposes into `scope=basin`,
    called once per basin of interest — the ring topology (which basins are adjacent) is a
    map-rendering concern the GUI already owns (`/api/basin/ring`), not something the public
    signature endpoint needs to model. Built onto `/api/signature` briefly, then pulled back out
    the same day once this was named — `/api/areas?scope=basin_ring` is untouched and still the
    live internal mechanism for the GUI's ring rendering.
  - **Correction to this doc's own earlier framing (2026-09-13 version, below):** that version
    treated `single_basin_signature()` (the areas engine's n=1 case of its general aggregator,
    WO14) as the ancestor for the single-basin public product. Wrong — Karl: treating
    single-basin as a degenerate case of the multi-basin aggregator "was always a mistake I
    should have halted way back." `scope=basin` reuses `get_signature()`, full stop;
    `single_basin_signature()` is not part of this endpoint's story (though `basin_ring_signature()`
    still calls it internally, once per ring member — that's `basin_ring_signature()`'s own
    business, not something `/api/signature`'s dispatch needs to know about).
- **Cliopatria polities are not a `scope` of their own.** A polity's signature is `scope=area`
  once its geometry is in hand. How that geometry gets resolved server-side (Section 1's
  `/clio` work) is a separate, internal concern Karl is explicitly not prescribing: "whatever
  it takes to fetch geometries and basins for clio polities, I don't care."
- A bbox-constructed WKT is just the **test input** for building/proving the generic
  `scope=area` case — short, simple, trivial to round-trip. Cliopatria's own geometry (which
  can be much larger) is handled by whatever `/clio` needs to do server-side; that's a
  separate concern from the generic case's test input, not a design fork to reconcile.

### 2026-09-13 version (superseded by the above — kept for the record)

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

## Section 2 — build `/api/signature` for `scope=basin | buffer`

**Status: done, 2026-09-14 (commits `a8b9e66`, `803d66c`, `fa71a31`).** Two further corrections
landed the same day, after the section was first marked done: `basin-ring` pulled back out
entirely (not a `scope` of its own — see the locked model above) and Band T made strict for
`scope=basin` too (422 without a timespan, matching `buffer` — "Band T is irrelevant without a
year or timespan," Karl). Public scope list is now `[basin, buffer]`, `area` still pending
(Section 3). Below is the original build narrative, current except for those two points.

Two corrections found and resolved during the original build (see below,
both folded back into the "locked" model at the top of this doc): basin-ring has no aggregate
to reshape (kept exactly as `basin_ring_signature()` returns it, its own third shape); `scope`
ended up required with no default at all ("scope is absolutely required, we can't default to
something there" — Karl), `level` defaults to 6 when omitted (was 8) since 6 is the safe
choice for an area-type query (L8 has ~10x L6's basin count) and there's no reason to punish an
omitted level with an error the way scope's ambiguity would be. Every real internal
`/api/signature` caller updated so none silently changed behavior (`sandbox.html` ×2 already
sent `level`, just needed `scope=basin` added; `workbench.html`'s Profile panel sent neither,
got `scope=basin&level=8` to preserve its exact current result; the research script needed
`scope=basin`). `docsite/api.md` regenerated from `generate_api_guide.py` (its hardcoded
example curls needed `scope=basin` too). 8 new tests, `test_api_examples.py` fixed (13 calls +
one pinned value that needed its implicit L8 dependency made explicit). Full suite: 568 passed,
21 skipped. Commit `a8b9e66`, branch `lod-prep`.

### Goal

Extend the **existing** `/api/signature` route (`routes_common.py`, `signature()`) with an
optional `scope` param, default `basin` — today's only behavior, so every existing caller
(`narrative.py`, `workbench.html`, `sandbox.html`'s Analysis-tab parallel fetch, the research
script) keeps working with zero code changes on their end, since none of them pass `scope`.
`scope=basin-ring`/`scope=buffer` dispatch to `basin_ring_signature()`/`areal_signature()` —
the same engine calls `/api/areas` already makes today, just reached from `/api/signature`
instead.

This is pure re-routing of already-correct, already-tested machinery under one name — no
reshaping. **Correction found mid-build, 2026-09-14:** `basin_ring_signature()`'s own docstring
is explicit that it has no aggregate to begin with ("there is no meaningful aggregate across
the ring — the per-neighbour comparison is the payload") — it returns the center's full
raw-value signature plus one raw-value signature per adjacent basin, not a `rows`-shaped
distribution. Karl's call: keep it exactly as `basin_ring_signature()` already returns it, own
shape, not reshaped toward `buffer`'s envelope. So all three scopes in this section are pure
re-routes, zero new aggregation or reshaping logic anywhere.

### What gets built

- `signature()` gains `scope` (default `basin`) and `radius_km` (required only when
  `scope=buffer`). `scope=basin` — unchanged, calls `get_signature()` exactly as today.
  `scope=buffer` — calls `areal_signature()`, returns its existing shape unchanged.
  `scope=basin-ring` — calls `basin_ring_signature()`, returns its existing shape unchanged
  (`type`/`lat`/`lon`/`level`/`center`/`ring` — its own, not `buffer`'s).
- `/api/areas`'s `scope=buffer`/`scope=single_basin`/`scope=basin_ring` branches — untouched
  in this section, stay live in case anything still calls them directly. Retiring `/api/areas`
  itself is a later, separate step, once nothing calls it.
- Sandbox frontend not touched — build + test only, same discipline as Section 1.

### Acceptance criteria

- `scope=basin-ring`/`scope=buffer` on `/api/signature` return byte-identical payloads to
  today's `/api/areas?scope=basin_ring`/`scope=buffer` for the same real query — true
  equivalence, not "equivalent modulo a reshape," since nothing is reshaped.
- Every existing `/api/signature` caller (no `scope` param) verified byte-identical —
  full backward compatibility, tested explicitly, not assumed.
- Full suite green.

### Explicitly not in this section

`scope=area` (Section 3). Retiring `/api/areas`. Cliopatria/`/clio` wiring (Section 4, feeds
`scope=area` once it exists).

---

## Section 3 — `scope=area`, generic case

**Status: done, 2026-09-14 (`d45ce3f`).** `geom_wkt` param, `POLYGON`/`MULTIPOLYGON` only (regex
check on the WKT prefix, 422 otherwise) — no `bbox`-to-WKT conversion helper built; the test
input is a hand-written bbox-shaped WKT string, not a separate parameter. Calls
`areal_signature_polygon()` directly, same as Cliopatria polities already do.

**Real bug found and fixed while building:** `areal_signature_polygon()` hardcoded
`scope['type']='polity'` unconditionally — a leftover from being originally polity-only (WO20).
"A generic area call should not hard-code the term 'polity'" (Karl). Fixed with a new
`scope_type` kwarg on the engine function itself (default `'polity'`, so the existing
Cliopatria polity branch is completely unaffected — proven by a dedicated safety-net test, not
just assumed); the route passes `scope_type="area"` explicitly.

**Prerequisite done (`f69fcfc`):** `lat`/`lon` made `Optional` at the param level ahead of this,
checked per-scope like `radius_km` already was — `area` doesn't ask for them at all.

6 new tests (required-param, WKT-type rejection, working end-to-end case, direct engine-call
equivalence, area's own type label, the polity-path safety net). Full suite: 576 passed, 21
skipped. Public `scope` list is now complete: `[basin, buffer, area]`.

**Follow-up, 2026-09-14 — shape-parity pass (post-Section-3, before Section 4):** eyeballing
real payloads (`output/edop/lod-prep/scope_{basin,buffer,area}.json`, gitignored) surfaced two
gaps against basin's shape:

- **Band T row-explosion.** buffer/area explode Band T into one row per HYDE-epoch/LMR-year per
  member basin (a 250-year span on a 5-basin buffer alone produced 792 rows / 66k+ lines) —
  unlike basin's compact per-basin time series. Fixed (`2c18d59`) by requiring `from_year ==
  to_year` for these two scopes when `T` is requested (422 otherwise); basin's genuine
  multi-year range is untouched. v0.4-scoped fix, not a row-representation redesign — a
  technical user wanting per-slice time series still has to parse the full-monte payload
  themselves.
- **No `meta` block.** basin had one, buffer/area didn't (`06535af`). Both now get
  `signature_version`/`generated`/`query`/`data_sources`, via one shared
  `_data_sources_block(level)` helper so the three scopes can't drift on what it says.
  `meta.scope` stays basin-only — buffer/area's existing top-level `scope` object (`n_units`,
  `member_ids`, ...) is real result data, not a request echo, and left where it was.

Left open, not actioned: whether buffer/area should ever get `profile_groups`-style band
nesting (no strong technical reason it's absent — the per-row `band` field makes it mechanically
feasible — but basin's flat/raw shape and buffer/area's aggregate/distribution shape may simply
be two genuinely different kinds of data, not just missing normalization); the v0.3-style "show
URL" / "view raw JSON in a modal" GUI affordance Karl flagged as missing from v0.4 (separate,
GUI-side, not a schema question).

---

## Section 4 — Cliopatria via `/clio`, feeding `scope=area` (deferred; was Section 2)

**Status: written 2026-09-14, deferred — not superseded, just reordered.** Everything below is
the plan as drafted before the destination shape was locked; still the right shape, just comes
after Section 3 now, since Cliopatria's job is producing a WKT for `scope=area` to consume, not
a `scope` of its own. Revisit for exact wiring once Section 3 exists.

### Goal

A new, fully self-contained endpoint, `GET /api/clio/signature`, owns the whole Cliopatria
signature computation — resolve a slice, compute over its geometry, return the result.
`/api/areas`'s `scope=polity` branch keeps running exactly as it does today, untouched, for
the duration of this section — it becomes deletable only once nothing calls it anymore
(Section 5, after this section's frontend wiring is confirmed working). End state this
section moves toward: no `scope=polity` on `/api/areas` at all.

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

- **4a — backend only.** Build `_clio_resolve_slice` + `/api/clio/signature`. Verify
  standalone: for a real slice, its payload matches `areas()?scope=polity&polity=...&year=...`
  for the same slice's own fromyear (equivalence test, same pattern as Section 1's). Existing
  `TestPolityPayload`/`TestPolityFixtureEquivalence` (11 tests, exercise `areas()`'s untouched
  polity branch) must stay green, unmodified — proves nothing existing moved. Frontend not
  touched at this point.
- **4b — frontend wiring.** Switch `_silentResig()` and the click handler to
  `/api/clio/signature`. The one step that changes what a real click does — browser-verified,
  not just green tests, per Karl's standing habit.

### Acceptance criteria

- 4a: new equivalence test passes; existing 11 polity tests on `areas()` unaffected; full
  suite green; `/api/clio/signature` confirmed live via direct curl against a real polity.
- 4b: live-verified in browser (Northern Song or similar) — signature content identical
  before/after, across a slider move and a `[Get Signature]` click.

### Explicitly not in this section

Removing `scope=polity` from `areas()` — stays live as-is throughout this section, deletable
only in a later section once this section's frontend wiring is confirmed and nothing calls it.
Retiring `/api/polity/*` or `/api/area`. Any part of the destination shape beyond this one
path (`basin-ring`'s shape fix is Section 2's job, not this one).

## Section 5 — not written yet

Retiring `/api/areas`, `/api/area`, and `/api/polity/*` once nothing live calls any of them.
To be written only after Sections 2–4 are built, tested, and confirmed — not before.
