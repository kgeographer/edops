# EDOPS Exploration Log

Running record of findings from the data exploration phase. See `docs/edop/data_exploration.md` for task list, conventions, and guardrails.

Each entry: **Date · Task · Method · Finding · Implication**

---

<!-- entries added below as findings accumulate -->

---

## 2026-04-18 · Task 1 · Marginal distributions, L8 globally

**Method**: `notebooks/edop/explore/01_marginal_distributions.ipynb` · 190,675 L8 sub-basins · all implemented scalar, categorical, and compositional variables

---

### F1.1 — Sentinel values (-9999) in six scalar columns

**Finding**: Six columns in `basin08` use -9999 as a NoData sentinel rather than NULL: `slp_dg_sav` (6,390 rows, 3.4%), `slp_dg_uav` (6,390, 3.4%), `sgr_dk_sav` (7,803, 4.1%), `cly_pc_sav` / `slt_pc_sav` / `snd_pc_sav` (17,374 each, 9.1%). No other scalar columns are affected.

**Implication**: These columns must be treated with `NULLIF(col, -9999)` in any SQL query, or replaced with NaN after loading (as done in the notebook via `df_raw.replace(-9999, np.nan)`). Statistics computed before this fix are invalid for these six variables. All downstream scripts must apply the same treatment.

**Action**: 2026-04-28 — Recreated both `v_basin08_persist_rev1` and `v_basin06_persist_rev1` with `NULLIF(col, -9999)` on all six affected columns (`slope_avg`, `slope_upstream`, `stream_gradient`, `pct_clay`, `pct_silt`, `pct_sand`). Migration saved as `sql/edop/migrate_v_basin08_persist_rev1_nullif.sql`. Verified: 0 rows with -9999 sentinel post-fix in either view.

---

### F1.2 — Slope is valid and right-skewed; apparent flatness is real

**Finding**: After sentinel removal, `slope_avg` has mean 41.7°, median 20°, skew 2.09. The distribution has a large spike near zero (flat basins) and a long right tail (mountain terrain). This is consistent with the BasinATLAS source map: plains, lowlands, and interior basins dominate by basin count; steep terrain (Andes, Himalayas) is numerically a small minority.

**Implication**: Slope is informative but right-skewed. A log-transform will be needed before using it in PCA or clustering. The averaging of slope over the entire sub-basin polygon means even "mountainous" basins have moderate mean slopes — point-based intuitions about steepness do not transfer to this variable.

**Action**: deferred — analytical guidance for classification phase

---

### F1.3 — Soil texture (clay, silt, sand) are the most normally distributed scalars

**Finding**: After sentinel removal, `pct_clay` (mean 19.8%), `pct_silt` (mean 30.8%), `pct_sand` (mean 49.3%) show roughly bell-shaped distributions with low skew. They sum to ~100% per basin (constrained compositional variables). 9.1% of basins are null for all three — the same 17,374 rows with -9999 sentinels.

**Implication**: These are among the most analytically tractable variables in the dataset — usable in PCA/clustering without transformation. However, their constrained sum (clay + silt + sand ≈ 100) means only two are independent. Including all three in dimensionality reduction will introduce a spurious linear dependency; one should be dropped.

**Action**: 2026-04-28 — All three kept in the signature (each carries interpretive value for a researcher). `pct_sand` designated as the redundant member to drop when building classification feature matrices (clay and silt are more directly linked to soil cohesion and fertility). Codebook note added to `pct_sand` row. No API change.

---

### F1.4 — Temperature is bimodal

**Finding**: `temp_yr` and `temp_yr_upstream` show a clear bimodal distribution: a cold cluster centered around -5°C to 5°C (high-latitude and high-altitude basins) and a warm cluster centered around 20°C–25°C (tropical and subtropical basins). The trough between peaks falls roughly at 10°C–12°C.

**Implication**: Temperature does not follow a single bell curve globally — there are two environmental "worlds" by thermal regime. This bimodality will drive clustering results significantly. Any global typology will likely separate along this axis first. Variables that correlate with temperature (aridity, precip, biome) will show related structure.

**Action**: deferred — analytical guidance for classification phase

---

### F1.5 — Aridity index: stored as P/PET × 100, counterintuitive name

**Finding**: `ari_ix_sav` (api key: `aridity`) is the Global Aridity Index (Zomer et al.), stored as P/PET × 100. Global median = 68 (P/PET = 0.68, semi-arid). P95 = 212 (P/PET = 2.12, moderately humid). Values above 100 indicate humid conditions (P > PET). The tail extends to ~1000 (wet tropics). Despite its name, higher values = wetter — it is a humidity index.

**Implication**: Do not interpret raw values as ratios — divide by 100 for P/PET. The "cap at 100" mentioned in the BasinATLAS catalog refers to the source product's raw ratio cap (P/PET = 100), stored as 10,000 — essentially never reached. The semi-arid global median is consistent with the biome distribution (deserts dominant by basin count). Codebook updated to reflect correct units and scale.

**Action**: 2026-04-28 — Confirmed: `edops_codebook_v01.tsv` `aridity_index` notes column already contains the correct explanation (P/PET × 100, arid/humid boundary at 100, higher = wetter, global median ~68). No further change needed.

---

### F1.6 — Discharge variables are extreme right-skew; heavy-tailed

**Finding**: `discharge_yr`, `discharge_min`, `discharge_max` have skewness values of 41.6, 45.1, and 34.0 respectively. The median annual discharge is ~5.7 m³/s but the mean is 264.7 m³/s — pulled far right by large river systems. The Amazon and Congo alone drive the tail.

**Implication**: Raw discharge values are not useful in PCA or clustering without log-transformation. Even after log-transform, extreme outliers (large tropical rivers) may form their own cluster. Discharge is best interpreted as a presence/magnitude variable; the distinction between "small stream" and "large river" matters more than precise magnitude differences.

**Action**: deferred — analytical guidance for classification phase

---

### F1.7 — Karst, permafrost, and wetlands are globally sparse; treat as flags

**Finding**: `karst` has 81.9% zero values (degenerate by heuristic). `karst_upstream` has 73.3% zeros, `permafrost_extent` 77.1%, `wet_pct_grp1` 56.9%, `wet_pct_grp2` 71.1%. These are real phenomena but absent for the majority of basins.

**Implication**: These variables carry meaningful signal where they are non-zero, but including them as continuous variables in global PCA/clustering will not work — the near-zero mass dominates. Consider binary encoding (present/absent) or analyzing the non-zero subset separately. Karst and permafrost in particular are strong environmental signals for the minority of basins where they occur.

**Action**: deferred — analytical guidance for classification phase

---

### F1.8 — PNV shares are compositionally degenerate; majority class is sufficient

**Finding**: The PNV diversity chart shows ~95,000 basins with Shannon entropy ≈ 0 (single dominant class), a secondary cluster around 1.0 bit (two roughly equal classes), and a sparse long tail. The dominant class share chart shows the overwhelming majority of basins above the 95% threshold — one PNV class covers >95% of the basin area for most basins.

**Implication**: The full `pnv_shares` compositional object adds negligible information over `pnv_majority` for the vast majority of basins. For global analyses, use `pnv_majority` (categorical). The `pnv_shares` field is potentially useful only for identifying ecotone/transition basins, which form a small minority and could be flagged separately.

**Action**: deferred — analytical guidance for classification phase

---

### F1.9 — Categorical variables: all high entropy; deserts and xeric systems dominate by count

**Finding**: All nine categorical variables have normalized entropy 0.748–0.958 — none are degenerate in the categorical sense. However, dominant classes reveal a consistent pattern: Deserts & Xeric Shrublands is the top biome (36,023 basins); Xeric freshwaters and endorheic basins is the top freshwater habitat type (43,609); Unconsolidated Sediments is the top lithology (52,788). Climate stratum is the most evenly distributed (entropy 0.958, 125 classes). Wetland class has 49.2% null — nearly half of basins unclassified.

**Implication**: The dataset is globally representative but skews arid by basin count — consistent with the aridity and biome scalar findings. Historical scholarship concentrates in non-desert environments, so the basin-count distribution is not the same as the scholarship-relevant distribution (this will be examined in Task 6). Climate stratum is the most discriminating categorical variable. Wetland class null rate should be investigated — it likely reflects genuine absence but the boundary between "no wetland" and "unclassified" is worth clarifying.

**Action**: deferred — analytical guidance for classification phase

---

### F1.10 — Terrestrial ecoregion count skewed by large high-latitude basins

**Finding**: Of 784 terrestrial ecoregions, East Siberian taiga leads by basin count (5,654 basins). High-latitude boreal and tundra ecoregions dominate the top ranks not because they are the most common environment but because L8 sub-basins in Siberia and northern Canada are physically large polygons, generating more basin-count entries per unit area than tropical sub-basins.

**Implication**: Ecoregion basin counts reflect polygon size as much as environmental prevalence. When comparing ecoregion representation, area-weighted counts would be more meaningful than raw basin counts. This applies to any L8-level frequency analysis: large cold basins are over-counted relative to their ecological significance for human settlement.

**Action**: deferred — analytical guidance for classification phase

---

## 2026-04-19 · Task 2 · Missing-data and degenerate-value patterns, L8 vs. L6

**Method**: `notebooks/edop/explore/02_missing_data.ipynb` · L8: 190,675 basins · L6: 16,397 basins · 38 scalar variables · outputs: `02_missing_data_crosstab.csv`, `02_scale_scatter.png`, `02_distribution_shift.csv`, `02_scale_sensitivity.csv`

---

### F2.1 — Null rates universally decrease at L6; soil texture most affected

**Finding**: Every variable with non-zero null rates at L8 shows lower null rates at L6. The three soil texture variables (`pct_clay`, `pct_silt`, `pct_sand`) have the largest improvement: 9.11% null at L8 vs. 4.62% null at L6 (delta −4.49%). Slope and stream gradient also improve (L8: 3.3–4.1% null; L6: 1.8–2.5% null). No variable shows higher null rates at L6.

**Implication**: Null rates decreasing at coarser resolution is paradoxical but explicable: L6 polygons are larger and more likely to overlap the source dataset's coverage area. This is a coverage geometry effect, not improved data quality. The soil texture variables' content is essentially unchanged (std_shift ≤ 0.026) — only spatial coverage improves. Null-rate comparisons between levels cannot be interpreted as data quality degradation in either direction for these variables; they reflect source-dataset footprint vs. basin polygon size.

**Action**: deferred — analytical guidance for classification phase

---

### F2.2 — Zero rates reveal which variables are structurally sparse vs. scale-sensitive

**Finding**: Zero rates at L8 vs. L6 diverge in two directions. Most variables show *lower* zero rates at L6 (more non-zero basins at coarser scale), consistent with larger basin polygons capturing more of each phenomenon. Exceptions: `dist_sink` jumps from 13.69% zeros at L8 to 33.35% at L6 (+19.66%); `elev_min` rises from 6.03% to 11.29% (+5.26%). Wetland variables show the largest absolute decreases in zero rate: `wet_pct_grp1` drops −23.78%, `wet_pct_grp2` −19.19%, `karst` −12.29%, `karst_upstream` −12.09%, `reservoir_vol` −12.65%.

**Implication**: The `dist_sink` zero-rate increase at L6 is a topology artifact: L6 basins are larger and more likely to *be* terminal basins (with `dist_sink` = 0 by definition), inflating the zero count. This variable is sensitive to basin level in a structural way — the zero is not "no data" but "this is an outlet basin," and more basins qualify at L6. For spatially sparse phenomena (karst, wetlands, reservoirs), larger L6 polygons capture more non-zero signal — the variable becomes *more* informative at L6 for presence/absence purposes, though continuous values will differ.

**Action**: deferred — analytical guidance for classification phase

---

### F2.3 — River area is the most scale-sensitive variable; a fundamentally different measure at L6

**Finding**: `river_area` has a standardized mean shift of 4.49 between L8 and L6 — by far the largest of any variable. L8 mean: 192.7 ha, median: 71.8 ha. L6 mean: 2,241.3 ha, median: 914.2 ha. The variable increases roughly 10-fold in mean and 13-fold in median. `river_area_upstream` shifts at 0.234 (mean doubles from 8,172 ha to 25,574 ha).

**Implication**: `river_area` at L6 is not a scaled version of L8 `river_area` — it is a structurally different quantity. The polygon area of the river network within a large L6 basin is not comparable to the local sub-basin river area at L8. Do not use `river_area` for cross-level comparisons or treat L6 values as approximations of L8. For any analysis requiring this variable, pin to a single level. Flag in any methodology document.

**Action**: deferred — analytical guidance for classification phase

---

### F2.4 — Elevation extremes shift predictably with scale; a geometric consequence

**Finding**: `elev_min` shifts −0.208 std (L8 mean 445 m → L6 mean 308 m); `elev_max` shifts +0.239 std (L8 mean 1,058 m → L6 mean 1,341 m). Both shifts are in the expected direction: larger L6 basin polygons span greater elevation ranges, so their minimum is lower and their maximum is higher.

**Implication**: This is a geometric scale effect, not a data quality issue. L6 `elev_max` and `elev_min` are valid — they correctly describe the elevation range of a larger basin. But they are not interchangeable with L8 values for the same location. For a historical site query, L8 gives the local basin's elevation envelope; L6 gives a broader regional range. Both are useful, for different analytical purposes. Scale context must be stated when reporting either.

**Action**: deferred — analytical guidance for classification phase

---

### F2.5 — Discharge max is scale-sensitive; discharge annual and min are N-artifacts

**Finding**: `discharge_max` shifts +0.216 std (L8 mean 516 m³/s → L6 mean 1,572 m³/s). `discharge_yr` shifts +0.173 std and `discharge_min` +0.130 std, but both are classified as N-artifacts given modest zero-rate deltas and the confound of L6's smaller sample (16,397 vs. 190,675 basins). `river_area_upstream` shifts +0.234 std (scale-sensitive).

**Implication**: Maximum discharge genuinely increases at L6 because larger basins drain larger catchments — a structural hydrological reality. Annual and minimum discharge distributions shift less conclusively; part of the apparent shift may reflect which basins are present in L6's smaller sample. For discharge variables, L8 is preferred when the analysis concerns a specific sub-basin; L6 is appropriate when regional basin-scale hydrology is the frame.

**Action**: deferred — analytical guidance for classification phase

---

### F2.6 — 27 of 38 variables are stable across levels; climate and soil are level-agnostic

**Finding**: Climate variables (temperature, precipitation, aridity — local and upstream), soil texture, human footprint, GDP, cropland extent, karst, permafrost, slope, runoff, and groundwater depth all show |std_shift| < 0.1 with zero null delta. These 27 variables classify as stable across L8 and L6.

**Implication**: The signature's climatic and socioeconomic content is essentially level-invariant — the same environmental regime description applies whether queried at L8 or L6 resolution. For correspondence testing (D-PLACE, settlement patterns), these variables can be used at either level without cross-level comparability concerns. Scale-sensitivity is primarily a hydrological geometry problem, concentrated in river area and discharge max.

**Action**: deferred — analytical guidance for classification phase

---

### F2.7 — Methodological caveats on the N-artifact classification and std_shift threshold

**Finding** (review note): Two limits of the Task 2 classification scheme warrant flagging before any paper-writing use of these results. (1) The L6 sample is 16,397 basins vs. L8's 190,675 — an 11.6× ratio. Standardized mean shifts computed across these different-sized samples have different statistical power characteristics. Variables classified as "N-artifacts" (discharge_yr, discharge_min, dist_sink — F2.5) were flagged as *possibly* confounded by smaller-N rather than confirmed to be so. A permutation or bootstrap test would be needed to formally distinguish "apparent shift due to smaller sample" from "real shift that is harder to detect with fewer observations." (2) The std_shift threshold of 0.1 for the stable/scale-sensitive boundary is a reasonable heuristic but a heuristic. No variables in this dataset sit conspicuously near 0.1, so edge cases are not acute here, but any dichotomous classification of this kind has a fuzzy boundary that warrants visual inspection of borderline cases before treating the classification as definitive.

**Implication**: F2.3–F2.6 findings are reliable for characterization purposes. For any methodology paper, the N-artifact cases should either be formally tested or explicitly flagged as provisional classifications pending a more rigorous comparison. The stable/scale-sensitive dichotomy should be presented as a heuristic summary, not a sharp boundary.

**Action**: deferred — analytical guidance for classification phase

---

## 2026-04-19 · Task 3 · Local/upstream divergence distribution

**Method**: `notebooks/edop/explore/03_su_divergence.ipynb` · L8: 190,675 basins · 9 s/u pairs · divergence metric: log₂(u/s) for ratio pairs (aridity, precip, slope, river_area); u−s for difference pairs (temp, wetland, karst, cropland, human footprint) · outputs: `03_su_divergence_summary.csv`, `03_su_divergence_ecdf.png`

---

### F3.1 — Median divergence is zero for all nine pairs; s/u duality is a tail phenomenon

**Finding**: For every s/u variable pair, the global median divergence is exactly 0 — local and upstream values are identical at the 50th percentile. The interquartile range (p25–p75) is also at or near zero for six of nine pairs. Strong divergence is concentrated in the tails: p95+ for most variables, p99+ for the strongest cases. By basin count, most L8 sub-basins are headwaters or near-headwaters whose upstream footprint is approximately equal to their local footprint.

**Implication**: The s/u duality is not a generic feature of the dataset; it is a signal that fires in specific basin positions. A large divergence value is itself a meaningful finding — it identifies a basin that sits at an environmental boundary between local conditions and its upstream source region. For the majority of basins, reporting s and u separately adds no information. For the minority where they diverge, the divergence is the environmentally distinctive fact. This has direct implications for how the signature should be presented: the divergence magnitude (not just the u value) is the contribution.

**Action**: deferred — analytical guidance for classification phase

---

### F3.2 — Temperature divergence is directionally asymmetric: upstream is almost always colder

**Finding**: `temp_yr` divergence (u−s, °C) is strongly left-skewed. Only 8.2% of basins have upstream warmer than local; 91.8% have upstream colder or identical. The cold tail is heavy: p05 = −3.13°C, p01 = −7.2°C. The warm tail is short: p95 = +0.2°C, p99 = +1.3°C. This is the most directionally asymmetric of all nine pairs.

**Implication**: The asymmetry is physically consistent: tributaries and upstream sub-basins are overwhelmingly at higher elevation than lowland outlet basins. Where the signature shows a large negative temp divergence, the basin sits in a lowland receiving cold-source water from mountain headwaters — a hydrologically distinctive position. The Tigris/Euphrates and Nile are canonical cases of this pattern. A rare positive divergence (warm upstream) would signal a thermally unusual configuration worth investigating.

**Action**: deferred — analytical guidance for classification phase

---

### F3.3 — Aridity and precipitation divergence: moderate symmetric tails; 30% of basins receive upstream moisture

**Finding**: `aridity` and `precip_yr` have nearly identical divergence distributions (high correlation, expected from shared underlying hydrology). Both show moderate, roughly symmetric tails: aridity p95 = +0.555 log₂ (upstream 1.47× wetter), p05 = −0.15. Precipitation p95 = +0.393 log₂, p05 = −0.159. About 30–31% of basins have upstream wetter than local; 69–70% have local wetter or identical.

**Implication**: Positive aridity/precipitation divergence (wetter upstream) is the characteristic signature of exotic river systems — rivers that originate in humid mountains and flow into arid lowlands. About one-third of all basins globally have some degree of this pattern. The claim that "Ur is a distinctive exotic-river case" requires placing Ur in this distribution — whether it falls at p90, p95, or p99 determines how distinctive the claim is. That analysis requires the place-percentile output from Cells 8–10 (not yet run).

**Action**: deferred — analytical guidance for classification phase

---

### F3.4 — Slope divergence: widest environmental tails; upstream-steeper pattern common

**Finding**: `slope` has the widest ratio-pair tails: p95 = +2.32 log₂ (upstream 5× steeper than local), p99 = +4.59 (24× steeper). The negative tail is also significant: p01 = −1.81 (local 3.5× steeper than upstream). 31% of basins have upstream steeper than local — the same proportion as aridity and precip, suggesting a structural correlation: steep upstream terrain drives both cold temperatures and concentrated precipitation.

**Implication**: Large positive slope divergence identifies piedmont and alluvial-fan basins — locally flat terrain at the base of steep upstream catchments. This is an important class for historical settlement (Ur, Nippur, the Indus cities all sit on alluvial plains fed by mountain catchments). The combination of steep-upstream + cold-upstream + wet-upstream is the signature of the exotic river basin type; Task 4's correlation matrix should confirm these variables co-vary.

**Action**: deferred — analytical guidance for classification phase

---

### F3.5 — Human footprint and land use: local concentration is the dominant pattern

**Finding**: `human_fp_09`, `cropland`, `wet_pct_g1`, and `karst` all show left-skewed divergence distributions: local values exceed upstream values for 80–90% of basins. `human_fp_09` has the largest absolute divergence values of the difference pairs: p01 = −113 index points (local footprint 113 points above upstream), p95 = +23. Cropland: p01 = −33%, p95 = +6%. Wetlands: p01 = −82%, p95 = +3%.

**Implication**: Human activity, agriculture, and wetland occurrence are predominantly local phenomena — they occur in lowland, accessible basin positions and are absent or reduced in upstream catchments. The left skew means that for most historically significant sites, local human footprint exceeds upstream footprint: the settlement IS the concentration. Cases where upstream footprint exceeds local (13–20% of basins) could identify downstream agricultural peripheries or basins where agricultural land is disproportionately concentrated in headwater valleys — a less common but analytically interesting configuration.

**Action**: deferred — analytical guidance for classification phase

---

### F3.6 — River area divergence: a network-geometry artifact, not an environmental variable

**Finding**: `river_area` has extreme ratio tails: p95 = +6.68 log₂ (upstream network 102× larger than local basin river area), p99 = +9.18 (575× larger). The distribution is driven by basin position in the drainage network: headwater basins have u≈s (log₂≈0), while basins near major river mouths have upstream network areas orders of magnitude larger. 44.5% of basins show upstream-greater — higher than any other pair.

**Implication**: River area divergence measures network position, not environmental character. Including it in a divergence ranking alongside climate or terrain variables is misleading. For the signature, `river_area` (local) and `river_area_upstream` are better treated as independent descriptors of local channel size and network magnitude respectively, not as a local/upstream pair in the divergence sense. Flag for any future dimensionality-reduction work: these two variables are not measuring the same phenomenon at different scales.

**Action**: deferred — analytical guidance for classification phase

---

### F3.7 — Timbuktu: extreme exotic moisture at p99.9, Inner Niger Delta wetland position

**Finding**: Timbuktu (hybas_id 1080561810, up_area 379,818 km²). Dominant divergence signals, ranked by deviation from median: `precip_yr` log₂(u/s) = 2.369 (upstream 5.1× wetter, **p99.9**); `aridity` = 2.385 (upstream 5.2× more humid, **p99.8**); `slope` = 3.585 (upstream 12× steeper, p97.9); `human_fp_09` = +31 (local footprint higher, p96.7); `wet_pct_g1` = −56% (local 56% more wetland than upstream, **p2.2**). Temperature divergence is modest: −1.6°C upstream colder (p11.4).

**Implication**: Timbuktu is in the top 0.1% of all basins globally for upstream moisture divergence — this is not a moderate exotic-river signal but an extreme one. The Niger's headwaters in the Fouta Djallon highlands (~2,000 mm/yr precipitation) feed into the hyper-arid Saharan basin (~200 mm/yr locally). The simultaneously low wetland-divergence percentile (p2.2) is not paradoxical — it confirms Timbuktu's position at the edge of the Inner Niger Delta, where Niger water creates one of Africa's largest wetland complexes locally, producing a wetland concentration that exceeds the upstream average. The signature is: extreme upstream moisture delivery + local wetland terminus + local human concentration. Temperature divergence is slight because the Niger headwaters are not high-altitude cold sources — the exotic character is purely hydrological, not thermal.

**Action**: deferred — analytical guidance for classification phase

---

### F3.8 — Ur: dual asymmetry — upstream agricultural core, local marsh terminus

**Finding**: Ur (hybas_id 2080818060, up_area 456,772 km²). `aridity` log₂(u/s) = 2.070 (upstream 4.2× more humid, **p99.6**); `precip_yr` = 1.457 (upstream 2.75× wetter, p99.5); `temp_yr` = −6.0°C (upstream 6°C colder, p1.6); `wet_pct_g1` = −46% (local 46% more wetland, p3.0); `karst` = +16% (upstream more karst, p95.6). The surprises: `human_fp_09` = −64 index points (upstream footprint **64 points higher** than local, p2.5); `cropland` = −45% (upstream **45% more cropland**, p0.4).

**Implication**: Ur occupies a structurally distinctive position in the Tigris–Euphrates drainage. Two divergence signals point in opposite directions simultaneously. The moisture/temperature signals (aridity p99.6, temp p1.6) confirm the classic exotic-river pattern: cold, wet Zagros and Taurus headwaters draining into a hyper-arid lowland. The human and cropland signals reverse: Ur's local basin is the southern marshland terminus (Mesopotamian marshes), while the upstream basin encompasses the Tigris–Euphrates agricultural heartland — Baghdad, the Fertile Crescent irrigation zone, the full Mesopotamian agricultural core. At the time of Ur's florescence, the upstream was already intensively farmed; Ur itself sat at the wetland edge. The karst signal (upstream more karst, p95.6) reflects Zagros/Taurus limestone terrain. The combination — upstream wetter + upstream colder + upstream more agricultural + local more wetland — is a compact environmental description of what Ur was: a marsh-edge settlement at the foot of a massive agricultural and hydraulic system.

**Action**: deferred — analytical guidance for classification phase

---

### F3.9 — Kaifeng: extreme topographic discontinuity, inverted moisture gradient

**Finding**: Kaifeng (hybas_id 4080602410, up_area 734,701 km²). `slope` log₂(u/s) = 6.492 (upstream **91× steeper**, **p99.9**); `temp_yr` = −8.8°C (upstream 8.8°C colder, p0.6); `human_fp_09` = −85 (upstream footprint 85 points higher, p1.6); `cropland` = −48% (upstream 48% more cropland, p0.3). Crucially: `precip_yr` log₂(u/s) = −0.393 (local **1.3× wetter** than upstream, p1.8); `aridity` = +0.084 (effectively zero divergence, p79.0).

**Implication**: Kaifeng has a fundamentally different divergence profile from Timbuktu and Ur. The dominant signal is topographic, not hydrological: the Yellow River descends from the Tibetan Plateau through the Loess Plateau onto the North China Plain, producing the most extreme slope divergence of the three sites (p99.9, upstream 91× steeper). The cold upstream (-8.8°C, p0.6) follows from altitude. But the moisture gradient runs in the opposite direction from the other two: Kaifeng is wetter locally than upstream, because the East Asian monsoon delivers increasing precipitation eastward toward the coast while the Yellow River headwaters lie in the rain-shadow interior. The cropland and human-footprint inversions (upstream more agricultural, p0.3 and p1.6) reflect the Loess Plateau and Wei River valley agricultural landscape, which has been intensively farmed for millennia — the upstream here is not wilderness but the older, denser agricultural core from which the Yellow River civilizations descended. Kaifeng's position on the North China Plain gives it local agricultural productivity but the plain was settled later and less intensively than the upriver valleys. The signature is: extreme topographic descent, cold source, wetter locally (monsoon), and agricultural antiquity concentrated upstream.

**Action**: deferred — analytical guidance for classification phase

---

### F3.10 — Comparative: three sites, three divergence types; no single exotic-river template

**Finding**: Timbuktu, Ur, and Kaifeng each fall in the extreme tail (p95+) for at least one divergence variable, confirming that historically significant exotic-river settlements are not in the modal basin class. But their divergence profiles are structurally different: Timbuktu's signal is pure moisture delivery (upstream precipitation p99.9, aridity p99.8) with minimal temperature divergence; Ur's signal is moisture plus thermal plus a social reversal (upstream agricultural core); Kaifeng's dominant signal is topographic (slope p99.9) with inverted moisture gradient (locally wetter). No single variable captures all three. The s/u divergence is multidimensional, and different river systems produce distinctive divergence signatures.

**Implication**: The s/u duality's contribution is not reducible to a single "exotic river index." Different environmental mechanisms produce different divergence fingerprints. A composite divergence profile — which variables diverge, in which direction, and by how much — is more informative than any single divergence score. This has direct implications for how the signature is used in correspondence testing and in the narrative layer: the divergence profile should be described per-variable, not collapsed. Practically, this also means the three example sites should not be treated as equivalent instances of the same type — they should be used to illustrate different divergence regimes.

**Action**: deferred — analytical guidance for classification phase

---

## 2026-04-19 · Task 4 · Correlation structure within and across bands

**Method**: `notebooks/edop/explore/04_correlation_matrix.ipynb` · L8: 190,675 basins · 37 scalar variables · Spearman rank correlation (pairwise complete observations) · outputs: `04_correlation_matrix.csv`, `04_correlation_heatmap.png`, `04_high_correlation_pairs.csv`

---

### F4.1 — s/u pair redundancy: local and upstream climate variables are globally near-identical

**Finding**: The three climate s/u pairs are the most correlated in the entire matrix: `aridity` / `aridity_upstream` r = 0.984; `precip_yr` / `precip_yr_upstream` r = 0.987; `temp_yr` / `temp_yr_upstream` r = 0.989. Human variable pairs follow: `human_footprint_09` / `human_footprint_09_upstream` r = 0.951; `cropland_extent` / `cropland_extent_upstream` r = 0.950. These are not independent variables — globally, local and upstream values are nearly interchangeable for these variables.

**Implication**: The global near-identity of s/u pairs is consistent with F3.1 (median divergence = 0 for all pairs). For the majority of basins, including both local and upstream versions of the same climate or land-use variable in PCA adds a near-duplicate dimension without new information. In dimensionality reduction, one member of each s/u pair should be dropped — retain whichever is more theoretically motivated (upstream for process-aware characterization, local for site description). The divergence value itself (u−s or log₂(u/s)) may be more useful than either raw value for capturing the signature's distinctive content.

**Action**: deferred — analytical guidance for classification phase

---

### F4.2 — Temperature internal redundancy; four variables behave as one

**Finding**: `temp_yr`, `temp_min`, `temp_max`, and `temp_yr_upstream` form the tightest cluster in the matrix. All six pairwise correlations exceed r = 0.77; four of six exceed r = 0.88. The highest: `temp_yr` / `temp_yr_upstream` = 0.989, `temp_yr` / `temp_min` = 0.963, `temp_min` / `temp_yr_upstream` = 0.954. The exception: `temp_min` / `temp_max` = 0.771 — seasonal range is partially independent of mean. Visible on the heatmap as the dark red 4×4 block in the Band C region.

**Implication**: For PCA or any dimensionality reduction, including all four temperature variables contributes three near-redundant dimensions. A single temperature variable (most likely `temp_yr`) represents the cluster; `temp_max` is the most independent of the four (lowest average r with others) and could be retained as a second temperature dimension if capturing thermal range is analytically important. `temp_yr_upstream` adds negligible information over `temp_yr` globally (r = 0.989) and can be dropped from dimensionality reduction — its signal is already in `temp_yr`.

**Action**: deferred — analytical guidance for classification phase

---

### F4.3 — Discharge cluster redundancy; discharge_max proxies network size

**Finding**: `discharge_yr`, `discharge_min`, and `discharge_max` are strongly mutually correlated: yr/max r = 0.967; yr/min r = 0.933; max/min r = 0.855. Additionally, `discharge_max` / `river_area_upstream` r = 0.937 — the peak discharge of a basin is almost perfectly predicted by its total upstream network area. `discharge_yr` / `river_area_upstream` r = 0.886. These hydrological size variables form a single redundant cluster.

**Implication**: Only one discharge variable is needed in dimensionality reduction — `discharge_yr` is the natural choice (most commonly reported, best-studied). `river_area_upstream` is nearly redundant with `discharge_max` and represents the same underlying quantity (drainage network magnitude). The three discharge variables + `river_area_upstream` can be treated as four measures of one latent variable: basin hydrological size. Retain one; note the others as alternative representations.

**Action**: deferred — analytical guidance for classification phase

---

### F4.4 — Human variables split into two sub-clusters: intensity and development

**Finding**: Band D contains two near-redundant sub-clusters. Sub-cluster 1 (human intensity): `pop_density`, `human_footprint_09`, `human_footprint_09_upstream`, `cropland_extent`, `cropland_extent_upstream` — all pairwise r = 0.72–0.95. Sub-cluster 2 (economic development): `gdp_avg` / `human_dev_idx` r = 0.910. The two sub-clusters are weakly to negatively correlated with each other: `gdp_avg` / `human_footprint_09` r = −0.307; `gdp_avg` / `pop_density` r = −0.452. High GDP/HDI areas are not the same as densely populated or heavily farmed areas — wealthy but sparsely settled economies (Northern Europe, North America) drive the negative cross-cluster correlation.

**Implication**: The two human sub-clusters measure different things and should not be collapsed. Sub-cluster 1 (intensity) captures anthropogenic landscape modification — agriculture, settlement, infrastructure. Sub-cluster 2 (development) captures economic modernity. For PCA, retain one variable from each sub-cluster: `human_footprint_09` from sub-cluster 1 (composite index), `gdp_avg` or `human_dev_idx` from sub-cluster 2. The negative cross-cluster correlation is itself a finding: intensive land use and economic development are not the same axis, and confusing them in a rubric would produce misleading environmental characterizations.

**Action**: deferred — analytical guidance for classification phase

---

### F4.5 — Cross-band: soil texture co-varies with temperature; a weathering signal

**Finding**: The strongest cross-band correlations in the matrix involve soil texture (Band B) and temperature (Band C). `pct_clay` / `temp_min` r = 0.754; `pct_clay` / `temp_yr` r = 0.710; `pct_clay` / `temp_yr_upstream` r = 0.703. Inverse for silt: `pct_silt` / `temp_min` r = −0.701; `pct_silt` / `temp_yr` r = −0.658. Sand is less strongly correlated with temperature. Also: `pct_clay` / `permafrost_extent` r = −0.582 (warm soils have more clay; permafrost regions less). Visible on the heatmap as a red rectangle crossing the Band B soil-texture rows into the Band C temperature block.

**Implication**: This is a pedogenic signal, not a methodological artifact. Chemical weathering (which produces clay minerals) is temperature-dependent — hot, humid tropical environments produce deep, clay-rich soils; cold, high-latitude or high-altitude environments are dominated by physical weathering (which produces silt and sand from parent rock). The B×C correlation encodes a fundamental climate-soil feedback that operates over geological timescales. Practically: `pct_clay` is not an independent variable for PCA relative to temperature. Including both adds limited new information in warm-climate basins, though they diverge in cold or arid regions where weathering regimes differ.

**Action**: deferred — analytical guidance for classification phase

---

### F4.6 — Cross-band: runoff and aridity are climate-determined; Band B partially redundant with Band C

**Finding**: `runoff` (Band B) / `aridity` (Band C) r = 0.782; `runoff` / `aridity_upstream` r = 0.775; `runoff` / `precip_yr` r = 0.774; `runoff` / `precip_yr_upstream` r = 0.760. Runoff is more strongly correlated with the climate variables than with most of its Band B neighbors. `discharge_yr` / `precip_yr` r = 0.544; `discharge_yr` / `aridity` r = 0.496.

**Implication**: Runoff is largely predictable from precipitation and aridity — it measures what is left after evapotranspiration, which is climate-driven. For dimensionality reduction, runoff does not add substantial new information beyond what aridity and precipitation already encode, except at the margin (where local geology, soil permeability, and land cover modify the climate signal). It may be worth retaining as a Band B representative if the goal is to have hydrology represented independently of climate, but its inclusion should be flagged as partially redundant.

**Action**: deferred — analytical guidance for classification phase

---

### F4.7 — Permafrost as cross-band bridge: cold = uninhabited = high silt

**Finding**: `permafrost_extent` correlates negatively with the entire Band D human cluster: `pop_density` r = −0.512; `human_footprint_09` r = −0.534; `human_footprint_09_upstream` r = −0.557; `cropland_extent` r = −0.437; `cropland_extent_upstream` r = −0.452. It also correlates negatively with `pct_clay` (r = −0.582, Band B) and strongly negatively with all temperature variables (r = −0.688 to −0.720, Band C). In the heatmap: permafrost appears as a blue stripe running across both the Band C temperature block and the Band D human block.

**Implication**: Permafrost is a cross-band integrator: it encodes cold climate (C), physically-weathered soils (B), and absence of human settlement (D) in a single variable. Its correlations are not coincidences but reflect a coherent environmental syndrome — the high-latitude/high-altitude biome where climate, pedology, and human geography all co-vary. This makes permafrost a potentially powerful typological discriminator for clustering (Task 5), even though it is zero for 77% of basins (F1.7). When it fires, it organizes structure across multiple bands simultaneously.

**Action**: deferred — analytical guidance for classification phase

---

### F4.8 — Band E (dist_sink) is structurally independent

**Finding**: `dist_sink` (flow distance to marine outlet) has no correlation above |r| = 0.41 with any other variable. Its strongest correlations: `elev_min` r = 0.408 (higher minimum elevation → farther from coast, expected); `discharge_yr` r = 0.270; `discharge_min` r = 0.280. All others are r < 0.25. The dist_sink row/column appears as a largely neutral (pale) stripe in the heatmap.

**Implication**: Coastality is structurally independent from climate, terrain, hydrology, and human variables — it adds a genuinely orthogonal dimension to the signature. A basin 5,000 km from the ocean is not systematically different in temperature, rainfall, or human footprint from a coastal basin — the position in the drainage network is a separate axis. This validates the prospectus claim that coastality is a "first-class signature component" — it is not captured by any other variable in the dataset.

**Action**: deferred — analytical guidance for classification phase

---

### F4.9 — PCA exclusion candidates: variables redundant at |r| > 0.9

**Finding**: Eleven variable pairs exceed |r| = 0.9 (full list in `04_high_correlation_pairs.csv`). Grouped by redundancy cluster, the recommended exclusions for any PCA or clustering are: (1) from the climate s/u pairs, drop `temp_yr_upstream`, `precip_yr_upstream`, `aridity_upstream` — retain local values; (2) from the discharge cluster, drop `discharge_min` and `discharge_max` — retain `discharge_yr`; (3) drop `river_area_upstream` (r = 0.937 with `discharge_max`); (4) from human footprint, drop `human_footprint_09_upstream` — retain local; (5) drop `cropland_extent_upstream` — retain local; (6) drop `human_dev_idx` — retain `gdp_avg`. These six drops reduce the 37-variable set to 31 without losing substantial information.

**Implication**: The 31-variable reduced set retains one representative per redundant cluster and eliminates the most egregiously collinear variables. A further reduction to ~20 variables would require judgment calls about which cross-band redundancies to address (soil texture vs. temperature, runoff vs. aridity). That reduction decision belongs in Task 5 design, not Task 4 characterization — document it there with explicit rationale.

**Action**: deferred — analytical guidance for classification phase

---

## 2026-04-19 · Task 5 · Geographic pre-clustering

**Method**: `notebooks/edop/explore/05_preclustering.ipynb` · L8: 190,675 basins · 20 Band A+B+C variables (post-F4.9 reductions) · log1p + StandardScaler normalization · k-means k=20 (n_init=10) + sklearn HDBSCAN (min_cluster_size=1000, min_samples=50) · outputs: `05_kmeans_global_map.png`, `05_hdbscan_global_map.png`, `05_kmeans_cluster_summary.csv`, `05_cluster_comparison.png`, `05_cluster_assignments.csv`

---

### F5.1 — k-means global map: clusters recover recognizable environmental zones without geographic input

**Finding**: The k-means global map shows strong geographic coherence — contiguous regional blocks aligning with known environmental zones — despite the algorithm receiving no geographic coordinates, only environmental variables. Major correspondences: cold permafrost clusters concentrate in Siberia, northern Canada, and high-altitude interiors; hyperarid clusters (km=2, precip=37mm/yr) cover Sahara, Arabian Peninsula, central Australia, and Atacama; tropical wet clusters (km=0, precip=2,049mm/yr) cover the equatorial belt; tropical wetland clusters (km=5) appear in Amazon and Congo floodplains; mountain-specific clusters appear along the Andes, Himalayas, Rockies, and Ethiopian Highlands. Similar-colored basins appear on different continents when their environmental signatures match.

**Implication**: Geographic coherence without geographic input is a validation of the signature variables — they carry sufficient environmental information to reconstruct approximate biome geography. This is necessary but not sufficient validation: a bad variable set could produce geographically coherent but environmentally meaningless clusters. The coherence confirms the variables are measuring real structure, but the cluster boundaries are imposed cuts on a continuous surface (see F5.2) and should not be treated as natural types except at the extremes.

**Action**: deferred — analytical guidance for classification phase

---

### F5.2 — HDBSCAN finds one natural cluster: Greenland; global basin distribution is continuous

**Finding**: HDBSCAN (min_cluster_size=1000) produced 2 clusters and 37.7% noise (71,810 unclustered basins). Cluster 1 (4,856 basins) isolates Greenland and similar glaciated/periglacial Arctic environments. Cluster 0 (114,009 basins) is a single massive catch-all encompassing most of the world's landmass. The remaining 37.7% of basins are structurally ambiguous in HDBSCAN's density framework. Reducing min_cluster_size to 500 or adjusting min_samples would increase cluster count but at the cost of more noise — the fundamental result is robust: the global basin population does not contain sharply bounded natural types.

**Implication**: With one exception (glaciated Arctic environments), global basin character is a continuum. There are no sharp density peaks in environmental feature space corresponding to distinct basin types — the variation grades from one environment to another without gaps. This has two implications: (1) k-means clusters are working typology, not natural kinds — the cuts are analytically useful but arbitrary; (2) HDBSCAN is not the appropriate method for global basin typology at this dimensionality. The dimensionality issue is secondary: even with PCA reduction, the underlying continuity of the global basin distribution would likely produce a similar result. The commit is k-means for downstream use; HDBSCAN findings should be reported in any methods paper as evidence for the continuity claim.

**Action**: deferred — analytical guidance for classification phase

---

### F5.3 — Three karst clusters span the temperature gradient; karst is a cross-cutting typological axis

**Finding**: Three of the 20 k-means clusters are karst-dominated, distributed across the full temperature range: km=4 (cold, −8°C, karst=76%, permafrost=69% — cold karst highlands, likely Tibet/Qinghai margins); km=18 (warm, 15°C, karst=66%, humid, precip=1,073mm — warm humid karst, likely southern China/Southeast Asia); km=7 (hot, 22°C, karst=81%, arid — hot dry karst, Middle East/North Africa). The global mean karst coverage is ~10%; these clusters run 7–8× above that.

**Implication**: Karst geology creates a distinctive environmental signature that overrides climate in the clustering — even though karst% is one variable among 20, it pulls basins into separate clusters when it is extreme enough. This confirms F1.7 (karst as a flag variable rather than continuous) and suggests that for future typology work, karst presence should be treated as a stratifying variable, not just another input dimension. The three karst clusters also represent three genuinely different environmental conditions despite sharing the same geology — karst is a substrate that interacts differently with cold/wet/dry regimes, and any rubric that treats karst as a single type would miss this.

**Action**: deferred — analytical guidance for classification phase

---

### F5.4 — Special clusters: large rivers, regulated rivers, and flat tropical lowlands

**Finding**: Three clusters are defined by extreme single-variable values rather than a coherent environmental syndrome. **km=17** (n=5,416): mean annual discharge 5,693 m³/s (11× global mean), reservoir volume 33,432 km³ — the large river systems cluster dominated by Amazon, Congo, Ganges, and Mississippi basin sub-basins. **km=8** (n=8,524): discharge 581 m³/s, reservoir volume 6,592 km³ — heavily regulated rivers with major dam infrastructure. **km=14** (n=7,276): slope 1.21° (flattest cluster), elevation range 34m — tropical lowland deltas and coastal plains, structurally flat.

**Implication**: The large-river and regulated-river clusters are partially artifacts of the basin-count representation: large river systems are split into many L8 sub-basins, each carrying the upstream discharge signal, which concentrates them in a cluster that is really a "position in large drainage network" type rather than a local environmental type. For any correspondence testing that uses cluster membership to situate historical sites, these three clusters require special interpretive care — a site in km=17 is being classified by the regional river system it sits within, not its local environment. This is not wrong, but it should be stated.

**Action**: deferred — analytical guidance for classification phase

---

### F5.5 — Comparison with existing workbench clustering: ARI=0.179, variable-set difference is the driver

**Finding**: Adjusted Rand Index between the new k-means (20 variables, Bands A+B+C) and the existing workbench `cluster_id` (bands A–D, includes human variables) = 0.179. This is substantially above chance (0.0) but far from perfect agreement (1.0). The contingency heatmap shows: a small number of extreme-environment old clusters map cleanly to specific new clusters (dark blue cells — the permafrost and hyperarid cases are stable); most mid-range old clusters spread diffusely across multiple new clusters.

**Implication**: The two clusterings agree on the environmental extremes (where the signal is strong enough to dominate regardless of variable set) but diverge significantly in the middle of the distribution, where Band D human variables were reshaping cluster boundaries in the old result. This answers the question raised in the exploration plan: the difference between the two clusterings is primarily driven by variable set, not by random initialization or different underlying structure. Including human variables (Band D) in the old clustering pulled mid-range basins into groupings reflecting agricultural and settlement patterns rather than purely physical environment. For the use scenarios driving this project — situating historical settlements within their physical environmental context, and testing correspondence between environmental signatures and cultural patterns — Band D inclusion is structurally inappropriate: it makes human presence a feature of the "environmental type," which then gets used to interpret where humans are. That is circular. Band D variables are outcomes to be explained by environmental context, not inputs to it. The A+B+C-only clustering is the correct instrument for correspondence testing; Band D belongs in the analysis only as a dependent variable or secondary descriptor, not as a typology input.

**Action**: deferred — analytical guidance for classification phase

---

### F5.6 — Method resolution: commit to k-means; normalization decision documented

**Finding**: k-means (k=20) is the working typology for all downstream exploration and correspondence work. HDBSCAN is rejected for global basin typology at this resolution on the grounds that: (1) the global basin distribution is fundamentally continuous (F5.2), making density-based cluster detection largely futile; (2) 37.7% noise is not analytically useful for a typology that needs to situate every site; (3) the two clusters HDBSCAN found (Greenland + rest-of-world) provide no discrimination within the historically relevant portion of the basin distribution. Normalization: log1p applied to all non-negative right-skewed variables (terrain, hydrology, aridity, precipitation, sparse indicators); StandardScaler applied throughout; temperature (can be negative) receives StandardScaler only. Median imputation for the ~9% null rate in soil texture variables and ~4% in slope/gradient. k=20 retained to enable comparison with existing workbench result; this choice is arbitrary and should be revisited before any formal typology is published.

**Action**: deferred — analytical guidance for classification phase

---

### F5.7 — L6 clusters are geographically dispersed; L8 clusters are spatially coherent — a structural difference with implications for CDOP correspondence work

**Finding**: k-means clustering on L6 basins (Task 5b) produces clusters with no geographic coherence — similar signatures appear scattered across all continents. The same clustering on L8 basins produces clusters with strong spatial unity: similar signatures tend to co-locate regionally. This difference holds even though geographic coordinates are not used in either clustering. At L8, the signature is locally specific enough that similar drainage, terrain, climate and hydrology co-occur in the same regions, produced by the same regional geology, orography and atmospheric circulation. At L6, large-basin averaging smooths out that local specificity: a big basin in temperate western Europe and one in temperate northeastern China can produce nearly identical L6 averages, because values are means over areas large enough that regional character dissolves into broad climate-zone statistics.

**Implication**: L8 is the right scale for asking "what is the local environmental character of this specific place" — it has geographic discriminating power. L6 is the right scale for asking "what kinds of environments like this exist globally, and what human adaptations arise in them" — its geographic dispersion is what makes environment-culture correspondence testable rather than trivially geographic. For CDOP correspondence work (do similar environments produce similar cultural adaptations, wherever those environments occur?), L6's geographic non-clustering is a feature, not a defect: it decouples environmental similarity from regional proximity, allowing genuine environmental causation to be distinguished from cultural diffusion or shared history. The two levels are complementary instruments for different research questions, not one better than the other.

**Action**: deferred — analytical guidance for classification phase

---

## 2026-04-19 · Task 6 · Geographic coverage and sampling-bias characterization

**Method**: `notebooks/edop/explore/06_coverage_sampling_bias.ipynb` · D-PLACE (6,408 societies with coordinates) and WH Cities (258) assigned to k-means clusters via PostGIS nearest-basin lookup (`basin08.geog` column + GIST index). Distribution comparison and log₂ representation ratios computed against global basin baseline (190,675 L8 basins). Outputs: `06_coverage_distribution.csv`, `06_dplace_cluster_assignments.csv`, `06_representation_ratios.png`, `06_coverage_map.png`.

---

### F6.1 — D-PLACE over-samples tropical wet mountains (3.65×); all cold and arid types severely under-sampled

**Finding**: D-PLACE has a single strongly over-represented cluster — "Tropical wet mountains" (5.9% of global basins, 21.6% of D-PLACE societies; ratio 3.65×). Ten clusters are under-represented at ratio < 0.5, including Arctic highland (0.01×), hyperarid desert (0.11×), cold boreal (0.16×), cold karst highland (0.23×). Cool temperate lowlands (7% of global basins, the second-largest cluster) is at 0.40×.

**Implication**: D-PLACE ethnographic coverage reflects fieldwork access patterns and population density, not environmental prevalence. Mesoamerican, Andean, and SE Asian societies dominate. Cold and hyperarid environments are structurally absent from correspondence testing using D-PLACE alone.

**Action**: deferred — analytical guidance for classification phase

---

### F6.2 — WH Cities is dominated by regulated river corridors (5.55×); a civilization-geography bias

**Finding**: WH Cities has three over-represented clusters: "Regulated rivers" (4.47% global → 24.81% WHC; ratio 5.55×), "Warm humid karst" (3.27×), and "Tropical wet mountains" (2.68×). Six cluster types have zero WHC representation: warm semi-arid, cold boreal, subarctic wetlands, northern peatlands, cold karst highland, Arctic highland. "Tropical humid" — the single largest global cluster at 9.49% of all basins — has only 1.16% of WH Cities (ratio 0.12×).

**Implication**: WH Cities is a *river-corridor civilization* artifact: the Nile, Tigris-Euphrates, Indus, Yellow River, Rhine and analogous regulated systems account for a disproportionate share. Sub-Saharan Africa and Amazonia are essentially absent — a known critique of UNESCO designation patterns quantified here. "Regulated rivers" and "Warm humid karst" are the clusters with greatest WHC statistical power for correspondence testing.

**Action**: deferred — analytical guidance for classification phase

---

### F6.3 — D-PLACE and WH Cities have divergent biases; they sample different parts of the environmental space

**Finding**: The two scholarship datasets concentrate in different clusters. D-PLACE over-samples tropical mountains (ethnographic reach); WHC over-samples river corridors and karst (monumental urbanism). Cool temperate lowlands are under-sampled by D-PLACE (0.40×) but near-proportional in WHC (1.60×), reflecting European academic bias in UNESCO nominations but relative absence from the fieldwork tradition. Neither dataset covers cold or hyperarid environments.

**Implication**: For correspondence testing, the two datasets are complementary rather than redundant. Combining them broadens coverage but does not resolve the shared cold/arid blind spot. Any rubric developed from a dataset skewed toward one cluster type should be validated against the other before generalization.

**Action**: deferred — analytical guidance for classification phase

---

### F6.4 — Coverage map confirms D-PLACE has impressive global reach but Argentina/Pampas is a notable blank

**Finding**: The global coverage map (`06_coverage_map.png`) shows D-PLACE societies spread across six continents with dense coverage in sub-Saharan Africa, SE Asia, North America, and Amazonia. A striking blank appears across Argentina (Pampas, Patagonia) and parts of the southern cone. Northwest North America is well covered.

**Implication**: The Argentine gap reflects colonial erasure before the ethnographic moment — the Conquest of the Desert (1870s–80s) decimated Tehuelche, Mapuche, and Querandí populations before systematic fieldwork was possible. The Ethnographic Atlas and HRAF had no data to draw from. This contrasts with the Northwest US, where rugged geography (Coast Range, dense rainforest, fjords) slowed colonial advance sufficiently for Boas-era documentation (1880s–1900s) to occur. D-PLACE blank spots have heterogeneous causes: sampling reach, population sparsity, and colonial destruction of source populations are distinct mechanisms that should not be conflated in interpreting under-representation.

**Action**: deferred — analytical guidance for classification phase

---

### F6.5 — Clusters with correspondence-testing power vs. clusters with no statistical basis

**Finding**: Clusters where both D-PLACE and WHC ratios are near zero (Arctic highland, cold boreal, subarctic wetlands, northern peatlands, cold karst highland) represent environments where no statistical correspondence testing is feasible with current datasets. These account for ~20% of global basin area. Clusters with strong signal in both datasets: tropical wet mountains, regulated rivers, warm humid karst. Clusters with signal in one only: hot wet tropics and tropical humid (D-PLACE only); cool temperate lowlands (WHC slightly).

**Implication**: Power analysis should precede any correspondence test design. Do not report null results for cold/arid environments as evidence against environmental correspondence — absence of data is the explanation.

**Action**: deferred — analytical guidance for classification phase

---
## 2026-04-25 · Task 7 · eVolv2k v4 distribution and aggregation design

**Method**: `notebooks/edop/explore/07_evolv2k_distribution.ipynb` · 256 events total, 1–1890 CE (LMR window) · CSV only, no DB required

---

### F7.1 — Catalog ends at 1890 CE; 20th-century queries return empty volcanic record

**Finding**: The eVolv2k v4 CSV contains 256 events with `year_ad` max = 1890. No events exist for 1891–1998 CE, despite the LMR window extending to 1998. Pinatubo 1991, Agung 1963, El Chichón 1982, and other major 20th-century eruptions are absent. This is an ice-core archive coverage limitation, not quiescence.

**Implication**: Band T queries with date ranges extending past ~1890 will return empty `volcanic_events` lists — which could be misread as "no significant eruptions." A `volcanic_events_coverage_note` field (or equivalent warning) should be added to the API response to flag this. The eVolv2k component of Band T is reliable only to ~1890 CE.

**Action**: 2026-04-28 — Added `volcanic_events_note` to `get_temporal_context()` return dict (`app/db/temporal.py`). Field is non-null only when `year_end > 1890`; text: "eVolv2k v4 catalog covers ~1–1890 CE; events after 1890 (e.g. Pinatubo, Agung, El Chichón) are not in the record."

---

### F7.2 — Catalog is dominated by small, anonymous events; named volcanoes are 16% of the record

**Finding**: 83.6% of events (214/256) have no named source volcano — they are ice-core-detected sulfate anomalies with no attributed eruption. Named events are 42/256 (16.4%). Tephra confirmation is even sparser (21 events). All canonical historically significant eruptions are present and correctly attributed: Samalas 1257 (59.42 Tg), Tambora 1815 (28.08 Tg), Eldgjá 939 (16.23 Tg), 536 CE mystery eruption (18.81 Tg), Krakatoa 1883 (9.34 Tg), Kuwae 1453 (9.97 Tg).

**Implication**: Users expect named volcanoes; most events have none. API responses should set this expectation explicitly. The unnamed events are still valid forcing signals — they simply lack attribution. Do not filter to named events only.

**Action**: deferred — guidance for API documentation and narrative layer

---

### F7.3 — 5 Tg is the right default threshold; 10 Tg excludes Krakatoa and Kuwae

**Finding**: At VSSI ≥ 5 Tg: 55 events (21% of catalog). At ≥ 10 Tg: 33 events. Krakatoa 1883 (9.34 Tg) and Kuwae 1453 (9.97 Tg) fall below the 10 Tg threshold. Both are historically consequential and climatically documented. The 5 Tg floor captures the interpretable tier without pulling in marginal noise.

**Implication**: Confirm `vssi_min=5.0` as the API default. Document as a named, adjustable parameter with rationale. The 10 Tg level is useful as a "major event" label in response fields but should not be the default filter.

**Action**: deferred — API documentation; vssi_min=5.0 default already implemented

---

### F7.4 — Empty-window rates at 5 Tg: 30% at 50 yr, 3% at 100 yr, 0% at 200 yr

**Finding**: Sliding-window analysis (step=10 yr) across 1–1998 CE: at VSSI ≥ 5 Tg, 70.3% of 50-yr windows contain ≥1 event; 96.8% of 100-yr windows; 100% of 200-yr windows. At ≥ 10 Tg: 50.8% / 78.9% / 97.2% respectively.

**Implication**: For 100-year queries (the dominant humanities use case), volcanic context is almost always available at the 5 Tg threshold. For 50-year queries, 30% will return empty — this is a genuine "no significant forcing" finding, not an error. The API should frame empty returns explicitly. Rubric: 100-year window + 5 Tg threshold is the reliable operating zone; 50-year + 10 Tg is probabilistic.

**Action**: deferred — guidance for API documentation and sandbox example window sizes

---

### F7.5 — Aggregation: count and sum-VSSI are correlated (r=0.868) but not interchangeable; all three summaries serve distinct purposes

**Finding**: In 100-yr sliding windows at ≥5 Tg: median count=2, median sum-VSSI=28 Tg, median time-since-last-major=47 yr. Count and sum-VSSI correlate at r=0.868 — high but not redundant. The 13% unexplained variance is driven by Samalas-class outliers: a window containing Samalas 1257 (59 Tg) registers count=4 (unremarkable) but sum-VSSI=120 Tg (extraordinary). Time-since-last-major captures recency structure count and sum cannot.

**Implication**: Return all three aggregations in the API response: `volcanic_event_count`, `volcanic_vssi_sum_tg`, `years_since_last_major`. They are complementary, not redundant. Sum-VSSI is the key discriminator for outlier centuries.

**Action**: 2026-04-28 — Added all three as computed fields in the `get_temporal_context()` return block (`app/db/temporal.py`). Computed from the already-fetched `events` list at zero extra DB cost. `years_since_last_major` uses 10 Tg as the "major event" threshold (per F7.3); returns None if no qualifying event in the window. Codebook updated with three new Band T implemented rows.

---

### F7.6 — Asymmetry field is binary for small events, continuous for climatically significant ones

**Finding**: Full catalog asymmetry distribution is strongly bimodal at 0.0 and 1.0 — most small events are coded as purely SH or purely NH based on detection in a single polar ice sheet. Above 5 Tg, the distribution becomes genuinely spread across intermediate values (0.0–1.0), reflecting real bilateral stratospheric dispersal for large tropical eruptions (Samalas 0.588, Tambora 0.456, Krakatoa 0.629).

**Implication**: Asymmetry is not a reliable continuous filter across the full catalog — it is an encoding artifact for sub-threshold events. Above 5 Tg it carries real signal about hemispheric reach. Return `asymmetry` as a per-event field; do not use it as a hard API filter. Location-aware weighting (if ever added) should apply only to events above threshold.

**Action**: deferred — asymmetry already returned as per-event field; hemispheric filtering ruled out (see F7.8)

---

### F7.7 — Kaifeng 1000–1100 CE sits at the end of the Medieval volcanic quiet; the following century is the most volcanically intense in the record

**Finding**: The 950–1100 CE window is the deepest volcanic quiet in the 2000-year eVolv2k record — near-zero event count and sum-VSSI. The Northern Song flourished in this period (consistent with the benign climatic baseline). The 1200–1300 CE window — covering the Northern Song's aftermath and the Mongol expansion — contains Samalas 1257 (59 Tg), making it the highest sum-VSSI century in the record (~120 Tg in 100-yr windows centered on 1250).

**Implication**: The Kaifeng 1000–1100 query (baked in as a sandbox example by Ruth) captures the *end* of a climatically favorable period. The collapse of the Northern Song (1127 CE, Jingkang Incident) and subsequent Southern Song vulnerability to Mongol conquest (1279 CE) both fall in a dramatically more volcanically active and likely climatically disrupted period. This is a worked example of why temporal window choice matters — and a candidate correspondence hypothesis for future Band T work. Flag to Ruth.

**Action**: deferred — candidate hypothesis for Band T correspondence work; note flagged for Ruth

---

### F7.8 — Hemispheric filtering is asymmetric and should not be implemented as a default API behavior

**Finding**: 100-yr sliding window counts at VSSI ≥ 5 Tg by hemispheric filter: NH-relevant (asymmetry > 0.5) median=2, empty=10.5% — virtually identical to unfiltered (median=2, empty=3.2%). SH-relevant (asymmetry < 0.5) median=0, empty=60.5%. Symmetric-only median=1, empty=45.8%. NH filtering has near-zero effect because the catalog is 64.5% NH-dominant by event count. SH filtering makes the record uninformative — 60% of century-scale windows contain no SH-dominant events at the 5 Tg threshold.

**Implication**: Do not implement hemispheric filtering as an API parameter. The catalog's NH bias is a dataset property to be documented, not compensated for. All events above the VSSI threshold should be returned regardless of query location, with `asymmetry` included as a per-event field for users who want to apply their own weighting. The "SH-relevant reduces median by 100%" result is a consequence of the median hitting zero, not universal emptiness — but the 60% empty-window rate is sufficient to rule out filtering as a useful default. API guide should note that eVolv2k is NH-biased by construction and that asymmetry should be interpreted accordingly.

**Action**: deferred — hemispheric filtering ruled out; NH bias disclosure flagged for API guide

---

### F7.9 — eVolv2k and LMR are currently coupled by the LMR date window, but should be decoupled in the API

**Finding**: The current Band T implementation gates eVolv2k returns by the LMR date range (1–1998 CE), because both layers were introduced together. But eVolv2k's actual coverage extends to ~500 BCE — the full catalog contains 45 pre-CE events, including the 44 BCE Okmok eruption (a candidate forcing event for the fall of the Roman Republic) and other historically significant BCE eruptions. These are inaccessible to any current Band T query. LMR's 1 CE floor is a proxy-network limitation: paleoclimate reanalysis requires sufficient tree ring, ice core, and speleothem density, which thins rapidly before ~200 CE and is untenable before 1 CE globally. That constraint is specific to LMR and does not apply to eVolv2k.

**Implication**: Decouple the two layers in the API. eVolv2k should be queryable for any window within its actual coverage (~500 BCE–1890 CE), returning events with a status indicating the volcanic record is available even when LMR is not. LMR should retain its 1–1998 CE gate with a note about proxy network thinning. A query for Babylon 600–400 BCE should return volcanic events (if any above threshold) alongside an explicit `lmr_status: out_of_range` — not silence. This is a design change to route and document before the API is finalized, not a characterization task. Flag for prospectus update.

**Action**: 2026-04-28 — Decoupled in `app/db/temporal.py`: LMR clamped to 0–1998, eVolv2k clamped to −491–1890 independently. `lmr_status` field added ("available"/"out_of_range"). BCE queries now return volcanic events with empty LMR series. Hard rejection gate removed from `app/api/routes.py`. DB confirmed: 59.33 Tg event at 426 BCE (largest pre-CE event in catalog). Three new tests added to `tests/test_band_t.py`: BCE LMR out_of_range, 426 BCE event detection, BCE aggregates.

---

## 2026-04-25 · Task 8 · HYDE 3.4 — per-epoch distributions and signal emergence

**Method**: `notebooks/edop/explore/08_hyde_distributions.ipynb` · 5 NetCDF files (cropland, grazing_land, urban_area, population_density, total_rice) · 8 epochs (-8000, -4000, -1000, 0, 1000, 1500, 1900, 2000) · xarray lazy slicing, one time step loaded at a time

**Dataset note**: Files are labeled HYDE 3.4 (created April 2025), not 3.5. Time axis uses `cftime.DatetimeNoLeap` with `has_year_zero=True` (astronomical year numbering). 128 time steps with variable resolution: millennial BCE, centennial 100–1700 CE, decadal 1710–1950, annual 1951–2025. Grid: 2160 × 4320 cells at 5-arcmin (~9km) resolution. Units: km² for area variables; capita/km² for population_density.

** KG ?s **: 
- What happens when a request overlaps or spans time steps, e.g. 150-250?
- the cells cover ocean as well, can those be skipped if a table is row-per-call?
- a basin may enclose cells with very different values; that info loss seems very problemmatic. is there a way to preserve the detail that HYDE provides?
- what is meant by "land use anomaly fields"? why bring the analytic step of a baseline into the picture?

---

### F8.1 — Grazing land is the first and most spatially extensive anthropogenic signal; cropland follows

**Finding**: At 4000 BCE, grazing land is already at ~80% zero cells (20% non-zero) while cropland is at ~94% zero (6% non-zero). By 1000 BCE grazing reaches 68% zero vs. cropland 83%. The gap persists through the full record — at 2000 CE grazing is 41% zero, cropland 56% zero. On the log-scale mean trajectory, grazing consistently exceeds cropland in absolute km² area at every epoch. Both variables follow roughly log-linear growth trajectories, implying consistent exponential expansion rates across the full period.

**Implication**: For Band T queries in the BCE period, grazing land is the more informative land-use variable. The emergence of non-trivial cropland signal begins around 4000–1000 BCE, concentrated in the Fertile Crescent, Nile valley, Indus, and Yellow River regions. Grazing's earlier and broader signal reflects the archaeological reality that pastoralism preceded and spatially exceeded sedentary agriculture.

**Action**: deferred — analytical guidance for Band T HYDE implementation and narrative layer

---

### F8.2 — Urban area and total rice are globally invisible at distribution scale; specialty variables only

**Finding**: Urban area remains at ~99–100% zero cells through 1900 CE; the p99 value is 0.096 km² even at 1900 CE. Total rice is 100% zero at 8000 BCE and still 98.5% zero at 2000 CE. Both variables show signal only in very high percentiles, concentrated in a small number of cells. On the log-scale trajectory, urban area shows a hockey-stick inflection after 1900 CE reflecting intensification within already-occupied cells rather than spatial expansion.

**Implication**: Urban area and total rice will return zero for the vast majority of Band T basin queries regardless of epoch. They are not useful as default Band T fields. Consider making them opt-in, or returning them only when non-zero. Their value is for specialist queries — urban area for pre-modern city studies, total rice for SE Asian agricultural history.

**Action**: deferred — HYDE variable selection for Band T implementation; urban area and rice are opt-in candidates

---

### F8.3 — Population density % zero is flat across 10,000 years; this is a model artifact, not an empirical finding

**Finding**: Population density shows ~45% zero cells at 8000 BCE, declining only to ~40% at 2000 CE — a nearly flat trajectory. This is not an empirical finding about human settlement history. HYDE's deep-time population layer distributes a global population estimate (derived from secondary historical sources) across all land cells proportionally to a habitability potential score. Any cell with non-zero habitability receives a non-zero population density value, even if that value is 0.0003 cap/km² — statistically less than one person per square kilometer. The % zero metric is measuring the extent of HYDE's habitability model, not the presence of humans.

**Implication**: This does not pass a basic smell test. The Out of Africa dispersal, the late peopling of the Americas (~15,000 BCE), the settlement of the Pacific — none of this spatial history is recoverable from a model that pre-populates every habitable cell from the start. HYDE's population layer is redundant with EDOP's own environmental suitability characterization (Bands A–E) in the deep BCE period, and less honest. Population density from HYDE is likely meaningful only from roughly 0–1000 CE onward, where global population estimates are anchored by documentary and archaeological evidence and spatial allocation has real data to constrain it. Pre-CE HYDE population values should either be excluded from Band T API responses or returned with a strong epistemic caveat. Do not use % zero as the signal-emergence metric for this variable — use a meaningful density threshold (e.g. ≥ 1 cap/km²) instead.

**Action**: deferred — population density reliability caveat documented; open design question (F8.6) flagged for expert review

---

### F8.5 — EDOP's climate characterization (Band C) is silently wrong for BCE queries

**Finding**: Band C (bioclimatic proxies: temperature, precipitation, aridity, biome, ecoregion) is sourced from WorldClim, a contemporary climatology representing approximately 1970–2000 CE. For any BCE query, EDOP returns contemporary climate values without qualification. A query for Çatalhöyük 7000 BCE returns present-day Anatolian climate, not Neolithic climate. LMR (the paleoclimate reconstruction in Band T) covers only 1–1998 CE and does not extend into the BCE period. There is currently no paleoclimate layer in EDOP that covers BCE conditions. Bands A (physiography), B (hydrology), and E (coastality) are geomorphological and topological — effectively timeless on human timescales — and remain valid for BCE queries. Band C is not.

**Implication**: BCE queries in EDOP are implicitly geomorphological characterizations, not environmental ones in the full sense. This should be disclosed in the API response, not left for users to discover. A `climate_note` field — e.g. "Band C reflects contemporary baselines (WorldClim ~1970–2000 CE); no paleoclimate reconstruction is available for this query period" — should be injected when `to_year < 0` or when no LMR data is available. The HYDE habitability model (which may internally use Holocene paleoclimate reconstructions) is not a reliable substitute — its spatial allocation methodology is too indirect and its assumptions are opaque. The right fix is disclosure, not patching. Flag for API design and prospectus update.

**Action**: 2026-04-28 — Added `_note` to `profile_groups["C"]` and `profile_groups["D"]` in `routes.py` when `from_year < 0`. Band C note: contemporary climatology (WorldClim ~1970–2000 CE), not epoch-representative. Band D note: contemporary land use/demographic data (~2000–2009 CE), not epoch-representative. Both bands are still returned — the note informs, it does not gatekeep; users may request them for comparison or reference and are entitled to do so. Sandbox year inputs changed from `min="0"` to `min="-491"`. Design principle established: qualifying notes are first-class payload content owned by the API; consuming apps surface them, they do not generate them. A corollary: any band that a user receives was requested by them; the API's responsibility is disclosure, not suppression. Prospectus update to capture this framing flagged as a follow-on task after sigrefine phase.

---

### F8.4 — Population density mean shows a 20th-century hockey stick; land use variables do not

**Finding**: On a linear scale, mean population density is essentially flat from 8000 BCE through 1500 CE, rises modestly to ~11 cap/km² by 1900 CE, then jumps to ~40 cap/km² at 2000 CE — more than 3× growth in a single century. The area variables (cropland, grazing) show no equivalent hockey stick on their log-scale trajectories; their growth rates are roughly constant across the full period. The industrial-era population explosion is a qualitatively different phenomenon from the steady long-run expansion of land use.

**Implication**: For Band T queries spanning 1900–2000 CE, population density is the most dramatically changing variable. For pre-1900 queries, the intensity signal is modest on an absolute scale even if the spatial footprint (measured by % non-zero) is ancient. This has direct bearing on how Band T summarizes HYDE for historical period queries: the 20th-century values should be treated as a distinct regime, not just the continuation of a long trend.

**Action**: deferred — guidance for Band T HYDE narrative interpretation; 20th-century as distinct regime flagged for LLM prompt design

---

### F8.7 — 1000 BCE is the defensible global baseline for land-use anomaly reporting

**Finding**: Ratio of CE epoch mean to candidate baseline epochs for cropland and grazing land:
- vs 8000 BCE: ratios of 1000x–9500x (cropland) and 400x–3500x (grazing) — denominator too near-zero to be analytically useful
- vs 4000 BCE: ratios of 19x–157x (cropland) and 16x–129x (grazing) — large but more tractable
- vs 1000 BCE: ratios of 2.8x–23x (cropland) and 3.9x–32x (grazing) — interpretable and historically meaningful

At 1000 BCE, agriculture is established in all core civilizational regions (Fertile Crescent, Nile, Indus, Yellow River) but has not yet intensified globally. Cropland at 1000 CE is ~3x the 1000 BCE level; at 2000 CE ~23x. These are ratios a non-specialist user can interpret.

**Implication**: Use 1000 BCE as the global pre-anthropogenic baseline for HYDE land-use anomaly fields in the Band T API response. Return both the raw epoch value and the ratio to 1000 BCE. Caveat in API guide: the baseline is global — in already-agricultural regions (Mesopotamia, Egypt, China) the 1000 BCE baseline is not "pre-agricultural," so local ratios will understate intensification relative to a truly pre-agricultural local condition. A future regional baseline refinement is possible but deferred.

**Action**: deferred — 1000 BCE baseline convention established; implementation deferred to Band T HYDE integration

---

### F8.6 — Open design questions deferred to October expert meeting

**Question 1 — Does population density belong in an environmental signature?** Population is a human phenomenon, not an environmental one. EDOP's core claim is environmental characterization of place; including population density in Band T muddies that boundary. The land use variables (cropland, grazing) characterize human transformation of the landscape, which is defensibly environmental. Population density characterizes human presence, which is more ambiguously so. Whether Band T should include population density at all — or whether it belongs in a future CDOP layer — is a design question that warrants expert input.

**Question 2 — Should HYDE habitability be surfaced for BCE queries as an explicit, qualified signal?** For BCE queries where Band C (contemporary climate) is not representative and LMR is out of range, HYDE's internal habitability model — whatever its limitations — may be the only available proxy for environmental conditions at the query epoch. Rather than discarding it, it could be returned as a clearly labeled, heavily caveated field: "HYDE-modeled habitability index at epoch X (reconstruction uncertainty high; treat as indicative only)." Whether this adds value or misleads users is a judgment call that benefits from domain expert review. Flag for the October 2026 Pitt presentation as an open question.

**Action**: deferred — open design questions flagged for October 2026 expert meeting

---

### F8.8 — HYDE temporal resolution varies by era; BCE queries typically return a single epoch

**Finding**: Confirmed from `temporal.hyde_times` (128 rows). Resolution structure:
- −10000 to −1000 BCE: 1000-year steps (10 epochs)
- 0 to 1700 CE: 100-year steps (18 epochs)
- 1710 to 1950: 10-year steps (25 epochs)
- 1951 to 2025: annual steps (75 epochs)

A 200-year BCE window (e.g. −1100 to −900) returns exactly 1 epoch (−1000 CE). Mixed-resolution windows are possible: a 1650–1750 query returns centennial steps at the low end and decadal at the high end; the row-per-epoch structure is honest about this but it is not obvious to a consumer.

**Implication**: Band T HYDE payload must carry a temporal resolution note. A user requesting a BCE window must be told they are receiving a single millennium-average, not a trend. Mixed-resolution windows need narrative-layer disclosure. The note is API responsibility — not left to consuming apps.

**Action**: add `hyde_resolution_note` to Band T HYDE payload in `app/db/hyde.py`; surface note in sandbox Band T accordion alongside existing LMR and climate notes.

---

### F8.9 — Spatial join performance: functional centroid index required; cold-cache L8 ~640ms

**Finding**: Query `notebooks/edop/hyde_query_design.ipynb` (2026-04-29), Timbuktu L8 basin (hybas_id=1071469810, 7 cells), L6 basin (basin06, ~30ms warm-cache).

Without functional index on `ST_Centroid(geom)`: 6.7s (full 2.2M-row seq scan — GIST index on `hc.geom` is bypassed by the function wrapper).

After `CREATE INDEX idx_hyde_cells_centroid ON temporal.hyde_cells USING GIST (ST_Centroid(geom))` + `ANALYZE`: 640ms cold-cache, ~300ms warm-cache for L8. L6: ~30ms (warm cache + simpler polygon geometry). Window size (3 vs 38 vs 128 time steps) barely affects total cost — the spatial join dominates; the cross join and array access are cheap at all window sizes.

Alternative predicates (`ST_Intersects`, `ST_Within(hc.geom)`) are within 50ms of centroid method but return different cell counts (17 and 1 respectively vs 7 for centroid). Centroid method retained as correct.

**Implication**: Cold-cache L8 ~640ms is acceptable as a supplementary Band T enrichment query. No pre-materialized basin→cell lookup table needed at current scale.

**Action**: add `idx_hyde_cells_centroid` functional index and `ANALYZE` to `sql/edop/create_hyde_cells.sql` and `scripts/edop/load_hyde_cells.py` so future reloads include them automatically.

---

### F8.10 — Response shape confirmed; notes-in-payload principle applies to HYDE

**Finding**: Per-epoch dict structure validated at Timbuktu 1000–1200 CE (3 epochs, 7 cells):
```json
{
  "year_ce": 1000,
  "cropland_km2": 0.079,  "grazing_km2": 4.705,
  "pasture_km2": 0.0,     "rangeland_km2": 4.705,
  "basin_area_km2": 573.4, "n_cells": 7,
  "cropland_pct": 0.01,   "grazing_pct": 0.82,
  "pasture_pct": 0.0,     "rangeland_pct": 0.82
}
```
`grazing_km2 == rangeland_km2` when pasture = 0 (by HYDE definition: grazing_land = pasture + rangeland) — expected for semi-arid Sahel. Cropland ~0.01–0.02% of basin area in medieval Timbuktu basin is geographically plausible.

SQL must use `::float8` (not `::numeric`) to return native Python floats from psycopg3; `::numeric` returns `decimal.Decimal` which breaks downstream arithmetic without explicit casting.

**Implication**: The qualifying-notes-as-first-class-payload principle (established for Bands C, D, T in sigrefine01) extends to HYDE: temporal resolution disclosure, BCE single-epoch caveat, and mixed-resolution window note all belong in the payload as `_note` fields. Consuming apps (sandbox, Federico's API) surface them; they do not generate them.

**Action**: implement `app/db/hyde.py` with this response structure; use `::float8` throughout; include `_note` field carrying resolution disclosure; wire into Band T response in `app/db/temporal.py` or `app/api/routes.py`; add 4 HYDE rows to codebook; surface in sandbox Band T accordion.

---
## 2026-04-26 · Task 9 · HYDE basin aggregation and s/u characterization

**Method**: `notebooks/edop/explore/09_hyde_basin_aggregation.ipynb` · L8: 500-basin stratified sample (25/cluster × 20 clusters); L6: 500-basin stratified sample from Task 5b clusters · HYDE variables: cropland, grazing_land · Epochs: 1000 BCE, 0 CE, 1000 CE, 2000 CE · Aggregation: polygon-interior mean (shapely vectorized contains) for s values; centroid lookup + sub_area-weighted traversal for u values

---
### F9.1 — Polygon-interior and centroid agree for small basins; diverge meaningfully above ~100 km²

**Finding**: Aggregation comparison at 2000 CE cropland (L8 sample, 500 basins): median absolute difference = 0.000 km², p95 = 8.7 km². Disagreement is essentially zero for basins under ~10 km² and grows with basin size, concentrated above ~100 km² sub_area. Median cells per basin = 8; p95 = 39. 39 of 500 basins (8%) had no HYDE cell center inside their polygon and required centroid fallback — these are the smallest, most rugged sub-basins. One notable outlier: a basin where centroid returned ~0 km² cropland but polygon-interior returned ~38 km², a case where the centroid cell landed on an unfarmed patch while the polygon interior was predominantly agricultural. The relative-diff p95 = 1.0 is a denominator artifact (near-zero poly_val), not evidence of systematic disagreement.

**Implication**: Polygon-interior is the correct aggregation method and earns its computational cost for basins above ~100 km². For the smallest L8 sub-basins it is equivalent to centroid but not worse. The outlier case demonstrates the failure mode centroid is prone to and justifies the polygon-interior choice on principle. Centroid fallback for the 8% of tiny basins is acceptable.

**Action**: deferred — polygon-interior confirmed as correct method; guidance for Band T HYDE implementation

---

### F9.2 — HYDE s values: global distribution confirms heavy zeros; grazing more extensive than cropland at all epochs

**Finding**: L8 sample (500 basins), polygon-interior s values. At all epochs through 1000 CE, cropland median = 0 and 25th percentile = 0 — more than half the sample has no cropland signal. At 2000 CE, cropland median rises to only 0.008 km²/cell, 75th percentile = 8.0 km²/cell. Grazing land is consistently more spatially extensive: at 2000 CE grazing median = 1.52 km²/cell vs cropland median = 0.008 km²/cell. Mean growth from 1000 BCE to 2000 CE: cropland ~18×, grazing ~32×. The grazing expansion reflects colonial-era pastoral land transformation (Americas, Australia, sub-Saharan Africa) rather than industrialization; the land-area footprint of grazing far exceeds cropland globally.

**Implication**: For Band T basin-level HYDE queries, zero returns will be the majority result for cropland at all pre-CE epochs and for most basins even at 2000 CE. Non-zero values are concentrated in a minority of agriculturally significant basins. Grazing land signal emerges earlier and covers more basins than cropland — it is the more globally representative land-use variable for historical queries. API responses should frame zero as an honest "no land use signal at this location/epoch," not a missing-data condition.

**Action**: deferred — analytical guidance for Band T HYDE API design and response framing

---

### F9.3 — L6 medians substantially higher than L8; larger polygons capture earlier and wider land-use signal

**Finding**: L6 sample s values show consistently higher medians than L8 at the same epochs. At 1000 CE: L8 cropland median = 0.000, L6 = 0.022 km²/cell. At 2000 CE: L8 cropland median = 0.008, L6 = 1.055 km²/cell; L8 grazing median = 1.52, L6 = 7.27 km²/cell. Means are also slightly higher at L6 (cropland 2000 CE: L8 mean = 7.32, L6 = 8.46 km²/cell) but the median shift is the more telling statistic. A near-zero floating-point value (1.3×10⁻⁷) appears at L6 cropland 0 CE — a HYDE model artefact consistent with F8.3, not a real signal.

**Implication**: L6 basins are more likely to contain at least some agricultural land within their larger polygon boundary even when the local sub-basin core is unfarmed — the larger polygon casts a wider net and captures more of the agricultural fringe. L6 signatures are inherently more land-use-signal-rich than L8 at the same epoch. This has design implications: a Band T HYDE query at L6 will return more non-zero values and apparent earlier signal emergence than the same query at L8, but the signal reflects a broader regional average rather than local conditions. The two levels are answering different questions, consistent with F5.7.

**Action**: deferred — analytical guidance for Band T HYDE implementation; L8 vs L6 distinction documented

---

### F9.4 — HYDE s/u divergence is dramatically wider than climate divergence; effective N is small

**Finding**: HYDE s/u divergence (log₂(upstream/local)) was computed for basins where both s and u exceeded 0.001 km². Effective N ranged from 42 (L8 cropland 1000 BCE) to 104 (L8 grazing 2000 CE) — 8–21% of the 500-basin sample. The rest are headwaters (no upstream), zero-land-use environments, or both. Tail extents are far wider than the climate divergences in Task 3: HYDE p95 reaches +5.52 log₂ (upstream 46× more cropland than local, L6 2000 CE) vs climate precipitation p95 of +0.39 log₂. Cropland medians are consistently negative (local > upstream, range −0.91 to −0.07), meaning for most historically active basins the local site IS the agricultural concentration. Grazing medians are near zero at all epochs. A positive right tail persists at every epoch in both variables — the minority of Ur-type configurations where an unfarmed or less-farmed local basin sits downstream of an agricultural heartland.

**Implication**: HYDE s/u divergence is a stronger and more structurally interesting signal than climate divergence when it fires, but fires in a smaller fraction of basins. The negative cropland median (local > upstream) and the persistent positive tail (upstream > local) are both analytically meaningful and point in opposite cultural-historical directions: the first describes a settlement at the agricultural core; the second describes a downstream receiver of upstream agricultural surplus or runoff. Both configurations are real and historically attested.

**Action**: deferred — analytical guidance for classification phase and Band T HYDE divergence reporting

---

### F9.5 — s/u divergence collapses toward zero by 2000 CE; the most analytically useful window is 0–1000 CE

**Finding**: Divergence distributions shift markedly between 1000 BCE and 2000 CE. At 1000 BCE, distributions are flat and wide — sparse, patchy land use produces large and variable local/upstream contrasts in either direction. By 2000 CE, both cropland and grazing distributions tighten sharply around zero and converge with each other. This reflects land use expanding broadly enough that most basins and their upstream catchments have comparable amounts — the contrast collapses. The convergence is consistent with agricultural and pastoral expansion filling in the landscape relatively uniformly across both local and upstream positions, rather than remaining concentrated in a few hotspots. The positive and negative tails persist but the bulk of the distribution loses its divergence signal.

**Implication**: For CDOP correspondence work, HYDE s/u divergence is most analytically productive in the middle epochs (roughly 0–1000 CE), where land use is established enough for divergence to be computable but not yet so globally widespread that the local/upstream contrast has washed out. Queries at 2000 CE will return near-zero divergence for most basins — not because land use is absent but because it is now too uniform to discriminate. This has direct implications for Band T API design: the divergence field is most informative for pre-industrial historical queries and should be interpreted cautiously for modern-era baselines. Open question for expert review: whether the convergence is genuinely "expansion in place" (uniform spread) or partly a large-basin averaging artefact at L6 — the L8 and L6 distributions show the same pattern, suggesting the former, but not conclusively.

**Action**: deferred — analytical guidance for Band T HYDE divergence; 0–1000 CE as productive window documented

---

### F9.6 — BasinATLAS (EarthStat) and HYDE 2000 CE cropland agree globally but diverge spatially at sub-basin scale; Band D is not a proxy for historical land use

**Finding**: BasinATLAS `crp_pc_sse` is sourced from EarthStat circa 2000 — a hybrid product combining agricultural inventory data with MODIS/GLC2000 satellite classification. HYDE 3.4 at 2000 CE uses the same inventory data (FAO statistics) allocated spatially via population density and suitability models. Globally their totals agree closely (~15M km² cropland each). Divergence is therefore a **spatial allocation** problem, not a definitional one.

At three reference sites, HYDE 2000 CE (as % of basin area) vs static EarthStat:

| Site | EarthStat (static) | HYDE 1000 BCE | HYDE 1 CE | HYDE 1000 CE | HYDE 2000 CE |
|---|---|---|---|---|---|
| Timbuktu | 0% | 0.0% | 0.02% | 0.08% | 1.3% |
| Ur | 60% | 4.0% | 2.9% | 4.9% | 18.1% |
| Kaifeng | 71% | 16.6% | 65.4% | 37.7% | 59.7% |

Kaifeng is coherent across the two sources (59.7% vs 71% at 2000 CE; the HYDE 1 CE peak at 65% reflects Han dynasty intensification). Timbuktu is consistent (both near zero). Ur is the outlier: EarthStat assigns 60% to the sub-basin while HYDE allocates only 18% at 2000 CE — a ~3× gap despite agreeing globally. Small L8 basins in high-intensity, irrigation-dominated agricultural regions (Mesopotamian plain) are most exposed to this kind of spatial allocation disagreement.

**Implication**: The divergence is not a HYDE calibration failure — it reflects genuine uncertainty in *where* cropland sits within a region at fine spatial resolution, which both products resolve differently. HYDE's historical time series is internally consistent and should be interpreted as trajectories and anomalies, not absolute ground truth per sub-basin. For small L8 basins in agricultural hotspots, the EarthStat static value and HYDE temporal query are not interchangeable. Band D (EarthStat) and Band T (HYDE) measure related but distinct things; researchers should not use Band D as a proxy for historical land use. This divergence is flagged for expert review alongside F8.5 and F8.6 (October 2026 meeting).

**Action**: deferred — EarthStat/HYDE spatial divergence flagged for October 2026 expert review; Band D vs Band T distinction documented

---

### F9.7 — Reference site HYDE trajectories are historically legible; Kaifeng shows Han dynasty peak, Ur shows ancient agriculture, Timbuktu is near-zero throughout

**Finding**: Polygon-interior HYDE cropland (km², local basin) at three reference sites across four epochs:

| Site | 1000 BCE | 1 CE | 1000 CE | 2000 CE |
|---|---|---|---|---|
| Timbuktu | 0.00 | 0.02 | 0.08 | 1.30 |
| Ur | 10.79 | 10.06 | 17.55 | 72.03 |
| Kaifeng | 28.81 | 174.72 | 100.78 | 159.47 |

(Values are total km² of cropland within the L8 sub-basin polygon, computed as polygon-interior mean × n_cells.)

Kaifeng's 1 CE peak at ~175 km² — the highest value across all epochs and sites — corresponds to Han dynasty agricultural intensification in the Yellow River basin, one of the most productive agricultural regions in the ancient world. The drop to ~101 km² at 1000 CE and recovery to ~160 km² at 2000 CE traces the contraction and re-expansion of farming across the Song–Ming–Qing periods. Ur shows a modest but consistent ancient signal (10–18 km²) across all pre-modern epochs, consistent with Mesopotamian irrigated agriculture predating the HYDE window; the 2000 CE jump to 72 km² reflects modern Iraqi irrigation expansion. Timbuktu is effectively zero throughout — the Saharan fringe location produces no land-use signal at sub-basin scale.

**Implication**: HYDE trajectories at individual reference sites are historically interpretable and align with known cultural-historical patterns. The signal is real and discriminating, not noise. This validates the Band T HYDE component as a meaningful input for CDOP correspondence work, particularly for the 0–1000 CE window identified in F9.5 as the most analytically productive epoch range.

**Action**: deferred — reference site validation complete; analytical guidance for Band T HYDE implementation

----

## 2026-04-26 · Task 10 · LMR v2.1 temporal/spatial structure and grid behaviour

**Method**: `notebooks/edop/explore/10_lmr_structure.ipynb` · Variables: PDSI, air temperature (anomaly), precipitation rate (anomaly) · Grid: 2°×2°, 16,380 cells globally (values at all cells including ocean) · Temporal: 0–1998 CE, 2001 annual steps · Ensemble: 20 MCruns × (mean + spread) files

### F10.1 — LMR time series show an expanding-funnel shape: an artifact of proxy density, not a climate signal

**Finding**: All three variables (PDSI, temperature, precipitation) show compressed year-to-year variance in the early period (0–500 CE) that expands progressively through the record. In the early centuries each line in the time series gallery hugs close to zero with small oscillations; from ~1200 CE onward the same lines swing widely. This pattern is uniform across all latitude bands and locations.

This is the LMR "regression to prior" effect. When proxy records are sparse (early centuries), all 20 MCruns produce cautious reconstructions constrained by the model's long-run climatology prior — their grand mean stays near zero. As proxy density increases in later centuries, each MCrun is pulled by real proxy data toward a genuine signal; the grand mean inherits that signal's variability. The funnel shape is a data-quality signature, not a climate signature: pre-500 CE reconstruction amplitude is systematically suppressed relative to the actual historical climate variability at those locations.

**Implication**: LMR is not equally reliable across its full 0–1998 CE window. The early period (roughly 0–700 CE) is the least trustworthy — not because the data is wrong, but because the reconstruction has low power to detect anomalies when proxies are sparse. Band T queries in this window should carry a caveat about reduced reconstruction fidelity. The most analytically productive window is approximately 700–1900 CE, where proxy networks are dense enough to constrain the reconstruction meaningfully. This interacts with the HYDE finding (F9.5) that s/u divergence is most useful at 0–1000 CE — the overlap of reliable LMR and meaningful HYDE divergence is roughly 700–1000 CE.

**Action**: addressed via F10.3 (lmr_fidelity_note added to Band T response, firing when year_start < 700)

---

### F10.2 — Temporal variance dominates geographic variance for all three LMR variables; Band T is genuinely non-redundant with Band C

**Finding**: Variance decomposition across 34 sample locations × 2001 years:

| Variable | Geographic % | Temporal % | Dominant |
|---|---|---|---|
| PDSI | 23.7% | 76.3% | Temporal |
| Air temperature | 31.6% | 68.4% | Temporal |
| Precipitation rate | 7.3% | 92.7% | Temporal |

Geographic variance measures how much the 2000-year mean anomaly differs between locations; temporal variance measures how much a single location's value swings from year to year. Since LMR stores anomalies from the model climatology prior (not absolute values), all locations have long-run means near zero — geographic differences nearly vanish. Temporal fluctuations driven by proxy data are the dominant source of variance.

**Implication**: The result is the opposite of what was anticipated for temperature (expected geographic dominance). Because LMR variables are anomaly fields, knowing *when* a query is placed matters more than knowing *where* for all three variables. This validates Band T as genuinely non-redundant with Band C: Band C provides absolute climatology (what temperature/precipitation is typical here); LMR provides the departure from that norm at a given epoch (how anomalous was this period). A long-window LMR mean would converge toward zero and add little — the value is in the temporal structure. Precipitation is the most temporally dominated (92.7%), consistent with high interannual variability and near-zero long-run anomaly means.

**Action**: deferred — validates Band T / Band C non-redundancy; analytical guidance for signature documentation

---

### F10.3 — Within-run spread dominates across-run std by ~4.6×; spread is stable across the record and a usable uncertainty field

**Finding**: Median uncertainty magnitudes across sample locations and all years:

| Variable | Within-run spread | Across-run std | Ratio |
|---|---|---|---|
| PDSI | 1.51 | 0.33 | 4.63× |
| Air temperature | 0.48 K | 0.11 K | 4.32× |
| Precipitation rate | ~0 (display precision) | ~0 | ~4.9× |

Within-run spread (std across ~100 particles within each MCrun) is ~4.6× larger than across-run std (disagreement between the 20 MCruns). The 20 MCruns — each using a different random proxy subset — produce consistent grand means. The dominant uncertainty is particle dispersion within each MCrun: the range of plausible climate states the model's dynamics and proxy assimilation admit at each time step.

PDSI spread early (0–500 CE) vs late (1500–1998 CE): 1.55 vs 1.36, ratio 1.13×. Spread is only modestly elevated in the early period despite the dramatic funnel visible in the grand mean. This is because spread captures model intrinsic uncertainty (which sets a floor even without proxies), while the funnel reflects suppression of the *mean signal* by regression to the prior. Proxies constrain the mean but don't eliminate particle dispersion.

**Implication**: The within-run spread is the appropriate uncertainty field to expose in the Band T API — it is the larger, more meaningful source, and it is reasonably stable across the record (~13% elevation in early centuries vs late). It cannot serve as a standalone proxy for the funnel-effect (F10.1): spread alone will not strongly flag early-period reconstructions as less reliable. An explicit epoch-based caveat (e.g. "reconstruction fidelity reduced before ~700 CE due to sparse proxy networks") is necessary in addition to returning the spread value.

**Action**: 2026-04-28 — Added `lmr_fidelity_note` to `get_temporal_context()` return dict, firing when `lmr_available and year_start < 700`. Text: "Climate reconstructions before 700 CE carry greater uncertainty due to sparser proxy records for this period; treat values as indicative." Rendered as yellow alert at top of Band T accordion body in sandbox.

---

### F10.4 — Band C and LMR are statistically orthogonal; 1850–1900 window sits within LIA cooling

**Finding**: Spearman correlation between Band C absolute climatology and LMR 1850–1900 anomaly (relative to full 2000-year mean): temperature r = −0.055 (p = 0.759), precipitation r = −0.112 (p = 0.527). Both near zero and non-significant across 34 sample locations. LMR 1850–1900 temperature anomaly stats: mean = −0.065 K, median = −0.053 K, std = 0.075 K, range −0.221 to +0.061 K. The 75th percentile is −0.010 K — most locations are slightly below the 2000-year mean in this window. Only a few locations (high Subtropical NH) show positive anomalies.

The negative mean anomaly reflects the LIA signal: 1850–1900 sits at the end of the Little Ice Age cooling period relative to the 2000-year mean. The Medieval Climate Anomaly (950–1250 CE) raised the 2000-year mean for NH locations, making 1850–1900 appear cool in comparison. The industrial warming that dominates post-1900 is largely outside LMR's effective window for aggregate comparison.

**Implication**: Band C (absolute climatology, WorldClim) and LMR (temporal anomaly, paleoclimate reanalysis) contain statistically independent information and are genuinely non-redundant in the signature. A researcher using both receives orthogonal characterisations: what is the typical climate here (Band C), and how much did climate at this location depart from its long-run norm at a given epoch (Band T/LMR). There is no risk of double-counting. This also means there is no useful "sanity check" between the two in the traditional sense — agreement is not expected and near-zero correlation is the correct outcome.

**Action**: deferred — validates Band C / Band T statistical independence; analytical guidance for signature documentation

---

### F10.5 — LMR 2°×2° grid is ~38× coarser than L8 basin resolution; spatial precision ceiling is ~200 km

**Finding**: 190,675 L8 basins map to 4,999 unique LMR 2°×2° cells — a 38:1 compression ratio. Basins-per-cell distribution: median 39, p75 56, p95 74, max 109. LMR provides values at all 16,380 grid cells globally (land and ocean); 4,999 of those cells (30%) contain at least one L8 basin, covering the land areas with HydroSHEDS river basin coverage. The remaining 11,381 cells are ocean, polar regions, or endorheic areas outside HydroSHEDS. The highest basin densities (approaching 110 per cell) occur in mountain zones — Alps, Himalayas, Rockies — where many small headwater sub-basins pack into a single 2° square.

**Implication**: A Band T LMR query for any given L8 basin returns the same value as ~39 neighboring basins on average. The spatial precision of the LMR component is approximately one 2°×2° cell (~200 km at mid-latitudes), regardless of basin size. Fine-grained local climate anomaly characterisation is not possible with LMR at L8 resolution — the reconstruction is inherently regional. This should be disclosed in API documentation: "LMR climate anomaly values are resolved at 2° spatial resolution (~200 km); multiple adjacent basins will return identical values." For CDOP correspondence work, LMR anomalies can distinguish broad regional climate periods but not local micro-climate differences between neighboring basins.

**Action**: deferred — 2° spatial resolution ceiling flagged for API documentation; ~200 km precision caveat to be added to API guide


---
## 2026-04-27 · Task 11 · LMR period and event fingerprints

**Method**: `notebooks/edop/explore/11_lmr_periods_volcanics.ipynb` · Reuses 34-cell L8-anchored sample from Task 10 · Period anomalies: PDSI and air temperature for Late Antique (500–700 CE), MCA (950–1250 CE), LIA (1300–1850 CE) relative to three reference windows · Volcanic composite: 5 events ≥20 Tg in reliable window (700–1900 CE), lag-response at individual cells and nhmt/gmt hemisphere means · Location-specific validation: Kaifeng (~35°N, 114°E) and Central Europe (~48°N, 10°E) across the full Song dynasty (960–1280 CE) with Samalas (1257, 59 Tg) close-up

---

### F11.1 — MCA and LIA temperature signals are near the noise floor at global scale; reference choice matters qualitatively

**Finding**: Median air temperature anomaly across the 34-cell global sample:

| Period | vs full record (0–1998) | vs reliable pre-ind (1000–1850) |
|---|---|---|
| MCA (950–1250 CE) | −0.041 K (IQR 0.041) | +0.011 K (IQR 0.054) |
| LIA (1300–1850 CE) | −0.041 K (IQR 0.041) | −0.003 K (IQR 0.017) |

Using the full-record reference, MCA and LIA are statistically indistinguishable — both appear as pre-industrial cooling because the 20th-century industrial warming shifts the 2000-year mean upward, making every pre-1900 period look cool relative to it. Switching to the reliable pre-industrial reference (1000–1850 CE) recovers the correct sign: MCA positive, LIA negative. However, the absolute magnitudes remain marginal — MCA warming of +0.011 K against an IQR of 0.054 K is a direction, not a confident detection.

PDSI shows the expected pattern (MCA slightly wetter, LIA slightly drier) but with similar signal-to-noise limitations globally. The Late Antique period (500–700 CE) shows an artificial positive air temperature anomaly (~+0.016 K, 73% of cells positive) — this is the funnel/regression-to-prior effect (F10.1), not a climate signal.

**Important caveat**: Global-sample analysis systematically understates LMR's utility for the actual API use case. These are median anomalies across tropical, SH, and NH cells combined. MCA and LIA are NH-biased phenomena; averaging over cells where neither anomaly was expressed drives the global median toward zero. Location-specific queries — the API's primary mode — will show stronger regional signals (see F11.5).

**Implication**: Do not report global-sample period anomalies as characterising what a researcher will see at their query location. The global characterisation establishes the noise floor and the reference-choice sensitivity; location-specific queries in the relevant latitude band will yield larger, more interpretable anomalies.

**Action**: deferred — analytical guidance for API documentation and narrative layer; global-sample caveats noted

---

### F11.2 — Reliable pre-industrial (1000–1850 CE) is the recommended baseline convention for Band T anomaly reporting

**Finding**: Three reference windows compared for MCA and LIA anomalies at 34 cells:

- **Full record (0–1998 CE)**: Contaminated by 20th-century industrial warming. Reverses MCA temperature sign (negative instead of positive). Inappropriate for pre-industrial period queries.
- **Reliable pre-industrial (1000–1850 CE)**: Recovers correct sign for both MCA (warm) and LIA (cool). Excludes industrial era and funnel zone. Consistent IQR and predictable behaviour across variables.
- **Surrounding 200yr window**: Self-defeating for MCA (reference overlaps period; anomaly collapses to ~0). Marginally useful for LIA but produces inconsistent PDSI sign (LIA PDSI flips from −0.009 to +0.010 depending on which reference is used), revealing that the global PDSI signal is near zero and heterogeneous regardless.

**Implication**: Reliable pre-industrial (1000–1850 CE) is the standard Band T reference window. This should be documented in the API and applied consistently when reporting period anomalies. Queries in the 0–700 CE window carry the additional funnel caveat (F10.1); the reference window does not resolve that issue.

**Action**: 2026-04-28 — Baseline convention documented via `lmr_fidelity_note` (see F10.1 action). 1000–1850 CE as reliable pre-industrial window noted in API docs / prospectus update (flagged for follow-on task).

---

### F11.3 — LMR volcanic composite is underpowered; Samalas-class events detectable at individual cells but not in hemisphere mean

**Finding**: Composite of 5 events ≥20 Tg in the reliable window (700–1900 CE):

- **nhmt hemisphere mean at lag 0** (eruption year): −0.013 K — within the pre-eruption noise floor of ±0.05 K. No detectable cooling signal.
- **Lag +1**: +0.098 K — warming, not cooling. Consistent with documented dynamic warming response (stratospheric aerosol heating can strengthen winter circulation patterns in the year following large NH eruptions), but with only 5 events the composite is underpowered and this could equally be noise.
- **Individual cells, pooled across 5 events**: median −0.051 K at lag 0 (64% of cells cooler). Modest but directionally correct.
- **Per-event cell plots**: Samalas (59 Tg) shows a clear negative median at lag 0 (~−0.15 K, IQR below zero). Kuwae (33 Tg) shows cooling at lag 0 but a strong lag+1 rebound. Events at 21–24 Tg show no consistent signal.

The apparent detection threshold for individual-basin LMR values is approximately 50+ Tg; below that, inter-annual noise (~±0.3 K per cell) swamps the forced response.

**Implication**: LMR cannot reliably quantify volcanic forcing for the events that make up the bulk of the eVolv2k catalog. The volcanic signal in Band T must come from eVolv2k directly (event count, VSSI, years-since-last-major), not from LMR temperature. These two components are genuinely complementary and non-substitutable: eVolv2k provides the event record; LMR provides the climate-state reconstruction. Users should not expect LMR temperature to confirm what eVolv2k reports. See F11.4 for API design implications.

**Action**: deferred — eVolv2k/LMR decoupling confirmed; analytical guidance for API documentation and narrative layer

---

### F11.4 — eVolv2k and LMR must remain decoupled; Pinatubo scaling is the bridge for non-specialist users

**Finding**: The weak LMR volcanic response reflects known reconstruction limitations, not a scientific misunderstanding of volcanic climate effects. Modern observational evidence is unambiguous: Pinatubo (1991, ~20 Tg) caused ~0.5°C global mean cooling over 1–2 years, measured directly by satellites and surface networks. El Chichón (1982) caused ~0.3°C. By Pinatubo scaling, Tambora (~28 Tg) ≈ 0.7°C and Samalas (~59 Tg) ≈ 1.5°C — effects that were almost certainly catastrophic at the regional scale. LMR attenuates these signals for several compounding reasons: the model prior has no volcanic forcing; tree rings (the dominant proxy type) record growing-season not annual-mean temperature; ensemble mean averaging dampens single-year spikes; and early-medieval proxy networks are sparse in the regions most affected by tropical eruptions.

**Implication**: API design should expose eVolv2k as a standalone catalog component. The narrative layer (LLM prompt) should carry a fixed Pinatubo calibration reference: "Pinatubo (1991) = ~20 Tg → ~0.5°C global cooling over 1–2 years; scale accordingly." This bridges the interpretive gap for non-specialist users who cannot be assumed to have domain knowledge of volcanic climate forcing. Do not imply that LMR temperature values confirm or deny the volcanic signal — state explicitly that they are independent and that LMR's attenuation is a known reconstruction property.

**Action**: deferred — Pinatubo calibration text flagged for narrative layer LLM prompt; eVolv2k standalone status already implemented

---

### F11.5 — At specific NH locations, LMR resolves Samalas cooling and MCA/LIA structure; global-sample findings understate location-specific utility

**Finding**: Kaifeng (~35°N, 114°E) and Central Europe (~48°N, 10°E) cells extracted for the full Song dynasty (960–1280 CE) and the Samalas close-up (1247–1272 CE):

**Samalas response** (relative to 1252–1256 baseline):
- Central Europe 1257: −0.432 K — approximately 4× the pre-eruption inter-annual noise amplitude. A convincing, clearly detectable signal.
- Kaifeng 1257: −0.132 K — within the noise range for that cell (~±0.27 K). However, Kaifeng shows sustained predominantly-negative values from 1260–1264 (−0.241, −0.158, −0.090 K), suggesting a real but delayed and attenuated response. Whether the delay reflects physical differences in regional climate response or sparser East Asian proxy coverage in LMR is not determinable from this test alone.
- Both cells show predominantly negative temperatures from 1257 through at least 1264 — 7+ years of persistent cooling consistent with a Samalas-magnitude event.

**Song dynasty overview**: The Kaifeng cell shows a cooler-than-baseline Northern Song (960–1127), a warm pulse in the mid-Southern Song (~1170–1220 CE) consistent with the MCA, and a cooling trend from ~1230 onward into which Samalas lands. These are features invisible in the 34-cell global median but detectable at specific locations. The two cells diverge throughout the dynasty — they represent genuinely different regional climate trajectories that converge on the post-Samalas cooling. This confirms: location-specific queries are more informative than global-sample characterisation for the actual API use case.

**Implication**: The global-sample noise floor established in F11.1 should not be read as the typical user experience. A researcher querying a NH Temperate location for MCA or LIA will see a directional signal. A researcher querying for the period immediately following Samalas will see cooling at Central European locations; Kaifeng shows a more attenuated and delayed signal. Both cases provide historically meaningful information. The caveat is about magnitude precision, not about whether any signal exists.

**Action**: deferred — analytical guidance for API documentation; location-specific vs global-sample distinction noted for narrative layer

---

### F11.6 — LMR proxy network has a systematic geographic bias that disadvantages East Asian and SH researchers

**Finding**: The stronger and better-timed Samalas signal at Central Europe (−0.432 K in 1257) vs Kaifeng (−0.132 K, delayed) is most parsimoniously explained by proxy network density, not by physical climate differences alone. European paleoclimate proxy networks — dominated by tree rings, ice cores, and documentary records — are far denser than East Asian networks in LMR's assimilation. A well-constrained cell will produce a cleaner, more temporally precise reconstruction of the same forcing. A poorly-constrained cell regresses more toward the prior between proxy constraint points, producing a noisier signal with less precise event timing.

This is not a property unique to LMR — it characterises virtually all multi-proxy paleoclimate reconstructions currently available. The bias is geographic and reflects the history of paleoclimate data collection, which has been concentrated in Europe, North America, and parts of the Pacific. Researchers working on East Asia, South Asia, Africa, and most of the Southern Hemisphere receive a systematically less well-constrained LMR reconstruction than their European counterparts — not because those regions experienced less climate variability, but because fewer proxies from those regions have been incorporated.

**Implication**: This limitation must be explicitly stated in Band T API documentation, not buried in technical notes. A Song dynasty historian using EDOP to query climate at Kaifeng should know that the LMR values there are less precisely constrained than equivalent values for a medieval European site. The within-run spread field (F10.3) does not adequately capture this geographic bias — spread is driven by model dynamics and does not scale with proxy density in a way users can easily interpret. A qualitative disclosure is needed: "LMR reconstruction quality varies by region; coverage is strongest in Europe and North America and weaker in East Asia, South Asia, and the Southern Hemisphere."

**Action**: 2026-04-28 — Added `lmr_proxy_bias_note` to `get_temporal_context()` return dict, present whenever `lmr_available`. Text: "LMR reconstruction quality is strongest for Europe and North America, where proxy records are densest; results for East Asia, South Asia, and the Southern Hemisphere carry greater uncertainty." Rendered as yellow alert in Band T accordion body alongside `lmr_fidelity_note`. `_note` on bands A–E upgraded to list to support multiple notes per band going forward.

---
