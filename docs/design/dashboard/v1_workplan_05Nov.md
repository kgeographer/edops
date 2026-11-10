# Sample page for Stephen and Ruth: two-week plan

Draft 2026-11-05, for Karl. Target: send by Saturday 21 November, before Kathmandu.

## What the sample page is for

A page showing what the [Environmental Profile] modal on a WHG place page could say, for three or four places. Stephen and Ruth react to it while Karl is away: they may want all of it, less, or more, and they will have views on the language. Their response shapes the endpoint work in January.

The page doesn't need everything to be built. It shows two kinds of sentence, marked differently:

- **Generated**: produced by EDOPS rules from real data.
- **Planned**: written by hand in the intended style, for sentences whose rules are not yet built.

That lets them judge the full scope, and comment on the language, before we fix the rules. A short cover note goes with the page: what is built, what is planned, and the questions we'd like their view on.

## First decision: does each section speak about the place or the basin?

The WO-04 profiles showed the problem. Tbilisi's profile says "Temperatures average 5.3 °C, from -5.9 °C in January." That is true of its 23,000 km² basin, most of it higher ground upstream, but not of the city, which averages roughly 13 °C. A reader takes the sentence as being about Tbilisi, and finds it wrong.

Three options, shown for Tbilisi:

**A. Setting about the place; everything else about the basin, openly.** (recommended)
> Tbilisi sits at about 500 m above sea level, in the Caucasus mixed forests ecoregion. Across its surrounding basin of about 23,000 km², rainfall averages about 760 mm a year and temperatures average 5 °C …

The place gets what is cheap to look up at the point (elevation, ecoregion). The basin stays the unit of analysis and is named as such. Point climate can be added later.

**B. Everything about the basin.**
> The basin of about 23,000 km² that contains Tbilisi lies mostly in the Caucasus mixed forests ecoregion. Rainfall across it averages …

Simplest, and needs no point layer. It reads more like a data sheet and less like a description of a place.

**C. Everything about the place, with point climate.**
> Tbilisi sits at about 500 m … Rainfall here averages about 500 mm a year; temperatures average 13 °C …

The most natural reading, but it needs point values for climate (and later other measures). It also mixes scales: point climate next to basin land cover.

Values in these examples are illustrative.

## Setting: what makes a place's setting distinctive

Basin values can hide a place's real setting. Tbilisi sits low in the Kura valley with higher ground on most sides; its basin's averages describe the higher, colder land around and upstream of it. Three comparisons can expose this, at very different cost:

1. **The point against its own basin.** Where the place's elevation falls in its basin's range.
   - *Now:* from `elev_min` and `elev_max` (and the basin's mean elevation, if loaded): "Tbilisi sits at about 500 m, in a basin that runs from about 300 m to over 3,000 m." A number, no cutoff. Goes in WO-05.
   - *Later:* the basin's elevation distribution, for "lower than four-fifths of its basin". Not to hand; needs one zonal histogram per L6 basin from a DEM, a one-off precompute alongside the persisted build.
2. **The core against the ring.** Elevation range, relief and roughness (the Terrain lens measures) compared across the basins that meet here: "the most rugged of the eight basins around it". Comes with the neighbour-comparison rules, if WO-06 includes the terrain measures.
3. **The point in its immediate landform.** "In a valley floor, with higher ground on most sides"; "within 20 km the land rises 1,200 m above the city." Needs elevation around the point at a few radii (say 5, 20 and 50 km). A DEM of about 1 km (30 arc-seconds) is enough at that scale, so a 50 km window is roughly 10,000 cells: read live per click or cached per place, independent of the 16,000-basin build. Class words could come from a published scheme (topographic position index classes, as in Weiss's landform classification) rather than a cutoff of our own. Planned sentence on the sample page; built in January.

To turn cost into numbers before January, WO-05 also times: a DEM window read at the ten test places, and the elevation histogram for a few dozen basins.

## Places

Three or four that show range:

- **Timbuktu**: a river corridor set in a contrasting surround.
- **Tbilisi**: a place on a gradient, where the ring crosses a major divide.
- **Kaifeng**: the river that defines the place is not the basin's own.
- **Santa Fe or Chaco Canyon**: anchors the New Mexico worked example, and Santa Fe is where Karl will be from 28 December.

## Work, in order

The dates are calendar days and assume Karl's usual pace; move them as needed. Each step is one CC work order with one gate, and Karl reviews each before it goes.

**Thu 5 to Fri 6 Nov. Framing decision.** Karl chooses A, B or C. Opus revises the templates in `modal_dummy.md` to match and drafts WO-05.

**Sat 7 to Tue 10 Nov. WO-05: place layer and fixes.**
- Point elevation (a DEM sample or WHG's own value) and the point's ecoregion.
- The point against its basin's elevation range (Setting, comparison 1, the version from `elev_min` and `elev_max`).
- Timings: a DEM window read at the ten test places; the elevation histogram for a few dozen basins.
- Templates reworded to the chosen framing.
- Small fixes from WO-04: a rule for "0 km" to the sea; a check of all 847 ecoregion-to-Wikipedia links (Alexandria's goes to "Woodland"); readable labels in place of internal names such as `wet_pct_grp1`; check Alexandria's 100% karst at source; check how the source classes the Caspian ("drains to the sea" at Tbilisi).
- Wording for the four kinds of basin the water sentence does not yet fit (it fits 5% of basins now).

**Wed 11 to Sun 15 Nov. WO-06: neighbour comparisons.** The rules behind the Surroundings section and the "among the driest" kind of statement: rank among the basins that meet here, counts above and below, ties, zeros. One decision for Karl first: how a rank is worded. Include the Terrain lens measures (elevation range, relief, roughness), so the core-against-ring setting comparison comes with it. Tested over the 306 sample basins. The Surroundings section is the newest and most interesting part of the profile, so it should be generated, not planned.

**Mon 16 to Tue 17 Nov. WO-07: class words, the straightforward ones.** Relief and river-size classes from the published schemes in `wo04_schemes.md`; soil texture and aridity if they are equally direct. Anything needing a sweep waits.

**Wed 18 Nov. Cut line.** Building stops. Whatever is not generated by now becomes a planned sentence.

**Wed 18 to Thu 19 Nov. Assemble the page.** CC regenerates the profiles for the chosen places. Opus writes the planned sentences, marked as planned, and lays out the page. Karl carves the language.

**Fri 20 Nov. Cover note.** Opus drafts it; Karl rewrites it.

**Sat 21 Nov. Send.**

## What the page could look like

Either a markdown or PDF document, or a web page laid out like the modal itself (sections, buttons, generated and planned sentences in different styles) that Karl can share by link. The second shows the modal as a WHG user would meet it. Karl's call.

## Questions for the cover note (draft)

- Is this the right set of sections? What is missing, and what would you drop?
- Place or basin: does the framing read clearly?
- The language: tone, length, and how numbers are spoken.
- The buttons: a link into EDOPS for the full signature, the ecoregion's Wikipedia page, and the data as JSON. Is a link from WHG into EDOPS acceptable?
- Should the profile include generated text from a language model, clearly marked, or rules only?
- Setting statements of the "valley floor, higher ground on most sides" kind: are these what you'd value most?

## If time runs short

In order of what to drop: the class words (WO-07) become planned sentences first; then the wording for the other water classes; then the point ecoregion. The framing decision and the neighbour comparisons stay.

## After the trip

**1 to 7 December.** Read their response, decide what changes, and write the January plan. If their response is slow to arrive, the OWDA pre-build checks (readmes, file structure, year convention, licence) fit here as a small CC job.

**28 December onward, Santa Fe.** Endpoint tuning and the demo; the non-global dataset architecture; the worked examples.

