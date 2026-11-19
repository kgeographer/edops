# dash WO-10: edge cases WHG will hit

Draft of 19 Nov 2026, for Karl's review. Check first, then fix what needs it. On the `dashboard` branch.

## Goal

Any point a caller sends gets a clear answer, never a bare error: a signature, a signature for a nearby basin with the move stated, or a plain statement that there is no basin there and why. WHG will call the public API from place pages, many of them ports and coastal places.

## Background

- The v1 plan lists edge cases as a Must: coastal points that return 404, open water, no basin, bad coordinates. WO-02 (permalink estimate) noted that a coastal point can 404 on single basin ("known gap"). WO-03 dropped Tristan da Cunha as an example because it has no basin.
- The profile generator already has a moved-point note (S8.3, S8.point), so some snapping exists somewhere.
- WHG's experiments called `/api/signature?scope=basin` at Level 8 with coordinates from its records.

## Items

1. **Check current behaviour.** For each case, record what `/api/signature?scope=basin` (Levels 6 and 8), `/api/areas` and the Dashboard do today: status code, body, what the page shows.
   - a coastal city whose point falls just offshore of its basin (try Alexandria, a few ports, and a point 1 to 2 km offshore of each);
   - a point in open water;
   - a small island with no basin (Tristan da Cunha);
   - a point beyond BasinATLAS coverage (Antarctica);
   - points near the antimeridian and the poles;
   - bad input: out-of-range latitude or longitude, missing or non-numeric values, latitude and longitude swapped (a point that lands in the sea).

   Also say where the existing moved-point logic lives and when it applies.

2. **Fix what needs it.** Where a case gives a bare error or a misleading result:
   - **Near the coast:** use the nearest basin within a set distance, and say so in the response (the distance and that the point was moved), consistent with the profile's moved-point note. Propose the distance from data (for example, how far real port and coastal points in the samples fall from a basin), not from a few motivating cases.
   - **Open water, no basin, outside coverage:** a structured response that says there is no basin and why, with a status code chosen consistently across routes.
   - **Bad input:** a validation error naming the problem.
   - The Dashboard shows each of these as a plain message.

## Provisos

- Keep it short. One check per case, not a sweep. List anything else worth looking into in one line under "Needs attention" and stop there.
- No change to how points inside a basin are handled.
- The Sandbox is unchanged except through shared API code; say if it is affected.
- List any change to the public API's responses (status codes, fields) in the results, for the v1 release notes.

## Deliverables and gate

- `dash_wo10_summary.md`, one page; `dash_wo10_results.md`, with a table: case, behaviour before, behaviour after.
- Tests for each case.

Gate: Karl tries Alexandria, a point offshore, Tristan da Cunha and a bad coordinate in the Dashboard and against the API, and each gets a clear answer.
