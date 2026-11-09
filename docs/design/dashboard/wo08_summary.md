# WO-08 summary

9 Nov 2026. Detail and evidence: `wo08_results.md`. Profiles from the current template (v15): `wo08_filled_profiles.md`. Branch `whg-profile`, nothing pushed.

## What was done

- **A1 to A6.** Land cover dated "around 2000"; no UNEP aridity sentence in the cold GEnS zones (1 to 4 and 6); "level" for slopes under 0.1%; missing values handled in one place (`missing.py`); river names need two sources (Natural Earth within 5 km and an OpenStreetMap line within 3 km); counts for every measure that qualifies.
- **B1 to B6.** Built: S2.1b (when the rain falls), S3.4 (lakes and wetlands), S1.4 (other ecoregions, 10% share), S8.3 (point moved to the nearest basin, up to 1 km), S7.2 and S7.3 (the seacoast). Tried and dropped: S1.3 (next ecoregion) and S7.1a (distance to the coast).
- **Data added** (additive, in `gaz`): `ne_coastline_10m`, `ne_rivers_10m` (Natural Earth copy with the Colorado ids corrected; the shapefile is untouched), `osm_river_lines`.
- **Gate.** Ten profiles regenerate from v15; the river names for Timbuktu, Tbilisi and Kaifeng survive the OSM check; 93 of 97 names shown on the test points, WH Cities and the sample pass, and three of the four blocks were right.

## Where we stand: placeholders remaining

The goal is to fill the template's placeholders. At the WO-04c baseline 22 units were placeholders; in the ten profiles at v15, **4 remain**. 16 are filled (several speak only where the data qualify, and are silent otherwise) and 2 were tried and dropped (S1.3, S7.1a). In WO-08 alone: filled S2.1b, S3.4, S1.4, S8.3, S7.3 (plus S7.2); dropped S1.3 and S7.1a.

The four that remain, each blocked on something outside the rules:
- **S1.2b**, a one-line ecoregion gist: needs stored summaries that are reliable (many were made from the wrong Wikipedia article; 7 are refusals; open items E1, E2).
- **S6.2c**, a description of a neighbouring basin: needs ring rules and wording.
- **S8.1b**, the years of the datasets: needs the glossary.
- **S9.1**, the link into EDOPS: needs the URL scheme from WHG.

## Decisions waiting for Karl

1. **OpenStreetMap attribution (ODbL).** Anything that shows an OSM-gated river name needs "contains information from OpenStreetMap, ODbL" on the page. Where does it go?
2. **Push.** Nothing is pushed. When, and does `whg-profile` merge to `main` only when the phase is accepted?
3. **Ring table counts `outside_active_domain` as 0.** About 193 of 3,486 member rows are really 1%, so S5.2 cropland and pasture comparisons tie where they should not. Fix by rebuilding the ring table (about 40 minutes), or leave?
4. **The signature's coast flag misses about a third of basins that touch the sea.** S7.2 therefore uses the flag or the coastline layer. Report to the maintainers, or leave?
5. **World-scale river names.** The OSM gate is built for 118 rivers. A version for the world is about 500 rivers and a few hours of Overpass queries, with a polite User-Agent that has a real contact. Not for the sample page. Plan it, or leave?

## For Opus

- **The place's point is often a centroid.** It can lie away from a city's port or shore, so statements tied to the point (S7.3, the elevation at the point, river distances S3.1 and S3.3, the S8.3 snap) may overstate precision. Keep S7.3? How should point-based statements be worded?
- **The coastline follows tidal estuaries** (Natural Earth, GSHHG and OSM alike), so S7.2 "touches the sea" is true to the data for ports such as Hamburg and Rotterdam, but does not say the open sea is near.
- **The Caspian is counted as sea** in the signature (`endo = 0`) and in the coastline layer, although it is hydrologically an inland (endorheic) lake. Tbilisi's "drains to the sea about 664 km beyond its outlet" depends on it (open item R3).
- **Wikidata ids on Natural Earth lines are unreliable for same-name rivers.** One hand fix (Colorado) was made because it produced a wrong block; other wrong ids that happen to pass the OSM check would not be seen.
- **Levuka's basin has 131 pieces (175,335 km²).** Coastal points with no ecoregion polygon fall back silently to the basin ecoregion.
- **Seasonality payload.** The `/whgmodal` payload should carry the twelve monthly precipitation and temperature values so WHG can draw its own chart.

## Still parked

I-3, R1, R2, E3, S3.2b ("wetter"), S1.2b placeholder, S6.2c, S8.1b, S9.1; the UNEP bands as a secondary source.
