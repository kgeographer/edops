# WHG Reconciliation API — `fclasses` does not compose with `bounds` (returns 0)

*Draft for the WHG repo / Stephen Gadd. Probed against the live service 2026-09-09.*

## Summary

In `POST /reconcile`, adding a feature-class facet (`fclasses`) to a query that
also has a spatial constraint (`bounds`, or `lat`/`lng`/`radius`) makes the query
return **zero results**. Without the spatial constraint, `fclasses` works
(e.g. with `countries`); without `fclasses`, the spatial constraint works. Only
the combination fails.

This blocks a very common use case: *"populated places / sites within this
bounding box."* We (EDOPS, edops.computingplace.org) resolve user-typed
settlement names to a location, constrained to the current map viewport. With
`fclasses` unavailable in that path, the results mix in administrative areas,
physical features (bays, rivers), metro-area labels, and points of interest.

## Reproduction

Endpoint: `POST https://whgazetteer.org/reconcile`
Auth: `Authorization: Bearer <token>`
Bounding polygon used below (northern Italy):

```json
{"type":"Polygon","coordinates":[[[7.0,44.0],[14.0,44.0],[14.0,47.0],[7.0,47.0],[7.0,44.0]]]}
```

| # | query object | result |
|---|---|---|
| 1 | `{"query":"Venice","mode":"fuzzy","bounds":<poly>}` | **12 results** (Venice/Venezia points, "Gulf of Venice", "Province de Venise", "Comune di Venezia", …) |
| 2 | `{"query":"Venice","mode":"fuzzy","bounds":<poly>,"fclasses":["P","S"]}` | **0 results** |
| 3 | `{"query":"Venice","mode":"fuzzy","bounds":<poly>,"namespaces":["whg","gn"]}` | **12 results** |
| 4 | `{"query":"Venice","mode":"fuzzy","bounds":<poly>,"namespaces":["whg","gn"],"fclasses":["P","S"]}` | **0 results** |
| 5 | `{"query":"Venice","mode":"exact","countries":["IT"],"fclasses":["P","S"]}` | **1 result** — Venezia (so `fclasses` composes fine with `countries`) |
| 6 | `{"query":"Pittsburgh","mode":"fuzzy","lat":45.44,"lng":12.33,"radius":200000,"fclasses":["P","S"]}` | **0 results** |
| 7 | same as 6 without `fclasses` | **8 results** |
| 8 | `{"query":"Venice","mode":"fuzzy","bounds":<poly>,"types":["aat:300008347"]}` | **1 result** — the AAT `types` facet *does* compose with `bounds` (non-zero), unlike `fclasses`; coverage is thin (only the TGN record carried that exact AAT type) |
| 9 | `{"query":"Venice","mode":"fuzzy","contained_in":["un:ita"],"fclasses":["P","S"]}` | **0 results** (also 0 with `bounds` added) |

So: `fclasses` + (`bounds` \| `lat`/`lng`/`radius` \| `contained_in`) → 0,
regardless of `mode`, and regardless of restricting `namespaces` to `whg`,`gn`
(rows 3–4). The parallel AAT `types` facet is *not* broken this way (row 8) — it
returns results, just with sparse coverage.

Batches were single-query POSTs of the form `{"queries":{"q1": <object>}}`;
also confirmed in multi-query batches.

## Hypothesis (Karl Grossner)

The index now spans tens of millions of records from many gazetteers, and only
GeoNames and the WHG-native store carry GeoNames-style feature classes
(P/S/A/H/…). If the spatial-filter path and the `fclasses` filter are ANDed and
the spatial path draws from (or the fclass field is null on) records that lack a
feature class, the intersection collapses to empty.

Row 4 argues against a pure namespace-coverage explanation: even with
`namespaces` pinned to `whg`,`gn` — the fclass-bearing sources — the combination
still returns 0. So it looks more like the two filters are not being combined on
the same result set (e.g. the spatial pre-filter runs on an index/shard where
`fclasses` is not applied, or vice versa).

## Impact

For "name + viewport" or "name + radius" lookups there is currently **no way to
restrict to populated places / sites**. Callers must either:

- accept administrative and physical-feature results in the candidate list, or
- omit the spatial constraint and filter client-side (defeats the point — the
  right nearby place may not be in the first N by string score), or
- fall back to `countries` + `fclasses` and lose sub-national precision
  (e.g. "Pittsburgh" without pinning to Pennsylvania).

## Requests

1. Make `fclasses` compose with `bounds`, `lat`/`lng`/`radius`, and
   `contained_in` (AND on the same result set) — the AAT `types` facet already
   behaves this way (row 8), so `fclasses` seemingly should too.
2. If that is infeasible for some sources, document which `namespaces` support
   `fclasses` and have the API apply `fclasses` where it can rather than zeroing
   the whole result.
3. Backfill GeoNames feature classes onto more of the index (or expose the AAT
   `types` mapping more widely), so `types` becomes a viable spatial place-type
   filter — its coverage is currently too thin to rely on (row 8).
