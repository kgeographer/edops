# reg WO-07 results: LBDA v3 through the registry

2026-11-19 to 20. Spec `reg_wo07_lbda.md`; summary `reg_wo07_summary.md`. Branch `lbda` (cut from `v1`). Basis: `data/lbda_v3/LBDA-v3_characterization.md`.

## Item 1: table and loader

`scripts/edop/regionality/load_lbda.py` (`--dry-run`, `--replace`) loads `data/lbda_v3/LBDA-v3.nc` into `temporal.lbda_climate` (local database): one row per cell with data (3,277), `pmdi real[2026]` (position year + 1, years 0 to 2025, read from the file), NULL before the cell's `first_year`, point and cell geometry, area, the same three indexes as GEDA, the file's md5 in the table comment. The loader refuses a file in which any cell has a gap after its first year. 26 MB.

Check against the netCDF: 4,906,596 non-NULL values (file: the same); min, max, mean and SD equal; 300 random cells equal to 1e-5; six named places (Four Corners, Chaco, Albuquerque, Santa Fe, Cahokia, Boston) equal, with NULL exactly before their first years (0, 0, 0, 210, 920, 1135); cells with data by year equal to the file (722 in year 0, 1,098 in 300, 2,983 in 1000, 3,277 from 1473). Tests: `tests/lbda/test_lbda_table.py`.

## Item 2: registry, catalog, caveats

Registry entry `lbda_v3` (status `served` since item 3; footprint `first_year_column`; coverage rule `per_year`); catalog row `lbda_pmdi` (status `planned`; becomes `implemented` when a release serves it on the public route); caveat texts `lbda_caveat` and `lbda_instrumental` (placeholder wording); `meta.data_sources` gains `temporal_drought_conus` in the code and in both schema JSON files. The registry tests' list of expected ids gained `lbda_v3`.

## Item 3: coverage by year

- `source_registry.check()` judges a `per_year` source year by year: coverage in a year is the share of the query area inside the cells that have a value that year. It never falls, so the years that meet the floor (0.1) are one run to the end of the span; the span is clipped to it (earlier years get no rows). `Decision` gains `requested_span` and `coverage_by_year`. A source with a fixed footprint (GEDA) takes the old path unchanged.
- `sources_block` gains the clipped-span flag, for any source: `years: {requested, returned}` on a `used` entry when the two differ.
- Engine `_band_t_lbda`: one `lbda_pmdi` row per year, each with its own coverage and status (`ok`, or `low_coverage` below 0.5); a year's mean and histogram use only the cells that have a value that year. The entry's note says which years are partly covered.

Cases (25 km buffer, or Level 6 single basin where marked), from the engine and `/api/areas`:

| Case | Result |
| --- | --- |
| Chaco 1100 to 1200 | 101 rows, all `ok`, coverage 1.00 |
| Santa Fe 100 to 300 (25 km buffer) | 201 rows; coverage 0.36 at year 100 rising to 1.00; early years `low_coverage`, later `ok`; note "partly covered" |
| Santa Fe 100 to 300 (Level 6 basin) | 201 rows, all `ok` (coverage 0.77 at year 100) |
| Cahokia 300 to 1000 | span clipped to 920 to 1000 (81 rows); `years: {requested [300, 1000], returned [920, 1000]}` |
| Cahokia 300 to 800 | not applied, `below_coverage_floor` |
| Lviv 1000 to 1100 | LBDA not applied, `outside_footprint`; GEDA as before |
| Chaco -500 to 100 | clipped to 0 to 100 |
| Chaco 2100 to 2200 | not applied, `outside_span` |
| A polygon inside one cell, 1100 to 1103 | each year's value equals the stored cell value (1e-5) |

Timings 0.03 to 0.08 s per call.

**Tests that had to change** (all in `tests/regionality`): the 10 baseline cases and 8 exact-list assertions failed because every Band T response now carries LBDA in its `sources` lists. Fix: the baseline comparison matches the `sources` lists by id and allows added sources (a removed source or a changed entry is still a difference), so **no reference payload was re-captured**; the exact-list tests use `tests/regionality/sources.py`, which filters to the sources that existed at WO-06 and reads later sources' variables from the registry, so adding another source needs no test edits. Six unit tests pin the comparison rule (`test_baseline_sources.py`). The Dashboard's two exact sources-line assertions got the same treatment.

## Item 4: year 0

LMR's table holds 2,001 values per cell with year Y at position Y + 1: years 0 to 2000 (the registry's [0, 2000] is right; CLAUDE.md's "1 to 2001 CE" was wrong and is corrected). LBDA's table has 2,026 values, year Y at position Y + 1, years 0 to 2025. HYDE has a step at year 0 (step 10; then 100, 200, 300). All three treat 0 as 0 CE with no offset between them.

## Item 5: Dashboard

An LBDA block after LMR on the Signature tab's Band T section, built like GEDA's: its own histogram and year slider, the mean line, instrumental years (1900 on) shaded with a legend, "1920 CE · instrumental" under the histogram. Labels say PMDI, June to August, not standardized, cannot be compared with GEDA. Notes for a clipped span, partly covered years and a coarse histogram; the payload's caveat texts. LBDA is in the sources line ("Available for this query: ... LBDA drought"; "Not applied: LBDA drought, because this place is outside its footprint"). The spread band shows only when every year has at least 5 cells (`MIN_CELLS_FOR_BAND`, a placeholder until the time-series design sets it from the data; LBDA only, GEDA unchanged). All wording is placeholder (yellow). The shading function and the year stamp are shared with GEDA and handle both. Browser tests in `tests/lbda/test_lbda_block_ui.py` (5). The browser-test server fixture moved from `tests/dashboard/conftest.py` to `tests/conftest.py` so both folders share it. Karl looked at it in a browser (Chaco).

## Item 6: the public basin route (report only; nothing built)

`/api/signature?scope=basin` with Band T builds its Band T from older code for LMR and HYDE (`app/db/temporal.py`, `app/db/hyde.py`: nearest cell, centroid rule) and serves GEDA through the engine: `_geda_for_basin` calls `band_t_geda_for_point`, which runs the engine's GEDA block on the containing basin's polygon (so its numbers match `/api/areas?scope=single_basin`) and turns the rows into a compact `geda_scpdsi` block (status, n_cells, coverage, mean, min, max, a series of year, value, p10, p90 and an observed flag, the caveat). Its decision then goes into the `sources` block.

Today for Chaco on that route (checked): no LBDA block; `sources.used` and `sources.not_applied` do not mention LBDA (the route lists only the decisions it builds); `meta.data_sources` does list LBDA (it lists every source).

Serving LBDA there would take, about the size of item 2:
1. `band_t_lbda_for_point` in the engine (three lines, like GEDA's), and `_lbda_for_basin` in `routes_common.py` that builds an `lbda_pmdi` block: the same fields as GEDA's with `pmdi`, an `instrumental` flag per year, a per-year `coverage`, the span actually returned; or `{status: not_applied, reason}`.
2. The LBDA decision added to the route's list of decisions, so the `sources` block reports it (and the clipped-span flag).
3. Documentation: the route's docstring, `edops_schema_basin.json` (example block and a note), the generated API guide (`docsite/api.md`), the data-sources page.
4. Tests modelled on `tests/regionality/test_public_basin_geda.py` (in `tests/lbda`), and optionally baseline cases for a US point.
5. Decisions: the public `from_year` and `to_year` are documented as 0 to 2000 (LMR's range) while LBDA runs to 2025; a full 0 to 2025 span returns up to 2,026 series items (about 100 KB), so a size limit or a note may be wanted. The block shape (the compact series against full rows) is a public API commitment.
Numbers would match `/api/areas`, as for GEDA; the LMR and HYDE difference between the two paths (unchanged) remains.

## Public API changes (for the release notes; none released)

- `/api/signature` (scope=basin) responses: unchanged apart from the new `meta.data_sources.temporal_drought_conus` line. Scope=buffer and area (engine path) now include `lbda_pmdi` rows for US places and an LBDA entry in `sources` (used, or not applied with a reason). Any `sources` entry may carry `years` when a span was clipped.
- `Decision` (internal) gains two fields.

## Deploy note

`temporal.lbda_climate` must be loaded on the server database before code that serves LBDA runs there (the v1 alpha shares the live `cedop`): `pg_dump -Fc -t temporal.lbda_climate` locally, `pg_restore` on the box, as for GEDA. Nothing from this work order is on the alpha: `v1` has not been pushed and `lbda` is a local branch.

## Needs attention

Reorganized for Opus on 20 Nov (the earlier numbering is in brackets). Nothing in A, B or C has been started; the branch `lbda` stays unmerged until these are settled.

### A. Decisions (Karl, with Opus's view)

(The untracked whgmodal reply draft listed here earlier was committed on 20 Nov; it belongs to the WHG modal work and stays in `docs/edop/_v1/whgmodal/` until that endpoint is built.)

1. **Wording** [1]. The block's text, the two caveat texts (`lbda_caveat`, `lbda_instrumental`) and the notes are placeholder (yellow in the Dashboard). The caveats carry: not standardized and not comparable with GEDA; the pre-1900 smoothness; modest skill and no per-cell skill; the 1900 blend; thinner coverage early.
2. **Thresholds** [2, 10]. The spread band needs at least 5 cells in every year (`MIN_CELLS_FOR_BAND`, a placeholder; the design note says the threshold is to be set from the data). The coverage rule is GEDA's, copied: below 0.1 no value, 0.1 to 0.5 flagged `low_coverage`, from 0.5 `ok`. Consequence: a basin with early gaps is not flagged. At Santa Fe in year 150 a Level 6 basin has 77% coverage and a Level 8 basin 64%, so no note, although a quarter to a third of the area has no data before 210 CE; a 25 km or 50 km buffer there (36%, 43%) is flagged. The work order's gate case (Santa Fe 150 to 300) shows its note only with a buffer.
3. **The public basin route** [7]. It does not serve LBDA (the work order said report only). Serving it is about the size of item 2: a helper, a block builder, the decision in the `sources` block, schema and API-guide documentation, tests. Open choices: the public `from_year` and `to_year` are documented as 0 to 2000 while LBDA runs to 2025; a full span returns up to 2,026 series items (about 100 KB); the block shape is a public API commitment.
4. **The sources line** [6]. "Not applied: ... outside its footprint" now appears for GEDA or LBDA on almost every query. Karl: leave it to the UI review.

### B. CC can do these (each small; none started)

6. **Flag early gaps by how coverage changes over time** [10]. Note the years whose coverage is more than a few points below the later years' (for example "150 to 209: 77 to 95% of the area, against 100% from 210"), in the engine's `sources` note and the Dashboard block, leaving the 0.5 `low_coverage` status as it is. This would flag the Santa Fe basin without changing the thresholds. About an hour: one engine note, one Dashboard note, two tests.
7. **Data for the band threshold** [2]. The number of LBDA cells under each Level 6 and Level 8 basin across the contiguous US (what share has fewer than 5, 10, 20), so the threshold is set from the data, not from example places. A short query and a table.
8. **Is the pre-1900 smoothness general?** [3]. Pairwise correlation between cells against distance, before and after 1900, in several LBDA regions (West, Plains, East); and the same for GEDA over Lviv- and Kyiv-sized areas. Says whether the Band T histogram across cells needs different presentation for reconstructed years, and whether it is LBDA's method or a property of drought atlases. About an hour; a table.
9. **An indirect test of the 1900 blend** [5]. Correlate LBDA's Four Corners series with LMR's PDSI (an independent reconstruction) in 1800 to 1899 against 1900 to 1999 and later: a stable relationship suggests no seam; a break at 1900 would be a flag. Indicative only. A short script.
10. **Documentation** [8]. A LBDA section in `docsite/data-sources.md` modelled on GEDA's, and regenerating the Codebook (the catalog row is `planned`, and becomes `implemented` when a release serves LBDA). Small.
11. **Baseline cases** [9]. The regression baseline has no reference with LBDA rows. Add two or three US cases (for example Chaco, Santa Fe as a buffer, Cahokia clipped) as additions; existing references are not re-captured. Needs a check that the capture script can add cases without rewriting the others.

### C. Can only be recorded (nothing to fix from here)

12. **No per-cell skill in the file** [4]. The 2010 paper's Fig. 6 is the only place (read by eye). Authors' or NCEI calibration and verification grids may exist; CC cannot load the NCEI page, so Karl would have to look. The caveat says so in words.
13. **The 1900 blend cannot be separated from climate** [5]. Version 3 has no overlap years; B9 gives indirect evidence only.
14. **Why neighbouring cells agree before 1900** [3]. The cause (shared tree-ring chronologies) is CC's reading and is not stated in the 2010 paper; the method paper (Cook et al. 1999) or the authors would confirm it.
