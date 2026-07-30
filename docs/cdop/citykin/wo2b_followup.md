# CITYKIN WO2b — the shipping-facet correlation, and what Kansas is evidence of

**Status:** draft for review.
**Prior:** `wo2a_findings.md` (relief-range survives the area-confound probe and ships; the
description-vs-prediction argument against the 0.70 drop bar), `CITYKIN_session-opener.md` (WO2 scope),
`wo1a_findings.md` (the r=0.62 elevation-vs-relief check this WO is the basin-scale analogue of).
**Type:** closing diagnostic. One reading WO2a didn't take, one record correction. No wiring, no UI.
Runs against the notebook WO2a already built.

Goal-setting with provisos. CC discovers implementation particulars; Karl reviews every write and runs
every cell.

---

## Why

WO2a settled the question it was asked and cleared `relief_range` to ship. But its redundancy reading
was `corr(relief_range, slp_dg_sav)` — and `slp_dg_sav` is not a shipping facet. **The correlation
between the two facets that actually ship, `ele_mt_sav` and `relief_range`, was never reported at
either level.** That is the reading the lens depends on, and it is the direct basin-scale analogue of
WO1a's r=0.62 elevation-vs-relief check on the point-window lens. One line against an already-run
notebook.

Second, smaller: `wo2a_findings.md` cites the Kansas basin twice, for opposite conclusions — as the
illustration of the area confound (large, gentle, relief above what slope predicts) and as the
illustration of why relief must be kept (locally distinctive signal a slope-only facet would flatten).
Both readings are defensible; the same basin cannot serve both in one record without the strongest
evidence for keeping relief also being the strongest evidence that relief measures size. This WO
separates them empirically rather than by choosing which sentence to keep.

## Part A — the shipping-facet correlation

Report, at **L06 and L08**, from the WO2a sample as already pulled and masked:

- `corr(ele_mt_sav, relief_range)`
- the same, as a scatter or hexbin, so the shape is visible and not only the coefficient

Provisos:

- Same masking as WO2a (`-9999` → NaN; L08's six non-positive `sub_area` rows). No re-derivation of the
  sample — this reads the frame WO2a already built.
- Report the number; do not compare it to the 0.70 bar. See the decision rule below.

## Part B — what Kansas is evidence of

The two readings are separable, because they are two different conditional expectations. For the
western-Kansas basin, report its `relief_range` against **both**:

1. **Expected relief given its slope**, corpus-wide — the reading that makes it a *keep-relief*
   illustration (relief carries information slope does not).
2. **Expected relief given its area**, corpus-wide, at its slope quartile — the reading that makes it a
   *confound* illustration (relief is elevated because the basin is large).

If it exceeds the first but sits near the second, its excess relief is size and it belongs only in the
confound paragraph. If it exceeds both, it is genuinely locally distinctive and belongs in the
keep-relief argument, with the confound illustrated by the quartile cell alone (which is corpus-wide
and needs no single basin to carry it). Whichever way it lands, `wo2a_findings.md` is edited in the
same pass to cite Kansas once, for one thing.

Proviso: simple conditional means or a fitted line are both fine — this is a placement question about
one basin, not a modeling exercise. Do not build the residual facet here (see Forward).

## Decision rule — stated before the numbers

**Part A's correlation is a reading that informs the lens's description and its knob defaults. It is
not a gate, and it does not trigger a drop at any value.**

Recorded explicitly because WO2a's own decision rule (mine) imported the project's 0.70
Mahalanobis/drop bar without asking what that bar is for, and Karl's findings were right to reject it.
Two reasons it does not transfer here, the second of which WO2a did not state:

- **Description, not prediction** — `wo2a_findings.md` § Decision, and `CLAUDE.md`'s standing rule
  against removing signature variables on global co-variation. Not re-derived here.
- **The bar comes from a compensatory-distance context.** In a quadrature sum, correlated facets
  double-count shared physics, and Mahalanobis exists to correct exactly that. WO2's lens is a
  **non-compensatory tolerance-band conjunction**: each facet is its own in/out test, and correlation
  between bands distorts nothing. It costs **selectivity** — the second band rarely excludes what the
  first already did — which is a fact about how tight the knobs need to be, not a reason to drop a
  variable.

So the consequences of Part A's number are:

- **Moderate or low** — the two bands do independent work; knob defaults set on each facet's own spread,
  as WO1a did.
- **High** — the two bands are near-duplicates and the lens is effectively one facet wearing two knobs.
  That does not drop either one, but it must be **said in the guide** rather than left for a user to
  discover, and it is the one legitimate argument for a third facet in WO2 — which would then need its
  own justification, not this number alone.

The line between those is set by Karl after seeing the spread and before writing the guide language, in
that order, and goes in the findings with its basis.

## Accept gate

**`corr(ele_mt_sav, relief_range)` is reported at both levels with its scatter; Kansas is placed against
both conditional expectations and `wo2a_findings.md` is edited to cite it once, for one conclusion; and
the Part A consequence (independent bands vs near-duplicate bands) is recorded in `wo2a_findings.md`
alongside the number.** No wiring, no persisted column, no third facet built.

## Validation order

1. Part A at both levels, reported to Karl.
2. Part B, reported to Karl.
3. Karl sets the description consequence; `wo2a_findings.md` edited in one pass (both the new reading
   and the Kansas correction); tracker's *Last updated* stamp reset.

## Notebook conventions

Appends to `notebooks/cdop/citykin/wo2-3_terrain_basin.ipynb` (Cells 9+; renamed from
`wo2_terrain_basin.ipynb` once WO3 also came to live in it), continuing WO2a's numbering.
`# Cell N` first line of every cell; SQLAlchemy warning suppressed in DB cells; `print(df.to_string())`
for tabular output. Figures follow the standing render pattern (`fig.patch.set_facecolor('white')`,
save-then-`display`, `print("drawing ...")` immediately before the `subplots` call). Karl runs cell by
cell and reports output — no number asserted as a finding before Karl has shared it.

## Forward — not this WO, carried to WO2's design conversation

- **The residual facet** (`relief_range` regressed on `slp_dg_sav`), named in `wo2a_findings.md` § Open.
  The tension to weigh when it is taken up: its value is **corpus-relative** — the zero point is an
  artifact of a global regression, and differs between L06 and L08 — while every other facet in this
  lens family is anchored **query-relatively, in physical units**. A basin's residual is not a fact
  about the basin the way its mean elevation is. Not disqualifying, but it cannot be explained in the
  guide the way the other facets can, and the "no one reads anything" rule bites hardest on the facet
  needing the most explanation.
- **Fixture selection for WO2's smell test**: select basins by **area quantile from the table**, then
  see what is there — do not coordinate-pick and hope. WO2a's named-basin check was inconclusive on its
  size axis for exactly this reason: HydroBASINS delineates by drainage topology, so a point in a small
  landscape can land in a very large basin (Innsbruck, 25,920 km²).
- WO2's lens design proper — tolerance knobs, defaults, paint-a-set head, guide language, and the
  basin-scale discrimination smell-test.
  