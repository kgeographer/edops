# SURFACE — Phase tracker

**This is the living source of truth** for the Surface phase: current state, roadmap, and
locked decisions. If any other Surface document disagrees with this one about *where things
stand*, this one wins.

- **Location:** `docs/edop/surface/SURFACE_tracker.md`
- **Last updated:** 2026-07-03 (Playwright set up; 263/263 tests)
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
live server fixture in `tests/surface/conftest.py`. Total: 263/263 tests pass.

**Next: WO3 = Step 2** (leaf widget polish: histogram, coherence badge, range-bar, mixture bar).

---

## Roadmap (seed)

| Item | What | Status |
|---|---|---|
| Sandbox capability-gap analysis | Inventory: what the engine now offers that no UI exposes; what `sandbox.html` currently exposes; the delta; and whether the existing markup can absorb the new elements or forces a new page. | **complete** — see SF.1 |
| WO1 — exemplar payload inspection | Capture + inspect real payload dumps for all five query scopes (single-basin, buffer, polity+Band T, basin-ring, polygon). Ground truth for page design decisions. | **complete** — F1.1–F1.13; TODOs fixed |
| New sandbox page — Step 0 skeleton | `sandbox_v2.html` at `/sandbox/lookup2`; scope gate + Band T toggle; Level L06 fixed; 5 scopes; 4 examples; 40 tests. | **complete** |
| New sandbox page — Step 1 rows-renderer | Atomic rows-renderer against single-basin exemplar fixture; all 6 method leaves render something before any are made nice. | **complete — WO2** |
| Playwright setup | Browser-automation test harness for JS state tests (scope gate, T toggle, renderer output). Karl evaluated and confirmed. | **complete** |
| New sandbox page — Step 2 leaf widgets | Polish each method leaf one at a time: histogram widget, coherence badge, range-bar, mixture bar. One review gate per leaf. | **next — WO3** |
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
