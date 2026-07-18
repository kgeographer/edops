# DEMO — Phase tracker

**This is the living source of truth** for the Demo phase: current state, roadmap, and
locked decisions. If any other Demo document disagrees with this one about *where things
stand*, this one wins.

- **Location:** `docs/edop/demo/DEMO_tracker.md`
- **Last updated:** 2026-07-17 (WO7a complete — lens registry + /api/similarity + two-dropdown UI)
- **Maintained:** updated by CC at session end and whenever a decision is locked; read at the
  start of each step and each phase gate.
- **Rule:** when a decision is locked or a gap is resolved, remove the corresponding
  forward-walking note in the same edit — never leave a resolved item as an open question
  elsewhere in the file.

---

## What DEMO is

Where SURFACE asked *does the instrument do X*, DEMO asks *what does the instrument say to a
person who has never seen it*. The work is curation, framing, and legibility — not
capability-building. Every prioritization call resolves against one question: **does this
help the Braga audience (21 Sep 2026)?**

Three tracks, sequenced:

1. **Track 1 — Hero shots**: curation + the features they need. Find the two or three polity
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
**583 tests pass, 52 skipped.**

Active page: `sandbox_v3.html` at `/sandbox/lookup3` — two-tab surface (Settlements +
Polities), all four scopes operable, BasinATLAS/LMR/HYDE choropleth, L06/L08 level toggle,
Analysis tab live on Settlements.

**WO1 + WO1a complete.** Findings in `docs/edop/demo/wo1_findings.md` and
`docs/edop/demo/wo1a_findings.md`; notebook in
`notebooks/edop/demo/wo1_within_polity_variance.ipynb`; merged to `demo` 2026-07-11.

**WO2 complete and merged** — slice slider + VCR, Band T inputs hidden on Polities tab,
coverage guards (BCE + below-floor), HYDE nearest-year fallback (Band T always present in
signature), polity examples added, Polities tab now default. Findings in
`docs/edop/demo/wo2_findings.md`.

**WO3a complete (read-only probe)** — scale-compare investigation. Findings in
`docs/edop/demo/wo3_probe_findings.md`. Key results:
- Tbilisi confirmed as demo case: 30 pp aridity drop, biome full flip (Temperate Broadleaf →
  Deserts & Xeric) between L06 and L08. Story carried by existing toggle on Settlements tab.
- N Song gradient holds at L08: spread values within 1–3 pp of L06, confirming gradient is real.
- Level toggle on Polities wired but L08 broken: `/api/area|areas` never returns `member_ids`,
  so `_sigMemberIds` = null; L08 paint guard fires. **Backend fix required (see roadmap).**
- Pacific Northwest (ARI.5): slide/Explorer only; sandbox shows geography, not LISA classes.

**WO3b complete (2026-07-13)** — polity–basin08 spatial crosswalk built:
- `temporal.polity_basin08_crosswalk`: 9,033,709 rows · 12,975 polities · 0 bad geometry
- 12 island/oceanic polities have no crosswalk rows (Hawaii, Mauritius, Seychelles, etc.) — correct; no L08 basins in open ocean
- Geometry repair required: 1,282 invalid slices fixed with `ST_MakeValid` + `ST_CollectionExtract`; build SQL changed to `ST_Intersection(b.geom, p.geom)::geography` (geometry path, matches engine) — geography×geography path caused 2,186 GEOS side-location conflicts
- `gaz.clio_polities` backed up to `gaz.clio_polities_backup` before repair
- Full findings: `docs/edop/demo/wo3b_polity-crosswalk.md`

**WO3c complete (2026-07-13)** — member_ids in API response + L08 speed via crosswalk:
- `resolve_crosswalk()` added to engine.py — keyed L08 lookup (~50 ms vs 3–10 s live query)
- `areal_signature_polygon()` accepts optional `polity_id`; uses crosswalk at L08 with live fallback for island polities
- Both `/api/area` and `/api/areas?type=polity` now return `member_ids` list (L08 hybas_ids)
- Frontend: `member_ids` path fixed (was incorrectly nested under `neighborhood`); `applySlice()` calls `_silentResig()` so member set updates before repaint on slice change; spinner on status el during slice step when variable active; Level select disabled for grid vars (LMR/HYDE), re-enabled for BasinATLAS
- Verified: N Song L08 aridity choropleth paints correctly; slice stepping repaints correctly; level toggle works
- Full spec + findings: `docs/edop/demo/wo3c_member-ids-and-l08-speed.md`

**tweaks0712 merged (2026-07-12)** — map cartography + UX polish:
- AWMC historical terrain basemap (replaces OSM+hillshade)
- Global HydroRIVERS PMTiles base layer (`app/static/sandbox/rivers.pmtiles`; gitignored); layer control toggle
- Basin fill-opacity → 0 (choropleth shows through; event targets preserved)
- White casing on all basin outline layers; color → charcoal `#3d3835` (avoids river-blue conflict)
- 4 placed settlement examples with Band T years (Timbuktu, Rome, Kaifeng, Santa Fe)
- Reset clears sig panel, re-disables tabs, returns to Map tab, resets example select
- Polity slice year overlay (top-left map corner, large `#993333` text, updates on every slice step)

**WO4a complete (2026-07-13, read-only probe)** — Analysis tab inventory + demo assessment:
- Scale-mismatch alert: does not fire on Tbilisi (1.4× ratio, threshold 50×); detects size
  disparity not MAUP effect — **dropped**, not ported.
- s/u divergence + provenance: fires correctly on archetype cases. Cairo L08: 26.9× precip
  ratio. Baghdad L08: 3.6×. Timbuktu L06: 5.05×; at L08 basin too small (588 km²) to resolve
  Niger signal. Lima: coastal terminal, orographic story absent at L08.
- Global divergence ranking feasibility: trivial query (precomputed columns); notebook pending.
- Full findings: `docs/edop/demo/wo4a_findings.md`

**WO4c–4e complete (2026-07-14) — Basin-similarity research (Track 2):**
- **WO4c** (Cell 1–14): Space characterisation — correlation structure, PCA (PC1 thermal 27%,
  PC2 moisture 21%, PC3 terrain 15%, PC4 provenance 8%), variable selection (13 local + 2 upstream),
  feature matrices. Validation: Mediterranean five fails (seasonality gap); Rhine/Willamette resolves
  correctly; Timbuktu provenance directional but weak in composite; Tbilisi test withdrawn for WO4d.
- **WO4d** (Cells 15–18): Dilution confirmed — Euclidean composite tracks temperature at 98% but
  moisture at 18% / wrong direction. Per-band distances built; κ=55.1 (well-conditioned). Rain-fed
  control non-existent at L06; discharge already carries provenance signal in composite.
- **WO4e** (Cells 19–23): Per-band Mahalanobis (κ per band 3.1–21.6, all Mah). C_climate Mah
  fixes dilution: 100%/111%/91%. Band-weighted composite fails (−47%/−57%/+30%): terrain dominates
  inter-level distance (1.206 vs climate 0.777); equal band weight amplifies not corrects. Provenance
  band validated: climate twins (dist_C ≈ 0.107) are provenance-distant (dist_prov median 2.024,
  precip_ratio median 1.00 vs Timbuktu 5.05). Band-weighted composite retired.
- **Instrument settled**: per-band Mahalanobis profile (primary); Euclidean composite for holistic
  queries; C_climate Mahalanobis for climate-primary queries. Comparison vector is Phase-4
  correspondence substrate.
- Findings: `wo4c_findings.md`, `wo4d_findings.md`, `wo4e_findings.md`

**WO4b complete (2026-07-13)** — Analysis tab ported to v3 Settlements:
- `sigVal()` + `renderAnalysis()` ported from v1; powered by parallel `/api/signature` fetch
  (raw values; `/api/areas` returns normalized scores only).
- Scale-mismatch alert dropped. Small-basin caveat made actionable (explains mechanism,
  directs to L06). Level-toggle note added at panel top.
- Example-select `change` now calls `_resetRightColumn()` — previously analysis pane lingered
  on example switch.
- Polity Analysis tab: open design question (logged in roadmap); pane left at placeholder.
  Upstream fields in polity signature are area-weighted means of per-basin upstream values —
  not "water from outside polity borders." Different question, unresolved.
- Full findings: `docs/edop/demo/wo4b_findings.md`

**WO7 + WO7a complete (2026-07-17) — Similarity tab: lens registry + two-dropdown UI:**

WO7 (Parts A/B, previously complete): seasonal-phase similarity endpoint, Similarity tab scaffold
with MapLibre world map, distance-based color ramp, SF example, named-place filter removed.

WO7a (Parts A–C, complete 2026-07-17):
- **Part A** (notebook `wo7a_climate_lenses.ipynb`): settled variable sets and metrics for
  three Climate sub-lenses. Confirmed: `ari_ix_sav` rejected from Precipitation lens (dimension
  mixing); Mahalanobis mandatory for Temperature (r = −0.837); NE adequate for Precip and Phase.
- **Part B** (`app/db/seasonality.py` refactor): `LENS_REGISTRY` drives all three active lenses.
  `load_similarity_index()` loads arrays once at startup; `find_similar(hybas_id, lens_id, n)`
  dispatches to Euclidean or Mahalanobis per lens. New: `GET /api/similarity?lens=<id>` (richer
  shape with `query_values` and per-result `values`); `GET /api/similarity/lenses` (registry for
  UI). `/api/seasonality/similar` kept as backward-compat wrapper.
- **Part C** (sandbox_v3 UI): single lens select replaced by group + sub-lens dropdowns populated
  from registry at page load. Anchor persists across sub-lens changes; switching sub-lens refetches
  for same location. `_simBlurb()` dispatches by lens_id with distinct text per lens.
- 3 new contract tests (backward-compat SF, London Mahalanobis maritime check, registry shape).
  583 tests pass, 52 skipped.
- **Part D (threshold rendering) → WO7b.** Current fixed top-200 works but is unprincipled —
  result count should reflect the actual similarity neighborhood, not an arbitrary cap.
- Branch: `demo_wo7a`. Spec: `wo7a_similarity-lenses.md`; findings: `wo7a_findings.md`.

**WO6 complete (2026-07-16) — Seasonality tab in sandbox_v3 (Settlements):**
- Fourth tab added to right-column strip: Map / Signature / Analysis / **Seasonality**.
- Disabled at cold start; enabled after "Get signature" on Settlements tab.
- Settlement name (H5) from `_currentPlaceName` — tracked in both WHG resolve and example paths.
- Two SVG charts side by side: Walter-Lieth dual-axis bar+line (precip bars + temp line) and
  polar (12 sectors radius ∝ precip; near-clear temp polygon). Both raw SVG, no library.
- Generated blurb: three rule-based sentences from concentration, phase offset+peak months,
  amplitude. Stays within what the scalar readings can claim — no geographic inference.
- Scalar table: peak months rendered as month name (not 0–11 index); gloss blank for those rows.
- No new tests (UI-only). 580 tests pass, 52 skipped.
- Spec: `docs/edop/demo/wo6_seasonality-tab.md`; findings: `docs/edop/demo/wo6_findings.md`

**WO5 complete (2026-07-15) — Seasonality arrays + derived indices (Band C):**
- `v_basin06_persist_rev2` / `v_basin08_persist_rev2` views created in DB: add
  `pre_mm_monthly float[]` (12 monthly precip values) and `tmp_dc_monthly float[]`
  (monthly temp in °C, ×10 division applied in view) alongside all rev1 columns.
- `signature.py` switched to rev2 views (`_VIEW_FOR_LEVEL`); rev1 views untouched as rollback.
- `_circ_stats()` + `_seasonality_indices()` compute 6 derived scalars from the arrays:
  `pre_concentration`, `pre_peak_month`, `tmp_concentration`, `tmp_peak_month`,
  `seas_phase_offset` (circular distance between precip and temp peaks, months [0,6]),
  `tmp_seas_amp` (max−min monthly temp).
- Arrays and derived scalars in top-level `out` only — not in `profile_groups` — so v1
  sandbox accordion is unaffected.
- Variable catalog updated: 2 rows promoted to implemented (type=object); 6 new derived rows added.
- Engine contract test updated: DERIVED_KEYS + count 5→11.
- 3 new WO5 contract tests in `tests/test_api_examples.py`:
  `test_seasonality_arrays_rome`, `test_seasonality_scalars_rome` (pinned ±0.05),
  `test_seasonality_discrimination` (Rome offset > 3.5; Delhi offset < 1.5; London conc < 0.2).
- 580 tests pass, 52 skipped.
- Notebook investigation: `notebooks/edop/demo/wo5_seasonality.ipynb`
- Findings: `docs/edop/demo/wo5_findings.md`

---

## Roadmap (seed)

| Item | What | Status |
|---|---|---|
| Within-polity-variance ranking notebook (WO1 + WO1a) | Rank polities by spread; trajectory + size-confound validation; membership spot-check; hero-shot shortlist confirmed | **complete** |
| Continuous time slider + signature fixes (WO2) | Slider + VCR, Band T inputs hidden, coverage guards, HYDE nearest-year fallback, polity examples | **complete — merged** |
| Scale-compare probe (WO3a) | Tbilisi case + N Song gradient + level-toggle diagnosis | **complete** |
| Polity–basin08 crosswalk (WO3b) | `temporal.polity_basin08_crosswalk` — 9M rows, 12,975 polities, 0 bad geometry | **complete** |
| L08 polity choropleth fix (WO3c) | member_ids in API; crosswalk-lookup path in engine; level toggle on Polities tab working | **complete — merged** |
| Analysis tab — s/u divergence + provenance (WO4a–4b) | WO4a probe confirmed Cairo/Baghdad as archetype cases; WO4b ports divergence table + provenance badge to v3 Settlements tab | **complete — merged** |
| Basin-similarity research (WO4c–4e) | Instrument settled: per-band Mah profile + Euclidean composite + C_climate Mah; band-weighted retired; all four bands exercised | **complete** |
| Hero shot curation | Manual curation once UI is stable; Karl selects cases in browser | pending — Karl-driven |
| L06 ↔ L08 toggle demo (MAUP) | Toggle on Settlements tab already works; Polities tab L08 now working | pending |
| Analysis tab — polity scope | What the Analysis tab shows for a polity is an open design question; upstream fields in polity signature are area-weighted means of per-basin upstream values, not "water from outside polity borders" | pending design |
| Scale-sensitivity flag | *"This location is scale-sensitive"* tag from L06↔L08 signature diff; replaces dropped v1 scale-mismatch alert | pending |
| Global divergence ranking | Notebook: rank basins by `precip_yr_upstream / precip_yr` to surface allochthonous places globally; trivial query, both columns precomputed in basin06/basin08 | pending |
| Correspondence surfacing | D-PLACE / Workbench Societies screen; decision: port vs. demo-as-is | pending |
| Seasonality (WO5) | Monthly arrays + 6 derived indices in signature; rev2 DB views; catalog updated; 3 contract tests | **complete** |
| Seasonality tab (WO6) | Walter-Lieth + polar SVG charts; generated blurb; scalar table with month names; settlement name heading | **complete** |
| Similarity lens registry + UI (WO7 + WO7a) | Lens registry; `/api/similarity`; two-dropdown group+sub-lens UI; three Climate sub-lenses live; Parts A–C complete | **complete — branch demo_wo7a, pending merge** |
| Similarity threshold rendering (WO7b) | Distance-threshold result sets (variable-N) so result count reflects actual similarity neighborhood; honest stringency control | **next** |
| Terrain/hydrology discrimination tests | Per-band discrimination tests analogous to WO4e Cell 23; needed only if a use case requires it | deferred |
| Surface integration — similarity instruments | Expose per-band profile + Euclidean composite + C_climate Mah in sandbox_v3; separate future WO | deferred |
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

**2026-07-17**

- **WO7a lens registry architecture locked** — `LENS_REGISTRY` in `seasonality.py` is the
  single source of truth for similarity lens definitions. Adding a lens is a registry entry;
  no new distance logic is needed. Three active Climate sub-lenses shipped:
  `climate.precip` (NE, 2 vars), `climate.temp` (Mahalanobis, 3 vars), `climate.phase`
  (NE, 2 vars). Disabled stubs for Terrain and Hydrology present in registry.
  `/api/seasonality/similar` kept as backward-compat wrapper indefinitely.

- **Fixed top-N is insufficient for honest similarity display** — current top-200 result set
  has no principled relationship to the query basin's actual similarity neighborhood. A
  Mediterranean-type basin (rare climate) and a tropical monsoon basin (common climate) both
  return 200 results at wildly different distance spreads. WO7b will introduce a distance
  threshold (SD-radius or equivalent) so map density reflects how many basins genuinely
  qualify — not how many the cap allows.

**2026-07-15**

- **WO5 seasonality architecture locked** — Monthly arrays (`pre_mm_monthly`, `tmp_dc_monthly`)
  live in rev2 views alongside all rev1 columns; `signature.py` points to rev2; rev1 stays live
  as instant rollback. Six derived scalars computed in Python from arrays; placed in top-level
  `out` only (not `profile_groups`) so v1 sandbox is unaffected. Acceptance criteria (notebook
  cell 8, 2026-07-14): Rome pre_concentration ≈ 0.280 (±0.05), seas_phase_offset ≈ 4.486 (±0.05);
  Delhi seas_phase_offset < 1.5; London pre_concentration < 0.2. Engine.py `_LEVEL_VIEW` still
  points to rev1 — separate step when engine needs seasonality.

**2026-07-14**

- **Basin-similarity instrument settled** — Per-band Mahalanobis profile is the primary
  instrument; Euclidean composite (13 local vars) for holistic "similar places" queries;
  C_climate Mahalanobis for climate-primary queries. Band-weighted composite retired: it
  amplifies rather than corrects imbalance when one band dominates the inter-level distance.
  The comparison vector is Phase-4 correspondence substrate — do not re-derive.
  Open (not WO4 loose ends): terrain/hydrology discrimination tests; surface integration
  (separate future WO). Seasonality (WO5) complete — see 2026-07-15 locked decision above.

**2026-07-13**

- **s/u divergence is substantially an L06 instrument** — at L08 most basins are small enough
  that upstream catchment barely exceeds themselves, so divergence tends to unity by construction.
  Cairo works at L08 only because it sits at the base of the Nile with 2.9M km² upstream — the
  exception, not the pattern. The Analysis panel reflects this: level-toggle note at top; small-
  basin caveat directs user to L06 rather than reporting "undetermined."

- **Analysis tab Polities scope is an open design question** — upstream fields in the polity
  signature (`precip_yr_upstream`, etc.) are area-weighted means of each member basin's own
  upstream value, not a measure of "water from outside polity borders." The naive ratio would
  be misleading. No Analysis content wired for Polities tab; design deferred.

- **WHG API broken (2026-07-13)** — all WHG endpoints return 403 "Bot access denied." Token
  is valid and quota decrements. Root cause: WHG Cloudflare bot-filter change; `User-Agent:
  notbot` per docs does not resolve it. Stephen Gadd (WHG developer) contacted. Reverted
  User-Agent to original browser string pending response. WHG lookup non-functional in both
  local and production until resolved.

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
