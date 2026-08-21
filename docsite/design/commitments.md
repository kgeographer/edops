# Premises and commitments

EDOPS makes a small number of consequential choices about what to measure, over what units, and
with what warrant. None of them is neutral, and each closes off alternatives worth naming. This
page sets them out so that results can be read against the assumptions that produced them.

Known defects, coverage gaps, and dataset-specific problems are a different matter and are
collected under [Caveats and limits](caveats.md).

## Attestation, not ground truth

EDOPS does not assert environmental facts on its own authority. Every value it serves is traceable
to a source that produced it, by a method that source documents. The service resolves a place to a
spatial unit, retrieves what the sources say about that unit, and reports it with provenance. It
does not adjudicate between sources, correct them, or present a synthesis as though it were a
measurement.

This is a claim about the service's role, not about the quality of the underlying data — and the
distinction matters, because the data varies enormously in kind. Elevation derived from digital
terrain models is about as close to direct measurement as environmental data gets. Cropland extent
in 3000 BCE, from HYDE, is a model output carrying substantial uncertainty. Paleoclimate fields
from LMR are reconstructions with quantifiable ensemble spread. EDOPS treats all three the same
way: it serves them, attributes them, and leaves the assessment of their standing to the person
using them.

Aggregation is what makes even the measured variables into attestations rather than observations.
A satellite measures reflectance at a pixel; BasinATLAS reports a mean, a maximum, or a majority
class over a basin. That basin-level value is not wrong, but neither is it a measurement of
anything a person could go and stand on. It is a statement about a unit that somebody chose, under
an aggregation rule that somebody selected. Both choices are recoverable, and both are consequential
— which is the subject of the two sections below.

Readers who know the [Linked Places Format](https://github.com/LinkedPasts/linked-places-format) or
the World Historical Gazetteer will recognise the move. A gazetteer built on attestation does not
tell you where a place was; it tells you what sources say about where it was, and leaves the
reconciliation visible. EDOPS applies the same discipline to environmental description.

## The basin as spatial unit

Any instrument that reports environmental attributes for arbitrary places needs a space-filling
partition of the terrestrial surface to report them over. The realistic candidates are
administrative units, a discrete global grid, or hydrological basins.

Administrative units are unusable for this purpose. They are the wrong shape, they change over
time in ways uncorrelated with anything physical, and their boundaries reflect political history
rather than environment. Discrete global grids are geometrically well-behaved and carry no
environmental meaning whatsoever; a hexagon is a hexagon wherever it falls.

Hydrological basins are different in kind. Their boundaries are derived from terrain rather than
imposed on it: a drainage divide is a physical feature, and the partition is a consequence of the
landscape rather than a convenience laid over it. Since water availability is among the most
consequential environmental facts for human settlement, agriculture, and movement, a partition
organised around drainage is defensible as a framework for exactly the questions EDOPS exists to
support.

The basin also brings something no grid or polity has: **a relation**. Basins nest, and water
flows between them in a known direction. That drainage topology is what makes it possible to
distinguish what a place has locally from what its upstream catchment supplies — the distinction
EDOPS reports as *local* versus *upstream* values, and the basis of its water-provenance
classification. A grid cell has neighbours; a basin has a headwater and an outlet.

This choice has costs, and they fall unevenly. Coastal and island societies are poorly served: a
partition organised around inland drainage has little to say about maritime environments, and some
places do not resolve to a meaningful basin at all. Basins can also be internally heterogeneous in
ways that make a basin-level summary a poor description of any particular location within it — the
subject of the next section, and a caution repeated at the point of use throughout the interface.

## Scale-conditionality

The size and shape of the units over which values are aggregated determines the values. Draw the
boundaries differently and the numbers change; draw them at a different size and they change again.
This is the modifiable areal unit problem, and it is not a flaw in EDOPS or in BasinATLAS. It is a
property of every areal summary ever computed.

EDOPS treats it as a design input rather than a caveat. Two Pfafstetter levels are served — level 6
and level 8, averaging roughly 8,232 km² and 708 km² respectively — and the interface makes the
level an explicit, visible choice rather than a hidden default. Values are reported at the level
you asked for, and switching levels is one click.

The commitment here is a refusal: EDOPS does not pick a correct scale on the user's behalf, because
there isn't one. There are questions better served by the coarser level and questions better served
by the finer one, and the same place can look materially different at each. Where the two levels
disagree, that disagreement is information about the place — it says the surrounding landscape is
heterogeneous at that scale — and the service is built to make it visible rather than to resolve it.

## Persistence bands and temporality

EDOPS exists to be useful for historical research, and historical research needs environmental
description through time. Very few global historical environmental datasets exist. Most of what is
available describes the recent past — typically a late-twentieth-century baseline — and says
nothing directly about any earlier period.

The response is not to pretend otherwise but to be explicit about how far a contemporary
measurement can be carried backward. EDOPS groups its variables into **bands**, six in all. Bands A
through D are persistence tiers, ordered by how quickly the thing a variable measures changes: at
one end, attributes effectively fixed over the whole span of human history; at the other,
attributes that change within decades.

Two bands sit outside that ordering. **Band E, coastality**, holds the variables describing a
basin's relation to the sea or to its terminal sink — distance to sink, outlet type, coastal
fraction. These are the drainage-topology attributes discussed above, the ones a grid cell cannot
have, and they are highly persistent; grouped by persistence alone they would sit near Band A. They
are broken out because they answer a different kind of question — not what a place is like, but how
it is connected. **Band T** is temporal: variables from datasets where values are indexed to time
rather than projected across it.

For Bands A through D, the band is therefore a warrant, not a category. It tells you what you are
entitled to infer about a period the measurement does not cover. A contemporary value in a
high-persistence band is reasonable evidence about conditions two millennia ago. A contemporary
value in a low-persistence band is evidence about the late twentieth century and very little else.
Reading a variable without attending to its band is the most likely way to misuse this service.

Band assignments and the reasoning behind each are given in the [Codebook](../codebook.md); coverage
and reference periods for the temporal datasets are in [Data sources](../data-sources.md).

## The service resolves; interpretation happens elsewhere

EDOPS computes and serves. It does not conclude.

There are no significance verdicts in the API, no automatic judgements about whether two places are
similar enough to matter, no thresholds encoding what counts as a meaningful difference. Where the
interface applies a threshold — a tolerance band in a similarity query, for instance — the value is
exposed as a control the user sets, not buried as a constant the service chose.

This is deliberate and it has a cost: it puts more work on the person asking the question. The
alternative costs more. A service that returns verdicts has to decide what counts as significant
for questions it cannot anticipate, and those decisions become invisible the moment they are
embedded. Keeping them at the surface, where the use case is, means they stay arguable.