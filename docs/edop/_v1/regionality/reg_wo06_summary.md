# WO-06 summary: one engine or two?

Spec: `reg_wo06_refactor-questions.md`. Record: `reg_wo06_results.md` (Parts A to D, with tables). Assessment only; no code changed.

## The three answers

**(a) Is the divergence a real problem?** Partly. For bands A-E the two paths return identical values for every variable they share (checked on four places); they differ in which variables they offer, their names and their shape, which are presentation and a response contract, defensible. For Band T the divergence is real: LMR (nearest cell against overlap-weighted) differs by under about 10% of the series' spread, HYDE (whole cells whose centroid is in the basin against overlap-weighted) differs by up to 19% on single variables, and the basin path's HYDE returns nothing for about 7% of level-8 basins (a sample of 200) where the engine returns almost always. The basin path also knows nothing of GEDA and says nothing about it in `sources`.

**(b) Too big for now?** Full unification: yes (40 to 70 hours at high risk; it touches the Sandbox's Analysis and Seasonality tabs and the WHG profile pipeline, for little gain in A-E). Moving only Band T onto the engine: about 12 to 20 hours, moderate risk. No in-repo caller asks the basin path for Band T. An honest-reporting stopgap: 2 to 3 hours.

**(c) Does delay add cost?** For A-E, little. For Band T, yes, mostly as duplicated work: each further regional source is written twice or missing from `scope=basin`. The breaking-change cost at 1.0 is close to nil in practice: the production `query_log` shows 41 `/api/signature` calls in three weeks, 12 with Band T, none since 2026-10-29, clustered around deploy days (probably the project's own testing).

## Recommendation

1. Move Band T (LMR, HYDE, and GEDA arriving for free) onto the engine's source functions before 1.0, as its own work order, if the v1 plan has room (about 2 to 3 working days).
2. If it does not fit, do the stopgap now (2 to 3 hours) and make the Band T move the first roadmap item after 1.0. Given how little external use the query log shows, waiting costs little in breakage; the cost is duplicated work for each regional source added meanwhile.
3. Do not unify A-E now. Put it on the v1 roadmap, to be decided with the dashboard and the catalog-completeness work order.
4. Write a short "two paths" page for the next developer from the results.

This agrees with Karl's inclination on the broad refactor and differs only on the narrower Band T move, where delay adds cost.

## Open

Who made the 41 logged calls (a `user_agent` query would show); the unproven hour estimates.
