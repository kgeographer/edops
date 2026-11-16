# dash WO-04 summary: arrival on the map, Get signature, small fixes

2026-11-16. Spec `dash_wo04_misc-fixes.md`; record `dash_wo04_results.md`. Branch `dashboard`. Nothing deployed.

- **Item 1, arrival on the map.** Every way of choosing a place (splash or Dashboard example, a WHG lookup, a chosen polity) lands on the Map tab, zoomed to the basin, with the query run and the tabs filling behind it. The old Map, Signature, Profile sequence came from the run handlers switching tabs; they no longer do. A link that names Profile or Signature selects it once, early, with a loading line. Map is the first tab; polities have no Profile tab; a spinner shows on the Signature tab during a run.
- **Item 2, Get signature.** Enabled only when the controls differ from the last successful run, and disabled while running. After an automatic run it is disabled; a changed parameter enables it; a failed run leaves it enabled. Settlements and polities alike. The control-by-control table is in the results.
- **Item 3.** "Load an example" stays visible and usable after a place is resolved.
- **Item 4.** `/api/profile` takes optional `lat` and `lon` and returns a sample profile only for the place it describes (within 10 km); the page passes the point and no longer checks itself. A later store uses the same two parameters for point statements.
- **Item 5.** One setting feeds the version pill on the splash and every header ("v1.0 alpha"); the query log documents `src=link`; the signature version stays 0.5.
- **Tests:** 76 dashboard tests passed (about 3.5 minutes).
- **Open:** Context and Similarity still follow the level control at once; scope and radius changes still clear results; the polity search locks its example dropdown; prose still saying v0.4 (About modal, Computing Place tile).

**Gate.** Karl checks in a browser: Tbilisi on the splash lands on the map with the tabs filling; Get signature does not re-run the same query; a level change is applied by the button; a confirmed WHG place arrives the same way.
