# WO9 audit findings

**WO:** wo9_audit
**Phase:** Surface
**Date:** 2026-07-04
**Type:** Investigation (read-only; one proposed register diff for Karl's sign-off)

---

## Part A — Single-basin true state

### A1 — Fixture or DB?

**FIXTURE.** When the user selects single-basin and clicks Get Signature, the handler
falls into the `else` branch of the sig button click handler (`sandbox_v2.html` ~line 971):

```js
} else {
    payload = await loadFixture(currentScope);
}
```

`FIXTURE_URLS.single` = `/dev/exemplars/01_single_basin_detail.json` — a static JSON file.
No DB call is made.

### A2 — Does `/api/areas` accept `type=single_basin`?

**No.** The dispatch in `app/api/routes.py` line 3032–3036:

```python
else:
    raise HTTPException(
        status_code=422,
        detail=f"Unsupported type '{type}'. Supported: buffer, polity",
    )
```

`type=single_basin` 422s immediately.

### A3 — Reachable at all?

**No.** `single_basin_signature` is exported from `engine.py` but wired to no HTTP route.
The only routes that call into the engine are `/api/areas` (buffer + polity) and the old
`/api/area` (polity only via `areal_signature_polygon`). Neither touches
`single_basin_signature`.

### A4 — Band T

**Three layers, three answers:**

1. **Fixture:** No T rows — confirmed by WO2 design note ("T rows absent from single-basin
   fixture by design"). `01_single_basin_detail.json` has bands A–E only.

2. **Engine entry point:** The `single_basin_signature` docstring says "Band T is not yet
   supported … Deferred." This is **stale**. The function retrieves `basin_geom_wkt` and
   passes it with `from_year`/`to_year` to `_areal_signature_from_basin_set`
   (`engine.py` ~line 2151):
   ```python
   return _areal_signature_from_basin_set(
       basin_set, level, conn,
       geom_wkt=basin_geom_wkt,
       from_year=from_year,
       to_year=to_year,
       ...
   )
   ```
   `_areal_signature_from_basin_set` calls `aggregate_band_t(..., geom_wkt=geom_wkt)`
   when a span is given. `aggregate_band_t` already accepts a `geom_wkt` polygon path
   (line 918: `if geom_wkt is not None: buf_geom_sql = f"ST_GeomFromText('{geom_wkt}', 4326)"`).
   The polygon Band T path was built for the polity resolver; `single_basin_signature`
   passes the basin polygon through the same route. The code should produce T rows.
   Has never been exercised via HTTP because the entry point is unwired.

3. **Page toggle:** The Band T checkbox is not scope-gated. But regardless of whether T
   is checked, single-basin loads the static fixture, so T rows never appear on the page.

### Part A — Single-basin true state (summary paragraph)

Single-basin is **fixture-only with no live path**. "Load an example → single basin" fetches
`/dev/exemplars/01_single_basin_detail.json` — a static file, no DB call. `/api/areas`
rejects `type=single_basin` with a 422; `single_basin_signature` is not wired to any HTTP
route. The fixture has no Band T rows (by design); the Band T toggle is not scope-gated but
is irrelevant since the fixture path ignores it. At the engine level, the "not yet supported"
docstring is stale — the code passes the basin polygon WKT and span params through the polygon
Band T path, which should produce T rows. This has never been verified via HTTP because the
route doesn't exist.

**The tracker claim "single-basin not HTTP-wired" is accurate.** No continuity-prompt
overclaim — the page delivers a fixture, not a live call.

---

## Part B — Basin-ring weight policy

### B1 — What weight scheme ships?

**None — the ring is not aggregated.** `basin_ring_signature` (`engine.py` lines 2261–2339)
calls `single_basin_signature` independently for the center and for each ring member via
`ST_PointOnSurface` query points. It returns:

```python
return {
    'type':  'basin_ring',
    'center': center_sig,   # single_basin_signature payload
    'ring':   ring_members, # list, one per adjacent basin
}
```

Each ring member is an independent, unweighted signature. `sub_area_km2` and `shared_km`
are carried as descriptive metadata per member. They are not used to weight any aggregation.

There is no combined ring score. The weight question — equal / area-proportional /
border-length — was about combining ring members into one number. That combination was
never built.

### B2 — Decision record?

The WO16 session log (2026-06-26) is where the deferred register row was created —
three weight schemes were computed for Timbuktu L06, no winner chosen, row added as open.

The WO17 session log (2026-06-27/28, `session_log_20260701.md`) describes `resolve_basin_ring`
producing `(center_df, ring_gdf)` for a "per-neighbor transition diagnostic." The outputs are
**per-neighbor signatures for comparison** — the WO18 "transition-character comparator" then
operates on those individual signatures. There is no log entry deciding "we will not aggregate";
the per-basin design just arrived without a formal weight-policy decision.

The 2026-07-01 promotion session (`session_log_20260701.md` line 49) notes:
> "S4 basin-ring has no top-level `rows`."

That is the clearest evidence: the fixture contract itself reflects the non-aggregate design.

No explicit record says "weight policy superseded." It was superseded implicitly when the
ring design solidified as a per-neighbor comparison payload.

### B3 — Verdict

The register row is **stale**. The shipped design never aggregates ring members; the weight
policy question it tracks was superseded when `basin_ring_signature` crystallised as a
per-neighbor comparison structure (no `rows`, no combined score). The open row will never
have a resolution in the originally-posed form.

**Proposed register diff for Karl's sign-off:**

Remove from the open section "Surfaces before basin-ring resolver (WO17)":

```
| Basin-ring weight policy | WO16 computed three candidate schemes for the Timbuktu L06 ring:
  equal (0.2 each), area-proportional (0.469–0.017), border-length (0.423–0.035). ...
  | WO17 resolver design. Opus decides; CC implements. |
```

Add to the Closed section:

```
| Basin-ring weight policy | 2026-07-04 | Superseded by design. `basin_ring_signature`
  returns per-member signatures (center + ring), not a weighted aggregate. Weight policy
  was framed for a combined ring score that was never built. The per-neighbor comparison
  payload made it moot. WO17/promotion (2026-07-01). |
```

---

## Tracker update needed

The tracker currently says:

> Next: WO9 — TBD. Discuss with Opus. Candidates: single-basin scope on map (WO-b); basin-ring scope live; HYDE dense-epoch UI compensation (F7.5).

After this audit:
- Single-basin (WO-b) requires: (1) a `type=single_basin` entry in `/api/areas`, (2) a map layer (the containing basin polygon), and (3) the fixture should probably gain a live path. These are the tasks for the next WO.
- The single_basin_signature docstring saying "Band T not yet supported" should be updated — that path exists in the code.
- Basin-ring weight policy row closes.
