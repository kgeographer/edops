# WO4d — Similarity: is the metric seeing what we know is there?

**Phase:** DEMO · Track 2
**Kind:** Research. Notebook only — extends `wo4c_basin_similarity.ipynb`. No surface, no engine.
**Branch:** `demo`
**Precondition:** WO4c complete.

**Scope is deliberately small.** This is a diagnostic increment, not a rebuild. We are testing one
suspicion. If it is confirmed, the fix is a separate WO.

---

## The suspicion

WO3 established, through two independent channels, that L06 Tbilisi and L08 Tbilisi are different
environments:

- aridity **93 → 63** (−30 percentile points), temp **+5.5 °C**
- biome **Temperate Broadleaf & Mixed Forests → Deserts & Xeric Shrublands**

A hand-drawn vegetation classification and a continuous moisture variable agree. The difference is
real and it is large.

WO4c Test 4 then found that Tbilisi's **analogue set** stays biome-4-dominant at *both* levels
(8/20 at L06, 11/20 at L08), and read this as a success — the metric being "more scale-stable than
the biome label."

**That reading may be backwards.** If the two basins are genuinely different environments, their
nearest neighbours ought to be *different sets of places*. L08's neighbours should be arid valley
floors. If the metric returns much the same kind of place for both, it may be **failing to see a
difference that both the aridity value and the biome label plainly show**.

Two readings, and WO4c cannot distinguish them:

- **Robustness** — Tbilisi sits near a categorical boundary; the 4→13 flip is a threshold artifact
  and the metric correctly reports a transitional environment at both scales.
- **Dilution** — a few variables move a lot, eleven others hold, and Euclidean distance over 13
  variables cannot feel it. The neighbourhood barely re-ranks.

**Dilution is not a new hypothesis.** It is CC's own diagnosis of Test 3's weakness: *"the distance
penalty is distributed across 15 variables."* If that is right, the same defect is presenting as a
*weakness* in Test 3 and as a *strength* in Test 4. One mechanism, two tests, opposite verdicts.
This WO decides which.

---

## Step 1 — Drop biome as an evaluation criterion

WO4c scored analogue sets by biome-label agreement. **This is circular** — biome is the coarse,
expert-drawn, hand-delineated classification the metric is meant to improve on. Agreement does not
validate; disagreement does not indict. They measure different things.

Biome stays useful only as a **gross smell-test** (if Tbilisi's analogues came back tropical
rainforest, something is broken) and as an **argumentative foil**. It is not a yardstick.

**All evaluation below is on the continuous variables.**

---

## Step 2 — Per-level coherence (the test WO4c should have run)

Not *"are the analogue sets stable across levels"* — they should not be. Instead, for each level
**separately**:

**Are this basin's analogues coherent with this basin's own values?**

For L06 Tbilisi and L08 Tbilisi independently, report for the top-20 analogues:

- the **query basin's** values on the 13 selected variables
- the **analogues' distributions** on those same variables (median, IQR)
- per-variable: does the analogue set centre on the query value, or drift off it?

Then the question that matters: **do the two analogue sets differ from each other in the way the
query basins differ?** L08 Tbilisi is 30 percentile points more arid and 5.5 °C warmer than L06
Tbilisi. Are its analogues correspondingly more arid and warmer?

- **They are** → the metric tracks scale-conditionality. Good result, and a real claim: *the metric
  responds continuously to a difference the biome label can only express as a categorical snap.*
- **They are not** → dilution confirmed. The metric is under-responsive, and Test 4's "stability"
  was the defect wearing a compliment.

Report **overlap** between the two analogue sets (how many of the 20 are shared). High overlap
despite a large query-basin difference is the signature of dilution.

---

## Step 3 — Per-band distances (specified in WO4c, not built)

WO4c Step 3 asked for distance per band plus a composite. Only `X_local` (13) and `X_combined` (15)
were built. **Build the per-band distances now** — they are the instrument for *seeing* dilution
rather than inferring it:

- **A_terrain** (3): `ele_mt_sav`, `slp_dg_sav`, `kar_pc_sse`
- **B_hydrology** (5): `dis_m3_pyr`, `gwt_cm_sav`, `wet_pc_sg1`, `cly_pc_sav`, `slt_pc_sav`
- **C_climate** (4): `ari_ix_sav`, `pre_mm_syr`, `tmp_dc_syr`, `prm_pc_sse`
- **provenance** (3): `ari_ix_uav`, `pre_mm_uyr`, `dist_sink`

With per-band distances, the Tbilisi L06→L08 difference should be **large in C_climate** and small
elsewhere. If the composite washes that out, the arithmetic of the dilution is visible, not
speculative.

Per-band distance is also the honest answer to *"similar in what respect?"* — it lets the instrument
say **"twins in bioclimate, opposites in terrain,"** which no single scalar and no biome label can.

---

## Step 4 — Test 3, as originally specified

WO4c ran a different test than the one specified, and CC's own diagnosis explains why it came out
weak: two upstream variables out of fifteen cannot move a Euclidean neighbourhood, however large
the provenance difference. **The dilution was measured; the apparatus was not tested.**

The specified test is a **two-basin discrimination**, not a neighbourhood restructure:

- **Timbuktu** — local precip 189 mm/yr, aridity 9; upstream 955 mm/yr, aridity 47; ratio ≈ 5.05
- **A matched local-water Sahelian basin** — closely matched on local precip / aridity / temp, but
  precip_ratio ≈ 1.0 (rain-fed, no exogenous water). Find it by query, don't hand-pick.

Then:

- **C_climate distance** between them should be ≈ 0 (they are climatic twins by construction)
- **provenance-band distance** should be **large**

If it is, the s/u apparatus discriminates, and *"twins in bioclimate, opposites in provenance"* is
demonstrated in a single pair. If the provenance distance is also small, the apparatus does not
discriminate at L06 and that is a serious finding — one consistent with WO4c's r = 0.975 between
`ari_ix_uav` and `ari_ix_sav`.

**This is the test that decides whether the s/u apparatus does work no biome label can.** It is the
one that matters most in this WO.

---

## Step 5 — κ of the selected 13

WO4c reported κ = 6,091 for the full 27-variable set (singular; Mahalanobis unreliable) but never
computed κ for the selected 13. Compute it. It determines whether Mahalanobis is available at all,
and Mahalanobis is the principled response *if* dilution is confirmed — it reweights by the data's
own covariance instead of letting every variable vote once.

**Do not implement Mahalanobis in this WO.** Just report whether the door is open.

---

## Deliverables

- New cells appended to `notebooks/edop/demo/wo4c_basin_similarity.ipynb` (continue `# Cell N`;
  do not renumber existing cells)
- `docs/edop/demo/wo4d_findings.md`
- Amend `wo4c_findings.md` Test 4: the biome-agreement criterion is circular and the "scale-stable"
  verdict is withdrawn pending Step 2. Do not leave a superseded conclusion standing.

## Accept gate

- Per-level coherence reported for L06 and L08 Tbilisi, on continuous variables, with analogue-set
  overlap.
- Per-band distances built; the Tbilisi L06↔L08 per-band profile reported.
- Test 3 run as a two-basin discrimination, with the matched Sahelian basin identified by query.
- κ of the selected 13 reported.
- **Dilution: confirmed or not, stated plainly.** Either answer is a result.
- Karl reviews.

## Out of scope

Mahalanobis implementation. Seasonality variables (`pre_mm_s01..s12` — the Test 1 fix; a separate
question, and the answer is likely two derived indices, not twelve monthly columns). L08 as a
general similarity surface. Any UI. Any change to the selected variable set — WO4d diagnoses, it
does not re-select.
