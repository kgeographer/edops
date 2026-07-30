# CITYKIN WO2a — findings

Technical record for the WO2a diagnostic probe: does basin relief-range measure terrain, or basin
size? Extended by WO2b (Opus's follow-up, below) — the correlation between the two facets that
actually ship, and a correction to how the Kansas basin is cited. Tracker:
`docs/cdop/citykin/CITYKIN_tracker.md` (summary + pointer only). WO: `docs/cdop/citykin/
wo2a_basin-relief.md`, `docs/cdop/citykin/wo2b_followup.md`. Notebook: `notebooks/cdop/citykin/
wo2-3_terrain_basin.ipynb` (Cells 1–10, all run — renamed from `wo2_terrain_basin.ipynb` once WO3
also came to live in it). No exec summary for either (Karl).

---

## Why

WO2 proposes `relief_range` (`ele_mt_smx − ele_mt_smn`) as one of two facets for the coarse basin-scale
Terrain regime lens. `smx`/`smn` are order statistics over a basin's pixels: a larger basin draws more
pixels, pushing the expected max up and the expected min down before any real difference in terrain,
plus a real longitudinal gradient a small basin can't accumulate. Whether that confound is large
enough to matter was a magnitude question, not presumed — this WO measured it, at both L06 and L08.

## Part A — the sample

All L06 (16,397) and L08 (190,675) basins: `ele_mt_sav`/`ele_mt_smn`/`ele_mt_smx`, `slp_dg_sav`
(stored ×10, converted on read), `sub_area`. `-9999` masked to NaN (302 L06 / 6,390 L08 basins,
`slp_dg_sav` only — Greenland). L08 additionally turned up 6 basins with `sub_area <= 0`
(divide-by-zero into `log10`, caught rather than suppressed) — a genuine zero/negative-area edge case
at the finer resolution, not the `-9999` sentinel; masked the same way, negligible (6/190,675).

## Part B / C — the three readings, both levels

| Reading | L06 (n=16,095) | L08 (n=184,285) |
|---|---|---|
| corr(relief_range, slp_dg_sav) — redundancy | **0.739** | **0.809** |
| corr(relief_range, log_area) | 0.322 | 0.260 |
| corr(slp_dg_sav, log_area) | 0.124 | 0.090 |
| partial corr(relief_range, log_area \| slp_dg_sav) | **0.344** | **0.320** |
| diagnostic cell: large-area/low-slope vs small-area/high-slope | 382.9m vs 1467.6m (gap −1084.8m) | 143.2m vs 959.4m (gap −816.2m) |

**Scale-conditionality check (Part C's purpose) passed as predicted**: L08's narrower area spread
produced a *smaller* confound on both measures that carry a comparable one — partial correlation
dropped (0.344 → 0.320) and the diagnostic gap shrank (−1084.8m → −816.2m) — consistent with area
being the real mechanism, not an artifact of one scale. The one number that moved the *other* way is
redundancy itself: relief-range and slope grew more entangled at the finer resolution (0.739 → 0.809),
not less.

At both scales the diagnostic cell clearly favors relief-range's primary terrain signal: going from
flattest to steepest slope quartile multiplies mean relief 15–25× at fixed area; going from smallest
to largest area at fixed (flat) slope only multiplies it ~3.7–4.6×. Slope dominates by an order of
magnitude. The area effect is real, not fictional, but secondary — concentrated in the low-slope end
(a large, genuinely gentle basin still reads higher relief than a small gentle one).

## WO2b — the shipping-facet correlation (Opus follow-up)

WO2a's redundancy reading (above) was `corr(relief_range, slp_dg_sav)` — but `slp_dg_sav` is not a
WO2 shipping facet. The correlation the lens actually depends on, between the two facets that do ship,
is lower: **`corr(ele_mt_sav, relief_range) = 0.541` (L06) / `0.566` (L08)**, confirmed against a
hexbin scatter (`output/cdop/citykin/wo2b_shipping_facet_scatter.png`) so the shape is visible, not
only the coefficient. The pair that actually goes into the lens is less entangled than the WO2a
correlation implied — if anything this strengthens the case for keeping both facets, not weakens it.

This number is a description informing the lens's guide language and knob defaults, not a gate — it is
never compared to the project's 0.70 Mahalanobis/drop bar, for a reason WO2a didn't state: that bar
corrects double-counting in a **compensatory** (quadrature-sum) distance. WO2's lens is a
**non-compensatory tolerance-band conjunction** — each facet is its own independent in/out test, so
correlation between bands distorts nothing about the distance. What it costs is **selectivity**: the
second band will frequently admit what the first already did, at a rate that tracks this correlation.
Karl's call on the consequence: 0.541/0.566 reads as **moderate — the two bands do independent work**,
not near-duplicate; no caveat needed in the guide language, no case for a third facet on this evidence.
Practical note carried to WO2's design (Opus): derive tolerance-band defaults against the **observed
joint admission rate**, not against the two bands' individual admission rates multiplied together —
the correlation means the conjunction won't be as selective as independence would suggest, and knobs
set assuming independence will end up looser than intended.

## Named-basin plausibility check — partial miss, one clean illustration

Five coordinate-picked basins meant to span the area×terrain grid (Cell 5). Two of five landed in
basins that didn't match their intended size label — a small Alpine point (Innsbruck) landed in the
*largest* basin in the set (25,920 km²), and a small-lowland point (Netherlands polder) landed larger
(6,727 km²) than either "large lowland" pick (Amazon 3,485 km² / Congo 4,384 km²). HydroBASINS
delineates by drainage topology, not local landscape scale, so a coordinate doesn't guarantee the
intended basin size at L06 — a selection error, not a data problem; the size axis of this check is
inconclusive as designed.

One clean illustration survived it regardless: the western-Kansas basin (hybas_id 7060622710, 33,460
km², the largest of the five, nearly flat at 0.5° mean slope) posted **642m of relief**. WO2b (Cell 10)
placed it against two conditional expectations rather than one, since a single basin cited for two
different conclusions (confound illustration vs. keep-relief illustration) can't honestly serve both:
relief expected given slope alone, corpus-wide (206.9m — Kansas exceeds by 435.1m), and relief expected
given its own area-and-slope-quartile cell jointly (382.9m — Kansas exceeds by 259.1m).

Opus's read of that pair, corrected against a first pass that forced a binary "confound or distinctive"
call the data doesn't support: **it's a mixture, and both parts are real.** Of Kansas's 435.1m excess
over the slope-alone expectation, 176.0m (~40%, the gap between the slope-alone and joint expectations)
is attributable to its being in the largest area quartile; the remaining 259.1m (~60%) is not explained
by either its slope or its area quartile — genuinely locally distinctive. **The honest citation**:
Kansas is distinctive beyond what area alone explains, with the area contribution named rather than
left out — still a keep-relief case, just not an unqualified one, and more persuasive for saying what
it accounted for.

## Decision — both facets kept; `relief_range` is not replaced

Against WO2a's own decision rule: the diagnostic-cell test favors keeping `relief_range` clearly at
both scales (does not trigger "slope replaces it"); the partial correlation (0.32–0.34) is real but
not the kind of number that forces "substantial" on its own. The one bright-line trigger was the
redundancy clause — both scales clear the project's standing 0.70 Mahalanobis/drop bar (used
throughout WO8/WO1a), which reads as "pick on redundancy, prefer the area-invariant one" — i.e.
replace `relief_range` with `slp_dg_sav`. **WO2b corrected this evidence**: that redundancy reading
was against `slp_dg_sav`, which isn't even a shipping facet — the pair that actually ships correlates
at 0.541/0.566 (§ WO2b above), well under the bar on its own terms. The bright-line trigger for
replacement doesn't survive contact with the right pair of variables, independent of the argument
below.

**Karl's call, unchanged and now doubly supported: don't replace. Keep both facets.** The
redundancy-threshold logic that would drop `relief_range` is imported from a prediction-modeling
tradition, where shared variance between two variables is treated as inefficiency to collapse —
multicollinearity destabilizes a model's coefficients and burns degrees of freedom, so dropping the
redundant one is the right move *for prediction*. EDOPS is not doing prediction; the instrument's job
is description/characterization. Under that job, a global correlation describes a *mean* relationship
across a corpus with real, expected spatial heterogeneity — it doesn't mean the two variables carry no
distinct local information. The residual — where a basin's relief diverges from what its own slope
would predict — is precisely the locally distinctive signal a characterization tool should be able to
surface, not the noise a prediction tool would be right to discard. Kansas (§ Named-basin plausibility
check, above) is the concrete case, correctly qualified: ~60% of its apparent excess relief is not
explained by either its slope or its area — exactly the kind of basin a drop-to-slope facet would
flatten into indistinguishability from any other gentle basin its size.

This is also not a new question for the project — it was already settled once, for the signature
itself: `CLAUDE.md`'s standing rule (never remove EDOPS signature variables based on global
co-variation; L8 basin signatures need local character even when globally redundant) makes the
identical argument this WO just re-derived for a lens instead of the signature. And the method was
already inconsistent about it in a way that argues against using the threshold as the decision
mechanism at all — independent of WO2b's correction below: WO1a kept `grid_elev_mean` and
`relief_range_m` together in the terrain lens at r=0.62 (under the bar, no drop triggered); WO2a's
(subsequently-corrected) redundancy reading, crossed at 0.74–0.81, would have triggered a drop for a
pair whose descriptive value didn't actually change — only where the number landed relative to an
arbitrary line did. WO2b independently found a second reason the same bar doesn't apply here at all
(§ WO2b above): it's built for compensatory quadrature-sum distances, and WO2's lens isn't one.

Karl, on the general principle (worth keeping on record — this is a recurring stance for the project,
not a one-off): his work as a data modeler/ontologist is, half-jokingly, "making trouble for
cartographers" — the better the model, including often the *less* information lost, the more analysis
it can support down the line. He trusts cartographers and dataviz work to find ways of translating
that complexity into visual media; the risk he wants EDOPS to avoid is deciding, upstream in the data
model, that the complexity wasn't worth keeping in the first place.

**WO2's actual facet set is unaffected in scope**: both `ele_mt_sav` and `relief_range` (not
`slp_dg_sav`) ship as WO2's coarse two-facet floor, as originally proposed — this WO's job was to
check whether that proposal was safe, not to change it, and it is.

## Open / carried forward — for WO2's actual design

- **The residual-facet idea.** Rather than a binary choice between `relief_range` and `slp_dg_sav`, a
  facet built from the **residual of `relief_range` regressed on `slp_dg_sav`** would split the
  generic, slope-predictable component from the locally distinctive one explicitly — giving the lens
  access to "how much more/less relief this basin has than its own slope would suggest" as its own
  dimension, rather than leaving that signal either buried inside a correlated raw variable or
  discarded by a drop-to-cleaner-variable move. Not scoped or built here — WO2's own two-facet floor
  doesn't need a third knob to satisfy this WO's accept gate, and adding one needs its own
  justification per the tracker's standing decision on that. Tension to weigh when it's taken up
  (Opus, WO2b): its value is corpus-relative — the zero point is an artifact of a global regression,
  differing between L06 and L08 — while every other facet in this lens family is anchored
  query-relatively, in physical units. Named as a candidate, not a requirement.
- **Derive tolerance-band defaults against the observed joint admission rate, not assumed
  independence** (Opus, WO2b). `corr(ele_mt_sav, relief_range) = 0.541/0.566` means the second band
  will frequently admit what the first already did — multiplying the two bands' individual admission
  rates will overstate how selective the conjunction actually is, and defaults set that way will end up
  looser than intended. A design constraint for WO2's tolerance-knob defaults, not a reason to change
  the facet set.
- **Fixture selection for WO2's smell test**: select basins by area quantile from the table, then see
  what's there — do not coordinate-pick and hope (Opus, WO2b). WO2a's named-basin check was
  inconclusive on its size axis for exactly this reason: HydroBASINS delineates by drainage topology,
  so a point in a small landscape can land in a very large basin (Innsbruck, 25,920 km²).

## Not resolved by this WO

- WO2's actual lens design (tolerance knobs, defaults, paint-a-set head, guide language) — WO2 itself.
- The basin-scale discrimination smell-test (Alpine vs plains, plausible neighbors) named in the
  session opener — tests the lens as a whole, not this WO's single-ingredient question.
- The three items above — all named, none designed or built.
