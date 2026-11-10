# WO-04 summary: where the profile stands, and what to do next

2026-11-05. Detail files: `wo04a_inventory.md` (sources), `wo04a_results.md` (a verdict per unit), `wo04_schemes.md` (published classes for the dummy's words), `wo04c_results.md` and `wo04_filled_profiles.md` (the dummy filled from real data). Unit ids (S2.3 and so on) refer to `modal_dummy_annotated.md`.

## Where WO-04's deliverables are

The work ran in three parts (04a inventory and verdicts, 04b schemes, 04c fill), so some file names differ from the list in `wo04_generate-the-modal.md`.

| WO-04 asked for | File | Part |
|---|---|---|
| `wo04_summary.md` | this file | all |
| `wo04_results.md` (a row per unit) | `wo04a_results.md`; sources in `wo04a_inventory.md` | 04a |
| `modal_dummy_annotated.md` | same name | 04a |
| `wo04_schemes.md` | same name | 04b |
| `wo04_modals.md` (filled modals) | `wo04_filled_profiles.md` (the term "modal" is kept for the WHG screen) | 04c |
| (not asked for) fill rates and issues | `wo04c_results.md` | 04c |

Code: `scripts/edop/whg/wo04_fill.py`, `notebooks/edop/whg/wo04c_fill.ipynb`.

Not done as the WO words it: each filled value was read for oddities (reported in `wo04c_results.md`) but not checked one by one against an outside source.

## What this work order has accomplished

1. **Broke the dummy into 57 items** (units) that can each be judged: sentences, optional parts, and the Timbuktu example's extra statements.
2. **Listed where each item's data comes from**, with what EDOPS already computes (Seasonality, Analysis, Context, the ring, the river layer) and what it does not.
3. **Gave each item a feasibility verdict.** 22 can be filled from data held now (yes). 28 can be filled once one named thing exists (maybe). 7 are not feasible as worded (no).
4. **Found published schemes** for the dummy's class words (relief, river size), so those cutoffs need not be invented.
5. **Wrote a throwaway fill script and filled the dummy at ten places.** Each result is a filled_profile: the 16 items a basin's data can fill are real text, and every other item is a visible placeholder that names what is missing.
6. **Tested the filling over 306 basins.** All 16 fill reliably. Optional parts left out by rule: the sea-touch sentence (253 of 306 basins, inland), upstream/downstream neighbours (122), the "wetter than local" part (290). The only failures are 5 ecoregions with no Wikipedia text.
7. **Found problems early** (listed in `wo04c_results.md`): a wrong Wikipedia link, basin averages read as the place's, "0 km" distances, and a water sentence that fits only 5% of basins.

## What the 28 maybes are waiting on

A maybe is a job to do, not a stop. The 28 fall into five kinds of job:

| Job | Items | What it is |
|---|---|---|
| 1. Neighbour-comparison rules | 6 | S2.3, S5.2, S6.2c, S6.3b, S6.4, S6.5. One shared set of rules (rank among the ring's basins, counts above and below, ties, zeros) unblocks all six. |
| 2. Class words and cutoffs | 9 | S1.1c, S1.4, S2.1b, S3.X1, S4.1a, S4.1b, S4.3, S4.X1, S5.1c. Pick a published scheme or a cutoff (the Sandbox's fixed thresholds can be reused). |
| 3. The point-specific layer | 7 | S1.1b, S1.3, S3.1a, S3.1b, S3.3, S7.3, S8.3. Elevation at the point, distance to the nearest river and the basin edge, the snap. |
| 4. Text to write or agree | 3 | S1.2b (ecoregion one-line gist), S8.1b (dataset years), S9.1 (link from WHG into EDOPS). |
| 5. New data or fields | 3 | S7.1a (coastline), S3.4 (lake share into the payload), S6.X1 (basin shape). |

The 7 `no` rows (direction words, positions inside the basin, a relation that exists only in text) are reworded or dropped, not built.

## What I suggest next, in order

1. **Build the neighbour-comparison rules** (job 1). Six items, no new data, no WHG dependency. Write the rule set and the ties and zero wording, then test over the 306 basins. Needs your or Opus's decision on how "among the driest" is worded.
2. **Add the class words** (job 2). Nine items. Take the published relief and river-size classes from `wo04_schemes.md`, reuse the Sandbox cutoffs for the rest, and sweep the few that need it. Then the filled_profiles read as prose, not placeholders.
3. **Fix the problems the fill exposed**, which are small: wording for the other four water classes, a rule for "0 km", climate wording for large basins, and the ecoregion-to-Wikipedia mapping.
4. **Add the point-specific layer** (job 3). Decide first whether WHG supplies elevation. Then point elevation, the point's ecoregion, nearest river and the snap.
5. **Write the text items** (job 4) and **get the coastline data** (job 5). The link scheme needs WHG's agreement, so it waits for the demo.

Steps 1 and 2 cover 15 of the 28 maybes and need no outside input. After them, the ten places and the 306 basins can be re-filled, and the result goes to Opus for comment and then to the ISHI demo.

## Cost

Filling 306 basins took 480 s (1.6 s each). Extrapolated, all 16,397 L6 basins would take about 7 hours. A persisted build that reads the database directly should be faster.
