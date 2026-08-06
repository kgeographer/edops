# EDOPS Sandbox guide

The Sandbox is the main signature lookup tool: choose a place or a historical polity on the left, then
read its environmental signature across six of the seven tabs on the right.

## Choosing a place: Settlements vs. Polities

The left panel has two forks, plus a shared **Reset** button that clears everything back to a
cold start.

**Settlements** resolves a place by name (optionally `"Name, Country"`) or `lat,lon` coordinates
via the World Historical Gazetteer, or loads one of four worked examples (Timbuktu, Kaifeng,
Tbilisi, Santa Fe, San Francisco, each with a preset date range). Once a place is resolved you choose:

- **Neighborhood scope** — *Single basin* (default; containing basin only), *Buffer* (all basins
  within a radius you set, default 100 km, aggregated into one summary), or *Basin ring* (the
  containing basin's immediate neighbors — **not** aggregated; Get signature loads the center
  basin, and each ring member on the map is individually clickable to load its own signature for
  comparison). Buffer changes what "the basin" means for every tab that follows, since it's a
  genuine aggregate across more basins than a single-basin query. Basin ring is different in kind,
  not just degree — it's a per-neighbor comparison tool, not an aggregation scope.
- **Level** — L06 (16,397 basins globally) or L08 (190,675 basins) — a coarser vs. finer
  BasinATLAS resolution.
- **Signature bands** — A (Physiographic), B (Hydroclimatic), C (Bioclimatic), D (Anthropocene),
  E (Coastality), and T (Temporal — LMR/HYDE/eVolv2k enrichment). Checking T reveals a
  from-year/to-year range to set the aggregation window for those temporal layers.

**Polities** searches Seshat polities by name, or loads one of six worked examples (Northern
Song, Abbasid Caliphate, Tibetan Empire, Tang Dynasty, Pagan Kingdom, Qin — the last flagged "no
LMR" since it predates LMR's 1 CE coverage start). Selecting a polity reveals two independent
temporal controls: a time-slice slider with VCR-style transport controls
(first/previous/play/next) for stepping through the polity's historical boundary changes, and —
separately — a Band T from-year/to-year range (T is pre-checked) for the paleoclimate/land-use
aggregation window. The two aren't linked: moving the slider changes which boundary is shown, not
the Band T window, and vice versa. Level and Bands otherwise work the same as Settlements.

Either fork ends the same way: a **Get signature** button that fires the query.

## The seven tabs

**Map** shows the basin boundaries for the current neighborhood scope, and paints them by
whichever variable is selected for coloring, if one is.

**Signature** lists every requested variable, organized into accordions by band.

**Analysis** is auto-generated interpretation, not raw values: a basin-context table (upstream
catchment area, distance to ocean outlet, drainage type), a local–upstream divergence table
comparing "local" (s) against "upstream" (u) values for key variables, and a water-provenance
classification — *Endorheic*, *Coastal terminal*, *Exogenous water supply*, *Catchment-uniform*,
*Local-dominant*, or *Undetermined* (the last when the upstream catchment is too small at the
current level to resolve distant sources — switching to L06 usually resolves it).

**Seasonality** plots monthly precipitation and temperature as both a histogram and a radial
(polar) chart, with an auto-generated prose summary of the precip/temp phase relationship
(e.g. Mediterranean-type anti-phase vs. monsoon-type co-incidence) and a stats table of derived
seasonality variables (precip concentration, peak month, precip–temp phase offset).

**Context** answers "how typical is this basin?" — a table of global percentiles for seven key
variables, computed two ways: against all basins worldwide, and against just the basins within a
chosen radius (250/500/1000/2500 km, default 500) of this one — plus a map painting the mean
value of a chosen variable across that radius. The two percentile columns can diverge sharply: a
basin can be unremarkable globally but an outlier regionally, or vice versa.

**Similarity** paints every basin that satisfies *all* the tolerance conditions of a chosen
regime lens — a non-compensatory conjunction, not a distance ranking. Four lenses are available:
Precipitation regime, Temperature regime, Climate (precip + temp combined), and Terrain regime.
Each lens exposes a subset of tolerance dials relevant to it (e.g. precipitation shape/annual
total/amplitude for the precip lens; elevation/relief range for terrain), each a tight/default/broad
three-way choice — there's no single strict/moderate/loose ladder across the whole panel, each
dial is independently query-relative.

**Atlas** is the one tab that isn't about the currently-selected place — it's a standing world
map of precipitation regime classification, viewable by Modality (Arid, Even year-round, One wet
season, Two wet seasons, Undetermined) or Phase (which season the wet period falls in, e.g.
"Mediterranean" = one wet season with cool-season rain).

---

*Draft — grounded directly in `sandbox_v3.html`, cross-checked against
`docs/design/sitemap_aug2026.txt`. Flagging for review: the water-provenance badge names and the
exact regime-lens tolerance dial set are copied verbatim from the code's current labels/logic and
may be more implementation detail than a first-time reader needs — trim as you see fit. Voice is
neutral/technical throughout; wordsmith freely.*
