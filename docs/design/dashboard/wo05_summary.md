# WO-05 summary: the place layer, framing A, and the WO-04 fixes

2026-11-07. Detail is in `wo05_results.md` (one section per item, issues log). Branch `whg-profile`.

## What was done

- **Place layer built.** Setting now speaks about the place: point elevation (S1.1b, live 30 m OpenTopoData), the point's ecoregion (S1.2a), the basin's majority ecoregion when it differs (S1.2c) and the basin's elevation range (S1.5a, S1.5b). All five are filled at every one of the 306 sample basins and at the nine test places with a basin. The point's ecoregion differs from the basin's at 18 of 306 basins (5.9%). Tristan da Cunha (no basin) lies in no ecoregion polygon and gets no elevation.
- **Water wording checked for every class** against the Analysis rule over the 306 basins. Four phrases changed (template v4): the uniform class is 87% headwater basins (nothing drains in), which the old phrase misdescribed, so there is a new headwater sentence; the local-dominant phrase claimed "most water falls locally" when 43 of 46 such basins have far larger upstream catchments; the coastal phrase now applies only when the upstream area is at most twice the basin's; the sea sentence now reads "beyond its outlet". Exogenous, endorheic and undetermined are unchanged.
- **WO-04 fixes answered.** Readable names work in S8.2 (all 22 measures that appear have catalog names). Alexandria's karst 100% is the loaded source value, consistent with its neighbours; not checkable against the source file, which is not local. The Caspian is an ordinary outlet in the source (`endo` = 0); "sea" stays by Karl's decision. The ecoregion link audit is done (see below).
- **Timings not measured.** There is no local elevation grid. Candidates, sources and sizes where found are in the results (item 4); which grid to download is Karl's and Opus's call.
- **Generator safeguards added.** The script now refuses a template file with an unrecognised or missing key, and each generated file is stamped with the template version and the script's commit state. The v4 template is now the live `profile_templates.md`.

## Open issues for Karl and Opus (found, not fixed)

1. **Wikipedia-derived text is not safe to ship as it stands.** 129 of 847 ecoregion links are flagged by name; of the 40 weakest, about 15 look wrong or too broad (from titles only; 89 unread). 7 stored summaries are model refusals; others read fluently but describe the wrong thing. Cause: the January harvest accepted any search hit whose words were contained in the ecoregion name (fuzzy scorer gives 100), and any Wikipedia redirect unchecked. Also a licensing question (CC BY-SA) not yet looked at. Options are in `wo05_results.md`; none applied. Keep link and gist as `maybe` units until resolved.
2. **Garbled ecoregion names:** 36 names in `lu_tec` have broken encoding and reach the Explorer; not checked in the signature.
3. **Headwater sentence at big rivers.** Kaifeng, on the Yellow River, reads "No other basin drains into this one". That is what the data say but may contradict what a reader knows. Not investigated.
4. **S8.2 zero list** includes `dist_sink` and `wetland_class`, which read oddly there.
5. **Basin average beside a point value** (Tbilisi: 418 m point, 5.3 °C basin mean over 255 to 3,838 m). For WO-06.
6. The catalog name "Flow distance to marine outlet" is looser than its name for basins ending at a lake-sea.

## Gate

Met, checked on the regenerated `wo05_filled_profiles.md` (stamped `profile_templates.md v4`): all ten profiles regenerate from the live template; S1.1b, S1.2a, S1.5a and S1.5b are filled at all nine places with a basin, and S1.2c fires at the three where the point and basin ecoregions differ (Timbuktu, Tbilisi, Alexandria); each water class has checked wording (item 2); each item in section 3 has an answer; both timings are reported as not measured, with the missing data named (no local elevation grid). Tristan da Cunha (no basin) shows the no-basin text and its placeholders, as intended. No v1 wording ("falls locally", "downstream of the basin") remains in the output.

## Files

`wo05_results.md`, `wo05_filled_profiles.md` (regenerated from live `profile_templates.md` v4), `wo05_wikilinks.csv` (all 847 rows, suspect flag), `profile_templates.md` (v4, live; the WO-05 working copy `profile_templates_v4_target.md` was deleted after the swap, recoverable from commit 58fae48), `profile_templates_v2_target.md` (Opus's original v2, untouched), notebook `notebooks/edop/whg/wo05_place_layer.ipynb`.
