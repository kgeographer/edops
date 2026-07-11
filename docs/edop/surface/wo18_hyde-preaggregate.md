# WO18 — HYDE pre-aggregation + route swap

**Branch:** `surf_wo18` — notebook + table build + route swap + test update.
**Type:** Data artifact + code change. Two gates: notebook accept (table built, timing
confirmed), then code accept (route swap; 93/93 tests pass).

## Goal

Pre-aggregate `temporal.hyde_basin06_weights` across all 128 HYDE steps × 4 variables into
`temporal.hyde_basin06_steps (hybas_id, step_idx, cropland_frac, grazing_frac, pasture_frac,
rangeland_frac)`. Then swap `/api/hyde/values` to query the pre-aggregated table. Per-request
drops from 2.67s (WO17 finding) to an indexed point-lookup, expected <200ms.

## Why

WO17 proved that area-weighted aggregation via `hyde_basin06_weights` is correct (r=0.902 vs
centroid 0.689) but the per-request join — 2.82M crosswalk rows × 2.21M `hyde_cells` rows for
the array access — costs 2.67s. That's 8× slower than the centroid route and fails the go/no-go
for slice-reactive repaint. The crosswalk itself is correct; the problem is re-running the
expensive join on every request. Pre-aggregating runs that join once per step and stores the
results flat. Per-request becomes `SELECT hybas_id, cropland_frac FROM ... WHERE step_idx = N`
— an indexed scan of 16,281 rows, no array access, no spatial join.

## Build (notebook)

1. **Table schema** — `temporal.hyde_basin06_steps`:
   ```
   hybas_id       bigint    NOT NULL
   step_idx       smallint  NOT NULL   -- 0-based; matches temporal.hyde_times
   cropland_frac  real                 -- cropland km² in basin / sub_area; null if no coverage
   grazing_frac   real
   pasture_frac   real
   rangeland_frac real
   PRIMARY KEY (hybas_id, step_idx)
   ```
   Fractions are `frac_full` (÷ `sub_area`) — the WO17 denominator decision. Null means no
   land-cell coverage (116 basins), not zero cropland; null paints transparent.

2. **Build loop** — for each of the 128 `step_idx` values, run one aggregation query against
   the crosswalk:
   ```sql
   SELECT w.hybas_id,
          SUM(h.cropland[{pg_idx}]  * w.overlap_frac) / NULLIF(MAX(b.sub_area), 0) AS cropland_frac,
          SUM(h.grazing[{pg_idx}]   * w.overlap_frac) / NULLIF(MAX(b.sub_area), 0) AS grazing_frac,
          SUM(h.pasture[{pg_idx}]   * w.overlap_frac) / NULLIF(MAX(b.sub_area), 0) AS pasture_frac,
          SUM(h.rangeland[{pg_idx}] * w.overlap_frac) / NULLIF(MAX(b.sub_area), 0) AS rangeland_frac
   FROM temporal.hyde_basin06_weights w
   JOIN temporal.hyde_cells h  USING (cell_id)
   JOIN public.basin06        b USING (hybas_id)
   GROUP BY w.hybas_id
   ```
   Each iteration inserts into `hyde_basin06_steps` with the current `step_idx`. All four vars
   in one pass per step — not four separate passes. Commit in batches (every N steps, or all at
   end) — your call; report which and why.

3. **Indexes** — after the full insert:
   ```sql
   CREATE INDEX ON temporal.hyde_basin06_steps (step_idx);
   CREATE INDEX ON temporal.hyde_basin06_steps (hybas_id, step_idx);
   ```
   The route queries `WHERE step_idx = $1` (returns all 16,281 basins for that step). A
   `step_idx` index alone is sufficient for the route; the composite is for any future
   per-basin lookups.

4. **Build time** — expected ~128 × 2.67s ≈ 6 min for the insert loop. Report actual.
   Build all 128 steps. `temporal.hyde_times` has 10 BCE steps (step_idx 0–9,
   year_ce −10000 to −1000); HYDE 3.4 covers 10,000 BCE to 2025 CE, so the arrays are
   populated. All 128 costs ~6 extra seconds over CE-only and keeps the table complete.

## Validation (notebook)

- **Per-request query time** — time `SELECT hybas_id, cropland_frac FROM temporal.hyde_basin06_steps WHERE step_idx = N` for a CE step. Must be <200ms. Report actual.
- **Value agreement with WO17** — for a sample of basins (say 500), compare `hyde_basin06_steps` values at step 20 (1000 CE) against the WO17 on-the-fly crosswalk query. Values should agree within floating-point tolerance (real precision). Report max absolute difference; if any exceed 1e-5, investigate.
- **Unit guard** — assert max fraction ≤ 1.0 across all vars and all steps (or a representative CE-era sample). Should hold by construction given WO17's passed guard, but confirm.
- **Row count** — should be 16,281 basins × 128 steps (or × 118 if CE-only). Report actual.

## Route swap (code change, after notebook accept)

Update `/api/hyde/values` in `app/api/routes.py`:

- **Floor-snap year → step_idx** — same as current: `WHERE year_ce <= year ORDER BY year_ce DESC LIMIT 1`.
- **Values query** — replace the centroid join with:
  ```sql
  SELECT hybas_id, {var}_frac AS value
  FROM temporal.hyde_basin06_steps
  WHERE step_idx = %(step_idx)s
  ```
  where `{var}` is the safe-var name (`cropland`, `grazing`, etc.). Column name is `{var}_frac`.
- **Return shape** — identical to current: `{"var": var, "year": year, "actual_year": actual_year, "values": {hybas_id: fraction}}`. No change to callers.
- **Null handling** — null fractions (116 basins with no land coverage) should remain null in the dict, not coerced to 0.

The `_HYDE_SAFE_VARS` allowlist stays; column name construction is `f"{var}_frac"` — validate that the constructed name is in the expected set, not freeform.

## Accept gate

**Gate 1 — notebook:**
- Table built; build time reported and acceptable.
- Per-request query time <200ms (vs 2.67s WO17 baseline).
- Value agreement with WO17 crosswalk confirmed within floating-point tolerance.
- Unit guard passed; row count correct.

**Gate 2 — code:**
- Route swap in place; 93/93 existing structural tests pass.
- `TestHydeValuesRoute` tests pass against the new route (values will differ from centroid; update any hardcoded value assertions to use the new area-weighted values, or relax to range checks).

## Explicitly not in this WO

- **No change to `sandbox_v2.html`** — the frontend already calls `/api/hyde/values`; the route swap is transparent to it. Slice-reactive repaint continues to work unchanged.
- **L8** — L6 only. The crosswalk and steps tables are both L6. An L8 parallel is a separate data artifact by the same construction.
- **BCE range** — the route floor-snaps to the lowest available step; BCE queries are a separate API concern (noted in CLAUDE.md as open). The steps table may include BCE steps (your call above), but the route contract doesn't change.
- **LMR per-year values API** — separate deferred item; not touched here.
- **State model pass (C1–C7)** — unresolved from WO15 audit; not touched here.

## Deliverables

- `notebooks/edop/surface/wo18_hyde_preaggregate.ipynb` — build loop, timing, validation.
- `temporal.hyde_basin06_steps` table + its indexes.
- Updated `app/api/routes.py` — `/api/hyde/values` queries pre-aggregated table.
- `docs/edop/surface/wo18_findings.md` — build time; per-request time; value agreement; row count; unit guard; any surprises.

## Findings

`docs/edop/surface/wo18_findings.md`.
