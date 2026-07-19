# WO7b — Honest similarity neighborhoods: distance threshold + rendering

**Branch:** `demo_wo7b` off `demo`
**Track:** 2 (Features) + 3 (Sandbox UI)
**Depends on:** WO7a — lens registry live; three Climate sub-lenses (two Euclidean, one
Mahalanobis); Similarity tab with map + distance coloring; fixed top-200 result set.

---

## Goal

Replace the fixed top-N result set with an **honest, distance-thresholded neighborhood** whose
size varies by how common the query basin's climate type is. The varying count *is the
finding*: a tight Mediterranean cluster and a sprawling monsoon belt should look different in
extent, because they are different. Resolve the rendering-performance question this raises
(potentially 1000+ basins painted), since a common-type query is the stress case.

This is the increment that turns the Similarity tab into a source of **hero shots** — the
visual contrast between a rare, tightly-clustered pattern and a common, globally-diffuse one
is the demonstrator. Fixed-N suppresses exactly that contrast; the threshold reveals it.

---

## Design principles (carried from prior discussion)

- **The count is signal, not noise.** "SF's Mediterranean pattern is shared by ~60 basins in
  five tight pockets; Tbilisi's weak-seasonal pattern by ~1,500 scattered across three
  continents" is a substantive result about climate-type prevalence. Let N vary; report it.
- **Threshold is a declared analytical parameter.** Expose it as a coarse stringency control
  (strict / moderate / loose), not a frozen hidden constant. The user should see that
  "similar" is a choice.
- **Threshold is a distance radius, calibrated empirically per lens — not derived from a
  normality assumption.** The indices are bounded and non-normal (`pre_concentration` skewed,
  `seas_phase_offset` bimodal), so chi-square probability mappings are heuristics only. Do not
  sell a radius as a confidence level. Calibrate against known cases (SF-as-known-answer) and
  confirm behavior generalizes.
- **Per-lens calibration is required, not a single global radius.** A Euclidean-on-z lens (2
  vars) and a Mahalanobis lens (3 vars) enclose different fractions of basins at the same
  numeric radius — different dimensionality and covariance. Each lens carries its own
  strict/moderate/loose radii in the registry.

---

## Part A — Performance probe first (blocking gate)

WO7a Part D left the rendering-cost number unmeasured. Establish it before building the
threshold, because it determines the rendering approach.

**Notebook or quick harness:** `notebooks/edop/demo/wo7b_perf_probe.ipynb` (or inline).

- For each of the three Climate lenses, find the query location that produces the *largest*
  plausible thresholded neighborhood (a common climate type — Timbuktu-monsoon or a common
  temperate regime). Report the basin count at a "loose" radius.
- Paint that worst-case set in the current Leaflet/GeoJSON setup. Measure: initial render
  time, pan/zoom responsiveness, memory. Record actual numbers.

**Decision from the probe** (record in findings, then proceed):
- If current SVG-path GeoJSON handles the worst case acceptably → keep it; proceed to Part B.
- If it stutters → apply the cheapest sufficient fix, in this order:
  1. **Canvas renderer** — Leaflet `preferCanvas: true` / `L.canvas()`. Usually the single
     biggest win for many polygons; low effort.
  2. **Geometry simplification** — serve simplified basin outlines for the similarity map
     (`ST_SimplifyPreserveTopology` at a tolerance suited to world-map zoom, or a pre-built
     simplified geometry column). The similarity map doesn't need full-resolution basin edges.
  3. Only if 1+2 are insufficient: reconsider the delivery format (vector tiles). Flag for
     discussion rather than building — this would be a larger detour.

Do not over-engineer. The probe may well show Canvas alone suffices. Pick the least change
that makes the worst case smooth.

---

## Part B — Threshold calibration (notebook)

**Notebook:** `notebooks/edop/demo/wo7b_threshold.ipynb`

For each of the three Climate lenses, establish strict / moderate / loose distance radii.

### B1 — Distance distributions against known cases

For each lens, pick the validated anchor(s) from WO7a (SF for phase, Rome/Timbuktu for
precip, Tbilisi/London for temp). Compute sorted distance-to-anchor across all 16k basins.
Plot the CDFs together per lens.

- Look for the elbow: the distance beyond which results shade from "same regime" into
  "different regime." Rare types (Mediterranean) should show a tight cluster then a gap;
  common types (monsoon, temperate) a gentler slope with no clean gap — that difference is
  expected and is itself the finding.

### B2 — Set the three radii per lens

For each lens, choose:
- **strict** — the radius that returns the tight known cluster and little else (calibrate on
  the *rare*-type anchor, where you can eyeball correctness: SF should return the Mediterranean
  pocket, ~tens of basins).
- **moderate** — the default; a sensible working neighborhood.
- **loose** — inclusive; where the common-type query blooms to its full extent.

Report, per lens, the three radii and the resulting counts for each validation anchor. Sanity
check: strict on a rare type returns a small tight set; loose on a common type returns a large
diffuse set; the same radius returns very different counts across anchors *within a lens*
(that's correct).

### B3 — Cross-lens note

Confirm the radii differ across lenses (2-var Euclidean vs 3-var Mahalanobis will not share
scale). Record each lens's radii in the registry spec. No attempt to make radii comparable
*across* lenses — they answer different questions.

---

## Part C — Backend: threshold query

Extend the similarity endpoint to support threshold mode:

```
GET /api/similarity?lat&lon&lens&mode=threshold&stringency=moderate
```

- `stringency` ∈ {strict, moderate, loose} → resolves to the lens's calibrated radius from
  the registry.
- Returns *all* basins within the radius (variable count), ranked by distance, each with lens
  values as before.
- Response includes `result_count` and the resolved `radius` in `query_meta` so the UI can
  report "N basins within threshold."
- Keep `mode=topn&n=...` supported as a fallback / comparison path (useful for the perf probe
  and for A/B looking).
- **NaN-masked basins** (the 59 hyper-arid on phase/concentration, plus any lens-specific
  nulls) are excluded from results, never treated as distance-0 or distance-∞ silently.
  Confirm the mask propagates per lens.

Registry addition per active lens:
```python
"thresholds": {"strict": <r>, "moderate": <r>, "loose": <r>}
```

---

## Part D — UI: stringency control + honest count

- Add a **strict / moderate / loose** control to the Similarity tab (segmented control or
  small dropdown), default **moderate**.
- Changing stringency re-queries and repaints; anchor and lens persist (same contract as
  sub-lens switching).
- **Report the count** in or near the blurb: "Showing all N basins within the moderate
  threshold" — replacing the current "Showing the 200 most similar basins." The count is the
  point; make it visible.
- Distance coloring unchanged (continuous, most-similar dark). Consider a soft fade toward the
  threshold edge rather than a hard cutoff, so the boundary doesn't imply false precision about
  where "similar" stops — optional, only if low-cost.
- Blurb text per lens already dispatches by `lens_id` (WO7a); extend it to fold in the count
  and, where useful, a prevalence gloss ("this is a common climate type — results are globally
  dispersed" vs. "this is a comparatively rare pattern — results cluster tightly"). The
  prevalence read can key off the result count against a per-lens common/rare cutoff from B2.

---

## Acceptance

- Perf probe (Part A) recorded with actual numbers; rendering approach chosen and worst-case
  paints smoothly (pan/zoom without stutter).
- Threshold notebook (Part B) reports strict/moderate/loose radii per lens with counts for each
  validation anchor; rare-type-strict is tight, common-type-loose is broad.
- Endpoint returns variable-count thresholded neighborhoods; count and radius surfaced in
  `query_meta`; NaN masking confirmed per lens.
- UI stringency control re-queries and repaints; count reported in the blurb; anchor + lens
  persist across stringency changes.
- **Hero-shot check:** for a fixed lens (Seasonal phase) at moderate stringency, SF returns a
  visibly tight, geographically clustered set and Timbuktu returns a visibly broad, dispersed
  set — the contrast is legible at a glance on the map. This is the demonstrator; confirm it
  reads.
- All existing tests pass; contract test added asserting variable count (rare-anchor count <
  common-anchor count at the same stringency for at least one lens).

---

## Out of scope for WO7b

- Terrain / Hydrology / Vegetation lens groups — future WOs, each its own notebook.
- Vector-tile migration of the similarity map, unless Part A forces it — flag for discussion,
  don't build.
- Timbuktu precip-vs-hydrology presentation split — still a deferred presentation concern.
- Cross-lens comparability of thresholds — explicitly not attempted.
- Settlement/place overlays on the thresholded set beyond what WO7 already returns — future, if
  the thresholded view proves it wants place anchors.
  