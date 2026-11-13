# WO-04 item 6: refactor plan for `aggregate_band_t`

2026-11-13. For review by Karl and Opus before any code is touched. Source: `scripts/edop/areas/engine.py:971-1189`.

## Purpose, and where GEDA fits

This refactor must leave every existing response exactly as it is; the regression baseline is how we prove that. It exists to prepare the ground for the registry. Today HYDE, LMR and eVolv2k are written inline in one function, each hard-wired. A registry that decides whether a source applies to a place and a span needs each source to be a unit it can sit in front of. So WO-04 pulls the three existing sources apart, puts the registry's in-or-out decision in front of each, and adds the `sources` block to responses; no existing output changes. The new regional data set, GEDA, is not part of WO-04: it has a registry entry (`status: stored`) and nothing queries it. In stage 3 it joins as a fourth source through the same gate, using the location test and coverage rule already written in its registry entry.

## What it is today

One function, about 220 lines, one caller: `_areal_signature_from_basin_set` (`engine.py:2349`), which serves all four public entry points (buffer, polygon/polity, single basin, basin ring). It is called only when Band T is requested and a span is given.

| Step | Lines | What it does |
|---|---|---|
| Geometry | 1003-1014 | Builds the query geometry as SQL text (a polygon from WKT, or a circular buffer around lat/lon) and computes its area once |
| HYDE | 1018-1095 | One SQL query (cell overlaps crossed with the epochs in the span, or the single nearest epoch when none fall in the span), then four variables per epoch through `_agg_hyde_b7`, each a row |
| LMR | 1097-1165 | Clips the span to `_LMR_RANGE`; one SQL query for the 2-degree cells touching the geometry (array slices); then three variables per year, area-weighted in Python, each a row |
| eVolv2k | 1167-1187 | Clips the span to `_EVOLV_RANGE`; one SQL query; one row per event |

Rows are appended in this order: HYDE (by year, then variable), LMR (by year, then variable), eVolv2k (by year). The order is kept as it is.

## State the blocks share

- The two geometry SQL strings and `buf_area_m2`. HYDE and LMR use all three; eVolv2k uses none.
- `from_year`, `to_year`, `resolver_year` (stamped into the HYDE and LMR histograms), and the connection.
- The `rows` list.

Nothing else is shared. HYDE, LMR and eVolv2k do not read each other's results, which is what makes the extraction safe.

## Proposed functions

A small container for the shared state, and one function per source. The code inside each moves as it is.

```python
@dataclass(frozen=True)
class _BandTQuery:
    buf_geom_sql: str
    buf_geog_sql: str
    buf_area_m2: float
    from_year: int
    to_year: int
    resolver_year: int | None
    conn: Any

def _band_t_query(lat, lon, radius_km, from_year, to_year, conn, geom_wkt, resolver_year) -> _BandTQuery   # lines 1003-1014
def _band_t_hyde(q: _BandTQuery) -> list[dict]        # lines 1018-1095
def _band_t_lmr(q: _BandTQuery) -> list[dict]         # lines 1097-1165
def _band_t_evolv2k(q: _BandTQuery) -> list[dict]     # lines 1167-1187

def aggregate_band_t(lat, lon, radius_km, from_year, to_year, conn, geom_wkt=None, resolver_year=None):
    q = _band_t_query(...)
    return _band_t_hyde(q) + _band_t_lmr(q) + _band_t_evolv2k(q)
```

`aggregate_band_t` keeps its name and signature, so its one caller is untouched. `_agg_hyde_b7` and `_agg_lmr_b7` stay where they are (`tests/engine` imports the first). The histogram stamp (`resolver_year`, `band_t_from`, `band_t_to`) is repeated in the HYDE and LMR blocks; I would leave it repeated, so each move stays literal.

## Order of work

1. eVolv2k (smallest, no geometry), then LMR, then HYDE. One commit each; after each: the regionality partition (the baseline) and the engine partition. If either fails, stop and report.
2. Then Part C, on the extracted functions: each `_band_t_<source>` asks the registry first and takes its covered years from it; `_LMR_RANGE` and `_EVOLV_RANGE` are removed.

## Where the registry plugs in (Part C and D), for review

- **Registry module location.** I propose `scripts/edop/areas/source_registry.py`, beside the engine. Routes already import the engine, so the public path can import it for Part D without a new direction of dependency.
- **The `permitted` option** goes on `aggregate_band_t(..., permitted=None)`, passed to each source function. The unit test (item 9) calls `aggregate_band_t` directly.
- **Reporting what was used or not applied (Part D).** The source functions need to report their decision (in, or out with a reason), and today `aggregate_band_t` returns only rows. Cleanest: each `_band_t_<source>` returns `(rows, decision)`, and `aggregate_band_t` returns `(rows, decisions)`. That changes the return type for the one caller, `engine.py:2349`, which I would update in the same commit. Alternative: leave the return type and collect decisions in a list the caller passes in. I prefer the tuple. **Decision for review.**

## Things the baseline does not cover

The four Band T baseline payloads (Timbuktu and Kyiv, spans 1236-1240 and 1300-1400, single basin) exercise: HYDE in-span and nearest-year rows, LMR, and eVolv2k with events. They do not exercise:

- a buffer or polity request with Band T (the buffer-geometry branch, `radius_km`, is not run by any baseline request);
- a span that includes 1950 (the HYDE 1950 caveat);
- a span with no eVolv2k events, or one outside LMR's years.

I propose capturing three new reference payloads from the code as it is now, before any extraction: a buffer with a span that includes 1950, a polity with Band T, and a span that falls outside LMR and eVolv2k (for example 2010-2020). These are additions, not a re-capture; existing files stay untouched. **Decision for review**, since the WO says no re-capture.

## Behaviour that looks odd (recorded, not fixed)

1. HYDE is never "outside its span". If no epoch falls in the span, it returns the nearest epoch (a span of 2100-2200 returns the 2025 epoch), flagged `hyde_nearest_year`. A registry gate that returns `outside_span` for HYDE would change this. The WO says HYDE's step rule stays in code, so for HYDE the gate must not suppress the nearest-epoch rule in this WO. **Question for Opus:** should the `sources` block report HYDE as `used` in that case?
2. LMR assumes at least one cell touches the geometry. The grid is global (16,380 cells), so this holds, but an empty result would divide by zero and fail on indexing.
3. All three queries are built by putting numbers and the WKT text into the SQL string. The inputs come from the resolver and range-checked parameters, not from free text, so I'd record it but not change it here.
4. LMR rows always carry `status: ok` and eVolv2k rows `coverage: None`, whatever the overlap; the status field cannot signal a partial overlap for those two.
