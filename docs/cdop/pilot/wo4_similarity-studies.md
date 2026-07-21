# WO4 — What is similarity for? Four instruments on shared probes

**Status:** draft for review.
**Branch:** `cdop_pilot` (existing); notebook under the existing `notebooks/cdop/` structure.
**Type:** exploratory. No engine writes, no registry changes, no API, no UI.

Goal-setting with provisos. CC discovers implementation particulars; Karl reviews every write.

---

## Why

Three similarity failures in one session (phase, precipitation, Tbilisi/temperature) had a
common shape: none was a failure of distance computation. Each was a failure to declare what
the comparison was *for*.

Similarity is not a property of objects. It is a relation induced by a purpose — a carved tree
stump is a chair if it affords sitting, and no attribute list settles it. The lens registry
already asks *similar with respect to what*. It does not yet ask *similar for what purpose*, or
*similar as what object*.

This notebook tests whether four distinct jobs are hiding under one word. If their answers on the
same query differ substantially, they are four instruments and should be built separately. If
they largely agree, the current architecture stands and the failures were local.

**This is a question, not a plan.** A result showing the four converge would be a useful finding
and should be reported as such.

---

## Reading requirement

The output is meant to be read, not just computed. Every part prints in a form Karl can judge
without reconstructing the method: named places rather than `hybas_id` alone, monthly profile
glyphs beside precipitation results, distances and ranks visible, and a short plain-language
statement of what the cell did. Where a part produces a table, it should be small enough to read.

This is the diagnostic rule from WO3 Part D applied to the notebook itself: **draw the compared
dimension before theorising about the metric.**

---

## Probes

Six query basins, chosen so that right answers are judgeable:

| Probe | Why |
|---|---|
| Mombasa | Bimodal equatorial; validated case (WO2a) |
| Augsburg | Temperate distributed; the WO1 false match |
| Tbilisi | Container failure — basin mean 5.3 °C vs city ~13.8 °C |
| Kaifeng | Container success — low-relief plain, basin representative |
| Timbuktu | Sharp single monsoon, arid margin |
| George Town | High-baseline equatorial; the WO2 mischaracterised case |

Provisos: resolve each at both L06 and L08 (see Part 0). Add a Southern Hemisphere probe if one
suggests itself — Santiago would test hemisphere behaviour, which the retired phase lens never
resolved.

**Lens:** use the WO3 continuous precipitation features `(a1, b1, a2, b2)` + annual total. They
are validated and the glyph exists. Run `climate.temp` as a secondary where it is informative —
particularly for Tbilisi, where the container problem is sharpest. Do not build new lenses here.

---

## Part 0 — The undeclared argument: container

Before any of the four, establish what is currently invisible: **the same query at L06 and L08 is
not the same query.**

For each probe, report side by side at both levels: the lens feature values, basin elevation
range, basin mean elevation against site elevation, and the top-5 analogue results.

Then, across the WHG settlement corpus, compute the divergence between site elevation and basin
mean elevation at both levels, and convert with a standard lapse rate (~6.5 °C/km) to an implied
temperature gap. Plot the distribution.

Tbilisi's 8.5 °C gap implies roughly 1,300 m of divergence. The question this part answers is
whether that is a thin alpine tail or a substantial share of historically significant settlements
— which are disproportionately in mountain valleys, river confluences, and defensible terrain.

**This is the highest-value single result in the WO** and does not depend on anything else here.
It can run first and stand alone.

Proviso: report exposure in units of use — share of WHG settlements, share of D-PLACE societies —
not share of basin inventory. The 2.4% bimodal figure taught this lesson once already.

---

## Part 1 — Analogue

The current instrument: global nearest neighbours in lens space, no exclusions.

For each probe, top-10 with distances, place names where resolvable, and monthly profile glyphs
(raw bars plus two-harmonic fit overlay).

Additionally, for each probe report the **great-circle distance of each result from the query**.
This is the quantity that makes Part 2 interpretable and it has never been looked at.

Proviso: use topN here, not thresholds. The strict/moderate/loose ladder is under separate
question (uncalibrated for temp, geometrically incoherent at 1×/3×/6× radius) and importing it
would confound this test. Report the raw distance distribution so the threshold question can be
informed by, but not entangled with, this work.

---

## Part 2 — Analogue net of geography

Same computation, excluding all basins within *n* km of the query. Sweep *n* — say 250, 1000,
2500, 5000 km — and show how the answer changes.

The premise: environmental variables are heavily spatially autocorrelated (Moran's I is a
denominator, not a finding), so a similarity map that shows a blob around the query is a correct
result carrying no information. Mombasa→Ghana coast was valuable *because* it was 7,000 km away.

Questions this part should answer:

- At what exclusion radius do results stop being the query's own neighbourhood?
- Which probes have genuine distant analogues, and which run out?
- Does a probe with no analogue beyond some radius exist in the set? That would be a finding
  about the place, and it is the honest-scarcity signal that quantile thresholds would otherwise
  hide.

Proviso: this is a candidate UI control (exclusion radius as a slider), not just a diagnostic.
Note how it behaves, but do not design the control here.

---

## Part 3 — Matched control set

The instrument the D-PLACE correspondence test will actually need, and the one that does not
currently exist.

**The problem it addresses (Galton's problem).** Galton objected to Tylor in 1889 that societies
are not independent observations: they inherit traits from common ancestors and borrow from
neighbours. A correlation across 100 societies may rest on five or ten independent origins, so
the effective N is far smaller than the nominal N and significance tests built on it are
meaningless.

Environmental similarity makes this *worse*, not better: environmentally similar basins are
usually geographically close, hence linguistically and historically related. Thirty East African
fishing societies in bimodal basins may be one fact about the Swahili coast rather than thirty
facts about environment and subsistence.

**What the instrument does:** rather than ranking neighbours, assemble a *balanced set* — societies
that differ on a cultural variable but sit in environmentally comparable basins, selected to
maximise phylogenetic and geographic spread.

Concretely, for `EA042` (dominant subsistence):

- Join D-PLACE societies to basin signatures (87% have assignments; the 13% dropout must be
  reported, not silently excluded)
- Select pairs or small groups matched on precipitation-lens distance below some tolerance
- Require members to differ on `EA042`
- Require different language families and large geographic separation
- Output a **balance table** — how comparable are the matched environments? — alongside the set

Provisos:

- Output is a set with a balance table, not a sorted list. Different shape from Parts 1–2, and
  that difference is the point.
- Language family is in D-PLACE; use it as the phylogenetic proxy rather than constructing
  anything.
- **`EA042` here is a validation case, not a finding.** Subsistence and water are near-tautologically
  linked; if the instrument cannot recover that association, the instrument is broken. Treat a
  positive result as a smoke test, not a discovery.
- Do not run the actual correspondence test in this WO. The question here is whether balanced
  sets can be constructed at all and how large they are. If matched sets turn out to be tiny, that
  is the finding, and it constrains Phase 4 substantially.

---

## Part 4 — Typological position

No comparison to instances at all. Where does this basin sit in the global distribution?

For each probe: per-variable percentile against the full L06 population, plus categorical
position where a label exists (`pre_modality`, bioclimate). Output should be readable as prose —
this is the input to a rule-based blurb, and the Seasonality narrative already established that
pattern.

This is also the instrument behind *"show me all bimodal precipitation basins like this one"* —
a set-membership query, not a distance query.

Proviso: `pre_modality`'s thresholds are known-suspect (`THRESH_DBL` was fitted to probe cases;
George Town was mischaracterised; high baseline suppresses `R_dbl`). Use it, and flag where a
probe sits near a class boundary rather than reporting the label alone. Distance-to-boundary is
the honest analogue of confidence.

---

## Part 5 — Local anomaly (cheap; drop if it distorts the WO)

Not one of the four, but nearly free and directly useful to the blurb work.

Compare each probe against its own spatial neighbourhood rather than the globe: percentile within
*n* km. *This basin is unusually dry for its region. This basin has unusually low relief for its
surroundings.*

This ports the ESDA finding — local heterogeneity is where the value is; HH/LL cluster cores are
confirmatory, HL/LH outliers and ecotonal seams are the interesting cases — from the Explorer
choropleth to the point query. Nothing there needs redoing; it needs connecting.

---

## Part 6 — Do they differ?

The comparison that justifies the WO.

For each probe, place the four result sets side by side and quantify overlap — Jaccard or simple
intersection counts between Part 1, Part 2, and the environmental neighbours implied by Part 3's
matched sets. Part 4 produces no instance list, which is itself the answer for that one.

Then state plainly, per probe: **are these four settings of one instrument, or four instruments?**

---

## Accept gate

**The four jobs are run on the same six probes with readable output, and the notebook states
whether their answers differ substantially — with the Part 0 container measurement reported
across the WHG corpus regardless of what the rest shows.**

Not a correctness gate. Convergence is a legitimate outcome and should be reported plainly rather
than argued around.

---

## Explicitly not in scope

- Any engine, registry, API, or UI change
- Threshold recalibration or the quantile proposal
- Deciding whether similarity moves to L08
- Building the connectivity lens, or any Terrain or Hydrology lens
- Running the actual D-PLACE correspondence test
- Rebuilding phase similarity in any form

---

## Standing hazard to guard against in this WO

Three times in one session a cut point or interpretation was set by checking whether the result
matched an expectation: `THRESH_DBL` fitted to George Town and Mombasa, the SE Asia held-out cases
reinterpreted after the numbers arrived, and the proposed temp `moderate` value derived from
"what strict is doing correctly."

In this notebook, where a judgement is made about whether a result is *right*, write down the
expectation first and record it as an expectation. Where a result contradicts one, report the
contradiction before explaining it.

---

## What the outcome informs

If the four differ, a lens definition needs three declared arguments rather than one: which
variables, which job, and which container. That is an extension of the existing registry, not a
new architecture — the engine still resolves and serves; purpose is declared at the surface.

If they converge, the architecture stands and the session's failures were local to the phase
lens and the Tbilisi container.
