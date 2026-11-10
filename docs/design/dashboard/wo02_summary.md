# WO-02 summary: statements derivable from one signature payload (tier 1)

2026-10-31. Read this first. Detail is in `wo02_results.md` (family sections, issues 1 to 8) and `notebooks/edop/dashboard/wo02_master_table.csv` (one row per statement type: inputs, rule, template, applies to, UI today, needs new data, fixture and population results, sweep result).

## What was done

Payloads from the local server (code at commit `bb80fee`, v0.4.2 plus the dashboard branch): 34 fixtures chosen for conditions, 11 Band T fixtures, and a 506-query population sample (306 basins stratified by climate zone, with buffer and L8 variants; weighted to the world by zone size). A field-availability check found the payload structure matches the cheat sheet. Then nine families of rule-based statements were built, each tested on the fixtures and the sample, with cutoff-dependent wording swept over a grid. **54 statement types.** No app behaviour was changed.

| Family | Types | What it says |
|---|---|---|
| Position | 7 | percentile with its reference frame; raw value; zero here; rank among non-zero; share of an area at the bottom |
| Empty cells | 6 | why a value is missing or withheld, one sentence per cause |
| Local and upstream | 5 | the gap between a variable and its `_upstream` pair |
| Coverage and shortfall | 4 | how much of the area the numbers describe |
| Distribution | 6 | spread behind a headline percentile |
| Categorical | 4 | the class, the mixture, the top classes |
| Within-band | 8 | soil texture, discharge, wetlands, temperature, elevation, land use |
| Cross-band | 4 | variables furthest from the global median; how typical a place is |
| Band T | 10 | LMR anomalies, HYDE land use, volcanic events over a span |

## What is already in the Sandbox, and what is new

Of the 54, 15 are shown by the Sandbox, 13 in part, and **26 are new**. New: the local-and-upstream gap (5 of 5), all of cross-band (4 of 4), nearly all of within-band (7 of 8), three of the four coverage statements (including the share of an area outside any basin), and the zero-aware percentile wording. The Sandbox shows that an empty value is empty ("not present here", "no data") but not why.

## What is unstable, and what the payload cannot give

- **Wording that needs a cutoff flipped in every sweep.** Five fall back to stating the number alone: the "Most of" share (POS-06), "agree or differ" for local versus upstream (LU-01, LU-02), concentrated for continuous spreads (DIS-06) and for categorical mixtures (CAT-04; 66% of rows change wording across the grid). Two cannot be swept because the payload lacks the input (DIS-04 the tied weight, BT-03 the LMR effective weight).
- **18 of the 54 need information outside the payload.** The recurring gaps: what a variable's high or low means (7a), unit wording and display scale (7b), what a zero means (7c), what area a variable covers (7d), what the source's -9999 means per variable (issue 5), what each HYDE layer contains (issue 8), readable names for Band T, and the catalog's zero fractions (the catalog has none for `reservoir_vol`; `dist_sink` is zero-aware at L6 but not at L8). These belong to the friendly-name crosswalk work order.

## Patterns across the families

1. **Buffers produce a disproportionate share of the awkward cases:** 3 of the 7 anomalies in the first field matrix, empty cells twice as common as at single basin (about a quarter of rows), pair gaps lost for 47% of pairs, and the sea changing the engine's own verdicts (119 rows in 19 buffers read `ok` although all land is at zero). Karl's position and the evidence are in one section of the results file.
2. **Spatial dependence narrows every spread:** a 100 km buffer's middle 80% is about 5.5 times narrower than random basins would give, so "concentrated" is true for 9 rows in 10.
3. **A quarter of buffer scores are suppressed** (the two-group call; polities skip it), and at 2 to 4 basins the call is close to automatic.
4. **Coastal points a few metres offshore get a 404** for single basin and ring (issue 1; deferred).

## Limits of the evidence

Band T rests on 18 queries (no population sample). Polities rest on 4 to 5 fixture queries. Rates are for buffers on random basins, not on settlements, which sit on coasts more often.

## Cheat sheet corrections queued (none made)

`friendly_name` and `db_col` absent on Band T rows, `db_col` null on two derived rows; `weight_at_zero` for every area-weighted row and a share of the circle in a buffer; `modality` placeholder values; `detail` keys (`regimes`, `suppressed_score`, `modal_label`, `perennial`, HYDE `sd` and `w_eff`, extra `distribution` keys, no histogram on `distribution_only`); polity top-level keys missing from the 2.3 list; one-basin buffers; suppression against basin count; `no_data` meaning by variable. Payload size is now measured (36 to 84 KB for bands A to E, up to 309 KB with a span, 1 MB for a 401-year span).

## Decisions for Karl

Whether the buffer scope stays (cheat sheet 7.2 item 12); the crosswalk work order; the shortfall floor for polities (COV-01); engine changes this WO excluded (zero fractions in the payload, normalising `outlet_type`, the zero guard under sea); coastal mitigation.

## Index to `wo02_results.md`

Step 2 summary; Step 3 results by family (1 Position, 2 Empty cells, 3 Local and upstream, 4 Coverage and shortfall, 5 Distribution, 6 Categorical, 7 Within-band, 8 Cross-band, 9 Band T); the buffer scope; issues 1 coastal gap, 2 buffer 404, 3 coordinate box, 4 coastality, 5 `no_data` meanings, 6 payload behaviours (6a to 6j), 7 prose hazards (7a to 7d), 8 HYDE grazing; working notes.
