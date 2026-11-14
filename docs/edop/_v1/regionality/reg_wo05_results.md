# WO-05 results: GEDA served through the registry (stage 3)

Spec: `reg_wo05_geda_through_registry.md` (with its "Adjustments after review"). Branch `geda`, cut from `registry`; no merge back planned. Parts 0 to E done. Commits: 1efa67e, 36b7cf5 (spec), c638ef4, 25d4cad, 931e5f5, 638984b, and the docs and results commit that carries this file.

## Done

**Part 0: the path.** The Sandbox's Get signature calls `/api/areas`, which passes the Band T span to all four engine entry points (`areal_signature`, `single_basin_signature`, `basin_ring_signature`, `areal_signature_polygon`). `areal_signature`, `single_basin_signature` and `areal_signature_polygon` each call `_areal_signature_from_basin_set`, which holds the one call to `aggregate_band_t` (the ring was not read; the Sandbox never sends it). The Sandbox's second request (`/api/signature?scope=basin&bands=ABCE`) never carries T, so GEDA never appears there.

**Part A: registry and catalog (1efa67e).**
- GEDA's registry entry: `status: served`; `variables` (payload `geda_scpdsi`, catalog `geda_scpdsi`, column `scpdsi`, units "SD (z-score)"); caveats `geda_caveat` (every row) and `geda_observed` (1990-2020, named by the year flag); `describes.version` now cites the Zenodo deposit; `describes.notes` updated.
- Catalog row `geda_scpdsi` (band T, `temporal_climate`, key equal to the payload name, so it joins with no crosswalk). `concordance_notes` left empty (not tested for GEDA); the phase-4 placeholders follow the LMR rows. Codebook regenerated (103 rows).
- `geda_caveat` and `geda_observed` in `CAVEAT_TEXTS`.
- Two registry unit tests that used GEDA as their "stored" source now use a temporary `stored_demo` source.

**Part B: `check()` and the GEDA block (c638ef4, 25d4cad).**
- `source_registry.check()` now judges a regional source: permission, status, years (no database work when the span is outside), then the footprint (cells of `temporal.geda_climate.cell_geom` under the geometry) and the coverage rule (below 0.1 `below_coverage_floor`; 0.1 to 0.5 applied with `flag='low_coverage'`; from 0.5 ok). `Decision` carries `coverage` and `flag`; `coverage_outcome()` holds the rule; `year_caveats()` reads the registry's year flags. `geometry` is a `(SQL expression, parameters)` pair; table and column names come from the YAML through `psycopg.sql` identifiers. A regional source without geometry or connection raises `ValueError`.
- `_BandTQuery` gained `geom`, built beside the existing text forms in `_band_t_query`; the HYDE, LMR and eVolv2k blocks are unchanged.
- `_band_t_geda(q)`, called last so existing row order is unchanged: one `geda_scpdsi` row per year (clipped to 1000-2020), shaped like an LMR row (`method: grid_areal_distribution`, `unit_type: geda_cell`, weighted mean in `representative_raw`, `detail.distribution` with bins, weights, p10, p90, min, max, mean, `low_resolution`). Status `low_coverage` below 0.5 coverage. Zero touching cells is a normal outcome (no rows, decision says why). Parameterized SQL throughout. Regression anchors from WO-02 reproduce: Kyiv basin 2060448220, 1350: mean -0.408, p10 -0.567, p90 -0.261, 27 cells, effective 14.25.
- Two departures from the WO's wording: (a) "observed" is a second caveat key, `geda_observed`, on 1990-2020 rows, not an `observed: true` field. A new row field would add a key to every row of every payload (`make_row` is shared), and `project_row` drops `detail` in the lean form, so the caveat list is the only place a flag survives in both forms; it is also how HYDE marks 1950. (b) The effective cell count is `detail.w_eff`, as for HYDE; LMR rows do not carry it, and it is the one structural difference between a GEDA row and an LMR row (tested).

**Part C: the `sources` block (931e5f5).** The GEDA decision flows through `sources_block()` with no extra wiring: `used` when rows are returned (with the note "covers 49.8% of the area" when low coverage), `not_applied` with `outside_span`, `outside_footprint` or `below_coverage_floor`, in neither list when Band T is not requested or GEDA is not permitted. Tested through the real routes, including the public buffer route (Kyiv, 100 km, single year), whose `variables` carry the GEDA row and whose `sources` is top-level.

**Part D: tests and baseline (638984b).**
- New: `test_source_registry_footprint.py` (13), `test_band_t_geda.py` (12), `test_sources_block_geda.py` (7), plus `year_caveats` unit tests.
- Existing tests updated for a fourth source: Northern Song counts in `tests/test_areas.py` (372/320 to 473/421, +101 GEDA years); the four frozen-fixture equivalence tests now compare on rows other than GEDA (the fixture predates it); the `sources`-block and permitted-sources tests expect GEDA's decision. One test of mine compared two runs of the HYDE rows with exact equality; the HYDE query does not fix cell order, so sums differ in the last digits. It now compares to tolerance.
- Pre-re-capture diff (fresh payloads against the 13 references, additions included; reviewed by Karl): no removed fields; changed values only in the `sources` lists; added fields only GEDA rows and `caveats.geda_caveat`. Kyiv Band T 1236-1240 and 1300-1400: +5 and +101 GEDA rows, GEDA in `used`. Timbuktu (four payloads): GEDA in `not_applied`, `outside_footprint` (the WO's assumption held). Northern Song 950-970: `not_applied`, `outside_span`. The five A-E payloads and the public signature: unchanged.
- Re-capture: all 13 references re-captured; three added (`kyiv_buffer100_bandT_1300_1400`, `chaco_canyon_bandT_1300_1400`, `geda_edge_basin_bandT_1300_1400`); `signature_version` stays "0.5". The baseline now carries `sources` and GEDA.
- Full suite after the re-capture: 755 passed, 21 skipped (the usual), no failures. Commit 25d4cad alone fails seven baseline payloads (the references follow in 638984b): use the two together.

**Part E: docs.** `docsite/data-sources.md` GEDA section: served on the engine path, not on `scope=basin`, not on the Sandbox page; how it is returned, the coverage rule and the observed years. `docs/design/dashboard/sandbox_cheatsheet.md`: GEDA in the Band T lists, §3.2, §4.3, §5.3 and the catalog counts (a stale "0-1998" in §3.2's LMR row, missed in WO-04, corrected to 0-2000).

## Timings

`_band_t_geda` (including `check()`'s footprint query) against `_band_t_lmr` on the same geometry; local database, median of three.

| Case | Span | Cells | GEDA | LMR |
|---|---|---|---|---|
| Single basin (Kyiv L6) | 1300-1400 / 1000-2020 | 27 | 0.014 / 0.045 s | 0.011 / 0.079 s |
| Buffer 100 km (Kyiv) | 1300-1400 / 1000-2020 | 24 | 0.008 / 0.040 s | 0.014 / 0.078 s |
| Buffer 1000 km (Kyiv) | 1300-1400 / 1000-2020 | 1,517 | 0.12 / 0.82 s | 0.028 / 0.25 s |
| Polity (Northern Song 961) | 1300-1400 / 1000-2020 | 431 | 0.046 / 0.29 s | 0.016 / 0.13 s |

GEDA's grid is finer (about 16 times as many cells per area as LMR's), so it costs more only for very large areas. A full 1000-2020 span returns 1,021 rows.

## Sandbox check

`renderTBand` draws only the LMR, HYDE and eVolv2k groups, and `wireTSliders` only touches sliders that exist for them, so GEDA rows are ignored: nothing crashes and nothing is drawn. The Band T badge counts every Band T row, so for a place in the footprint a 100-year span adds 101 to it. (Read from the code; the browser check is Karl's.)

## Needs attention going forward

1. **What the Band T headline should be (deferred, display).** LMR and GEDA rows lead with a weighted mean in `representative_raw`; HYDE rows lead with a sum (an extensive quantity); BasinATLAS multi-basin rows lead with a percentile and no native value. Each Band T row carries its distribution in `detail`, but `project_row` drops `detail` unless `detail=true`, so the public API by default returns only the mean. Decide whether the headline should be the distribution or a percentile; it would change LMR, HYDE and GEDA together, with a deliberate re-capture. Karl: GEDA reads like LMR for now; the display decides what to emphasise.
2. **Deploy checklist.** `temporal.geda_climate` (28,970 cells) must be loaded to the server database, as the other static datasets are, before code that serves GEDA runs there: with `status: served`, a server without the table would fail every Band T request (the footprint query runs first). `public.source_registry` is no longer used and needs no load.
3. **Versioning.** The earlier rule "a minor bump for each additive change" no longer applies before 1.0. `signature_version` "0.5" is the registry-era signature and holds through GEDA; the number moves to 1.0 at the deploy, when Karl names it. `tests/test_live_server.py` stays at "0.4" (it tests prod) until then.
4. **SQL built from polygon text (existing code, not GEDA).** The HYDE, LMR and eVolv2k blocks put the polygon text into the SQL string (`ST_GeomFromText('{geom_wkt}', 4326)`), and the public `scope=area` route checks only that the text starts with POLYGON or MULTIPOLYGON. Probably contained today, because the basin-resolution step parses the same text first through a parameterized call, but not verified against every PostGIS parsing quirk. Production v0.4.2 has the same code. Parameterize the existing blocks (the pattern is `_band_t_query`'s `geom`) or validate the polygon, before anything public relies on this.
5. **GEDA is not on the public basin path** (`/api/signature?scope=basin`: `signature.py`, `temporal.py`, `hyde.py`); that waits for the unification of the two paths' methods.
6. **The effective cell count.** `w_eff` is in GEDA's and HYDE's `detail` but not LMR's. Adding it to the shared histogram (`_weighted_histogram` computes it) would be a one-line change that adds a key to every LMR and basin distribution; noted, not done.
7. **Sandbox display** (item 1 and the Sandbox check above): GEDA is not drawn; the Band T badge counts its rows. For the display work order.
8. **Catalog row wording.** `friendly_name`, `notes` and the empty `concordance_notes` for `geda_scpdsi` follow Karl's draft; the co-variation check behind LMR's `concordance_notes` was not run for GEDA. Closes WO-04 results item 10 (zero-cell handling and parameterized SQL are done for GEDA).
9. **Docs not updated here:** the overview `how_edops_works.md` still lists GEDA as planned; the HYDE 3.4 mentions and `sources` in the schema JSONs and API guide wait for the pre-v1 docs check (WO-04 results items 2 and 17); `documentation/edops_schema_*.json` show no `sources` block or GEDA.
10. **Local table.** `public.source_registry` (WO-04) remains, unused, in the local database.
