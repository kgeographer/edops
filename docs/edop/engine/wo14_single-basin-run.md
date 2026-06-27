# WO14 — Single-basin run + v0.3 reference comparison

**Phase:** Areas · **Sub-phase:** engine · **Date:** 2026-06-26
**Depends on:** single-basin resolver + same-basin confirmation (done); `v03_timbuktu_signature.json` persisted.
**Branch:** continue the single-basin branch.

---

## Goal

Run the v0.4 engine as single-basin at the now-canonical Timbuktu fixture, lean and `&detail`, and compare against the persisted v0.3 signature. Two questions: **do the engines agree where they compute the same quantity** (the v0.3 reference), and **does the v0.4 aggregator degrade cleanly at n=1** (degeneracy).

---

## Part 1 — Run

Call `areal_signature` single-basin at the fixture, **Band T span matched to v0.3** (its `pdsi_series` is 101 years → 1100–1200 CE; confirm and match), lean and `&detail`. Capture the payload. Confirm `neighborhood.type=basin`, `n_units=1`, and `shortfall` resolves per the single-basin semantics settled in step 1.

---

## Part 2 — The comparison map (investigatory notebook, cell by cell)

Every v0.3 field and every v0.4 row falls into exactly one bucket. The discipline: **bucket 1 must match; bucket 3 absences must each be explained; bucket 4 transformations must verify.** An unexplained absence or a bucket-1 mismatch is a bug; a bucket-2/3/4 difference is a designed generation difference, not a failure.

**Bucket 1 — shared, directly comparable (the reference).** Most A–D continuous and categorical variables. Note the scoring envelope splits how you check:
- **`area_weighted` rows** carry `representative_raw=null` (native-unit means deferred) — only a percentile `representative_score`. So compare **v0.4 `representative_score` against the percentile rank of v0.3's raw value** for this basin. At n=1 the basin's own value's rank *is* what the scorer computes, so this validates the **scorer**, not just the aggregator. (Don't get stuck on the null raw.)
- **`dominant_basin` / `extreme` / `flag_fraction` / `class_mixture` rows** carry `representative_raw` → compare **v0.4 raw against v0.3's value** directly. At n=1 the one basin is trivially the dominant / the extreme / 100% of the mixture, so these validate the **selection/aggregation** branches degrade correctly.

**Bucket 2 — v0.4-only (inventory + degeneracy check).** The trust layer (`coherence`, `modality`, `weight_at_zero`, `caveat`, `coverage`, `status`), `representative_score` itself, and the synthesized `outlet_type` / `coast_fraction`. No v0.3 counterpart to compare; instead assert they're sane at n=1 (Part 3).

**Bucket 3 — v0.3-only (every absence must be explained).** Confirm each v0.3 field absent from v0.4 maps to a *known reason*, not an accidental drop:
- point/profile constructs — `elev_point`, `relief_position`, `profile_summary`, `profile_groups`, `elev_source`/`dataset`/`resolution` — areal engine doesn't carry point geometry. *(Expected.)*
- `river_area_upstream` — deferred in v0.4 (contract §3). *(Expected.)*
- `endorheic`, `coast_flag` — consumed as inputs to the B4 synthetics, no row of their own. *(Expected — see bucket 4.)*
- `ecoregion` — deduped into `eco_id` (contract §3). *(Expected.)*
- anything else absent → **flag it; an unexplained drop is a bug.**

**Bucket 4 — same concept, different representation (verify the transformation).**
- **Band E flags → synthetics:** v0.4 emits `outlet_type` + `coast_fraction` where v0.3 emits raw `endorheic` + `coast_flag`. Check the synthesis: does v0.4's `outlet_type` for this basin match what v0.3's `endorheic`/`coast_flag` values imply? This validates the B4 derivation against its raw inputs.
- **`pnv_majority` + `pnv_shares`** (v0.3) → how v0.4 emits pnv (class_mixture modal label + shares). Confirm the modal class and shares correspond.
- **`up_area`** (v0.3 top-level) → wherever v0.4 carries upstream area, if at all.

Output a comparison TSV: one row per shared/mapped variable with v0.3 value, v0.4 value (raw or score-vs-rank as above), bucket, and verdict (`match` / `explained-difference` / **`MISMATCH`** / **`UNEXPLAINED`**).

---

## Part 3 — n=1 degeneracy assertions (bands A–E)

Assert the aggregator degrades cleanly. Failures here are bugs:
- `coherence = concentrated` on every continuous row (spread = 0).
- `modality` never `two_regime` (unimodal or null) — no false regime is detectable at n=1. (Also confirms the retirement + degeneracy both hold.)
- `score_suppressed` never true.
- `weight_at_zero` ∈ {0, 1} only (the single basin is at zero or it isn't — no fractional value).
- `coverage` = 1.0 where the basin has data, else `status=no_data`.
- `class_mixture` rows = 100% one class; the modal label is that class.

---

## Part 4 — Band T against the v0.3 reference (per dataset — each treated differently)

v0.3 treats the two paleo datasets differently, so each is checked differently:

- **LMR (2°×2°) — single-cell in v0.3** (`grid_cell={16,−2}`, 101 annual values). The basin (3687.8 km²) is far smaller than one 2° cell, so v0.4's ECC should mark it sub-resolution (`distribution='collapsed_subresolution'`) and collapse to that same cell. v0.4 LMR should then **reproduce v0.3 over the full 101-year series**: `pdsi` mean −0.0393 / min −0.3804 / max 0.2768, temp anomaly −0.1246 K, precip anomaly −0.0153 mm/day. (The no-within-span rule keeps all 101 annual values, so mean/min/max are over the same series.) A match validates ECC sub-resolution detection *and* that the collapse picks the right cell.

- **HYDE — already basin-areal in v0.3** (45 cells, `basin_area=3687.8 km²`, 2 epochs). **Correction from the prior summary:** v0.3 HYDE is *not* a point extraction, so it is a **direct reference, not a designed difference.** v0.4 single-basin HYDE should reproduce v0.3 epoch-for-epoch: `n_cells=45`, `basin_area≈3687.8`, and per epoch (1100, 1200) the cropland and grazing **area (km²), percent, and the cross-cell `p10`/`p90`/`std`** (the distribution stats require `&detail`). Confirm the genuine HYDE epoch set in [1100,1200] is exactly {1100,1200}; if so v0.3's endpoints coincide with the full native set and v0.4 must match both (resolution, not decimation). *(This span can't expose v0.3's "endpoints-only" decimation risk — here endpoints = genuine epochs; that needs a wider-span fixture, not WO14.)*

- **Volcanic (eVolv2k) — `global_forcing`**, same everywhere → v0.4 reports **exactly** v0.3's `volcanic_events=4`. An exact invariant.

**HYDE is the one non-degenerate distribution at single-basin.** Bands A–E are n=1 (zero spread). HYDE Band T resolves 45 cells with real cross-cell spread (`p10`/`p90`/`std`), so it is where single-basin actually exercises the areal distribution machinery — and v0.3 supplies matching spread stats to check it against. It is the most informative reference check in the comparison; treat a HYDE per-epoch mismatch as a bug, not a generation difference.

---

## Notes for CC

- Don't flag the contract's **blessed deviations** as mismatches: the LMR caveat on every LMR row, the perennial flag, the modal class label in `representative_raw` (contract §9). These are intended v0.4 content.
- Hold span/level/coordinates identical to v0.3; the only structural difference should be point-vs-areal, which is the thing under test.

---

## Deliverables

1. v0.4 single-basin payload (lean + `&detail`) persisted alongside the v0.3 json.
2. Comparison notebook + comparison TSV (the four-bucket table with verdicts).
3. Part 3 degeneracy assertions (pass/fail).
4. Part 4 Band T / ECC result.
5. Findings: the reference result (bucket 1 agreement, scorer validated at n=1), the v0.4-only / v0.3-only inventories, the synthesis check (bucket 4), the ECC-against-reference result.

---

## Acceptance

- Engine runs single-basin without error; `n_units=1`, `type=basin`.
- Bucket 1: all shared quantities `match` (raw-vs-raw, or score-vs-rank), or any difference traced to a known cause.
- Bucket 3: every v0.3-only absence explained; no unexplained drops.
- Part 3 degeneracy assertions pass.
- Part 4: LMR reproduces the v0.3 cell over the full series; HYDE reproduces v0.3 epoch-for-epoch (n_cells, basin_area, area/pct/p10/p90/std); volcanic matches exactly.
- Findings written.

---

## Back to Opus

Round-trip on: any **bucket-1 MISMATCH** or **bucket-3 UNEXPLAINED** (those are bugs, decide the fix); the **outlet_type synthesis** result (does the derived value match the raw flags — first real test of the B4 synthesis against its inputs); whether **LMR collapses to the v0.3 cell** (if not, the ECC sub-resolution logic needs a look); and any **HYDE per-epoch divergence** — now a reference, it should match exactly, so a difference is a bug in the areal HYDE path, and it's the cleanest place we'll ever have to catch one.
