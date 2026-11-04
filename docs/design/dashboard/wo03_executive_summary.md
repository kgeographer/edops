# WO-03 executive summary: what each question was for, what it found, what it might mean

Draft 2026-11-04 by Claude Code, for Karl and Opus. Not reviewed. Plain language, few numbers; every number here is in `wo03_results.md` (section named in each heading) and `wo03_summary.md` (decisions list).

## The aim these findings feed

Rules that read a place's environmental data and produce friendly prose about its setting: its basin, the basins around it, its ecoregion, its rivers. The prose will mostly not recite numbers. The numbers (values, distances, counts) need to be available somewhere, perhaps a click away. The size and shape of the payload are not decided. WO-03 measured what the data and the existing code do, so that those decisions rest on evidence. It makes no recommendation. "Might" below means a possibility the findings make visible, not a conclusion.

Throughout, two kinds of place were used. The random-basin sample (306 basins, interior points) is not a settlement sample. The 258 World Heritage Cities are real settlements, but probably sit nearer rivers and coasts than settlements in general. Where both were used, they roughly bracket the answer.

## Q1. The ring as it stands (results 1a to 1l, issues I-1 to I-8)

**Why it was asked.** The profile describes a place against the basins that touch its own. Before designing that, we needed to know how big a ring is, what it costs to compute and send, who counts as a neighbour, and whether the existing direction words ("to the north-east") can be trusted.

**What was found.**
- A ring typically has about 5 neighbours (most have 3 to 9; the largest 18). Coastal basins often have few or none; island basins have none.
- The existing call takes roughly a second per basin (5 to 17 s for a ring) and returns 89 to 290 KB. A compact neighbour row would weigh about 7.6 KB; a whole compact ring 43 to 114 KB, 3 to 6 KB compressed. All the scores for a ring can be computed in one pass with identical results to computing them one at a time.
- "Touching" includes corner contacts with no shared border (1.5% of neighbours, mostly coastal) and very short borders.
- Direction words are measured from the middle of the core basin, not from the place. Measured from the place, the word changes for about 1 neighbour in 5 (8-point), and the different ways of computing a direction often disagree.
- Where a variable is zero often differs between the core and its neighbours.
- "Coastal" means three different things in three places in the code.

**What it might mean for prose.** A ring is small enough that "the basins around it" can be a handful of facts. Compass words are the weakest part: a rule might drop them, or use them only when the methods agree. Statements about neighbours need a rule for corner contacts and very short borders, and a choice of which "coastal" they mean. Rings with no neighbours need their own wording.

**Not answered.** Whether the faster one-pass build can feed the whole rest of the pipeline (not tested).

## Q2. Flow relation of neighbours (results Q2, issue I-8)

**Why it was asked.** Compass words are shaky. "Upstream of", "downstream of" and "across a divide" might be a sturdier way to relate neighbours to a place, and a more meaningful one in a river-basin dataset.

**What was found.** Each neighbour can be labelled upstream, downstream or off the core's stream from the source's own topology, with no unknowns. Only about a quarter of neighbours are on the core's own stream (12% upstream, 12% downstream); three quarters are across a divide. 30% of rings have an upstream neighbour, 58% a downstream one. Some small inland sinks have a link to a downstream basin that is not real surface flow (the source flags these; they were cut). For variables describing the whole upstream catchment, flow neighbours differ from the core by about half as much as other neighbours, mostly because their catchments overlap heavily.

**What it might mean for prose.** A rule might say "drains into" or "receives water from" when true, and speak of "across the divide" otherwise, without compass words. For near-identical catchments (a neighbour that is almost the same upstream area) a statement about differences would manufacture contrast that is not there; ties and zeros also need handling in "ranks Nth of M" wording.

## Q3. Ecoregions (results Q3)

**Why it was asked.** The profile names an ecoregion, with a Wikipedia link and summary. We needed to know how many ecoregions a basin and a ring typically touch, whether the place's own ecoregion is also the basin's main one, and how complete the text coverage is.

**What was found.** A basin typically touches 1 or 2 ecoregions of any real size (about half have just one at 5% of area or more); a ring 2 or 3. The place's own ecoregion is the basin's largest in 94% of sample basins; in the rest the place sits in a smaller one. Coastal and lake basins are partly outside every ecoregion polygon. 26 of 847 ecoregions have no Wikipedia text; Karl suspects renamed or newly added ecoregions (unchecked).

**What it might mean for prose.** One ecoregion can usually be named for a place with little risk. A second can be mentioned when it covers a meaningful share, which needs a cutoff (the data gives 1% and 5% as comparisons). A coastal or lake share outside every ecoregion needs wording that does not invent one. The position of each ecoregion within the basin (for example "the north of the basin is mountain forest") was not measured; it is noted for the algorithm stage.

## Q4. River names (results Q4, issue I-9)

**Why it was asked.** Prose about rivers reads better with names. The database has rivers but no names, so we tested whether Natural Earth's named river lines (supplied by Karl; visible gaps in deserts and mountains) would serve.

**What was found.** Near the main river, the layer has a named line for about 60% of World Heritage Cities (higher in Europe, low for Arab states) and about 38% of random basins. When there is a match it is tight, but the named river can be far from the place, and some names are branches (the Lek, not the Rhine). A missing name never means a missing river: the river network shows a river where the layer has no line (Berlin).

**What it might mean for prose.** A rule might state that a river of a given size passes a given distance away, and add a name only for a close, confident match: "Vienna is on the Danube" needs a close named line and a close river reach. Otherwise generic wording ("a river runs nearby"). The layer is an optional enrichment, not a dependency.

**Not done.** The work order's version (match names along main stems; share of cores and rings with a named river) was not run. One of the two river tables in the database is incomplete (northern North America and Greenland missing); the complete one was used.

## Q5. Nearest main stem (results Q5)

**Why it was asked.** A basin's own numbers may not describe the river that defines a place. Kaifeng sits in a small basin beside a very large river.

**What was found.** At Kaifeng the nearest large river is 11.5 km away and drains 48 times the basin's own area. In random basins, the nearest river above the cutoff is at least 10 times the basin's own area for about 4% (1,000 km² cutoff; median 10 km away) and 15% (10,000 km²; median 62 km away); at 100,000 km² the nearest such river is typically hundreds of km away. No river that touches the core was 10 or more times its area. Upstream area measures size at that point, not the river's size overall: a major river near its source looks small.

**What it might mean for prose.** A rule might add "the nearest large river is N km away" where the basin's own signature would miss it, and it must pair any "much larger than" claim with a distance. The measure should not be used to say how important a river is.

## Q6. Where the point sits (results Q6)

**Why it was asked.** Two design questions: how near a place usually is to its basin's edge (so "near the edge of its basin" can be worded), and what to do when a point is in no basin (the snap tolerance).

**What was found.** For World Heritage Cities the median distance to the basin's outline is 7.6 km, about 8% of the basin's size; a neighbouring basin lies within 5 km for 19% and within 25 km for 69%. For a third of cities the nearest edge is the coast, not a divide. Of 3,000 settlements, 2,994 have a basin. The six that do not are five islands the basin data does not cover and one point 0.2 km outside an edge (Akureyri); Levuka (Fiji) is under 5 m outside.

**What it might mean for prose.** "Near the edge" needs to say which kind of edge. A snap of about 1 km would fix the near-edge cases and nothing else, so island places need a structured no-basin response, and any description of them would have to come from something other than basin data (ecoregion data may still apply; not tested). Points just offshore of a coast were not measured.

## What WO-03 does not settle

Payload size and shape, any statement wording, whether the one-pass score build is acceptable, a cutoff for "neighbour", "near" or "significant", and whether users want any of this. The decisions list in `wo03_summary.md` (items 1 to 11) is where those open choices are collected.
