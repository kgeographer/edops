# WO5 findings

**WO:** wo5_polity-slice  
**Phase:** Surface  
**Branch:** surf_wo5

---

## F5.1 — Band T is a span, not a slice snapshot ✓ confirmed

**Context:** The critical open question from the WO5 spec (finding #2): does the polity
payload carry a single slice's snapshot or a span?

**Answer:** Span confirmed. For the Northern Song fixture (from_year=1000, to_year=1100):

| Source | Variables | Rows/var | Shape |
|---|---|---|---|
| LMR v2.1 | lmr_pdsi, lmr_air, lmr_prate | 101 | One per year, 1000–1100 CE |
| HYDE 3.4 | hyde_cropland, hyde_grazing, hyde_pasture, hyde_rangeland | 2 | Epoch endpoints (1000 CE, 1100 CE) |
| eVolv2k v4 | evolv2k_vssi | 9 | Discrete events within span |

**Methods:** `grid_areal_distribution` for LMR and HYDE; `global_forcing` for eVolv2k.

**Implication:** No engine change needed for the span case. The engine already returns a
full per-year time series for LMR, epoch endpoints for HYDE, and discrete events for
eVolv2k. The "single slice snapshot" scenario does not arise — the payload is already
what a time-series visualization needs.

---

## F5.2 — Payload shape and renderer behaviour at polity scale

**Rows:** 372 total (52 A–E + 320 T). A–E is identical in structure to the buffer case
(same 52 rows, same methods, same renderer path — the existing `renderSignature` + widgets
handled it without modification). T rows are heavier: 320 rows for a 101-year span.

**Renderer coping:** No strain observed at polity scale. The accordion structure holds;
Band T renders as a distinct content block (not a table of rows). The `marginal_exposure`
field is present in the neighborhood block (`{lt_50pct: 0.030, lt_20pct: 0.008}`) —
noted for future display; not rendered in WO5.

**n_units (LMR):** 93 LMR cells over Northern Song. HYDE n_units is much larger
(~37,901 HYDE cells) — different spatial resolution from LMR, as expected.

---

## F5.3 — Time marginal + value marginal built directly; raw dump stage skipped

**Context:** The WO5 spec called for a "raw dump" to see the material before designing
a visualization. Karl identified the design (time marginal + value marginal, per the
mockup) before writing began, and the fixture confirmed the data was there to support it.
The raw dump stage was skipped.

**What was built:**
- **Time marginal SVG** (per LMR variable): mean line (dark blue) + p10–p90 envelope
  (light fill) over the full year span. y-axis labeled with min/max; x-axis with year
  range. Zero line dashed where range crosses zero.
- **Year slider** (per LMR variable): range input `min=from_year` `max=to_year`. Updates
  the value marginal histogram on input. Initial position: midpoint of span.
- **Value marginal histogram**: the `detail.distribution` from the selected year's row —
  the same `renderHistogram` function used for B1 rows. Temporal stamp shows
  `boundary_year · span` (from existing histogram stamp logic).
- **HYDE table**: two-column epoch table (1000 CE, 1100 CE) × four HYDE variables.
  Two data points do not make a time series; table is honest and readable.
- **eVolv2k event list**: year + VSSI (Tg S) per event.

**Browser result:** LMR time marginals and sliders work as intended. Slider updates the
per-year histogram live (client-side only — all data loaded with the fixture).

---

## F5.4 — What's missing for an eventual map

**Context:** Finding question #4: gap between Band T and what a Cliopatria-style map paint
would need.

**Gap:** The Band T payload aggregates values over the polity's basins/cells — each T row
is a weighted summary statistic for the whole polity at a given year. A choropleth (painting
individual basins or LMR cells by value at a selected year) needs **per-unit values at
a specific year**, not an aggregate. That data is not in the current endpoint response.

**What a map would need:** A separate endpoint or query delivering `{unit_id: value}` for
a variable at a chosen year, over the polity's spatial footprint. This is a different
product from the signature — closer to the Explorer's `/api/explorer/values` flat-dict
pattern, scoped to a polity.

**Status:** Not a WO5 concern. Noted as a future engine/route task; add to deferred register
when the map step is planned.

---

## F5.5 — HYDE blocky-bar deferred; table is sufficient for now

**Context:** Karl noted that the HYDE epoch table could be a "blocky histogram" (two bars,
before/after) matching the LMR visual language. With only two data points the table is
already readable, and the visual treatment is cosmetic rather than informative.

**Status:** Deferred to a polish pass. The table stays.
