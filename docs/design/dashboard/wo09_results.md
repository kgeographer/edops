# WO-09 results

9 Nov 2026. One section per numbered item of `wo09_fixes-before-demo-page.md`. Template: `profile_templates.md` (version 19). Code: `scripts/edop/whg/` (`wo04_fill.py`, `wo06_rings.py`, `wo07_rivers.py`, `wo08_units.py`, `wo09_patch_ring.py` new); notebook `notebooks/edop/whg/wo09_fixes.ipynb`; tests `tests/test_whg_wo09.py`, `tests/test_whg_ring_patch.py`. Profiles: `wo09_filled_profiles.md` (nine places with a basin, and Tristan da Cunha, which has none). Full suite: 619 passed, 21 skipped.

## 1. The ring table

- **Cause.** The ring payload leaves `representative_raw` empty where the engine flags a share `outside_active_domain`; `fetch_ring_rows` stored that row with an empty value, and `member_values` counted every such row as 0. The value was never in the table, so a rebuild through the endpoint would have stored it empty again.
- **Fix (not the 40-minute rebuild).** `wo09_patch_ring.py` writes the `basin06` value into each flagged row of the 11 share variables (cropland, pasture, karst, permafrost and wetland groups 1 and 2, each with its upstream version; `dist_sink` is a distance and is left alone). `status` is unchanged. The original is `output/edop/whg/wo06_ring_values.pre_wo09.csv` and the patch always reads from it. `member_values` counts a flagged row at its stored value, 0 if empty.
- **Size.** 14,344 flagged rows (1,739 of the 1,743 members); 13,617 are shares and were given a value; 1,346 of those are 1% in `basin06`, the rest true zeros. `basin06` holds only 0 or 1 for them, none null. The "193" of WO-08 counted the cropland and pasture members S5.2 compares.
- **Tests.** Same 90,906 rows and columns; only flagged share rows changed, with values 0 or 1; values equal `basin06` (150 members per variable); `dist_sink` untouched; `member_values` uses the stored value.
- **Effect.** One sentence changed, at Timbuktu (S5.2): "Its basin has less pasture than three of the five basins around it" became "…has less cropland than three and less pasture than three". Timbuktu's cropland is a true 0, and three neighbours are really 1%, so a tie became a comparison. The other eight places with a basin did not change.
- **Not done.** A spot check of a few rows against a live ring call.

## 2. "No cropland is recorded"

- Timbuktu's value is a true zero in `basin06`, so the sentence is right there. The rule says "none" only of a zero value (the engine flag is a percentile guard, not a zero); Chaco Canyon reads "about 1%".
- **Sample check (Cell 3, 306 basins, 612 units):** 292 units say "no ..."; **none** has a raw value above zero. 123 basins have both shares at zero; 38 say "of the basin is pasture" (cropland zero, pasture not).

## 3. Zero-share wording

`S5.1b.some_full` ("{value} of the basin is pasture", used when cropland is zero) and `S5.both_none` with `S5.frame.both_none`. Utqiaġvik reads "neither cropland nor pasture is recorded; the commonest cover is sparse herbaceous or sparse shrub cover, at about 81%". The word "other" is dropped there.

## 4. The "no percentile" list (R2)

`NOT_A_SHARE` = flow distance and wetland class, left out. A measure and its upstream version both zero are named once. A flagged measure whose value is above zero is not called zero. Singular wording for one measure (`S8.2.zero.one`, `S8.2.other.one`: "1 measures are zero" read badly at Santa Fe and Chaco Canyon). The flagged-measure change also altered wetland-group lines in eight profiles; I had predicted only Chaco Canyon, so this is noted.

## 5. OpenStreetMap credit

`S8.osm` appears when a river name passed the OSM check: Timbuktu, Tbilisi and Kaifeng. Silent elsewhere.

## 6. Where the point comes from

`S8.point` appears in all nine places with a basin (whenever an elevation or a distance is stated).

## 7. S7.3

Silenced (the key is `S7.frame: {S7.2}`); code kept.

## 8. Fallbacks noted

Already in the fill notes (the ecoregion fallback to the basin's majority ecoregion); no change needed.

## 9. Tristan da Cunha

Included as the tenth profile: "No basin contains this point", and two placeholders (S1.1b, S9.1).

## 10. Flagged Wikipedia links

Hidden where flagged in `wo05_wikilinks.csv`. **One of the nine places loses the button: Timbuktu** ("Sahel"). It now has the OneEarth button (see below).

## Added during WO-09: ecoregion links (E1)

- **Wikidata (read-only).** Property P1294 (WWF ecoregion code, the 2001 scheme) lists 881 items, 830 with an English article. Our table has no such code, so matching was by name: 631 of 846 matched exactly; 601 have an article; 583 agree with our current link; 18 differ; 215 unmatched; 30 matched items have no English article. These are the Wikipedia fallback; not acted on.
- **OneEarth.** We hold the slug for 845 of 846 ecoregions. All 845 pages `https://www.oneearth.org/ecoregions/<slug>/` answered 200 (9 Nov). The terms page (updated 15 Apr 2026) reserves the site's original content and gives no reuse licence, so linking is fine; showing their text needs permission. The Bioregions shapefile is CC BY-NC 4.0, cite One Earth (Edward Bell, 13 Jan 2026). Draft email: `misc/oneearth_email_draft.txt` (gitignored).
- **Template v18, S9.4.** `[Ecoregion on OneEarth: {S9.4}]` before the Wikipedia button; opens in a new tab (`target="_blank"`, recorded in the Changes line and each fill note). If an ecoregion has no slug the button is left out.

## Template changes

- v16: S5.1b.some_full, S5.both_none (+ bare, frame), S8.osm, S8.point, S7.frame, S9.frame.nowiki.
- v17: singular S8.2 wording.
- v18: S9.4, the OneEarth button.
- v19: `S5.2.counts` takes the verb ("its basin has {list}"), so two measures no longer repeat "has"; eight profiles reworded.

## Gate

- Every item above is done; item 1 by patch, not rebuild.
- The profiles regenerate from the current template (v19).
- No profile says "none" of a share whose raw value is above zero (Cell 3).
