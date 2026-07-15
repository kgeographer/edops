# WO5 — Seasonality: monthly arrays + derived indices

**Branch:** `demo_wo5` off `demo`  
**Track:** 2 (Features)  
**Motivation:** Annual means cannot see seasonal structure. The Mediterranean failure in WO4c
(Test 1) is the diagnostic case: Mediterranean and monsoon climates can share nearly identical
annual precip and temp but have opposite seasonal phasing. Seasonality is the dimension
subsistence-scale societies most plausibly key on, making it critical groundwork for the
D-PLACE correspondence work in Phase 4.

Two catalog rows are already staked (`precipitation_monthly` and `temperature_monthly`, both
`planned`). This WO implements them and adds five derived scalar indices.

---

## Step 1 — Extend both basin views

Rewrite `v_basin06_persist_rev1` and its basin08 counterpart to add two array columns:

```sql
ARRAY[
  b.pre_mm_s01, b.pre_mm_s02, b.pre_mm_s03, b.pre_mm_s04,
  b.pre_mm_s05, b.pre_mm_s06, b.pre_mm_s07, b.pre_mm_s08,
  b.pre_mm_s09, b.pre_mm_s10, b.pre_mm_s11, b.pre_mm_s12
]::float[] AS pre_mm_monthly,

ARRAY[
  b.tmp_dc_s01::numeric / 10.0, b.tmp_dc_s02::numeric / 10.0,
  b.tmp_dc_s03::numeric / 10.0, b.tmp_dc_s04::numeric / 10.0,
  b.tmp_dc_s05::numeric / 10.0, b.tmp_dc_s06::numeric / 10.0,
  b.tmp_dc_s07::numeric / 10.0, b.tmp_dc_s08::numeric / 10.0,
  b.tmp_dc_s09::numeric / 10.0, b.tmp_dc_s10::numeric / 10.0,
  b.tmp_dc_s11::numeric / 10.0, b.tmp_dc_s12::numeric / 10.0
]::float[] AS tmp_dc_monthly
```

Apply ÷10 inside the array construction — consistent with the scalar fields already in the
view. The individual `pre_mm_s{nn}` / `tmp_dc_s{nn}` columns do **not** need to be added
individually; the array is the interface. Index 0 = January, index 11 = December.

---

## Step 2 — Derive five scalar indices in `signature.py`

After the basin row is fetched, compute the following from `pre_mm_monthly` and
`tmp_dc_monthly` in Python. All five are `s`-only (no upstream variant).

### 2a. Circular seasonality quantities (mean resultant vector)

For a 12-month cycle, assign each month an angle θₘ = 2π·m/12 (m = 0..11).
Compute the weighted mean resultant vector:

```
Rₓ = Σ(wₘ · cos θₘ) / Σwₘ
Rᵧ = Σ(wₘ · sin θₘ) / Σwₘ
```

where wₘ is the monthly value (precip mm, or temp °C — but see note on temp below).

From this:

- **`pre_concentration`** — magnitude of the precip resultant: `√(Rₓ² + Rᵧ²)`. Range 0
  (perfectly uniform) to 1 (single-month spike). Supersedes PCI; monotonically related.
- **`pre_peak_month`** — peak precip month as a continuous value:
  `(atan2(Rᵧ, Rₓ) / (2π) · 12) mod 12`. Range [0, 12); 0 = January.
- **`tmp_concentration`** — same calculation using temp weights. **Note:** monthly temp
  includes negative values in cold climates, which breaks the weighting assumption (negative
  weights would pull the resultant the wrong way). Shift by subtracting the minimum monthly
  temp before computing: `wₘ = tmp_dc_monthly[m] - min(tmp_dc_monthly)`. This preserves the
  shape of the seasonal cycle while ensuring non-negative weights. The shift does not affect
  concentration or peak month.
- **`tmp_peak_month`** — peak temp month, same formula as `pre_peak_month` using shifted
  weights.

### 2b. Phase offset

- **`seas_phase_offset`** — angular distance between precip and temp peaks, in months.
  Compute the absolute circular difference between the two peak angles, folded to [0, 6]:

```
delta = abs(pre_peak_angle - tmp_peak_angle)  # in radians
phase_offset_months = min(delta, 2π - delta) / (2π) · 12
```

Range [0, 6]. 0 = in-phase (monsoon/continental); 6 = anti-phase (Mediterranean).
This is the primary Mediterranean discriminator.

### 2c. Temperature seasonality amplitude

- **`tmp_seas_amp`** — `max(tmp_dc_monthly) - min(tmp_dc_monthly)`, in °C. Simple,
  interpretable, independent of phasing. High = continental; low = tropical or maritime.

---

## Step 3 — Wire into the signature payload

Add to Band C in `signature.py`. All seven new fields (2 arrays + 5 scalars):

| api_key | type | description |
|---|---|---|
| `pre_mm_monthly` | float[12] | Monthly precip Jan–Dec (mm) |
| `tmp_dc_monthly` | float[12] | Monthly temp Jan–Dec (°C, already ÷10) |
| `pre_concentration` | float | Precip seasonality concentration (0–1) |
| `pre_peak_month` | float | Peak precip month, continuous (0=Jan, 11=Dec) |
| `tmp_concentration` | float | Temp seasonality concentration (0–1) |
| `tmp_peak_month` | float | Peak temp month, continuous (0=Jan, 11=Dec) |
| `seas_phase_offset` | float | Precip–temp phase offset in months (0=in-phase, 6=anti-phase) |
| `tmp_seas_amp` | float | Temp annual amplitude in °C (max−min monthly) |

**Proviso:** CC may find that `signature.py` fetches basin rows differently from what's
assumed here — the array columns need to come through cleanly as Python lists (not psycopg3
memoryview or similar). Check that the array type survives the fetch; handle if not.

---

## Step 4 — Update variable catalog

Mark `precipitation_monthly` and `temperature_monthly` status → `implemented`. Add six new
rows for the derived scalars. Schema keys: `pre_concentration`, `pre_peak_month`,
`tmp_concentration`, `tmp_peak_month`, `seas_phase_offset`, `tmp_seas_amp`. All Band C,
source `Derived`, `historical_validity` = `pre-1500 valid` (they derive from BasinATLAS
climatological means, same provenance as `precip_annual` / `temp_annual`).

Use the following as the `notes` field for each derived scalar:

- **`pre_concentration`**: Circular concentration of the monthly precipitation cycle (0 = rain
  distributed evenly across all months; 1 = all rain falls in a single month). Derived from
  the mean resultant vector of the 12-month precip profile. High values indicate strongly
  seasonal rainfall (monsoon, Mediterranean); low values indicate year-round moisture
  (equatorial, maritime west coast).
- **`pre_peak_month`**: Month of peak precipitation as a continuous value derived from the
  circular mean of the monthly precip profile (0 = January, 11 = December; non-integer values
  indicate a peak between calendar months). Complements `pre_concentration`: together they
  identify when and how sharply the wet season peaks.
- **`tmp_concentration`**: Circular concentration of the monthly temperature cycle (0 = nearly
  isothermal year-round; 1 = extreme single-month peak). Computed after shifting monthly temps
  to non-negative values to preserve cycle shape. Low in the tropics and maritime climates;
  high in continental interiors.
- **`tmp_peak_month`**: Month of peak temperature as a continuous value (0 = January, 11 =
  December). In the Northern Hemisphere typically near 6–7 (July–August); Southern Hemisphere
  near 0–1 or 11–12.
- **`seas_phase_offset`**: Circular distance in months between the peak precipitation month
  and the peak temperature month. Range 0–6. Values near 0 indicate co-occurring wet and warm
  seasons (monsoon, continental). Values near 6 indicate anti-phased seasons: wet-cool /
  dry-warm (Mediterranean, maritime west coast with summer drought). The primary
  seasonality-type discriminator for basin similarity.
- **`tmp_seas_amp`**: Difference between the warmest and coldest month mean temperature (°C).
  High values (>30°C) indicate strongly continental climates; low values (<5°C) indicate
  tropical or maritime climates. Independent of phase: captures the magnitude of the seasonal
  swing regardless of when it occurs.

---

## Acceptance criteria

- `GET /api/signature?lat=41.9&lon=12.5` (Rome) returns `pre_concentration` ~0.5–0.7,
  `seas_phase_offset` ~5–6 (winter-wet / summer-dry Mediterranean signal).
- `GET /api/signature?lat=28.6&lon=77.2` (Delhi) returns `seas_phase_offset` ~0–1
  (summer monsoon co-incident with heat peak).
- `GET /api/signature?lat=51.5&lon=-0.1` (London) returns `pre_concentration` < 0.2
  (year-round rainfall).
- Array fields `pre_mm_monthly` and `tmp_dc_monthly` are present, length 12, no nulls for
  all three locations.
- All existing tests pass; new contract tests added for the three acceptance cases above.

---

## Out of scope for WO5

- Exposing the new fields in the sandbox UI — separate future WO.
- Incorporating the new indices into the similarity instrument (C_climate Mahalanobis) —
  separate future WO, after WO5 acceptance.
- Upstream variants of the monthly arrays or derived scalars — not in BasinATLAS; not planned.
