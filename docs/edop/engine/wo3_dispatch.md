# CC work order — Engine assembly WO3: dispatch_variable

**Date:** 2026-06-22
**Branch:** engine01 is fine
**Pace:** one unit, stop for review. This is the last pre-contract extraction.

---

## Why this is next, and how it differs

Dispatch is the last contract-independent piece and the smallest. It's pure routing: read a variable's `typology_cluster` (and whatever else genuinely tips the decision) and return which branch handles it. No values flow through it, so it can't disturb the matrix or the envelope — the firewall holds exactly as in WO1 and WO2.

But the extraction is a different *kind* from the first two. Per the step0 inventory, this routing **does not exist as a function** — it's implicit in cell-level `meta_df` filters scattered across step3. So WO3 is *consolidating a rule that's currently spread across cells*, not lifting one block of code. The hazard is therefore not a hidden input; it's that the rule may not be perfectly consistent across the cells it's spread through. Pulling it into one function is precisely what would expose any disagreement — and if you find one, **surface it, don't silently pick a side**.

**Standing rule (in memory/tracker, restated):** extraction is one-directional. The step3 notebook is left frozen as the research record; logic moves out into `engine.py`. Duplicates left behind are provenance.

**Locked principle this function must honor:** `typology_cluster` is the governing axis. Edge cases are fixed **at the dispatch point, never by editing the column.** This function is exactly where that principle lives.

## Before you start

Read the step0 inventory and the step3 cells where the `meta_df` filters select variables into each block. Reconstruct the routing rule from those filters.

## Scope — one function

Consolidate the scattered routing into one importable function in `engine.py`. Inventory's suggested shape, to finalize against the actual filters:

`dispatch_variable(typology_cluster, zero_fraction, kind) -> block_label`

It routes each variable to its **primary** aggregation branch:

- B1 — coherence / concentrated-vs-spread (continental-gradient and scale-dependent continuous vars; zero-inflated vars take the hurdle variant)
- B2 — dominant-basin (network-topology: the discharge vars)
- B3 — categorical class-mixture
- B4 — flag / structural (outlet_type, coast_fraction)
- B5 — untyped continuous fallback (distribution-only) and the local-anomaly extreme (river_area)
- B7 — Band T gridded (HYDE / LMR / eVolv2k), routed by band membership

**B6 (modality) is not a dispatch target** — it's a refinement applied after B1/B5 to distribution-bearing continuous results, so `dispatch_variable` should not route to it.

Two things to determine from the code and **flag for Karl**, rather than assume: (a) whether `zero_fraction` actually changes the *routing* decision or is only consumed downstream in scoring — if the latter, drop it from the signature the way WO2 dropped `level`; (b) the final signature.

## Architecture note (observation, not a mandate)

Routing depends only on a variable's catalog properties, not on the query — so dispatch belongs to the **build-once layer**, alongside the `load_catalog` concern WO2 surfaced, not the per-query path. You may compute it per-variable or precompute it into the catalog at build time; either is fine for WO3. Flagging only because it reinforces the startup-vs-per-query seam the engine will eventually name explicitly.

## Acceptance — coverage, not a float diff

Dispatch produces routing labels, not data, so there's no values TSV to diff. The check is a full-catalog coverage test: run `dispatch_variable` over every variable in the catalog and confirm each routes to the **same branch the notebooks actually sent it to.** Ground truth is recoverable from the frozen step3 result TSVs — each variable's row records the `method`/block that produced it. Pass = every variable's dispatched label matches its recorded block, with no variable unrouted and no variable routed to two branches.

## Out of scope (explicit)

- the seven branches themselves — post-contract.
- anything about the response shape, envelope fields, or `make_row`.
- `dispatch_variable` must **not call** any branch; it returns a label only.

## On completion

Report the coverage result, any cross-cell routing inconsistency the consolidation exposed, the `zero_fraction` determination, and the final signature. Update the tracker (WO3 done; pre-contract extractions complete). Stop for Karl's review.
