# WO-06: comparing a place's basin with the basins around it

2026-11-07, reviewed by Karl. Goal-setting, not a specification. Part of the two-week plan for the sample page; target finish Sunday 15 November.

## Goal

Fill the Surroundings section, and the comparison sentences in Climate and Land cover, from real data. Today the Surroundings section prints raw counts ("upstream: 2 direct, 0 further") and four placeholders. At the end, each of the ten test places should say, in plain sentences, how its basin compares with the basins that meet it, and what, if anything, sets it apart.

The units are S2.3, S5.2, S6.2, S6.3, S6.4 and S6.5. S6.2c (a description of a neighbouring basin) stays planned unless it turns out to be easy.

## Background to read first

`profile_templates.md` (v4 or later), `wo05_filled_profiles.md`, `whg_ring_profile_spec_prelim.md` (the ring and its core-and-surroundings rules), `wo03_summary.md` and `wo03_results.md` (neighbour counts, flow relation, point contacts, the -9999 class), `profile_open_items.md`.

## The approach: facts that need no cutoff

Most comparison words hide a threshold: "stands out", "resembles", "much drier". This WO avoids them by stating only things that are true without one:

- **Extremes.** "The driest of the six basins that meet here." Being highest or lowest of the set is a fact, not a judgement.
- **Counts.** "Drier than four of the five basins around it." "On 18 of 24 measures, its values lie within the range of the basins around it."
- **All or none.** "The basins across its divides are all drier."

Where a sentence in the dummy needs a cutoff ("resembles", "stands out"), reword it into one of these forms. The wording below does this already.

## Which basins and which measures

- **Neighbours.** Every basin that shares a border with the core. Basins that touch it only at a point are left out of these sentences (WO-03: 1.5% of neighbours, all coastal).
- **Flow relation.** Upstream (drains into the core), downstream (the core drains into it), or across a divide. WO-03 found this reliable.
- **Local measures only.** Compare the basins on their own local values. Upstream measures stay in the Water section: a basin downstream of the core contains the core's catchment, so comparing upstream values across the ring measures position on the river, not difference.
- **Measures with data.** Count only neighbours that have a value: "drier than four of the five basins with data". A measure that is zero in the core and in every neighbour produces no sentence.
- **Ties.** Report equal values as equal; never turn a tie into a rank.
- **Temperature by difference.** Compare temperature in degrees, never by ratio (open item R1). This applies to the Analysis rule too.
- **Area.** Neighbours vary greatly in size (Timbuktu's northern neighbour dwarfs its core). Carry each neighbour's area in the fill notes, so a reader of the results can see when a count rests on very unequal basins. No sentence about it yet.

**Which measures each sentence draws on** is an editorial choice, not a statistical one. A first list, for Karl to change:

- S2.3 (Climate): precipitation, temperature, aridity.
- S5.2 (Land cover): cropland, pasture, population density.
- S6.5 (Surroundings): the Terrain lens measures (elevation range, relief, roughness), wetland, forest, karst, soil texture shares. This lets the setting comparison of a lowland basin among higher ones come through.
- S6.4 (Surroundings): all local measures with data.

A measure already stated in S2.3 or S5.2 is not repeated in S6.5.

## Wording: how a rank is said

**Decided (Karl, 7 Nov): option A.** The measure lists above stand as a first version. Both will be adjusted after the sample page has been seen. The options considered:

- **A. Extremes as superlatives, otherwise counts** (recommended). "It is the driest of the six basins that meet here." When not at an extreme: "It is drier than four of the five basins around it." Only the extreme is a superlative.
- **B. Counts only.** "Of the five basins around it, four are wetter and one is drier."
- **C. Ordinals.** "The second driest of six." Not recommended: an ordinal invites a reading of precision the data does not support, and ties make it awkward.

The draft lines below follow A.

## Draft template lines

These need new keys, which CC adds to the script. CC may restructure the keys, keeping the wording; anything changed is reported. Karl saves the result into `profile_templates.md` with a version bump.

Flow relation (replaces the current `S6.2`):

```
S6.2.in_none: None of them drains into it.
S6.2.in_one: One of them drains into it.
S6.2.in_some: {n} of them drain into it.
S6.2.out_one: It drains into one of them.
S6.2.out_none: It drains into none of them.
```

Comparison words, one set per measure. Example for precipitation; CC writes the others in the same pattern and lists them for review.

```
cmp.precip.top: the wettest
cmp.precip.bottom: the driest
cmp.precip.more: wetter
cmp.precip.less: drier
```

Sentences:

```
S2.3.extreme: Its basin is {cmp} of the {n} basins that meet here.
S2.3.count: Its basin is {cmp} than {k} of the {m} basins around it.
S5.2.extreme: Its basin has {cmp} of the {n} basins that meet here.
S5.2.count: Its basin has {cmp} than {k} of the {m} basins around it.
S6.3.all: The basins across its divides are all {cmp}.
S6.4: On {k} of {m} measures, its values lie within the range of the basins around it.
S6.5: Of the {n} basins that meet here, it has {list}.
```

S6.5's `{list}` joins phrases such as "the most wetland" and "the least relief". When more than one measure qualifies for a sentence, CC proposes how many to state and in what order (for example, the order of the lists above) and reports how often the limit bites.

## Housekeeping folded in

- **The -9999 class (WO-03, I-3).** Fix before any class comparison is built.
- **Temperature by difference (open item R1).**
- **The "no percentile" list (R2).** List only share and extent measures; name a measure once when its upstream version is also zero.
- **Garbled ecoregion names (E3).** Reload the 36 names with the right encoding.

## Evidence

- Regenerate the ten filled_profiles with these units built.
- Over the 306 sample basins: how often each sentence fires, how many extremes a basin typically has, how often S6.3's "all" holds, and the distribution of S6.4's count. Santa Fe should come out with few statements, Timbuktu and Tbilisi with several; say if that is not so, and why.
- Check each statement at the fixtures against what is known about the place, and report anything wrong or odd.

## Provisos

- Wording changes go through `profile_templates.md` as its header says; rules stay in the script.
- No class words (WO-07), no nearest river (WO-07), no snap.
- Read-only against the database except for the I-3 and encoding fixes; record the commit.
- Where an item needs data or code that is not there, name it and stop on that item.

## Deliverables and gate

- `wo06_summary.md`: one page, read first.
- `wo06_results.md`: the rules as built, firing rates, the measure lists as used, issues found.
- `wo06_filled_profiles.md`: the ten filled_profiles.

**Gate:** the ten filled_profiles regenerate from the current template version with S2.3, S5.2, S6.2, S6.3, S6.4 and S6.5 filled wherever they apply and silent where they do not; firing rates over the 306 basins are reported; the four housekeeping items are done or their blocker named.