# Sandbox Overview

The Sandbox is the main signature lookup tool: choose a place or a historical polity on the left, then
read its environmental signature across six of the seven tabs on the right.

## Choosing a place: Settlements vs. Polities

The left panel has two forks, plus a shared **Reset** button that clears everything back to a
cold start.

**Settlements** resolves a place by name (optionally `"Name, Country"`) or `lat,lon` coordinates
via the World Historical Gazetteer, or loads one of five worked examples (Timbuktu, Kaifeng,
Tbilisi, Santa Fe, San Francisco, each with a preset date range). 

__Note:__ _you must zoom to the vicinity of the place you are seeking, in order to constrain results_. Once a place is resolved you can accept or 
change defaults for:

- **Scope** — *Single basin* (default; containing basin only), *Buffer* (all basins
  within a radius you set, default 100 km, aggregated into one summary), or *Basin ring* (the
  containing basin's immediate neighbors — **not** aggregated; Get signature loads the center
  basin, and each ring member on the map is individually clickable to load its own signature for
  comparison). With a buffer, the Signature tab summarizes the whole set of basins; Analysis,
  Seasonality, Context and Similarity always describe the containing basin. Basin ring is different in kind,
  not just degree — it's a per-neighbor comparison tool, not an aggregation scope.
- **Level** — L06 (16,397 basins globally) or L08 (190,675 basins) — a coarser vs. finer
  BasinATLAS resolution.
- **Signature bands** — A (Physiographic), B (Hydroclimatic), C (Bioclimatic), D (Anthropocene),
  E (Coastality), and T (Temporal — LMR/HYDE/eVolv2k enrichment). Checking T reveals a
  from-year/to-year range to set the aggregation window for those temporal layers.

**Polities:** Either search the Seshat project's 
[Cliopatria polities](https://github.com/Seshat-Global-History-Databank/cliopatria) by name, 
or load one of eight worked examples (Northern
Song, Inca Empire, Pagan Kingdom, Mali Empire, Kingdom of Poland, Abbasid Caliphate, Tibetan
Empire, Qin — the last flagged "no LMR" since it predates the LMR record, which begins at 0 CE).
Selecting a polity reveals a time-slice slider with VCR-style transport controls
(first/previous/play/next) for stepping through the polity's historical boundary changes. Band T
is pre-checked, and its time window is the selected slice's own years, so there is no separate
date range to set. **Get signature** resolves the signature for the current slice.
Level and Bands otherwise work the same as Settlements.

For both forks, the **Get signature** button always fires the query for the current parameters.

## The seven tabs

### Map

Shows the basin boundaries for the current scope. Selecting a variable from the
dropdown list paints basins by that variable: every basin worldwide at L06, and at L08 only the
basins in the current scope (plus the neighbours of a single basin).

### Signature

Lists every requested variable, organized into accordions by band.

### Analysis

Auto-generated interpretation, not raw values: a basin-context table (upstream
catchment area, distance to ocean outlet, drainage type), a local–upstream divergence table
comparing "local" (s) against "upstream" (u) values for key variables, and a water-provenance
classification — *Endorheic*, *Coastal terminal*, *Exogenous water supply*, *Catchment-uniform*,
*Local-dominant*, or *Undetermined* (the last when the upstream catchment is too small at the
current level to resolve distant sources — switching to L06 usually resolves it).

### Seasonality

Plots monthly precipitation and temperature as a climate diagram (precipitation bars with a
temperature line) and a radial (polar) chart, with an auto-generated prose summary of the precip/temp phase relationship
(e.g. Mediterranean-type anti-phase vs. monsoon-type co-incidence) and a stats table of derived
seasonality variables (precip concentration, peak month, precip–temp phase offset).

### Context

Answers "how typical is this basin?" — a table of global percentiles for seven key
variables, computed two ways: against all basins worldwide, and against just the basins within a
chosen radius (250/500/1000/2500 km, default 500) of this one — plus a map painting each
basin in that radius with its own value of a chosen variable. The two percentile columns can diverge sharply: a
basin can be unremarkable globally but an outlier regionally, or vice versa.

### Similarity

Paints every basin that satisfies *all* the tolerance conditions of a chosen
regime lens — a non-compensatory conjunction, not a distance ranking. Four lenses are available:
Precipitation regime, Temperature regime, Climate (precip + temp combined), and Terrain regime.
Each lens exposes a subset of tolerance dials relevant to it (e.g. precipitation shape/annual
total/amplitude for the precip lens; elevation/relief range for terrain), each a tight/default/broad
three-way choice — there's no single strict/moderate/loose ladder across the whole panel, each
dial is independently query-relative.

### Atlas

The one tab that isn't about the currently-selected place — it's a standing world
map of precipitation regime classification, viewable by Modality (Arid, Even year-round, One wet
season, Two wet seasons, Undetermined) or Phase (which season the wet period falls in, e.g.
"Mediterranean" = one wet season with cool-season rain).


