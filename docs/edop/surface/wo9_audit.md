# WO9 (audit) — Single-basin true state + ring-weight register reconciliation

**Type:** Investigation. No feature build. Read-only except **one proposed doc diff**
(deferred register), which is presented for Karl's review, not written.

**Why:** Two inconsistencies surfaced when Surface resumed. We resolve them before the map
sequence continues — unresolved, they are landmines for future us. Establish ground truth by
inspection and propose the register fix.

Lead each Part with the **yes/no answers first**; evidence, file paths, and line citations
after. Do not assume filenames — verify them.

---

## Part A — What is single-basin's actual state?

The continuity prompt claimed single-basin is "live off the DB, fully proven." `CLAUDE.md`
(entry point list) and `SURFACE_tracker.md` say `single_basin_signature` is **not HTTP-wired**
and no wiring WO exists. Both can't be true. Karl's read: the "Load an example" option delivers
a signature, but probably from a fixture, and no Band T ever arrives. Confirm or refute.

Answer each explicitly:

**A1 — Fixture or DB?** When the user selects the single-basin **"Load an example"** option in
`app/templates/sandbox_v2.html` and runs the signature, does the delivered signature come from
a **live DB call** (an `/api/…` route hitting Postgres) or from a **static fixture**
(`/dev/exemplars/…`)?
- Trace the Sig-button handler and the single-basin URL/source builder. WO6 noted non-live
  scopes "fall through to fixture" — confirm whether single-basin is one of them.
- Report the exact source: route path, or fixture filename.

**A2 — Does the route accept it?** Does `GET /api/areas` accept `type=single_basin`? Read the
type dispatch in `app/api/routes.py`. If it 422s or is unhandled, say so.

**A3 — Reachable at all?** Is the engine `single_basin_signature` entry point reachable through
**any** HTTP route today? Yes/no + which route, or "none."

**A4 — Band T.** Does Band T arrive for single-basin in **any** path? Check three layers and
report each separately:
1. Does the single-basin exemplar fixture in `output/edop/surface/exemplars/` contain Band T
   rows? (WO2 note said "T rows absent from single-basin fixture by design" — confirm still true.)
2. Does the engine `single_basin_signature` entry point produce or accept Band T at all?
3. Is the Band T toggle enabled or gated for the single-basin scope on the page?

**Part A deliverable:** a short "single-basin true state" paragraph — what works, what is
fixture-only, what is absent — written so it can replace the overclaim in the tracker. If
single-basin is a fixture-only example with no live route and no Band T, state exactly that.

---

## Part B — Is the ring weight policy settled? Reconcile the register.

`resolve_basin_ring` + `basin_ring_signature` were promoted to the engine on 2026-07-01
(77/77 tests). The deferred register still carries an **open** row *"Basin-ring weight policy"*
under the heading *"Surfaces before basin-ring resolver (WO17)."* Determine whether that row is
stale. Karl believes the weight was settled.

**B1 — What ships?** What weighting does the **shipped** ring resolver actually use? Read
`resolve_basin_ring` / `basin_ring_signature` in `scripts/edop/areas/engine.py`. Report the
scheme (equal / area-proportional / border-length / other) with line citations.

**B2 — Decision record?** Is there a record of that choice being made? Check: `AREAS_tracker.md`
locked decisions; any `wo16_*` / `wo17_*` findings; the session log around 2026-07-01. Point to
it (or confirm none exists).

**B3 — Verdict.**
- If the code implements a definite scheme **and** a decision record exists → the register row
  is **stale**. Propose the exact edit: move the row into the register's **"Closed"** section
  with date + one-line "how," and remove it from the open *"before WO17"* section.
  **Present the diff; do not write it.**
- If the resolver shipped with a provisional/placeholder weight and **no** decision was
  recorded → the row stays **open**. Say so plainly, and flag that the resolver carries an
  unratified weight (a real gap, not just a doc artifact).

**Part B deliverable:** the weight scheme in code, the decision record (or its absence), the
verdict, and — if stale — the proposed register diff for Karl's sign-off.

---

## Constraints

- Read-only except the single proposed register diff, presented for review.
- No test changes; no feature code.
- Yes/no answers first in each Part; evidence and citations after.
- Findings → `docs/edop/surface/wo9_audit_findings.md` (or append to the session log — your
  call; tell us which). Rename to match the final WO number if it changes (see below).

## Numbering note (for Karl)

This takes the WO9 slot as an audit; step b (single-basin on the map) then becomes WO10. If you
prefer to keep WO9 = step b, we rename this to WO9-audit / pre-b. Your call before it goes to CC.