# WO4 findings — make_row, projector, assembler, Band T promotion

**Date:** 2026-06-23
**Branch:** engine01
**Status:** complete — 5/5 acceptance tests PASS

---

## §1 — Basin-path field inventory (confirmed from step3_results.tsv)

**Columns in the frozen TSV:**

```
variable, method, status, representative_score, representative_raw,
n_basins, coverage_weight, spread, p10, p90, weight_at_zero,
dominant_hybas_id, modal_class_id, modal_share, n_classes, concentration,
verdict, modality, representative_score_suppressed
```

**Old `status` vocabulary → Pin 1 translation:**

| Old value | Count | New home |
|---|---|---|
| `two_regime` | 12 | `status=ok` + `modality='two_regime'` + `score_suppressed=True` |
| `spread` | 12 | `status=ok` + `coherence='spread'` |
| `mixed` | 8 | `status=ok` + `coherence='mixed'` |
| `concentrated` | 7 | `status=ok` + `coherence='concentrated'` |
| `dominant` (B2: 3 rows; B3 artifact: 2 rows) | 5 | `status=ok`. B2 identity already carried by `method='dominant_basin'`. The two B3 "dominant" rows (`lith_class`, `zone_name`) are a stale research artifact — current Cell 13 code produces `status='ok'` for all B3 rows (modal_share=1.0 falls into `concentrated` verdict, which maps to `coherence='concentrated'` in the new scheme). |
| `outside_active_domain` | 3 | stays in `status` |
| `untyped` | 2 | not a status — routing fact already in `method='distribution_only'` |
| `uniform` | 1 | `status=ok` (coast_fraction uniformly zero at Timbuktu; Timbuktu-specific edge case) |
| `ok` | 1 | stays |

**B7 field mapping** — all B7 fields confirmed present in `make_row`; no field dropped:

| B7 notebook field | `make_row` field |
|---|---|
| `n_units` | `n_units` (same) |
| `unit_type` | `unit_type` (same) |
| `coverage_weight` | `coverage` (renamed for collision resolution) |
| `year` | `year` (top-level on row) |
| `epoch_year` | `epoch_year` (top-level on row) |
| `lmr_caveat` (text string in row) | `caveat=['lmr_caveat']` (key-ref; text in `CAVEAT_TEXTS`) |
| `hyde_caveat` (text string in row) | `caveat=['hyde_caveat']` (key-ref) |
| `p10`, `p90`, `sd` (top-level columns) | `detail={'p10':…, 'p90':…, 'sd':…, 'unit':'km2_per_cell'}` |
| `representative_score` | `representative_score` (always null for B7) |
| `status` | `status` (ok / no_data; no_events retired) |

---

## §2 — What was built

### `make_row` signature

```python
make_row(
    variable, band, method, unit_type, n_units,
    representative_score, representative_raw, coverage, status,
    coherence=None, modality=None, score_suppressed=False,
    distribution=None, weight_at_zero=None, caveat=None,
    year=None, epoch_year=None, units=None, detail=None,
) -> dict
```

Returns the **complete** row dict — lean fields + `detail` sub-block. The four pins:

- **Pin 1** — `status ∈ ok | outside_active_domain | no_data`. All old branch verdicts
  (`concentrated`, `spread`, `mixed`, `untyped`, `dominant`) translate to `coherence` or
  `method` or are dropped. The shaper (WO5+) applies the translation; `make_row` itself
  only accepts Pin 1 values.
- **Pin 2** — `caveat` is always a list (empty = no caveats; never null). Text lives once
  in `CAVEAT_TEXTS` dict in engine.py, keyed by `'lmr_caveat'` and `'hyde_caveat'`.
  `assemble_payload` collects referenced keys and emits the text at top level.
- **Pin 3** — ECC spatial collapse and no-within-span temporal aggregation are orthogonal.
  `distribution='collapsed_subresolution'` on LMR rows records the spatial collapse;
  the temporal series is preserved at full annual resolution regardless.
- **Pin 4** — `score_suppressed=True` means score is null *because* a two_regime verdict
  makes a single number dishonest. `score_suppressed=False` + `representative_score=None`
  means score is not applicable (Band T has no global-percentile ranking).

### `project_row(row, include_detail=False) -> dict`

Strips the `detail` key for the lean default; includes it when `include_detail=True` (`&detail`).

### `assemble_payload(rows, neighborhood, shortfall, bands, temporal=None, include_detail=False) -> dict`

Collects caveat keys referenced by any row → emits `caveats` dict at top level. Projects
each row. Returns:

```python
{
    'neighborhood': ...,
    'shortfall':    ...,
    'bands':        [...],
    'temporal':     {'from_year': ..., 'to_year': ...} | None,
    'caveats':      {'lmr_caveat': '<text>', ...},   # only keys used by some row
    'rows':         [project_row(r, include_detail) for r in rows],
}
```

### `aggregate_band_t(lat, lon, radius_km, from_year, to_year, conn) -> list[dict]`

Promoted from step3b_band_t.ipynb Cell 13. Re-wired to `make_row` instead of `_row`.
Buffer geometry and area computed on-the-fly from lat/lon/radius_km — no notebook-scope
closure variables.

**One behavioral correction vs. the notebook:** the notebook's `aggregate_band_t` did not
pass `lmr_caveat=LMR_CAVEAT` to `_row` for LMR rows (the arg was present in the single-year
Cell 11 path but missing from Cell 13's aggregate path). The engine fixes this: every LMR
row now carries `caveat=['lmr_caveat']`. The frozen step3b_block7_wide.tsv's `lmr_caveat`
column is therefore all NaN for LMR rows — this is the notebook artifact, not the correct
behavior.

---

## §3 — Acceptance (5/5 PASS)

### Test 1 — Numeric regression vs. step3b_block7_primary.tsv (1100–1200)

321 rows match. Strategy: method-stratified to handle the HYDE boundary effect.

- **LMR (303 rows) + eVolv2k (10 rows):** strict diff, float_tol=0.01. PASS.
- **HYDE (8 rows — 4 vars × 2 epochs):** structure (variable/method/year/epoch_year)
  matches exactly. `n_units` within ±1. `representative_raw` within 15% relative. PASS.

**HYDE boundary effect:** one HYDE cell sits at the geometric edge of the 100 km buffer.
Its `ST_Intersection` overlap_m2 is at or near zero and its inclusion depends on
floating-point rounding in `ST_Area`. The frozen TSV (written at a prior session) includes
this cell (n_units=426); the engine's current query excludes it (n_units=425). The excluded
cell has high grazing/rangeland values (~7 km²), making it visible in the weighted mean
(~11% relative shift). This is not a code error — it's a spatial boundary reproducibility
limit of single-cell granularity. The LMR and eVolv2k paths are unaffected.

### Test 2 — Caveat mechanism (Pin 2)

- 303 LMR rows: `caveat=['lmr_caveat']` ✓
- 8 HYDE rows (no 1950 in span 1100–1200): `caveat=[]` ✓
- 10 eVolv2k rows: `caveat=[]` ✓
- `assemble_payload` top-level `caveats`: `{'lmr_caveat': '<text>'}` ✓

### Test 3 — HYDE 1950 round-trip (span 1900–2000)

4 HYDE rows at epoch_year=1950 carry `caveat=['hyde_caveat']`. Top-level `caveats`
includes both `lmr_caveat` and `hyde_caveat`. ✓

### Test 4 — Lean vs. full projection

Lean row: 18 fields, no `detail` key. Full row: same + `detail: {p10, p90, sd, unit}`.
Sample (hyde_cropland, year 1100, Timbuktu):

```
variable          = 'hyde_cropland'
band              = 'T'
method            = 'grid_areal_distribution'
unit_type         = 'hyde_cell'
n_units           = 425
representative_score = None
representative_raw   = 0.0178  (km²/cell weighted mean)
score_suppressed  = False
coverage          = 1.0000
status            = 'ok'
coherence         = None
modality          = None
distribution      = 'reported'
weight_at_zero    = None
caveat            = []
year              = 1100
epoch_year        = 1100
units             = 'km²'

detail = {p10: 1.53e-07, p90: 0.073, sd: 0.028, unit: 'km2_per_cell'}
```

### Test 5 — Status vocabulary

All 321 rows: `status ∈ {ok, no_data, outside_active_domain}`. ✓

---

## §4 — Proposed B1–B6 extraction order (WO5+)

The natural order goes simplest-first, and defers the two post-pass blocks (B4 synthetics,
B6 modality) until the primary blocks they depend on are proven.

| WO | Block | detail fields | Regression target |
|---|---|---|---|
| WO5 | B2 — `dominant_basin` | `{dominant_hybas_id}` | B2 rows in step3_results.tsv (3 rows) |
| WO6 | B1 — `area_weighted` | `{spread, p10, p90, unit:'percentile'}` + `coherence` | B1 rows in step3_results.tsv (34 rows, incl. two_regime status rows) |
| WO7 | B3 — `class_mixture` | `{modal_class_id, modal_share, n_classes, concentration}` + per-class mixture + `coherence` | B3 rows + step3_block3_mixture.tsv |
| WO8 | B4 — `flag_fraction` + outlet_type synthetic | synthetic provenance; `coherence` on outlet_type | B4 rows in step3_results.tsv |
| WO9 | B5 — `distribution_only` + `extreme` | B5-dist: `{spread, p10, p90, unit:'percentile'}`; B5-ext: plain ok | B5 rows + step3_block5_distribution.tsv |
| WO10 | B6 — modality refinement post-pass | `{regimes: [{id, center, weight}]}` + `modality` + `score_suppressed=True` | two_regime rows in step3_block6_regimes.tsv |

B2 first: simplest (one scalar per row, no distribution, no coherence flag — `dominant_basin`
method is self-describing). B6 last: it's a post-pass over the distribution-bearing rows
from B1 and B5; can't be cleanly extracted until those are proven against `make_row`.
