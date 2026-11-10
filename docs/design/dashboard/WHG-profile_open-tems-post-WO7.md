# Profile work: open items

Started 2026-11-07; brought up to date 2026-11-09 (after WO-08, during WO-09). Things found in the profile work that are not done. Only items actually encountered; nothing anticipated. When an item is taken into a work order, note the WO; when it is done, move it to Closed with the date.

**When** says where it is likely to land: *WO-09* (by Wed 11 Nov), *sample page* (send Sat 21 Nov), *Dec* (1 to 7 Dec), *Jan* (Santa Fe), *later*. Results behind each item are in the `wo0n_results.md` file named.

## The placeholders still open (4 of 22 at the WO-04c baseline)

These are the four units the ten profiles still show as `⟦...⟧`. The goal is to fill them.

- **S1.2b, the one-line ecoregion gist.** Blocked on reliable stored summaries: see E1 and E2.
- **S6.2c, a description of a neighbouring basin.** The slot in the flow sentence: "Upstream, {neighbour description} drains into it; downstream, it drains into {neighbour description}" (`modal_dummy_annotated.md`, S6.2a and S6.2b). It describes one specific neighbour, the one the flow points at, and basins have no names, so something must identify it. S6.2 today gives counts only ("one basin drains into it") and does not describe. Two ways are named in `wo04a_results.md` (row S6.2c, Q4): *by character*, from how the neighbour ranks on the measures the ring comparisons already use ("a drier, higher basin"); or *by its main river* ("the basin of the Niger"). A third, by shape ("a narrow corridor along the Niger", `S6.X1`), needs basin shape (O2), which is not started. The river-name gate (WO-08 A5) may make the second cheaper; not checked for a neighbour's reach, nor what it says when no river passes. *For Opus:* choose between character and river (or both, river first), and the wording. WO-06 left it as "planned unless it turns out to be easy". *When:* not scheduled.
- **S8.1b, the years of the datasets.** Needs the glossary of dataset years. *When:* with the glossary.
- **S9.1, the link from WHG into EDOPS.** Our side, January work (WO-10a): EDOPS defines the URL, a permalink into the Sandbox that opens a place's signature from `lat`, `lon`, `name`, `scope` and `level`; WHG builds it from a place's name and coordinates. Not blocked on WHG.

## Ecoregions and Wikipedia

**E1. Ecoregion-to-Wikipedia links are unreliable.** 129 of 847 flagged by name; of the 40 weakest, about 15 look wrong or too broad. Cause: the January harvest accepted any search hit whose words appear in the ecoregion name, and redirects unchecked. Example: 833 North Saharan Xeric Steppe and Woodland links to "Woodland". *Found:* WO-05 (`wo05_results.md`, `wo05_wikilinks.csv`). *Karl, 9 Nov:* the aim is every link valid, not only flagged ones hidden; name mismatches are to be identified and handled. *OneEarth button (v18, 9 Nov):* every ecoregion with a OneEarth slug (845 of 846; all 845 pages answered 200) gets a button to its OneEarth page, opening in a new tab; this settles the broken-link part for the button. One Earth's page text may not be reproduced without permission (site terms); the data are CC BY-NC 4.0, cite One Earth. Karl is writing to One Earth (draft in `misc/oneearth_email_draft.txt`). Wikidata (P1294, WWF 2001 codes) matched 631 of 846 by exact name; 583 agree with our link, 18 differ, 215 unmatched: the Wikipedia fallback for gists. *Stopgap in WO-09 (item 10):* the button is hidden where the link is flagged (1 of the ten places, Timbuktu, loses it); this also hides some good links. *Next:* scope the repair: look each ecoregion up through Wikidata's WWF ecoregion code property instead of by name; check that every link resolves to an article about that ecoregion and not a broad or disambiguation page; review what remains by hand. A short read-only look at how many of the 847 Wikidata resolves comes first. *Karl, 9 Nov:* the Wikipedia-link repair is shelved (the current links will never be satisfactory) unless someone has a better idea; waiting on One Earth's reply (email sent 9 Nov) for the gist. *When:* shelved.

**E2. Ecoregion summaries (the gist, S1.2b).** 7 stored summaries are refusals from the summarising model; others read well but describe the wrong thing, because they were made from the wrong article (E1). *Found:* WO-05. *Karl, 9 Nov:* generating new summaries against the Claude API is acceptable if that is what it takes. *Next:* regenerate summaries for every link E1 changes; mark generated text as generated; decide where the API key lives (the prose layer plan is BYOK for the live service; for a one-time batch the key can be Karl's own). *When:* after E1. S1.2b stays a placeholder until then.

**E3. Garbled ecoregion names.** 36 names in `lu_tec` have broken character encoding and reach the Explorer. *Found:* WO-05. *Next:* reload with the right encoding. *When:* parked.

**E4. Wikipedia licence.** CC BY-SA. Karl's position: attribute and display. *Found:* WO-05 raised it. *Next:* none unless WHG asks; record the attribution wording when the button is built.

**E5. Ecoregion at the point falls back silently.** Where the point lies in no ecoregion polygon (Levuka and other coastal points), S1.2a uses the basin's majority ecoregion; the fill note says so, the profile text does not. *Found:* WO-08 (`wo08_results.md`, B4/B5). *When:* decide whether the text should say so.

## Elevation and setting

**L1. No local elevation grid.** The two timings for January (a DEM window at 5, 20 and 50 km around each place; an elevation histogram per basin) could not be measured. *Found:* WO-05. *Next:* download GMTED2010 at 30 arc-seconds (land only, so coastal windows are not pulled down by sea depths); ETOPO 2022 with sea cells masked as fallback. Then run the timings. *When:* Dec or early Jan.

**L2. Point elevation comes from a public service.** OpenTopoData's public API, which is rate-limited. Fine for the sample page, not for production. *Found:* WO-05. *Next:* read point elevation from the local grid once L1 is done, or take WHG's own value. *When:* Jan.

**L3. Setting statements beyond the elevation range.** "Lower than four-fifths of its basin" and "in a valley floor, higher ground on most sides" need L1. *Found:* Karl, 5 Nov (Tbilisi). *When:* Jan.

**L4. The place's point is often a centroid.** A gazetteer point for a city can lie away from its port or shore, so statements tied to the point (elevation, river distances S3.1 and S3.3, the S8.3 snap) may overstate precision. WO-09 adds a line to About these figures (S8.point) saying so. *Found:* Karl, 8 Nov (`wo08_results.md`, B6). *Next:* Opus: how point-based statements should be worded. *When:* open.

## Rules and wording

**R1. Temperature compared by ratio.** The Analysis rule's local-to-upstream temperature ratio misbehaves near 0 °C; temperature in °C should be compared by difference, never by ratio. The ring sentences already compare by order. *Found:* WO-05. *Next:* rule change in the Analysis rule (needs a threshold decision). *When:* parked.

**R3. Catalog name "Flow distance to marine outlet"** is looser than its name for basins ending at a lake-sea such as the Caspian, which the signature and the coastline layer both count as sea although it is hydrologically an inland lake. Tbilisi's "drains to the sea about 664 km beyond its outlet" depends on it. *Found:* WO-05, WO-08. *Next:* reword in the catalog or the glossary. *When:* with the glossary.

**R4. "Wetter" wording of S3.2b.** *Found:* WO-05. *When:* parked.

**R5. Wetland groups and other flagged measures.** The engine's `outside_active_domain` flag hides a value of at most 1%. WO-08 made S5.1a and S5.1b state the value; WO-09 stopped the About list calling a flagged measure zero when its value is above zero. The same flag may hide a 1% in karst, permafrost and wetland groups, where nothing states it. *Found:* WO-08, WO-09. *When:* only if a unit starts to read those measures.

## Data to check

**D1. Alexandria's karst at 100%.** Consistent with its neighbours in the loaded data (92 to 100%; 379 of 16,397 basins sit at 100%), but not checked against the source file, which is not local; it sits awkwardly beside "unconsolidated sediments". *Found:* WO-04, WO-05, WO-07. *Next:* check against the source download. *When:* later; not shown as a karst word until checked.

**D2. Tristan da Cunha.** No basin, no ecoregion polygon, no elevation from the public service. WO-09 shows the no-basin profile as it is (a "no basin" text and two placeholders). *Found:* WO-05. *Next:* decide what a no-basin profile should show (perhaps only the nearest basin's distance and a note). *When:* Jan.

**D3. The signature's coast flag misses about a third of the basins that touch the sea.** Of 81 basins with flag 0 whose outline lies within 2 km of the coastline, 77 are terminal basins (Rotterdam, Hamburg, Stockholm, Porto, Bordeaux, Philadelphia, Saint Petersburg, Riga, Quito). Why is not verified. S7.2 therefore uses the flag or the coastline layer. *Found:* WO-08 (`wo08_results.md`, B6). *Next:* a note to the HydroSHEDS team (Opus, 9 Nov). *When:* open.

**D4. The coastline follows tidal estuaries** (Natural Earth, GSHHG and OSM alike), so S7.2 "touches the sea" is true to the data for ports such as Hamburg and Rotterdam but does not say the open sea is near. *Found:* WO-08. *When:* open; reported as a limit.

**D5. Levuka's basin has 131 pieces (175,335 km²).** *Found:* WO-08. *When:* open.

**D6. Missing-value marker in columns the profile does not read yet** (stream gradient, soil carbon, moisture index, snow cover): not guarded; use `missing.py` when a unit first reads them. The check ran over the 103 sample basins that carry the marker, not over all 16,397. *Found:* WO-08 (A4). *When:* as units are added.

**D7. I-3, the marker stored as a class (WO-03).** The class-id frame is in a frozen research notebook; no live profile script builds such a frame; `missing.class_label` is the fix for any future use, tested. Treated as closed in practice, not as a code change. *Found:* WO-03.

## River names

**N1. World-scale river names.** The OpenStreetMap check is built for 118 rivers (115 with a line in `gaz.osm_river_lines`). A version for the world is about 500 rivers and a few hours of queries to the public Overpass server (30 to 90 s a river, occasional 502); use a User-Agent with a real contact. *Found:* WO-08 (A5). *When:* later.

**N2. Natural Earth's Wikidata ids are unreliable for same-name rivers.** The 11 US Colorado lines carried the Argentine river's id; corrected in our database copy `gaz.ne_rivers_10m` (the source shapefile is never edited). Other wrong ids that happen to pass the OSM check would not be seen. *Found:* WO-08. *When:* open.

**N3. OpenStreetMap relations have gaps.** The Snake River's relation has no ways near a reach in southeast Washington, so a true name is silenced as "a river". *Found:* WO-08. *When:* accepted cost.

**N4. ODbL.** The OSM credit sentence (S8.osm, WO-09 item 5) appears on a profile that shows a gated river name. Any page that carries such a profile must show it. *Found:* WO-08.

## Sandbox and Analysis tab (outside the profile, found during it)

**S1. "Coastal terminal" badge** disagrees with the `coast` flag for 45% of the basins it labels. *Found:* WO-03. *When:* later.

**S2. "Distance to ocean outlet" label** shown for endorheic basins, where it is the distance to an inland sink. *Found:* WO-03. *When:* later.

**S3. `gaz.hydrorivers` incomplete.** *Found:* WO-03. Status not re-checked: WO-07 read `gaz.rivers` (HydroRIVERS). *When:* check.

## Endpoint

**P1. Speed.** The ring takes 5 to 17 s per call today. Options: precompute compact signatures for all 16,397 L6 basins (about 125 MB), or a one-pass route. *Found:* WO-03. *When:* Jan. The sample page is generated offline.

**P2. Monthly arrays in the `/whgmodal` payload.** Twelve monthly precipitation and temperature values (the Sandbox chart reads `pre_mm_monthly` and `tmp_dc_monthly`) so WHG can draw its own chart. *Found:* Karl, 8 Nov; agreed by Opus 9 Nov. *When:* Jan, with the endpoint work.

## Other

**O1. UNEP aridity bands as a secondary source** for the aridity sentence (A2 left them alone outside the cold zones). *Found:* WO-08.

**O2. Basin shape (new data).** Listed as planned for the sample page; not started. *When:* later.

**O3. Push.** `whg-profile` is local only. Karl 9 Nov: no push until he says so.

## Closed

- **R6. The ring table counted flagged rows as 0** (WO-09 item 1, 9 Nov): fixed by patching the table from `basin06` (`wo09_patch_ring.py`, 13,617 rows; 1,346 are really 1%). One sentence changed, at Timbuktu.
- **R2. The "no percentile" list** (WO-09 item 4, 9 Nov): flow distance and wetland class left out, a measure named once when its upstream version is also zero, a flagged measure with a value above zero not called zero, singular wording for one measure. Template v16 and v17.
- **S1.3, the next ecoregion** (WO-08 B3, 8 Nov): tried and dropped.
- **S1.4, the basin's other ecoregions** (WO-08 B4, 8 Nov): built, share limit 10%.
- **S2.1b, when the rain falls** (WO-08 B1, 8 Nov): built.
- **S3.4, lakes and wetlands** (WO-08 B2, 8 Nov): built.
- **S7.1a, distance to the coast** (WO-08 B6, 8 Nov): tried and dropped.
- **S7.2, S7.3, the seacoast** (WO-08 B6): built; S7.3 silenced in WO-09 (item 7, 9 Nov), code kept.
- **S8.3, the snap to the nearest basin** (WO-08 B5, 8 Nov): built.
- **A5, river names need two sources** (WO-08, 9 Nov): the OpenStreetMap gate, 3 km.
