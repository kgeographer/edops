# Typology review — continental-gradient suspects

## Entry 1 — 2026-06-14

### Trigger

Step 3 block 1 (Timbuktu 100 km buffer, L06, T = 20) aggregated all variables typed
`continental-gradient` in the catalog. Five came back with zero-dominated distributions
inconsistent with the continental-gradient assumption of a smooth, highly
spatially-autocorrelated field:

| variable | verdict | spread | p10 | p90 |
|---|---|---|---|---|
| permafrost_extent | concentrated | 0.00 | 0.0 | 0.0 |
| pasture_extent | spread | 85.06 | 0.0 | 85.06 |
| pasture_extent_upstream | spread | 78.01 | 0.0 | 78.01 |
| pct_silt_upstream | spread | 30.93 | 0.0 | 30.93 |
| pct_clay_upstream | spread | 64.23 | 0.0 | 64.23 |

---

### Per-variable findings

#### permafrost_extent (`prm_pc_sse`)

**Catalog:** I_L6 = 0.96, I_L8 = 0.98. distribution_notes: "Skewness 2.21; zero-fraction
0.77." position_notes: "77.1% zero basins included in CDF as-is."

**Global L06:** 76.6% of all 16,397 basins are at exactly 0. p10=p25=p50=p75=0; p90=71;
max=100. No NoData.

**Analysis:** The catalog already knew about the zero-fraction and recorded it. The Moran's
I is near-saturated (0.96/0.98), so the variable is genuinely spatially autocorrelated
within its geographic range — permafrost IS a continental gradient across the polar and
high-altitude zones. The problem is that it is a restricted-extent variable: for any query
location outside the permafrost zone, the entire buffer returns 0. Block 1 returned
spread=0, mean=0, verdict=concentrated — technically correct by the algorithm but
informationally empty. The number 0 and spread 0 are not saying the same thing as
a warm-climate variable with mean p5 and spread 3.

**Verdict:** `continental-gradient` typing is correct. No reclassification warranted.
The issue is algorithmic, not a catalog error: block 1 needs a degenerate-at-zero guard
— when every basin in the buffer is at the global floor, suppress the mean or flag as
"outside variable's active domain" rather than emitting a concentrated verdict at 0.

---

#### pasture_extent (`pst_pc_sse`) and pasture_extent_upstream (`pst_pc_use`)

**Catalog:** I_L6 = 0.86, I_L8 = 0.90. distribution_notes: "Skewness 1.21; zero-fraction
0.33." position_notes: **"best-effort; not yet implemented; transform to be confirmed on
implementation."**

**Global L06:** 32.9% (s) / 31.3% (u) at exactly 0. Median = 7 / 9; p90 = 64 / 62; max =
100. No NoData.

**Analysis:** The Moran's I (0.86) supports continental-gradient: pasture has large-scale
spatial structure (agricultural zones, climatically constrained). The spread seen in block 1
(p10=0, p90≈85) is likely genuine — the Timbuktu buffer straddles the Niger floodplain and
the Saharan interior, a real environmental contrast. The distribution is right-skewed with a
33% zero-floor, which is substantial but not disqualifying for a gradient cluster. The
sharper concern is the catalog's own position_notes: **this variable's transform was marked
as not yet confirmed at the time of catalog writing.** `percentile` is the assigned method,
but `log_percentile` may be more appropriate given the skew. The wide block-1 spread is at
least partly a consequence of scoring right-skewed data on a linear CDF.

**Verdict:** `continental-gradient` typing plausible (Moran's I supports it). No
reclassification. However, **position_method needs confirmation before this variable is
relied on in block 1 or any aggregation.** Specifically: reconsider whether `log_percentile`
is more appropriate than `percentile` for a right-skewed (1.21), zero-inflated (33%) variable.
The "not yet implemented" note in the catalog was a deferred flag that was never resolved.

---

#### pct_silt_upstream (`slt_pc_uav`) and pct_clay_upstream (`cly_pc_uav`)

**Catalog:** I_L6 = 0.96 (silt) / 0.90 (clay), I_L8 = 0.96 / 0.93. distribution_notes:
"Skewness −0.29 / 0.19; missing 461.7%." (The "461.7%" is almost certainly a decimal
placement error in the catalog — likely 4.617%; the actual NoData fraction at L06 is 4.1%,
consistent with the position_notes value of 9.1% at L8.) The local variants (pct_silt_s,
pct_clay_s) have no NoData in the buffer and showed no zero-floor issue in block 1.

**Global L06:** Only 3.3% (silt) / 4.0% (clay) of valid basins are at zero. Distributions
are smooth and near-normal: silt p10=12, p50=31, p90=44; clay p10=8, p50=18, p90=29.
4.1% NoData. No global zero-inflation.

**Analysis:** The block-1 zero at p10 is a small-sample artifact, not a global pathology.
The dominant-weight Saharan basin (hybas_id 1060041510, weight 0.277) has cly_pc_uav = 0
and slt_pc_uav = 0 in the raw data. With 9 basins and weight 0.277 > 0.10, the weighted
p10 falls within that basin's value, which happens to be 0. The local variants (cly_pc_sav,
slt_pc_sav) did not show this because none of the nine basins has a zero local soil-texture
reading — the zero appears only in the upstream-average. A upstream average of 0% clay or
silt for a basin whose upstream catchment is deep Saharan is geologically plausible (aeolian
sand sheets covering carbonate or crystalline basement). Globally the distribution is smooth
and the Moran's I is near-saturated (0.96/0.90), fully consistent with continental-gradient.

**Verdict:** `continental-gradient` typing is correct. No reclassification. The p10=0 in
block 1 is a true value for a genuinely sandy Saharan upstream catchment, not a data artifact
or a typing error. Worth noting that the upstream soil variants are more susceptible than
local variants to extreme values when the buffer contains a headwater basin draining a
uniform geological terrain. The catalog's "missing 461.7%" note should be corrected to
4.617% (decimal error) when the catalog is next edited.

---

### Summary of recommendations

| variable | current typing | recommendation |
|---|---|---|
| permafrost_extent | continental-gradient | Keep. Add degenerate-at-zero guard in block 1 logic. |
| pasture_extent (s+u) | continental-gradient | Keep. **Resolve deferred position_method question** (percentile vs log_percentile) before relying on block-1 output. |
| pct_silt_upstream | continental-gradient | Keep. Zero is a true value; small-sample artifact. Fix "461.7%" typo in catalog. |
| pct_clay_upstream | continental-gradient | Keep. Same as silt_upstream. Fix "461.7%" typo in catalog. |

No reclassifications. Two action items:
1. **permafrost_extent**: block 1 needs a guard for variables where the entire buffer sits at
   the global distributional floor — emit "outside active domain" rather than concentrated at 0.
2. **pasture_extent (s+u)**: confirm position_method (the catalog's own "not yet implemented"
   flag was never resolved).
