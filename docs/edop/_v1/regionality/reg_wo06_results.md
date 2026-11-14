# WO-06 results: one engine or two? Assessment of the signature paths

Spec: `reg_wo06_refactor-questions.md` (with its "Adjustments after review"). Assessment only: no code changed. Measurements were made on 2026-11-14 against the local database with scratch scripts (not in the repo; the comparison script is `compare_paths.py` in the session scratchpad). Estimates are mine, from reading the code; where uncertain, the uncertainty is stated.

## Part A: the facts

### A1. History

| Path | Written | Note |
|---|---|---|
| Basin path: `app/db/signature.py` | initial commit, 2025-12-31 | Phase 1: the original signature, one basin per point |
| `app/db/temporal.py` (LMR, eVolv2k) | 2026-04-11 | Band T, nearest LMR cell to the point |
| `app/db/hyde.py` | 2026-04-29 | Band T HYDE, cells whose centroid lies in the basin |
| Engine: `scripts/edop/areas/engine.py` | 2026-06-22 (Areas phase, closed 2026-06-30) | Resolver, aggregator, payload for areas of many basins; Band T computed on the query geometry |
| Buffer and area routed to the engine on `/api/signature` | 2026-09-13 and 14 (`scope=area` added; `/api/area` and `/api/areas` made internal) | `scope=buffer` and `scope=area` return the engine payload, rows renamed to `variables`, plus a `meta` block |
| Registry on the engine path | 2026-11-13 and 14 (WO-04, WO-05) | The basin path got only the `sources` block, rebuilt in the route |

So the divergence is historical: the basin path is the original code; the engine was written six months later for areas and later exposed on the public route. Nothing was ever decided to keep them different.

### A2. Callers

In the repo (from code):

| Caller | Route and scope | Bands | Band T? |
|---|---|---|---|
| Sandbox, second request (Analysis and Seasonality tabs; `sandbox.html`) | `/api/signature?scope=basin` | ABCE | no |
| Workbench (`workbench.html:2411`) | `/api/signature?scope=basin&level=8` | default (ABCDE) | no |
| WHG profile scripts (`scripts/edop/whg/wo04_fill.py`, `wo10_profiles.py`) | `/api/signature?scope=basin` (also `/api/areas`) | ABCDE | no |
| `scripts/edop/sig/civ_centers_compare.py` | `/api/signature?scope=basin` | ABCE | no |
| Docs generators and the cheat-sheet example script | `/api/signature`, `/api/areas` | A-E | no |
| `routes_sandbox.py` (internal routes) | imports `get_signature`, `get_temporal_context`, `get_hyde_land_use` | | |
| Sandbox page, Polities tab and first request | `/api/areas` (engine) | any | yes |

Every in-repo caller of `scope=basin` asks for bands A-E; none asks for Band T. The baseline's only public-signature payload is also bands ABCE, so the public basin path's Band T has no baseline reference.

External traffic is on the production server only. For Karl to run over SSH (read-only):

```sql
SELECT src, endpoint, scope, bands, count(*) AS n, min(ts)::date AS first, max(ts)::date AS last
FROM public.query_log
WHERE endpoint = '/api/signature'
GROUP BY 1, 2, 3, 4
ORDER BY n DESC;
```

Karl ran it on 2026-11-14 (the log starts 2026-10-21; `src=api` is untagged, so it includes Karl's own tests):

| scope | bands | calls | first | last |
|---|---|---|---|---|
| basin | ABCDE | 23 | 2026-10-21 | 2026-11-10 |
| basin | ABCDET | 8 | 2026-10-21 | 2026-10-21 |
| basin | T | 3 | 2026-10-28 | 2026-10-29 |
| basin | A | 1 | 2026-10-25 | 2026-10-25 |
| area | ABCDE | 4 | 2026-10-21 | 2026-10-22 |
| area | ABCDET | 1 | 2026-10-21 | 2026-10-21 |
| buffer | A | 1 | 2026-10-28 | 2026-10-28 |

41 calls in three weeks. Twelve asked for Band T (11 on `scope=basin`, 1 on `scope=area`), all between 10-21 and 10-29, clustered around the v0.4.2 deploy (2026-10-29), which fits the project's own testing; the table has no caller identity, so that is an inference. The only calls since 10-29 are `basin` ABCDE (last 11-10). The `user_agent` column would separate test tools from others (a second query, not run).

### A3. Differences, by band

Classes: **P** presentation, **S** shape (a documented response contract), **C** computation (two answers to the same question).

**Bands A-E** (checked by running both paths on the same basin, level 6, at Timbuktu, Tbilisi, Kyiv and Bruges):

| Difference | Class |
|---|---|
| Values: of the variables both paths return, 31, 28, 33 and 28 numeric values were compared (the four places); **none differed** (tolerance 1e-6). Both read the same BasinATLAS columns. | none |
| Basin path only (18): elevation point (`elev_point`), relief (`relief_range_m`, `relief_position`), eight seasonality variables (`pre_concentration`, `pre_peak_month`, `pre_mm_monthly`, `seas_phase_offset`, `tmp_concentration`, `tmp_peak_month`, `tmp_dc_monthly`, `tmp_seas_amp`), four the engine omits by design (`gdp_avg`, `human_dev_idx`, `pnv_shares`, `river_area_upstream`), and three that the engine returns in another form (`coast_flag`, `endorheic`, `ecoregion`) | P (variable set) |
| Engine only (4): `coast_fraction`, `outlet_type`, `zone_name`, `land_cover_name` (class labels and fractions) | P |
| Response shape: `signature_bands.A..E.items[{key, label, value}]` and `profile_summary` against `rows[]` with score, method, coherence, status | S |
| Percentile, coherence, status and method fields: engine only (the basin path returns raw values) | P |
| Notes for BCE queries on bands C and D (F8.5): basin path only | P |

**Band T:**

| Difference | Class |
|---|---|
| LMR: nearest 2 degree cell to the query point (basin path) against area-weighted mean over the cells that overlap the basin geometry (engine) | C |
| HYDE: whole cells whose centroid lies in the basin, summed (basin path) against overlap-fraction-weighted sum (engine) | C |
| HYDE: the basin path's `basin_area_km2` is the summed area of the cells it counted, not the basin's area, so its `_pct` fields are relative to that | C (a defect) |
| HYDE: unweighted `percentile_cont` p10 and p90 for cropland and grazing only (basin path) against weighted p10, p90, sd and effective cell count for all four (engine) | C / P |
| HYDE with no step inside the span: none returned (basin path) against the nearest step, flagged (engine) | P (policy, documented) |
| eVolv2k: same data; basin path filters events at 5 Tg by default and adds count, sum and years-since-last-major; engine returns all events, none of the summaries | P |
| GEDA: absent from the basin path, and silent in its `sources` | gap |
| Band T span: the basin path takes a span; public buffer and area take one year (a route rule); `/api/areas` takes a span | P (policy) |
| Shape: `signature_bands.T = {lmr_status, pdsi_series[], air_series[], prate_series[], volcanic_*, hyde_land_use{epochs[]}}` against `rows[]` plus `caveats` and `temporal` | S |
| `sources` block: rebuilt in the route from the span and what was returned (basin path) against emitted from the decisions (engine) | implementation |

### A4. Size of the change in values (Band T, span 1300-1400, level 6)

LMR, basin path (nearest cell) against engine (overlap-weighted), per year:

| Place | Variable | Mean abs diff | Max abs diff | Series sd | Mean diff / sd |
|---|---|---|---|---|---|
| Timbuktu | PDSI / air / precip | 0.0037 / 0.0013 / 0.0005 | 0.013 / 0.005 / 0.002 | 0.110 / 0.096 / 0.016 | 0.01 / 0.00 / 0.02 |
| Tbilisi | PDSI / air / precip | 0.049 / 0.005 / 0.010 | 0.127 / 0.016 / 0.039 | 0.475 / 0.132 / 0.045 | -0.04 / -0.02 / 0.12 |
| Kyiv | PDSI / air / precip | 0.030 / 0.010 / 0.010 | 0.092 / 0.032 / 0.022 | 0.312 / 0.198 / 0.045 | -0.07 / 0.02 / -0.22 |
| Bruges | PDSI / air / precip | 0.0011 / 0.0003 / 0.0002 | 0.003 / 0.001 / 0.001 | 0.201 / 0.168 / 0.029 | 0.00 / 0.00 / 0.00 |

The LMR differences are small against the series' own spread: the mean absolute difference is at most about 10% of the series sd (Tbilisi PDSI), usually under 5%; the systematic offset is at most 0.22 sd (Kyiv precipitation).

HYDE at 1300, engine sum over basin sum (the values differ because the two cell rules select different cells: 45 against 80 cells at Timbuktu, 363 against 448 at Tbilisi, 502 against 600 at Kyiv, 49 against 77 at Bruges):

| Place | Cropland | Grazing | Pasture | Rangeland |
|---|---|---|---|---|
| Timbuktu | 1.00 | 1.11 | 0 | 1.11 |
| Tbilisi | 1.03 | 1.02 | 1.01 | 1.19 |
| Kyiv | 1.00 | 1.01 | 1.00 | 0 |
| Bruges | 0.82 | 0.99 | 0.99 | 0 |

Most HYDE totals agree within about 3%; single variables differ by up to 19% (Tbilisi rangeland, Bruges cropland at 0.82).

HYDE at level 8, where basins are small: in a random sample of 200 L8 basins (mean area 736 km2), the basin path's centroid rule finds no cell at all for **15 (7.5%, roughly plus or minus 2 percentage points)**, so those basins get no HYDE; the overlap rule finds none for 1 (0.5%). This is a defect of the basin path at L8, not just a difference.

Bands A-E: no change in values (see A3). Unification would change how A-E variables are named and shaped for callers only if the presentation layer were not kept.

## Part B: the options

Estimates are hours including review, from reading the code; they have not been tested by doing the work.

| Option | What changes | Estimate | Risk | Tests and baselines | What callers see |
|---|---|---|---|---|---|
| 1. Full unification now | Every scope on the engine. Engine gains the 18 basin-path variables (elevation lookup with its fallback chain, relief, seasonality, four omitted variables, three renamed forms); a presentation layer rebuilds `signature_bands`, `profile_summary` and the top-level fields | 40-70 h (plus or minus 50%) | High: touches the Sandbox's Analysis and Seasonality tabs (they read the basin response), the WHG profile pipeline, and the catalog names | New baseline references for the public basin response (none cover Band T today); UI tests and browser checks; schema JSONs and docs regenerated | A-E values unchanged; shape unchanged if the presentation layer is faithful; Band T values change slightly; GEDA everywhere |
| 2. Band T now, A-E later | The basin path's LMR and HYDE come from the engine's source functions on the basin polygon (the engine already accepts a polygon); GEDA arrives; eVolv2k can stay as is (same data); a mapping layer keeps the existing `signature_bands.T` shape; the `sources` block comes straight from the decisions | 12-20 h (plus or minus 40%) | Moderate: values change slightly (A4); the shape mapping needs care (HYDE `_pct` needs the true basin area, which also fixes the defect) | New baseline references for public basin Band T; tests for the mapping | Band T values shift by the amounts in A4; HYDE appears for the 7% of L8 basins that lost it; GEDA appears under a new key; nothing in A-E changes |
| 3a. Stopgap: report GEDA honestly | The basin path runs `check()` for GEDA and reports the real outcome in `sources`; needs a new reason (for example `not_served_on_route`) for places inside the footprint | 2-3 h | Low | A few tests | `sources` stops being silent; no GEDA values |
| 3b. Stopgap: its own GEDA block | The basin path calls the engine's `_band_t_geda` on the basin polygon and adds a key | 4-6 h | Low | Baseline reference and tests | GEDA values on `scope=basin`; the rest unchanged |
| 4. Defer all | A page documenting the two paths, their differences (this results file is most of it) and why | 3-5 h | None | None | Nothing changes |

## Part C: the cost of delay

| What grows | Assessment |
|---|---|
| Each further regional source (LBDA and others) | On the engine path a new source costs one work order, as GEDA did. On the basin path each source needs its own code and a mapping, or is missing from `scope=basin`. With two paths this is paid twice, and the registry cannot help the basin path until it uses the engine's blocks. This grows with every source added. |
| Breaking change after 1.0 | Real in principle: after 1.0, moving `scope=basin` Band T onto the engine changes its values for public callers. Before 1.0 it is free: v1 is a new site and v0.4.2 stays frozen. In size, the change is small (A4) and no in-repo caller requests Band T from the basin path. The production `query_log` shows 41 `/api/signature` calls in three weeks, 12 with Band T, none since 2026-10-29, and the Band T calls cluster around deploy days. In practice the breaking-change cost is close to nil. |
| Two sets of docs, tests and baselines | The baseline has no public Band T payload, so the basin path's Band T is currently untested by it. Two schema JSONs and two shapes already exist. The cost is steady, not growing quickly. |
| Knowledge | The reasons are clearest now and are recorded here (A1, A3). Cheap to preserve with Option 4; hard to recover later. |
| Anything cheaper later | A-E unification may become cheaper or unnecessary if the v1 dashboard no longer uses the Sandbox's Analysis and Seasonality tabs: the second request that depends on the basin response would go. Band T has no such effect: it does not get cheaper by waiting, and each new source adds to it. |

## Part D: recommendation

**Answers.**
- **(a) Warranted?** Split. For bands A-E the paths do not compute differently: every shared variable has identical values in the four places tested. The differences are the variable set, names and shape, which are presentation and contract, defensible and not a computation problem. For Band T there are real computation differences (LMR cell choice, HYDE cell rule), a defect (HYDE fails for about 7% of L8 basins, and `basin_area_km2` is the wrong quantity), and a gap (GEDA, silent). Small in value for LMR, up to about 19% on single HYDE variables.
- **(b) Too big for now?** Full unification: yes, 40-70 h at high risk, for little gain in A-E. Band T alone: about 12-20 h, moderate risk, and no in-repo caller depends on the basin path's Band T. The stopgap is 2-3 h.
- **(c) Does delay add cost?** For A-E, little. For Band T, yes, but mostly through duplicated work: each regional source added is paid twice or missing from `scope=basin`. The breaking-change cost at 1.0 is, on the evidence of the query log, close to nil in practice (Part A2).

**Recommendation.** Option 2 for Band T, before 1.0, as its own work order (a WO-07 candidate), and leave A-E alone, documented (Option 4). Concretely:

1. Schedule the Band T move onto the engine before the 1.0 deploy if the v1 plan has room: about 2 to 3 working days. It fixes the L8 HYDE gaps and the HYDE area defect, brings GEDA and every later regional source to `scope=basin` for free, and replaces the route's reconstruction of `sources` with the engine's decisions.
2. If it will not fit before the deploy, do the 3a stopgap now (2-3 h) so `sources` is honest and record the Band T move as the first roadmap item after 1.0. Waiting costs little in breakage (the query log shows almost no external use, and none of Band T lately) and costs duplicated work for each regional source added meanwhile; on this evidence the urgency is lower than the breaking-change argument alone suggested.
3. Do not unify A-E. Put "unify A-E and retire the duplicated variable code" on the v1 roadmap, to be decided with the dashboard (it depends on whether the Analysis and Seasonality tabs survive). The catalog-completeness work order should settle the payload names together with item 1 here (the catalog's LMR `api_key_s` is the basin path's naming).
4. Write the short "two paths" page for the next developer from A1 and A3 (Option 4's content), whichever of the above is chosen.

This partly agrees with Karl's inclination: the broad refactor belongs on the roadmap, and nothing here affects Karl's own research use after February. The narrower Band T move is the exception, because delay adds cost to it.

**What is not known.** Who made the 41 logged calls (the log has no caller identity; `user_agent` would separate test tools from others); what the WHG profile scripts do with A-E values beyond reading them (not affected if A-E is left alone); the UI tests were not run for this assessment; the L8 HYDE figure is from a sample of 200 (plus or minus about 2 points); all hour estimates are unproven, Option 1's the least certain.
