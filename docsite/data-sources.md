# Data sources

EDOPS draws on two groups of external resources: datasets that contribute to the environmental
signature itself, and the datasets and services the platform uses for search, mapping, and
correspondence testing. Full academic citations for the signature datasets are in the repo's
[detailed project summary](https://github.com/kgeographer/edops/blob/main/documentation/EDOP_summary_v04.md);
this page maintains the complete, grouped list.

EDOPS serves what these sources say, with attribution, and does not adjudicate between them. Each
signature dataset is therefore described here twice: what it is, and what it is not. The second half
matters as much as the first, and in the case of the historical datasets it is the difference
between using them well and misreading them.

Limitations arising from EDOPS itself — coverage gaps, known defects, interpretive cautions — are in
[Caveats and limits](design/caveats.md).

## Signature data

The datasets whose variables are actually part of an EDOPS signature.

### BasinATLAS

[Dataset](https://www.hydrosheds.org/hydroatlas) ·
[Article](https://doi.org/10.1038/s41597-019-0300-6)

Physiographic, hydrological, climate, and anthropogenic variables aggregated at basin scale
(Bands A–D). The core source: most of what appears in a signature comes from here.

**What to know.** Values describe a recent baseline — climate normals and contemporary land cover —
not any historical period. How far back each can reasonably be carried is what the persistence bands
encode. Every attribute is an aggregate over a basin delineated by drainage topology, so it
describes the basin rather than any particular location inside it. Some attributes are stored as
integers scaled by 10 or 100; where EDOPS displays these the scaling is given in the label, and the
[Codebook](codebook.md) entry states it for every variable.

### HYDE 3.4

[Dataset](https://www.pbl.nl/en/image/links/hyde) ·
[Article](https://essd.copernicus.org/articles/9/927/2017/essd-9-927-2017.pdf)

Historical land use — cropland, pasture, grazing, rangeland — 10,000 BCE–2023 CE. Band T.

**What to know.** HYDE is an allocation model, not a record of settlement. It distributes estimated
national totals across grid cells by rules based on population density, terrain, and soil quality.
It is not built from archaeological or historical evidence about where people actually farmed, and
its developers are explicit that it should be used alongside finer-scale historical and
archaeological information rather than in place of it.

Three consequences follow, and they bear most on exactly the periods EDOPS exists to serve.

*It under-allocates to ecologically marginal locations.* The rules favour flat terrain and
high-quality soils. Terraced, irrigated, and hill-farmed systems — productive because of human
engineering rather than terrain suitability — come out systematically under-represented. Published
validation has found HYDE assigning zero cropland above 10° slope in landscapes where archaeology
shows intensive farming.

*Misplacement is paired.* Because the national total is fixed, cropland missing from one region has
been allocated to another. A region that looks too empty implies one that looks too full.

*It gets worse further back.* Allocation is driven by population estimates, which are least
constrained for early periods. Recent work finds gridded population products systematically
undercount rural population, traced to incompleteness in national censuses rather than to any
model's method. HYDE inherits that input problem, and compounds it where no census exists at all.

*Worked example.* For Northern Song China at 1000 CE, HYDE yields roughly a third of the cropland
area given by document-based reconstructions from Chinese historical geography. The shortfall
concentrates in the lower Yangtze delta, the middle Yangtze, and Sichuan — the wet-rice and terraced
regions — while cultivation is over-allocated to the flat Huang-Huai plain. At that date the Song
economic centre had already shifted south and the lower Yangtze was the most productive agricultural
region in the world; HYDE puts the intensity on the northern plain instead.
{verify: final figures and citations after WO6 merges}

*Zeros are sometimes right.* Grazing, pasture, and rangeland read zero across the pre-contact
Americas because there were no domesticated grazing animals there. That is the model working, not
missing data.

### Last Millennium Reanalysis v2.1 (LMR)

[Dataset](https://www.ncei.noaa.gov/access/paleo-search/study/27850) ·
[Article](https://doi.org/10.5194/cp-15-1251-2019)

Gridded paleoclimate reanalysis — PDSI, temperature, precipitation — 1–2000 CE. Band T.

**What to know.** Reconstruction quality is geographically uneven: strongest for Europe and North
America, where proxy records are densest, with greater uncertainty for East Asia, South Asia, and
the Southern Hemisphere. A value is returned everywhere; the confidence behind it is not the same
everywhere.

Values are anomalies — departures from a reference period — not the absolute conditions a person
would have experienced. The grid is coarse: a single cell spans a large area, and the number of
cells intersecting a query is reported alongside the values. A query smaller than one cell is
reading a regional average.

### eVolv2k v4

[Dataset and citation](https://doi.org/10.1594/PANGAEA.971968)

Volcanic stratospheric forcing events, 500 BCE–1900 CE. Band T. The name links directly to the
dataset's own DOI, which serves as its citation.

**What to know.** Events are inferred from ice-core sulfate, primarily Greenland and Antarctica, so
what is recorded is a deposition signal rather than the eruption itself. Small eruptions fall below
detection, and the record thins going back in time.
{verify: dating uncertainty by period, and how source volcanoes are attributed}

## Platform services

Resources the Sandbox, Workbench, and Data Explorer call on, but which aren't themselves signature
variables.

- **[World Historical Gazetteer (WHG)](https://whgazetteer.org)** — place-name search and
  reconciliation for settlement lookup.
- **[HydroRIVERS](https://www.hydrosheds.org/products/hydrorivers)** — the global river network
  drawn on Sandbox's neighborhood map.
- **[OpenTopoData](https://www.opentopodata.org)** — live elevation lookups (Mapzen dataset) for
  point queries and the terrain similarity lens.
- **[One Earth](https://www.oneearth.org)** — the bioregions framework behind Workbench's
  Ecoregions tab.
- **[Cliopatria polities](https://github.com/Seshat-Global-History-Databank/cliopatria)** —
  historical polity boundaries for Sandbox's Polities interface and Workbench correspondence
  testing. Cliopatria is a Seshat project dataset; a fuller linkage to the
  [Seshat: Global History Databank](https://seshat-db.com) itself is future work.
- **[D-PLACE](https://d-place.org)** — anthropological society, subsistence, and social-organization
  data for Workbench's Societies tab.
- **World Heritage Cities** — Workbench's WH Cities corpus, compiled from the member-city list of
  the **[Organisation of World Heritage Cities (OVPM)](https://www.ovpm.org)**, via Wikipedia.
- **[Ancient World Mapping Center (AWMC)](https://cawm.lib.uiowa.edu)** — the historical basemap
  tiles under Sandbox's map.
