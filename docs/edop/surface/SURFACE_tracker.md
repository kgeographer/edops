# SURFACE — Phase tracker

**This is the living source of truth** for the Surface phase: current state, roadmap, and
locked decisions. If any other Surface document disagrees with this one about *where things
stand*, this one wins.

- **Location:** `docs/edop/surface/SURFACE_tracker.md`
- **Last updated:** 2026-07-04 (WO7 complete; 313/313 tests)
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

**Next: WO8** — TBD. Discuss with Opus. Candidates: ring scope live; map boundary paint;
HYDE dense-epoch UI compensation (F7.5).

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
