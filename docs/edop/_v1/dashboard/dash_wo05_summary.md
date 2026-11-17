# dash WO-05 summary: GEDA in Band T, sources line, long-span measurements

2026-11-16. Spec `dash_wo05_GEDA_long-span-caution.md`; record `dash_wo05_results.md`. Branch `dashboard`. Nothing deployed.

- **Item 1, GEDA block.** The Signature tab's Band T shows GEDA after LMR: own histogram and slider, mean line with p10 to p90 band, observed years (1990 to 2020) shaded and tagged, caveats from the payload, notes for low coverage and clipped spans. The slider year now shows under the histogram and as a marker on the line chart (LMR and GEDA).
- **Item 2, sources line.** "Available for this query: …" at the top of Band T, with a sentence for low coverage, HYDE's nearest step and each not-applied reason. Every state is tested with a real place.
- **Item 3, measurements only.** Payload grows about 3.5 KB per year; a single basin stays near 1 to 3 s up to 1,000 years; a polity climbs from 2.8 s (100 years) to 66 s (1,000). HYDE's table gets one column per year after 1950. No caution built: a time-series design comes first.
- **Item 5.** The polity example dropdown stays usable after a search.
- **Also:** pressing Get signature shows the Signature tab (automatic runs stay on the map); a late map preview no longer pulls the reader back.
- **Item 4, out-of-date results (2026-11-17).** Settled as one rule instead of keep-and-dim: any change of place, scope, radius or level disables the six result tabs and returns to the Map; bands and timespan leave them alone (stale results stay viewable until the button is pressed; left open for the UX review). The only gap was level change (scope and radius already reset); it now resets on Settlements and Polities. The button reads "Get new signature" when enabled with earlier results for the same place or polity. Dashboard folder 104 passed.
- **Open:** a time-series UX design; polity cost with span; HYDE table width; placeholder wording; Band T headline value.

**Gate.** Karl checks in a browser: Lviv, Band T 1300–1400 (GEDA beside LMR, the sources line); Santa Fe, same span (GEDA not applied, outside footprint); Lviv 1960–2010 (observed shading, year text, marker); pressing Get signature after a level change lands on Signature.
