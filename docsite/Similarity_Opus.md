# Similarity instruments

EDOPS can answer two different questions about environmental similarity, and it answers them in two different ways. The wording on screen doesn't always make the difference obvious — both surfaces use words like "regime" and "similar" — so this page explains what each one is doing and what its results let you say.

The short version:

|  | **Sandbox → Similarity** | **Workbench → WH Cities** |
| - | :-: | :-: |
| The question | Where else meets *all* of these conditions? | Which places are *most like* this one? |
| What comes back | A set — every member cleared every bar | A ranked list — nearest first |
| Can it come back empty? | Yes, and that's a real answer | No — ask for five, get five |
| Compared against | All 16,397 basins (or 190,675 at level 8) | The 254 World Heritage Cities |


Both are built on the same validated comparison of monthly climate curves. They differ in what they do with it.


## The distinction that matters

Ask whether a good match on one thing can make up for a bad match on another.

**Sandbox says no.** Each condition is a separate pass/fail test in ordinary units. Does this basin's rainfall curve track your query's closely enough? Is its annual total within a factor of 1.5? Is its mean temperature within 3 °C? Fail any single test and the basin is out, however well it does on the others. What comes back is everything that cleared every bar — a set you can paint on the map, not a leaderboard.

**WH Cities says yes.** It summarises each city's climate as a handful of numbers and measures the straight-line distance between cities in that summarised space. Because distance adds up the mismatches, a city that's wrong about *when* the rain falls can still score well by being very right about *how much* falls — the errors trade against each other. What comes back is the five nearest, in order.

Neither is more correct. They suit different questions, and one consequence is worth stating plainly:

!!! note "An empty set is information" When the Sandbox returns nothing, that is a finding, not a failure. It means nowhere else on Earth is simultaneously that wet, that seasonal, and that warm. A ranked list can never tell you this — ask for the nearest five and you will always get five, no matter how far away they turn out to be.

### The same query, three lenses

Ask the Sandbox about Tbilisi's basin at the default settings and switch lenses:

| Lens | Basins in the set | Set spans |
| - | - | - |
| Precipitation regime | 38 | 11,983 km |
| Temperature regime | 425 | 12,750 km |
| Climate (precipitation + temperature) | **14** | **2,036 km** |


Two things happen when you combine the conditions. The set gets smaller, which you'd expect. But it also gets *geographically coherent*: the precipitation and temperature sets are each scattered across continents, while their intersection is a single region — Romania and the Caucasus, about 2,000 km across.

Nothing in the instrument asked for that. No condition mentions location, distance, or continent. The places that satisfy all five requirements at once simply turn out to be near each other, and that is the kind of thing this instrument exists to notice.

Terrain, at the same settings, does the opposite and is worth seeing for contrast: **6 basins** **spanning 13,361 km** — the most selective lens on the panel returning the most widely scattered set, slivers from Nevada to Afghanistan. A small set is not the same as a local one.


## Sandbox → Similarity: the set

Pick a lens, set how tight you want each requirement, and the map paints every basin that satisfies all of them. Basins outside the set are left unpainted.

Four lenses are available, and each asks about a different physical thing:

- **Precipitation regime** — the timing, the amount, and the evenness of the rainfall year, all three at once.

- **Temperature regime** — how warm the year is on average and how wide the swing between seasons is. There is no timing requirement here: temperature curves within a hemisphere are too much alike for timing to distinguish them, so asking would add a condition nothing fails.

- **Climate (precip + temp)** — all five requirements together. The two lenses above are subsets of this one, so its set can only be smaller than either.

- **Terrain regime** — how high the basin sits and how much vertical range it contains.

Each control's own tooltip explains what it measures. The thing to know about all of them is that **every band is measured against your query's own values**, not against a fixed global cutoff. Asking "what's like Bruges" and "what's like Tbilisi" runs the same instrument; only the anchor moves.

### Reading the result

The line above the map gives you the size of the set and how far it spreads:

> Your query matches **38** basins under *Precipitation regime* — spanning 11,983 km.

**Both figures are global.** The span is the distance between the two furthest-apart members anywhere on Earth, and 11,983 km is far more than the map in front of you can show — so if you are looking at Europe, you are seeing part of this set, not all of it. Zoom out before concluding anything about where the matches are.

That spread is often the interesting part. The Tbilisi query above returns basins in Romania *and* in the Caucasus, plus more elsewhere: a set that is genuinely disjunct, in clusters thousands of kilometres apart. A ranked list of nearest neighbours would have shown you the closest few and told you nothing about that shape.

**The legend tells you which kind of lens you're on.** A gradient reading *weaker shape match →* *stronger* means the lens has a shape condition, and members are shaded by how closely their rainfall curve matches yours. A solid swatch reading *in the set* means it doesn't, so there is nothing to shade by and every member looks alike.

Where there is shading, it is for reading the map, not a verdict. Every painted basin passed every condition. A pale member is not a worse match — it is a member.

### One refusal worth knowing about

Below about 100 mm of rain a year, the shape of the monthly curve is mostly noise — the numbers are too small for the pattern to mean anything. Rather than compare them anyway and hand back a confident number, EDOPS excludes very arid basins from any shape condition. They stay eligible on annual total and on temperature, which are still real measurements. If you query a desert basin and the precipitation lens returns nothing, this is usually why.

### The footnote under the map is doing real work

*"This describes the Level 6 basin Tbilisi sits in, not Tbilisi itself."*

Basins are delineated by drainage topology, not by anything a person would recognise as a locality, and they can be far larger and more varied than the place you asked about. San Francisco's level-6 basin is a long peninsular ridge catchment with 1,602 m of internal relief; downtown San Francisco tops out around 280 m. Innsbruck behaves the same way.

On the Terrain lens the footnote says more, and means it: the figures are the basin's overall elevation and relief range, not fine-grained ruggedness, and they carry no information about *where* *within* the basin your place sits. A basin can match on both bands while looking nothing like the ground your settlement actually occupies.


## Workbench → WH Cities: the ranked list

The corpus here is 258 World Heritage Cities, 254 of which sit in a basin EDOPS can resolve. Tbilisi appears at the top of the picker as a 259th entry; it is not an OWHC member and sits deliberately apart from that count.

**Precipitation regime** and **Temperature regime** compress each city's climate into a small set of summary figures — for precipitation, its annual total plus four numbers describing the shape of its year; for temperature, its annual mean plus two describing the size and concentration of its seasonal swing. Cities are then ranked by distance in that summarised space and the nearest five returned.

**Terrain regime** works differently again, and differs from the Sandbox's terrain lens in the thing it measures rather than just in how it ranks. Instead of using basin-wide averages, it samples a 5 × 5 grid of elevations spanning about 10 km around the city's actual coordinates, fetched live. Three tolerance bands — elevation, local ruggedness, and landform position — decide which cities are *eligible*; the eligible ones are then ranked and the top eight shown. So it filters like the Sandbox and ranks like WH Cities: a hybrid.

Sampling around the coordinates is the more faithful measurement of the two, for exactly the reason the Sandbox's footnote gives — it reads the place rather than the basin. It exists only for this corpus because fetching live elevation grids for every basin on Earth isn't practical.

### Why not use the Sandbox's method here?

Because the corpus is two orders of magnitude smaller, and that changes what selectivity means. A tolerance band tuned to be genuinely discriminating across 16,397 basins picks out a fraction of one percent of them. The same discipline applied to 254 cities admits roughly 9–14% — twenty to thirty five cities. That isn't a tuning error; it's what happens when the pool is small. Twenty-five "eligible" cities is a weaker answer than five ranked ones, so the retrieval head reports rank and distance instead.


## Semantic similarity

The WH Cities panel has a second dropdown, **Similar (semantic)**, which shares the page and nothing else. It compares cities by the text of their Wikipedia articles, sliced into thematic bands — Environment, History, Culture, Modern, or a composite of all of them — and returns cities discussed in similar terms.

This measures **discourse, not environment**. Two cities can come back as semantically similar because the same things get written about them, which may reflect shared history, shared scholarly attention, or shared editorial habits rather than any physical resemblance. It's a genuinely useful lens on a different question. Don't read it as environmental evidence, and don't expect it to agree with the environmental lenses.

Semantic similarity is unavailable for Tbilisi, which has no scraped article text.


## What a result licenses

These instruments retrieve; they do not test. A returned set or ranked list says *these places* *resemble each other in the respects this lens measures* — nothing about why, and nothing about whether the resemblance matters for anything cultural.

In particular, none of these results speak to whether environment shapes culture. That's a different question with different machinery, and finding that two cities share a rainfall regime is not evidence about it in either direction.

The environment↔culture correspondence work on the Workbench's Societies tab is a separate instrument answering a separate question. It isn't documented here.

