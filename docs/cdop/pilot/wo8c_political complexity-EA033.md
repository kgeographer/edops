# WO8c — Environment↔culture correspondence: political complexity (EA033)

**Status:** draft for review.
**Prior:** `wo8b_findings.md` (Climate-envelope bet + drop-to-representative metric; 84% subsistence
collapse; Freedman–Lane partial; PERMDISP; the near-collinearity hazard), `wo8a_findings.md`
(substrate; "environment permits, doesn't determine"), `wo4_findings.md` (L08 join; family
crosswalk 92.6%), BasinATLAS info sheets P01 (elevation `sav/smn/smx/uav`), L03/L04 (PNV, 15
nominal classes, `pnv_shares` jsonb).
**Type:** statistical-test notebook, no engine / API / UI. CC authors; Karl runs cell by cell.

Goal-setting with provisos. CC discovers implementation particulars; Karl reviews every write.

---

## Why

WO8a and WO8b were **calibration** — traits whose answers we could check against intuition
(subsistence is environmental; sedentism tracks farming country), run to prove the instrument works
and that the phylogenetic control bites. It passed. WO8c is the **first genuinely speculative test**:
the first trait pointed at a question we cannot pre-check. That changes the success criterion. 8b
succeeded by *working*; 8c succeeds by producing an *honest answer to an unknown*, which means **a
null is a fully legitimate — and on the 8b base rate, the modal — outcome**, not a failure.

The trait is **EA033 jurisdictional hierarchy** — an ordinal ladder from acephalous (no authority
beyond the local community) through chiefdoms to states, 1,012/1,133 coded. It is the contested
rung, and the rehearsal for high-gods (8d): complexity and moralizing-gods are tightly coupled in
the big-gods debate, so the covariate discipline and reporting stance 8c establishes carry forward.

**What 8c actually tests — and what it cannot.** The *marginal* complexity↔environment test will
light up strongly and read largely as subsistence, by construction: EA033 is empirically correlated
with EA042 in D-PLACE (states co-occur with intensive agriculture, acephalous societies with
foraging), so the marginal number re-measures that correlation. It is uninformative here. The whole
question is the **nested residual** — is there an environmental signal specific to political
organization that survives the subsistence (and settlement) substrate.

The literature's environmental hypothesis for complexity is **circumscription** (Carneiro: states
arise where arable land is bounded by desert/mountain/sea so defeated populations cannot disperse
and stratify instead) — a claim about the *boundedness of productive land*, a relational spatial
property, **not a climate scalar**. The current Climate-envelope signature almost certainly cannot
express it (enclosure is a basin-neighborhood computation not yet built — see Forward). So **8c does
not test circumscription.** It tests whether complexity tracks the *measurable* environment (climate,
plus a cheap within-place terrain lens) net of culture. State this scoping plainly in the notebook:
a null does not refute circumscription; it leaves circumscription untested for want of the variable.
This is the two-nulls problem, named up front rather than discovered in the result.

## Predictor eligibility

Climate-envelope bet + drop-to-representative metric, carried from 8b: `ari_log`,
`temperature_annual`, `tmp_seas_amp`. All `pre-1500 valid` / `full-record`.

- **Terrain is period-robust** — elevation/slope are physical and stable on century scales, so
  present-day DEM values are valid for the 1850–1940 ethnographic present. The cheap terrain lens
  (Part D) is therefore eligible.
- **Land-use / human-modification layers are not, and cannot be back-projected.** Modern cropland,
  pasture, irrigation-equipped-area (L10), degree-of-regulation (L07) are `modern-only` snapshots;
  for the correspondence programme they can serve only as *audit flags* (which societies sit in
  heavily-modified basins), never as predictors. Standing limit, logged: the human-water relationship
  changed radically over the periods CDOP will eventually address (cf. Mostern's Yellow River work),
  so a present-day modification raster is categorically wrong for the past, not merely noisy.

---

## Part A — substrate extension

Extend `output/cdop/wo8b_substrate.parquet` with **EA033 jurisdictional hierarchy** (ordinal, from
`dplace.data`/`dplace.codes`). Subsistence, fixity, and the language-family crosswalk are already
present from WO8b.

Provisos:

- EA033 coverage **1,012/1,133**; the uncoded drop (named scope limit). Report the eligible n after
  intersecting EA033 + EA042 + EA030 + family (all four needed for the nested test).
- **Report cell counts before any test** — EA033 × subsistence, EA033 × fixity, EA033 × family.
  Complexity, subsistence, and fixity are three near-collinear cultural variables; the nested residual
  rests on whatever independent complexity-variation survives holding the other two, and if that is
  thin the residual is an overlap artifact, not a fact about nature. Look first.

## Part B — covariate structure and metric

Metric: **drop-to-representative** (`ari_log`, `temperature_annual`, `tmp_seas_amp`), carried from 8b
with its sensitivity already established; no re-litigation unless a correlation check on this sample
diverges materially.

Covariate set: **subsistence + fixity** is the headline nested control (Karl's call), but run
**subsistence-alone alongside it** — not optional, for a specific methodological reason:

- **Fixity may be a mediator, not a confound.** If the causal path is environment → settlement →
  complexity, then controlling for fixity *removes part of the very environment→complexity signal 8c
  is trying to detect* (over-control / adjusting for a mediator). Subsistence is a cleaner confound
  (economy as common cause); fixity is ambiguous. So report both: complexity net of {subsistence} and
  net of {subsistence + fixity}. The **gap between them** measures how much fixity absorbs, and tells
  you whether the subsistence+fixity number is a confound-control or a signal-eater. Do not headline
  the two-covariate number without the one-covariate number beside it.

## Part C — the test

Both nested specifications (above), each with **factor** (ordinal collapsed to a declared coarser
grain if cell counts require — state the collapse as a convention, do not fit it to cases) and
**ordinal-trend** (db-RDA, EA033 as ordered predictor — closer to "environment climbs the complexity
ladder" than "the centroids differ"), plus the **marginal** for completeness (expected strong,
expected mostly subsistence — reported as the confound baseline, not a finding).

Provisos:

- **Freedman–Lane residual permutation within family**, now partialling *two* covariates for the
  subsistence+fixity spec. The restricted-partial scheme is the same as 8b's but with a larger
  reduced model; CC to confirm the library expresses it correctly (naive full-label permutation gives
  the wrong nested null).
- **PERMDISP alongside each spec** — complexity groups may differ in environmental breadth as fixity
  did; a spread difference must not be read as a location shift.
- **The collinearity caveat is worse here than in 8b** (three near-collinear cultural variables, not
  two) and must be stated wherever the confound-share is reported.

## Part D — the cheap terrain lens

A parallel lens (its own physical question — *is this rough / broken country* — one lens, one
question), not folded into the Climate-envelope distance. Terrain characterization sampled at the
society's location: **local relief / ruggedness** and a **landform-position ratio**
(`(mean−min)/(max−min)`: near 0 = mass at the floor, valley-like; near 0.5 = uniform slope).

Provisos:

- **This tests ruggedness, not enclosure — and the distinction is load-bearing.** Ruggedness/local
  relief is a *fragmentation* proxy (rough country divides polities → possibly *less* complexity);
  circumscription/enclosure is a *containment* proxy (bounded arable land → possibly *more*
  complexity). These are different variables with **opposite expected signs**, and this lens measures
  only the first. So the terrain lens has *no clean directional prediction*, and a null on it narrows
  but does **not** close the terrain question — enclosure is a different, unbuilt, relational grain
  (Forward). Its job is to partially disambiguate the two-nulls problem: if ruggedness lights up,
  terrain matters and enclosure becomes worth building; if not, terrain is narrowed, not excluded.
- **Prefer point-window terrain from the D-PLACE coordinate over basin `smx−smn`.** The point-window
  (ruggedness in a fixed radius around the coord, straight from the DEM) dodges the container problem
  — no basin-mean smearing, no dependence on where the L08 polygon fell relative to the valley floor.
  Basin `smx−smn` is the already-joined fallback. CC's implementation call; flag the preference.
- **Representative-point caveat, with a quiet alignment.** The D-PLACE coordinate is often a centroid
  or type-site, a weak terrain sample for a mobile or large-territory society — but *most reliable for
  fixed, nucleated societies*, which is exactly the high-complexity end 8c most wants to get right.
  Note it; do not over-trust it for the low-complexity end.

---

## The expectation (stated up front)

On the 8b base rate (strong marginal, near-total collapse under the economy control) and the
subsistence routing, the **modal expected outcome is a null or sub-floor residual** net of
subsistence (± fixity). This is stated not as a mechanistic prediction (unlike 8b's aridity/temperature
call) but to **pre-arm the reporting stance**: a small surviving residual is *expected noise at
n≈1,000*, not a discovery, and must clear the pre-set floor to be interpreted at all.

## Precondition — the effect-size floor (a committed rule, not a pre-named number)

The reporting stance needs a floor below which a surviving residual is reported as *no interpretable
independent effect*. The hazard to avoid is **circularity**: choosing a threshold by looking at the
cliff in *this trait's own result* and then reporting the result against that threshold is using the
answer to set the bar the answer clears. But the fix is *not* to name a number cold (there is no
principled a-priori R² constant in this setting; effect sizes are n- and domain-specific). The fix is
to **pre-commit the rule now and let the data set the value** — which keeps the floor data-driven
(read off a distribution) while removing the circularity (the distribution is the null, not the
observed effect).

**The rule, committed here:** the floor is the **95th-percentile R² of the family-restricted
permutation null**. The permutation runs already produce a whole distribution of R² values under
"the trait means nothing"; its 95th percentile is the largest effect noise routinely manufactures
under your own null at your own n and covariate structure. A residual below it is, by construction,
indistinguishable from noise. This is decided *before* complexity's number is in hand — but the
*value* it yields is not something Karl (or CC) controls; it is read from the null.

- **Cross-check anchor:** the WO8b fixity residual (R² ≈ 0.01–0.03), which the instrument's own
  calibration already adjudicated as *not interpretable*. An effect smaller than the leftover of a
  trait you've already judged uninterpretable is uninterpretable. If the permutation-null 95th
  percentile and the fixity-residual anchor disagree materially, that disagreement is itself
  informative about how much n≈1,000 is inflating small effects — report it rather than picking one.
- **If the null-R² distribution has no clean upper edge** (a smeared plateau rather than a cliff — the
  situation the modality `cv` histogram was in), do not fit a cliff that isn't there: use the
  95th-percentile convention and *state that no natural break existed*. Same discipline as the `cv`
  cut.
- The notebook may compute the residual; the **verdict** (interpretable vs no interpretable
  independent effect) is the residual read against this floor.
- **Reference (Karl's check-it-yourself anchor, statistics side — auditable):** Anderson, M.J.
  (2001), *A new method for non-parametric multivariate analysis of variance*, Austral Ecology 26:
  32–46 — the originating PERMANOVA paper, including the permutation construction of the null against
  which effect size is read. The permutation-percentile-as-floor practice is the standard companion to
  the effect-size-not-p-value stance already adopted in this arc.

## Anthropology claims to verify — the offloading guard

Flagged for confirmation before load-bearing; no anthropologist on the team, so Karl source-checks
("two more eyes"), and any test is framed as *testing a named hypothesis*, never *confirming* it:

- **Carneiro (1970), circumscription theory** — political complexity arises where arable land is
  bounded. Named as the motivating hypothesis. Reiterate the scoping: **8c does not test it** (the
  boundedness variable is unbuilt); it is named so the eventual enclosure build has a citable target.

---

## Accept gate

As in 8b, **not "is it significant"** — a significance gate corrupts the instrument's credibility,
which is the asset the arc is accumulating. The gate is:

**A defensible, reported effect size for complexity — marginal, nested|subsistence, and
nested|subsistence+fixity — with the family-restricted null and PERMDISP, plus the cheap-terrain lens
result, interpretable whichever way it came out.** A null passes; on the base rate it is the expected
result. What the gate requires: pre-test cell counts reported; the residual read against the committed
floor (permutation-null 95th percentile), fixity-residual cross-check reported alongside; the
collinearity caveat stated with the confound-share; the two-covariate and one-covariate numbers
reported side by side; and the notebook stating explicitly what a null does and does not rule out
(specifically: it does not rule out circumscription, which is untested).

---

## Forward — not drafted

- **8d — EA034 high-gods**, the contested finale, read against a now three-point calibrated scale
  (subsistence strong / fixity middle / complexity 8c-result). Framed around an honest effect size and
  a clean family-controlled null, not a hunt for separation.
- **Terrain-characterization variable track (high-priority EDOPS item, placement TBD).** A
  scale-parameterized basin-neighborhood terrain characterizer of which the cheap absolute tiers
  (ruggedness, landform position — Part D) are buildable now, and the **contrastive enclosure tier**
  (focal-basin-vs-ring contrast, needing the spatial-adjacency graph — `ST_Touches`, distinct from
  HydroBASINS drainage topology) is the real deferred build. **Trigger for the enclosure build:** an
  ambiguous 8c null (climate null + ruggedness null) plus reason to believe circumscription
  specifically. CDOP will want general terrain characterization for many things (Karl); this WO does
  not fund it, but records it so the eventual build has a spec and a use case, and to bound lost motion
  when it lands.

## Out of scope

- **The enclosure / basin-ring operator** — deferred with a named trigger (Forward). 8c uses only the
  cheap within-place terrain tier.
- **The PNV compositional lens** (natural-productivity / vegetation-heterogeneity probe on
  `pnv_shares`, compositional distance — Aitchison / Bray–Curtis / JSD, *never* a hand-ranking of the
  15 nominal classes). Held; reached for only if the climate + terrain result is ambiguous. Caveat
  when built: PNV is *modeled* (Haexeltine & Prentice) in human-dominated regions, so its uncertainty
  concentrates exactly where complexity is highest.
- **Modern land-use / irrigation / regulation layers as predictors** — audit flags at most; never
  predictors (anachronism, above).
- **Any engine / API / UI.** 8c is a notebook.

