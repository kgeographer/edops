# WO — Exemplar payload capture (Surface phase)

**Branch:** `surface`
**Phase:** Surface · **Sub-phase:** page design (pre-build)
**Type:** capture/inspection, not an engine change. No new engine logic; call existing entry
points and persist their output for joint review.

## Goal

Generate and persist real payload dumps for each query scope, lean and `&detail`, so the new
sandbox page is designed against actual engine output rather than a described schema. The
dumps are the ground truth we read the UI decisions against — which `method` leaf-renderers
are really needed, where histograms actually appear, how Band T rows are shaped, where the
two temporal axes land, and what fields the UI will want that no row carries.

## Framing decision (settled this session)

**The sandbox consumes `&detail`; lean is captured for contract-comparison, not because the
page renders from it.** The page's purpose is to surface distributional richness (coherence
badges, histograms, the envelope/value marginals) — all of which live in `detail`. Lean is
the API caller's economy option and the thing the "show API call" / build-a-call features must
represent. So we capture both, but detail is the working payload and lean is the reference.
Capturing both side by side confirms the lean/detail line is drawn in the right place by
showing exactly what lean drops.

## Scenarios to capture

Five scopes, two payload shapes. Chosen to span the shapes and the axes that stress the
renderer. Use known fixtures where possible.

| # | Scope | Entry point | Fixture | Why this one |
|---|---|---|---|---|
| 1 | Single basin | `single_basin_signature` | Timbuktu, L06 | Degenerate n=1 case — the baseline every other shape degenerates toward. Confirms envelope→line, histogram→point, s/u divergence present. |
| 2 | Buffer | `areal_signature` | Timbuktu, 100km, L06 | First true multi-unit `{rows[]}`, small n. Coherence/spread at modest cell counts. |
| 3 | Polity | `areal_signature_polygon` (or `/api/area`) | Northern Song, year=1000, L06, **bands incl. T**, `from_year=1000 to_year=1100` | Large-n `{rows[]}` with Band T. Stresses everything: spread rows, histograms across all three substrates, both temporal axes, marginal_exposure. |
| 4 | Basin ring | `basin_ring_signature` | Timbuktu (or Kaifeng), L06 | The `{center, ring[]}` exception — the one shape that doesn't share the renderer. |
| 5 | Arbitrary polygon | `areal_signature_polygon` | a drawn rectangle over any land area | Confirms it routes identically to polity minus the name/period lookup. |

For **each** scenario capture **both** lean and `&detail=true`.
Scenario 3 (polity) is the priority — if time is short, do 3 first and completely.

## Persistence

- Write to `docs/edop/surface/exemplars/` (create dir).
- Naming: `NN_scope_lean.json` and `NN_scope_detail.json`
  (e.g. `03_polity_nsong_detail.json`).
- Pretty-printed JSON (indent=2), one file per payload.
- Add a short `exemplars/README.md`: for each file, the exact call made (entry point +
  arguments) so the dump is reproducible and self-documenting.

## Inspection checklist (record findings in `exemplars/README.md` per scenario)

For each scenario, note:

1. **Methods present** — which `method` values appear and their counts. This tells us how many
   leaf-renderer types the Signature tab must actually implement (we sketched eight; the
   payloads show which fire and how often).
2. **Histogram presence** — where `detail['distribution']` appears (expected: B1, B5, Band T)
   and where it's absent. Record one histogram object's actual `unit_type`, bin count, and
   temporal-stamp fields (`resolver_year`, `band_t_from`, `band_t_to`).
3. **Band T shape** — confirm Band T rows are one-row-per-year-per-variable (HYDE/LMR) and
   per-event (eVolv2k). Note whether collating them into a per-year series (for the envelope
   chart) is mechanically clean or fights the structure.
4. **Temporal axes location** — where the two axes actually live in the payload (top-level?
   per-row? per-histogram? all?). This drives whether the envelope-cursor / map-slider /
   resolver-year distinction is readable from fields or must be reconstructed client-side.
5. **Lean vs detail delta** — for the same scenario, what exactly does lean drop that detail
   carries? Confirms the split is drawn correctly (and that the sandbox is right to consume
   detail).
6. **Missing fields** — anything the UI design (component inventory) wants that no row carries.
   This is the real yield: each gap becomes either an engine addition or a surface-computed
   value. List them explicitly.

## Out of scope

- No engine changes. If a scenario reveals a missing field, record it — do not fix it here.
- No endpoint wiring. Scenarios 1, 2, 4 call the engine callables directly (they're not yet
  HTTP-wired); that's fine — we want the payloads, not the routes. (HTTP wiring is a separate
  prerequisite WO.)
- No UI work.

## Return

- The populated `docs/edop/surface/exemplars/` directory (10 JSON files: 5 scopes × lean/detail,
  or fewer if a scope legitimately has no lean/detail distinction — note if so).
- `exemplars/README.md` with the reproducible calls and the six-point inspection findings per
  scenario.
- A one-paragraph summary of the **missing-fields** findings across all scenarios — the list
  that will drive the next round of engine-vs-surface decisions.
  