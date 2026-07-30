# CITYKIN WO1 — WH Cities environmental similarity: migrate to the validated instrument, add a terrain lens

**Status:** draft for review.
**Prior:** `wo6b_findings.md` (raw-curve backbone — the validated distance), `wo6c_findings.md`
(non-compensatory conjunction — *not* imported here; see Why), `wo5_findings.md` Part A (the Tbilisi
false-match: shape compensating for magnitude in Mahalanobis-over-correlated-variables — the exact
defect in the temp lens being retired), `wo8c_findings.md` (point-window terrain module,
`dplace.society_terrain`; the 211m-vs-928m container finding), catalog v0.3, and CC's audit note on
`app/db/seasonality.py` / `LENS_REGISTRY` / `/api/whc-similar-env-lens`.
**Type:** engine migration + one new lens + retirement of superseded code. Notebook validation first,
then wiring. CC authors; Karl reviews every write.

Goal-setting with provisos. CC discovers implementation particulars; Karl reviews every write.

## Context — what CITYKIN is

CITYKIN is the **retrieval head**: a place in, ranked environmentally-similar places out, over the
WH Cities corpus (254 of 258 basin-joined). Anchored query grammar (one origin → ranked neighbors),
distinct from the set-first cohesion grammar of the Societies/TRACE work. Retrieval has no Galton
problem — no cross-cultural inference, no hypothesis, no non-independence to control — so this WO
carries none of that machinery. It carries a *distance* and a *ranking*, nothing more.

---

## Why

The WH Cities "Similar (env)" dropdown already has the right **shape** — per-lens (currently
Precipitation regime, Temperature regime), corpus-relative ranked list, distance shown beside each
result (the magnitude-with-rank honesty rule, already correct on screen). What it has underneath is
the **wrong engine**: pre-WO6 machinery that the sandbox arc superseded and never migrated.

- `climate.precip` runs WO2a's harmonic-scalar feature set (`log_pre`, a1/b1/a2/b2). Better than the
  retired PCA composite (the Jerusalem/Acre-near-Mombasa bug is gone), but it is the *harmonic scalar*
  representation the handoff explicitly retired — "(a1,b1,a2,b2) is more expressive than any scalar
  derived from it… raw-curve correlation superseded all of it." One generation behind.
- `climate.temp` runs Mahalanobis over three correlated variables including `tmp_concentration` — the
  **exact Tbilisi false-match configuration WO5 Part A caught**, admitting matches ~10 °C off by
  letting shape compensate for magnitude. Not "behind"; known-broken, live on the page.

The validated instrument (WO6b raw-curve distance) exists but lives only in sandbox_v3,
feature-flagged, deliberately never migrated ("stays reachable unchanged until the new panel is judged
good"). The panel was judged good. This WO does the migration, retires the old path outright, and adds
the terrain lens the corpus has always wanted.

**One deliberate non-import.** WO6c's non-compensatory *conjunction* (paint-a-set) is a set-query
head — the Societies/TRACE grammar. CITYKIN is retrieval. So this WO takes WO6b's validated
**distance**, under a **ranked-retrieval** head, and does **not** adopt the conjunction. Same distance
core, different head — the standing test-vs-retrieval separation.

---

## Part A — retire the superseded path

Delete, not deprecate-in-place: the WO2a harmonic-precip lens and the Mahalanobis-`tmp_concentration`
temp lens, and the `/api/whc-similar-env-lens` code that serves them, once Part B replaces them. The
"stays reachable until judged good" bridge has served its purpose. One instrument on the page, the
validated one.

Provisos:

- Confirm nothing else in cdop_pilot consumes the retired `LENS_REGISTRY` entries before deleting; if
  something does, migrate it too or flag it.
- The **sandbox_v3 conjunction path is untouched** — it is the set-query instrument and stays. This WO
  retires only the *cdop_pilot WH Cities* superseded lenses.

## Part B — the lens set, on the validated distance

Each lens answers one physical question, on the WO6b-validated machinery. Ranked-retrieval form
(corpus-relative, distance shown), the existing UI shape kept.

**Climate / water lenses:**

- **Precipitation regime** — the twelve-value raw-curve backbone (WO6b), replacing the harmonic
  scalars. "*When* does the rain fall."
- **Temperature regime** — the raw-curve treatment on the temperature annual cycle, replacing the
  broken Mahalanobis lens. "*When* is it warm, and how much does it swing."
- **Aridity / water-balance** — a single water-balance lens (`ari_log`, the drop-to-representative
  choice from WO8b). "*How much* water overall." **Kept separate from precipitation regime on
  purpose** — timing vs amount are different physical questions (WO8 established this); the UI labels
  carry the distinction ("rainfall *timing*" vs "overall *aridity*") rather than collapsing it.

**Terrain lens (new) — Tier-1 of a staged design (see Part C).**

- **Terrain character** — a three-facet lens on the **point-window** terrain module (`society_terrain`
  analogue for cities, sampled at the city coordinate): **elevation level** (absolute height),
  **local ruggedness** (point-window relief range), **landform position** (floor / mid-slope / ridge,
  the `relief_position` scalar). "Is this the same *kind* of terrain."

Provisos:

- **Metric-within-lens is decided by a correlation check on the 254, not assumed.** For the terrain
  lens especially: check whether the three facets are near-independent on the corpus (z-scored
  Euclidean) or correlated (ruggedness↔position plausibly; elevation likely independent →
  drop-to-representative or Mahalanobis on the correlated pair). Same lens discipline as WO8b, applied
  within the lens. Report the correlation matrix; do not let a composite silently double-count.
- **Point-window, not basin-aggregate, for terrain.** WO8c established point-window is materially
  better (211m vs 928m local relief — the container effect). The lens reads the *place*, not the
  polygon. Tbilisi is the reason (Part D).
- **No modern-only / land-use lens.** The old "band D — anthropocene" idea is dead: those variables are
  `modern-only` and cannot be a legitimate environmental-similarity lens (they measure present-day
  human modification, not the physical setting). Not built, named as permanently out.

## Part C — the terrain lens as a staged, single lens (durable design note)

Recorded here so the design persists (it has evaporated across prior sessions — only the `relief_position`
ingredient survived). CC and Karl decide where the durable copy lives (deferred register / design doc);
this WO carries the canonical statement.

**One lens, rising fidelity — the tiers are upgrades to the same lens, not new lenses:**

- **Tier 1 (this WO):** the three point-window facets above (level, ruggedness, position). Ships now.
  Composite-ish done honestly — a multi-facet distance, non-compensatory if the facets are independent
  enough, never a hand-weighted scalar.
- **Tier 2 (deferred, trigger-gated):** **enclosure / containment** — the *relational* terrain facet
  (is this place ringed by higher, steeper ground — circumscription). Requires the spatial-adjacency
  graph (`ST_Touches`, distinct from HydroBASINS drainage topology). This is the genuinely involved
  build; it is a between-basin geometry the point-window cannot see. Named, not built.
- **Tier 3 (horizon):** a **local high-resolution DEM**, if acquired — richer point-window facets
  (viewshed, aspect, hydrological position, navigability). Swaps the terrain *source* under the same
  lens. Named as horizon.

The staging property that makes this safe: all three tiers are the *same lens* at increasing fidelity,
so Tier 2 and Tier 3 are source/facet upgrades, not new lenses or a rewrite. Write the Tier-1 lens as
"terrain character from the best available terrain source, starting with the point-window facets" so
the upgrades slot in.

## Part D — the Tbilisi acceptance fixture

The terrain lens has a torture-test fixture, the way the sandbox used Timbuktu for the neighborhood
problem. **Tbilisi is a high valley** — elevated, but a *floor* within surrounding highlands. So the
correct result is not "5 high-elevation cities" but **"5 high *valley-floor* cities"** — other high
intermontane basins (candidates: Kathmandu, Quito, Mexico City, Bogotá, Sanaa), and it must **exclude**
high *plateaus* and *mountaintops* that share elevation but not landform position.

Acceptance gate for the terrain lens: **choosing Tbilisi returns high-valley-floor cities and correctly
excludes high-flat and high-peak cities that share only elevation.** If it returns high-but-mixed-landform
results, the three facets are not separating and the lens is under-built — a by-eye gate, readable
without a metric, in the spirit of WO7's "cool-wet × unimodal paints the five Mediterranean regions and
little else." It also validates the container choice: point-window reads Tbilisi's valley floor;
basin-aggregate would smear it with the highlands.

---

## Validation order (notebook first, then wire)

1. Recompute the point-window terrain facets for the 254 (the `society_terrain` approach, city
   coordinates). Confirm coverage.
2. Correlation check per lens on the 254 → set each lens's metric (Part B proviso). Report matrices.
3. **Tbilisi fixture (Part D) in the notebook** before any UI wiring — does the terrain lens
   discriminate high-valley from high-flat from high-peak, by eye, on the 254. Accept gate.
4. Only then wire the lenses to the ranked-retrieval UI, retire the old path (Part A).

## Accept gate

Not a statistical verdict (retrieval, no hypothesis). The gate is:

**The WH Cities env-similarity dropdown runs entirely on the WO6b-validated distance; the superseded
harmonic-precip and broken Mahalanobis-temp lenses are gone; the four lenses (precip regime, temp
regime, aridity, terrain) each answer one physical question with its metric set by a reported
correlation check; each result carries its distance (magnitude with rank); and the Tbilisi fixture
passes — high-valley-floor cities returned, high-flat and high-peak excluded.**

Supporting: point-window (not basin-aggregate) terrain confirmed; aridity kept separate from precip
with labels carrying the distinction; the terrain lens written as staged (Tier-1 shipping, Tiers 2–3
named as fidelity upgrades to the same lens); modern-only lens permanently out; sandbox_v3 conjunction
path untouched.

## Out of scope / deferred

- **Enclosure / containment (Tier-2 terrain)** — the basin-ring / `ST_Touches` build. Trigger-gated,
  named in Part C, not built.
- **Local DEM (Tier-3 terrain)** — horizon, named, not built.
- **Non-compensatory conjunction head** — stays in sandbox_v3 as the set-query instrument; CITYKIN is
  ranked retrieval.
- **Additional lenses** (coastality, offshore topology, at-a-distance measures) — Karl's wishlist,
  demand-funded, named, not this WO.
- **The semantic (Wikipedia-text, section-sliced) similarity channel** — a separate capability on the
  same page, unaffected by this WO; not touched here.
- **Any change to the Societies / TRACE surfaces.**
- 