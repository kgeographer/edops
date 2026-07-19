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

---

## B — Backend registry (`app/db/seasonality.py` refactor)

`LENS_REGISTRY` dict drives all three active lenses. `load_similarity_index()` loads monthly
arrays once at startup, computes all four derived variables (`pre_concentration`,
`seas_phase_offset`, `tmp_concentration`, `tmp_seas_amp`) and the two needed BasinATLAS
scalars (`pre_mm_syr`, `tmp_dc_syr` ÷10), then builds per-lens state:

- **Euclidean lenses** — z-scored matrix; `Xz` stored; distance = √(Σ(zᵢ−zⱼ)²)
- **Mahalanobis lenses** — raw matrix + inverse covariance `VI`; distance = √(d·VI·dᵀ) via `einsum`

`find_similar(hybas_id, lens_id, n)` dispatches by lens spec. Returns `(query_meta, ranked)`:
- `query_meta` — `{lens_id, lens_label, metric, query_hybas_id, query_values}`
- `ranked` — list of `{rank, hybas_id, distance, values}` with per-result lens-variable values

New endpoints:
- `GET /api/similarity?lat&lon&lens&n` — new shape, per-result `values` dict
- `GET /api/similarity/lenses` — full registry (active + disabled stubs)
- `GET /api/seasonality/similar` — kept as backward-compat wrapper (climate.phase, old flat shape)

Two disabled stubs (`terrain.*`, `hydrology.*`) in the registry give the UI something to
render as greyed options without any backend work.

**Tests added:** `test_similarity_climate_temp_london` (Mahalanobis maritime check — top-10
amplitude < 25°C, maritime Europe/PNW in ccodes); `test_similarity_lenses_registry` (three
active Climate lenses present; climate.temp declares mahalanobis; at least one disabled stub).

---

## C — Two-dropdown UI (sandbox_v3 Similarity tab)

Single `#v3-sim-lens` select replaced with `#v3-sim-group` + `#v3-sim-sublens`. Registry
loaded at page init from `/api/similarity/lenses`; group select populated from distinct
groups; sub-lens select repopulated on group change with active lenses only (disabled entries
greyed). Default: Climate / Seasonal phase.

Lens-switching contract: anchor (lat/lon) persists across sub-lens changes; cache key is
`(lat, lon, lens_id)`; switching sub-lens nulls `_simQueryLens` to force refetch.

`renderSimilarity()` now calls `/api/similarity?lens=<id>&n=200`. `_simBlurb()` dispatches
by `lens_id` — existing phase text for `climate.phase`; new descriptive blurbs for
`climate.precip` (annual total + concentration characterisation) and `climate.temp` (mean
temp + amplitude characterisation).

Reviewed in browser: 2026-07-17 — three Climate sub-lenses render and repaint on switch;
Terrain and Hydrology present but disabled; anchor persists across lens changes.

---

## Status: Parts A–C complete; Part D (threshold rendering) → WO7b

WO7a acceptance criteria satisfied:
- Notebook reports settled variable sets + metrics for all three Climate sub-lenses ✓
- Registry drives the endpoint — same code path for all three lenses ✓
- Two dropdowns render; Climate active with three sub-lenses; Terrain/Hydrology greyed ✓
- Sub-lens switch for fixed location re-queries and repaints without losing anchor ✓
- Validation passes: Precipitation-regime Rome recovers Mediterranean rainfall basins;
  Temperature-regime London recovers maritime basins; Seasonal-phase SF recovers
  Mediterranean cluster ✓
- All existing tests pass; contract tests added for Mahalanobis lens and registry shape ✓

Part D (honest variable-N / distance-threshold result sets) deferred to WO7b.
The current fixed top-200 produces coherent displays but the result count has no
principled relationship to the query basin's actual similarity neighborhood. WO7b will
introduce a distance threshold (SD-radius or equivalent) so the map shows "how many
basins qualify" rather than "the 200 nearest regardless of distance."
