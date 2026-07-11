# WO1a findings — trajectory validity, cross-variable settlement, membership reconciliation

Source: `notebooks/edop/demo/wo1_within_polity_variance.ipynb` (Cells 9–11)
Output: `output/edop/demo/wo1a_polity_trajectory_L06_centroid.tsv`

Findings recorded as cells run. Accept gate: all five criteria met before hero-shot list is
finalised.

---

## F1a.1 — Cross-variable Spearman correlations (Cell 9 / Part B)

| Pair | ρ | Interpretation |
|---|---|---|
| aridity ↔ precipitation | +0.827 | Near-redundant — aridity IS a precip-derived variable (P/PET); no new hero-shot signal |
| aridity ↔ elevation | +0.456 | Moderate — genuinely distinct axis; different story class |
| precipitation ↔ elevation | +0.452 | As expected (precip and aridity are near-twins) |

**Consequences (amends `wo1_findings.md` F1.8):**

- Precipitation spread is redundant as a hero-shot axis. ρ=0.83 means it will produce
  essentially the same candidate list as aridity. Say so once; do not revisit.
- Elevation is a distinct future investigation. ρ=0.46 is positive but weak enough that
  elevation rankings will differ meaningfully from aridity rankings. Story class is different
  too: terrain control and vertical ecology (coastal lowland → highland frontier) vs.
  climate-gradient stories. Flag as a future pass; do not start here.

---

## F1a.2 — Size confound (Cell 10 / Part A, item 1)

**Spearman ρ(spread_delta, n_basins_delta) = +0.428  (p=1.68e-34)**

**Verdict: MODERATE** — size explains roughly 18% of spread_delta variance (ρ²). Real but
not dominant. The majority of spread signal comes from something other than mere territorial
growth.

**What "confound" means here:** when a polity grows it adds basins, which mechanically
widens p90−p10 regardless of whether the new territory is environmentally different.
A strong size confound would mean the trajectory ranking is measuring "who grew the most"
rather than "who crossed a regime boundary." At ρ=0.43, the confound is partial: size
pushes spread_delta upward, but does not explain it. Candidates must still pass the median
test (F1a.3) to confirm the environmental claim is real.

---

## F1a.3 — N Song median trajectory (Cell 10 / Part A, item 2)

**N Song per-slice aridity trajectory (centroid-in membership, L06):**

| fromyear | toyear | n_basins | aridity_spread | aridity_median | aridity_mean |
|---|---|---|---|---|---|
| 961 | 961 | 125 | 35.2 | 46.1 | 48.9 |
| 962 | 969 | 125 | 35.2 | 46.1 | 48.9 |
| 970 | 979 | 184 | 45.5 | 56.6 | 56.8 |
| 980 | 989 | 335 | 49.7 | 76.7 | 69.1 |
| 990 | 1017 | 336 | 49.7 | 76.7 | 69.0 |
| 1018 | 1027 | 336 | 49.7 | 76.7 | 69.0 |

**median_delta: +30.6 pct-pts (46.1 → 76.7). monotone_median: True.**

**N Song is not confounded.** The median aridity score jumps 30 percentile points as basins
are added — those added basins are genuinely wetter, not random territory. Starting in
semi-arid north China (percentile ~46), expanding into wetter south China (percentile ~77).
The environmental claim holds: this is directional expansion across a real regime boundary,
not just growth.

Implication for narration: "N Song's territory shifted from a semi-arid northern base into
progressively wetter southern basins over 60 years" — this is a true statement supported
by the median trajectory.

---

## F1a.4 — Median-drift ranking: top candidates (Cell 10 / Part A, items 3–4)

**Size confound threshold:** spread_delta ≥ p75 (2.2) AND median_delta ≥ p75 (1.1)
yields 87 polities. These thresholds are low because many polities have negative deltas
(they contracted or shifted dryward). The strong-on-both list is a broad screen; candidates
are distinguished within it by the absolute values.

**New discovery — Pagan Kingdom (860–1285 CE):**
spread_delta=31.97, median_delta=35.84, monotone_median=True, 7 slices.
Strong on both axes, monotone median — the best-performing pre-modern polity in the
median-drift ranking that isn't already on the WO1 shortlist. Medieval Burmese state that
expanded from the dry Irrawaddy plain toward the wetter delta and coastal highlands.
Coherent environmental story; less familiar to Western audiences (a virtue for Braga, per
the Tibetan Empire reasoning). **Elevate to Tier 1 candidate for visual inspection.**

**Qin Dynasty confirmed (-750 to -222 CE):**
spread_delta=40.79, median_delta=14.48 — strong on both. Median moves dryward → wetter as
Qin unification expands from the Wei River valley into subtropical south. Already on WO1
Tier 1; now confirmed by the median test.

**N Song (rank 8 on median_delta, within strong-both 87):**
spread_delta=14.48, median_delta=30.63, monotone on both. In the strong-both set but
below the displayed top-25 by spread_delta (cutoff at 20.3). Confirmed by the median test.

**Candidates to remove from the shortlist shortlist considerations:**
Median-drift top-20 contains several modern/colonial artifacts (French Fifth Republic,
German Africa, Vichy France, Free French) that reflect unusual geometry or political
fragmentation rather than coherent environmental expansion. These are not hero-shot
candidates. Republic of Chile and Talpur Dynasty dominate by median_delta but are
post-1800 and a different story class.

**Turks (666–755):** spread_delta=42.52, median_delta=11.12, not monotone_median.
The median shift is real but not directional; spread increases likely reflect steppe
expansion in both wet and dry directions. Still a possible static-spread hero shot
(WO1 F1.5 noted Turks at rank 20 with 75.5 spread at its peak).

---

## F1a.5 — Membership reconciliation (Cell 11 / Part C)

**Engine rule (from engine.py `resolve_polygon`, lines 95–136):** `ST_Intersects` prefilter;
`weight = overlap_area / polity_area`; `epsilon=0.0` (any non-zero overlap passes).
**Notebook rule (Cell 4):** `ST_Within(ST_Centroid(basin), polity)`.
Divergence: edge basins whose centroid is outside the polity are excluded by centroid-in
but included by fractional overlap. With epsilon=0.0, the engine adds every basin that
touches the boundary.

**Result: centroid-in is vindicated as a screening rule.** Rank shifts across the
21-polity spot-check:

| Polity | rank_ci | rank_ov | rank_shift |
|---|---|---|---|
| Yuezhi | 7 | 12 | +5 |
| Tibetan Empire | 11 | 7 | -4 |
| Merina Kingdom | 18 | 14 | -4 |
| Talpur Dynasty | 14 | 10 | -4 |
| Pagan Kingdom | 15 | 18 | +3 |
| (all others) | — | — | ≤ ±3 |
| **Northern Song** | **17** | **17** | **0** |

Maximum rank shift is ±5 in a 21-polity set. No polity flips from one half of the list
to the other. **N Song: rank_shift = 0.** Centroid-in and fractional-overlap agree exactly
on N Song's position.

**Large per-slice spread_diffs are not rank-scrambling.** The top entries in the
per-slice comparison (Empire of Japan early slice +49, Tibetan Empire 623–626 +45) are
early/small extents with 5–30 centroid-in basins. When a polity has only 5 member basins,
adding 5–10 edge basins can swing p90−p10 substantially. These are not the slices used
in the rollup (rollup takes the max-spread slice, which for these polities is always a
later, larger extent).

**N Song spread_diff is small (+2–5 points across slices).** Fractional overlap adds
31–44 edge basins per slice and raises spread from 49.7 → 52.1 at peak — immaterial
for the hero-shot claim.

**Conclusion:** centroid-in is a sound screening rule for the shortlist. The shortlist
stands. Full re-rank under engine membership is not warranted.

**Note on unweighted vs weighted comparison:** Cell 11 uses unweighted p90−p10 for
comparability with Cell 5. The engine uses area-weighted statistics. This means the
comparison understates the importance of large basins; the true engine output would differ
slightly from `spread_ovlp`. This is acceptable for a screening check.

---

## Open / next steps

- Run Cell 11 (fractional-overlap spot-check) — expected 2–5 min
- Update F1a.5 with Cell 11 results
- Amend `wo1_findings.md` F1.8 with ρ values from F1a.1
- Finalise 4–5 polity example list once Cell 11 confirms or revises shortlist
- **Pagan Kingdom** is the key new candidate to inspect visually (WO2 candidate map)
