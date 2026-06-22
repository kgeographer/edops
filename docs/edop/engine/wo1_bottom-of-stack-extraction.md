# CC work order — Engine assembly WO1: bottom-of-stack extraction

**Date:** 2026-06-21
**Branch:** engine01 branch
**Pace:** small first unit, stop for review. Inventory (step0) is done; this is the first construction.

---

## Why this is first

The step0 inventory showed the engine's bottom of the stack — the resolver and shared primitives — is **contract-independent**: it doesn't touch the response envelope, so it can be promoted before the response-shape contract is settled (Opus is drafting that separately for Karl). This work order promotes that foundation and stands up the regression harness every later extraction depends on. It deliberately touches nothing about the envelope, `n_basins`/`n_units`, coverage labels, or the shaper — those wait for the contract.

## Before you start

Read `AREAS_tracker.md`, `deferred_items_register.md`, `areas_findings.md`, and the step0 inventory. The relevant existing code: step1 Cell 3 (buffer-resolver SQL), step2 Cell 3 (the verbatim duplicate of it), step3 Cell 6 (`weighted_quantile`), step3b Cell 11 (`_weighted_quantile`).

Propose where the engine module should live (e.g. an importable `engine.py` the notebooks call into) but **don't commit the location** — flag it for Karl.

---

## Scope — three things

### 1. Promote `resolve_buffer`

Lift the step1 buffer-resolver SQL into one importable function. Suggested signature from the inventory:

`resolve_buffer(lat, lon, radius_km, level, conn, epsilon) -> DataFrame[hybas_id, weight]`

It must reproduce the step1 result exactly. Acceptance fixture — Timbuktu (lat 16.8167, lon −2.9833), r = 100 km, L06:

- 9 basins returned
- weights sum to 1.0000, shortfall 0.0000
- the nine weights match step1: 0.277, 0.174, 0.163, 0.137, 0.106, 0.088, 0.025, 0.018, 0.012 (float tolerance), with the same `hybas_id`s as the step1 output TSV

Keep the locked behavior: weight = fraction of buffer area covered, slivers dropped below epsilon, **open-water shortfall reported, not renormalized**. `hybas_id` always int64. Then **remove the duplicate inline SQL in step2 Cell 3** and have step2 call `resolve_buffer`, so there is a single source of truth.

### 2. Stand up the regression harness

Build the small, reusable diff helper the rest of assembly will use: given an engine output and the matching block TSV(s) in `output/areas`, it reports mismatches in row count, column set, and values (float tolerance). For WO1 the only thing to regress is the resolver against the step1 basin set, but write it generally so attachment and each branch can diff against their TSVs later. This is the safety net for the whole refactor — keep it simple, not a framework.

### 3. Dedupe `weighted_quantile`

`weighted_quantile` (step3) and `_weighted_quantile` (step3b) are identical. Consolidate into one shared utility and import both call sites from it. Confirm via the harness that the B1/B5 and B7-HYDE outputs are unchanged after the swap.

---

## Out of scope (explicit)

- `attach_values` — that's WO2.
- dispatch and the seven branches — post-contract.
- anything about the response shape, the envelope fields, `n_units`/`unit_type`, coverage labels, or the quality flags — Opus is drafting the contract; these foundation pieces don't depend on it and must not pre-empt it.

## On completion

Report the harness results — resolver reproduces the step1 fixture exactly, quantile dedupe leaves outputs unchanged — and your proposed module location. Update the tracker (engine assembly underway; WO1 done) and stop for Karl's review before WO2.
