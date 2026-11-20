# reg WO-08: LBDA, finishing items

Draft of 20 Nov 2026, for Karl's review. Small; on the `lbda` branch, to be merged into `v1` when done. Follows `reg_wo07_results.md` ("Needs attention", section B).

## Goal

Close the small items left by WO-07 so that `lbda` can merge into `v1` before Karl's trip.

## Items

1. **Flag early gaps by change over time** (WO-07 B6). In the engine's `sources` note and in the Dashboard's LBDA block, name the years whose coverage is clearly below the coverage of the later years of the span (for example "150–209: 77–95% of the area, against 100% from 210"). Keep the 0.1 and 0.5 thresholds and the `low_coverage` status as they are. Propose what "clearly below" means and say why. Tests: the Santa Fe Level 6 basin, 150–300, is flagged; Chaco 1100–1200 is not.

2. **Data for the band threshold** (WO-07 B7). Count the LBDA cells under each Level 6 and Level 8 basin in the contiguous US, at a year when coverage is complete. Report the shares with fewer than 5, 10 and 20 cells, as a table. Do not change `MIN_CELLS_FOR_BAND`; Karl sets it from the table.

3. **Documentation** (WO-07 B10). An LBDA section in `docsite/data-sources.md`, modelled on GEDA's; regenerate the Codebook.

4. **Baseline cases** (WO-07 B11). Add two or three US cases to the regression baseline (Chaco, Santa Fe as a buffer, Cahokia clipped) as additions. No existing reference is re-captured; if the capture script cannot add cases without rewriting the others, say so and stop.

## Provisos

- Keep it short. One check per case. List anything else in one line under "Needs attention" and stop there.
- No change to how GEDA, LMR, HYDE or eVolv2k are computed or displayed.
- The public basin route is not touched; it waits on the WHG modal contract, so the block's shape is designed once.

## Deliverables and gate

- `reg_wo08_summary.md`, one page; `reg_wo08_results.md`, with the item 2 table.
- Tests for item 1; the new baseline cases.

Gate: Karl checks the Santa Fe basin, 150–300, in the Dashboard and sees the early years named; then `lbda` merges into `v1`.
