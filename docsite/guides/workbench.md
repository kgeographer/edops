# Workbench guide

The Workbench is where EDOP's environmental signatures meet CDOP's cultural/reference datasets —
three tabs test different kinds of environment↔culture correspondence. A map and an environmental
profile panel on the right stay visible across all three; what drives them changes per tab. Results
here are **necessary-not-sufficient evidence, not causal claims** — a correspondence surviving these
tests means it isn't obviously explained by chance, not that environment *caused* the cultural
pattern.

## Societies (D-PLACE)

1,291 ethnographically documented societies from [D-PLACE](https://d-place.org/), coded across 94
anthropological variables (subsistence, settlement, kinship, social organization), mostly at their
"ethnographic present" (focal years 1850–1940). 87% have been spatially joined to an EDOP basin
signature; the remaining 13% (mostly islands and coastal locations) lack one.

Two queries are available, and they're deliberately asymmetric in what their second display mode
offers:

- **Dominant subsistence (EA042)** can be shown either as *Ecoregions by realm* (which OneEarth
  ecoregions the societies choosing each subsistence strategy fall into) or as a **Climate
  envelope** scatter — a confirmatory view, because subsistence strategy has a specific
  theoretical hook worth testing directly.
- **High gods (EA034)** offers *Ecoregions by realm* or an **Environment scan** — exploratory
  rather than confirmatory, because this variable has no single predicted environmental axis to
  test against; the scan surfaces whatever pattern is there rather than confirming one.

That confirmatory/exploratory split is the point: EA042's climate envelope is answering a specific
question, EA034's scan is asking an open one. Read results accordingly.

## Ecoregions (OneEarth)

A drill-down browser through the [OneEarth Bioregions](https://www.oneearth.org/bioregions/)
hierarchy — 14 realms, 53 subrealms, 185 bioregions, 847 ecoregions — via a breadcrumb trail
(Realms → Subrealms → Bioregions → Ecoregions). Selecting an ecoregion shows its boundary on the
map and, where available, a Wikipedia summary alongside a link back to the OneEarth source page.
This tab is mostly a reference browser rather than a correspondence test in its own right — it's
what the Societies tab's "Ecoregions by realm" view is drawing its categories from.

## WH Cities

258 World Heritage Cities ([OVPM](https://www.ovpm.org/) member cities), 254 of 258 basin-assigned.
Selecting a city from the dropdown (grouped by UNESCO region) shows its environmental profile and
enables two independent kinds of similarity search:

- **Similar (env)** — a regime-lens conjunction search, same non-compensatory logic as the Sandbox
  Similarity tab: Precipitation regime, Temperature regime, or Terrain regime (three lenses here,
  vs. four on Sandbox — no combined Climate lens for cities). Terrain regime exposes three
  query-relative tolerance dials (elevation, relief, landform position).
- **Similar (semantic)** — text-based similarity over Wikipedia-derived discourse about each city,
  by band: Composite, Environment, History, Culture, or Modern.

Comparing what the two searches surface for the same city — environmentally similar vs.
discursively similar — is itself informative: agreement is a hint worth investigating further,
disagreement is not a failure of either measure.

---

*Draft — grounded directly in `workbench.html` (renamed from `cdop_pilot.html` 2026-08-05) and the
CITYKIN WO4 findings noted in CLAUDE.md, cross-checked against
`docs/design/sitemap_aug2026.txt`. Two things worth flagging: the sitemap describes the Societies
tab's second display mode as simply "Climate envelope" for both queries — the actual UI splits it
into Climate envelope (EA042) vs. Environment scan (EA034), which I've kept distinct here since the
confirmatory/exploratory difference seemed like exactly the kind of thing a Guide should surface,
not smooth over. Also: whether the Ecoregions tab stays on this page at all is still an open
question per your own note — written here as currently shipped, not as a settled inclusion.*
