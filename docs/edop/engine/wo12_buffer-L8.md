# WO12 — Buffer at L8

**Phase:** Areas · **Sub-phase:** engine (handling more cases) · **Date:** 2026-06-26
**Depends on:** WO11b (`areal_signature` assembled and whole; 51 basin + 321 Band T rows, 8/8 capstone PASS at L06)
**Branch:** suggest `engine-l8` off the WO11b state — CC's call, but keep it off the frozen L6 artifacts.

---

## Why now

First move in the post-assembly trust program. The engine is proven on exactly one fixture, one level (L06), one neighborhood (buffer). Before adding *shapes* we change *support* once, on the fixture we already trust, to get the clean MAUP read: **same area, different support — `level` is the only changed input.** This produces the long-standing observation the deferred register has been holding (per-level verdicts, open since 2026-06-13: do coherence/modality verdicts shift L6→L8?) and exercises the aggregator at the high end of cardinality (~40–80 basins vs L6's 9), bracketing the eventual single-basin n=1 case from the other side.

It is an **observation, not a closure.** See Scope guards.

---

## Goal

Run the Timbuktu 100 km buffer through `areal_signature` at `level=8`, holding every other input identical to the L6 capstone, and characterize what moves L6→L8 — per variable: coherence, modality, status, score, and the dominant/carrier-basin identities — against a set of invariants that must *not* move. Ensure you use the identical coordinates used in the current state - and 1st step is to confirm whether these are the same as those used in current sandbox code (16.7742, -3.0079)

---

## Scope guards (what this WO is NOT)

- **No threshold retuning.** `T=20`, `MODALITY_GAP=0.50`, `MIN_REGIME_WEIGHT=0.20`, `ECC_THRESHOLD=10`, the 0.90 zero-coverage guard — all stay at their current provisional values. We observe flips *at* those thresholds; we do not move them. Retuning is the multi-fixture calibration step (tracker "Later in the phase"), gated on ≥2 fixtures beyond Timbuktu.
- **Does not close the per-level register item.** It feeds it. Any flip seen here is "at Timbuktu, at current thresholds" — fixture-specific, not a general L6/L8 policy. The register notes verdict shifts are fixture-dependent; honor that.
- **No edits to the frozen L6 TSVs** and no change to the L06 capstone fixture.
- **Single fixture.** Timbuktu only.

---

## Part 0 — Verify level-threading (gated)

The engine *takes* a `level` parameter but has only ever been *run* at L06. The single most likely failure mode is an L06-hardcoded spot that never had to flex. Before the run, audit every decision point where `level` should drive a choice and report whether it is parameterized or hardcoded:

- `resolve_buffer` — does it query `public.basin08` (and the right geometry/`geog` source) at L8, or is `basin06` baked in?
- `attach_values` / the SQL builders (`_val_expr`, `rank_expr`, `two_pass_sql`) — does the PERCENT_RANK population rank over `basin08` at L8? Does it read the L8 persistence view (`v_basin08_persist_rev1`)?
- Zero-inflation — does the scorer/guard read the **`_L8`** zero-fraction columns (`zero_fraction_{s,u}_L8`) rather than the `_L6` ones?
- `load_catalog(level, …)` / `_CATALOG_CACHE` — does the L8 catalog load and cache correctly under its own key?

**Gate:** if threading is clean, say so and proceed to Part 1 in the same session. **If any spot is L06-hardcoded, stop and report it with a proposed minimal fix — do not write the fix until Karl signs off.** (Karl reviews all writes before they land.) Keep any fix minimal and parameterizing; resist the urge to refactor.

---

## Part 1 — Run L8

Call `areal_signature` at `level=8` on the Timbuktu fixture. **Critical control:** use the *exact* coordinates, radius, and Band T span the L6 capstone used (the documented Band T fixture coordinates in the test file — the WHG-resolved precise ones, not rounded). WO4b is the cautionary tale: a ~4 km coordinate shift changed the marginal cell set and looked like a bug. Here, coordinates/radius/span are held fixed so that the *only* thing that can move a number is the support change. Request the same bands and the same Band T span (1100–1200 CE) as the capstone, with `include_detail=True` so the dominant/carrier-basin identities and regime breakdowns are available for the comparison.

Capture the full L8 payload to disk. Re-load the frozen L6 capstone payload (or regenerate it at L06 in the same notebook for a guaranteed apples-to-apples object shape).

---

## Part 2 — Compare (investigatory notebook, cell by cell)

This is the learning part — a notebook, run cell by cell, `# Cell N` convention, CLAUDE.md notebook + TSV conventions (`db_utils.read_areas_tsv`, int64 `hybas_id`). Join L6 and L8 on `variable` and surface the deltas.

**Invariants — assert these; a failure is a bug, not a finding:**

| Invariant | Why it must hold |
|---|---|
| **Band T rows identical L6 vs L8** (representative_raw/score, coherence, `distribution`, caveat keys, and the `hyde_cell`/`lmr_cell` counts) | The grid paths aggregate over the *buffer geometry*, not basins. Same buffer → same cell set, regardless of basin level. If Band T moves, `level` is leaking into the grid path. |
| **`shortfall` identical** | Buffer geometry unchanged; L8 sub-basins partition L6 basins, so their union over the buffer is the same land area. Timbuktu inland ⇒ ~0 both. |

**Expected to move — characterize, don't prejudge direction:**

| Watch | What to report |
|---|---|
| `coherence` flips (concentrated ↔ spread ↔ mixed) | The headline MAUP question. Count and list which vars flip and which way. Finer support can resolve *more* spread (units no longer average it out) or *more* concentration (smoother sampling of a gradient) — empirical, no prior. |
| `modality` flips (unimodal ↔ two_regime) | Watch **`temp_yr_upstream`** and **`pct_sand`** specifically — both already flagged known-weak. More basins = more distribution support for the detector; they may resolve differently. |
| `status` flips | Especially any var crossing into `outside_active_domain` (zero guard fires on L8 `weight_at_zero` ≥ 0.90, recomputed with L8 zero-fractions and L8 weights). Report `dist_sink_km` `weight_at_zero`: L6=0.47 → L8=? |
| `representative_score` deltas (B1/B2/B5) | Will move (different rank population + basin set). Summarize: per-var delta, and a rank-order correlation across the 34 B1 vars as a one-number "how much did the picture shift" stat. |
| B2 dominant basin | The dominant `hybas_id` *will* differ (different polygons). The question is whether the **discharge value and the perennial verdict are stable** — the main-stem Niger should still dominate (cumulative discharge), just under a finer id. |
| B5 `river_area` extreme carrier | The Inner Niger Delta split (carrier ≠ B2 discharge dominant) was informative at L6. Does it persist at L8? |

**Secondary (cross-block consistency at the new support):**

- endorheic-fraction (B4) ≈ `dist_sink` `weight_at_zero` (B1) — held to 0.005 at L6 (shortfall≈0). Re-check at L8 as a finer-support stability probe. Per the register, exact agreement is only expected when shortfall≈0, which holds here.

**Sanity:** L8 `n_units` should land roughly 40–80 basins for a 100 km buffer. A count near 9 (level not applied) or in the thousands (wrong table/geometry) flags a resolver bug — surface it.

---

## Deliverables

1. **Part 0 audit note** — level-threading table (clean / hardcoded), in the WO reply or a short scratch `.md`. Any fixes gated on sign-off.
2. **Notebook** — `notebooks/edop/areas/buffer_l8_comparison.ipynb` (or per convention), cell-by-cell, the join + invariant assertions + flip tables.
3. **Comparison TSV** — `output/edop/areas/wo12_l6_l8_comparison.tsv`: one row per variable with `band`, `method`, the L6 and L8 values of {score, coherence, modality, status, n_units}, and boolean flip columns.
4. **Findings** — new `AF.n` entries in `docs/edop/areas/areas_findings.md`: the invariants confirmed (Band T / shortfall level-invariance is itself a finding worth recording), the flip inventory, the dist_sink status read, and the dominant/carrier-basin stability.
5. **Tracker + register updates** — changelog line in `AREAS_tracker.md`; in the register, record the observation against the **"Per-level verdicts (L6 vs L8)"** row — *update, do not close* (note it remains open for multi-fixture consolidation).

---

## Acceptance criteria

- `areal_signature` runs at `level=8` on the Timbuktu fixture without error; `n_units` in the plausible L8 range.
- **Both invariants hold** (Band T identical, shortfall identical) — or, if either doesn't, it is surfaced as a bug and diagnosed, not waved through.
- Comparison TSV produced; coherence / modality / status flips enumerated; score deltas summarized with the rank-order stat.
- Findings written; non-closure of the per-level item explicitly recorded.

---

## Back to Opus

Worth a round-trip after results land, on three things specifically: (1) the **direction** and **pattern** of any coherence flips — whether finer support systematically resolves more spread or more concentration, since that bears on how the eventual L6/L8 policy should read a single-level verdict; (2) whether `temp_yr_upstream` / `pct_sand` modality resolves or persists at finer support, which is partial evidence on the absolute-separation-floor question; (3) any invariant *violation*, immediately — that's a leak, not a MAUP finding, and changes the plan.
