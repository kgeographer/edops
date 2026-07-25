# WO8a — Environment–culture correspondence: descriptive probes (Societies)

**Status:** draft for review.
**Prior:** `wo4_findings.md` (L08 `society_basin` join; family crosswalk 92.6%; container
exposure 13.4% > 2 °C at L08), `wo6b_findings.md` (raw-curve backbone; modality emergent),
`wo7_findings.md` (climate classes; phase quantity validated against climatology),
`CDOP_PILOT_tracker.md` (the WH-Cities / D-PLACE fork), `EDOPS_variable_catalog_v0.3.tsv`
(predictor eligibility).
**Type:** notebook, descriptive only — no engine / API / UI change. CC authors; Karl runs
cell by cell.

Goal-setting with provisos. CC discovers implementation particulars; Karl reviews every write.

---

## Why

The Societies tab today **gestures**: markers show where a cultural type sits, and a listing shows
which opaque-labelled regions it falls in — OneEarth ecoregion-by-realm (prose labels, no formal
environmental content) and the distrusted `basin08_pca_clusters`. It can say "supporting-morality
societies pile up in Sahelian savanna and the Mediterranean," and no more. It cannot say what
environmental *dimension* the pile-up is, or whether it is anything beyond societies being
neighbours.

EDOPS's contribution is to swap the opaque label for a formal, continuous, decomposable signature.
The eventual question is **does cultural trait X covary with environmental setting, net of shared
ancestry and diffusion** — an effect size, a phylogeny-restricted null, a decomposition of which
signature dimensions carry the association. That test is WO8b/8c.

WO8a is the step before the test: **build the shared substrate, and draw the compared dimension
before theorising about any metric.** It is the project's own standing rule (it caught every real
bug in the WO6 arc; its one omission cost four design rounds), applied to the Societies question.
If the near-tautologically-environmental control trait does not *visibly* separate in a picture, no
F-ratio will save it — and we learn that in an afternoon, not after a build. WO8a produces
comparable pictures and one course-setting decision; it runs no test.

## Predictor eligibility (locked this session)

Static environmental predictors must be `pre-1500 valid` or `full-record` in the catalog. The
societies' focal years are 1850–1940 (the "ethnographic present"), so a predictor's value must be
the same then as in the BasinATLAS baseline. This excludes the entire `modern-only` set (cropland,
pasture, human footprint, population density, GDP, HDI) — testing subsistence against ~2000 CE
observed cropland is anachronistic or circular. The temporal bands (LMR / HYDE / eVolv2k) are a
separate analysis, not columns in this matrix. The rule kills the obvious "agriculture" variable
and forces the agriculture bet (held, below) onto soil + climate + water, which is the more honest
instrument regardless.

---

## Part A — The shared substrate (society → basin → signature)

Assemble, once, the table WO8b/8c consume and WH Cities will later reuse: for each L08-joined EA
society, its `hybas_id` and its historically-valid source (`s`) signature values. Keyed by
`society_id` + `hybas_id`, persisted for reuse.

Provisos:

- **Consume the existing join; do not re-derive it.** WO4 Part 3 recorded `society_basin` at L08,
  1,133 of 1,291 EA societies (87.8%). Confirm the table name and that it is L08-keyed before use;
  flag if it differs from what WO4 left.
- **The ~158 unjoined societies (islands, coastal) are dropped from the test.** This is a scope
  limit to name in the notebook, not a bug to fix. The instrument speaks for the 1,133; it makes no
  claim about the 158.
- **The container caveat rides along, disclosed, not fixed.** Basin mean ≠ site; at L08 this is the
  better level but 13.4% of societies still show a > 2 °C implied gap (WO4 Part 0B). This is a
  correct, direct read of the source data (WO5 Part C — nothing to fix because nothing is wrong),
  and it is disclosed, per "no one reads caveats." It is not a metric to correct.
- **Source (`s`) values.** The society's own basin is the read of "the environment of this place."
  Upstream / allochthonous water (Timbuktu-on-the-Niger, a desert basin with a river through it) is
  a real second question — noted, not built here; `runoff` in Bet 1 is the local-water proxy, and
  discharge/upstream is a candidate only if a bet needs it later.
- **Mask `−9999` before anything; zero is a value, never absence** (CLAUDE.md). Trait values come
  from the D-PLACE CLDF tables already imported (WO4 schema audit), joined to the EA slice.

## Part B — The named bets (continuous)

For each bet: z-score its continuous variables, **inspect the within-bet correlation matrix first**
(high within-bet correlation is a finding to report, not to bury — it is the composite-distance
hazard showing itself), build a distance matrix, compute a **PCoA** (principal coordinates — the
2D ordination that pairs with a distance matrix and with the eventual PERMANOVA), and colour
**EA042 subsistence** on. Overlay the **WO7 modality class** as a second colouring of the same
ordination.

The bets, in real `schema_key`s:

- **Water** — `aridity_index` (log-transformed; P/PET water balance — "water from above"),
  `precipitation_annual` (absolute water in; correlated with aridity but not ≥ 0.90, so it carries
  the desert-vs-tundra distinction aridity alone blurs), `runoff` (mm/yr, full-record — "or flowing
  nearby," cleaner than cumulative `discharge_annual`). The minimal "people need water" bet, split
  deliberately across both water sources.
- **Climate envelope** — Water plus `temperature_annual` (thermal level) and `tmp_seas_amp`
  (warmest-minus-coldest swing; phase-independent continentality, not the `tmp_concentration`
  scalar). The standard bioclimatic-envelope bet.
- **Landscape** — Climate envelope plus `elevation_mean` and `slope_deg`. The bet where terrain is
  expected to begin dominating the ordination — and that expectation is itself the test (elevation
  is adaptable: terraces, high-altitude settlement). Whether elevation *separates* or merely
  *smears* the subsistence groups is directly informative.

Provisos:

- **Catalog co-variation constraints, baked in:** never both `temperature_annual` and
  `temperature_min` (co-vary ≥ 0.90); never two discharge variables (annual/max/min co-vary
  ≥ 0.90). Both would inject fake dependency, the WO1–WO6 composite-distance defect in miniature.
- **`elevation_mean` is not API-wired** — it is `planned`, present in `basin08` as `ele_mt_sav`.
  Read it directly from the DB in the notebook (a research record reads the DB directly; extraction
  is one-directional). Flag it so CC does not look for it in the signature payload, and so it is
  visible if Landscape ever graduates toward anything productiony.
- **Distance metric: z-scored Euclidean as the descriptive baseline, with the correlation matrix
  shown.** Where a bet carries a strongly correlated pair, flag it as a candidate for Mahalanobis
  or variable-drop in WO8b — do not silently absorb it. WO8a's job is to make the hazard *visible*,
  not to resolve it; resolving the metric is 8b's, with a real question attached.
- **Held: Bet 4 — Agriculture suitability**, not opened in 8a. `pct_clay` + `pct_silt` (drop
  `pct_sand` — catalog flags clay+silt+sand ≈ 100, compositional; all three inject a fake linear
  dependency) plus `soil_organic_carbon` (fertility proxy; `soc_th_sav`, also not API-wired), on
  the climate core. Named so it is not rediscovered; opens only if the subsistence contrast in 8b
  asks for it (soil matters for farmers, less for pastoralists — Karl).

## Part C — The seasonality-representation fork

Within one bet (Climate envelope is the natural host), fill the seasonality slot three ways and
draw all three PCoAs side by side. This settles empirically — by looking — which representation
carries into 8b, rather than by assertion.

1. **`pre_concentration` scalar** — the WO6-known-weak link, included *precisely so its failure is
   visible*. Its two-peaks-nearly-cancel defect is the exact bug that broke Mombasa in WO1; if it
   is going to quietly re-enter a distance matrix, it should do so where we can see it fail.
2. **Raw twelve-value precipitation curve** — the WO6b backbone (correlation on the mean-centred
   curve). Faithful, heavier.
3. **Discrete WO7 modality class** — categorical, validated against published climatology, ported
   cleanly to any basin. The lightest and the only one with external validation.

Provisos:

- **Keep the three representations pure — no combination in 8a.** The point is a clean comparison
  of pictures. Mixing a categorical class with continuous axes is legitimate *only* as Gower
  distance (per-variable natural metric, declared contribution — the mixed-type analogue of the
  lens discipline), never as z-scored concatenation. Gower is named here so it is not reinvented as
  naive concatenation; it is deferred until a bet is shown close-but-incomplete and there is a
  reason to combine.
- Expectation (to be confirmed or refuted by the picture, not assumed): representation 3 gives the
  cleanest subsistence separation, because it dodges the bimodal-cancellation bug and carries WO7's
  validation. If the picture disagrees, the picture wins.

## Part D — The modality-standalone bet

A distance built purely on class membership: two societies are close iff they share modality (and,
as a second variant, modality × phase). PCoA, and how EA042 distributes across the classes.

Provisos:

- This is a legitimate standalone bet, not a curiosity — the discrete-class route with WO7
  provenance, and the coarse categorical corroborator the Phase-4 scoping wanted (a second method
  landing on the same fact as the continuous bets, or not).
- Coarser than the continuous bets by construction (a class cell holds hundreds; WO4 Part 4 found
  categorical typology concretely coarser than the continuous lens). Report it as coarser, not as a
  competitor at a different setting.

---

## Accept gate

**Single, visual, and able to fail.** In at least one bet's PCoA, does **EA042 subsistence visibly
separate**? EA042 is near-tautologically environmental — foragers, pastoralists, and intensive
farmers occupy different environments almost by definition. If it does *not* separate, the
instrument is suspect and nothing it later says about a contested trait is trustworthy. This is the
positive-control calibration, done by looking.

The gate resolves into three decisions, then stop:

- which **bet** carries the cleanest subsistence separation into 8b;
- which **seasonality representation** (Part C) it uses;
- whether the **modality-standalone bet** (Part D) is informative enough to keep as the categorical
  corroborator.

Supporting: within-bet correlation matrices reported for every bet; the container caveat and the
158-society scope limit stated in the notebook; notebook conventions observed (`# Cell N`,
`print(df.to_string())`, `db_connect`, no bare-DataFrame last expressions).

---

## Next (8b, 8c) — contingent, not drafted

Sketched so the arc is visible; specified only after 8a's pictures land, per the WO6/WO7 rhythm.

- **8b — first test, on the positive control.** PERMANOVA of EA042 on 8a's winning bet +
  representation, with **restricted permutation within language family** (the Galton control,
  native to the method — family crosswalk from WO4 Part 3), and **PERMDISP** run alongside so a
  dispersion difference is not misread as a location shift. Calibration of the ruler: large R²,
  clears the family-restricted null, and which dimensions carry it (decomposition).
- **8c — the contested question.** The calibrated instrument pointed at EA034 high-gods (or another
  chosen trait). An honest effect-size + null-distribution result — positive, null, or
  dispersion-confounded — reported as found.

---

## Out of scope

- **Any test.** PERMANOVA / PERMDISP is 8b, not 8a. 8a draws; it does not decide significance.
- **Gower / any combination of representations.** Deferred and named (Part C proviso); not built
  until a bet is shown close-but-incomplete.
- **The held agriculture bet.** Opens only if 8b's subsistence contrast asks for it.
- **Any container-problem fix.** Disclosed, never fixed (WO5 Part C).
- **The 158 unjoined societies.** A named scope limit, not addressed here.
- **WH Cities.** A separate future thread; it shares only the Part A substrate (the distance core),
  onto which it puts a ranked-retrieval head plus a wiki-text channel — a different head on the same
  engine, not this WO.
- **Any new tab, route, dataset, or UI.** 8a is a notebook.