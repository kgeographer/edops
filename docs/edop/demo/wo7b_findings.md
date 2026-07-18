# WO7b findings — Distance threshold rendering

Notebook: `notebooks/edop/demo/wo7b_threshold.ipynb`

---

## A — Performance probe

### Approach

Rather than a separate notebook, the probe was done directly by raising the top-N cap and
switching the basin-geom fetch to a POST endpoint. Two engineering changes were required
before the threshold could be meaningful:

- **GET → POST for `/api/basin-geom`**: GET with comma-separated IDs has implicit URL-length
  limits at ~1,000+ basins (~13 KB URL). Replaced with POST accepting a JSON body; cap raised
  to 6,000 IDs.
- **GeoJSON coordinate precision**: `ST_AsGeoJSON(geom, 3)` (3 dp ≈ 111 m precision) in place
  of the default 5 dp — reduces payload verbosity ~5–10× with no visible impact at world zoom.

### Results

Worst-case set rendered: **5,272 basins** (Tbilisi / Temperature lens / loose threshold).
Render time: **~2 seconds** in browser on first load; pan/zoom smooth. MapLibre WebGL handles
this comfortably — no canvas renderer switch needed, no geometry simplification needed.

**Decision:** keep current GeoJSON delivery; proceed directly to threshold calibration.
Spinner noted as a future improvement; not blocking.

---

## B — Threshold calibration

16,397 L06 basins total. Active data:
- `climate.phase`, `climate.precip`: 16,338 valid (59 hyper-arid basins masked — all-zero
  monthly precip makes circular concentration undefined; NaN throughout, never coerced to 0
  or ∞).
- `climate.temp`: 16,397 valid (all basins have temperature data).

### B1 — CDF shapes

**`climate.phase` (Euclidean, 2 vars):** smooth concave-up power-law curve — no geometric
elbow. The rare anchor (SF Mediterranean) and common anchor (Timbuktu monsoon) trace
parallel curves; SF is consistently below Timbuktu at every radius, confirming the rarity
signal. No natural breakpoint; thresholds are declared analytical choices.

**`climate.precip` (Euclidean, 2 vars):** similar smooth power-law shape. Notable: Rome and
Timbuktu are nearly identical counts at small radii (both moderately common precipitation
regimes) but diverge sharply above r ≈ 0.3 — Rome's "Mediterranean-amount" rainfall becomes
increasingly rare relative to Timbuktu's Sahelian amounts at larger radii.

**`climate.temp` (Mahalanobis, 3 vars):** S-shaped CDF with geometric breakpoints — a foot,
a steep central rise, and a shoulder — consistent with a chi distribution (k=3). Numeric
scale larger than Euclidean lenses (different dimensionality + covariance). The maritime
(London) and continental (Tbilisi) anchors are close in count at strict but diverge at
moderate and loose, reflecting the greater global prevalence of continental thermal regimes.

### B2 — Counts at candidate radii

**climate.phase** (normalized Euclidean):

| radius | SF (rare) | Timbuktu (common) |
|--------|-----------|-------------------|
| 0.10   | 34        | 74                |
| 0.20   | 119       | 251               |
| 0.30   | 216       | 436               |
| 0.50   | 541       | 784               |
| 0.75   | 1059      | 1548              |
| 1.00   | 1600      | 2409              |
| 1.50   | 2684      | 4206              |
| 2.00   | 3867      | 6087              |

**climate.precip** (normalized Euclidean):

| radius | Rome      | Timbuktu  |
|--------|-----------|-----------|
| 0.10   | 72        | 71        |
| 0.20   | 246       | 239       |
| 0.30   | 541       | 450       |
| 0.50   | 1521      | 750       |
| 0.75   | 3052      | 1378      |
| 1.00   | 4877      | 2285      |
| 1.50   | 7961      | 4100      |
| 2.00   | 10366     | 6202      |

**climate.temp** (Mahalanobis):

| radius | London (maritime) | Tbilisi (continental) |
|--------|-------------------|-----------------------|
| 0.25   | 52                | 61                    |
| 0.50   | 234               | 339                   |
| 0.75   | 550               | 852                   |
| 1.00   | 1094              | 1672                  |
| 1.50   | 3242              | 5272                  |
| 2.00   | 6708              | 10939                 |
| 3.00   | 13759             | 15610                 |
| 4.00   | 15974             | 16230                 |

### B3 — Settled radii

Calibration target: strict returns the tight known cluster for the rare-type anchor (~tens of
basins); loose lets the common-type anchor bloom to its full continental extent.

| lens_id        | strict | moderate | loose | strict SF/Rome | moderate SF/Rome | loose Timbuktu |
|----------------|--------|----------|-------|---------------|-----------------|----------------|
| climate.phase  | 0.10   | 0.30     | 0.75  | 34            | 216             | 1548           |
| climate.precip | 0.10   | 0.20     | 0.50  | 72            | 246             | 750            |
| climate.temp   | 0.25   | 0.75     | 1.50  | 52            | 550             | 5272           |

Cross-lens note: radii are not comparable across lenses — 2-var Euclidean and 3-var
Mahalanobis enclose very different fractions of the basin distribution at the same numeric
radius. No attempt at cross-lens comparability is made or intended.

---

## C — Backend: threshold query mode

### `LENS_REGISTRY` additions

`thresholds: {strict, moderate, loose}` added to each active lens entry. Also exposed in
`/api/similarity/lenses` registry response so the UI can read calibrated values without
hardcoding.

### `find_similar()` signature extension

```python
find_similar(
    query_hybas_id: int,
    lens_id: str = "climate.phase",
    n: int = 200,
    mode: str = "threshold",     # NEW — "threshold" | "topn"
    stringency: str = "moderate" # NEW — "strict" | "moderate" | "loose"
)
```

**Threshold path:** resolves `radius = LENS_REGISTRY[lens_id]["thresholds"][stringency]`;
returns all basins where `dist ≤ radius`, sorted by distance. Count varies by query.
`query_meta` gains `mode`, `stringency`, `radius`, `result_count`.

**Top-N path:** unchanged — `np.argsort(dist)[:n]`. Retained as fallback / comparison path.

**NaN masking:** unchanged — propagated from index build time. Masked basins have
`dist = np.inf` and are excluded from both paths without special-casing.

### `/api/similarity` endpoint

```
GET /api/similarity?lat&lon&lens&mode=threshold&stringency=moderate
```

New parameters: `mode` (default `"threshold"`), `stringency` (default `"moderate"`),
`n` (default 200, max 2000, only used in topn mode). Input validation: 400 on unknown mode
or stringency value.

Response gains `mode` always; `stringency`, `radius`, `result_count` when `mode=threshold`.

`/api/seasonality/similar` (deprecated backward-compat wrapper) permanently pinned to
`mode="topn"` — its shape contract is frozen; do not change.

### Tests added

- `test_similarity_threshold_response_shape` — SF query confirms `mode`, `stringency`,
  `radius`, `result_count` present; all returned distances ≤ declared radius; ascending order.
- `test_similarity_threshold_variable_count` — SF < Timbuktu at `climate.phase` moderate:
  the core prevalence contract. If this fails, the threshold is not differentiating by
  climate-type rarity.
- `test_similarity_lenses_registry` extended — all active lenses must expose
  `thresholds: {strict, moderate, loose}` with values strictly ordered.

585 tests pass, 38 skipped.

---

## D — UI: stringency control

**Strict / Moderate / Loose** segmented control (Bootstrap radio button group) added to the
Similarity tab controls row, to the right of the lens dropdowns. Default: Moderate.

Changing stringency: nulls `_simQueryStringency` → triggers re-query → repaints. Cache key
is now `(lat, lon, lens_id, stringency)`; anchor and lens persist across stringency changes
(same contract as sub-lens switching).

Blurb updated: "Showing all N basins within the moderate threshold." Count is `result_count`
from the server — the total returned by the threshold query, not the rendered polygon count.
Per-lens type descriptions retained; the count sentence replaces the former fixed-N tail.

`_simQueryStringency` added to `_resetRightColumn()` so a new point query forces a fresh
fetch even if stringency is unchanged.

---

## Acceptance

- Perf probe confirmed: 5,272 basins (worst-case, Tbilisi / temp / loose) renders in ~2
  seconds; pan/zoom smooth. No rendering architecture change required. ✓
- Threshold notebook reports strict/moderate/loose radii per lens with counts for validation
  anchors; rare-type-strict is tight (SF/phase/strict = 34 basins);
  common-type-loose is broad (Timbuktu/temp/loose = 5,272 basins). ✓
- Endpoint returns variable-count thresholded neighborhoods; `result_count` and `radius`
  surfaced in response; NaN masking confirmed per lens. ✓
- UI stringency control re-queries and repaints; count reported in blurb; anchor + lens
  persist across stringency changes. ✓
- **Hero-shot check (pending Karl browser review):** SF moderate on Seasonal Phase should
  show tight Mediterranean cluster; Timbuktu moderate should show broad monsoon dispersion.
  The count contrast is the demonstrator.
- All existing tests pass; two new contract tests added. ✓
