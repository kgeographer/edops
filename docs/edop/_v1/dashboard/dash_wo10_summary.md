# dash WO-10 summary: edge cases WHG will hit

2026-11-19. Spec `dash_wo10_edge-cases.md`; record `dash_wo10_results.md`. Branch `dashboard`.

- **Check.** About 8,700 of WHG's 1.5 million places fall in no BasinATLAS basin (the outlines are coarse at coasts); the API answered 404 for them, with three different sentences and no reason. Open water, Tristan da Cunha, Antarctica and the poles also 404; out-of-range coordinates gave the framework's raw error list.
- **Snap.** A point within 5 km of a basin (Karl's choice; 94% of the places within 50 km of one) is moved just inside the nearest basin and the response carries `point_moved` (basin, distance, from, to). Done once, in the engine, for the public basin route, `/api/areas` single basin and ring, the ring geometry route, Context and conjunction. The profile pages' snap uses the same distance (it was 1 km).
- **No basin.** Beyond 5 km: 404 with one sentence on every route ("No basin within 5 km of this point; the nearest is N km away. It may be open water, or outside BasinATLAS coverage") plus `reason` and `nearest_basin_km`. Not pursued further (alpha; a later release can refine).
- **Bad input.** 422 `detail` is a sentence naming the parameter; the old list is in `errors`.
- **Dashboard.** A one-line note on the Signature tab when the point was moved (placeholder wording).
- **Public API changes** for the release notes: listed in the results file (404 becomes 200 within 5 km; new `point_moved`, `reason`, `nearest_basin_km`; 422 `detail` is a string).
- **Tests.** `tests/dashboard/test_edge_cases.py`, 14, using real WHG places. Targeted suites: 683 passed, 0 failed (two older tests updated: the 404 wording, and the page-background test, which still expected the reverted pale colour). No full suite yet.

Needs Karl: the gate (Alexandria, an offshore point, Tristan da Cunha, a bad coordinate, in the Dashboard and against the API); the note's wording.
