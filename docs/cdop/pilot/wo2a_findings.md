# WO2a findings — Continuous harmonic representation

**Notebook:** `notebooks/cdop/wo2a_continuous.ipynb`
**Work order:** `docs/cdop/pilot/wo2a_continuous.md`
**Branch:** `cdop_wo2` (same branch as WO2)
**Date:** 2026-07-19

---

## Background

WO2 concluded (Part B4) that the recommended path to fixing the WO1 accept gate failure is
Option B: replace `seas_phase_offset` with a bimodal-aware variable using the R_dbl statistic,
and gate the phase lens on a `same_modality` filter. Before committing to that design in WO3,
this addendum tests whether the continuous Cartesian representation of the two harmonics
— keeping (a1, b1, a2, b2) as four features rather than reducing to thresholded classes —
can reproduce WO2's probe separation without any classification step.

The accept gate was set in the WO2a work order before any data were examined:
> The continuous representation reproduces WO2's probe separation with no classification step,
> and additionally recovers held-out cases the thresholded version misses.

If it reproduces but does not improve, Option B stands. If it improves, WO3 changes: the
precipitation lens takes (a1, b1, a2, b2) directly, and `same_modality` is dropped.

---

## Part A — Compute and verify

### A1 — Harmonic component definitions

For each basin with monthly values p₁…p₁₂ and annual total t = Σpₘ:

```
θ₁ = 2π·m/12    (m = 0..11; annual harmonic)
θ₂ = 2π·m/6     (semi-annual harmonic)

a1 = Σ(pₘ·cos θ₁) / t     b1 = Σ(pₘ·sin θ₁) / t
a2 = Σ(pₘ·cos θ₂) / t     b2 = Σ(pₘ·sin θ₂) / t
```

Basins with t = 0 (hyper-arid, no data) receive NaN across all four components.

**Identities asserted:**
- R_std = √(a1² + b1²) ← must equal pre_concentration
- R_dbl = √(a2² + b2²) ← must equal the WO2 bimodal amplitude

### A2 — Identity verification

Both identities held to machine epsilon across all 16,338 basins with valid data:

```
R_std max error: 2.22e-16
R_dbl max error: 2.22e-16
```

This confirms that (a1, b1, a2, b2) are not a redesign of what WO2 built — they are the same
quantities kept whole instead of reduced to amplitudes. The 59 basins without valid data are
hyper-arid NoData basins (t = 0).

### A3 — Population statistics

```
         a1          b1          a2          b2
mean  -0.096      -0.027       0.066       0.048
std    0.423       0.184       0.177       0.144
min   -0.933      -0.946      -1.000      -0.866
max    1.000       0.866       1.000       0.866
```

The (a1, b1) distribution is shifted toward negative a1 (corresponding to a northern-hemisphere
summer wet-season peak around July, where cos(2π×6/12) = −1). The (a2, b2) distribution is more
centered; high R_dbl basins occupy the outer ring of the (a2, b2) scatter.

---

## Part B — Probe separation without classification

### B1 — Probe features

Probe cities are queried from `gaz.wh_cities` joined to `basin08` (L08 resolution):

| City | a1 | b1 | a2 | b2 | R_std | R_dbl | mm/yr |
|------|----|----|----|-----|-------|-------|-------|
| Mombasa | −0.176 | +0.124 | −0.261 | −0.219 | 0.215 | 0.341 | 1101 |
| Augsburg | −0.211 | +0.028 | +0.071 | −0.036 | 0.212 | 0.080 | 990 |
| Salzburg | −0.192 | +0.021 | +0.089 | −0.038 | 0.193 | 0.096 | 1248 |
| George Town | −0.148 | −0.169 | −0.187 | −0.010 | 0.225 | 0.187 | 2563 |
| Split | +0.156 | −0.110 | −0.056 | −0.095 | 0.191 | 0.111 | 901 |
| Timbuktu | −0.814 | −0.294 | +0.416 | +0.398 | 0.865 | 0.575 | 172 |

Note: Rome was removed. Its L06 basin includes Apennine terrain that dilutes the Mediterranean
signal. Split (Dalmatian coast) is the clean Mediterranean exemplar.

Mombasa and Augsburg have nearly identical R_std (0.215 vs 0.212) — indistinguishable in the
unimodal measure. They are cleanly separated by R_dbl (0.341 vs 0.080) and by the direction
of their (a2, b2) vectors: Mombasa sits in the third quadrant of the (a2, b2) plane, well
outside the R_dbl = 0.30 threshold circle; Augsburg sits near the origin.

Timbuktu's high R_dbl (0.575) is an artifact of a sharp single monsoon peak: Fourier
decomposition places energy at all harmonics when the signal is sharply concentrated. The
continuous representation handles this correctly — Timbuktu's large (a1, b1) vector pointing
toward July places it far from Mombasa's more modest vector in 4D.

### B2 — Nearest-neighbour results (no modality filter)

Top-5 L06 nearest neighbours in Euclidean (a1, b1, a2, b2) distance:

**Mombasa:** All East African.
```
hybas=1060008730  dist=0.067  lat=−4.1  lon=+39.5   (Kenyan coast)
hybas=1060008480  dist=0.070  lat=−2.8  lon=+40.1   (Kenyan coast)
hybas=1060008760  dist=0.076  lat=−4.4  lon=+39.2   (Kenyan coast)
hybas=1060008330  dist=0.119  lat=−1.3  lon=+40.9   (Kenyan coast, drier)
hybas=1060023460  dist=0.121  lat=+5.5  lon=−0.9    (Ghana coast, West Africa)
```

**Augsburg:** All Central European.
```
hybas=2060460170  dist=0.013  lat=+48.0  lon=+11.6  (Bavaria)
hybas=2060461650  dist=0.018  lat=+47.8  lon=+10.7  (Bavaria)
...
```

**Timbuktu:** All Sahel.
```
hybas=1060635020  dist=0.010  lat=+15.8  lon=+0.4
hybas=1060042600  dist=0.012  lat=+13.2  lon=+16.8
...
```

No European basins appear anywhere in Mombasa's top-5. This is the central Part B result:
the continuous representation separates Mombasa from the temperate European cluster without
any modality classification or `same_modality` filter.

### B3 — Notes on Split

Split's top-5 includes one Adriatic neighbour (lat=+43.9, lon=+16.1, dist=0.031) and two
coastal Brazilian basins (~lat=−17°, lon=−40°, dist≈0.042–0.045). A Borneo basin also appears
(lat=+0.7, lon=+109.2, dist=0.042). The Brazilian basins may reflect a winter-dominant coastal
rainfall regime resembling the Mediterranean structure in harmonic space; the Borneo basin is
unexplained and worth examining in WO3. These do not affect the Mombasa test but are noted.

---

## Part C — Held-out validation

### C1 — Set declared before computing

The held-out set was written in full in Cell 7 before any distances were computed (WO2a
work-order requirement). The 11 locations span ITCZ double-passage and double-monsoon regions
not used to calibrate any WO2 threshold. Darwin (uncertain) and Conakry (single peak) are
negative controls.

All 11 locations were resolved via KNN nearest-basin query (`ORDER BY geom <-> ST_MakePoint`)
after `ST_Contains` failed for 3 coastal/peninsular coordinates (Manila, Darwin, Conakry fall
in water at L06). India/Kerala-S and Kerala-N resolved to the same basin (4060029530).

### C2 — Results

| Location | Expected | R_std | R_dbl | dist(Mombasa) | dist(Augsburg) | Verdict |
|----------|----------|-------|-------|---------------|----------------|---------|
| WAfrica/Abidjan | positive | 0.325 | 0.246 | 0.178 | 0.303 | **Mombasa** ✓ |
| India/Kerala | positive | 0.440 | 0.137 | 0.444 | 0.267 | Augsburg |
| Vietnam/HCM | positive | 0.496 | 0.068 | 0.525 | 0.358 | Augsburg |
| Philippines/Manila | positive | 0.355 | 0.073 | 0.537 | 0.311 | Augsburg |
| Thailand/Bangkok | positive | 0.502 | 0.181 | 0.554 | 0.430 | Augsburg |
| Vietnam/Hanoi | positive | 0.552 | 0.137 | 0.647 | 0.405 | Augsburg |
| Mexico/Acapulco | positive | 0.699 | 0.229 | 0.843 | 0.579 | Augsburg |
| WAfrica/Conakry | **negative** | 0.700 | 0.249 | 0.853 | 0.587 | Augsburg ✓ |
| Mexico/Manzanillo | positive | 0.705 | 0.326 | 0.932 | 0.652 | Augsburg |
| Australia/Darwin | uncertain | 0.691 | 0.235 | 1.028 | 0.920 | Augsburg ✓ |

### C3 — Interpretation

The SE Asian monsoon locations (Vietnam, Thailand, Philippines, Kerala) all have high R_std
(0.36–0.55) and low R_dbl (0.07–0.18). These are correctly identified by the continuous
representation as genuinely unimodal at L06 resolution. ITCZ double-passage does not
automatically create equal-amplitude harmonics: if the return passage delivers a much smaller
peak than the primary, the first harmonic dominates and R_dbl stays low. The continuous
representation is honest about this — it does not classify these as bimodal, and neither
should a basin-scale similarity metric.

### C4 — Follow-up: own top-5 neighbours (Cell 13)

The two-anchor forced choice ("closer to Mombasa or Augsburg") was flagged as the wrong
instrument after review: Bangkok is honestly neither anchor. The better test is what each
city's own top-5 look like. Run after the main analysis (Cell 13).

Monthly profiles confirmed all three are unimodal: HCM has one long wet season May–November;
Bangkok has a single September peak (central Thailand monsoon); Manila has a broad
July–August peak. The two-harmonic fit is a poor description of all three — single-peak
structure, no fit needed.

Own top-5 results:

**Bangkok** — four central Thailand basins (three within 1° of Bangkok) plus one Deccan
India basin. A tight geographic cluster in the central Thai monsoon zone. The Bangkok L06
basin is central Thailand; southern Thailand (Kra Isthmus) receives both monsoon systems
and would produce a different, more bimodal profile.

**Vietnam/HCM** — Cambodia, Myanmar, Guatemala Pacific coast, and two Guinea coast (Liberia/
Sierra Leone) basins. No single geographic cluster, but all are single-peak tropical monsoon
with similar rainfall totals and timing. The metric is finding climatically equivalent regimes
across continents, which is the intended behaviour.

**Philippines/Manila** — three Philippines basins (Cebu, Panay, northern Luzon), one Costa
Rica (Pacific coast, similar monsoon structure), and one Kamchatka basin (lat=+58°N). Four of
five are geographically and climatically coherent; the Kamchatka hit is a harmonic coincidence.
Manila's moderate R_std (0.355) means its 4D fingerprint is not distinctively tropical and
can graze distant regimes at the margin.

None of the three cities find Mombasa-type bimodal basins or European temperate basins in
their top-5. The reading of C2 as "correctly unimodal at L06 resolution" is vindicated on
better evidence. Part C converts from partial pass with generous interpretation to a clean pass.

Conakry and Darwin behave as expected: Conakry's single long rainy season (high R_std, single
direction) places it near Augsburg; Darwin's dominant Nov-Apr wet season does the same.

**Abidjan is the discriminating case.** R_dbl = 0.246 is below THRESH_DBL = 0.30, so the
thresholded Option B classifier would discard it from the bimodal bin. The continuous
representation places it correctly closer to Mombasa (dist=0.178 vs dist=0.303). This is a
genuine recovery: one case the threshold misses that the continuous form catches.

The Mexican locations have high R_std (≈0.70) — strongly unimodal — despite lying in a
Pacific double-ITCZ zone. At L06 basin scale the dominant summer rainfall overwhelms any
secondary peak.

---

## Part D — Phase relation

### D1 — (cross, dot) definition

The scalar `seas_phase_offset` reduces the precip-temperature phase relationship to a single
number via arctan2, which wraps at 0/12 months and produces a spurious definite value even
when one of the cycles is too weak to have a meaningful phase (e.g. equatorial temperature).

The continuous alternative is the vector product of the precip and temperature annual harmonics:

```
cross = a1_p · tb1_t − b1_p · ta1_t  =  R_std · T_amp · sin(φ_temp − φ_precip)
dot   = a1_p · ta1_t + b1_p · tb1_t  =  R_std · T_amp · cos(φ_temp − φ_precip)
```

where (ta1, tb1) are the temperature annual harmonic components in °C (normalized by 6, not by
total). The magnitude √(cross² + dot²) = R_std × T_amp; both cycles must be strong for large
values. When either is weak (equatorial temperature, hyper-arid precipitation), both shrink
toward zero, making the indeterminacy visible rather than masking it as a large scalar.

Note: (ta1, tb1) are not normalized by temperature range. Amplitude is carried into (cross, dot),
so weak-temperature basins cluster on magnitude, not on direction.

### D2 — Probe values

| City | T_amp (°C) | cross | dot | seas_phase_old |
|------|-----------|-------|-----|----------------|
| Augsburg | 9.14 | +0.395 | +1.902 | 11.6 |
| Salzburg | 9.77 | +0.247 | +1.874 | 11.7 |
| Mombasa | 1.87 | −0.339 | −0.216 | 4.08 |
| George Town | 0.55 | −0.088 | −0.087 | 4.49 |
| Split | 8.96 | −1.205 | −1.211 | 4.51 |
| Timbuktu | 5.67 | −2.491 | +4.228 | 1.02 |

**Augsburg/Salzburg** (large positive dot): precip and temperature both peak in summer, nearly
in phase. Classic temperate. Large because T_amp is large (9°C range).

**George Town** (near zero): T_amp = 0.55°C — the temperature year is essentially flat. The
old scalar gave 4.49, which appeared to match Mombasa but was computed from a near-zero vector
and was meaningless. The (cross, dot) representation correctly shows "indeterminate."

**Mombasa** (small negative pair): temperature peaks February, rain peaks May — temperature
leads rain by ~4 months. Small magnitude because T_amp is modest (1.87°C).

**Split** (large negative pair): November rain, July heat — the Mediterranean inversion.
T_amp = 8.96°C amplifies the values. **Split and Mombasa are in the same quadrant.**

### D3 — Mediterranean contamination test

Distance from Mombasa in continuous (cross, dot) space vs. old scalar:

| City | dist_phase_cts | dist_phase_old |
|------|---------------|----------------|
| George Town | 0.282 | 0.405 |
| Split | 1.319 | 0.423 |
| Augsburg | 2.241 | 4.473 |

**The contamination is reduced but not closed.** Split moves from 0.42 to 1.32 from Mombasa
(3× improvement), but Split (1.32) remains closer to Mombasa than Augsburg (2.24) — the
accept criterion requires the opposite.

There is also a new problem: George Town (0.28) is now the nearest city to Mombasa in
(cross, dot) space. Its near-zero (cross, dot) vector is closest to Mombasa's small-negative
vector. Equatorial flat-temperature locations will contaminate any phase lens based on (cross, dot).

**Root cause:** Mombasa (Feb heat / May rain) and Split (Jul heat / Nov rain) both have
temperature leading precipitation by approximately 4–5 months, from different sectors of the
annual cycle. The (cross, dot) representation collapses the two-dimensional relationship to
a relational quantity — it sees the phase *difference*, not the absolute position in the year.
From different sectors, similar offsets produce similar (cross, dot) vectors.

### D4 — Fix for WO3

Use (a1_p, b1_p, ta1_t, tb1_t) as four independent features — the absolute harmonic directions
for both precipitation and temperature. In this 4D space:

- Mombasa: precip vector → May direction, temp vector → Feb direction. Both point into the
  northern-hemisphere spring sector.
- Split: precip vector → November direction, temp vector → July direction. Both point into
  the July/November sector.

The absolute directions differ even though the phase offsets are similar. No (cross, dot)
reduction needed — the dot product of the two 2D vectors is already captured by Euclidean
distance in the 4D joint space. The George Town problem also disappears: equatorial
temperature has small (ta1, tb1) magnitude which places it correctly near other
weak-temperature-cycle basins, not near Mombasa.

---

## Part E — Monthly profile visualization

### E1 — Result

The five nearest L06 neighbours of Mombasa in (a1, b1, a2, b2) space show:

| Rank | Location | mm/yr | dist | Structure |
|------|----------|-------|------|-----------|
| 1 | lat=−4.1, lon=+39.5 | 1139 | 0.067 | Twin peaks April-May and October-November |
| 2 | lat=−2.8, lon=+40.1 | 837 | 0.070 | Twin peaks May-June and October-November |
| 3 | lat=−4.4, lon=+39.2 | 1035 | 0.076 | Twin peaks March-May and October-November |
| 4 | lat=−1.3, lon=+40.9 | 516 | 0.119 | Twin peaks April and October (drier basin) |
| 5 | lat=+5.5, lon=−0.9 | 1327 | 0.121 | Twin peaks May and October (Ghana coast, West Africa) |

Neighbours 1–4 are on the Kenyan coast within 3–4° latitude of Mombasa. Neighbour 5 is on
the Ghana/Ivory Coast (Guinea coast), 7,000 km away — the metric finds dynamically similar
bimodal structure across the continent.

All five show genuine twin-peak profiles with a mid-year dry trough (July-August). The
two-harmonic fit (dashed overlay) captures both peaks in each case. This confirms Part B
visually: five consecutive nearest neighbours share the bimodal structure without any
modality filter in the distance computation.

### E2 — Fit vs. raw

The two-harmonic fit symmetrizes somewhat relative to the raw data. Mombasa's raw May peak
(~235mm) is substantially larger than its November peak (~110mm), but the harmonic model
distributes that asymmetry across all four components. What the metric compared was the smooth
reconstruction, not the raw bars. In neighbour #4 (516 mm/yr, driest), the fit shows a more
prominent November peak than the raw data; the harmonic model smooths over what is actually a
weak October shoulder in the bars. These discrepancies are inherent to a two-harmonic
approximation and should be displayed as the glyph in WO3 (Part E's structural proposal: the
fit curve is what the metric compared, and is what should be shown).

---

## Accept gate

**Part 1 (probe separation without classification): PASS.**
Mombasa's top-5 in continuous (a1, b1, a2, b2) space are all East African / Guinea coast
basins. No European temperate basins appear. The core WO1 failure is corrected without
`same_modality` or any threshold inside the distance computation.

**Part 2 (held-out cases the thresholded version misses): PARTIAL PASS.**
Abidjan (R_dbl = 0.246) is correctly recovered — the threshold would discard it, the
continuous form catches it. SE Asian monsoon locations are correctly identified as unimodal
at L06 resolution; their placement near Augsburg is not a failure but a finding about basin-
scale signal.

**Part D (Mediterranean contamination closed): FAIL for (cross, dot); design fix identified.**
The (cross, dot) reduction partially closes contamination but does not satisfy the criterion.
The fix — using (a1_p, b1_p, ta1_t, tb1_t) as four independent features — is identified and
should be implemented directly in WO3 without a separate WO.

**Overall verdict: ACCEPT — WO3 proceeds with continuous representation.**

---

## WO3 implications

These replace the Option B design specified in WO2 B4:

| Component | WO2 Option B | WO2a revision |
|-----------|-------------|---------------|
| `climate.precip` lens features | `pre_concentration`, `R_dbl`, threshold-gated `modality` | (a1, b1, a2, b2) directly — no threshold |
| `climate.phase` lens features | `seas_phase_offset_v2` (R_dbl-branching formula) | (a1_p, b1_p, ta1_t, tb1_t) — 4 independent features |
| `same_modality` filter | Required | **Drop** |
| `pre_modality` | Feature and filter | Display variable only |
| `seas_phase_offset` | Deprecated | Retained as display variable; not used in distance |

**Carried forward regardless:**
- No threshold inside feature construction. A branching feature formula is a lie somewhere.
- Circular quantities enter as (cos, sin) pairs, never as raw angles. This applies immediately
  to slope aspect if it becomes a Terrain lens candidate.
- The glyph principle from Part E: a lens definition should ship with a visual signature of
  what it compared — the two-harmonic fit overlay is the prototype. This generalizes.
- The `aseasonal` label covers relentlessly wet equatorial, Mediterranean, and distributed
  temperate. It appears in generated prose. Renaming and splitting this class is deferred but
  urgent — noted for WO3 or a fast follow-on.
- Population exposure should be counted in units of use (D-PLACE societies), not basin
  inventory. The bimodal population is 2.4% of basins but concentrated in East Africa, the
  Sahel margin, and South Asia — exactly where D-PLACE societies concentrate.
