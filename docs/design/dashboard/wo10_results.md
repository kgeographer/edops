# WO-10 results

Sample profile page at `/profiles` (branch `whg-profile-page`, local, not pushed). What was built is in `wo10_summary.md`. This file holds the findings and the questions for Opus.

## Wording problems found

Both are in `profile_templates.md` wording, so any fix is a version bump (v21) with a Changes line, on Karl's word.

**1. Land cover percentages can add up to more than 100% (S5.1a, S5.1b, S5.1c).**
The sentence reads as one partition of the basin: "about 2% of the basin is cropland and 49% is pasture; the commonest other cover is shrub cover, closed-open, deciduous (with or without sparse tree layer), at about 53%." That is 104%.

Cause: two datasets in one sentence. Cropland and pasture are BasinATLAS land-use extents (Band D, `crp_pc_sse`, `pst_pc_sse`). "The commonest other cover" is the largest GLC2000 class (`glc_pc_s01` to `s22`) other than "cultivated and managed areas" (`wo07_classes.glc_other`). Pasture is a land-use figure and covers land that GLC maps as shrub, herbaceous or bare, so "other" means other than GLC's cultivated class, not other than the cropland and pasture just stated.

Of the nine places with a basin, two exceed 100%: Chaco Canyon (1% + 66% + 59% = 126%) and Santa Fe (2% + 49% + 53% = 104%). The other seven stay under 100% but carry the same overlap. Poltava's is milder: 64% cropland, then "the commonest other cover is mosaic: cropland/shrub and/or herbaceous cover".

Options:
- Reword S5.1c to say what it is: "In the land cover map, the commonest class other than cultivated land is {label}, at about {share}%."
- Add a sentence to "About these figures" that the cropland and pasture shares and the land-cover classes come from different datasets and can overlap.
- A rule that drops S5.1c where the stated percentages exceed 100%. Simple, but it hides information where the overlap is most interesting.

CC suggests the first two together.

**2. "Permafrost extent is zero here and so has no percentile" (About these figures).**
The page shows no percentiles, so the sentence refers to nothing the reader can see. To check: whether it is a leftover from the full modal text, and whether it should appear at all in this profile.

## Open questions for Opus

**A. The preview page and the `/whgmodal` endpoint are two tasks.**
The page previews the prose and what is generated from data. The endpoint is separate work: Stephen Gadd will call it from a button in WHG and format the response himself. The stored record behind the page's "Profile as JSON" button (about 33 KB per place: units, template segments and lines, slot values, fill notes, provenance) is the generator's own store, not a design for a consumer. Decisions needed:
- the shape of the `/whgmodal` response. CC's view: place, basin id, template version and date; sections with `id`, `title`, plain `text` and `runs` (the text with the OneEarth links); links as absolute URLs; the OSM/ODbL credit as a field wherever river names appear; and data for figures. Template lines, slot values, unit traces and fill notes stay out, with an optional `?explain=1`.
- whether the page keeps a "Profile as JSON" button, and what it should open meanwhile.

**B. Monthly precipitation and temperature in the response.**
The page draws a chart under Climate from `monthly` (12 values each, mm and °C, basin level, from the signature's `pre_mm_monthly` and `tmp_dc_monthly`). The caption tells Stephen that a portal can draw it from the 24 monthly values. Decision: whether the response always carries the arrays, with units and a note that they describe the basin, not the point. This is the "monthly arrays in the payload" item (P2) that WO-10 listed as out of scope.

**C. Point units and basin units.**
Some units speak about the point (elevation, point ecoregion, the distance a point was moved to the nearest basin) and some about the basin. A per-basin store cannot carry the point ones. `/whgmodal` would take WHG's lat/lon and combine a stored basin record with live point units, which needs a live elevation call. The `scope` tag on each unit in the stored record marks which is which. The split decides how the endpoint is built.

**D. Permalink to a place in the Sandbox (the Dashboard in v1).**
Read `lat`, `lon`, `name`, `scope` and `level` from the URL and run Get signature on load. The Sandbox reads only `?tab=` today. Recorded under Parked ideas in `EDOPS v1 plan 09Nov.md`.

**E. The S9 frame still describes a OneEarth button.**
The ecoregion name now links to its OneEarth page, and the page has no OneEarth button. `S9.frame` and `S9.frame.nowiki` in `profile_templates.md` still list `[Ecoregion on OneEarth: {S9.4}]`, and the generator reads that line to decide whether to build the URL. Needs a v21 edit with the generator changed to match, and a decision on whether the Wikipedia link should also move onto the ecoregion name (it waits on the repair of flagged Wikipedia links).

## Notes

- **Full signature link.** The button opens the public `/api/signature?scope=basin&level=6&lat=…&lon=…`. The response is compact JSON, and `geom_geojson` (the basin outline, about 14 KB of 21 KB) is a JSON string inside the JSON, so a reader scrolls past it. Left as it is by decision: a reader of raw JSON can pretty-print it.
- **Template view and the markdown.** The generator's markdown for each place equals `wo09_filled_profiles.md` except where the page's records hide unbuilt units (S1.2b, S6.2c, S8.1b). Checked section by section.
