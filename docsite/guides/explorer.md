# EDOPS Data Explorer guide

The Explorer is a visual exhibit of the full EDOPS variable catalog as a choropleth — pick a
variable on the left, see it painted across all 16,397 (L6) or 190,675 (L8) basins worldwide on
the right. Three tabs offer different ways to look at the same underlying data.

## Choosing a variable

The left panel is a searchable, filterable catalog, not just a picker: a text search box, a
status filter (**All** / **Implemented** / **Planned** — not every cataloged variable has a live
choropleth yet), a variable-typology dropdown (**Continental-gradient**, **Scale-dependent**,
**Network-topology**, **Local-anomaly** — each describing a different kind of spatial structure a
variable tends to show), and an accordion listing every variable grouped by band (A–E, T).

## Shared controls

A control strip above the map applies across tabs, though which controls are visible depends on
what kind of variable is selected:

- **Level** — L6 or L8.
- **Values / LISA** — raw values, or a Local Indicators of Spatial Association classification
  (which basins are part of a statistically significant high/high or low/low cluster, vs. not
  significant).
- **s / u / Δ** — for variables where it applies, local value / upstream-catchment value /
  their difference.
- **Month** — for monthly-resolution variables, which month's value to display.
- **Band T controls** — swap in entirely for temporal-layer variables, since they aggregate
  differently: an LMR period selector (five fixed windows, Early/MCA/Transitional/LIA/Industrial),
  a HYDE view-mode toggle (First epoch / Persistence / Current value) with a 7-epoch selector
  spanning 10,000 BCE–2025 CE, or an eVolv2k year-range picker (491 BCE–1890 CE).

## The three tabs

**Global** shows the world choropleth plus a histogram of the selected variable's distribution
across all basins.

**Regions** is six synchronized regional maps side by side — East Asia, South Asia, SW Asia,
Mediterranean, Mesoamerica, Pacific NW — for comparing the same variable's pattern across
distinct parts of the world at a glance, with a shared color-ramp legend.

**Compare** is a bivariate scatterplot between any two variables, not just a fixed set: four
named preset pairs are one click away (T×P sign reversal, Elevation×Slope plateau,
Elevation×Precipitation orographic, Temperature×Snow cold-arid), or choose any X and Y variable
from the dropdowns directly. Below the scatter, a regional Spearman correlation strip shows the
X–Y relationship's strength broken out by region alongside the global figure — a pair can
correlate globally while behaving quite differently region to region.

---

*Draft — grounded directly in `explorer.html`, cross-checked against
`docs/design/sitemap_aug2026.txt`. One correction from the sitemap: Compare isn't only "4 variable
pairs" — those are presets on top of free X/Y selection, and the "regional filter buttons" are
actually a Spearman-correlation-by-region readout, not a filter. Voice is neutral/technical
throughout; wordsmith freely.*
