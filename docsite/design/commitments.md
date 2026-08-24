# Premises and commitments

EDOPS makes a small number of consequential choices about what to measure, over what units, and with what warrant. None of them is neutral, and each closes off alternatives worth naming. This page sets them out so that results can be read against the assumptions that produced them.

Known defects and coverage gaps are collected under [Caveats and limits](caveats.md). Dataset-specific issues are described in [Data sources](../data-sources.md).

## Attestation vs. ground truth

The environmental facts asserted in EDOPS signatures are traceable to their source datasets, derived by methods each source documents. EDOPS resolves a named place or set of coordinates to one or more spatial units, retrieves what the sources say about them, and reports it with provenance. It does not adjudicate between sources or correct them. A limited number of values returned in signatures or by site features (e.g. derived variables, and similarity measures) are computed from source datasets rather than read from them directly.

It is possible that two sources will have different values for the same variable at a given location. In this sense, the contents of EDOPS signature—seven instrument measures—are attestations. Furthermore, the aggregation of pixel values overlapping a basin as means or majority classes is an analytical step made under a selected rule.

Elevation derived from digital terrain models is as close to direct measurement as environmental data gets. Cropland extent in 3000 BCE, from HYDE, is a model output carrying substantial uncertainty. Paleoclimate fields from LMR are reconstructions with quantifiable ensemble spread. EDOPS treats all three the same way: it serves them, attributes them, and leaves the assessment of their standing to the person using them.

## The basin as spatial unit

An instrument that reports environmental attributes for arbitrary places needs a space-filling
partition of the terrestrial surface to report them over. The realistic candidates are
administrative units, a discrete global grid, or hydrological basins. The boundaries of administrative units reflect political history rather than environment, and while discrete global grids are geometrically well-behaved, they carry no environmental meaning whatsoever. 

Hydrological basins are different in kind. Their boundaries are derived from terrain rather than
imposed on it: a drainage divide is a physical feature, a consequence of the landscape. Furthermore, water availability is among the most consequential environmental facts for human settlement, agriculture, and movement, so a partition organised around drainage is defensible as a framework for the questions EDOPS exists to support.

Basins nest, and water flows between them in a known direction. That drainage topology makes it possible to distinguish what a place has locally from an aggregation (mean or sum) of its entire contributing catchment. EDOPS reports these *local* versus *upstream* values, as the basis of its derived water-provenance classification. A basin is an element in a dynamic system, with a headwater and an outlet.

Basins do have drawbacks. Coastal and island societies are not well served by basins alone, so EDOPS will need to supplement them with maritime variables essential to characterizing their environmental settings. Basins can also be internally heterogeneous to the extent that summaries of their values can be poor descriptions of any particular location within them — the subject of the next section concerning scale.

## Scale-conditionality

The size and shape of the units over which values are aggregated determines their values. Draw boundaries differently and the numbers change. This is the modifiable areal unit problem (MAUP), a property of all areal summaries and not a flaw in EDOPS or in BasinATLAS.

EDOPS treats level/scale choice as a design input rather than a caveat. Two Pfafstetter levels are currently served — levels 6 and 8, averaging roughly 8,232 km² and 708 km² respectively — and the EDOPS interface makes the level an explicit, visible choice rather than a hidden default. Values are reported at the level you asked for, and switching levels is one click. 

EDOPS cannot pick a correct scale on the user's behalf, because there isn't one. Some questions are better served by the coarser level and others by the finer one, and the description of a place's environmental setting can look materially different at each. Disagreement between signatures at the two levels indicates heterogeneity of the common area surrounding a place and the service is built to make this visible rather than to resolve it.

## Persistence bands and temporality

EDOPS is intended to be useful for historical research, which needs environmental description through time, but very few global historical environmental datasets exist. Most of what is available, including BasinATLAS, describes conditions in the recent past — in the case of BasinATLAS, a 21st century baseline — and says nothing explicitly about any earlier period.

EDOPS has taken two steps to mitigate this shortcoming. Firstly, signature variables are grouped into **bands**, six in all. Bands A through D are persistence tiers, ordered by and large by how quickly the things they measures change. At one end is _A - Physiographic bedrock_ - attributes effectively fixed over the whole span of human history. Following that are _B - Hydroclimatic baselines_, _C - Bioclimatic proxies_, and _D - Anthropocene markers_. Band _E - Coastality_ is a work-in-progress, so far holding variables describing a basin's relation to the sea or to its terminal sink. These drainage-topology attributes, grouped by persistence alone, would sit near Band A.

The second step was adding variables for climate, land use, and volcanic eruptions from three datasets where values are indexed to time in Band _T - Temporal_.

For Bands A through D, the band is therefore a warrant, not a category. It tells you what you might infer about a period the measurement does not cover. A contemporary value in a high-persistence band is reasonable evidence about conditions two millennia ago. A contemporary value in a low-persistence band is evidence about the late twentieth century and very little else. Bands are parameters in signature requests, both in the web interface and the API.

Band assignments and the reasoning behind each are given in the [Codebook](../codebook.md); coverage and reference periods for the temporal datasets are in [Data sources](../data-sources.md).

## EDOPS computes and serves. It does not conclude.

There are no significance verdicts in the API, no automated judgements about whether two places are similar enough to matter, no thresholds encoding what counts as a meaningful difference. Where the interface applies a threshold — a tolerance band in a similarity query, for instance — the value is exposed as a control the user sets. 
