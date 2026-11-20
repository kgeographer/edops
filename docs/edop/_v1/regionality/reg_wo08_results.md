# reg WO-08 results: LBDA, finishing items

2026-11-20. Spec `reg_wo08_lbda-finish.md`; summary `reg_wo08_summary.md`. Branch `lbda`. Follows `reg_wo07_results.md` (section B).

## Item 1: early gaps named by change over time

**What "clearly below" means.** A year is flagged when its coverage is more than **5 percentage points below the coverage of the span's final year** (`LBDA_CLEARLY_BELOW` in `engine.py`). Coverage never falls as the years go on, so the final year is the highest and the flagged years are one run at the start. Why 5 points: coverage steps up whenever a cell enters the area, and one cell can add only a point or two; flagging any step would be noise, and five points is a difference a reader sees. The 0.1 and 0.5 thresholds and the `low_coverage` status are unchanged.

- Engine: the LBDA entry's `sources` note reads, for example, "early years cover less of the area: 150-209 at 77%, against 100% from 210 on" (a range as "50-90%"; several steps give the lowest and highest). When coverage is low throughout and does not change, the note is "covers 30% of the area". `_lbda_coverage_note`.
- Dashboard: the LBDA block shows that same note ("LBDA: early years cover less of the area: ...; read those years with care."), taken from the `sources` block, so the wording has one source. The block's own recomputation from the `low_coverage` status was removed.
- Cases: Santa Fe Level 6 basin, 150 to 300: "150-209 at 77%, against 100% from 210 on" (every year still has status `ok`); Level 8 basin: 64%; 25 km buffer: 36%. Chaco 1100 to 1200: no note. Cahokia 300 to 1000: no note (the span is clipped to 920 to 1000, and the `years` flag says so).
- Tests: in `tests/lbda`: the note for Santa Fe and Chaco through `/api/areas`, five synthetic cases pinning the 5-point rule (a 3-point step is not named; a 6-point step is; two steps; low throughout; low then ok), and the Dashboard block for Santa Fe and Chaco.

## Item 2: LBDA cells under each basin (for the band threshold)

Counted for every basin whose extent lies in the box 24 to 50 N, 125 to 66 W, at a year when every cell has data (1473 or later): the cells overlapping the basin by any area, as the engine counts `n_units`. Basins grouped by the share of their area covered by LBDA cells.

| Basins | Number | Under 5 cells | Under 10 | Under 20 | Median | 10th, 25th, 75th, 90th percentile |
| --- | --- | --- | --- | --- | --- | --- |
| Level 6, coverage 0.5 or more (returned as `ok`) | 932 | 22.4% | 62.9% | 91.6% | 8 | 3, 5, 12, 19 |
| Level 6, coverage 0.1 or more (returned at all) | 971 | 24.0% | 64.2% | 92.0% | 7 | 3, 5, 12, 18 |
| Level 8, coverage 0.5 or more | 10,933 | 90.5% | 99.9% | 100% | 2 | 1, 2, 4, 4 |
| Level 8, coverage 0.1 or more | 11,176 | 90.7% | 99.9% | 100% | 2 | 1, 2, 4, 4 |

`MIN_CELLS_FOR_BAND` is unchanged (5; the spread band is drawn only when every year has at least that many cells). Read against the table: at 5 cells, about 78% of Level 6 basins get a band and about 10% of Level 8 basins; at 10 cells, about 37% and 0.1%; at 20, about 8% and none. The Dashboard's default is Level 6. Karl sets the value.

## Item 3: documentation

An LBDA section in `docsite/data-sources.md` after GEDA's (status, what the data is, what to know, how it is returned including the per-year coverage and the clipped span, licence as the citation request). The Codebook was regenerated (`scripts/edop/docsite/generate_codebook.py`): the `lbda_pmdi` row appears under Band T (16 variables, 15 implemented). The catalog row is now `implemented` (it was `planned`): LBDA is returned by `/api/areas`, the Dashboard and the buffer and area scopes of `/api/signature`, as GEDA's row is; its note says it is not yet on `scope=basin`. The Codebook's hand-written Band T introduction still names LMR, eVolv2k and HYDE only (GEDA is not in it either); left for the docs pass.

## Item 4: baseline cases

Three added to `tests/regionality/baseline.py` and captured with `capture_baseline.py` (it captures only requests without a reference; **no existing reference file changed**): `chaco_canyon_lbda_bandT_1100_1110` (full coverage, 7 kB), `santa_fe_buffer25_lbda_bandT_200_220` (a buffer that gains cells at 210, early years partly covered, with the note; 10 kB), `cahokia_lbda_bandT_900_930` (span clipped to 920 to 930 with the `years` flag; 11 kB). The script rewrote the manifest's capture date and commit for every request on each run; it now keeps the original date and commit and records additions under `added`.

## Tests

`pytest -m lbda`: 40 passed (about 30 s). Regionality, codebook alignment, public API surface and examples: 152 passed (about 64 s), including the 3 new baseline cases.

## Needs attention

1. **Karl sets `MIN_CELLS_FOR_BAND`** from the item 2 table. (Open from WO-07.)
2. **Still open from WO-07, not in this work order:** the placeholder wording; whether `scope=basin` should serve LBDA (waits on the WHG modal contract); the sources-line noise (UI review); the pre-1900 smoothness check against GEDA and the 1900 seam test against LMR (section B of the WO-07 results, left out of this WO); no per-cell skill; the 1900 blend cannot be separated from climate; the cause of the pre-1900 agreement between cells.
3. **Before any deploy of code that serves LBDA,** `temporal.lbda_climate` must be loaded on the server database (`pg_dump -Fc -t temporal.lbda_climate`, `pg_restore`). `lbda` is local and unpushed; the alpha is unchanged.
4. **The Codebook's Band T introduction** is hand-written and does not name GEDA or LBDA.
