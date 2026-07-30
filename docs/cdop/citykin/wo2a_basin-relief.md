# CITYKIN WO2a — does basin relief-range measure terrain, or basin size?

**Status:** draft for review.
**Prior:** `CITYKIN_session-opener.md` (WO2 scope — coarse Terrain regime on the sandbox Similarity
panel, basin-aggregate columns, L06 first), `wo1a_findings.md` (the WH Cities point-window lens — a
different scale and a different data path; not the instrument here).
**Type:** diagnostic notebook. No wiring, no UI, no persisted artifact. Settles one facet-choice
question ahead of WO2's design.

Goal-setting with provisos. CC discovers implementation particulars; Karl reviews every write and runs
every cell.

---

## Why

WO2 proposes two facets for the coarse basin-scale Terrain regime, both native BasinATLAS columns
already in the table: **mean elevation** (`ele_mt_sav`) and **relief-range** (`ele_mt_smx − ele_mt_smn`).
Mean elevation is uncontroversial — an intensive basin average, area-invariant in expectation.

Relief-range is not obviously safe. `smx` and `smn` are **order statistics** over the basin's pixels:
the larger the basin, the more pixels drawn, and the higher the expected max and lower the expected
min — before any difference in terrain. A large lowland basin also has a real longitudinal gradient
(floor dropping downstream, divide standing higher at the rim) that a small basin cannot accumulate.
Both effects push relief-range up with area on terrain that is gentle everywhere.

Whether that matters is a question of **magnitude, not mechanism**, and it has not been measured. If
large flat basins land at 150–250m against Alpine basins at 2000m+, the confound is real but too small
to affect a coarse lens and relief-range ships as scoped. If large flat basins land near or above small
rugged ones, then a fraction of what the lens paints is basin size, and `slp_dg_sav` — a mean of
per-pixel gradients, area-invariant in expectation, equally already-loaded — is the better carrier of
the same facet.

This WO measures it. It does not presume the outcome.

## Part A — the sample

A corpus-wide read, not a fixture list. Pull for **all L06 basins**: `hybas_id`, `ele_mt_sav`,
`ele_mt_smn`, `ele_mt_smx`, `slp_dg_sav`, and the basin's own area column. Derive `relief_range` and
`log10(area)`.

Provisos:

- **`_sav` / `_smn` / `_smx`, never `_uav`.** The `_uav` variants aggregate the entire upstream
  watershed, not the basin — adjacent in the catalog, wrong here, and wrong in a way that would look
  plausible.
- **Slope is stored in degrees ×10.** Convert on read. `-9999` is NoData (assigned to all of Greenland
  for `slp_dg_*` and `sgr_dk_*`) — mask to NULL/NaN, never coerce to zero.
- **Confirm the area column name against the table before writing it into a cell**, per the standing
  inspect-before-hardcoding rule. Do not assume the catalog's name matches the loaded schema.

## Part B — the measurement

Three readings, in this order:

1. **Does relief-range track slope, or track area?** Report the correlation of `relief_range` with
   `slp_dg_sav` and with `log10(area)`, and the **partial correlation of `relief_range` with
   `log10(area)` controlling for slope**. That last number is the whole question: it is the association
   with size that is *not* explained by terrain.
2. **Is relief-range redundant with slope?** Report `corr(relief_range, slp_dg_sav)`. If it is very
   high, the two facets are carrying one signal and the choice is between equivalent instruments —
   decide on the cleaner one, not on discrimination.
3. **The quartile grid.** Cross-tabulate mean `relief_range` and mean `slp_dg_sav` by area quartile ×
   slope quartile. The diagnostic cell is **large-area / low-slope**: what does relief-range read for
   big gentle basins, in meters, next to **small-area / high-slope**? This is the check in the form
   Karl asked for — the numbers side by side, not a coefficient.

Then, for plausibility only, print the same columns for a handful of named basins spanning the grid
(a large lowland Amazon or Congo basin, a small Alpine one, a large flat plains basin, a small
lowland one). **These are for eyeball sanity, not the finding** — the finding is corpus-wide. Locate
them by coordinate lookup against the table; confirm each is the basin intended before reading
anything from it.

## Part C — L08 secondary

Repeat Part B at L08. Not a separate question — a check on whether the answer is scale-conditional.
L08's area spread is narrower, so the confound should be *weaker* there if the mechanism is what this
WO says it is. If it is instead stronger or unchanged, the mechanism is not area and the diagnosis is
wrong — report that rather than reconciling it.

Cheap; same query shape. Report alongside L06, do not merge the two into one verdict.

## Decision rule — stated before the numbers

Recorded here so the choice is not made by inspecting the output and reasoning backwards to a
threshold. The standing project hazard is fitting the criterion to the motivating case; this WO's
motivating case is a suspicion of mine, which deserves the same guard.

- **Relief-range ships as the WO2 facet** if its partial correlation with `log10(area)` (controlling
  for slope) is weak, *and* the large-flat quartile cell reads clearly below the small-rugged cell in
  meters. The confound exists but does not reach the lens.
- **`slp_dg_sav` replaces it** if the partial correlation is substantial, *or* the large-flat cell
  reads at or above the small-rugged cell. In that case a nontrivial share of what the lens would
  paint is basin size.
- **Either is defensible; pick on redundancy** if `corr(relief_range, slp_dg_sav)` is high enough that
  they are one signal. Prefer the area-invariant one.
- **Both, as a third facet** is *not* an outcome this WO endorses by default. If the numbers argue for
  it, say so and why — but the WO2 scope is a coarse two-facet floor, and adding a knob needs its own
  justification, not a tie-break.

"Weak" and "substantial" are deliberately unquantified here: Karl sets the line **after seeing the
spread and before choosing the facet**, in that order, and the number goes in the findings with its
basis.

## Accept gate

**The three Part B readings and the Part C repeat are reported at both levels; the facet choice is made
against the decision rule above; and the chosen facet, the rejected one, and the numbers that decided
between them are recorded in `wo2a_findings.md`.** No wiring, no persisted column, no UI in this WO.

## Validation order

1. Pull and derive (Part A), NoData masked, area column confirmed against the schema.
2. Three readings at L06 (Part B), reported to Karl.
3. Same at L08 (Part C).
4. Karl sets the line, chooses the facet, and the choice is written to `CITYKIN_tracker.md` §
   *Locked decisions* with its numeric basis in the same edit.

## Notebook conventions

`notebooks/cdop/citykin/wo2-3_terrain_basin.ipynb` (opened as `wo2_terrain_basin.ipynb`, renamed once
WO3 also came to live in it), new. `# Cell N` first line of every code cell;
`%matplotlib inline` first line of Cell 1; SQLAlchemy pandas warning suppressed in any DB cell;
`print(df.to_string())` for all tabular output, never a bare DataFrame. Karl runs cell by cell and
reports output — no Bash-run notebook logic, no number asserted as a finding before Karl has shared it.

## Not this WO

- The Terrain regime lens itself — tolerance knobs, defaults, paint-a-set head, guide language. WO2.
- The basin-scale discrimination smell-test (Alpine vs plains, plausible neighbors) named in the
  session opener. That tests the *lens*; this tests one *ingredient*, and it comes first because the
  smell-test's result would be uninterpretable if the facet under it is partly measuring area.
- Any within-basin ruggedness or roughness measure. Requires cell-level data, not available; post-Braga
  full-DEM work, deferred.
- Landform position, containment, or any neighbor-relative facet. Not in WO2 scope.
- 