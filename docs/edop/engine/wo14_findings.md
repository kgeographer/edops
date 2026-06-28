# WO14 — Single-basin run + v0.3 comparison: findings

**Fixture:** 16.8167, −2.9833 (Timbuktu), L06, 1100–1200 CE
**Notebook:** `notebooks/edop/areas/single_basin_comparison.ipynb`
**Branch:** engine_v0.4b
**Date:** 2026-06-27

---

## Part 1 — Resolver + single_basin_signature run

**Result:** PASS.

`resolve_single_basin` returns a 1-row DataFrame: hybas_id=1060551560, weight=1.0.
Shortfall = 0.0 structurally — the query IS the basin; there is no boundary to miss.
`single_basin_signature` mirrors `areal_signature` without `radius_km`;
`neighborhood.type=basin`, `n_units=1`, `level=6`.

**Payload:** 373 rows — 52 basin rows (Bands A–E) + 321 Band T rows.
Method breakdown: area_weighted 34, class_mixture 10, distribution_only 3,
dominant_basin 3, extreme 1, flag_fraction 1, global_forcing 10,
grid_areal_collapsed 303, grid_areal_distribution 8.

**Band T un-deferred:** `aggregate_band_t` extended with `geom_wkt=None` parameter.
When provided, uses `ST_GeomFromText(wkt, 4326)` as the query area instead of a
circular buffer — backward-compatible; all 51 prior tests still pass.
Basin polygon fetched via `ST_AsText(geom)` for the resolved hybas_id and passed
directly. This closes the Band T deferral for the single-basin path.

**reservoir_vol fix:** The only codebook variable with a `_u` column and no `_s` column.
Fix is an upstream-only coalesce in `load_catalog._emit`: when `su=='s'` and `col`
is None but `col_u` exists, use `col_u`. This preserves the s/u semantic distinction
(not a codebook edit) and routes `reservoir_vol` to B5 as `distribution_only`.

**Same-basin precondition confirmed:** v0.3 `/api/signature` returns the same
hybas_id (internal id=1478 → hybas_id=1060551560). The two engines are looking at
identical source data.

---

## Part 2 — Four-bucket comparison

**Result:** 0 MISMATCH, 0 UNEXPLAINED. All bucket 1 match; all bucket 3 explained;
bucket 4 transformations verified or explained.

### Bucket 1 — 17 checks, all match

**Raw-vs-raw (4 vars):** discharge_yr, discharge_max, discharge_min, river_area — exact
match to 3 decimal places. At n=1 the dominant basin IS the query basin; trivially
correct, but confirms the dominant_basin and extreme extraction paths degrade cleanly.

**Categorical (8 vars):** biome, freshwater_ecoregion_name/class, lith_class,
pnv_majority, wetland_class, zone_name, land_cover_name — all exact label matches.

**Score-vs-rank spot-check (5 vars):** aridity (Δ=0.0003), temp_yr (Δ=0.0034),
precip_yr (Δ=0.0044), dist_sink (Δ=0.0040), pop_density (Δ=0.0023). All < 0.01 pp.

*Key finding on the spot-check:* the validation SQL must mirror `engine.rank_expr`
exactly — zero-aware PARTITION BY for vars with `zero_fraction ≥ 0.20`, plain
PERCENT_RANK otherwise, with -9999 guard and NULLS LAST in both branches. A naive
subquery PERCENT_RANK diverges for zero-aware vars (aridity Δ=1.48, dist_sink Δ=6.59,
pop_density Δ=7.12 before the fix). Those deltas are not bugs — they reflect the
intentional v0.4 scorer improvement over v0.3's naive global percentile.

Also: the WHERE clause must be in a subquery, not on the outer query — filtering before
the window function restricts the window to one row, returning PERCENT_RANK=0 always
(first failure mode encountered).

*Schema note:* for score-vs-rank rows in `wo14_comparison.tsv`, `v3_value` holds the
native raw value and `v4_value` holds the v0.4 percentile score — not directly comparable
numbers; `delta` records the engine-vs-DB spot-check delta, not v3 minus v4. Correct
but requires the `check` column to interpret.

### Bucket 2 — 7 v0.4-only items (all expected)

Trust layer fields: coherence, modality, weight_at_zero, score_suppressed, caveat,
distribution, representative_score. No v0.3 counterpart; sanity-checked in Part 3.

### Bucket 3 — 13 v0.3-only absences (all explained)

Point/profile constructs (7): elev_point, elev_source, elev_dataset, elev_resolution_m,
relief_range_m, relief_position, profile_summary — areal engine has no point geometry.
The v0.3 values are visible in the TSV and are coherent: elev_point=267 m,
relief_range_m=22 m (very flat — Inner Niger Delta), up_area=382,644 km².

Deferred or skipped (4): river_area_upstream (B5 deferred), gdp_avg and human_dev_idx
(both in _SKIP_API_KEYS), geom_geojson (polygon not included in row payload).

Structural (1): `id` (internal DB row ID; v0.4 uses hybas_id in neighborhood).

Interesting values surfaced: gdp_avg=2,285, human_dev_idx=0.442 (low, Mali-consistent),
river_area_upstream=107,497 km² (substantial — Niger River system).

### Bucket 4 — 4 transformations (2 match, 2 explained-difference)

**outlet_type synthesis:** endorheic=0, coast_flag=0 → "Exorheic, non-coastal". Matches.
First real test of the B4 synthesis against its raw flag inputs — passes.

**coast_fraction:** coast_flag=0 → coast_fraction=0.0. Exact match.

**eco_id:** v0.3 carries numeric id=71 + text label; v0.4 carries text label only.
Labels match ("Inner Niger Delta flooded savanna"). Numeric ID loss: expected, noted.

**pnv_shares:** EXPLAINED-DIFFERENCE — architectural, not a bug.
v0.3 `signature.py` had bespoke code reading all `pnv_pc_*` percent-coverage columns
to build the within-basin PNV class distribution: {Desert: 16%, Open shrubland: 51%,
Grassland/steppe: 33%}. v0.4 engine is codebook-driven (one db_col per variable);
`pnv_shares` is flagged `raw_type='object'` with no db_col and skipped. v0.4
`class_mixture` correctly aggregates the per-basin majority label across basins — right
for the multi-basin case — but at n=1 shows only "Open shrubland: 100%".
Modal class matches (Open shrubland = pnv_majority). Within-basin grain is lost.
Two deferred items added to register: "pnv_shares within-basin distribution" and
"multi-column variable gap in engine/codebook model."

---

## Part 3 — n=1 degeneracy assertions

**Result:** PASS — all assertions hold. 52 basin rows, 100+ individual checks.

Six properties checked, all clean:

1. **coherence = concentrated** on every row that carries it (43 rows: 30 area_weighted,
   10 class_mixture, 3 distribution_only). Rows without coherence (dominant_basin,
   extreme, flag_fraction) correctly carry `coherence=None`.

2. **modality ≠ two_regime** on all 38 rows that carry modality — all report `unimodal`.
   This confirms the B6 two_regime path is unreachable at n=1 (as required: no regime
   structure is detectable from a single data point).

3. **score_suppressed = False** on all 52 rows. No false suppressions.

4. **weight_at_zero ∈ {0.0, 1.0}** on all 34 area_weighted rows that carry it.
   Notable values that read 1.0: `cropland_extent`, `karst`, `karst_upstream`,
   `permafrost_extent` — all structurally absent at this Inner Niger Delta / Sahel
   fixture (no karst, no permafrost, minimal cropland). The 1.0 values are correct;
   at n=1 the basin is either entirely at zero or it isn't.

5. **coverage = 1.0** for all 51 rows with `status='ok'`. (1 row has
   `status='outside_active_domain'` — see below.)

6. **class_mixture: modal_share=1.0, n_classes=1, len(mixture)=1** for all 10
   class_mixture rows (biome, zone_name, eco_id, freshwater_ecoregion_name/class,
   land_cover_name, lith_class, pnv_majority, wetland_class, outlet_type). Each
   correctly reports 100% one class when there is only one basin.

**Incidental finding — `outside_active_domain` at n=1:** `cropland_extent` has
`status='outside_active_domain'`, `coherence=None`, `representative_score=None`,
`weight_at_zero=1.0`. This is the degenerate-at-floor guard firing correctly: the
basin's zero_fraction ≥ 0.20 and weight_at_zero=1.0 (the whole basin is at the
cropland floor). The engine correctly refuses to score a zero-inflated variable when
the entire query area is at zero. `modality='unimodal'` is still emitted (set before
the domain guard) — a minor sequencing artifact, not a problem.

This is the cleanest possible degeneracy result: the aggregator has no pathological
behavior at the n=1 boundary.

---

## Part 4 — Band T reference checks

### LMR — sub-resolution collapse

**Result:** Correct behavior confirmed; stats within tolerance.

`distribution='collapsed_subresolution'` on all 101 LMR rows — ECC correctly
identified the basin (~3,688 km²) as sub-resolution relative to the 2°×2° LMR grid
(~47,700 km²/cell at 16°N). n_units=3: the basin polygon clips 3 LMR cells; the
engine area-weight-collapses them rather than using a single cell as v0.3 did.

Series stats vs v0.3 single-cell reference (tolerance 0.01):

| var | stat | v0.3 | v0.4 | Δ |
|---|---|---|---|---|
| pdsi | mean | −0.0393 | −0.0404 | 0.0011 ✓ |
| pdsi | min | −0.3804 | −0.3776 | 0.0028 ✓ |
| pdsi | max | +0.2768 | +0.2712 | 0.0056 ✓ |
| air | mean | −0.1246 | −0.1252 | 0.0006 ✓ |
| prate | mean | −0.0153 | −0.0151 | 0.0002 ✓ |

The small deviations are mechanically explained: v0.4 returns a 3-cell area-weighted
mean; v0.3 extracted purely from cell (16.0, −2.0). The neighboring cells are
geographically proximate and climatically similar, so their weight contribution
shifts the series slightly but does not change the signal direction.

### HYDE — epoch-for-epoch check

**Result:** Distribution stats agree closely; n_units diverges significantly (80 vs 45).

Per-epoch comparison for cropland and grazing (1100 and 1200 CE):

- **p10**: essentially identical (Δ ≤ 0.0003 for all four cases)
- **p90**: near-identical for cropland (Δ ≤ 0.0003), slightly wider for grazing (Δ 0.14/0.16)
- **sd**: near-identical for cropland (Δ ≤ 0.0006), larger divergence for grazing (Δ 0.34/0.37)
- **mean/cell**: cropland ~3% off; grazing ~7-8% off

The distribution shape is well-preserved for cropland (near-zero coverage; p90/sd match
to within 1%). Grazing diverges more in mean and sd — indicating the extra 35 boundary
cells carry higher grazing values than the 45 interior cells.

**n_units = 80 vs v0.3 n_cells = 45.** This is the central discrepancy. v0.3
`hyde.py` uses `ST_Within(ST_Centroid(hc.geom), b.geom)` — centroid-in-polygon;
only cells whose center falls inside the basin are included. v0.4 uses `ST_Intersects`
(any polygon contact), also capturing edge cells whose centroid lies outside the basin
but whose polygon overlaps it. The 35 additional cells are boundary cells; they have
similar p10/p90 to the interior (distribution shape preserved) but pull the mean and
sd toward higher grazing values. At this fixture the difference is modest, but at a
basin straddling a sharp land-use boundary, edge cells could carry substantially
different values and bias the mean. The most principled fix is area-weighted intersection
(weight each cell by fractional overlap with the query polygon). **Added to deferred register.**

### Volcanic — global_forcing count

**Result:** Not an exact invariant as the design doc expected; all 4 large events present.

v0.3 returned `volcanic_events=4`; v0.4 returns 10 rows. The 4 large events (vssi > 5
Tg S) are present in v0.4: years 1108 (19.16), 1171 (18.05), 1182 (10.05), 1191
(8.53). The 6 additional v0.4 rows have vssi 0.29–3.68 — small eruptions filtered by
v0.3's display threshold.

v0.3 applied a VSSI threshold (~5 Tg S) before counting; v0.4 returns all eVolv2k
rows in the span (no threshold). This is a design difference, not a bug. v0.4's
approach is arguably better — it gives researchers the full record and lets them apply
their own significance filter. The exact-invariant claim in the WO14 design doc was
wrong; the correct framing is "all events v0.3 considered notable are present in v0.4."

---

## Part 5 — Findings synthesis

### What WO14 confirms

**The single-basin path works.** `resolve_single_basin` → `single_basin_signature`
runs without error, returns the correct basin, and produces a well-formed 373-row
payload. `neighborhood.type=basin`, `n_units=1`, `shortfall=0.0` — all structurally
correct.

**Bucket 1 (17/17 match).** Every directly comparable quantity between v0.3 and v0.4
agrees: raw values for discharge and river_area are exact; categorical labels match;
scorer spot-check confirms v0.4 percentile ranks match the DB to within 0.005 pp.
This validates the scorer end-to-end at the single-basin boundary: the zero-aware
two-pass SQL, the NULLS LAST guard, the log_percentile variant — all produce DB-verifiable
results.

**Bucket 3 (13/13 explained).** Every v0.3-only field has a known reason for absence.
No accidental drops.

**Bucket 4 — B4 synthesis verified.** outlet_type and coast_fraction are derived
correctly from endorheic and coast_flag raw inputs — the first real end-to-end test
of the B4 synthesis path against its source data.

**Part 3 — degeneracy is clean.** All six properties hold at n=1 without exception:
concentrated coherence, unimodal everywhere, no score suppression, binary weight_at_zero,
full coverage, 100%-one-class mixtures. The `outside_active_domain` guard on
`cropland_extent` (zero_fraction ≥ 0.20, weight_at_zero=1.0) fires correctly —
the engine refuses to score a zero-inflated variable when the query is entirely at
the floor.

**LMR ECC confirmed.** `distribution='collapsed_subresolution'` on all 101 annual
rows; series stats within 0.006 of v0.3's single-cell reference. The 3-cell collapse
introduces a small but mechanically explained deviation.

### What WO14 surfaces

**Zero-aware scorer is a scorer improvement over v0.3**, not a regression. Variables
with `zero_fraction ≥ 0.20` (aridity, dist_sink, pop_density) score differently in
v0.4 than v0.3 because v0.4 ranks non-zeros within the positive subpopulation.
The v0.4 result is more principled; v0.3's naive global percentile compressed the
non-zero range by including the zero pile. The comparison spot-check must replicate
`rank_expr` exactly to serve as a valid oracle.

**pnv_shares architectural gap.** v0.3 held the within-basin PNV grid-cell distribution
(3-class split for Timbuktu); v0.4 holds the cross-basin label mixture (100% one class
at n=1). Both are architecturally coherent for what each engine does, but the within-basin
information is genuinely lost. Two deferred items added: within-basin PNV distribution
and the general multi-column variable gap in the codebook model.

**HYDE cell-selection.** ST_Intersects returns 80 cells vs v0.3's 45. Distribution
shape (p10/p90) is preserved well; mean and sd diverge ~3-8% for grazing. The correct
long-term fix is area-weighted intersection (weight each cell by fractional overlap),
not a boolean flag. Added to register.

**Volcanic threshold.** The exact-invariant claim in the WO14 design doc was wrong:
v0.4 returns all 10 eVolv2k rows in the span, not just the 4 v0.3 filtered at vssi > 5.
The 4 large events are present. v0.4's approach (no threshold, full record) is better
for research; the display layer should handle significance filtering, not the engine.

### Deferred items added during WO14
- pnv_shares within-basin distribution
- Multi-column variable gap in engine/codebook model
- HYDE cell-selection: ST_Intersects vs area-weighted intersection
