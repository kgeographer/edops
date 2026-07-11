# Single-basin neighborhood — statement of purpose & outline

**Phase:** Areas · **Sub-phase:** engine · **Date:** 2026-06-26
**Status:** guiding document. WOs are cut *from* this; this is not itself a WO.
**For:** Opus (design), Karl (review/judgment), CC (implementation).

---

## Purpose

Single-basin is the degenerate areal query: the containing basin at a point resolves to a one-unit weighted set, `{hybas_id: 1.0}`, and everything downstream of the resolver runs unchanged. It is cheap to wire — the only new code is a resolver — but it earns its place for three reasons that have nothing to do with cost.

**It is the first meaningful-boundary neighborhood.** The engine was built entirely on the buffer, which we demoted to the analyst drawer because an arbitrary boundary can clip an extreme edge unit. Single-basin's boundary follows a watershed — it can't clip — so this is the first time the engine produces a *headline-eligible* result, the first step onto the dashboard path. The contract already reserves `neighborhood.type = basin`; this fills in a slot it anticipated.

**It is the only neighborhood with a deployed oracle.** The v0.3 `get_signature()` endpoint already computes the signature of the containing basin at a point. So the new v0.4 engine, run as single-basin at the same point, can be checked against an independent, already-trusted result. Every other neighborhood (buffer, ring, polity) is validated only against frozen TSVs we produced ourselves. This is a free correctness check we should take while it's free.

**It is the clean case under the resolve/serve principle.** At n=1 there is no distribution to characterize, so none of the machinery we just spent days on fires — spread is zero, the coherence descriptor is trivially `concentrated`, and there is no modality gate to misfire (retired). Single-basin validates the rest of the pipeline without re-opening any of that.

---

## What this gets us (three distinct aims, three success criteria)

**A. Correctness oracle — substance.** Where v0.3 and v0.4 compute the *same quantity for the same basin*, they should agree. Disagreement is a bug in one engine, or a documented intentional change (the contract's blessed deviations, the scoring envelope, the trust layer). *Success:* every shared quantity either matches, or its difference is traced to a known, intended generation change. The spine of the comparison is exactly this sort — separating **expected generation differences** (v0.4 says more, or says it in the new envelope) from **unexpected disagreements** (the two engines disagree on a value they both claim to compute).

**B. Graceful degradation at n=1 — engine behavior.** The buffer fixture exercised n=9; nothing has run at n=1. Branches carrying distribution logic must degrade cleanly: B1 spread → 0, B6 → no false regime, weighted quantiles → the single value, B2/B5 selection → the one basin, `class_mixture` → 100% one class, `coherence` → `concentrated`. *Success:* no divide-by-zero, no nonsense verdict, no mislabel; the lean payload reads as an honest one-basin description.

**C. Generation diff — forward-looking.** What does v0.4 carry that v0.3 couldn't (trust layer, derived synthetics `outlet_type`/`coast_fraction`, scoring envelope, parameterized Band T)? This documents the delta for the cleanest possible case — exactly what's wanted the day the dashboard replaces v0.3 with v0.4. *Success:* a clear inventory of v0.4-only content for single-basin.

---

## Controls & open questions to settle *before* comparing

1. **Same-basin precondition.** The comparison is only clean if both engines resolve to the *identical* `hybas_id` at the same point and level. Confirm this first; pin to the sandbox `/signature` coordinates (16.7742, −3.0079) so v0.4 is compared against the actual deployed result. (Same discipline as WO12's coordinate control — a mismatch confounds everything.)
2. **What does v0.3 actually emit** — which bands, what structure, and **does it produce Band T at all?** This determines how much of the comparison is oracle (the A–E overlap) versus generation-diff (likely all of Band T, if v0.3 predates it). CC confirms before the comparison is scoped.
3. **Band T is *not* an n=1 case.** Band T aggregates HYDE/LMR grid cells over the basin geometry, not over the single basin as a unit — so it's a genuine multi-cell aggregation. The n=1 degeneracy story (aim B) is **bands A–E only**; Band T behaves as it does for any area.
4. **Shortfall semantics for single-basin.** For a buffer, shortfall is the fraction of the query area with no basin beneath it. For single-basin the query *is* the basin, so shortfall is structurally 0 (or NA). Decide and document which.
5. **Expectation-setting on lean vs detail.** At n=1 the A–E spatial detail is degenerate (p10 = p90 = value; mixture = 100% one class; envelope min = max). So `&detail` adds little over lean for A–E — the real lean/detail contrast here lives in Band T. This step does **not** meaningfully exercise the lean/full split for A–E; that validation belongs to ring and polity. Don't oversell it.

---

## Outline of the work (→ likely WOs)

1. **Resolver + same-basin confirmation.** Single-basin resolver (`point → {hybas_id: 1.0}`, area, `neighborhood.type=basin`); confirm it resolves to the same `hybas_id` as v0.3 at the fixture point/level. Settle shortfall semantics here. *(Gate: same basin confirmed before proceeding.)*
2. **Run v0.4 single-basin** at the fixture (lean and `&detail`), capture payload.
3. **Characterize v0.3's output** (bands, structure, Band T presence) so the comparison's oracle-vs-diff partition is known.
4. **Comparison** (investigatory notebook, cell by cell): join v0.3 and v0.4 on shared quantities; classify each as *match*, *expected generation difference* (with the reason), or *unexpected disagreement* (a bug to chase). Separately, the n=1 degeneracy checks (aim B) as assertions.
5. **Findings + write-up:** the oracle result, the degeneracy result, the v0.4-only inventory.

Each step is a sign-off gate; CC implements, Karl reviews writes, results round-trip to Opus where the oracle-vs-diff classification or a degeneracy surprise needs judgment.

---

## What this is *not*

- Not the lean/full split validation (that's ring/polity).
- Not closing any per-level item (orthogonal; L8 is its own axis).
- Single fixture (Timbuktu). A clean oracle here is "the engines agree at Timbuktu," not a general proof.

---

## Why now, in one line

It opens the dashboard path with the one neighborhood that comes with its own answer key, tests the engine at the low end of the cardinality axis (bracketing WO12's high-n L8 run), and does both in the case where none of the hard summarization questions apply — so it's the cheapest honest forward step available.
