# WO4c — Basin similarity: research notebook

**Phase:** DEMO · Track 2
**Kind:** Research. Notebook only — no surface, no API, no engine change.
**Branch:** `demo` (notebook + findings commit directly)
**Precondition:** WO4b complete.

---

## Why this exists

The EDOPS research programme is correspondence: *do cultural practices correspond to particular
environmental settings?* That question cannot be asked without a defensible way to say two settings
are alike. Similarity is not a feature — it is the basis of classification, and classification is
what the correspondence work runs on.

EDOPS already ships classifications (biome, ecoregion, climate clusters) — all borrowed, all
opaque. This notebook is where EDOPS earns its own.

**Unit: basin-to-basin, L06.** The basin is the only unit whose signature is *primitive* — computed
directly from BasinATLAS, not aggregated. Every other unit (polity, ring, polygon) is a set of
basins with an aggregation method in between. Polity similarity, if it comes, is a function over
basin similarity — so solving it here first avoids solving the metric and the aggregation at once.
L06 (16,397 basins) is the regional scale at which "environmental setting" is a coherent notion.
**L08 is out of scope.**

---

## Step 1 — Characterize the space

Read `public.basin06` directly (`db_connect()` / `pd.read_sql`). Raw BasinATLAS columns are all
present; the API's `representative_raw: None` gap (WO4b) does not apply here.

- Correlation matrix across the continuous signature variables at L06.
- **How many independent dimensions are actually there?** 40-odd variables that are really 6–8
  dimensions is a finding about the signature, publishable independent of any metric.
- Is Σ invertible, or near-singular? (Strong redundancy → unstable inversion → Mahalanobis
  distances become noise. Need to know before relying on it.)
- PCA for inspection: what does PC1 load on? If it reads as "moisture" and PC2 as "terrain
  energy," that is worth more to a paper than any distance number.
- **Per-variable transforms** decided here, on the distributions, not by rule. Precedent exists:
  discharge is skewness ~41 and log is canonical (DIS.3). Note raw vs. percentile-score choice
  per variable; both are available (`basin06` raw, `basin06_scores` materialized PERCENT_RANK).
  Percentile-ranking flattens distribution shape — two basins 5 points apart in the arid tail are
  more different than two 5 points apart at the median. Where that matters, say so.

**Step 1 is a deliverable on its own.** Even if no metric validates, the correlation structure of
the EDOPS signature is a result.

---

## Step 2 — Select fields, deliberately, per band

**Not blind decorrelation.** Mahalanobis' Σ⁻¹ or PCA will weight automatically — principled, but
uninterpretable: you cannot tell a reader *why* two places came out similar when the weighting is a
40×40 matrix.

Instead: choose variables that are conceptually distinct and empirically non-redundant, using
CHAR's ρ matrix and the §4 typology (continental-gradient / network-topology / scale-dependent /
local-anomaly) as the material. The result is a vector you can **name** — *"similarity on moisture,
thermal regime, terrain energy, substrate"* — which a geographer can defend, argue with, publish.

Known redundancy to respect: **aridity ↔ precipitation ρ = 0.827** (WO1a F1a.1). Including both
makes moisture vote twice. This is the mechanism the selection exists to prevent.

Mahalanobis then serves as a **check on the selection**, not a substitute for it: if Σ⁻¹ over the
chosen set still down-weights something substantially, the selection was wrong.

**The signature stays whole.** The comparison vector is a separate derived product — this does not
prune the signature.

---

## Step 3 — Distance per band, plus composite

Per-band distance (A–E) **and** a composite. Per-band is not a nice-to-have: it is the honest
answer to *"similar in what respect?"* It lets the instrument say *"twins in bioclimate, opposites
in terrain"* — which is more useful and more truthful than a scalar, and is something no biome
label can say. The composite sits on top as a summary, not as the answer.

Include **upstream (u) values** in at least one framing. Two river-mouth basins with identical
local climate and opposite water provenance should come out far apart; if they don't, the s/u
apparatus is not doing work.

Compute is not a constraint: 16,397 basins against one query point is brute-force in milliseconds.
No approximate-NN index needed.

---

## Step 4 — Validate against known analogues

*(Revised 2026-07-14 — CC/KG. Original spec centred validation on Timbuktu. Concern: Timbuktu,
Cairo, and Baghdad are all extreme outliers on the upstream distribution. If the metric separates
them, it may be doing so trivially — the upstream values are so large they dominate any distance,
confirming the upstream fields have weight, not that the metric is well-calibrated for ordinary
basins. Validation must span the typology space, including mundane cases.)*

The metric must **recover analogues that are independently attested**, and it must do so **better
than a biome label**, or EDOPS has produced an expensive route to Köppen.

Four tests spanning the typology space:

1. **Mediterranean five — floor** (Mediterranean basin, coastal California, central Chile, the Cape,
   southwest Australia). Universally accepted analogues. A biome label already gets this right —
   so this is the **floor, not the ceiling**. If the metric misses it, stop and reconsider.

2. **A mundane matched pair — ordinary-basin check.** Maritime temperate: Rhine lowlands (NW
   Europe) vs. Willamette Valley (Pacific Northwest). No extreme upstream values, no exotic
   provenance — two wet, mild, low-relief basins that should come out close. Validates that
   the metric works for the 95% of basins that are not outliers. If this fails, variable
   selection is wrong.

3. **Provenance-contrast pair within a biome — controlled upstream test.** Two Sahelian basins
   with matched local climate (similar aridity, precipitation, temperature): one lying on or
   near the Niger (exogenous water supply) and one that is genuinely rain-fed Sahel (e.g.
   interior Burkina Faso or Mali, away from a major river). **If including upstream values
   separates them and excluding it does not, the s/u apparatus is vindicated** — and EDOPS
   has done something no biome label can. Because neither basin is an extreme outlier, the
   separation must come from the metric working, not from a 500× upstream anomaly swamping
   the distance. This test is the core claim.

4. **Tbilisi — metric stability test.** Does the analogue set survive L06 → L08? WO3 proved
   the *biome label* does not (Temperate Broadleaf → Deserts & Xeric Shrublands at L08).
   This is a *metric property* test — scale stability — not an analogue-recovery test. Run
   both levels; report whether the top-N analogue set changes less than the biome label does.
   A stable analogue set at both levels is a strong claim.

---

## Deliverables

- `notebooks/edop/demo/wo4c_basin_similarity.ipynb` (`# Cell N` convention; `db_connect()`;
  output path derived from module location)
- `output/edop/demo/wo4c_*` — correlation matrix, selected fields per band, analogue results
- `docs/edop/demo/wo4c_findings.md`

## Accept gate

- Correlation structure reported: how many independent dimensions, Σ conditioning, PCA loadings.
- Selected fields per band, with the reason for each inclusion/exclusion.
- All four tests run, with results **whichever way they fall**.
- **A negative is a real result.** If no defensible framing recovers the Mediterranean five, that is
  a serious finding about the signature's construction and it gets reported as such — not smoothed
  over, not retried until it passes.
- Karl reviews before anything is proposed for the surface.

## Out of scope

L08. Polity/polygon similarity (a function over basin similarity — later). Any UI. Approximate-NN
indexing. Seshat/D-PLACE correspondence — **but note in the tracker: the comparison vector is
Phase-4 correspondence substrate.** Building it here is groundwork, not a competing effort, and it
should not be re-derived later.
