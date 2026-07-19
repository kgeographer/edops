# L08 similarity inquiry — findings

**Branch:** `l08` (cut from `demo`)
**Notebook:** `notebooks/edop/demo/wo_l08_similarity.ipynb`
**Purpose:** Establish whether the LENS_REGISTRY similarity index can be built and served at
L08 (190,675 basins) to support the CDOP Workbench metric swap (increment 1 of
`docs/cdop/CDOP_workplan_v1.md`). Four questions: build feasibility, query performance,
L06 threshold transfer, and topN-vs-threshold for the 258-city WH Cities corpus.

---

## A — Build feasibility

**Data sources confirmed:**
- `public.v_basin08_persist_rev2` — has `pre_mm_monthly` and `tmp_dc_monthly` (same columns
  as the L06 rev2 view used by `load_similarity_index`)
- `public.basin08` — has `pre_mm_syr` and `tmp_dc_syr` scalar columns needed by active lenses
- `gaz.wh_cities.basin_id` → `basin08.id` (sequential 1–190,675), not `hybas_id` — join
  through `basin08` to get `hybas_id` for index lookup

**Timing and memory:**

| Step | Time | Memory |
|---|---|---|
| Load arrays (`v_basin08_persist_rev2`) | 2.4 s | 36.6 MB |
| Compute derived variables | 0.03 s | 6.1 MB |
| Load scalars (`basin08`) | 1.6 s | — |
| Build all three lens states | 0.03 s total | 17 MB |
| **Total startup** | **~4 s** | **~17 MB steady-state** |

**NaN profile:** 719 basins (0.4%) have NaN in `pre_concentration` and `seas_phase_offset`
(hyper-arid, zero monthly precip — circular concentration undefined). Slightly more than the
59 at L06 because small L08 basins in arid regions don't aggregate into non-zero monthly
values. Existing NaN masking in `_build_euclidean_state` handles them correctly.
`climate.temp` has 0 NaN (all 190,675 basins valid).

**Verdict: VIABLE.** Total startup cost ~4 s and 17 MB — viable alongside the existing L06
index (~1.5 MB). Two indices at startup adds ~18 MB and ~5–6 s; well within reason for the
app server.

---

## B — Query performance

Test anchors: Jerusalem (hybas_id 2080000410) and Timbuktu (hybas_id 1080563570), resolved
via `ST_Contains` on `basin08`.

| Anchor | Lens | Time | Nearest | p50 |
|---|---|---|---|---|
| Jerusalem | climate.precip | 3.1 ms | 0.0028 | 1.775 |
| Jerusalem | climate.temp | 4.5 ms | 0.0145 | 1.601 |
| Jerusalem | climate.phase | 2.9 ms | 0.0179 | 2.859 |
| Timbuktu | climate.precip | 2.4 ms | 0.0026 | 2.372 |
| Timbuktu | climate.temp | 4.1 ms | 0.0256 | 1.912 |
| Timbuktu | climate.phase | 2.4 ms | 0.0019 | 2.394 |

**Verdict: FINE.** 2.4–4.5 ms per query across all three lenses. Well inside any
request/response budget. The p50 distances (~1.6–2.9) are substantially larger than L06
(where p50 for the same lenses is typically 0.8–1.5), consistent with the threshold transfer
finding below.

---

## C — Threshold transfer

The L06 thresholds (strict/moderate/loose) were calibrated on 16,397 L06 basins. At L08 the
same radii return roughly 10× more basins in absolute terms — consistent with the 11.6×
basin count — but the proportional story is more nuanced.

**Counts at L06 thresholds applied to L08:**

| Lens | Anchor | strict | moderate | loose |
|---|---|---|---|---|
| climate.precip | Jerusalem | 372 | 2,067 | 14,802 |
| climate.precip | Timbuktu | 843 | 2,770 | 9,421 |
| climate.temp | Jerusalem | 1,406 | 21,220 | 87,792 |
| climate.temp | Timbuktu | 839 | 10,493 | 55,531 |
| climate.phase | Jerusalem | 94 | 1,395 | 6,586 |
| climate.phase | Timbuktu | 725 | 4,777 | 17,901 |

**Proportional note:** Timbuktu/phase/moderate = 4,777/190,675 = 2.5% at L08 vs ~2.7% at L06
— the calibration intent (rare type returns smaller fraction than common type) survives
proportionally for precip and phase. But `climate.temp/loose` returns 87,792 basins (46% of
all L08 basins) for Jerusalem. Temperature regime is highly spatially autocorrelated at small
basin scales; adjacent L08 basins have nearly identical thermal signatures. The loose
threshold is effectively global at L08.

**Verdict: L06 THRESHOLDS DO NOT TRANSFER CLEANLY.** Absolute counts are inflated ~10×;
temp/loose is meaningless at L08. Recalibration against L08 CDFs would be required if
threshold mode is used for global L08 display. For the WH Cities use case (see D) this is
moot — the corpus is too small for threshold mode regardless.

---

## D — topN vs threshold for WH Cities corpus

**Corpus:** 254 of 258 WH Cities have an L08 basin assignment via `gaz.wh_cities.basin_id →
basin08.id → basin08.hybas_id`. The remaining 4 are coastal/island cities with no containing
L08 basin. All 254 found in the L08 index.

**Pairwise distance distribution:** the within-corpus distances span a wide range (0–4.5+
depending on lens), with distributions peaking between 0.5 and 2.5. All L06 threshold lines
(strict, moderate, loose) land in the left tail of these distributions — the corpus is too
globally distributed for the L06 calibration scale to apply.

**Peer counts at L06 thresholds (within corpus, excluding self):**

| Lens | Threshold | Median peers | Min | Max | % with zero |
|---|---|---|---|---|---|
| climate.precip | strict 0.10 | 1 | 0 | 7 | 36% |
| climate.precip | moderate 0.20 | 5 | 0 | 21 | 10% |
| climate.precip | loose 0.50 | 24 | 0 | 78 | 1% |
| climate.temp | strict 0.25 | 2 | 0 | 15 | 19% |
| climate.temp | moderate 0.75 | 30 | 0 | 83 | 1% |
| climate.temp | loose 1.50 | 148 | 2 | 205 | 0% |
| climate.phase | strict 0.10 | 1 | 0 | 8 | 39% |
| climate.phase | moderate 0.30 | 8 | 0 | 24 | 2% |
| climate.phase | loose 0.75 | 36 | 6 | 64 | 0% |

**Problems with threshold mode for this corpus:**
- Strict returns zero peers for 36–39% of cities (precip, phase) — one in three cities
  shows nothing. Broken UX for a demo.
- Loose temp returns median 148/254 peers — 58% of the corpus; not discrimination.
- No single threshold gives consistent peer density across all three lenses.

**Verdict: USE topN=5.**
- Never returns zero; consistent UX across all lenses.
- topN=5 matches what moderate precip/phase naturally return for the median city (median=5
  and 8 respectively), so it is not arbitrary — it approximates the empirically natural
  discrimination scale for this corpus.
- Current workbench already uses `limit=5` for `whc-similar` queries; no change needed.
- Honest label: **"5 most similar cities in this collection"** — scope is corpus-relative,
  not a global similarity neighborhood. This distinguishes it from the sandbox similarity
  tab, which does make global neighborhood claims.

---

## Acceptance

- L08 index build: viable at startup (~4 s, 17 MB). ✓
- Per-query performance: 2.4–4.5 ms. ✓
- L06 thresholds confirmed non-transferable at L08; recalibration deferred (not needed for
  WH Cities use case). ✓
- topN=5 with corpus-scoped label confirmed as correct mode for WH Cities. ✓
- `gaz.wh_cities.basin_id` FK path documented: `basin_id → basin08.id → basin08.hybas_id`. ✓
