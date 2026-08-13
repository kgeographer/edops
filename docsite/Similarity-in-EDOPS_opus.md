## Similarity in EDOPS

### Why similarity

EDOPS is being developed to support a variety of research perspectives, including investigations of  correspondences between cultural practices and environmental settings at places. Before you can ask whether environment and culture align in any particular case, you need a defensible way to say which environmental settings are alike. You can then discover whether the practice tends to occur in any particular setting, or whether environment truly is not a determining factor.

Environmental settings are characterized in EDOPS as “signatures” comprising dozens of variables grouped thematically in “persistence bands” using the spatial unit of hydrological basins at two scale “levels.” Naively, basins and sets of basins could be compared in their totality—their similarity to all basins globally at a given scale measureable as distances in a multidimensional space. But offering comparisons across composits of all signature variables would simply lead to the followup question, “similar with respect to what?”

### There is no such thing as similar

Two places are never simply similar. They are similar in one or moraspects of precipitation (amount, seasonality), or of terrain (elevation, slope, ruggedness), or in the shape of their annual temperature curve. Being alike in one of those says nothing about the others. Timbuktu and Dakar share a precipitation regime and share almost nothing else. Two Alpine valleys twenty kilometres apart can differ more in seasonal rainfall than either does from a valley in Anatolia.

For this reason, the EDOPS platform has adopted a “lens” approach for the similarity tools in its Sandbox and Workbench pages. A similarity lens incorporates values from related variables. So far we have implemented lenses for three “regimes” and a Climate composite:

**Precipitation:  *annual\_total*, *amplitude*, *shape*   
Temperature**: *temperature\_level*, *temperature\_range*  
**Terrain**: *elevation*, *relief\_range  
***Climate**: Precipitation+Temperature

In the Sandbox page’s Similarity panel, we expose the threshholds used in considering variable values similar, and offer users the option to adjust threshholds to “tight” or “broad” levels. Variable definitions are supplied in help tooltips. In the Workbench page’s WH Cities panel, threshholds are not currently exposed.

### Sandbox similarity



**The respects are chosen before the results are seen.** Each set of variables in EDOPS answers one physical question — how much water arrives and when; how rugged the ground is — and the variables belong together because they belong to that question, not because they were the ones that made a favoured comparison come out well. This is a discipline rather than a nicety. Loosening a condition until an expected match appears is the easiest way to manufacture a result, and it is the failure mode this design is guarding against.

**Nothing is averaged across respects.** A place cannot be excellent on temperature and poor on rainfall and come out "moderately similar." Levels and shapes answer different questions, and letting one compensate for the other produces a number that describes nothing.

## What the platform actually does

There are three distinct similarity operations in v0.4. They answer different questions and are not interchangeable.

### 1. Sandbox — conditions on a single basin

Given a place, the Sandbox finds other basins that satisfy a set of conditions simultaneously. For the climate lens those conditions are five, each in real units: the correlation between the two annual precipitation curves, the ratio of annual totals, the difference in seasonal amplitude, the difference in temperature level, and the difference in temperature range.

All five must pass. A basin that matches beautifully on temperature and fails on annual total does not appear in the result — there is no partial credit and no ranking of near-misses. What comes back is a set: the places that meet the conditions you set.

Because each condition is a tolerance band, the relation is symmetric. Places similar to Tbilisi and places to which Tbilisi is similar are the same set. That is worth stating because people generally expect otherwise.

The tolerances are exposed as controls, with tooltips explaining each. The defaults were arrived at through extended testing against contrasting reference cases, but they are defaults, not truths, and you can change them. When you do, the panel shows what you changed — so anyone reading a result can see what was loosened to get it.

### 2. Workbench, WH Cities — nearest neighbours in a closed collection

The WH Cities view asks a different question: within *this* set of 258 cities, which are the closest to the one I have selected? Rather than a set of places meeting conditions, you get a ranked list with a distance value against each.

This is a corpus-relative ranking. The nearest city in a collection of 258 may still be very unlike your selection — the ranking is silent about that, which is why the distances are shown. Reading the numbers matters more than reading the order.

\<!-- CHECK: confirm whether the env ranking uses the same five gated variables as the Sandbox climate lens without gating, or a distinct variable set. The page currently avoids asserting either. --\>

The distances are informative in a way the ranks are not. Selecting Dakar under the precipitation regime returns Saint-Louis at 0.30 and then jumps to Timbuktu at 2.61. That gap is the finding. Dakar has one close counterpart in this collection and no second one; the remaining four are the least distant of a distant field, not matches. A selection whose top five distances are tightly clustered is telling you something quite different — that its regime is common among world heritage cities.

### 3. Workbench, WH Cities — semantic similarity

The same view offers a second, unrelated kind of similarity: distance between cities in an embedding space derived from their Wikipedia text, reported as cosine similarity and available by facet — environment, history, culture, modern, or a composite.

\<!-- CHECK: state briefly how the facets are derived from the source text (section selection? classification? separate embeddings?). Users will ask, and the answer affects how much weight the facet distinction deserves. --\>

This is similarity in *how cities are written about*, not in what they are. It is a useful and quite different probe, but it carries its own respects, and they are less tractable than a rainfall curve: the length and quality of an article, the interests of its editors, and the language of the source all shape the result. A city with a thin article will sit oddly in the space for reasons that have nothing to do with the city.

**Treat agreement between the two as a question, not a confirmation.** Dakar's nearest neighbour is Saint-Louis under both the precipitation regime and the historical facet. That is not two independent measures converging on a truth. Both are substantially driven by the fact that the two cities are 250 kilometres apart in the same country — shared region is the obvious explanation for both, and it has to be exhausted before anything else is entertained. Agreement between an environmental and a semantic measure is most interesting when the two places are *far apart*.

## What you can get out of it

Concretely, the questions these panels can answer:

- **Does this place have environmental counterparts elsewhere?** Distant places sharing a rainfall regime or a terrain character are the raw material for any comparison that needs proximity ruled out as an explanation.

- **Is this place environmentally unusual or ordinary?** Few matches at default tolerances means unusual; many means ordinary. This is often more useful than the identity of the matches, and it is a property of the place worth knowing before you build an argument on it.

- **Which condition is the binding one?** When an expected match fails, loosening one condition at a time tells you which respect the two places actually diverge in. This is diagnostic rather than exploratory, and it is probably the most underused thing in the panel.

- **How far away is "nearest"?** In a closed collection, the distance column tells you whether a ranked neighbour is a genuine counterpart or merely the least distant option available.

And what they cannot answer: whether the environmental resemblance means anything. That is downstream work. EDOPS reports distance under declared conditions with the sources intact; it makes no claim that a resemblance is explanatory, and none of these panels constitutes a test of anything.

## The harder problem, not yet addressed

Everything above compares single basins. A single basin has one value per variable, so a distance is well defined.

A polity does not. It covers many basins — often spanning mountain and lowland, arid and humid — and its environment is a distribution, not a value. Comparing two such extents means comparing two distributions, and the tempting shortcut of reducing each to an average describes a place that exists nowhere. The ring of basins around Tbilisi runs from high Caucasus to Kura lowland; its mean elevation corresponds to no part of it. This is why EDOPS returns areal queries as distributions with ranges rather than as single numbers, and why extent-to-extent similarity is not offered in v0.4.

Comparing a polity to *itself* over time is harder again. Both the extent and the climate move, and separating a change in territory from a change in conditions is not something the current tools attempt. The temporal variables are there and can be examined; the comparison is not automated, and treating it as though it were would produce results that look like findings and are not.

Both of these are known gaps rather than oversights. They are the reason the similarity work so far stops where it does.

*The respects-relativity problem discussed above has a long literature in philosophy and cognitive science, and the matching problem in the causal inference literature addresses the same difficulty from the statistical side. Pointers are in the further reading section of the methods documentation.*

