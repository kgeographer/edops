# Profile templates: the wording the filled_profile generator uses

This file is the target of the WO-04 to WO-07 work: the wording of the Environmental Profile as the generator (`scripts/edop/whg/wo04_fill.py`) puts it together. The generator reads this file every time it runs. Edit the wording here; the rules (what is true, which number, which branch) stay in the script.

**How to edit.** Each line is `key: text`. A `{slot}` is replaced by the generator: `{name}` is the place name; `{S2.1a}` and the like are units of `modal_dummy_annotated.md` (a filled value, or a visible placeholder when the unit is not built yet). Other slots in the Phrases part (for example `{km}`) are named in the notes beside them. Keep the slots you want to show; remove one and the value is dropped. A slot the generator does not supply stops the run with the key and the slot named.

**Every change is recorded.** Whoever edits this file (Karl, Opus or Claude Code) raises `Version:` by one and adds a line to Changes: `- vN | date | who | what and why`. The generator will not run if the newest line in Changes does not match `Version:`. Each generated file states the version, the last commit of this file, and whether it has been edited since.

Version: 6

## Changes

- v1 | 2026-11-05 | CC | Wording moved out of wo04_fill.py into this file. No wording changed: the ten filled_profiles regenerate identically.
- v2 | 2026-11-05 | Opus | Framing A (Karl's decision): Setting speaks about the place; the other sections name the basin they describe. S1.2a now means the point's ecoregion. New units S1.2c (the basin's majority ecoregion, when it differs) and S1.5a, S1.5b (the basin's elevation range); wording for the four water classes other than exogenous; a phrase for a basin that meets the sea at its outlet; S8 says which figures are the place's and which the basin's. Needs WO-05 for the new units and phrases before it runs.
- v3 | 2026-11-05 | CC | Two lines added, no other wording changed: `S3.2.undetermined` (empty, like endorheic; the sixth class of the Analysis tab's rule, a basin whose upstream area is under 500 km², where the rule makes no comparison) and `label.upstream` (readable names in the S8.2 lists, from the variable catalog; an upstream measure reads "Karst area (upstream)").
- v4 | 2026-11-07 | CC | Water wording checked against the Analysis rule's classes over 306 sample basins (WO-05 item 2, `wo05_results.md`). New `S3.2.headwater`, used for the uniform and local classes when no other basin drains into this one (area ratio 1.05 or less; 118 of 181 such basins): "uniform" had said "1.0 times the size ... with much the same climate", which compares a basin with itself. `S3.2.local` rewritten: it had said "most of the water passing here falls locally", but 43 of 46 sample basins in the class have an upstream catchment over twice the local basin, and the class is the rule's residual. New `S3.2.coastal_large`, used when a coastal-terminal basin has an area ratio over 2: the rule tests only distance to the sea, so "little water arrives from upstream" is not safe there; `S3.2.coastal` unchanged otherwise. `S3.5.sea` and `S3.5.inland` reworded ("beyond its outlet") because "downstream of the basin" repeated the subject. Exogenous, endorheic and undetermined unchanged. Needs the script rule for the headwater and coastal_large switches (wo04_fill.py).
- v5 | 2026-11-07 | CC | Ring comparison wording (WO-06), from Opus's draft in `wo06_basin-rings-comparisons.md` with these changes: `S6.2` (one line) is replaced by `S6.2.in_none`, `S6.2.in_one`, `S6.2.in_some`, `S6.2.out_one`, `S6.2.out_some` (new: a basin can drain into more than one of the basins around it, through a chain) and `S6.2.out_none`; new `S2.3.extreme`, `S2.3.count`, `S5.2.extreme`, `S5.2.count`, `S6.3.all`, `S6.4` (states the count of measures outside the neighbours' range, and is silent when there are none), `S6.5`; `cmp.<measure>.top|bottom|more|less` for every measure the sentences use (the full list is in the Comparisons part below; relief, slope, forest, karst and the soil shares have only top and bottom, since they appear only in S6.5). Precipitation has its own frames (`S2.3.extreme.precip`, `S2.3.count.precip`, `S6.3.all.precip`: "receives the least precipitation"), so that "dry", "wet", "arid" and "humid" are used for aridity only; extremes over the same set of basins and frame are joined into one sentence. Small numbers are written as words (one to ten) by the script. No existing wording changed, but the ring keys switch the new rules on: a template without them still regenerates as v4.
- v6 | 2026-11-08 | CC | WO-07 part A, from `wo07_...` Opus draft with these changes: ring sentences state an extreme, "all" or "all but one" first and a count only when none of those holds (new `S2.3.allbutone`, `S2.3.allbutone.precip`, `S5.2.allbutone`, `S6.3.allbutone`, `S6.3.allbutone.precip`; the script needs at least five basins with a value for "all but one"); the middle-count lines `S2.3.count`, `S2.3.count.precip` and `S5.2.count` stay in, at Karl's decision (Opus's draft dropped them; the stakeholder review can cut them, and removing those three lines switches the counts off, their content then staying in the fill notes); `S6.4` and its slot in `S6.frame` are removed (a value outside the neighbours' range is being highest or lowest, which S6.5 names); `S6.5` now also draws on runoff, permafrost and water-table depth (new `cmp.runoff.*`, `cmp.permafrost.*`, `cmp.gwdepth.*`); population density and human footprint are left out of the sentences (`cmp.popdens.*` removed); `S2.3.extreme` is one sentence in the form "Of the n basins that meet here, it receives the least precipitation and is the most arid" (the S2.3 `top`/`bottom` words become verb phrases; `S2.3.extreme.precip` removed); `S5.2.extreme` opens "Among the n basins" so that the sections do not repeat one opening; `S6.2.out_some` reads "Its water flows on through n of them" (a basin whose next basin downstream also has a further one at its border drains into both, but not by two outlets); `S3.2.headwater` and `S5.1b.some` as Opus worded them. WO-07 part C: new `S3.1.on`, `S3.1.named`, `S3.1.unnamed_on`, `S3.1.unnamed` (S3.1 is now a sentence of its own and the Water frame no longer opens with the place's name; it names a close river, says there is one when none is named, and is silent when none is close), `S3.3.named`, `S3.3.unnamed`, `S3.3.same`, `S3.3.same.named` (when the much larger river is the one S3.1 already names; the nearest river and a much larger river nearby; the script reads the HydroRIVERS discharge class and Natural Earth names).

## Section titles

S1.title: Setting
S2.title: Climate
S3.title: Water
S4.title: Land and geology
S5.title: Land cover today
S6.title: Surroundings
S7.title: Coast and reach
S8.title: About these figures
S9.title: Buttons

## Section sentences

Slots are unit ids. `{S1.2c}`, `{S3.2}`, `{S5.1a}` and `{S5.1b}` are built from the phrases further down.

Setting speaks about the place. `{S1.1b}` is the elevation at the point; `{S1.5a}` and `{S1.5b}` are the lowest and highest elevation in the basin that contains it; `{S1.1c}` is a terrain word for that basin (WO-07). `{S1.2a}` is the ecoregion at the point.

S1.frame: {name} sits at about {S1.1b} m above sea level, in a basin of {S1.1c} country that runs from about {S1.5a} m to {S1.5b} m. It lies in the {S1.2a} ecoregion, {S1.2b}. {S1.2c} {S1.3} {S1.4}

The other sections speak about the basin and say so.

S2.frame: Across the surrounding basin of about {S8.1a} km², rainfall averages about {S2.1a} mm a year, {S2.1b}. Temperatures there average {S2.2a} °C, {S2.2bc}. {S2.3}
S3.frame: {S3.1} {S3.2} {S3.3} {S3.4} The basin drains {S3.5}.
S4.frame: Across the basin, the land is {S4.1a}, with {S4.1b}. The underlying rock is mostly {S4.2}. {S4.3}
S5.frame: Today {S5.1a} and {S5.1b}; {S5.1c} covers most of the rest. {S5.2}
S6.frame: {name}'s basin is one of {S6.1a} that meet here. {S6.2} {S6.2c} {S6.3} {S6.5}
S7.frame: {S7.1a} {S7.2} {S7.3}
S8.frame: The elevation and ecoregion under Setting are for {name} itself. The other figures describe the basin of about {S8.1a} km² that contains it, from global datasets of about {S8.1b}. {S8.2} {S8.3}
S9.frame: {S9.1} [Ecoregion on Wikipedia: {S9.2}] [Data as JSON: always]

## Phrases

Setting. `{eco}`: the basin's majority ecoregion. S1.2c appears only when it differs from the point's.

S1.2c: Most of its basin lies in the {eco} ecoregion.

Climate. `{lo_temp}`, `{lo_month}`, `{hi_temp}`, `{hi_month}`: coldest and warmest month of the monthly temperature curve.

S2.2bc: from {lo_temp} °C in {lo_month} to {hi_temp} °C in {hi_month}

Water. S3.2 takes one form for each class of the Analysis tab's rule. `{S3.2a}`: ratio of the catchment above to the local basin. `{S3.2b}`: the comparison word. `{km}`: distance along the river from the basin's outlet to the sea or inland sink. The four forms other than exogenous are drafts; CC checks each against the rule's definition of its class and reports where the wording claims more than the class means.

S3.2.exogenous: Most of the water passing here falls far upstream: the catchment above is {S3.2a} times the size of the local basin, and {S3.2b} than it.
S3.2.uniform: The catchment above is {S3.2a} times the size of the local basin, with much the same climate.
S3.2.headwater: No other basin drains into this one: its rivers rise within it.
S3.2.local: The catchment above is {S3.2a} times the size of the local basin, in a somewhat different climate from it.
S3.2.coastal: The basin meets the sea at its outlet, so little water arrives from upstream.
S3.2.coastal_large: The basin meets the sea at its outlet.
S3.2.endorheic:
S3.2.undetermined:
S3.2b.wetter: wetter
S3.1.on: {name} is on the {river}.
S3.1.named: {name} is about {d} km from the {river}.
S3.1.unnamed_on: {name} is on a river.
S3.1.unnamed: A river runs about {d} km from {name}.
S3.3.named: A much larger river, the {river}, runs about {d} km away.
S3.3.unnamed: A much larger river runs about {d} km away.
S3.3.same: That river is much larger than any river within the basin.
S3.3.same.named: The {river} is much larger than any river within the basin.
S3.5.sea: to the sea about {km} km beyond its outlet
S3.5.sea_zero: directly to the sea
S3.5.inland: to an inland sink about {km} km beyond its outlet
S3.5.closed: nowhere: it is a closed basin, an inland sink

Land cover. `{value}`: the share, as a whole-number percentage.

S5.1a.some: about {value} of the basin is cropland
S5.1a.none: no cropland is recorded
S5.1b.some: {value} is pasture
S5.1b.none: no pasture is recorded

Surroundings. The flow lines say how many of the basins that meet here drain into this basin, and how many this basin drains into (directly or through another basin). `{n}`: that number, as a word up to ten. Wording for this section is WO-06's.

S6.2.in_none: None of them drains into it.
S6.2.in_one: One of them drains into it.
S6.2.in_some: {n} of them drain into it.
S6.2.out_one: It drains into one of them.
S6.2.out_some: Its water flows on through {n} of them.
S6.2.out_none: It drains into none of them.

## Comparisons with the basins around

How a basin is said to compare with the basins that share a border with it. `{n}`: the basins that meet here, counting this one. `{m}`: the neighbours with a value. `{k}`: how many of them the basin is more or less than. `{cmp}`: a word from the `cmp` lines below. `{list}`: phrases joined by commas and "and". Numbers up to ten are words. A tie is never turned into a rank.

S2.3.extreme: Of the {n} basins that meet here, it {cmp}.
S2.3.count: Its basin is {cmp} than {k} of the {m} basins around it.
S2.3.count.precip: Its basin receives {cmp} precipitation than {k} of the {m} basins around it.
S2.3.allbutone: Its basin is {cmp} than all but one of the {m} basins around it.
S2.3.allbutone.precip: Its basin receives {cmp} precipitation than all but one of the {m} basins around it.
S5.2.extreme: Among the {n} basins that meet here, it has {cmp}.
S5.2.count: Its basin has {cmp} than {k} of the {m} basins around it.
S5.2.allbutone: Its basin has {cmp} than all but one of the {m} basins around it.
S6.3.all: The basins across its divides are all {cmp}.
S6.3.all.precip: The basins across its divides all receive {cmp} precipitation.
S6.3.allbutone: All but one of the basins across its divides are {cmp}.
S6.3.allbutone.precip: All but one of the basins across its divides receive {cmp} precipitation.
S6.5: Of the {n} basins that meet here, it has {list}.

Words for each measure. `top` and `bottom`: the basin is the highest or lowest of the set. `more` and `less`: it is more or less than most of its neighbours (S2.3, S5.2), or, in S6.3, what its neighbours all are.

cmp.precip.top: receives the most precipitation
cmp.precip.bottom: receives the least precipitation
cmp.precip.more: more
cmp.precip.less: less
cmp.temp.top: is the warmest
cmp.temp.bottom: is the coolest
cmp.temp.more: warmer
cmp.temp.less: cooler
cmp.aridity.top: is the most humid
cmp.aridity.bottom: is the most arid
cmp.aridity.more: more humid
cmp.aridity.less: more arid
cmp.elev.top: the highest mean elevation
cmp.elev.bottom: the lowest mean elevation
cmp.elev.more: higher
cmp.elev.less: lower
cmp.cropland.top: the most cropland
cmp.cropland.bottom: the least cropland
cmp.cropland.more: more cropland
cmp.cropland.less: less cropland
cmp.pasture.top: the most pasture
cmp.pasture.bottom: the least pasture
cmp.pasture.more: more pasture
cmp.pasture.less: less pasture
cmp.relief.top: the most relief
cmp.relief.bottom: the least relief
cmp.slope.top: the steepest slopes
cmp.slope.bottom: the gentlest slopes
cmp.forest.top: the most forest
cmp.forest.bottom: the least forest
cmp.karst.top: the most karst
cmp.karst.bottom: the least karst
cmp.sand.top: the most sand
cmp.sand.bottom: the least sand
cmp.silt.top: the most silt
cmp.silt.bottom: the least silt
cmp.clay.top: the most clay
cmp.clay.bottom: the least clay
cmp.runoff.top: the most runoff
cmp.runoff.bottom: the least runoff
cmp.permafrost.top: the most permafrost
cmp.permafrost.bottom: the least permafrost
cmp.gwdepth.top: the deepest water table
cmp.gwdepth.bottom: the shallowest water table

Coast.

S7.2: Its basin touches the sea.

About these figures. `{parts}`: the statements below, joined by full stops. `{n}`: the number of measures. `{list}`: their readable names (WO-05), not internal field names.

S8.2: {parts}.
label.upstream: {label} (upstream)
S8.2.zero: {n} measures are zero here and so have no percentile: {list}
S8.2.other: {n} have no value: {list}

Reasons a measure has no value (inserted in the list of the line above, in brackets).

status.outside_active_domain: zero here, so no percentile
status.no_data: no data in the source
status.low_coverage: low coverage
status.not_areal: not defined for an area

A point inside no basin.

nobasin.text: No basin contains this point (structured response `no_basin`; nearest basin: see WO-03 Q6). Every basin-keyed unit is empty.
nobasin.frame: {S1.1b} {S1.3} {S9.1}
