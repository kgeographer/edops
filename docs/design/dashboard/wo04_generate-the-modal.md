# WO-04: can we generate the modal?

Draft 2026-11-04, for Karl's review. Goal-setting, not a specification. Accompanies `modal_dummy.md`. (This takes the WO-04 number; the sweeps listed at the end of `profile_questions.md` move to a later WO.)

## Goal

`modal_dummy.md` imagines the contents of the WHG [Environmental Profile] modal: eight sections of templated sentences, with a Timbuktu example whose values are partly invented. Find out how much of it EDOPS can generate with confidence, sentence by sentence, from data it has or could reasonably get. The answer shapes the payload proposal and the v1 hours.

## The question for each sentence

Treat each sentence, and each optional [bracketed] part and slot within it, as a unit. Give each unit one verdict:

- **yes**: a deterministic rule can fill it from data EDOPS already holds, at L6, for most places, and the values check out at the test places.
- **maybe (needs X)**: possible once X exists. Name X specifically. Typical kinds:
  - a cutoff and a sweep, for any verdict word (stands out, much larger, resembles, mainly, near);
  - a glossary entry (what high or zero means, units, area covered);
  - a field computed from data we have but do not compute yet;
  - new data, named, with a likely source;
  - code, such as precomputation for speed.
- **no**: not feasible for v1, with the reason.

**What to audit.** The templates are the object. The Timbuktu examples are illustrations, and their values are not to be checked. Where an example says something its template does not (for instance "a narrow corridor", or "wetter than the desert basins to the north"), treat that sentence as an extra unit: it shows a kind of statement wanted.

**Unit ids.** Number the units by section and position (S1.1, S1.2a, ...), and return an annotated copy of `modal_dummy.md` with the ids marked, so every row in the results points back to its place in the dummy.

Where a small change of wording would move a unit up a level (for example "near the coast" to "{distance} km from the coast"), say so and give the reworded version. Rewording to fit the data is welcome; it is the point of the exercise.

## Things to watch

- **Point, basin and ring are different things.** "Timbuktu sits at about 260 m" is a point value; basin values describe an area the place may sit at the edge of (WO-03: World Heritage Cities sit a median 7.6 km from their basin's outline). Say which each unit needs and whether we have it.
- **Every comparison word is a cutoff.** "Among the driest", "stands out", "resembles its neighbours", "much larger", "mainly sandy" all hide thresholds. Identify the quantity and what a sweep would vary. Do not choose cutoffs.
- **WO-02 hazards apply.** Zero-aware variables, unknown zero fraction (`reservoir_vol`), spatial dependence (neighbours resemble the core, so contrasts are easy to manufacture), units and area covered.
- **WO-03 findings apply.** No per-neighbour compass words (D2); flow relation is reliable; three meanings of "coastal" (I-7); the -9999 class (I-3); Kaifeng-type cases where the nearest large river is not the basin's own.
- **The ecoregion gist.** The template takes a phrase from the ecoregion summary. Say whether that is a lookup (a stored short description), or needs text generation; generation from anything other than the fact list departs from a locked decision, so flag it rather than solve it.
- **Direction words** ("to the south-west", "the basins to the north"). Say what, if anything, can support them, given D2.
- **Elevation and terrain.** The point's elevation, and the basin's elevation, slope and roughness (the Terrain lens on the Similarity tab), are different values. Report what is stored for L6 basins and where, and where the point's elevation would come from: a DEM sample at the point, or WHG itself, which already shows elevation on its place pages.

## Published classification schemes

This is a main line of inquiry, not a side note. Wherever a template uses a class word (flat or mountainous, sandy, arid, cropland), an established, citable classification may supply the word in place of a cutoff we would have to choose and defend. A class read from a published scheme is a categorical fact, which fits the locked decision (no verdict words of our own) better than a threshold we set.

For each class word in `modal_dummy.md`:

1. **Is a class field already in the data?** HydroATLAS carries several class fields, for example climate zones, biomes, land cover, lithology, wetland types and potential natural vegetation (CC confirms what is loaded and how it is stored). These may already be **yes**.
2. **If not, is there a published scheme whose inputs we have?** Candidates to check, not a list to adopt: the UNEP aridity zones on the aridity index; USDA soil texture classes from sand, silt and clay shares; Köppen-Geiger climate classes; relief classes such as Meybeck's or the Iwahashi and Pike landform types.
3. **Does the scheme fit our unit?** Many schemes are defined for grid cells or points, not for averages over a basin. Applying a cell-level scheme to a basin mean changes what the class means (a basin of mixed hills and plains may average out as "rolling"). Say whether the scheme can be applied to a basin's distribution (for example, the share of the basin in each class) rather than to its mean.

The word lists in the dummy are placeholders. Where a scheme fits, its own class labels replace them, even if they read less smoothly; say so in the row.

Record the citation for each scheme. A sweep may still be worth running to show how sensitive the class is, but the cutoff is no longer ours.

## Evidence

Use the WO-03 test places: Timbuktu, Tbilisi, Santa Fe, Kaifeng, Lviv, Poltava, Chaco Canyon, Alexandria, Utqiaġvik, and the island town. Write a throwaway script, without any LLM, that fills every **yes** unit from real data for each test place, and leaves each **maybe** or **no** unit as a visible placeholder naming what is missing. These filled modals are the main evidence; they show what the modal would look like now. Check the filled values against what is known about each place, and report anything wrong or odd.

For "most places", a quick check of how often each **yes** unit can be filled across the WO-02 population sample is enough (a fill rate, not a study).

## Provisos

- Read-only against the local database and server; record the commit.
- Scripts and notebooks wherever WO-03's went.
- No engine, endpoint or Sandbox changes. No cutoffs chosen. No prose polishing beyond what a template needs.
- Where a unit needs new data, name the dataset and its likely source, and stop there.
- Effort for each **maybe**: a rough size (small: hours; medium: a day or two; large: more), labelled as a guess.

## Deliverables and gate

- `wo04_summary.md`: one page, read first. A table of the eight sections with counts of yes, maybe and no; the largest gaps; the rewordings that would gain most.
- `wo04_results.md`: one row per unit: section, unit, verdict, data or field it reads, what is needed, effort, notes; then issues found.
- `wo04_modals.md`: the filled modals for the test places.
- `modal_dummy_annotated.md`: the dummy with unit ids marked.
- `wo04_schemes.md`: one row per class word: the word, a class field already in the data (if any), candidate published schemes, inputs present or missing, whether the scheme fits a basin, citation, recommendation.

**Gate:** every unit in `modal_dummy.md` has a verdict with its reason, every class word has a row in `wo04_schemes.md`, and the filled modals exist for all test places.

