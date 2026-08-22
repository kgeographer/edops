# Caveats and limits

EDOPS is a research prototype and work in progress, now at v0.4. Some signature variables and platform features planned for a Spring, 2027 v1.0 release are in development. Some limitations of the current release and overall project are listed below.

The design choices behind the framework, e.g. why basins, why two scales, why bands, are discussed in [Premises and commitments](commitments.md). Limitations of the source datasets rather than to EDOPS are described alongside each source in
[Data sources](../data-sources.md), worth reading particularly before relying on the current historical layers.



## Spatial coverage

**Some small islands are missed.** The basin framework is built from terrestrial drainage. Islands below
the delineation threshold do not appear, so places on them do not resolve.

**Coastline precision is unverified.** Basin boundaries at the coast inherit whatever the source
delineation did there. We have not yet analyzed how good this is. Treat coastal basin extents as approximate.

**Maritime environments are absent entirely.** Nothing in EDOPS describes what is offshore. For a
coastal settlement, important environmental attributes are missing, Bathymetry and shelf characterisation are planned, but absent so far. Derived measures of fishery potential or port suitability will need to be defined.

**Terrain is described, accessibility is not.** Elevation and relief are useful descriptors of a
landscape, but measures of the the cost of crossing it are lacking and would be a useful addition.

## Temporal coverage

**Most variables are contemporary.** The bulk of the EDOPS catalogue comes from BasinATLAS data and describes a recent baseline. Grouping of variables in "persistence bands" (see [Premises](commitments.md)) imparts some rubric for how far back in time each can reasonably be carried, but ony Band T holds the variables that are genuinely time-indexed.

**Band T sources cover different spans** at different resolutions, so a single query date or timespan will return values from some temporal datasets and not others. Coverage per source is in [Data sources](../data-sources.md).

**BCE handling.** For the HYDE and eVolv2k datasets, dates before year 1 use astronomical year numbering (year 0 = 1 BCE, year -1 = 2 BCE), not traditional historical calendars' no-year-zero convention. These are annually-resolved reconstructions, so a one-year offset in labeling isn't meaningful next to the datasets' own uncertainty. 

**Global only, by design and by constraint.** For an ostensibly historical resource we are doing
what we can with what exists globally. Regional paleoenvironmental reconstructions are often better
than anything global, but we are not using them at this time. Mixing regional coverage into EDOPS' global framework is under consideration, but would raise significant data-architecture and interface issues. Pointers to global
datasets we have missed are welcome.

## Known data anomalies and defects

**Endorheic basins and `dist_sink`.** In closed basins the terminal sink is not the ocean, so distance-to-sink does not mean what it means for the exorheic case - it measures distance to that system's own terminal sink (e.g. a lake, playa, salt flat)


## Interpretive limits

These are properties of the instrument.

**A basin value is not a site value.** Basin summaries can be poor descriptions of any particular location inside them, and the disagreement grows with basin size and internal heterogeneity. This is flagged at the point of use throughout the interface.

**Level 6 and level 8 basins can disagree** about the same place. This well-known effect of alternative aggregation scale and shape is termed the Modifiable Areal Unit Problem (MAUP). Because a basin summarizes each measured property into a single value, larger units fold in more internal variation than smaller ones. In EDOPS, Level 8 describes a more immediate character of a location than the larger Level 6, which situates it in a broader context. Both are valid; they answer different questions, not the same question at different resolutions.

Which to choose follows from the reach of the process you are asking about, not from the size of the place. A settlement's immediate terrain and agricultural land are Level 8 questions. Its water supply may originate far upstream, which is a Level 6 question even for a single point — the water-provenance classification can return "Undetermined" at Level 8 when the upstream catchment is too small to resolve distant sources. The two levels disagreeing sharply is itself informative: it says the place sits in a landscape that is heterogeneous at that scale. Fuller guidance on choosing a level is planned.

**A modelled value is not an observation.** Sources in band T - Temporal are reconstructions — estimates produced
by a model under stated assumptions — but they render exactly like measured attributes. What a given
value is, and how it was produced, is recorded in the [Codebook](../codebook.md) and in
[Data sources](../data-sources.md).

**Correspondence is not cause.** Where EDOPS supports comparison between environmental and cultural
data in the Workbench page, a correspondence is a starting point for interpretation, not evidence about mechanism or
direction.
