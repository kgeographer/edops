# DEMO — Phase tracker

**This is the living source of truth** for the Demo phase: current state, roadmap, and
locked decisions. If any other Demo document disagrees with this one about *where things
stand*, this one wins.

- **Location:** `docs/edop/demo/DEMO_tracker.md`
- **Last updated:** 2026-07-12 (tweaks0712 merged)
- **Maintained:** updated by CC at session end and whenever a decision is locked; read at the
  start of each step and each phase gate.
- **Rule:** when a decision is locked or a gap is resolved, remove the corresponding
  forward-looking note in the same edit — never leave a resolved item as an open question
  elsewhere in the file.

---

## What DEMO is

Where SURFACE asked *does the instrument do X*, DEMO asks *what does the instrument say to a
person who has never seen it*. The work is curation, framing, and legibility — not
capability-building. Every prioritization call resolves against one question: **does this
help the Braga audience (21 Sep 2026)?**

Three tracks, sequenced:

1. **Track 1 — Money shots**: curation + the features they need. Find the two or three polity
   cases that land (a polity the audience recognises + an environmental gradient the paint makes
   obvious + a historical fact the gradient illuminates). The within-polity-variance ranking
   notebook is the curation mechanic; the continuous time slider and L06↔L08 compare are the
   two demo-enabling features that are also hero shots in themselves.

2. **Track 2 — Features**: demo-driven exposure of built-but-unexposed pieces. Analysis tab,
   more variables, correspondence surfacing — expose only what a demo or slide actually uses.

3. **Track 3 — Legibility**: after feature-freeze (~early September), make the frozen surface
   explain itself to a stranger at a demo table.

Full rationale and sequencing logic: `docs/edop/demo/DEMO_workplan.md`.

## Relationship to Surface

Surface is **frozen reference** (`SURFACE_tracker.md`, closed 2026-07-10). The instrument's
full range — scope, scale, variables, state management — is built. Read Surface for settled
UI/engine background. Do not extend it. The **deferred items register is shared** and
cross-phase: consult at every step resumption, add rows there
(`docs/design/areas/deferred_items_register.md`).

---

## You are here

Phase opened 2026-07-10. Branch: `demo` (cut fresh from main after Surface merge).
**575 tests pass, 52 skipped.**

Active page: `sandbox_v3.html` at `/sandbox/lookup3` — two-tab surface (Settlements +
Polities), all four scopes operable, BasinATLAS/LMR/HYDE choropleth, L06/L08 level toggle.

**WO1 + WO1a complete.** Findings in `docs/edop/demo/wo1_findings.md` and
`docs/edop/demo/wo1a_findings.md`; notebook in
`notebooks/edop/demo/wo1_within_polity_variance.ipynb`; merged to `demo` 2026-07-11.

**WO2 complete and merged** — slice slider + VCR, Band T inputs hidden on Polities tab,
coverage guards (BCE + below-floor), HYDE nearest-year fallback (Band T always present in
signature), polity examples added, Polities tab now default. Findings in
`docs/edop/demo/wo2_findings.md`.

**tweaks0712 merged (2026-07-12)** — map cartography + UX polish:
- AWMC historical terrain basemap (replaces OSM+hillshade)
- Global HydroRIVERS PMTiles base layer (`app/static/sandbox/rivers.pmtiles`; gitignored); layer control toggle
- Basin fill-opacity → 0 (choropleth shows through; event targets preserved)
- White casing on all basin outline layers; color → charcoal `#3d3835` (avoids river-blue conflict)
- 4 placed settlement examples with Band T years (Timbuktu, Rome, Kaifeng, Santa Fe)
- Reset clears sig panel, re-disables tabs, returns to Map tab, resets example select
- Polity slice year overlay (top-left map corner, large `#993333` text, updates on every slice step)

---

## Roadmap (seed)

| Item | What | Status |
|---|---|---|
| Within-polity-variance ranking notebook (WO1 + WO1a) | Rank polities by spread; trajectory + size-confound validation; membership spot-check; hero-shot shortlist confirmed | **complete** |
| Continuous time slider + signature fixes (WO2) | Slider + VCR, Band T inputs hidden, coverage guards, HYDE nearest-year fallback, polity examples | **complete — merged** |
| Money shot curation | Identify 2–3 polity/variable/history triples for demo; requires notebook output | pending |
| L06 ↔ L08 scale compare (MAUP demo) | Side-by-side view at two scales; Track 1 feature after hero shots confirmed | pending |
| Analysis tab port/review | Content exists in v1; port/expand only if it carries a demo point | pending Track-2 pull |
| Correspondence surfacing | D-PLACE / Workbench Societies screen; decision: port vs. demo-as-is | pending |
| Track 3 legibility pass | Basin-ring explanation, map legibility, minimal user guide — over frozen surface only | post feature-freeze |
| Feature freeze / UX review | Hard calendar checkpoint; surface declared demo-frozen | ~early September 2026 |

---

## Known constraints (carried in)

- **`sandbox.html` (Lookup) and `explorer.html` (Explorer) are public, all-green, untouched.**
  Do not edit them. DEMO work is additive on `sandbox_v3.html`.
- **Two temporal axes: independent on Settlements, slice-determined on Polities.**
  On the Settlements tab a point has no span of its own; `resolver_year` and Band T span are
  genuinely independent user choices. On the Polities tab, `resolver_year` and Band T span are
  the same fact — delivered by the active slice. Band T inputs on the Polities tab are read-only
  plumbing that mirrors the slice; they are not exposed to the user. (Scoping correction locked
  2026-07-11; original "do not collapse" principle holds for the Settlements tab.)
- **Expose only what a demo or slide uses** — the discipline is demand-driven, not
  "the control is sitting there empty."
- **Track 3 legibility is last** — prerequisite is feature-freeze. Do not write "here's what
  you're looking at" for controls still in flux.

---

## Milestone

- **Braga (2026-09-20)** — Spatial Humanities 2026 conference, UNED; small presentation slot
  + possible demo table. ~11 weeks from phase open. The organizing question for every
  prioritization call.

---

## Locked decisions

Append-only; dated. Settled unless explicitly revisited here.

**2026-07-11**

- **Two-axis scoping: independent on Settlements, slice-determined on Polities** — the
  "two axes remain independent" standing constraint applies to the Settlements tab only. On
  the Polities tab, `resolver_year` and the Band T span are the same fact (delivered by the
  active Cliopatria slice); they cannot be set independently without mispairing a border with
  a value it did not hold. Band T inputs on the Polities tab are hidden — read-only plumbing
  that `applySlice()` writes and the API reads; the user never sees them.

- **Band T tracks the active polity slice** — `applySlice()` writes `s.fromyear`/`s.toyear`
  to the Band T inputs and repaints the choropleth on every slice change. Aggregating over
  the full polity lifespan discards exactly the temporal signal the LMR layer is meant to
  show. The two-axis independence principle is preserved: users can still manually override
  Band T after slice selection.

**2026-07-10 (phase open)**

- **WO numbering restarts at WO1 for DEMO** — next work order is WO1.
- **`DEMO_workplan.md` is the seed document** — carries the rationale, track structure, and
  sequencing logic. This tracker is the live state; workplan is the rationale record.
- **Correspondence: demo workbench as-is for Braga** — the Societies screen is substantially
  built and live; porting into sandbox_v3 is real work with no confirmed Braga payoff.
  Decision: demo the workbench as a separate live thing alongside for the conference.
  Full correspondence tab is post-Braga / CDOP-phase.

---

## Session log pointer

Session-by-session detail lives in `logs/session_log_YYYYMMDD.md`.
Findings for this phase: `docs/edop/demo/` (per-WO findings files as work orders proceed).
