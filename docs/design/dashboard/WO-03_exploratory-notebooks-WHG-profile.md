# WO-03: exploratory notebooks for the WHG environmental profile

Draft 2026-11-01, for Karl's review. Goal-setting, not a specification: CC finds table names, functions and particulars in the code and database.

## Goal

Get the numbers that the design of the WHG [Environmental Profile] modal and its payload depends on. The profile answers questions at three scales: the core basin (L6), its ring of first-order neighbours, and the ecoregion. This WO measures what is to hand, what is cheap, and what is unexpectedly hard, so that the questions document and the payload proposal rest on evidence. No app behaviour changes.

## Background to read first

`whg_ring_profile_spec_prelim.md` (ring spec and its seven open questions), `wo02_summary.md` and `wo02_results.md` (rule families; issue 1 coastal gap; 7a to 7d prose hazards), `sandbox_cheatsheet.md`, the Sandbox Analysis tab (local and upstream pairs, upstream area, distance to ocean outlet, drainage type), the Workbench Ecoregions tab (Wikipedia links and LLM summaries).

## Test places

Approximate coordinates; CC confirms each lands where intended and records the resolved `hybas_id`.

| Place | Lat, lon | Why |
|---|---|---|
| Timbuktu | 16.77, -3.01 | primary fixture; river corridor in a contrasting surround; point at the core's tip |
| Tbilisi | 41.72, 44.79 | second fixture; ring spans a gradient and crosses a major divide |
| Santa Fe | 35.69, -105.94 | ring much like the core; tests saying little |
| Kaifeng | 34.80, 114.31 | perched river: the containing basin is not the river that defines the place |
| Lviv | 49.84, 24.03 | Galicia worked example; near the Baltic and Black Sea divide |
| Poltava | 49.59, 34.55 | Ukraine worked example (breadbasket); likely uniform ring |
| Chaco Canyon (Pueblo Bonito) | 36.06, -107.96 | New Mexico worked example; with Santa Fe brackets the San Juan to Rio Grande movement |
| Alexandria | 31.20, 29.92 | delta port; coastal |
| Utqiaġvik | 71.29, -156.79 | Arctic coastal; the ecoregion example |
| one oceanic island town | CC chooses | no basin expected |

For counts and rates, also use the WO-02 population sample (306 basins stratified by climate zone). If a settlement sample is readily available (for example a WHG export), use it as well and say so: WO-02 rates are for random basins, and settlements sit on coasts and rivers more often.

## Questions

**Q1. The ring as it stands.** For each test place, run the existing `resolve_basin_ring` and `basin_ring_signature`. Report the neighbour count, the spread of neighbour areas relative to the core (largest and smallest ratio), time per call, and payload size. Can the per-basin percentiles be computed once for the set (ring spec, verify item)? What would a compact neighbour row weigh?

**Q2. Flow relation of neighbours.** Can each neighbour be classed as upstream of the core, downstream of it, or off the core's stream, from the HydroATLAS topology (`next_down` or equivalent)? For the `_upstream` variables, show how a neighbour's rank depends on that class at Santa Fe, Timbuktu and Kaifeng. Report how often a ring contains at least one upstream and one downstream neighbour in the population sample.

**Q3. Ecoregions.** For the core and the ring at each test place, and for the population sample: how many ecoregions intersect, with area shares; whether the point's ecoregion equals the core's largest-share ecoregion; distribution of the count across the sample. Check coverage of Wikipedia links and LLM summaries over all ecoregions, and list any without one.

**Q4. River names.** Identify the named sources (Natural Earth river layers in the database, which scales) and the unnamed rivers table (likely HydroRIVERS; confirm). Try matching names onto the network and carrying them along main stems. Report, for the test places and the sample: the share of cores and of rings with at least one named river; examples of wrong or doubtful matches; time per query. One method is enough if it works; note others tried.

**Q5. Nearest main stem.** For each test place, find the nearest river reach above an upstream-area threshold (CC picks two or three thresholds), its distance from the point, its upstream area, and its name where Q4 gives one. Compare with the containing basin's upstream area. Kaifeng should show a large gap. Report how often the gap exceeds an order of magnitude in the sample, and in the settlement sample if used.

**Q6. Where the point sits.** Distance from the point to the core's boundary, as a share of the core's size measure CC finds appropriate; which neighbour is nearest; for the island and coastal points, distance to the nearest basin (input to snap tolerance, ring spec question 1).

## Provisos

- Read-only against the local database and server; record the commit.
- Notebooks under `notebooks/edop/whg/` (or wherever CC judges consistent with WO-02).
- Timing is local and labelled as such; measure, do not optimise.
- No statement wording in this WO beyond what illustrates a finding. Numbers, no verdict words.
- Where a question turns out to need data or code that is not there, say what is missing and stop on that question; do not build it.

## Out of scope

Engine or endpoint changes; the rule family for core and surroundings; Band T; regional datasets; the URL scheme for linking from WHG into EDOPS; payload size targets.

## Deliverables and gate

`wo03_summary.md` (one page, read first), `wo03_results.md` (one section per question, tables, and issues found), and the notebooks.

**Gate:** the summary answers Q1 to Q6 with numbers, or says why a question could not be answered and what it would take.

