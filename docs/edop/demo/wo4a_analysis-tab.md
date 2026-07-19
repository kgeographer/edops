# WO4a — Analysis tab: inventory + demo assessment (read-only; no build)

**Phase:** DEMO · Track 2 (demand-driven exposure)
**Kind:** Probe. No changes. Findings → `docs/edop/demo/wo4a_findings.md`.

Track 2's discipline: **expose only what a demo or slide uses.** This probe is not "what can we
keep" — it is "what does Braga need, and does any of this carry it." A component that survives
only because it exists does not survive.

## Part 1 — Inventory (what is actually there)

For the Analysis α tab in `sandbox.html` (v1 Lookup) — for each of **water provenance**,
**s/u divergence**, and the **scale-mismatch alert**:

- What does it compute, from what inputs, via which route or engine path?
- What does it display, and in what form?
- Is the underlying computation still live in the engine, or has it drifted since Phase 1?
- What would porting it to `sandbox_v3.html` actually cost — is it engine-backed (cheap) or
  does it carry v1-only client logic (expensive)?
- Does it work at **L08**, or was it built L06-only? (Post-WO3 this matters: the scale-mismatch
  alert in particular is meaningless if it can't see both levels.)
- Does it work on **polities**, or points only?

## Part 2 — Demo assessment (does it carry a Braga claim)

Three specific questions; answer each on the evidence, not on the code's ambition.

1. **Scale-mismatch alert.** WO3 established that L06 and L08 give different true answers
   (Tbilisi: biome flips, aridity −30 pp, while `dist_sink` and upstream stats hold). Does this
   alert *fire on Tbilisi*? If it does, it is the second half of the scale story — the instrument
   reporting its own scale-sensitivity rather than leaving the user to discover it. Report what
   it actually flags and on what criterion.

2. **Water provenance / s/u divergence — the allochthonous case.** Divergence is a **tail**
   phenomenon (median divergence ≈ 0 across all pairs; the signal is at the extremes —
   allochthonous water arrival, orographic transition). So the question is not "does the panel
   work" but **"which places does it light up?"**
   Run it on: **Timbuktu** (canonical fixture; Niger), **Cairo / lower Nile**, **Baghdad or lower
   Mesopotamia**, and one orographic case (**Lima**, or a Central Asian oasis). Report the s/u
   divergence and what the panel says for each.
   The claim we would make at Braga: *a place's environmental character can be governed by
   processes far outside it — the polygon does not contain the explanation.* Does the instrument
   support that claim, on these places, today?

3. **What would a global ranking give us?** The WO1a mechanic run on **s/u divergence** would
   *hand* us the allochthonous places rather than guessing at four. Is the divergence value
   precomputed per basin (i.e. is such a ranking a cheap query), or would it need a build?
   **Report feasibility only — do not run it.**

## Part 3 — Recommendation

Three verdicts, each with a reason: **port / demo-from-v1 / drop.** Note that v1 `sandbox.html`
is public, all-green, and untouched — demoing a component *from v1 alongside v3* is a legitimate
option and costs nothing, exactly as the correspondence workbench decision (2026-07-10) went.

## Out of scope

Any change to `sandbox.html`, `explorer.html`, or `sandbox_v3.html`. This is a probe.
