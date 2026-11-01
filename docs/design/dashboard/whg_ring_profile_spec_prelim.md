# Preliminary spec: basin-ring environmental profile for the WHG place modal

**Status: preliminary, draft 2026-11-01. Not agreed. Revisit before work starts.** Items marked *(verify)* are assumptions about the code that have not been checked.

## Purpose

A WHG place record opens a modal with an "environmental profile": what EDOPS knows about the place's basin, and how it relates to the basins immediately around it. A WHG-tuned endpoint calls a new engine function for this. Working name: `GET /api/whg/profile?lat=&lon=&level=6` (path not decided).

## Principles

1. **Distributions, not aggregates.** No means, no suppression, no weights. The payload keeps each basin's own value (WO-02: aggregation caused most of the buffer anomalies).
2. **The rule layer derives the relations.** The engine returns per-basin values; "where the core sits among the set", counts above and below, agreement of classes and so on are computed by rules from those values (as in `scripts/edop/dashboard/wo02_rules_*.py`). Watch performance; measure before optimising.
3. **Payload-only rules.** Statements read the payload; per-variable meanings (direction, meaning of zero, units, area covered) come from a glossary built from the data-source docs (Karl is writing those).
4. **Caveats are decided by rules**, never left to prose generation.

## Input

`lat`, `lon` (a WHG place's point); `level` (6 default; 8 optional); `bands` (default A–E; the modal may want a subset, open); optional `from_year`/`to_year` for Band T on the core.

## Resolution

Reuse `resolve_basin_ring(lat, lon, level, conn)`: the core basin plus its first-order adjacent basins, each with area, shared border length and bearing. A point in no basin (issue 1 in `wo02_results.md`: coastal points a few metres offshore; oceanic islands have no basins) returns a structured error with a reason (`no_basin`, nearest basin distance if any), not a bare 404. Snap tolerance is an open decision.

## Engine function (new)

`basin_ring_profile(lat, lon, conn, level=6, bands=None, from_year=None, to_year=None)`

- Compute the per-basin percentile matrix **once for the set** (core and neighbours), not N+1 single-basin calls *(verify that the single-basin path can run over a set)*.
- **Returns**
  - `core`: the existing single-basin payload shape (rows with `variable`, `method`, `status`, `representative_score`, `representative_raw`, `units`, `weight_at_zero`, `coverage`, `detail` for the core only).
  - `neighbours[]`: `hybas_id`, `area_km2`, `bearing`, `shared_border_km`, and a **compact** `rows` list (variable, method, status, score, raw, class label; no histograms) to keep the payload small.
  - `ring`: neighbour count, level, centre id; geometry optional (off by default).
  - `bands`, `temporal`, `caveats` as today.
  - **No aggregate rows, no shortfall.**
- **Band T:** core only in v1 (a basin's own geometry). LMR cells are 2 degrees wide, so neighbours touch the same few cells and would repeat one value (WO-02, Band T). Ring-union Band T is open.
- Rough size: core about 43 KB, neighbours about 5 to 10 KB each (compact), so about 100 to 150 KB for a typical ring, before gzip *(estimate, verify)*.

## Rule layer (new family, "core and surroundings")

Run the existing Position, Empty-cells and Coverage rules on the core unchanged. New statements over core plus neighbours, all descriptive:
- where the core's percentile ranks among the N+1 basins ("2nd highest of 7");
- how many neighbours rank above or below ("5 of 6 below");
- the range of the neighbours' values, as values, not quantiles (5 to 10 values is too few for p10 to p90);
- class variables: how many neighbours share the core's class;
- how many neighbours have a value ("5 of 6"; statuses vary per basin) and how many are at zero;
- ring size and geometry notes (a coastal core has no neighbours seaward).

Constraints from WO-02: zero-aware variables need Position's wording (a neighbour's percentile 0 means zero here); neighbours resemble the core (spatial dependence), so most differences are small and statements should not manufacture contrasts; variables with an unknown zero fraction (`reservoir_vol`) are excluded from rankings.

## Endpoint response

Core payload, neighbours, and the **generated statements** (id, text, stat) so a prose layer or the modal can consume facts directly. Rules run server-side in Python *(performance to measure)*.

## Performance and caching

Target a few seconds. A basin's signature depends only on (`hybas_id`, level, bands), so cache per basin: neighbours are reused across places. The existing nginx `/api/` cache (6 h) covers repeats.

## Not decided or out of scope

Aggregated ring values; per-neighbour Band T; second-order rings; polygon scope (`scope=area`); WHG authentication and rate limits; the LLM prose layer and BYOK (separate); mapping WHG place ids to points.

## Open questions

1. Snap tolerance and the response for coastal and island points.
2. Default bands for the modal (Band D is heavily discounted).
3. Core-only Band T, or also the ring union.
4. Whether L8 is offered as a second profile.
5. Exact compact fields for neighbours.
6. Rules server-side or client-side.
7. Which place identifier the endpoint takes, and the cache key.

## Existing pieces

`resolve_basin_ring` and `basin_ring_signature` (`engine.py:2546, 2635`: today a centre plus per-neighbour single-basin signatures); `/api/basin/ring` (topology); the rule modules and master table from WO-02.
