# WO4d findings — Basin similarity diagnostic

**Date:** 2026-07-14
**Branch:** `demo_wo4`
**Notebook:** `notebooks/edop/demo/wo4c_basin_similarity.ipynb` (Cells 15–18)
**Precondition:** WO4c complete; findings in `wo4c_findings.md`

---

## The question

WO4c left two competing readings:

- **Robustness** — the metric correctly reports a transitional environment at both Tbilisi scales,
  and correctly identifies Timbuktu as a provenance outlier.
- **Dilution** — 2–3 variables move substantially; 10 others hold; Euclidean distance over 13
  variables cannot feel the difference. The neighbourhood barely re-ranks.

WO4d tests both claims directly, on continuous variables only.

---

## Step 5 — κ of the selected 13 (Cell 15)

| Set | κ | Status |
|---|---|---|
| Full 27-variable set (WO4c) | 6,091.8 | SINGULAR — Mahalanobis unreliable |
| Selected 13-variable set | **55.1** | WELL-CONDITIONED — Mahalanobis available |

Lowest three eigenvalues of Σ₁₃: 0.056, 0.162, 0.201 — all well above zero.

**Finding:** Variable selection reduced the condition number 110×. If dilution is confirmed and
Mahalanobis is the next step, the door is open. Do not implement in this WO.

---

## Step 2 — Per-level coherence: Tbilisi (Cell 17)

WO3 established that L06 and L08 Tbilisi are genuinely different environments:
aridity 93 → 63 (−30 units), precipitation 762 → 622 mm (−140 mm), temperature 5.3 → 10.8°C (+5.5°C).

The test: **do the analogue sets shift in the same direction, and in proportion?**

### Query values vs. analogue medians

| Variable | L06 query | L06 ana. med | L08 query | L08 ana. med | Δ query | Δ medians | Tracking |
|---|---|---|---|---|---|---|---|
| ari_ix_sav | 93 | 60 | 63 | 54.5 | −30 | −5.5 | **18% — diluted** |
| pre_mm_syr | 762 | 578 | 622 | 607.5 | −140 | +29.5 | **wrong direction** |
| tmp_dc_syr | 5.3 | 6.4 | 10.8 | 11.8 | +5.5°C | +5.4°C | **near-perfect** |

### Analogue value ranges

| Variable | L06 analogues | L08 analogues |
|---|---|---|
| ari_ix_sav | [47, 141] | [35, 86] |
| pre_mm_syr | [408, 998] mm | [383, 753] mm |
| tmp_dc_syr | [0.3, 12.8]°C | [4.9, 14.1]°C |

### Verdict: partial dilution confirmed

**Temperature** (PC1, 27% of global variance) is the dominant axis. A 5.5°C shift moves enough
basins globally to restructure the analogue neighbourhood almost perfectly.

**Aridity and precipitation** (PC2, 21%) are diluted. The 9 non-climate variables that do not
change between L06 and L08 Tbilisi — terrain, discharge, groundwater depth, wetland, soil texture —
anchor the neighbourhood in place. The climate variables have 4 votes out of 13; the non-climate
variables have 9. Aridity tracks only 18% of its actual shift; precipitation goes the wrong way.

This is the dilution mechanism made visible: the metric responds to the strongest global axis
(temperature, PC1) but loses the moisture signal under weight from non-moving variables. The
analogue sets are not wrong — they are coherent with the full 13-variable vector at each level.
The problem is that the full 13-variable vector gives moisture insufficient weight relative to its
importance to environmental character.

---

## Step 4 — Test 3 as two-basin discrimination (Cell 18)

### Setup

- **Timbuktu:** ari_ix_sav=9, pre_mm_syr=189mm, ari_ix_uav=47, pre_mm_uyr=955mm, precip_ratio=5.05
- **Rain-fed match sought:** same local climate, precip_ratio ≈ 1.0

### Result: the premise could not be met

The best rain-fed match from Timbuktu's local top-50 (the basin with precip_ratio closest to 1.0):

| | Rain-fed match | Timbuktu |
|---|---|---|
| hybas_id | 1060652110 | 1060551560 |
| rank in local top-50 | 21 | — |
| ari_ix_sav | 32 | 9 |
| pre_mm_syr | 662 mm | 189 mm |
| tmp_dc_syr | 27.2°C | (similar) |
| precip_ratio | 1.00 | 5.05 |

**The two basins are not climate twins.** Local precipitation differs 3.5×; aridity index differs
3.6×. The test specified "C_climate distance ≈ 0 by construction" — but C_climate = 1.312, a
substantial distance.

### Per-band distances (Timbuktu vs. rain-fed match)

| Band | Distance |
|---|---|
| **total** | 2.202 |
| A_terrain | 0.026 |
| B_hydrology | **1.581** |
| C_climate | 1.312 |
| provenance | 0.790 |

**provenance / C_climate = 0.790 / 1.312 = 0.60×** — provenance is the *smallest* band distance,
not the largest.

### Two findings from this failure

**1. Locally arid + rain-fed is nearly empty at L06.**
Basins as dry as Timbuktu (ari=9, pre=189mm) are either on allochthonous rivers or they have
almost no discharge at all. A rain-fed Sahelian basin with similar local aridity does not appear
to exist in the global L06 set at this scale. The "control" the test required — same local climate,
different provenance — cannot be constructed because locally-arid and rain-fed are ecologically
near-incompatible at basin scale.

**2. Discharge already carries the provenance signal.**
B_hydrology (1.581) is the dominant band distance, driven primarily by dis_m3_pyr. The Niger
gives Timbuktu enormous discharge (200,000+ m³/s) wildly incommensurate with 189mm/yr local
rainfall. That disproportion shows up in the hydrology band regardless of whether the upstream
variables (ari_ix_uav, pre_mm_uyr) are included. The s/u apparatus tries to add explicit upstream
information, but dis_m3_pyr has already captured most of that signal.

**Consequence:** the s/u apparatus does not add discriminating power at L06 that is not already
partially expressed through discharge. This is consistent with the r=0.975 correlation between
ari_ix_uav and ari_ix_sav (Cell 5) and with the weak neighbourhood restructure in WO4c Test 3
(overlap 15/20; mean precip_ratio shift 2.01 → 2.39).

---

## On Timbuktu's global uniqueness

Karl noted the impression that Timbuktu has no close analogues in the combined sense. This is
broadly correct, and the metric is right to show it.

The local top-20 (Cell 12) does find analogues on local climate alone: other hyper-arid Sahelian
basins that share Timbuktu's temperature and low local rainfall. What makes Timbuktu near-unique
in the full 13-variable space is the combination of very low local precipitation and very high
discharge (the Niger). That pairing is genuinely rare globally — it is the signature of a major
allochthonous river crossing a desert. The metric correctly places Timbuktu in a sparse
neighbourhood because that combination is objectively unusual. The failure is not that the metric
finds no analogues; it is that the variable carrying the provenance signal is discharge (in
B_hydrology), not the explicit upstream variables (ari_ix_uav, pre_mm_uyr).

---

## Overall synthesis

| Question | Answer |
|---|---|
| Is Mahalanobis available on the 13-var set? | Yes (κ=55.1) |
| Does the metric track genuine scale-conditionality (Tbilisi)? | Partially — temperature yes, moisture no |
| Is moisture (aridity/precipitation) diluted by non-climate variables? | Yes — confirmed |
| Does the s/u apparatus discriminate allochthonous basins? | Not at L06 — discharge already carries the signal |
| Does locally arid + rain-fed exist as a testable category? | No — ecologically near-empty at L06 |

### What this means for the metric

The metric as built (Euclidean over 13 z-scored variables) performs well on temperature-dominated
distinctions and correctly identifies extreme outliers like Timbuktu. It under-responds to
moisture-regime differences because the climate band (4 variables) is outvoted by the non-climate
bands (9 variables) in Euclidean space. The s/u apparatus adds little at L06 because its
information is already partially expressed through discharge and because upstream and local climate
are nearly collinear at this scale.

**Two principled responses, both for future WOs:**
1. **Mahalanobis distance** — reweights by the inverse covariance, effectively amplifying
   under-represented dimensions. κ=55.1 confirms this is now viable.
2. **Band-weighted composite** — assign explicit weights by band rather than variable, so each of
   the four environmental dimensions (terrain, hydrology, climate, provenance) votes once rather
   than in proportion to how many variables it has.

Neither is implemented here. WO4d diagnoses; it does not re-build.

---

## Accept gate

- [x] κ of selected 13 reported: 55.1, well-conditioned
- [x] Per-level coherence: Tbilisi analogue medians at L06 and L08 on continuous variables
- [x] Dilution verdict stated plainly: confirmed for moisture, not for temperature
- [x] Test 3 run as two-basin discrimination; premise failure documented as a finding
- [x] Discharge identified as the variable already carrying the provenance signal
- [x] Timbuktu global uniqueness addressed
- [ ] Karl review

## Next steps

- Band-weighted composite or Mahalanobis as a follow-on WO, if the metric goes to the surface
- Monthly precipitation variables (`pre_mm_s01..s12`) when available remain the fix for Test 1
  (Mediterranean) and will strengthen the climate band's discriminating power
- The metric as built is appropriate for holistic environmental similarity; it is not yet
  appropriate for climate-primary similarity queries
