# Engine response contract — Areas signature payload

**Date:** 2026-06-22
**Status:** draft for Karl's approval. This is the design gate; branch extraction (WO4+) builds the shaper to it. Nothing here is code — it's the contract the shaper and every branch must satisfy.
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
| `temporal` | Present only if Band T was requested: the `from_year`/`to_year` span. Its absence is the Band T gate (see §6). |
| `rows` | The list of per-output rows (§3–4). |

The `neighborhood` echo is what keeps the object route-agnostic: the engine returns the same shape whether a buffer or a polygon produced the unit set; only the echo's `type` and parameters differ.

---

## 3. Rows are keyed on emitted-output identity

WO3 established this and it's a structural requirement, not a detail. The set of rows is **not** the set of catalog variables. Three departures, all explained by locked decisions or register deferrals:

- **Catalog variables that emit nothing** — `strata_code` (excluded), `ecoregion` (deduped into `eco_id`), `river_area_upstream` (deferred), `endorheic` and `coast_flag` (consumed as *inputs* to synthetics). These have no row.
- **Synthetic outputs with no catalog row** — `outlet_type` and `coast_fraction` are produced inside B4 from the flag inputs. These have rows but no single catalog provenance.
- The result: 54 catalog vars → 49 direct emitters + 2 synthetics = the 51 rows `step3_results` holds.

So the row's `variable` field names an **emitted output identity**, which may be synthetic. A row carries `derived_from` (the catalog inputs) when it's synthetic, and is self-identifying otherwise. The contract must be comfortable with both a `variable` that has no catalog row and catalog rows that produce nothing. This is the B4 two-consumers choice — the legible named output over the machine-tidy flags — showing up as a keying requirement.

---

## 4. The row envelope — lean default

Every row carries this much with no switches. It extends the locked 2026-06-15 envelope. The principle: **the lean row is self-trusting** — it gives the headline *and* every flag that tells you whether the headline lies, so a consumer can act on the lean payload alone and know when not to trust a number.

| Field | Meaning | Notes |
|---|---|---|
| `variable` | Emitted-output identity (§3). | May be synthetic. |
| `band` | A–E or T. | |
| `method` | The branch/method that produced it (`area_weighted`, `dominant_basin`, `class_mixture`, `flag_fraction`, `extreme`, `distribution_only`, `grid_areal_distribution`, `grid_areal_collapsed`, `global_forcing`). | |
| `unit_type` | `basin` \| `hyde_cell` \| `lmr_cell` \| `global`. | Collision 1 resolution, §5. |
| `n_units` | Count of contributing units. | Replaces `n_basins`. |
| `representative_score` | Headline in global-percentile space (0–100), or **null**. | Null for Band T (no temporal scoring), and null when a verdict says no single number is honest (two-regime). |
| `representative_raw` | Headline in native units, or null. | Carries the Band T headline. |
| `coverage` | Per-variable: fraction of in-area weight that contributed a usable value for *this* variable, after the path's absence handling. | Collision 2 resolution, §5. |
| `status` | `ok` \| `outside_active_domain` \| … | Confirm full value set against code (§8). |
| **quality flags** | The verdicts that qualify the headline — always present in lean: | See flag inventory below. |

**Quality flag inventory (the lean payload's trust layer):**

| Flag | Values | Tells the consumer |
|---|---|---|
| `coherence` | `concentrated` \| `spread` | Whether the representative score is a fair summary or papers over a wide spread. (B1) |
| `modality` | `unimodal` \| `two_regime` \| `suppressed` | Whether the area holds one regime or two; when `two_regime`, `representative_score` is nulled and the consumer should open `&detail`. (B6) |
| `distribution` | `reported` \| `collapsed_subresolution` | For Band T: whether cross-cell spread is real signal (HYDE, high ECC) or a sub-resolution artifact collapsed away (LMR). (B7 / ECC diagnostic) |
| `weight_at_zero` | float | Zero-inflation exposure; pairs with `outside_active_domain` status. (B1 hurdle) |
| `caveat` | refs: `lmr_caveat`, `hyde_caveat` | Mandatory provenance riders — LMR-is-the-prior (every LMR row), HYDE 1950 cadence artifact. Carried as references; the caveat text lives once at top level. |

The flags are tiny and they are the thing that makes bulk navigable: a distribution preserved without its verdict is preserved-but-buried. Keeping the verdicts in the lean default is what lets a consumer decide *whether* to pay for the detail.

---

## 5. The three collisions, resolved

| Collision | Resolution | Rationale |
|---|---|---|
| **`n_basins` vs `n_units`/`unit_type`** | Unify globally: every row carries `n_units` + `unit_type`. The basin path sets `unit_type="basin"`; Band T sets `hyde_cell`/`lmr_cell`/`global`. `n_basins` retired. | One field the machine-comparing consumer reads uniformly; the unit kind travels as data, not as a column-name difference. |
| **Two `coverage_weight` meanings** | One semantic: `coverage` = the fraction of in-area weight that contributed a usable value for this variable. Basin path computes it as renormalized surviving weight after dropping nodata basins; grid path as data-bearing-cell fraction. Same *meaning*, path-specific computation. Geographic absence stays separate as top-level `shortfall`. | The basin path already splits attribute-absence (`coverage`, renormalized) from geographic-absence (`shortfall`). Unifying the *meaning* of coverage and keeping shortfall at top level removes the same-name-different-thing trap without forcing rework. |
| **Spread units (percentile-points vs km²/cell)** | No bare `spread` field at row level. All distribution detail lives in the `&detail` block (§6), and every distribution field is **space/unit-tagged** (`space: "percentile"` for basin paths, `unit: "km2_per_cell"` etc. for Band T). | The same conceptual slot means different things by path; the tag makes the space explicit at the point of use rather than implicit in the column name. |

**Deferred, with a trigger:** the grid path's `coverage` currently *fuses* geographic and attribute absence into one cell-fraction (at inland Timbuktu both are ~0, so coverage = 1.0 and the fusion is invisible). Splitting Band T coverage into geographic `shortfall` + attribute `coverage`, to match the basin path, is an engine-assembly refinement triggered by **the first coastal Band T query** — the same coastal fixture that would first exercise the open-water shortfall path at all. Register item.

---

## 6. Projections (opt-in bulk)

| Projection | Adds | Status |
|---|---|---|
| *(default)* | The lean row envelope (§4) only. | Defined. |
| `&detail` | The bounded spatial detail behind each verdict: distribution summaries (spread, p10/p90 — unit-tagged), full class mixtures (B3/B4 per-class %), two-regime breakdowns (B6 regime weights), the dominant-basin envelope (B2 min/max + `dominant_hybas_id`), and per-epoch spatial spread for Band T HYDE. | Defined. |
| `&dists` | Reserved for finer-grain full-resolution control (e.g. full sorted distributions, or a temporal-decimation opt-out). | **Named, not defined** — semantics to settle against a real payload, per your preference to let specifics emerge. |

The two axes behave differently and that's why the switches matter. Spatial detail is **bounded** — a fixed stat set per variable. The temporal trajectory is the axis that **explodes**: because the no-within-span-collapse rule (locked) preserves native temporal resolution, a wide LMR span returns its full annual series in the *lean* default already (the 3,427-row case). 

Year-to-interval mapping is permitted only as resolution — snapping a query year to a dataset's genuine native step (HYDE's irregular epochs are real, so this is lossless) — and never as decimation: the LMR five-notch buckets used in the cliopatria display layer are 200–400-year pre-averages, and collapsing LMR's native annual series into them would be the within-span temporal averaging this contract forbids. The notch and epoch labels may ride alongside native values as human-readable interval tags (the role lmr_caveat/hyde_caveat already play), never as substitutes for them.

So `&detail` governs the bounded spatial expansion; the temporal volume is governed by the span itself, not a switch. If payload size from wide LMR spans becomes a problem, the lever is the parked LMR-decimation question — which would land under `&dists` or as presentation-layer binning (the Explorer already bins LMR to five periods), not as an engine default.

**Band T gate:** Band T is opt-in by construction — it can't be requested without a `from_year`/`to_year` span, and the default `bands` omits T. No separate mechanism needed.

The ECC diagnostic governs spatial collapse (whether a query resolves a grid's cells or treats them as sub-resolution); the no-within-span rule governs temporal aggregation (never averaging across the requested span). They are orthogonal: an LMR query can collapse spatially at each step while preserving every step.


---

## 7. What needs your decision

1. **Collision 1** — confirm the global `n_units`/`unit_type` unification (retire `n_basins`), versus keeping `n_basins` on the basin path and `n_units` only on Band T.
2. **Collision 2** — confirm `coverage` as one meaning with `shortfall` separate at top level, and the coastal-trigger deferral of the Band T split.
3. **`&detail` contents** — confirm the bounded-summary boundary above, and whether `&dists` should be defined now or left reserved.
4. **Lean flag set** — confirm the five quality flags (§4) are the right lean trust layer: enough to know when a headline lies, without leaking into bulk.
5. **Synthetic provenance** — confirm `derived_from` on synthetic rows (`outlet_type`, `coast_fraction`) is wanted, versus leaving them unprovenanced.

## 8. What CC must confirm against the code (flagged reconstructions)

- The exact field names and value sets in the inline B1–B6 dicts (`spread`, `p10`, `p90`, `weight_at_zero`, `dominant_hybas_id`, the status values) — these were assembled ad hoc per block and the contract proposes unifying them; the real names need verifying before the shaper standardizes them.
- Whether `status` carries values beyond `ok` / `outside_active_domain`.
- The B7 `_row` fields already named (`n_units`, `unit_type`, `year`, `epoch_year`, `lmr_caveat`) map onto this envelope as the template the basin paths conform *to* — confirm no B7 field is dropped in the unification.

## 9. Regression note

The first assembled payload — the full-monte form, every projection on — must reproduce the 13 TSVs exactly, since those are the frozen ground truth. The lean projection is then a filter *on top of* a payload already proven complete. So the shaper is built and regressed at full bulk first; the projections are validated as subsets second.
