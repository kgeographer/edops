# Engine response contract — Areas signature payload

**Date:** 2026-06-24 (amended — folds in WO1–WO9 as built; supersedes the 2026-06-22 draft)
**Status:** Reflects the engine as built through WO9. Branches B1–B5 + B7 emit through `make_row`; B6 (WO10) and final assembly remain. Every draft decision in §7 is resolved except **one open item** (§7). Amendment record: `contract_amendments.md`.
**Scope:** governs the engine's return object and its projections. Route-agnostic (the same object serves the buffer path on `/signature` and the polygon path on `/area`); consumer-agnostic (serves both the human reading one area and the machine comparing many). Does **not** govern route mechanics or branch internals.

---

## 1. The governing shape

The engine always computes **one complete object**. Parameters select which parts of it serialize. The default serialization is **lean**; bulk is opt-in. Nothing is ever lost, because the complete form is always available to ask for — the parameters decide what's *sent*, not what's *computed*.

This is the resolution of the preserve-everything instinct and the less-is-more instinct at once: the complete object honors the first (the distributions and trajectories we went to trouble to keep are always there to request), and the lean default honors the second (a consumer who passes nothing gets a compact, honest payload). It also *is* the two-consumers split made structural — the lean projection is the comparison vector; `&detail` is the human view of one area.

---

## 2. Top-level fields (query-scoped, emitted once)

| Field | Meaning |
|---|---|
| `neighborhood` | Echo of the resolved query: type (`buffer` \| `basin` \| `upstream` \| `polygon`), its parameters (point, radius, level, or polygon id/geometry), and the resolved-set summary (`n_units` total, `unit_type`). |
| `shortfall` | **Geographic** absence — fraction of the query area with no data-bearing spatial unit beneath it (open water / no basin). Reported, never renormalized. A query-level property, not per-variable. (Locked 2026-06-13.) |
| `bands` | Which bands were requested. |
| `temporal` | Present only if Band T was requested: the `from_year`/`to_year` span. Its absence is the Band T gate (§6). |
| `caveats` | Maps each caveat key referenced by any row to its text, emitted once. Contains only keys some row used (empty when none). The row-level `caveat` list points into this. (Pin 2.) |
| `rows` | The list of per-output rows (§3–4). |

The `neighborhood` echo is what keeps the object route-agnostic: the engine returns the same shape whether a buffer or a polygon produced the unit set; only the echo's `type` and parameters differ.

---

## 3. Rows are keyed on emitted-output identity

The set of rows is **not** one-to-one with the catalog, but every emitted row keys to a catalog entry — some of them derived. The asymmetry runs in one direction only: catalog variables that emit nothing for a given query.

- **Catalog variables that emit nothing** — `strata_code` (excluded), `ecoregion` (deduped into `eco_id`), `river_area_upstream` (deferred), and `endorheic` / `coast_flag` (consumed as *inputs* to the B4 synthetics). No row.
- **The two synthesized outputs** — `outlet_type` and `coast_fraction` — are **catalog-resident derived variables** (added WO7b), their provenance carried in the catalog `notes` column following the existing derived-variable pattern. So they key to a catalog entry like any other row.

Count: 54 catalog vars + 2 derived (`outlet_type`, `coast_fraction`) = 56 catalog rows; minus the 5 non-emitters = the 51 rows `step3_results` holds.

So a row's `variable` field names an **emitted-output identity** that maps to a catalog entry (possibly a derived one). *(The draft's "synthetic with no catalog row / `derived_from` on the row" framing is retired: synthetics live in the catalog, provenance in `notes`, not in the payload.)* This is the B4 two-consumers choice — the legible named output over the machine-tidy flags — as a keying requirement.

---

## 4. The row envelope — lean default

Every row carries this much with no switches. It extends the locked 2026-06-15 envelope. The principle: **the lean row is self-trusting** — it gives the headline *and* every flag that tells you whether the headline lies, so a consumer can act on the lean payload alone and know when not to trust a number.

| Field | Meaning | Notes |
|---|---|---|
| `variable` | Emitted-output identity (§3). | Keys to a catalog entry, possibly derived. |
| `band` | A–E or T. | |
| `method` | `area_weighted` \| `dominant_basin` \| `class_mixture` \| `flag_fraction` \| `extreme` \| `distribution_only` \| `grid_areal_distribution` \| `grid_areal_collapsed` \| `global_forcing`. | |
| `unit_type` | `basin` \| `hyde_cell` \| `lmr_cell` \| `global`. | Collision 1, §5. |
| `n_units` | The resolved unit-set size. | Aggregating methods: every unit contributes. Selection methods (`dominant_basin`, `extreme`): the value rests on one unit, named in `detail`; `n_units` still reports the pool. Nothing downstream branches on the distinction. |
| `representative_score` | Headline in global-percentile space (0–100), or **null**. | Null arises four ways, each distinguished by another field: `spread` (B1 — `coherence='spread'`); two-regime suppression (B6 — `score_suppressed=true`); Band T (`band='T'`); categorical/flag methods not percentile-scored (`method`). Read the explaining field to know which null it is. |
| `representative_raw` | Headline in native units, or null. | Carries: the Band T value; the discharge value (`dominant_basin`); the **modal class label** (`class_mixture`, WO7b); the extreme value (`extreme`); the fraction (`flag_fraction`). Null where no native headline applies (e.g. `area_weighted` — native-unit means deferred). |
| `score_suppressed` | bool | `true` when `representative_score` is null *because* B6 found `two_regime` and a single number would lie — distinguishes a withheld score from a not-applicable one. (Pin 4.) |
| `coverage` | Per-variable: fraction of in-area weight that contributed a usable value for *this* variable, after the path's absence handling. | Collision 2, §5. |
| `status` | `ok` \| `outside_active_domain` \| `no_data`. | Final value set (confirmed WO4–WO9). Execution outcome only; verdicts live in the flags. |
| **quality flags** | The verdicts that qualify the headline — always present in lean. | Inventory below. |

Band T rows additionally carry `year`, `epoch_year`, and `units` (the native-value unit).

**Quality flag inventory (the lean payload's trust layer):**

| Flag | Values | Tells the consumer |
|---|---|---|
| `coherence` | `concentrated` \| `spread` \| `mixed` \| `null` | Whether the headline is a fair summary: `concentrated` (one value/class dominates), `spread` (continuous, wide), `mixed` (categorical, no dominant class), `null` (no verdict — `flag_fraction`, `extreme`, Band T; **and `distribution_only` pending §7**). |
| `modality` | `unimodal` \| `two_regime` \| `null` | One regime or two (B6, continuous only; `null` elsewhere). When `two_regime`, `representative_score` is nulled and `score_suppressed=true`. (Pin 4 — `suppressed` dropped as a modality value.) |
| `distribution` | `reported` \| `collapsed_subresolution` | Band T: whether cross-cell spread is real signal (HYDE, high ECC) or a sub-resolution artifact collapsed away (LMR). (B7 / ECC.) |
| `weight_at_zero` | float | Zero-inflation exposure; pairs with `outside_active_domain`. (B1 hurdle.) |
| `caveat` | list of keys (empty list, never null) | The caveat-text keys this row references — `lmr_caveat` (every LMR row), `hyde_caveat` (HYDE 1950 epoch). Text lives once in the top-level `caveats` dict (§2). (Pin 2.) |

The flags are tiny and they make bulk navigable: a distribution preserved without its verdict is preserved-but-buried. Keeping the verdicts in the lean default is what lets a consumer decide *whether* to pay for the detail.

---

## 5. The three collisions, resolved (built WO4–WO9)

| Collision | Resolution |
|---|---|
| **`n_basins` vs `n_units`/`unit_type`** | Unified globally: every row carries `n_units` + `unit_type` (`basin` for the basin path; `hyde_cell`/`lmr_cell`/`global` for Band T). `n_basins` retired. One field the machine consumer reads uniformly. |
| **Two `coverage_weight` meanings** | One semantic: `coverage` = fraction of in-area weight that contributed a usable value for this variable. Basin path = renormalized surviving weight; grid path = data-bearing-cell fraction. Same meaning, path-specific computation. Geographic absence stays separate as top-level `shortfall`. |
| **Spread units** | No bare `spread` at row level. Distribution detail lives in `&detail` (§6), every distribution field **space/unit-tagged** (`unit:'percentile'` for basin paths, `unit:'km2_per_cell'` for Band T HYDE). |

**Deferred, with a trigger:** the grid path's `coverage` currently *fuses* geographic and attribute absence into one cell-fraction (at inland Timbuktu both ~0, so coverage = 1.0 and the fusion is invisible). Splitting it to match the basin path is triggered by the first **coastal Band T query** — the same coastal fixture pending for the open-water shortfall path and the endorheic-fraction / `weight_at_zero` consistency check. Register items.

---

## 6. Projections (opt-in bulk)

| Projection | Adds |
|---|---|
| *(default)* | The lean row envelope (§4) only. |
| `&detail` | The bounded spatial detail behind each verdict: distribution summaries (spread, p10/p90 — unit-tagged), full class mixtures (B3/B4 per-class %), two-regime breakdowns (B6 regime weights), the dominant-basin envelope (B2 min/max + `dominant_hybas_id`), the extreme carrier basin, and per-epoch spatial spread for Band T HYDE. |

*(`&dists` is dropped — a single `&detail` switch covers distributions, regimes, and temporal detail.)*

Spatial detail is **bounded** — a fixed stat set per variable. The temporal trajectory is the axis that **explodes**: because the no-within-span-collapse rule (locked) preserves native temporal resolution, a wide LMR span returns its full annual series in the *lean* default already (the 3,427-row case).

Year-to-interval mapping is permitted only as **resolution** — snapping a query year to a dataset's genuine native step (HYDE's irregular epochs are real, so this is lossless) — and never as **decimation**: the LMR five-notch buckets used in the cliopatria display layer are 200–400-year pre-averages, and collapsing LMR's native annual series into them would be the within-span temporal averaging this contract forbids. The notch and epoch labels may ride alongside native values as human-readable interval tags (the role `lmr_caveat`/`hyde_caveat` already play), never as substitutes for them.

So `&detail` governs the bounded spatial expansion; the temporal volume is governed by the span itself, not a switch. If wide-LMR payload size becomes a problem, the lever is the parked LMR-decimation question — presentation-layer binning (the Explorer bins LMR to five periods) or a future temporal-step parameter, not an engine default.

**Band T gate:** Band T is opt-in by construction — it can't be requested without a `from_year`/`to_year` span, and the default `bands` omits T.

**ECC vs no-collapse — orthogonal:** the ECC diagnostic governs **spatial** collapse (whether a query resolves a grid's cells or treats them as sub-resolution); the no-within-span rule governs **temporal** aggregation (never averaging across the span). An LMR query can collapse spatially at each step while preserving every step. (Pin 3.)

---

## 7. Decisions

**Resolved (draft §7, now built):** ① `n_units`/`unit_type` unified, `n_basins` retired. ② `coverage` one meaning, `shortfall` separate top-level, Band T split deferred to the coastal fixture. ③ single `&detail`, `&dists` dropped. ④ lean trust layer confirmed — `coherence`, `modality`, `distribution`, `weight_at_zero`, `caveat`, plus `score_suppressed`. ⑤ synthetic provenance lives in the catalog `notes` column, not a payload field.

**Open — one decision:** **distribution_only coherence.** `distribution_only` populates `representative_score` but emits `coherence=null`, leaving a headline with no trust flag — the one place the self-trusting-lean-row principle isn't met. `coherence` is a pure spread test (weighted p90−p10 < T) that B5 already computes, so it's free to emit. **Recommendation: emit it.** Settle at the post-WO10 consistency pass.

## 8. Reconstructions — confirmed (closed)

Confirmed during extraction WO4–WO9: the inline B1–B6 field names; the `status` value set (`{ok, outside_active_domain, no_data}`); that no B7 `_row` field is dropped in the unification (`n_units`, `unit_type`, `year`, `epoch_year`, the caveat keys all carried). This section is closed.

## 9. Regression note

The assembled payload — full-monte, every projection on — reproduces the 13 TSVs as the frozen ground truth; the lean projection is a filter on top of a payload proven complete. **Blessed deviations:** three rows deliberately depart from the frozen TSVs where the engine corrects a notebook omission, each re-frozen with sign-off — the LMR caveat on every LMR row (WO4), the perennial flag (WO5), and the modal class label in `representative_raw` (WO7/7b). These are corrections, not regressions.