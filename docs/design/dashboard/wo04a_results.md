# WO-04a results: a verdict for each unit of the dummy modal

2026-11-05. Provisional: the fill script (wo04c) will test the yes rows against real data. Unit ids refer to `modal_dummy_annotated.md`; the data sources are in `wo04a_inventory.md`. One row per sentence or part, with slots broken out only where they differ. This is a menu with a price on each item, not a recommendation on what to include.

**Verdict.** yes: a rule can fill it from data held now. maybe: possible once the thing named in 'Reads, or needs' exists (a cutoff or scheme, a glossary entry, a computed field, new data, or code). no: not feasible for v1. **Kind.** T: a relation or class read straight from the data (shown as the data row). H: a word that depends on a cutoff or a published scheme (needs the number and the cutoff). N: a value (needs the number). **Keyed.** B: stored per basin. L: the thin live layer, specific to the point. W: supplied by WHG. **Effort.** small: hours; medium: a day or two; large: more. All guesses.

## Counts

| Section | yes | maybe | no | rows |
|---|---|---|---|---|
| S1 Setting | 2 | 5 | 1 | 8 |
| S2 Climate | 3 | 2 | 1 | 6 |
| S3 Water | 6 | 5 | 0 | 11 |
| S4 Land and geology | 1 | 4 | 0 | 5 |
| S5 Land cover today | 2 | 2 | 2 | 6 |
| S6 Surroundings | 3 | 5 | 3 | 11 |
| S7 Coast and reach | 1 | 2 | 0 | 3 |
| S8 About these figures | 2 | 2 | 0 | 4 |
| S9 Buttons | 2 | 1 | 0 | 3 |
| **All** | **22** | **28** | **7** | **57** |

## S1. Setting

| Unit | What it says | Verdict | Kind | Reads, or needs | Keyed | Where the number is in the Full signature | Effort (guess) | Note |
|---|---|---|---|---|---|---|---|---|
| S1.1a | place name | yes | T | name from WHG, or the gazetteer | W | n/a | none |  |
| S1.1b | elevation at the point | maybe | N | live point elevation (OpenTopoData, Open-Meteo fallback) or WHG's own elevation; or reword to the basin's range, `elev_min` to `elev_max` (WB-07 exists) | L | range: Signature tab; point value: public signature only (to check) | small | reword gains a level |
| S1.1c | terrain word (flat ... mountainous) | maybe | H | a published relief class or a cutoff on relief range and slope (wo04b); `relief_range_m` is public-signature only, slope is in both | B | slope: Signature tab | medium | scheme choice |
| S1.2a | the ecoregion | yes | T | basin's majority ecoregion (`eco_id`, both payloads). The dummy names the point's ecoregion: point-in-polygon, one match for 297 of 298 sample points (WO-03 Q3) | B / L | basin's: Signature tab; point's: not shown | small | the two differ for about 6% of sample basins |
| S1.2b | one-line gist of the ecoregion | maybe | T | a stored gist per ecoregion: first sentence of the `eco_wikitext` summary, or an offline-written line that is reviewed; 26 of 847 ecoregions have no text | B | n/a | small to medium | stored text is a lookup; runtime generation is excluded by the locked decision |
| S1.3 | [other ecoregion, distance, direction] | maybe | N | distance from the point to the next ecoregion polygon (computable); direction: not available (compass words, WO-03 D2) | L | not shown | small | reword to distance only |
| S1.4 | [basin also takes parts of ecoregions 2 and 3] | maybe | H | area shares per basin (WO-03 Q3) and a share cutoff, swept; about half of sample basins have two or more at 5% | B | not shown | small | cutoff |
| S1.X1 | gist says 'between the Sahara and the wetter savannas to the south' | no |  | the relation exists only in the text; a rule cannot derive it |  |  |  | fine if kept inside a stored gist |

## S2. Climate

| Unit | What it says | Verdict | Kind | Reads, or needs | Keyed | Where the number is in the Full signature | Effort (guess) | Note |
|---|---|---|---|---|---|---|---|---|
| S2.1a | annual rainfall | yes | N | `precip_yr` | B | Signature tab | none |  |
| S2.1b | when the rain falls | maybe | H | monthly rainfall array (public signature) and a rule for 'mostly in {months}'; the Seasonality tab already has a sentence with cutoffs on concentration (0.15, 0.35, 0.60) | B | Seasonality tab (chart) | small | choose or reuse the rule |
| S2.2a | annual temperature | yes | N | `temp_yr` | B | Signature tab | none |  |
| S2.2b | coldest and warmest month, with means | yes | N | monthly temperature array (public `tmp_dc_monthly`); the payload does not say whether `temp_min` and `temp_max` are those months (WO-02 WB-06), the array settles it | B | Seasonality tab (chart) | small |  |
| S2.3 | [among the driest/wettest/warmest/coolest of N+1 basins] | maybe | H | ring ranks are not built; wording must report above, below and equal and handle ties and zeros (WO-03 D5). Alternative, built: Context percentile within a radius | B | Context tab (radius, not ring) | medium | two comparison sets |
| S2.X1 | 'wetter than the desert basins to the north, drier than the delta basins to the south' | no |  | compass words (D2) and class words for neighbours; reword to counts, as S2.3 ('drier than 4 of its 6 neighbours') |  |  |  |  |

## S3. Water

| Unit | What it says | Verdict | Kind | Reads, or needs | Keyed | Where the number is in the Full signature | Effort (guess) | Note |
|---|---|---|---|---|---|---|---|---|
| S3.1a | distance to a river | maybe | N | nearest reach above a size threshold (WO-03 Q5, `gaz.rivers`, 0 to 1 s); the threshold has to be chosen | L | not shown | small | reword option: the main river through the basin, basin-keyed |
| S3.1b | river name, or 'a river' | maybe | H | Natural Earth name when a named line is close to a close reach (WO-03 Q4: 60% of WH Cities, 38% of random basins), else generic; both distances swept | L | not shown | medium | absent name is never absent river |
| S3.1c | [the reach's upstream area] | yes | N | `upland_skm` of the reach | L | not shown | none |  |
| S3.2a | catchment above is N times the local basin | yes | N | `up_area` over `sub_area` (basin06); the areas rows carry neither; public signature has `up_area` | B | Analysis tab shows upstream area; the ratio is not shown | small |  |
| S3.2b | [wetter/drier/cooler than the local basin] | yes | H | Analysis tab: local and upstream precipitation, moisture, temperature as ratios, and a provenance class; fixed cutoffs 1.5x, 0.9 to 1.1, and 500 km² for 'undetermined' | B | Analysis tab | small | reuse built rule |
| S3.3 | [a much larger river: name, distance] | maybe | H | WO-03 Q5 gap: nearest reach above a threshold against the core's `up_area`; ratio and distance cutoffs both needed (WO-03 D9: rate not yet measured on WH Cities); name as S3.1b | L | not shown | medium | sweep |
| S3.4 | [lakes and wetlands share] | maybe | N | wetland shares are in the rows (WB-04); lake share `lka_pc_sse` is in basin06 but not in any payload | B | wetland: Signature tab; lakes: not shown | small |  |
| S3.5a | drains to the sea, distance | yes | N | `dist_sink` and `outlet_type`; wording must say along the river from the basin's outlet, not from the place | B | Analysis tab; Signature tab (Band E) | small | reworded; WO-03 I-7 |
| S3.5b | drains to an inland sink, distance | yes | N | same field; the Analysis label says 'ocean outlet' even for inland sinks | B | Analysis tab; Signature tab | small | reworded |
| S3.5c | closed basin | yes | T | `outlet_type` or `endorheic` | B | Analysis tab (badge); Signature tab | none |  |
| S3.X1 | 'seasonal wetlands cover a large share' | maybe | H | a share as a number (WB-04) or a size word with a cutoff; 'seasonal' needs the wetland class legend (not checked) | B | Signature tab | small |  |

## S4. Land and geology

| Unit | What it says | Verdict | Kind | Reads, or needs | Keyed | Where the number is in the Full signature | Effort (guess) | Note |
|---|---|---|---|---|---|---|---|---|
| S4.1a | relief description | maybe | H | as S1.1c | B | slope: Signature tab | medium | scheme choice |
| S4.1b | soil description (sandy, clay, loamy) | maybe | H | a published texture class from sand, silt and clay shares (USDA triangle: inputs present, basin means only; wo04b); the composition statement (WB-01: '66% sand ...') is a yes without a class word | B | Signature tab | small to medium |  |
| S4.2 | [underlying rock] | yes | T | `lith_class` (GLiM, majority class only; CAT-01) | B | Signature tab | none |  |
| S4.3 | [karst or permafrost: extensive/present/absent] | maybe | H | `karst`, `permafrost_extent` in percent; 'absent' is zero (T; EMP-01 handles `outside_active_domain`); 'extensive' and 'present' need cutoffs | B | Signature tab | small | cutoff |
| S4.X1 | 'low and nearly level'; 'over unconsolidated sediments' | maybe | H | relief word as S1.1c; the rock phrase is S4.2 (yes) | B |  |  |  |

## S5. Land cover today

| Unit | What it says | Verdict | Kind | Reads, or needs | Keyed | Where the number is in the Full signature | Effort (guess) | Note |
|---|---|---|---|---|---|---|---|---|
| S5.1a | cropland share | yes | N | `cropland_extent` (WB-08); zero reads as 'none recorded' (EMP-01) | B | Signature tab | none | zero at Timbuktu |
| S5.1b | pasture share | yes | N | `pasture_extent` | B | Signature tab | none |  |
| S5.1c | most of the rest is forest/shrubland/bare ground | maybe | T | `land_cover_name` (GLC2000 majority, 22 classes) or per-class shares in basin06; the dummy's three words are not GLC2000's class names, so use the source's labels or a mapping | B | Signature tab | small |  |
| S5.2 | [population density; higher/lower than most basins around] | maybe | N | density: `pop_density` (yes); the comparison is as S2.3 | B | density: Signature tab | medium | shares S2.3 |
| S5.X1 | 'concentrated along the river' | no |  | needs land cover inside the basin at fine grain; only basin aggregates are stored |  |  | large | new data (a land cover raster) |
| S5.X2 | 'sparse outside the town and the river corridor' | no |  | as S5.X1, for population |  |  | large | new data (a population grid) |

## S6. Surroundings

| Unit | What it says | Verdict | Kind | Reads, or needs | Keyed | Where the number is in the Full signature | Effort (guess) | Note |
|---|---|---|---|---|---|---|---|---|
| S6.1a | one of N+1 basins | yes | N | the ring (WO-03 Q1); point contacts excluded (D1); empty rings need wording | B | ring glyph only | none |  |
| S6.2a | upstream neighbour drains into it | yes | T | flow relation (WO-03 Q2) | B | not shown | none |  |
| S6.2b | it drains into the downstream neighbour | yes | T | flow relation | B | not shown | none | sinks with virtual links excluded |
| S6.2c | neighbour description | maybe | H | basins have no names; describe by character (ring rules) or by its main river (Q4) | B | values after selecting a neighbour | medium |  |
| S6.3a | direction ('to the north') | no |  | compass words are unreliable (WO-03 D2); a fitted direction is a possible Should |  |  |  | reword to counts |
| S6.3b | [contrast across the divide] | maybe | H | counts over off-stream neighbours ('3 of 4 are drier'); ring rules, ties, zeros | B | not shown | medium | reworded |
| S6.4 | [resembles its neighbours] | maybe | H | a cutoff swept; neighbours resemble the core (WO-02 hazard) | B | not shown | medium |  |
| S6.5 | [stands out for {variables}] | maybe | H | a ring 'furthest from the set' rule (like XB-01 within the set); Context tab has extremes against the globe and the region | B | Context tab (not ring) | medium |  |
| S6.X1 | 'a narrow corridor' | maybe | H | a shape measure from the basin geometry (not computed today) and a cutoff | B | not shown | small to medium |  |
| S6.X2 | 'the Niger arrives from the Inner Delta; continues east' | no |  | a named river with a direction; reword as S6.2 |  |  |  |  |
| S6.X3 | 'basins to the north are desert, far drier, almost no cropland' | no |  | as S2.X1 |  |  |  |  |

## S7. Coast and reach

| Unit | What it says | Verdict | Kind | Reads, or needs | Keyed | Where the number is in the Full signature | Effort (guess) | Note |
|---|---|---|---|---|---|---|---|---|
| S7.1a | distance to the nearest coast | maybe | N | no field exists (`dist_sink` is along the river, from the basin's outlet); needs coastline data, for example Natural Earth coastline or GSHHG | L | not shown | small to medium | new data |
| S7.2 | [basin touches the sea] | yes | T | `coast` flag; three meanings of coastal exist (WO-03 I-7) | B | Signature tab (Band E) | none | choose the flag |
| S7.3 | [nearest basin edge is the coast] | maybe | T | WO-03 Q6 edge kind, specific to the point | L | not shown | small |  |

## S8. About these figures

| Unit | What it says | Verdict | Kind | Reads, or needs | Keyed | Where the number is in the Full signature | Effort (guess) | Note |
|---|---|---|---|---|---|---|---|---|
| S8.1a | basin area | yes | N | `sub_area` (basin06); not in the areas rows | B | not shown | small |  |
| S8.1b | data years | maybe |  | a glossary of years per dataset (Karl's data-source docs); the payload names sources only | B | not shown | small | documentation |
| S8.2 | [n measures with no value, reasons] | yes | T | row `status` and `coverage`; the meaning of -9999 per variable is not in the payload (EMP-03) | B | Signature tab (statuses) | small |  |
| S8.3 | [point was moved N m] | maybe | N | snap not built (WO-03 D10: about 1 km) | L | not shown | small |  |

## S9. Buttons

| Unit | What it says | Verdict | Kind | Reads, or needs | Keyed | Where the number is in the Full signature | Effort (guess) | Note |
|---|---|---|---|---|---|---|---|---|
| S9.1 | Full environmental signature in EDOPS | maybe |  | a URL scheme for linking from WHG into EDOPS; not defined (out of scope for WO-03 and WO-04) |  | n/a | small | needs WHG agreement |
| S9.2 | Ecoregion on Wikipedia | yes | T | `eco_wikitext` link, 821 of 847; hide otherwise | B | n/a | none |  |
| S9.3 | Data as JSON | yes |  | the endpoint's own response | B | n/a | none |  |

## What the table shows

- **16 yes or maybe rows rest on numbers the Full signature does not show today** (column 'not shown'): S1.3, S1.4, S3.1a, S3.1b, S3.1c, S3.3, S6.2a, S6.2b, S6.3b, S6.4, S6.X1, S7.1a, S7.3, S8.1a, S8.1b, S8.3. These are mostly the WO-03 computations (rivers, ecoregion shares, ring, point position). For these to be defensible with the Full signature button, the numbers would have to be added to it, or reached some other way.
- **The live layer** (rows keyed L, or B / L): S1.1b, S1.2a, S1.3, S3.1a, S3.1b, S3.1c, S3.3, S7.1a, S7.3, S8.3.
- **No** rows: S1.X1, S2.X1, S5.X1, S5.X2, S6.3a, S6.X2, S6.X3. Four involve direction words (S2.X1, S6.3a, S6.X2, S6.X3), two need positions inside the basin (S5.X1, S5.X2), one depends on text only (S1.X1).
- **The largest dependency is the ring rules** (S2.3, S5.2, S6.2c, S6.3b, S6.4, S6.5): one set of rules (rank, counts above and below, ties, zeros, a cutoff for 'among' and 'resembles') serves several rows. Context-tab percentiles are built and cover some of this against the globe and a radius, not against the ring.
- **The largest cutoff dependency** is the H rows: they need a published scheme (wo04b) or a swept cutoff. The ones that could take a scheme: S1.1c, S4.1a, S4.1b.
