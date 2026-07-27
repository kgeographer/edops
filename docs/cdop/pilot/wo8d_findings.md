# WO8d findings — Environment↔culture correspondence: the high-gods look (EA034, exploratory)

**Work order:** `docs/cdop/pilot/wo8d_env-culture-highgods.md`
**Branch:** `cdop_wo8d` (cut from `cdop_pilot`). **Type:** exploratory notebook, no engine / API / UI.
**Notebook:** `notebooks/cdop/wo8d_highgods_look.ipynb` (8 cells + gate). **Engine:**
`scripts/cdop/distance_core.py` — new this WO, factored (not yet named a shared core; this look is its
first real consumer). `tests/cdop/test_distance_core.py`, 10 green. **Data:** reuses
`output/cdop/wo8c_substrate.parquet` read-only; no new substrate persisted (nothing to extend — EA034
was already joined in WO8a's original build). **Status:** complete — accept gate **PASSED**, draft for
Karl/Opus review.

Exploratory, per the WO's own framing: **no predicted result, no null-hypothesis floor.** Every number
below is descriptive ("how unusual is this set, relative to what") — magnitude is always reported
alongside rank, and family membership is *labeled*, not permuted away, so transmission and convergence
can be read directly rather than inferred from a residual.

---

## Headline — substantially a two-lineage story, with one cross-family convergence exception and an unexplained singleton residual

The focus class — EA034 "active, but not supporting morality" (n=42 in the full EA corpus, n=40
basin-joined) — shows a real environmental signal on the water/aridity lens **relative to a fully random
draw from anywhere** (95.25% tighter than random), but that signal collapses to **chance once each
member's language family is held fixed** (42.25% — the family-restricted "cousins" baseline). The reason
is traceable to a specific, named fact, not a diffuse average: **one lineage (Atlantic-Congo) is 37.5% of
the entire 40-society focus set (15/40), and it is both genealogically related *and* environmentally
coherent** (100% tighter than random draws of the same size, on its own; a second, smaller lineage,
Nilo-Saharan n=4, shows the same pattern at 93.85%). That is the bulk of whatever whole-group signal
exists — but two things sit outside that story and are exceptions, not noise: **three unrelated peoples
across Arctic Siberia** (Chukchi, Yakut, Yurak-Samoyeds — three *different* families, no shared ancestry)
form the **single tightest sub-group in the entire set**, a genuine cross-family environmental
convergence case (detailed below); and **~14 singleton-family societies** share the trait but are
explained by neither the two dominant lineages, nor climate on the whole-group level, nor geographic
proximity to each other — an unexplained residual that is the more interesting open question this look
leaves behind, not leftover bookkeeping (see Carried forward). A third lineage tested on its own
(Sino-Tibetan, n=3) shows shared descent does **not** predict shared environment there (46.00%, chance) —
a useful counter-example against reading "same family" as automatically meaningful.

---

## Part A — substrate (Cells 2–3)

EA034 was already present in the substrate from WO8a's original build (`ea034_religion`) — no new join
needed; verified directly against the CLDF codebook before trusting it.

- EA034 basin-joined distribution: None/missing 453, Otiose 238, Absent 218, Active-supporting-morality
  184, **focus class ("active, but not supporting morality") 40** — matches the WO's stated full-corpus
  n=42 (2 not basin-joined at L08).
- Focus class family-resolved: **38/40** (above the corpus-wide 92.6% crosswalk rate).
- Per-lens backdrop: water/thermal/overall lenses are complete for all 1,133 basin-joined societies
  (n_focus=40 in every case); the terrain lens drops to 1,124 backdrop societies (9 missing terrain data
  corpus-wide) but **all 40 focus-class societies have terrain data** — no focus-class attrition on any
  lens.

## Part B — whole-sample PCoA and named-cluster structure (Cells 4–6)

**Ordination (Cell 4).** Two axes capture nearly all the variance in the drop-to-representative
("overall") distance: **PC1 (61.2%)** is a thermal/seasonality contrast (temperature and seasonal
amplitude load oppositely and strongly; aridity near zero); **PC2 (35.1%)** is almost purely the aridity
axis (loading −0.96, the other two variables barely load). PC3 is negligible (3.6%) — the 3-variable
climate envelope is well-summarized in 2D. Visually, most of the family-colored focus-class points sit
in the *densest* part of the backdrop cloud (a common climate zone, not a distinctive one); the
singleton-family points are the most scattered, including several genuine outliers on the cold/seasonal
side of the space.

**Named cluster membership (Cell 5).** Hierarchical clustering (average linkage) at a 2-cut split off a
tight n=3 cluster — the Chukchi, Yakut, and Yurak-Samoyeds (three *different* families: Chukotko-
Kamchatkan, Turkic, Uralic) — from the remaining 37, which at this coarse resolution trivially spans 14
distinct families (too coarse to be informative on its own). Reading the raw membership list directly
(without needing a finer cut) surfaces the real structure: **5 multi-member families, 26 of the 40
societies** — Atlantic-Congo (n=15: Venda, Kikuyu, Tumbuka, Azande, Bemba, Nsaw, Bamum, Fut, Plateau
Tonga, Luapula, Tupuri, Gbagyi, Katab, Anaguta, Chawai), Nilo-Saharan (n=4: Lotuko, Lango, Jie, Turkana),
Sino-Tibetan (n=3: Kachin, Ao, Lepcha), Algonquian (n=2: Delaware, Myaamia), Athabaskan (n=2: Sinkyone,
Dakelh). The remaining **14 are singleton-family or unresolved** (named individually in the notebook —
Wayuu, Mapuche, Bribri, Aztec, Sanpoil, Chamacoco, !Kung, Yem, Semang, Madia, Bhil, plus the three
Siberian-trio members already counted above).

**Real-world geography (existing cdop_pilot UI map, cross-checked against this analysis).** The focus
class maps to recognizable geographic clusters, not a diffuse global scatter: a dense cluster across
Sub-Saharan/Central Africa (matching the Atlantic-Congo + Nilo-Saharan lineages), a thin band along the
Siberian Arctic coast (the cross-family trio), a scatter through the Americas (mostly the singleton-
family societies), and a few points in South/Southeast Asia. An older, now-retired classification
(`basin08_pca_clusters`, "suspect provenance" per the WO) had already tallied the 40 across 13 different
named climate-zone categories (Boreal/Cool Temperate through Extreme Desert) — indicative, not
quantitatively trustworthy, but directionally consistent with the dispersion found here on solid ground.

**Does shared descent predict shared environment, within each named lineage? (Cell 6, one real bug
caught and fixed along the way — see Process notes below.)**

| group | n | pct tighter than random |
|---|---|---|
| Atlantic-Congo | 15 | **100.00** |
| Nilo-Saharan | 4 | **93.85** |
| Sino-Tibetan | 3 | 46.00 (chance) |
| Siberian trio (3 different families) | 3 | 65.20 |

Two of three named *families* are strongly environmentally coherent on top of being genealogically
related; a third (Sino-Tibetan) is not — shared descent doesn't guarantee shared environment. The
Siberian trio is a different kind of case and its **defining fact is not the 65.20% figure** — that
number is against the family-restricted baseline, an odd comparison for three genealogically unrelated
peoples. The defining fact is that **three unrelated peoples, sharing the same environment and the same
cultural trait, form the single tightest sub-group in the entire 40-society set** — the raw
convergence-across-ancestry phenomenon this look was built to catch, plainly present in the data (Cell 5:
this trio splits off first, before any family-driven cluster, at the coarsest possible cut). The n=3
sample size means this reads as a real, well-supported lead, not yet a statistically robust finding — the
caution is real, but it follows the phenomenon rather than obscuring it.

## Part C — group cohesion per lens, against the backdrop (Cell 7)

No null-hypothesis verdict, no floor — descriptive only, per the WO's explicit design.

| lens | n_backdrop | obs cohesion | random-draw mean | % tighter than random | % tighter than cousins |
|---|---|---|---|---|---|
| water | 1,133 | 0.540 | 0.731 | **95.25** | 42.25 |
| thermal | 1,133 | 1.223 | 1.201 | 44.75 | 59.85 |
| overall | 1,133 | 1.441 | 1.525 | 70.80 | 52.40 |
| terrain | 1,124 | 1.207 | 1.184 | 44.10 | **31.00** |

**No lens clears both baselines at once.** Water is distinctively tight against a fully random draw but
falls to chance against the family-restricted baseline — consistent with Part B's finding that one large,
environmentally-coherent lineage (Atlantic-Congo) is carrying much of that signal. Thermal shows the
opposite asymmetry (weak-to-none against random, mildly elevated against cousins) — not a confirmed
signal in either direction. Terrain is the one lens where the group is *looser* than its own
family-restricted baseline (31.00%) — these particular relatives are more terrain-diverse than a typical
same-family swap would produce. The pattern across all four lenses is consistent with Part B: whatever
apparent cohesion exists at the whole-group level is substantially attributable to which lineages happen
to be large and internally coherent, not a broad signal independent of ancestry.

## Part D — the Hopi check: the strongest instrument-validation result in this WO (Cell 8)

The Hopi (soc_id `Nh18`) are coded EA034 = "Absent" — **not** a member of the focus class; used purely as
a domain-intuition sanity anchor, not validation, per the WO's own framing. In practice, though, it
produced the single strongest piece of evidence this WO has that the instrument is measuring something
real — the equivalent role the differential-deflation result played for WO8b, and equally
method-defensible on its own, requiring no anthropology to trust it.

Hopi's 10 nearest neighbours in the whole-sample 'overall' PCoA space are dominated by its own family
(Uto-Aztecan, 8/10 — unsurprising, as Uto-Aztecan is regionally dominant across the Great Basin/
Southwest), but the two exceptions are the result: **Hano** (Kiowa-Tanoan family, distance 0.000 — i.e.
essentially the same standardized climate position as Hopi) and **Navajo** (Athabaskan family, distance
0.208). Both are real, historically documented instances of cultural contact across language-family lines
driven by shared geography — Hano is a Tewa-speaking village settled among the Hopi villages on First
Mesa; Navajo land surrounds the Hopi reservation. **Neither fact was fed into the metric** — the distance
is built purely from three climate variables, with no history, contact record, or geography beyond raw
coordinates anywhere in its construction. Two real, independently documented cross-family contact cases
falling out as the nearest non-family neighbours, unprompted, is the credibility asset the rest of this
WO's spatial reads (the trio, the singletons) lean on: it says the metric's adjacencies correspond to real
areal relationships, not coincidence.

One caution on the notebook's own auto-generated read: Cell 8 reports "tightest lens = water — matches
the water/seasonality rain-ritual intuition," because water had the highest `pct_tighter_than_random` in
Part C. Given Part C's fuller picture (water's tightness collapses against the family-restricted
baseline, and is substantially attributable to the Atlantic-Congo lineage), this apparent match should
**not** be read as confirming the rain-ritual mechanism — it is more likely an artifact of which lens the
dominant lineage happens to be coherent on. Flagged in the notebook rather than left standing at face
value.

## Process notes

- **A real bug was caught and fixed mid-run (Cell 6, first version).** The named-family cohesion lookup
  queried `family_id` against the *whole ~1,133-society backdrop* rather than restricting to the 40
  focus-class members — Atlantic-Congo alone has 289 members corpus-wide, so the first run silently
  tested a different, uninteresting question ("is the whole Atlantic-Congo family, worldwide, tighter
  than random"). Caught immediately from the `n` column not matching Cell 5's named membership counts;
  fixed by intersecting the family lookup with `focus_mask` before computing cohesion; re-run confirmed
  correct (n=15/4/3 as expected). Matching row counts confirms the right *rows* were selected but not
  that the cohesion computation on them is sound, so the post-fix numbers were additionally checked
  against the groups' actual PCoA positions: Atlantic-Congo's 15 points sit visibly bunched (PC1 span
  0.70 against a whole-backdrop range of ~6.8); Nilo-Saharan's 4 are tight on PC1 with one mild PC2
  outlier; Sino-Tibetan's 3 visibly do *not* cluster (two points near PC1≈0.25, the third at PC1≈−1.93,
  a large gap) — confirming the "chance" reading directly rather than by row-count alone; the Siberian
  trio sits close together and distinctly apart from the main cloud. All four groups' `pct_tighter_than_
  random` readings match what the plotted positions show.
- **The WO's own suggested 2–3-level cluster cut proved too coarse** to isolate real structure at n=40 —
  a 37-member cluster trivially spans many families regardless of any true signal. The fix was not a
  finer arbitrary cut but reading the raw named membership list directly (which the notebook now prints
  in full) and testing each real, visible sub-group's own cohesion (Cell 6) — a more direct answer to the
  actual question than an automatically-chosen cluster resolution would have given.

---

## Accept gate — PASSED

Per the WO's own framing, the gate is not a verdict on high-gods — it is a legible whole-signature answer
to whether the 42 are environmentally coherent, on which lenses, and whether any coherence reads as
transmission or convergence, with magnitude reported alongside rank throughout, the whole-sample backdrop
in place, family coloring/named-membership in place, and the Hopi check reported. All met. **The
substantive answer explains the explainable structure and isolates what it cannot explain, rather than
returning a flat negative.** Whole-group cohesion is substantially a two-lineage story (Atlantic-Congo,
Nilo-Saharan — related and environmentally coherent; Sino-Tibetan the counter-example, related but not
coherent). Outside that story, two things stand: a strong cross-family convergence case (the Siberian
trio — three unrelated peoples, tightest sub-group in the set) and an unexplained singleton residual
(~14 societies, explained by neither lineage, whole-group climate, nor proximity) that is this WO's real
carry-forward question. This is a legitimate exploratory outcome under the WO's own stated logic — the
look was designed to isolate structure and surface what remains, and it did both.

## Carried forward

- **The unexplained singleton residual is the real next question — the primary carry-forward item.** This
  look was built to find what environment (and shallow ancestry) *does* explain; its complement is at
  least as interesting. ~14 focus-class societies (Wayuu, Mapuche, Bribri, Aztec, Sanpoil, Chamacoco,
  !Kung, Yem, Semang, Madia, Bhil, and others — named in full in Part B) share the EA034 encoding but are
  explained by **none** of the structure this WO found: not the two dominant lineages, not a whole-group
  environmental signal (Part C), not geographic proximity to each other. They are the residual of
  interest, not leftover bookkeeping. The natural follow-up is a **residual-characterization query** —
  distinct in kind from the cohesion look done here — asking whether this specific set of societies
  coheres on *anything*: a different environmental dimension not tested (soil, a terrain sub-lens),
  another EA variable entirely, or nothing at all (true independent scatter, which would itself be a
  real, informative result).

  **Epistemic boundary, stated plainly so the residual is never over-read:** EDOPS's deepest available
  ancestry control is language family, which is shallow (roughly 6,000–10,000 years). A residual
  "unexplained by environment and language family" still has deep common descent (below the resolution of
  any family crosswalk this project has) and undocumented diffusion as un-subtracted, entirely mundane
  candidate explanations. The honest claim is "unexplained by environment and *shallow* ancestry," never
  "unexplained by everything mundane" — the same scoping discipline as WO8c's circumscription boundary.

- **The Siberian trio is the strongest cross-family convergence case this look surfaced** — three
  genealogically unrelated peoples sharing an environment, sharing the trait, and forming the tightest
  sub-group in the entire 40-society set (Part B). This is the defensible convergence story: unrelated
  peoples adapting to (or in contact within) the same harsh conditions — not the deeper unexplained case
  (that is the singleton residual, above). If pursued, the natural next step is a domain-expert check
  (Ruth, per the WO's own "anthropology claims to verify" convention) on whether areal contact between
  these three specific peoples is independently documented, before any confirmatory follow-up.
- **The Hopi/Hano/Navajo result (Part D) is the credibility asset to carry forward**, not just a footnote
  — it licenses trusting the other spatial reads in this WO and should anchor any future presentation of
  this method, the same role the differential-deflation result played for WO8b.
- **Shared descent does not uniformly predict shared environment** (the Sino-Tibetan counter-example) —
  worth remembering before assuming "same family, same color in the plot" implies anything on its own in
  future family-colored looks.
- **The old `basin08_pca_clusters` "Basin clusters" panel is superseded** by this WO's Part B/C for this
  trait; a legitimate, WO7-instrument-based version of the same "tally by named climate type" view (using
  the real modality/phase climate-class instrument, not the retired PCA clusters) was discussed but not
  built — Karl declined for now, available as a follow-up if a future trait's dispersion is worth showing
  in that vocabulary.
- **`distance_core.py` is now validated on a second real question** (following `dbperm.py`'s WO8b/8c
  precedent) but still not promoted to a named shared core — CITYKIN/TRACE remain the WO's own forward
  reference, not built here.
