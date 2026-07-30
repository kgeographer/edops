# CITYKIN WO3 — coarse Terrain regime on the sandbox Similarity panel

**Status:** draft for review.
**Prior:** `CITYKIN_session-opener.md` (WO2 scope as Karl set it — basin-aggregate columns, draw-from-
the-DB, L06 first, coarse floor for the Braga v0.4 lens set), `wo2a_findings.md` + WO2b addendum
(`relief_range` cleared the area-confound probe and ships; `corr(ele_mt_sav, relief_range)` = 0.541
L06 / 0.566 L08 — the two shipping facets do independent work), `wo1a_findings.md` (the query-relative
tolerance pattern, and the two-fixture generalization rule that caught the 400m gate).
**Type:** lens build + wiring. Notebook validation first, then the panel.

Goal-setting with provisos. CC discovers implementation particulars; Karl reviews every write and runs
every cell.

---

## What this is

A fourth lens on the sandbox Similarity panel's dropdown, alongside Precipitation regime, Temperature
regime, and Climate (precip + temp): **Terrain regime**. Same grammar as its neighbours — a
**paint-a-set** head, query basin in, tolerance knobs, the matching set painted with a
weaker/stronger ramp and everything outside it unpainted, headed by the existing
"Your query matches *N* basins under *Terrain regime* — spanning *N* km" line.

Two facets, both native BasinATLAS columns already loaded:

- **Mean elevation** — `ele_mt_sav`. How high.
- **Relief range** — `ele_mt_smx − ele_mt_smn`, derived on the fly. How much vertical range the basin
  contains.

**L06 first**, matching how the other similarity and climate-class instruments default.

## What this is not — and the guide must say so

This is the **coarse floor**, shipped to complete the v0.4 lens set for Braga. It characterizes a
basin's overall elevation *level* and internal *range*. It does **not** measure fine-grained
ruggedness, roughness, or accessibility — those need cell-level data the project does not yet hold,
and are post-Braga work.

It also says nothing about **where within a basin** a place sits. Two cities in the same basin, one on
the valley floor and one on a ridge, receive identical answers. That is not a defect of the coarse
floor — it is what basin-to-basin means — but it is exactly the capability the WH Cities point-window
lens has and this one structurally cannot, and the two will sit on the same platform. The panel
already carries the right precedent in its own footnote ("This describes the Level 6 basin Tbilisi sits
in, not Tbilisi itself"); the guide language extends it rather than inventing a new register.

Write this honestly and briefly. Per the standing rule, no one reads anything — so the limitation
belongs in the short visible line, not only in a guide paragraph.

## Part A — the tolerance core

Same query-relative pattern as the climate regimes and as WO1a's terrain lens: each facet is a `±`
band anchored to the **query basin's own** value. A high-relief Alpine basin asks "what's like this";
a flat lowland basin asks "what's like this". No global constant anywhere in the instrument.

Provisos:

- **Non-compensatory conjunction**, matching the panel's existing grammar: each band is its own in/out
  test, both must pass. Not a quadrature sum. This is why the project's 0.70 Mahalanobis/drop bar does
  not apply here and why `corr = 0.54` triggers nothing (WO2b).
- **Reuse the tolerance/knob logic, not the data path.** WO1a's `terrain_lens.py` core is
  point-window-fed; this lens is fed by basin-aggregate columns. The knob semantics carry over; the
  ingredient does not. Do not force a shared function that has to branch on which world it is in.
- **NoData is NULL, never zero.** WO2a found the `-9999` sentinel affects `slp_dg_sav` only (302 L06 /
  6,390 L08 basins, Greenland) — the elevation columns are clean, so this lens has full coverage. Still
  guard it: any basin with a NULL facet is *excluded from the candidate set*, not admitted with a
  coerced value.
- **Serving path follows the existing convention** — the similarity/conjunction family is built as an
  in-memory startup index from the persist views (`main.py` lifespan), not per-request SQL and not a
  loose parquet. This lens joins that family. Confirm the actual pattern in code before choosing;
  do not infer it from this line.

## Part B — deriving the defaults

Three levels per knob (tight / default / broad), auto-applying `<select>`s, matching the sandbox
conjunction panel's own convention exactly — the locked decision from the WO1a wiring pass.

Start from the WO1a pattern: round fractions of each facet's **own corpus spread**, with the middle
level as the shipped default. Derive from the L06 distribution; do not assert.

One proviso that WO1a did not need, and this lens does:

- **Set defaults against the observed *joint* admission rate, not the product of the two bands'
  individual rates.** The facets correlate at 0.54, so the second band frequently admits what the first
  already did — the set will be **larger** than an independence assumption predicts. Knobs tuned on
  per-facet spread alone will therefore run looser than intended. Measure the joint rate across a
  spread of query basins and let that inform the middle level.
- Report the resulting typical set size as a **fraction of the ~16,397 L06 basins**. Unlike the WH
  Cities corpus (where a comparable band admitted 9–14% and argued for a top-N presentation), a
  basin-scale set of a fraction of a percent reads as properly selective — the existing "matches 38
  basins" headline is the right shape here. Do not import the WH Cities caution.
- **Thresholds are never set by map inspection.** Derive from the distribution, then look at the map to
  check plausibility — in that order, and the findings say which number came from which step.

## Part C — the two fixtures (the generalization check)

The standing rule from WO1a applies to any terrain lens on this project: **a rugged query and a flat
query, at the same default knob settings, no per-fixture tuning.** Single-fixture validation is exactly
how the 400m gate slipped through.

- **A rugged fixture** (an Alpine basin, or Tbilisi's own L06 basin — already in the corpus and already
  the project's canonical terrain case) → terrain-coherent high-relief neighbours.
- **A flat fixture** (a large lowland plains basin) → terrain-coherent low-relief neighbours. This is
  the generalization gate.

Plus the check Karl named in the session opener, folded in here rather than run separately: does the
lens **actually discriminate** — does the rugged query's painted set visibly exclude the flat regions
and vice versa, or is aggregate relief too lossy to separate them even coarsely? If it cannot, that is
the finding, and it is worth knowing before the panel is wired.

Provisos:

- **Select fixture basins by area quantile from the table, then see what is there** — do not
  coordinate-pick and hope. HydroBASINS delineates by drainage topology, so a point in a small
  landscape can land in a very large basin (WO2a's Innsbruck case, 25,920 km²).
- Include a **large flat** basin among the fixtures, not only a flat one. WO2a established the area
  effect on `relief_range` is real but secondary; this is where it would show up in the product if it
  shows up anywhere.

## Part D — wiring

"Terrain regime" added to the Similarity panel's Lens dropdown; two knobs appear when it is selected;
adjusting a knob re-queries and repaints. Headline line, span-in-km, weaker/stronger ramp, unpainted
outside the set — all as the existing lenses do. Guide language per *What this is not* above.

Karl reviews in the browser before any commit.

## Accept gate

**Both fixtures — one rugged, one flat, at the same default knob settings with no per-fixture tuning —
paint terrain-coherent, visibly different sets; the defaults are derived from the corpus distribution
and the observed joint admission rate, not from map inspection; the lens is selectable in the panel
with two auto-applying knobs; and the guide language states plainly that this is basin-level elevation
level and range, not ruggedness and not within-basin position.**

If the flat fixture requires different settings than the rugged one, the instrument is still
query-shaped rather than query-relative and the accept gate has not been met.

## Validation order

1. Build the tolerance core against the L06 facets (Part A); confirm the serving path convention.
2. Derive the three knob levels from the corpus distribution and the joint admission rate (Part B);
   report to Karl.
3. Run both fixtures at shared defaults (Part C); report set sizes, spans, and neighbour plausibility.
4. Karl accepts the defaults; then wire (Part D); Karl reviews in the browser.
5. Findings to `wo3_findings.md`; tracker roadmap row, *Last updated* stamp, and any settled forward
   note into *Locked decisions* / *Deferred* in the same edit.

## Notebook conventions

Continues `notebooks/cdop/citykin/wo2-3_terrain_basin.ipynb` (renamed from `wo2_terrain_basin.ipynb`
once WO3 joined it, since it covers both WOs). `# Cell N`
first line of every cell; SQLAlchemy warning suppressed in DB cells; `print(df.to_string())` for
tabular output; standing figure-render pattern for any map. Karl runs cell by cell and reports output —
no number asserted as a finding before Karl has shared it.

## Forward — not this WO

- **L08.** Same facets, same core, finer basins; `relief_range`'s area effect is weaker there (WO2a),
  and the knob levels will need their own derivation rather than inheriting L06's. Not in this WO's
  gate.
- **The residual facet** (`relief_range` regressed on `slp_dg_sav`) — named in `wo2a_findings.md`
  § Open. Tension to weigh if it is taken up: its zero point is corpus-relative and differs by level,
  while every other facet in this lens family is query-relative and in physical units.
- **Fine-grained ruggedness / roughness / TRI**, and any within-basin landform composition — needs
  cell-level data. Post-Braga. The EarthEnv topography suite is a candidate substrate under separate
  evaluation; **nothing in WO3 anticipates it**. A floor built on aggregate columns is coherent; a
  floor that half-anticipates a substrate it does not have is neither.
- **Neighbour-relative facets** (is this basin low or high relative to what surrounds it) — the Tier-2
  containment question. Named, not scoped, not this WO.**