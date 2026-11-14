# Results 02: GEDA on the public basin route (follow-on to WO-06)

Follows `reg_wo06_refactor-questions.md` and its results (`reg_wo06_results.md`). Branch `geda`. No separate WO spec: Karl's instruction was that adding `T` to the bands of an `/api/signature` call returns GEDA as well as the others, where the place and years fit what the source can provide. This is WO-06's option 3b (the basin path runs the engine's GEDA block and adds a key) together with 3a (an honest `sources` entry). The broader refactor stays on the roadmap.

Commits: b5759cd (code and tests), 76c1197 (baseline), 49ff07e (docs); all pushed. Full suite: 768 passed, 21 skipped, no failures.

## What was built

- **Engine entry point.** `band_t_geda_for_point(lat, lon, level, from_year, to_year, conn)` in `engine.py`: resolves the basin containing the point with the engine's own lookup (`resolve_single_basin`), takes its polygon, and runs the existing `_band_t_geda` block. The numbers therefore match `/api/areas?scope=single_basin` (a test compares them year by year, including p10 and p90).
- **Route.** In the `scope=basin` branch of `routes_common.py`, when T is requested, `_geda_for_basin()` calls it and shapes the result into `signature_bands.T.geda_scpdsi` (`temporal.geda_scpdsi` with `flat=true`):
  - Applied: `{status: "ok" | "low_coverage", n_cells, coverage, mean, min, max, series: [{year, scpdsi, p10, p90, observed?}], caveat}`. `observed: true` appears only on years from 1990. No histograms, so the block stays compact (101 years is a few kilobytes; the full 1000-2020 span is 1,021 small items).
  - Not applied: `{status: "not_applied", reason}` with `outside_footprint`, `outside_span` or `below_coverage_floor`.
  - A source the registry leaves out silently (not permitted, not served) gives no block.
- **`sources` block.** The GEDA decision is added to the route's decisions, so GEDA is `used` (with the note "covers 49.8% of the area" when low coverage) or `not_applied` with its reason. Before this the basin response said nothing about GEDA.
- **Key name.** `geda_scpdsi`, the catalog key and the engine's payload name, so the basin response creates no new naming mismatch (LMR's basin key `pdsi_series` against the engine's `lmr_pdsi` is the existing one). A later regional source would add one key the same way.
- **Single year not required.** Considered and rejected: the single-year rule on public buffer and area exists for payload size (rows with histograms per year), and the route's comments describe `scope=basin` Band T as a compact time series. A GEDA that accepted only one year would have broken that expectation within the same block. Spans are accepted and clipped to 1000-2020.

## Checks

- Tbilisi 1150-1250: 101 years from 25 cells, status ok, in `sources.used`. Timbuktu: `outside_footprint`. Span 500-900: `outside_span`. Span 980-1010: years 1000 to 1010. Span 1985-1995: `observed` from 1990. Level 8 works. Libya edge point: `low_coverage`, coverage 0.498. A basin at coverage 0.067: `below_coverage_floor`. Flat mode carries the block under `temporal`. No Band T: no GEDA anywhere.
- Tests: `test_public_basin_geda.py` (11); three public-basin `sources` tests updated (Timbuktu now reports GEDA as `outside_footprint`).
- Baseline: two new references for the public basin route's Band T, which had none (`tbilisi_public_bandT_1150_1250`, `timbuktu_public_bandT_1236_1240`). Additions only; no existing reference re-captured; `signature_version` stays "0.5".
- Docs: the route's response text and the regenerated `docsite/api.md`; the basin schema JSON (a `geda_scpdsi` entry, shown for the Timbuktu example, with a note giving the applied shape); the docsite GEDA status line.
- One mistake caught on the way: the basin response's `id` is a short internal integer (for example 5023), not the hybas id. Using the engine's own point lookup avoids it.

## Needs attention going forward

1. **Mixed methods in one basin response.** LMR keeps the nearest cell and HYDE its centroid rule, while GEDA uses the overlap-weighted method; neither is wrong, but they are not alike (WO-06, Part A3, gives the sizes of the differences for LMR and HYDE). Not yet said in the docs. Unifying Band T onto the engine's blocks (the WO-06 recommendation) remains a roadmap item; GEDA's block and key would stay as they are.
2. **Deploy checklist, now wider.** `temporal.geda_climate` must be loaded to the server database before this code runs there. With this change the public basin route also depends on it: a Band T basin request on a server without the table would fail where it worked before. A silent fallback was not added, so the failure would be visible.
3. **`meta.data_sources` does not list GEDA.** It is slated for retirement at 1.0; `sources` carries GEDA's name, version, citation and licence.
4. **The single-year limit on public buffer and area** is unchanged. It is a route rule; lifting it would need those scopes to return lean series, not full rows with histograms. Roadmap.
5. **Docs not updated here:** the guide pages that describe Band T (`sandbox/reading-a-signature.md` and others), `documentation/edops_schema_area.json`, and the overview `how_edops_works.md`, for the pre-v1 docs check. The cheat sheet needs nothing: the Sandbox's basin request never asks for T.
6. **Cost per request.** One more database connection and query per basin Band T request: about 0.01 to 0.05 s for a basin (WO-05 timings).
