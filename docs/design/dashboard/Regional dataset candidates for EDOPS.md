# Regional dataset candidates for EDOPS

Desk search of 2026-10-31. Nothing here has been downloaded or opened as data yet. File lists come from NOAA metadata records, because the NCEI study pages are a JavaScript app that could not be read directly.

## Recommendation

Pilot with the **Old World Drought Atlas (OWDA)**. It is a half-degree grid, 0 to 2012 CE, and its date span lines up with the existing Band T sources. Plan the **European Russia Drought Atlas (ERDA)** as the natural second dataset, because it fills the part of OWDA's domain where OWDA is weakest. For Ancestral Puebloan examples, the **Living Blended Drought Atlas (LBDA)** is the North American counterpart.

## Terms

- **JJA**: June, July, August. The season the northern-hemisphere atlases reconstruct (boreal summer).
- **DJF**: December, January, February. The season the southern-hemisphere atlases reconstruct (austral summer). It spans two calendar years, so the year a DJF value is assigned to is a convention to check in each readme.
- **PDSI**: Palmer Drought Severity Index, positive wet, negative dry, usually between -6 and +6.
- **scPDSI**: self-calibrating PDSI (OWDA, ERDA, MXDA, SADA).
- **PMDI**: Palmer Modified Drought Index (LBDA). Not the same index as PDSI; the payload addendum must name the variant.

## Candidates

| Dataset | Region | Years (CE) | Grid | Index and season | NCEI study |
| --- | --- | --- | --- | --- | --- |
| OWDA | Europe, North Africa, Middle East (27.25 to 70.75 N, -11.75 to 44.75 E) | 0 to 2012 | 0.5 degree, 5,414 points | scPDSI, JJA | 19419 |
| ERDA | East European Plain to the Urals | 1400 to 2016 | 0.5 degree, 4,259 points | scPDSI, JJA | 28630 |
| LBDA (original, Cook et al. 2010) | North America including Alaska | 0 to 2005 | 0.5 degree, 11,396 points | PMDI, JJA | 19119 |
| LBDA v3 | Continental US only, extended to present | 0 to present | 0.5 degree | PMDI, JJA | 22454 |
| NADA v2a (older NCEI page) | North America to 63 N | 0 to 2006 | 2.5 degree, 286 points | PDSI, JJA | not on the current NCEI list |
| MADA (v2 exists) | Monsoon Asia | v2 back to 1000 (most of domain) | v2 1.0 degree | scPDSI, JJA | 10435 (version not confirmed) |
| MXDA | Mexico, 14 to 34 N, 75 to 120 W | 1400 to 2012 | 0.5 degree | scPDSI, JJA | 20353 |
| SADA | South America south of 12 S | 1400 to 2000 | 0.5 degree | scPDSI, DJF | 30612 |
| ANZDA | Eastern Australia and New Zealand | back to 1500 | 0.5 degree | PDSI, DJF | 20245 |
| Pauling et al. 2006 | Europe, 30 to 71 N, 30 W to 40 E | 1500 to 1900, joined to gridded observations to 2000 | 0.5 degree | seasonal precipitation (mm), all four seasons; not a drought index | NOAA paleo "pauling2006precip" |

## Confirmed download details

### Old World Drought Atlas
- Landing page (NOAA NCEI paleo): https://www.ncei.noaa.gov/access/paleo-search/study/19419 (the drought.gov entry links here).
- DOI: 10.25921/rjm6-mq74.
- Files under https://www.ncei.noaa.gov/pub/data/paleo/treering/reconstructions/europe/: `owda.nc` (netCDF), `owda.txt` (text), `owda-xy.txt` (coordinate pairs), `owda-readme.txt` (data description), `owda-maps.zip` (annual JPG maps), `owda-animation.zip`.
- Coverage: 0 to 2012 CE; latitude 27.25 to 70.75, longitude -11.75 to 44.75. Note the eastern edge: the domain stops at 44.75 E, so much of the Middle East is outside it.
- Access constraints: none. Use constraints: cite the original publication (Cook et al. 2015, Science Advances 1(10), e1500561), the online resource, the dataset DOI and the access date.

### North America
- LBDA original: study page https://www.ncei.noaa.gov/access/paleo-search/study/19119; files under https://www.ncei.noaa.gov/pub/data/paleo/drought/LBDA2010/ (`LBDA_PMDI_JJA_Recons.txt`, `nada_hd2_cl.nc`, calibration/verification stats, instrumental data). 0 to 2005 CE. Access constraints none; same citation terms.
- LBDA v2 and v3 are US-only, recalibrated and extended with instrumental data. v2 files are under `.../drought/LBDP-v2/` (for example `lbda-v2_kddm_pmdi_2017.nc`); v3 overview is study 22454.
- NADA v2a (2.5 degree, 0 to 2006 CE) is described on an older NCEI page and by a readme at paleo.ltrr.arizona.edu; the current NCEI "Drought Variability" page no longer lists it.

## Caveats

- **OWDA is thin in the east.** Its tree-ring network used only ten chronologies from the former European USSR: four in northwest Russia, four in western Ukraine and two in Georgia. ERDA (4,259 points, 697 chronologies) was built because of that, and its authors report it is much more skillful than OWDA where they overlap in the western part of its domain. Ukraine examples will want both.
- **Tree-ring PDSI can carry seasonal biases**, for example stronger winter-precipitation signals than instrumental PDSI (shown for NADA).
- **Regional averages are often more skillful than single grid points.** That supports aggregating to basins.
- **Season only.** These are summer (JJA or DJF) values, not annual.
- **LBDA blends in instrumental data** in later years, and the recalibration differs between versions.

## Design implications for the footprint index and the payload addendum

1. Record per dataset: region and bounds, native grid, season, index variant, years, source and citation. The addendum states them with the values.
2. Resolution (my arithmetic): a half-degree cell at 45 N is about 2,200 km2. An L6 basin averages about 8,200 km2 (about four cells); an L8 basin averages about 700 km2 (a third of a cell). L6 aggregation is meaningful. At L8 the dataset's value just repeats across neighbouring basins, and the addendum should say so.
3. Overlaps (OWDA and ERDA) need a rule: report both, or prefer the more skillful one for the overlap area. This is a design decision for Karl.
4. Outside every footprint the addendum is simply absent, never zero.
5. The same grid-cell distribution machinery used for LMR in Band T (`grid_areal_distribution`) should serve these datasets.

## Before building

- Read each dataset's readme and open the netCDF: variable names, missing-value flags, year axis and coordinate order.
- DJF year convention for SADA and ANZDA.
- Confirm the licence terms beyond "cite the source" with NOAA if the data will be redistributed in a payload.
- Locate the MADA v2 download.
- Check how infilled or smoothed values (ERDA is spatially smoothed and infilled) should be described.

## Sources

- https://www.drought.gov/data-maps-tools/old-world-drought-atlas
- https://www.ncei.noaa.gov/pub/data/metadata/published/paleo/dif/xml/noaa-recon-19419.xml
- https://www.ncei.noaa.gov/products/paleoclimatology/drought-variability
- https://pmc.ncbi.nlm.nih.gov/articles/PMC4640589
- https://ocp.ldeo.columbia.edu/res/div/ocp/pub/seager/CookEtAl2015OldWorld.pdf
- https://par.nsf.gov/servlets/purl/10186849 (ERDA paper)
- https://www.ldeo.columbia.edu/res/fac/trl/public/ftp/Public/To_NOAA_NCEI/ERDA_paper.docx
- https://catalog-beta.data.gov/dataset/noaa-wds-paleoclimatology-the-living-blended-drought-atlas-lbda-north-american-drought-rec
- https://catalog.data.gov/dataset/noaa-wds-paleoclimatology-living-blended-drought-atlas-lbda-version-2-recalibrated-reconst
- https://www.ncei.noaa.gov/node/1373
- https://paleo.ltrr.arizona.edu/drought/NAmericanDroughtAtlas.v2/readme-NADAv2-2008.txt
- https://climatedataguide.ucar.edu/climate-data/drought-atlases-tree-rings
- https://ltrr.arizona.edu/node/2985 (MADA v2)
- https://paleo.ltrr.arizona.edu/treering/chronologies/northamerica/usa/nm603-noaa.crn (MXDA)
- https://ui.adsabs.harvard.edu/abs/2019AGUFMGC51A..06M/abstract (SADA)
- https://paleo.ltrr.arizona.edu/dc/noaa-recon-20245.xml (ANZDA)
- https://link.springer.com/doi/10.1007/s00382-005-0090-8 (Pauling et al.)
- https://core.ac.uk/download/161457945.pdf (PDSI biases in drought atlases)
- 