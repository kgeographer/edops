# WO17 — Area-weighted HYDE-to-basin aggregation (notebook proof + crosswalk)

**Branch:** `surf_wo17` — notebook + crosswalk build script + materialized table. **No change
to `sandbox_v2.html`, `/api/hyde/values`, or any live paint path.**
**Type:** Experiment / proof + data artifact. Karl accepts against the notebook's results, not a
code change. The route swap is the follow-on (WO18), gated on that accept.

## Goal

Replace the centroid point-sample (F16.4 approach B, shipped) with a **proper area-weighted basin
aggregate** for HYDE values, proven in a notebook before any live-code change. Produce the
materialized crosswalk table and the validated aggregation; on accept, WO18 swaps the route to use
it.

## Why

Centroid lookup paints each basin with the value of the single HYDE cell containing its centroid
(F16.4), scoring r=0.689 against BasinATLAS `crp_pc_sse` (F16.5). The defect isn't that basin
aggregation loses within-basin detail — it does, **by design, exactly as BasinATLAS does** at every
level, and that's a consistent and honest choice for a basin instrument. The defect is that
centroid **isn't an aggregate at all**: it's a point-sample masquerading as a basin value, the only
paint in the stack whose claim (basin aggregate) and delivery (one cell) diverge. The crosswalk
(F16.8) converts it to a true area-weighted aggregate — the same epistemic object every other
EDOPS band already is. This WO proves that method.

## Define "proper" — the target quantity

For each L6 basin *b* and HYDE step, the honest basin value is the area-weighted aggregate over
overlapping cells — physically, **cropland area within the basin ÷ basin area**:

> basin_fraction ≈ ( Σᵢ cropland_km²ᵢ · fᵢᵦ ) / ( Σᵢ area_km²ᵢ · fᵢᵦ ),  where fᵢᵦ = area(cellᵢ ∩ basinᵦ) / cell_areaᵢ

under the **uniform-within-cell distribution assumption** — cropland is taken as evenly spread
within each 5-arc-min cell, because that is the finest structure the source asserts. State this
assumption explicitly in the methods note: it is the honest claim boundary. We do the physically
consistent aggregation given HYDE's native grain; we do **not** recover sub-cell structure and
don't claim to. (This is the same boundary BasinATLAS operates within.)

The exact algebra and units are yours to finalize — **F16.3 applies and compounds here**: HYDE
stores km² per cell, not fraction, and the weighted sum is now km²-within-basin over km²-basin-area,
so the unit handling that produced the >100% bug in the WO16a notebook must be carried carefully
through the weighting. Guard against it in the notebook (assert no fraction > 1.0).

## Build (notebook, no live-code change)

1. **Crosswalk table** — materialize `temporal.hyde_basin06_weights` (the F16.8 Cell 9 script).
   The expensive geometry (cell∩basin intersection) is computed **once** here, not per request —
   that's the whole point; approach A's per-request spatial join was 140 s (F16.4). Store whatever
   the aggregation needs (intersection area + cell area, or a precomputed weight — your call;
   report the schema and why).
2. **Aggregation** — per-value query as a **join against the materialized crosswalk**, not a live
   intersection. Apply the F16.3 unit division inside the weighted sum.
3. Materialize the table as the concrete deliverable — WO18's route swap depends on it existing.

## Validation — this is what the accept gate is against

- **Shift vs centroid.** How many basins change, by how much, and the distribution of the delta.
  This quantifies how badly centroid was distorting — the justification for the whole WO.
- **vs BasinATLAS `crp_pc_sse`.** Does correlation improve over centroid's r=0.689? Expect
  improvement, since BasinATLAS derives its per-basin means the same area-weighted way. Note this
  tests **pattern agreement, not value agreement** — HYDE and BasinATLAS are different source
  datasets (HYDE ran ~40% higher, F16.5); r won't approach 1, and shouldn't. Improvement over
  centroid is the signal that the point-sampling error is reduced.
- **Coverage.** Centroid reached 16,040 / 16,397; 357 coastal/island basins were null (centroid
  outside land coverage). Does area-weighting recover any (basins that *partially* overlap a land
  cell even when their centroid doesn't)? Report which recover and which stay genuinely null.
  Confirm null → transparent, **never coerced to zero** (zero is a value, not an absence marker).
- **Performance — two separate numbers.**
  - *Build time* (one-off): acceptable at minutes (F16.8 estimated 30–90 min). Report actual.
  - *Per-request query time* against the materialized crosswalk: **must be centroid-comparable
    (~0.3 s)** or the method isn't viable for live paint and slice-reactive repaint (F16.10). This
    is the real go/no-go — the crosswalk only wins if precomputing the geometry keeps per-request
    fast. Report it plainly; if it's slow, that's a finding that stops the route swap, not a thing
    to optimize away silently.

## Methods decisions to surface for Karl — don't decide these in code

- **Denominator for partial/coastal basins.** Divide by full basin area (understates where a basin
  extends over ocean / no-data) or by covered area (overstates confidence where coverage is
  partial)? A real lying-with-maps choice — a half-ocean coastal basin's "cropland fraction" means
  different things under each. Show both in the notebook; Karl picks. Don't pick silently.
- **The uniform-within-cell assumption** — state it as the claim boundary in the methods note.
- **Crosswalk stored as area or fraction weights** — implementation, your call, but report it since
  WO18 and any future reuse depend on the schema.

## Explicitly not in this WO

- No change to `/api/hyde/values`, `sandbox_v2.html`, or the live paint. The route swap is **WO18**,
  on Karl's accept of this notebook.
- **L8** — L6 only, as everywhere. Note, though: the crosswalk method is level-parametric — an L8
  aggregate is a parallel table by the same construction. Build L6, but don't hardcode L6
  assumptions that would block the `level` parameter already in the API. (Karl flagged L8 as the
  honest lever for more within-basin articulation; nothing here should foreclose it.)
- **Native per-step raster tiles** (the "show the real 5-arc-min grid" artifact) — a separate,
  optional artifact answering a different question (source-grid fidelity vs. basin aggregate). Not
  this WO; not a correction to it.

## Accept gate (against the notebook)

- Crosswalk materialized; build time reported and acceptable.
- Area-weighted values computed for all reachable basins; **per-request query time
  centroid-comparable** (the go/no-go).
- Validation complete: shift-vs-centroid quantified; correlation-vs-BasinATLAS reported (improved,
  or the divergence explained); coverage delta reported; nulls stay null (not zero); no fraction > 1.
- Methods decisions surfaced for Karl (denominator shown both ways; assumption stated).
- No live-code touched.

## Deliverable

- `notebooks/edop/surface/wo17_hyde_area_weighted.ipynb` — build, aggregation, validation, both
  denominators shown.
- The materialized `temporal.hyde_basin06_weights` table + its build script.
- A short **methods note** stating the target quantity, the uniform-within-cell claim boundary, and
  (once Karl decides) the denominator choice. This note is what the paint's honest label will
  eventually cite.

## Findings

`docs/edop/surface/wo17_findings.md`. Report: crosswalk schema + why; build time; per-request query
time (the go/no-go); shift-vs-centroid distribution; correlation-vs-BasinATLAS; coverage delta +
which nulls recovered; the denominator options with data for Karl's call; F16.3 unit handling in
the weighted sum; confirmation no fraction exceeded 1.
