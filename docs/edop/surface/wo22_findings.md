# WO22 Findings — L08 viability + Level-select wiring

Stage 1 notebook: `notebooks/edop/surface/wo22_l08_viability.ipynb`

---

## F22.1 — Choropleth values: L06 vs L08 (API side)

| | Basins | Query time | Payload (raw) |
|---|---|---|---|
| L06 | 16,397 | 0.051 s | 0.26 MB |
| L08 | 190,675 | 0.465 s | 3.05 MB |
| Ratio | 11.6× | 9.1× | 11.7× |

`/api/explorer/values` already dispatches on `level=` and returns correct `hybas_id`s at both
levels. `basin06` and `basin08` have identical columns; no variable mapping differences.
The values API side is **affordable at L08**.

The global 190k payload (3 MB) is a one-time load — not per-interaction. Under the selective-paint
design (F22.7), the feature-state loop only touches scope member basins (~100s, not 190k), so
the JS-side cost is also manageable. **Server side: GO.**

Unknown not measurable in notebook: MapLibre feature-state loop over 190k features if global paint
were attempted. Resolved by selective-paint decision (F22.7) — global loop never happens.

---

## F22.2 — Tileset reachability

`basin08.pmtiles` does not exist locally or on the server. This is the **hard prerequisite**
for L08 choropleth. Without it, feature-state paint has no vector source to target regardless
of values API performance.

`basin06.pmtiles` actual size: **18 MB** (local; PMTiles compression is very effective).
L08 file would be larger (11.6× more features, though smaller/simpler geometries per basin);
estimate 80–150 MB. Must be generated (tippecanoe from `basin08` geometry) and rsynced to server.

Explorer's L6/L8 toggle is a partially-wired dead control: the values API call reads `level=8`
correctly, but all `setFeatureState` calls target `basin06`/`basin06.pmtiles` throughout.
L8 values arrive but cannot paint. The toggle has never been fully wired anywhere.

**Verdict: blocker, not a performance question — must build and deploy before any L08 choropleth.**

---

## F22.3 — HYDE at L08

No L08 HYDE tables exist. Both crosswalk and steps table would need to be built from scratch.
`basin08` has `geom` and `geog` columns; build is feasible.

**Crosswalk (`temporal.hyde_basin08_weights`):**
- L08 basins are small (~19 HYDE cells/basin avg vs ~172 for L06); total crosswalk rows ≈ 3.6M
  (only modestly larger than L06's 2.82M, not 11.6×)
- Sample build time: 1.5 ms/basin → extrapolated ~5 min for 190k basins (one-time)

**Steps table (`temporal.hyde_basin08_steps`):**
- ~24M rows (190k basins × 128 steps; vs L06's 2.08M)
- Estimated build: ~2 hours (one-time); ~2.3 GB storage (Hetzner has adequate disk)
- Estimated per-request query time: ~0.38 s (vs L06's 0.033 s) — acceptable

**Verdict: affordable-with-build.** Same pre-aggregation pattern as WO17→WO18; larger but not
qualitatively different. Build is a one-time cost gated on Stage 2 approval.

---

## F22.4 — LMR at L08

`/api/lmr/values` queries `temporal.lmr_climate` only (2°×2° grid, 16,380 cells) — no basin
table join. Level has no effect on LMR paint.

**Verdict: level-agnostic. No work needed. ✓**

---

## F22.5 — Signature aggregation at L08

| Scope | L06 | L08 | Ratio | Basins (L06→L08) |
|---|---|---|---|---|
| N Song polity (with T) | ~3.6 s | 23.32 s | 6.4× | 372 → 4,214 |
| Buffer 150 km (with T) | 1.29 s | 17.96 s | 13.9× | 14 → 111 |
| Buffer 150 km (no T) | 1.25 s | 18.47 s | 14.7× | 14 → 111 |

Removing Band T made no meaningful difference (14.7× vs 13.9×), ruling out Band T and the
absence of `hyde_basin08_steps` as the cause.

**Root cause: per-request `PERCENT_RANK()` over the full basin table (F22.8).**

**After fix (F22.9):** Pre-materialized `public.basin08_scores` + `attach_values` fast path:
Buffer L06 (no T): 1.17s / Buffer L08 (no T): **0.90s** — L08 is now *faster* than L06
because the indexed lookup beats L06's live PERCENT_RANK computation entirely.

---

## F22.6 — Explorer L8 toggle: current wiring state

Values API at L08 works and returns correct L08 `hybas_id`s. Render side is dead: all
`setFeatureState` calls in `explorer.html` target the `basin06` source/layer throughout.
The toggle exists visually but has never been functionally wired for choropleth paint.

---

## F22.7 — Selective paint design decision (locked)

Global L08 tileset (`basin08.pmtiles`) built once covering all 190,675 basins. Paint is
selective: only the member basins of the resolved scope receive variable values and color;
all other basins remain transparent. This mirrors the scope-member approach already used
for geometry drawing (buffer basins, ring members).

Rationale: at L08, the research value is fine-grained local texture around the resolved scope,
not a finer-grained world map. Selective paint is better UX, not just a performance compromise.
The "prowl" affordance is preserved at L06 globally; L08 adds local depth.

Implication: the 190k feature-state loop problem is resolved — only ~100s of basins get
painted per interaction.

---

## F22.8 — PERCENT_RANK bottleneck in areal signatures at L08

The 18–23 s areal signature times at L08 are caused by `attach_values()` in `engine.py`
(lines 664–666): a monolithic query computes `PERCENT_RANK() OVER (ORDER BY val)` across
the **entire basin table** (190,675 rows) for every continuous variable on every request.
This full-table window function + sort is the bottleneck — not Band T, not HYDE tables.

At L06 this costs ~1–4 s depending on scope size; at L08 (~11.6× rows) it costs 18–23 s.
The fix would be to pre-materialize percentile scores for L08 into a materialized view or
table (analogous to `hyde_basin06_steps`). That is a non-trivial engine change.

**Single-basin scope is unaffected** — one row ranked against 190k is fast; no aggregation loop.
Buffer and polity at L08 are slow by this mechanism regardless of Band T or HYDE tables.

---

---

## F22.9 — Pre-materialized L08 percentile scores (`public.basin08_scores`)

`public.basin08_scores`: 190,675 rows × 42 continuous-variable score columns. Each column stores
`PERCENT_RANK() * 100` computed once over the full L08 basin population, matching the three scoring
cases in `attach_values` (clean / nodata two-pass / zero-aware partitioned scoring). Build ~10–15 min
(one full-table sort per variable; one-time cost).

`attach_values` fast path (branch on `table = 'public.basin08'`): `SELECT hybas_id, {alias_cols}
FROM public.basin08_scores WHERE hybas_id IN (...)` replaces the full-table PERCENT_RANK window
function. Index on `hybas_id`.

**Result:** Buffer L08, Bands A–E: **0.90 s** — faster than L06's 1.17 s, because the indexed
JOIN beats L06's live PERCENT_RANK computation entirely. L08 buffer/polity signatures are no longer
the bottleneck.

---

## F22.10 — HYDE L08 tables: build outcomes

| Table | Rows | Build time | Per-request query |
|---|---|---|---|
| `temporal.hyde_basin08_weights` | 4,306,122 | 56 s | — (build artifact) |
| `temporal.hyde_basin08_steps` | 24,300,800 | 22.5 min (1350 s) | 0.402 s |

189,850 basins with HYDE data (vs 190,675 total; 825 no-land basins absent). Per-request 0.402 s
is 12× slower than L06's 0.033 s, reflecting the larger table; well within the acceptable
threshold for a choropleth load. Schema identical to L06 steps table (`hybas_id`, `step_idx`,
`cropland_frac`, `grazing_frac`, `pasture_frac`, `rangeland_frac`). `/api/hyde/values` dispatches
on `level` param to the correct table.

---

## F22.11 — `#v3-level` disable-at-cold-start design

Settlements level select disabled at cold start (parallel to `#v3-polity-level`) — the control
has no visible effect until a place is resolved, and enabling it before then produces a confusing
"I changed this but nothing happened" experience. Enabled in `setResolvedPoint()` and the example
handler; disabled in `clearResolvedPoint()` and `resetSettlements()`. Reset also resets the value
to `'6'`.

Structural test `test_settlements_level_disabled_on_load` documents the contract; Playwright tests
cover the enable-on-example and disable-on-reset lifecycle.

---

## F22.12 — `_onLevelChange()`: silent resig, no tab switch

Level change must not navigate away from the Map tab (user is there to see the geometry change).
Solution: `_onLevelChange()` calls `_drawScopePreview(scope)` (redraws basin outline at new level)
and `_silentResig()` (background re-fetch of scope membership at new level without touching the
spinner or any tab). `_silentResig()` calls `_repaintChoropleth()` on success.

`_basinLayerLevel` state variable tracks which level the `basin-choropleth` PMTiles source is
currently loaded at. Set to `null` on level change, forcing `loadBasinLayer()` to tear down and
reload at the new level. Null = force reload.

`_repaintChoropleth()` is a shared helper called both after Get Sig success and after
`_silentResig()` — ensures choropleth stays in sync whenever membership or level changes.

---

## F22.13 — Single-basin L08: auto-extend to ring for choropleth

A single L08 basin is typically a small sub-catchment; painting one basin on a global tileset
provides no local context. Auto-extend: at L08, `_sigMemberIds` includes the center basin + all
ring neighbors (parallel fetch of sig + `/api/basin/ring`). At L06, single-basin sets
`_sigMemberIds = {hybas_id}` only (one basin is a meaningful geographic unit at L06).

This is purely a choropleth paint decision — the signature in the Sig tab is still the center basin's
signature only. The extended `_sigMemberIds` controls which basins receive paint color; it does not
change what is computed.

---

## F22.14 — LMR longitude convention mismatch (bug fix)

`temporal.lmr_climate` stores lon in 0–360° convention (from the LMR source data). `lmr_notches.geojson`
(the client-side paint target) uses -180–180° convention. The join key in `/api/lmr/values` was
`CONCAT(lat, ',', lon)`, which produced keys like `"70,200"` for a point at lon = -160°. The GeoJSON
property equivalent was `${f.properties.lat},${f.properties.lon}` → `"70,-160"`. Keys never matched
for Western Hemisphere cells (lon > 180° in DB).

Effect: silent no-paint for all Western Hemisphere cells. Only Eastern Hemisphere cells (0°–180° lon)
painted — appearing as a vertical band covering Eurasia/Africa but not the Americas.

Fix in SQL CONCAT: `CASE WHEN lon > 180 THEN lon - 360 ELSE lon END`. 16,380 cells now paint correctly.

---

## F22.15 — Band T nudge: LMR alert + flash; HYDE flash-only

When a time-dependent choropleth variable is selected without a Band T span set:

**LMR** (hard failure — no span = no data): `_bandTNudge(msg)` shows a Bootstrap `alert-warning`
in the `#v3-basin-status` div (font-size 0.82rem, `py-1 px-2`) and calls `_flashBandT()`. Alert
auto-dismisses after 8 s. Message: *"LMR requires a time span — check T and enter a year range."*

**HYDE** (soft default — falls back to 1000 CE and paints successfully): `_flashBandT()` only.
Showing an alert is wrong because `applyHydeChoropleth` immediately overwrites the status div with
`'Loading…'`; the alert would vanish in < 100 ms. The T checkbox flash is sufficient to orient the
user without a racing alert.

`_flashBandT()`: adds CSS class `v3-band-t-flash` to the T checkbox's `.form-check` container;
removes after 2 s. Animation: `@keyframes v3-flash-yellow` — transparent → #fff3cd (Bootstrap
warning yellow) → transparent over 2 s. Reflow forced (`void el.offsetWidth`) so re-triggering
the animation works without removing and re-adding the element.

---

## Stage 2 — Accept gate

| Consumer | L08 result | Notes |
|---|---|---|
| Areal signature (buffer/polity) | **0.90 s** (L08) vs 1.17 s (L06) | `basin08_scores` fast path |
| Areal signature (single-basin) | Fast at any level | One-row ranked lookup |
| Choropleth values (BasinATLAS) | 0.465 s, 3 MB | Selective paint; only ~100 basins touched |
| HYDE steps (L08) | 0.402 s/request | 24.3M-row table; 22.5 min one-time build |
| LMR | Level-agnostic | Grid-based; no basin join |
| `basin08.pmtiles` | ✓ built, 76 MB | At `app/static/explorer/basin08.pmtiles` |
| Level select wired | ✓ | Both Settlements + Polities; disable/enable lifecycle |
| Tests | 571 pass, 50 skipped | Zero failures; WO22 adds 20 structural + 7 Playwright |

Level-select wiring closes SURFACE's last surfacing gap: the engine and API have supported `&level=`
throughout; sandbox_v3 now exposes it operably. The L06↔L08 compare (MAUP demo asset) is a future
Demo-phase concern.

---

## Stage 2a — Prerequisites (spec)

Two one-time build tasks. No dependencies on each other; can run in parallel.
Neither touches L06 paths. Both must exist and be verified before any Stage 2 UI wiring.

---

### 2a-1: `basin08.pmtiles`

**What:** Generate a global PMTiles vector tileset from `basin08` geometry, matching the
conventions of `basin06.pmtiles` so the existing shell + feature-state paint architecture
works unchanged.

**Requirements:**
- Source-layer name: `basin08` (parallel to `basin06` in `basin06.pmtiles`)
- Feature IDs must be `hybas_id` integers — `setFeatureState` keys on this
- Export `basin08` from PostGIS: `SELECT hybas_id, geom FROM public.basin08`
- Tippecanoe: follow same zoom/simplification settings used for `basin06.pmtiles`
  (check how `basin06.pmtiles` was generated; replicate for `basin08`)
- Output: `app/static/explorer/basin08.pmtiles`
- Rsync to server alongside `basin06.pmtiles`

**Verify:**
- `HEAD /static/explorer/basin08.pmtiles` → 200 locally and on server
- MapLibre can load as `pmtiles:///static/explorer/basin08.pmtiles` vector source
- Feature IDs present and match `hybas_id` values from `/api/explorer/values?level=8`

**Expected size:** 80–150 MB (estimate; L08 has 11.6× more features than L06's 18 MB,
partially offset by smaller/simpler geometries per basin)

**Performance to evaluate after build:**
- Time to load the source in MapLibre (first tile fetch)
- Feature-state paint time for a representative scope member set (~100 basins)

---

### 2a-2: Pre-materialized L08 percentile scores

**What:** Compute `PERCENT_RANK()` once for all continuous variables across all 190k L08
basins and store in a table. Modify `attach_values` in `engine.py` to do a fast indexed
JOIN instead of a full-table window function per request.

**Why:** Per-request PERCENT_RANK over 190k rows costs 18–23 s for buffer/polity scopes.
Basin data is static; scores computed once are valid indefinitely.

**Build: `public.basin08_scores`**

Schema: `(hybas_id bigint PRIMARY KEY, {pos_col} real, ...)` — one column per continuous
variable, named to match the alias pattern in `attach_values` (`pos_{api_key}`).

Three scoring cases to handle (matching `attach_values` logic):
1. **Clean vars** (no nodata): `PERCENT_RANK() OVER (ORDER BY {val}) * 100`
2. **Nodata vars** (two-pass): PERCENT_RANK over valid population only; nodata rows → NULL
3. **Zero-aware vars**: partitioned scoring (zero values score 0; nonzero values ranked
   within nonzero population × `(1 − zero_fraction)`)

Build approach: generate the table in a notebook (`wo22_build_scores.ipynb`) using the
catalog to enumerate continuous variables and their scoring method. Index on `hybas_id`.

**Engine change: `attach_values` in `engine.py`**

When `table = 'public.basin08'`, substitute the pre-computed lookup:
```python
# instead of: ranked CTE over full table
# do: SELECT hybas_id, {alias_cols} FROM public.basin08_scores WHERE hybas_id IN (...)
```
L06 path (`table = 'public.basin06'`) unchanged.

**Verify:**
- Buffer Timbuktu 150 km at L08: target < 3 s (vs 18 s now; L06 baseline 1.25 s)
- N Song polity at L08: target < 10 s (vs 23 s now; L06 baseline ~3.6 s)
- L06 results unchanged (engine contract tests must stay green)
- Zero-aware and nodata variable scores match expected values

**Expected build time:** 10–30 min (one PERCENT_RANK sort per continuous variable × ~100
variables over 190k rows). Run as a single SQL script or notebook.

---

## Stage 1 verdict (pending review)

| Consumer | L08 verdict |
|---|---|
| Choropleth values (API) | GO — 0.465 s, 3 MB; selective paint resolves JS-side concern |
| Tileset (`basin08.pmtiles`) | **BLOCKER** — must build before any choropleth |
| HYDE steps table | Affordable-with-build (~2h one-time, ~0.38 s/request) |
| LMR | GO — level-agnostic ✓ |
| Areal sig — single-basin | GO — fast at any level |
| Areal sig — buffer/polity | **SLOW** — 18–23 s due to PERCENT_RANK; engine fix required |
| Explorer L8 toggle | Dead render side; values side already works |
