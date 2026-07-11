# WO1 findings — exemplar payload inspection

Source: `notebooks/edop/surface/wo1_exemplar_inspection.ipynb`
Payloads: `output/edop/surface/exemplars/` (gitignored)

Findings recorded as cells are run and results discussed.

---

## F1.1 — Payload load and row counts

All 10 payloads load in ~256ms. Row counts:

- S1 single-basin, S2 buffer, S5 4-corners: **52 rows** each (lean and detail identical count)
- S3 polity (N Song, Band T 1000–1100): **372 rows** = 52 base (A–E) + 320 Band T
- S4 basin-ring: **no top-level `rows`** — structural outlier; payload is `{center: {rows:[52]}, ring: [{signature:{rows:[52]}}, ...]}`

All non-ring scopes return exactly 52 base rows regardless of n_units (1 basin vs 376).
Scope affects scores, coherence verdicts, quality flags — not row count or structure.

---

## F1.2 — Payload envelope structure (Cell 2)

**Three envelope variants across five scopes:**

| Scope | Top-level keys | Notes |
|---|---|---|
| S1 single-basin | `bands, caveats, neighborhood, rows, shortfall, temporal` | baseline shape |
| S2 buffer | same | identical structure |
| S3 polity | + `modality_post_pass` | polygon path adds this diagnostic key |
| S4 basin-ring | `center, lat, level, lon, ring, type` | structurally distinct — no `rows`, no `shortfall`, no `caveats` |
| S5 4-corners | + `modality_post_pass` | polygon path, same as S3 |

`modality_post_pass` is a diagnostic key on polygon paths (value: "skipped — not calibrated for polygon scale"). UI can ignore it or surface as metadata; it is not display data.

**Neighborhood block varies by resolver type:**
- Single-basin: carries `hybas_id` (the resolved basin)
- Buffer: carries `radius_km`
- Polygon: carries `marginal_exposure: {lt_50pct, lt_20pct}`; **no `lat`/`lon`** (polygon path receives only WKT, not the query point)
- Basin-ring center: same as single-basin

**Three small issues for the UI layer:**

1. **`caveats` is `{}` on standard paths but `None` on basin-ring.** Surface should treat both as "no caveats" — do not rely on truthiness of the caveats value alone.

2. **S5 shortfall is -5.9e-05** — floating-point rounding artifact. UI should clamp shortfall ≤ 0 to zero; never display a negative shortfall.

3. **Polygon/polity neighborhood carries no `lat`/`lon` and no polity name/period.** If the UI header needs "Northern Song (990–1017)" or a query-point marker, that must come from the user's input or be added at the route layer — it is not in the payload. (See M1/M2 in gap list.)

---

## F1.3 — Methods inventory (Cell 3)

**Base rows (Bands A–E) are structurally identical across all six signatures** — center, ring
member, and all four non-ring scopes return the same 6 method types with the same row counts:

| Method | Count | Block |
|---|---|---|
| `area_weighted` | 34 | B1 |
| `class_mixture` | 10 | B3/B4 |
| `dominant_basin` | 3 | B2 |
| `distribution_only` | 3 | B5 |
| `flag_fraction` | 1 | B4 |
| `extreme` | 1 | B5 |
| **Total** | **52** | |

The Signature tab renderer can be built against a fixed schema — no runtime adaptation needed.
6 leaf-renderer types cover the full space of Bands A–E.

**Band T (S3 polity, 1000–1100 CE): 320 rows across 3 substrates:**

| Substrate | Method | Rows | Structure |
|---|---|---|---|
| LMR | `grid_areal_distribution` | 303 | 3 vars × 101 years (annual, 1000–1100 inclusive) |
| HYDE | `grid_areal_distribution` | 8 | 4 vars × 2 epochs (1000 CE, 1100 CE only) |
| eVolv2k | `global_forcing` | 9 | 9 events in the span |

LMR is annual — a 100-year span always yields 101 rows per variable. Time-series collation:
filter by `variable`, sort by `year`. HYDE epoch count is variable and span-dependent (2 epochs
here; could be 1 or more for other spans). eVolv2k event count varies with volcanic activity
(early 11th century was notably active — 9 events in 100 years).

---

## F1.4 — Histogram presence by method (Cell 4)

**Histogram presence is fully determined by method type — identical across all scopes.**

Base rows (Bands A–E, all scopes):

| Has histogram | Methods | Count |
|---|---|---|
| Yes | `area_weighted` | 34 |
| No | `dominant_basin`, `class_mixture`, `distribution_only`, `extreme` | 18 (3+10+3+1) |

Band T rows (S3 polity, 320 rows):

| Has histogram | Method | Count |
|---|---|---|
| Yes | `grid_areal_distribution` (LMR + HYDE) | 311 |
| No | `global_forcing` (eVolv2k) | 9 |

**Implication for the UI:** the histogram widget is keyed to method type, not to a null check
on `detail['distribution']`. Two trigger methods: `area_weighted` (base rows) and
`grid_areal_distribution` (Band T). eVolv2k rows (`global_forcing`) never carry a histogram —
they are global scalars (volcanic forcing), not spatial distributions, so a histogram
would be meaningless.

Total histogram-bearing rows in a full S3 detail payload: 34 base + 311 Band T = **345**.

---

## F1.5 — Histogram anatomy (Cell 5)

**Both histogram types share an identical 13-key schema** — one widget rendering path covers all cases.

```
keys: band_t_from, band_t_to, bins, low_resolution, max, mean, min,
      n_units, p10, p90, resolver_year, unit_type, weights
```

**`bins` / `weights` convention:** `bins` = N+1 edge values; `weights` = N bar heights.
Standard histogram format — bins[i] to bins[i+1] is the i-th bar.

**`unit_type`** identifies what each bar aggregates: `basin` (base rows), `lmr_cell` (LMR Band T).
HYDE Band T presumably uses `hyde_cell` — to confirm in Cell 7.

**`score` vs `mean`:** For `area_weighted` (base rows), score equals mean and is non-null.
For `grid_areal_distribution` (Band T), score is `None` by design — it is a distribution-only
method with no single representative value. The UI must null-check score before rendering
a score chip; it can always render mean.

**Temporal stamps — two axes, fully independent:**

| Context | resolver_year | band_t_from | band_t_to |
|---|---|---|---|
| Buffer base row (S2, aridity) | None | None | None |
| LMR row (S3, lmr_pdsi yr=1000) | 1000 | 1000 | 1100 |

For the LMR row: `resolver_year=1000` is the year the polity boundary was snapped
(independent axis); `band_t_from/to` is the aggregation window. The row's `year` field
(1000 CE) is the LMR annual time step — a third axis. All three are distinct and must not
be conflated in the UI.

**`n_units` and `low_resolution`:**
- S2 buffer (9 basins): `n_units=9`, `low_resolution=False`
- S3 LMR (N. Song): `n_units=93` LMR cells — useful for provenance disclosure
- `low_resolution=False` here; this flag signals when basin count is very small and the
  histogram shape may be unreliable (defined in engine; UI should surface this)

---

## F1.6 — LMR time-series collation (Cell 6)

303 rows = 3 variables × 101 years (1000–1100 inclusive). Variables: `lmr_air`, `lmr_pdsi`, `lmr_prate`.

**`score` is null for every LMR row** — the time-series value is `detail['distribution']['mean']`,
not the row score. Collation recipe: filter by `variable`, sort by `year`, extract
`distribution.mean` (line) + `distribution.p10`/`p90` (spread band).

**Detail mode is required for Band T time-series visualization.** Lean payload has no
`detail` sub-dict; there is no mean, p10, or p90 to plot. A request for a Band T chart
must be a detail-mode call.

**What p10/p90 represent for LMR rows:** the spatial spread of the annual climate signal
across the polity area. Year 1002 example: mean PDSI = 0.2033, p10 = −0.2575 — some LMR
cells within N. Song were in drought while the polity-weighted mean was slightly positive.
The shaded band is meaningful and should be shown, not suppressed.

---

## F1.7 — HYDE epochs and eVolv2k events (Cell 7)

**HYDE (8 rows = 4 vars × 2 epochs):**

All scores None (`grid_areal_distribution`). Epoch years are the two HYDE timesteps that
fall within the 1000–1100 CE query span. Values are in km² (area units, unlike LMR's
dimensionless indices). Example: N. Song cropland 1000 CE → 3.32 km², 1100 CE → 8.01 km²
(~2.4× increase — visibly meaningful even from these two snapshots).

Unit label required in the UI: LMR rows are dimensionless; HYDE rows are km².
Values come from `detail['distribution']['mean']` (detail mode required, same as LMR).

**eVolv2k (9 events in 1000–1100 CE):**

`global_forcing` method — no histogram (confirmed F1.4). Score is None; display value
is `vssi` (Tg SO₂) from the row data directly (not from a distribution sub-dict — there
is none). The 1028 CE event (7.78 Tg SO₂) dominates; 1003 CE (4.98 Tg SO₂) is
secondary. Event count and magnitude vary with volcanic activity — this span is notably
active (9 events in 100 years is high).

Other per-event fields available from engine schema: `so4_grl`, `so4_ant`, `lat`,
`location` — useful for event annotation (e.g. eruption name/location label).

**Band T rendering trifurcation** — three distinct visualizations, not one:

| Substrate | Rows | Shape | Renderer |
|---|---|---|---|
| LMR | 303 (annual) | continuous time series | line + p10/p90 shaded band |
| HYDE | 8 (epoch snapshots) | sparse discrete steps | bar or step chart per variable |
| eVolv2k | 9 (events) | point events | spike / event timeline |

The existing sandbox Band T panel renders all three on a shared time axis — the new page
should preserve this model, but now with spatial spread from the histogram (p10/p90) for LMR.

---

## F1.8 — Where the two temporal axes live (Cell 8)

**Band T span (`from_year`/`to_year`):** top-level `payload["temporal"]` — always accessible,
lean or detail.

**`resolver_year`:** NOT at top level. Not in `neighborhood`. Only in histogram stamps
(`detail['distribution']['resolver_year']`). Accessible only in detail mode.

This matters: to display "Boundary year: 1000 CE" in the UI header, the surface must either
(a) pull it from a histogram stamp (detail mode required, no clean top-level home), or
(b) pass the query parameter down from the route layer — the cleaner fix.

**Confirmed M1 from F1.2:** The `/api/area` route should add `resolver_year` to the
`neighborhood` block (or a new `query` or `metadata` top-level key). This is a
route-layer change; the engine already stamps `resolver_year` correctly on every histogram.

**`resolver_year` on base rows:** Even for non-Band-T rows (e.g., aridity), the histogram
stamp carries `resolver_year=1000` with `band_t_from=None, band_t_to=None`. The polity
boundary year is always stamped — it is only the Band T span that may be absent. The two
axes are therefore fully independent, as designed.

**Lean vs. detail access matrix:**

| Axis | Lean | Detail |
|---|---|---|
| Band T span (`from_year`/`to_year`) | `payload["temporal"]` ✓ | same |
| Resolver year | not accessible | `any_histogram_row.detail.distribution.resolver_year` |
| Polity name / period | not in payload | not in payload (M2 — must come from route or caller) |

---

## F1.9 — Lean vs detail delta; detail sub-dict anatomy (Cell 9)

**Lean/detail difference is exactly one key.** Every row carries the same top-level key set
regardless of mode; `detail` is always present and is either `None` (lean) or a sub-dict.

**Naming trap:** there is a top-level `row["distribution"]` key that is ALWAYS null, even in
detail mode. The histogram lives at `row["detail"]["distribution"]`, not `row["distribution"]`.
Any UI code that reads `row.distribution` will get null and miss the histogram entirely.

**Detail sub-dict contents by method:**

| Method | detail keys | Histogram |
|---|---|---|
| `area_weighted` | `distribution, p10, p90, spread, unit` | ✓ |
| `dominant_basin` | `dominant_hybas_id` | — |
| `class_mixture` | `concentration, mixture, modal_class_id, modal_share, n_classes` | — |
| `flag_fraction` | *(empty)* | — |
| `distribution_only` | `p10, p90, regimes, spread, suppressed_score, unit` | — |
| `extreme` | `dominant_hybas_id` | — |
| `grid_areal_distribution` | `distribution, p10, p90, sd, unit, w_eff` | ✓ |
| `global_forcing` | *(empty)* | — |

**Method-specific notes for the UI:**

- `class_mixture`: `mixture` likely contains the full class breakdown; `modal_class_id`/`modal_share`
  are the dominant class and its share; `n_classes` and `concentration` describe diversity.
  Sufficient data for a categorical breakdown (small bar or pie chart per variable).

- `distribution_only`: `regimes` = multi-modal regime detection output; `suppressed_score`
  = the score value that was suppressed due to multi-modality. These variables have scores
  withheld in lean mode because the distribution is meaningfully non-unimodal.

- `flag_fraction` and `global_forcing`: empty detail sub-dicts — detail mode has no effect on
  these rows. Including `&detail=true` is harmless but adds no data for them.

- `grid_areal_distribution` (Band T) adds `sd` and `w_eff` beyond `area_weighted`'s set.
  `sd` = standard deviation across cells; `w_eff` = effective sample weight (precision metric).
  Both are available as supplementary uncertainty disclosures if the UI wants them.

---

## F1.10 — Per-method rendering anatomy (Cell 10)

Six distinct rendering situations for base rows. All examples from S2 buffer (Timbuktu 100km).

**`area_weighted` (aridity):**
score=10.19 (percentile), raw=None, coherence=concentrated, modality=unimodal.
`detail.unit='percentile'`; `detail.spread=p90−p10=7.13`. Histogram present.
The score IS the mean; raw is absent (no physical-unit value stored for percentile variables).

**`dominant_basin` (discharge_yr):**
score=86.01 (percentile), raw=567.595 (physical units), `detail.dominant_hybas_id=1060564960`.
Both score and raw present. UI can render: "86th pct | 567.6 [units] in basin 1060564960".
No spread — single-basin snapshot.

**`class_mixture` (biome):**
score=None, raw='Tropical & Subtropical Grasslands…' (modal class label string).
`detail.modal_class_id=7, modal_share=0.708, n_classes=2, concentration=0.586`.
`detail.mixture=[{class_id, class_label, weight}, …]` — full breakdown array.
`concentration` ≠ `modal_share`: concentration is a diversity index (Herfindahl-type);
modal_share is simply the dominant class fraction. Both available for display.
The `mixture` array supports a small categorical breakdown chart.

**`flag_fraction` (coast_fraction):**
score=None, raw=0.0 (the fraction, 0–1). Empty detail dict. Render as a plain fraction
or binary indicator. No histogram, no spread — a single areal fraction value.

**`distribution_only` (reservoir_vol):**
score=None (suppressed), raw=None, coherence=spread, modality=two_regime.
`detail.suppressed_score=26.18` (the weighted-mean value, withheld because the
distribution is bimodal and the mean would misrepresent it).
`detail.regimes=[{center:0.0, weight:0.708}, {center:89.59, weight:0.292}]`:
70.8% of basins have near-zero reservoir volume; 29.2% have very high volume.
The suppressed score (26.18) is the misleading mean. UI should render the regime
breakdown rather than a single score for `two_regime` rows. `suppressed_score`
can be shown with a caveat, not as the headline.

**`extreme` (river_area):**
score=86.07 (percentile of the extreme basin), raw=4273.4 (physical value),
`detail.dominant_hybas_id=1060582960`. Same structure as `dominant_basin`.

**Cross-cutting: `raw` field semantics vary by method:**

| Method | `raw` contains |
|---|---|
| `area_weighted` | None (percentile — no physical counterpart) |
| `dominant_basin` | actual sensor value (physical units) |
| `class_mixture` | modal class label (string) |
| `flag_fraction` | the fraction value (0–1) |
| `distribution_only` | None |
| `extreme` | actual measurement value (physical units) |

The UI must branch on method type to interpret `raw` correctly — it is not consistently
a physical-unit numeric. The `class_mixture` case (raw = string label) is the sharpest
example: treat it as display text, not a number.

---

## F1.11 — Basin-ring payload structure (Cell 11)

Top-level: `{center, lat, level, lon, ring, type}` — no `rows`, no `shortfall`, no `caveats`.
`center` is a full `single_basin_signature` payload; each of the 5 `ring` members carries a
`signature` key that is also a full `single_basin_signature` payload (52 rows, standard envelope).
Result: **6 complete signatures** (1 center + 5 ring members) in one response.

Ring member metadata (sorted by border_bearing — i.e. clockwise from north):

| hybas_id | sub_area_km² | shared_km | border_bearing | centroid_bearing |
|---|---|---|---|---|
| 1060041510 | 24,966 | 230.3 | 5.0° N | 46.3° NE |
| 1060550540 | 921 | 19.3 | 72.0° ENE | 71.6° ENE |
| 1060551770 | 10,323 | 153.6 | 91.9° E | 133.2° SE |
| 1060564960 | 5,734 | 80.7 | 231.2° SW | 214.4° SW |
| 1060564740 | 11,276 | 61.0 | 277.4° W | 259.3° W |

**Size variation is extreme**: 921 km² (tiny ENE neighbor) vs 24,966 km² (vast N neighbor,
likely the Saharan interior drainage basin). Size-weighted rendering is important — a tiny
neighbor that happens to share a small border tells a different story than a massive neighbor.

**border_bearing vs centroid_bearing**: generally close, but member 1060551770 diverges
(border=92° E, centroid=133° SE). Means the shared edge is due east but the basin's
body extends southeast. Both bearings carry distinct information for orientation UI.

**Rendering implications**: basin-ring has no aggregated `rows` — it cannot use the same
signature table renderer as other scopes. Three display paths:
1. **Comparison table**: 6 columns (center + 5 neighbors), one row per variable — cross-basin
   comparison of any variable; `border_bearing` provides natural column order.
2. **Schematic map**: center basin with neighbors shown as oriented segments (position +
   shared_km proportional to edge thickness); `sub_area_km²` scales neighbor glyphs.
3. **Per-member deep-dive**: select a ring member, render its full 52-row signature using the
   same renderer as single-basin — the data is already there.

Detail mode applies to each nested signature's rows independently — same `detail` key
structure within each `member.signature.rows[n]`.

---

## F1.12 — 4 Corners / Santa Fe polygon spot check (Cell 12)

28 L06 basins within `POLYGON((-110 35, -105.5 35, -105.5 38, -110 38, -110 35))`.
shortfall = -5.9e-05 (floating-point artifact; confirmed clamp-to-zero needed).

**Marginal exposure — a polygon-fit quality metric:**

`neighborhood.marginal_exposure = {lt_50pct, lt_20pct}` reports the fraction of included
basins whose intersection with the polygon is less than 50% / 20% of their area. Higher
values mean the polygon edge cuts through more basins, diluting result reliability.

| Polygon | n_units | lt_50pct | lt_20pct | Interpretation |
|---|---|---|---|---|
| N. Song polity (S3) | 376 | 0.030 | 0.008 | Historical boundary aligns well with basins |
| 4 Corners rectangle (S5) | 28 | 0.147 | 0.039 | Straight edges slice through ~15% of basins |

The contrast is instructive: a historically mapped polity boundary tracks basin edges better
than an arbitrary bounding box. `marginal_exposure` should be surfaced in the UI as a data
quality indicator — a high lt_50pct is a signal to the analyst that edge basins have
partial weight.

**Aridity — 4 Corners score=30.21, coherence=spread:**
30th percentile (relatively dry globally — consistent with the Colorado Plateau / high desert).
coherence=spread means the 28 basins span a wide aridity range — expected given the mix of
canyon-cut river valleys, high plateau, and semi-arid grassland in this region. The spatial
spread is substantive, not noise, and should be shown (histogram).

---

## F1.13 — Missing fields / gap survey (Cell 13)

Five confirmed gaps or design notes arising from the payload inspection.

**M1 — `resolver_year` not surfaced at top level** *(route-layer fix needed)*
Not in payload top-level keys; not in `neighborhood`. Only accessible as a histogram stamp
in detail mode. To display "Boundary year: 1000 CE" in a header without requiring detail
mode, the `/api/area` route must inject `resolver_year` into `neighborhood` (or a new
`query` / `metadata` block) from the request parameter.

**M2 — Polity name and period absent from payload** *(route-layer addition needed)*
`neighborhood` keys: `level, marginal_exposure, n_units, type, unit_type` — no polity name,
no resolved `fromyear`/`toyear`. A UI header showing "Northern Song (960–1127)" must come
from the caller's query parameters or a supplementary route. The `/api/area` route should
echo back `polity`, `resolver_year`, and optionally the resolved period.

**M3 — No LMR scalar in lean mode** *(by design; note for UI)*
LMR rows in lean: `score=None, detail=None`. There is no per-year value accessible without
`&detail=true`. Band T time-series charts require detail mode unconditionally.

**M4 — `distribution_only` uses range-bar, not histogram** *(design note)*
`distribution_only` rows have `p10`, `p90`, `regimes`, `suppressed_score` in detail but no
histogram. The right widget is a range-bar (p10–p90 span) with regime breakdown, not a
histogram. `suppressed_score` should be labelled as suppressed (bimodal distribution) if
shown at all.

**M5 — `marginal_exposure` conditionally present** *(UI must handle absence)*

| Scope | marginal_exposure present? |
|---|---|
| S1 single-basin | No — single basin, no edge |
| S2 buffer | No — radial, no polygon edge |
| S3 polity (polygon) | Yes |
| S5 arbitrary polygon | Yes |

Presence is confined to polygon-path scopes (`resolve_polygon`, `resolve_polity`). Buffer
and single-basin scopes never produce it. UI should render the quality badge conditionally;
absence is not an error.

---

*Inspection complete — all 13 cells run. See TODO compilation for action items derived from
F1.1–F1.13.*
