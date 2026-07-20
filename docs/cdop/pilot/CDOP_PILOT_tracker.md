# CDOP Pilot — Phase tracker

**This is the living source of truth** for the CDOP Pilot phase: current state, roadmap,
and locked decisions. If any other CDOP document disagrees with this one about *where things
stand*, this one wins — for CDOP Pilot scope only.

- **Location:** `docs/cdop/pilot/CDOP_PILOT_tracker.md`
- **Last updated:** 2026-07-20 (WO3 Parts A+B complete; similarity in stasis pending approach reconsideration)
- **Rule:** when a decision is locked or a gap is resolved, remove the corresponding
  forward-walking note in the same edit — never leave a resolved item as an open question
  elsewhere in the file.

---

## What CDOP Pilot is

CDOP (Cultural Dimensions of Place) is the companion component to EDOP within the
**Computing Place** research platform. EDOP delivers environmental signatures; CDOP delivers
cultural/comparative material. They are two components of one frame — the frame belongs to
Computing Place, not to either component.

The pilot stands up `cdop_pilot.html` as CDOP's own surface, separating it from the
Workbench (which was CDOP work filed under EDOPS by chronology). The first increment
replaces the broken PCA-composite environmental similarity on WH Cities with the
LENS_REGISTRY instrument at L08.

**Why the old similarity is broken:** the PCA composite returns Jerusalem (Arid/Desert) and
Acre (Mediterranean) among the top-5 neighbours of Mombasa (Extremely hot and moist). This
is the WO4d dilution finding displayed live, with the contradicting glosses printed alongside.
The Workbench link is disabled on the EDOPS home page for this reason.

Full rationale: `docs/cdop/CDOP_workplan_v1.md`. Feasibility evidence: `docs/edop/demo/wo_l08_findings.md`.

## Relationship to DEMO

DEMO is **frozen reference** (`docs/edop/demo/DEMO_tracker.md`, closed 2026-07-18).
Do not extend it. The **deferred items register is shared** and cross-phase:
consult at every step resumption, add rows there (`docs/design/areas/deferred_items_register.md`).

---

## You are here

Phase opened 2026-07-18. Integration branch: `cdop` (cut from `main` after DEMO merge).
WO branches cut from `cdop`, merged back on accept.
**584 tests pass, 50 skipped.**

**Similarity in stasis.** WO3 Parts A+B complete and merged to `cdop_pilot`. Parts C+D
(scalar hygiene, glyph) suspended. The temperature lens maps are producing geographically
wrong results at moderate threshold; the overall similarity approach needs reconsideration
before further WO3 work. Problem statement drafted for Opus. See WO3 section.

---

## Roadmap

| Step | Branch | Status | Notes |
|---|---|---|---|
| WO1 — CDOP pilot page + L08 lens similarity | `cdop_pilot` | **blocked** | Plumbing complete; accept gate partial fail; blocked on WO3 |
| WO2 — Rainfall modality investigation | `cdop_wo2` | **complete** | Bimodal characterization; continuous (a1,b1,a2,b2) representation validated |
| WO2a — Continuous harmonic representation | `cdop_wo2` | **complete** | Part B pass; Part C clean on own-top-5 evidence; phase lens retired |
| WO3 — Continuous precip lens + retire phase lens | `cdop_wo3` | **stasis** | A+B complete (merged); C+D suspended; similarity approach under reconsideration |

---

## WO1 — CDOP pilot page + L08 lens similarity

**Work order:** `docs/cdop/pilot/wo1_cdop-pilot.md`
**Branch:** `cdop_pilot` (cut from `cdop`)

### Parts

**Part A — Phase scaffolding:** ✓ Phase folders exist (`docs/cdop/`, `notebooks/cdop/`,
`scripts/cdop/`, `output/cdop/`, `sql/cdop/`). This tracker created. DEMO_tracker.md header
scope-qualified.

**Part B — `cdop_pilot.html`:** in progress
- Cloned from `workbench.html`
- Tabs retained: Societies (active default), Ecoregions, WH Cities
- Tabs dropped: Main, Basins, WH Sites
- Route added: `GET /cdop` → `cdop_pilot.html`
- Old `/workbench` route and page untouched

**Part C — L08 lens index:** in progress
- `load_similarity_index(conn, level)` parameterized; level selects view + scalars table
- `_INDEX` dict keyed by level holds both L06 and L08 state at runtime
- Legacy L06 globals (`_HYBAS_IDS`, `_LENS_STATE`) kept in sync — existing callers unaffected
- `find_similar()` gains `level` (default 6) and `filter_hybas_ids` parameters
- `main.py` lifespan loads L06 then L08 at startup (~4 s, ~17 MB for L08)
- Level tables: L06 → `v_basin06_persist_rev2` + `basin06`; L08 → `v_basin08_persist_rev2` + `basin08`

**Part D — Wire `#whc-similar-env-btn`:** in progress
- New route `GET /api/whc-similar-env-lens?city_id&lens_id&limit=5`
- Uses L08 index, `mode='topn'`, corpus-restricted via `filter_hybas_ids`
- FK path: `gaz.wh_cities.basin_id → basin08.id → basin08.hybas_id`
- Dropdown items: Seasonal phase / Precipitation regime / Temperature regime (replaces A/B/C/D bands)
- Heading: "5 most similar cities in this collection" (corpus-relative; honest scope)
- Semantic similarity heading updated to same corpus-relative label
- 254/258 count shown in panel subhead

### Accept gate: partially met

Checked 2026-07-18. Results by lens:

- **Temperature regime — PASS**: Trinidad (Cuba), Camagüey (Cuba), Mompox (Colombia),
  Galle (Sri Lanka), Santa Ana de Coro (Venezuela). All tropical. ✓
- **Seasonal phase — FAIL**: Split (Croatia), Ibiza (Spain), Vatican City appear in top 5.
  Three of five are Mediterranean. ✗
- **Precipitation regime — FAIL**: Augsburg, Salzburg, Kotor, Tinn dominate. Clearly wrong. ✗

Root-cause hypothesis: Mombasa has bimodal rainfall (Apr–May + Oct–Nov peaks). Unimodal
circular statistics (`pre_concentration`, `seas_phase_offset`) can't represent bimodal
patterns — the two peaks nearly cancel, making Mombasa look like a city with even year-round
rainfall. European cities with distributed rainfall score as nearest neighbours.

Jerusalem is absent from all three lenses — the specific PCA failure is fixed. The bimodal
limitation is a different problem. See `wo1_findings.md` for full analysis.

**Decision deferred to Opus review session.**

### Open / pending

- [ ] Similarity approach reconsideration — problem statement drafted; Opus review pending
- [x] Test suite green (584 pass, 50 skipped, 0 failed — 2026-07-20)
- [ ] Merge `cdop_pilot → cdop` on WO1 accept gate met

---

## WO3 — Continuous precip lens + retire phase lens + scalar hygiene

**Work order:** `docs/cdop/pilot/wo3_retire-phase.md`
**Branch:** `cdop_wo3` (merged to `cdop_pilot` 2026-07-20)

### Parts A+B — Complete

**Part A** — `climate.precip` feature set replaced: `(pre_mm_syr, pre_concentration)` →
`(log_pre_mm_syr, a1, b1, a2, b2)`. Continuous harmonic form; no threshold in feature
construction; log total keeps magnitude independent of shape. `_compute_derived()` rewritten.
Provisional L06 thresholds set (strict: 0.25, moderate: 0.60, loose: 1.20); CDF
recalibration deferred.

**Part B** — `climate.phase` retired from `LENS_REGISTRY` (status → `"retired"`).
Deprecated `/api/seasonality/similar` route removed. Dropdown removed from `cdop_pilot.html`.
Phase blurb block removed from `sandbox_v3.html`. All defaults updated to `climate.precip`.

### Parts C+D — Suspended

Scalar hygiene (`pre_peak_month`, `pre_concentration` rename, narrative fix) and the
monthly-profile glyph are suspended. Reason: similarity approach is under reconsideration
before further investment.

### Problems discovered during map review (2026-07-20)

Two distinct problems with the **temperature lens** found during visual review:

**1. `climate.temp` Mahalanobis distortion.** At moderate threshold (0.75), Tbilisi returns
852 basins including coastal Norway — wrong, as coastal Scandinavian basins have amplitude
8–12 °C vs Tbilisi's 21.7 °C. The global covariance matrix is dominated by the
mean-temperature/latitude correlation, tilting the Mahalanobis ellipse so that amplitude
differences become secondary. The strict threshold (0.25) produces geographically coherent
results. The moderate-to-strict jump (3×) is too large and crosses a distortion boundary.
`climate.temp` thresholds were never CDF-calibrated; carried over from WO7 without review.

**2. L06 container-constitutes-the-place.** Tbilisi city mean annual temperature ~13.8 °C;
L06 basin reports 5.3 °C. The 8.5 °C gap is because the basin extends into the Greater
Caucasus at 3,000–5,000 m. The similarity query answers "what is similar to the upper Kura
headwaters?" not "what is similar to Tbilisi?" This is inherent to L06 for mountain-valley
cities; L08 would give a smaller, more representative basin. The sandbox similarity tab is
hardwired to L06 (two lines) regardless of the level toggle — an oversight noted but not yet
fixed.

Problem statement for Opus drafted (session_log_20260720.md).

---

## Locked decisions

| Decision | Rationale |
|---|---|
| topN=5 for WH Cities | Threshold mode returns zero peers for 36–39% of cities at strict; loose temp returns median 148/254. topN=5 approximates empirical moderate scale for precip/phase. From `wo_l08_findings.md` Part D. |
| L06 thresholds not used at L08 | Counts inflate ~10×; `climate.temp/loose` returns 46% of all L08 basins. Recalibration deferred and not needed for this use case. |
| Corpus-relative label | "5 most similar cities in this collection" — scope is the 258-city corpus, not a global neighbourhood. Distinguishes from sandbox Similarity tab. |
| Old Workbench stays live | Rollback path; retire/redirect decision deferred. |
| Basins tab dropped but recoverable | Passed the inverted-query test; dropped as EDOP-side classification. Clone makes it recoverable. Not rediscovered as a new idea. |
| `climate.precip` features: continuous (a1,b1,a2,b2) | Identities verified to machine epsilon; Mombasa top-5 all East African with no modality filter; Abidjan recovered (R_dbl=0.246 < 0.30 threshold, continuous correct). No threshold inside feature construction. `pre_concentration` and `R_dbl` are redundant once components included — do not add. `same_modality` dropped. From WO2a Part B. |
| `climate.phase` lens retired | The lens was never one question: it bundled how-many-wet-seasons (now in precip lens), hemisphere-blind phase relation, and hemisphere-aware seasonal timing. Questions 2 and 3 cannot share a lens — each fix breaks the other's repair. Undefined across the equatorial belt where D-PLACE work is concentrated. Retired, not redesigned. Phase fork recorded in deferred register. From WO3 spec. |
| Phase fork recorded, not planned | Hemisphere-blind relation and hemisphere-aware timing are two distinct lenses. Neither is built until a use case asks for it. Analysis is done; do not re-derive. From `wo3_retire-phase.md` deferred register. |

---

## Deferred / out of scope

- Similarity approach reconsideration — overall instrument validity; Mahalanobis vs Euclidean
  for climate.temp; L06 container problem for mountain cities; threshold CDF calibration for
  all active lenses; wiring level toggle into sandbox similarity tab (2-line fix, held)
- WO3 Parts C+D — scalar hygiene + monthly profile glyph (suspended pending approach decision)
- L08 threshold recalibration
- Semantic-similarity calibration
- Ecoregion IDs in the signature
- Retiring or redirecting the old Workbench page
- Terrain lens group (open; decide after WO1)
- Any new tab, dataset, or UI restructuring
