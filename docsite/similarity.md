## Why similarity

EDOPS is being developed to support a variety of research perspectives, including investigations of correspondences between cultural practices and environmental settings at places. Before you can ask whether environment and culture align in any particular case, you need a defensible way to say which environmental settings are alike. You can then discover whether the practice tends to occur in any particular setting, or whether environment truly is not a determining factor.

Environmental settings are characterized in EDOPS as "signatures" comprising dozens of variables grouped thematically in "persistence bands" using the spatial unit of hydrological basins at two scale "levels." Naively, basins and sets of basins could be compared in their totality—their similarity to all basins globally at a given scale measurable as distances in a multidimensional space. But offering comparisons across composites of all signature variables would simply lead to the followup question, "similar with respect to what?"

## There is no such thing as similar

Two places are never simply similar. They are similar in one or more aspects of precipitation (amount, seasonality), or of terrain (elevation, slope, ruggedness), or in the shape of their annual temperature curve. Being alike in one of those says nothing about the others. Timbuktu and Dakar share a precipitation regime and share almost nothing else. Two Alpine valleys twenty kilometres apart can differ more in seasonal rainfall than either does from a valley in Anatolia.

For this reason, the EDOPS platform has adopted a "lens" approach for the similarity tools in its Sandbox and Workbench pages. A similarity lens incorporates values from related variables. So far we have implemented four lenses, three for thematic "regimes" and one combining precipitation and temperature as "Climate":

**Precipitation**:  *annual\_total*, *amplitude*, *shape*  
**Temperature**: *temperature\_level*, *temperature\_range*  
**Terrain**: *elevation*, *relief\_range*  
**Climate**: Precipitation+Temperature

In the Sandbox page’s Similarity panel, we expose the thresholds used to judge variable values similar, and offer the option to adjust thresholds to "tight" or "broad" levels. Variable definitions are supplied in help tooltips. The Workbench page’s WH Cities panel offers two similarity measures, "environmental (env)" and "semantic." Thresholds are not applicable for either, as explained below.

Lenses in EDOPS let you ask one question at a time, which is what you need when you don't yet know which question matters.

## Two cases, three algorithms

The two panels are not asking the same question, and they don't use the same method to answer it. The Sandbox panel asks: given a place and a declared threshold on each variable, which basins — out of roughly sixteen thousand at the coarse scale, nearly two hundred thousand at the fine one — actually meet it? The Workbench's WH Cities panel asks something narrower: within a fixed collection of 254 named places, which are most similar to the one selected? These sound like the same question asked at different scales but they are not, and each gets its own algorithm.

**The Sandbox question is a membership test**. A basin clears every declared threshold or it doesn't — no partial credit, no compensating a poor score on one condition with a good one on another. The result is a set, and the set can be small, large, or empty; an empty one, meaning nothing else on Earth meets these conditions together, is as real and useful an answer as a crowded one. Ranking has no role here, because nothing beyond passing or failing is being measured. Questions the Sandbox can answer, *per lens* include:

- Does this place have environmental counterparts elsewhere?

- Is this place environmentally unusual or ordinary?

**The two Workbench options are rankings, one statistical the other semantic**. World Heritage cities are a small, fixed, named collection, and someone who picks one wants to know which of the other 253 come closest—not which clear some declared bar, since a strict bar applied to a set this small could easily return nothing, or everything. That calls for distance measures and sorted lists, not a pass/fail test: genuinely different computations, not looser or stricter versions of the same one.

- **Statistical**. Ranked by distance on environmental variables—precipitation, temperature, terrain—computed against the other 253 cities rather than the full basin corpus. Answering, _which World Heritage cities have environmental settings most similar to this one?_

- **Semantic**. Ranked by cosine similarity between Wikipedia-article text embeddings, computed for the whole article as a Composite, or separately for one of four thematic sections — Environment, History, Culture, Modern. Answering, _which World Heritage cities are written about, in that respect, most like this one?_

## The remaining challenge: Areas

All the similarity measures above, apart from the "semantics" of Wikipedia articles for cities, resolve to a single place-containing basin compared to the global set at one of two scales. Whichever scope a settlement query returns—single basin, basin-ring, or buffer—the similarity lenses offered compare the single basin containing the place to the global set. The ring and buffer choices widen what is returned to sets of basin signatures, and distributions of their values are displayed in histograms, but the similarity measure does not extend to the entire set. 

Polities are the other case. Their signatures are always sets, with values likewise displayed as distributions and nothing is ever averaged down to one value. Unlike the settlement scopes, no similarity measure is offered for them at all, because there is no single focus basin in this case.

That leaves "similarity for an area" open in three places: basin-ring and buffer scopes, where what the user actually sees is a set of signatures even though the similarity tool quietly falls back to the one containing basin; and polities, where no similarity is attempted at all. In all three the underlying payload is a set of signatures, and the outstanding problem is comparing sets of sets of variables — even after they've been reduced to lenses.

*[annual_total]: How much a basin's total annual rainfall may differ from the query basin's, as a multiplicative factor — 1.5 allows anywhere from two-thirds to one-and-a-half times as much.
*[amplitude]: How closely a basin's month-to-month rainfall variability must match the query basin's — how sharply seasonal the rainfall is.
*[shape]: How strongly a basin's month-by-month rainfall pattern must correlate with the query basin's — compares the timing of wet and dry months.

