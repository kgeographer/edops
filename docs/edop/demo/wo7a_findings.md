# WO7a findings — Climate similarity lenses

Notebook: `notebooks/edop/demo/wo7a_climate_lenses.ipynb`

---

## A1 — Data completeness

16,397 L06 basins. All BasinATLAS scalars (`pre_mm_syr`, `ari_ix_sav`, `tmp_dc_syr`) fully
populated. 59 null basins on `pre_concentration` / `seas_phase_offset` — hyper-arid basins
where all-zero monthly precip makes circular concentration undefined. These 59 are masked as
NaN throughout; never zero-coerced.

**Storage note:** `tmp_dc_monthly` in `v_basin06_persist_rev2` is already in °C (not ×10).
Do not divide by 10 when loading this array. The scalar `tmp_dc_syr` in `basin06` IS stored
×10 and must be divided. The circular-stats computations (concentration, phase) are
scale-invariant and unaffected either way, but `tmp_seas_amp` (max−min) must use the
un-divided monthly array to produce correct °C values.

---

## A2 — Sub-lens 1: Precipitation regime

### Variable selection

**Rejected:** `pre_mm_syr` + `ari_ix_sav` + `pre_concentration`.

`ari_ix_sav` (aridity index, P/PET × 100) is a *moisture-balance* variable, not a
precipitation variable. It conflates precipitation with temperature-driven evaporative demand
(PET). Including it in a "Precipitation regime" lens produces matches on similar annual
moisture balance rather than similar precipitation pattern — validated by Rome test where
South Asian basins with similar P/PET ratios appeared despite having different seasonal
distributions.

**Settled variable set:** `pre_mm_syr` + `pre_concentration`

- `pre_mm_syr`: annual precipitation amount
- `pre_concentration`: circular concentration of the monthly precip cycle

Together these answer "where else receives a similar amount of rain, distributed with
similar seasonality?" — honest for the label "Precipitation regime."

`ari_ix_sav` is parked for a possible future **Moisture balance** lens (distinct question:
where else has similar P/PET ratio?).

### Metric

r(pre_mm_syr, pre_concentration) = −0.200. **Normalized Euclidean** adequate.

### Validation

**Timbuktu** (hybas 1060551560): top 15 are Sahelian African basins, 165–206 mm/yr,
pre_concentration 0.856–0.874. Strong pass.

**Rome** (hybas 2060015610): matches have pre_mm_syr 808–858 mm, pre_concentration
0.122–0.135. Internally consistent but concentration is lower than the ~0.28 value at
L08. **Basin-scale effect:** the L06 basin containing Rome averages in sub-humid Apennine
and surrounding areas, diluting the Mediterranean seasonal signal. The metric is correct —
Rome's L06 basin is genuinely not a strong Mediterranean exemplar. Mediterranean
seasonality character is better discriminated by the Seasonal phase lens.

---

## A3 — Sub-lens 2: Temperature regime

### Correlations

All three candidate variables are strongly correlated:

| Pair | r |
|---|---|
| tmp_dc_syr ↔ tmp_seas_amp | −0.837 |
| tmp_dc_syr ↔ tmp_concentration | −0.592 |
| tmp_seas_amp ↔ tmp_concentration | +0.552 |

Physical interpretation: cold mean annual temp, high seasonal amplitude, and high circular
concentration of the temperature cycle all increase together toward continental interiors
and high latitudes. **Mahalanobis mandatory** — r = −0.837 is severe redundancy; NE would
double-count the continental/tropical axis.

All three variables are purely thermal (no dimension-mixing). They are correlated because
the underlying climate physics links them, which is exactly the Mahalanobis use case.

### Settled variable set and metric

`tmp_dc_syr` + `tmp_seas_amp` + `tmp_concentration`, **Mahalanobis**.

### Validation

**Tbilisi** (hybas 2060616700): top 15 are cool-temperate continental basins, 3.6–6.3°C
mean annual, high amplitude, across Eurasia (2060\* Europe, 4060\* Central/East Asia,
7060\* South Asia). Pass.

**London** (hybas 2060053790): top 15 are mild maritime basins, 8.8–10.7°C mean annual,
low amplitude (~13–15°C), in Europe (2060\*) and Pacific NW North America (6060\*). Pass.

---

## A4 — Sub-lens 3: Seasonal phase

**Confirmed unchanged from WO7.**

Variables: `pre_concentration` + `seas_phase_offset`. r = −0.121. **NE adequate.**

**San Francisco** (hybas 7060013180): top 15 have pre_concentration 0.591–0.612 and
seas_phase_offset 5.56–5.74 — tight Mediterranean cluster of Californian (6060\*) and
circum-Mediterranean European (2060\*) basins. Strong pass.

---

## Design principle confirmed

**Do not mix variables from different physical dimensions within a single lens.**
`ari_ix_sav` (moisture balance = precip ÷ evaporative demand) does not belong in a
precipitation lens. This generalizes: each lens must answer exactly one physical question,
honestly reflected in its label. Mixing variables whose correlation structure is driven by
different physical processes produces results that cannot be truthfully labelled.

---

## A-summary: settled lens specifications

| lens_id | label | variables | metric | r_max |
|---|---|---|---|---|
| climate.precip | Precipitation regime | pre_mm_syr, pre_concentration | euclidean | −0.200 |
| climate.temp | Temperature regime | tmp_dc_syr, tmp_seas_amp, tmp_concentration | mahalanobis | −0.837 |
| climate.phase | Seasonal phase | pre_concentration, seas_phase_offset | euclidean | −0.121 |
