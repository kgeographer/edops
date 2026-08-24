# Environmental Dimensions of Place (EDOP)
### _Project Summary and Status, September 2026_

Karl Grossner, PhD, KGEO Research

## 1. Overview

Environmental Dimensions of Place (EDOP) is a project within a broader Computing Place research initiative that will be complemented in time with a Cultural Dimensions of Place (CDOP) project. The principal goal of EDOP is the development and publication of EDOPS, a computational service for generating standardized multivariate environmental descriptions (termed "signatures") for any terrestrial geographic location. The signatures provide environmental context data in a form suitable for comparative analysis, linking and integration with cultural datasets, and exploratory modeling of relationships between environmental patterns and human phenomena including cultural practices and historical events.

A working prototype web platform is in development and a v0.4 is currently accessible in two forms: a web application featuring Sandbox and Workbench pages, and an associated application programming interface (API). A richly featured Dashboard application is planned for the 2027 v1 release. The codebase is maintained in a public GitHub repository. This document describes the status and evolving design intent of the signature, service, and supporting web interfaces as of its publication date. The intellectual heritage of the Computing Place framework is set out in a blog post, “Computing Place: Toward Systematic Environmental Characterization for Cultural Research.” \[need updated manifesto\]

EDOPS is being developed in partnership with the Institute for Spatial History Innovation (ISHI) at the University of Pittsburgh, whose expertise in spatial history and ongoing work with the World Historical Gazetteer provide a natural integration context.

### 1.1 Who is this for?

EDOPS has several audiences, broadly corresponding to the project’s products. The current *Sandbox* and *Workbench* pages in the web platform are most useful to project developers and stakeholders. It also provides a visual and interactive preview of EDOPS functionality to interested observers as its development progresses. The API allows computationally-skilled researchers in multiple fields to query the existing data sources programmatically, to evaluate results and to potentially integrate them into their research. A forthcoming *EDOPS Dashboard* web application, with exploratory tools and guiding documentation, will be useful for the above groups and a broader audience of researchers, educators, and students in diverse fields across the humanities and social and environmental sciences.

## 2. Conceptual background, briefly

The Computing Place program of research takes as a formative premise that each inhabited area of the Earth lies within or is itself a *cultural landscape*, in much the same sense described by geographer Carl Sauer a century ago (1925). In this framing, physical geography and ecological characteristics (landscape) are the setting for human activity (culture) in a continually evolving bi-directional relationship. This close association is well-known to environmental historians, archaeologists, anthropologists, and many others studying the past in the humanities and social sciences. However, environmental context is typically invoked qualitatively in cultural, historical, and archaeological research. EDOP treats environmental context as a computable, multidimensional construct derived from global spatialized environmental datasets.

There are many conceptions of the term place. For this endeavor, a place is a named Earth location given meaning and significance by human activity and experience. The nature of a place is a function of what is there, what has happened there, and what can happen there—what activity the place affords. As such, the dimensions or properties of place are innumerable. EDOP presumes the physical geographic setting of a place over time is integral to all of these and that place descriptions can usefully include an environmental signature—a structured representation of settings, composed of standardized variables. These dimensions include, for example:

- Hydrological indicators

- Climate variables (modern baseline and historical)

- Terrain metrics

- Coastal and marine conditions

- Volcanic forcing events

- Ecoregion and biome classifications

The resulting signature is not a classification, but a structured, self-describing document, serialized as JSON, suitable for downstream analysis, comparison, and natural language interpretation.

Most geographic enrichment services describe a location by stacking attribute values from whatever layers overlap it. This represents a place as a point beneath a set of surfaces, and not "conditions at a distance"—the directional, process-mediated flows connecting a location to places it does not touch. A settlement sustained by a river drawing on distant headwaters is, under such a description, characterized by rainfall that never falls on it.

One organizing premise of EDOP, developed in conversation with geographer Michael Goodchild (2026), is that a place is better described by what it experiences than by what merely surrounds it. Its principal operationalization in v0.4 is the local/upstream duality set out in §3.1.2. BasinATLAS supplies, for 37 of the selected variables, both a local value and a value aggregated over the entire contributing catchment—summed for extensive quantities, area-weighted for intensive ones—following the drainage network's actual topology rather than a symmetric buffer. EDOPS treats the contrast between the two as a first-class, queryable property of a place: where local and upstream values diverge, a place occupies a materially different environmental position than where they converge.

The Tigris-Euphrates basin illustrates this clearly: Ur's local environment is hyper-arid (~94 mm/yr precipitation), but its upstream catchment receives substantially more, sustaining the riverine flow that made the site viable. That divergence is a central environmental fact about alluvial civilizations.

The catchment aggregates are BasinATLAS's own, and zonal statistics over watersheds are long established in hydrology. What is uncommon is their use as an interpretable dimension  of *place description*, exposed through a service addressed to researchers who will not compute such statistics themselves. The operationalization is also partial: the drainage graph describes both what reaches a place from above and what a place can reach below, and only the first is implemented in v0.4 (§3.1.3). Change over time is a separate capability resting on separate sources, addressed in §3.1.4.

The EDOPS signature is not a predictive model in the tradition of Archaeological Predictive Modeling (APM); it is not designed to classify locations as settled vs. unsettled, or to output a probability of settlement. It is better understood as a research instrument: a richly parameterized environmental characterization service that researchers bring their own questions to. As one example, a historian studying medieval Northern Song Dynasty expansion and asking which environmental dimensions are salient for that process, can configure the instrument accordingly and interpret the results in light of what they already know (Figure 1). The instrument can give them new environmental perspectives on phenomena they may already be studying by other means.

\[triptych figure\]

*Figure 1: Map series showing the expansion of the Northern Song Dynasty over an 18-year period in the 11th century, into markedly less arid territory. NB: Aridity Index values are from a 2008 dataset.*

## 3. Project Phases

EDOPS is under continuing development toward a v1.0 release planned for February 2027. This document reports on v0.4 (September 2026), a milestone release substantial enough to engender feedback from digital humanities researchers and from environmental science subject-matter experts at The University of Pittsburgh and elsewhere. Three broad phases of work are reported below, each at a different point in its own arc: *§3.1 Signature Design* and *§3.3 Platform Implementation* are both operational, but remain open to revision as review and use surface new requirements. Each phase is reported by its current products; forthcoming extensions toward v1.0 are sketched by its principal questions, not yet a design. *§3.2 Data Characterization (CHAR)* is closed, its findings a frozen deliverable.

*Platform Implementation*, specifically, has produced an operational backend serving both the Sandbox and Workbench interfaces, those two pages themselves, a Data Explorer surfacing CHAR's EDA and ESDA findings, and a usable API. Of these, only the Data Explorer is expected to remain as-is; the backend, Sandbox, Workbench, and API will continue to be refined and extended toward v1.0, which will also introduce a new Dashboard page—the project's intended primary public interface. The Sandbox and Workbench pages are expected to become prototyping and preview surfaces exposed to project team members.

The three operational/closed phases are not strictly sequential: the signature as described in §3.1 reflects the current v0.4 form, which includes some refinements established by CHAR (§3.2) — most consequentially the per-source reliability disclosures and the eVolv2k/LMR decoupling rule.

Three more phases lie ahead: extending the signature itself (§3.4), testing its correspondence with cultural and environmental phenomena (§3.5), and building the user-facing tools through which non-specialist scholars will engage the instrument (§3.6). These previews state principal questions, not designs.

### 3.1 Signature Design

#### 3.1.1 *Variable Selection and Signature Structure*

Variable selection follows a "rich but bounded" strategy: include all variables from selected datasets having a plausible theoretical connection to human activity or habitability, as indicated by prior literature on extending archaeological settlement predictors (Verhagen and Whitley 2012), environmental correlates of cultural practices encoded in anthropological fieldwork (Kirby et al. 2016), and the environmental science consensus represented by EDOPS core source, BasinATLAS (Linke et al. 2019). This has produced a richer default signature than may be strictly necessary in many cases, but as the service API is parameterized, researchers are able to select dimensions relevant for their questions from a principled superset. Variables whose utility is speculative but theoretically motivated are included and currently tagged as planned. Signature design is an ongoing process, subject to further expert review; its current state is maintained in a variables catalog and codebook document found in the repository documentation/ folder.

EDOPS relies on a set of open global environmental datasets. The most central of these is BasinATLAS (a layer of the broader HydroATLAS project), which provides physiographic, hydrological, climate, and anthropogenic variables from numerous modern supporting gridded datasets, aggregated at multiple basin scales. This is supplemented by three spatial-temporal datasets:

- HYDE 3.4 (Klein, Goldewijk et al. 2017) for selected land use variables (10000 BCE–2023 CE),

- Last Millennium Reanalysis v2.1 (LMR; Tardif et al. 2019) for 1–2000 CE continuous historical climate anomalies (deviations from a 1000–1850 CE reference mean), and

- eVolv2k v4 (Sigl & Toohey 2024) for volcanic forcing annotation (500 BCE–1900 CE).

The MapZen digital elevation model is accessed via OpenTopoData for point elevations. The bio- and eco-region framework developed by One Earth is made available in the Workbench, as is an experimental connection with D-PLACE anthropological data. Planned near-term additions for coastal enrichment include ICOADS marine climate data (1662 CE to present day) and seafloor topography (dataset TBD) for those basins where adjacent sea conditions are environmentally significant.

[Complete listing of EDOPS data resources](https://edops.computingplace.org/docs/data-sources/)

Variables from BasinATLAS are grouped in four "bands" corresponding to their relative persistence and applicability to successive historical eras: A - Physiographic bedrock, B - Hydroclimatic baselines, C - Bioclimatic proxies, and D - Anthropocene markers. This banding allows for a relatively coarse temporal scoping of queries: analyses of pre-industrial periods can suppress variables by group, e.g. the Group D variables, which reflect modern land cover and human pressure, are not indicative for many questions.

The signature’s 6-band structure also includes E - Coastality (a bucket for outlet type, distance to sink, and the future marine variables mentioned above), and T - Temporal (holding the HYDE and LMR variables).

The goal is a compact, interpretable signature that preserves meaningful environmental gradients—where "meaningful" is defined operationally through validation against independent signals rather than assumed from the variable set alone.

#### 3.1.2 *Local and Upstream Duality*

Of the selected BasinATLAS variables across Bands A–D, covering hydrology, climate, terrain, soils, and human presence, 37 carry both a local (s) and upstream catchment (u) value. This local/upstream duality is a first-class architectural feature of EDOPS signatures, as the contrast between s and u for a given variable is environmentally meaningful: a settlement where local aridity (s) diverges sharply from upstream catchment aridity (u) occupies a qualitatively different environmental position than one where the two converge. The Tigris-Euphrates basin example for Ur described in §2 illustrates this clearly.

Beyond the pre-computed u values, the BasinATLAS network encodes explicit upstream-downstream topology via hybas\_id and next\_down fields, forming a crawlable directed acyclic graph. This will enable computation of distance-stratified upstream profiles—near-upstream aggregates weighted to reflect proximity rather than contributing area, a designated research extension.

#### 3.1.3 *Downstream Connectivity and Coastality*

The upstream dimension captures what flows to a place. A complementary dimension captures its connectivity to the sea via the downstream drainage network. This element of what we term “coastality” is not fully implemented but is essential: for many historically significant locations, marine access is a primary environmental affordance.

Together, the upstream dimension and coastality in its hydrologic-connectivity mode reflect the current principal operationalization of the process-driven framing introduced in §2—environment including what acts on and flows to a place, not only local values stacked at a point.

Coastality also entails what may be called terrestrial-marine decoupling: in coastal environments, terrestrial and marine affordances are independent dimensions that can point in opposite directions, and settlement viability and history are a function of their combination, not either alone.

The Yaghan peoples of Tierra del Fuego present this case clearly. Their territory, the Beagle Channel and the Cape Horn archipelago, has among the most forbidding terrestrial signatures in the inhabited world: extreme temperature variability, and minimal agricultural potential. A purely terrestrial EDOPS signature would suggest low settlement potential. The Yaghan occupied this territory for millennia, because the marine affordance is extraordinary: the Malvinas Current brings cold, nutrient-rich water through highly productive fjord systems, sustaining dense shellfish, pinnipeds, and fish concentrations. The Yaghan were essentially aquatic in their subsistence. The terrestrial signature alone is in such cases blind to dimensions that actually mattered.

In sum, coastality operates through three distinct modes:

- Hydrologic connectivity: position within the drainage graph relative to a marine outlet— captured by dist\_sink\_km (flow distance to terminal outlet) and outlet\_type (exorheic / endorheic / terminal lake). Endorheic basins have no marine connection by definition and must be handled explicitly throughout.

- Ecological influence: marine productivity accessible from the location, driven by continental shelf width, upwelling zones, major current systems, and marine climate.

- Human accessibility: not yet included in signatures, this might include practical interaction with the sea, e.g. harbor morphology, navigable channel availability, coastal shelter.

Together, the upstream and downstream dimensions would frame a complete positional description within the hydrological graph: what a place receives from above, and what it can reach below. In v0.4 only the receiving half is implemented. Coastality is presently represented by hydrologic connectivity alone; the ecological-influence and human-accessibility modes remain design intent, and the Yaghan case above should be read as a specification for them rather than a demonstration of them.

#### 3.1.4 *Temporal Scope and Historical Depth*

Most global environmental datasets, including BasinATLAS, are contemporary and not ideally suited for historical analyses. For EDOPS, this temporal mismatch is addressed in two ways. First, the banding structure itself provides coarse temporal scoping: physiographic and hydro-climatic variables (Groups A and B) are largely stable over centuries to millennia and are defensible as historical baselines; Group D variables require exclusion or explicit qualification for pre-modern use. Second, and more directly, EDOPS integrates historical data from the three established datasets mentioned already:

**HYDE 3.4** (Klein Goldewijk et al. 2017) variables sourced for the signature characterize cropland and grazing (pasture and rangeland) as fractional basin area at each HYDE epoch. Coverage spans 10,000 BCE–2023 CE at approximately 10 km (5 arcmin) resolution. HYDE's temporal resolution is irregular—millennial in the deep BCE, centennial to 1700 CE, decadal to 1950, annual thereafter—and this structure is disclosed in every Band T response rather than smoothed by interpolation: the API returns all overlapping HYDE epochs within the query window, making the resolution structure visible to the consumer.

A key design feature distinguishes the HYDE implementation from a naive basin-average approach: within-basin cell heterogeneity is returned alongside basin totals. Standard deviation and p10/p90 percentiles of per-cell values are included when a basin contains more than one HYDE cell, enabling distinction between patchy land use (high spread, concentrated in a few cells) and uniform land use (low spread, evenly distributed). For example, Kaifeng (Northern Song, 216 cells, 15,347 km² basin) shows high cropland heterogeneity at 1000 CE, a signal consistent with a century of agricultural intensification spreading from established farming cores across previously uncultivated basin cells.

Band T (HYDE temporal) and Band D (EarthStat static, ~2000 CE calibration) land use variables are explicitly non-redundant: they answer different questions at different temporal granularities and must not be treated as interchangeable. A known methodological challenge is spatial divergence between the two at agricultural hotspot sub-basins (e.g. 3× difference at Ur for 2000 CE), reflecting genuine spatial allocation uncertainty in modeled historical land use rather than a data error. This divergence is flagged for domain expert review.

**Last Millennium Reanalysis v2.1** (LMR; Tardif et al. 2019) is a coarse spatially gridded (2°×2°), annually resolved paleoclimate reanalysis covering 0–1998 CE. Drawn from a 20-member ensemble, it provides the continuous climate context that the signature most needs when a query is placed in historical time. Variables include Palmer Drought Severity Index (PDSI), surface air temperature, and precipitation rate. Systematic exploration of the dataset structure established its key properties: temporal variance is greater than geographic variance for all three variables, confirming that Band C and Band T are genuinely non-redundant. LMR is a regional climate signal, not a local one, a limitation that must be stated explicitly in outputs. It was found to be most reliable in the window 700–1900 CE; the compressed variance of early centuries (0–700 CE) reflects sparse proxy coverage rather than a climate signal, and is disclosed to API consumers as a fidelity note.

A critical geographic limitation of LMR is that its proxy site distribution is systematically denser in Europe and North America than in East Asia, South Asia, or the Southern Hemisphere. The stronger European reconstruction signal reflects better-constrained estimation, not necessarily stronger physical forcing— a structural feature of paleoclimate science reflecting where the proxy networks were built, not where past climate variability is more real. For research use cases in these areas, LMR outputs carry meaningfully greater uncertainty than European queries at the same period. This geographic proxy bias is surfaced as a qualifying note in every Band T payload response.

Based on results of exploratory data analysis in the Data Characterization phase (§3.2 below), a narrower, recommended baseline window of 1000–1850 CE has been established for Band T’s LMR anomaly reporting — sitting inside the broader 700–1900 CE zone of reliability described above, but also avoiding the sparse-proxy funnel effect nearest that zone's early edge, the Medieval–LIA transition ambiguity, and the 20th-century industrial warming signal, none of which reliability alone rules out. It is the stated convention in API documentation.

**eVolv2k v4** (Sigl & Toohey 2024) is now the operational volcanic forcing annotation layer, live alongside HYDE and LMR in Band T. It provides 256 eruptions from ~500 BCE–1900 CE with stratospheric sulfur injection magnitudes (VSSI in Tg), eruption latitude, hemispheric asymmetry, and tephra confirmation. The VSSI threshold default is set to 5.0 Tg, to ensure historically significant events including Krakatoa and Kuwae are included. The Medieval Quiet Period (950–1100 CE) and the Samalas eruption of 1257 CE (59 Tg, the largest in the catalog) are both directly visible in Band T outputs.

A design principle established through the Band T implementation: eVolv2k and LMR are non-substitutable and are deliberately decoupled. eVolv2k returns volcanic events for BCE queries even when LMR data is unavailable (LMR coverage begins at 0 CE). Conversely, LMR cannot recover volcanic cooling signatures below approximately 50 Tg VSSI at basin scale — a known limitation of ensemble reanalysis methods confirmed by Task 11 analysis. The Pinatubo eruption (~20 Tg → ~0.5°C observed cooling) serves as the appropriate calibration reference for the narrative interpretation layer, not as an LMR-detectable signal.

#### 3.1.5 *Qualifying Notes as First-Class Payload Content*

A design principle articulated during the Band T implementation phase applies across all bands, not only Band T: qualifying notes are first-class API payload content. The service is responsible for disclosing the epistemic status of its outputs—temporal scope mismatches (Band C WorldClim data reflects contemporary climate, not historical; Band D EarthStat is calibrated ~2000 CE; HYDE resolution is era-dependent), geographic reconstruction biases (LMR proxy density), and data-source limitations (LMR spatial precision ceiling, eVolv2k detection threshold). These disclosures are returned as \_note fields on the relevant bands or layers in the JSON payload; consuming applications like the sandbox and dashboard will surface them; inclusion in API payloads ensures they travel with the data. A user querying Band C for a BCE site receives both the contemporary baseline (useful as a reference) and an explicit disclosure that it reflects contemporary climate, not the conditions of the query period.

The Signature Design phase produced three operating products: the signature schema described above and in a codebook; a FastAPI service delivering it (the /api/signature endpoint); and a Lookup page in the sandbox web application demonstrating point queries with neighborhood map, full signature display, and a Band T temporal view for queries with year ranges.

### 3.2 Data Characterization (CHAR)

The Data Characterization (CHAR) phase performed a systematic characterization of the chosen signature variables—their distributional properties, spatial structure, scale sensitivity, and redundancy relationships. This was necessarily undertaken before any correspondence testing or modeling, and before any use of the signature for inferential work. Some results of this work refined signature design, as reported in §3.1 above. CHAR work comprised two coordinated tracks: Exploratory Data Analysis (EDA) covering distributional, correlational, missing-data, local/upstream divergence, and sampling-bias characterizations across Bands A–E and Band T; and Exploratory *Spatial* Data Analysis (ESDA) covering univariate and bivariate Moran's I and LISA at two BasinATLAS Pfafstetter levels (L6, ~16,000 basins; L8, ~190,000 basins), categorical join-count coherence, and Band T spatial characterization at native grid resolution.

CHAR produced three operational outputs. An augmented variable codebook, which records for every variable in an EDOPS signature a position-attribute decision, a scale-sensitivity flag, a historical-validity assignment, redundancy partners, and a typology assignment. A set of methodological findings, reported in the project repository’s documentation/ folder, summarizes what the EDA and ESDA tracks established about the signature dataset and have informed subsequent work. An enumeration of design decisions distinguishes those CHAR has settled from those flagged for resolution in future meetings with domain experts, project stakeholders, and users.

Several findings are worth surfacing here as they shape the forthcoming phases. A variable typology was developed, assigning each continuous variable to one of four spatial-behavior classes—*continental-gradient*, *network-topology*, *scale-dependent*, or *local-anomaly*—suggesting what kind of spatial claim the variable supports. A scale finding distinguishes what L6 and L8 each resolve and what neither resolves, framing the choice of basin level as a use-case decision rather than a precision setting. A set of per-source reliability constraints are noted in §3.1, and now disclosed in \_note fields of the JSON payload as first-class content. Additionally, a set of sampling-bias findings were reported for two candidate cultural test datasets (D-PLACE over-sampling tropical wet mountains; a World Heritage Cities corpus over-sampling regulated river corridors); these in some ways bound what correspondence experiments in §3.5 can claim and will inform their design.

The product of CHAR within the v0.4 web application is the Data Explorer page, a visual exhibit of the dataset resources with three tabs: a Global view (world choropleth, distribution, Band T temporal layers), a Regions view (six synchronized regional panels), and a Compare view (paired-variable scatter with regional Spearman strip, surfacing variable relationships that diverge from their global structure in specific regions).

### 3.3 Platform Implementation

Where §3.1 and §3.2 concern the signature itself, this phase concerns the infrastructure that delivers it: the query engine, the variable catalog's growth, and the web interfaces built on both.

#### 3.3.1 *Areal Query Architecture*

The Signature Design phase delivered signatures for a single queried point, resolved to its containing basin. The service now supports four query types through a common resolver → aggregator → payload architecture: the original single containing basin; a basin ring (the containing basin plus its immediate neighbors, returned bearing-ordered); a circular buffer of a specified radius around a point; and an arbitrary polygon — in practice most often a historical polity boundary, resolved for a chosen year. The three areal types do not compress their member basins to an averaged value: each variable is returned as a distribution across the constituent basins, since an average can describe a polity or a basin ring that exists nowhere within it. Polity queries additionally carry two independent temporal axes — the boundary can be resolved to one year while Band T's climate aggregation window is set to another, since a polity's extent as of a given date and the climate conditions of interest need not be the same period.

#### 3.3.2 *Variable Catalog Growth*

Beyond the verbatim BasinATLAS extraction described in §3.1, the catalog now includes a set of derived variables computed at query time rather than stored — measures of precipitation concentration, seasonal timing, and related shape descriptors, computed from the underlying monthly precipitation and temperature arrays. The variable catalog and codebook referenced in §3.1 have been revised accordingly.

#### 3.3.3 *Similarity Tooling*

Two distinct mechanisms now let a researcher ask whether a place's environment is unusual or has counterparts elsewhere. The first is a threshold-based test: a place clears a declared tolerance on each of several variables or it doesn't, returning the (possibly empty) set of basins worldwide that qualify — useful for asking whether a specific environmental combination is rare. The second, applied to a small fixed corpus of named World Heritage cities, ranks that corpus by environmental or by textual similarity (the latter via similarity of Wikipedia-article language) rather than testing against a threshold, since a small named set calls for "which are closest" rather than "which qualify." Both operate through lenses: a comparison is always asked with respect to one facet — a precipitation regime, a temperature regime, terrain — rather than a place's full signature at once, since two places alike in one respect are routinely unlike in every other.

Both mechanisms compare single basins — to other single basins, or to the small named WH Cities corpus. Extending either to compare an area — a basin ring, a buffer scope, or a polity, each returned as a set of basin signatures rather than one — remains an open problem: there is not yet an established way to compare one set of signatures to another, even after each has been reduced to a lens.

#### 3.3.4 *Web Interfaces*

Two of the three prior web interfaces were substantially rebuilt on this new architecture; the third, Explorer (§3.2), is unchanged — it remains CHAR's own visual exhibit of the dataset. The original Lookup interface (§3.1) was replaced by a two-part Sandbox: a Settlements interface offering the areal query types above for any place resolved via the World Historical Gazetteer, and a Polities interface for searching and querying Cliopatria polities across their historical boundary changes — both with a live basin-neighborhood map and full signature display. A third interface, Workbench, was added: a set of correspondence-testing tools comparing D-PLACE societies, Cliopatria polities, and World Heritage cities against their environmental signatures, the first concrete instrument for the Correspondence Evaluation work previewed in §3.5.

### 3.4 Signature Extensions and Refinement

The CHAR phase's enumeration of design decisions identifies a set of variables whose inclusion, exclusion, or current implementation merits expert review. Three extension threads are open. Coastality (Band E) is partly implemented at the topological level (outlet type, flow distance to marine outlet, depth from coast); the ecological and human-accessibility modes are designed but not yet operational. Terrain navigability — a candidate set of variables describing how terrain affords or constrains historical network connectivity — is a plausible addition, in keeping with the process-driven framing introduced in §2. Planned but unimplemented BasinATLAS variables were carried through the CHAR sweep so that inclusion decisions are now empirically grounded; their disposition awaits that review.

### 3.5 Correspondence Evaluation

The Correspondence Evaluation phase asks whether and where EDOPS signatures correspond to independently attested cultural and environmental phenomena. Three datasets are staged for this work, at different stages of use. D-PLACE (anthropological field data, 1,291 societies with subsistence and social variables, spatially linked to basin08) has seen substantial exploratory use already: the Workbench's Societies interface offers confirmatory and exploratory correspondence queries against a society's environmental signature, and a parallel series of targeted analyses has tested specific trait-environment hypotheses, holding cultural relatedness and geography constant. One such analysis produced a genuine negative result — a predicted attenuation of a trait-environment association under stricter control did not hold, the association instead strengthening — an early indication that the instrument can produce findings that contradict as well as confirm expectation. Cliopatria (6,000 years of historical polities, temporally bounded polygons now queryable as areal inputs per §3.3) and the Tracks of Yu Yellow River database (4,000+ historical environmental events, contributed by Ruth Mostern's group) remain staged but not yet exercised for correspondence testing proper. The evaluation throughout is exploratory, not confirmatory: cases where signatures correspond to canonical historical understandings are existence proofs of the instrument's non-triviality; productive residuals — cases where they do not — are valuable findings also.

### 3.6 Dashboard Design and Development

The Dashboard is the user-facing tool through which scholars will explore data and build signatures without writing API calls. It will package the sandbox capabilities, a parameter rubric (which band combinations and basin levels are appropriate for which kinds of questions), and a user-facing casebook: a set of worked vignettes, each running to several pages, organized around a specific research question, naming the judgment calls and failure modes in the analysis. The casebook is documentation in the genre of methods-textbook worked examples rather than API cookbook recipes. An API endpoint delivering a payload for WHG place portal pages is a Dashboard-adjacent deliverable.

## 4. Future Possibilities

The EDOPS service is designed as consumable infrastructure: a JSON API delivering structured environmental signatures on request. Its current consumers are the Sandbox and Workbench pages of the web application. A forthcoming Dashboard will be the next, and other consumers are anticipated. The Cultural Dimensions of Place (CDOP) module of the Computing Place initiative will draw on EDOPS for environmental context in cultural-correspondence work. Third-party place-oriented platforms could consume signature payloads for analytical or educational purposes.

A federated extension to the EDOPS platform architecture has been discussed, in which contributors of region-specific high-resolution environmental data—historical hydrological reconstructions, paleoecological records, archaeological survey data—could enrich signatures within their coverage extent (Mostern, May 2026). This addition would begin to offset the proxy distribution bias discussed in §3.1. The conceptual and engineering implications for this are substantial: provenance layering, distinguishing global-baseline from contributed fields, a coverage registry, priority and fallback logic, and curation standards for vetting contributed reconstructions. This is a speculative v2 or v3 direction rather than a planned phase.

## 5. Closing Summary

EDOPS is research infrastructure: a service that delivers structured, multi-band environmental signatures for any terrestrial location on Earth, intended for use by digital humanities and cultural heritage platforms, by scholars investigating environment–culture relationships, and by Geographic Information Science researchers as a methodological reference. Its credibility rests on methodological transparency and reproducibility, including explicit disclosure of each variable's spatial behavior, temporal validity, and reliability constraints.

The signature as designed is operationalized and its sources characterized; what remains is to extend it where extensions are warranted, to enable similarity measures for areal features, to test its correspondence with cultural and environmental phenomena where suitable datasets exist, and to build the user-facing tools through which non-specialist scholars can engage the instrument. The next planned major checkpoint is a February 2027 meeting at ISHI.

## References

Goodchild, M. F. (2026, February). Personal communication.

Kirby, K.R., Gray, R. D., Greenhill, S. J., Jordan, F. M., Gomes-Ng, S., Bibiko, H-J, et al. (2016). D-PLACE: A Global Database of Cultural, Linguistic and Environmental Diversity. PLoS ONE, 11(7): e0158391. doi:10.1371/journal.pone.0158391.

Klein Goldewijk, K., Beusen, A., Doelman, J., & Stehfest, E. (2017). Anthropogenic land use estimates for the Holocene–HYDE 3.2. Earth System Science Data, 9(2), 927–953.

Linke, S., Lehner, B., Ouellet Dallaire, C., Ariwi, J., Grill, G., Anand, M., Beames, P., Burchard-Levine, V., Maxwell, S., Moidu, H., Tan, F., Thieme, M. (2019). Global hydro-environmental sub-basin and river reach characteristics at high spatial resolution. Scientific Data 6: 283. doi: [https://doi.org/10.1038/s41597-019-0300-6](https://doi.org/10.1038/s41597-019-0300-6)

Mostern, R. (2026). Personal communication. (May, 2026)

Sauer, C. O. (1925). The morphology of landscape. In Foundation Papers in Landscape Ecology (2007), 36–70.

Sigl, Michael; Toohey, Matthew (2024). Volcanic stratospheric sulfur injections from 500 BCE to 1900 CE, eVolv2k\_version4 \[dataset\]. PANGAEA. [https://doi.org/10.1594/PANGAEA.971968](https://doi.org/10.1594/PANGAEA.971968)

Tardif, R., G.J. Hakim, W.A. Perkins, K.A. Horlick, M.P. Erb, J. Emile-Geay, D.M. Anderson, E.J. Steig, and D. Noone. (2019). Last Millennium Reanalysis with an expanded proxy database and seasonal proxy modeling. Climate of the Past, 15, 1251–1273. doi: 10.5194/cp-15-1251-2019

Verhagen, P., & Whitley, T. G. (2012). Integrating archaeological theory and predictive modeling: a live report from the scene. Journal of Archaeological Method and Theory, 19(1), 49-100.

