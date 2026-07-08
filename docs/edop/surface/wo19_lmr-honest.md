# WO19 — LMR per-span values route: honest temporal paint

**Branch:** `surf_wo19` — new route + LMR paint rewire. **No change to basin/HYDE paint paths.**
**Type:** Build — retires the notch-based LMR paint and the hidden paint-year slider (F15.2). Closes
the last pre-Braga-required item in the choropleth space (F15.9); the last hidden-temporality paint
on a Braga-facing surface.

## Goal

Build `/api/lmr/values` over the **annual** arrays in `temporal.lmr_climate` and rewire the LMR
choropleth to paint the **mean anomaly over a real span**, replacing the 5-notch approximation
(`air_0`–`air_4` / `prate_0`–`prate_4` from `lmr_notches.geojson`).

## Why

LMR currently paints one of five coarse notches — Early (700–950), MCA (950–1250), Transition,
LIA, Industrial — snapped from a hidden paint-year slider defaulted to 1100 CE (F15.1/F15.2). So a
user painting LMR anomaly while their signature covers, say, Northern Song's actual window sees a
300-year bin silently standing in for the window they care about. It's the same defect *class* as
centroid-HYDE, on the temporal axis: the paint asserts a resolution the displayed value doesn't
have.

Unlike HYDE, this is **not** a performance rescue — the LMR grid is small (2°×2°, thousands of
cells at most). It's a fidelity fix. The annual arrays in `temporal.lmr_climate` let the paint
reflect a genuine [from, to] span.

## Target quantity — and two things to confirm, not assume

Per cell, the value is the **mean anomaly over the requested [from_year, to_year]** from the annual
series. Two points to establish and report, because they define what the paint honestly claims:

1. **Anomaly baseline.** Are the stored annual values already anomalies against the 850–1850 model
   climatology, or does the route compute the anomaly? The mandatory caveat (anomaly vs 850–1850
   mean; spatial structure reflects the reanalysis prior, not raw past climate) must remain exactly
   true of whatever the route returns. Confirm where the anomaly is taken and that the baseline is
   unchanged.
2. **"Weighted" mean or arithmetic mean?** F15.9 wrote "per-cell weighted means." Confirm whether
   any weighting actually applies (ensemble weighting in the reanalysis, uneven annual coverage) or
   whether it's the arithmetic mean over the span's annual values. Use whichever is correct for the
   data; report which and why.

## Route (goal-setting, not spec)

`/api/lmr/values?var=air|prate&from_year=N&to_year=N` → `{var, from_year, to_year, values:
{cell_id: mean_anomaly}}`, shape parallel to `/api/hyde/values`. Finalize the schema and the
`cell_id` key in implementation.

- **Quality floor: 700 CE** (F15.1 — the first ~700 years of the record are excluded for quality).
  Below-floor cells/years paint nothing: **absent/null → transparent, never coerced to zero** (zero
  is a value, not an absence marker). Handle a span that *straddles* the floor honestly — mean over
  the in-range years, or null if the whole span is below floor — and report the rule you chose.

## Frontend rewire

- Retire the notch path (`air_0`–`air_4` property paint, `lmrNotchForYear`) **and** the hidden
  paint-year slider (`#v2-lmr-year-slider`, F15.2). Both are superseded.
- Paint from the route. **Establish the join key** between the LMR grid geometry and the route's
  per-cell values — this is the crux, same as HYDE's `hybas_id` join. Two viable approaches; your
  call given the grid is small and static, report which and the key used:
  - feature-state from `{cell_id: value}` keyed to the grid geometry (consistent with basin/HYDE);
  - or data-driven property paint, rebuilding the static grid source with the span values baked in.
- **Diverging ramp centred on zero** and the anomaly-framed legend (F15.3) carry forward unchanged —
  the value is now a real span mean, so the framing is *more* accurate than under notches, not less.

## The one design decision for Karl — coupled vs decoupled span

LMR paint is inherently span-based; Band T is inherently a span the user already sets. Two ways to
drive the paint:

- **(a) Couple** — paint tracks the Band T span (and the slice from/to on polity scope). Simplest;
  unifies the signature's window and the paint's window; structurally cannot drift out of sync; and
  it eliminates the two-times-on-screen confusion that got the WO15 slider hidden in the first place.
- **(b) Decouple** — a separate paint-span control, so the signature can be held at one window while
  the paint scrubs a *different* climate window ("fixed signature, evolving climate" comparison).

This reverses the decoupling I argued in WO15 — but that argument assumed a single paint *instant*;
the honest data model is span-based, and Band-T-as-span makes coupling a match, not a collapse. **My
lean: couple as the default.** For the default case coupling is both simpler and more honest — the
paint shows "the anomaly field over the window your signature covers," a claim that can't desync. The
decoupled comparison is a real *analyst* affordance, but by your own meaningful-boundaries / no-one-
reads philosophy it's a drawer item — summoned explicitly when wanted, not the default that
reintroduces two clocks. So: couple now; a decoupled paint-span control is a later, explicitly-added
affordance if the comparison use-case earns it. Your call.

Note either way: **F16.10's slice-reactive repaint passes a single year (`s.fromyear`) to the LMR
branch — that must change to pass a span** (slice from/to) so the route returns a span mean, not a
one-year read.

## Performance — a check, not a gate; and don't misapply the HYDE pattern

LMR's grid is small, so the live span-mean query should be fast. Time it and report. **But if it's
slow, the HYDE fix does not transfer:** HYDE pre-aggregated 128 *enumerable* steps into a table;
LMR spans are continuous [from, to] and are **not enumerable**, so you cannot pre-aggregate by span.
If slow, optimize the query (array-slice/mean structure, indexing), don't reach for a steps table.
Stating this so the pattern you just learned isn't reflexively applied where it can't fit.

## Caveat text

Anomaly framing carries forward from WO15 (F15.3, currently hard-coded matching the payload). If the
new route can carry/return the caveat field, prefer sourcing it from the payload (the WO15 deferred
wiring); hard-coded match remains an acceptable fallback. Report which.

## Not in this WO

- HYDE (closed, WO18); basin choropleth; scope geometry paths.
- L8 — L6/native-grid only as applicable.
- The decoupled paint-span control, unless Karl calls for it above.
- Native-resolution / alternate-grid artifacts.

## Accept gate

- `/api/lmr/values` returns per-cell span-mean anomalies for a [from, to]; floor handled (below-floor
  → absent/null, never zero; straddle rule reported); anomaly baseline confirmed unchanged.
- LMR paint uses the route, not the notches; hidden slider and notch path retired.
- Paint reflects the active span per Karl's coupled/decoupled decision; slice-repaint passes a span
  for LMR, not a single year.
- Diverging ramp centred on zero preserved; anomaly-framed legend intact.
- Per-request time reported.
- basin/HYDE paths and `sandbox.html` untouched.

## Tests

- Route: shape; floor handling incl. the straddle case; span-mean correctness against a hand-checkable
  cell over a short span (assert it matches a manual mean of the annual values).
- Frontend: match the F15.10 honesty — write the LMR-paint UI coverage; if the choropleth Playwright
  suite is still skip-pending-state-model, skip under the same trigger rather than leave LMR uncovered
  silently. Note status.
- Engine/app suite green — zero FAILs, zero unexplained warnings. Note counts.

## Findings

`docs/edop/surface/wo19_findings.md`. Report: anomaly baseline (stored vs computed) and weighting
(arithmetic vs weighted) with rationale; the join key + paint approach chosen; the floor straddle
rule; per-request time; coupled-vs-decoupled as implemented per Karl; caveat source (payload field
vs matched hard-code); confirmation no below-floor value was coerced to zero.
