# WO-04c results: the dummy filled from real data

2026-11-05. Notebook `notebooks/edop/whg/wo04c_fill.ipynb`, rules in `scripts/edop/whg/wo04_fill.py`, commit 3623c5d plus uncommitted work. No LLM. Each result is a *filled_profile*: the dummy's template with every `yes` unit filled from data and every `maybe` or `no` unit left as a visible placeholder `⟦id maybe: needs ...⟧`. The ten filled_profiles are in `wo04_filled_profiles.md` (generated). Wording is the dummy's, not polished.

## What was tested

16 units (the `yes` rows of `wo04a_results.md` that a basin's data can fill; S1.1a is WHG's name and S3.1c, S9.3 need no basin data). Ten test places, then 306 basin interior points (the WO-02 sample, saved to `output/edop/whg/wo04c_fill.csv`). Every call went to the local server (`/api/signature`, `/api/areas`) and database.

## Fill rates over the 306 sample basins

"Not applicable" means an optional part of the template that the data says should not appear (no upstream neighbour, inland basin, and so on). It is left out by rule and is not a failure.

| Unit | Filled | Not applicable | Could not fill |
|---|---|---|---|
| S1.2a ecoregion (basin's majority) | 306 | 0 | 0 |
| S2.1a rainfall | 306 | 0 | 0 |
| S2.2a temperature | 306 | 0 | 0 |
| S2.2bc coldest and warmest month | 306 | 0 | 0 |
| S3.2a catchment ratio | 306 | 0 | 0 |
| S3.2b wetter than the local basin | 16 | 290 | 0 |
| S3.5 where the basin drains | 306 | 0 | 0 |
| S4.2 rock | 306 | 0 | 0 |
| S5.1a cropland | 306 | 0 | 0 |
| S5.1b pasture | 306 | 0 | 0 |
| S6.1a ring size | 306 | 0 | 0 |
| S6.2 up- and downstream neighbours | 184 | 122 | 0 |
| S7.2 basin touches the sea | 53 | 253 | 0 |
| S8.1a basin area | 306 | 0 | 0 |
| S8.2 measures with no value | 306 | 0 | 0 |
| S9.2 Wikipedia button | 301 | 0 | 5 |

The only units that could not be filled are 5 Wikipedia buttons (the ecoregion has no Wikipedia text).

The Analysis rule's class for the 306 sample basins: Catchment-uniform 135, Endorheic 56, Coastal terminal 53, Local-dominant 46, Exogenous water supply 16.

## Issues found

1. **S3.2b fires for 16 of 306 basins (5%).** The dummy sentence ("most of the water passing here falls far upstream ... wetter than it") fits only the Exogenous class, and the built rule has no "drier" or "cooler" statement. The other four classes have no dummy wording. S3.2a (the ratio) fills everywhere, but its sentence only makes sense where upstream water matters. This is the largest gap among the `yes` units.
2. **Wikipedia link for ecoregion 833 is wrong.** `public.eco_wikitext` maps eco_id 833 (North Saharan Xeric Steppe and Woodland) to the generic article "Woodland"; the Alexandria button shows it. Other rows may have the same problem; not checked.
3. **Basin average against the place.** Climate figures are basin averages, but the sentences read as the place's. Tbilisi's basin is 23,251 km² and the filled_profile says "Temperatures average 5.3 °C". Whether that suits a statement about the city is open; the point value (live layer) would settle it. The S8 line says the figures describe the basin; the Climate sentence does not.
4. **"Drains to the sea about 0 km downstream"** at Alexandria and Utqiagvik (Coastal terminal; `dist_sink` is 0). The S3.5 sentence needs a rule for 0.
5. **"Drains to the sea" at Tbilisi.** The data gives `endo=0`. The river reaches the Caspian, which is an enclosed sea. How the source classes it was not checked.
6. **`dist_sink` is among the "zero here, no percentile" measures** at Alexandria and Utqiagvik. For a coastal terminal basin that is a true zero, so the S8.2 list is correct but the reader may find it odd.
7. **Alexandria karst is 100%** in the payload. Raw value as delivered; not checked against the source.
8. **S1.2a names the basin's majority ecoregion**, not the point's. About 6% of sample basins differ (WO-03 Q3).
9. **Tristan da Cunha has no basin.** The filled_profile is a short stub (structured `no_basin`), as designed.

Corrected during this work: land cover name read from the areas rows (not in the public bands); S8.2 split so that "zero here" and "no value" are different statements; thousands separators; population density to one decimal; note wording for non-firing optional parts.

## Cost of a larger run

306 points took 480 s, about 1.6 s per point. For all 16,397 L6 basins that extrapolates to about 7 hours (L8, 190,675 basins: about 83 hours). The split between the two server calls and the live elevation lookup was not measured. A persisted build would read the database directly and should be faster.

## What this says for the demo

All `yes` units fill reliably over the sample. The weight of the demo rests on the 28 `maybe` rows (see `wo04_summary.md`).
