# WO3c · member_ids in API response + L08 speed via crosswalk

**Track:** Demo / infrastructure
**Depends on:** WO3b complete (`temporal.polity_basin08_crosswalk` built and verified)
**Unblocks:** L08 toggle on Polities tab; hero-shot curation at L08

**Findings from WO3a (F3.1):** level toggle on Polities tab is wired but inert at L08 because
`/api/area` and `/api/areas?type=polity` never return `member_ids`. The frontend reads
`nb.member_ids` in `_silentResig()` and sets `_sigMemberIds`; when that is null the L08
paint guard fires: "Get a signature first."

---

## What we are changing

**Two independent improvements, both in this WO:**

1. **`member_ids` in the API response** — adds a list of L08 hybas_ids to the polity payload so
   the frontend can populate `_sigMemberIds` and the level toggle works.

2. **L08 speed via crosswalk** — replaces the live `resolve_polygon` call (3–10 s) with a keyed
   crosswalk lookup (~50 ms) for `level=8` polity requests. Live fallback retained for any
   polity not in the crosswalk (the 12 island/oceanic cases).

---

## Change 1 — `member_ids` in the response

### Where the value comes from

`temporal.polity_basin08_crosswalk` holds every (polity_id, hybas_id) pair. After the polity
lookup resolves `polity_id`, one query returns all member basin ids:

```sql
SELECT hybas_id
FROM temporal.polity_basin08_crosswalk
WHERE polity_id = %s
ORDER BY weight DESC
```

### What to add to the payload

The frontend reads `nb.member_ids` as a top-level key on the response object. Add it there:

```python
payload["member_ids"] = [int(r[0]) for r in member_rows]
```

An empty list (island/oceanic polity) is correct — it means no L08 basins, so the guard
firing is the right behaviour.

### Which routes to modify

Both routes already have `polity_id` in scope when they call `areal_signature_polygon`:

- **`/api/area`** (routes.py ~3218): `polity_id` from the lookup rows; add the crosswalk
  query after `areal_signature_polygon` returns, before the `payload["resolver"]` block.

- **`/api/areas?type=polity`** (routes.py ~3406): same pattern; `polity_id` is in scope at
  line 3406.

The crosswalk query is the same in both routes — extract it as a one-liner helper or just
inline it.

---

## Change 2 — L08 speed via crosswalk

### New engine function

Add `resolve_crosswalk(polity_id, level, conn, epsilon=0.0001)` to `engine.py`. Returns the
same DataFrame as `resolve_polygon`: columns `[hybas_id, weight, basin_in_polity_fraction,
overlap_area_km2]`.

```python
def resolve_crosswalk(polity_id, level, conn, epsilon=0.0001):
    """Crosswalk resolver: polity_id → weighted basin set from pre-built crosswalk.

    Fast path for L08 polity signatures — replaces live ST_Intersection.
    Returns same schema as resolve_polygon. Empty DataFrame if polity not in crosswalk.
    """
    table  = f'public.basin{level:02d}'
    sql = """
    SELECT x.hybas_id,
           x.weight,
           x.basin_in_polity_frac  AS basin_in_polity_fraction,
           x.overlap_km2           AS overlap_area_km2
    FROM   temporal.polity_basin08_crosswalk x
    WHERE  x.polity_id = %s
      AND  x.weight >= %s
    ORDER  BY x.weight DESC
    """
    cur  = conn.execute(sql, (polity_id, epsilon))
    cols = [d[0] for d in cur.description]
    df   = pd.DataFrame(cur.fetchall(), columns=cols)
    df['hybas_id'] = df['hybas_id'].astype('int64')
    return df
```

Note: the crosswalk is L08-only. At L06, `resolve_polygon` remains the correct path (live
query is fast enough). The function is a no-op for L06 — just return the live result.

### Where to plug it in

`areal_signature_polygon` calls `resolve_polygon` internally. To use the crosswalk we add
an optional `polity_id` parameter; when present and `level=8`, try crosswalk first:

```python
def areal_signature_polygon(geom_wkt, conn, *, level=6, polity_id=None, ...):
    level_str = f'{level:02d}'
    if level == 8 and polity_id is not None:
        basin_set = resolve_crosswalk(polity_id, level, conn)
        if basin_set.empty:                      # island/oceanic — fall back
            basin_set = resolve_polygon(geom_wkt, level_str, conn)
    else:
        basin_set = resolve_polygon(geom_wkt, level_str, conn)
    # rest of function unchanged
```

Both routes already pass `polity_id` as a local variable; thread it through:

```python
payload = areal_signature_polygon(
    geom_wkt,
    conn,
    level=level,
    polity_id=polity_id,   # ← add this
    ...
)
```

---

## Scope limits

- **L06 crosswalk:** not needed — live query at L06 takes ~0.3 s; not a demo bottleneck.
- **member_ids at L06:** we return the crosswalk member_ids regardless of `level` because
  the crosswalk is L08-only; at L06 the paint guard doesn't fire so an absent `member_ids`
  at L06 is fine. Returning it at L08 is all the frontend needs.
- **Engine tests:** `resolve_crosswalk` needs a contract test added to
  `tests/engine/test_engine_contract.py` — N Song year=1000 should return non-empty
  DataFrame with `sum(weight)` close to 1.0.
- **`resolve_polity`** (engine.py ~145) — not touched; it goes through `resolve_polygon`
  directly and is not called by the routes we are modifying.

---

## Test plan

1. `python -m pytest tests/engine/test_engine_contract.py -v` — add `resolve_crosswalk` test
2. Curl check:
   ```
   curl "localhost:8000/api/areas?type=polity&polity=Northern+Song&year=1000&level=8&bands=A"
   ```
   Response should include `"member_ids": [...]` with non-empty list and return in < 1 s.
3. Browser — Polities tab:
   - Load N Song year 1000 → signature appears
   - Switch to L08 → choropleth paints (not "Get a signature first")
   - Switch a BasinATLAS variable — only N Song L08 basins paint

---

## Files to change

| File | Change |
|---|---|
| `scripts/edop/areas/engine.py` | Add `resolve_crosswalk()`; add `polity_id` param to `areal_signature_polygon` |
| `app/api/routes.py` | Thread `polity_id` into `areal_signature_polygon`; add `member_ids` to payload in both `/api/area` and `/api/areas?type=polity` |
| `tests/engine/test_engine_contract.py` | Add `resolve_crosswalk` contract test |

---

## Findings

### Bugs found during implementation

**Bug 1 — `member_ids` nested under wrong key.** The frontend read
`(await r.json()).neighborhood.member_ids` but the API puts `member_ids` at the response
top level (not inside `neighborhood`). Result: `_sigMemberIds` always null; first-slice paint
worked (initial signature fetch goes a different path) but level toggle never functioned.
Fix: read `data.member_ids` directly from the parsed response.

**Bug 2 — Slice stepping repainted with stale `_sigMemberIds`.** `applySlice()` called
`_repaintChoropleth()` directly, skipping `_silentResig()`. So `_sigMemberIds` still held the
previous slice's basin set when the new choropleth rendered: old basins stayed painted, new
basins in an expanded territory went uncolored.
Fix: `applySlice()` calls `_silentResig()` instead; `_silentResig()` updates `_sigMemberIds`
then calls `_repaintChoropleth()`.

### UX additions (not in original spec)

- **Spinner on slice step:** status element shows spinner + "Loading basins…" during the
  `/api/areas` fetch on slice change, but only when a variable is already active. Silent on
  initial polity load (no variable selected yet).
- **Level select disabled for grid variables:** switching to an LMR or HYDE variable disables
  `#v3-polity-level` and `#v3-level` (level has no meaning for raster/grid choropleth;
  changing it clears the paint). Re-enabled when a BasinATLAS variable is selected.

### Result

N Song 961 CE at L08: aridity gradient paints correctly across ~4,200 L08 basins.
Advancing through slices repaints correctly as polity boundary expands southward.
L08 renders a noticeably more nuanced spatial picture than L06 — the demo value
of the toggle is clear at this scale.

### Test counts

**577 passed, 52 skipped** (up 2 from two new `resolve_crosswalk` contract tests).
