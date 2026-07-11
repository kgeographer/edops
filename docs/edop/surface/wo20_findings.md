# WO20 findings — WHG probe + integration

## F20.1 — Suggest endpoint now returns `repr_point` directly

The suggest response now includes a `repr_point` field `[lon, lat]` (or `null`) for each
result. This is new — when v1's WHG wiring was written, coordinates required a secondary
entity call. Example (Timbuktu city):

```json
{
  "id": "place:5424806",
  "name": "Tombouctou",
  "ccodes": ["ML"],
  "repr_point": [-2.9833, 16.8167],
  "has_geom": false,
  "type": [{"id": "...", "name": "Place"}]
}
```

`repr_point` is null when the place has no recorded location (e.g. Roman Empire: `null`).
`has_geom` appears to flag areal (polygon) geometry, not point presence — `has_geom: false`
even on the Timbuktu city record which has a valid `repr_point`.

## F20.2 — `_extract_lonlat` is broken; `/api/whg-place` returns `no_geometry` for all IDs

The entity endpoint response format changed. Current format is a GeoJSON Feature:

```json
{
  "type": "Feature",
  "geometry": {"type": "Point", "coordinates": [-2.9833, 16.8167]},
  "properties": {"fclasses": ["P", "S"], "ccodes": ["ML"], ...},
  "types": [{"label": "inhabited places", "gn_class": "P"}, ...]
}
```

`_extract_lonlat` (routes.py:107) looks for `entity.get("geoms")` — that key no longer
exists. Result: `/api/whg-place` returns `{status: "no_geometry"}` for every ID.

Fix is straightforward: check `entity.get("geometry")` first (current format), then
fall through to `geoms` as a legacy fallback.

## F20.3 — Entity endpoint only works for WHG-native IDs

`/entity/{id}/api` returns 404 for all external-namespace IDs:
- `place:tgn:7000471` → 404
- `place:wd:Q339462` → 404
- `place:osm:n2108499149` → 404
- `place:5424806` → 200 ✓ (WHG-uploaded)
- `place:dgsd:25830` → 404

The `_whg_search_candidates` function (which uses suggest + entity) filters out results
without `fclasses` — this silently drops most of the reconcile candidates, since only
WHG-native IDs can have fclasses retrieved. The `_noisy` regex already strips wd/osm
prefixes from reconcile results.

## F20.4 — No fclass discriminator available on the reconcile path

`fclasses` (GeoNames feature class: P=populated place, A=admin, T=territory, H=water,
R=road, S=spot/site) is the natural point-type filter. But it only comes from the entity
endpoint, which only works for WHG-native IDs. Reconcile results are predominantly TGN
and other namespace-prefixed IDs where entity calls return 404.

**Practical filter available**: `repr_point !== null` on suggest, or coordinate presence
on reconcile. This lets through regions and empires whose point happens to be their capital
(e.g. "Roman Empire" lands at 12.485, 41.892 — indistinguishable from "Rome" by coordinate
alone). No reliable server-side fclass filter exists for the full candidate set.

## F20.5 — Areal-extent candidates: how they appear

Areal/regional/polity candidates do appear in WHG results. Examples with Italy bounds:

```
place:tgn:7003138  Roma (province of Rome)  lat=41.97, lon=12.67  score=100
place:tgn:7030347  Empire romain            lat=41.89, lon=12.49  score=99
```

Both have coordinates (their representative point, not a polygon extent). They are
visually distinguishable in the name ("Empire romain", "Provincia di Roma") but not by
coordinate type. For WO20, the user selects from a named list — the name is the filter.

The areal-extent case does not require different coordinate handling. The point resolves
to a basin regardless of whether the WHG entry is a city or an administrative region.

## F20.6 — Bounds filtering: reconcile supports it; suggest does not

The reconcile endpoint accepts a `bounds` GeoJSON polygon and returns spatially-filtered
results. The suggest endpoint has no bounds parameter. The v1 zoom-gate (map must be at
zoom ≥ 4 before searching) ensures bounds are meaningful — they constrain the candidate
set to the viewport region. Without bounds, "Rome" returns small US towns first.

With Italy viewport bounds, Rome returns correct (Italian) results first. With Mali bounds,
Timbuktu city ranks second — behind the Tombouctou administrative region, which scores 100
because its alt_names include "Timbuktu".

## F20.7 — No country-code filter exists

Neither endpoint supports `?country=ML` or equivalent. Bounds is the only spatial
constraint. User's zoom position is the practical country selector.

---

## Payload sample

**Reconcile result (Timbuktu, Mali bounds):**

```json
{
  "id": "place:tgn:7000471",
  "name": "Tombouctou",
  "score": 100,
  "match": false,
  "alt_names": ["Timbuktu", "Timbuctoo", ...],
  "description": "Country: ML",
  "lon": -2.9833,
  "lat": 16.8167,
  "country": "ML"
}
```

**Suggest result (Timbuktu, no bounds):**

```json
{
  "id": "place:5424806",
  "name": "Tombouctou",
  "score": 100,
  "ccodes": ["ML"],
  "repr_point": [-2.9833, 16.8167],
  "has_geom": false,
  "type": [{"id": "...", "name": "Place"}]
}
```

---

## Architecture recommendation for integration

**Keep the reconcile+extend path** (`/api/whg-reconcile`) for the settlement lookup:
- Bounds filtering is the key advantage — viewport constraint is already enforced by the
  map zoom-gate and is the only spatial disambiguation available.
- Route already works and returns `{id, name, lat, lon, country, alt_names}`.
- No server-side changes needed to the route itself.

**Fix `_extract_lonlat`** as a minimal correctness repair (entity format changed; easy fix).
This is not strictly required for the reconcile path, but corrects a broken route.

**No fclass filter for WO20** — the named candidate list is the filter. The user reads
"Empire romain" vs "Rome" and selects appropriately. A fclass-based visual indicator
(e.g. dim admin/territory results) would be nice but requires entity calls that are only
reliable for ~20% of candidates; deferred.

**MapLibre markers** — v1 uses Leaflet `circleMarker` and `divIcon`. v2 uses MapLibre.
Candidate markers will be MapLibre `Marker` elements (HTML-based) rather than Leaflet layers.

---

## State model decisions

(To be settled with Karl on this payload before integration.)

**Q1: Settled anchor or per-search?**
WO20 spec: resolved point is an anchor; buffer and ring are lenses over the same point.
Single-basin fires immediately on candidate selection (no extra Get Signature click).

**Q2: What clears the anchor?**
- User clicks a different candidate → new anchor, new single-basin draw.
- User clears the search field (clear button) → anchor null, map layers cleared.
- User switches to the area (polity) lane → anchor persists or clears?
  Spec says don't over-reach into area lane — leave this for CC to settle across Arc A.

**Q3: Get Signature activation**
Spec: "Get Signature activates" on candidate selection. Interpretation: button becomes
enabled (not auto-fired). Single-basin fires automatically (draws basin on map); the full
signature is user-triggered via the button. This matches v1 behavior.

**Q4: Band T pre-fill**
On candidate selection, Band T year range should not auto-fill (no context for it).
User manually enables Band T and enters years. This differs from the polity path which
auto-fills from polity lifespan.

---

## Task 2 — Integration findings

**F20.8 — suggest chosen over reconcile for the settlement lane**
Suggest: one round-trip, `repr_point` direct, native `fclasses` filtering, no secondary
entity fetch. Reconcile's strengths (authority alignment, `bounds=` param, richer multi-source
payload) belong in a fuller WHG integration work order, recorded in the deferred items register.
Country hint (`countries=` param on suggest) was implemented in place of bounds filtering.

**F20.9 — Comma-parse country hint works; ILIKE sufficient**
`resolveSettlement()` splits the query on the last comma: `"Timbuktu, Mali"` → `q="Timbuktu"`,
`country="Mali"`. Route resolves via `gaz.ccodes ILIKE '%Mali%'` → `countries=ML`, passed to WHG.
Country hint failure (no match) silently proceeds without the filter. ILIKE on 237 rows is fast.

**F20.10 — Client-side viewport filter resolves the zoom-gate gap**
Suggest has no `bounds=` param, so the F20.6 zoom-gate note required a client-side fix.
After receiving suggest results, `resolveSettlement()` filters to candidates within the current
map bounds: `map.getBounds().contains([r.lon, r.lat])`. Falls back to showing all candidates if
none land in viewport. "Timbuktu" while zoomed to Mali returns only Tombouctou [ML].
`window._whgResults` exposes the post-filter candidate array in the browser console.

**F20.11 — `updateSigButton` now requires resolved lat/lon for point scopes**
Before WO20, scope selection alone enabled Get Signature for all scopes. Now:
`POINT_SCOPES` (buffer, single_basin, basin_ring) require both scope AND resolved coordinate
(`currentLat/currentLon !== null`). Area scopes (polity, draw) unaffected. Two Playwright tests
updated to assert `to_be_disabled()` when scope selected but no point resolved.

**F20.12 — Candidate display: headword + country name + alt_names**
Each list item: (1) headword name bold; (2) country name in muted text (not ISO ccode — users
rarely know [ML]); (3) first 3 alt names on a second line in 0.75 rem muted text; "+N more"
expands remaining inline on click. Country name resolved from `app/data/ccodes.json` (237 entries,
generated from `gaz.ccodes`, loaded as `_CCODES` dict at module startup — no DB round-trip per
call). Alt_names limit raised from 5 → 10 at route level; display truncates at 3 + expand.
The improvement was clearly essential: "San Jose, Mexico" returns 8 results, all named "San Jose",
only distinguishable by alt names (e.g. "San Jose del Sitio", "San Jose Valle del Maiz").

**F20.13 — `_fitMap` / `_showMapTab` hoisted to module scope**
Both helpers were defined inside the example-handler event-listener closure, making them
unreachable from `setResolvedPoint()` at module scope. Hoisted to the outer IIFE.
The bug would have surfaced on the first candidate selection; caught during integration.

**F20.14 — New route `/api/whg/suggest`**
`GET /api/whg/suggest?q=<str>[&limit=N][&country=<str>]` — settlement/site lookup filtered to
`fclasses=P,S`. Returns `{results: [{id, name, lat, lon, ccodes, alt_names, cname}]}`.
`repr_point`-less candidates silently dropped. `cname` (full country name) resolved from
`_CCODES` static dict, not DB.

**F20.15 — Tests: 8 route tests + 2 Playwright updates**
`TestWhgSuggestRouteValidation` (8 tests): input validation (missing/empty/short q), response
shape including `cname`, `repr_point` filtering, `fclasses=P,S` enforcement, country hint →
ccode resolution, no-match fallback. Two Playwright tests updated (`test_single_basin`,
`test_ring_scope_requires_point`): now assert `to_be_disabled()` for scope-only state.

---

## Accept gate

All items confirmed in browser by Karl:

- Viewport filter narrows candidates to current map extent
- Candidate display: country name (not ccode), alt names with inline expand
- Candidate selection fires single-basin, draws basin on map, enables Get Signature
- Get Signature fires and renders full signature
- Buffer and ring reachable as lenses over the resolved point
- "Timbuktu, Mali" → single Tombouctou [ML] result
- "San Jose, Mexico" → 8 candidates, all in Mexico, alt names distinguish them
- `sandbox.html` and Cliopatria lane untouched

**416 tests pass, 50 skipped.**
