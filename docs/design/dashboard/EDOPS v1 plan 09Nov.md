# EDOPS v1 plan, Nov 2026 to Feb 2027

Draft of 2026-11-09, revising the draft of 2026-10-31.

## Summary

v1 delivers a live endpoint that WHG calls to get a short environmental description of any place, plus the documentation needed to use and hand over EDOPS. The earlier plan for a new Dashboard page is replaced by the existing Sandbox, renamed and given a Summary panel that uses the same code as the endpoint.

v1 also ingests a first regional dataset, and pairs it with one worked example that depends on it. The Old World Drought Atlas (OWDA) is the pilot dataset, and Ukraine is the first worked example: OWDA covers Ukraine, and the European Russia Drought Atlas (ERDA) overlaps it, so the dataset gives the example its evidence and the example shows why regional data matters. A Southwest US example (Chaco to the Rio Grande) would follow with the Living Blended Drought Atlas (LBDA) if hours allow, and otherwise goes on the roadmap.

Working time falls in three blocks: 2 to 21 November, 1 to 6 December, and 29 December to early February. That is about 360 hours at 6 hours a day, roughly the same as the 31 October plan. The plan below uses about 290 at midpoint estimates and leaves the rest as contingency. Hour figures are estimates, include review and decision time, and assume Claude Code does most of the coding.

## Contract lines

Four of the ten scope-of-services lines are done. Three are done apart from one item each (bathymetry, the LLM button, transfer documentation). The WHG payload is under way; the rubric and validation are not started.

| Scope-of-services line | Status | Proposed v1 treatment |
| --- | --- | --- |
| Production hosting on a Hetzner VM (Nginx, PostgreSQL/PostGIS, FastAPI) | Done | Maintain; document |
| Phase 1 prototype service at a public URL, JSON signature for any coordinate | Done | No change |
| Neighborhood construction for a point | Done: single basin, buffer, basin ring. Bonus: Cliopatria polity signatures | Endpoint profile uses the core basin plus its ring; buffer and polity stay in the Sandbox |
| Phase 1 work plan and signature design specification | Done | No change |
| Live API with parameter controls, including areas and polities | Done except enriched coastality (e.g. bathymetry) | Propose descoping bathymetry; document Band E as built and name a candidate source as future work |
| Public demo page with experimental LLM narrative summaries | Done; the LLM button is commented out | Restore the button; later feed it the endpoint's fact list |
| Documented rubric for parameter selection by use-case type | Not started | Write up the parameter choices made for the Ukraine worked example as a first case; generalization is future work |
| Documented validation with initial correspondence results | Scope unclear | Ask ISHI what is expected; minimal version is a labelled initial sensitivity study on documented settlements (Chandler–Modelski) |
| WHG place-portal payload specification | Under way | Core of v1: an endpoint WHG calls, with crosswalk, sentences, a sample profile page and a review round |
| Platform design configuration for transfer to Pitt/ISHI | Repo documentation | Setup instructions and a handover package |

## Work plan

Must and Should items total about 290 hours at midpoint estimates; Stretch items are taken in the order listed, and only if hours hold.

| Tier | Item | Hours (estimate) |
| --- | --- | --- |
| Must | Fix coastal points that return 404, plus other edge cases WHG will hit (open water, no basin, bad coordinates) | 15 to 25 |
| Must | Crosswalk for the 52 single-basin rows: friendly name, units, what high means, what zero means | 25 to 35 |
| Must | Sentence set and fact list for the core basin and ring: numbers, no verdict words | 30 to 45 |
| Must | Endpoint WHG calls: contract, versioning, caching, errors, about ten sample places including ports, a sample profile page, one review round with WHG and ISHI | 35 to 50 |
| Must | LLM paragraph generated from the fact list only, marked as generated; restore the demo button first | 15 to 25 |
| Must | Endpoint and handover documentation, including transfer setup | 20 to 30 |
| Must | First regional dataset ingested as a pilot: OWDA, aggregated to basins, served in the payload's addenda section (ERDA is the natural second) | 40 to 70 |
| Should | Non-global data design: footprint index of which datasets cover which basins, the addenda section in the payload, a cue in the interface | 30 to 45 |
| Should | Sandbox renamed Dashboard: Summary panel at the top of the Signature tab using the endpoint's sentence code, plus a short intro | 20 to 30 |
| Stretch | Worked example 1: Ukraine, using the OWDA pilot (and ERDA if ingested); research question drawn from Timothy Snyder's account of Ukraine's place in world history | 25 to 35 |
| Stretch | Validation study: initial sensitivity study on Chandler–Modelski settlements, once ISHI says what it means | 20 to 30 |
| Stretch | Parameter-selection rubric, first case, written up from worked example 1 | 10 to 20 |
| Stretch | Worked example 2: Southwest US, Chaco to the Rio Grande; needs LBDA as a second regional dataset | 25 to 35, plus LBDA ingest |

## Schedule

Proposed dates, November 2026 to February 2027.

| Item | Start | End |
| --- | --- | --- |
| Edge-case fixes | 2 Nov | 13 Nov |
| Crosswalk, sentences, endpoint | 9 Nov | 21 Nov |
| Milestone: sample profile page and samples to WHG and ISHI | 21 Nov | 21 Nov |
| Away (Nepal) | 22 Nov | 30 Nov |
| Revisions from early feedback | 1 Dec | 6 Dec |
| Travel; WHG and ISHI review period | 7 Dec | 28 Dec |
| Revisions and LLM paragraph | 29 Dec | 15 Jan |
| Regional pilot (OWDA) and worked example 1 (Ukraine) | 4 Jan | 29 Jan |
| Docs, handover, Summary panel | 11 Jan | 5 Feb |
| Validation and remaining stretch items | 18 Jan | 5 Feb |

November carries the endpoint Must items, so the sample profile page can reach WHG and ISHI before the Nepal trip. Their review runs through December. January covers revisions, the LLM paragraph, the regional pilot with its paired worked example, documentation and handover, the Summary panel, and whichever further stretch items the remaining hours allow. The Pitt meeting is in February; its date is not set.

## Parked or descoped

These are not in v1. Each gets a short entry in a Future work document in the repository, with the cheat sheet and the WO-02 results as the starting evidence.

- A new Dashboard page designed from scratch, and a generic landing page for all kinds of users.
- Buffer and polity statements in the endpoint. Buffers produced a disproportionate share of the awkward cases in the WO-02 results.
- Band T statements in the endpoint (the temporal band). Documented as an extension.
- Bathymetry and other enriched coastality measures.
- Regional datasets beyond the first pilot, except LBDA if worked example 2 goes ahead.
- A Galicia worked example.
- Batch or multi-place export of raw signatures. Users who want raw data are expected to script repeated requests and parse the JSON; a batch export is a roadmap item.
- Mentoring and further development after the February meeting. Questions about variables, sources, payloads and methods will still be answered.

## Open questions

**For ISHI**

- What does "validation with initial correspondence results" mean in practice, and what would count as sufficient?
- Is descoping bathymetry acceptable, with Band E documented as built?
- Is the plan to serve WHG from a Sandbox with a Summary panel, in place of a new Dashboard page, acceptable?
- Is pairing the regional pilot with a Ukraine worked example the right priority, ahead of the rubric?
- February meeting: dates, and in person or remote?

**For Karl**

- Is the Summary panel worth about 20 to 30 hours, or should those hours go to worked example 2?
- What is the research question for worked example 1? (Start from the Snyder material: separate the environmental premises EDOPS can speak to from the historical inferences built on them.)


## Parked ideas

Ideas that surface during the work, tagged v1 (could fit before February), roadmap (after) or undecided. The project-wide `docs/design/deferred_items_register.md` is still to be reviewed.

- **Permalink to a place in the Sandbox (the Dashboard in v1).** Read `lat`, `lon`, `name`, `scope` and `level` from the URL and run Get signature on load, so a link opens a place's full signature. The Sandbox reads only `?tab=` today. For the profile page it would replace, or sit beside, the raw-JSON button. Undecided; not in the plan above.
- **Absolute URLs for the profile page's buttons.** The stored buttons use site-relative URLs. A WHG modal on another origin needs `https://edops.computingplace.org/...`. Small; v1, once the modal's embedding is known.
- **Readable signature view.** A formatted signature with a spinner, in place of the raw JSON link. Roadmap.
- **Wikipedia link on the ecoregion name.** The ecoregion name links to OneEarth now; Wikipedia remains a button. Waiting on the repair of flagged Wikipedia links (see the open items file). Undecided.
