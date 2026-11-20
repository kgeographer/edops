# Using EDOPS: Purpose, Framing, and Communication Strategy

**Discussion synthesis and handoff notes for Opus / Claude Code**  
**November 19, 2026**  
**Context:** EDOPS v1 development — *Using EDOPS* page

## 1. Overview

A discussion about documenting the *Using EDOPS* page led to a clarification of what this section of the application is intended to accomplish, how its individual examples should be characterized, and how the page's introductory panel might establish an appropriate interpretive framework for visitors.

The central conclusion is:

**The *Using EDOPS* page demonstrates possible uses of environmental signatures as research resources. Its examples are exploratory applications, not completed research studies or demonstrations of established scientific findings.**

The examples illustrate how EDOPS signatures can be incorporated into different kinds of geographically grounded inquiries, from enriching place descriptions to comparing environmental characteristics across regions and exploring possible associations between environmental and cultural attributes.

Their purpose is to make the capabilities and potential utility of the underlying service intelligible, not to establish the validity of particular hypotheses.

This distinction is important for the v1 release, especially in anticipation of a February 2027 meeting at the University of Pittsburgh involving researchers with expertise in environmental history, environmental science, ecology, and related disciplines.

The page should invite such researchers to imagine applications of their own, rather than inviting them to evaluate the examples principally as finished disciplinary research.

## 2. The Intellectual Origins and Purpose of EDOPS

### 2.1 Place description as the underlying concern

EDOPS (Environmental Dimensions of Place) originates in a longstanding interest in the nature of *place*, particularly place as a polysemous concept represented through geographic information systems, historical gazetteers, semantic models, and computational infrastructure.

This interest extends through several related projects:

- World Historical Gazetteer (WHG)
- Environmental Dimensions of Place (EDOPS)
- Cultural Dimensions of Place (CDOP)
- Computing Place

A central concern across these projects is how knowledge about places can be represented, assembled, organized, and made available computationally.

Gazetteers provide an instructive historical model. They range from simple lists of place names and locations to extensive descriptive resources containing information about geography, environment, history, and cultural significance.

WHG addresses important dimensions of historical place identity, including names, locations, types, temporal information, relationships, and sources. But a gazetteer page could potentially convey much more about the environmental setting of a place.

During WHG development, discussions with Ruth Mostern included the possibility of automatically generating environmental descriptions for place pages. Some initial environmental context was provided through biome or ecoregion identification, but the broader ambition remained unrealized.

EDOPS provides infrastructure that could support a substantially richer form of environmental place description.

### 2.2 Environmental signatures as structured place descriptions

The central product of EDOPS is an environmental signature: a structured aggregation of environmental variables assembled from multiple datasets and associated with geographic units based on hydrological basins.

These signatures make environmental characteristics available in a consistent, computationally accessible form.

A signature is not itself a research conclusion or an explanation of historical events. It is a structured environmental characterization derived from source data and geographic processing.

The signatures can support several kinds of operations:

- Retrieving environmental characteristics associated with a place or location.
- Comparing the environmental characteristics of different places or sets of places.
- Enriching existing geographic and historical records.
- Joining environmental information to other geographically referenced datasets.
- Exploring spatial distributions and associations involving environmental variables.
- Supporting downstream computational analyses in other research environments.

The hydrological basin framework, selected variables, aggregation methods, source datasets, and temporal coverage all impose representational choices and limitations. EDOPS does not provide a complete environmental history of any place, nor does it claim to.

These choices should be documented and inspectable.

The service is intended to provide useful environmental evidence, not to make that evidence exhaustive or interpret it automatically.

### 2.3 Infrastructure rather than a prescribed research program

EDOPS is fundamentally a **data service and research infrastructure**, rather than an application designed to answer one particular scientific question.

Its purpose is to expose environmental information in a form that can be retrieved, inspected, compared, and incorporated into other computational systems.

The environmental signature is the primary deliverable.

The dashboard, visualizations, examples, and API are ways of making that deliverable accessible and useful.

This distinction is critical. EDOPS should not be judged solely by the particular research questions its developer has chosen to explore.

A successful data service can support rigorous scientific investigations, exploratory analysis, descriptive applications, and forms of inquiry that its developer has not anticipated.

The examples supplied with EDOPS are therefore neither exhaustive nor prescriptive.

## 3. The Role of the *Using EDOPS* Page

The *Using EDOPS* page should communicate what researchers and other users might do with environmental signatures once those signatures become available.

It performs a different function from technical documentation, the signature dashboard itself, or the API reference.

Technical documentation explains how the service works and what its data represent.

The *Using EDOPS* page shows the signatures being put to work.

Its examples are drawn from actual development and experimentation, not hypothetical applications invented merely to promote the service. They demonstrate capabilities that have already been implemented and exercised.

However, the examples should not be presented as equivalent to finished research.

### 3.1 Examples of use versus exemplars of research

This distinction emerged as one of the most important conclusions of the discussion.

An **example of use** demonstrates how a resource or capability can be applied to some problem.

An **exemplar of research** demonstrates a completed investigation whose methods, evidence, and conclusions meet the standards of a relevant research discipline.

The *Using EDOPS* examples belong primarily to the first category.

Some necessarily cross into the territory of substantive research questions. The Societies exploration, for example, asks about possible relationships between environmental characteristics and cultural traits.

But presenting a question, assembling relevant data, and exploring its possible answers are not equivalent to conducting a completed scientific investigation.

The examples should communicate what can be explored, what the interface makes visible, and what EDOPS contributes to the process.

They need not produce statistically supported conclusions.

### 3.2 What constitutes a successful demonstration?

A useful criterion for evaluating each example is:

**Does this example make a capability of environmental signatures apparent that was not obvious before?**

This criterion is more appropriate than asking whether the example establishes an important research finding.

A successful example might demonstrate that environmental signatures can be used to characterize historical places, compare geographic regions, or examine the environmental distributions of culturally defined populations.

The example succeeds if it makes a meaningful analytical possibility visible, even if further investigation would be needed before making substantive claims.

### 3.3 The intended audience

The audience for the v1 release includes potential users with a range of disciplinary backgrounds.

Environmental scientists may find particular examples methodologically elementary. Historians or anthropologists may recognize substantial unresolved questions. Technical users may be more interested in the API and data structures than in the examples themselves.

These reactions are not necessarily failures of the page.

The goal is not to convince every visitor that the existing demonstrations constitute sophisticated disciplinary scholarship.

It is to help visitors recognize the service's capabilities and consider how environmental signatures might be useful in their own work.

In particular, the Pittsburgh meeting may introduce EDOPS to researchers capable of pursuing applications or extensions that lie beyond the developer's current expertise, interests, or resources.

EDOPS v1 should be presented as functioning infrastructure with demonstrated possibilities for further use.

## 4. The Societies Exploration: What It Is and What It Is Not

The Societies panel is the most instructive example of the communication difficulty because it comes closest to resembling a conventional research study.

It was developed as an exploratory investigation using cultural data from D-PLACE and environmental signatures from EDOPS.

The initial question concerned possible associations between environmental characteristics and the geographic distribution of encoded cultural traits.

Two Ethnographic Atlas variables were selected, including EA034, concerning high gods, and EA042, concerning dominant subsistence.

The application allows users to select particular encoded values of these traits and examine the societies associated with them.

### 4.1 The high-gods exploration

One example discussed in detail was the EA034 value *Active, supporting morality*.

Selecting this value produces a mapped distribution of societies for which that response was recorded.

The interface then displays the environmental characteristics of the basins associated with those societies.

The environmental scan displays distributions across five selected dimensions:

- Aridity
- Temperature
- Seasonality
- Ruggedness
- Landform position

These displays situate the environmental values associated with the selected societies in relation to the broader range of values represented in the joined dataset.

The user can inspect whether the selected societies appear to occupy relatively concentrated, dispersed, or distinctive portions of these environmental distributions.

This is an exploratory comparison. It does not establish that any environmental variable explains the occurrence of the selected cultural trait.

### 4.2 The introduction of language families and Galton's problem

During development, Claude raised the relevance of **Galton's problem**, a longstanding methodological concern in comparative anthropology.

Societies sharing a cultural trait cannot necessarily be treated as independent observations.

Similarities may reflect:

- Shared cultural ancestry.
- Linguistic relationships.
- Historical transmission or diffusion.
- Geographic proximity and interaction.
- Independent responses to similar environmental conditions.

A geographic association between a cultural trait and an environmental characteristic therefore does not, by itself, establish an environmental explanation.

The application was extended to include a language-family distribution visualization.

The language-family donut chart allows users to inspect the composition of the selected society population. Interacting with a language-family category changes the mapped selection and environmental distributions accordingly.

This makes it possible to examine differences between the full set of societies sharing an encoded trait value and particular linguistic subsets.

The addition was motivated by the need to consider potential cultural and historical relationships alongside environmental associations.

It was not intended as a complete solution to Galton's problem.

Language-family affiliation is an imperfect proxy for shared cultural history. Language, geographic proximity, diffusion, and common descent can be difficult to disentangle. Visual selection of linguistic subsets cannot substitute for statistical controls or phylogenetic and spatial modeling.

Nevertheless, the interaction introduces a useful comparative dimension and exposes some of the complexities involved in interpreting cultural-environmental patterns.

### 4.3 Encountering prior research: Botero et al. (2014)

After the Societies exploration had been developed, a relevant published study was identified:

**Botero, Carlos A., et al. (2014). “The ecology of religious beliefs.” Proceedings of the National Academy of Sciences.**

The paper investigates relationships between environmental conditions and belief in moralizing high gods, using the same underlying Ethnographic Atlas variable represented in the EDOPS exploration.

The study predates the publication of D-PLACE, which subsequently provided access to the underlying ethnographic data alongside other cultural datasets.

Botero and colleagues carried out a substantially more rigorous and comprehensive investigation, using additional data and formal methods to address ecological associations and the non-independence of societies.

The paper explicitly discusses Galton's problem.

Its discovery changed the developer's understanding of the status of the EDOPS exploration.

The Societies panel should not be presented as an original investigation that establishes conclusions comparable to those of Botero et al.

Nor should it be retroactively reframed as a replication, improvement, or methodological challenge to their work.

It remains a much more modest exploratory use of environmental signatures.

The Botero paper can be cited in supplementary explanatory material as an example of the kind of disciplinary investigation required to pursue the high-gods question rigorously.

A thorough comparison of the two approaches is not necessary for the *Using EDOPS* page.

### 4.4 The appropriate characterization

The Societies panel should be described as an **interactive exploration of environmental distributions associated with selected ethnographic traits**, with the ability to examine geographic patterns and linguistic subsets.

Its primary value as an EDOPS example lies in demonstrating that environmental signatures can be joined to geographically referenced cultural observations and made available for comparative visual exploration.

The panel allows visitors to ask questions, inspect patterns, and identify possible directions for further investigation.

It does not provide evidence sufficient to establish causal or statistically supported relationships between environmental conditions and cultural attributes.

It is not necessary to diminish the example by apologizing for its preliminary status. Equally, its presentation should not imply a level of analytical rigor or explanatory power it does not possess.

An appropriate description should distinguish between:

1. What data have been brought together.
2. What the interface allows the visitor to inspect.
3. What kinds of questions those comparisons might suggest.
4. What the resulting displays cannot establish.

The final point need not dominate the interface, but it should be explicit wherever interpretation could otherwise exceed the evidence.

### 4.5 Recommended explanatory structure

The existing Societies panel can be accompanied by a small amount of contextual prose, potentially at different levels of detail.

**Navigation description:** A brief invitation identifying the cultural-environmental comparison. It should remain question-oriented rather than assertive.

**Panel introduction:** A short explanation of the selected ethnographic traits, their association with EDOPS environmental signatures, and the interactive comparative views.

**Optional explanatory modal:** A fuller account of the exploratory motivation, the environmental scans, language-family interaction, methodological limitations, and relevant published research.

The modal could explain Galton's problem and reference Botero et al. without making the entire development history of the exploration central to the presentation.

The *Using EDOPS* page does not need to become a history of how the Societies exploration was conceived and implemented.

Its purpose is to show a useful capability of the service.

## 5. Positioning the Other Examples

The discussion concentrated on Societies, but the underlying distinction applies to the other demonstrations as well.

### 5.1 World Historical Gazetteer / place enrichment

This example is closest to one of the original motivations for EDOPS.

The objective is to enrich geographically referenced place records with structured environmental information.

An environmental signature can support an automatically assembled profile of a place, potentially including a readable prose description generated from data and explicit rules.

This is an especially direct demonstration of EDOPS as infrastructure for place description.

It does not require making a causal claim about historical or cultural phenomena.

It illustrates how a gazetteer or other place-based information system can become more environmentally descriptive through integration with EDOPS.

### 5.2 African Regions / regionalization

The African Regions example demonstrates a different use of environmental signatures: comparing and characterizing geographic areas in terms of their environmental properties.

Its importance is not necessarily that it establishes a definitive regionalization of Africa.

Rather, it illustrates how the environmental variables made available through EDOPS can support regional comparison and exploratory classification.

The example should be presented as an exploration of environmental patterns and regional characterization, not as the final resolution of contested questions about regional boundaries or environmental homogeneity.

The specific analytical methods and findings should be described accurately from the existing implementation and development records.

### 5.3 Pueblo / historical-environmental inquiry

The Pueblo example points toward a further category of application, in which environmental characteristics are considered in relation to historical processes and questions.

As with Societies, it is important to distinguish between making environmental evidence available for historical inquiry and establishing an environmental explanation for historical events.

The example can illustrate the possible role of signatures in historically oriented investigation without requiring the dashboard to deliver a completed historical analysis.

### 5.4 A range of possible applications

Considered together, the examples span different relationships between environmental information and research activity:

| Example | Primary capability illustrated |
|---|---|
| WHG / place enrichment | Adding environmental descriptions to place records |
| African Regions | Comparing and characterizing environmental regions |
| Societies | Exploring environmental distributions associated with cultural traits |
| Pueblo | Bringing environmental information into historical inquiry |

These are different applications of the same underlying environmental signature service.

The range is important. It demonstrates that EDOPS is not tied to one kind of inquiry.

The examples should also be understood as a small selection of possible uses, limited by what has been developed so far.

Other users may identify applications that differ substantially from these demonstrations.

## 6. The Introductory Splash Panel

The *Using EDOPS* page currently opens with an introductory panel that does not display one of the individual examples.

This is an important opportunity.

Rather than using the opening panel merely as a navigation aid, it can establish the conceptual framework within which all subsequent examples should be understood.

The introductory panel can solve much of the communication problem centrally, reducing the need to explain the epistemic status of each exploratory example repeatedly.

### 6.1 What the introduction needs to communicate

The introductory panel should establish four ideas.

**First: EDOPS is a data service.**

It assembles environmental information from multiple sources and makes environmental signatures available for places through a common geographic framework.

**Second: the examples demonstrate possible uses of those signatures.**

They show ways the data can be incorporated into place descriptions, regional comparisons, and exploratory historical or cultural inquiry.

**Third: the examples are not completed research studies.**

They are preliminary explorations and working demonstrations intended to reveal possibilities rather than establish scientific findings.

**Fourth: the underlying signatures are available for other uses.**

The dashboard and API make it possible for researchers and developers to pursue their own questions and applications beyond those illustrated here.

This fourth point is particularly important because it prevents visitors from mistaking the existing examples for the intended limits of the system.

### 6.2 Recommended tone

The introductory statement should be:

- Clear and straightforward, avoiding promotional language.
- Confident about what EDOPS actually provides.
- Modest about what the exploratory examples establish.
- Inviting toward further inquiry and independent applications.

It should not read like an apology for methodological incompleteness.

Nor should it describe the examples as completed research contributions.

The point is to establish their intended function accurately.

### 6.3 Candidate introductory text

The following is a working formulation, not a final editorial decision:

> EDOPS brings together environmental variables from global datasets and makes them available as place-based signatures, organized by hydrological basins.
>
> The examples here illustrate ways these signatures can be used to explore questions about places, regions, and human history. They are preliminary investigations, intended to suggest possibilities rather than establish research findings.
>
> The underlying data are also available through the API for computational analysis and integration with other research tools.
>
> Choose an example on the left.

This text reflects the main conclusion of the discussion.

The particularly important wording is:

**“Intended to suggest possibilities rather than establish research findings.”**

It conveys the status of the examples without devaluing them.

An alternative could emphasize that these are applications developed so far, rather than a prescribed set of uses. This may help encourage visiting researchers to imagine their own applications.

### 6.4 Visual design considerations

The current splash panel has ample open space. There is no particular need to fill it with lengthy explanatory prose.

A small number of carefully composed paragraphs may suffice.

The individual navigation entries can remain concise and question-oriented.

Longer methodological explanations can be available within specific example panels or through optional modals and links.

The introductory panel establishes the general framing; the example panels explain the particular applications.

## 7. Communication Strategy for the v1 Release

The v1 communication problem should be understood in terms of the project’s actual scope.

EDOPS is a substantial environmental data infrastructure produced through a limited development effort.

Its creator has deep experience in geographic information, geosemantics, conceptual and data modeling, historical gazetteers, and research software, but does not claim specialized expertise across the environmental sciences or the many disciplinary fields in which EDOPS might be applied.

The examples reflect interests, questions, and experiments that arose during development.

Some touch on research areas in which there is already a sophisticated body of literature and methodology.

It is neither feasible nor necessary to carry every exploratory application to the level of a publishable research study.

The value proposition of EDOPS lies primarily in the environmental signature service itself: the capacity to deliver environmental characterizations in forms that can support additional inquiry.

This is the point the v1 release should communicate.

### 7.1 What the examples should invite visitors to do

Ideally, an interested visitor will recognize that EDOPS could be applied to a different set of geographic observations, historical places, cultural attributes, or environmental research questions.

The response we hope to encourage is not necessarily:

> This demonstration has established an interesting scientific result.

It is closer to:

> I have a geographically referenced dataset or research question. What might these environmental signatures allow me to examine?

That shift in audience expectations is central to the page.

### 7.2 Making limitations visible without allowing them to dominate

The source datasets, spatial aggregation framework, temporal applicability, and other methodological assumptions must be made available and explained.

For the exploratory examples, relevant interpretive limitations should also be stated.

However, the page need not become a collection of methodological disclaimers.

The distinction between data availability, exploratory analysis, and scientific inference can be established in the opening panel and reinforced selectively where needed.

The examples can then concentrate on demonstrating functionality and possible analytical value.

### 7.3 EDOPS as a starting point for other researchers

The February 2027 Pittsburgh meeting offers an opportunity to expose the service to researchers who may recognize new applications or important extensions.

This is part of the current rationale for releasing v1.

EDOPS cannot simultaneously pursue every avenue suggested by its environmental variables, geographic framework, and potential relationships to cultural and historical datasets.

The hope is that the functioning infrastructure will stimulate interest from people with relevant disciplinary expertise, research questions, and resources.

The *Using EDOPS* page should support that goal by showing a range of concrete applications without presenting them as the full scope of the service.

## 8. A Possible Visual Explanation of EDOPS

Near the end of the discussion, the idea emerged of producing a short animated visual explanation of EDOPS.

This is a related but distinct communication opportunity.

The initial concept involved representing an environmental signature as a JSON object and then showing how structured environmental values can become a readable description of a place.

The transformation could be depicted visually, with selected values highlighted and connected to the phrases produced from them.

This would make clear that the descriptive output is derived from underlying data according to explicit rules.

The process is inspectable, rather than a mysterious or opaque interpretive operation.

A possible sequence would move from:

**Place → Geographic association → Environmental data → Signature → Human-readable description**

A longer three-minute video could then illustrate how the same signatures can support comparison and exploratory research.

Two related visual presentations might eventually be useful:

1. **What EDOPS is and does:** An explanation centered on environmental signatures and their role in place description.
2. **What EDOPS signatures make possible:** An introduction to downstream applications, including examples from the *Using EDOPS* page.

A silent, text-led animated presentation may be preferable to one relying on spoken narration. Short intertitles and integrated explanatory labels could be combined with animated maps, data structures, and interface views.

Programmatic animation would be particularly suitable because actual EDOPS data, interface elements, maps, and values could be used rather than relying on generated imagery that might misrepresent technical details.

This is not a requirement for the immediate prose work, but it may provide a valuable complement to the introductory splash panel and the broader v1 presentation.

## 9. Implications for Drafting and Implementation

The immediate task is not to produce a comprehensive research paper about the Societies exploration.

It is to write a small amount of accurately framed explanatory text that supports the purposes of the *Using EDOPS* page.

Recommended priorities are:

### Priority 1: Establish the overall framing

Revise the opening splash panel to state clearly that the examples illustrate possible uses of environmental signatures rather than completed research findings.

This should be done before investing heavily in separate explanations for individual examples.

### Priority 2: Review the navigation descriptions

Ensure that each example is introduced in language that communicates its characteristic use of EDOPS.

Question-oriented descriptions are appropriate where they invite inquiry rather than imply proven results.

The navigation should convey variety without overpromising analytical conclusions.

### Priority 3: Revise the Societies introductory explanation

The Societies panel should explain the available cultural trait selection, geographic distribution, environmental scans, and language-family interaction.

It should present these as exploratory affordances.

The explanation should make the role of EDOPS signatures explicit.

### Priority 4: Consider an optional Societies methodology modal

A modal could provide more detailed context for interested visitors, including:

- The original motivation for comparing environmental characteristics and cultural traits.
- The use of D-PLACE / Ethnographic Atlas variables.
- The association of societies with basin-based environmental signatures.
- The interpretation of environmental distribution displays.
- The addition of language family in response to Galton's problem.
- The limits of visual comparison for distinguishing environmental, spatial, linguistic, and historical explanations.
- A reference to Botero et al. (2014) as a rigorous investigation of a related question.

This modal should not become a full narrative of the development process unless that is independently desirable.

### Priority 5: Apply consistent framing to the remaining examples

African Regions, Pueblo, and WHG should be reviewed with the same distinction in mind: what the example demonstrates about the use of signatures versus what substantive research claims, if any, it can support.

Their explanations should be grounded in the actual implementations and development records.

### Priority 6: Preserve the possibility of richer visual communication

The animated explanation concept can be developed separately, potentially providing a more immediate and engaging introduction to environmental signatures than prose alone.

It should complement rather than replace accurate textual descriptions and methodological documentation.

## 10. A Note on AI-Assisted Documentation

The discussion began with a question about the intellectual legitimacy of asking Claude to draft project prose from accumulated development context.

This is relevant to the present handoff because Claude has participated extensively in the development of EDOPS, and the project maintains session records, daily logs, work orders, code comments, and other documentation.

These materials can provide a valuable basis for reconstructing the purposes and decisions behind individual demonstrations.

However, the drafting process should distinguish between documented motivations, implemented functionality, observations actually made during exploration, and interpretations that a language model might plausibly propose.

In particular, an LLM should not supply apparent research conclusions merely to make an explanatory account more complete or persuasive.

The purpose of AI-assisted drafting here is to provide a useful first formulation of material already developed and discussed, with subsequent human review and editorial judgment.

The present document is itself a synthesis of a sustained conversation in which the intended framing of the *Using EDOPS* page became clearer.

The role of AI in the wider development of EDOPS is substantial and includes conceptual, methodological, educational, and technical assistance. That broader history is important but need not be foregrounded in the *Using EDOPS* introductory material, whose immediate purpose is to explain the service and its possible applications.

## 11. Central Conclusions

The most important conclusions from the discussion are these.

**EDOPS is fundamentally a service for generating and exposing structured environmental descriptions of places.** Its principal contribution is the environmental signature and the infrastructure that makes signatures accessible.

**The *Using EDOPS* page demonstrates the utility of that service.** It is not a collection of completed scientific studies.

**The existing examples represent actual exploratory applications.** They provide windows into possible uses of environmental signatures, but they do not define the limits of the service.

**The Societies exploration should remain an exploration.** Its value lies in showing how environmental signatures can be brought together with cultural and linguistic data and examined interactively. It need not be elevated into a rigorous investigation of environmental explanations for religious beliefs.

**Relevant scholarship should inform the framing without overwhelming it.** Botero et al. (2014) is particularly relevant to the Societies example, but the EDOPS demonstration should neither claim to replicate nor improve upon that research.

**The opening splash panel should establish these expectations for the whole page.** Doing so allows individual examples to remain approachable and visually focused while preserving appropriate methodological modesty.

**The desired outcome is that researchers recognize possibilities for their own work.** The page should encourage them to imagine how the signatures might be used in settings and investigations beyond the developer's own examples.

## 12. Final Framing

The *Using EDOPS* page occupies an important position between the technical infrastructure of EDOPS and the many possible research inquiries that might make use of it.

The project does not claim to explain the relationships between environment, culture, and history.

It provides environmental representations that can be brought into such investigations.

The examples are deliberately situated near this boundary. Some enrich the description of places; others begin to explore comparisons and possible associations. None should be mistaken for a completed disciplinary investigation merely because it raises a substantive research question.

The task for v1 is to make this distinction clear without diminishing the work, overstating its findings, or burdening the visitor with excessive methodological explanation.

A successful *Using EDOPS* page will leave visitors with an understanding of what environmental signatures are, evidence of several ways they can be used, and an invitation to consider what they might make possible in their own research.

**EDOPS provides the environmental information. The examples open windows onto possible uses. The questions and investigations that follow belong to the people who take the signatures further.**

