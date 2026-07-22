# WO4 findings — Four similarity instruments on shared probes

**Notebook:** `notebooks/cdop/wo4_similarity-studies.ipynb`
**Work order:** `docs/cdop/pilot/wo4_similarity-studies.md`
**Branch:** `cdop_pilot`
**Date:** 2026-07-21 (WO4 notebook complete — all six parts + Part 0 run, findings logged)

---

## Background

WO4 tests whether "similarity" is one instrument or four (analogue / analogue net of geography /
matched control set / typological position) on seven probe basins (the WO's six plus Santiago,
added for Southern Hemisphere coverage), plus a Part 0 measuring how often the L06/L08
basin-container mean diverges from actual site elevation. Prerequisite: a D-PLACE schema audit
(`data/dplace/dplace_audit_findings.md`) locked Part 3 to the EA corpus (1,291 societies) only.

---

## Setup — a real bug caught and fixed mid-session

The first pass through Cell 11 used only 4 features `(a1,b1,a2,b2)` with raw, unstandardized
Euclidean distance. Production `climate.precip` (`app/db/seasonality.py` — the WO text's
`app/db/similarity.py` doesn't exist) actually uses **5** features
`(log_pre_mm_syr, a1, b1, a2, b2)`, euclidean distance **on z-scored variables** (not
Mahalanobis — that's `climate.temp`'s metric, over a different feature set entirely).

Symptom that surfaced the bug: George Town's Part 1 top-10 (pre-fix) included two ~17,500 km
"matches" with no coherent geography — an artifact of comparing seasonal *shape* only, with no
magnitude dimension to rule out a wet and a dry climate sharing a similar normalized curve.

Fixed: `log_pre_mm_syr` now computed as `np.log1p(t)` (matching `_compute_derived` exactly);
all distance computations now z-score each of the 5 features against the relevant level's own
corpus mean/std (matching `_build_euclidean_state`) before taking Euclidean distance. All results
below are post-fix.

---

## Part 0 — The undeclared argument: container

### Containment verified directly (not inferred from `hybas_id` structure)

For all 7 probes, `ST_Within`/`ST_Contains` confirm the L08 basin is nested within (or, for
Mombasa, exactly equal to) its L06 parent. Area ratio (L08:L06) varies enormously:

| Probe | L08:L06 area ratio |
|---|---|
| Mombasa | 100% (`ST_Equals` true — no further subdivision exists) |
| Augsburg | 27.7% |
| Timbuktu | 15.4% |
| Santiago | 10.1% |
| Tbilisi | 9.8% |
| George Town | 7.2% |
| Kaifeng | 3.7% |

**Mombasa's L06 and L08 basins are the literal same polygon.** HydroBASINS' hierarchy
terminates early for some basins — not every L06 basin has a further L08 subdivision — and when
it doesn't, the same geometry is registered at both levels under different `hybas_id`s (only the
level segment changes, e.g. `1060008650` → `1080008650`, same trailing basin number). The
"move to L08" fix is therefore not a uniform correction: for a basin like Mombasa's, L08 offers
**zero** improvement, because there is no finer basin to move to.

### Site elevation vs. basin mean elevation, L06 vs L08

`implied_temp_gap_c = (site_elev_m − ele_mt_sav) / 1000 × 6.5` (standard lapse rate) — a proxy
for how far a basin's temperature signature likely misrepresents the actual site, since no free
per-point temperature API exists the way one does for elevation.

| Probe | L06 gap (°C) | L08 gap (°C) |
|---|---|---|
| Tbilisi | −7.90 | −2.56 |
| Santiago | −7.31 | −9.21 |
| Augsburg | −3.06 | −1.64 |
| George Town | −0.76 | −0.65 |
| Mombasa | −0.60 | −0.60 |
| Kaifeng | +0.14 | 0.00 |
| Timbuktu | +0.01 | −0.01 |

Tbilisi's L06 figure (−7.90°C) closely matches the original visual-review finding that kicked off
the whole similarity-approach reconsideration (city ~13.8°C actual vs. basin reporting 5.3°C,
~8.5°C gap) — two independent methods landing in the same neighborhood. Kaifeng and Timbuktu sit
at ~0 as expected (Kaifeng was explicitly chosen as the "container success" probe). Santiago's L08
gap is *larger* than its L06 gap — the one probe where narrowing the basin did not help.

### Part 0B — corpus-wide exposure

**Headline: a substantial share, not a thin tail — at either level.**

| Corpus | Level | median &#124;gap&#124; | p75 | p90 | share >2°C | share >5°C |
|---|---|---|---|---|---|---|
| D-PLACE EA (n=1133) | L06 | 0.68°C | 1.74°C | 3.39°C | 21.0% | 4.8% |
| D-PLACE EA (n=1132 at L06 / 1133 at L08) | L08 | 0.36°C | 1.09°C | 2.48°C | 13.4% | 1.6% |
| WH Cities (n=254) | L06 | 1.00°C | 2.19°C | 3.71°C | 28.7% | 8.3% |
| WH Cities (n=254) | L08 | 0.50°C | 1.38°C | 2.41°C | 14.6% | 2.4% |

L08 systematically roughly halves the median gap and the tail shares in **both** corpora —
a corpus-scale confirmation of what the Tbilisi/Kaifeng probe-level results already suggested.
But even at L08, the better level, **13.4–14.6% of both corpora still show a >2°C implied gap**,
and 1.6–2.4% show a >5°C gap. That answers the Part 0 framing question directly: this is not a
thin alpine tail, it's a real, double-digit-percent share of settlements/societies where a
basin-mean signature is measurably wrong about the site's actual thermal environment, even at
the more accurate level.

**WH Cities is consistently more exposed than D-PLACE EA at both levels** (median 1.00 vs 0.68°C
at L06; >5°C share 8.3% vs 4.8% at L06). This matches the WO's own framing: UNESCO World
Heritage cities skew toward historically monumental, topographically dramatic sites (river
confluences, defensible highland terrain), while D-PLACE's broader ethnographic sample includes
many societies in flatter terrain. The corpus closest to "historically significant settlements"
in the narrowest sense is also the most exposed to the container problem.

Histograms (`output/cdop/wo4_part0_elevation_gap_hist.png`) confirm this visually: the central
peak roughly doubles in height L06→L08 in both corpora (WH Cities ~70→~145; EA ~270→~620) while
the tails visibly thin. WH Cities L06 has a genuine long tail out toward −20°C that D-PLACE EA
doesn't show at either level — a specific outlier city, not just a generically fatter
distribution (candidate for a follow-up look via `corpus.nsmallest(3, 'temp_gap_l06_c')`).

Data note: D-PLACE EA shows n=1132 at L06 vs. n=1133 at L08 — one society's L06 resolution came
back null. Not every basin-linked EA society has a valid L06 gap.

---

## Part 1 — Analogue (top-10, L08, no exclusions)

Six of seven probes are **entirely local** in their top-10. That is a measurement of those
places' spatial structure, not a shortfall — it means the result is largely predictable from the
query's coordinates alone, which is exactly what Part 2 exists to make visible, not evidence that
Part 1 "failed":

| Probe | Farthest match in top-10 |
|---|---|
| George Town | 100 km |
| Mombasa | 152 km |
| Tbilisi | 197 km |
| Augsburg | 298 km |
| Kaifeng | 423 km |
| Timbuktu | 516 km |
| **Santiago** | **13,072 km** (3 of top 9 are Western Australian) |

Santiago's exception is a real, textbook climate-analogue relationship, not noise: Green Head,
Dongara, and Utakarra are all in Western Australia's wheatbelt. Central Chile and southwestern
Australia are two of the five classically recognized global Mediterranean-climate regions
(alongside California, the Mediterranean basin, and South Africa's Cape) — a genuine distant
analogue surfacing without any geography exclusion.

---

## Part 2 — Analogue net of geography (radii 250/1000/2500/5000 km)

| Probe | Best match beyond exclusion | Behavior across radii |
|---|---|---|
| Mombasa | Guitri, Ivory Coast (at n=5000 only) | Changes with radius |
| Augsburg | Bush Gully, New Zealand (from n=1000) | Changes with radius |
| Kaifeng | Mai Aini, Ethiopia (from n=1000) | Changes with radius |
| Timbuktu | Dedhi (from n=5000; intermediate stops closer) | Changes with radius |
| **Tbilisi** | "Stemwinder Mine" (reads as British Columbia) | **Identical at all 4 radii** |
| **George Town** | Barrancabermeja, Colombia | **Identical at all 4 radii** |
| **Santiago** | Green Head, Western Australia | **Identical at all 4 radii** |

**Mombasa → Guitri directly replicates WO2a's own validated finding** (Abidjan, R_dbl=0.246,
also Ivory Coast, right along the same coast) — two independent notebooks and pipeline versions
converging on the same distant analogue.

**Tbilisi and George Town show a pattern distinct from Mombasa/Augsburg/Kaifeng/Timbuktu**: the
single best match beyond exclusion is identical at 250 km all the way out to 5000 km, meaning
*nothing* in that entire 250–5000 km band beats one far-flung basin. Read plainly: these two
probes' climate signatures may be rare enough globally that their only competitive matches are
either immediately local (Part 1) or almost the only other place on Earth like them — nothing
in between. Worth treating as a claim to test further, not yet a settled finding.

---

## Part 3 — Matched control set (EA042 validation case)

Construction only, per the WO's own scope — not the correspondence test itself. EA-only,
locked by the D-PLACE audit (1,133 of 1,291 EA societies have an L08 basin, 87.8%).

### Two data-quality fixes found and applied mid-run

**Family resolution used the wrong field.** First pass matched raw `glottocode` against the
crosswalk and reached only 74.3% (842/1133). CLDF's own field description for
`language_level_glottocodes` says explicitly it "can be used to match societies to languages in
the Glottolog classification trees" — `glottocode` alone can be a dialect-level code that never
appears as a tree leaf. Fixed to try each code in the (space-separated)
`language_level_glottocodes` field first, falling back to `glottocode`: **92.6% (1049/1133)**.

**`EA042` included data-quality codes as if they were subsistence categories.** `"Two or more
sources"` is Murdock's own ambiguous-coding flag, not a real subsistence type; pairing a real
category against it isn't a meaningful cultural contrast. Fixed by applying the same exclusion
list `app/api/routes.py`'s `/societies` route already uses for this exact variable
(`'Missing data', '', 'Missing for at least 1 activity', 'Two or more sources'`).

### Result

997 of 1,133 usable (basin features + valid `EA042` + resolved family). **37 matched pairs**
found at `lens_dist < 0.25` (the locked `climate.precip` "strict" threshold), differing on
`EA042`, different language family, >1000 km apart. Confirmed the fix worked: all three pairs
that had been contaminated by `"Two or more sources"` in the pre-fix run (Pekangekum, Hemat,
Terena) are gone from the corrected list.

**37 is a real, working-mechanism result — not a huge number, but a positive one.** Out of 997
candidates, finding pairs that survive four simultaneous strict filters (environment-close,
subsistence-different, family-different, geography-far) at all confirms the instrument is
functional, not just theoretically sound. Genuine, well-separated examples: Wichí (Argentine
Gran Chaco) vs. Western Mono (California), 8,963 km, Fishing vs. Gathering; Mi'kmaq (Canada) vs.
Walloons (Belgium), 4,976 km, Hunting vs. Intensive agriculture; Délįne (Canada) vs. Nganasan
(Siberia), 4,626 km, Fishing vs. Hunting.

**Known limitation, not fixed — noted for later:** the 37 aren't all independent of each other.
Several share a "b" partner from what's really the same real-world cluster counted more than
once — Patwin and Nomlaki (both Wintun, California) both match Tswana at *identical* `lens_dist`
and `great_circle_km`; Bobo matches four Mandara Mountains groups (Mafa, Kapsiki, Podokwo,
Margi) at nearly identical distances; Nomlaki also separately matches Tsonga, itself close to
Tswana. The construction enforces independence *within* each pair (different family, far apart)
but not *across* the matched set — nothing currently collapses near-duplicate clusters on either
side. Rough eyeball: more like 30–32 genuinely distinct matches once duplicates are collapsed,
not 37. What the construction actually needs to exclude is non-independence, of which
geographic distance is only a proxy: two societies 1,500 km apart in the same language family
are less independent than two 900 km apart in unrelated families. Read that way, the
Bobo/Mandara-Mountains cluster is the proxy leaking — four societies that are one family-level
fact, not four, slipping through because distance alone can't see it. Left as a noted limitation
rather than fixed now; a dedup pass (collapse same-family, geographically-close societies before
counting) — which this reframing points at directly, not a tighter radius — would be the natural
next step if this number needs to be load-bearing later.

---

## Part 4 — Typological position (percentile + modality + bioclimate, L06)

### A correction found and fixed before this section ran

A first pass wrongly concluded no bioclimate label existed on `basin06`/`basin08` and left
`zone_name`/`biome` out. Corrected: the raw code is `tbi_cl_smj` on `basin06`/`basin08`; the
label lookup (`zone_name`, `biome`, `zone_id`, `biome_id`) is exposed by
`v_basin06_persist_rev2`/`v_basin08_persist_rev2` — the same views the signature build already
uses — joinable directly by `hybas_id`. Now included.

### `pre_modality`'s distance-to-boundary does not track actual correctness

This is the headline finding of this part. **Timbuktu shows `bimodal` with the *largest*
margin of any probe** (R_dbl − threshold = +0.279) — but WO2a already established this is a
known artifact: "Timbuktu's high R_dbl is an artifact of a sharp single monsoon peak — Fourier
decomposition places energy at all harmonics when the signal is sharply concentrated." The
most confident-looking bimodal signal in the table is the falsest one. Meanwhile **Mombasa —
validated genuinely bimodal in WO2a — sits at the thinnest margin of any probe** (+0.041).
The confidence measure has these two exactly backwards: high confidence on the artifact, low
confidence on the real thing. This isn't a rare edge case — it's the exact mechanism WO2a
diagnosed, showing up again here. Kaifeng's `unimodal` label is the next-least-confident
(−0.032, essentially on the boundary) — correctly flagged as uncertain this time.

### Bioclimate categories are coarser than the continuous lens — a concrete instance

**Mombasa and George Town land in the identical bucket** — "Extremely hot and moist" /
"Tropical & Subtropical Moist Broadleaf Forests" — despite the continuous lens showing them as
meaningfully different (R_dbl 0.341 bimodal vs. 0.178 unimodal; T_amp 1.87 vs. 0.50°C; annual
total 1101 vs. 2655mm). A concrete, non-hypothetical case of the categorical typology and the
continuous shape lens capturing genuinely different things, not the same information at
different resolution — directly relevant to Part 6's "one instrument or four" question.

One good confirmation: **Timbuktu's biome is "Flooded Grasslands & Savannas," not desert** —
correct, since Timbuktu sits on the Niger's inland delta floodplain, a seasonally-inundated
zone embedded in the Sahel. The basin-average classification caught that real detail correctly.

### Full percentile table

| Probe | pre_mm_syr pctl | T_mean pctl | T_amp pctl | ele_mt_sav pctl | R_dbl pctl | modality (margin) | zone / biome |
|---|---|---|---|---|---|---|---|
| Mombasa | 75.4 | 79.1 | 16.8 | 18.4 | 86.0 | bimodal (+0.041) | Extremely hot and moist / Trop. & Subtrop. Moist Broadleaf Forests |
| Augsburg | 72.5 | 31.4 | 51.2 | 80.5 | 27.1 | unimodal (−0.223) | Cold and mesic / Temperate Broadleaf & Mixed Forests |
| Tbilisi | 63.6 | 30.0 | 58.9 | 92.9 | 40.3 | unimodal (−0.194) | Cold and mesic / Temperate Broadleaf & Mixed Forests |
| Kaifeng | 61.2 | 45.5 | 71.1 | 8.4 | 78.6 | unimodal (−0.032) | Warm temperate and mesic / Temperate Broadleaf & Mixed Forests |
| Timbuktu | 17.0 | 98.1 | 31.8 | 38.7 | 96.5 | bimodal (+0.279) | Extremely hot and xeric / Flooded Grasslands & Savannas |
| George Town | 97.4 | 89.9 | 4.4 | 19.5 | 63.2 | unimodal (−0.122) | Extremely hot and moist / Trop. & Subtrop. Moist Broadleaf Forests |
| Santiago | 45.5 | 37.9 | 34.5 | 93.2 | 75.0 | unimodal (−0.059) | Warm temperate and mesic / Temperate Broadleaf & Mixed Forests |

---

## Part 5 — Local anomaly (percentile within 1000 km vs. global, L06)

### The container problem confirmed a third time, by a completely different method

**Tbilisi and Augsburg both collapse to the bottom few percent of their own region on
temperature**, despite unremarkable global percentiles: Tbilisi drops from the 30.0th
percentile globally to the **2.6th** locally; Augsburg from 31.4th to **3.6th**. Neither basin
is a global temperature outlier, but both are far colder than nearly everything within 1000 km.
This is a different instrument (percentile-within-radius, not elevation-vs-site) than Part 0's
elevation-gap proxy, arriving at the same real fact: both L06 basins extend into much higher,
colder terrain (Caucasus, Alps) than their cities actually occupy, so the basin-average signal
reads as a genuine regional cold outlier. Three independent methods now agree on Tbilisi
specifically — the original visual-review temperature comparison, Part 0's elevation proxy,
and this local-percentile result.

### Timbuktu's local wet anomaly corroborates Part 4's biome finding directly

Timbuktu's precipitation percentile jumps from 17.0 globally (dry) to **47.2 locally** — wetter
than nearly half its regional neighbors, because the true regional neighborhood is the
Sahara/Sahel, drier still. Same underlying fact as Part 4's "Flooded Grasslands & Savannas"
biome label (the Niger inland delta): a local wet anomaly inside an extremely arid surrounding
context, now confirmed by two independent methods in two different parts of the notebook.

### Everything else is a more ordinary regional-context effect

George Town and Kaifeng sit in generally warm/wet regions, so their extreme global percentiles
(97.4, 61.2 on precipitation) pull toward the middle locally (75.2, 52.2) — a real effect, but
not a surprising one. Santiago and Mombasa show modest 10–15 point shifts in the expected
direction. Full table:

| Probe (n_local) | pre_mm_syr global→local | T_mean global→local |
|---|---|---|
| Mombasa (253) | 75.4 → 77.5 | 79.1 → 64.0 |
| Augsburg (280) | 72.5 → 89.3 | 31.4 → **3.6** |
| Tbilisi (344) | 63.6 → 91.9 | 30.0 → **2.6** |
| Kaifeng (343) | 61.2 → 52.2 | 45.5 → 65.0 |
| Timbuktu (415) | 17.0 → **47.2** | 98.1 → 61.9 |
| George Town (121) | 97.4 → 75.2 | 89.9 → 66.1 |
| Santiago (210) | 45.5 → 61.0 | 37.9 → 22.9 |

---

## Part 6 — Do they differ? (Jaccard, Part 1 vs. Part 2 @5000km)

| Probe | Jaccard | Intersection |
|---|---|---|
| Mombasa | 0.00 | 0 |
| Augsburg | 0.00 | 0 |
| Tbilisi | 0.00 | 0 |
| Kaifeng | 0.00 | 0 |
| Timbuktu | 0.00 | 0 |
| George Town | 0.00 | 0 |
| **Santiago** | **0.25** | **4** |

**The six zeros are not new information — they're a mechanical consequence of Part 1's own
results.** Part 1 already showed all-local top-10s (farthest match ≤516 km) for these six
probes; Part 2 at 5000 km by definition only contains basins beyond that radius, so overlap
with an all-local set is impossible by construction. The Jaccard table quantifies what "6 of 7
probes are entirely local" already meant — it doesn't add a new fact about those six.

**Santiago's 0.25 is the one number that could have gone either way, and it's real
convergence.** Four of Santiago's Part 1 matches (Green Head, Dongara, Utakarra, and one
unnamed — all ~13,000 km) were already beyond 5000 km, so they were eligible to reappear in
Part 2's far-exclusion set — and all four do. Part 2, searching the entire rest of the world
beyond 5000 km, rediscovers the exact same Western Australia matches Part 1 found unprompted.
That's meaningful precisely because Santiago is the only probe where the two methods could have
disagreed.

---

## Overall WO4 verdict

**Locality is a measurement, not a judgement.** Six of seven probes return entirely local
top-10s at L08 (≤516 km); Santiago's reach 13,072 km. Both are true statements about those
places, and the contrast between them — not a verdict that the local ones "failed" — is the
finding. A result dominated by nearby basins is what an accurate instrument returns when a
basin's true nearest neighbours are, in fact, local; reporting that faithfully is the tool
working. Locality does mean something narrower and real: a local result is largely predictable
from the query's coordinates alone, so it adds comparatively little *beyond* geography — a
different claim from adding nothing, and one that varies by probe rather than a fixed property
of analogue search.

**Part 6's six zero-Jaccard cells are not independent evidence of anything.** Part 2 is defined
as the complement of Part 1's neighbourhood by construction, so once Part 1 returns an all-local
top-10, disjointness at 5000 km follows mechanically — it cannot be read as two instruments
disagreeing. Santiago's Jaccard of 0.25 is the one cell where the two methods could have
diverged and didn't; it is the only informative result in that table.

**Analogue with and without geography exclusion is one instrument with a parameter, not two.**
Part 1 and Part 2 share output shape (ranked list), feature set, and metric — excluding a radius
around the query is a setting, not a different kind of question. The genuinely distinct
instruments are the ones with different output shapes: ranked analogue (Parts 1–2, unified),
matched set with a balance table (Part 3), and positional statement with no instance list
(Parts 4 and 5 — typological position against the global population, and against the local
region, respectively). Four instruments survives as the conclusion; the membership changes from
the WO's original split (analogue / analogue-excluded / matched-set / typology) to this one
(analogue-with-radius-parameter / matched-set / global-typology / local-typology).

**Practical implication for CDOP**: geography exclusion is a second question a user may ask, not
a precondition for the first one to mean anything. Report the result set's spatial spread (e.g.
distance to the farthest of the top-N) alongside the ranked list so locality is visible rather
than implied, and make an exclusion-radius control available, default off, for the user who
wants the second question answered. The "exclusion radius as a UI slider" idea, flagged in Part
2's own spec as a candidate not designed there, still has empirical support for being built —
the reframe changes why it matters, not whether it's worth building.

**Parts 3, 4, and 5 confirm that output shape, not variable set, is what distinguishes
instruments.** Part 3 showed the matched-control-set instrument (Galton's problem) works but
needs care — a genuinely different question from ranked analogue, answered with a different
output shape (a set with a balance table, not a ranked list). Part 4 showed a categorical
instrument (typological position) can disagree sharply with the continuous lens on the same two
probes (Mombasa/George Town, same bioclimate bucket, different R_dbl and T_amp) and that its own
confidence measure can be actively misleading (Timbuktu's known-artifact bimodal reading looking
more confident than Mombasa's validated real one). Part 5 (local anomaly) independently
triangulated the exact same container-problem probes (Tbilisi, Augsburg) that Part 0 and the
original visual review had already flagged, via a third, unrelated method — and stands as its
own instrument alongside Part 4 once output shape, not reference population, is the criterion:
both produce a positional statement with no instance list, differing only in which population
they're positioned against.

**So: four instruments by output shape — ranked analogue, matched set, global-typological
position, local-typological position. Geography exclusion is a parameter of the first, not a
fifth instrument, and its value answers a second question, not a repair to the first.**

---

## Open items

- "Stemwinder Mine" and "Bush Gully" country/region read from context (HydroBASINS region code
  + plausible name), not yet confirmed against an authoritative gazetteer lookup.
- The Tbilisi/George Town "single distant match dominates the entire 250–5000 km band" pattern
  (Part 2) remains unexplained — a candidate follow-up, now that Part 6 shows Tbilisi and
  George Town are both firmly in the "Part 1/Part 2 disagree completely" camp (Jaccard 0.00).
- Part 3's matched-set count (37) is not dedup'd for near-duplicate clusters on either side of a
  pair — noted limitation, not fixed. See Part 3 section above.
- If a lens definition ever gets a second declared argument (per the WO's closing framing),
  Parts 1/2/3/4/5 here are the empirical basis for what that argument would need to
  distinguish: geography-inclusion (Part 1 vs 2), corpus/dedup semantics (Part 3), categorical
  vs. continuous representation (Part 4), and reference population (Part 5's local vs. global).
- **L06→L08 support change may explain the WO2a/WO4 Mombasa discrepancy — unconfirmed.** WO2a
  found Mombasa's L06 top-5 reaching the Ghana coast, thousands of km out; WO4 Part 1 at L08
  finds nothing beyond 152 km, recovering Guitri (Ivory Coast) only once geography is excluded
  at 5000 km. Same lens, same query, different answer in kind. Candidate mechanism: L08 has
  11.6x more basins than L06, so the query's own neighbourhood supplies far more near-identical
  competitors at finer support, crowding distant analogues out of any fixed top-N. If that
  holds, moving to finer support for the container fix and running a plain top-N analogue search
  work against each other on the same query — confirmable by running Part 1 at both L06 and L08
  for the same probes, not yet done.
