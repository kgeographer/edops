# WO1a — Trajectory validity, cross-variable settlement, membership reconciliation

**Phase:** DEMO · Track 1 (hero-shot curation, continued)
**Kind:** Research — addendum to WO1. No surface change; nothing touches `sandbox_v3.html`.
**Branch:** `demo`
**Precondition:** WO1 complete. Per-slice spread tables persisted for aridity, precipitation,
elevation (`output/edop/demo/wo1_polity_spread_{aridity|precip|elev}_L06_centroid.tsv`).

## Why this WO exists

WO1 produced the trajectory instrument (spread-delta + monotone-increasing) and the finding
that N Song's hero-shot value is trajectory-based, not spread-based (F1.7a). Before that
shortlist drives a feature build, three things must be settled — one methodological, one
analytical, one architectural. All three are cheap. None of them is a rebuild.

---

## Part A — The size confound (the methodological one)

**Spread delta is entangled with area growth.** Adding basins widens p90−p10 nearly
mechanically. Every polity on the delta list grew, by construction. So the trajectory ranking
may be measuring *"did this polity get bigger"* rather than *"did it expand across a regime
boundary."*

N Song's claim is **directional** — expansion into *wetter* territory. Rising spread is
consistent with that but does not establish it. The discriminator is **central tendency**: if
the median aridity score of member basins climbs monotonically across the six slices, the
polity moved into a new regime. If the median holds flat while spread widens, it merely grew,
and the gradient reading is an artifact of size.

**Do:**

1. **Per-slice trajectory table.** For every polity slice already joined in WO1, emit
   `n_basins`, `median_score`, `mean_score`, `spread (p90−p10)`. Aridity and elevation.
   (Elevation is the genuinely distinct axis — terrain-control stories, vertical ecology —
   and it is the same query, so it rides along free. Do **not** chase elevation candidates
   in this WO; the aridity list settles first.)

2. **The N Song test.** Does N Song's median aridity score rise monotonically across its six
   slices (961–1018 CE)? Report the actual per-slice numbers.
   **A flat median is a finding, not a failure.** It would mean the hero shot restates as
   "governed increasing environmental heterogeneity" rather than "expanded into wetter land"
   — a different and weaker claim, and one we would rather know now. N Song stays in the demo
   either way (Karl's call, locked). The check governs *narration*, not case selection.
   Do not smooth this over.

3. **Size-confound diagnostic.** Across the ~744 multi-slice polities, Spearman
   `spread_delta` vs `n_basins_delta`. Report ρ. High ρ ⇒ WO1's trajectory ranking is
   substantially a size ranking, and the Tier-1 shortlist is suspect as it stands.

4. **Median-drift ranking.** Rank polities by monotone *signed* drift of median score
   (wetward and dryward are both stories). Compare against WO1's spread-delta Tier 1.
   **Where the two lists disagree is the finding.** Polities strong on *both* are the
   defensible hero shots.

---

## Part B — Cross-variable settlement (the analytical one)

WO1 F1.8 asserts that precipitation rankings "largely replicate" aridity and that elevation
is "more distinct." Rankings for all three variables are persisted, but only aridity was
analyzed — so these are inferences presented as results. Close the gap with the data we
already have; no re-run.

**Do:**

1. Spearman the per-polity spread rankings against each other: aridity↔precipitation,
   aridity↔elevation, precipitation↔elevation. Report ρ.
2. State the consequence plainly: if aridity↔precip ρ is high, precipitation is redundant as
   a hero-shot axis and we say so once and stop revisiting it. If aridity↔elevation ρ is low,
   elevation is a genuinely separate hunt — flag it as a *future* pass, do not start it here.
3. **Amend `wo1_findings.md` F1.8** to carry the numbers instead of the inference. No claim
   rides on "expected."

---

## Part C — Membership reconciliation (the architectural one)

WO1 joined basins to polities by **centroid-in** (`ST_Within(ST_Centroid(basin.geom),
polity.geom)`) — the cheap fallback the WO permitted. But the project settled on
overlap/area-weighted membership: WO15 made areal aggregation fractional-overlap-correct and
explicitly superseded the centroid-in rule. So **the notebook's member-basin sets are built on
a rule the engine no longer uses.** A polity's spread in the notebook is therefore not
guaranteed to match what the sandbox actually paints and aggregates for the same polity and
year.

Centroid-in is legitimate for *screening* — we are hunting candidates, not producing a result.
The risk is only at the handoff: a polity that screens high could look materially different in
the app. That is a demo-table failure mode, and it is cheap to foreclose.

**Do:**

1. **Clarify, do not presume.** Establish from the code what membership rule the engine's
   polity path (`areal_signature_polygon` / `/api/areas?type=polity`) actually applies, and
   what the sandbox choropleth paints. Report it — this WO does not assume the answer.
2. **Spot-check, don't re-rank.** Recompute aridity spread under the engine's membership rule
   for **N Song plus the top ~20 of the trajectory shortlist only**. Compare ranks and spread
   values against the centroid-in figures.
   - Ranks hold ⇒ centroid-in is vindicated as a screening rule. Say so explicitly and move on.
   - Ranks scramble ⇒ the shortlist is rebuilt under engine membership before any polity is
     wired into the sandbox. Better found here than at Braga.
3. Full re-ranking of all 10,607 slices under engine membership is **out of scope** unless the
   spot-check fails.

---

## Deliverables

- New cells appended to `notebooks/edop/demo/wo1_within_polity_variance.ipynb`
  (continue `# Cell N` numbering; do not renumber existing cells)
- `output/edop/demo/wo1a_polity_trajectory_L06.tsv` — per-polity, per-slice `n_basins`,
  `median_score`, `mean_score`, `spread`, plus per-polity deltas; membership rule named in the
  filename or a header comment, not left implicit
- `docs/edop/demo/wo1a_findings.md`
- Amendment to `wo1_findings.md` F1.8 (Part B)
- Register rows (below)
- **Final example set: 4–5 polities**, each with a nominated slice range and a one-line
  historical hook. Criteria, applied explicitly:
  - survives the median-drift check (the environmental claim is real, not a size artifact)
  - survives the membership spot-check (it will look in the app the way it looks in the notebook)
  - contiguous extent — colonial/discontinuous empires and modern nation-states are out
    (WO1 F1.5/F1.7 identify these as a different story class, not noise)
  - recognizable *or* vivid to a spatial-humanities audience
  - **N Song is in regardless of rank** — benchmark case, locked
  Standing nominees to confirm or replace on the evidence: Songhai (Timbuktu tie-in), Qin
  (unification), Tibetan Empire (plateau → Tarim/Ganges), Inca (Atacama → Amazon).
  Empire of Japan is out.

## Accept gate

- N Song per-slice median reported with numbers, whichever way it falls
- Spearman ρ (spread_delta vs n_basins_delta) reported
- Three cross-variable ρ values reported; F1.8 amended to match
- Engine membership rule named from the code; spot-check result reported for N Song + top ~20
- 4–5 polity example list with slice ranges, justified against the criteria above
- Karl reviews before anything is wired into the sandbox

## Deferred items register (met-and-deferred — not predictions)

- **Contiguity / compactness filter for polity spread ranking.** Met in WO1 F1.5: the top of
  the aridity spread ranking is dominated by discontinuous colonial empires whose variance
  comes from disjoint territory, not from straddling a gradient edge. Culled by curation for
  now. Trigger: if the ranking is used programmatically rather than as a curation aid, or if
  the HYDE-variable pass revives the colonial class as its own story.
- **Membership rule — centroid-in exercised for screening.** Annotate the *existing*
  membership-rule row (do not open a new one) with the WO1/WO1a outcome: centroid-in used for
  candidate screening; engine rule is <as found in Part C>; divergence measured on the top ~20.

## Out of scope

Continuous time slider; sandbox example wiring; HYDE/LMR (Band T) spread; L08 re-rank;
candidate maps; full re-rank under engine membership (unless the spot-check fails).
WO1a settles the list. The slider is the next build.
