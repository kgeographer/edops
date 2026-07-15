# WO4c findings — Basin similarity

**Date:** 2026-07-14
**Branch:** `demo`
**Notebook:** `notebooks/edop/demo/wo4c_basin_similarity.ipynb`
**Outputs:** `output/edop/demo/wo4c_*`

---

## Step 1 — Space characterisation

### NoData audit (Cell 2)
All 31 candidate columns present in `public.basin06`. All pass pct_bad ≤ 20%:
- Clay / silt / sand worst at 4.6% (757 basins — likely oceanic/island with no soil texture data)
- Slope: 1.8%, stream gradient: 2.5%
- Everything else: effectively 0%

897 basins dropped from the feature matrix (union of soil-texture and slope NaN sets) → 15,500 / 16,397 = 94.5% coverage.

### Correlation structure (Cell 5)
High-correlation pairs (|r| ≥ 0.85), all confirmed redundant and excluded from SELECTED:

| Pair | r | Action |
|---|---|---|
| dis_m3_pmx ↔ dis_m3_pyr | +0.972 | exclude pmx |
| dis_m3_pmn ↔ dis_m3_pyr | +0.943 | exclude pmn |
| tmp_dc_smn ↔ tmp_dc_syr | +0.976 | exclude smn |
| tmp_dc_smx ↔ tmp_dc_syr | +0.903 | exclude smx |
| snw_pc_syr ↔ tmp_dc_syr | −0.895 | exclude snw |
| wet_pc_sg2 ↔ wet_pc_sg1 | +0.881 | exclude sg2 |
| ari_ix_uav ↔ ari_ix_sav | +0.975 | keep in upstream-only framing |
| pre_mm_uyr ↔ pre_mm_syr | +0.973 | keep in upstream-only framing |
| tmp_dc_uyr ↔ tmp_dc_syr | +0.990 | not selected |

**Key structural finding:** upstream climate variables are nearly redundant with local equivalents at L06 (r > 0.97). At this scale, most basins are their own upstream catchment. The s/u apparatus functions as an exception-detector, not a routine signal — it adds information only where provenance diverges from local climate.

### PCA (Cell 6)
- Σ condition number κ = 6,091.8 — singular; Mahalanobis over the full 27-variable set is unreliable. Selection is necessary, not optional.
- 9 components for 90% variance; 12 for 95% (of 27 non-Band-D variables).
- PC1 alone captures ~27% — a dominant first axis.

**Named axes:**

| PC | ~Variance | Signal | Dominant loadings |
|---|---|---|---|
| PC1 | 27% | **Thermal regime** | tmp_dc_syr/smn/smx (+), snw_pc_syr (−), prm_pc_sse (−) |
| PC2 | 21% | **Moisture / water availability** | ari_ix_sav, dis_m3_pyr, pre_mm_syr, run_mm_syr all positive |
| PC3 | 15% | **Terrain energy** | slp_dg_sav (+0.37), sgr_dk_sav (+0.39), ele_mt_smx (+0.41) |
| PC4 | 8% | **Provenance / network position** | dis_m3_pyr (+), dist_sink (+), pre_mm_syr (−) |
| PC5 | 5% | **Wetland extent** | wet_pc_sg1/sg2 (+0.54/0.56) |

PC4 is the s/u axis: high discharge + long distance to outlet + low local precipitation = exogenous river. The EDOPS s/u apparatus corresponds to the 4th principal axis of global basin space — real, but a minority signal (~8% of global variance). Upstream variables (ari_ix_uav, pre_mm_uyr) load identically to their local equivalents on PC1–3, confirming they add nothing for ordinary basins.

---

## Step 2 — Variable selection

### Final SELECTED — 13 local variables

**A_terrain (3):** `ele_mt_sav`, `slp_dg_sav`, `kar_pc_sse`
- sgr_dk_sav excluded: r=+0.807 with slp_dg_sav; slope is the more fundamental surface measure

**B_hydrology (5):** `dis_m3_pyr`, `gwt_cm_sav`, `wet_pc_sg1`, `cly_pc_sav`, `slt_pc_sav`
- run_mm_syr excluded: r=+0.838 with pre_mm_syr; net-of-evaporation signal already covered by ari_ix_sav (P/PET) and dis_m3_pyr (catchment-integrated runoff)
- snd_pc_sav excluded globally (compositional with clay+silt)

**C_climate (4):** `ari_ix_sav`, `pre_mm_syr`, `tmp_dc_syr`, `prm_pc_sse`

**E_coastality (1):** `dist_sink` — PC4 (provenance axis)

**Upstream framing only (2):** `ari_ix_uav`, `pre_mm_uyr`

Redundancy check on SELECTED: clean — no pair ≥ 0.80 within the local set. Each band targets a named PC dimension.

---

## Step 3 — Feature matrices

- **X_local:** 15,500 × 13 (local-only)
- **X_combined:** 15,500 × 15 (local + upstream)
- Same 897 NaN drops for both; upstream columns have no additional NaN.

---

## Step 4 — Validation

### Test 1 — Mediterranean five (floor): NEGATIVE

All five sites (Mediterranean Basin, Coastal California, Central Chile, The Cape, SW Australia) rank each other >50 in their top-50 local analogues.

**Diagnosis:** Mediterranean climate is defined by seasonal precipitation contrast (dry summer, wet winter), not annual means. With only annual-mean variables (`pre_mm_syr`, `ari_ix_sav`, `tmp_dc_syr`), Mediterranean basins are indistinguishable from other warm semi-arid basins globally. Each site sits inside a large cloud of similarly-valued basins; the five Mediterranean peers land outside the top 50.

**Fix:** `pre_mm_s01..s12` (monthly precipitation averages, planned in variable catalog) is the correct solution. This test directly motivates that catalog extension. The negative is a real result — not retried until it passes.

### Test 2 — Rhine/Willamette mundane pair: PREMISE WRONG

Neither site ranks the other in the top 30 — but the premise was incorrect, not the metric.

Rhine lowland analogues: aridity 81–126, precip 613–967 mm/yr, temp 6.5–12.5°C — Western/Central European temperate basins.  
Willamette Valley analogues: aridity 147–247, precip 1366–2014 mm/yr, temp 5.9–11.8°C — Pacific Northwest and wet maritime basins (NZ, southern Chile).

The two sites differ ~2× on precipitation at basin scale. The Willamette Valley receives substantially more annual rainfall than the Rhine lowlands. The metric correctly places them in different neighbourhoods within the broad "maritime temperate" class.

**Finding:** the metric makes fine discriminations within broad climate classes — it resolves within-biome moisture gradients. Each site finds geographically dispersed but environmentally coherent analogues across continents.

### Test 3 — Timbuktu provenance contrast: DIRECTIONAL, WEAK

Timbuktu query values: ari_ix_sav=9, pre_mm_syr=189 mm/yr; ari_ix_uav=47, pre_mm_uyr=955 mm/yr; precip_ratio ≈ 5.05.

| | Local top-20 | Combined top-20 |
|---|---|---|
| Overlap | — | 15/20 |
| Mean precip_ratio of analogues | 2.01 | 2.39 |
| Basins dropped | — | 5 (precip_ratio: 0.4, 0.4, 0.7, 1.0, 1.3) |

The five basins dropped by adding upstream are the most purely rain-fed (precip_ratio ≤ 1.3). The upstream dimension systematically pushes these out — directional. But the mean precip_ratio shift (2.01 → 2.39) is modest relative to Timbuktu's own 5.05 ratio. The top-20 does not dramatically restructure toward other allochthonous river-mouth basins.

**Interpretation:** consistent with the r=0.975 correlation between ari_ix_uav and ari_ix_sav. At L06, upstream dimension adds near-zero independent information for most basins. The combined framing correctly identifies Timbuktu as a high-provenance environment and marginally adjusts the analogue set, but cannot separate it sharply from the broader Sahelian neighbourhood because the distance penalty is distributed across 15 variables. The s/u apparatus is a quiet exception-detector at this scale.

### Test 4 — Tbilisi scale stability: PASS

| | L06 | L08 |
|---|---|---|
| Tbilisi biome label | 4 (Temperate Broadleaf) | 13 (Deserts & Xeric Shrublands) |
| Dominant analogue biome | **4** (8/20) | **4** (11/20) |
| L08 matrix size | — | 171,790 × 13 |

Tbilisi's own biome label flips from 4 to 13 between levels (confirming WO3). The metric's dominant analogue biome stays biome 4 at both levels. The analogue set is more stable than the biome label.

The L08 top-20 shifts slightly toward warmer/drier analogues (4 biome 13 + 3 biome 12 entries not present at L06), reflecting the Tbilisi L08 basin capturing the warmer Kura valley floor rather than surrounding Caucasus highlands. But biome 4 dominates at both levels and the neighbourhood remains globally distributed (Europe, Asia, North America).

**Finding (provisional — superseded by WO4d Step 2):** The biome flip (4→13) is a clean MAUP demonstration: L06 encompasses the Caucasus highlands (wetter); L08 is the valley floor (drier). Both are correct at their respective scales. WO4c read the analogue set staying biome-4-dominant at both levels as evidence the metric tracks this continuously. **This verdict is withdrawn.** Two readings are possible and WO4c cannot distinguish them: (a) the metric correctly identifies a transitional environment at both scales; (b) 2–3 climate variables moved while 10 others held, and Euclidean distance across 13 variables cannot feel it — the same dilution mechanism that weakened Test 3. WO4d Step 2 decides. See `wo4d_findings.md`.

---

## Synthesis

1. **Effective dimensionality:** 9 principal axes account for 90% of variance in the 27-variable non-Band-D set. These map onto four named environmental dimensions: thermal regime (PC1), moisture availability (PC2), terrain energy (PC3), provenance/network position (PC4). This is a publishable characterisation of the EDOPS signature's structure independent of any metric.

2. **Upstream corresponds to PC4** (~8% global variance). The s/u duality is a real dimension of basin space, but a minority signal. At L06, upstream and local climate measures are nearly collinear (r > 0.97) for most basins — the apparatus fires only for genuine provenance outliers.

3. **Seasonality is the missing dimension.** The Mediterranean five failure (Test 1 negative) and the weakness of within-biome discrimination both point to the same gap: annual-mean variables cannot capture seasonal structure. `pre_mm_s01..s12` (planned) is the fix.

4. **Test 4 verdict withdrawn pending WO4d.** Whether the metric tracks Tbilisi's L06→L08 environmental shift or is diluted by it is undecided. See `wo4d_findings.md`. Test 2 finding stands: the metric makes fine within-biome discriminations (Rhine vs. Willamette resolved at ~2× precip difference).

5. **Mahalanobis over the full variable set is not viable** (κ = 6,091). The selected 13-variable set removes the most collinear pairs; κ of the selected subset was not computed and should be checked before any Mahalanobis implementation.

---

## Accept gate

- [x] Correlation structure reported: effective dimensions, κ, PC loadings
- [x] Selected fields per band with reasons for each inclusion/exclusion
- [x] All four tests run, results reported whichever way they fell
- [x] Negative results reported honestly (Test 1 negative; Test 2 premise wrong)
- [ ] Karl review before anything proposed for the surface

## Next steps

- Monthly precip variables (`pre_mm_s01..s12`) when available will unlock Mediterranean recovery and substantially improve the metric
- κ of the 13-variable selected subset should be computed before any Mahalanobis implementation
- Polity/polygon similarity is a function over basin similarity — this comparison vector is Phase 4 correspondence substrate; do not re-derive it there
