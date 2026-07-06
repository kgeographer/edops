# WO15 — LMR paleoclimate anomaly paint + the paint-year control

**Branch:** `surf_wo15` → merge to `surface` at accept gate.
**Type:** Build — first gridded/time-indexed layer. Static-vector paint (LMR) + a new paint-year
control. HYDE raster overlay is WO16 and inherits the year control built here.

## Goal

Bring the two LMR variables live in the basin-variable selector — temperature anomaly,
precipitation anomaly — painted from `lmr_notches.geojson`, with a **paint-year control** that
scrubs the anomaly field across time, and the anomaly framing carried in the legend. cliopatria's
LMR handling is the reference; port what ports, adapt what doesn't, report which.

Splitting LMR (this WO) from HYDE (WO16) keeps one new rendering mechanism per increment. The new
thing in WO15 is the **year control** — built against LMR because LMR is vector paint, close to
the basin choropleth mechanism already proven in WO14. WO16 then inherits a working year control
and introduces only the raster path.

## The two "times" on this page — keep them decoupled

There are two independent temporal concepts here, and conflating them would be a quiet semantic
collapse that reads fine and means nothing:

- **Band T span** (`from_year`/`to_year`, e.g. 1000–1100) — the interval the *signature*
  aggregates over. Drives the signature accordions. Unchanged by this WO.
- **Paint year** — a *single instant* the choropleth colours. New in this WO. Drags year by year;
  moves the LMR anomaly field independent of Band T.

The paint year is its own control, **decoupled from Band T**. Do not derive it from the Band T
span (no "paint the midpoint"). A user can hold Band T at 1000–1100 for the signature while
scrubbing the paint year across the LMR record. Report where you place the control and how you
keep it visually distinct from the Band T from/to inputs so the two aren't confused.

## Scope this WO

- **LMR temperature anomaly** and **LMR precipitation anomaly** — enable the two disabled LMR
  entries in the selector.
- **Paint-year control** — single-year selection over the LMR temporal domain. Scrubbing repaints
  the LMR field for the selected year. Form (slider, stepper, dropdown) is CC's call given the
  LMR record's resolution and extent — report the domain (year range + step) and the control form
  chosen.
- **Anomaly framing in the legend** — LMR values are anomalies against the 850–1850 model
  climatology, and the spatial structure reflects the reanalysis prior, not raw past climate. On a
  painted map this framing must live *in the encoding*, not in prose no one reads: the legend/label
  states it (e.g. "Temperature anomaly (°C vs 850–1850 mean)"). See the caveat-field note below for
  where the text comes from.

## Caveat text — from the signature payload, not hand-written

The caveat is a field on the signature payload (established last session). Prefer sourcing the LMR
framing text from that field rather than hard-coding a string in the legend, so it stays bound to
the variable at the source. If the caveat field isn't readily reachable from the choropleth code
path (the paint is scope-independent and may not have a signature in hand), report that — a
hard-coded legend string is an acceptable WO15 fallback *if* it matches the payload's caveat text
verbatim, with a note that WO16/later wires it to the field. Don't invent framing language;
mirror the payload's.

## Rendering — port cliopatria's LMR path

`lmr_notches.geojson` is a static vector file. Load it as a shell-managed source and paint its
features by the selected variable at the selected paint year. Port cliopatria's approach:

- How cliopatria structures per-year values in the notches GeoJSON (a property per year? a
  separate fetch keyed by year? a value array indexed by year?) — read it and report; it
  determines how the year control drives the repaint.
- Colour ramp: anomaly data is diverging around zero — confirm cliopatria's ramp centres on zero
  (a diverging ramp with 0 at the neutral midpoint, not a p10–p90 stretch that would hide the
  sign). Report the ramp and domain; anomaly sign legibility (warm vs cool, wet vs dry relative to
  baseline) is the point.
- Layer ordering: LMR paint sits in the same z-order slot as the basin choropleth — below scope
  geometry (polity boundary etc.), using the `before`-insertion the shell gained in WO14 (F14.1).
- Selecting an LMR variable while a basin variable is active: the two are mutually exclusive paints
  on one selector, so selecting LMR clears the basin feature-state (and vice versa). Confirm the
  WO14 `removeFeatureState` clear path handles the basin→LMR switch, and that LMR→basin clears the
  LMR layer. No two paints stacked.

## Concurrency note (carry from F14.2 / F13.6)

WO14 hit tile-fetch contention (F14.2, the 20 s timeouts) and the ring has accumulating listeners
(F13.6). LMR adds a static GeoJSON load and a year control that repaints on every scrub. Watch
that rapid year-scrubbing doesn't spawn overlapping fetches/repaints (debounce or guard if the
repaint is non-trivial), and that the year-control listener doesn't accumulate across variable
switches the way F13.6's ring listeners do. Not a predicted-future concern — it's the same seam
that already bit once, met again here.

## Deliberately not in this WO

- HYDE raster overlay — WO16 (inherits this year control).
- Any change to Band T semantics or the signature path.
- L8 — L6 only.
- Wiring the caveat field end-to-end if it's not reachable from the choropleth path — fallback
  above, full wiring later.

## Accept gate

- Both LMR variables paint from `lmr_notches.geojson`, diverging ramp centred on zero, legend
  stating the anomaly framing.
- Paint-year control scrubs the LMR field year by year, **independent of Band T** (Band T
  unchanged by year scrubbing; year unchanged by Band T edits).
- Switching between basin and LMR variables clears the prior paint cleanly — no stacked paints.
- LMR paint sits below scope geometry.
- Rapid year-scrubbing doesn't spawn overlapping repaints or accumulate listeners.
- Basin choropleth (WO14), scope geometry paths, and `sandbox.html` untouched; HYDE entries stay
  inert-present.

## Tests

- Playwright: LMR variables selectable and paint; year control present, scrubbing triggers
  repaint; basin↔LMR switch clears prior paint (no console errors); legend shows anomaly framing;
  Band T inputs unchanged by year scrubbing.
- If the LMR per-year values come via a route, a route-level shape test; if from the static file,
  assert the file's structure the paint depends on (report which).
- Full suite green — zero FAILs, zero unexplained warnings. Note the new count; correct CLAUDE.md's
  surface count if stale (it's needed correcting twice now — F13.8, F14.8).

## Constraints

- Review before write — Karl signs off each write.
- Shell API only for the LMR source; keep the WO8/WO14 shell contract intact.
- Reuse cliopatria's LMR assets/routes read-only; don't modify shared Explorer paths.
- `sandbox.html` untouched.

## Findings

`docs/edop/surface/wo15_findings.md`. Report: the LMR per-year data structure and how the year
control drives repaint; the year domain + control form chosen; the ramp/domain and zero-centring;
where the caveat text came from (payload field vs matched fallback); paint-year control placement
and how it's kept distinct from Band T; the concurrency handling for scrub repaints; how much was
direct port vs. adapted.
