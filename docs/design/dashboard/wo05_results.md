# WO-05 results (running file, in progress)

Written as the cells come back. Sections follow the numbered items of `wo05_place layer-framingA-wo04-fixes.md`. Nothing here is final until `wo05_summary.md` exists. Evidence comes from `notebooks/edop/whg/wo05_place_layer.ipynb` (Karl ran it; outputs pasted in the session) and `output/edop/whg/wo05_fill.csv`. Wording under test is `profile_templates_v4_target.md` (now Version 3).

## 1. The place layer

Done at the ten places (Cell 2) and over the 306-basin sample (Cell 5).

- **S1.1b, point elevation.** Sampled live from OpenTopoData "mapzen" (30 m). It answered for all 306 sample points, so the 90 m Open-Meteo fallback was never used in this sample. No DEM is stored locally. At every place with a basin the point elevation falls inside the basin's `elev_min` to `elev_max`.
- **S1.2a, the point's ecoregion.** Point-in-polygon on `gaz."Ecoregions2017"`. It differs from the basin's majority at 18 of 306 basins (5.9%), matching WO-03's about 6%. At the ten places it differs at Timbuktu, Tbilisi and Alexandria.
- **S1.2c** therefore fires at those 18 of 306 (about 1 profile in 17).
- **S1.5a, S1.5b** (basin elevation range) and the mean `ele_mt_sav` filled at every place with a basin. Examples: Tbilisi point 418 m, basin 255 to 3,838 m, mean 1,638 m; Timbuktu 272 m in 257 to 279 m.
- **Tristan da Cunha** (no basin): the point lies in no Ecoregions2017 polygon, so there is no ecoregion to name. Elevation is also empty there, which I believe is because it is fetched from the signature response and that needs a basin (not verified). Whether the no-basin profile names an elevation is a later decision.
- **Source of elevation if WHG supplied it:** not examined; left as the later decision the WO names.

Gate part met: S1.1b, S1.2a, S1.2c, S1.5a, S1.5b filled at 306 of 306 sample basins.

## 2. Water wording for the classes

Evidence is Cell 6 plus the area ratio (upstream area over local area) per class from `wo05_fill.csv`. Sample of 306 basins; the class counts are Catchment-uniform 135, Endorheic 56, Coastal terminal 53, Local-dominant 46, Exogenous 16. No Undetermined basin in the sample.

What the Analysis rule's classes actually contain:

| Class | Area ratio | Climate ratios | Draft phrase | Verdict |
|---|---|---|---|---|
| Exogenous (16) | min 2.96, median 61.5 | all upstream wetter (precip 1.1 and over; aridity above 1.5 at 15 of 16) | "Most of the water passing here falls far upstream ... wetter than it" | Holds in this sample. "Most" is inferred from area and climate, not measured water volume. |
| Catchment-uniform (135) | 117 of 135 at 1.0 (nothing beyond the basin itself); 18 have real upstream area (2 to 652 times) | all within 0.9 to 1.1 | "The catchment above is 1.0 times the size of the local basin, with much the same climate." | Misleading for 117 (87%). Fine for the other 18. |
| Local-dominant (46) | 43 of 46 above 2; 29 above 10; median 17 | mixed: upstream wetter 1.1 to 1.5 in 20, drier in 16, near-same in 10 | "... most of the water passing here falls locally" | Wrong. These basins have the large upstream catchments; the class is the rule's residual (not uniform, not exogenous), so it says only that the climate differs somewhat. |
| Coastal terminal (53) | 52 of 53 at 1.0, max 2 | spread both ways | "so little water arrives from upstream" | Holds in this sample, but the rule tests only distance to the sea under 10 km, not upstream area. A big delta basin would break it. |
| Endorheic (56) | 44 at 1.0; 12 above 2 (8 above 10, max 2931) | mostly near 1 | empty | Keep empty: S3.5 already says "nowhere: it is a closed basin, an inland sink". |
| Undetermined | not in sample | | empty | Keep empty. |

**Why "uniform" is mostly headwaters.** A basin with no L6 basin draining into it has up_area equal to its own area, so every ratio is trivially 1. The Analysis rule then calls it uniform. At Tbilisi this means a basin of 23,251 km² reaching 3,838 m whose snow-fed streams start inside its own boundary; no other L6 basin feeds it. The streams exist; they are inside the polygon. (That the Kura has a large catchment above Tbilisi is from memory, not checked against data.) The climate ratio gives no information for such a basin, since it compares the basin with itself.

**Proposed corrections** (not yet in the template; awaiting Karl's yes):

1. New phrase `S3.2.headwater`, used when the area ratio is 1.05 or less, for the uniform and local classes (118 of the 181 sample basins in those two): "No other basin drains into this one: the water here is gathered within the basin itself." It makes no climate claim, because there is nothing to compare.
2. `S3.2.uniform` for the 18 with real upstream area stays as drafted.
3. `S3.2.local` becomes: "The catchment above is {S3.2a} times the size of the local basin, in a somewhat different climate from it." (No "most of the water falls locally".)
4. `S3.2.coastal` stays, but used only when the area ratio is 2 or less; otherwise the sentence "The basin meets the sea at its outlet." Script rule.
5. `S3.2.endorheic`, `S3.2.undetermined`: stay empty.
6. `S3.5.sea` and `S3.5.inland`: "downstream of the basin" repeats the subject ("The basin drains to the sea about 664 km downstream of the basin"). Proposed: "to the sea about {km} km beyond its outlet", and the same for inland. Whether Tbilisi's sea is the Caspian is item 3.

Open point for Opus: the temperature ratio is a ratio of degrees Celsius, which misbehaves near 0 °C. It is in the Analysis rule as well, so it was not changed here.

## 3. Fixes from WO-04

All four item 3 questions are now answered (below). Item 4 and the v4 wording decision remain.

**Tbilisi, "drains to the sea", the Caspian (Cell 10): the source treats the Caspian as an ordinary outlet, and its columns cannot tell it from the ocean.** Tbilisi's basin (hybas_id 2060617xxx, `dist_sink` 664 km) is the head of a chain of five basins running down to the terminal basin 2060070xxx (`next_down` 0, `dist_sink` 0). All five have `endo` = 0, so the source does not class the Kura as endorheic. The terminal basin has `coast` = 0. 17 L6 basins share this sink; all have `endo` = 0 and `dist_sink` from 0 to 824 km. The profile says "to the sea" for them because `endo` = 0.

A follow-up query shows `coast` = 0 and `endo` = 0 at the sink basin for 11,047 of 16,397 L6 basins (1,688 distinct sinks). That includes the Nile delta, which does reach the ocean, so these two columns cannot separate a lake-sea such as the Caspian from the ocean. I do not know from the data how the source handles other large closed seas (the Aral, for example); not checked. **Decision (Karl, 2026-11-07):** "sea" stays in the wording. The Caspian is a named sea, as are the Black Sea and the Mediterranean, so "drains to the sea" is acceptable for the Kura and no change is made. What remains is minor: the catalog name "Flow distance to marine outlet" is looser than its name for a basin whose outlet is a lake-sea, and telling lake-seas from the ocean would need an outside list of terminal basins, not built here and not needed for the wording.

**Alexandria karst at 100% (Cell 9): consistent with the source as loaded; not checked against the source file.** Alexandria's L6 basin (hybas_id 1060034170, 16,374.7 km², `sub_area` equals `up_area`) holds `kar_pc_sse` = 100 in `public.basin06`, and the signature returns 100, so nothing in EDOPS's signature layer changes the stored value. Its five neighbours read 100, 100, 92, 100, 100, so it is not an isolated value. Across all 16,397 L6 basins, 379 are at 99.5 or above, 1,488 at 50 or above, 11,411 are zero and none are negative (no NoData left). A 100 is therefore ordinary for this dataset, not an outlier. What is not established: whether the BasinATLAS source gives 100 for this basin, because the source geodatabase is not on this machine; the check goes only as far as the loaded table and its neighbours. That the area is karst or carbonate country (a limestone coast and plateau) is from general knowledge, not from anything in the data here.

**Ecoregion-to-Wikipedia links (Cell 8): listed, not corrected.** 847 ecoregions; 821 have a row in `public.eco_wikitext`; 26 have none (S9.2 then has nothing to link; the sample hit this at 4 of 306 basins). The check flags a row as suspect when the article title is less than 0.6 similar to the ecoregion name, or is a part of it: 129 rows. All 847 rows, with the suspect flag, are in `docs/design/dashboard/wo05_wikilinks.csv`. See "Ecoregion handling: investigation" below for why the matches are wrong. The check compares names only. Most flagged rows are the same place under a plainer name (Sudd, Sundarbans, Fiordland, Everglades, Bermuda, Easter Island). I read only the 40 weakest titles shown in the cell; the other 89 are unread. From those 40, by title alone and without opening any article:

- **Wrong target or a species, not a place:** 569 Dry Chaco links to "Dry Chaco fat-tailed opossum" (an animal); 833 North Saharan Xeric Steppe and Woodland links to "Woodland" (the known case); 25 Northern Swahili coastal forests links to "Swahili" (people or language, as far as the title shows); 609 St. Peter and St. Paul Rocks links to "Paul St. Peter".
- **Too broad, a generic article for a specific ecoregion:** 127, 134 and 414 (Antarctic and Arctic tundra) link to "Tundra", 125 to "Tundra of North America"; 842, 822, 845 (South, East and West Sahara desert) all link to "Sahara"; 2 Cameroon Highlands forests links to the country "Cameroon"; 53 Sahelian Acacia savanna links to "Sahel".
- **Partial or different scope, worth a look:** 69 East African halophytics (Lake Natron), 202 Jarrah-Karri (Warren bioregion), 66 Zambezian-Limpopo mixed woodlands (Dry miombo woodlands), 739 Syrian xeric grasslands (Middle East steppe), 107 Southwest Arabian coastal xeric shrublands (Arabian Peninsula coastal fog desert).

Where a link is "too broad", the filled_profile still shows a true article but not the one for that ecoregion; where it is wrong, the button misleads. The 26 missing and 129 flagged rows go to whoever fixes `eco_wikitext`; not corrected here, as the WO says.

**Readable names (Cell 7): answered.** Across the 306-basin sample, 22 distinct measures appear in the S8.2 "zero here" or "no value" lists. All 22 have a friendly name in `EDOPS_variable_catalog_v0.4.tsv`; none are missing, so there are no gaps to list. Most frequent: Karst area (226 basins), Wetland extent group 2 upstream (220), Permafrost extent (203). The upstream measures read "(upstream)" through the template line `label.upstream`.

Two entries are odd to list as "zero here and so have no percentile", though they are correct:
- **Flow distance to marine outlet** (`dist_sink`), 133 basins. It is zero for coastal basins (the outlet is the sea) and for closed basins (there is no marine outlet). In the second case a reader could take "zero" to mean "next to the sea". A distance is not an extent, and S3.5 already speaks about it.
- **Wetland class ID** (`wetland_class`), 84 basins. It is a category code, so "zero" means no wetland class and "no percentile" is not meaningful.

Suggest for Opus: leave both out of the S8.2 zero list. Not changed here, since which measures the list covers is a rule, not wording.

## 4. Two timings

**Neither timing was measured: there is no local DEM, so per the WO this item stops at naming one.** The only elevation EDOPS has today is the per-point lookup against OpenTopoData (30 m), which is a web call and not a local grid; `data/EarthEnv` holds only GMBA mountain polygons.

Candidates for a roughly 1 km (30 arc-second) global grid, from a web search on 2026-11-07. Sizes marked "not found" were not on any page I could reach, so they are unknown, not estimated:

- **ETOPO 2022, 30 arc-second** (NOAA). Single global tile in GeoTIFF or NetCDF ([ESSD paper](https://essd.copernicus.org/articles/17/1835/2025/essd-17-1835-2025.html)). NOAA's [directory listing](https://ngdc.noaa.gov/mgg/global/relief/ETOPO2022/data/30s/30s_geoid_gtif) shows the geoid-referenced GeoTIFF at 1.3 GB. The ice-surface and bedrock files' sizes were not found. It includes sea-floor depths as well as land.
- **GMTED2010, 30 arc-second mean** (USGS; [EROS archive page](https://www.usgs.gov/centers/eros/science/usgs-eros-archive-digital-elevation-global-multi-resolution-terrain-elevation-data-2010-gmted2010)). Downloaded through EarthExplorer under Digital Elevation; the 30 arc-second layer has global coverage including Greenland and Antarctica. File size and format of the mean grid: not found (one source says a commercial package ships it as JPEG2000, so the original may not be a GeoTIFF).
- **GTOPO30** (USGS, 1996; hosted by [UCAR](https://gdex.k8s.ucar.edu/datasets/d758000/)). 33 tiles of 16-bit binary raster; about 464 MB compressed, 4.6 GB as ASCII, per an NCEP note. Older and coarser in quality than the other two.
- **SRTM30:** nothing found on size or tiling.

For scale (my arithmetic, not a source figure): a 30 arc-second global grid is 43,200 by 21,600 cells, about 933 million, so roughly 1.9 GB as uncompressed 16-bit integers; a compressed GeoTIFF would be smaller.

**How it would be loaded.** Download the single global file once to a local data folder (outside git, like the other large assets), and read windows of it around a point or a basin with a raster library (rasterio, if it is installed here; not checked). Windowed reads of 5, 20 and 50 km around a point touch a few hundred to a few thousand cells, so I expect them to be fast, but that is an expectation and not a measurement. The basin histogram would need each basin's polygon rasterised or masked per basin; again not measured.

**Decision for Karl/Opus:** which grid to download. ETOPO 2022 has a confirmed single-file form and size; GMTED2010 is the land-elevation standard but its file details were not confirmed. No timing, window value or Tbilisi valley-floor evidence is reported, because none was measured.

## Issues log

- Uniform class is 87% headwater basins; the draft phrase is misleading for them (item 2).
- Local-dominant is the rule's residual class; the draft phrase contradicts its data (item 2).
- Tbilisi basin mean temperature (5.3 °C) averages the whole upper catchment including peaks; reads oddly beside a 418 m point. For WO-06.
- Tristan: no ecoregion polygon, no elevation fetched.
- **Headwater sentence may contradict what a reader knows.** At Kaifeng (on the Yellow River), the v4 filled_profile says "No other basin drains into this one: the water here is gathered within the basin itself." That is what the data say (upstream area equals the basin's own area, ratio 1.0), but a reader who knows the Yellow River passes Kaifeng would see a conflict. I have not investigated why the delineation gives Kaifeng no upstream basin (the lower Yellow River runs along a raised bed on a flat plain, which is one possible reason; unchecked). The same applies to any uniform basin on a large river. Worth a look before the sentence is shown to the WHG people.
- The fill note for S3.2 still names the class ("Catchment-uniform") and does not say that the headwater phrase was the one used. Small; not fixed.

## Ecoregion handling: investigation (Karl asked, after Cell 8)

Findings only; nothing has been changed or mitigated. Evidence is from reading the scripts and querying the database and Wikipedia (read-only), 2026-11-07.

**How ecoregions are handled, as built:**
- `gaz."Ecoregions2017"`: 847 polygons (RESOLVE / Dinerstein 2017), key `eco_id`, with `realm`, `biome_*`, `bioregion` and `oneearth_slug` columns. `gaz."Bioregions2023"` (185), `"Subrealm2023"` (53), `"Realm2023"` (14) are the OneEarth hierarchy polygons; they are what the Workbench Ecoregions tab navigates.
- BasinATLAS `tec_cl_smj` (the basin's majority terrestrial ecoregion) carries the same ids: every value in `basin06` matches an `eco_id` in `Ecoregions2017` (no orphans). So the join basin to ecoregion to `eco_wikitext` is sound. 689 distinct ids occur at L6.
- `public.eco_wikitext` (821 rows, one per ecoregion that got text; 26 got none) was loaded once, 2026-01-15, from `wiki_extracts_refilled.jsonl` by `scripts/edop/load_eco_wikitext.py`. That JSONL is not in the repo. The Workbench route `/eco/wikitext` returns the `summary` column, not the Wikipedia text. `summary` was generated by Sonnet (`scripts/edop/summarize_ecoregion_text.py`, 150 to 200 words) from the extract.

**Why titles are wrong** (`scripts/edop/harvest_ecoregion_wikipedia.py`):
- Step 1 asks Wikipedia for each ecoregion name as an exact page title, following redirects, and records a score of 100 without any further check. That accepts whatever page Wikipedia redirects to.
- Step 2, for names with no page, runs a Wikipedia search and picks the best candidate by `rapidfuzz.fuzz.token_set_ratio`, accepted at 80 or more. `token_set_ratio` returns 100 whenever every word of one string occurs in the other, so a one-word article title always matches any ecoregion name containing that word. I checked: "Canadian Middle Arctic Tundra" vs "Tundra" scores 100; "North Saharan Xeric Steppe and Woodland" vs "Woodland" 100; "Dry Chaco" vs "Dry Chaco fat-tailed opossum" 100; "Northern Swahili coastal forests" vs "Swahili" 100; "Cameroon Highlands forests" vs "Cameroon" 100. A plain character ratio gives 34 to 49 for the same pairs.
- Of the 129 suspect rows, 69 came through step 2 (the search and fuzzy path) and 60 through step 1 (an exact title or a Wikipedia redirect). I determined this by re-asking Wikipedia for each name today, so it is a reconstruction, not the original run log. Redirect rows such as Sahelian Acacia savanna to "Sahel" or East African halophytics to "Lake Natron" are Wikipedia editors' choices; whether the target's scope fits is a judgement not made here.
- Consequences visible in the table: several ecoregions share one article (Tundra x3, Sahara x3, Antarctic Peninsula x3, South Deccan Plateau dry deciduous forests x3, Trinidad and Tobago x2): 821 rows, 791 distinct titles. One row (623, Hawai'i) points at a "List of ... ecoregions" page. Others, such as the Antarctic and Arctic tundra rows, link a generic article for a specific ecoregion.

**Consequence for what users see:**
- 7 ecoregions have a stored summary that is a refusal from the summarising model, which the Workbench tab would show as the ecoregion's paragraph: ids 0 (Rock and Ice), 25 (Swahili, text is about the language), 569 (Dry Chaco, text is about an opossum), 575 (Espinal), 609 (St. Peter and St. Paul Rocks), 623 (the list page), 833 (Woodland).
- Other wrong titles produce summaries that read well but describe the wrong thing. 127 (Northwest Antarctic Peninsula tundra) has a summary of Arctic tundra generally. How many of the 129 are like this is not known; only the refusals can be found by text.
- The same table feeds the S9.2 button and the filled_profile Wikipedia link.

**Separate finding, names:** `public.lu_tec` (the BasinATLAS name lookup behind the catalog's `ecoregion_terrestrial_name`) has 36 names in broken encoding ("Alto Paranß Atlantic forests" for "Alto Paraná"; "Choc≤-DariΘn moist forests"). The `Ecoregions2017` names are correct. `routes_explorer.py:84` resolves ecoregion names through `lu_tec`, so the Explorer shows the garbled form for those ids. I did not check whether the signature response does the same.

**Not yet looked at:** the Workbench Ecoregions tab code beyond the `/eco/wikitext` route; how `oneearth_slug` and the OneEarth page links were built; whether the 26 ecoregions with no row are the ones the harvest could not find or ones it filtered (empty text rows are skipped by the loader).

## Threat assessment: Wikipedia-derived text in the /whgmodal payload (for Karl, Opus and CC)

Brief, from the investigation above. Not decided.

**What the payload would carry from this source:** the S9.2 Wikipedia link, and, if wanted, S1.2b (the one-line ecoregion gist) and any paragraph. All of it keyed by `eco_id` into `public.eco_wikitext`.

**As it stands, not safe to ship.** The name check flags 129 of 847 ecoregions (15%). Of the 40 weakest I judged about 15 wrong or too broad, from the titles only; the other 89 are unread. Seven stored summaries are refusals. Other wrong rows give fluent text about the wrong thing, which nothing in the data flags. A wrong article reads as authoritative, so the harm is higher than a missing one.

**Other implications, not yet checked:**
- Licensing: Wikipedia text is CC BY-SA. A summary derived from it by a model is a derivative; reuse in WHG's modal needs attribution and probably share-alike. Not looked into.
- The summaries were produced by a model from the article text, which is a second source of error beyond the choice of title.
- The 26 ecoregions with no row would show nothing.

**What would make it viable** (options, not a plan):
1. Replace the title matching with a verified mapping: one reviewed row per `eco_id` giving the article, or "none". Wikipedia and Wikidata may offer ecoregion identifiers or lists that give the match without fuzzy scoring (to be checked, not known). A human pass over 847 one-line rows (name, title, first sentence) is a day's work, and the 129 suspects are the priority.
2. Where an article covers several ecoregions or a larger area, either accept that and say so in the wording ("on Wikipedia: Tundra") or give no link.
3. If a summary is wanted, regenerate only from verified articles, store nothing when the model declines, and keep the article's revision id with the text.
4. Let the payload omit the link and text when no verified article exists. The template already handles an unfilled S9.2, so absence is safe; a wrong link is not.
5. A different source for the gist (S1.2b), such as the OneEarth bioregion descriptions, or a short text written by the team, would avoid the licence question for that one unit. Its terms are not checked.

**Cheap check available:** how many of the 306 sample points fall in the 129 suspect ecoregions, which gives the exposure in practice.

**Suggested for the decision:** keep the link and gist as `maybe` units until option 1 has been done for at least the ecoregions that the sample page actually shows.

## Gate check (2026-11-07)

Checked on `wo05_filled_profiles.md` regenerated from the live `profile_templates.md` v4 (stamp: `profile_templates.md v4 ... script wo04_fill.py`). Ten profiles. S1.1b, S1.2a, S1.5a, S1.5b filled at the nine places with a basin; S1.2c present at Timbuktu, Tbilisi and Alexandria only. Water wording by place: exogenous (Timbuktu), headwater (Tbilisi, Kaifeng, Lviv, Poltava, Chaco Canyon), local (Santa Fe), coastal (Alexandria, Utqiagvik). Tristan da Cunha: no-basin text. No superseded v1 wording remains. Gate met.
