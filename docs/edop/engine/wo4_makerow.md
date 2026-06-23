# CC work order — Engine assembly WO4: make_row, validated on Band T

**Date:** 2026-06-22 (revised — four envelope pins placed per CC's pre-build review)
**Branch:** new branch off WO3 (`engine04` or your naming)
**Pace:** one keystone build, one safe rewire, one confirmation. Stop for review.

---

## Why this is first among the contract work

The response contract is approved. Its keystone is `make_row` — the one row-builder every branch emits through. This WO stands it up and proves it on the **already-functional** Band T path, before any procedural branch is lifted. The point is to separate two risks that WO5+ would otherwise tangle: *is `make_row` contract-faithful* (this WO) vs *was a procedural branch lifted correctly* (later). B7 is the right proving ground because its code is already functions, its `_row` is the closest existing thing to `make_row`, and it's the path that drove the envelope's hardest decisions (`n_units`/`unit_type`, null scores, the caveats).

**Settled contract deltas since the draft you have** — build to these:
- Single `&detail` switch; `&dists` dropped.
- Collisions 1 and 2 confirmed: global `n_units` + `unit_type` (retire `n_basins`); one `coverage` meaning with `shortfall` separate at top level.
- Synthetics (`outlet_type`, `coast_fraction`) will be **catalog-resident derived variables**, provenance in the catalog `notes` column. Small confirmed catalog step before B4 — **not** this WO.
- Temporal step-size handling (three regimes) logged for the area/route work — **not** this WO.

**Standing rule:** one-directional extraction; notebooks stay frozen.

---

## Envelope pins (the four design decisions — build to these exactly)

These were open holes in the contract; they are now closed so `make_row` is built to a fixed target rather than guessed at mid-implementation.

### Pin 1 — `status` is a refactor, not a pass-through

The existing `status` is overloaded: each branch wrote its own verdict into it (B1: `concentrated`/`spread`/`outside_active_domain`; B3: `mixed`/`concentrated`/`no_data`; B5: `untyped`). The contract splits that. `status` becomes **execution outcome only**:

`status` ∈ `ok` | `outside_active_domain` | `no_data`

Everything else translates out, per this table — the shaper applies it, it does not pass old values through:

| Old `status` value | New home |
|---|---|
| `concentrated` / `spread` (continuous, B1) | `coherence` flag |
| `concentrated` / `mixed` (categorical, B3) | `coherence` flag (same "is the headline a fair summary" signal; categorical values `concentrated` \| `mixed`, continuous values `concentrated` \| `spread`) |
| `untyped` (B5) | not a status — it's the routing fact `method = distribution_only` |
| `outside_active_domain` | stays in `status` |
| `no_data` | stays in `status` |

`make_row` must **accept** a `coherence` field (B7 won't populate it — null on Band T rows). The exact categorical `coherence` value set is confirmed at B3 extraction; for WO4 it only needs to exist as a nullable field.

### Pin 2 — caveat mechanism, concrete shape

Row carries a list of keys (empty list, never null, so consumers can always iterate); the text lives once at top level, keyed, containing only keys some row referenced:

- Row: `"caveat": ["lmr_caveat"]`  (or `[]`)
- Top level: `"caveats": {"lmr_caveat": "<text>", "hyde_caveat": "<text>"}`

The Band T path exercises both keys (`lmr_caveat` on every LMR row, `hyde_caveat` on the 1950 epoch row), so WO4 is a real test of this mechanism, not just a stub.

### Pin 3 — two collapses are orthogonal (clarifying; no behavior change)

The ECC diagnostic governs **spatial** collapse (whether a query resolves a grid's cells or treats them as sub-resolution — the LMR-at-Timbuktu case). The locked no-within-span rule governs **temporal** aggregation (never averaging across the requested span). They are independent: an LMR query can collapse spatially at each step while preserving every step. Don't conflate them while reading step3b — the cell collapse it already does is spatial and stays; nothing in WO4 changes either.

### Pin 4 — `modality` values, and the two kinds of null score

Drop `suppressed` as a modality value. `modality` ∈ `unimodal` | `two_regime` (the honest verdict; null on Band T, where B6 doesn't apply). What was "suppressed" is the *score*, not the modality — convey it with a separate boolean:

- `score_suppressed: true` → `representative_score` is null **because** B6 found `two_regime` and a single score would lie.
- `score_suppressed: false` with `representative_score: null` → score is **not applicable** (Band T has no temporal score).

This disambiguates the two reasons a score is null. For B7 rows: `modality` null, `score_suppressed` false, `representative_score` null, `representative_raw` populated.

---

## Before you start

Read the response contract (§4 lean envelope, §5 collisions, §6 single `&detail`) alongside the four pins above. Source: B7's `_row`, `_agg_hyde`, `_agg_lmr`, `aggregate_band_t` in step3b, and the step3b output TSVs (regression target).

## Scope

### 1. Confirm the basin-path envelope fields (confirmatory)

Read the inline B1–B6 envelope dicts in step3 and confirm: the exact field names, and that the old `status` values are exactly the set named in Pin 1's table (flag any value not covered there). `make_row` must hold these fields even though B7 won't populate them. Report the list.

### 2. Build `make_row` (the keystone)

One `make_row` emitting the unified lean envelope for any branch:

- identity: `variable`, `band`, `method`, `unit_type` (`basin` | `hyde_cell` | `lmr_cell` | `global`)
- headline: `representative_score` (0–100 or null), `representative_raw` (native or null), `score_suppressed` (bool, Pin 4)
- `n_units`, `coverage`, `status` (Pin 1 value set)
- quality flags (always present in lean): `coherence` (Pin 1), `modality` (Pin 4), `distribution`, `weight_at_zero`, `caveat` (Pin 2 list form)

`make_row` builds the **complete** row (lean fields + a `detail` sub-block holding method-specific distribution/mixture/regime/dominant-envelope fields, each unit/space-tagged). **Lean-vs-`&detail` is a projection at serialization, not a branch of `make_row`** — `make_row` returns the complete object; a separate small projector filters to lean or full, and a separate top-level assembler emits `caveats` (Pin 2). Propose the `make_row` signature, the projector, and the assembler split; flag for Karl.

### 3. Re-wire B7 to `make_row`

Point `_agg_hyde` / `_agg_lmr` / `aggregate_band_t` at `make_row`; retire `_row`. No behavior change — same values, new envelope.

## Acceptance

Run the Band T path through `make_row` on the Timbuktu fixture and regress with `diff_output` against the step3b TSVs at **full detail** — same rows, same values, envelope now carrying `n_units`/`unit_type`/`coverage`/`status`/flags per contract, and the caveat mechanism (Pin 2) emitting `lmr_caveat`/`hyde_caveat` correctly. Then show the **lean** projection of the same payload so Karl sees both forms of a real row.

## Out of scope (explicit)

- B1–B6 extraction — WO5+, against this `make_row`.
- the synthetics catalog edit — separate confirmed step before B4.
- the temporal step-size parameter, area/polygon route, bulk endpoint — logged for later.

## On completion

Report the §1 field confirmation, the `make_row` / projector / assembler signatures, the B7 regression (full + lean shown, caveat mechanism exercised), and your proposed extraction order for B1–B6. Update the tracker (contract approved + four pins; WO4 done; `make_row` is the conformance target). Stop for Karl's review.
