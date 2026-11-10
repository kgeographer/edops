# Profile templates: the wording the filled_profile generator uses

This file is the target of the WO-04 to WO-07 work: the wording of the Environmental Profile as the generator (`scripts/edop/whg/wo04_fill.py`) puts it together. The generator reads this file every time it runs. Edit the wording here; the rules (what is true, which number, which branch) stay in the script.

**How to edit.** Each line is `key: text`. A `{slot}` is replaced by the generator: `{name}` is the place name; `{S2.1a}` and the like are units of `modal_dummy_annotated.md` (a filled value, or a visible placeholder when the unit is not built yet). Other slots in the Phrases part (for example `{km}`) are named in the notes beside them. Keep the slots you want to show; remove one and the value is dropped. A slot the generator does not supply stops the run with the key and the slot named.

**Every change is recorded.** Whoever edits this file (Karl, Opus or Claude Code) raises `Version:` by one and adds a line to Changes: `- vN | date | who | what and why`. The generator will not run if the newest line in Changes does not match `Version:`. Each generated file states the version, the last commit of this file, and whether it has been edited since.

Version: 2

## Changes

- v1 | 2026-11-05 | CC | Wording moved out of wo04_fill.py into this file. No wording changed: the ten filled_profiles regenerate identically.
- v2 | 2026-11-05 | Opus | Framing A (Karl's decision): Setting speaks about the place; the other sections name the basin they describe. S1.2a now means the point's ecoregion. New units S1.2c (the basin's majority ecoregion, when it differs) and S1.5a, S1.5b (the basin's elevation range); wording for the four water classes other than exogenous; a phrase for a basin that meets the sea at its outlet; S8 says which figures are the place's and which the basin's. Needs WO-05 for the new units and phrases before it runs.

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
S3.frame: {name} is {S3.1}. {S3.2} {S3.3} {S3.4} The basin drains {S3.5}.
S4.frame: Across the basin, the land is {S4.1a}, with {S4.1b}. The underlying rock is mostly {S4.2}. {S4.3}
S5.frame: Today {S5.1a} and {S5.1b}; {S5.1c} covers most of the rest. {S5.2}
S6.frame: {name}'s basin is one of {S6.1a} that meet here. {S6.2} {S6.2c} {S6.3} {S6.4} {S6.5}
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
S3.2.local: The catchment above is {S3.2a} times the size of the local basin; most of the water passing here falls locally.
S3.2.coastal: The basin meets the sea at its outlet, so little water arrives from upstream.
S3.2.endorheic:
S3.2b.wetter: wetter
S3.5.sea: to the sea about {km} km downstream of the basin
S3.5.sea_zero: directly to the sea
S3.5.inland: to an inland sink about {km} km downstream of the basin
S3.5.closed: nowhere: it is a closed basin, an inland sink

Land cover. `{value}`: the share, as a whole-number percentage.

S5.1a.some: about {value} of the basin is cropland
S5.1a.none: no cropland is recorded
S5.1b.some: {value} of the basin is pasture
S5.1b.none: no pasture is recorded

Surroundings. `{up1}`, `{upN}`, `{dn1}`, `{dnN}`: neighbours that drain into this basin (direct, further away), and that this basin drains into (direct, further away). Wording for this section is WO-06's.

S6.2: upstream: {up1} direct, {upN} further; downstream: {dn1} direct, {dnN} further

Coast.

S7.2: Its basin touches the sea.

About these figures. `{parts}`: the statements below, joined by full stops. `{n}`: the number of measures. `{list}`: their readable names (WO-05), not internal field names.

S8.2: {parts}.
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
