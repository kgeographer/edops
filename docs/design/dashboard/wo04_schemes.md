# WO-04b: published classification schemes for the class words in the dummy modal

2026-11-05. For each class word in `modal_dummy.md`: is a class already in the data, is there a published scheme that could supply the word instead of a cutoff of ours, do its inputs exist, and does it fit a basin value. Suggestions are labelled as such; the choice is Karl's and Opus's.

**How well each source was checked** (marked on every citation):
- **P**: read in a primary document in this session (the BasinATLAS catalog PDF, the HydroBASINS and HydroRIVERS technical documents, the FAO soil description guidelines).
- **S**: confirmed only from secondary web sources; the primary document was not read.
- **U**: not retrieved; named from memory or from a search that surfaced only the title.

## Summary

| Class word | Dummy units | Class already in the data | Published scheme | Inputs present | Fits a basin | Suggested |
|---|---|---|---|---|---|---|
| Terrain: flat, rolling, hilly, mountainous | S1.1c, S4.1a, S4.X1 | no | FAO slope classes and SOTER landform (P); mountain definitions (S, U) | mean slope, elevation min and max, relief range | partly | FAO slope class on the mean slope, number shown |
| Soil: sandy, clay, loamy | S4.1b | no | USDA texture classes (S); FAO texture triangle (title only) | sand, silt, clay means (top 5 cm) | partly | composition as the fact; class word optional |
| Rock type | S4.2, S4.X1 | **yes**, 16 GLiM classes | Hartmann and Moosdorf 2012 (P) | majority class | yes | source labels |
| Land cover: forest, shrubland, bare ground | S5.1c | **yes**, 22 GLC2000 classes and shares | Bartholomé and Belward 2005 (P) | majority and per-class shares | yes | source labels |
| Ecoregion, biome | S1.2a | **yes** | Dinerstein et al. 2017 (P) | basin majority; point lookup | yes | as is |
| Climate and aridity words ('desert', 'arid') | S2.X1, S6.X3 | **yes**, 18 GEnS zones | UNEP aridity classes (S); Köppen-Geiger (S) | aridity index, monthly climate | partly | GEnS zone name, or UNEP class on the index |
| Wetland type, 'seasonal' | S3.4, S3.X1 | **yes**, 12 GLWD classes | Lehner and Döll 2004 (P) | majority class, extents | yes | source labels; 'seasonal' only for class 9 |
| Karst, permafrost: extensive, present, absent | S4.3 | no (percent only) | IPA permafrost bands (S) | percent extent | **no** | state the share or zero; do not say 'absent' for karst |
| Drainage type | S3.5 | **yes** | source's own (P) | `endo`, `outlet_type` | yes | as is |
| River size: 'a much larger river' | S3.3 | **yes**, `ord_flow` 10 classes | Lehner and Grill 2013 (P) | on every reach | yes | step in the source's own classes |
| Comparatives: driest, among, resembles, stands out | S2.3, S5.2, S6.4, S6.5 | no | none | n/a | n/a | rank and counts; cutoffs stay ours, swept |

## Terrain: flat, rolling, hilly, mountainous (S1.1c, S4.1a, S4.X1)

- **In the data:** no class. `slope_avg` (degrees, basin mean), `elev_min`, `elev_max` (both payloads), `relief_range_m` (public signature only).
- **Schemes.**
  - FAO *Guidelines for soil description*, 4th ed. 2006, Table 7, slope gradient classes (**P**): flat 0 to 0.2%, level 0.2 to 0.5, nearly level 0.5 to 1.0, very gently sloping 1 to 2, gently sloping 2 to 5, sloping 5 to 10, strongly sloping 10 to 15, moderately steep 15 to 30, steep 30 to 60, very steep over 60. The guidelines say the classes may need to be modified to fit local topography.
  - Same document, Table 4, hierarchy of major landforms (from the SOTER database, ISRIC 2005) (**P**): by gradient and relief intensity (m per km). Level land: gradient under 10% and relief under 50 m/km (plain, plateau, depression, valley floor). Sloping land: 10 to 30% and 50 to 300 m/km (hill, mountain, dissected plain, escarpment zone, valley). Steep land: over 30% (hill, mountain, escarpment zone, valley). The guidelines say relief intensity is the median difference between the highest and lowest point per specified distance.
  - FAO soil map legend groupings (level to gently undulating, rolling to hilly, steeply dissected to mountainous): seen only in a Wikipedia summary (**S**); thresholds not confirmed. These match the dummy's wording most closely.
  - Mountain definitions: Kapos et al. 2000 (six classes from elevation and local elevation range, GTOPO30) and Körner et al. 2011 (ruggedness only): titles and one-line summaries from a search (**S**). Meybeck, Green and Vörösmarty 2001, a relief typology in *Mountain Research and Development* 21(1): not retrieved (**U**).
- **Inputs:** slope and elevation range present. Relief intensity per km is not stored; it would have to be computed from the basin geometry, and it depends on the distance chosen.
- **Fit to a basin:** these are site or terrain-unit classes. A basin mean slope can be classed, but a basin of plain and mountain averages to something gentle. Only the mean (and the upstream mean) is stored, not the distribution. L6 basins are large (median 5,318 km²; 10th percentile 754, 90th percentile 19,343, over all 16,397).
- **Suggested:** FAO Table 7 class names for the mean slope, with the number shown (the degrees converted to percent). The word "mountainous" has no support from this table (steep is 30% or more); a mountain definition would need a DEM-based grid not stored here.

## Soil: sandy, clay, loamy (S4.1b)

- **In the data:** no class. `pct_sand`, `pct_silt`, `pct_clay` (basin means; also upstream).
- **Provenance (P):** SoilGrids1km, Hengl et al. 2014; **the 0 to 5 cm top layer**; NoData pixels (mostly deserts and open water) excluded from averages; -9999 where the whole unit has none.
- **Schemes.** USDA soil texture classes: twelve classes defined on sand, silt and clay percentages summing to 100 (**S**: study notes and encyclopaedia summaries; the primary source is the USDA Soil Survey Manual, Handbook 18, not read). The FAO guidelines include a texture triangle (Figure 4, "Relation of constituents of fine earth by size, defining textural classes", **title only**). The FAO "key to textural classes" (Table 25, **P**) is a hand-texturing key and cannot be used with percentages.
- **Fit to a basin:** the triangle classes a soil sample's fine earth fraction. A class read from three basin means describes the average composition of the surface 5 cm, not the commonest soil in the basin; mixed basins can land on a class that few places in the basin have. The three means do not sum to exactly 100 (WO-02 WB-01 prints a note beyond 1.5 points).
- **Suggested:** the composition ("66% sand, ...") as the fact; a class word optional, worded as the average topsoil composition, after checking the boundaries against Handbook 18 or FAO Figure 4.

## Rock type (S4.2, S4.X1)

- **In the data (P):** `lit_cl_smj`, spatial majority of 16 GLiM classes (labels in `public.lu_lit`): unconsolidated sediments, basic and acid and intermediate volcanic and plutonic rocks, siliciclastic, mixed and carbonate sedimentary, metamorphic, pyroclastics, evaporites, water bodies, ice and glaciers, no data. Hartmann and Moosdorf 2012.
- **Fit:** majority class only; no per-class shares are stored for lithology. "Mostly" is the honest word.
- **Suggested:** the source label without its code (for example "Unconsolidated Sediments").

## Land cover: forest, shrubland, bare ground (S5.1c)

- **In the data (P):** `glc_cl_smj` and per-class percent shares `glc_pc_s01` to `s22` for 22 GLC2000 classes (labels in `public.lu_glc`, for example "Sparse herbaceous or sparse shrub cover", "Bare areas", "Tree cover, broadleaved, evergreen"). Bartholomé and Belward 2005 (year 2000). Potential natural vegetation (Ramankutty and Foley 1999, 15 classes, `lu_pnv`) is a separate scheme for what would grow without people.
- **Fit:** yes, a basin majority plus shares.
- **Suggested:** the source's labels. The dummy's three words (forest, shrubland, bare ground) are a grouping of ours; if wanted, the grouping should be written down as a mapping of the 22 classes.

## Ecoregion and biome (S1.2a)

- **In the data (P):** terrestrial ecoregions and biomes, Dinerstein et al. 2017 (updating Olson et al. 2001): 847 ecoregions, 14 biomes plus N/A (`lu_tec`, `lu_tbi`). Basin majority in the payloads; the point's ecoregion by lookup (WO-03 Q3).
- **Suggested:** as is. The scheme is categorical, so no cutoff is involved in naming one.

## Climate and aridity words (S2.X1, S6.X3 'desert', 'arid')

- **In the data (P):** GEnS climate zones (18, `lu_clz`: "Arctic 1" through "Hot and arid", "Extremely hot and xeric", "Extremely hot and moist") and 125 strata (`lu_cls`), Metzger et al. 2013, spatial majority; also EDOPS's own derived climate class (rainfall modality by phase, WO7). Timbuktu: "Extremely hot and xeric".
- **Schemes.**
  - UNEP aridity classes on the aridity index (P/PET): hyper-arid under 0.05, arid 0.05 to 0.2, semi-arid 0.2 to 0.5, dry sub-humid 0.5 to 0.65, humid 0.65 and over (**S**: consistent across secondary sources; attributed to UNEP 1992 and to Middleton and Thomas 1997, *World Atlas of Desertification* 2nd ed.; the edition and page were not confirmed, and the 1997 map is reported to have changed two boundaries).
  - Köppen-Geiger: Beck et al. 2018, *Scientific Data* 5:180214, 1 km maps, present day 1980 to 2016 (**S**). Not in the data; applying its rules to basin-mean monthly climate would be our own classification, not Beck's map classes.
- **Inputs (P):** `aridity` is the Global Aridity Index, Zomer et al. 2008, basin average, **stored multiplied by 100** and capped. Timbuktu's value of 9 is an index of 0.09, which sits in the UNEP arid band. The index's own PET method may differ from the one the UNEP bands were defined with (not checked).
- **Fit:** classing a basin's mean index hides mixed basins.
- **Suggested:** the GEnS zone name where a climate word is wanted, or the UNEP class from the index with the number shown. Both are citable; neither needs a cutoff of ours.

## Wetland type, 'seasonal' (S3.4, S3.X1)

- **In the data (P):** `wet_cl_smj`, 12 GLWD classes (`lu_wet`: lake, reservoir, river, freshwater marsh and floodplain, swamp forest, coastal wetland, pan and brackish, bog and fen and peatland, intermittent wetland or lake, 50 to 100% wetland, 25 to 50% wetland, wetland complex); the majority is among wetland areas only (-9999 for none). Extents `wet_pct_grp1`, `wet_pct_grp2` (group definitions are the provider's). Lehner and Döll 2004.
- **Fit:** yes. The word "seasonal" corresponds at most to class 9 "Intermittent wetland/lake"; floodplain (class 4) does not mean seasonal.
- **Suggested:** the source labels; "seasonal" only where the class is 9.

## Karst and permafrost: extensive, present, absent (S4.3)

- **In the data (P):** `kar_pc_sse`, `prm_pc_sse`, percent of the basin. Karst: World Map of Carbonate Rock Outcrops v3.0, Williams and Ford 2006, an **upper limit of exposed karst**; extensive karstified rock in subcrop is not mapped. Permafrost: the Permafrost Zonation Index, Gruber 2012, expressed as percent extent.
- **Schemes.** Permafrost zones by percent of area (continuous 90 to 100%, discontinuous 50 to 90, sporadic 10 to 50, isolated under 10), the IPA circum-arctic map (Brown et al. 1997, version 2 at NSIDC) (**S**). These are bands of a different dataset; the basin percentages are PZI-based, so applying the bands would stretch their definition. No karst class scheme applies to a percent of outcrop.
- **Suggested:** state the share, or "no mapped outcrop" for zero. Do not say karst is absent: the source maps outcrop only. No scheme to adopt.

## Drainage type (S3.5)

- **In the data:** `endo` (0 not endorheic, 1 part of an endorheic basin, 2 its sink), `outlet_type`, and `dist_sink` (distance from the polygon outlet along the river network to the next downstream sink, in km; HydroBASINS technical document, **P**). These are the source's own categories.
- **Suggested:** as is, with the wording that `dist_sink` is along the river from the basin's outlet.

## River size: 'a much larger river' (S3.3)

- **In the data (P):** `gaz.rivers` carries `ord_flow` (10 classes by long-term average discharge: class 1 at 100,000 m³/s or more, class 2 at 10,000 to 99,999, and so on by powers of ten down to class 10 under 0.001), `ord_clas` (classical order, main stem = 1) and `ord_stra` (Strahler). HydroRIVERS technical document v1.0 and Lehner and Grill 2013, *Hydrological Processes* 27(15): 2171 to 2186. The classes in our table match the definition (class 1 starts at 126,960 m³/s in the data; class 4 spans 100 to 999).
- **Fit:** these are reach-level classes, and the river network is complete in `gaz.rivers`. Class steps could stand in for the upstream-area thresholds used in WO-03 Q5; they are discharge classes, not catchment areas.
- **Suggested:** express "much larger" as a step of the source's own classes (for example two or more classes larger, a factor of 100 in discharge) and show the discharge. That is still a choice, but it is anchored in the source's classes and swept like any other cutoff.

## Comparatives (S2.3, S5.2, S6.4, S6.5)

No published scheme: "driest", "among", "resembles", "stands out" are relative statements. They are ranks, counts and percentiles; the cutoffs remain ours and are swept (WO-02 method).

## Not a class word, so no scheme

Cropland and pasture shares (Ramankutty et al. 2008) are percentages, and "a small share" is a cutoff. Population density has no class scheme in our sources; "sparse" is a cutoff.

## For Karl to confirm, if wanted

The sources I could not read in the primary: USDA Soil Survey Manual (Handbook 18) texture class boundaries or FAO 2006 Figure 4; UNEP aridity bands and the PET method they assume (Middleton and Thomas 1997); Meybeck et al. 2001 relief classes; Kapos et al. 2000 and Körner et al. 2011 if a mountain word is wanted; the IPA permafrost bands (Brown et al. 1997).

## Sources

- BasinATLAS Catalog v1.0, `documentation/BasinATLAS_Catalog_v10.pdf` (class fields, provenance, notes).
- HydroBASINS Technical Documentation v1.c, `data/HydroSheds/HydroBASINS_TechDoc_v1c.pdf` (`dist_sink`).
- HydroRIVERS Technical Documentation v1.0, https://data.hydrosheds.org/file/technical-documentation/HydroRIVERS_TechDoc_v10.pdf (`ORD_FLOW`, citation).
- FAO (2006), *Guidelines for soil description*, 4th ed., http://www.fao.org/4/a0541e/a0541e.pdf (Tables 4, 7, 25).
- Secondary: search results on the UNEP aridity classes, USDA texture classes, Köppen-Geiger (Beck et al. 2018, doi:10.1038/sdata.2018.214), IPA permafrost zones, mountain definitions.
