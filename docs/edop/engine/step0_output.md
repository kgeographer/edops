# Step 0 — Function inventory (engine assembly pre-read)

Generated from: step1_buffer_resolver, step2_value_attachment, step3_aggregation, step3b_band_t.
Purpose: map what exists across the four notebooks before any code moves, so assembly starts
with a clear picture of what to promote, what to consolidate, and what to write from scratch.

---

## Function table

E = engine piece-part · S = scaffolding

| Function | Notebook · Cell | One-line role | E / S | Role-slot | Collision flag |
|---|---|---|---|---|---|
| `_val(v)` | step2_value_attachment · Cell 4 | Coerce a catalog DataFrame cell to string or None (NaN/strip guard) | S | fixture-specific setup | — |
| `_zf(v)` | step2_value_attachment · Cell 4 | Coerce a catalog cell to float `zero_fraction` or None | S | fixture-specific setup | — |
| `_val_expr(db_col, method)` | step2_value_attachment · Cell 6 | Build the ORDER BY expression inside PERCENT_RANK for a given `position_method` (regular vs. log) | E | shared utility — scoring | — |
| `rank_expr(db_col, method, zero_fraction=None)` | step2_value_attachment · Cell 6 | Build monolithic PERCENT_RANK SQL with nodata guard and optional zero-aware (PARTITION BY) variant | E | attachment — basin values matrix | — |
| `two_pass_sql(db_col, alias, method, table, ids_clause)` | step2_value_attachment · Cell 6 | Build filtered-CTE PERCENT_RANK SQL for vars where the basin table has nodata rows (valid population excludes −9999/NULL) | E | attachment — basin values matrix | — |
| `weighted_quantile(scores, weights, q)` | step3_aggregation · Cell 6 | Weighted quantile via sorted cumulative weights + linear interpolation | E | shared utility — computation primitive; used by B1 and B5 | — |
| `detect_modality(var, spread)` | step3_aggregation · Cell 27 | Detect unimodal vs. two-regime distribution shape; return label, evidence dict, seam note | E | aggregation branch — B6 modality refinement | — |
| `_weighted_quantile(vals, weights, q)` | step3b_band_t · Cell 11 | Weighted quantile (identical logic to `weighted_quantile`; duplicate with underscore prefix) | E | shared utility — computation primitive; used by B7 HYDE | — |
| `_agg_hyde(df, var_col)` | step3b_band_t · Cell 11 | Area-weighted mean + p10/p90/sd for one HYDE variable (distribution path) | E | aggregation branch — B7 (HYDE distribution) | ✓ `p10`/`p90`/`sd` in km²/cell — native units, not percentile points |
| `_agg_lmr(df, var_col, scale=1.0)` | step3b_band_t · Cell 11 | Area-weighted mean for one LMR variable (collapse path; no distribution detail) | E | aggregation branch — B7 (LMR collapse) | — |
| `_row(variable, method, agg, units, unit_type, year, …)` | step3b_band_t · Cell 11 | Build one shared-envelope row for Band T (includes `n_units`/`unit_type`/`year`/`epoch_year`/`lmr_caveat`) | E | response-shaper — Band T only | ✓ `n_units`/`unit_type` diverges from B1–6 `n_basins`; `coverage_weight` = covered-area / buffer-area (cell fraction), not renormalized basin weights |
| `aggregate_band_t(from_year, to_year)` | step3b_band_t · Cell 13 | Full Band T aggregation — HYDE (distribution), LMR (collapse), eVolv2k (global forcing) over a temporal span; no mode flag | E | aggregation branch — B7 (Band T gridded) | ✓ Same `coverage_weight` divergence as `_row`; embeds HYDE `step_idx` lookup and LMR `pg_idx` calculation internally |

---

## Surprises

**1. `weighted_quantile` is defined twice.** `weighted_quantile` (step3) and `_weighted_quantile`
(step3b) are identical in logic. Assembly must consolidate them into one shared utility.

**2. Almost no functions in the two largest notebooks.** Step3 has 27 cells and only 2 named
functions. Every block (B1 classify, B2 dominant-basin, B3 categorical mixture, B4 outlet_type,
B5 extreme) is procedural inline code with no wrapper. `rank_expr` / `two_pass_sql` generate SQL
strings but the full attachment pass (assembling `pos_df`, `class_label_df`, `class_id_df`,
`flag_df`) is also procedural. The engine will need to write function wrappers around essentially
all of it.

**3. `detect_modality` is a closure.** It reads directly from notebook-scope variables `joined`
and `raw_df` rather than accepting them as parameters. It won't be portable as written — the
engine version will need a signature like
`detect_modality(scores, weights, spread, endorheic_set)`.

**4. The resolver has zero function abstraction.** Step1 is entirely raw SQL in Cell 3; step2
Cell 3 copies that exact SQL inline. The most fundamental building block of the engine —
"point + radius → weighted basin set" — has no function to move.

**5. `_row()` is a partial response-shaper.** It covers the Band T envelope (`n_units`,
`unit_type`, `year`) but has no counterpart for Blocks 1–6. B1–6 envelope rows are assembled
inline as ad-hoc dicts with different fields (`n_basins`, `spread`, `weight_at_zero`,
`dominant_hybas_id`).

---

## Skeleton roles with no function yet

Assembly must write these from scratch.

| Skeleton role | Gap | Suggested new function |
|---|---|---|
| resolver — basin set | Step1 Cell 3 SQL inline; duplicated verbatim in step2 Cell 3 | `resolve_buffer(lat, lon, radius_km, level, conn, epsilon)` → `DataFrame[hybas_id, weight]` |
| dispatch | Typology-cluster routing is implicit in cell-level `meta_df` filters; no routing function exists | `dispatch_variable(typology_cluster, zero_fraction, kind)` → block label |
| attachment — basin values matrix | `rank_expr` / `two_pass_sql` generate SQL; the full pass (pos_df + labels + flags) is procedural across Cells 4–7 of step2 | `attach_values(basin_set, meta_df, conn, level, table, view)` → `(matrix_df, class_id_df, raw_df)` |
| response-shaper — Blocks 1–6 | B1–6 rows are inline dicts with a different schema than `_row()` (B7) | A unified `make_row(variable, method, status, …)` that handles the `n_basins` / `n_units` fork |
| attachment — Band T temporal indexing | HYDE `step_idx` lookup and LMR `pg_idx` calculation embedded in `aggregate_band_t` and step3b Cell 10; no standalone function | Could be extracted as `resolve_temporal_indices(from_year, to_year, conn)`, or left inside `aggregate_band_t` if assembly keeps it monolithic |

---

## Naming note

`rank_expr` and `_val_expr` are SQL-generator helpers that sit between the attachment step
and the scoring concept. Closest label is *shared utility (scoring)*, but they occupy a
sub-step (SQL-string construction) the skeleton didn't name. Call the slot
**attachment — score SQL builder** for precision.
