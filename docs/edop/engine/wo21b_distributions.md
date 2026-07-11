# WO21b — Distribution histograms (polity never collapses)

**Branch:** `engine_v0.4b`
**Phase:** Areas · **Sub-phase:** neighborhoods (polity — response-shape)
**Fixture:** Northern Song, year=1000, L06
**Code home:** may be appended to the `wo20_*` notebook (Karl to sort placement with CC)

## Goal

The engine emits a weighted **histogram object** for every polity variable, delivered in `detail`. This is the engine's statement about within-polity distribution. **All rendering belongs to the dashboard surface, not the engine.**

## Governing rule — polity never collapses

The polity path **never collapses any variable to a single value.** No ECC gate, no subresolution branch, no mean-with-a-sentinel. Every variable — A–E basins, HYDE cells, LMR cells — emits its weighted histogram, however coarse. A variable with few effective cells emits a coarse histogram flagged `low_resolution: True`; it is still a distribution. The sentinels `distribution='reported'` and `distribution='collapsed_subresolution'` are removed.

## Division of labor

The Cliopatria pilot owns rendering and already works for every dropdown variable:
- onLoad renders `aridity_index` (Band C) at L06, no polity — global basin choropleth.
- Polity select draws the boundary as an overlay; the variable is unchanged.
- Variable select (incl. all 4 HYDE/LMR Band T variables) swaps in a global tileset for that dataset and paints cells worldwide, with a time slider for the time-indexed variables.

The map layer is global and query-independent. So:
- **Dashboard surface owns:** the global paint, the time slider, the polity boundary overlay, and any histogram *visualization*.
- **Engine owns (this WO):** the histogram **object** delivered when `&detail` is given — weighted, geometry-free, polity-scoped. No painting, no per-cell render values, no tileset/slider awareness.

Per-unit tile-paint values are descoped: the global tileset already feeds the map, so there is no per-unit rendering payload for the engine to produce.

## Part 1 — LMR per-cell distribution (confirmation)

The polity path no longer collapses, so there is no gate to investigate. Report the LMR per-cell value distribution over N Song / 1000 CE (min / p10 / p90 / max / mean, weighted by `w_eff`), plus the ECC (`w_eff`) value and whether the ~93 figure is raw or effective cells. Purpose: confirm the cells are heterogeneous and that the histogram surfaces it. Records the fact; gates nothing.

## Part 2 — Weighted histogram object in `detail`

One object per variable, uniform across substrates:
```
detail['distribution'] = {
    'bins':       [edge_0, ..., edge_k],          # k+1 bin edges
    'weights':    [w_0, ..., w_{k-1}],            # summed unit-weight per bin (NOT raw count)
    'n_units':    <int>,
    'unit_type':  'basin' | 'hyde_cell' | 'lmr_cell',
    'low_resolution': <bool>,                     # true when few effective units; still a distribution
    'min': <float>, 'max': <float>,
    'p10': <float>, 'p90': <float>, 'mean': <float>,
    'resolver_year':  <int>,                      # year polity boundary + unit set resolved at
    'band_t_from':    <int|null>,                 # Band T span start (null for static A-E)
    'band_t_to':      <int|null>                  # Band T span end   (null for static A-E)
}
```

Requirements:
- **Weighted, not counted.** Bin contributions are summed unit weights (basin area-weight; cell `w_eff`), never raw counts. Reuse existing weighting (WO6 weighted quantiles, WO15 `w_eff`) — one shared implementation, do not re-derive.
- **Bounded.** Fixed bin count (suggest ~20; implementer's call, note it) so 376 basins and 37,901 HYDE cells reduce to the same small object. Band T: bin on native units or scores as appropriate — note which.
- **Edge cells stay internal.** Boundary-straddling Band T cells contribute fractionally via `w_eff`, consumed inside the binning — never exposed as per-cell data.
- **Temporal stamp.** Stamp both axes (`resolver_year`; `band_t_from`/`band_t_to`) so a histogram is self-describing and cannot be silently compared across different boundary-years or Band T spans. Static A–E leaves Band T fields null.

## Scope

In: LMR per-cell distribution report; weighted-histogram `detail` object across all three substrates, temporally stamped; removal of collapse path and sentinels from the polity route.

Out: per-unit tile-paint endpoint; multi-timestep/slider wiring; Clio pilot restyling; cross-variable score reconciliation; L08.

## Deferred-register entry

> **Weight-aware per-unit polity rendering.** Per-cell/per-basin values with fractional-overlap weights, for choropleths painting edge units by partial membership or rendering a polity in isolation. Not needed while the map layer is global and query-independent (pilot paints a global tileset per variable/timestep; polity is a boundary overlay). Engine's polity-distribution contribution is the weighted histogram (WO21b Part 2). Revisit only if a use case wants weighted or polity-isolated rendering.

## Acceptance / return

- Part 1: LMR per-cell distribution stats + ECC value for N Song.
- Part 2: example histogram object each for `aridity` (basin), `cropland_fraction` (HYDE), and the LMR variable, dumped readable. Weights sum correctly; bins weighted not counted; both temporal axes present; no collapse path remains; sentinels gone.
- Existing buffer + WO20 polygon suites still PASS.
- New observations to `areas_findings.md` under AF.WO21.<m>.