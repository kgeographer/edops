# dash WO-01: the summary at Level 08

Draft of 14 Nov 2026, by Fable for Karl's review. Experiments and queries only; nothing in the app changes.

## Goal

Find out whether the rule-written summary (the WHG profile text) can follow a user from Level 06 to Level 08 in the Dashboard, and what that would cost. The results decide two things: how the summary behaves when Level 08 is chosen, and whether Level 08 profiles are generated and stored as Level 06 ones will be.

## Background

- The Dashboard is the Sandbox reshaped. Its working direction (pre-design, 14 Nov) is prose first: a user picks a place and reads a summary, with the full signature underneath.
- The summary is the profile the generator writes from `profile_templates.md`. Profiles are to be stored for all Level 06 basins. The Sandbox also offers Level 08, where no profile exists.
- Four behaviours at Level 08 are on the table:

  | Option | At Level 08 |
  | --- | --- |
  | Goes away | A line says the summary describes Level 06 basins only |
  | Stays, as the wider basin | The Level 06 summary remains, headed as the Level 06 basin that contains this one |
  | Generated on request | The rules run on the Level 08 signature |
  | Stored for Level 08 too | As at Level 06, for 190,675 basins |

- Known from earlier work: biome and aridity both change between Level 06 and Level 08 at Tbilisi. How common that is has not been measured.
- The summary stays within bands A to E. Statements about time-varying values are out, by decision.

## Items

1. **Generation time.** Time the generator per place, broken down by stage, over the ten WO-09 places and a sample of about 50 further basins. State which stages call anything outside the database (point elevation, for example), since a network dependency bears on a bulk run. From the timings, estimate a full run for all 16,397 Level 06 basins and for all 190,675 Level 08 basins. Describe what a run of that length would need to be safe (resumable, logged, checkable afterwards). Describe only; do not build it.

2. **Point units and basin units.** List every unit of the profile as one of: describes the place's point, describes the basin, or needs both. My reading is that point elevation (S1.1b), the point's ecoregion (S1.2a), the river distances (S3.1, S3.3) and the moved-point and point notes (S8.3, S8.point) are point units; confirm or correct. Then say how a store keyed by basin serves the point units when a profile is requested for a place, and what that costs per request.

3. **The generator at Level 08.** Run the generator at Level 08 for the ten places and set each result beside its Level 06 text. List every sentence that is wrong, empty, or true but odd at Level 08, with the rule responsible. Rules I would expect to need a look: the water classes (S3.2, whose small-catchment cutoff differs by level in the Analysis rule), the headwater test, the comparisons with neighbouring basins (S2.3, S5.2, S6, where "all but one" needs five basins with a value), the 10% limit on other ecoregions (S1.4) and "much larger river" (S3.3). If the generator cannot take a level today, say what it took to make it run, and keep that change out of the Level 06 path.

4. **Disagreement between levels.** For a sample of places, compare the Level 06 and Level 08 basins that contain the same point, and count how often each class-based statement changes: the UNEP aridity class, the seasonality class, the water class, the basin's majority ecoregion, the slope class, the soil texture class, the leading rock type, the commonest land cover class, and where the basin drains. Add any other class-based statement the templates hold. Report a rate per statement and the share of places where at least one changes. For the sample, the 306 basins of WO-02 with a point inside each would do, and so would the World Heritage cities already linked to Level 08 basins, which are real settlements; choose one or both and say why.

## Provisos

- No changes to `profile_templates.md`, the stored profiles, the `/whgmodal` endpoint, the `/profiles` page, the Sandbox or the engine. Level 06 output must regenerate identically after this work.
- Report rules that misfire; do not fix them. Report cutoffs that look wrong at Level 08; do not tune them.
- Report source values as they are, odd ones included.
- Work in a notebook or scratch scripts. Any table written is scratch and named as such.
- Karl and CC choose the branch.

## Out of scope

Storing Level 08 profiles; wording changes; statements about Band T; the Dashboard's layout; buffers, rings and polities.

## Deliverables and gate

- `dash_wo01_summary.md`, one page: for each item, the answer in a sentence or two and the figure behind it.
- `dash_wo01_results.md`: the four items in order, the side-by-side texts for item 3, the tables for item 4, and a short list of anything that needs attention.
- The notebook or scripts.

Gate: Karl reads the summary and chooses the Level 08 behaviour and whether Level 08 profiles are stored.
