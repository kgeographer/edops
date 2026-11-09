# WO-09: fixes before the demo page

2026-11-09, drafted by Opus after alignment with Karl. Goal-setting, not a specification. Small items only; target finish about Wednesday 11 November. The demo page is WO-10, separately.

## Goal

Close the loose ends found in WO-08 so the ten profiles are fit to show. No new units.

## Background

`wo08_summary.md`, `wo08_filled_profiles.md`, the live `profile_templates.md` (v15). **Things to keep in mind** in WO-08 still applies; in particular, edge cases first, and we report sources, we do not correct them.

## Items

1. **Rebuild the ring table** so a value flagged `outside_active_domain` keeps its value instead of being counted as 0 (WO-08 decision 3: about 193 of 3,486 member rows are really about 1%). Regenerate, and report which comparison sentences change at the ten places.

2. **Check Timbuktu's "no cropland is recorded".** Its fill note says the value was flagged outside the active domain. Report the raw value. If it is above zero, the sentence must say so, as Chaco Canyon's "about 1%" does. Then check every profile in the 306-basin sample: how often does "no cropland" or "no pasture" appear where the raw value is above zero? Fix the rule so "none" is said only of a true zero.

3. **Land cover wording when shares are zero.** Two cases read badly now:
   - Cropland zero, pasture not: "no cropland is recorded and 28% is pasture" has lost "of the basin".
   - Both zero (Utqiaġvik): "no cropland is recorded and no pasture is recorded; the commonest other cover…".

   Proposed wording (new keys or branches need script support; Karl saves the wording):

   ```
   S5.1b.some_full: {value} of the basin is pasture
   S5.both_none: neither cropland nor pasture is recorded; the commonest cover is {label}, at about {share}%
   ```

   `S5.1b.some_full` is used when cropland is zero. `S5.both_none` replaces the whole of `{S5.1a} and {S5.1b}; {S5.1c}` when both are zero. "Other" is dropped when nothing has been named before it.

4. **The "no percentile" list (open item R2).** List only measures that are shares or extents: leave out "Flow distance to marine outlet" (already said in Water) and the wetland class. When a measure and its upstream version are both zero, name it once.

5. **OpenStreetMap credit.** When a profile shows a river name that passed the OSM check, add a line to About these figures. Silent otherwise.

   ```
   S8.osm: River names contain information from OpenStreetMap, available under the ODbL.
   ```

6. **Where the point comes from.** One line in About these figures, always shown when a profile states a point elevation or a distance:

   ```
   S8.point: Elevation and distances are measured from the place's point in WHG, which may be the centre of a town rather than its shore or riverbank.
   ```

7. **Drop S7.3** ("The nearest edge of its basin is the seacoast") for now. Since distance to the coast was dropped, it repeats S7.2 at both coastal places. Keep the code; silence the unit.

8. **Fallbacks are noted.** Where the point's ecoregion falls back to the basin's (Levuka and other coastal points outside every ecoregion polygon), say so in the fill notes.

9. **The no-basin place.** Include Tristan da Cunha's profile in the filled profiles, showing exactly what a place with no basin gets.

10. **Flagged Wikipedia links.** Hide the Wikipedia button where the ecoregion's link is flagged in `wo05_wikilinks.csv` (Timbuktu's "Sahel" is one). Report how many of the ten places lose the button.

## Not in this WO

- Monthly precipitation and temperature values in the `/whgmodal` payload: agreed, for the endpoint work in January. Add to the open items.
- The Caspian wording (R3), world-scale river names, and a note to the HydroSHEDS team about the coast flag: open items.
- Still parked: I-3 if not already closed by WO-08's missing-value work (say which), R1, E3.

## Provisos

- Wording through `profile_templates.md` with a version and a Changes line; rules in the script.
- Edge cases first: Tristan da Cunha, Alexandria, Utqiaġvik, Levuka, Kaifeng, Timbuktu.
- After the gate, push the `whg-profile` branch to the remote as a backup (Karl's decision); do not merge to `main`.

## Deliverables and gate

- `wo09_summary.md`: one page, read first.
- `wo09_filled_profiles.md`: the ten profiles, plus Tristan da Cunha.

**Gate:** every item above is done or its blocker named; the profiles regenerate from the current template version; no profile says "none" of a share whose raw value is above zero.
