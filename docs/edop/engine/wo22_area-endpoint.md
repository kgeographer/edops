# WO22 — `/area` endpoint stub (polity-by-name+year)

**Branch:** `engine_v0.4b`
**Phase:** Areas · **Sub-phase:** endpoint wiring
**Depends on:** WO20 (`areal_signature_polygon`), WO21b (histograms in `detail`) — both done.

## Goal

Wire a FastAPI `/area` endpoint as a thin front door over the existing `areal_signature_polygon` callable. Polity-by-name+year input only, this cut. No new engine logic. This is the prerequisite for the new sandbox surface to exercise the polygon path.

## Governing constraints

- **Purely additive.** `/signature` and every existing route keep their signature and behavior unchanged. No edits to `signature.py` or the point-path engine.
- **Existing sandbox tests stay all-green.** `sandbox.html` is public; nothing here touches it. App test suite (`tests/ --ignore=tests/engine/`) must pass unchanged.
- **Stub, not a platform.** Route + resolve + call + return. Defer raw-GeoJSON input, buffer-fronting, and multi-timestep to later WOs.

## Endpoint contract

```
GET /api/area?polity=<name>&year=<int>[&level=6|8][&bands=ABCDET][&from_year=N&to_year=N][&detail=true]
```

Parameters:
- `polity` (required) — Cliopatria polity name; matched against `gaz.clio_polities.name`.
- `year` (required) — **resolver year**: the timestep at which the polity boundary is drawn. Selects the Cliopatria row where `fromyear <= year <= toyear`. This is the resolver temporal axis (WO20), independent of Band T span.
- `level` (default 6) — L6 or L8.
- `bands` (default all) — which bands to compute.
- `from_year` / `to_year` — **Band T span**: the window over which HYDE/LMR aggregate. Independent of `year`. Required only if Band T requested. If T requested without a span, return the same error `/signature` returns for that case (mirror existing behavior).
- `detail` (default false) — lean vs full, mirroring `areal_signature_polygon`'s `include_detail`. Lean returns the per-variable envelope; `detail=true` adds histogram objects (`detail['distribution']`) and per-basin detail.

The two temporal axes stay separate in the API surface exactly as they are in the engine — `year` moves the boundary, `from_year`/`to_year` moves the aggregation window. Do not collapse them into one parameter.

## Behavior

1. Look up the polity: `SELECT ... FROM gaz.clio_polities WHERE name = %s AND fromyear <= %s AND toyear >= %s`.
   - No match → 404 with a message naming the polity and year, and (nice-to-have) the available year ranges for that name if the name exists at other periods.
   - Multiple matches → return the row per the resolver's existing rule (WO20 `resolve_polity`); if that rule isn't deterministic here, 409 and surface the candidates rather than guessing.
2. Call `areal_signature_polygon(geom_wkt, level, conn, bands=..., from_year=..., to_year=..., include_detail=...)` with `resolver_year=year` threaded through (the field the histogram stamp uses).
3. Return the payload as JSON. Top-level payload carries `resolver_year` and, when Band T ran, the Band T span, so the response is self-describing on both axes.

## Out of scope

- Raw-GeoJSON / user-drawn polygon input (POST body) — later WO; raises the arbitrary-boundary analyst-drawer caveat.
- Fronting the buffer/point-rooted paths through `/area` — they stay on `/signature`; endpoint consolidation is a surface-driven question, deferred.
- Multi-timestep / time-series response shape — single resolver year, single Band T span this cut.
- Any sandbox / UI work.

## Acceptance / return

- `GET /api/area?polity=Northern+Song&year=1000&level=6&detail=true` returns the N Song payload matching the WO20/WO21b notebook run (376 basins, 35 spread verdicts, Yangtze dominant, histogram objects present with temporal stamp).
- Lean vs detail gating correct (histograms absent when `detail` unset).
- 404 path tested (bad polity, or year outside all ranges).
- Two-axis independence tested: a call with `year=1000` and a different `from_year`/`to_year` returns the boundary resolved at 1000 with Band T over the requested window.
- Existing app + engine suites pass unchanged; existing sandbox tests all-green.
- New tests in the app test suite (not engine contract).
- 