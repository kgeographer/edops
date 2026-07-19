# WO1 — CDOP pilot page + lens-based environmental similarity

**Phase:** CDOP1 (opened 2026-07-18; DEMO closed)
**Branch:** `cdop01` (cut from `main`)
**Goal:** Stand up `cdop_pilot.html` as the CDOP component's own surface, and replace the
legacy PCA-composite environmental similarity on WH Cities with the LENS_REGISTRY instrument
at L08.

This is a goal-setting document with provisos, not a specification. CC discovers
implementation particulars; Karl reviews every write.

Rationale: `docs/cdop/CDOP_workplan_v1.md`. Feasibility evidence: `wo_l08_findings.md`.

---

## Why

The Workbench's `Similar (env)` uses a PCA-composite distance predating the WO4c–4e research.
It returns Jerusalem (Arid/Desert) and Acre (Mediterranean/Dry Temperate) among the top-5
neighbours of Mombasa (Extremely hot and moist) — WO4d's dilution finding displayed live, with
the contradicting glosses printed alongside. This is the reason the Workbench link is disabled
on the EDOPS home page.

The correspondence material in the Workbench (Societies, WH Cities semantic similarity) is CDOP
work filed under EDOPS by accident of chronology. This WO begins the split.

---

## Scope

### Part A — Phase scaffolding

New phase folders, aptly named, following existing conventions (`docs/cdop/`,
`docs/cdop/cdop1/` or equivalent; notebook and output paths to match). CDOP1 tracker created
and made authoritative for CDOP state. WO numbering restarts at WO1.

Proviso: DEMO trackers become frozen reference. Each tracker's "this one wins" rule needs a
scope qualifier so DEMO and CDOP1 do not both claim global authority.

### Part B — `cdop_pilot.html`

New template, initially cloned from the Workbench. Tabs retained: **Societies, Ecoregions,
WH Cities**. Tabs dropped: **Main, Basins, WH Sites**.

Provisos:

- The existing Workbench page and route stay live and untouched — rollback path, and the
  retire/redirect decision is deferred until the new page is judged good. Note it as pending;
  do not let the old page linger by default.
- Ecoregions is retained because its disposition was never decided, not because it was
  affirmatively kept. The open item underneath it — BasinATLAS ecoregion IDs carried in the
  signature and unused — is not in scope here.
- Basins is dropped as EDOPS-side classification, but it passed the inverted-query test and the
  clone makes it recoverable. Record that, so it is not rediscovered as a new idea later.
- No new tabs, no new datasets, no UI restructuring in this WO. The redesign is subtractive.

### Part C — L08 lens index

Build the LENS_REGISTRY similarity index at L08 alongside the existing L06 index, and serve it.

Established by `wo_l08_findings.md`: build is viable (~4 s, ~17 MB at startup; ~5–6 s and
~18 MB for both indices), per-query 2.4–4.5 ms, sources are
`public.v_basin08_persist_rev2` (monthly arrays) and `public.basin08` (scalars). NaN profile
719 basins (0.4%), handled by existing masking.

Provisos:

- Level becomes a parameter of index selection, not a fork in the distance logic. The registry
  is the single source of truth; adding a level must not require new distance code.
- Startup cost is additive. If eager-loading both indices is objectionable, lazy-load L08 —
  but decide, don't discover.
- FK path is `gaz.wh_cities.basin_id → basin08.id → basin08.hybas_id`. `basin_id` is the
  sequential id, **not** `hybas_id`.
- **Thresholds are out of scope at L08.** L06 radii do not transfer (counts inflate ~10×;
  `climate.temp/loose` returns 46% of all L08 basins). Recalibration is not required by this
  use case and is not part of this WO.

### Part D — Wire `#whc-similar-env-btn`

The dropdown offers lens choices from the registry in place of the legacy A/B/C/D band
breakdown (which has been greyed out as future work since the Workbench was built). Lens
groups, not bands: bands are the signature's organisational scheme, lenses are physical
questions.

Provisos:

- **Mode is topN=5**, corpus-scoped. Established in `wo_l08_findings.md` Part D: threshold mode
  breaks on this corpus (strict returns zero peers for 36–39% of cities; loose temp returns a
  median 148 of 254). The existing `whc-similar` query already uses `limit=5` — no change
  needed. topN=5 is a defensible choice, not a derived constant; it approximates the natural
  discrimination scale for precip and phase but not temp (moderate median 30). Do not present
  it as empirically derived.
- **Label honestly and corpus-relatively**: "5 most similar cities in this collection." Scope is
  the 258-city corpus, not a global similarity neighbourhood — this is what distinguishes it
  from the sandbox Similarity tab, which does make global claims.
- 254 of 258 cities have an L08 basin; 4 coastal/island cities do not. Show the count; do not
  silently serve 254 as though it were 258.
- If a Composite option is retained, relabel it honestly — holistic and thermally weighted, not
  neutral.
- `Similar (semantic)` is untouched in this WO, but the same corpus-scoped label applies to it
  verbatim and costs nothing. Apply it. Semantic calibration remains an open question and is
  explicitly not in scope.

---

## Accept gate

One gate, on output rather than wiring:

**Mombasa, under a climate lens, returns no Arid/Desert or Mediterranean/Dry Temperate
neighbours in its top 5.**

If the dropdown populates correctly and Jerusalem is still in the list, the WO has failed.
Verify in the notebook before wiring the UI.

Supporting checks: page loads with the three retained tabs and no dead controls from the
dropped ones; existing Workbench page still functions; test suite green (zero-tolerance rule
applies).

---

## Out of scope

- L08 threshold recalibration
- Semantic-similarity calibration
- Ecoregion IDs in the signature
- Retiring or redirecting the old Workbench page
- Any new tab, dataset, or UI restructuring
- Terrain lens group (open; decide after this WO)

---

## Deliverables

- `cdop_pilot.html` + route
- L08 lens index + serving path
- CDOP1 tracker, phase folders
- `wo1_findings.md`
- Deferred/open items recorded per the register's discipline — actually-met items only, with
  triggers; not predictions

