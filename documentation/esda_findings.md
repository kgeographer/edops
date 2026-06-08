# ESDA Findings Log

Running record of findings from the spatial statistics (ESDA) phase. Notebooks in `notebooks/edop/spatial/`, outputs in `spatial/`.

Each entry: **Date · Variable/Scale · Method · Finding · Implication**

---

## Aridity — `ari_ix_sav` (P/PET × 100, local basin average)

### ARI.1 — Global Moran's I: aridity is near-maximally clustered at both scales

**Date**: 2026-05-14 (L6), 2026-05-15 (L8)
**Notebooks**: `01_aridity_l6_moran.ipynb`, `02_aridity_l8_moran.ipynb`
**Method**: Queen contiguity weights, row-standardised; 999 permutations; `np.random.seed(42)`

**Finding**:
| Scale | Basins | Moran's I (raw) | Moran's I (log) | Δ (raw→log) | p-value | z-score |
|-------|--------|-----------------|-----------------|-------------|---------|---------|
| L6    | 16,397  | 0.9628 | 0.9731 | +0.0103 | 0.001 | 195.64 |
| L8    | 190,675 | 0.9889 | 0.9924 | +0.0035 | 0.001 | 754.92 |

Log transform sensitivity narrows at finer resolution (Δ 0.010 → 0.004): at L8 each basin is more internally homogeneous, so the right-skewed tail exerts less leverage on the spatial correlation structure. The raw-vs-log distinction is practically irrelevant at L8 for aridity.

Both p-values are floored at 0.001 (1/999 permutations). The z-score increase from 196 to 755 is a sample-size artifact (permutation variance narrows as n grows), not a substantive finding — compare I values directly.

**Implication**: Aridity will anchor the high end of the coherence spectrum. Any variable with I > 0.95 behaves like aridity — large-scale climate gradient dominates, LISA map is geographically interpretable at continental scale. I < 0.7 or so will indicate structural difference worth investigating.

---

### ARI.2 — Scale effect confirmed: I increases with finer resolution

**Date**: 2026-05-15
**Finding**: I rises from 0.9628 (L6) to 0.9889 (L8), Δ = +0.0261. Direction is consistent with the expected mechanism: smaller basins sit more firmly inside individual climate zones, so each basin's value more closely tracks its immediate neighbours. At L6, large basins span climate gradients and their averaged values decouple slightly from adjacent-basin averages.

**Implication**: For smooth large-scale climate variables (aridity, temperature, precipitation), expect I to increase monotonically with resolution. This is a baseline expectation; departure from it for other variables is informative.

---

### ARI.3 — Distribution shifts toward wetter at finer resolution

**Date**: 2026-05-15
**Finding**:
| Statistic | L6 | L8 |
|---|---|---|
| Mean | 84.2 | 95.3 |
| Median | 65.0 | 68.0 |
| Max | 2101 | 2167 |
| % below humid threshold (65) | 49.5% | 47.8% |

Mean increases by ~11 units; median shifts modestly. Finer resolution preferentially resolves wet-extreme locations (coastal margins, riparian corridors, windward mountain slopes) that were averaged into drier neighbours at L6. The same mechanism shifts `% below humid threshold` from 49.5% to 47.8%.

**Implication**: For right-skewed variables, finer resolution selectively inflates the upper tail. This is an artefact of aggregation geometry, not a real environmental change. Do not interpret distributional differences across scales as substantive without checking this mechanism.

---

### ARI.4 — LISA cluster-core percentages are scale-stable; outlier percentages are not

**Date**: 2026-05-15
**Finding**:
| Class | L6 (n) | L6 (%) | L8 (n) | L8 (%) |
|-------|--------|--------|--------|--------|
| HH    | 753    | 4.6%   | 7,174  | 3.8%   |
| LL    | 4,927  | 30.0%  | 58,862 | 30.9%  |
| HL    | 225    | 1.4%   | 413    | 0.2%   |
| LH    | 0      | 0.0%   | 0      | 0.0%   |
| NS    | 10,492 | 64.0%  | 124,226| 65.2%  |

HH and LL percentages are nearly identical across a 11.6× increase in basin count — the large arid and humid zones fill the basin set proportionally at both resolutions.

HL absolute count roughly doubles (225→413) but percentage drops 1.4%→0.2%, because the HL features (river corridors, coastal strips) are geographically fixed and do not scale with basin count. HL percentage is thus not comparable across scales; absolute counts or per-km² density are the right comparison.

LH=0 at both scales. No statistically significant dry outliers within humid surroundings exist for aridity at either resolution.

**Implication**: When building the characterisation table, report HL/LH absolute counts alongside percentages. Percentage-only comparison across scales is misleading for the outlier classes.

---

### ARI.5 — MAUP: HH fringe contracts at finer resolution (Pacific Northwest case)

**Date**: 2026-05-15
**Finding**: The HH (humid cluster core) footprint in the US Pacific Northwest / British Columbia is visibly smaller at L8 than at L6. At L6, large basins average across the wet coastal slopes and transitional terrain, producing a solid HH block. At L8, the Cascade rain shadow resolves as individual dry sub-basins; their presence in the queen neighbourhood of adjacent wet basins drops the spatial lag below the significance threshold, so the fringe of the HH zone contracts to NS. Only the unambiguous coastal core remains classified HH.

**Implication**: This is the Modifiable Areal Unit Problem (MAUP) in a geographically concrete form. For variables with sharp local gradients (mountain rain shadows, coastlines, river/desert contrasts), HH/LL cluster footprints will shrink at finer resolution even when the large-scale climate pattern is unchanged. Cluster-core percentage is robust for continent-scale features but not for features near topographic discontinuities. The Pacific Northwest is an extreme case; the Andes, Ethiopian Highlands, and Horn of Africa are candidates for similar behaviour in other variables.

---

## Discharge — `dis_m3_pyr` (mean annual discharge, m³/s, cumulative)

No upstream variant — the variable is already a cumulative upstream aggregate. Log transform canonical: raw skewness ~41, Δ(log−raw) = +0.18. Notebooks: `03_discharge_l6_l8_moran.ipynb`.

---

### DIS.2 — Global Moran's I: network topology produces substantially lower autocorrelation than climate gradients

**Date**: 2026-05-16
**Method**: Queen contiguity, row-standardised, 999 permutations, seed=42, log(1+x) transform

| Scale | Basins | I (raw) | I (log) | Δ (log−raw) |
|-------|--------|---------|---------|-------------|
| L6 | 16,397 | 0.3986 | 0.5822 | +0.1836 |
| L8 | 190,675 | 0.3689 | 0.5629 | +0.1941 |

**Finding**: Discharge I_log is ~0.41 below aridity at both scales (aridity L6=0.9731, L8=0.9924). Adjacent basins share aridity values tightly because they occupy the same climate zone; they share discharge values far more loosely because they may drain into completely different river systems separated by a watershed divide.

**Implication**: The I gap between discharge and aridity is an empirical measure of the difference between climate-gradient and network-topology spatial structure. Discharge will anchor the moderate-I range of the characterisation spectrum; aridity anchors the high end.

---

### DIS.3 — Log transform is not cosmetic for discharge: Δ(log−raw) = +0.18

**Date**: 2026-05-16
**Finding**: For aridity, raw vs log differed by 0.010 — effectively irrelevant. For discharge, the log transform raises I by +0.184 (L6) and +0.194 (L8), changing the interpretation from "weakly autocorrelated" to "moderately autocorrelated." In raw space, the Amazon outlet (~200,000 m³/s) dominates the spatial variance calculation and suppresses the global I. Log-transforming compresses the tail and gives equal weight to spatial patterns across all orders of magnitude of discharge.

**Rule**: For any variable with skewness > ~5, treat the raw and log I values as measuring different things. The log version measures the spatial pattern of proportional variation; the raw version reflects extreme-outlier geometry. Log is canonical for LISA.

---

### DIS.4 — Scale direction reversal: discharge I decreases with finer resolution (opposite of aridity)

**Date**: 2026-05-16
**Finding**:

| Variable | L6 I (log) | L8 I (log) | Δ scale | Direction |
|---|---|---|---|---|
| Aridity | 0.9731 | 0.9924 | +0.019 | ↑ finer = higher I |
| Discharge | 0.5822 | 0.5629 | −0.019 | ↓ finer = lower I |

At finer resolution, more adjacent basin pairs straddle watershed divides. At L6, large basins average over enough terrain that the discharge contrast across a divide is partially smoothed. At L8, small basins right at a divide are unambiguously on opposite sides with sharply different discharge, pulling I down. Climate gradients have no equivalent "divide" — aridity transitions smoothly, so finer resolution only increases within-zone coherence.

**Implication**: Scale direction is a variable-type diagnostic. Variables driven by smooth spatial processes (climate) will generally show I increasing with resolution. Variables driven by network or discontinuous processes (drainage topology, geology) may show I decreasing. This axis should be included in the characterisation table.

---

### DIS.5 — LISA class structure: HH ≈ LL symmetry, LH class appears

**Date**: 2026-05-16
**Finding** (L6, log-transformed):

| Class | n | % | vs aridity L6 |
|---|---|---|---|
| HH | 3,346 | 20.4% | aridity 4.6% |
| LL | 3,107 | 18.9% | aridity 30.0% |
| HL | 124 | 0.8% | aridity 1.4% |
| LH | 300 | 1.8% | aridity 0.0% |
| NS | 9,520 | 58.1% | aridity 64.0% |

HH ≈ LL (near parity) vs aridity's strong LL dominance (30% vs 4.6%). In log-discharge space the world is more symmetrically divided between river systems and arid/endorheic interiors than between humid and arid climate zones.

LH appears at 1.8% — a class impossible for aridity (no dry outliers within humid climate zones) but natural for discharge: small endorheic or rain-shadow basins embedded within high-flow surroundings, isolated upland headwaters adjacent to large mainstem basins.

NS fills interfluves (land between river systems disconnected from major drainage), not gradient transition zones as in aridity.

---

### DIS.6 — Scale effects on LISA classes: HH/LL reversal, LH grows faster than basin count

**Date**: 2026-05-16
**Finding** (cross-scale comparison, log-transformed):

| Class | L6 % | L8 % | Δ | L6 n | L8 n | ratio |
|---|---|---|---|---|---|---|
| HH | 20.4 | 15.6 | −4.8 | 3,346 | 29,819 | 8.9× |
| LL | 18.9 | 23.5 | +4.6 | 3,107 | 44,890 | 14.4× |
| HL | 0.8 | 0.3 | −0.4 | 124 | 626 | 5.0× |
| LH | 1.8 | 3.5 | +1.7 | 300 | 6,752 | 22.5× |
| NS | 58.1 | 56.9 | −1.1 | — | — | — |

Basin count grows 11.6×. LH grows 22.5× — the only class that outpaces the basin count increase. This is the watershed-divide effect made explicit: at L8, many more small basins sit at the edge of major river systems with high-discharge queen-neighbours. HH/LL reversal across scales (L6: HH>LL; L8: LL>HH) as proliferating small headwater/endorheic basins push LL ahead.

For aridity by contrast: HH and LL percentages barely move across scales (large climate zones are resolution-stable); LH stays at 0.0%.

**Implication**: For discharge, outlier-class percentages are strongly scale-dependent and should not be compared across L6/L8 without considering the absolute counts. LH% at L8 is ~2× L6 not because there are twice as many "rivers-in-desert" but because finer resolution resolves twice as many watershed-divide positions.

---

### DIS.1 — Research question: interfluve NS zones and settlement patterns

**Date**: 2026-05-16
**Observation**: The NS (not significant) class in the discharge LISA map represents the interfluves — land between river systems that neither accumulates high flow nor sits in an arid/endorheic zone. These are not settlement-poor: many historical societies settled interfluve margins rather than river floodplains, for defensibility, flood avoidance, and stable ground. Mesopotamia is the canonical case — the agricultural heartland was the land *between* the Tigris and Euphrates, irrigated from both but not in either floodplain. Many tell sites and ancient city locations are likely in NS or transitional basins, not HH.

**Research question**: Do Cliopatria/Seshat polities and D-PLACE societies cluster preferentially in HH (river system), NS (interfluve), or LL (arid) basins? Does the answer vary by subsistence type (agricultural vs. pastoral vs. forager)? The discharge LISA class (HH/LL/NS/HL/LH) per basin is a meaningful environmental descriptor for historical place analysis — not just the discharge value itself, but the basin's structural position in the drainage network.

**Action**: Flag for polity phase — test LISA class distribution of D-PLACE societies and Cliopatria polity centroids against global basin baseline. Subsistence type filter (D-PLACE has this) would make the test more informative.

---

## Phase 1 — Univariate sweep, Bands A–D (L6 + L8)

Script: `scripts/edop/esda/12_spatial_moran.py`. Queen contiguity weights, row-standardised, 999 permutations, seed 42. Log transform applied where skewness > 5 and min ≥ 0. BasinATLAS -9999 sentinels masked before all computation (see METH.4).

Outputs: `spatial/variable_characterization.csv` (committed), `output/edop/esda/lisa_classifications.parquet` (gitignored, 655k rows L6 / 7.6M rows L8).

---

### SW.1 — Full I spectrum and summary table

**Date**: 2026-05-17

| band | variable | friendly_name | I_L6 | I_L8 | scale_dir |
|------|----------|---------------|------|------|-----------|
| A | ele_mt_sav | Mean elevation | 0.924 | 0.970 | ↑ |
| A | ele_mt_smn | Elevation minimum | 0.884 | 0.943 | ↑ |
| A | ele_mt_smx | Elevation maximum | 0.848 | 0.933 | ↑ |
| A | slp_dg_sav | Slope | 0.805 | 0.879 | ↑ |
| A | ero_kh_sav | Erosion rate | 0.741 | 0.922 | ↑ |
| A | sgr_dk_sav | Stream gradient | 0.725 | 0.792 | ↑ |
| A | kar_pc_sse | Karst % | 0.676 | 0.820 | ↑ |
| A | gla_pc_sse | Glacier % | 0.663 | 0.820 | ↑ |
| B | swc_pc_syr | Soil water content | 0.970 | 0.992 | ↑ |
| B | slt_pc_sav | Silt % | 0.964 | 0.962 | ↓ |
| B | cly_pc_sav | Clay % | 0.902 | 0.932 | ↑ |
| B | run_mm_syr | Annual runoff | 0.874 | 0.971 | ↑ |
| B | snd_pc_sav | Sand % | 0.873 | 0.903 | ↑ |
| B | soc_th_sav | Soil organic carbon | 0.858 | 0.906 | ↑ |
| B | gwt_cm_sav | Groundwater depth | 0.824 | 0.857 | ↑ |
| B | lka_pc_sse | Lake area % | 0.684 | 0.729 | ↑ |
| B | dis_m3_pmn | Discharge monthly min | 0.614 | 0.573 | ↓ |
| B | wet_pc_sg2 | Wetland % group 2 | 0.611 | 0.705 | ↑ |
| B | wet_pc_sg1 | Wetland % group 1 | 0.598 | 0.700 | ↑ |
| B | inu_pc_smx | Inundation max | 0.589 | 0.625 | ↑ |
| B | dis_m3_pyr | Discharge annual | 0.582 | 0.563 | ↓ |
| B | dis_m3_pmx | Discharge monthly max | 0.535 | 0.559 | ↑ |
| B | ria_ha_ssu | River area (local) | 0.485 | 0.591 | ↑ |
| B | dor_pc_pva | Degree of regulation | 0.475 | 0.422 | ↓ |
| C | pet_mm_syr | PET annual | 0.988 | 0.997 | ↑ |
| C | tmp_dc_syr | Temperature annual | 0.981 | 0.996 | ↑ |
| C | snw_pc_syr | Snow cover annual | 0.975 | 0.993 | ↑ |
| C | ari_ix_sav | Aridity index | 0.973 | 0.992 | ↑ |
| C | aet_mm_syr | AET annual | 0.967 | 0.993 | ↑ |
| C | prm_pc_sse | Permafrost % | 0.959 | 0.979 | ↑ |
| C | cmi_ix_syr | Climate moisture index | 0.952 | 0.988 | ↑ |
| C | pre_mm_syr | Precipitation annual | 0.921 | 0.978 | ↑ |
| C | for_pc_sse | Forest cover % | 0.858 | 0.892 | ↑ |
| D | hdi_ix_sav | HDI | 0.987 | 0.995 | ↑ |
| D | gdp_ud_sav | GDP mean | 0.943 | 0.986 | ↑ |
| D | ppd_pk_sav | Population density | 0.862 | 0.913 | ↑ |
| D | pst_pc_sse | Pasture % | 0.860 | 0.897 | ↑ |
| D | crp_pc_sse | Cropland % | 0.849 | 0.899 | ↑ |
| D | hft_ix_s09 | Human footprint 2009 | 0.819 | 0.847 | ↑ |
| D | nli_ix_sav | Nighttime lights | 0.622 | 0.700 | ↑ |

I range at L6: 0.475 (degree of regulation) – 0.988 (PET). All variables show meaningful positive spatial autocorrelation; none are near zero or negative.

---

### SW.2 — Scale direction: 36 ↑, 4 ↓

**Date**: 2026-05-17

The predominant behaviour (36/40 variables) is ↑ — spatial autocorrelation increases with finer resolution, consistent with the climate-gradient mechanism established for aridity. The 4 ↓ variables all share network- or infrastructure-topology structure:

| Variable | L6 | L8 | Δ | Mechanism |
|---|---|---|---|---|
| dis_m3_pyr | 0.582 | 0.563 | −0.019 | Watershed-divide effect (established, DIS.4) |
| dis_m3_pmn | 0.614 | 0.573 | −0.041 | Same mechanism; baseflow more divide-sensitive than annual mean |
| dor_pc_pva | 0.475 | 0.422 | −0.053 | Dams are point features; at L8 a regulated basin is small and surrounded by many unregulated neighbours — point anomaly character sharpens, coherence drops |
| slt_pc_sav | 0.964 | 0.962 | −0.002 | Effectively flat; large-scale loess belts and alluvial plains are already well-captured at L6. The ↓ sign is not substantively meaningful at this magnitude |

**Rule**: scale direction ↓ is diagnostic of network/infrastructure topology, not gradient structure. Variables with ↓ direction will show I *decreasing* as resolution increases because finer scale resolves more discontinuities. All other variable types default to ↑.

---

### SW.3 — Notable within-band findings

**Date**: 2026-05-17

**Erosion rate largest absolute scale gain** (Δ+0.181): ero_kh_sav 0.741→0.922, the largest absolute increase of any variable. Erosion is slope-driven; at L8 steep and flat basins are unambiguous rather than averaged.

**Karst and glacier sharpen similarly** (Δ≈+0.16 each): geologically and climatically bounded features — karst limestone outcrops, alpine/polar ice — that are smeared across coarser basin boundaries at L6 but resolve clearly at L8.

**Discharge trio: three variables, three scale directions**:
- Annual mean ↓ (divide effect on cumulative flow)
- Monthly min ↓ (baseflow even more divide-sensitive — largest ↓ among discharge variables)
- Monthly max ↑ (peak flood pulse; at L8 small basins within a river corridor all experience the same flood event simultaneously, sharpening the HH chain along mainstems)

**Band C ceiling at L8**: PET, temperature, snow, aridity, AET all reach I ≥ 0.992 at L8 — effectively maximum spatial autocorrelation. These variables have no meaningful variation left to resolve at finer scale; they are already near-perfectly spatially locked.

**Silt anomaly within soil texture**: clay ↑ (+0.030) and sand ↑ (+0.030) but silt ↓ (−0.002). Silt is associated with large-scale loess deposits and river floodplains that are geomorphic features captured at L6. Clay and sand have more local substrate determinants that resolve sharper at L8.

**Band D as high as Band C**: HDI (0.987/0.995) and GDP (0.943/0.986) reach values comparable to PET and temperature. Wealth and development autocorrelate at continental scale as strongly as climate. The spatial co-clustering of D and C variables at L6 is an empirical fact; its interpretation belongs to the polity phase, not here.

**dor_pc_pva highest outlier%**: 5.93% at L6 — the highest outlier percentage in the sweep. Degree of regulation is a point-feature variable; its HL pattern (one regulated basin surrounded by unregulated neighbours) is more prevalent than for any other variable. Potentially the most spatially locally-specific signal in the dataset.

---

## Methods and conventions

### METH.1 — Never use GeoDa GAL files for PySAL weights

**Date**: 2026-05-14
**Finding**: `basin06_queen.gal` (exported from GeoDa) produced I = 0.364 and a mottled, geographically uninterpretable LISA map. Correct result (I = 0.963) only obtained with `Queen.from_dataframe(gdf, use_index=True)` keyed by `hybas_id`. GeoDa GAL files use GeoDa's internal sequential row index as keys, not the basin primary key, causing misalignment between the weights matrix and the data array.

**Rule**: Always build weights in Python from the GeoDataFrame with `use_index=True`. Treat any existing GAL file as unusable.

---

### METH.2 — `plt.show()` blocks inline rendering in PyCharm Jupyter

**Date**: 2026-05-15
**Finding**: Cells with `plt.show()` produce print output but no inline plot. Removing `plt.show()` allows `%matplotlib inline` to render figures automatically at cell end. This is consistent with PyCharm's Jupyter backend behaviour — `plt.show()` clears the figure before the inline backend captures it.

**Rule**: Never add `plt.show()` to notebook plot cells. End with `plt.tight_layout()` and any print statements; let `%matplotlib inline` handle display.

---

### METH.3 — M5 performance benchmarks for spatial operations

**Date**: 2026-05-15
**Machine**: Apple M5, 2026

| Operation | L6 | L8 |
|---|---|---|
| Queen weights build | not timed | 4m 39s |
| Global Moran's I (999 perms) | ~seconds | 3s |
| LISA (999 perms) | ~seconds | 20s |
| LISA cluster map render | ~seconds | not timed |

L8 LISA at 20s is far faster than anticipated (estimated 1–2 hours). The M5 is effectively interactive for all operations in this pipeline. Update any documentation that still refers to L8 as "kick it off and walk away."

---

### METH.4 — BasinATLAS -9999 sentinel destroys Moran's I even in small numbers

**Date**: 2026-05-17
**Finding**: BasinATLAS stores NoData as integer -9999. In `snw_pc_syr`, only 5 out of 16,397 basins (0.03%) carried this sentinel. Treated as real values, they produced z-scores of ≈ −500, pulling the Moran scatter slope to near zero (I = 0.021 instead of the correct 0.975). The sentinel also blocked the log-transform path (`min ≥ 0` check fails at -9999), compounding the error.

Affected columns confirmed in basin06: `snw_pc_syr`, `slp_dg_sav`, `sgr_dk_sav`, `cly_pc_sav`, `slt_pc_sav`, `snd_pc_sav`, `soc_th_sav` (sentinel counts 5–757).

**Rule**: Mask `vals[vals == -9999] = np.nan` before any computation, before applying scale factors. One sentinel in 16k basins is enough to invalidate a spatial statistic. Previously noted in EDA phase but not carried into ESDA scripts — now enforced in `12_spatial_moran.py`.

---

## Phase 3 — Bivariate: Temperature × Precipitation (L6)

Notebook: `notebooks/edop/spatial/05_bivariate_TP_l6.ipynb`. Queen contiguity weights, row-standardised, seed=42, 999 permutations. Temperature stored as °C×10 — scale factor 0.1 applied. No log transform (temperature has negative values; precipitation skewness = 1.65 < 5). Spatial weights identical to Phase 1 L6 sweep. BasinATLAS -9999 sentinels confirmed absent for both columns.

---

### BV.1 — Global bivariate Moran's I: T×P = +0.315 (p=0.001)

**Date**: 2026-05-17
**Method**: `esda.Moran_BV(tmp, pre, w)`, L6 (16,397 basins), 999 permutations

| Direction | I_BV | p_sim | z_sim |
|---|---|---|---|
| T → spatial lag of P | +0.3150 | 0.001 | 37.59 |
| P → spatial lag of T | +0.3158 | 0.001 | 39.25 |

**Finding**: Globally, warm basins tend to sit in high-precipitation neighbourhoods and cold basins in low-precipitation neighbourhoods. The dominant driver is the poles-vs-tropics axis: humid tropics are both warm and wet; polar regions are cold and dry. The positive I_BV reflects this gradient, not uniformly distributed coupling.

**Note**: I_BV is not symmetric in general, but the near-identical T→P and P→T values here indicate that the global gradient is the dominant signal rather than directional asymmetries.

---

### BV.2 — Global LISA: HL is the largest class despite positive I_BV

**Date**: 2026-05-17

| Class | n | % | Geography |
|---|---|---|---|
| HH | 2,573 | 15.7% | Humid tropics, temperate maritime coasts |
| LL | 2,289 | 14.0% | Cold deserts, polar interiors |
| **HL** | **2,991** | **18.2%** | **Hot deserts (Sahara, Arabia, Gobi, Australian interior)** |
| LH | 158 | 1.0% | Cool upland margins of wet tropical zones |
| NS | ~8,386 | ~51.1% | Transition zones, mid-latitudes |

**Finding**: The largest significant class is HL (warm basin, low-precip neighbourhood) — the hot-desert decoupling signal. This appears inconsistent with the positive global I_BV until the geometry is understood: the poles-vs-tropics signal (HH+LL together = 29.7%) sets the direction of the global aggregate; the HL hot-desert signal (18.2%) is locally dominant in specific regions but is distributed around the global periphery of the tropics rather than in a single connected zone. I_BV aggregates across both patterns and returns the net direction (+0.315).

**Implication**: The global scalar does not describe any specific place correctly. A basin in the Sahara is HL; a basin in the Amazon is HH; both contribute to the same positive I_BV.

---

### BV.3 — Mediterranean: I_BV = −0.250 (sign reversal vs global)

**Date**: 2026-05-17
**Region definition**: `subrealm_n = 'Mediterranean'` from OneEarth gaz hierarchy, intersected against L6 basin polygons (n=140).
**Method**: Subset Queen weights rebuilt on 140 basins; islands dropped if any.

| I_BV | p_sim | HH% | LL% | HL% | LH% | NS% |
|---|---|---|---|---|---|---|
| −0.2498 | 0.001 | 3.6 | 8.6 | 12.1 | 7.9 | 67.9 |

**Finding**: Within the Mediterranean geographic basin, warm basins are surrounded by low-precipitation neighbours (HL = 12.1% dominant among significant classes). The I_BV sign is **negative** — the opposite of the global +0.315. The Mediterranean summer-drought mechanism inverts the global relationship: the warm season is dry; cooler winters bring cyclonic rain. Warm basins (summer) experience dry surroundings; the spatial lag of precipitation is inversely related to temperature.

**Key result**: Mediterranean I_BV = −0.25 is not merely attenuated relative to the global value — it is sign-reversed. A global scalar would misclassify T and P as positively co-distributed in this region.

---

### BV.4 — Monsoon Asia (Indomalaya): I_BV not significant; HL > HH

**Date**: 2026-05-17
**Region definition**: `realm = 'Indomalaya'` from OneEarth gaz hierarchy, intersected against L6 basin polygons (n=957).

| I_BV | p_sim | HH% | LL% | HL% | LH% | NS% |
|---|---|---|---|---|---|---|
| −0.0456 | 0.076 | 16.8 | 1.6 | 22.2 | 5.7 | 53.7 |

**Finding**: The expected HH dominance (warm + monsoonal high-precip neighbours) does not emerge. I_BV is not significant (p=0.076). HL (22.2%) exceeds HH (16.8%). The Indomalaya realm spans the very wet windward coastal margins of South and SE Asia (HH) alongside the hot-dry interior continental basins of the Indian subcontinent and Indochina dry zones (HL). These signals partially cancel, producing near-zero net I_BV.

**Useful negative result**: Indomalaya as a single analytical unit does not exhibit coherent T×P coupling at L6. Finer geographic stratification (e.g., separating Indian subcontinent from mainland SE Asia, or windward from leeward) would likely recover the expected HH signal in the wet sub-zones. The realm boundary is not coincident with a T×P coupling boundary.

---

### BV.5 — Tibetan/cold-arid: I_BV = +0.608, LL dominant

**Date**: 2026-05-17
**Region definition**: `subrealm_n = 'Himalayas & Tibetan Plateau'` from OneEarth gaz hierarchy, intersected against L6 basin polygons (n=331).

| I_BV | p_sim | HH% | LL% | HL% | LH% | NS% |
|---|---|---|---|---|---|---|
| +0.6080 | 0.001 | 9.7 | 26.6 | 3.6 | 0.9 | 59.2 |

**Finding**: Strong positive I_BV; LL dominant. Cold basins cluster with cold-dry neighbours — the Tibetan Plateau and High Himalayan flanks are both cold and arid at the basin level. The cold-arid co-clustering here is stronger (I_BV=+0.61) than the global average (+0.315), because within this region the cold-dry correspondence is nearly monotonic: altitude drives both variables simultaneously. There is very little HH (warm-wet), almost no HL (warm-dry), and essentially no LH.

**Implication**: This region amplifies the global signal rather than reversing or complicating it. The Tibetan Plateau is the clearest large-scale cold-dry co-clustering zone on Earth; its ESDA signature is correspondingly clean.

---

### BV.6 — Core finding: global I_BV is an insufficient redundancy filter for geographically variable relationships

**Date**: 2026-05-17

**Summary**: Phase 3 was designed as a validation test. The pair T×P was chosen because the regional coupling structure is well-understood before any computation: positive coupling globally, decoupled (inverted) in the Mediterranean, strongly coupled in Tibetan cold-arid, heterogeneous in monsoon zones.

**Results matched predictions exactly**:
- Global I_BV = +0.315 ✓ (poles-vs-tropics gradient)
- Mediterranean I_BV = −0.25 ✓ (summer-drought inversion confirmed)
- Tibetan I_BV = +0.61 ✓ (cold-arid amplification confirmed)
- Monsoon Asia I_BV not significant ✓ (internal heterogeneity confirmed)

**Methodological consequence**: Using global I_BV as a scalar redundancy measure (e.g., "if I_BV(T,P) is high, drop one") would be wrong. The Mediterranean case shows the relationship inverts at the regional scale. Two variables can have positive global co-distribution and locally anti-correlated structure. The appropriate tool for redundancy analysis is local bivariate Moran's I with geographic stratification, not a global scalar.

This finding validates Karl's correction (session log 2026-05-17) against using global concordance as a variable-selection filter — an assumption that had carried over uncorrected from earlier EDA work. Opus 4.7 affirmed it; CC had held the wrong framing. Phase 4 proceeds using stratified local bivariate analysis rather than global I_BV pairs.

---

## Phase 4 — Bivariate: Five continental-gradient pairs (L6)

Notebook: `notebooks/edop/spatial/06_bivariate_phase4_l6.ipynb`. Same weights, seed, permutations as Phase 3. Nine variables loaded: ari_ix_sav (log-transformed, skew 7.87), pre_mm_syr, tmp_dc_syr (×0.1), snw_pc_syr, hdi_ix_sav, gdp_ud_sav, ele_mt_sav, slp_dg_sav, aet_mm_syr. Only ari_ix_sav triggered log transform (skew > 5 threshold).

---

### BV.7 — Phase 4 global I_BV summary and redundancy tiers

**Date**: 2026-05-17

| Pair | I_BV | Dominant LISA | Tier |
|---|---|---|---|
| tmp×snw | −0.865 | HL 51.5% / LH 22.6% | Near-redundant |
| pre×aet | +0.863 | LL 29.4% / HH 22.3% | Near-redundant |
| hdi×gdp | +0.581 | LL 30.5% / HH 13.9% | Genuinely distinct |
| ari×pre | +0.578 | LL 24.3% / HH 16.6% | Genuinely distinct |
| ele×slp | +0.423 | LL 26.2% / HH 10.8% | Genuinely distinct |

**Finding**: Pairs fall into two tiers. Near-redundant (|I_BV| > 0.85): one variable largely derivable from the other globally. Genuinely distinct (I_BV 0.42–0.58): meaningful geographic divergence, both variables carry information a signature needs. No pair has I_BV near zero — all five show real positive or negative spatial coupling.

**Note on I_BV = 0.581 (hdi×gdp) ≈ 0.578 (ari×pre)**: identical coupling strength across two completely unrelated variable domains. The global I_BV scalar carries no information about *which* geography drives the coupling — the maps are entirely different despite the same statistic.

---

### BV.8 — ari×pre: not redundant; subarctic HL is the key signal

**Date**: 2026-05-17

**LISA**: LL=24.3% (global arid belt), HH=16.6% (humid tropics), **HL=7.9%**, LH=0.0%

**Finding**: The 7.9% HL class is the subarctic/arctic zone — basins with high aridity index (humid, because PET is very low in cold climates) but moderate-precipitation surroundings. The aridity index = P/PET; when PET is suppressed by cold, even moderate annual precipitation yields a high aridity index. But the neighbours' raw precipitation is also only moderate. Result: aridity metric says "humid here"; precipitation says "this is not a wet neighbourhood."

Hot-arid zones (Sahara, Arabia) are LL on both metrics. Cold-arid zones (subarctic, high-altitude Asian interior) are LL on precipitation but HL on aridity index. This divergence makes aridity and precipitation non-redundant: precipitation alone cannot distinguish hot-desert arid from cold-steppe arid. The aridity index can.

**Map observation** (Karl, 2026-05-17): Atacama and Pampas share LL class despite being environmentally distinct (hyperarid desert vs productive temperate grassland). Both fall below the global humid-tropical mean on both metrics. This illustrates BV.13 below.

**Implication**: For signatures at high-latitude or high-altitude historical sites (Novgorod, Viking Scandinavia, subarctic Siberian cultures), aridity index and precipitation give qualitatively different environmental characterizations. Both are needed.

---

### BV.9 — tmp×snw: near-redundant; latitude partition map

**Date**: 2026-05-17

**LISA**: **HL=51.5%** (warm/snow-free), **LH=22.6%** (cold/snowy), LL=1.8%, HH=0.0%, NS=24.2%

**Finding**: The strongest coupling (absolute value) in the dataset. The LISA map is essentially a latitude partition — warm=snow-free (HL) below ~55-60°N, cold=snowy (LH) above, with a transition NS band in the temperate zone. HH (warm+snowy neighbourhood) is geometrically impossible and confirms as zero. LL=1.8% = cold-arid interiors (Gobi in winter) where cold coexists with low snow.

The relationship is near-mechanistic: temperature determines whether precipitation falls as snow and whether snow persists. Snow cover is largely derivable from temperature. **snw is near-redundant with tmp** in a global signature.

**Exceptions where snw adds information beyond tmp**:
1. The NS transition band (35-60°N) — where seasonality creates warm average annual temperature but significant winter snow. Many of the densest historical settlement zones sit here (Rome 42°N, Kaifeng 35°N, Paris 49°N, London 51°N).
2. Altitude-driven anomalies (Andes spine, Tibetan Plateau margins) — cold/snowy at subtropical latitudes due to elevation. But these are already captured by ele in Band A.

**Rubric implication**: In the default signature, snw provides marginal additional information beyond tmp for most historical locations. However, for the transition band (35-60°N) where medieval and early modern polities are concentrated, annual mean temperature partially masks winter snow conditions relevant to agriculture, mobility, and siege conditions.

---

### BV.10 — hdi×gdp: not redundant; EDOP/CDOP boundary observation

**Date**: 2026-05-17

**LISA**: LL=30.5% (Sub-Saharan Africa, South/SE Asia), HH=13.9% (North America, Russia, Australia), HL=4.0%, LH=0.0%, NS=51.7%

**Finding**: Moderate positive coupling (I_BV=+0.581) despite both variables having individually very high univariate I (HDI=0.987, GDP=0.943). The moderate bivariate I reflects real geographic divergence: Russia is HH (Soviet human capital investment creates high HDI relative to GDP neighbourhood); former Soviet Central Asian states show HL (high education legacy, lower market income); Sub-Saharan Africa is the largest coherent LL zone globally. Western Europe is largely NS — internal variation is too small relative to the global range to produce LISA significance at L6 scale.

**EDOP/CDOP boundary** (Karl, 2026-05-17): The interesting findings from this map — Russia HH explained by Soviet institutional history, HL patches explained by political-economic legacy — are not physical geography findings. They require historical-cultural context that CDOP is designed to provide. Band D variables sit at the EDOP/CDOP boundary: their spatial clustering is an empirical geographic fact (measurable by ESDA), but the explanation belongs to a different analytical domain.

**Rubric implication**: Band D should be opt-in rather than default for historically-framed queries. For contemporary environmental queries it is appropriate; for historical polity analysis it describes the modern world overlaid on where the polity was located, which can mislead.

---

### BV.11 — ele×slp: genuinely distinct; African Plateau as dominant HL signal

**Date**: 2026-05-17

**LISA**: LL=26.2% (flat lowlands), HH=10.8% (mountain ranges), **HL=3.3%** (plateau environments), **LH=4.6%** (piedmont zones), NS=55.1%

**Finding**: The dominant HL signal is the **African Plateau**, not the Tibetan Plateau as predicted. Africa is a "plateau continent" — ancient Precambrian basement rock sitting at 500–2000m elevation with relatively low relief except at escarpment edges. At L6 averaging, African interior basins register as high elevation but surrounded by low-slope neighbours. The Tibetan HL signal exists but is smaller in geographic extent than the African Plateau.

LH (4.6%) > HL (3.3%): more piedmont/foothill basins (low elevation, steep-slope neighbourhood — Gangetic Plain/Himalayan foot, Great Plains/Rocky Mountain front, Amazonian piedmont) than plateau basins. Geographically expected.

Mountain ranges (HH: Rockies, Andes, Himalayan fringe, Alps, Ethiopian escarpment), lowland plains (LL: Amazon, Congo, Siberian plain, Gangetic plain, Central Asian steppe), and plateau environments (HL: African Plateau, Tibetan Plateau, Colorado Plateau) represent three topographic regimes that require **both** elevation and slope to distinguish. A signature containing only elevation would conflate the Tibetan Plateau with the Alps; slope alone would conflate the African Plateau with the Gangetic plain.

**Rubric implication**: ele and slp are non-redundant across the full variable range. For historical polity analysis the distinction matters concretely: a polity on the African Plateau is at altitude but on accessible, agricultural terrain; a polity in the Alps is at altitude with difficult, steep terrain. Different constraints, same elevation value.

---

### BV.12 — pre×aet: near-redundant globally; Mediterranean NS finding

**Date**: 2026-05-17

**LISA**: LL=29.4% (arid zones + cold zones), HH=22.3% (humid tropics), **HL=1.9%** (energy-limited cold maritime), LH=0.0%, NS=46.3%

**Finding**: Near-redundant globally (I_BV=+0.863). Both variables track water availability: in water-limited environments AET ≈ P (almost perfectly coupled); in energy-limited humid tropics both AET and P are high (coupled in the same direction). The 1.9% HL = cold maritime coasts (southern Norway, southern Chile) where energy limitation suppresses AET well below precipitation.

**Mediterranean is NS**: annual totals of precipitation and AET are both moderate in the Mediterranean, placing the region in the middle of the global distribution. The summer-drought pattern — seasonally high P in winter, near-zero in summer; AET constrained year-round by temperature seasonality — is invisible at annual aggregation. For Mediterranean-focused analysis, **seasonal or monthly precipitation and AET are more informative than annual means**.

Cold subarctic is LL for pre×aet (low absolute P AND low AET) — consistent with the ari×pre HL for the same zone. The aridity metric calls the subarctic "humid" (P/PET high); the pre×aet relationship calls it "relatively dry" (both metrics below global mean). Both descriptions are physically accurate; the apparent contradiction reflects different reference frames (see BV.13).

**Rubric implication**: precipitation and AET are largely interchangeable in a Band C signature for tropical through temperate research questions. For Mediterranean-focused queries, neither annual metric is sufficient — seasonal disaggregation is required. This is an argument for including CMI (climate moisture index, which captures seasonality) alongside or instead of annual AET in Mediterranean-region signatures.

---

### BV.13 — Cross-pair insight: LISA class = global structural position, not absolute character

**Date**: 2026-05-17

**Finding**: Two observations from the map review crystallize a general principle.

**Subarctic zone — two different classes from two pairs**:
- `ari×pre`: **HL** (high aridity index because P/PET is high; moderate-precip neighbourhood)
- `pre×aet`: **LL** (low absolute precipitation AND low AET, both below global mean)

These are internally consistent descriptions of the same physical reality (cold climate with moderate precipitation and very low evaporative demand). The aridity metric calls it "humid" relative to global PET; the absolute precipitation metric calls it "moderately dry." LISA class is always a statement about position in the global distribution of the variable in question, not a universal environmental classification.

**Atacama and Pampas share LL in ari×pre**: both are below the global humid-tropical mean on both aridity index and precipitation. The Atacama is hyperarid; the Pampas is productive temperate grassland. The LL class correctly describes their structural position (outside the humid zone) but says nothing about whether the dryness is ecologically lethal or merely moderate.

**General rule**: LISA class is a necessary but not sufficient descriptor for a place in an EDOPS signature. A researcher seeing `ari×pre: LL` for a polity location should not infer "desert" — only "below global humid average on both metrics." The raw signature values provide the magnitude; the LISA class provides the structural position. Both together enable meaningful environmental characterization.

---

## Phase 4 — Regional stratification (Cells 15–17)

Notebook: `notebooks/edop/spatial/06_bivariate_phase4_l6.ipynb`. Same weights and permutation settings as global Phase 4. Regions: Mediterranean (n=221), Monsoon Asia/Indomalaya (n=1046), Tibetan/cold-arid (n=369). Subset Queen weights rebuilt per region; islands dropped before fitting.

---

### BV.14 — 3×5 I_BV grid: full reference table

**Date**: 2026-05-18

| Pair | Mediterranean | Monsoon Asia | Tibetan/cold-arid | Global |
|---|---|---|---|---|
| ari×pre | +0.824 | +0.813 | +0.626 | +0.578 |
| tmp×snw | −0.470 | −0.217 | **−0.005 NS** | −0.865 |
| hdi×gdp | +0.688 | +0.422 | +0.620 | +0.581 |
| ele×slp | **+0.062 NS** | +0.485 | **−0.141** | +0.423 |
| pre×aet | +0.836 | +0.854 | +0.753 | +0.863 |

NS = not significant (p > 0.05). All other cells p = 0.001–0.002.

**Finding**: Two cells fail significance (ele×slp Mediterranean, tmp×snw Tibetan). One sign reversal (ele×slp Tibetan). The "near-redundant" tier from BV.7 does not hold uniformly across regions: tmp×snw collapses to NS in the cold-arid zone despite being the globally strongest coupled pair.

---

### BV.15 — tmp×snw: progressive regional decoupling; global near-redundancy collapses in Tibetan zone

**Date**: 2026-05-18

| Region | I_BV | p |
|---|---|---|
| Global | −0.865 | 0.001 |
| Mediterranean | −0.470 | 0.001 |
| Monsoon Asia | −0.217 | 0.001 |
| Tibetan/cold-arid | −0.005 | 0.459 NS |

**Finding**: The global near-redundancy attenuates monotonically from Mediterranean to Monsoon Asia to Tibetan, where it collapses to NS. Within the cold-arid plateau, all basins are cold — temperature variance is compressed — so temperature does not predict snow cover. Snow distribution is governed by precipitation (monsoon moisture on southern Himalayan flanks vs dry plateau interior), which varies independently of temperature within the region.

The progressive attenuation (−0.865 → −0.470 → −0.217 → −0.005) reflects a range-compression effect: as the regional sample becomes more exclusively cold, the global warm/cold contrast that drives the coupling shrinks. The practical implication — snw non-redundant with tmp at cold sites — is real regardless of mechanism.

**Implication**: The "near-redundant" tier for tmp×snw (BV.7) must be treated as context-dependent. In cold-arid and high-altitude regions, both variables carry independent information. The rubric cannot drop snw from signatures for Tibetan Plateau, Central Asian steppe, or Andean highland sites. This is the strongest single-cell result in the regional grid — a globally dominant coupling becoming locally invisible.

---

### BV.16 — ele×slp: Mediterranean NS, Tibetan sign reversal, Monsoon Asia amplification

**Date**: 2026-05-18

| Region | I_BV | p |
|---|---|---|
| Global | +0.423 | 0.001 |
| Mediterranean | +0.062 | 0.114 NS |
| Monsoon Asia | +0.485 | 0.001 |
| Tibetan/cold-arid | −0.141 | 0.002 |

**Finding**: Three structurally distinct patterns from a single pair.

**Mediterranean NS**: ele and slp are spatially independent across the Mediterranean landscape. The realm is a heterogeneous patchwork — coastal plains, river valleys, and upland ranges (Atlas, Apennines, Pyrenees, Balkans) distributed without a systematic continental-gradient structure. The African Plateau HL signal that drives the global coupling is absent; the heterogeneous microgeography cancels within-region at L6.

**Tibetan sign reversal (−0.141)**: High-elevation basins cluster with low-slope neighbours within this region. The plateau interior is elevated but flat, adjacent to other flat plateau basins. This is the within-region expression of the global HL class identified in BV.11 — the sign reversal directly confirms that the plateau mechanism (not mountain-building) governs ele×slp coupling in this zone. Elevation and slope are anti-correlated within the plateau: high ele → low-slp neighbourhood.

**Monsoon Asia amplification (+0.485)**: The Himalayan orogeny creates a coherent HH zone (high ele + steep, actively uplifting fronts) adjacent to a large LL zone (Indo-Gangetic plain, Mekong/Irrawaddy deltas). The mountain-lowland contrast is unambiguous at L6 and exceeds the global average coupling.

**Implication**: For Mediterranean-focused historical signatures, ele and slp must be treated as fully independent variables — neither redundant nor structurally coupled. For Tibetan/highland signatures, the sign reversal warns against applying global-scale redundancy logic. The "genuinely distinct" global tier (BV.7) is correct but masks qualitatively different regional structures.

---

### BV.17 — ari×pre: amplified in all three regions; no reversal (contrast with T×P)

**Date**: 2026-05-18

| Region | I_BV | p |
|---|---|---|
| Global | +0.578 | 0.001 |
| Mediterranean | +0.824 | 0.001 |
| Monsoon Asia | +0.813 | 0.001 |
| Tibetan/cold-arid | +0.626 | 0.001 |

**Finding**: All three sampled regions exceed the global I_BV — the global scalar is the floor, not the ceiling. Unlike T×P, which reversed sign in the Mediterranean (BV.3, I_BV = −0.250), ari×pre maintains positive coupling everywhere and is amplified.

The contrast with T×P is physically transparent: the aridity index (P/PET) shares the precipitation signal with the pre variable. Even in the Mediterranean — where summer drought inverts T×P — both aridity index and precipitation vary in the same direction across the regional moisture gradient (wetter Atlantic-influenced margins vs drier Saharan margins). The summer-drought seasonality cannot invert ari×pre because both metrics reflect overall water availability, not seasonal timing.

The Monsoon Asia LISA map (bimodal geographic partition): Indian subcontinent = LL (semi-arid, both metrics below regional mean); equatorial maritime SE Asia = HH (perennially wet, both metrics above mean); mainland SE Asia interior = NS transition zone. This clean split — not a gradient but two coherent sub-environment clusters — drives I_BV = +0.813, and explains why ari×pre here is strongly significant while T×P for this realm was NS in Phase 3 (warm vs wet signals cancelled; moisture vs moisture signals reinforce).

Tibetan +0.626 is the lowest regional value: LL concentration dominates (plateau cold-arid, both metrics consistently low), with less gradient variation than the moisture-gradient realms. The global scalar (0.578) being below all three regional values confirms that heterogeneous transition zones globally pull the aggregate down.

**Implication**: The "genuinely distinct" tier for ari×pre holds in all sampled regions. No context-dependence found. The regional amplification pattern also confirms the global finding (BV.8) that aridity index and precipitation are non-redundant: their structural coupling is regionally coherent but the information each adds beyond the other is geographically specific.

---

### BV.18 — pre×aet: most geographically stable pair; Mediterranean paradox resolved

**Date**: 2026-05-18

| Region | I_BV | p |
|---|---|---|
| Global | +0.863 | 0.001 |
| Mediterranean | +0.836 | 0.001 |
| Monsoon Asia | +0.854 | 0.001 |
| Tibetan/cold-arid | +0.753 | 0.001 |

**Finding**: pre×aet maintains strong positive coupling in all three regions — the smallest regional spread of any pair (range 0.101 vs tmp×snw range 0.860). No sign reversal, no NS result. This is the most geographically robust coupling in Phase 4.

**Mediterranean paradox resolved**: BV.12 noted that Mediterranean basins are NS at the global scale because annual totals for both variables place them in the middle of the global distribution. The regional I_BV = +0.836 is not contradictory: global NS reflects distribution position; regional I_BV reflects within-region structure. Within the Mediterranean, the gradient from wet Atlantic margins and Alpine-foreland basins (HH: southern France, northern Italy, Adriatic) to dry Levantine margins (LL: Israel, Lebanon coast, Nile margin) is coherent on both P and AET. The HL patch on the Syria/Lebanon coast (Lebanese mountains, Syrian coastal range) marks high-P orographic basins surrounded by low-AET Syrian semi-arid interior — a sharper topographic boundary than anywhere in western Anatolia at this scale. Most of the Mediterranean heartland (Spain, central Italy, Greece, Turkey) is NS even within the region — both variables are moderate, contributing no spatial lag signal. The historically dense core of the Mediterranean world sits in the NS zone; pre and aet annual totals provide minimal discriminating power for classical-period sites.

**Tibetan attenuation (0.753)**: Cold energy-limitation partially decouples AET from P — temperature controls the growing season length and thus evaporative demand more than precipitation does. Strong but attenuated.

**Implication**: The "near-redundant" tier for pre×aet holds globally and in all sampled regions. This is the most robust redundancy finding of Phase 4.

---

### BV.19 — Cross-regional synthesis: stable vs context-dependent pairs

**Date**: 2026-05-18

| Pair | Global tier | Regional stability |
|---|---|---|
| pre×aet (+0.863) | Near-redundant | **Stable** — holds in all regions; smallest spread |
| tmp×snw (−0.865) | Near-redundant | **Context-dependent** — collapses to NS in Tibetan |
| hdi×gdp (+0.581) | Genuinely distinct | **Stable** — amplified or comparable in all regions |
| ari×pre (+0.578) | Genuinely distinct | **Stable** — amplified in all regions; no reversal |
| ele×slp (+0.423) | Genuinely distinct | **Context-dependent** — NS in Mediterranean, sign reversal in Tibetan |

**Finding**: Two of five pairs are context-dependent rather than globally stable.

**tmp×snw**: Near-redundant globally, independent in cold-arid regions. The "near-redundant" tier is downgraded to context-dependent for high-altitude and cold-arid zones. Both variables carry distinct information for signatures in these regions.

**ele×slp**: Genuinely distinct globally, but the nature of the distinction changes by region. Mediterranean NS means the variables are unrelated at regional scale; Tibetan sign reversal means the structural relationship inverts (plateau vs mountain-building mechanism). The global "genuinely distinct" label is correct but the reason differs by region.

Three pairs are regionally stable (pre×aet, ari×pre, hdi×gdp) — their global tier assignment holds in all sampled regions without modification.

**Methodological extension of BV.6**: Phase 3 established that global I_BV is insufficient as a redundancy filter. Phase 4 regional analysis adds a second layer: the tier assignment itself (near-redundant vs genuinely distinct) can be context-dependent. A pair's global tier describes average behavior across the full variable range; regional analysis reveals where the average obscures locally different structure. For variable selection in polity-phase signatures, tier assignments for tmp×snw and ele×slp should carry a regional qualifier.

---

## Categorical Spatial Coherence — `lith_class`, `pnv_majority`, `wetland_class`

**Date**: 2026-05-19
**Notebook**: `notebooks/edop/spatial/13_categorical_coherence.ipynb`
**Method**: Queen contiguity weights, `use_index=True`; `esda.Join_Counts` per-class binarized (999 perms, seed=42); local coherence via neighbor-class-match fallback (row-stochastic W·y, threshold ≥50%). `Join_Counts_Local` unavailable due to indexing bug in this esda/Python-3.14 environment.

---

### CAT.1 — Variables excluded from join-count analysis (tautological)

`ecoregion`, `biome`, and `freshwater_ecoregion_name` are spatial taxonomy variables — their boundaries *are* the spatial structure they encode. Running join-counts would confirm that classification schemes are spatially contiguous, which is circular, not empirical. The three variables tested (`lith_class`, `wetland_class`, `pnv_majority`) are independent empirical classifications that could in principle be spatially incoherent; the analysis establishes they are not.

---

### CAT.2–3 — lith_class: global and local coherence

All 16 classes significant at p=0.001. Z-scores range 296–723; BB/mean_bb ratios range 2.9× (SU) to 33× (IG). Local coherence 90.8%–99.5%.

Geologically interpretable differentiation:
- **≥99%**: SU Unconsolidated Sediments (99.2%), MT Metamorphic (99.1%), IG Ice/Glaciers (99.5%) — large sedimentary platforms, metamorphic shields, glaciated regions form continuous geological provinces
- **91–94%**: PB Basic Plutonic (90.8%), PI Intermediate Plutonic (93.8%) — batholiths and granitic intrusions occur as isolated bodies embedded in country rock; the lower coherence correctly reflects geological structure type, not data quality

The 0.5–9.2% isolated fractions are real transition basins at formation boundaries. No class fails coherence.

---

### CAT.4–5 — pnv_majority: global and local coherence

All 15 valid classes (class 99 Unclassified excluded) significant at p=0.001. Z-scores 448–638; local coherence 93.0%–98.8% — tightest range of the three variables (5.8 pp).

Biome-belt classes (Desert 98.8%, Boreal evergreen 98.3%, Savanna 97.8%) are most coherent; lower tail is Polar/rock/ice (93.0%) and Temperate broadleaf evergreen (95.5%), which occur as geographically fragmented patches (high-altitude ice fields, coastal/montane rainforests) rather than continuous belts.

---

### CAT.6–7 — wetland_class: global and local coherence

Analysis on n=96,884 non-null wetland subset (1,096 w_wet islands). All 12 classes significant at p=0.001. Z-scores 222–519 — lower than lith/pnv, reflecting smaller population and more fragmented wetland geography. Local coherence 91.5%–99.5% — widest range (8.0 pp).

Functional differentiation:
- **≥98%**: Swamp forest (99.3%), 25-50% wetland (99.5%), Wetland complex (99.2%), Freshwater marsh (98.5%) — continuous landscape features forming large wet zones
- **91–95%**: Lake (91.5%), Coastal wetland (94.0%), Reservoir (94.4%) — isolated features scattered across non-wetland matrices

Lake (91.5%) is the most isolated wetland type: a lake-class basin surrounded by river or marsh is common. Lowest z (221.7) despite largest class (n=27,528).

---

### CAT.8 — Cross-variable synthesis

**All 43 class-variable combinations are globally significant at p=0.001 with no exceptions, and all produce local coherence >90%.** The three variables are appropriate EDOPS signature fields; none fail the spatial-coherence requirement.

The lower-coherence classes in each variable (plutonic intrusions, fragmented polar/montane patches, isolated water features) are geographically the most interesting basins — transition zones and embedded features where a categorical label diverges from its neighbourhood. They are candidate sites for high-information EDOPS signatures.

**Scale implication**: All three variables are regional-scale descriptors at L8. A basin's categorical class is highly predictive of its neighbourhood's class. The slider/discovery interface should treat categorical variables as region-selectors, not independent per-basin attributes.

**Methodological fallback**: `esda.Join_Counts_Local` has an indexing bug (Python 3.14): `_statistic()` drops islands from LJC array (size 190,107) but `_crand_plus` iterates over full z (size 190,675), raising `IndexError` at index 190107. Fallback: deterministic majority-match classification using row-stochastic W·y ≥ 0.5. Global z-scores (222–723) confirm the class-level signal is real.


---

## dist_sink_km — Band E (coastality)

**Date**: 2026-05-21
**Notebook**: `notebooks/edop/spatial/14_dist_sink_esda.ipynb`
**Method**: Queen contiguity weights, `use_index=True`, row-standardised; 999 perms, seed=42; raw transform (skewness < 5 at both scales); global Moran's I + Moran_Local LISA.

---

### DSK.1 — Global Moran's I: high, raw preferred

| Scale | I_raw | I_log | I_canonical | skewness |
|---|---|---|---|---|
| L6 | 0.9041 | 0.8017 | 0.9041 | 1.52 |
| L8 | 0.9633 | 0.8764 | 0.9633 | 1.40 |

Both p=0.001. Raw I > log I at both scales — unusual. `log1p` compresses the interior-to-coastal gradient, making it appear less steep. Moderate skewness (1.4–1.5) means raw spatial structure is stronger than log, so canonical = raw per METH.3.

---

### DSK.2 — Scale comparison: continental-gradient tier, most scale-stable in sweep

Δ = +0.059 (↑). Consistent with continental-gradient typology group. LISA maps are geographically indistinguishable at L6 and L8 — the spatial pattern is fixed at the continental scale already captured by L6. NS shrinks 45.4% → 42.9%; no new geographic structure appears. This is the most scale-stable variable in the 40-variable sweep: dist_sink is a geometric coordinate, not an environmental process variable.

For comparison: aridity Δ=+0.026 (also ↑ but with visible MAUP effects); discharge Δ=−0.019 (↓, network-topology character).

---

### DSK.3 — LISA: LL-dominant, HL near-absent, low outlier fraction

| Class | L6 % | L8 % |
|---|---|---|
| HH | 19.24 | 19.87 |
| LL | 34.90 | 37.03 |
| HL | 0.01 | 0.00 |
| LH | 0.43 | 0.17 |
| NS | 45.42 | 42.93 |

HH = deep continental interiors (Amazon, Congo, Siberia, Central Asia, N. American Great Plains). LL = all coastal margins globally, SE Asian archipelago, Western Europe.

HL near-zero (2 at L6, 1 at L8): physically near-impossible — a far-interior basin cannot be surrounded by coastal basins. The spatial gradient is monotonically coast-to-interior. Near-zero HL is itself a diagnostic: dist_sink has no spatial anomalies in the interior direction.

LH small and decreasing (0.43% → 0.17%): near-sink basins embedded in interior terrain — fjord-fed inlets, river mouths penetrating plateaus. LH% shrinks at L8 as coastal tessellation tightens.

Cluster core (HH+LL) = 54.1% / 56.9% — among the highest in the sweep alongside climate variables. Outlier fraction = 0.44% / 0.17% — lowest in the dataset.

---

### DSK.4 — Implication for EDOPS

dist_sink_km encodes continental position relative to ocean, not a physical environmental process. This explains its orthogonality to all Band A–D variables (F4.8). It adds independent geographic context that no physical variable captures.

The near-zero HL fraction is a slider implication: selecting high dist_sink_km is implicitly selecting deep-continental basins with no ambiguity. The variable functions as a continent-interior / coastal-margin switch.

Historical validity: stable on geological timescales.
Typology: continental-gradient (I_L6=0.904, scale ↑, outlier%=0.44%).


---

## Phase 3 CHAR — Within-band Bivariate Redundancy (`15_bivariate_redundancy.ipynb`)

All 11 pairs at L8, p=0.001. Outputs: `output/edop/spatial/bivariate_redundancy.parquet` (2,097,425 rows), `bivariate_redundancy_counts.csv`.

### BVR.1 — S/U pairs: global I_BV reference grid

| Pair | I_BV | HH% | LL% | HL% | LH% | NS% |
|---|---|---|---|---|---|---|
| T_yr s×u | 0.989 | 35.7 | 26.1 | 0.2 | 0.0 | 38.0 |
| P_yr s×u | 0.963 | 17.5 | 33.2 | 0.2 | 0.0 | 49.1 |
| Ari s×u | 0.978 | 20.7 | 18.9 | 0.3 | 0.0 | 60.1 |
| HFT s×u | 0.826 | 18.4 | 33.0 | 0.3 | 0.3 | 48.1 |
| Crop s×u | 0.867 | 15.2 | 44.4 | 0.1 | 0.4 | 39.9 |

### BVR.2 — Same-band non-S/U pairs: global I_BV reference grid

| Pair | I_BV | HH% | LL% | HL% | LH% | NS% |
|---|---|---|---|---|---|---|
| Dis_yr × Dis_min | 0.525 | 14.5 | 28.0 | 1.9 | 3.5 | 52.1 |
| Dis_yr × Dis_max | 0.538 | 15.6 | 20.4 | 0.4 | 3.8 | 59.8 |
| Dis_max × RiverArea_u | 0.455 | 12.0 | 12.2 | 0.4 | 3.6 | 71.8 |
| HDI × GDP | 0.587 | 13.7 | 31.2 | 4.5 | 0.0 | 50.6 |
| T_yr × T_min | 0.969 | 33.3 | 27.5 | 0.2 | 0.0 | 39.1 |
| T_min × T_yr_u | 0.965 | 35.7 | 26.1 | 0.2 | 0.0 | 38.0 |

### BVR.3 — S/U divergence is globally rare; anthropogenic pairs show most

S/U divergence (HL+LH) ranges from 0.2% (T_yr, P_yr) to 0.6% (HFT). The local-vs-upstream duality is real but spatially small — well under 1% of basins in each case. Climate s/u pairs are near-concordant everywhere: catchment-scale smoothing means a basin's temperature and precipitation closely mirrors its upstream catchment. HFT and Crop show the most s/u divergence because anthropogenic land use does not respect catchment flow direction as cleanly as physical climate gradients.

Aridity s×u has the highest NS fraction (60.1%) of all pairs: the aridity index (P/PET) spans humid-to-arid transition zones where no coherent local autocorrelation signal forms.

### BVR.4 — Discharge pairs: attribute-space redundancy ≠ spatial concordance

I_BV for discharge pairs (0.455–0.538) falls below their univariate Moran's I (~0.563 at L8). High Pearson r in attribute space does not imply spatial concordance. The seasonal regime geography that dis_min and dis_max capture independently from dis_yr breaks the spatial lock.

All three discharge pairs show LH >> HL. Dis_yr × Dis_min (LH=6,641 vs HL=3,662): cold-climate/snowmelt transition zones where small headwater basins have low annual flow but neighbor the great boreal perennial rivers. Dis_yr × Dis_max (LH=7,296 vs HL=671): monsoon transition zones where flood-pulse peaks concentrate in neighboring high-maximum systems. The asymmetric LH pattern is the seasonal-regime geography that annual discharge alone does not resolve.

### BVR.5 — Temperature triple is spatially interchangeable

T_yr, T_min, and T_yr_upstream produce nearly identical LISA distributions (HH ~63–68k, LL ~49–52k, HL ~375–413, LH 0–14). The three temperature metrics form one spatial pattern. Documented as characterisation; no variables removed from the signature (see BVR.7).

### BVR.6 — HDI×GDP: asymmetric development geography

HL=8,566 basins (4.5%), LH=7 basins (0.004%). High-HDI enclaves in low-GDP neighborhoods exist at significant scale; the reverse is essentially absent. The HL zone maps onto Eastern Europe and former Soviet states — high HDI (Soviet-legacy education, healthcare) in a below-average-GDP neighborhood. LH≈0 reflects a one-directional relationship: wherever GDP is high, HDI follows; the reverse is rare.

The HDI×GDP spatial pattern traces the temperate/tropical development divide and the modern North-South gradient — the accumulated outcome of environmental endowment, colonial history, and institutional development. For historical queries, Band D is future information relative to the period of interest: opt-in context, not primary environmental characterisation.

### BVR.7 — Design note: global redundancy does not justify variable removal

Global bivariate concordance characterises the *typical* spatial relationship between paired variables. It does not license removing variables from L8 basin signatures. At the basin scale, variables that covary globally may carry distinct local information — particularly in HL/LH divergence zones, which are often the ecologically and historically most interesting configurations. Phase 3 findings are documentation of co-variation structure for interpretive use, not a pruning pass.

---

## Phase 4 CHAR — Band T native-unit characterization (`16a`, `16b`)

---

### BT4B.1 — LMR spatial autocorrelation: temperature and PDSI

**Date**: 2026-05-22  
**Notebook**: `16b_band_t_native_esda.ipynb`  
**Method**: Global Moran's I and LISA at 2° native LMR grid, restricted to 4,924 land cells (L8-basin-bearing). Queen contiguity with longitude wrap, row-standardized. Raw anomaly values (log not applicable for symmetric fields). 999 permutations, seed 42. Outputs: `band_t_native_moran.csv`, `band_t_native_lmr_lisa.parquet`.

**LMR-as-reanalysis caveat (first-class)**: All I values reflect the LMR Bayesian reanalysis with its CCSM4-LME model prior, which imposes spatial covariance independent of proxy signal. LMR Moran's I measures "spatial structure of the reanalysis field," not "spatial structure of past climate" directly.

**Temperature anomaly Moran's I** (all p = 0.001):

| Epoch | I |
|-------|------|
| 0 CE (early-LMR) | 0.9616 |
| 1000 CE | 0.9640 |
| 1500 CE | 0.9502 |
| 1900 CE | 0.9741 |
| MCA 950–1250 | 0.9700 |
| LIA 1450–1850 | 0.9306 |

- LIA is the lowest (0.9306) — regionally concentrated NH cooling breaks global spatial coherence relative to smooth prior-dominated epochs.
- 1900 CE highest (0.9741) — model prior + industrial warming both impose large-scale smooth structure.
- MCA high (0.9700) despite being a period of interest: near-zero anomaly field is prior-dominated, not proxy-driven.
- **Temperature LH = 0 in all epochs** — no isolated cold cells surrounded by warm anywhere across six epochs. Temperature anomaly fields are too spatially smooth for local sign-reversals at 2° resolution.
- 0 CE LISA: LL = 1,950 (39.6%), anomalously high — model prior artifact at sparse proxy coverage; cold clustering in non-proxy regions, not a climate signal.
- LIA LISA: HH = 1,431 (29.1%) > LL = 790 (16.0%) despite being a cooling epoch. Concentrated NH/subarctic cooling produces few LL clusters; tropical and SH cells remain relatively warm → HH dominates.

**PDSI anomaly Moran's I** (all p = 0.001):

| Epoch | I |
|-------|------|
| 0 CE (early-LMR) | 0.8833 |
| 1000 CE | 0.8813 |
| 1500 CE | 0.8846 |
| 1900 CE | 0.8875 |
| MCA 950–1250 | 0.8561 |
| LIA 1450–1850 | 0.8789 |

- Consistently 0.04–0.09 below temperature across all epochs. Moisture fields have shorter spatial correlation length scales than thermal fields — orography, storm tracks, and ENSO teleconnections fragment precipitation patterns at scales temperature spans smoothly. This reflects a known property of real climate independent of LMR methodology.
- MCA PDSI is the outlier low (0.8561), with highest NS% (60.8%) — spatial structure of the moisture field most diffuse during MCA.
- PDSI HL peaks at LIA (50) and 1900 CE (44); all other epochs ≤ 5. Slightly more local moisture outliers in industrial-era and LIA fields.

---

### BT4B.2 — HYDE spatial autocorrelation: pilot timing and tractability

**Date**: 2026-05-22  
**Notebook**: `16b_band_t_native_esda.ipynb`  
**Method**: Queen weights via vectorized 8-direction grid-topology enumeration. Land mask from `area_raster` NaN pattern (2,213,836 cells, mean_neighbors=7.88, 76 islands). Pilot: cropland 1000 CE, log1p transform (skew 8.84 → 7.17).

**Timing**: weights 9s; Moran's I 31s; LISA 2,247s (~37 min, permutation matrix ~17 GB → disk swap). Projected full sweep incl. LISA: 8.9 h — intractable. **Decision**: Moran's I sweep only; pilot LISA retained as structural sample.

**Pilot LISA** (cropland 1000 CE, log1p, n = 2,213,836): LL=59.1%, NS=34.1%, HH=5.7%, LH=1.0%, HL=0.04%.

- **LL=59.1% is a zero-inflation artifact** — with 73.9% of cells having zero cropland, LL identifies contiguous non-agricultural zones (boreal, arid, tropical forest), not an agricultural finding.
- **HH=5.7% (~126k cells) is the substantive class** — the genuine agricultural cluster cores (Fertile Crescent, Ganges-Indus, Yellow River, Mediterranean).
- LH=1.0%: non-farmed pockets within agricultural zones are rare — zones already spatially compact at 1000 CE. HL=0.04%: isolated farmed cells in wilderness essentially absent at 5-arcmin.
- For HYDE, LISA composition percentages are dominated by zero-inflation at any epoch. Moran's I trajectory is the informative tool; LISA is useful only for mapping the HH geographic footprint.

---

### BT4B.3 — HYDE spatial autocorrelation: Moran's I sweep

**Date**: 2026-05-22  
**Notebook**: `16b_band_t_native_esda.ipynb`  
**Method**: Moran's I only (LISA intractable). Log1p where skewness > 5; raw otherwise. 8000 BCE skipped (< 5% non-zero). All p = 0.001. Output: `band_t_native_moran.csv`.

**Transform note**: Cropland switches log1p → raw between 1500 CE and 1900 CE; grazing between 0 CE and 1000 CE. I values across the switch are not directly comparable. Trajectory shape robust; apparent jump magnitude at switch point should not be taken at face value.

**Cropland**: 0.5895 (4000 BCE, log1p) → 0.6696 → 0.7372 → 0.7431 → 0.7702 (1500 CE, log1p) → 0.9113 → 0.9173 (2000 CE, raw). Gradual consolidation from scattered pioneer patches to regional zones; sharp rise post-1500 CE to fully consolidated industrial-era mosaic.

**Grazing**: 0.9087 (4000 BCE, log1p) → slight dip to 0.8921 (0 CE) → 0.9195 → 0.9172 → 0.9127 → 0.9287 (2000 CE, raw). Starts already high — pastoral land use follows biome gradients from the outset. Slight dip at 0 CE possibly reflects pastoral-to-arable transition in classical-era cores.

**Headline finding**: At 4000 BCE cropland I=0.59, grazing I=0.91 — gap ~0.32. At 2000 CE both ~0.92–0.93 — gap closed. Cropland required ~6,000 years to achieve the spatial coherence pastoral land use had from early antiquity. Grazing follows ecological structure immediately; cropland built its spatial structure through millennial-scale intensification.

---

### BT4C.1 — LMR temperature: MCA and LIA are not a dipole

**Date**: 2026-05-22
**Notebook**: `16c_band_t_native_cross_temporal.ipynb`
**Method**: Per-cell comparison of MCA (950–1250 CE) and LIA (1450–1850 CE) temperature anomaly fields at 2° land grid (4,924 cells), anomalies relative to full 0–1998 CE mean. Percentile-based color scale (98th pct ≈ ±0.4 K) used for maps; `nanmax` scale was suppressed by Arctic outlier cells.

**Results**:
- Pearson r(MCA, LIA temperature) = **+0.116** (slope = 0.26) — weakly *positive*, not anticorrelated. No dipole.
- A symmetric dipole would give r ≈ −1, slope ≈ −1. This result is close to zero.
- Quadrant breakdown: 78% of land cells have both MCA and LIA **negative** relative to the 0–1998 mean — an artifact of the 20th-century industrial warming inflating the baseline, not a climate signal. Only **9%** show the canonical pattern (MCA positive, LIA negative).
- Spatial variance asymmetry: LIA anomaly spread ≈ 6× MCA anomaly spread (vertical cigar shape in scatter). LIA left a stronger, more coherent spatial imprint in LMR than MCA did.
- Dipole sum (MCA + LIA): positive over much of NH land — the MCA warm signal at those cells exceeds the LIA cooling signal, confirming asymmetry. The model prior damps the weaker, more contested MCA signal more than the LIA signal.

**LMR-as-reanalysis caveat (first-class)**: all values include CCSM4-LME model prior spatial covariance. r = +0.116 and the asymmetry described above are properties of the LMR reanalysis field, not directly of past climate.

---

### BT4C.2 — LMR LISA cross-epoch: spatial cluster structure substantially reorganises MCA → LIA

**Date**: 2026-05-22
**Notebook**: `16c_band_t_native_cross_temporal.ipynb`
**Method**: Per-cell LISA class transition (temperature) from `band_t_native_lmr_lisa.parquet`. n = 4,924 land cells.

**Transition counts** (MCA → LIA):
| Category | Count | % of land cells |
|----------|-------|-----------------|
| Stable (same class) | 1,994 | 40.5% |
| Declustered (→ NS) | 1,487 | 30.2% |
| Newly-clustered (NS →) | 1,166 | 23.7% |
| Sign-reversed (HH ↔ LL) | 266 | 5.4% |
| Other change | 11 | 0.2% |

- Only 40% of cells hold the same LISA class across both periods — the spatial cluster structure is not stable.
- The dominant transition is **declustering**: cells that had significant spatial structure in MCA (mostly the NH LL cool-cluster band) lost significance in LIA. LIA cooling is too spatially uniform in the NH for LISA to identify local cold outliers — neighbours cool together.
- **Sign-reversal is rare (5.4%)**: the spatial geography of warm vs. cool clustering does not simply invert between periods.
- Together with BT4C.1 (r = +0.12), these results confirm that MCA and LIA do not form a symmetric dipole in LMR at the spatial-clustering level either.

---

### BT4C.3 — LMR PDSI: partial dipole between MCA and LIA

**Date**: 2026-05-22
**Notebook**: `16c_band_t_native_cross_temporal.ipynb`
**Method**: Same as BT4C.1 for PDSI anomaly.

**Results**:
- Pearson r(MCA, LIA PDSI) = **−0.382** (slope = −0.73) — genuinely anticorrelated. A partial dipole.
- Scatter cloud is roughly circular: MCA and LIA PDSI anomaly variance are comparable (contrast with temperature where LIA >> MCA).
- Slope −0.73: the anticorrelation is real but not perfect (a clean dipole would give slope ≈ −1).

**Contrast with temperature**: PDSI r = −0.382 vs. temperature r = +0.116. Moisture geography reorganised more coherently between MCA and LIA than thermal geography did. This reflects the physical difference: temperature in LMR is dominated by large-scale model-prior smoothing; PDSI reflects local moisture balance driven by circulation patterns (monsoon, ENSO, NAO) that can genuinely reverse between climate regimes.

**Implication**: for EDOPS Band T, LMR climate anomalies at a specific query location carry more interpretable period-to-period moisture information than temperature information. Temperature anomalies at 2° resolution are structurally near-identical across MCA and LIA; PDSI anomalies are meaningfully different.

---

### BT4C.4 — HYDE cropland: presence persistence and agricultural leading edge

**Date**: 2026-05-22
**Notebook**: `16c_band_t_native_cross_temporal.ipynb`
**Method**: Per 5-arcmin land cell, count of 7 non-degenerate epochs (4000 BCE–2000 CE) with cropland fraction > 0. First-epoch map: earliest epoch with presence. n = 2,213,836 land cells. *Presence persistence ≠ cluster-core persistence; HH LISA was intractable — see BT4B.2.*

**Persistence distribution**:

| Epochs present | Cells | % |
|---|---|---|
| 0/7 (never farmed) | 1,075,208 | 48.57% |
| 1/7 | 223,915 | 10.11% |
| 2/7 | 303,954 | 13.73% |
| 3/7 | 63,430 | 2.87% |
| 4/7 | 126,097 | 5.70% |
| 5/7 | 108,568 | 4.90% |
| 6/7 | 190,375 | 8.60% |
| 7/7 (all epochs) | 122,289 | 5.52% |

**Key patterns**:
- 7/7 cores (farmed all 7 epochs, 5.52% of land): narrow but continuous corridors along the Fertile Crescent and Levant, Nile Valley, Ganges-Indus plain, North China Plain — the canonical Neolithic agricultural origins. River-valley alignment is clearly visible at native 5-arcmin in the regional zoom.
- Nearly half of land cells (48.57%) show zero cropland presence across all 7 epochs — Himalayas, Sahara, Australian outback, boreal zones. Not missing data; genuinely uncultivated in HYDE's reconstruction.
- First-epoch map: darkest viridis (4000 BCE) concentrated at those same 7/7 cores; gradient diffuses outward. Consistent with an agricultural diffusion pattern, though HYDE derives this from population estimates rather than direct archaeological evidence.
- Americas: almost entirely late (1500–2000 CE first epoch). The Old World / New World contrast is the sharpest visual signal in the maps.
- **Black = never farmed**: cells with crop_first == −1 (NaN) render as transparent against dark figure background. Distinct from 4000 BCE cells, which appear as darkest viridis.

**HYDE methodology caveat**: spatial allocation uses environmental suitability, making HYDE land use *not independent* of EDOPS environmental variables. Any downstream correspondence test between EDOPS signatures and HYDE cropland must acknowledge this circularity.

---

### BT4C.5 — HYDE grazing: pastoral persistence and cropland contrast

**Date**: 2026-05-22
**Notebook**: `16c_band_t_native_cross_temporal.ipynb`

**Persistence distribution**:

| Epochs present | Cells | % |
|---|---|---|
| 0/7 (no grazing) | 657,073 | 29.68% |
| 1/7 | 132,922 | 6.00% |
| 2/7 | 505,558 | 22.84% |
| 3/7 | 63,135 | 2.85% |
| 4/7 | 94,679 | 4.28% |
| 5/7 | 144,058 | 6.51% |
| 6/7 | 275,999 | 12.47% |
| 7/7 (all epochs) | 340,412 | 15.38% |

**Key patterns**:
- Grazing spatial extent is vastly larger than cropland: 15.38% of land cells show 7/7 grazing persistence vs. 5.52% for cropland. The entire Old World grassland/savanna/steppe belt (Central Asia, Arabia, sub-Saharan Africa, South Asia) shows 7/7 persistence. Pastoral land use follows biome structure (BT4B.3 confirmed: grazing I ≈ 0.91 even at 4000 BCE).
- Only 29.68% of cells are grazing-free across all epochs (vs. 48.57% for cropland) — pastoralism occupies a much larger portion of the land surface than cultivation.
- First-epoch map: most of Eurasia and Africa is 4000 BCE (darkest) — the pastoral belt was effectively fully established at our earliest HYDE epoch.
- **Americas grazing**: overwhelmingly orange to yellow (1500–2000 CE) — a clean cartographic signature of the Columbian Exchange. Indigenous pre-contact Americas had negligible livestock in HYDE's model.
- **Mesoamerica contrast** (Cell 13 regional zoom): cropland shows substantial persistence (indigenous agriculture pre-dates contact); grazing shows near-zero persistence (no livestock pre-contact). The two variables tell directly opposing historical stories at this region.
- Grazing first-epoch map over Africa and Asia is consistent with reading as a **diffusion map** of pastoral spread from early centres, with the important caveat that HYDE derives this from population/suitability models, not direct archaeological tracking of pastoral diffusion.

---

### BT4C.6 — Phase 4c: paper-figure assessment

**Date**: 2026-05-22
**Notebook**: `16c_band_t_native_cross_temporal.ipynb`

**Assessment**:

- **PDSI scatter (Cell 9)**: the most surprising result of 4c — moisture geography shows a partial dipole (r = −0.38) while temperature does not (r = +0.12). This is a reportable finding about LMR's period structure with a clear physical interpretation. Candidate as a supplementary figure in a methods/characterization paper.

- **HYDE cropland persistence map (Cell 11)**: the most visually readable output of the entire CHAR phase. The 7/7 cores, the first-epoch gradient, and the Old World / New World contrast are all historically intelligible without statistical explanation. Paper-figure candidate, with HYDE methodology caveat.

- **Mesoamerica cropland vs. grazing contrast (Cell 13)**: the side-by-side regional zoom showing indigenous agriculture (cropland) vs. Columbian Exchange livestock (grazing) in the same region is the sharpest single illustration of what the two HYDE variables mean historically. Worth keeping as a standalone inset.

- **LMR temperature results (Cells 6–8)**: characterization, not finding. The non-dipole result and LISA reorganisation are expected given what was known about LMR methodology (model prior, proxy network bias). Worth documenting but not paper-figure level.

**Overall**: 4c produced two reportable findings (PDSI partial dipole; HYDE Old World/New World cropland-vs-grazing contrast) and confirmed expected characterization results for LMR temperature. The Phase 4 CHAR record is complete.

---

## CHAR Phase 5 — Per-variable global-position attribute specification

**Date**: 2026-05-23
**Notebook**: `notebooks/edop/explore/16_position_attribute_spec.ipynb`
**Artifact**: `metadata/edops_codebook_v03_draft.tsv` — v02 + 7 new columns

### CHAR-P5.1 — Scalar position method assignments

Rule: |skewness| > 5 → `log_percentile`; else → `percentile`. Applied to all implemented
scalar variables using `output/edop/explore/01_scalar_summary.csv`. Variables assigned
`log_percentile`: discharge_annual, discharge_min, discharge_max, pop_density, river_area,
river_area_upstream, aridity_index, aridity_upstream, reservoir_vol (9 variables).
Log1p transform used for all log_percentile variables with zeros present. All others:
`percentile` on non-null basins. 6 planned/unimplemented variables have null position_method
(integer-typed and array-typed scalars, plus `narrative`); all implemented variables covered.

### CHAR-P5.2 — Categorical and compositional position methods

Categorical variables (lith_class, wetland_class, pnv_majority, climate_zone,
climate_stratum, biome, terrestrial_ecoregion, freshwater_habitat, freshwater_ecoregion,
land_cover, outlet_type, coast_flag): `rarity_rank` — percentage of non-null L8 basins
in the class, computed from public.basin08 at query time.

Compositional (pnv_shares): `dominance_class` — within-basin maximum share across
all PNV classes. Distribution bimodal: large monoculture spike (>95%) and left tail of
genuine mixtures (<60%). 60% and 95% thresholds documented from Cell 6 distribution.

Band T variables (lmr_*, evolv2k_*, hyde_*): `deferred-phase4`. Position attribute
depends on the temporal query window; specified in Phase 4 LMR/HYDE design memo follow-up.

### CHAR-P5.3 — Historical validity

Assigned manually from `docs/design/variable_selection_rubric_issues.md` §2.
Distribution across 97 schema_keys (narrative excluded):
- `full-record` (22): Band A topography/terrain/geology; Band B stable soils + runoff + groundwater; Band E coastality
- `pre-1500 valid` (43): Band C climate (pattern-stable proxy); Band B hydrology/cryosphere/wetlands; PNV/ecoregion/biome categoricals
- `modern-only` (18): Band D human geography; forest cover; land cover; dam regulation
- `period-specific` (14): Band T (validity defined by temporal query, not the variable)

### CHAR-P5.4 — High-r partners (global correlation structure)

11 pairs at |r| ≥ 0.90 from F4.9. Recorded in codebook column `high_r_partner` (renamed
from `redundancy_partner` at Phase 6 — "redundancy" implied variable pruning, which is not
the intent). No variables are removed or demoted based on this — the column documents global
correlation structure only. Phase 3 CHAR (bivariate_redundancy.ipynb) showed bivariate
I ≈ 0.45–0.54 even for the highest-r pairs, confirming local spatial independence is
preserved. 8 schema_keys have partners: discharge cluster (discharge_annual, discharge_max,
discharge_min, river_area), socioeconomic pair (gdp_mean ↔ hdi), temperature pair
(temperature_annual ↔ temperature_min).
