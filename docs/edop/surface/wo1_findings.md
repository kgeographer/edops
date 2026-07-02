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
