# Data sources

EDOPS draws on two distinct groups of external resources: the datasets that make up the
environmental signature itself, and the services the platform calls on for search, mapping, and
correspondence testing. Full academic citations for the signature datasets are in the
[project summary](project.md); this page is the complete, grouped list with a link on each name.

## Signature data

The datasets whose variables are actually part of an EDOPS signature.

- **[BasinATLAS](https://www.hydrosheds.org/hydroatlas)** ([article](https://doi.org/10.1038/s41597-019-0300-6))
  — physiographic, hydrological, climate, and anthropogenic variables aggregated at basin scale
  (Bands A–D). The core source.
- **[HYDE 3.4](https://www.pbl.nl/en/image/links/hyde)**
  ([article](https://essd.copernicus.org/articles/9/927/2017/essd-9-927-2017.pdf)) — historical
  land use (cropland, pasture, grazing, rangeland), 10,000 BCE–2023 CE. Band T.
- **[Last Millennium Reanalysis v2.1 (LMR)](https://www.ncei.noaa.gov/access/paleo-search/study/27850)**
  ([article](https://doi.org/10.5194/cp-15-1251-2019)) — gridded paleoclimate reanalysis (PDSI,
  temperature, precipitation), 1–2000 CE. Band T.
- **[eVolv2k v4](https://doi.org/10.1594/PANGAEA.971968)** — volcanic stratospheric forcing events,
  500 BCE–1900 CE. Band T. (Name links directly to the dataset's own DOI, which serves as its
  citation.)

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
