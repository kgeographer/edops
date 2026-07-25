# WO8a findings — Environment–culture correspondence: descriptive probes (Societies)

**Work order:** `docs/cdop/pilot/wo8a_culture-probes.md`
**Branch:** `cdop_wo8a` (cut from `cdop_pilot`). **Type:** descriptive notebook, no engine / API / UI.
**Notebook:** `notebooks/cdop/wo8a_culture_probes.ipynb` (12 cells + accept-gate markdown, all run
2026-07-25). **Figures/data:** `output/cdop/wo8a_*.png`, `output/cdop/wo8a_substrate.parquet`.
**Status:** complete — accept gate **PASSED**; three decisions locked (below).

WO8a builds the shared substrate and *draws the compared dimension before theorising any metric*
(the project's standing rule). It runs no statistical test — that is WO8b (PERMANOVA/PERMDISP with
within-family restricted permutation) on the bet this notebook selects.

---

## Part A — the shared substrate (Cells 2–3)

`dplace.societies` (EA slice, `contribution_id='dplace-dataset-ea'`) → `dplace.society_basin`
(`basin_level=8`, `basin_id` = hybas_id) → `basin08` + persist view `v_basin08_persist_rev2`, with
EA042 subsistence + EA034 religion via `dplace.data`/`dplace.codes`. Persisted to
`output/cdop/wo8a_substrate.parquet` for WO8b/8c reuse.

- **1,133 of 1,291 EA societies join at L08 (87.8%)** — matches WO4 Part 3 exactly. 971 unique basins
  (societies cluster; many share a basin). 0 EA042/EA034 fan-out. All 1,133 have a non-missing EA042.
- **158 unjoined societies dropped** — a named scope limit (islands/coastal), not a bug.
- **Container caveat rides along, disclosed not fixed** (WO4 0B / WO5 Part C): basin mean ≠ site; at
  L08 ~13.4% still show a >2 °C implied gap. A correct read of the source; not a metric to correct.
- **Temperature sourced from the persist-view monthly mean (already °C)**, not raw `tmp_dc_syr`
  (stored ×10) — sidesteps the ×10 trap. `−9999` masked → NaN before use.
- Reused production classifiers (`cc.classify_modality/classify_phase`) and
  `se._circ_conc_angle`/`se._row_normalise` rather than re-deriving. Every WO-named predictor
  `schema_key` verified against the catalog (no drift; all `pre-1500 valid` or `full-record`).
- Modality distribution textbook: 1-season 924 (82%), 2-season 98, aseasonal 61, arid 34,
  undetermined 16.

---

## Part B — the named bets (Cells 5–8)

Correlation matrices drawn **first** (Cell 5), the composite-distance hazard made visible. Classical
PCoA (hand-rolled Torgerson) on z-scored Euclidean distance; aridity log1p-transformed.

**Within-bet correlations (the hazard, flagged for 8b — all |r| < 0.90, so no catalog co-variation
guard is violated; these are "correlated but legitimately distinct" pairs the naive metric
over-counts):**

- **Water is ~one axis measured three times:** ari↔precip 0.76, precip↔runoff 0.83, ari↔runoff 0.66.
  The deliberate "water from above / flowing nearby" split bought little independence.
- **Climate envelope adds a thermal block:** temperature_annual ↔ tmp_seas_amp **−0.83** (textbook
  continentality). Euclidean over-weights the 3-member water block vs the 2-member thermal block.
- **Landscape:** elevation ↔ slope 0.51 (not flagged); terrain only weakly tied to climate
  (elevation's strongest is −0.36 with temp = lapse rate) → it adds a genuinely fresh dimension.

**The bet ladder (the pictures):**

| Bet | PCo1 · PCo2 | Reading |
|---|---|---|
| Water | 83% · 12% | One wetness gradient (boomerang = arch artifact). Poles separate — pastoralism at the dry tip, agriculture on the wet arm — but the moderate-wetness bulk overlaps. **The floor.** |
| **Climate envelope** | **58% · 32%** | Temperature opens a real second axis. The dry-left jam resolves **vertically**: cold foragers upper-left, warm-dry pastoralists lower-left; agriculture holds the wet-mild quadrant. Three modes → three regions. **The winner.** |
| Landscape | 42% · 30% | Terrain adds a third axis's worth of variance (top-2 90%→72%) but it is **subsistence-orthogonal** — every mode scatters into it alike. Elevation *smears*, does not *separate*. Over-reaches. |

The WO's live question — does elevation separate or smear? — is answered by looking: **smear**.
Physically sensible (elevation is adaptable: terraces, high-altitude settlement).

---

## Part C — the seasonality-representation fork (Cell 9)

Three *pure* representations of the precipitation-seasonality slot, each its own distance, no
combination (Gower deferred). A few hyper-arid basins have zero/flat precip → `pre_concentration`
and the raw-curve norm are undefined (NaN), and classical PCoA propagates a single NaN across the
whole double-centred matrix (empty panel, "PCo 0%"). Fixed with complete-case *per representation*
(rep1 drops the undefined-concentration basins, rep2 the flat curves; modality keeps them as `arid`).

- **rep1 `pre_concentration` scalar** — 1-D (PCo1 100%). The **two-peaks-cancel bug is visible**:
  2-season basins land in the *middle* of the concentration axis, indistinguishable from mildly
  seasonal unimodal (the Mombasa/WO1 failure).
- **rep2 raw 12-value curve (correlation)** — a **phase ring** (PCo1 64% · PCo2 14%): curves arrange
  by *when* the wet season falls; 2-season pulls to distinct ring positions (modality emergent, no
  bug). Faithful and information-rich (the WO6b backbone).
- **rep3 WO7 modality class** — five tight blobs; the lossy discretization of rep2.

**Cross-cutting result — the whole top (EA042) row shows no subsistence separation in any
representation.** Rainfall *timing/shape/modality* is largely orthogonal to subsistence — what
separates farmers from herders is *how much* water and *how warm*, not *when* the rain arrives. This
**refutes the WO's stated expectation** that rep3 (modality class) would separate cleanest; the
picture wins.

**Decision 2:** if 8b carries a seasonality term at all, use the **raw curve** (faithful, bug-free);
but it is **non-load-bearing** for subsistence. Climate envelope's power is aridity + temperature.

---

## Part D — the modality-standalone bet (Cells 10–11)

**The crosstab (Cell 10) is the informative lens; the class-disagreement PCoA (Cell 11) is not.** The
PCoA collapses to one blob per climate class, each holding the full subsistence range — it shows only
"classes hold everything." The crosstab extracts the marginal enrichments the blobs (and the
continuous ordination) hide:

- **Pastoralism → 25% arid** (every other type ≤ 4%). The sharpest single environment↔subsistence
  signal in the notebook. Herders live where you can't rain-fed farm.
- **Intensive agriculture → 4% arid** (11 societies; extensive ag = 0%). **Irrigation** — intensive
  farming is the only farming that reaches into arid basins (Nile, Mesopotamia, oases).
- **Fishing / Gathering → 1-season | cool-wet** (~40% each). Cool-season-rain coastal-temperate
  foragers — the **Pacific-NW salmon-fisher / Mediterranean-forager** pattern, a validating result.
- **Extensive agriculture → 1-season | no thermal cycle** (~56%): tropical/subtropical summer-rain
  farming.

So the discrete-class view is a **weak but real secondary axis** that surfaces specific, interpretable
associations — the coarse corroborator role the WO scoped.

**Decision 3:** keep Part D as the categorical corroborator, **read via the crosstab, not the PCoA**.

---

## Accept gate — PASSED; the three decisions

EA042 subsistence visibly separates (most clearly in Climate envelope) → the instrument is calibrated
on the positive control; WO8b has a legitimate ruler.

1. **Bet into 8b → Climate envelope.**
2. **Seasonality representation → raw 12-value curve if any, flagged non-load-bearing.**
3. **Keep modality-standalone (Part D) → yes, via the Cell 10 crosstab.**

### Headline — environment sets bounds, it does not determine

One near-hard constraint (**water for rain-fed agriculture**; intensive ag reaches arid only via
irrigation), one soft gradient (**temperature/continentality**: foragers lean cold, fishers cool-wet),
and broad adaptability everywhere else (rainfall timing, elevation). The instrument is honest enough to
*show* this rather than manufacture separation — a credibility result going into 8b/8c.

**Consequence for 8c:** EA042 is near-tautologically environmental and still only *partially*
separates. A contested trait (EA034 high-gods) should be expected to couple *weakly* — the value is an
honest effect size + a clean family-controlled null (positive, null, or dispersion-confounded), not a
big separation. Set that expectation before the test.

---

## Carried forward / notes for WO8b

- **Bet = Climate envelope**, z-scored Euclidean baseline; the Cell 5 |r|≥0.70 pairs (water triple,
  temp continentality −0.83) are the **Mahalanobis-or-drop candidates** — resolve the metric there,
  with the real question attached (WO8a made the hazard visible; it did not resolve it).
- **`ele_mt_sav` (elevation_mean) and `soc_th_sav` (soil_organic_carbon) are catalog-`planned`** —
  read directly from `basin08` in the notebook. `elevation_mean` is also the standing
  deferred-register catalog-status item. Not needed for the Climate envelope bet (Landscape/held
  Bet 4 only).
- **Substrate parquet** (`output/cdop/wo8a_substrate.parquet`) is the reusable core; WH Cities (a
  separate future thread) shares only this Part A distance core, with a different retrieval head.
- **Held Bet 4 — Agriculture suitability** (soil texture + SOC) not opened; opens only if 8b's
  subsistence contrast asks for it.
