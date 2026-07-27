# WO8d — Environment↔culture correspondence: the high-gods look (EA034, exploratory)

**Status:** draft for review.
**Prior:** `wo8c_findings.md` (drop-to-representative metric; the necessary-not-sufficient floor
lesson; collinearity), `wo8b_findings.md` (raw-curve backbone; family crosswalk usage),
`wo8a_findings.md` (substrate; PCoA ordination), `wo4_findings.md` (L08 join; family crosswalk
92.6%). Conversational origin: the fresh-eyes reframing of high-gods from a confirmatory PERMANOVA
into an **exploratory look** — no predicted result, "is there an environmental thread among these
societies, and is it more than shared ancestry."
**Type:** exploratory notebook, no engine / API / UI. CC authors; Karl runs cell by cell.

Goal-setting with provisos. CC discovers implementation particulars; Karl reviews every write.

## Context — two near-future phases this WO references (CITYKIN, TRACE)

Two upcoming work phases are named in passing below; CC has not seen them yet, so briefly:

- **CITYKIN** — the *retrieval* head: per-place, per-band environmental similarity over a corpus
  (the WH Cities env-similarity remake — a place/basin in, ranked similar places out). Surfaces the
  WO6b/6c lens machinery. **Anchored** query grammar (one origin → ranked neighbors).
- **TRACE** — the *test* head: traces an apparent environment↔culture correspondence down through
  its controls (subsistence, settlement, phylogeny) to what survives. Surfaces the WO8a–8c
  PERMANOVA work. **Group-level** question.

WO8d is neither. It builds only the **shared distance substrate** both heads would sit on (as a
byproduct — see Part A), and its own query grammar is **set-first** (a trait filter in, group
cohesion out), distinct from CITYKIN's anchored grammar. The references below are only to place
WO8d relative to that near-term roadmap, not to build either phase here.

---

## Why

This closes the WO8 arc on high-gods (EA034), but **not** as the confirmatory test the arc's logic
pointed at. Fresh eyes changed the question. The confirmatory frame — "does moralizing high-gods
track environment, net of ancestry, as a defensible generalization" — is the wrong instrument for
where Karl actually is: hunting for *instances* of environment↔culture coupling (the Hopi
rain-ritual pattern as the known exemplar), not making sweeping claims about all societies. For
instance-hunting, a null-first test is over-built; the honest first move is to **look**, against an
honest backdrop, and decide what's worth chasing.

Two corrections to the confirmatory framing, both established in conversation, both load-bearing here:

- **Language family is not only a confound to null out — it is a second finding.** The
  confirmatory test permutes family away and reports only the residual. But three cousins clustering
  with several non-cousins is *two* results in one picture: some transmission (the cousins) *and*
  some convergence (unrelated peoples in the same setting). The exploratory move is to **label**
  ancestry, not erase it — color every society by family so transmission and convergence are read
  directly, per cluster. "Family is the only correlate" becomes a thing you see (a monochrome
  cluster), not a thing the null hides.
- **Spatial dispersion already argues against pure ancestry.** The EA034 "active but not supporting
  morality" set (n=42) is scattered across Subarctic Eurasia, Afrotropics, Indomalaya, the Americas
  — a trait recurring in disparate places is, by construction, *not* one family counted many times.
  The dispersion is the interesting thing, not a problem to control away.

**Scope and honesty of the look.** This is exploratory. It produces leads, not verdicts. The one
reading to refuse is the single-variable-out-of-many hit (with ~15 signature dimensions and n=42,
some variable will look consistent by chance) — so the look asks a **whole-signature, group-cohesion**
question ("are the 42 coherent, on which lenses, more than chance"), never "find a variable where the
42 agree." A null result — the 42 scatter, no thread — is a legitimate and likely outcome, stated as
such.

## The query grammar — set-first, not anchored

Record why this is its own shape and **not** CITYKIN. CITYKIN is *anchored* (a place in, ranked
neighbors out). This is *set-first* (a trait filter in, a property of the resulting set out). The
native question is **cohesion** — does this set hold together environmentally, on which dimensions,
colored by ancestry — not a ranking from an origin. Ranking the 42 is a legitimate *secondary*
drill-down (pick the Hopi as exemplar, rank the other 41 by distance to it) but it requires inventing
an anchor and is not the primary output. Cohesion first; exemplar-ranking second, for exploration.

---

## Part A — substrate and the factored distance core

Extend the WO8-series substrate with **EA034 high-gods** (the four coded classes: Absent / Otiose /
Active-not-supporting-morality / Active-supporting-morality; `dplace.data`/`dplace.codes`). Family
crosswalk already present.

**The distance computation is written as a callable module, not inline notebook code.** WO8d does not
declare or build "the shared distance core" as infrastructure — that would be speculative, built
toward imagined consumers (CITYKIN/TRACE) rather than a real one. But the look *is* the core's first
real consumer, so the distance computation is **factored as a module the notebook calls** (metric,
per-lens option, whole-sample backdrop), so that if it proves reusable a later extraction is a
lift-and-name, not a rewrite. The core emerges factored-out; it is not *named* a core until a second
consumer validates its shape.

Provisos:

- **Metric: drop-to-representative**, carried from WO8b/8c (`ari_log`, `temperature_annual`,
  `tmp_seas_amp`), with the per-lens decomposition available (water / thermal / terrain as separate
  lenses) so cohesion can be asked *per physical question*, not only overall. No new metric
  litigation.
- **Whole-sample backdrop.** The distance module computes over **all ~1,000 basin-joined societies**,
  not just the 42 — because "the 42 are tight" is meaningless without "tighter than a random 42
  would be," and "the 42 crowd into environmental region X" is meaningless without knowing region X's
  global occupancy. The backdrop is what makes "distinctive" and "tight" measurable at all.
- EA034 focus class is "active but not supporting morality" (n=42), per Karl's selection; the module
  should accept any EA034 class (and any trait) so the look generalizes, but the notebook reports the
  42.

## Part B — the whole-sample view (the honest replacement for the PCA-cluster tally)

The cdop_pilot "Basin clusters" panel already asks this query shape (tally the 42 by environmental
type) but on `basin08_pca_clusters` — suspect provenance, unknown loadings, opaque labels. WO8d does
the same query on ground that can be stood on:

- **PCoA over the drop-to-representative distance, all ~1,000 societies as a grey cloud, the 42 lit
  and family-colored.** Continuous, no imposed cluster boundaries (avoids the Mombasa/George Town
  discretization trap — WO4 Part 4). You read directly whether the 42 fall in a tight region or
  scatter, and the family colors say per-knot whether tightness is transmission or convergence.
- **Named axes.** Because the metric is drop-to-representative, "the 42 cluster" arrives with "on
  aridity and thermal seasonality" — the thing the PCA-table labels could never state. Report which
  signature dimensions the ordination's axes load on.

Provisos:

- **This replaces the PCA-cluster view; it does not endorse it.** `basin08_pca_clusters` stays
  quarantined. The query *shape* is similar; the clustering is not reused.
- An optional **hierarchical-clustering labeling layer** over the *same* distance may be added if
  discrete types read more legibly than a scatter (for Karl, or a later stakeholder) — cut at 2–3
  levels, shown stable across cuts (or noted where not), and always as a *caption over* the
  continuous ordination, never the primary claim.

## Part C — group cohesion, per lens, against the backdrop

The core quantitative output, and the one that defuses the "tight but not very" trap by construction.

- For the 42, compute cohesion (within-group dispersion) **overall and per lens** (water / thermal /
  terrain), and compare each to the distribution of cohesion for **random draws of 42** from the
  ~1,000. The comparison is what turns "the 42 are tight" into "the 42 are tighter than X% of random
  42-sets, on the water lens specifically."
- **Report magnitude with rank, always.** A ranking or a cohesion statistic is never shown without
  its absolute scale against the global distance distribution — "most similar / tightest" must carry
  "and here is how tight, versus typical." "Tight but not very" is then a *visible, readable* outcome,
  not a caveat: a group no tighter than random draws simply reads as no-thread.
- **Per-lens divergence is the finding to watch for.** If the 42 are tight on water/seasonality but
  scattered on everything else, that is a specific, chase-able lead — and it directly echoes the Hopi
  rain-ritual prior. If tight on nothing, that is a clean negative.

Provisos:

- **Baseline choice is Karl's, stated up front.** Random draws restricted *within family* (stringent:
  "tighter than random cousins") vs fully random (looser: "tighter than any random 42"). Given the
  spatial dispersion already argues against a family explanation, the looser fully-random baseline is
  the honest first look; the within-family baseline is the stricter confirmatory version. Report which
  was used; optionally both.
- **No null-hypothesis verdict, no floor.** This is a look. The random-draw comparison is descriptive
  context ("how unusual is this set"), not a significance gate. If a lead pans out, the confirmatory
  version (PERMANOVA, family-restricted null, the WO8c floor discipline) is a *separate follow-up WO*,
  not this one.

## Part D — the Hopi check

The look has a built-in sanity anchor: Karl's known instance. Locate the Hopi (or nearest EA
society) in the ordination and in the cohesion result. Is the Hopi in an environment-driven
(family-diverse) knot, or a family knot? Does the lens the 42 are tightest on (if any) match the
rain-ritual intuition (water/seasonality)? This is not validation — it is a coherence check that the
look is measuring something real against a case Karl already understands.

---

## Explicitly out / back-burnered

- **Force-directed graph** — back-burnered (Karl). It preserves topology not distance and *invents*
  apparent clusters even from random data, so it is the view most prone to fake the cohesion the look
  is testing for. If revisited later, only with thresholded edges (below a global-percentile distance,
  so connectivity = real closeness and "not similar" renders as an edgeless scatter) and shown beside
  PCoA as a cross-check. Not in WO8d.
- **CITYKIN / TRACE as such** — not built here. WO8d builds the factored distance module they may
  later share, as a byproduct of the look, and records (above) why the set-first grammar is not
  CITYKIN's anchored grammar.
- **The confirmatory PERMANOVA on EA034** — deliberately not this WO. A lead from the look triggers it
  as a follow-up; a null from the look closes it.
- **Any engine / API / UI, any new derived variable.** Exploratory notebook only.

## Accept gate

Exploratory, so the gate is not a verdict on high-gods. It is: **a legible whole-signature answer to
"are the 42 environmentally coherent, on which lenses, and is any coherence transmission or
convergence" — with magnitude reported alongside rank (so "tight but not very" is visible), the
whole-sample backdrop in place (so "distinctive" is measurable), family coloring in place (so
transmission/convergence is readable), and the Hopi check reported.** A clean negative (the 42
scatter; no thread) passes the gate — it is a real, honest outcome, not a failure. What the gate
refuses is a single-variable-out-of-many hit dressed as a finding, and a ranking shown without its
scale.

## Carried forward

- If the look yields a lead, the follow-up is a **confirmatory WO** (family-restricted PERMANOVA, the
  WO8c necessary-not-sufficient floor) — a different instrument, named so it is not conflated with the
  look.
- If the factored distance module proves reusable across a second consumer, extract it then as the
  named shared core — demand-validated, not pre-declared.
- The set-first cohesion view, if it proves worth a UI, is the honest replacement for the cdop_pilot
  "Basin clusters" panel, and is closer to TRACE's family (group-level environment-culture structure)
  than to CITYKIN's anchored retrieval.