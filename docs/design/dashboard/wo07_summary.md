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

## Still to try: maybes not yet attempted (for the next WO)

Of the 28 maybes in `wo04a_results.md`, 13 are filled (S1.1b, S1.1c folded into S4.1a, S2.3, S3.1a, S3.1b, S3.3, S4.1a, S4.1b, S4.3, S5.1c, S5.2, S6.3b, S6.5), 1 was resolved by dropping it (S6.4), and **14 have not been tried**: the 11 units below and 3 example rows. None of the maybes tried so far has turned out to be a no. The 7 nos are untouched by design.

| Unit | Says | What it needs | Kind |
|---|---|---|---|
| S2.1b | when the rain falls | monthly array (in the signature); a "mostly in {months}" rule; the Seasonality tab already has one with cutoffs (concentration 0.15, 0.35, 0.60) | rule, data in hand |
| S3.4 | lakes and wetlands share | `lka_pc_sse` is in basin06 but not in a payload; wetland shares are in the rows | rule, small read from the DB |
| S1.3 | next ecoregion, distance | distance from the point to the next ecoregion polygon (computable); direction dropped (compass words unreliable) | rule, live layer |
| S1.4 | basin also takes parts of other ecoregions | WO-03 shares (146 of 298 sample basins have one ecoregion at 5%, 111 two, 41 three or more); needs a share cutoff | rule plus a cutoff decision |
| S7.1a, S7.3 | distance to the coast; nearest basin edge is the coast | no coast-distance field (`dist_sink` is along the river); needs a coastline layer (Natural Earth or GSHHG); WO-03 Q6 edge kind (for 84 of 254 WH Cities the nearest edge is the coast) | one new layer, two units |
| S6.2c | description of a neighbouring basin | basins have no names; describe by character (ring rules) or by main river | design, medium |
| S1.2b | one-line ecoregion gist | stored gist per ecoregion (first sentence of the Wikipedia summary, or a reviewed line); 26 of 847 have no text; the Wikipedia text is not safe as it stands (129 of 847 links flagged) | decision on source, then lookup |
| S8.1b | data years | a glossary of years per dataset (Karl's data-source docs) | documentation |
| S8.3 | point moved N m | snap not built (about 1 km would catch the edge cases only) | build, small |
| S9.1 | link into EDOPS | a URL scheme, needs WHG agreement | decision with WHG |

Example rows from the mockup, also untried: S3.X1 (seasonal wetlands; needs S3.4 and the wetland class legend), S4.X1 (largely covered now by S4.1a and S4.2), S6.X1 ("a narrow corridor"; needs a shape measure and a cutoff).

**Parked, untouched:** I-3, R1, R2, E3 and the open-items file `WHG-profile_open-tems-post-WO7.md` (WO-07 cites it as `profile_open_items.md`); the "wetter" wording of S3.2b; point elevation depends on a live service (no local DEM); Wikipedia text is not safe for the payload (129 of 847 links flagged).

**Not decided:** pushing the branch.
