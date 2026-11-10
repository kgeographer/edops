# WO-08: WO-07 decisions, six new units, and the coastline

2026-11-08, drafted by Opus after alignment with Karl. Goal-setting, not a specification. Target finish about Friday 13 November; the sample page is assembled after this WO, as a separate step, and sent by 21 November.

## Goal

Act on the decisions taken after WO-07, fill six more units of the profile, and add a coastline layer so the Coast and reach section speaks. At the end, the ten filled_profiles are the material for the sample page.

## Background to read first

`wo07_summary.md` and `wo07_filled_profiles.md`, `wo04_schemes.md` (GEnS zones), `wo03_results.md` (Q3 ecoregion shares, Q6 the point's position and the snap), the live `profile_templates.md`, the open-items file. Read **Things to keep in mind** at the end before starting.

## Places

The ten test places, regenerated in full. Five extra points for specific checks, not profiled in full: Dujiangyan and Oaxaca (river names), Akureyri and Levuka (snap), Tristan da Cunha (no basin). Use the coordinates from WO-03 and WO-07.

## A. Decisions from WO-07

1. **Date the land cover.** GLC2000 describes about 2000. Confirm the reference year of the cropland and pasture source too; if the two differ, state each.

   ```
   S5.title: Land cover around 2000
   S5.frame: Around 2000, {S5.1a} and {S5.1b}; {S5.1c}. {S5.2}
   ```

2. **No UNEP aridity sentence in Arctic climate zones.** The UNEP classes were drawn for drylands and mislead on tundra (Utqiaġvik "dry sub-humid"). Leave S2.4 out where the basin's GEnS zone is one of the Arctic zones. List which zones were treated this way and which of the 306 sample basins and ten places are affected. This uses a class already in the data, not a cutoff of ours.

3. **Slopes under 0.1%.** Say "a mean slope under 0.1%" instead of "0.0%".

4. **Missing values everywhere.** The engine handles -9999 for signatures, but WO-07's class words read `basin06` directly and a -9999 got through. Audit every direct read in the profile scripts (WO-04 to WO-07) so each treats missing values exactly as the engine does, preferably through one shared helper. Fix open item I-3 (-9999 stored as a class) with it. Report which units, if any, have been showing a missing value as data.

5. **A gate for river names.** Show a name only where two independent sources agree: the Natural Earth line's name (through its Wikidata label) and a Wikidata river item whose coordinates fall near the reach. Otherwise say "a river". If a model check of the disagreements is cheap, try it and report what it adds; it does not decide on its own. Report how many names survive the gate across the ten places, the extra points, and the 306 sample basins. Dujiangyan's "Tuo River" should not survive; the Niger, Kura and Yellow River should.

6. **Counts for every measure that qualifies.** Today S2.3 and S5.2 report a count for one measure only, even where the others also qualify. Report all qualifying measures in one sentence; a measure already stated as an extreme or "all but one" is not repeated.

   New keys:

   - `S2.3.counts`: "Compared with the {m} basins around it, its basin {list}." For example: "Compared with the nine basins around it, its basin receives less precipitation than five, is cooler than seven and is more humid than six."
   - `S5.2.counts`: the same pattern for cropland, pasture and forest.

## B. New units

1. **S2.1b, when the rain falls.** The Seasonality tab already classifies seasonality, with its own cutoffs (concentration 0.15, 0.35, 0.60). Use that rule rather than a new one, and map its classes to phrases in the existing slot ("rainfall averages about 189 mm a year, {S2.1b}"). Suggested phrases, which CC fits to the tab's classes:
   - `S2.1b.season`: "most of it falling between {m1} and {m2}"
   - `S2.1b.spread`: "spread through the year"
   - `S2.1b.two`: "in two seasons, {m1} to {m2} and {m3} to {m4}", if the tab distinguishes two seasons.

   Expected: Timbuktu between July and September.

2. **S3.4, lakes and wetlands.** Lake share from `lka_pc_sse` (in `basin06`, not yet in a payload); wetland extent from the rows already used. Silent when both are zero. Use the source's wetland definitions as they are; do not group or relabel them.
   - `S3.4`: "Lakes cover about {l}% of the basin and wetlands about {w}%." Each part appears only when its share is above zero.

3. **S1.3, the next ecoregion.** The distance from the point to the nearest polygon of a different ecoregion, and that ecoregion's name. No direction (WO-03: compass words are unreliable). Report the distances at the ten places and their distribution over the 306 sample basins, so Karl can set a limit beyond which the sentence stays silent; try 25, 50 and 100 km.
   - `S1.3`: "The {eco} ecoregion begins about {d} km away."

4. **S1.4, the basin's other ecoregions.** Ecoregions other than the point's and the basin's majority that cover more than a share of the basin. Report results at 5%, 10% and 20%; Karl chooses.
   - `S1.4`: "Its basin also takes in parts of the {eco1} [and {eco2}] ecoregion[s]."

5. **S8.3, the snap.** A point within 1 km of a basin and inside none is moved to the nearest basin (WO-03: this catches Akureyri and Levuka and nothing else). Points further away get the `no_basin` response, as now.
   - `S8.3`: "The point lies just outside the basin data and was moved {d} m to the nearest basin."

6. **S7.1a and S7.3, the coastline.** Choose a coastline dataset that fits (for example GSHHG at full resolution, OSM land polygons, or Natural Earth at 1:10 million), and say why. Report how it treats the Caspian and other large inland water: whether a basin on the Caspian counts as coastal decides what Tbilisi's "drains to the sea" should become (open item R3).
   - `S7.1a`: "{name} is about {d} km from the coast." Under 1 km: "{name} is on the coast."
   - `S7.3`: "The nearest edge of its basin is the coast." Only when the nearest part of the basin's outline to the point is coastline, as measured in WO-03 Q6.

   Check that S7.2 ("Its basin touches the sea") and S7.3 agree with the coastline layer at Alexandria and Utqiaġvik.

## Provisos

- Wording goes through `profile_templates.md` as its header says; rules stay in the script. New keys need script support before Karl saves the wording.
- Before any full run over the 306 basins, run the edge cases first: Tristan da Cunha, Alexandria, Utqiaġvik, Akureyri, Levuka, Kaifeng.
- Where a choice of cutoff is Karl's (S1.3, S1.4), report results and do not choose.
- Read-only against the database except for the I-3 fix and loading the coastline; record the commit.
- Where an item needs data or code that is not there, name it and stop on that item.

## Deliverables and gate

- `wo08_summary.md`: one page, read first, including the decisions waiting for Karl.
- `wo08_results.md`: one section per numbered item, with issues found.
- `wo08_filled_profiles.md`: the ten filled_profiles.

**Gate:** the ten filled_profiles regenerate from the current template version with every item in A done, every unit in B filled or silent by rule (with the cutoff results for S1.3 and S1.4 reported), the missing-value audit reported, and the name gate's survival rate reported.

## Things to keep in mind

Carried from WO-07, with additions marked new.

1. **Basins are not places.** Ring comparisons describe a basin among basins; they cannot see where a place sits inside its basin (Tbilisi).
2. **Setting speaks about the place; everything else names the basin.**
3. **Places are where people are.** Gazetteer places sit on rivers and coasts and in populous basins far more often than random basins do.
4. **A true sentence can still mislead.** Read each sentence with its neighbours (Kaifeng's headwater sentence is safe only with the Yellow River sentence after it).
5. **State what is true without a cutoff where possible:** extremes, "all", "all but one", counts, a share, a source's own class. Where a cutoff is unavoidable, anchor it in the source's classes and report results at several values.
6. **A basin mean hides a mixed basin.** Say "on average", show the number, prefer the source's labels.
7. **Respect the sources' own caveats.** Karst is mapped outcrop, an upper limit; aridity is stored multiplied by 100; soil is the top 5 cm.
8. **Silence is a valid output.**
9. **Unchecked data does not reach the sample page unflagged.**
10. *(new)* **We report sources; we do not correct them.** Where a value looks odd (Alexandria's karst beside unconsolidated sediments), the profile states what the source says, worded with the source's own caveats. Raising a question about a value is a matter for the roadmap (a form for readers to query or suggest edits), not for the rules.
11. *(new)* **Names need two sources.** A place name or river name shown to a reader must be confirmed by two independent sources; one source alone, or a model, is not enough.
12. *(new)* **Edge cases first.** Run the known edge cases before any long run.
13. 