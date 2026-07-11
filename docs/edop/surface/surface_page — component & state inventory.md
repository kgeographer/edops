# Surface page — component & state inventory

**Purpose:** the logical spec for the new sandbox page — every control, its visibility rule
(which scope shows it), the endpoint it executes, and the payload it targets. This is the
"data-contract half" of the wireframe; visual layout/proportion is Karl's authoring pass on
top of it. Two spots explicitly flagged as needing visual judgment: the conditional temporal
controls and the Signature-tab per-method leaf layout.

**Reference:** current sandbox layout (header + 1/3 left column + 2/3 right column with
Map/Signature/Analysis tabs). The skeleton is retained; what changes is noted per component.

**Status:** draft for review. Endpoint-wiring for the three unwired point-rooted paths is a
prerequisite WO, not yet cut.

---

## Scope model (settled)

Five scopes, four payload shapes. The arbitrary-polygon scope has three input methods.

| # | Scope | Resolver | Endpoint | Payload shape | Input obtained via |
|---|---|---|---|---|---|
| 1 | Single basin | `resolve_single_basin` | `single_basin_signature` **(unwired)** | `{rows[], neighborhood}` | point (WHG / lat,lon) |
| 2 | Buffer | `resolve_buffer` | `areal_signature` **(unwired)** | `{rows[], neighborhood}` | point + radius_km |
| 3 | Basin ring | `resolve_basin_ring` | `basin_ring_signature` **(unwired)** | **`{center, ring[]}`** ← exception | point |
| 4 | Polity | `resolve_polity` | `GET /api/area` **(wired, WO22)** | `{rows[], neighborhood}` | polity name + year |
| 5 | Arbitrary polygon | `resolve_polygon` | `areal_signature_polygon` **(unwired as HTTP)** | `{rows[], neighborhood}` | draw-rect \| draw-freehand \| upload GeoJSON |

Prerequisite WO (not cut yet): wire the point-rooted trio (single-basin, buffer, ring) plus a
polygon-accepting route for scope 5. Polity (4) is done.

---

## Left column — inputs (top to bottom)

| Component | Visibility | Executes / feeds | State it holds | New/existing | Notes |
|---|---|---|---|---|---|
| WHG name lookup + Resolve | scopes 1,2,3 (point-rooted) | WHG reconcile API → candidate list → lat/lon | resolved point; candidate list | existing | Unchanged getter. Map-bounds constraint on search stays. |
| Examples dropdown | always | client presets → sets scope + inputs | selected preset | existing | Extend presets: add a polity example and a drawn-area example. |
| **Scope selector** | always | routes Get-signature dispatch | current scope (1–5) | **NEW — the spine** | A mode switch. Drives which inputs below are visible and which endpoint fires. |
| Polity name field + period | scope 4 | `/api/polity/search` (typeahead) then `/api/area` | polity name; resolver_year | **NEW** | Name resolves to available periods; period picker sets `resolver_year`. |
| Radius input | scope 2 | param on buffer endpoint | radius_km | **NEW** | Numeric, km. |
| Draw / upload control | scope 5 | map draw tools OR file input → WKT/GeoJSON | the polygon geometry | **NEW** | Three input methods, one scope. Draw modes live on the Map tab; upload is a file input here. |
| Level dropdown | always | param on all endpoints | level (frozen L6) | existing, **frozen** | Greyed at L6. Kept visible so the axis isn't forgotten; L8 later. |
| Band checkboxes (A–E, T) | always | `bands` param | selected bands | existing | Unchanged. |
| **Temporal controls** | conditional (see below) | `from_year`/`to_year` and/or `resolver_year` | the two temporal axes | **NEW** | ⚠ visual-judgment spot #1. Detailed below. |
| Get signature button | always | dispatches per scope to the right endpoint | — | existing button, **new dispatch** | One button, five possible targets. |
| Summary-on-load panel | after a signature loads | (renders from payload) | n_units, shortfall/coverage, marginal_exposure, resolved polity+period | replaces instructions | "What you queried" readout. Scope-level metadata that isn't per-variable. |

### Temporal controls — the two-axis problem (visual-judgment spot #1)

Two independent axes, shown conditionally by scope. Collapsing them into one control
reintroduces the confounding the histogram temporal-stamp was built to prevent.

| Axis | Param | Meaning | Shown when |
|---|---|---|---|
| Resolver year | `resolver_year` | which year's polity boundary to resolve | scope 4 (polity) only — the only scope with a moving boundary |
| Band T span | `from_year` / `to_year` | HYDE/LMR aggregation window | any scope, only when **T** band is ticked |

So: non-polity scope with T ticked → span control only. Polity scope with T ticked → both
(boundary-year picker AND span). Polity scope without T → boundary-year picker only (the
boundary still needs a year even if Band T isn't aggregated). The two must remain visually
distinct; the histogram caption echoes both to keep them legible downstream. **This is the
layout/affordance problem most worth a wireframe** — conditional appearance + clear
separation of two year-inputs that look superficially alike.

---

## Right column — Map tab

| Aspect | Behavior | New/existing |
|---|---|---|
| Base display | hillshade + OSM (Leaflet) | existing |
| Point preview | containing basin (orange) + adjacent ring choropleth by up_area + rivers | existing (img 2) — note ring is *already drawn*; scope 3 finally surfaces its values |
| Bounds → search constraint | zoom constrains WHG name search | existing |
| **Draw rectangle** | scope 5 input method → polygon WKT | **NEW** — map becomes bidirectional |
| **Draw freehand polygon** | scope 5 input method → polygon WKT | **NEW** |
| **Polity boundary overlay** | scope 4 → GeoJSON from `/api/polity/geom` | **NEW** |

Map library stays Leaflet (SF.1 decision): boundary overlay + basin preview need no PMTiles
choropleth. The map gains an input role (draw capture) it didn't have; no structural change,
just bidirectional.

---

## Right column — Signature tab (visual-judgment spot #2)

The accordion *container* (band grouping) survives. The *leaf renderer* is new: per-`method`
dispatch replaces flat `{label, value}` pairs, because the engine's quality metadata
(coherence, modality, coverage, weight_at_zero, histogram) is the new product and a flat value
discards it.

### Header row (retained, extended)
- Title: scope-appropriate ("Timbuktu (Level 06)" for basin; "Northern Song · 1000 CE · N basins" for polity)
- JSON / API links (existing) — download payload + show the API call. Keep; the "show API call"
  serves the API-caller audience and the future "build a call from the UI" idea.

### Per-method leaf renderers

| `method` | Bands | Renders | Detail (`&detail=true`) adds |
|---|---|---|---|
| `area_weighted` | B1 | score + coherence badge (concentrated/spread) | histogram widget; p10/p90/spread |
| `dominant_basin` | B2 | score + raw + which basin carried it | — |
| `class_mixture` | B3/B4 | modal class label + mixture bar | full mixture breakdown |
| `flag_fraction` | B4 | scalar fraction (e.g. coast %) | — |
| `distribution_only` | B5 fallback | mean percentile + spread | histogram widget |
| `extreme` | B5 | carrier-basin score | — |
| `grid_areal_distribution` | T (HYDE/LMR) | per-year series (needs collation) | per-cell histogram per year |
| `global_forcing` | T (eVolv2k) | per-event rows (volcano table) | — |

⚠ **visual-judgment spot #2:** the leaf layout — how a row shows value + coherence badge +
optional histogram without becoming noisy across ~50 variables. This is dense; proportion and
restraint matter. A wireframe of one representative row per method type would settle it.

### Band T sub-panel (retained target, inverted data path)
Keep the current 3-sub-tab design (LMR infovis / HYDE infovis / volcano table) as the output
shape. But the input stage changes: v0.3 handed a pre-assembled `{pdsi_series, …}` blob; the
engine hands one row per year per variable and does **not** pre-collapse. So the page must
collate `rows[]` by variable → year into series before charting.
- HYDE/LMR (`grid_areal_distribution`): collate per-year → time series → existing SVG charts.
- eVolv2k (`global_forcing`): per-event → volcano table.
The charts downstream are reusable; the collation is the new work.

### Histogram widget (new, reusable)
- Input: `detail['distribution']` — `bins` (21 edges) + `weights` (20) → SVG histogram.
- Weighted bars (weights, not counts). Two x-axis modes: percentile (basin-path) and
  native-unit (Band T).
- Caption carries the temporal stamp: `resolver_year`, `band_t_from`, `band_t_to` — the
  two-axis guard made visible.

---

## Right column — Analysis tab

Auto-interpretation from signature values (the "interpretation lives at the surface" principle
made concrete). Existing content stays; new scope-aware content added.

| Content | Source | Scope | New/existing |
|---|---|---|---|
| Basin context (upstream area, dist-to-outlet, drainage type) | single-basin fields | scope 1 (and center of scope 3) | existing (img 4) |
| s/u divergence table + water-provenance verdict | s/u fields | scope 1 only (no single s/u pair for areas) | existing; **now scope-gated** |
| **Marginal exposure / shortfall caveat** | `marginal_exposure`, `shortfall` | scopes 4,5 (arbitrary/given boundaries) | **NEW** — "result rests X% on basins mostly outside the boundary" |
| **Coherence / distribution story** | coherence + histogram stats | scopes 2–5 | **NEW** — plain-language "aridity is spread across this area (p10–p90 spans 49 pts)" |
| **Analyst-drawer caveat** | scope flag | scope 5 (arbitrary polygon) | **NEW** — arbitrary boundaries can clip extreme-valued edge units silently |

Analysis must know which scope produced the payload and show scope-appropriate interpretation.
That scope branch is real work, not a freebie: single-basin interpretation (s/u divergence)
and area interpretation (coherence, marginal exposure) are different stories.

---

## Basin-ring rendering — the payload exception

Scope 3 returns `{center, ring[]}`, not `{rows[], neighborhood}`. It needs its own path:
- **Signature tab:** center signature rendered as scope-1 would; each ring member rendered as a
  compact comparison against center. No aggregate "ring score" — the point is per-neighbour
  comparison (bearings, shared-border km).
- **Map tab:** already draws the ring (img 2); now the ring members are selectable/hoverable to
  surface their signatures — closing the gap SF.1 named (map implies neighbours, values were
  never delivered).
- **Analysis tab:** center gets standard single-basin interpretation; ring divergence (how each
  neighbour differs from center) is a candidate interpretive output, deferable to v2.

This is the one scope that genuinely doesn't fit the shared renderer. Worth deciding whether it
ships in the first page or is a fast-follow, since it roughly doubles the Signature-tab render
paths.

---

## Prerequisite & sequencing

1. **Endpoint-wiring WO** (prerequisite): wire single-basin, buffer, ring (the three unwired
   point-rooted paths) + a polygon-accepting HTTP route for scope 5. Polity done (WO22).
2. **This inventory → Karl's wireframe pass** on the two flagged spots (temporal controls;
   Signature leaf layout).
3. **Page build**, likely staged: shared `{rows[]}` renderer + map + Analysis first (covers
   scopes 1,2,4,5); basin-ring path (scope 3) as a defined second stage given its exceptional
   shape.

---

## Open questions for Karl

- **Ring in v1 or fast-follow?** It doubles Signature render paths and has no shared-renderer
  reuse. Shipping scopes 1/2/4/5 first (one renderer) then ring may be the cleaner staging.
- **Draw tooling:** hand-rolled Leaflet rectangle, or pull in Leaflet.draw for freehand? Freehand
  polygon is heavier; rectangle alone may suffice for a first proving-ground.
- **"Show API call" build-a-request:** the inventory keeps the existing JSON/API links. Whether
  the page becomes an API-call *builder* (the TBD dashboard idea) is out of scope here but the
  scope-selector state is exactly what such a builder would serialize — worth keeping that state
  clean for later reuse.