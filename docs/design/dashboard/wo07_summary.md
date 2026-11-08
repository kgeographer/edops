# WO-07 summary (read first)

2026-11-08. Detail: `wo07_results.md`. Filled profiles for the ten places: `wo07_filled_profiles.md`. Template: `profile_templates.md` v6. Branch `whg-profile`, local only.

**What was done**

- **A, ring sentences.** State an extreme, "all" or "all but one", else a count only when more than half the set (counts kept; three template lines switch them off). S6.4 removed, S6.5 widened to 11 measures, aridity never called "driest". Over 306 sample basins, 98% of basins with three or more neighbours get at least one comparison sentence.
- **B, class words.** Terrain (FAO slope class, percent shown; the three classes under 1% merged as "level"), soil composition with the USDA texture class (checked against the Soil Survey Manual), karst and permafrost, land cover (largest class other than cultivated), UNEP aridity class. Rock label in lower case. Terrain word removed from Setting. Every unit fills at every place with a basin.
- **C, nearest river.** S3.1 in three tiers (a named river of class 4 or larger within 25 km; else an unnamed river of class 5 or larger within 3 km; else silence); S3.3 "a much larger river nearby". Names from Natural Earth lines via a one-time Wikidata label lookup.

**Gate.** The ten filled_profiles regenerate from template v6 with A's adjustments; every B unit fills; every cutoff tried in C is reported. One departure: S3.1 is deliberately silent where no river is close (Karl: nothing about a river 70 km away), so it is not filled at every place with a basin (Timbuktu, Tbilisi, Kaifeng, Poltava have one; the other five are silent).

**Needs a decision (Karl, Opus)**

1. **River names can be wrong and nothing automatic catches it** (Oaxaca "Balsas" now silenced by the class 4 cutoff; Dujiangyan "Tuo River" still said). Whether the pilot shows names, and with what safeguard, is open (`wo07_results.md`, Part C).
2. **"Today" and "Land cover today"** are wrong for GLC2000 (year 2000) and HYDE; a stated date is Karl's preference.
3. **Utqiagvik "dry sub-humid"** (UNEP class on a precipitation-over-PET index reads odd for tundra).
4. **Alexandria karst "up to about 100%"** beside "unconsolidated sediments"; a source pattern, left as is.
5. The -9999 leak found in Part B probably also affects older units; take up with open item I-3.

**Parked, untouched:** I-3, R1, R2, E3 and the open-items file `WHG-profile_open-tems-post-WO7.md` (WO-07 cites it as `profile_open_items.md`); the "wetter" wording of S3.2b; point elevation depends on a live service (no local DEM); Wikipedia text is not safe for the payload (129 of 847 links flagged).

**Not decided:** pushing the branch.
