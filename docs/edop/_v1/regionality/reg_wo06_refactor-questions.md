# WO-06 (regionality): one engine or two? Assessment of the signature paths

Draft of 2026-11-14.

## Goal

Decide, with evidence, whether to refactor the signature code so that every route computes through one engine. Three questions to answer:

- **(a) Warranted?** Is the divergence between the paths a real problem, or a defensible difference?
- **(b) Too big for now?** What would it take, in hours and risk, before the February delivery?
- **(c) Does delay add cost?** If it waits until after February, does the work get bigger, riskier or more awkward, or does it cost the same later?

This WO is an assessment only: no code changes. It ends with a recommendation and options for Karl and Opus to decide.

## Context

- The public `/api/signature` serves `scope=basin` from its own code (`signature.py`, `temporal.py`, `hyde.py`); `scope=buffer` and `scope=area` go to the engine (`aggregate_band_t` and the areal functions), as does the Sandbox's `/api/areas`.
- After WO-04 and WO-05, the engine path consults the registry and serves GEDA; the basin path does not, and is silent about GEDA (no entry in `sources`).
- Known differences in Band T: LMR nearest cell against overlap weights; HYDE centroid-in-basin against overlap weights; HYDE nearest-step reporting; Band T as a span against a single year depending on route. Bands A–E also differ: the basin path has point elevation, relief and seasonality variables the engine does not.
- Target design for discussion ("one engine, many presentations"): resolve (any scope to a query geometry and basin set), compute (one function per source, registry-gated, full detail), present (each route chooses variables, lean or detailed form, names). Differences that are presentation stay; differences in computation go.
- After February, other developers may take EDOPS on; Karl steps back. Karl's own research use after February does not depend on this change, and his inclination is that the refactor belongs in the v1 roadmap document, not in the v1 scope. This WO tests that inclination with evidence; its recommendation need not agree with it.
- The basin path is not only a public-API matter. Its consumers in the repo: the Sandbox's second request (`/api/signature?scope=basin&bands=ABCE`, feeding the Analysis and Seasonality tabs; never Band T), the Workbench (`workbench.html`, level 8), the WHG profile scripts (`scripts/edop/whg/wo04_fill.py`, `wo10_profiles.py`) and the example and docs generators; `routes_sandbox.py` also imports the basin-path functions.
- The basin response shape (`signature_bands`, `profile_summary`, documented in `documentation/edops_schema_basin.json`) is a contract. Unification would change where values come from, not that shape.

## Part A: the facts

1. **History.** From the git log: when and why each path was written, and when buffer and area scopes were routed to the engine. Short.
2. **Callers.** Who calls each route and scope today: the Sandbox, the Explorer and other pages, the WHG profile generation, the docs' examples, known external users. Which callers would see changed values if `scope=basin` moved onto the engine. Real external traffic is on the production server only (`public.query_log`): Karl runs a read-only query over SSH (counts by scope, bands and use of years; `src=api` rows); the assessment reports what the code shows and what the extract shows, separately.
3. **Differences, by band.** For each band (A–E and T): every difference between the basin path and the engine path, in method, step rules, not-covered behaviour, field names and shapes, and variables offered. For each, classify: **presentation** (belongs in a route's choice of output; would stay), **shape** (field names and nesting of a documented response; a contract that a presentation layer must keep) or **computation** (two answers to the same question; would go). Route rules such as the single-year limit on public buffer and area are presentation (policy), not computation: the engine takes spans.
4. **Size of the change in values.** For the baseline places, what `scope=basin` returns now against what the engine returns for the same basin: how large the differences are. Scope: Band T values (LMR, HYDE) and any A–E variable both paths return, at the baseline places only; the full per-variable comparison is kept for the option chosen. This tells callers what unification would change.

## Part B: the options

5. Describe and estimate each (hours, risk, tests and baselines affected, what callers see):
   - **Full unification now:** every scope on the engine; the basin path's extra A–E variables become engine features offered per route.
   - **Band T now, A–E later:** the basin path's Band T moves onto the engine's source functions (GEDA arrives on every scope); A–E stays as is for now.
   - **Stopgap:** the basin path stays separate but reports GEDA honestly in `sources` (for example `not_applied` with a reason), or gets its own GEDA block.
   - **Defer all:** document the two paths and their differences for the next developer.

   Each estimate must also say: (i) which payload names would win where the paths differ. The catalog's `api_key_s` for LMR is the basin path's naming (`pdsi_series`, `air_series`) while the engine uses `lmr_pdsi`, `lmr_air`, the key gap in the catalog-completeness work order, so the two should be sequenced together; (ii) for the stopgap, the reason to report: today's `not_applied` reasons are span, footprint and coverage, and "this route does not serve it" is not one, so it needs a new reason (for example `not_served_on_route`) or a real `check()` outcome reported without rows.

## Part C: the cost of delay

6. For each option deferred past February, assess what grows:
   - Each further regional source (LBDA and others) written twice or missing from `scope=basin`.
   - After 1.0, changing `scope=basin` values is a breaking change for public callers (deprecation, versioning, notice). Before 1.0 it is not: v1 is a new site and the deployed v0.4.2 stays frozen. Assess how asymmetric this is, given how little public traffic there may be.
   - Two sets of docs, tests and baselines to maintain.
   - Knowledge: the reasons for the current state are clearest now; a new developer meets two paths with no account of why.
   - Anything that makes it cheaper later (for example, less code once something else is retired).

## Part D: recommendation

7. A recommendation with its reasons, stated as one of the options in Part B (or a combination), and what it would mean for the schedule to February.

## Provisos

- No code changes.
- Report facts and estimates; where an estimate is uncertain, say how uncertain.
- Hours are estimates including review time, as in the v1 plan.

## Deliverables

- `reg_wo06_results.md` (Parts A to D, with tables) and `reg_wo06_summary.md` (one page: the three answers and the recommendation).

## Acceptance gate

Questions (a), (b) and (c) each have a direct answer backed by Part A; the options are estimated; the recommendation is stated.

## Adjustments after review (2026-11-14, Claude Code, with Karl)

Changed in place above: the context (Karl's inclination; the consumers beyond the public API; the response shape as a contract); Part A items 2 to 4 (the production query log for callers, the third class "shape", the narrower value comparison); Part B (the catalog naming and the stopgap reason); Part C (the pre- and post-1.0 asymmetry). Karl's wish: if the evidence shows a real benefit and there is time before v1, recommend it for before v1; otherwise recommend it for the v1 roadmap. Code changes remain out of scope.
