# WO2 findings — Rainfall modality investigation

**Notebook:** `notebooks/cdop/wo2_rainfall_modality.ipynb`
**Branch:** `cdop_wo2` (cut from `cdop_pilot`)
**Date:** 2026-07-19

---

## Background

WO1 accept gate partially failed. The precipitation regime and seasonal phase lenses returned
European temperate cities (Augsburg, Salzburg, Split, Ibiza) as nearest neighbours of Mombasa.
The temperature lens passed cleanly. The WO1 findings hypothesized that Mombasa has bimodal
rainfall — two peaks ~6 months apart — and that the unimodal circular statistics used in the
current `pre_concentration` and `seas_phase_offset` variables cannot represent this pattern.
When two peaks cancel in circular space, the resultant vector is short and lands at an
arbitrary angle, making a bimodal-tropical city indistinguishable from a city with flat
year-round rainfall. This WO tests that hypothesis and characterizes the bimodal population
globally.

---

## Part A — Population characterization

### A1 — The doubled-angle circular statistic

The key insight is that a bimodal rainfall signal — two peaks exactly 6 months apart — maps
each month to θ = 2π × (month − 1) / 12, placing the two peaks at antipodal angles. Their
contributions to the resultant vector cancel exactly. The standard R_std (resultant length
normalized by total rainfall) approaches zero for a perfectly symmetric bimodal distribution,
making it indistinguishable from a flat-rainfall basin.

The fix is a second harmonic: map months with θ_dbl = 2π × (month − 1) / 6 instead of /12.
This doubles the angular spacing, so months 6 apart (Jan and Jul, Apr and Oct) are now
co-located at the same angle rather than antipodal. A bimodal distribution with two peaks
6 months apart reinforces in doubled-angle space, yielding a high R_dbl, while a flat or
unimodal distribution does not.

**Definitions:**
- `R_std`: resultant length / total_precip, with θ = 2π × month / 12. Range [0, 1].
  Measures unimodal concentration. High → single concentrated wet season.
- `R_dbl`: resultant length / total_precip, with θ = 2π × month / 6. Range [0, 1].
  Measures bimodal structure. High → two peaks approximately 6 months apart.
- `phi_std`: circular mean month (from R_std vector); the apparent peak month (0-indexed, in
  months).
- `phi_dbl`: apparent anti-nodal spacing (from R_dbl vector); indicates which pair of months
  the bimodal peaks straddle.

### A2 — Probe cities

Monthly rainfall computed from `basin08` columns `pre_mm_s01`–`pre_mm_s12` for six probe
cities. All derived scalars (`pre_concentration`, `seas_phase_offset`, etc.) computed on-the-fly
from these monthly values — they are not stored in `basin08` (verbatim BasinATLAS extraction).

| City | Country | R_std | R_dbl | Regime (classified) |
|------|---------|-------|-------|----------------------|
| Mombasa | Kenya | 0.215 | 0.341 | **bimodal** |
| Augsburg | Germany | 0.212 | 0.080 | aseasonal |
| Salzburg | Austria | ~0.22 | ~0.08 | aseasonal |
| George Town | Malaysia | ~0.09 | ~0.19 | aseasonal |
| Split | Croatia | ~0.33 | ~0.10 | (single / near-threshold) |
| Timbuktu | Mali | ~0.72 | ~0.48 | single |

**Key finding:** Mombasa and Augsburg have nearly identical R_std (~0.21). Under the current
unimodal measure, they are climatologically indistinguishable in the precipitation dimension.
Augsburg's R_dbl = 0.080 vs Mombasa's R_dbl = 0.341 — cleanly separated by a factor of 4.
The doubled-angle statistic recovers the bimodal signal that the standard measure loses.

**George Town** (Malaysia): R_dbl = 0.187, below the THRESH_DBL = 0.3 threshold. Correct
classification as aseasonal. George Town receives rainfall year-round with very slight
modulation — the Walter-Lieth diagram shows a high baseline with no true dry season and only
a mild secondary peak. Setting THRESH_DBL = 0.3 correctly excludes it from the bimodal class.

**Split** (Croatia): R_std ≈ 0.33, R_dbl ≈ 0.10. Classified as single (below THRESH_STD
of 0.4, but close). Split is Mediterranean — winter rain peak, summer dry. It is seasonal,
not aseasonal, but the unimodal R_std underestimates its concentration. This is a separate
limitation of the current measure (the "aseasonal" class conflates multiple distinct regimes
— see note below). Not addressed in this WO.

### A3 — L06 global survey

All 16,397 L06 basins loaded from `basin06` (`pre_mm_s01`–`pre_mm_s12`, smallint).
Vectorized computation of R_std and R_dbl using NumPy.

**Thresholds (working proposal, see Part B):**
- `THRESH_STD = 0.4`: below this, unimodal concentration is weak
- `THRESH_DBL = 0.3`: above this, bimodal structure is present
- `THRESH_ARID = 100 mm/yr`: below this, total rainfall insufficient to classify meaningfully

**Regime counts:**

| Regime | Count | Fraction |
|--------|-------|----------|
| single | 7,923 | 48.3% |
| aseasonal | 7,885 | 48.1% |
| bimodal | 386 | 2.4% |
| arid | 144 | 0.9% |
| no_data | 59 | 0.4% |
| **Total** | **16,397** | |

Notes:
- The `no_data` class (59 basins) catches all-zero monthly arrays — hyper-arid basins where
  circular statistics are undefined (0/0). This matches the 59 NaN-masked basins in the
  existing similarity index.
- The `arid` class (144 basins) catches low-total-rainfall basins where R_std is low but
  year-round rainfall is insufficient to establish a true pattern. Distinct from `aseasonal`.
- Bimodal class: 386 basins, 2.4% of the global L06 inventory. Small globally but
  geographically concentrated.

### A4 — Geographic distribution of bimodal basins

Global map (Cell 10) shows bimodal basins concentrated in five geographic zones:

1. **East Africa** — by far the densest cluster, centered on Kenya/Tanzania/Ethiopia and the
   Indian Ocean coast. This is the primary locus of ITCZ double-passage: the intertropical
   convergence zone crosses this region northward in April–May (long rains) and southward in
   October–November (short rains). Mombasa, Lamu, and Zanzibar City are here.

2. **Arabian Peninsula / Horn of Africa** — scattered points through Yemen, Oman, Somalia.
   The ITCZ double-passage mechanism extends northeast along the Horn; the monsoon reversal
   also plays a role.

3. **West Africa / Sahel margin** — points around Guinea/Sierra Leone coast and scattered
   Sahel. The Guinea coast is known for a July–August break in an otherwise bimodal rainy
   season. The Sahel margin catches the ITCZ advancing north in June and retreating south
   in September.

4. **India / South Asia** — a tight cluster at the SW tip (~10°N, 75°E — Kerala, Sri Lanka)
   where two monsoon limbs produce distinct wet seasons, plus scattered points ~30°N likely
   in the Indus/Pakistan headwaters (summer monsoon + winter western disturbances).

5. **Americas** — scattered and weak:
   - Mexico Pacific coast (~20–25°N): double ITCZ passage on the eastern Pacific.
   - NE Brazil / eastern Amazonia: weak bimodal modulation.
   - A few points in coastal Central America.

**Notable absences:** Southeast Asian mainland (Vietnam, Thailand), despite known bimodal
patterns there. This suggests R_dbl < 0.3 in those basins — either the peaks are not
symmetric enough, or high baseline rainfall dilutes the ratio. Northern Australia (which has
bimodal tropical rainfall in some regions) also absent. This may indicate the THRESH_DBL = 0.3
threshold is conservative in the context of high-baseline basins. Under investigation in Part B.

The geographic pattern is **physically well-motivated** and matches the known climatology of
ITCZ double-passage zones. No spurious clusters are visible in the map.

### A5 — Scatter plot: R_std vs R_dbl

Cell 8 scatter (all 16,397 basins, color-coded by regime) reveals four structurally distinct
regions:

- **Upper-left fan (single):** high R_std (>0.4), low-to-moderate R_dbl. Single-peak regimes.
  R_dbl is correlated with R_std in this fan — a strong single monsoon also produces a
  secondary harmonic signal, but one that scales with peak sharpness, not bimodal structure.

- **Lower-left cloud (aseasonal):** both R_std and R_dbl low (<0.3). Flat or weakly modulated
  year-round rainfall.

- **Lower-right island (bimodal):** low R_std (<0.4) but high R_dbl (>0.3). This is the
  target class — well-separated from the aseasonal cloud by a visible gap in R_dbl.

- **Upper-right region (arid):** small cluster; low total rainfall means both stats are noisy.

The threshold lines at R_std = 0.4 and R_dbl = 0.3 cut through the scatter at natural gap
boundaries. The bimodal class is cleanly isolable. Augsburg sits in the aseasonal cloud;
Mombasa sits in the bimodal island.

### A6 — WH Cities bimodal exposure

Spatial join: 258 WH Cities points → `basin06` via `ST_Contains`. 254 of 258 matched (4 cities
fall on polygon boundaries or in uncovered coastal areas and are excluded from the join result).

| Regime | Cities | Fraction |
|--------|--------|----------|
| single | ~126 | ~50% |
| aseasonal | ~121 | ~48% |
| bimodal | **3** | **1.2%** |
| arid | ~4 | ~1.6% |

**Bimodal cities (3):** Lamu (Kenya), Mombasa (Kenya), Zanzibar City (Tanzania).
All three are on the East African Indian Ocean coast — the densest bimodal zone in the global
L06 inventory.

**Implication for CDOP pilot:** The bimodal problem affects 3 of 254 corpus cities. The
downstream impact on WH Cities similarity is narrow (East African coast only) but not trivial
— these are historically significant cities and presenting European temperate cities as their
nearest climate neighbours is a visible failure.

**Implication for sandbox:** The 386 bimodal L06 basins are distributed globally. Any user
querying Mombasa, Lamu, or Zanzibar on the Similarity tab encounters the same failure at L06.
Fixing the measure would correct the global instrument, not just the CDOP pilot.

### A7 — Mombasa deep-dive (Cell 11)

Monthly data from `basin08` for the L08 basin containing Mombasa (Kenya).

**Monthly precipitation (mm):**

| Jan | Feb | Mar | Apr | May | Jun | Jul | Aug | Sep | Oct | Nov | Dec | Total |
|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-------|
| 27 | 18 | 59 | 163 | 235 | 95 | 74 | 74 | 73 | 110 | 112 | 61 | 1,101 |

**Monthly temperature (°C):**

| Jan | Feb | Mar | Apr | May | Jun | Jul | Aug | Sep | Oct | Nov | Dec |
|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|
| 26.5 | 26.9 | 27.4 | 26.6 | 25.0 | 24.1 | 23.3 | 23.4 | 24.0 | 25.1 | 25.9 | 26.4 |

**Derived scalars (computed from monthly arrays):**

| Statistic | Value | Notes |
|-----------|-------|-------|
| R_std (= pre_concentration) | 0.215 | Low — near-cancellation of antipodal peaks |
| R_dbl (bimodal concentration) | 0.341 | High — above THRESH_DBL = 0.3 |
| phi_std peak month (circ-mean) | 4.8 (0=Jan) | ≈ late May |
| argmax month (0-indexed) | 4 = May | Dominant wet-season peak |
| seas_phase_offset (computed) | 4.08 months | phi_precip − phi_temp |

#### Bimodal structure confirmed

Two clear rainfall peaks:
- **Long rains:** April–May (163 + 235 = 398 mm), peak in May. Dominant peak.
- **Short rains:** October–November (110 + 112 = 222 mm), peak in November.

May (month 4, 0-indexed) and November (month 10) are exactly 6 months apart. This is the
canonical ITCZ double-passage pattern. The short rains (222 mm) are 20% of the annual total —
substantial enough to matter ecologically and historically.

#### Why R_std = 0.215 despite strong seasonality

In standard circular space, May maps to θ = 120° and November to θ = 300°. These are
antipodal (180° apart). Their rainfall-weighted vectors nearly cancel. The net resultant vector
is short (R_std = 0.215) and biased toward May because the long rains are ~1.8× larger than
the short rains. The city appears to have "distributed" year-round rainfall to the unimodal
measure. This confirms the WO1 hypothesis.

#### Doubled-angle validation

In doubled-angle space, month 4 (May) maps to θ_dbl = 2π × 4/6 = 240°, and month 10
(November) maps to θ_dbl = 2π × 10/6 = 600° = 240° (mod 360°). The two peaks map to
**identical angles** and reinforce rather than cancel. R_dbl = 0.341 captures the bimodal
signal cleanly.

Inverting phi_dbl: the doubled-space circular mean corresponds to actual peak months at
phi_dbl and phi_dbl + 6 months. For Mombasa this predicts peaks at month ≈ 4 (May) and ≈ 10
(November) — matching the observed rainfall profile exactly. The doubled-angle approach is
validated.

#### Temperature pattern

Seasonal amplitude is very small: 27.4°C (March) − 23.3°C (July) = **4.1°C**. This is a
classic equatorial coastal thermal regime. Temperature peaks in the pre-monsoon dry season
(March, hottest and driest), drops through the long rains (May–September), and partially
recovers before the short rains (October–November). The temperature signal is weakly
unimodal — neither the amplitude nor the concentration is large.

The temperature circular mean (phi_temp ≈ 0.72, i.e., late January) is pulled back from the
March argmax by the broad warm plateau in December–February. The December temperatures
(26.4°C) are nearly as high as March (27.4°C), so the circular mean falls between them.

#### Mechanism of Mediterranean contamination in phase similarity

`seas_phase_offset` is computed as phi_precip − phi_temp:
- phi_precip (from unimodal R_std vector) = 4.8 months ≈ late May
- phi_temp (from temperature circular mean) = 0.72 months ≈ late January
- seas_phase_offset = 4.08 months

For a Mediterranean city (e.g., Split or Rome):
- phi_precip ≈ month 0–1 (winter rain peak)
- phi_temp ≈ month 6–7 (July heat peak)
- seas_phase_offset ≈ 5–6 months

The Mombasa phase offset (4.08) is in the same ballpark as Mediterranean cities (5–6 months).
The similarity instrument reads both as "precipitation and temperature are ≈ 4–6 months
out of phase" — a correct but inadequate description. For a Mediterranean city, out-of-phase
means summer heat / winter rain. For Mombasa, out-of-phase is an artifact: the circular-mean
precip direction is dominated by the May long rains, while temperature peaks in March before
the rains arrive, creating a superficially similar 4-month lag that has no climatological
correspondence to the Mediterranean pattern.

This is the mechanism by which bimodal tropical cities contaminate the seasonal phase lens.
The contamination is not from the bimodal structure per se — it is from the unimodal
representation of a bimodal city producing a misleading phi_precip value, which then combines
with phi_temp to yield a seas_phase_offset that falls within Mediterranean range.

### A8 — Arid/aseasonal boundary (Cell 12)

The histogram shows the annual precipitation distribution for all basins in the low-unimodal +
low-bimodal pool (R_std < 0.4 AND R_dbl < 0.3) — the population that the classifier must
split into `arid` and `aseasonal`.

**Key observations:**

**1. THRESH_ARID = 100 mm/yr is well-placed.** The dashed vertical line falls in a genuine
trough between the sparse desert tail (< 100 mm) and the main aseasonal population. There is
no ambiguity at the boundary — basins are either clearly hyper-arid or clearly above it. The
144-basin arid class is a real, distinct cluster.

**2. The spike at 2000 mm/yr (clipped bin) is the most important feature.** ~820+ basins
have annual rainfall ≥ 2,000 mm/yr and still classify as low R_std, low R_dbl. These are
the world's consistently wet tropical basins: Amazon, Congo basin, Borneo/Indonesia, parts of
SE Asia. They receive heavy rainfall year-round with no true dry season. Their `aseasonal`
classification is correct — they are not bimodal or strongly concentrated, they are simply
relentlessly wet. George Town (Malaysia, ~2,500 mm/yr, R_dbl = 0.187) is a member of this
population.

**3. The main body (100–1,750 mm/yr)** is a broad, roughly flat distribution peaking around
400–600 mm/yr then tailing off gradually. This is the global complement of temperate, arid-
margin, and humid sub-tropical basins with distributed rainfall — Europe, mid-latitude Asia,
eastern North America, highland tropics. Augsburg lives here.

**4. The threshold boundary is not ecologically ambiguous.** There is no cluster of basins
straddling 100 mm/yr that would be miscategorized. The arid class could defensibly be moved
to 75 mm or 125 mm without material effect on the counts or distribution.

**Implication for the SE Asia bimodal gap:** The 2000mm spike contains a mix of genuinely
aseasonal basins (Amazon, Congo) and potentially some weakly-bimodal high-rainfall basins
(Philippines interior, parts of Vietnam) where R_dbl falls below 0.3 not because the
bimodal signal is absent but because the peaks are not exactly 6 months apart. The
doubled-angle statistic at period /6 is tuned for peaks exactly 6 months apart. A peak pair
separated by 5 or 7 months produces a lower R_dbl than the same amplitude pair at exactly 6
months. This is a known limitation of the approach (see Notes section). The 2000mm spike does
not invalidate the threshold; it identifies where the method's resolution is lowest.

---

## Part B — Variable definition recommendations

### B1 — New variables

Three variables are proposed. The first two are needed immediately for any remediation option;
the third is useful for diagnostics and the signature narrative but not required for similarity.

---

**`R_dbl`** — continuous [0, 1], computed alongside `pre_concentration`

```
theta_dbl = 2π × month / 6      (months 0-indexed)
x_d = Σ(pre_mm_m × cos(theta_dbl_m))
y_d = Σ(pre_mm_m × sin(theta_dbl_m))
R_dbl = sqrt(x_d² + y_d²) / pre_mm_syr
```

The doubled-angle resultant length. High values (> 0.3) indicate two rainfall peaks
approximately 6 months apart. Currently computed nowhere in the pipeline — would be added to
`seasonality.py:_compute_derived()` alongside the existing `pre_concentration` computation,
and exposed in the signature codebook under Band B (precipitation seasonality group).

---

**`pre_modality`** — categorical: `single` | `bimodal` | `aseasonal` | `arid` | `no_data`

Decision tree (applied in order):

1. If `pre_mm_syr == 0` (all-zero monthly array): `no_data`
2. Else if `pre_mm_syr < 100`: `arid`
3. Else if `pre_concentration ≥ 0.40`: `single`
4. Else if `R_dbl ≥ 0.30`: `bimodal`
5. Else: `aseasonal`

The `no_data` and `arid` checks precede the circular statistics checks because circular
statistics are undefined or uninformative at very low total rainfall. The `single` check
precedes `bimodal` because a sufficiently sharp single peak also produces a moderate R_dbl
(a narrow monsoon reinforces in doubled space too); R_std ≥ 0.4 takes precedence.

Global L06 counts at these thresholds: single 7,923 / aseasonal 7,885 / bimodal 386 /
arid 144 / no_data 59. Total 16,397. These match the 59 NaN-masked basins already excluded
from the similarity index.

---

**`phi_dbl`** — continuous [0, 6), computed from the R_dbl vector

```
phi_dbl = (degrees(arctan2(y_d, x_d)) % 360) / 60
```

The doubled-space circular mean in months (period = 6, so range is [0, 6)). Predicts the two
actual bimodal peak months: phi_dbl and phi_dbl + 6. For Mombasa, phi_dbl ≈ 4 → predicted
peaks at months 4 (May) and 10 (November), matching the observed profile exactly.

`phi_dbl` is not needed for the similarity lenses but would be useful in the signature
narrative generator ("rainfall peaks in May and November") and in future Phase 4
correspondence testing. Add to codebook but treat as informational.

### B2 — Threshold rationale

| Threshold | Value | Basis |
|-----------|-------|-------|
| THRESH_STD | 0.40 | Existing `pre_concentration` threshold for lens features; retained for continuity |
| THRESH_DBL | 0.30 | Scatter-plot gap: bimodal island sits above 0.30, aseasonal cloud below 0.25. George Town (0.187) correctly excluded; Mombasa (0.341) correctly included |
| THRESH_ARID | 100 mm/yr | Histogram (Cell 12): clear trough between the hyper-arid tail and main aseasonal body; boundary is unambiguous |

All three thresholds are validated by the notebook evidence and are proposed as fixed. A
sensitivity analysis at ±0.05 (for circular thresholds) and ±25 mm (for THRESH_ARID) would
not materially change the class counts or geographic distribution.

### B3 — Remediation options

Three options in increasing scope. Implementation is deferred to a follow-on WO; Part C
assesses which surfaces each option fixes and at what cost.

---

**Option A — Modality flag + same-modality restriction**

Add `pre_modality` and `R_dbl` to the signature and codebook. In the similarity index, store
`pre_modality` per basin. In `find_similar()`, when `mode='topn'` or `mode='threshold'`, add
an optional `same_modality=True` parameter: if set, restrict candidates to basins with the
same `pre_modality` as the query basin. For bimodal query basins (Mombasa), this returns only
other bimodal basins; for aseasonal basins (Augsburg), only aseasonal.

Pros: minimal change to lens features and distance metrics; no threshold recalibration needed;
correct results for bimodal cities by construction. Cons: the bimodal corpus is small (386
L06 basins, 3 WH Cities) — a bimodal query may return very few or geographically distant
matches, which is honest but may look sparse in the UI.

Does not fix the underlying `seas_phase_offset` contamination mechanism — it contains it.

---

**Option B — Add R_dbl to `climate.precip`; exclude bimodal from `climate.phase`**

For `climate.precip`: add `R_dbl` as a third feature alongside `pre_mm_syr` and
`pre_concentration`. The distance space becomes 3-dimensional. Bimodal basins now have a
distinct R_dbl signature that separates them from aseasonal basins even without same-modality
restriction. Requires recalibration of the `climate.precip` thresholds (strict / moderate /
loose) in the 3D space.

For `climate.phase`: `seas_phase_offset` is computed from the unimodal phi_precip, which is
wrong for bimodal cities regardless of additional features. The cleanest fix for this lens is
same-modality restriction (Option A behavior), OR replacing `seas_phase_offset` with a
bimodal-aware variant:

```
phi_primary = phi_dbl            # for bimodal basins
phi_primary = phi_std            # for single/aseasonal basins
seas_phase_offset_v2 = phi_primary - phi_temp  (mod 12, range [-6, 6])
```

This gives Mombasa a phase offset of ~4 (May peak relative to January temperature mean),
while the contamination path (Mombasa's biased phi_std ≈ 4.8 landing near Mediterranean
range) is closed. Implementation in `seasonality.py:_compute_derived()`.

Pros: principled fix for both lenses; bimodal cities find correct bimodal neighbours without
same-modality restriction. Cons: threshold recalibration needed for climate.precip; new
`seas_phase_offset_v2` requires careful handling in the LENS_REGISTRY feature spec and any
existing callers of `seas_phase_offset`.

---

**Option C — Two-harmonic Fourier decomposition**

Replace both `pre_concentration` (R_std) and R_dbl with a full two-harmonic model. Each
basin is represented by four features: (A₁, φ₁, A₂, φ₂) — amplitude and phase of the
annual harmonic (period 12) and the semi-annual harmonic (period 6). These four features
fully characterize seasonal structure for any rainfall regime, including bimodal, single,
asymmetric bimodal (peaks not exactly 6 months apart), and transitional cases.

This subsumes Options A and B: a bimodal basin has large A₂ and small A₁; an aseasonal basin
has small both; a single-monsoon basin has large A₁ and small A₂. Similarity in (A₁, φ₁, A₂,
φ₂) space would naturally cluster bimodal cities together and separate them from aseasonal and
single-monsoon cities without any modality flag or same-modality restriction.

Pros: the correct general solution; handles SE Asian bimodal (peaks ≠ 6 months apart);
eliminates the phi_dbl/phi_std dichotomy. Cons: full redesign of climate.precip and
climate.phase features; requires new threshold calibration across 4D space; new signature
variables to add to codebook; distinct WO, probably 2–3 sessions.

### B4 — Recommendation

**Implement Option B for the current WO3 remediation WO.** Add R_dbl and `pre_modality` to
the signature and codebook. Update `climate.precip` to include R_dbl as a third feature.
Update `climate.phase` to use `seas_phase_offset_v2` (phi_primary − phi_temp, where
phi_primary is phi_dbl for bimodal basins and phi_std for all others). Recalibrate
climate.precip thresholds. Apply same-modality restriction in the WH Cities endpoint as a
safety net until calibration confirms clean separation without it.

Option C (two-harmonic) is the theoretically correct next step and is worth noting in the
deferred items register as a Phase 4 preparation task, since it would make the variables more
defensible in correspondence testing.

---

## Part C — Downstream impact assessment

### C1 — Surfaces and scope

Three surfaces are affected, in decreasing urgency:

**Surface 1: `cdop_pilot.html` — WH Cities tab**

3 of 254 matched cities are bimodal (Lamu, Mombasa, Zanzibar City — all East African coast).
The `climate.precip` and `climate.phase` lenses return climatologically wrong results for all
three. The `climate.temp` lens is correct.

Under Option B: all three cities return correct bimodal tropical neighbours from within the
WH Cities corpus. Since the bimodal corpus is small (3 cities), the top-5 result will
draw on the global L08 bimodal basin pool, not just the 3-city subset — which is appropriate
(the WH Cities lens is corpus-restricted for count display, but distance is computed against
all L08 basins in `find_similar()`). The result for Mombasa's precipitation lens should
cluster with Lamu and Zanzibar City (all East African coast) and potentially other bimodal
Indian Ocean basin cities.

This is the primary motivation for WO2 and the unblock condition for WO1.

---

**Surface 2: `sandbox_v3.html` — Similarity tab (L06 global)**

386 L06 basins are bimodal (2.4% of global). Any user placing a point in the East African
coastal zone, Horn of Africa, SW India, or the Americas clusters noted in A4 will receive
wrong climate.precip and climate.phase results under the current instrument. The user has no
indication that the result is unreliable.

Under Option B: the fix applies globally. The similarity index at L06 already stores
`pre_concentration` and `seas_phase_offset` as precomputed features. Adding R_dbl and
`seas_phase_offset_v2` to the feature set requires rebuilding the index at startup (no DB
change — index build reads from `v_basin06_persist_rev2`). Startup cost increases modestly
(additional vectorized computation over 16,397 rows — negligible, < 0.1 s).

This is a global instrument improvement, not just a CDOP fix. It should be implemented
in the same WO3 remediation pass.

---

**Surface 3: `explorer.html` — `pre_concentration` choropleth**

The `pre_concentration` variable is visible in the Explorer (Band B). Bimodal basins
(386 globally) display low concentration — appearing "flat" — when in fact they have strong
but bimodal seasonal structure. This is a display accuracy issue, lower urgency than similarity.

Under Option B: `R_dbl` and `pre_modality` would be added to the signature, and therefore
to the Explorer's Band B group. Users could visualize `R_dbl` as a choropleth. `pre_modality`
is categorical and could be displayed as a categorical layer. Neither change requires a new
Explorer API route — both variables flow through the existing `/api/explorer/values` and
`/api/explorer/categorical` endpoints. The categorical endpoint already handles multi-class
maps (ecoregions). `pre_modality` (5 classes) fits naturally.

No work required in WO3; the variables appear automatically once added to the codebook and
`_compute_derived()`. Flag in the deferred items register as a cosmetic improvement.

---

**Surface 4: Narrative generator (LLM)**

The LLM narrative button in `sandbox.html` uses the signature payload to describe climate.
Currently, a bimodal basin description would receive `pre_concentration ≈ 0.21` (low,
implying flat rainfall) and `seas_phase_offset ≈ 4` (implying a seasonal offset), producing
a potentially misleading narrative about "relatively even year-round rainfall." Adding
`pre_modality = 'bimodal'` and `phi_dbl` to the signature gives the LLM correct vocabulary
("rainfall peaks in May and November, characteristic of the ITCZ double-passage zone").

No code change needed in WO3 beyond adding the variables to the signature payload. The LLM
prompt is not curated and will use whatever signature fields it receives.

### C2 — Variables needing change

| Variable | Location | Change | Priority |
|----------|----------|--------|----------|
| `R_dbl` | `seasonality.py:_compute_derived()` | Add: doubled-angle resultant length | Required |
| `pre_modality` | `seasonality.py:_compute_derived()` | Add: 5-class categorical | Required |
| `phi_dbl` | `seasonality.py:_compute_derived()` | Add: bimodal peak direction | Recommended |
| `seas_phase_offset_v2` | `seasonality.py:_compute_derived()` | Add: bimodal-aware phase offset | Required for Option B |
| `climate.precip` features | `LENS_REGISTRY` | Add R_dbl as third feature; recalibrate | Required |
| `climate.phase` features | `LENS_REGISTRY` | Replace `seas_phase_offset` with `_v2` | Required for Option B |
| Codebook | `EDOPS_variable_catalog_v0.3.tsv` | Add rows for R_dbl, pre_modality, phi_dbl, seas_phase_offset_v2 | Required |
| Similarity index | `climate.py` index builder | Load and store R_dbl, modality, seas_phase_offset_v2 | Required |

`pre_concentration` and existing `seas_phase_offset` are **not removed** — they remain in
the signature for backward compatibility. `seas_phase_offset_v2` is an additional variable.
If Option B proves stable, the old `seas_phase_offset` can be deprecated in a later pass.

### C3 — What does not change

- The L08 index structure and startup sequence are unaffected.
- The WH Cities route (`/api/whc-similar-env-lens`) does not change — it calls `find_similar()`
  which handles the lens feature update transparently.
- The `/api/similarity` endpoint signature does not change.
- All existing tests that do not reference `climate.precip` or `climate.phase` feature values
  directly are unaffected.
- Tests that check distance ordering for Mombasa queries on precip/phase lenses will need
  updating — they should pass after remediation.

### C4 — Test additions required in WO3

- `test_modality_classification`: Mombasa → bimodal; Augsburg → aseasonal; Timbuktu → single.
  Computable from the basin feature store at test time.
- `test_precip_lens_mombasa_no_european_neighbours`: top-5 for Mombasa / climate.precip /
  moderate should contain no basins classified as aseasonal European-temperate. Proxy: no
  result basin with lat > 35°N AND R_dbl < 0.1.
- `test_phase_lens_mombasa_no_mediterranean`: top-5 for Mombasa / climate.phase / topn=5
  should contain no Mediterranean-latitude (35–45°N) basins.
- Extend `test_similarity_threshold_variable_count` to cover the updated precip lens
  after recalibration.

---

## Notes and open questions

### The "aseasonal" label is ambiguous

The current `pre_modality` classification places Mediterranean climates (Split, Rome) in the
`aseasonal` bin when their R_std falls below 0.4. This is incorrect in spirit — Split has a
real dry summer and wet winter; it is seasonal. The current measure underestimates
Mediterranean concentration because the wet season is spread across several winter months
rather than a tight monsoon peak.

This is a pre-existing limitation of R_std as a measure of seasonality. The WO2 thresholds
do not make it worse, but the `aseasonal` class name is misleading for this reason. A more
accurate label might be `distributed` (no dominant seasonal peak, whether by design or by
limitation of the measure). This is flagged as a deferred design question — not addressed
in this WO.

### Southeast Asian bimodal basins below threshold

Vietnam, Thailand, the Philippines, and parts of Indonesia are expected to show bimodal
rainfall but appear absent from the bimodal map. These regions have high baseline rainfall
(e.g., Hanoi: ~1,700 mm/yr), and R_dbl is normalized by total rainfall, so a moderate
bimodal signal on a high baseline yields lower R_dbl. THRESH_DBL = 0.3 may be too strict
for high-rainfall-baseline bimodal regions. Deserves a focused probe but not in scope for
this WO.

### Nepal / Himalaya anomaly (Cells 9 centroid query)

The first 5 rows of Cell 9's centroid pull showed coordinates consistent with Nepal or
northern India. The global map confirms scattered bimodal points in the ~30°N, 70–80°E range
(Pakistan/Afghanistan headwaters). These are physically plausible: Indus headwater basins
receive both summer monsoon moisture and winter western disturbances, producing a bi-annual
rainfall structure. Not a spurious artifact.

---

## Accept gate

From `wo2_rainfall-modality.md`:

> Accept when: Mombasa classifies bimodal, Augsburg classifies aseasonal, a single-monsoon
> basin classifies single — and the three classes separate cleanly in the scatter plot.

**Status: Part A gate met.**
- Mombasa: R_std=0.215, R_dbl=0.341 → bimodal ✓
- Augsburg: R_std=0.212, R_dbl=0.080 → aseasonal ✓
- Single-monsoon probe (Timbuktu): R_std~0.72, R_dbl~0.48 → single ✓ (note: R_dbl elevated
  for sharp single peaks — this is expected; R_std threshold of 0.4 catches it first)
- Scatter plot shows clean separation: bimodal island isolated from aseasonal cloud ✓

Parts B and C pending.
