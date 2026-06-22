# AREAS — Phase 3 tracker

**This is the living source of truth** for the Areas phase: current state, the step roadmap,
and locked decisions. If any other Areas document disagrees with this one about *where things
stand*, this one wins.

- **Location:** `docs/edop/areas/AREAS_tracker.md`
- **Last updated:** 2026-06-21
- **Maintained:** updated by CC at session end (part of the pre-commit ritual) and whenever a
  decision is locked; read at the start of each step and each phase gate.
- **Rule:** when a decision is locked or a gap is resolved, remove the corresponding
  forward-looking note (in "You are here", block table, or deferred register) **in the same
  edit** — never leave a resolved item as an open question elsewhere in the file.

---

## You are here

Building the aggregation **engine** (resolver → aggregator) along the buffer-neighborhood path,
using the **Timbuktu 100 km / L06 buffer** as the working fixture. Steps 1–2 complete. Step 3
(aggregator) is underway: **all blocks 1–7 done; engine assembly is next.**

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
| — | Engine assembly + response shape (aggregate + distribution + coverage + neighborhood echo) | todo |

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
  