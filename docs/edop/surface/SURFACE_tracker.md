# SURFACE — Phase tracker

**This is the living source of truth** for the Surface phase: current state, roadmap, and
locked decisions. If any other Surface document disagrees with this one about *where things
stand*, this one wins.

- **Location:** `docs/edop/surface/SURFACE_tracker.md`
- **Last updated:** 2026-07-02 (WO1 complete; all TODOs fixed; 80/80 engine tests)
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

**Next: new sandbox page spec** (Karl working with Opus; fresh session).

---

## Roadmap (seed)

| Item | What | Status |
|---|---|---|
| Sandbox capability-gap analysis | Inventory: what the engine now offers that no UI exposes; what `sandbox.html` currently exposes; the delta; and whether the existing markup can absorb the new elements or forces a new page. | **complete** — see SF.1 |
| WO1 — exemplar payload inspection | Capture + inspect real payload dumps for all five query scopes (single-basin, buffer, polity+Band T, basin-ring, polygon). Ground truth for page design decisions. | **complete** — F1.1–F1.13; TODOs fixed |
| New sandbox page spec | Spec for a fresh page exercising the engine end to end: point-rooted queries (buffer, single-basin) AND polity path. Lean + `&detail`. Both temporal axes as distinct controls. Histogram widget. Polity boundary overlay on map. Depends on WO1 complete. | **next** |
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
