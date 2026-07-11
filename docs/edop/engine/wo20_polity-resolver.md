# WO20 — Polity resolver and single-timestep Northern Song through the engine

**Branch:** continues on `engine_v0.4b` unless you'd prefer a new branch.
**Phase:** Areas · **Sub-phase:** neighborhoods (polity — final area type)
**Fixture:** Northern Song, single timestep (year TBD — confirm in Part 1)

## Goal

Add polity polygons as a first-class input to the engine, time-indexed at the resolver, and validate end-to-end on Northern Song at one timestep. This closes the Areas phase contract: every area type served by one resolve-and-serve pipeline, no bespoke side channels. Single-timestep only — the time slider, multi-timestep response shape, and cliopatria-style surface wiring are explicitly out of scope and will come later.

## Scope

In: time-indexed polity resolver, area-weighted polygon clipping, marginal-exposure diagnostic, polygon entry point to `areal_signature`, single-timestep N Song run, gate checks.

Out: time slider, multi-timestep payload shape, choropleth surface, L08 (deferred register), comparison to `cliopatria.html` numbers (anticipated divergence — "blessed deviation," do not treat as regression), Phase 4 correspondence work.

## Architecture

Three new public callables in `scripts/edop/areas/engine.py`, layered:

1. **`resolve_polygon(geom_wkt, level, conn) → basin_set DataFrame`** — geometry-first primitive. Returns columns `hybas_id`, `weight`, `basin_in_polity_fraction`, `overlap_area_km2`. The `weight` is `overlap_area / polity_area` (consistent with the buffer resolver's `overlap/buffer_area`); `basin_in_polity_fraction` is `overlap_area / basin_area` and is the WO15 cell-coverage analog, recorded per basin for the marginal-exposure diagnostic but not used as the weight.

2. **`resolve_polity(polity_name, year, level, conn) → (geom_wkt, basin_set, polity_meta)`** — wrapper. Looks up the Cliopatria row whose `name = polity_name` and `fromyear ≤ year ≤ toyear`, extracts geom, calls `resolve_polygon`. `polity_meta` carries the matched row's `name`, `fromyear`, `toyear` plus the year passed in, so downstream consumers can confirm which territorial phase was resolved.

3. **`areal_signature_polygon(geom_wkt, level, conn, *, bands, from_year, to_year, include_detail)`** — polygon-input entry point to the full engine. Probably implemented by extracting shared logic from `areal_signature` into a private `_areal_signature_from_basin_set(basin_set, geom_wkt, level, conn, ...)` that both buffer and polygon variants call, leaving `areal_signature` unchanged in signature and behavior. The aggregation path is identical to the buffer case — same attachment, same B1–B6, same B6 post-pass, same Band T. The only differences are the resolver and the `geom_wkt` passed to `aggregate_band_t` (the path WO14 already opened).

The `weight = overlap/polity_area` choice matters: weights sum to ≤1 over the polity (=1 if no shortfall), matching the buffer convention, so all downstream weighted-quantile and weighted-mean math is unchanged. Confirm one shared `ST_Area(ST_Intersection(A, B))` implementation is reused — the polygon-clips-basin geometry is the same primitive as basin-clips-cell from WO15, and there should be one place this lives.

## Marginal exposure diagnostic

A new per-payload field describing how much of the result rests on basins that are mostly outside the polity. Two reporting choices to settle in this WO:

- Per-basin, in `basin_set`: the `basin_in_polity_fraction` column, always present (range 0–1).
- Polity-level, in the payload's top-level dict alongside `coverage_weight`: `marginal_exposure` = sum of `weight` over basins with `basin_in_polity_fraction < 0.5`, plus an analogous figure at `< 0.2`. Both thresholds reported; the engine does not pick one — describe, don't decide.

This is distinct from the two coverage notions already in the deferred register (basin-renormalized vs. data-bearing-cell). Name it `marginal_exposure`, not `coverage_*`, to avoid loading that term further. Add a row to the deferred register noting the three coverage-like notions now in the schema.

## Fixture: Northern Song

Confirm in Part 1 by query against `gaz.clio_polities`:

- Exact `name` string (likely "Northern Song" but verify — Cliopatria naming conventions vary).
- The set of `(fromyear, toyear)` rows — N Song should appear as one or more territorial phases.
- Pick a single year inside one phase for the WO20 run. Suggest 1100 CE if a row covers it (round mid-N-Song, useful symmetry with the Timbuktu 1100–1200 Band T fixture). If 1100 isn't covered, pick the nearest year that is and note the choice.

Level: **L06 only.** L08 stays in the deferred register.

## Parts

**Part 1 — polity lookup.** Verify the name, list available `(fromyear, toyear)` ranges, pick a year, fetch the geom. Sanity-check the geom (`ST_IsValid`, area in km²). Save the geom_wkt to a notebook variable for downstream use. Document the chosen year.

**Part 2 — `resolve_polygon`.** Implement and unit-test the SQL. Acceptance:
- All basins with `ST_Intersects(basin.geom, polity.geom)` are returned.
- `weight = overlap_area / polity_area`, all in the same equal-area projection or via PostGIS geographic-area functions consistent with the buffer resolver.
- `basin_in_polity_fraction = overlap_area / basin_area`, range 0–1.
- `Σ weight ≤ 1`; shortfall = `1 − Σ weight` reported (the buffer's `shortfall` semantic carries over).
- Expected basin count: N Song at L06 should be on the order of dozens (transition doc says "dozens"); confirm.

**Part 3 — `resolve_polity`.** Thin wrapper. Acceptance: returns the polity row where `fromyear ≤ year ≤ toyear`; raises if no row matches; if multiple rows match, picks the most specific (or asks — flag if this case arises).

**Part 4 — `areal_signature_polygon`.** Extract shared logic, route polygon path through it. Acceptance: existing buffer regression suite (51 tests) still PASS. New polygon-path tests added against the N Song fixture (record current numbers as the contract, since there is no prior frozen TSV for polity — these become the regression baseline).

**Part 5 — N Song single-timestep run.** Call `areal_signature_polygon` with the resolved geom, L06, Band T span TBD (suggest 1050–1150 CE around the chosen year, or 1100 snapshot). Inspect the payload. Document:
- Basin row count.
- Distribution of `coherence` verdicts across B1 + B3 + B5 rows — N Song is expected to fire many `spread`/`mixed` verdicts (desert north / humid south). The test is that the heterogeneity surfaces in the engine output, not that the engine hides it.
- B6 modality outcomes — N Song should fire `two_regime` on several variables that the Timbuktu fixture fires unimodally; this is the engine independently discovering the territorial bimodality.
- B2 dominant basin — for a polity this large, the dominant-discharge basin is interesting and probably identifies a major Yellow River or Yangtze tributary. Worth noting.
- Marginal exposure values at both thresholds.

**Part 6 — gate.**
- Weight invariants hold (Σweight ≤ 1, all weights ≤ `basin_in_polity_fraction`).
- Payload structure matches buffer-case schema (same lean envelope; `n_basins`, `coverage_weight` semantics carry over; new `marginal_exposure` field present at top level).
- Spread verdicts fire — at least, say, 10 B1 rows with `coherence='spread'` (calibrate after first run).
- No engine collapse to a misleading scalar — every B1 variable that spans the polity reports p10/p90 honestly; the `representative_score` is emitted but the verdict makes its meaning explicit (the surface, not the engine, decides whether to display the headline).
- Existing buffer test suite PASS unchanged.

## Notes

- **No cliopatria-numerical-comparison.** Anticipated to diverge (zero-aware scorer, area-weighted clipping, etc.); flag as engine correcting preview, do not panic.
- **No per-basin matrix surfacing yet.** The lean payload doesn't carry the per-basin value matrix needed for choropleth. That's a response-shape question for the next WO; do not solve it here unless it falls out trivially.
- **The two temporal axes** (resolver timestep vs. Band T span) remain separable. WO20 fixes both to single values; multi-timestep is later.
- **Findings.** New observations to `areas_findings.md` under the new AF.WO20.\<m\> numbering scheme.

Ready for your review. If accepted, this goes to CC; first deliverable back should be Part 1 (polity lookup), before any code in `engine.py`.