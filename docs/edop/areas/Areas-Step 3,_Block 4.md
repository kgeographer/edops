# CC Work Order — Areas Step 3, Block 4: Flag / structural path

Branch: `areas_step3`. Fixture: Timbuktu 100 km / L06. Goal: collapse the structural fields
(coast, endorheic) for the buffer's weighted basin set, and surface the derived `outlet_type`
4-class categorical. Reuses the Block-3 `class_mixture` aggregator wherever the output is a
% -of-class mixture.

## The decision this block resolves

`outlet_type` (4-class, derived from endo×coast) fully contains both the endorheic 3-class
field and the coast flag — coast fraction = the "Exorheic, coastal" class; endorheic fraction =
the two endorheic classes. So for the *areal* product I recommend:

- **`outlet_type`** — emit as the primary structural variable: 4-class `class_mixture`
  (modal class + plurality verdict, identical machinery to Block 3).
- **`coast_fraction`** — emit as a convenience scalar (method `flag_fraction`): the
  area-weighted fraction with coast=1. Strictly derivable from `outlet_type`, but a single
  "% coastal" number is a clean feature for the machine/comparison consumer, so worth its own row.
- **`endorheic` (standalone 3-class)** — do NOT emit separately in the areal output; it's fully
  recoverable from `outlet_type` and a third overlapping product would be noise.

This last point revises the locked "endorheic as 3-class" decision **for the areal case only** —
the point signature is unaffected and keeps raw `endo`/`coast`. Flagging because it touches a
locked decision; proceed on this path unless Karl says otherwise.

## outlet_type derivation (authoritative mapping)

Per the global (endo, coast) cross-tab — the only four combinations that occur:

| endo | coast | class_id | label |
|---|---|---|---|
| 0 | 0 | `00` | Exorheic, non-coastal |
| 0 | 1 | `01` | Exorheic, coastal |
| 1 | 0 | `10` | Endorheic (drains to inland sink) |
| 2 | 0 | `20` | Terminal sink basin |

Use a stable composite `class_id` (e.g. the `f"{endo}{coast}"` string, or `endo*10+coast` as
Int64) so ids are deterministic, not positional. **Assert** that no basin has `coast==1 &
endo>=1`; raise on violation. Optionally carry the global frequencies
(11047 / 2094 / 1570 / 1686) as a `global_freq` reference so "this buffer vs the global
baseline" is computable downstream.

## Cells

**Cell N — load + derive.** Read the buffer set + the raw per-basin `endo` and `coast` flag
values from the Step-2 outputs (these are the raw-emitted flags; confirm the file/columns).
`hybas_id` int64. Build the per-basin `outlet_type` class via the mapping above, with the
exclusivity assertion.

**Cell N+1 — aggregate.** Route `outlet_type` through the existing Block-3 `class_mixture`
function (weighted % of class, drop NoData + renormalize, modal/share/n_classes/concentration,
plurality verdict at the same `PLURALITY_THRESHOLD = 0.85`). Compute `coast_fraction` as the
area-weighted mean of coast over the buffer set (NoData handling consistent with the rest).

**Cell N+2 — assemble (no writes).**
- `outlet_type` → one `class_mixture` headline row (envelope + Block-3 detail cols) and its
  mixture rows appended to `step3_block3_mixture.tsv` (or a `block4` mixture file — match
  whatever Block 3 settled on).
- `coast_fraction` → one `flag_fraction` row: `representative_raw` = the fraction,
  `representative_score` = null, `n_basins`, `coverage_weight`; no verdict (status `uniform`
  if fraction is exactly 0 or 1, else `ok`).

**Cell N+3 — validate (print).**
- Mixture sums to 1.0; coverage separate; ids Int64; exclusivity assertion passed.
- Timbuktu expectations: `coast_fraction` = 0.0 (deep interior, no coastal basins), so no
  "Exorheic, coastal" class should appear. `outlet_type` should split between exorheic
  (Niger drainage) and endorheic (Saharan closed basins / delta margins).
- **Cross-check worth eyeballing, not asserting:** the endorheic fraction (classes `10`+`20`)
  against Block 1's `dist_sink_km` `weight_at_zero` (0.47 at Timbuktu). If they're in the same
  ballpark, that's a nice internal-consistency signal across two independent variables; if they
  diverge, the gap is informative about how `dist_sink` defines "sink" (terminal-only, endo==2,
  vs any endorheic) — note it rather than forcing agreement.

**Cell N+4 — write (gated).** After review, append rows and mixture entries.

## Done =

`step3_results.tsv` carries `outlet_type` (class_mixture) + `coast_fraction` (flag_fraction)
alongside the existing rows; endorheic not separately emitted areally; Timbuktu shows zero
coastal weight and an interpretable exorheic/endorheic split; exclusivity guard live.