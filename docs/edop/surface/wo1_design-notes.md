# WO1 design notes — UI considerations from payload inspection

Source: `docs/edop/surface/wo1_findings.md` (F1.1–F1.13)
Access these when building the new sandbox page. Not bugs — constraints, widget choices,
and rendering decisions that the payload structure dictates.

---

## DN1 — `resolver_year` not at top level (M1)

`resolver_year` is only accessible in `detail['distribution']['resolver_year']` on any
histogram-bearing row. It is not in the payload top-level or `neighborhood` block.
**When wiring `/api/area`:** inject `resolver_year` into `neighborhood` (or a new `query`
block) from the route parameter. This avoids requiring detail mode just to display the
boundary year in a header.

See also: DN2 (polity name / period).

---

## DN2 — Polity name and period absent from payload (M2)

`neighborhood` carries `level, marginal_exposure, n_units, type, unit_type` — no polity
name, no `fromyear`/`toyear` period. A header showing "Northern Song (960–1127)" must be
sourced from query parameters or a supplementary `/api/polity/period` call.
**Route-layer fix (same pass as DN1):** echo back `polity`, `resolver_year`, and resolved
`fromyear`/`toyear` in the neighborhood or a `query` block.

---

## DN3 — Band T time-series requires detail mode (M3)

LMR (and HYDE) rows in lean mode: `score=None, detail=None`. There is no per-year value
accessible without `&detail=true`. Time-series charts must use a detail-mode call.
The design implication: the Band T panel should trigger a detail request, not a lean one.
There is no workaround within the current API shape.

---

## DN4 — `distribution_only` → range-bar, not histogram (M4)

`distribution_only` rows (`reservoir_vol` and two others) carry `p10`, `p90`, `regimes`,
`suppressed_score` in detail — but no histogram. The appropriate widget is a range-bar
spanning p10–p90 with a regime breakdown (for `two_regime` modality), not a histogram.
`suppressed_score` can be displayed with a caveat label ("score suppressed — bimodal").
Do not show it as the headline value.

---

## DN5 — `marginal_exposure` conditionally present (M5)

Only present on polygon-path scopes (`resolve_polygon`, `resolve_polity`). Absent for
single-basin and buffer. The UI quality badge should render conditionally; absence is not
an error and must not throw.

Threshold guidance: `lt_50pct > 0.10` could trigger a caution indicator (>10% of basins
are less than half-covered). The N. Song / 4 Corners comparison (0.030 vs 0.147) gives
a sense of scale.

---

## DN6 — Band T rendering trifurcation (F1.7)

Three distinct substrates, three distinct renderers — all sharing a time axis:

| Substrate | Method | Widget |
|---|---|---|
| LMR (3 vars, annual) | `grid_areal_distribution` | Line chart + p10/p90 shaded band |
| HYDE (4 vars, epochs) | `grid_areal_distribution` | Step/bar chart per variable |
| eVolv2k (events) | `global_forcing` | Spike / event timeline |

LMR p10/p90 is spatial spread across the polity (meaningful — show it).
HYDE values are in km² (unit label required); LMR is dimensionless.
eVolv2k primary field is `vssi` (Tg SO₂); `location` field can label events.

---

## DN7 — `raw` field semantics vary by method (F1.10)

`raw` is not uniformly a physical-unit number. Branch on `method`:

| Method | `raw` contains |
|---|---|
| `area_weighted` | None |
| `dominant_basin` | actual sensor value (physical units) |
| `class_mixture` | modal class label (string — treat as display text) |
| `flag_fraction` | the fraction value (0–1) |
| `distribution_only` | None |
| `extreme` | actual measurement value (physical units) |

`class_mixture` is the sharpest case: `raw` is a string label, not a number.

---

## DN8 — Basin-ring requires its own renderer (F1.11)

No top-level `rows` — cannot share the signature table renderer used by other scopes.
Three viable display paths (may be combined as tabs or progressive disclosure):
1. **Comparison table**: 6 columns (center + 5 ring members), one row per variable;
   `border_bearing` provides natural clockwise column order.
2. **Schematic map / compass**: center with neighbors at bearing; `shared_km` →
   edge thickness; `sub_area_km²` → neighbor glyph size.
3. **Per-member deep-dive**: select a ring member → render its full 52-row signature
   via the single-basin renderer (all data is present in `member.signature`).

Size variation can be extreme (921 km² vs 24,966 km² in the Timbuktu example). Do not
weight neighbors equally in any visual treatment.

---

## DN9 — Histogram widget trigger is method type, not null-check (F1.4, F1.9)

Histogram present ↔ method is `area_weighted` or `grid_areal_distribution`.
Do not trigger the widget by checking whether `detail['distribution']` is non-null — check
`row['method']` instead. The null-check works in practice today, but it couples the widget
to an implementation detail rather than the semantic intent.

Note: `row["distribution"]` (top-level, always null) is NOT the histogram. See TODO 2.

---

## DN10 — `flag_fraction` and `global_forcing` detail dicts are empty (F1.9)

`&detail=true` is harmless for these rows but adds no data. No histogram, no p10/p90,
no supplementary sub-dict. Render `flag_fraction` as a plain fraction or binary indicator;
render `global_forcing` (eVolv2k) from the row fields directly (`vssi`, `year`, etc.).
