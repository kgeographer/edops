# WO4e findings — Band-weighted and per-band Mahalanobis distance

**Date:** 2026-07-14
**Branch:** `demo_wo4`
**Notebook:** `notebooks/edop/demo/wo4c_basin_similarity.ipynb` (Cells 19–22)
**Precondition:** WO4d complete; findings in `wo4d_findings.md`

---

## The question

WO4d confirmed dilution: under full 13-var Euclidean, Tbilisi's analogue medians tracked only 18%
of the aridity shift and went the *wrong direction* on precipitation. Two principled fixes were
proposed: within-band Mahalanobis and a band-weighted composite. WO4e builds both and tests them
against the same Tbilisi coherence check.

---

## Step 1 — Per-band condition numbers (Cell 19)

All four bands are well-conditioned. No Euclidean fallback required anywhere.

| Band | n vars | κ | Instrument |
|---|---|---|---|
| A_terrain | 3 | 3.12 | Mahalanobis |
| B_hydrology | 5 | 3.08 | Mahalanobis |
| provenance | 3 | 4.55 | Mahalanobis |
| C_climate | 4 | 21.61 | Mahalanobis |
| **13-var combined** | 13 | **55.1** | (Cell 15 reference) |
| **27-var full** | 27 | **6091.8** | singular — unusable |

C_climate is highest because aridity and precipitation are correlated (r=0.83), but 21.6 is far
below the 100 fallback threshold. Banding collapses the condition number because each band is
internally coherent and the collinear cross-band pairs have been separated.

---

## Step 2 — Tbilisi per-band distance profile (Cell 21)

The per-band Mahalanobis distances between L06 and L08 Tbilisi (L08 projected into L06 combined
z-score space):

| Band | Distance | Mode |
|---|---|---|
| A_terrain | **1.206** | Mahalanobis |
| C_climate | 0.777 | Mahalanobis |
| B_hydrology | 0.445 | Mahalanobis |
| provenance | **0.000** | Mahalanobis |

**Terrain is the dominant inter-level difference, not climate.** L06 Tbilisi captures the Caucasus
highlands (high elevation, high slope); L08 is the Kura valley floor (lower elevation, lower slope).
C_climate difference is real and large (0.777) but comes second.

**Provenance = 0.000.** The two Tbilisi basins have identical provenance signatures: same network
position (`dist_sink`), same upstream aridity and precipitation at both levels. The s/u apparatus
sees no inter-level difference at Tbilisi. The entire L06→L08 environmental shift is terrain +
climate, not provenance.

---

## Step 3 — Three-instrument comparison (Cells 20–22)

The Tbilisi coherence check re-run with all three instruments. Tracking % = 100 × Δmed_analogues /
Δquery; +100% is perfect, negative is wrong direction.

| Variable | Query Δ | Euclidean (WO4d) | C_climate Mah | Band-weighted |
|---|---|---|---|---|
| ari_ix_sav | −30 | +18% | **+100%** | −47% |
| pre_mm_syr | −140 mm | −21% | **+111%** | −57% |
| tmp_c | +5.5°C | +98% | +91% | +30% |

---

## Findings

### C_climate Mahalanobis: dilution fully resolved

Under the C_climate instrument — top-20 selected by climate-band Mahalanobis distance alone —
moisture tracking is 100% and 111%. The signal is fully present in the data. It was not missing in
WO4d; it was outvoted.

Temperature drops slightly from 98% to 91% because within-band Mahalanobis de-weights the
ari↔pre correlation, redistributing some of temperature's previous dominance. This is the correct
behaviour: Mahalanobis normalises by the band's own covariance rather than treating each variable
as a single equal vote.

### Band-weighted composite: worse than Euclidean

The band-weighted composite (equal 1/4 weight per band, each band Mahalanobis) produced tracking
of −47%, −57%, +30% — *worse* than the WO4d Euclidean baseline on every variable. The mechanism:

1. **Terrain dominates the inter-level difference** (A_terrain Mah = 1.206 vs C_climate = 0.777).
   Giving terrain equal band weight relative to climate does not reduce terrain's influence; it
   increases it relative to WO4d Euclidean (where terrain had 3 of 13 variable votes = 23%).
   Equal band weight gives terrain 25% — and Mahalanobis amplifies the within-band signal, so
   terrain now drives the composite harder than before.

2. **Terrain and climate correlate globally in the wrong direction for this comparison.** High-
   elevation (L06-like) basins globally tend to be cooler and wetter than surrounding lowlands.
   Valley-floor (L08-like) basins tend to be warmer and drier. The composite finds
   terrain-coherent analogues at each level whose climate medians shift in the opposite direction
   from the actual L06→L08 query shift.

**Band-weighted composite is not a general-purpose dilution fix.** It is coherent only when the
four bands are roughly equally differentiated for the comparison of interest. When one band
dominates the inter-level distance (as terrain does here), equal band weighting amplifies rather
than corrects the imbalance.

### What this means for the metric

**The per-band profile is the primary instrument.** The answer to "how do L06 and L08 Tbilisi
differ?" is: terrain 1.21, climate 0.78, hydrology 0.45, provenance 0.00. No scalar composite
conveys this; no biome label can; only the four-number profile captures the full picture.

**The instrument choice depends on the question:**

| Question | Instrument |
|---|---|
| "What places are holistically similar to this basin?" | Euclidean (or band composite) |
| "What places have similar climate to this basin?" | C_climate Mahalanobis |
| "How does this place differ across levels?" | Per-band Mahalanobis profile |

The moisture signal is fully recoverable — once you ask the right question with the right
instrument. The composite's inability to track moisture is not a data failure; it is a question
mismatch.

---

## Overall synthesis

The WO4c–4e arc resolves to three clean findings:

1. **The full composite is not broken — it is answering a different question.** Holistic
   environmental similarity correctly weights every dimension, which means it will always be
   diluted on any one dimension that is a minority signal (climate = 4 of 13 votes). For
   holistic queries this is correct behaviour.

2. **C_climate Mahalanobis is the climate-primary instrument.** It answers "what places have
   the most similar climate profile" and does so accurately (100%/111%/91% tracking on the
   Tbilisi test). It is the right tool when climate is the research question.

3. **Band-weighted composite does not generalise.** It works when the bands are equally loaded;
   it fails when one band dominates, as terrain does at Tbilisi. Do not surface it.

**Two instruments for the surface, not three:**
- The composite (Euclidean over 13 local vars) for holistic "similar places" queries.
- C_climate Mahalanobis for climate-primary "similar climate" queries.
- The per-band profile as the explanatory layer for both: it says *why* the neighbourhood
  looks the way it does and *in what respects* two places are similar.

---

## Accept gate

- [x] WO4d s/u overreach amended (see `wo4d_findings.md`)
- [x] Per-band κ reported: all four bands well-conditioned (κ=3.1–21.6), no fallback
- [x] Per-band Mahalanobis distance profile for Tbilisi L06 vs L08 reported
- [x] Within-band Mahalanobis (C_climate) coherence check: moisture tracks 100%/111%
- [x] Band-weighted composite built and tested: fails (−47%, −57%, +30%)
- [x] Reason for failure stated plainly: terrain dominates inter-level distance; global terrain-climate covariance corrupts composite analogue medians
- [x] Instrument selection guidance given
- [ ] Karl review

## Next steps

- **WO5** if proceeding: monthly precipitation indices to fix Mediterranean (Test 1) and sharpen
  the C_climate Mahalanobis instrument. Seasonality is the remaining gap.
- **Surface integration** (separate WO): two query modes — holistic (Euclidean composite) and
  climate-primary (C_climate Mahalanobis) — with per-band profile as the explanatory overlay.
- Band-weighted composite: do not surface. The finding is documented; the instrument is retired.
