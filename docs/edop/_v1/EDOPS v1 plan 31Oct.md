# EDOPS v1 plan, Nov 2026 to Feb 2027

Draft of 2026-10-31.

## Summary

v1 delivers a live endpoint that WHG calls to get a short environmental description of any place, plus the documentation needed to use and hand over EDOPS. The earlier plan for a new Dashboard page is replaced by the existing Sandbox, renamed and given a Summary panel that uses the same code as the endpoint.

At 6 hours a day in November and January, about 366 hours are available. The plan below uses about 235 at midpoint estimates and leaves the rest as contingency. December is a break. Hour figures are estimates, include review and decision time, and assume Claude Code does most of the coding.

## Contract lines

Four of the ten scope-of-services lines are done. Three are done apart from one item each (bathymetry, the LLM button, transfer documentation), and three are not started: the WHG payload, the rubric and validation.

| Scope-of-services line | Status | Proposed v1 treatment |
| --- | --- | --- |
| Production hosting on a Hetzner VM (Nginx, PostgreSQL/PostGIS, FastAPI) | Done | Maintain; document |
| Phase 1 prototype service at a public URL, JSON signature for any coordinate | Done | No change |
| Neighborhood construction for a point | Done: single basin, buffer, basin ring. Bonus: Cliopatria polity signatures | Endpoint uses single basin (ring optional); buffer and polity stay in the Sandbox |
| Phase 1 work plan and signature design specification | Done | No change |
| Live API with parameter controls, including areas and polities | Done except enriched coastality (e.g. bathymetry) | Propose descoping bathymetry; document Band E as built and name a candidate source as future work |
| Public demo page with experimental LLM narrative summaries | Done; the LLM button is commented out | Restore the button; later feed it the endpoint's fact list |
| Documented rubric for parameter selection by use-case type | Not started | Build from the Workbench worked examples |
| Documented validation with initial correspondence results | Scope unclear | Ask ISHI what is expected; minimal version is a labelled initial sensitivity study on documented settlements |
| WHG place-portal payload specification | Not started | Core of v1: a single-basin endpoint WHG calls, with crosswalk, sentences, samples and a review round |
| Platform design configuration for transfer to Pitt/ISHI | Repo documentation | Setup instructions and a handover package |

## Work plan

Must and Should items total about 235 hours at midpoint estimates; Stretch items are taken only if hours hold.

| Tier | Item | Hours (estimate) |
| --- | --- | --- |
| Must | Fix coastal points that return 404, plus other edge cases WHG will hit (open water, no basin, bad coordinates) | 15 to 25 |
| Must | Crosswalk for the 52 single-basin rows: friendly name, units, what high means, what zero means | 25 to 35 |
| Must | Sentence set and fact list for a single basin: numbers, no verdict words (ring optional) | 30 to 45 |
| Must | Endpoint WHG calls: contract, versioning, caching, errors, about ten sample places including ports, one review round with WHG and ISHI | 35 to 50 |
| Must | LLM paragraph generated from the fact list only, marked as generated; restore the demo button first | 15 to 25 |
| Must | Endpoint and handover documentation, including transfer setup | 20 to 30 |
| Should | Non-global data, design only: footprint index of which datasets cover which basins, a separate addenda section in the payload, a cue in the interface | 30 to 45 |
| Should | Sandbox renamed Dashboard: Summary panel at the top of the Signature tab using the endpoint's sentence code, plus a short intro | 20 to 30 |
| Stretch | First regional dataset ingested as a pilot (tree-ring drought atlas is the candidate; needs aggregation to basins) | 40 to 70 |
| Stretch | Workbench worked example (Ukraine, Galicia, or Ancestral Puebloan), each | 25 to 35 |
| Stretch | Parameter-selection rubric, built from the worked examples | 20 to 30 |
| Stretch | Validation study, once ISHI says what it means | to be sized |

## Schedule

Proposed dates, November 2026 to January 2027.

| Item | Start | End |
| --- | --- | --- |
| Edge-case fixes | 2 Nov | 13 Nov |
| Crosswalk, sentences, endpoint | 9 Nov | 27 Nov |
| Milestone: spec and samples to WHG and ISHI | 27 Nov | 27 Nov |
| December break; WHG and ISHI review period | 1 Dec | 31 Dec |
| Revisions and LLM paragraph | 4 Jan | 15 Jan |
| Docs, handover, Summary panel | 11 Jan | 29 Jan |
| Non-global design, stretch items | 18 Jan | 29 Jan |

November carries the Must items, so the endpoint contract and sample places can reach WHG and ISHI by about 27 November (proposed). Their review runs through the December break. January covers revisions, the LLM paragraph, documentation and handover, the Summary panel, and whichever stretch item the remaining hours allow. The Pitt meeting is in February; its date is not set.

## Parked or descoped

These are not in v1. Each gets a short entry in a Future work document in the repository, with the cheat sheet and the WO-02 results as the starting evidence.

- A new Dashboard page designed from scratch, and a generic landing page for all kinds of users.
- Buffer and polity statements in the endpoint. Buffers produced a disproportionate share of the awkward cases in the WO-02 results.
- Band T statements in the endpoint (the temporal band). Documented as an extension.
- Bathymetry and other enriched coastality measures.
- Regional datasets beyond the first pilot.
- Mentoring and further development after the February meeting. Questions about variables, sources, payloads and methods will still be answered.

## Open questions

**For ISHI**

- What does "validation with initial correspondence results" mean in practice, and what would count as sufficient?
- Is descoping bathymetry acceptable, with Band E documented as built?
- Is the plan to serve WHG from a Sandbox with a Summary panel, in place of a new Dashboard page, acceptable?
- Which stretch item matters most: the regional dataset pilot, a worked example, or the rubric?
- February meeting: dates, and in person or remote?

**For Karl**

- Is the Summary panel worth about 20 to 30 hours, or should those hours go to the regional pilot?
- Which regional dataset first, and is the tree-ring atlas still the choice?
- Are 6-hour days sustainable in January, or should the plan assume less?
- Who on the WHG side reviews the payload contract, and by when?
- 