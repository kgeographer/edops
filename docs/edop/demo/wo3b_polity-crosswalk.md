# WO3b · Polity–basin08 spatial crosswalk

**Track:** Demo / infrastructure
**Status: complete — 2026-07-13**
**Motivation:** L08 signature queries for polities take 2.7–10.5 s (live `ST_Intersection` over
190K basins). Pre-materialising the spatial join as a crosswalk table reduces this to a keyed
lookup (~50–200 ms), and makes `member_ids` available in the API response at no extra cost,
unblocking the L08 choropleth on the Polities tab.

**Probe findings:** `docs/edop/demo/wo3_probe_findings.md` F3.1

---

## What we built

`temporal.polity_basin08_crosswalk` — one row per (polity slice, intersecting L08 basin):

```
polity_id             integer   — gaz.clio_polities.id (serial; internal key — see note)
hybas_id              bigint    — basin08 basin
weight                float     — overlap_m2 / polity_area_m2  (same convention as engine)
basin_in_polity_frac  float     — overlap_m2 / basin_area_m2
overlap_km2           real      — overlap area in km²
```

Primary key: `(polity_id, hybas_id)`. Index on `polity_id`.

**Note on `polity_id`:** `gaz.clio_polities.id` is a serial — an internal DB key, not a
Cliopatria canonical identifier (the canonical ID is `name`). The crosswalk is valid as long as
`clio_polities` is not truncated and reloaded; if it is, IDs reassign and the crosswalk must be
rebuilt. This is the same key already used in the `/api/area` resolver response.

Scope: `NOT is_component` slices only (12,987 rows).
Epsilon: 0.0001 (matches `resolve_polygon` in engine.py).

**Final result: 9,033,709 rows · 12,975 polities covered · 0 bad geometry**

12 polities have no crosswalk rows — all are island/oceanic territories with no L08 basin
coverage (Hawaii, Mauritius, Seychelles, one single-year Portugal fragment, one British East
Africa coastal enclave). This is correct behaviour, not failure.

---

## Step 1 — Add `geog` column to `gaz.clio_polities`

```sql
ALTER TABLE gaz.clio_polities
  ADD COLUMN IF NOT EXISTS geog geography(Geometry, 4326)
  GENERATED ALWAYS AS (geom::geography) STORED;

CREATE INDEX IF NOT EXISTS clio_polities_geog_idx
  ON gaz.clio_polities USING GIST (geog);
```

Complete. Also added backup table `gaz.clio_polities_backup` before any geometry edits.

---

## Step 2 — Build script

**Location:** `scripts/edop/build_polity_crosswalk.py`

All geometry stays in the database — no WKT passes through Python. The INSERT SQL joins
directly to `gaz.clio_polities` by `id`. Python only drives the loop and tracks progress.
Script is resumable: re-running skips already-processed polity ids.

**Key SQL — use geometry×geometry→geography (NOT geography×geography):**

```sql
WITH polity AS (
    SELECT geom, ST_Area(geom::geography) AS polity_m2
    FROM   gaz.clio_polities
    WHERE  id = %(polity_id)s
),
inter AS (
    SELECT b.hybas_id,
           ST_Area(ST_Intersection(b.geom, p.geom)::geography) AS overlap_m2,
           ST_Area(b.geog)                                     AS basin_m2
    FROM   public.basin08 b, polity p
    WHERE  ST_Intersects(b.geom, p.geom)
)
```

`ST_Intersection(b.geom, p.geom)::geography` — planar intersection then cast for area.
This matches the engine's own `resolve_polygon` path and is more numerically stable than
`ST_Intersection(p.geog, b.geog)` (spheroidal intersection direct), which caused 2,186
GEOS side-location conflicts. See findings below.

---

## Step 3 — Verify

N Song spot-check (run before Step 4):

```sql
SELECT COUNT(*), ROUND(SUM(weight)::numeric, 4) AS sum_weight
FROM temporal.polity_basin08_crosswalk
WHERE polity_id = (
    SELECT id FROM gaz.clio_polities
    WHERE name = 'Northern Song' AND fromyear <= 1000 AND toyear >= 1000
      AND NOT is_component
    LIMIT 1
);
-- sum(weight) should be close to 1.0 (small shortfall expected at polity edges)
```

---

## Step 4 — Next WO

- Plumb `member_ids` into `/api/area` + `/api/areas` neighborhood response using the crosswalk
- Add crosswalk-lookup path in engine for L08 speed gain (replaces live `resolve_polygon`)
- L06 crosswalk (optional; live query is fast enough at L06)

---

## Findings

### Geometry repair — what happened

Initial build used `ST_Intersection(p.geog, b.geog)` (geography×geography). This produced
**2,186 GEOS side-location conflicts** (TopologyException) across 482 distinct polity names,
including Ottoman Empire, Roman Empire, Byzantine Empire, Mughal Empire, and others.

Diagnostic (`ST_IsValid` + `ST_IsValidReason` on the 2,186 missing polities):

- **331 outright invalid** — self-intersecting rings (classic geometry errors)
- **1,855 valid-but-fragile** — `ST_IsValid = true` but near-coincident vertices cause
  contradictory side labels during two-geometry overlay

**Pass 1 — fix invalid geometries (run on full table):**

```sql
UPDATE gaz.clio_polities
SET geom = ST_Multi(ST_CollectionExtract(ST_MakeValid(geom), 3))
WHERE NOT is_component AND NOT ST_IsValid(geom);
-- 1,282 rows updated (includes component-adjacent slices beyond our 331)
```

`ST_CollectionExtract(..., 3)` required because `ST_MakeValid` returns `GeometryCollection`
when a self-intersecting polygon decomposes into mixed types; column type is `MultiPolygon`.

After pass 1: `ST_IsValid = true` for all 12,987 non-component slices. All 2,186 formerly-
missing polities now report valid — confirming they were all in the valid-but-fragile category.

**Pass 2 — SnapToGrid on the 2,186 valid-but-fragile slices:**

```sql
UPDATE gaz.clio_polities
SET geom = ST_Multi(ST_CollectionExtract(ST_MakeValid(ST_SnapToGrid(geom, 0.0001)), 3))
WHERE NOT is_component
  AND id NOT IN (SELECT DISTINCT polity_id FROM temporal.polity_basin08_crosswalk);
```

This did NOT fix the crosswalk failures. The insight: SnapToGrid repairs the polity geometry
in isolation, but the side-location conflict happens at the **overlay between polity and basin
boundaries**, not within the polity alone. No amount of in-isolation geometry repair eliminates
conflicts that arise from how two geometries interact.

**The real fix:** change the crosswalk INSERT SQL to use geometry intersection, not geography:

```
-- broken:  ST_Area(ST_Intersection(p.geog, b.geog))
-- working: ST_Area(ST_Intersection(b.geom, p.geom)::geography)
```

Geography×geography intersection uses a spheroidal computation path that is numerically more
demanding and more prone to GEOS overlay conflicts. The engine's `resolve_polygon` already
uses the geometry path for exactly this reason. The crosswalk should match the engine.

With this change: second build run completed in 0.66 h, **0 bad geometry**, all 2,186
previously-failing polities successfully processed.

### Timeline (actual)

| Step | Time |
|---|---|
| Add `geog` + index to `clio_polities` | < 1 min |
| First build run (10,801 polities, geography path) | ~5 h |
| Geometry repair (SQL, DBeaver) | ~1 h |
| Second build run (2,186 remaining, geometry path) | 0.66 h |
| **Total** | **~7 h** |

### Key lesson

Always use `ST_Intersection(a.geom, b.geom)::geography` for area computation in spatial
crosswalk builds. The geography×geography path is stricter and fails on geometries that the
geometry path handles without error. The engine already encodes this correctly in
`resolve_polygon`; the crosswalk must match.
