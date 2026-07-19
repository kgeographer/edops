# CDOP Pilot — Phase tracker

**This is the living source of truth** for the CDOP Pilot phase: current state, roadmap,
and locked decisions. If any other CDOP document disagrees with this one about *where things
stand*, this one wins — for CDOP Pilot scope only.

- **Location:** `docs/cdop/pilot/CDOP_PILOT_tracker.md`
- **Last updated:** 2026-07-19 (WO2 opened — rainfall modality investigation; notebook-only; EDOP work homed here)
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
**585 tests pass, 52 skipped.**

**WO2 open** on branch `cdop_wo2` (cut from `cdop_pilot`). WO1 blocked pending WO2 outcome.

---

## Roadmap

| Step | Branch | Status | Notes |
|---|---|---|---|
| WO1 — CDOP pilot page + L08 lens similarity | `cdop_pilot` | **blocked** | Plumbing complete; accept gate partial fail; blocked on WO2 |
| WO2 — Rainfall modality investigation | `cdop_wo2` | **open** | Notebook-only; EDOP work; doubles as WO1 unblock |

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

- [ ] WO2 complete: bimodal class characterized, variable definitions recommended
- [ ] Remediation implementation (scope set by WO2 Part B/C findings)
- [ ] Test suite green after L08 startup change
- [ ] Merge `cdop_pilot → cdop` on accept

---

## Locked decisions

| Decision | Rationale |
|---|---|
| topN=5 for WH Cities | Threshold mode returns zero peers for 36–39% of cities at strict; loose temp returns median 148/254. topN=5 approximates empirical moderate scale for precip/phase. From `wo_l08_findings.md` Part D. |
| L06 thresholds not used at L08 | Counts inflate ~10×; `climate.temp/loose` returns 46% of all L08 basins. Recalibration deferred and not needed for this use case. |
| Corpus-relative label | "5 most similar cities in this collection" — scope is the 258-city corpus, not a global neighbourhood. Distinguishes from sandbox Similarity tab. |
| Old Workbench stays live | Rollback path; retire/redirect decision deferred. |
| Basins tab dropped but recoverable | Passed the inverted-query test; dropped as EDOP-side classification. Clone makes it recoverable. Not rediscovered as a new idea. |

---

## Deferred / out of scope

- L08 threshold recalibration
- Semantic-similarity calibration
- Ecoregion IDs in the signature
- Retiring or redirecting the old Workbench page
- Terrain lens group (open; decide after WO1)
- Any new tab, dataset, or UI restructuring
