# Profile templates: the wording the filled_profile generator uses

This file is the target of the WO-04 to WO-07 work: the wording of the Environmental Profile as the generator (`scripts/edop/whg/wo04_fill.py`) puts it together. The generator reads this file every time it runs. Edit the wording here; the rules (what is true, which number, which branch) stay in the script.

**How to edit.** Each line is `key: text`. A `{slot}` is replaced by the generator: `{name}` is the place name; `{S2.1a}` and the like are units of `modal_dummy_annotated.md` (a filled value, or a visible placeholder when the unit is not built yet). Other slots in the Phrases part (for example `{km}`) are named in the notes beside them. Keep the slots you want to show; remove one and the value is dropped. A slot the generator does not supply stops the run with the key and the slot named.

**Every change is recorded.** Whoever edits this file (Karl, Opus or Claude Code) raises `Version:` by one and adds a line to Changes: `- vN | date | who | what and why`. The generator will not run if the newest line in Changes does not match `Version:`. Each generated file states the version, the last commit of this file, and whether it has been edited since.

Version: 1

## Changes

- v1 | 2026-11-05 | CC | Wording moved out of wo04_fill.py into this file. No wording changed: the ten filled_profiles regenerate identically.

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

Slots are unit ids. `{S3.2}`, `{S5.1a}` and `{S5.1b}` are built from the phrases further down.

S1.frame: {name} sits at about {S1.1b} m above sea level, in {S1.1c} country. It lies in the {S1.2a} ecoregion, {S1.2b}. {S1.3} {S1.4}
S2.frame: Rainfall averages about {S2.1a} mm a year, {S2.1b}. Temperatures average {S2.2a} °C, {S2.2bc}. {S2.3}
S3.frame: {name} is {S3.1}. {S3.2} {S3.3} {S3.4} The basin drains {S3.5}.
S4.frame: The land is {S4.1a}, with {S4.1b}. The underlying rock is mostly {S4.2}. {S4.3}
S5.frame: Today {S5.1a} and {S5.1b}; {S5.1c} covers most of the rest. {S5.2}
S6.frame: {name}'s basin is one of {S6.1a} that meet here. {S6.2} {S6.2c} {S6.3} {S6.4} {S6.5}
S7.frame: {S7.1a} {S7.2} {S7.3}
S8.frame: These figures describe the basin of about {S8.1a} km² that contains {name}, from global datasets of about {S8.1b}. {S8.2} {S8.3}
S9.frame: {S9.1} [Ecoregion on Wikipedia: {S9.2}] [Data as JSON: always]

## Phrases

Climate. `{lo_temp}`, `{lo_month}`, `{hi_temp}`, `{hi_month}`: coldest and warmest month of the monthly temperature curve.

S2.2bc: from {lo_temp} °C in {lo_month} to {hi_temp} °C in {hi_month}

Water. S3.2 appears only where the Analysis tab's rule says the water supply is exogenous. `{S3.2a}`: ratio of the catchment above to the local basin. `{S3.2b}`: the comparison word. `{km}`: distance along the river from the basin's outlet to the sea or inland sink.

S3.2: Most of the water passing here falls far upstream: the catchment above is {S3.2a} times the size of the local basin, and {S3.2b} than it.
S3.2b.wetter: wetter
S3.5.sea: to the sea about {km} km downstream along the river from the basin's outlet
S3.5.inland: to an inland sink about {km} km downstream along the river from the basin's outlet
S3.5.closed: nowhere: it is a closed basin, an inland sink

Land cover. `{value}`: the share, as a whole-number percentage.

S5.1a.some: about {value} of the basin is cropland
S5.1a.none: no cropland is recorded
S5.1b.some: {value} of the basin is pasture
S5.1b.none: no pasture is recorded

Surroundings. `{up1}`, `{upN}`, `{dn1}`, `{dnN}`: neighbours that drain into this basin (direct, further away), and that this basin drains into (direct, further away).

S6.2: upstream: {up1} direct, {upN} further; downstream: {dn1} direct, {dnN} further

Coast.

S7.2: Its basin touches the sea.

About these figures. `{parts}`: the statements below, joined by full stops. `{n}`: the number of measures. `{list}`: their names.

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
