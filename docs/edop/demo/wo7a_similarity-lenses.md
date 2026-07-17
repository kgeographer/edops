# WO7a — Similarity lens registry + Climate sub-lenses

**Branch:** `demo_wo7a` off `demo`
**Track:** 2 (Features) + 3 (Sandbox UI)
**Depends on:** WO7 Parts A/B — similarity endpoint delivering ranked similar basins for the
seasonal-phase metric; Similarity tab scaffold with map + distance coloring live.

---

## Goal

Generalize the similarity feature from a single hardwired metric into an extensible **lens
registry**, and prove the abstraction by populating a **Climate** lens group with three
thematically coherent sub-lenses, each with its own declared variable set and distance metric.

This is a plumbing-and-architecture increment. The existing seasonal-phase metric becomes one
entry in the registry, not a special case. The registry must support per-lens metric choice
(Euclidean vs. Mahalanobis) because different sub-lenses have different variable structures.

Result set stays **bounded** for this WO (existing top-N or a fixed threshold — see Part D).
Honest variable-N / threshold rendering and its performance implications are deferred to WO7b.

---

## Design principles (locked from prior discussion)

- **A lens is a declared claim.** Each sub-lens = a label + a variable set + a metric. The
  label must honestly describe what the metric measures. No lens promises more breadth than
  its variables deliver.
- **Metric follows variable structure.** Few, near-independent variables → normalized
  Euclidean. Several correlated variables → Mahalanobis (accounts for redundancy so
  overlapping variables don't silently gain weight). Per-lens choice, declared in the registry.
- **Climate lenses are strictly atmospheric.** Precipitation, aridity, temperature — what the
  sky delivers and how hot it is. Surface-water (discharge, runoff, river) belongs to a future
  Hydrology lens group, NOT here. Do not build a blended "water availability" lens that merges
  precip and discharge — that would merge two physically distinct water sources into one
  dishonest number. (Timbuktu is the motivating case: atmospherically Sahelian, hydrologically
  exotic-river-fed; those are two different similarity questions and must stay separate.)
- **Circular variables stay out of the distance metrics.** `pre_peak_month` / `tmp_peak_month`
  are angles (Dec and Jan are adjacent), so raw values break Euclidean/Mahalanobis. Leave them
  out of the distance computation for this WO; they remain descriptive fields. The notebook
  confirms they aren't needed for discrimination.

---

## Part A — Notebook: settle sub-lens membership + metric

**Notebook:** `notebooks/edop/demo/wo7a_climate_lenses.ipynb`

Three proposed Climate sub-lenses. For each, the notebook confirms the variable set and the
metric choice against known cases. **Variable membership is a notebook question — the lists
below are candidate intents, not locked specs.**

### Sub-lens 1 — Precipitation regime (the moisture-from-sky story)

Candidate variables: `precip_yr` (annual precip), `aridity`, `pre_concentration`.
- Compute pairwise correlations across all 16k L06 basins. Expectation: precip and aridity
  correlate (wet places are less arid) → Mahalanobis warranted. Confirm.
- Note the precip/aridity redundancy explicitly — this is the textbook case for Mahalanobis
  down-weighting overlapping information.
- Validation: query from Rome (Mediterranean) and Timbuktu (Sahel). Rome should recover
  Mediterranean rainfall regimes; Timbuktu should recover Sahel / dry-monsoon-margin basins.

### Sub-lens 2 — Temperature regime (the thermal story)

Candidate variables: `temp_yr` (annual mean temp), `tmp_seas_amp`, `tmp_concentration`.
- Compute pairwise correlations. Expectation: continental places are both colder and more
  variable → some correlation → Mahalanobis likely warranted. Confirm.
- Validation: query from a continental interior (e.g. Tbilisi) and a maritime location
  (e.g. London). Continental query should recover high-amplitude interiors; maritime should
  recover equable coastal/oceanic basins.

### Sub-lens 3 — Seasonal phase (the wet/warm vs. wet/cool axis)

Variables: `pre_concentration`, `seas_phase_offset` — the existing WO7 metric.
- Two near-independent indices → normalized Euclidean (confirm |r| < ~0.3 across basins).
- This is the focused view: kept as-is, re-homed into the registry as one sub-lens entry.
- Validation: unchanged from WO7 — SF recovers the Mediterranean cluster.

### A-summary deliverable

For each sub-lens, report: final variable set, measured correlation structure, chosen metric
(with the correlation evidence justifying the choice), and validation result against the named
cases. Flag any candidate variable that underperforms or should be dropped.

---

## Part B — Lens registry (backend)

Refactor the similarity computation so a lens is a declared, data-driven object rather than
hardwired logic. Registry entry shape (provisional — CC adjusts to fit the codebase):

```python
LENS_REGISTRY = {
    "climate.precip": {
        "group": "Climate",
        "label": "Precipitation regime",
        "variables": [...],        # settled in Part A
        "metric": "mahalanobis",   # per-lens
        "status": "active",
    },
    "climate.temp":  { "group": "Climate", "label": "Temperature regime",
                       "variables": [...], "metric": "mahalanobis", "status": "active" },
    "climate.phase": { "group": "Climate", "label": "Seasonal phase",
                       "variables": ["pre_concentration", "seas_phase_offset"],
                       "metric": "euclidean", "status": "active" },
    # future groups stubbed disabled:
    "terrain.*":     { "group": "Terrain",   "status": "disabled" },
    "water.*":       { "group": "Hydrology", "status": "disabled" },
}
```

Requirements:
- **Per-lens metric dispatch.** The distance computation reads the lens's `metric` field and
  applies Euclidean-on-z or Mahalanobis accordingly. Covariance for Mahalanobis is estimated
  from the full basin population per lens (trivial at 16k; confirm no perf issue).
- **Variable resolution.** The lens's variable list keys into the per-basin values already
  available (top-level `out` for seasonality scalars; existing band fields for precip/aridity/
  temp). Confirm all named variables are fetchable for all basins; handle NoData as
  NULL/NaN — never coerce to zero (locked principle; a zero-coerced aridity would corrupt the
  distance).
- **Endpoint takes a lens ID:**
  ```
  GET /api/similarity?lat=...&lon=...&lens=climate.precip&n=...
  ```
  Returns query basin's own values for the lens variables in each result (so the UI can show
  why a place matched), plus distance and rank.

---

## Part C — Two-dropdown UI

Replace the single "Lens: Seasonality" dropdown with **two side-by-side selects**:

- **Left (lens group):** Climate active; Terrain, Hydrology present but disabled/greyed.
- **Right (sub-lens):** populated from the selected group's active sub-lenses. For Climate:
  Precipitation regime, Temperature regime, Seasonal phase.

Behavior:
- Changing the group repopulates the sub-lens dropdown and selects that group's default
  sub-lens.
- Changing the sub-lens re-queries the endpoint with the new lens ID and repaints the map.
- The current anchor location persists across sub-lens changes (switching sub-lens for the
  *same* location is the core research gesture — "how does the similar-set change when I ask a
  different question about this place").
- Caption/blurb below the map updates per sub-lens, describing what that lens measures and
  reporting the result count.

Anchor-source contract (settle in build): the query anchor is the last-selected location and
survives tab and sub-lens switches. Empty state before any location: "Select a location to
compare."

---

## Part D — Result set bound (interim)

Keep the result set **bounded** for this WO — do NOT implement honest variable-N threshold
rendering here (that's WO7b, bundled with its performance question). Use either the existing
top-N or a single fixed SD-radius threshold, whichever is already working. The point of WO7a
is proving the registry + dropdowns + three lenses, not the threshold epistemics.

**Optional performance probe** (informational, non-blocking): paint the largest result a
bounded query produces for a diffuse case (e.g. Temperature-regime from a common thermal
regime) and note Leaflet/GeoJSON render time. This informs the WO7b decision on whether
Leaflet survives the variable-N rendering or a different approach is needed. Record the number;
don't act on it in this WO.

---

## Acceptance

- Notebook (Part A) reports settled variable set + justified metric for all three Climate
  sub-lenses, with validation against named cases passing.
- Registry drives the endpoint: same code path serves all three lenses; adding a lens is a
  registry entry, not new distance logic.
- Two dropdowns render; Climate group active with three sub-lenses; Terrain/Hydrology greyed.
- Switching sub-lens for a fixed location re-queries and repaints without losing the anchor.
- Precipitation-regime query from Rome recovers Mediterranean rainfall basins; Temperature-
  regime query from a continental location recovers high-amplitude interiors; Seasonal-phase
  query from SF recovers the Mediterranean cluster (unchanged from WO7).
- NoData handled as NaN in all metrics; no zero-coercion.
- All existing tests pass; contract tests added for at least one Mahalanobis lens and the
  existing Euclidean lens.

---

## Out of scope for WO7a (→ WO7b and later)

- Honest variable-N / distance-threshold result sets and the strict/moderate/loose stringency
  control — WO7b.
- Rendering-performance resolution (Leaflet vs. alternative for ~1000+ basins) — WO7b, informed
  by the Part D probe.
- Terrain, Hydrology, Vegetation lens groups and their metrics — future WOs, each with its own
  notebook investigation.
- Any UI presentation of the precip-vs-hydrology split for exotic-river cases like Timbuktu —
  noted as a future presentation concern; not built here.
- Circular peak-month variables in distance metrics — excluded by design.

