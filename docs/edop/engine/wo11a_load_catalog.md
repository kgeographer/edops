# CC work order — WO11a: load_catalog and the derived/sourced fork

**Date:** 2026-06-24 · branch off WO10b · the build-once catalog layer, due before final assembly. Stop for review.

---

## Why now

WO11 referenced `load_catalog` as if it existed; it doesn't — WO2 deferred it. Writing it surfaces a seam the stale `meta_df` hid: the codebook now has two **derived** rows (`outlet_type`, `coast_fraction`, added WO7b) with no DB column, and the engine has never had to distinguish them from **sourced** rows. This WO builds the catalog layer and the fork. It's the precursor to assembly (WO11).

**The fork (already latent in the data):**
- **Sourced** row — has a source column (`basin08_col_s`). Flows the normal path: `attach_values` reads the column, `dispatch_variable` routes it to a branch.
- **Derived** row — no source column, marked derived. Synthesized by its branch (B4), *not* attached or dispatched. Present in the catalog so the payload can key to it and carry its `notes` provenance.

**Decision confirmed (not open):** the derived rows belong in the catalog (contract §3 — the catalog is the truth of the signature); they are not premature. The missing piece was the engine's handling of the derived class, which is this WO.

**Standing rule:** one-directional; notebooks frozen.

## Scope

### 1. `load_catalog`
Write `load_catalog` (build-once, query-independent — the startup layer, per the WO2 seam) that reads the **current codebook** and produces the engine's `meta_df`, marking each row sourced vs derived (by presence of a source column).

### 2. The fork in attach + dispatch
- `attach_values` operates only on sourced rows — skip derived (no column to attach).
- `dispatch_variable` operates only on sourced rows — derived rows are not routed to a branch; they're produced by one.
- Derived rows remain available in `meta_df` so a branch's emitted row can key to its catalog entry and pull `notes` provenance.

### 3. Integrity check (the WO5–10 continuity guard)
Prove `load_catalog`'s **sourced-row** output reproduces the frozen `step2_meta.tsv` exactly — same rows, same columns, same values. The only delta between the stale snapshot and `load_catalog`'s output must be the two derived rows. If that holds, B1–B5 are fed byte-identical inputs and every WO5–10 regression still stands; the difference is contained to the two rows the branches skip. Report the diff.

## Acceptance

- `load_catalog` produces `meta_df`; sourced rows == `step2_meta.tsv` (strict); the two derived rows present and marked.
- `attach_values` and `dispatch_variable` skip derived rows; re-run a couple of branch regressions (e.g. B1, B4) against `load_catalog`'s `meta_df` and confirm unchanged from their WO6/WO8 results.
- `dispatch_variable` over the full catalog routes every sourced var and skips the two derived ones — no derived var misrouted as ordinary.

## Out of scope

- the full assembly wiring — WO11, immediately after this.
- the routes; future resolvers (v0.4).

## On completion

Report the `load_catalog` signature, the sourced-rows == `step2_meta.tsv` diff, and confirmation the derived fork is handled in attach + dispatch. Add a tracker locked decision: **derived catalog rows (no source column) are skipped by attach/dispatch and produced by their synthesizing branch; present in the catalog for keying and provenance.** Stop for review. WO11 (assembly) follows, with `load_catalog` now real.
