# CDOP Pilot — Phase tracker

**This is the living source of truth** for the CDOP Pilot phase: current state, roadmap,
and locked decisions. If any other CDOP document disagrees with this one about *where things
stand*, this one wins — for CDOP Pilot scope only.

- **Location:** `docs/cdop/pilot/CDOP_PILOT_tracker.md`
- **Last updated:** 2026-07-21 (WO4 complete — all six parts run, findings logged, overall
  verdict delivered; verdict language corrected same day — locality reframed as measurement not
  deficiency, four-instrument membership corrected; next decision is what to build in response,
  not more investigation)
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
consult at every step resumption, add rows there (`docs/design/deferred_items_register.md`).

---

## You are here

Phase opened 2026-07-18. Integration branch: `cdop` (cut from `main` after DEMO merge).
WO branches cut from `cdop`, merged back on accept.
**584 tests pass, 50 skipped.**

**WO4 complete — verdict delivered; similarity architecture decision now pending.** WO3 Parts
A+B complete and merged to `cdop_pilot`. Parts C+D (scalar hygiene, glyph) remain suspended —
WO4 (`wo4_similarity-studies.md`, approved 2026-07-20) was the similarity-approach
reconsideration this was waiting on: `notebooks/cdop/wo4_similarity-studies.ipynb`, testing
whether "similarity" is one instrument or four, ran to completion. **Verdict: four instruments
distinguished by output shape — ranked analogue (geography-exclusion is a parameter of this one
instrument, not a separate instrument), matched control set, global-typological position,
local-typological position.** Locality in a ranked-analogue result is a measurement of the
place, not a deficiency in the instrument; geography exclusion answers a second, different
question, available as a control rather than a default. Full findings:
`docs/cdop/pilot/wo4_findings.md`. **Next step is a design decision** (what WO3 Parts C+D and
WO1's accept gate should actually do in response), not more investigation — see WO4 section.

---

## Roadmap

| Step | Branch | Status | Notes |
|---|---|---|---|
| WO1 — CDOP pilot page + L08 lens similarity | `cdop_pilot` | **blocked** | Plumbing complete; accept gate partial fail; blocked on WO3 |
| WO2 — Rainfall modality investigation | `cdop_wo2` | **complete** | Bimodal characterization; continuous (a1,b1,a2,b2) representation validated |
| WO2a — Continuous harmonic representation | `cdop_wo2` | **complete** | Part B pass; Part C clean on own-top-5 evidence; phase lens retired |
| WO3 — Continuous precip lens + retire phase lens | `cdop_wo3` | **stasis** | A+B complete (merged); C+D suspended; similarity approach under reconsideration |
| WO4 — Four similarity instruments on shared probes | `cdop_pilot` | **complete** | All six parts run; verdict: four instruments by output shape (ranked analogue w/ exclusion parameter, matched set, global/local typology). Design decision on architecture now pending. |

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

## WO4 — Four similarity instruments on shared probes

**Work order:** `docs/cdop/pilot/wo4_similarity-studies.md` (approved 2026-07-20)
**Branch:** `cdop_pilot`. Notebook: `notebooks/cdop/wo4_similarity-studies.ipynb` (complete, all
six parts run). Full findings: `docs/cdop/pilot/wo4_findings.md`.

Tests whether "similarity" is one instrument or four (analogue / analogue net of geography /
matched control set / typological position) on seven probe basins (the WO's six plus Santiago,
added for Southern Hemisphere coverage), plus a Part 0 measuring how often the L06/L08
basin-container mean diverges from actual site elevation across historically significant
settlements.

### Prerequisite — D-PLACE schema audit (complete 2026-07-20)

Part 3 (matched control set, addressing Galton's problem for the eventual D-PLACE
correspondence test) needs a trustworthy society↔basin join and a phylogenetic proxy. Full
findings: `data/dplace/dplace_audit_findings.md` (gitignored — data-adjacent working doc).
Follow-up EDA: `notebooks/cdop/dplace_eda.ipynb`.

Headline: the core CLDF tables (`societies`, `data`, `variables`, `codes`, `contributions`)
are a complete, exact, current import of D-PLACE CLDF v3.1.1 — not the stale hodgepodge
suspected going in. `dplace.societies` (6,684 rows) holds 4,085 `languoid` scaffold rows plus
2,599 real `society` rows across **seven** independent ethnographic samples (EA 1,291; ccmc
410; binford 339; sccs 186; wnai 172; carneiro4 127; carneiro6 74) — `cdop_pilot`/workbench
currently surfaces only the EA slice (via `contribution_id='dplace-dataset-ea'`), which is why
the app shows 1,291 against the table's 6,684.

**Locked decisions:**

- **EA-only for WO4 Part 3.** `xd_id`/`glottocode` cross-checks (`dplace_eda.ipynb`) show 41.8%
  of EA's 1,291 societies (540) have a same-culture match in another sample — 395 via `xd_id`
  to Binford/SCCS/WNAI, 281 via `glottocode` to ccmc/carneiro4/6 — and carneiro4/6 mostly
  duplicate EA outright (83–86% overlap; two editions of the same source). Pooling would
  overcount and needs real dedup work. EA is the one sample with existing basin/bioregion
  linkage (`society_basin`, `society_spatial`) and no internal duplication problem of its own.
- **`society_basin` L06 backfill: still held.** Only L08 rows exist (1,133 of 1,291 EA
  societies, 87.8% — matches Part 3's own cited figure). Not needed — Part 3 runs at L08 only.
- **Family crosswalk: built in Part 3, not held anymore.** 85 Glottolog family tree files on
  disk parsed by regex (leaf glottocodes only, no tree-topology parsing) → 1,245-glottocode
  crosswalk. Matching on raw `glottocode` alone only resolved 74.3% of EA societies to a
  family; CLDF's `language_level_glottocodes` field exists specifically for this and raised it
  to 92.6% (1,049/1,133). Detail in `wo4_findings.md` Part 3.
- **D-PLACE enrichment (pooling variables from the other six samples onto EA societies via
  `xd_id`/`glottocode`, not adding new society rows) logged as deferred**, not built now:
  `docs/design/deferred_items_register.md` § CDOP — D-PLACE data.
- **Two dead scripts deleted**: `scripts/edop/dplace_env_correlations_{signature,exploratory}.py`
  referenced a `dplace.societies.basin_id` column that doesn't exist in the current schema and
  would error if run. Superseded by `app/api/routes.py`'s `/societies` route.
- **Deferred items register relocated**: `docs/design/areas/deferred_items_register.md` →
  `docs/design/deferred_items_register.md` — it was never Areas-specific, just nested there.
  All full-path references repo-wide updated in the same edit.

### Notebook setup decisions (resolved)

- **Part 0's "WHG settlement corpus" scope**: full `gaz.whg_gaz` (1.5M rows) was infeasible
  against the free elevation API. Resolved to two corpora, matching the WO's own proviso to
  count exposure in units of use — WH Cities (254/258) **and** D-PLACE EA (1,133/1,291) — run
  side by side, not either alone.
- **A real bug found and fixed early**: the notebook's first pass used only the 4 shape
  features `(a1,b1,a2,b2)` with raw Euclidean distance. Production `climate.precip`
  (`app/db/seasonality.py` — the WO text's `app/db/similarity.py` doesn't exist) actually uses
  5 features including `log_pre_mm_syr`, Euclidean on **z-scored** variables. Fixed; surfaced
  by spurious ~17,500 km "matches" for George Town before the fix. Full detail in
  `wo4_findings.md`.

### Results (Parts 0–6) — full detail in `wo4_findings.md`

- **Part 0**: L08 basin nested in (or, for Mombasa, exactly equal to — HydroBASINS' hierarchy
  terminates early for some basins) its L06 parent, confirmed for all 7 probes directly against
  geometry. Corpus-wide exposure (Part 0B): container mismatch is **a substantial share, not a
  thin tail**, even at L08 — 13.4% (EA) to 14.6% (WH Cities) still show a >2°C implied
  temperature gap at the better level.
- **Part 1**: 6 of 7 probes are entirely local in their unrestricted top-10 (autocorrelation,
  not analogy). Santiago's exception (Western Australia wheatbelt matches) is a genuine,
  textbook Mediterranean-climate teleconnection.
- **Part 2**: Mombasa → Guitri, Ivory Coast replicates WO2a's own validated Abidjan finding.
  Tbilisi and George Town show single distant matches that don't change across any exclusion
  radius from 250–5000 km — an unexplained pattern, noted for follow-up.
- **Part 3**: matched-control-set construction (Galton's problem instrument, `EA042` as a
  smoke test) works — 37 matched pairs found (997 usable societies). Known limitation, not
  fixed: some pairs share a "b" partner from the same real-world cluster counted more than once
  (~30–32 genuinely distinct once collapsed).
- **Part 4**: `pre_modality`'s distance-to-boundary confidence measure is actively misleading —
  Timbuktu's known-artifact "bimodal" reading (WO2a) shows the *largest* margin of any probe,
  while Mombasa's validated real bimodal case shows the *thinnest*. Mombasa and George Town land
  in the identical bioclimate bucket despite meaningfully different continuous-lens values —
  categorical typology is coarser than the continuous lens, concretely.
- **Part 5**: local-anomaly percentiles independently reconfirm the container problem for
  Tbilisi and Augsburg (both collapse to the bottom ~3% of their own 1000 km region on
  temperature despite unremarkable global percentiles) — a third, unrelated method landing on
  the same fact Part 0 and the original visual review already established.
- **Part 6**: Jaccard(Part 1, Part 2) = 0.00 for 6 of 7 probes (mechanically guaranteed once
  Part 1 showed those probes were all-local) and 0.25 for Santiago (real convergence — Part 2
  independently rediscovers the same distant Western Australia matches Part 1 found
  unprompted).

**Overall verdict**: four instruments distinguished by output shape, not by whether geography is
excluded — ranked analogue (Parts 1–2 unified; exclusion radius is a parameter of this one
instrument), matched control set (Part 3), global-typological position (Part 4),
local-typological position (Part 5). Six of seven probes returning all-local top-10s at L08 is a
measurement of those places, not a failure of the instrument; Part 6's six zero-Jaccard cells
follow mechanically from Part 1's own results and aren't independent evidence for anything
(Santiago's 0.25 is the one informative cell). Geography exclusion answers a second question a
user may ask — worth a control, default off — not a precondition for the first question to mean
anything. **Next step is a design decision** on what this means for the lens registry /
similarity architecture (e.g. whether a lens needs a declared geography-inclusion argument, not
just a variable set) — not further investigation. Not made here; needs Karl/Opus review.

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

- Overall instrument validity — **answered by WO4** (four instruments by output shape; see WO4
  section above); implementation decision still pending, not further investigation
- Mahalanobis vs Euclidean for climate.temp; L06 container problem for mountain cities;
  threshold CDF calibration for all active lenses; wiring level toggle into sandbox similarity
  tab (2-line fix, held)
- WO3 Parts C+D — scalar hygiene + monthly profile glyph (suspended pending approach decision)
- L08 threshold recalibration
- Semantic-similarity calibration
- Ecoregion IDs in the signature
- Retiring or redirecting the old Workbench page
- Terrain lens group (open; decide after WO1)
- Any new tab, dataset, or UI restructuring
