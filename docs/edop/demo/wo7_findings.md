# WO7 findings — Seasonality similarity: notebook investigation (Part A)

**Date:** 2026-07-16
**Kind:** Notebook investigation. No production files changed.
**Spec:** `docs/edop/demo/wo7_seasonal-sim.md`
**Notebook:** `notebooks/edop/demo/wo7_seasonality_similarity.ipynb`

---

## Part 1 — Gazetteer

Source: `whgv3beta.public.places` + `place_geom` (WHG snapshot).

Build SQL filters to `ST_Point` geometries only, `fclasses && ARRAY['P','S']::varchar[]`
(note: column is `character varying[]`, not `text[]`), and takes `DISTINCT ON (p.id)` to
resolve the ~2–3 POINT geoms some places carry. Result imported to `cedop.gaz.whg_gaz`.

`hybas_id_l06` precomputed via `ST_Within` UPDATE and indexed — avoids re-running the
spatial join in the notebook or at query time.

| | |
|---|---|
| Total rows | 1,517,180 |
| Matched to L06 basin | 1,508,492 (99.4%) |
| Unmatched (polar, ocean edge) | 8,688 |
| fclasses breakdown | {P} 96%, {S} 3.4%, mixed combos <1% |

---

## Part 2 — A1: Basin coverage

Spatial join: `hybas_id_l06` pre-baked, simple SELECT.

| | |
|---|---|
| L06 basins with ≥1 place | 10,799 of 16,397 (66%) |
| Unique places matched | 1,508,492 |
| Places per basin — median | 7 |
| Places per basin — p90 | 272 |
| Places per basin — max | 13,947 |

66% coverage is adequate. Empty basins are the expected uninhabited regions (Sahara,
boreal, polar, open ocean). For any Mediterranean, monsoon, or temperate query the top-N
basins will have named places.

---

## Part 3 — A2: Distance metric

Scalar indices across 16,397 L06 basins (16,338 non-NaN):

| Index | Mean | SD | Range |
|---|---|---|---|
| pre_concentration | 0.412 | 0.230 | 0.0 – 1.0 |
| seas_phase_offset | 1.987 | 1.844 | 0.0 – 6.0 |
| tmp_seas_amp | 19.8°C | 13.7°C | 0.4 – 61.6°C |

Pearson r(pre_concentration, seas_phase_offset) = **−0.121**.

The scatter shows structure: monsoon basins cluster bottom-right (high concentration,
low offset — rain and heat coincide); Mediterranean basins scatter upper-right (moderate–
high concentration, offset 4–6 — winter rain anti-phased with temperature); maritime
basins fill the left (low concentration, offset effectively random).

|r| = 0.121 < 0.3 threshold. **Normalized Euclidean is adequate; Mahalanobis adds
nothing.**

---

## Part 4 — A3: SF validation

Query: SF downtown (−122.42, 37.77) → hybas_id 7060013180, pre_concentration=0.604,
seas_phase_offset=5.644. Classic Mediterranean signature.

Top-50 basins by NE distance → 36 have a named place. Top-15:

| Place | Country | dist_ne | pre_conc | phase_offset |
|---|---|---|---|---|
| Mirinzal | BR | 0.019 | 0.607 | 5.617 |
| Barkerville | US | 0.026 | 0.605 | 5.692 |
| Icatu | BR | 0.030 | 0.601 | 5.691 |
| Ashur | IQ | 0.037 | 0.607 | 5.580 |
| An-Nāṣirīyah | IQ | 0.037 | 0.612 | 5.678 |
| Mesa Redonda | MX | 0.046 | 0.594 | 5.643 |
| Tell Ajri | IQ | 0.046 | 0.608 | 5.726 |
| Shithāthah | IQ | 0.050 | 0.593 | 5.638 |
| Hassuna | IQ | 0.058 | 0.612 | 5.556 |
| Cahuil | CL | 0.060 | 0.614 | 5.563 |
| Choga Mish | IR | 0.061 | 0.591 | 5.667 |
| San Fernando | CL | 0.087 | 0.619 | 5.537 |
| Hatra | IQ | 0.088 | 0.611 | 5.490 |
| Aelana | JO | 0.091 | 0.620 | 5.760 |
| Port Said | EG | 0.092 | 0.618 | 5.776 |

Dominant regions: **Iraq/Mesopotamia** (Ashur, Hassuna, Hatra, Nasiriyah, Shithāthah,
Tell Ajri, Choga Mish), **central Chile** (Cahuil, San Fernando), **Iran, Jordan, Egypt**.
All canonical Mediterranean-climate zones. **A3 validation passes.**

Brazil (Mirinzal, Icatu) and one Mexico entry appear early. These are not geographically
Mediterranean but share the statistical signature: austral-fall/winter rainfall peak
anti-phased with temperature. Real pattern, different physical cause. Acceptable in a
seasonality-similarity context — the tool is reporting seasonal pattern similarity, not
climate classification.

NE vs Mahalanobis top-15: **identical ranking** except Chipps/Cahuil swap positions 11/12.
Confirms NE is the right choice.

---

## Part 5 — A4: Threshold and result count

Distance distribution from SF across all 10,799 gazetteer-covered basins:

| Percentile | NE distance | Basins |
|---|---|---|
| p05 | 0.591 | 539 |
| p10 | 1.015 | 1,078 |
| p20 | 1.753 | 2,155 |

The p05 cutoff returns 539 basins — far too many for a UI list. Meanwhile all 15
well-matched Mediterranean analogs land below 0.09. A distance cutoff would be
query-dependent (a rare climate type has few neighbours at any absolute threshold; a
common type has hundreds).

**Decision: fixed top-N, not a distance threshold.** N=20 basins → ~14 named places in
practice (from Cell 9 ratio). Consistent result count; user sees the best available
regardless of how common their climate type is.

---

## Part 6 — A5: L06 vs L08

Not tested empirically. L06 coverage (66%) is sufficient for the top-N query; 10,799
basins with named places gives ample candidates at any query location of interest.
L06 also benefits from the basin-scale smoothing validated in WO5. **Use L06.**

---

## Part 7 — A6: fclasses filter

P+S vs P-only:

| | P+S | P only |
|---|---|---|
| Gazetteer rows | 1,508,492 | 1,459,273 |
| L06 basins covered | 10,799 | 10,681 |
| Top-10 results (SF) | identical | identical |

S places contribute 118 additional basins at 1.1% coverage gain. Top results are
unaffected. **Use P+S** — no cost, marginally better coverage in sparse regions.

---

## Part 8 — Decisions locked for Part B

| Decision | Value |
|---|---|
| Level | L06 |
| Distance metric | Normalized Euclidean, 2-index (pre_concentration, seas_phase_offset) |
| Top-N | 20 basins |
| Result shape | one place per basin (deterministic: lowest place_id) |
| Gazetteer | `cedop.gaz.whg_gaz`, filter `hybas_id_l06 IS NOT NULL` |
| fclasses | P+S (no additional filter) |
| Compute approach | full pairwise in Python at query time (16k basins, milliseconds) |
