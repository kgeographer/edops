# AREAS — Phase 3 tracker

**This is the living source of truth** for the Areas phase: current state, the step roadmap,
and locked decisions. If any other Areas document disagrees with this one about *where things
stand*, this one wins.

- **Location:** `docs/edop/areas/AREAS_tracker.md`
- **Last updated:** 2026-06-25
- **Maintained:** updated by CC at session end (part of the pre-commit ritual) and whenever a
  decision is locked; read at the start of each step and each phase gate.
- **Rule:** when a decision is locked or a gap is resolved, remove the corresponding
  forward-looking note (in "You are here", block table, or deferred register) **in the same
  edit** — never leave a resolved item as an open question elsewhere in the file.

---

## You are here

Building the aggregation **engine** (resolver → aggregator) along the buffer-neighborhood path,
using the **Timbuktu 100 km / L06 buffer** as the working fixture. Steps 1–2 complete. Step 3
(aggregator) is underway: all blocks 1–7 done. **WO1–WO11a done.** Response contract fully closed.
`make_row` is the conformance target. All primary branches B1–B5 + B7 emit through `make_row`; B6 post-pass closes the WO6-deferred fields. `load_catalog` reads the live codebook → meta_df (build-once startup layer); sourced/derived fork in place. **`areal_signature` is the public entry point; engine assembled and whole.**

**Next:** extend to additional resolver types and scales before wiring routes. Candidate work: (1) L8 experiment — run Timbuktu at level=8 (77 basins vs. 9) to assess MAUP sensitivity; (2) polity resolver — polygon WKT in → ST_Intersection weights → same pipeline (directly enables Cliopatria queries and Phase 4); (3) multi-basin topology resolver — containing basin + ST_Touches adjacency. Routes are thin front doors and come after at least one new resolver is validated.

---

## What Areas is

Extends EDOPS signatures from a single point to an areal extent — a neighborhood around a
point, or a polygon (polity, study area). The hard part throughout is that a region rarely
reduces to one honest number, so the work is as much about *when a summary is meaningful* as
about computing it.

## Architecture (the spine)

Every areal query resolves in two stages: a **resolver** turns the query into a weighted basin
set `[{basin_id, weight}]`; an **aggregator** collapses that set, per variable, into a
signature. Point-rooted neighborhoods (`basin`, `buffer`, `upstream`) are parameters on
`/signature`; polygons go to a future `/area` endpoint. Both are thin front doors over one
shared engine — later query types reuse the attachment and aggregator and only add a new
resolver.

---

## Roadmap

### The engine (current focus)

| Step | What | Status |
|---|---|---|
| 1 | Buffer resolver — point + radius → weighted basin set | **done** (Timbuktu 100 km / L06; 9 basins, weights sum to 1) |
| 2 | Value attachment — basin set → scores + labels matrix | **done** (re-run with corrections: flags raw, gdp/hdi excluded, categoricals as labels) |
| 3 | Aggregator — collapse the set per variable, with coherence | **in progress**, by block (below) |

#### Step 3 blocks

| Block | What | Status |
|---|---|---|
| 1 | Coherence check + concentrated/gradient path | **done** — incl. zero-inflation handling; validated on Timbuktu (5 concentrated, 13 spread, 1 outside_active_domain) |
| 2 | Network-topology path — dominant basin (discharge_annual, discharge_min, discharge_max) | **done** — all three vars; dominant basin hybas_id 1060564960 (Niger main-stem: 567.6 m³/s annual, 301.8 m³/s min → perennial, 1089.2 m³/s max). All discharge units m³/s. |
| 2b | scale-dependent → Block 1; local-anomaly → Block 5 | **resolved** — scale-dependent vars use area-weighted coherence (same as continental-gradient); dispatch updated in step3 Cell 4. river_area (local-anomaly) deferred to Block 5 fallback. No new math needed. |
| 3 | Categorical path (% of class) | **done** — 9 vars (lith_class, wetland_class, zone_name, biome, eco_id, pnv_majority, freshwater_ecoregion_class/name, land_cover_name). strata_code excluded (opaque sub-zone codes; see register). |
| 4 | Flag / structural path — outlet_type (4-class mixture) + coast_fraction (flag_fraction) | **done** — outlet_type derived from endo×coast (4 non-overlapping classes); Timbuktu: exorheic 53.5% / terminal-sink 46.5%, coast_fraction=0.0 (uniform). Endorheic fraction 0.4654 = dist_sink weight_at_zero (cross-block consistency). step3_results.tsv: 48 rows. |
| 5 | Untyped fallback (distribution-only) + extreme (river_area) | **done** — 2 untyped continuous vars (temp_min, temp_max; band C); river_area extreme (dominant basin 1060582960, 4273 km², ≠ Block 2 discharge dominant — Inner Niger Delta split, informative). step3_results.tsv: 51 rows. step3_block5_distribution.tsv written (18 companion rows). |
| 6 | Modality refinement (broad vs two-regime) | **done** — 12 two_regime vars detected across 36 distribution-bearing rows; 11/12 seam-aligned with Block 4 endorheic partition (Block 6 independently rediscovers the Niger/Sahara boundary). 2 scores suppressed (cropland_extent 5.29→null, temp_yr_upstream 96.45→null; both were `concentrated` but two-regime). Regimes companion written (24 rows, 12 vars × 2). Weak calls (temp_yr_upstream, pct_sand) flagged for multi-fixture calibration. |
| 7 | Gridded temporal path (Band T) — areal aggregation of HYDE + LMR over the buffer; temporally scoped; distribution vs. collapsed mean governed by ECC diagnostic. eVolv2k global forcing, no areal step. | **done** — ECC_THRESHOLD=10 separates HYDE (393, distribution) from LMR (3.75, collapse). `aggregate_band_t(from_year, to_year)` handles snapshot and wide-span with no mode flag. Primary (1100–1200): 321 rows. Wide (1000–2000): 3427 rows. Three outputs: `step3b_block7_primary.tsv`, `step3b_block7_wide.tsv`, `step3b_block7_hyde_distributions.tsv`. Two engine-assembly consequences in register: `n_units`/`unit_type` generalization; second coverage notion. |
| WO1 | Bottom-of-stack extraction — `resolve_buffer`, `weighted_quantile`, `diff_output` harness → `scripts/edop/areas/engine.py` | **done** — regression passes vs step2_raw.tsv |
| WO2 | Attachment pass — `attach_values` + SQL builders (`_val_expr`, `rank_expr`, `two_pass_sql`) → engine.py | **done** — regression passes vs step2_matrix.tsv, step2_raw.tsv, step2_class_ids.tsv |
| WO3 | Dispatch — `dispatch_variable(typology_cluster, kind)` → block label | **done** — 49/54 meta_df vars verified; 5 surfaced (see below) |
| WO4 | `make_row` + projector + assembler + Band T promotion | **done** — `make_row`, `project_row`, `assemble_payload`, `CAVEAT_TEXTS` + `aggregate_band_t` (wired to make_row) in engine.py. All 5 acceptance tests PASS. `make_row` is now the conformance target for B1–B6 extraction. |
| WO5 | B2 — `dominant_basin` extraction | **done** — `aggregate_b2(basin_set, matrix_df, raw_df, meta_df)` in engine.py. 4/4 acceptance tests PASS. Three determinations: (1) B2 rows carry both score + raw; (2) `perennial` stored in `detail` on discharge_min row (engine enrichment); (3) `n_units=9` = full buffer set (not 1); dominant basin carried via `detail['dominant_hybas_id']`. `test_engine_wo5.py` strict PASS. |
| WO6 | B1 — `area_weighted` extraction | **done** — `aggregate_b1(basin_set, matrix_df, meta_df, …)` in engine.py. 5/5 acceptance tests PASS. `representative_raw=None` throughout (native-unit means deferred). Spread computed from un-rounded p10_raw/p90_raw (matches notebook ordering; avoids 0.01 rounding boundary). Two-regime rows: B1 emits correct non-null scores for 2 concentrated two_regime rows (≈ frozen `representative_score_suppressed`); B6 post-pass is WO10. `test_engine_wo6.py` strict PASS. |
| WO7 | B3 — `class_mixture` extraction | **done** — `aggregate_b3(basin_set, matrix_df, class_id_df, meta_df, …)` in engine.py. 6/6 acceptance tests PASS. Three determinations: (1) `representative_raw=None` — modal label in `detail['modal_label']`, not lean row (confirmed from frozen TSV); (2) lean carries `coherence`; detail carries `modal_class_id`, `modal_label`, `modal_share`, `n_classes`, `concentration`, `mixture` list; (3) coherence rule: `modal_share >= 0.85` → `'concentrated'`, else `'mixed'` — value set is exactly `{concentrated, mixed}`, no `no_data` in fixture. Special case: `eco_id` text labels come from `matrix_df['ecoregion']`, not `matrix_df['eco_id']` (which holds integers). `test_engine_wo7.py` strict PASS. |
| WO8 | B4 — `flag/structural` extraction | **done** — `aggregate_b4(basin_set, raw_df)` in engine.py. 7/7 acceptance tests PASS. Determinations: (1) `coast_fraction` carries `coherence=None` (scalar; no concentrated/mixed concept); `representative_raw=0.0` (the fraction); (2) `outlet_type` `representative_raw='Exorheic, non-coastal'` (modal label; WO7b convention; frozen TSV re-frozen); (3) cross-block consistency confirmed: endorheic fraction (0.4654) ≈ `dist_sink` `weight_at_zero` (0.4700, gap=0.005). Exclusivity assertion live. `endorheic` and `coast_flag` not emitted standalone. `test_engine_wo8.py` strict PASS. |
| WO9 | B5 — `distribution_only` + `extreme` extraction | **done** — `aggregate_b5(basin_set, matrix_df, raw_df, meta_df)` in engine.py. Returns `(rows, companion_rows)`. 6/6 acceptance tests PASS. Determinations: (1) `distribution_only` `coherence=None` — fallback surfaces distribution without rendering a typed verdict; `representative_score` = weighted mean percentile (always populated); (2) `extreme` `representative_raw` = max raw value (km²); `representative_score` = carrier percentile; `dominant_hybas_id` in detail; `coherence=None`. Inner Niger Delta split preserved: river_area carrier (1060582960) ≠ B2 discharge dominant (1060564960). `test_engine_wo9.py` strict PASS. |
| WO10 | B6 — modality post-pass | **done** — `detect_modality(scores, weights_norm, spread, …)` + `apply_modality(rows, basin_set, matrix_df)` in engine.py. Returns `(rows, regimes_companion)`. 6/6 acceptance tests PASS. De-closure: `detect_modality` consumed `joined[var]` (scores), `joined['weight']` (weights), `endo_hybas` (seam annotation only — not detection). **Determination: `endorheic_set` is used only for seam-alignment reporting, not detection; omitted in engine.** Modality ∈ {`unimodal`, `two_regime`} on all 36 distribution-bearing rows (contract §4 values; not `concentrated`/`broad`). `score_suppressed=True` only when B6 is reason for null (was concentrated): `cropland_extent` (5.29→null) + `temp_yr_upstream` (96.45→null); suppressed values preserved in `detail['suppressed_score']`. 11/12 regime centers match frozen TSV exactly. **Data lineage artifact:** `pct_sand` regime centers (76.16/94.05 engine vs 72.65/89.71 frozen) — step3_block6_regimes.tsv produced pre-population-hygiene-fix; regime_weight and two_regime classification correct. Action: re-freeze pct_sand rows. |
| WO11a | Catalog layer — `load_catalog` + sourced/derived fork | **done** — `load_catalog(level, codebook_path)` in engine.py. Reads live codebook → meta_df (59 rows: 54 sourced + 5 derived). Sourced rows == step2_meta.tsv on all columns; one expected diff: `endorheic.schema_key='endorheic'` (Karl's 2026-06-24 catalog edit; frozen was 'outlet_type'). `kind` derivation: `_FLAG_API_KEYS` override first; `position_method='rarity_rank'` → categorical (covers integer-coded class IDs eco_id/wetland_class); else type-based. Derived rows (coast_fraction, elev_point, outlet_type, relief_position, relief_range_m): all `derived=True`, `db_col=None`. `attach_values` skips derived rows; dispatch routing 54 sourced vars: B1=34, B2=3, B3=11, B4=2, B5=4, unknowns=0. 7/7 acceptance tests PASS including B1 + B4 live regressions. WO expected 2 derived rows; actual 5 (elev_point/relief_position/relief_range_m were already status='implemented'). |
| WO11b | Final assembly — `areal_signature` public callable | **done** — `areal_signature(lat, lon, radius_km, conn, level, bands, from_year, to_year, include_detail)` in engine.py. Build-once catalog cached in `_CATALOG_CACHE` per level. Pipeline: resolve_buffer → attach_values → B1–B5 → B6 post-pass (B1+B5 only) → Band T (gated on span) → assemble_payload. 8/8 capstone tests PASS: basin rows=51; all representative_scores strict vs step3_results.tsv; B3 mixture (22 rows), B5 companion (18 rows), B6 regimes (24 rows), Band T primary (321 rows) all strict; payload structure + lean/full gating correct. No number changed vs per-branch regressions — assembly is a seam-up. |

### Later in the phase

| Item | What | Status |
|---|---|---|
| Upstream neighborhood | Resolver via network traversal; reuses attachment + aggregator; distinct from the routed `_u` values | todo |
| `threeTier` neighborhood | Structured combination; define only once simpler neighborhoods show what it must add | todo — see register |
| Polygon `/area` endpoint | Geometry/id input (polity, bbox, GeoJSON) → same engine | todo |
| Sandbox / dashboard surfacing | Area query results made visible | todo |
| Multi-fixture calibration | Tune all provisional thresholds (T=20, MODALITY_GAP=0.50, MIN_REGIME_WEIGHT=0.20, per-level L6/L8 policy) against Egypt, Song, and other fixtures beyond Timbuktu. Add an absolute-separation floor to the modality detector; recheck known-weak Block 6 calls (temp_yr_upstream, pct_sand). Single destination for all "provisional, needs more fixtures" items. | Once ≥2 additional fixtures are available |

---

## Locked decisions

Append-only; dated. Settled unless explicitly revisited here.

**2026-06-13 / 14**

- **Architecture** — query → weighted basin set (resolver) → variable-aware aggregation
  (aggregator); one engine, point-rooted neighborhoods on `/signature`, polygons on `/area`.
- **Buffer weighting** — each basin's weight = fraction of the buffer area it covers; slivers
  dropped below epsilon; open-water shortfall is *reported*, not renormalized.
- **Coverage shortfall (per variable)** — *renormalize* the surviving basins' weights
  (data-absence), distinct from the buffer's geographic-absence shortfall. Label the two
  distinctly (`coverage` vs `shortfall`).
- **Score space** — aggregation works on global-percentile scores (0–100); native-unit means
  deferred.
- **Dispatch** — aggregation method chosen per variable from `typology_cluster`.
- **Block-1 coherence** — spread-based; `concentrated` if weighted (p90 − p10) < T;
  **T = 20, provisional.**
- **Categoricals** carried as class labels/ids, aggregated as % of class. **Flags raw:**
  `coast_flag` boolean, `endorheic` is 0/1/2 (handle as 3-class, not boolean). **Excluded from
  the signature:** `gdp_avg`, `human_dev_idx`.
- **Zero-inflation as a first-class property** — four catalog columns
  `zero_fraction_{s,u}_{L6,L8}`; **threshold 0.20, provisional**; scorer hurdle-scores a
  variable above threshold (ranks non-zeros within the active domain); aggregator emits
  `outside_active_domain` when a query's `weight_at_zero ≥ 0.90`.
- **Level matters** — scores and zero-fractions are level-specific; all current results are
  **L06**.

**2026-06-25**

- **Derived catalog rows** — rows with `source='Derived'` have no DB column and are skipped by `attach_values` (no SQL query) and the assembly dispatch loop (no branch routing). They are present in meta_df so the assembly can key to them by api_key and pull catalog provenance (`notes`, `position_notes`). Their values are produced by their synthesizing branch: B4 for `outlet_type` / `coast_fraction`; future branches for `elev_point`, `relief_range_m`, `relief_position`.
- **`kind` derivation in `load_catalog`** — flags detected by `_FLAG_API_KEYS = {'endorheic', 'coast_flag'}` (endorheic is `type='string'` in the catalog but consumed as a raw-integer B4 input); categoricals by `position_method='rarity_rank'` (logically coherent: rarity_rank is chosen specifically for class-membership variables with no intrinsic ordering; covers integer-coded class IDs like eco_id/wetland_class that map to text via lu_* views); all others continuous by type.

**2026-06-18**

- **Block 4 outlet_type** — for the *areal* product, `outlet_type` (4-class: exorheic non-coastal, exorheic coastal, endorheic inland, terminal sink) replaces separate `endorheic` 3-class and `coast_flag` outputs. `coast_fraction` emitted as a convenience scalar (method `flag_fraction`). `endorheic` standalone NOT emitted areally — recoverable from outlet_type. This revises the locked "endorheic as 3-class" decision **for the areal case only**; point signature is unaffected.
- **PERCENT_RANK population hygiene** — step2 scorer now excludes BasinATLAS nodata (-9999/NULL) from the ranked population via two-pass SQL (CTE `valid_pop` filters out nodata, then LEFT JOIN returns NULL for those basins). Affected vars: pct_clay, pct_silt, pct_sand, pct_clay_upstream, pct_silt_upstream, pct_sand_upstream, stream_gradient, slope_avg, slope_upstream (9 vars; ~1–5 pp score correction). Zero-aware vars already clean (PARTITION places nodata in partition 0). Production API and Explorer unaffected (return raw values, no PERCENT_RANK). Principle: **percentiles are computed over the variable's defined domain — nodata is out-of-domain exactly as zeros are for zero-aware vars.**

**2026-06-15**

- **Shared output envelope** — every block emits the same top-level fields: `variable`,
  `method`, `status`, `representative_score` (single headline score or null),
  `representative_raw` (native-unit headline or null), `n_basins`, `coverage_weight`. Plus
  method-specific detail columns: block 1 adds `spread`, `p10`, `p90`, `weight_at_zero`;
  block 2 adds `dominant_hybas_id`. Downstream comparison work reads `representative_score`
  uniformly across all variable types.
- **Block 2 method — dominant_basin** — discharge is cumulative; no mean, no area-weighted
  distribution. Dominant river = basin with highest `discharge_yr` in the buffer set.
  `discharge_annual`, `discharge_min`, and `discharge_max` all read from that one basin.
  `discharge_min > 0` → perennial; `= 0` → seasonal/intermittent. All discharge units are
  **m³/s**. Second-river detection deferred (needs upstream traversal; see register).
- **discharge_max re-typed** — catalog `typology_cluster` changed from `scale-dependent` to
  `network-topology` (2026-06-15). Step2 must be re-run to propagate to `step2_meta.tsv`.
- **scale-dependent → Block 1** — field-like vars (slope, karst, wetlands, cropland,
  groundwater, etc.) use the same area-weighted coherence recipe as `continental-gradient`.
  `scale_sensitivity` column in catalog already captures the quantitative sensitivity values.
- **local-anomaly (river_area) → Block 5 fallback** — deferred; see register.
- **hybas_id always int64** — `dtype={'hybas_id': 'int64'}` on every `read_csv`; never rely
  on pandas float coercion for basin IDs.

---

## Standing problems (the things that keep biting)

Brief here; fuller treatment in `docs/design/areas/areas_phase_outline.md` (background).

- **Incommensurable geometries** (basins / HYDE / LMR); LMR is often coarser than the query area.
- **Membership** — which basins count as "in" a polygon whose border doesn't follow basin lines.
- **The meaningless mean** — knowing *when* a summary lies (the coherence work).
- **Variable-type aggregation** — one recipe doesn't fit climate, discharge, anomalies, categoricals.
- **Two consumers** — a human viewing one area (map/distribution) vs a machine comparing many (a vector).
- **Global vs local frame** — the global percentile is commensurable but doesn't discriminate within an area.
- **Scale (L06 vs L08)** — verdicts and zero-fractions shift with support; current results are L06 only.

---

## Document map

| Document | Role | Status |
|---|---|---|
| `docs/edop/areas/AREAS_tracker.md` (this) | Current state, roadmap, locked decisions — the goto | **living** |
| `docs/design/areas/deferred_items_register.md` | Parked items + their triggers | **living** |
| `docs/edop/areas/areas_findings.md` | Coded observations (AF.n) — method behavior, signals, data properties | **living** |
| project session log | Chronological record of what happened each day | append-only |
| `docs/edop/areas/typology_review.md` | Zero-inflation / typing investigation | dated artifact |
| CC work orders, result TSVs | Implementation snapshots and evidence | dated artifacts |
| `docs/design/areas/areas.md` | Original design brief (provenance) | frozen background |
| `docs/design/areas/areas_phase_outline.md` | Early deliverables / challenges / decisions | frozen background |

---

## Changelog

- **2026-06-25** — Engine WO11b complete. `areal_signature(lat, lon, radius_km, conn, …)` added to engine.py. Build-once catalog cached per level. Full Timbuktu capstone (r=100 km, L06, Band T 1100–1200 CE): basin rows=51, Band T rows=321, total payload=372 rows. All 8 capstone tests PASS. Engine assembled and whole; v0.3 areal signature complete end to end. `assembly` branch.
- **2026-06-25** — Engine WO11a complete. `load_catalog(level, codebook_path)` added to engine.py. Reads live codebook → meta_df (59 rows: 54 sourced + 5 derived). Sourced rows reproduce step2_meta.tsv with one expected diff (endorheic.schema_key). `kind` derivation: _FLAG_API_KEYS override → flag; rarity_rank → categorical; else type-based. Derived rows (5): coast_fraction, elev_point, outlet_type, relief_position, relief_range_m — all derived=True, db_col=None. `attach_values` patched to skip derived rows. dispatch routing: B1=34, B2=3, B3=11, B4=2, B5=4. 7/7 PASS. WO1–WO10 suite still 34/34 PASS. `assembly` branch. WO11b (final assembly) is next.
- **2026-06-24** — Engine WO7 complete. `aggregate_b3(basin_set, matrix_df, class_id_df, meta_df, …)` added to engine.py. 6/6 acceptance tests PASS. Three determinations confirmed: (1) `representative_raw=None`; (2) lean carries `coherence`; detail carries modal summary + per-class mixture list with human-readable labels; (3) coherence rule: `modal_share >= 0.85` → `'concentrated'`, else `'mixed'`. eco_id special case: text labels from `matrix_df['ecoregion']` not `matrix_df['eco_id']` (integer col). Coherence split: 2 concentrated (lith_class, zone_name; modal_share=1.0), 7 mixed. `test_engine_wo7.py` strict PASS. Synthetics→catalog step (deferred register) must land before WO8.
- **2026-06-24** — Engine WO6 complete. `aggregate_b1(basin_set, matrix_df, meta_df, …)` added to engine.py. 5/5 acceptance tests PASS. Key fix during implementation: spread must be computed from un-rounded p10_raw/p90_raw (matching notebook's computation order); rounding p10/p90 first then subtracting causes 0.01 boundary error on ~7 vars. `representative_raw=None` confirmed throughout. Two-regime rows verified: B1 emits non-null mean for 2 concentrated two_regime vars (correct B6 input); 10 spread two_regime vars correctly emit null score. B6 post-pass ownership (score-nulling, modality) remains WO10.
- **2026-06-24** — Engine WO5 complete. `aggregate_b2(basin_set, matrix_df, raw_df, meta_df)` added to engine.py. 4/4 acceptance tests PASS. Three determinations flagged: (1) B2 rows carry both representative_score (dominant basin percentile) and representative_raw (m³/s); (2) perennial flag stored in detail on discharge_min row (engine enrichment not in frozen TSV); (3) n_units=9 = full buffer set — dominant basin identified via detail['dominant_hybas_id'], not by a separate n_contributing field.
- **2026-06-23** — Engine WO4b complete (diagnosis-only; no code change). WO4b surfaced a contradiction: engine returned 425 HYDE cells and an 11% higher grazing mean vs the TSV's 426 cells. Diagnosis confirmed: step3b notebook used rounded coordinates (LAT=16.8167, LON=-2.9833); engine test used WHG-resolved precise coordinates (16.76618535, -3.00777252). A ~4 km buffer shift changes the marginal cell set. Engine IS deterministic (verified: same result on two runs, DB unchanged). Fix: update test fixture to notebook coordinates. No weighting bug, no DB change, no geometry non-determinism. Regression now strictly PASS (float_tol=0.01) with no loose tolerances. Band T fixture coordinates documented in test file.
- **2026-06-23** — Engine WO4 complete. `make_row`, `project_row`, `assemble_payload`, `CAVEAT_TEXTS` added to engine.py. `aggregate_band_t` promoted from step3b_band_t.ipynb and re-wired to `make_row` (no behavior change to numeric outputs). Four contract pins implemented: Pin 1 status vocabulary (ok|outside_active_domain|no_data); Pin 2 caveat key-refs in rows + text in assemble_payload top-level dict; Pin 4 score_suppressed bool disambiguates null-because-two_regime from null-not-applicable. LMR caveat now applied to all LMR rows in `aggregate_band_t` (was missing from notebook's aggregate path). Spatial boundary effect noted: 1 HYDE cell at the 100 km buffer edge gives n_units=425 vs TSV's 426; high-value cell (grazing/rangeland ~7 km²) shifts mean ~10%; not a code error. `test_engine_wo4.py` 5/5 PASS. `make_row` is now the conformance target for WO5+ B1–B6 extraction.
- **2026-06-22** — Engine WO3 complete. `dispatch_variable(typology_cluster, kind)` added to engine.py. `zero_fraction` dropped from proposed signature (confirmed not a routing input). Coverage: 49/54 meta_df vars verified against step3_results.tsv methods; 5 surfaced — `river_area_upstream` (B5, deferred within B5; `EXTREME_VARS` hardcoded to `['river_area']`), `strata_code` (B3, excluded within B3; opaque codes), `ecoregion` (B3, deduped within B3; same col as eco_id), `endorheic` + `coast_flag` (B4, produce synthetic outputs `outlet_type`/`coast_fraction` — not standalone in results). Band T confirmed separate path (not in meta_df). Pre-contract extractions now complete. `test_engine_wo3.py` PASS.
- **2026-06-22** — Engine WO1 and WO2 complete. `scripts/edop/areas/engine.py` now has `resolve_buffer`, `weighted_quantile`, `diff_output` (WO1) and `_val_expr`, `rank_expr`, `two_pass_sql`, `attach_values` (WO2). Implicit-input hazard surfaced: `rank_expr` had a closure over notebook-scope `ZERO_FRACTION_THRESHOLD` — fixed as explicit parameter; `_val` (catalog coercion helper) not promoted (only needed for catalog loading, not attachment); `diff_output` null-normalization fix (None vs NaN treated as equivalent). `test_engine_wo2.py` regressions PASS on all three step2 TSVs. WO3 (dispatch) is next.
- **2026-06-21** — Block 7 complete (Band T gridded path). New notebook `step3b_band_t.ipynb`. ECC diagnostic routes HYDE (393 cells) to distribution and LMR (3.75 effective cells) to area-weighted collapse. `aggregate_band_t()` handles any span with no mode flag. Three output TSVs: primary (321 rows), wide (3427 rows), HYDE distributions companion (332 rows). HYDE 1950 cadence-transition artifact tagged with `hyde_caveat`. Two engine-assembly register items added: `n_units`/`unit_type` generalization and second coverage notion. Findings file `docs/edop/areas/areas_findings.md` created. All blocks 1–7 done; engine assembly is next.
- **2026-06-19** — Block 6 complete (modality refinement). 12 two_regime vars from 36 distribution-bearing rows; seam cross-check confirms Block 6 independently recovers the Niger/Sahara endorheic boundary. 2 concentrated vars (cropland_extent, temp_yr_upstream) found to be two_regime; scores suppressed. step3_results.tsv: 51 rows + modality column. step3_block6_regimes.tsv: 24 rows. Multi-fixture calibration item added to tracker "Later in the phase"; 5 related deferred items consolidated to point at it. Block 5 also complete (distribution_only: temp_min, temp_max; extreme: river_area). Catalog audit: actual untyped-continuous backlog not yet in step2: 4 vars (elev_point, relief_range_m, relief_position, reservoir_vol). Deferred register corrected.
- **2026-06-18** — Block 4 complete (outlet_type class_mixture + coast_fraction flag_fraction). PERCENT_RANK population hygiene fix applied to step2 Cell 6 (two-pass SQL, 9 affected vars); step3 re-run with corrected scores; pct_clay spread 27.89 → 29.24 pp, no verdict flips. step3_results.tsv: 48 rows. step3_block3_mixture.tsv: 22 rows (B3+B4 outlet_type mixtures). Block 5 (untyped fallback) is next.
- **2026-06-17** — Block 3 complete (9 categorical vars; strata_code excluded — opaque
  sub-zone codes, see register). step3_results.tsv: 46 rows. step3_block3_mixture.tsv written.
- **2026-06-15 (session 2)** — Block 2 complete (all 3 discharge vars, dominant basin
  hybas_id 1060564960). Block 2b resolved: scale-dependent → Block 1, local-anomaly →
  Block 5 deferred. discharge_max re-typed in catalog + step2_meta.tsv patched.
  step3_results.tsv: 37 rows, no duplicates, validated. Block 3 (categoricals) unblocked.
  Branch: `areas_step3`.
- **2026-06-15 (session 1)** — Tracker created; consolidates current state from `areas.md`
  and `areas_phase_outline.md` (now frozen background) and the step/block work through 06-14.
- **2026-06-13 / 14** — Steps 1–2 built and validated (incl. step-2 corrections). Step 3
  block 1 built; surfaced zero-inflation; typology review done and the `zero_fraction` columns
  added; block 1 re-run clean. Deferred-items register created.
  