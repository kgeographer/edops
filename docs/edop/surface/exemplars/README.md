# Exemplar payloads — inspection findings

Generated 2026-07-01. Payloads at `output/edop/surface/exemplars/` (gitignored).
Capture script: `scripts/edop/surface/capture_exemplar_payloads.py`.

---

## Reproducible calls

| File | Entry point | Arguments |
|---|---|---|
| `01_single_basin_{lean\|detail}.json` | `single_basin_signature` | `lat=16.8167, lon=-2.9833, level=6, bands=ABCDE` |
| `02_buffer_{lean\|detail}.json` | `areal_signature` | `lat=16.8167, lon=-2.9833, radius_km=100, level=6, bands=ABCDE` |
| `03_polity_nsong_{lean\|detail}.json` | `areal_signature_polygon` | `geom_wkt=Northern Song @ year=1000 (990–1017), level=6, bands=ABCDET, from_year=1000, to_year=1100, resolver_year=1000` |
| `04_basin_ring_{lean\|detail}.json` | `basin_ring_signature` | `lat=16.8167, lon=-2.9833, level=6, bands=ABCDE` |
| `05_polygon_4corners_{lean\|detail}.json` | `areal_signature_polygon` | `geom_wkt=POLYGON((-110 35,-105.5 35,-105.5 38,-110 38,-110 35)), level=6, bands=ABCDE` (4 Corners / Santa Fe / upper Rio Grande) |

---

## Checklist findings

### 1. Methods present

All five scopes produce exactly **52 base rows** (Bands A–E) with the same 6 method types,
regardless of scope (single-basin, buffer, polygon). The scope affects scores and coherence
verdicts, not row structure.

| Method | Count | Block | Notes |
|---|---|---|---|
| `area_weighted` | 34 | B1 | Continuous variables; the workhorse |
| `class_mixture` | 10 | B3/B4 | Categorical: biome, soil type, etc. |
| `dominant_basin` | 3 | B2 | Network-topology: discharge, dis_m3_pyr, dis_m3_pmth |
| `distribution_only` | 3 | B5 | reservoir_vol, temp_max, temp_min |
| `flag_fraction` | 1 | B4 | coast_fraction only |
| `extreme` | 1 | B5 | river_area only |

Band T (S3, 1000–1100 CE) adds 320 rows:

| Method | Count | Unit type | Variables |
|---|---|---|---|
| `grid_areal_distribution` | 303 | `lmr_cell` | lmr_pdsi × 101 yrs, lmr_air × 101, lmr_prate × 101 |
| `grid_areal_distribution` | 8 | `hyde_cell` | hyde_cropland/grazing/pasture/rangeland × 2 epochs |
| `global_forcing` | 9 | `global` | evolv2k_vssi × 9 events in 1000–1100 CE |

**8 leaf-renderer types confirmed** (as sketched). The 6 base types + 2 Band T types cover the
full space. No surprises.

---

### 2. Histogram presence

Histograms (`detail['distribution']` object) appear in **exactly two method contexts**:

- `area_weighted` (B1) — **all 34 rows** carry a histogram in detail mode
- `grid_areal_distribution` (Band T, LMR) — **all 303 LMR rows** carry a histogram in detail mode

**No histograms** in: `class_mixture`, `dominant_basin`, `distribution_only`, `flag_fraction`,
`extreme`, `global_forcing`.

Implication: the histogram widget is needed in 2 of the 8 renderer contexts. `distribution_only`
(B5) carries `p10`, `p90`, `spread` in detail but **no distribution object** — a range-bar or
p10–p90 indicator suffices there, not a full histogram.

Sample histogram object (B1, `aridity`, S2 buffer):
```json
{
  "bins": [21 floats],  "weights": [20 floats],
  "n_units": 9,  "unit_type": "basin",  "low_resolution": false,
  "min": ...,  "max": ...,  "p10": ...,  "p90": ...,  "mean": ...,
  "resolver_year": null,  "band_t_from": null,  "band_t_to": null
}
```

Sample histogram (Band T, `lmr_pdsi`, S3 polity):
```json
{
  "bins": [21 floats],  "weights": [20 floats],
  "n_units": 93,  "unit_type": "lmr_cell",  "low_resolution": false,
  "mean": 0.164,  "p10": 0.010,  "p90": 0.320,
  "resolver_year": 1000,  "band_t_from": 1000,  "band_t_to": 1100
}
```

Note: HYDE rows (`grid_areal_distribution`, `hyde_cell`) do **not** carry a distribution
histogram — they carry only `representative_raw` (weighted mean km²) and no `detail.distribution`.
This is expected: HYDE is reported as a scalar per epoch, not a per-cell distribution.

---

### 3. Band T shape

**LMR (303 rows, 3 vars × 101 years):**
- One row per year per variable. Field `year` holds the CE year (1000–1100).
- `representative_score`: null for all LMR rows — the value is distribution-only.
- `representative_raw`: null.
- Time series collation: filter by `variable`, sort by `year`. Use `detail.distribution.mean`
  as the scalar for a line chart; `p10`/`p90` from the same distribution for the envelope.
  Mechanically clean — groupby-and-sort, then read `.mean`. **Requires detail mode.**

**HYDE (8 rows, 4 vars × 2 epochs):**
- Field `epoch_year` (not `year`) holds the CE epoch (1000, 1100 here — HYDE has non-regular
  steps so 2 epochs fell in 1000–1100).
- `representative_raw`: weighted mean km² across intersecting grid cells (e.g. cropland at
  epoch 1000: 3.32 km², at 1100: 8.01 km² — Song agricultural expansion is legible).
- `representative_score`: null. Native-unit display only; no percentile score for HYDE epoch values.
- No histogram. The display is epoch bars (raw values in km²), not a distribution.

**eVolv2k (9 events in 1000–1100 CE):**
- One row per event. Field `year` holds the event year (1003, 1011, 1020, 1028, …, 1092).
- `representative_raw`: vssi value (e.g. 4.98, 1.61, 7.78 …) — volcanic forcing in Tg SO₂.
- `representative_score`: null. No percentile ranking for forcing events.
- No histogram. Display as an event timeline, not a distribution.

---

### 4. Temporal axes location

| Axis | Where it lives |
|---|---|
| Band T span (`from_year`/`to_year`) | `payload.temporal = {from_year, to_year}` |
| `resolver_year` | **Not a top-level key.** Stamped on histogram objects only: `row.detail.distribution.resolver_year` |

Both axes appear together in LMR histogram stamps: `{resolver_year: 1000, band_t_from: 1000, band_t_to: 1100}`.
B1 histograms carry `resolver_year` but `band_t_from/to` are null (correct — B1 has no Band T).

**Gap**: `resolver_year` is not exposed at the top level of the payload. A UI label such as
"Boundary year: 1000 CE" requires digging into any histogram's stamp, or the route must add it
to the `neighborhood` block when serving a polity query. Flagged as a missing field (see §6).

---

### 5. Lean vs detail delta

The ONLY structural difference between lean and detail is the `detail` key on each row:

- **Lean**: `detail: null` on every row
- **Detail**: `detail: {...}` sub-dict present; content varies by method:
  - `area_weighted` → `{distribution, p10, p90, spread, unit}`
  - `distribution_only` → `{p10, p90, spread, unit}` ± `regimes` (no distribution histogram)
  - `class_mixture` → `{concentration, mixture, modal_class_id, modal_share, n_classes}`
  - `dominant_basin` → `{dominant_hybas_id}`
  - `extreme` → `{dominant_hybas_id}`
  - `flag_fraction` → no detail sub-dict
  - `grid_areal_distribution` (LMR) → `{distribution, …}` (histogram per year)
  - `global_forcing` → no detail sub-dict

Every other field in the row — `representative_score`, `representative_raw`, `coherence`,
`modality`, `coverage`, `status`, `n_units`, `caveat`, `year`, `epoch_year` — is identical
between lean and detail. The split is correctly drawn. The sandbox page consumes detail; lean is
the API-caller reference.

Note: there is a top-level `distribution` field on every row that is always null. This appears
to be a legacy field that the engine emits but does not populate. It can be ignored by the UI.

---

### 6. Missing fields

Fields the UI design wants that no row currently carries:

| # | Missing | Where needed | Resolution |
|---|---|---|---|
| M1 | `resolver_year` at top level | Polity path: UI label for boundary year | Add to `neighborhood` in the route handler (not engine); or surface reads `rows[0].detail.distribution.resolver_year` |
| M2 | Polity name + period in payload | UI header "Northern Song (990–1017)" | Route adds from `polity_meta` returned by `resolve_polity`; engine doesn't carry it |
| M3 | LMR scalar in lean mode | Any time-series chart without `&detail` | By design: LMR mean lives only in `detail.distribution.mean`; page must use detail |
| M4 | HYDE epoch score (percentile) | Comparison to other regions | By design: HYDE is reported in km²; no percentile relative to global — would need engine addition |
| M5 | `marginal_exposure` on non-polygon scopes | Buffer/single-basin UI parity | By design: `marginal_exposure` is a polygon-path concept; UI must conditionally show it |
| M6 | Ring-level aggregation / summary | Any "overall" ring view | By design: the engine doesn't aggregate the ring; surface must decide if/how to summarize |

M1 and M2 are route-layer additions, not engine changes. M3–M5 are by-design constraints
the UI must respect. M6 is a Surface design question deferred to the page spec.

---

## Cross-scenario summary: missing-fields paragraph

The payload is substantially complete for the new sandbox page. Two gaps require route-layer
(not engine) fixes before the polity UI path is complete: **`resolver_year` is not exposed at
the payload top level** (only stamped on histogram objects), and **the polity name and temporal
span are not in the payload** (they're returned by `resolve_polity` but not forwarded to
`areal_signature_polygon`). Both are small additions to the `/api/area` route handler. Beyond
those, the binding constraint for any time-series or envelope chart is that **LMR scores are
null in lean mode** — the page must request `&detail=true` to access `distribution.mean` per
year, confirming the WO's framing decision. Everything else — 8 renderer types, histogram
widget on B1 and LMR only, HYDE as epoch bars in km², eVolv2k as a forcing timeline — follows
cleanly from the payload structure without further engine work.
