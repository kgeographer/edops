# WO-07: WO-06 adjustments, class words, and the nearest river

2026-11-07, drafted by Opus for Karl's review. Goal-setting, not a specification. The last planned build before the sample page; cut line Wednesday 18 November.

## Goal

Three parts, in order:

- **A.** Adjust the WO-06 sentences after reading the ten profiles.
- **B.** Fill the class words (terrain, soil, land cover, karst and permafrost, aridity) from the sources' own classes, following `wo04_schemes.md`.
- **C.** Fill the nearest river (S3.1) and "a much larger river nearby" (S3.3).

At the end, the ten filled_profiles should have no placeholders in Land and geology or Land cover, and the Water section should say which river the place is near.

## Background to read first

`wo06_summary.md` and `wo06_filled_profiles.md`, `wo04_schemes.md` (for B), `wo03_results.md` Q4 and Q5 (for C), `profile_templates.md` (live version), `profile_open_items.md`. Read **Things to keep in mind** at the end before starting.

## A. Adjustments to the WO-06 sentences

1. **Speak only extremes, "all", and "all but one".** Middle counts ("less precipitation than three of the five basins around it") read as noise and make up most of what fires. Keep extremes and "all" as built; add "all but one" as a new form; drop other counts from the sentences. Counts stay in the fill notes and, later, the payload.
2. **Drop S6.4.** A value outside the neighbours' range is the same as being highest or lowest of the set, so S6.4 counts what S6.5 names. Widen S6.5 to name extremes on any measure not already stated in Climate or Land cover, up to three, in the order of the WO-06 measure lists. Report how often the cap of three bites.
3. **Leave population density and human footprint out of the ring sentences.** Places in a gazetteer are where people are, so a place's basin will usually have the highest density of its ring; the sentence says nothing. Keep both in the fill notes.
4. **One sentence pattern for extremes.** Fold the extremes of a section into one sentence: "Of the eight basins that meet here, it receives the least precipitation and is the most arid."
5. **Number style.** If either number in a count is above ten, use figures for both ("10 of the 12", not "ten of the 12").
6. **Check Kaifeng's "It drains into two of them".** A basin has one next basin downstream. Find whether this counts a basin further down, a branching in the source, or an error, and fix the rule if needed.

Template lines (Karl saves them with a version bump; new keys need script support):

```
S2.3.extreme: Of the {n} basins that meet here, it {cmp}.
S5.2.extreme: Of the {n} basins that meet here, it has {cmp}.
S3.2.headwater: No other basin drains into this one: its rivers rise within it.
S5.1b.some: {value} is pasture
```

New keys: `S2.3.allbutone`, `S5.2.allbutone` and `S6.3.allbutone`, worded on the pattern "Its basin is {cmp} than all but one of the {m} basins around it." The extreme forms of `cmp` change to fit ("receives the least precipitation", "is the most arid", "the most cropland"). Where Climate and Land cover extremes would repeat the "Of the n basins" opening in consecutive sections, CC may propose a lighter second opening.

## B. Class words

Use the sources' own classes wherever `wo04_schemes.md` found them, show the number beside any class read from a mean, and say "on average" where a basin mean is classed.

- **Terrain (S4.1a).** FAO slope gradient class (Guidelines for soil description, 2006, Table 7) on the basin's mean slope converted to percent, with the percent shown. "Mountainous" has no support in that table; do not use it. Remove the terrain word from Setting (S1.1c): Setting gives the elevation range, which already says more, and the word then appears once, in Land and geology.
- **Soil (S4.1b).** The composition is the fact: "topsoil that averages 66% sand, 20% silt and 14% clay". Add the USDA texture class only after checking the class boundaries against the USDA Soil Survey Manual or FAO Figure 4; normalise the three shares to 100 first, and report where that changes the class.
- **Rock (S4.2).** The GLiM label, in lower case in the sentence ("unconsolidated sediments").
- **Land cover (S5.1c).** The GLC2000 label of the largest class other than cultivated and managed areas, with its share. Where the majority class is "Cultivated and managed areas" (Tbilisi, Kaifeng, Lviv, Poltava), the current sentence says cultivation covers "most of the rest" after the cropland share has been stated; that contradicts itself. Report how often the second-largest class is itself small (for example under 10%), so we can see whether the sentence needs a floor.
- **Karst and permafrost (S4.3).** State the share; silent at zero. Karst is mapped outcrop, an upper limit, so say "up to": never say karst is absent. Alexandria's 100% is unchecked against the source (open item D1); report what Alexandria's sentence would say, and Karl decides whether it appears on the sample page.
- **Aridity (new, S2.4).** The UNEP aridity class on the aridity index (stored multiplied by 100; Timbuktu's 9 is 0.09, arid), with the index shown. The bands are confirmed only from secondary sources; say so in the results, and check them against a primary source if one can be found quickly.

Template lines:

```
S1.frame: {name} sits at about {S1.1b} m above sea level, in a basin that runs from about {S1.5a} m to {S1.5b} m. It lies in the {S1.2a} ecoregion, {S1.2b}. {S1.2c} {S1.3} {S1.4}
S4.frame: Across the basin, the land is {S4.1a}, with topsoil that averages {S4.1b}. The underlying rock is mostly {S4.2}. {S4.3}
S5.frame: Today {S5.1a} and {S5.1b}; {S5.1c}. {S5.2}
```

New keys and what they should show:

- `S4.1a`: "{class} on average (a mean slope of {pct}%)", for example "very gently sloping on average (a mean slope of 1.5%)".
- `S4.1b`: "{sand}% sand, {silt}% silt and {clay}% clay", with ", a {texture} texture" added when the class is confirmed.
- `S4.3.karst`: "Karst outcrop covers up to about {k}% of the basin."
- `S4.3.permafrost`: "Permafrost underlies about {p}% of it."
- `S5.1c`: "the commonest other cover is {label}, at about {share}%".
- `S2.4`: "Its aridity index of {ai} falls in the UNEP {class} class." Appended to S2.frame.

## C. The nearest river

Use `gaz.rivers` (complete, per WO-04; `gaz.hydrorivers` is not), its discharge classes `ord_flow` (powers of ten in m³/s), and the name matching from WO-03 Q4.

- **S3.1, the nearest river.** The nearest reach to the point above a minimum size, its distance, and its name where the match is close; otherwise "a river". The minimum size is a choice: try discharge class 5 (10 m³/s or more) and class 6 (1 m³/s or more), and report what each gives at the ten places. Expected: Timbuktu about 13 km from the Niger.
- **S3.3, a much larger river nearby.** A reach within a distance D whose discharge class is at least two steps larger (a factor of 100) than the largest reach in the place's own basin. Try D at 10, 25 and 50 km. Kaifeng should report the Yellow River. Report the rate across the 306 sample basins, and across the World Heritage Cities used in WO-03 (open item D9 follow-up: random basins understate it).
- **Names.** Name a river only when a named line lies close to the matched reach (WO-03 Q4's test). Report doubtful matches.

New keys:

- `S3.1.named`: "about {d} km from the {river}".
- `S3.1.unnamed`: "about {d} km from a river".
- `S3.3.named`: "A much larger river, the {river}, runs about {d} km away."
- `S3.3.unnamed`: "A much larger river runs about {d} km away."

The cutoffs here (minimum size, D, two classes) are ours, anchored in the source's own classes. Report the results at each value tried; Karl chooses.

## Provisos

- Wording goes through `profile_templates.md` as its header says; rules stay in the script.
- Parked housekeeping stays parked (I-3, R1, R2, E3); Karl and CC review the open items after this WO.
- Read-only against the database; record the commit.
- Where an item needs data or code that is not there, name it and stop on that item.

## Deliverables and gate

- `wo07_summary.md`: one page, read first.
- `wo07_results.md`: one section per part (A, B, C), with the cutoff results in C and issues found.
- `wo07_filled_profiles.md`: the ten filled_profiles.

**Gate:** the ten filled_profiles regenerate from the current template version with A's adjustments made, every unit in B filled or its blocker named, S3.1 filled at every place with a basin, and the results for each cutoff value tried in C reported.

## Things to keep in mind

Observations from WO-03 to WO-06 that apply to this work and to what follows. They travel with the process; add to them.

1. **Basins are not places.** Ring comparisons describe a basin among basins; they cannot see where a place sits inside its basin. Tbilisi's basin is the largest of its ring and contains the mountains, so it differs little from its neighbours; what makes Tbilisi distinctive is its position low at the basin's eastern end. That needs the point layer (open item L3), not more ring rules.
2. **Setting speaks about the place; everything else names the basin** (framing A). A sentence that reads as about the place but carries a basin value is wrong for the reader even when the number is right (Tbilisi's 5.3 °C).
3. **Places are where people are.** Gazetteer places sit on rivers, coasts and in populous basins far more often than random basins do. Measures of people (population, human footprint) are close to circular for them; rates from the random sample of 306 basins understate how often river and coastal cases arise.
4. **A true sentence can still mislead.** Kaifeng's "No other basin drains into this one" follows the data, but a reader knows the Yellow River runs past the city. The sentence is safe only when the sentence that follows sets it right (S3.3). Read each sentence with its neighbours.
5. **State what is true without a cutoff where possible:** extremes, "all", "all but one", a share, a source's own class. Where a cutoff is unavoidable, anchor it in the source's own classes and report results at several values.
6. **A basin mean hides a mixed basin.** Say "on average" when classing a mean, show the number, and prefer the source's labels to words of ours.
7. **Respect the sources' own caveats.** Karst is mapped outcrop, an upper limit; aridity is stored multiplied by 100; soil composition is the top 5 cm.
8. **Silence is a valid output.** A section with nothing true to say says nothing.
9. **Unchecked data does not reach the sample page unflagged.** Alexandria's karst and the ecoregion links (open items D1, E1) need a decision before the page is assembled.


