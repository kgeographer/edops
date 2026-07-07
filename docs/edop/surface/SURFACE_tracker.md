# SURFACE — Phase tracker

**This is the living source of truth** for the Surface phase: current state, roadmap, and
locked decisions. If any other Surface document disagrees with this one about *where things
stand*, this one wins.

- **Location:** `docs/edop/surface/SURFACE_tracker.md`
- **Last updated:** 2026-07-07 (post-WO18: pasture/rangeland dropdown, Playwright fix, cropland ramp nit; 399 tests pass)
- **Maintained:** updated by CC at session end and whenever a decision is locked; read at the
  start of each step and each phase gate.
- **Rule:** when a decision is locked or a gap is resolved, remove the corresponding
  forward-looking note in the same edit — never leave a resolved item as an open question
  elsewhere in the file.

---

## What Surface is

Where the EDOPS engine meets a user. Areas built the engine (resolver → aggregator →
endpoint, whole); Surface builds what a person sees and does with it. The work is
consumer/UI discipline — page architecture, endpoint UX, what's meaningfully displayable —
distinct from the engine work that defined Areas.

**Two callers frame every display decision** (locked framing, carried from Areas discussion):
- **Raw API caller** — knows the payload, manipulates lean/`&detail` for their own purposes.
- **Dashboard/sandbox user** — interacts through a surface, and may (functionality TBD) use
  the surface to *build* an API call.

Much of what appears in the lean vs `&detail` payload is ultimately driven by these two
cases. Some display decisions legitimately ride until a dashboard is spec'd; the near-term
goal is to get a surface complete enough to *learn* what a dashboard can reasonably provide.

**The engine resolves and serves; it does not interpret** (Areas locked decision, 2026-06-27).
Summarization, significance thresholds, verdict-gates, and interpretive lenses live here, at
the surface, with the use case — not in the engine.

## Relationship to Areas

Areas is **frozen reference** (`AREAS_tracker.md`, closed 2026-06-30). Read it for settled
engine background — resolver types, aggregator blocks, the envelope, locked engine decisions.
Do not extend it. The **deferred items register is shared** and cross-phase: consult at every
step resumption, add rows there.

---

## You are here

Phase opened 2026-06-30. Engine is whole: four entry points, five resolvers, all in engine.py.
`resolve_basin_ring` + `basin_ring_signature` were promoted from notebooks on 2026-07-01 (77/77 tests).

**SF.1 (sandbox capability-gap analysis) complete** — `docs/edop/surface/surface_findings.md`.

**WO1 (exemplar payload inspection) complete** — all 13 cells run; findings F1.1–F1.13 in
`docs/edop/surface/wo1_findings.md`. Three engine TODOs fixed (shortfall clamp, dead
`row["distribution"]` field removed, basin-ring key contract); 80/80 engine tests pass.
Design notes for UI work in `docs/edop/surface/wo1_design-notes.md` (DN1–DN10).

**Step 0 (skeleton) complete** — `app/templates/sandbox_v2.html` at `/sandbox/lookup2`
(not linked from anywhere); scope gate + Band T toggle JS; Level fixed L06; 5-scope dropdown;
4 exemplar examples; 40 structural tests in `tests/surface/test_sandbox_v2.py`.

**Build workflow established:** `docs/edop/surface/surface_workflow_opus.md`.
**State/renderer model:** `docs/edop/surface/surface_state-analysis.md`.

**Playwright browser tests complete** — 22 UI state tests in `tests/surface/test_sandbox_v2_ui.py`;
live server fixture in `tests/surface/conftest.py`.

**WO3 (Step 2 leaf widgets) complete** — buffer scope live; B1 histogram (weighted SVG, native-unit
axis); B2 coherence badge (concentrated/spread/null); B3 range-bar (p10–p90 + regime marks);
B4 mixture bar (modal label + proportion fill). Findings F3.1–F3.4; 263/263 tests pass.
Per-WO branch pattern established: `surf_wo3` merged back to `surface`.

**WO4 (`/api/areas` + buffer live) complete** — `GET /api/areas?type=buffer` wired; two-pass
validation; buffer scope on sandbox_v2 makes live DB calls. Accept-gate equivalence tests
(live vs `02_buffer_detail.json` fixture) pass; 271/271 tests pass (excl. Playwright).

**WO5 (polity fixture + Band T charts) complete** — Northern Song example wired to polity
fixture; Band T accordion renders LMR time marginal (mean + p10–p90 envelope) + per-variable
year slider → value marginal histogram; HYDE epoch table; eVolv2k event list. A–E unchanged.
Findings F5.1–F5.5 in `wo5_findings.md`; 271 non-Playwright + 22 Playwright = 293 total.

**WO6 (polity scope live) complete** — `type=polity` added to `/api/areas`; Northern Song
example wired to live call; equivalence confirmed against fixture (F6.1–F6.3).
286 non-Playwright + 22 Playwright = 308 total tests pass.

**WO7 (arbitrary polity search) complete** — polity search field wired to `/api/polity/search`
(220 ms debounce, from cliopatria.html); results dropdown → `selectPolity` → `/api/polity/slices`
→ slice picker dropdown; selecting a slice draws the boundary and fires `applySlice`. Band T
auto-fills from polity full lifespan (not individual slice dates — F7.2); resolver year threads
targetYear to preserve the requested year (F7.3). Three UX polish items: accordions default
A–E collapsed / T open; map tab switches on polity change; spinner on signature load.
Findings F7.1–F7.5 in `wo7_findings.md`. 291 non-Playwright + 22 Playwright = **313 total tests pass**.

**WO8 (MapLibre stack + layer shell) complete** — Leaflet replaced with MapLibre GL JS on v2
page only; layer-management shell (`add`/`remove`/`restyle`/`clear`) established; polity
boundary outline reproduced via shell as acceptance proof. GeoJSON sources for low-cardinality
scopes; PMTiles deferred to polity choropleth. `map.invalidateSize()` → `map.resize()`.
Findings F8.1–F8.3 in `wo8_findings.md`. 313/313 tests pass (no changes needed).

**WO9 (audit) complete** — single-basin true state confirmed (fixture-only, no live route);
basin-ring weight policy row closed in deferred register (design: per-member signatures, no
aggregate). Findings in `wo9_audit_findings.md`.

**WO10 (single-basin live) complete** — `type=single_basin` added to `/api/areas`;
`single_basin_signature` entry point now HTTP-wired; frontend live branch added; Band T
verified live via polygon path. Stale "not yet supported" docstring corrected. Playwright
`TestRenderer` updated to use live path. 332/332 tests pass.
Findings in `wo10_findings.md`.

**WO11 (single-basin map) complete** — `drawSingleBasin()` added; fetches `/api/basin-preview`,
confirms `hybas_id` honesty check (sig ↔ map same basin), draws polygon via `shell.add('single-basin', ...)`,
fit-bounds to basin. No tab switch on sig load (design: user navigates Map tab themselves).
Timbuktu basin is MultiPolygon — test accepts both polygon types. 336/336 tests pass.
Findings in `wo11_findings.md`.

**WO12 (example-select standard + buffer map) complete** — example handler standardised
(single/buffer/polity/ring/draw all follow one shape); Map is default landing tab after
Get signature; buffer geometry drawn via shell (member basins unclipped + dashed circle);
`member_ids` added to buffer neighborhood; new `GET /api/basin/geom` route; `FIXTURE_URLS`
cleaned up; ring and draw get placeholder messages. `fitBounds` refactored to fire via
`map.once('resize')` after tab switch (was off-centre when map hidden). `geojsonBbox`
extended for FeatureCollections. Findings in `wo12_findings.md`.

**WO13 (basin-ring live) complete** — ring scope end-to-end: center sig in accordions (full
Band T), center + ring drawn on map (two shell layers, categorically colored), ring members
clickable for on-demand member sig (~1 s fetch), return-to-center via center basin click.
Parallel fetch architecture: center sig + ring topology in parallel (~1.1 s total vs 6.7 s
sequential full-ring). New `GET /api/basin/ring` fast topology route (92 ms). Ring info div
in left column explains the new interaction. Band T available for all members (per-member
`type=single_basin` calls use current UI settings). 391/391 tests pass (109 surface + 282
non-surface). Findings in `wo13_findings.md`.

**WO14 (basin choropleth) complete** — PMTiles basin06 vector source + feature-state paint
loop for 4 BasinATLAS variables (aridity, precip, temperature, cropland); RDBU colour ramp
direct-port from cliopatria; LMR/HYDE entries present-but-inert (WO15 enables). Shell
extended with `{ before }` option for insertion below existing scope layers. `#v2-intro`
restructured: `#v2-intro-text` hides on sig load, `#v2-choropleth` persists. Legend shows
p10–p90 domain + ramp. 395/395 tests pass (+4 BS, +11 Playwright, +3 route). Findings in
`wo14_findings.md`.

**WO15 (LMR paint + example-select UX) complete** — LMR temperature and precipitation anomaly
variables live in the basin-variable selector; painted from `lmr_notches.geojson` (5 notch
periods, not per-year); diverging RDBU ramp centred on zero; legend states anomaly framing.
Paint-year slider built but hidden (default 1100 CE / MCA notch); deferred UI pending state
model resolution (pre-Braga required item in deferred register). State audit conducted:
7 conflict types documented in `wo15_state_audit.md`; scope dropdown sidelined as hidden
on load / display-only for polity example; example dropdown is the controlling input.
Preview geometry drawn immediately on example select for all 4 active scopes (single, buffer,
ring, polity). Get Signature now lands on Signature tab (not Map tab). Choropleth cleared
and selector reset on example change. `_fitMap()` helper resolves fitBounds when map tab
already active. 80/80 structural tests pass (+9 from WO15). Findings in `wo15_findings.md`.

**WO16a (HYDE basin values — feasibility + implementation) complete** — Architecture review
established that pre-baked epoch raster tiles (Explorer approach) are wrong for EDOPS: 7-epoch
bins average 10–30 DB steps each, destroying temporal precision. Correct architecture:
values-API + feature-state on `basin06.pmtiles` (same pattern as basin choropleth). Feasibility
notebook (`notebooks/edop/surface/wo16a_hyde_basin_values.ipynb`) confirmed: centroid lookup
returns 16,040-basin dict in 0.31s, 354 KB — same shape as `/api/explorer/values`. New
`/api/hyde/values?var=X&year=N` route (centroid lookup; cropland stored as km²/cell, divided
by `area_km2` for fraction; year floor-snapped via `temporal.hyde_times`). Frontend: raster
block replaced by `applyHydeChoropleth` using `interpTwo` + feature-state. Slice-change
reactive repaint: `applySlice` now re-fires active HYDE or LMR paint with `s.fromyear`,
so slice switches update the choropleth without requiring a new Get Signature. 93/93 structural
tests pass (+13 from WO16a). Findings in `wo16_findings.md`.

**WO17 (area-weighted HYDE crosswalk) complete** — `temporal.hyde_basin06_weights` materialized
(2.82M rows, 1.2 min build); area-weighted method validated against BasinATLAS `crp_pc_sse`
(r=0.902 vs centroid 0.689). Route swap blocked: per-request query time 2.67s vs 0.31s centroid
— the 2.82M-row join to `hyde_cells` for per-step array access is the bottleneck. Crosswalk is
correct; route swap requires pre-aggregation (WO18). Denominator settled: `frac_full` (÷ sub_area),
consistent with BasinATLAS. 241 centroid-null basins recovered; 116 genuinely null → transparent.
Findings in `wo17_findings.md`. Notebook: `wo17_hyde_area_weighted.ipynb`.

**Post-WO18 (2026-07-07)** — HYDE pasture and rangeland added to choropleth dropdown
(`HYDE_DB_VAR` + `HYDE_RAMPS` extended; 2 new structural tests). 12 stale Playwright tests
fixed (WO15 had hidden the scope dropdown and changed tab routing without updating the tests).
Cropland ramp lo colour corrected to white (0 = no cropland, not pale green) — `kg_nits01`
branch merged. **128 surface tests pass, 36 skipped; 399 total (app + engine + surface).**

**WO18 (HYDE pre-aggregation + route swap) complete** — `temporal.hyde_basin06_steps`
materialized (2.08M rows, 9.9 min build; 128 steps × 16,281 basins × 4 vars). Per-request
0.033s (80× faster than WO17 2.67s; 6× under threshold). `/api/hyde/values` now queries
pre-aggregated table; centroid join retired. One basin (hybas_id 5060271430) has grazing/rangeland
frac = 1.0016 due to sub_area/covered_km2 mismatch; clamped to 1.0 in route. Coverage 16,281
(vs centroid 16,040). Value agreement with WO17 max delta 7.94e-08. 364/364 tests pass.
Findings in `wo18_findings.md`.

---

## Roadmap (seed)

| Item | What | Status |
|---|---|---|
| Sandbox capability-gap analysis | Inventory: what the engine now offers that no UI exposes; what `sandbox.html` currently exposes; the delta; and whether the existing markup can absorb the new elements or forces a new page. | **complete** — see SF.1 |
| WO1 — exemplar payload inspection | Capture + inspect real payload dumps for all five query scopes (single-basin, buffer, polity+Band T, basin-ring, polygon). Ground truth for page design decisions. | **complete** — F1.1–F1.13; TODOs fixed |
| New sandbox page — Step 0 skeleton | `sandbox_v2.html` at `/sandbox/lookup2`; scope gate + Band T toggle; Level L06 fixed; 5 scopes; 4 examples; 40 tests. | **complete** |
| New sandbox page — Step 1 rows-renderer | Atomic rows-renderer against single-basin exemplar fixture; all 6 method leaves render something before any are made nice. | **complete — WO2** |
| Playwright setup | Browser-automation test harness for JS state tests (scope gate, T toggle, renderer output). Karl evaluated and confirmed. | **complete** |
| New sandbox page — Step 2 leaf widgets | Polish each method leaf one at a time: histogram widget, coherence badge, range-bar, mixture bar. One review gate per leaf. | **complete — WO3** |
| `/api/areas` + buffer live | New type-dispatched route; buffer scope live with accept-gate equivalence test. | **complete — WO4** |
| Polity fixture + Band T charts | Northern Song fixture-wired; LMR time marginal + slider + value marginal; HYDE epoch table; eVolv2k events. | **complete — WO5** |
| Polity scope live | `type=polity` in `/api/areas`; Northern Song wired to live DB call; equivalence confirmed. | **complete — WO6** |
| Arbitrary polity search | Polity search field → `/api/polity/search` → slice picker → live sig call for any polity. | **complete — WO7** |
| MapLibre stack + layer shell | Leaflet → MapLibre on v2; layer-management shell; polity outline via shell as proof. | **complete — WO8** |
| Single-basin live | `type=single_basin` in `/api/areas`; frontend live; Band T verified via polygon path. | **complete — WO10** |
| Single-basin map | Containing basin polygon drawn via shell after sig load; honesty check; fit-bounds. | **complete — WO11** |
| Example-select standard + buffer map | One handler shape for all scopes; Map-first landing; buffer basins + circle via shell; member_ids in payload; /api/basin/geom route. | **complete — WO12** |
| Basin-ring live | Ring scope end-to-end: center sig + ring map (two layers) + clickable members + return-to-center. Parallel fetch; /api/basin/ring topology route. | **complete — WO13** |
| Basin choropleth | PMTiles vector source + feature-state paint for 4 BasinATLAS vars; RDBU ramp; legend; `#v2-intro` restructured; shell `before` extension. | **complete — WO14** |
| LMR paint + example-select UX | LMR temp/precip anomaly choropleth; 5-notch data structure; diverging ramp; state audit; scope dropdown sidelined; preview geometry on example select. | **complete — WO15** |
| HYDE choropleth (values-API) | Architecture review → values-API over epoch rasters; feasibility notebook; `/api/hyde/values` route; `applyHydeChoropleth`; slice-reactive repaint for HYDE + LMR. | **complete — WO16a** |
| HYDE area-weighted crosswalk | Proof that area-weighted aggregation is correct (r=0.902); crosswalk materialized; route swap blocked by 2.67s query time. Pre-aggregation required. | **complete — WO17** |
| HYDE pre-aggregation + route swap | `hyde_basin06_steps` built; `/api/hyde/values` swapped; 0.033s per-request; 364/364 tests. | **complete — WO18** |
| `/area` input types beyond polity | Raw GeoJSON (user-drawn study area, POST body; arbitrary-boundary analyst-drawer caveat); buffer-fronting / endpoint consolidation; multi-timestep response shape. | surface-driven; deferred until the page pulls for them |
| Dashboard (true) | Stakeholder-polished. Some ways off. The sandbox is the intermediate that teaches what a dashboard can provide. | future |

---

## Known constraints (carried in, treat as locked)

- **Existing sandbox (`sandbox.html`) is public; its tests stay all-green.** No edits to the
  working Lookup page. The new page is additive.
- **Explorer (`explorer.html`) is a Phase 2 CHAR exhibit** — reports the finished
  characterization off the flat values API. It has no reason to call the areal engine; do not
  retrofit it.
- **Two temporal axes are independent and must present as such.** `resolver_year` (moves the
  polity boundary) and Band T span (`from_year`/`to_year`, moves aggregation). The engine
  keeps them separate and stamps both on the histogram; the surface must not collapse them
  into one control, or it reintroduces the confounding the stamp was built to prevent. This
  is the sharpest new UI problem the polity path introduces, since the old sandbox only did
  point/buffer and had no moving boundary.
- **Map paint comes from the existing global tileset, not `/area`.** Selecting a polity draws
  a boundary overlay on a query-independent global layer; the endpoint serves signature +
  histograms, not geometry for painting.

---

## Milestone

- **Braga (2026-09-20)** — UNED Digital Humanities conference; demo with Pitt colleagues.
  Stated target: v0.4 signature + updated sandbox surfacing the areal engine (lean/full, new
  resolver types, endpoint params). The new sandbox page is the deliverable that serves this.
  ~11 weeks out at phase open.

---

## Locked decisions

Append-only; dated. Settled unless explicitly revisited here.

**2026-07-06 (WO16a — HYDE basin values)**

- **Values-API over epoch rasters** — pre-baked PNG tiles average multiple DB steps (epoch 4
  averages 10 steps: 100–1000 CE), destroying temporal precision. Correct architecture:
  geometry from `basin06.pmtiles` (static, already loaded) + `/api/hyde/values` (values per
  request). Same pattern as basin choropleth and LMR.
- **`/api/hyde/values?var=X&year=N`** — centroid lookup: basin centroid → containing HYDE cell;
  year floor-snapped via `WHERE year_ce <= year ORDER BY year_ce DESC LIMIT 1`. Returns
  `{hybas_id: fraction}` dict (~354 KB, 0.31s). `cropland` stored as km²/cell — divided by
  `area_km2` for fraction. 357 missing basins (island/coastal) return null (transparent paint).
- **118 CE-era steps available** — `temporal.hyde_times` has 100-year resolution through ~2010,
  annual thereafter. Any of these steps addressable via the route.
- **Slice-reactive repaint** — `applySlice` re-fires active HYDE or LMR paint with `s.fromyear`
  whenever the slice picker changes. Both temporal choropleth types now track the displayed slice.
- **Crosswalk built in WO17** — `temporal.hyde_basin06_weights` materialized; see WO17 locked decisions below for details. Route swap to use it requires pre-aggregation (WO18).

**2026-07-07 (WO18 — HYDE pre-aggregation + route swap)**

- **`temporal.hyde_basin06_steps`** — 2,083,968 rows (16,281 basins × 128 steps × 4 vars).
  `frac_full` (÷ `sub_area`) per WO17 decision. Indexes: `(step_idx)`, `(hybas_id, step_idx)`.
- **`/api/hyde/values` route swap** — centroid join retired; now `SELECT hybas_id, {var}_frac
  FROM temporal.hyde_basin06_steps WHERE step_idx = N`. Per-request: 0.033s (vs 2.67s WO17,
  0.31s centroid). Response shape unchanged; frontend requires no change.
- **Clamp at 1.0** — `min(v, 1.0)` in route dict comprehension. One basin (hybas_id 5060271430)
  has grazing/rangeland frac = 1.0016 due to `sub_area`/covered_km2 mismatch (0.16%). Table
  stores the honest arithmetic; physical constraint enforced at display layer.
- **116 no-land basins** — absent from table (no rows), not NULL rows. Route returns no entry
  for these basins; frontend treats absence as null → transparent paint.

**2026-07-07 (WO17 — area-weighted HYDE crosswalk)**

- **`temporal.hyde_basin06_weights` schema**: `(hybas_id bigint, cell_id integer, overlap_frac real)`.
  `overlap_frac = ST_Area(intersection) / ST_Area(cell)` — planar ratio; distortion cancels.
  Denominator choice deferred to query time (not baked in), enabling both `frac_full` and `frac_covered`.
- **Denominator: `frac_full` (÷ sub_area)** — empirically identical to `frac_covered` for 95%+ of basins
  (coverage ratio ≈ 1.0); r values differ by 0.001. `frac_full` is consistent with BasinATLAS.
- **Route swap blocked**: per-request join = 2.67s vs 0.31s centroid baseline. Bottleneck is
  2.82M-row join to `hyde_cells` for array access. **WO18** resolves by pre-aggregating all
  128 steps × 4 vars → `temporal.hyde_basin06_steps (hybas_id, step_idx, cropland_frac, grazing_frac, ...)`.
  Per-request becomes an indexed point lookup, expected <100ms.
- **r improvement 0.689 → 0.902** at 2000 CE vs BasinATLAS `crp_pc_sse`. Validates method.
- **Coverage**: 16,281 of 16,397 basins (241 centroid-nulls recovered; 116 genuinely no-land → transparent).
- **Unit guard passed**: no fraction exceeds 1.0.
- **Methods note**: uniform-within-cell distribution assumed (finest structure HYDE 3.4 asserts);
  within-basin heterogeneity not represented — basin-level summary, same epistemic object as all other EDOPS bands.

**2026-07-06 (WO15 — LMR paint + example-select UX)**

- **LMR data structure: 5 notches, not per-year** — `lmr_notches.geojson` stores pre-aggregated
  notch-period means (`air_0`–`air_4`, `prate_0`–`prate_4`); quality floor at 700 CE (years
  < 700 CE paint nothing silently). Per-year paint requires a new API route; logged in deferred
  register as pre-Braga required.
- **Paint-year slider hidden** — slider in DOM at default 1100 CE (MCA notch); hidden from user.
  Showing it creates framing confusion with Band T from/to. Deferred until the slice-synced
  route exists.
- **Anomaly ramp** — RDBU diverging, centred on zero. Domain = ±abs-max of painted values.
  Legend mid-label: `0 (850–1850 mean)`. Caveat hard-coded (payload field unreachable from
  scope-independent choropleth path — acceptable WO15 fallback; wiring deferred).
- **Scope dropdown sidelined** — `#v2-scope-wrap` hidden on page load (`display:none`). On
  polity example select: shown with all options disabled (display-only, confirms scope). On
  single/buffer/ring: remains hidden. Scope dropdown as a free-standing input is deferred.
  Example dropdown is the controlling input.
- **Example-select preview geometry** — geometry drawn immediately on example select, before
  Get Signature: single → `drawSingleBasin(lat, lon, null)` (honesty check skipped when
  `sigHybas_id=null`); buffer → geodesic dashed circle only (basin polygons require resolver
  output); ring → `/api/basin/ring` fetch + `drawRingGeometry` (full topology, hover/click
  ready). Prior scope layers cleared before each preview draw.
- **`_fitMap(bbox)`** — calls `map.fitBounds` directly if map tab already active; otherwise
  `map.once('resize')`. Replaces brittle resize-only pattern.
- **Get Signature → Signature tab** — sig button handler no longer switches to Map tab on
  success. User has seen the map via preview; sig tab was already shown with spinner at fetch
  start. Map `fitBounds` queued via `map.once('resize')` for next manual Map tab open.
- **Choropleth clear on example change** — `clearLMRPaint()` + `removeFeatureState` on basin
  source + selector reset to blank on every example select.
- **State audit** — 7 conflict types (C1–C7) between two generators documented in
  `wo15_state_audit.md`. No architectural fix this WO; audit is prerequisite for state-model pass.

**2026-07-05 (WO12 — example-select standard + buffer map)**

- **`member_ids`** added to buffer neighborhood block in `areal_signature` — list of
  hybas_ids for the member basin set, enabling the map draw honesty check.
- **`GET /api/basin/geom?ids=<csv>&level=6`** — new read-only route; returns GeoJSON
  FeatureCollection for a hybas_id list. hybas_ids cast to int (DB returns float).
- **Buffer map:** `shell.add('buffer-basins', fc, [fill, line])` (fill + 0.75 px border)
  then `shell.add('buffer-circle', geodesicCircle, [dashed line])`. Circle constructed
  client-side (64-step geodesic trig, no library). Honesty check: returned id set must
  equal `member_ids` exactly.
- **Map-first landing** — after Get signature (single, buffer, polity), Map tab becomes
  active. `fitBounds` fires via `map.once('resize', ...)` registered before tab switch;
  `shown.bs.tab` → `map.resize()` → fitBounds with correct container dimensions.
- **`geojsonBbox` extended** for FeatureCollections — collects coordinates from all features.
- **`FIXTURE_URLS` cleaned up** — all three entries were dead (live handler branches
  precede the else fallthrough). Ring and draw get explicit placeholder branches.

**2026-07-05 (WO14 — basin choropleth)**

- **PMTiles source via shell** — `shell.add('basin-choropleth', {type:'vector', url:'pmtiles://...'}, layerSpecs)` works as-claimed; no restructuring of the shell was required for the vector source type.
- **Shell extended: `{ before }` option** — `shell.add(name, sourceSpec, layerSpecs, { before })` (optional fourth arg) passes `before` to `map.addLayer`. Enables insertion below existing layers. Required to guarantee choropleth renders under scope geometry when loaded lazily (after Get Signature).
- **Lazy load on first variable select** — `loadBasinLayer()` is not called at map init; it runs at first non-empty variable selection. `_basinLayerLoaded` flag prevents re-registration. Eager init caused PMTiles tile-fetch requests to contend with ring sig API calls in concurrent tests.
- **`#v2-intro` restructured** — `#v2-intro` is now a container with two residents: `#v2-intro-text` (hidden on sig load) and `#v2-choropleth` (always visible). Choropleth controls persist after any sig load.
- **4 live variables, LMR/HYDE inert-present** — `aridity_index`, `precipitation_annual`, `temperature_annual` (reverse=true), `cropland_pct` (green, fixed domain). LMR/HYDE as disabled `<option>` entries for WO15 activation without menu restructuring.
- **Colour ramp** — RDBU_PAL (`interpRdbu`) shared across all 4 vars; reverse flag for temperature; `interpTwo` (custom green) for cropland. Direct port from cliopatria.

**2026-07-05 (WO13 — basin-ring live)**

- **`GET /api/basin/ring`** — fast topology route; returns `{center: Feature, ring: [{hybas_id, neighbor_lat, neighbor_lon, feature: Feature}, ...]}`. 92 ms. Used by frontend; `type=basin_ring` on `/api/areas` retained for API completeness only.
- **Ring frontend: parallel fetch** — center sig (`type=single_basin`) + ring topology (`/api/basin/ring`) fetched in parallel. Total ~1.1 s vs 6.7 s sequential. Center sig stored as `_centerPayload` for return-to-center.
- **Ring map: two shell layers** — `ring-center` (darker, 0.30 fill opacity) and `ring-members` (lighter, 0.12 fill opacity). Categorical distinction only; no value encoding.
- **Per-member sig on demand** — clicked member fetches `type=single_basin` at `neighbor_lat/neighbor_lon` with current UI Band T settings. Band T fully available for members.
- **Return-to-center** — click center basin → `renderCenterSig()` restores `_centerPayload`; switches to Sig tab. No re-fetch.
- **Hover affordance** — MapLibre Popup (`closeButton:false, closeOnClick:false`); ring members show "View signature", center shows "Return to center". No summary content in hover — link only.
- **Ring info div** — `#v2-ring-info` shown by `applyScope('ring')`, hidden for all other scopes; persists through sig load; explains clickable-member interaction.
- **Example handler standard** — one shape for all five scopes; polity's
  slice-fetch-renders-immediately remains codified, not a special case.

**2026-07-04 (WO11 — single-basin map)**

- **`drawSingleBasin(lat, lon, sigHybas_id)`** — fetches `/api/basin-preview`, extracts
  `containing_basin`, compares `hybas_id` to `payload.neighborhood.hybas_id` before drawing.
  Mismatch logs error and skips draw. Map mismatch guard is a contract test in `TestSingleBasinMapHonestyCheck`.
- **Shell call:** `shell.add('single-basin', { type: 'geojson', data: feature }, [fill, line])`.
  Fill: `#4a90c4` at 0.15 opacity; line: `#2c5f8a` 1.5 px. `fitBounds` with 40 px padding.
- **No tab switch** after sig load — user navigates Map tab themselves. Polity switches to Map
  on *selection* (before sig fetch); single-basin doesn't have that natural trigger.
- **MultiPolygon basins** — Timbuktu L06 basin is MultiPolygon. Shell and MapLibre handle both
  polygon types without change.

**2026-07-04 (WO8 — MapLibre stack + layer shell)**

- **Leaflet → MapLibre GL JS** on v2 page only; `sandbox.html` (Lookup) keeps Leaflet.
- **Layer shell** (`add`/`remove`/`restyle`/`clear`) — named layers, each = one MapLibre
  source + one or more layer specs. All future map WOs call the shell; no scope knows about
  `map.addSource` / `map.addLayer` directly.
- **GeoJSON sources for low-cardinality scopes** (single basin, ring, polity outline).
  PMTiles deferred to polity choropleth (WO-e), where vector-tile performance is actually
  needed. Shell accepts either source type without branching — no restructuring required at WO-e.
- **`_polityLayer` retired** — `drawPolityBoundary` now calls `shell.add('polity-boundary', ...)`
  and `geojsonBbox` for fit-bounds. Slice changes auto-remove the old layer via shell idempotency.
- No test changes needed; no Playwright assertions were Leaflet-specific.

**2026-07-04 (WO7 — arbitrary polity search)**

- **`applySlice` is the Band T auto-fill point** — both the example handler (pre-fills before
  calling `selectPolity`) and the manual search path converge on `applySlice`. Guard:
  `if (!tCb.checked || !fyEl.value)` preserves any explicit pre-fill; only auto-fills when T
  is unchecked or from_year is empty.
- **Band T span = full polity lifespan** — `Math.min/max` over `_politySlices` fromyear/toyear.
  Individual slice dates can be a single year (e.g., N Song 961–961), which falls between HYDE
  time steps and misses eVolv2k entirely. Full lifespan is the correct temporal window for
  polity analysis. Resolver year and Band T span remain strictly separate (two-axes invariant).
- **`resolverYear` param threaded through `selectPolity → applySlice`** — resolver year carries
  the user-requested year (from example targetYear or slice fromyear), not silently snapped to
  a slice endpoint.
- **Accordion default: T open, A–E collapsed** — polity queries land on temporal charts
  without scrolling past the A–E rows first.
- **Map tab on polity change** — `selectPolity` and slice-change listener both switch to Map
  tab so the user sees the new boundary before inspecting the signature.
- **Spinner on signature load** — immediate pane feedback + tab switch before fetch; button
  disabled during load; re-enabled in `finally`.
- **HYDE dense-epoch layout (F7.5)** — HYDE shifts to annual steps post-~1950; the current
  table breaks with O(span_years) columns. Deferred to a polish pass; add to deferred register.

**2026-07-04 (WO6 — polity scope live)**

- **`type=polity` in `/api/areas`** — same DB lookup + narrowest-span logic as `/api/area`;
  appends `resolver` block and `band_t_span` to payload. `/api/area` untouched.
- **Equivalence confirmed** — live N Song response matches `03_polity_nsong_detail.json`
  on variable list, methods, bands, row count (372), neighborhood shape.
- **`resolver` + `band_t_span` are route-added metadata** absent from fixture (fixture was
  captured direct from engine). Renderers ignore them; equivalence tests allow extra keys.

**2026-07-03 (WO5 — polity fixture + Band T charts)**

- **Band T visualization for LMR**: time marginal (mean line + p10–p90 envelope SVG) +
  per-variable year slider → value marginal histogram. Built directly from per-year row
  structure (`detail.distribution` in each T row). Raw-dump stage skipped — design was
  clear from fixture inspection.
- **Band T is a span, not a snapshot** (F5.1) — confirmed from fixture. LMR: 101 rows/var;
  HYDE: 2 epoch rows/var; eVolv2k: 9 discrete events. No engine change needed for the
  span case.
- **HYDE epoch table** — two data points; blocky-bar treatment deferred; table stays.
- **eVolv2k event list** — year + VSSI (Tg S); discrete events, not a distribution.
- **Polity scope fixture-only** — Northern Song example wired to `03_polity_nsong_detail.json`.
  Live polity call (`/api/areas?type=polity`) deferred to WO6.
- **Map: no action in WO5** — polity boundary overlay on map is a later step.
- **What a map would need** (F5.4) — per-unit values at a specific year, not an aggregate.
  A separate endpoint scoped to a polity; add to deferred register when map step is planned.

**2026-07-03 (WO4 — `/api/areas` + buffer live)**

- **`GET /api/areas`** — type-dispatched front door over area resolvers. `type=buffer` only
  in WO4 (others 422). Two-pass validation: type-params first, Band T span second.
  Serialize unmodified — no transform in the route.
- **`/api/area` untouched** — live route serving the existing three pages; never aliased,
  folded, or deprecated within Surface work. `/api/areas` is a new route alongside it.
- **Accept-gate equivalence test** — `TestFixtureEquivalence` in `tests/test_areas.py`
  loads `02_buffer_detail.json` and diffs against the live response: variable list, method
  per variable, band per variable, scores within 0.5 pct, neighborhood n_units/unit_type.
- **Polity scope** — deferred in WO4; live polity path belongs in WO6.

**2026-07-03 (WO3 — leaf widgets)**

- **Native-unit histogram axis** — bins are native values, not global percentiles. Fixed
  0–100 domain dropped. Each histogram has its own x-scale; cross-variable visual comparison
  is intentionally foreclosed (shape within a variable is the read; score handles global rank).
  Forward: Band T reuses the same `renderHistogram` function with native units.
- **Histogram trigger on method, not null-check (DN9)** — `renderHistogram` called inside
  `area_weighted` case only; safe-returns empty string if distribution data absent.
- **`detail.classes` null for all resolver types** — minority class breakdown unavailable
  from the engine. Mixture bar shows modal label + proportion fill only. Engine gap logged in
  deferred register; surface display deferred pending engine change.
- **Modality trigger is `regimes !== null`**, not `modality === 'two_regime'` — fixture shows
  `modality: null` even for bimodal rows; regime marks drawn when `det.regimes` is non-null.
- **Per-WO branch pattern** — `surf_wo3` branched from `surface`, merged back on accept gate.
  Pattern: `surf_wo{n}` → feature work → merge to `surface` at WO close.
- **n=1 cross-unit widget suppression** — histogram and coherence badge should render nothing
  when `n_units === 1` (no spread to show). Deferred to polish pass; rule generalises to all
  cross-unit widgets.
- **Per-variable direction metadata needed** — aridity is humidity-positive (low score = dry),
  exposing a semantic-inversion class of error present across multiple variables. Surface needs
  a direction annotation read from the variable catalog, not per-variable hardcoding. Catalog
  audit and `direction_note` column are the action item (F3.3).

**2026-07-03 (Playwright setup)**

- **Playwright** — `pytest-playwright` confirmed as the browser-automation layer for JS
  state tests. `tests/surface/conftest.py` provides a session-scoped `live_server_url`
  fixture (uvicorn daemon thread on port 8765; health-check poll before yielding).
  `tests/surface/test_sandbox_v2_ui.py` — 22 tests across 5 classes: initial state (6),
  scope gate (6), Band T toggle (2), example pre-fill (4), renderer (4).
  Playwright `page` fixture is function-scoped (fresh browser page per test).
  Class-token matching uses `re.compile(r"\bdisabled\b")` — `to_have_class` with a plain
  string checks the whole attribute, not a token.

**2026-07-02 (WO2 — rows-renderer)**

- **Fixture harness** — `app/main.py` conditionally mounts `output/edop/surface/exemplars/`
  at `/dev/exemplars/` via `StaticFiles` (try/except so absent on server). JS fetches the
  static JSON; swapping `FIXTURE_URLS[scope]` value to a live route is the one-line wiring
  step. Forward constraint: route must serialize payload unmodified when wired.
- **`renderSignature(payload)`** — builds band accordion (A–E) from `payload.rows[]`;
  dispatches each row on `row.method` to `renderLeaf`. Written single-basin-atomic; same
  function over more rows covers multi-unit. All 6 method branches implemented:
  `area_weighted` (score + coherence + `[hist]` slot), `dominant_basin` (score + raw numeric
  + carrier basin id), `class_mixture` (string label from `representative_raw` — DN7 handled),
  `flag_fraction` (0–1 fraction), `distribution_only` (p10–p90 range + suppressed caveat),
  `extreme` (score + raw + carrier basin).
- **Field names confirmed from fixture:** `representative_score`, `representative_raw`,
  `score_suppressed` (not the shorthand `score`/`raw` in the WO doc).
- **13 fixture contract tests** added to `tests/surface/test_sandbox_v2.py`: fixture served,
  top-level keys, row count (52), all 6 methods present, field name guards, DN7 string-raw
  check, neighborhood block, rows in each band.
- **Accept gate passed** — all 6 method types render without throwing; single-basin fixture
  loads and displays in the Signature accordion.
- Band T not rendered (out of scope for WO2; T rows absent from single-basin fixture by design).

**2026-07-02 (Step 0 skeleton)**

- **`sandbox_v2.html` / `/sandbox/lookup2`** — template name and route established. Not
  linked from anywhere (same pattern as `cliopatria.html`). No nav cross-links to existing
  pages. Revisit linking once the page is meaningfully functional.
- **Level fixed L06** — no level toggle on the new page (unlike the existing Lookup). Basin
  resolution for areal scopes operates at L06 throughout. This may be revisited if a use case
  for L08 areal signatures emerges; for now L06 is locked.
- **5-scope dropdown order** — Single basin → Buffer → Basin ring → Polity → Draw a study area.
  Order reflects build sequence (simpler/point-rooted first). Locked unless user research says otherwise.
- **`tests/surface/`** — path for all surface UI structural tests. Uses FastAPI TestClient +
  BeautifulSoup (same pattern as app suite). Browser-automation tests (Playwright) deferred;
  Karl evaluating. Surface tests run as part of the full `python -m pytest tests/` suite.
- **`pages.py` TemplateResponse signature** — updated to new Starlette API
  (`TemplateResponse(request, name)`) via `_render()` helper; removes deprecation warning.

**2026-06-30 (phase open)**

- **New page, not in-place.** The new sandbox is a fresh template; `sandbox.html` is untouched
  and its tests stay green. Rationale: the working Lookup is public and in use; a new page can
  call the areal engine freely without destabilizing it, and keeps the proven Lookup as a
  reference.
- **`/area` first cut is polity-by-name+year only** (WO22). Other input types deferred to
  surface-driven need.
- **Surface owns interpretation.** Summarization, significance filtering, verdict-gates, and
  rendering are surface concerns (engine resolves-and-serves, Areas 2026-06-27). The histogram
  *object* is the engine's; the histogram *visualization* is the surface's.

---

## Session log pointer

Session-by-session detail lives in `logs/session_log_YYYYMMDD.md`. Findings for this phase:
`docs/edop/surface/surface_findings.md` (create at first finding; coded SF.n or per the
AF.WO<n>.<m> convention as preferred).
