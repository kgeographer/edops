# WO19 Findings — LMR per-span values route (feasibility)

**Branch:** `surf_wo19`
**Date:** 2026-07-07
**Notebook:** `notebooks/edop/surface/wo19_lmr_honest_paint.ipynb`

---

## Status

Feasibility complete. All six findings confirmed. Implementation next.

---

## F19.1 — Anomaly baseline confirmed (Tardif et al. 2019)

The stored values ARE anomalies vs the **CCSM4 model climatology 850–1850 CE**.
Reference: the CCSM4 simulation's own long-term mean over 850–1850 — not an
instrumental or observational baseline. The LMR reanalysis uses CCSM4 as the
prior; anomalies are departures from that prior's 850–1850 mean.

The empirical check (Cell 2: 1900–2000 CE spatial mean ≈ -0.0008) is consistent
with this. The global spatial average of the reanalysis does not strongly depart
from the model prior even in the 20th century because (a) the prior is a strong
constraint and (b) spatial averaging smooths proxy signal. It does NOT indicate
the reference is 20th-century; the reference period is 850–1850 by construction.

**WO15 caveat text ('anomaly relative to 850–1850 CE mean') is confirmed correct
and carries forward unchanged.**

## F19.2 — Weighting: arithmetic mean

`temporal.lmr_climate` stores the LMR v2.1 grand ensemble mean at each year
(MC runs collapsed at ingest). Span mean = arithmetic AVG over the annual
ensemble-mean values in the slice. No additional weighting applies.

Cell 3 confirms: `numpy.mean(air[1000:1010])` = -0.15672, matching the
PostgreSQL arithmetic mean of 11 values (PostgreSQL slice `[y1:y2]` is
inclusive on both ends).

Array indexing note: year Y CE → PostgreSQL index Y (e.g., year 1000 CE =
`air[1000]`). Both endpoints of the SQL slice are included in the mean.

## F19.3 — Join key: lat,lon string; property paint

16,380 rows in `temporal.lmr_climate`; 16,380 distinct `(lat, lon)` pairs;
`lmr_notches.geojson` has 16,380 features with 16,380 unique lat/lon pairs —
perfect 1:1. Zero duplicate `CONCAT(lat, ',', lon)` keys confirmed (Cell 7).

Route returns `{lat_lon: mean_anomaly}` (e.g. `{"20.0,-10.0": -0.23}`).
Frontend matches on GeoJSON feature `properties.lat` + `properties.lon`.
Paint approach: **property paint** — rebuild the static GeoJSON source
in-memory with the span value baked in as a property, then re-add to the map.
Consistent with WO15 notch approach; avoids requiring a feature-state `id` on
the GeoJSON.

## F19.4 — Performance: 0.546s — GO

Full Python/pandas round-trip (Cell 5, Northern Song span 1000–1100 CE):

| Rows | Query time | mean_air range |
|------|-----------|----------------|
| 16,380 | **0.546s** | -1.34 to +0.42 K |

Slower than HYDE's 0.033s pre-aggregated lookup, but the comparison is unfair:
HYDE has 128 enumerable step indices; LMR spans are continuous [from, to] and
cannot be pre-aggregated. The unnest subquery is the irreducible cost.

0.546s is perceptible but acceptable for a choropleth repaint triggered by
scope or slice change (spinner covers it). No further optimization attempted.

## F19.5 — Floor rule: mean over in-range portion

Quality floor: 700 CE (F15.1). Three cases confirmed (Cell 6):

| Case | Example | Result |
|------|---------|--------|
| Entirely below floor | 500–600 CE | `None` → absent key → transparent |
| Entirely above floor | 1000–1100 CE | Normal mean |
| Straddles floor | 500–900 CE → effective 700–900 CE | Mean over [700, to_year] |

No below-floor value is ever coerced to zero. Route returns `actual_from` =
`max(from_year, 700)` so the frontend can disclose the effective range if needed.
Absent key = transparent paint — zero is a meaningful anomaly value, not absence.

## F19.6 — Span coupling: coupled to Band T

LMR paint tracks Band T `from_year`/`to_year`. `applySlice` currently passes a
single year (`s.fromyear`) to the LMR branch; this must change to pass the span
so the route returns a span mean, not a one-year read. Slice-reactive repaint
updated as part of implementation.
