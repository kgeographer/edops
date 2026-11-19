# Reply to Stephen on the whgmodal payload proposal: draft

Draft of 19 Nov 2026 (Opus), for Karl to cut. Answers Stephen's email of 19 Nov and `developer/edops-whgmodal-payload-proposal.md` in the WHG repo. Suggest cc Ruth.

---

**Subject:** Re: EDOPS in the WHG beta, and the payload proposal

Hi Stephen (cc Ruth),

That was quick! The beta modal looks good, and the payload proposal is a good working basis. It's close to what EDOPS already returns and to decisions made on this side: a scale on every section (place or whole basin), a `sources` list with reasons, caveats passed through unedited, rule-generated text labelled as such, and raw numbers for you to chart. Let's treat your document as the draft contract and refine it there.

One thing about order: the shape is yours and mine to settle, but what the profile says is still with Ruth and Palak, who have the sample profiles to review. So the sections are slots for now; their content waits on that.

Your questions:

1. **One `series` block per unit:** fine.
2. **Profile at Level 8:** for now, the Level 6 parent basin's profile, with its id, and the section scales saying so. I may generate Level 8 profiles later.
3. **`sources` on every response, including `no_basin`:** yes. The v1 code now gives a `reason` and the distance to the nearest basin when there is none; points within 5 km of a basin are moved to it, and the response says so (`point_moved`).
4. **Series for areas:** summaries only for now.
5. **A `citation` string:** yes, for EDOPS, along with each source's own citation, which EDOPS's source registry already holds.
6. **Logo and terms:** SVG attached. Terms below.

Two things EDOPS needs from the shape:

- **`series.timeline` should be a list keyed by source, not fixed LMR fields.** EDOPS now has regional drought atlases: GEDA (Eurasia, 1000–2020) is served, and LBDA (contiguous US, 0–2025) is coming. Each has its own index and units and must never be pooled with another. A list of series, each with its source id, variables, units, scale and caveats, lets a new source arrive without a schema change.
- **Records with several attestations.** Your beta sends a convex hull as an area. I'd like to think about this with you: one representative point, a centroid, or the set of basins the attestations fall in. The answer changes what the profile can say. Not urgent, but it belongs in the contract.

Smaller points: the version labels will change (the land-use data is HYDE 3.5, not 3.4, and `signature_version` will be 1.0 in v1), and a line on caching would help: EDOPS's server caches `/api/` responses for 6 hours.

**Terms.** EDOPS output combines sources that are free to use with attribution: GEDA, eVolv2k and Cliopatria under CC BY 4.0, BasinATLAS under CC BY 4.0, HYDE under CC BY 3.0, and NOAA's drought atlases with a citation request. EDOPS's own contribution (the profile text, derived values and structure) can be CC BY 4.0. The obligation that matters is carrying the source attributions, which is what the `sources` block and the citation strings are for. Suggested wording for the modal: "Environmental data from EDOPS (Environmental Dimensions of Place Service), Computing Place, Karl Grossner, CC BY 4.0, which draws on the sources listed." I'll confirm the details as the endpoint takes shape.

I'm away 22–30 November (Nepal) and will pick this up properly in early December. The v1 endpoint for you to test should be ready in January.

Best,
Karl

---

## Notes for Karl (not for sending)

- **Licence, from the source registry** (`documentation/EDOPS_source_registry.yaml`): GEDA, eVolv2k, Cliopatria CC BY 4.0; HYDE 3.5 CC BY 3.0; LBDA a NOAA citation request; BasinATLAS "CC BY 4.0 (database as a whole); some attribute columns may be ODbL 1.0", not yet checked against the columns EDOPS serves; LMR has no licence found (NOAA); point elevation is a composite with several attribution requirements (OpenTopoData/Mapzen), and the Open-Meteo fallback is free for non-commercial use only. No single licence covers everything: each source's terms travel with its data. CC BY 4.0 for EDOPS's own layer is consistent with all the attribution licences. **One thing to check before stating terms firmly:** whether any BasinATLAS column EDOPS serves is ODbL, which is share-alike. If so, that column's terms would also apply to anything built from it. I'm not a lawyer; this is a reading of the stated terms.
- **The logo SVG:** check you have one; the draft says "attached".
- **Deliberately not in the reply:** the profile store design, Level 8 compute, the Time series tab. Keep the reply about the payload.
- **Cutting options:** the "two things" and "smaller points" paragraphs could go to a comment on his GitHub document instead, leaving the email short.
