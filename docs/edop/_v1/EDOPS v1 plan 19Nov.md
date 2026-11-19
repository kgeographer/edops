# EDOPS v1 plan, Nov 2026 to Feb 2027

Draft of 2026-11-19, revising the draft of 2026-11-09.

## Summary

v1 delivers an endpoint WHG calls for an environmental profile of a place, a reworked public site (splash, Dashboard, Using EDOPS, Data Explorer), at least one worked example that tests the instrument against an established result, and the documentation needed to use and hand over EDOPS.

Since 9 November: the Sandbox was cloned as the Dashboard with a Profile tab, permalinks and GEDA in Band T; the first regional dataset is GEDA (it supersedes OWDA), served through a source registry; a v1 alpha site is deployed for Pitt alongside the sample profile page. The endpoint now waits on Pitt's view of the content. The worked examples have changed order: Pueblo (Chaco to the Rio Grande) is now the primary example, as a known-answer test, which brings LBDA forward; Ukraine becomes an audit of Snyder's environmental premises.

Working time: 19–21 November; 1–6 December; 29 December to early February. The Pitt meeting is proposed for 10–12 February. Build speed is no longer the constraint; review and decision time is, so this plan carries no hour estimates.

## Contract lines

| Scope-of-services line | Status | v1 treatment |
| --- | --- | --- |
| Production hosting on a Hetzner VM (Nginx, PostgreSQL/PostGIS, FastAPI) | Done; a v1 alpha service added | Maintain; document |
| Phase 1 prototype service at a public URL, JSON signature for any coordinate | Done | No change |
| Neighborhood construction for a point | Done: single basin, buffer, basin ring; Cliopatria polities | Endpoint profile uses the core basin plus its ring |
| Phase 1 work plan and signature design specification | Done | No change |
| Live API with parameter controls, including areas and polities | Done except enriched coastality (bathymetry); GEDA in Band T, `sources` block, server time limit added | Propose descoping bathymetry; document Band E as built |
| Public demo page with experimental LLM narrative summaries | The v1 alpha Dashboard is the demo page; the LLM button is still out | Restore the button, fed by the profile's facts only, marked as generated |
| Documented rubric for parameter selection by use-case type | Not started | First case written from the worked examples ("what can be said, on what grounds, from which band") |
| Documented validation with initial correspondence results | Scope unclear | Propose Pueblo as a known-answer test; Chandler–Modelski sensitivity study if ISHI wants more |
| WHG place-portal payload specification | Sample profile page and alpha delivered; endpoint not built | Build after Pitt agrees the content; account for multi-attestation records |
| Platform design configuration for transfer to Pitt/ISHI | Not started | Setup instructions and a handover package |

## Work plan

**Must**
- Edge cases WHG will hit: coastal points that return 404, open water, no basin, bad coordinates. Check status first.
- `/whgmodal` endpoint, once Pitt agrees the content. Includes how a multi-attestation WHG record is served (one point, a centroid, or a set of basins).
- Profile store for all Level 06 basins, built after the endpoint shape is agreed (facts per basin, assembled on request: `profile-store-design-fable.md`).
- LBDA ingested through the registry, for the Pueblo example. Can start before Nepal.
- Worked example: Pueblo, Chaco to the Rio Grande (`rubrics/Pueblo_notes.md`).
- LLM paragraph from the profile's facts; restore the demo button.
- Documentation for v1 (replacing the 0.4 docs where they describe the Sandbox), the endpoint, and handover.
- The harvest: every "Needs attention" list, the deferred items register and the ideas raised in discussion, sorted into done, v1 and roadmap. The roadmap file delivered with v1 comes out of it.

**Should**
- Worked example: Ukraine as an audit of premises (`rubrics/Ukraine_notes.md`), if Pueblo holds.
- Rubric, first case, from the worked examples.
- Time series tab, settlements and single basins (`dashboard/time-series_design note.md`).
- Using EDOPS: intros for Societies, African Regions and WHG (their content is known; Pueblo and Ukraine wait for their examples).
- Dashboard: a distinct look (colour), pending any larger redesign.

**Stretch**
- Profile store for Level 08 basins (190,675). WHG's current calls use Level 8. The same build as Level 06 with level 8; the compute may take a day or more, run in the background, on the Hetzner server or on rented cloud.
- Validation study on Chandler–Modelski settlements, if ISHI asks for it.
- "Show me" guides on Using EDOPS.

## Schedule

| Period | Work |
| --- | --- |
| 19–21 Nov | This plan; edge-case check and, if needed, a work order; start LBDA |
| 22–30 Nov | Away (Nepal) |
| 1–6 Dec | Pitt feedback; edge cases; LBDA; endpoint shape if agreed |
| 7–28 Dec | Travel; Pitt review period |
| 29 Dec – mid Jan | Harvest; endpoint and profile store; LLM paragraph |
| January | Pueblo example; Ukraine if it holds; Time series tab; docs; Level 08 store if time allows |
| Late Jan – early Feb | Handover, roadmap file, v1 deploy |
| 10–12 Feb (proposed) | Pitt meeting |

## Parked or descoped

Not in v1; each becomes an entry in the roadmap file.

- A panel layout for the Dashboard (expandable panels in place of tabs), and its name.
- Areas tab (type a country, get an area signature); switching sources off; rule-written prose about time-varying values.
- Time series for polities and buffers (a polity's boundary changes over a span); comparison of more than two places.
- Profiles for buffers and polities; Band T in the endpoint unless Pitt asks.
- Bathymetry and other enriched coastality.
- Regional datasets beyond GEDA and LBDA.
- A Galicia worked example.
- Batch or multi-place export of raw signatures.
- Unifying the two Band T paths (public basin route and engine path).
- Porting the Workbench content into the Using page in place of frames.
- Mentoring and further development after the February meeting.

## Open questions

**For ISHI and WHG**
- What content they want in the modal: the profile, raw values for figures, Band T for a record's dates.
- How WHG would call for a multi-attestation record.
- What "validation with initial correspondence results" means; whether Pueblo as a known-answer test meets it.
- Is descoping bathymetry acceptable?
- February meeting: confirm 10–12 February, and in person or remote.

**For Karl**
- Keep Ukraine as the second example?
- The LLM paragraph: still Must, or Should?
- The Dashboard's name.
