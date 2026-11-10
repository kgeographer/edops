# WO-10a summary: adjustments to the sample profile page

Spec: `wo10a_profile-page-adjustments.md`. Branch `whg-profile-page`, local only: not pushed, not deployed, not merged. Template version 23. The 38 WHG and page tests pass. The records and the ten response files were regenerated (Cell 2) under v23. Karl has yet to check the chart ticks and the "Profile as JSON" button in the browser, and to take the Chaco Canyon full-page screenshot.

## Done, by item

- **1a. Land cover sentence (v21).** `S5.1c` and `S5.both_none` name the map: "in the GLC2000 land cover map, the commonest class other than cultivated land is {label}, at about {share}%" (and "the commonest class is …" where there is no cropland or pasture). Checked at the three places named: Chaco Canyon (1% cropland, 66% pasture, shrub cover 59%) and Santa Fe (2%, 49%, 53%) still total over 100%, but the sentence now says two datasets are in play. Poltava still reads oddly (below).
- **1b. S8.2 dropped (v21).** `{S8.2}` is out of `S8.frame` and `S8.frame.noyears`. The unit is still filled and sits in the stored record's `units`; its keys are unchanged. Checked at Alexandria, Utqiagvik and Kaifeng.
- **1c. S9 frame unchanged.** The Wikipedia button shows when the ecoregion has a Wikipedia link (the point's, else the basin's) and, because `S9.frame.nowiki` is in the template, the ecoregion is not flagged `suspect` in `wo05_wikilinks.csv` (`suspect_wiki_ids()`). Of the ten places only Timbuktu is flagged, so only Timbuktu has no Wikipedia button. The ecoregion names link to OneEarth inline.
- **2. "Profile as JSON" opens the proposed response.** `to_response()` in `wo10_profiles.py` builds it from the stored record; ten files in `app/static/profiles/response/<slug>.json`. The stored record still sits in `app/static/profiles/` (the template view and the chart read it) and is no longer linked from the page. Sizes: 5,085 to 6,747 bytes for the nine with a basin (Kaifeng 5,978), 275 bytes for Tristan; the stored records are 28 to 35 KB.
  - Shape: `place`, `lat`, `lon`, `hybas_id`, `generated`, `template_version`, `no_basin`; `sections[]` (`id`, `title`, `text`, `runs`); `monthly`; `links` (`ecoregions[]` with name and OneEarth URL, `wikipedia`, `signature`, all absolute URLs). A place with no basin has `no_basin: true` and a `message` only.
  - Left out: template lines, slot values, unit traces, fill notes and provenance. These would come with `?explain=1`.
  - Decision (Karl): the OSM/ODbL credit stays a sentence in the About section's text, not a separate field.
- **3. Monthly arrays.** `monthly` carries `scope: "basin"`, `level: 6`, `source`, `units` (`precip_mm`: millimetres per month; `temp_c`: degrees Celsius, monthly mean), a note that it describes the basin and not the point, and the 12 + 12 values the chart draws.
- **6a. Kaifeng flow sentence (v21).** Cause: Kaifeng has one basin directly downstream and a second three steps further down; the template counted them together as "two". New `S6.2.out_chain`: "It drains into one of them, and its water then passes through one more." It applies where there is exactly one direct downstream neighbour and others beyond; only Kaifeng among the ten. "Flows on through {n} of them" stays for other cases of more than one. Opus's "a second" would read better when the count is one; not done (needs a special case).
- **6d. Counts folded into the extremes sentence (v23, from Opus's reading of Chaco Canyon).** "Of the eight basins that meet here, it receives the least precipitation and is the most arid. Its basin is warmer than four of the seven basins around it." counted the same set two ways. New `S2.3.extreme.counts` and `S5.2.extreme.counts`: "Of the eight basins that meet here, it receives the least precipitation and is the most arid; of the other seven, it is warmer than four." Used only when the extremes and the counts are about the same set of basins; otherwise the two sentences stay. Of the ten places it changes Chaco Canyon and Utqiagvik ("…of the other three, it is cooler than two and is more arid than two"); the others have no extreme and read as before. Opus's own wording put "of the other seven" last ("it is warmer than four of the other seven"); I put it first so that two counts do not read ambiguously.
- **6b. Chart ticks.** Round steps (1, 2, 2.5, 5, 10 × a power of ten) on both axes; the precipitation axis ends on a tick, so Kaifeng's reads 0, 100, 200.
- **6c. Sources line.** No action.

## Notes for the endpoint work (nothing built)

- **Point and basin units (item 4).** Plan for January: store the basin record; compute the point units at request time. The point's ecoregion (polygon lookup), the nearest river and the snap to the nearest basin are local and fast. Only elevation needs an outside call. Two routes: WHG sends its own elevation with the request, since its place pages already show one; or a local elevation grid (open items L1 to L3). The `scope` tag on each unit in the stored record marks which units are which.
- **Permalink (item 5).** It is the EDOPS half of S9.1: EDOPS defines the URL and WHG builds it from a place's name and coordinates, so S9.1 is not blocked on WHG. Moved to January work in the open-items file and the v1 plan.

## Found while checking

- **Tristan da Cunha's message was developer wording** ("No basin contains this point (structured response `no_basin`; nearest basin: see WO-03 Q6). Every basin-keyed unit is empty."), on the page and in the response. Replaced in v22: "This place lies outside any drainage basin in the data, so there is no environmental profile to show." It does not say "island", since the message covers any point outside a basin.
- **Poltava's land cover class** is "mosaic: cropland/shrub and/or herbaceous cover", so the sentence reads "64% is cropland … the commonest class other than cultivated land is mosaic: cropland/shrub …". A rule that skips the mosaic classes, or wording that treats them as cultivated, would fix it. Not done; for Opus.
- **Other multi-basin flow cases.** `S6.2.out_some` ("flows on through {n} of them") is unchanged and unexercised among the ten places; wider samples will show whether it reads well.

## Waiting

- Karl: chart ticks, the button, the Chaco Canyon full-page screenshot.
- Opus: the "a second" wording; the mosaic classes; whether the response needs anything the shape above lacks.
- Not done, as agreed: push, deploy, merge; the full app test suite (before any merge).
