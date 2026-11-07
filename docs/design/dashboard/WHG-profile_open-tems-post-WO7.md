# Profile work: open items outside WO-06 and WO-07

Started 2026-11-07. Things found in WO-03 to WO-05 that need work but are not in the next two work orders. Only items actually encountered; nothing anticipated. When an item is taken into a work order, note the WO; when it is done, move it to Closed with the date.

**When** says where it is likely to land: *sample page* (before 21 Nov), *Dec* (1 to 7 Dec), *Jan* (Santa Fe), *later*.

## Ecoregions

**E1. Ecoregion-to-Wikipedia links are unreliable.** 129 of 847 flagged by name; of the 40 weakest, about 15 look wrong or too broad. Cause: the January harvest accepted any search hit whose words appear in the ecoregion name, and redirects unchecked. Example: 833 North Saharan Xeric Steppe and Woodland links to "Woodland". *Found:* WO-05 (`wo05_results.md`, `wo05_wikilinks.csv`). *Next:* try looking links up through Wikidata's WWF ecoregion code property instead of by name, then check what remains by hand. *When:* Jan. Until then the Wikipedia button is shown only where the link is not flagged, or not at all on the sample page (Karl's call).

**E2. Ecoregion summaries (the gist, S1.2b).** 7 stored summaries are refusals from the summarising model; others read well but describe the wrong thing, because they were made from the wrong article (E1). *Found:* WO-05. *Next:* regenerate summaries for every link E1 changes; mark generated text as generated. *When:* Jan, after E1. Sample page: planned sentence.

**E3. Garbled ecoregion names.** 36 names in `lu_tec` have broken character encoding and reach the Explorer. *Found:* WO-05. *Next:* reload with the right encoding. *When:* fold into WO-06 or WO-07 as housekeeping.

**E4. Wikipedia licence.** CC BY-SA. Karl's position: attribute and display. *Found:* WO-05 raised it. *Next:* none unless WHG asks; record the attribution wording when the button is built.

## Elevation and setting

**L1. No local elevation grid.** The two timings for January (a DEM window at 5, 20 and 50 km around each place; an elevation histogram per basin) could not be measured. *Found:* WO-05. *Next:* download GMTED2010 at 30 arc-seconds (land only, so coastal windows are not pulled down by sea depths); ETOPO 2022 with sea cells masked as fallback. Then run the timings. *When:* Dec or early Jan.

**L2. Point elevation comes from a public service.** OpenTopoData's public API, which is rate-limited. Fine for the sample page, not for production. *Found:* WO-05. *Next:* read point elevation from the local grid once L1 is done, or take WHG's own value. *When:* Jan.

**L3. Setting statements beyond the elevation range.** "Lower than four-fifths of its basin" and "in a valley floor, higher ground on most sides" need L1. *Found:* Karl, 5 Nov (Tbilisi). *When:* Jan. Sample page: planned sentences.

## Rules and wording

**R1. Temperature compared by ratio.** The Analysis rule's local-to-upstream temperature ratio misbehaves near 0 °C; temperature in °C should be compared by difference, never by ratio. *Found:* WO-05. *Next:* rule change in the Analysis rule and the generator. *When:* fold into WO-06.

**R2. The "no percentile" list in About these figures.** It names "Flow distance to marine outlet" (already stated as "drains directly to the sea") and the wetland class (a category, not a quantity), and lists each measure twice when its upstream version is also zero. *Found:* WO-05. *Next:* list only share and extent measures; name a measure once when both versions are zero. *When:* fold into WO-06 or WO-07.

**R3. Catalog name "Flow distance to marine outlet"** is looser than its name for basins ending at a lake-sea such as the Caspian. *Found:* WO-05. *Next:* reword in the catalog or the glossary. *When:* with the glossary.

## Data to check

**D1. Alexandria's karst at 100%.** Consistent with its neighbours in the loaded data, but not checked against the source file, which is not local. *Found:* WO-04, WO-05. *Next:* check against the source download. *When:* later; not shown as a karst word until checked.

**D2. Tristan da Cunha.** No basin, no ecoregion polygon, no elevation from the public service. The no-basin profile has almost nothing to say. *Found:* WO-05. *Next:* decide what a no-basin profile shows (perhaps only the nearest basin's distance and a note). *When:* Jan.

## Sandbox and Analysis tab (outside the profile, found during it)

**S1. "Coastal terminal" badge** disagrees with the `coast` flag for 45% of the basins it labels. *Found:* WO-03. *When:* later.

**S2. "Distance to ocean outlet" label** shown for endorheic basins, where it is the distance to an inland sink. *Found:* WO-03. *When:* later.

**S3. `gaz.hydrorivers` incomplete.** *Found:* WO-03. *When:* check before the nearest-river work in WO-07 relies on it.

## Endpoint

**P1. Speed.** The ring takes 5 to 17 s per call today. Options: precompute compact signatures for all 16,397 L6 basins (about 125 MB), or a one-pass route. *Found:* WO-03. *When:* Jan. The sample page is generated offline, so it does not need this.

## Maybes that stay planned for the sample page

Not built before 21 Nov; shown as planned sentences. Each needs its own work later.

- S1.3, distance from the point to the next ecoregion.
- S2.1b, the months when most rain falls.
- S3.4, lake and wetland share (not in the payloads).
- S7.1a, distance to the coast (needs coastline data).
- S7.3, which kind of edge is nearest the point.
- S8.1b, the years of the datasets (needs the glossary).
- S8.3, the snap to the nearest basin.
- S9.1, the link from WHG into EDOPS (needs a URL scheme).
- Basin shape (new data).

## Closed

(none yet)
