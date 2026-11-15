# dash WO-01 results: the summary at Level 08

2026-11-14. Spec: `dash_wo01_summary-Level08.md` (Fable). Branch `dashboard`, cut from `v1`. Nothing in the app, the templates, the stored profiles or the engine was changed; Level 06 output was not touched. Scripts: `scripts/edop/dashboard/dash_wo01_time_stages.py`, `dash_wo01_eco_counts.py`. Scratch output (gitignored): `output/edop/dashboard/dash_wo01/` (`stage_timings.csv`, `fill_timings_l6.csv`, `eco_counts.csv`). Local machine, local database, one process.

## What was done, and what was not

Karl's goal for this WO, in his words: find out what it would cost to provide Level 08 profiles in the way Level 06 ones are to be provided. Item 1 (cost) was done. Item 2 (point and basin units) was done in part, as needed to read the cost. **Items 3 (the generator's wording at Level 08) and 4 (how often the two levels disagree) were not started.** One extra measurement was made that the WO did not ask for: the number of ecoregions per basin at each level.

## Item 1: generation time

### What a run needs

The generator (`wo04_fill.py`) works from a place. For one place it makes two requests to the local app (`/api/signature` and `/api/areas`), reads a number of values straight from the database, and reads three precomputed tables: neighbour pairs, flow between neighbours, and ring values. **Those three tables exist only for the test sample** (neighbour pairs and flow: 1,740 rows over 307 core basins; ring values: 90,907 rows over 315 core basins). They have never been built for all Level 06 basins, and at Level 08 they would be built for 190,675. Ring values were built by one ring call per basin (WO-06: 311 basins in 2,374 s, 7.6 s each).

No point stage (point elevation, the point's ecoregion, river distances) is part of a stored basin profile and none is timed here.

### Measured per basin, mean seconds (20 Level 08 basins, and the Level 06 basin at the same point)

| Stage | Level 06 | Level 08 |
| --- | --- | --- |
| Signature for one basin (bands A to E) | 1.25 | 1.00 |
| Ring call: signature for the core and each neighbour (what built the ring table) | 9.04 (median 8.12, p90 13.1, max 16.8) | 6.26 (median 5.81, p90 7.83, max 10.3) |
| Ring resolve (neighbours, shared border) | 0.021 | 0.077 |
| Land cover shares | 0.003 | 0.072 |
| Climate zone | 0.002 | 0.070 |
| Lake share | 0.001 | 0.067 |
| Coast | 0.046 | 0.091 |
| Ecoregion shares, as written (`wo08_units.eco_shares`) | 1.45 (median 0.036, p90 3.3, max 17.2) | **35.5 (median 34.9, range 34 to 40)** |
| Wiki and OneEarth link lookups | under 0.001 | 0.003 (timed with a fixed ecoregion id, so only indicative) |
| Neighbours per basin | mean 6.7, median 6 | mean 5.6, median 5 |

Template fill at Level 06, six test places: `fill_units` 0.001 to 0.004 s. `build_facts` (the two local requests plus lookups) 1.65 to 2.07 s per place; its cost is the same signature work as above.

### Why the ecoregion query costs 35 s at Level 08

`EXPLAIN ANALYZE` on one Level 08 basin: the planner starts from the 847 ecoregion polygons (about 290 KB each) and probes `basin08`'s spatial index once for each, applying the `hybas_id` test afterwards as a filter (826,469 buffers read). Neither `public.basin06` nor `public.basin08` has an index on `hybas_id`: the only index on each is the primary key, on `id`. At Level 06 the table is about a twelfth the size, so the same plan costs 0.04 s at the median.

The same query written with the basin picked first (a `MATERIALIZED` CTE) returned identical ecoregions and shares on the two basins compared, and took 0.093 to 0.117 s on seven of eight basins and 1.29 s on one (mean 0.254 s, n = 8; **corrected 15 Nov:** a second model timed 100 random basins in one batch at 0.51 s per basin at Level 08 and 0.68 s at Level 06, so the mean of 8 understated a tail of large and coastal basins; the table below uses 0.51 s). The cost is the plan, not the geometry. Nothing was changed.

The same missing index explains the 70 ms land cover, zone and lake lookups at Level 08 (2 ms at Level 06): a lookup by `hybas_id` takes 87 ms. An index would probably bring them down; that was not tested.

### Estimates for a full run (one process; sample of 20; sums of the means above)

| Level 08, 190,675 basins | Per basin | Total |
| --- | --- | --- |
| As built (ring call per basin; ecoregion query as written) | 42.0 s | about 93 days |
| As built, ecoregion query with the basin picked first | 7.1 s | about 16 days |
| Each basin's signature computed once and reused for its neighbours; ecoregion query fixed | 1.9 s | about 4.2 days |
| The same with an index on `hybas_id` (estimate: lookups fall to about 0.01 s) | 1.6 s | about 3.5 days |

Level 06, 16,397 basins, same method: as built, 10.5 s per basin, about 2.0 days; signature reuse with the ecoregion query as written, 2.8 s per basin, about 13 hours (the signature alone is about 6 hours).

Template fill for 190,675 basins: about 6 minutes.

What the estimates rest on: the ring call recomputes every basin's signature once for itself and once as a neighbour of each adjacent basin (about 6 to 7 times in all; the ring call costs 7.2 times a single signature at Level 06 and 6.3 times at Level 08); reuse means computing and storing each basin's signature once. The flow classification (pure Python over `next_down`) was not timed. Storage was not measured. **Corrected 15 Nov:** the 29 to 36 KB of a stored place record includes template segments, unit traces and notes, so the 0.5 to 0.6 GB and 5.5 to 7 GB I first derived from it were on the wrong basis; a second model estimates a facts store at tens to a few hundred MB per level (an estimate, not tested). Production server speed and parallel workers are untimed.

## Item 2: point units and basin units (partly done)

Confirmed from the generator code and templates, for the units on the opening sentence:

| Unit | What it describes | Stored per basin? |
| --- | --- | --- |
| S1.1b elevation at the point | The place | No: needs the point |
| S1.2a the point's ecoregion | The place | No: needs the point |
| S1.2c the basin's majority ecoregion, when it differs | The basin | Yes |
| S1.5a, S1.5b the basin's lowest and highest elevation | The basin | Yes |
| S1.4 other ecoregions the basin takes in | The basin, **relative to the point**: the rule skips the point's ecoregion, the signature's, and the largest by area, and keeps those covering 10% or more | Ingredients only (see below) |
| S7.3 coast near the point (`basin_coast`) | The place; S7.2 (the basin touches the coast) describes the basin | Split |
| S8.3 moved point, S8.point where the point came from | The place | No |

Not yet checked unit by unit: S3.1 and S3.3 (river distances; the river lookup is called with the point's latitude and longitude, which supports the WO's reading), and the other sections.

**Consequence.** A stored basin profile cannot be one finished paragraph, because the Setting sentence mixes place and basin facts and S1.4 depends on the place. What can be stored per basin is the basin's ingredients: its values, its basin-only sentences, and the full list of its ecoregions with their shares. At request time the point's elevation and ecoregion are looked up, the point's ecoregion is removed from the stored list to give the S1.4 sentence, and the text is assembled. The point lookups were not timed here. This is a design consequence for the Dashboard and the WHG endpoint, not something this WO tested.

## Extra: ecoregions per basin (300 Level 08 basins, the Level 06 basin at the same point; unweighted)

| | Level 06 | Level 08 |
| --- | --- | --- |
| Ecoregions with any area: mean (median, max) | 2.16 (2, 7) | 1.32 (1, 4) |
| Basins with one ecoregion at 10% or more | 50% | 80% |
| Two | 39% | 18% |
| Three or more | 11% | 2% |
| S1.4 ("also takes in parts of …") would speak | 37% | 18% |

The S1.4 test is approximate: it skips the point's ecoregion and the largest by area, where the generator also skips the signature's own `eco_id`. Counts are unweighted by area, population or place density, and the points are interior points of random basins, not real places. The ecoregions of the neighbouring basins (the ring context Karl described) were not counted.

## Needs attention going forward

1. **Index on `hybas_id`** for `basin06` and `basin08` (none exists; primary key is `id`). It affects every per-basin lookup at Level 08 and would be a database change on the server too. Not made.
2. **The ecoregion share query** (`wo08_units.SHARES_SQL`) is 35 s per Level 08 basin as written; the basin-first form is 0.1 to 0.5 s with identical results (two basins compared here; 100 Level 06 basins by the second model, no difference above 1e-6). Not changed (WO proviso). A full pass is about 27 hours for Level 08 and 3 hours for Level 06 on one connection, by the second model's timing.
3. **Signature reuse.** A bulk run needs each basin's signature stored once and the ring built from the store, not the ring call as it works now. This is a design item for any bulk run.
4. **Items 3 and 4 of the WO** are open. At Level 08 the median basin has 5 neighbours (6 at Level 06); the ring rules need 3 neighbours with a value for any comparison and 5 for "all but one", so those sentences will speak less often. Not tested.
5. **Neighbour ecoregion context** (whether neighbouring basins touch other ecoregions) is not in the current templates as far as the code shows; counting it would be cheap once per-basin shares exist.
6. **Estimates are local and single-process**, from 20 timed basins; the Level 06 ecoregion timing has a long tail (one basin 17 s), so the Level 08 mean may hide outliers. Production speed, parallel workers and storage size are untested.
7. **Level 08 ring table, pair table and flow table** do not exist; the generator also hard-codes Level 06 in `wo04_fill.py` (the two requests, `basin06`), `wo06_rings.py` and `wo10_profiles.py` (signature button, monthly block), and the per-basin helpers. None was changed.

## Review by a second model (15 Nov; figures not verified by me)

A Fable agent was given the open question and this repo, and measured on its own (read-only). It saw `profile-store-design-fable.md`, which is in the repo, so its design is not independent of Fable's. Its findings that bear on this record:
- Level 06's 1.4 s fixed cost per signature is the full-table `PERCENT_RANK` (1.40 s for 1 basin, 1.39 s for 10, 1.95 s for all 16,397). A `basin06_scores` table built like `basin08_scores` removes it.
- Level 08's signature time is the missing `hybas_id` index: about a dozen table scans of about 70 ms each inside `attach_values`. With an index the Level 08 signature would fall to about 0.1 to 0.2 s (its estimate, not measured).
- Neighbour pairs by `ST_Touches` cost 2 to 5 ms per basin (about 6 minutes for Level 08); flow from `next_down` is pure Python.
- A bulk build need not use the one-request-at-a-time path: running `single_basin_signature` in-process with a scores table is estimated at 30 to 40 minutes for Level 06, and about a day for Level 08 (mostly the ecoregion pass).
- Request time, Tbilisi: point to basin under 10 ms, point ecoregion under 1 ms, rivers 0 to 10 ms, coast 15 ms, external point elevation 0.40 to 0.45 s per call.
- River names depend on `gaz.osm_river_lines`, which holds only the 122 rivers met in the samples.
- Nothing in `app/` serves `/whgmodal`; only `/profiles` reads the stored JSON.
