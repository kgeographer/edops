# WO3 — Buffer scope live + leaf widget polish

**Branch:** Surface / sandbox v2 page
**Phase:** Surface · **Step:** 2 (leaf widgets) + first half of Step 3 (buffer scope live)
**Depends on:** WO2 (atomic rows-renderer, fixture harness) — done.
**Type:** front-end, fixture-driven. No engine change. No endpoint call (fixture loader only).
Touches only the sandbox v2 page's own code. Live Lookup (`sandbox.html`) untouched.

## Goal

Two coupled pieces:
1. **Enable the buffer scope** in the fixture harness so selecting "Buffer" renders
   `02_buffer_detail.json` through the existing `renderSignature`. This gives the widgets a
   live multi-unit case to render, not just build-time test data.
2. **Polish the four leaf widgets** — histogram, coherence badge, range-bar, mixture bar —
   each against the fixture that exercises it.

The renderer needs no structural change: buffer returns the same `{rows[], neighborhood}`
shape as single-basin (WO2's atomic-first build already covers "same function over more rows").
This WO adds a scope entry, one input control, and replaces the minimal WO2 leaf renders with
real widgets.

## Part A — buffer scope live

- Add buffer to `FIXTURE_URLS` → `/dev/exemplars/02_buffer_detail.json`.
- Show a **radius (km) input** when scope = Buffer (hidden otherwise, per the left-column
  fallout). In fixture mode this control is **honest but non-functional**: populate it to the
  fixture's actual radius (Timbuktu 100 km — confirm from the fixture's `neighborhood` block)
  so the page doesn't misrepresent what produced the data. It becomes functional when buffer
  gets a live route (later WO); note that forward.
- Selecting Buffer + Get signature loads the buffer fixture and renders it through
  `renderSignature` unchanged. Confirm the multi-unit payload renders (n > 1; coherence rows
  now show real `concentrated`/`spread` variation, not the single-basin trivial `concentrated`).
- Header reflects buffer scope (n_units from `neighborhood`, not "n=1").

## Part B — leaf widgets (one accept gate each)

Build in this order; the histogram is the marquee piece and gets its own sub-review.

**B1 — histogram widget** (`area_weighted` rows).
- **Static weighted histogram.** Bins on x, summed unit-weight on y. No time axis, no envelope,
  no scrubber — the envelope/scrubber is a Band-T interaction, deferred to that step.
- Input: `row.detail.distribution` — `bins` (21 edges) + `weights` (20). Weighted bars, not
  counts.
- Trigger on **`row.method`** (`area_weighted`), NOT a detail-null check (DN9).
- x-axis is percentile (0–100) for these B1 rows.
- Build/verify against `02_buffer_detail.json` (real spread). Degenerates correctly on the
  single-basin fixture (n=1 → single populated bin) — verify it doesn't break there.
- Replaces the `[hist]` placeholder slot from WO2.
- **Null temporal-stamp path (fixture-confirmed):** buffer rows carry
  `resolver_year=None, band_t_from=None, band_t_to=None` (buffer is atemporal). Any caption or
  stamp that will later show the two temporal axes for Band T rows must render **nothing** when
  those fields are null. Build that null path now so the Band-T step (which populates them) is
  a no-op change to this widget, not a surprise. `unit_type` is `basin` here.
- Fixture-confirmed: all 34 `area_weighted` rows carry `detail.distribution` with 21 bin edges
  + 20 weights + summary stats + the stamp fields above.

**B2 — coherence badge** (`area_weighted` rows).
- Render `row.coherence` (`concentrated` / `spread`) as a styled badge, not plain text.
- Meaningful only multi-unit — build against buffer fixture. On single-basin it's trivially
  `concentrated`; that's correct, not a bug.
- **Three states, fixture-confirmed:** the buffer fixture's `area_weighted` rows split
  `spread` (22) / `concentrated` (9) / `None` (3). `coherence: None` must render **no badge**
  (not an empty or default one) — it's the "coherence doesn't apply" case, not a missing value.
  Build the no-badge path explicitly.

**B3 — range-bar** (`distribution_only` rows).
- A horizontal bar spanning **p10–p90** (from `row.detail`), NOT a histogram (DN4).
- If modality is `two_regime`, show the regime breakdown; show `score_suppressed` with a
  caveat label ("score suppressed — bimodal"), never as the headline value (DN4).
- **Fixture-confirmed — both branches present in `02_buffer_detail.json`:**
  - Unimodal: `temp_max` (score 95.56, p10 93.6 / p90 96.83) and `temp_min` (score 78.98,
    p10 75.43 / p90 81.07). Plain range-bar, `regimes=None`.
  - `two_regime` suppressed: `reservoir_vol` (`score=None`, `suppressed=True`,
    `suppressed_score` in detail, p10 0.0 / p90 89.59, `regimes=[{center:0.0, weight:0.708},
    {center:89.59, weight:0.292}]`).
- **Regime-marks refinement (do not skip):** for a `two_regime` row, draw the regime centers
  as marks on the bar, sized/weighted by their `weight`. `reservoir_vol` spans p10 0.0 → p90
  89.59 — nearly the full axis — but that is **two spikes with an empty middle** (most basins
  have no reservoir; a few have large ones), not a wide uniform spread. A bare p10–p90 bar would
  misread as high uniform spread. The `regimes` array is there to be drawn, not just captioned.

**B4 — mixture bar** (`class_mixture` rows).
- Modal class label + a proportion bar for the mixture breakdown.
- `row.representative_raw` is the **string class label** — render as text, never format numeric
  (DN7). WO2 already handles the string case; B4 makes it a styled bar instead of bare text.
- Single-basin fixture exercises this ("Open shrubland 100%", "Freshwater marsh 100%"); buffer
  will show true multi-class mixtures.

**Physical-value rows** (`dominant_basin`, `extreme`) — WO2 already renders these acceptably
(score + physical raw + carrier basin, e.g. "84.9 pct · 499.33 m³/s basin 1060551560"). Polish
only if they read poorly next to the new widgets; otherwise leave. `flag_fraction` likewise
(plain fraction, empty detail per DN10).

## Out of scope

- No live endpoint / route wiring (fixture loader only; buffer's live route is a later WO).
- No envelope/scrubber histogram (Band-T step).
- No Band T rendering (T rows absent from single-basin and buffer A–E fixtures).
- No polity/ring/polygon scope enablement (later steps). Polity fixture may be used to
  stress-test the histogram if useful, but polity *scope* stays inert.
- No Analysis tab work.
- `marginal_exposure` — absent on buffer (DN5, polygon-path only); must not throw on absence.

## DN references honored

- DN4 — `distribution_only` → range-bar + suppressed-score caveat, not histogram.
- DN7 — `class_mixture.raw` string label rendered as text.
- DN9 — histogram triggered by `row.method`, not detail-null.
- DN10 — `flag_fraction` empty detail; render from row fields.
- DN5 — `marginal_exposure` absence on buffer is normal; guard.

## Accept gates

Per-widget review before write (B1→B2→B3→B4), plus Part A reviewed before Part B starts:
- **Part A:** Buffer selectable; buffer fixture renders through `renderSignature`; multi-unit
  header; radius input shown and honest.
- **B1:** histogram renders weighted bars from `distribution` on buffer fixture; method-triggered;
  degenerates safely on single-basin.
- **B2:** coherence badge styled; real `spread`/`concentrated` variation visible on buffer.
- **B3:** range-bar spans p10–p90 on unimodal rows; `reservoir_vol` shows regime marks +
  suppressed-score caveat (not a bare wide bar).
- **B4:** mixture bar renders string label + proportions.
- Live Lookup page untouched; full `pytest tests/` green (structural + Playwright).
- Karl reviews each write before it lands.

## Forward notes

- When buffer gets a live route, the radius input becomes functional and the route must
  serialize the callable payload **unmodified** (WO2 constraint) or the fixture ceases to be a
  valid proxy.
- Histogram widget built here is reused for Band T `grid_areal_distribution` rows later (same
  weighted-bar widget, native-unit x-axis instead of percentile). Keep it parameterizable on
  x-axis label/scale so the Band-T step doesn't rebuild it.