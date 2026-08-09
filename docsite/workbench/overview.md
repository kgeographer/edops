# Workbench overview

The Workbench is where various experimental tools are prototyped. Some link EDOP's environmental signatures with
cultural datasets (e.g. D-Place **Societies**), others expose potential data resources under consideration — cultural and/or environmental (e.g. **WH Cities** and OneEarth **Ecoregions**).

The three tools currently in place in tabs on the left share a world map on the right. Their purpose and functionality are outlined below.

## Societies ([D-PLACE](https://d-place.org/about))

> "_D-PLACE contains cultural, linguistic, environmental and geographic information for over 1400 human ‘societies’. A ‘society’ in D-PLACE represents a group of people in a particular locality, who often share a language and cultural identity._"

The D-PLACE data used in the Societies panel are from The Ethnographic Atlas (Murdock et al 2025), describing cultural practices for 1,291 societies, coded across 94 anthropological variables (subsistence, settlement, kinship, social organization), mostly at their "ethnographic present" (focal years 1850–1940). 87% have been spatially joined to an EDOP basin signature; the remaining 13% (mostly islands and coastal locations) lack one.

Two sets of trait-value queries are currently available, both filter map markers and by default list the ecoregions represented, grouped by global region. Each trait offers a second pair of visualizations:

- **Dominant subsistence (EA042)** results can display either *Ecoregions by realm* (which OneEarth
  ecoregions the chosen societies fall into) or a **_Climate
  envelope_** scatter (aridity/temperature) — a confirmatory view, because subsistence strategy has a specific
  theoretical hook worth testing directly. A donut graph shows the distribution of language families, often suggestive spatio-cultural diffusion factors. Spatial outliers are of particular interest.

- **High gods (EA034)** offers *Ecoregions by realm* or an **_Environment scan_** — exploratory
  rather than confirmatory, because this variable has no single predicted environmental axis to
  test against; the scan surfaces whatever environmenta patterns are present. The language graph reveals family clusters and non-clustered outlier instances.

The confirmatory/exploratory split with these examples is intentional: EA042's climate envelope tests a specific
theoretical correspondence; EA034's scan explores an unusual proposition: a potential association of religion with environmental setting.

## WH Cities

254 of the 258 [OWHC](https://www.ovpm.org/about-the-owhc/) member World Heritage Cities, have been linked to Level 08 basins.
These are listed in a dropdown list, grouped by UNESCO region. Selecting a city retrieves the environmental signature of its containing basin and offers two independent kinds of similarity search:

- **Similar (env)** — a regime-lens conjunction search, same non-compensatory logic as the Sandbox
  Similarity tab: Precipitation regime, Temperature regime, or Terrain regime (three lenses here,
  vs. four on Sandbox). Terrain regime exposes three
  query-relative tolerance dropdown "dials" (elevation, relief, landform position).
- **Similar (semantic)** — experimental embedding-derived similarity over Wikipedia text about each city,
  by thematic band: _Composite_, _Environment_, _History_, _Culture_, or _Modern_.

Comparing what the two searches surface for the same city — environmentally similar vs.
discursively similar — is itself informative: agreement is a hint worth investigating further,
disagreement is not a failure of either measure.

## Ecoregions (OneEarth)

A simple drill-down browser through the [OneEarth Bioregions](https://www.oneearth.org/bioregions/)
hierarchy — 14 realms, 53 subrealms, 185 bioregions, 847 ecoregions — via a breadcrumb trail
(Realms → Subrealms → Bioregions → Ecoregions). Selecting an ecoregion shows its boundary on the
map and, where available, a Wikipedia summary alongside a link back to the OneEarth source page.
This tool is a reference browser rather than a correspondence test in its own right — it's
what the Societies tab's "Ecoregions by realm" view is drawing its categories from.


## References
Murdock, G. P., R. Textor, H. Barry, I., D. R. White, J. P. Gray, & W. T. Divale. (2025). D-PLACE dataset derived from Murdock et al. 1999 'Ethnographic Atlas' (v3.2.1) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.17602181
