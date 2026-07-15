# WO4e — Similarity metric: band-weighted and per-band-Mahalanobis distance

**Phase:** DEMO · Track 2
**Kind:** Research. Notebook only — extends `wo4c_basin_similarity.ipynb`. No surface, no engine.
**Branch:** `demo`
**Precondition:** WO4d complete.

**Scope:** resolve WO4d's confirmed dilution into a working per-band instrument on the existing 13
variables. No new data. This is the increment that turns "the composite drowns moisture" into "here
is a distance that doesn't."

---

## What WO4d established (the starting point)

- **Dilution confirmed.** Tbilisi L06→L08: temperature tracks near-perfectly (+5.5 query / +5.4
  analogue medians), aridity tracks 18% of its shift, precipitation runs the *wrong* way. Climate
  gets 4 votes of 13; nine non-moving variables anchor the neighbourhood.
- **The composite is the wrong instrument for "what's like this place."** It can't say *in what
  respect*, and "in what respect" is the whole question.
- **κ of the selected 13 = 55.1** — well-conditioned. Mahalanobis is available.
- **Per-band distances exist** (built in WO4d Step 3).

---

## Step 0 — Amend the WO4d record first

Before building anything, correct one overreach in `wo4d_findings.md`. The synthesis states the s/u
apparatus "does not add discriminating power at L06 — discharge already carries the signal." **The
test that would show this never ran** — the two-basin discrimination failed at the premise (no
locally-arid rain-fed control basin exists at L06), so the apparatus was not tested; the *control's
non-existence* was the finding.

Amend the synthesis line to read, in substance: *"s/u discrimination untested at L06 — the control
category (locally arid + rain-fed) is ecologically near-empty, which is itself a finding about
aridity–provenance entanglement at basin scale. Whether the apparatus discriminates is a live
question at L08, where basins can be locally arid and genuinely dry. The L06 near-collinearity
(r=0.975) and discharge's partial capture of provenance are real, but do not establish that the
apparatus adds nothing."* Do not leave the stronger negative standing.

---

## Step 1 — Per-band distance as the primary object

Reframe the instrument: **the answer to "what places are like this one" is a four-number profile,
not a scalar.** For a query basin, report per-band distance to every other basin:

- **A_terrain** (3): `ele_mt_sav`, `slp_dg_sav`, `kar_pc_sse`
- **B_hydrology** (5): `dis_m3_pyr`, `gwt_cm_sav`, `wet_pc_sg1`, `cly_pc_sav`, `slt_pc_sav`
- **C_climate** (4): `ari_ix_sav`, `pre_mm_syr`, `tmp_dc_syr`, `prm_pc_sse`
- **provenance** (3): `ari_ix_uav`, `pre_mm_uyr`, `dist_sink`

This is the answer Karl specified he would accept: *"similar along three bands, not the fourth."*
The composite becomes a summary *of* the profile, not a replacement for it.

## Step 2 — Within-band Mahalanobis

Even inside the 4-variable climate band, aridity↔precipitation r=0.83 — so plain Euclidean *within
a band* still double-counts moisture. Compute each band's distance as **Mahalanobis over that band's
own covariance** (Σ_band⁻¹). κ=55.1 was for the full 13; report κ **per band** — a 3–5 variable band
should be very well-conditioned, but confirm, and fall back to Euclidean for any band that isn't.

The difference to look for: does within-band Mahalanobis fix the precipitation-runs-backwards
result on Tbilisi? Climate-band distance between L06 and L08 Tbilisi should be **large** (they are
30 aridity points and 5.5°C apart) and should not be dragged by the aridity/precip correlation.

## Step 3 — Band-weighted composite (the second principled response)

Where per-band Mahalanobis corrects *within*-band redundancy, a band-weighted composite corrects
*across*-band vote-counting: each of the four dimensions votes **once**, not in proportion to how
many variables it holds. Compute a composite where the four band distances are combined with equal
band weight (not equal variable weight).

Report both instruments — per-band Mahalanobis and the band-weighted composite. They answer
different questions (the profile vs. a single summary that doesn't drown moisture); Karl decides
which, or both, is worth surfacing later.

## Step 4 — Re-run the Tbilisi coherence check on the new instrument

The WO4d per-level coherence test, re-run:

- Under **per-band Mahalanobis**, do L08 Tbilisi's climate-band nearest neighbours actually centre
  on *its* aridity/precip/temp (arid, warm) rather than L06's (wetter, cooler)?
- Under the **band-weighted composite**, does the aridity shift now track more than 18%?

If moisture now tracks, the dilution is fixed and the instrument responds to scale-conditionality
across *all* bands, not just temperature. If it still doesn't, that is a finding about the variables
themselves, not the weighting — and it points at the seasonality gap (WO5).

---

## Deliverables

- New cells appended to `notebooks/edop/demo/wo4c_basin_similarity.ipynb` (continue `# Cell N`)
- `docs/edop/demo/wo4e_findings.md`
- Amendment to `wo4d_findings.md` (Step 0)

## Accept gate

- WO4d s/u overreach amended.
- Per-band distance profile computed for query basins; κ reported per band.
- Within-band Mahalanobis built; its effect on the Tbilisi climate-band distance reported.
- Band-weighted composite built.
- Tbilisi coherence re-run on both instruments; **does moisture now track — yes or no, plainly.**
- Karl reviews.

## Out of scope

Seasonality indices and the monthly columns they need (**WO5** — data load; then the indices).
The D-PLACE subsistence correspondence test (waits on WO5; it is Karl's research line, not
infrastructure). L08 as a general surface. Any UI. Full re-selection of the 13 variables — WO4e
reweights the existing set, it does not re-choose it.
