# WO3 findings — Scale compare, crosswalk, L08 choropleth

**Work orders:** WO3a (scale-probe), WO3b (crosswalk build), WO3c (member_ids + L08 speed)
**Date:** 2026-07-12–13
**Status:** all three complete; merged to `demo` branch

---

## F3.1 — L06 ↔ L08 toggle: working on Settlements, working on Polities (after fix)

The level toggle was wired for both tabs but inert on Polities at L08. Root cause: neither
`/api/area` nor `/api/areas?type=polity` returned `member_ids`. The frontend guard
(`level === 8 && !_sigMemberIds?.size`) fired, clearing the choropleth.

Fix (WO3c): both polity routes now return `member_ids` (list of L08 hybas_ids from the
crosswalk). Engine uses crosswalk lookup at L08 (~50 ms) replacing live `ST_Intersection`
(3–10 s). The toggle now works on the Polities tab. **577 tests pass.**

---

## F3.2 — Tbilisi: confirmed demo case (Settlements tab, toggle already working)

L06 → L08 on Tbilisi: aridity 93 → 63 (−30 pp), biome flips Temperate Broadleaf → Deserts
& Xeric Shrublands, ecoregion flips entirely, +5.5 °C. The Settlements tab toggle is live
today — no further build needed for this demo point. Full variable diff in `wo3_probe_findings.md`.

---

## F3.3 — N Song aridity gradient: confirmed real at L08

Spread values (p90−p10) within 1–3 pp of L06 at all three expansion states (961/970/980).
L08 confirms the structural gradient with 7–27× more basins; it does not dissolve it. Three-state
expansion is a clean demo arc: N Song ingests progressively more arid territory as it expands
south. L08 visually sharpens the picture — see screenshots.

---

## F3.4 — No side-by-side needed for demo

Toggle + signature panel diff carries the Tbilisi and N Song stories without a two-pane
side-by-side layout. Side-by-side estimated at 2–3 days; not warranted for Braga.

---

## F3.5 — ARI.5 (Pacific Northwest MAUP): slide/Explorer only

LISA classifications not in sandbox paint path. The geographic pattern is visible in the basin
choropleth (zoom Pacific Northwest, select Band C variable) but the formal outlier classification
requires Explorer or a pre-rendered slide. Explorer screenshots are the answer for Braga.

---

## F3.6 — Cliopatria geometry: repaired, crosswalk complete

`temporal.polity_basin08_crosswalk` built: **9,033,709 rows · 12,975 polities · 0 bad geometry**.
12 island/oceanic polities (Hawaii, Mauritius, Seychelles, etc.) intentionally have no rows —
correct, no L08 basins in open ocean.

Geometry repair was required before the build succeeded:
- 1,282 slices were invalid (self-intersecting rings) — fixed with `ST_MakeValid` +
  `ST_CollectionExtract` (returns MultiPolygon; raw `ST_MakeValid` returns GeometryCollection)
- Remaining failures were not geometry invalidity but GEOS numerical instability during
  `ST_Intersection(p.geog, b.geog)` (geography×geography path). Fix: switch to
  `ST_Intersection(b.geom, p.geom)::geography` — planar intersection then cast for area.
  This matches the engine's own `resolve_polygon` path and is numerically more stable.
- `gaz.clio_polities` backed up before repair; `gaz.clio_polities_backup` retained.

**Key rule confirmed:** always use `ST_Intersection(a.geom, b.geom)::geography` for
crosswalk/engine intersection. Geography×geography is more demanding and fails on polity
geometries that the geometry path handles without error.

---

## F3.7 — Two frontend bugs found during WO3c

1. **`member_ids` path wrong:** JS read `response.neighborhood.member_ids` but the API puts
   `member_ids` at the top level. This meant `_sigMemberIds` was always null even after the
   backend fix was in place.

2. **`applySlice()` bypassed `_silentResig()`:** slice stepping called `_repaintChoropleth()`
   directly, painting with the previous slice's member set. New basins in an expanded territory
   went uncolored. Fix: `applySlice()` calls `_silentResig()` instead.

---

## What's next

**Hero-shot curation** — the Polities tab L08 toggle is now the primary demo instrument.
Candidates from WO1a shortlist: N Song (aridity gradient + expansion arc), Tbilisi via
Settlements tab (scale contrast), others TBD. Identify 2–3 polity/variable/history triples and
confirm they render well in the browser before committing to slides.
