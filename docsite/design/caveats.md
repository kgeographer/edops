# Caveats and limits

Known gaps and defects in EDOPS v0.4. The design choices behind the framework — why basins, why
two scales, why bands — are in [Premises and commitments](commitments.md); this page is about where
the data thins out or misbehaves.

EDOPS is a research prototype. Nothing here is a stability guarantee.

## Spatial coverage

**Small islands are missed.** The basin framework is built from terrestrial drainage. Islands below
the delineation threshold do not appear, and places on them do not resolve.

**Coastline precision is unverified.** Basin boundaries at the coast inherit whatever the source
delineation did there. We have not characterised how good this is, and it is probably not good.
Treat coastal basin extents as approximate.

**Maritime environments are absent entirely.** Nothing in EDOPS describes what is offshore. For a
coastal settlement, the half of the environment that may have mattered most — fisheries, shelf
productivity, whether the site is usable as a harbour at all — is not represented. Bathymetry and
shelf characterisation are wanted; port suitability would need a definition we do not yet have,
since a coastline is not automatically a viable port.

**Terrain is described, accessibility is not.** Elevation and relief say something about a
landscape, but not about the cost of crossing it. A walking-distance or terrain-cost measure would
be a substantial addition and is not present.

## Temporal coverage

**Most variables are contemporary.** The bulk of the catalogue describes a recent baseline.
Persistence bands (see [Premises](commitments.md)) indicate how far back each can reasonably be
carried; Band T holds the variables that are genuinely time-indexed.

**Band T sources cover different spans**, so a single query date will return values from some
temporal datasets and not others. Coverage per source is listed in
[Data sources](../data-sources.md). {verify: state the three ranges — LMR v2.1, HYDE 3.4, eVolv2k v4}

**{verify: BCE handling}** — how dates before the common era are accepted and interpreted, and any
known rough edges.

**Global only, by design and by constraint.** For an ostensibly historical resource we are doing
what we can with what exists globally. Regional paleoenvironmental reconstructions are often better
than anything global, and we are not using them: mixing regional coverage into a global framework
raises data-architecture and interface problems — what a user sees when their query falls inside a
well-covered region versus outside one — that v0.4 does not attempt to solve. Pointers to global
datasets we have missed are welcome.

## Known data defects

**Endorheic basins and `dist_sink`.** In closed basins the terminal sink is not the ocean, so
distance-to-sink does not mean what it means elsewhere. Band E variables should be read with this
in mind for any basin without a marine outlet. {verify: exact current behaviour — undefined, or
distance to terminal lake?}

**{verify: any others.}** Candidates from earlier notes not yet confirmed as still live.

## Interpretive limits

**A basin value is not a site value.** Basin summaries can be poor descriptions of any particular
location inside them, and the disagreement grows with basin size and internal heterogeneity. This
is flagged at the point of use throughout the interface and is worth taking literally.

**Level 6 and level 8 can disagree** about the same place. That is a real property of the landscape
rather than an error, but it means a single-level result should not be reported as though it were
the value for that place.

**Correspondence is not cause.** Where EDOPS supports comparison between environmental and cultural
data, a correspondence is a starting point for interpretation, not evidence about mechanism or
direction.