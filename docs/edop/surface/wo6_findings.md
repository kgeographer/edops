# WO6 findings

**WO:** wo6_polity-live  
**Phase:** Surface  
**Branch:** surf_wo6

---

## F6.1 — Live polity call matches fixture; serialization is clean

`GET /api/areas?type=polity&polity=Northern+Song&year=1000&bands=ABCDET&from_year=1000&to_year=1100&detail=true`
returns 372 rows (52 A–E + 320 T), variable list in order, method and band per variable —
all matching `03_polity_nsong_detail.json`. `TestPolityFixtureEquivalence` (5 tests) confirms
structural equivalence. No serialize-transform bug.

The live response adds a `resolver` block and `band_t_span` key absent from the fixture
(the fixture was captured direct from the engine, not via the route). These are metadata
only; the renderer ignores them and the equivalence tests allow for extra top-level keys.

---

## F6.2 — `marginal_exposure` confirmed in live neighborhood block

`neighborhood.marginal_exposure = {lt_50pct: 0.030, lt_20pct: 0.008}` — present in the
live response as in the fixture (per WO6 accept gate, F5.2). Not rendered; logged for a
future display pass.

---

## F6.3 — No render divergence; WO5 widgets hold at polity scale live

The Band T time marginals, sliders, and value marginal histograms render identically from
the live payload as from the fixture. The WO5 renderer makes no assumptions that would
break on a live response vs a static JSON. No render changes needed.
