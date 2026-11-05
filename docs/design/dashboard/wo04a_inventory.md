# WO-04a inventory: what EDOPS already computes, against what the dummy modal needs

2026-11-05, rewritten after discussion with Karl. Read-only: the Sandbox cheat sheet (`sandbox_cheatsheet.md`), the variable catalog, saved examples, and two live GETs for Timbuktu (16.8167, -2.9833, L6). Unit ids refer to `modal_dummy_annotated.md`. Data inventory only; verdicts per unit come next.

## Frame (Karl's decisions, 2026-11-05)

- The modal endpoint (provisional name `/whgmodal`) reads a **persisted source of prose and data built for it, keyed by basin**. Nothing in that source is limited by what `/api/areas` returns or by speed.
- Whatever EDOPS delivers today, by any route, can feed it: signature rows, Sandbox panels, other tables, the WO-03 computations.
- A **thin live layer** handles what depends on the point and not the basin.
- WHG packs facts about the place into its call (name, and possibly more). Along for the ride, possibly useful to the prose. **What the call carries is to be worked out with WHG after the proposed endpoint and modal are shown** (a demo, then discussion with Ruth Mostern and Stephen Gadd); none of it is assumed here. Karl's note: things have changed at WHG since he left. Place pages that aggregate several attestations (as the old Place Portal did) have several point geometries, so WHG must pick one or send a centroid. A centroid can fall outside the place's own basin, in water, or in a different basin from any single attestation.

## 1. What the app already delivers for a basin

| Source | What it yields | Has statement text or fixed thresholds already? |
|---|---|---|
| **Signature rows, areas payload** (52 variables, A to E) | value, percentile score, status, coverage, weight at zero, caveat, per row | no (the Sandbox shows `coverage`, `weight_at_zero` and the caveat texts nowhere; cheat sheet 4.7) |
| **Public signature** (66 variables, A to E) | raw values: monthly rainfall and temperature, derived seasonality, point elevation, relief, `up_area`, 11-item profile summary | no |
| **Seasonality tab** | 12-month rainfall and temperature, six derived indices (precip concentration and peak month, temperature concentration and peak month, phase offset, temperature amplitude) | yes: a generated sentence, three fixed cutoff sets (cheat sheet 4.5, 9) |
| **Analysis tab** | upstream area, distance to ocean outlet, drainage badge (Endorheic, Coastal terminal, Exorheic interior); local and upstream precipitation, moisture and temperature as ratios; water provenance class (Endorheic, Coastal terminal, Exogenous water supply, Undetermined, Catchment-uniform, Local-dominant) | yes: a one-sentence note per class; cutoffs 500 km² (L6), 1.5x, 0.9 to 1.1 |
| **Context tab** | 7 variables (precipitation, temperature, temperature range, elevation, slope, aridity, runoff), each as an ordinal percentile against all basins and against basins within 250 to 2,500 km | yes: a rule-based paragraph (extreme at 10 or 15 points, gap of 25 points, "close to the global median" at 25 to 75) |
| **Similarity tab** | count and reach of basins matching on precipitation, temperature, climate or terrain (elevation and relief) | readout sentence; seven tolerances, user-set |
| **Atlas / climate classes** | per-basin class: rainfall modality (arid, even, one wet season, two wet seasons) and phase (warm- or cool-season rain, weak coupling); catalog "Climate class", e.g. "One wet season, cool-season rain" | blurb and declared conventions (arid under 100 mm; even under cv 0.2) |
| **Ring, topology** | neighbours, areas, shared border, bearings, interior points | glyph only; no statements |
| **Rivers in the basin** (`/api/basin-preview`) | river geometry (GeoJSON) near the point | none |
| **Raw `basin06`** (300 columns) | everything in BasinATLAS: per-class shares (land cover 44 columns, natural vegetation 30, wetland 22), cropland, pasture, forest, lake, glacier, urban, karst percentages; `sub_area`, `up_area` | none |
| **WO-03 computations** | ecoregion areas and shares in core and ring; flow relation of neighbours; nearest reach by size class (`gaz.rivers`) with Natural Earth names where matched; distance to the basin edge and nearest neighbour; no-basin and snap distances | none |
| **Ecoregion text** (`public.eco_wikitext`) | Wikipedia link and a paragraph summary for 821 of 847 ecoregions | LLM summary (marked as generated) |

The cheat sheet records a decision (Karl, 2026-10-27) that a rule-based prose layer may use the Sandbox's thresholds. Several are marked provisional in the code.

## 2. What the dummy needs, against those sources

Columns: **where it comes from now**, and **what stays live** (point-specific).

| Dummy need (units) | Source now | Note |
|---|---|---|
| Elevation at the point (S1.1b) | public signature `elev_point`; live OpenTopoData, Open-Meteo fallback | **live layer**; or WHG supplies it, or reword to the basin's range (`elev_min`, `elev_max`, both payloads) |
| Terrain word (S1.1c, S4.1a) | `slope_avg`, `relief_range_m`; Similarity Terrain lens uses elevation and relief | no class words anywhere yet |
| Ecoregion (S1.2a) | basin majority in both payloads (Timbuktu: Inner Niger Delta flooded savanna) | the dummy names the **point's** ecoregion (Sahelian Acacia savanna): point-in-polygon, **live layer**; the point's ecoregion differs from the core's largest-area ecoregion in about 6% of sample basins (WO-03 Q3 comparison; the BasinATLAS majority field was not compared) |
| Other ecoregions, shares (S1.3, S1.4) | WO-03 Q3 intersections | basin-keyed; the compass "direction" in S1.3c is not available |
| Ecoregion gist, link (S1.2b, S9.2) | `eco_wikitext` paragraph | a one-line gist is not stored |
| Rainfall, season (S2.1) | `precip_yr`; monthly arrays and peak month (public); Seasonality sentence | |
| Temperature, coldest and warmest month (S2.2) | `temp_yr`, `temp_min`, `temp_max` (monthly extremes); monthly array in public | month names derivable |
| Rank among the surrounding basins (S2.3, S5.2, S6.4, S6.5) | Context percentiles (global, within a radius) for 7 variables; ring ranks are WO-02/WO-03 designs, not built | **two comparison sets exist**: within a radius (built) and the ring (not built); the dummy says "N+1 basins around it" |
| Distance to river, size, name (S3.1, S3.3) | `gaz.rivers` query and Natural Earth names (WO-03 Q4, Q5) | distance from the point: **live layer**; the river's own size and name are basin-keyed |
| Upstream area and ratio to the local basin (S3.1c, S3.2) | `up_area`, `sub_area`; Analysis local-upstream ratios and provenance class | exists, with wording |
| Wetland, lake share (S3.4) | `wet_pct_grp1`, `wet_pct_grp2`, `wetland_class`; lake share only in `basin06` (`lka_pc_sse`) | |
| Where the water goes (S3.5) | `dist_sink`, `outlet_type`, drainage badge | `dist_sink` is the distance along the river network from the **basin's outlet** to the next downstream sink, ending at an inland sink if the basin is endorheic, else the ocean (HydroBASINS technical document, `data/HydroSheds`). It is not a distance to the coast, and not measured from the place. Analysis badge vs engine `outlet_type` vs `coast`: three meanings of coastal (WO-03 I-7) |
| Soil, lithology, karst, permafrost (S4) | `pct_sand/silt/clay`, `lith_class`, `karst`, `permafrost_extent` | majority lithology only; texture class not stored; two can be `outside_active_domain` |
| Land cover, cropland, pasture, population (S5) | `land_cover_name`, per-class shares in `basin06`, `cropland_extent`, `pasture_extent`, `pop_density` | |
| Ring size, upstream and downstream neighbours (S6.1, S6.2) | ring topology and WO-03 flow relation | S6.3 direction words: not available (WO-03 D2) |
| Distance to the nearest coast (S7.1a) | **no field** | only `coast` flag, distance to the river's outlet (`dist_sink`) and a planned hop count |
| Basin touches sea, nearest edge is coast (S7.2, S7.3) | `coast` flag; WO-03 Q6 edge kind | edge kind is point-specific: **live layer** |
| Measures without a value, point moved (S8.2, S8.3) | row `status` and `caveat`; WO-03 Q6 snap distance | snap is **live layer** |
| Data years (S8.1b) | catalog and glossary; payload names sources only | |

## 3. What the inventory shows

1. **A lot is already built, with wording.** Seasonality, Context and Analysis each have rules, thresholds and generated sentences in the Sandbox. For S2, S3.2, S3.5 and parts of S6 the question changes from "can we derive it" to "which existing rule, and do we reuse its cutoffs".
2. **Two comparison sets.** The Context tab compares against all basins within a radius; the dummy and the ring spec compare against the ring. Only the first is built.
3. **The live layer is small and specific:** point elevation (or WHG's), the point's ecoregion, distance from the point to the basin edge and nearest neighbour, nearest river from the point, the snap.
4. **Basin ecoregion or point ecoregion** is a choice; the payloads carry only the basin's.
5. **Distance to the nearest coast does not exist** as a field.
6. **Fields can be present and empty** (`outside_active_domain` for cropland, karst and permafrost at Timbuktu); a template slot reading one needs the zero case handled.
7. **Payload fields the Sandbox never displays** (per-row `coverage`, `weight_at_zero`, caveat texts, `shortfall`) are in the data; the cheat sheet says a prose generator could use them to explain missing values (S8.2).
8. **The catalog is older than the code** in places: it marks `coast_fraction` and `land cover class name` as absent from the point response, but both appear in the areas single-basin rows.
9. **Example sentences and data disagree at Timbuktu** (marked illustrative): cropland described as a small share, payload says 0% with pasture 28%; elevation 260 against 267 m; sink distance about 1,900 against 2,331 km.

## 4. Not yet checked

- What WHG's call carries (Karl to specify).
- Whether the monthly values can name the coldest and warmest months in the form S2.2 wants (likely).
- Which of the 54 WO-02 statement types already cover a dummy sentence.
- Units and scales for each percentage field, for the glossary.
