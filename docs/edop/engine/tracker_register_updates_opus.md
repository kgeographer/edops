# Draft: tracker + register updates — WO14 (full) and WO15

Drop-in drafts. Destinations labeled. Nothing here is written to the live files — review and place.
Two items at the end are **optional** (locked-decision candidates) — take or leave.

---

## 1 — Tracker changelog (new entries, newest-on-top, above the 2026-06-26 WO14 Part 1 line)

> **2026-06-27** — WO15 complete. Area-weighted grid-cell weighting refined in `aggregate_band_t` (HYDE + LMR paths). **Correction to WO14 framing:** the engine was *already* area-weighting boundary cells by `ST_Area(ST_Intersection(...))` — not boolean weight-1; the 80-vs-45 cell divergence from v0.3 was correct fractional-overlap inclusion, not a defect. WO15 changes the normalization from `overlap/Σoverlap` (size-biases unequal cells) to `overlap/cell_area` (each cell's own fractional coverage), removing a latitude-driven size bias via cos(φ). `w_eff` (effective cell count = sum of fractional coverages) added to the HYDE detail block. Impact at 16°N is correctly minimal: LMR Δ<0.001 (equal-area cells at one latitude), HYDE stat shifts <5%; wo11b Band T regression passes at float_tol=0.01, **no re-freeze required**. Test suite 58 PASS — note the 7 DB-fixture tests came online this WO via a new `scripts/edop/areas/conftest.py` (their prior absence was a missing-fixture failure, not introduced by WO15; the standing bar was 51 through WO14). Branch: `engine_v0.4b`.

> **2026-06-27** — WO14 complete (Parts 2–5). Single-basin run + v0.3 reference comparison on the Timbuktu fixture (L06, 1100–1200 CE). Payload now **373 rows (52 basin + 321 Band T)** — the 52nd basin row is `reservoir_vol`, newly emitted after an upstream-only coalesce in `load_catalog._emit` (when `su=='s'`, `col` is None but `col_u` exists, use `col_u`; preserves s/u semantics, no codebook edit) routes it to B5 `distribution_only`. **Four-bucket comparison: 0 MISMATCH, 0 UNEXPLAINED** — bucket 1 (17 shared quantities) all match; bucket 3 (13 v0.3-only) all explained (point/profile constructs, deferred/skipped vars, internal id); bucket 4 (4 transforms) — `outlet_type` and `coast_fraction` synthesis verified against raw flag inputs (first end-to-end B4 test), `eco_id` numeric-id loss and `pnv_shares` within-basin distribution as explained differences. **Degeneracy at n=1 clean** (6 properties): coherence=concentrated, modality never two_regime, no score suppression, weight_at_zero∈{0,1}, coverage=1.0 where data, class_mixture=100%-one-class. Incidental: `cropland_extent` correctly fires `outside_active_domain` (zero_fraction≥0.20, weight_at_zero=1.0 — whole basin at floor). **Scorer validated end-to-end:** zero-aware two-pass rank reconciles to <0.005 pp once the check mirrors `rank_expr`; the larger naive deltas (aridity 1.48, dist_sink 6.59, pop_density 7.12) are v0.4's intentional zero-aware improvement over v0.3's naive global percentile, not regressions. **LMR ECC confirmed:** `collapsed_subresolution` on all 101 rows; 3-cell area-weighted collapse reproduces v0.3's single-cell series within 0.006. **Volcanic:** v0.4 returns the full unfiltered eVolv2k record (10 rows); v0.3's `volcanic_events=4` reflects a ~5 Tg S VSSI display threshold — all 4 large events present; the exact-invariant claim in the WO14 design doc was wrong (significance filtering is a surface concern). Notebook `single_basin_comparison.ipynb`; `wo14_comparison.tsv`; AF.11+ written. Branch: `engine_v0.4b`.

---

## 2 — Tracker "You are here" (proposed replacement)

> Engine **assembled and whole**; now being extended across the neighborhood and support axes off the buffer-built core (everything downstream of the weighted basin set is reused; only resolvers are neighborhood-specific). **WO12** (L8 buffer — clean MAUP read) and **WO14** (single-basin — first *meaningful-boundary* neighborhood, validated end-to-end against the deployed v0.3 reference) done; **WO15** (area-weighted cell weighting) done. The engine has now been exercised at both ends of cardinality: n=1 (single-basin) and ~74 basins (L8 buffer). **Neighborhood taxonomy governs the path:** meaningful-boundary neighborhoods (`basin`, ring-expansion, polity) follow something real and can't silently clip an extreme edge unit — they are the dashboard/headline path; arbitrary-boundary neighborhoods (`buffer`, bbox) are analyst-drawer only. The buffer was the right build fixture and is now demoted from a headline feature on those grounds. **Next on the neighborhood axis: basin-ring** (first *multi-basin* meaningful-boundary neighborhood), then polity.

---

## 3 — Register: update the existing HYDE cell-selection row (currently under "within step 3 — engine assembly")

WO15 settled the *mean* part of this item; the *distribution* part is still open and shouldn't be lost. Suggested replacement for the `HYDE cell-selection: ST_Intersects vs restricted overlap` row:

> | **HYDE/grid distribution stats under sharply-differing boundary cells** | WO15 settled cell *weighting*: the areal mean is now fractional-overlap-correct and size-unbiased (`overlap/cell_area`, both grid paths). v0.3's centroid-in rule (45 cells) and the prior boolean-inclusion read (80 cells) are both superseded — neither was the target. **Open:** whether the cross-cell distribution stats (`p10`/`p90`/`sd`) stay faithful when boundary cells carry values far from the interior. A low-overlap edge cell with an extreme value is still *in the weighted sample*; weighted-quantile behavior there is untested. Timbuktu can't expose it — its edge cells resemble its interior (the <5% WO15 shifts). | First **boundary-straddling fixture** (basin-ring, or a Sahel-edge polity where interior≠boundary). Adjacent to the edge-sensitivity diagnostic item (basin-path analogue). |

(If you'd rather, split it: move "weighting fixed" to **Closed** as WO15, keep only the distribution-stats question open. Either works; I kept it as one row so the lineage stays in one place. This is the "keep the flag" call from the last exchange — strike the open half if you've decided weighted-quantile is fine and it's a ghost.)

---

## 4 — Register: retarget the pnv item; narrow the multi-column item

**`pnv_shares` row** — deferral confirmed to multi-basin (your call), with the design note attached so it isn't re-derived. Suggested trigger + note update:

> Trigger: **first multi-basin neighborhood (basin-ring)** — that's where the design fork bites. Parked design: lean keeps `pnv_majority` + the cross-basin vote-mixture (correct headline); `&detail` carries the **area-weighted pooled composition** (sum each class's area across basins ÷ total area — the true ground breakdown; degenerates to the single basin's `pnv_pc_*` shares at n=1). Open fork: whether `&detail` *also* wants the per-basin spread of compositions. Pooled vs per-basin-majority diverge hardest exactly at the desert/sown margin (every basin 60/40 → pooled 60/40 but vote-mixture 100% one class).

**`Multi-column variable gap` row** — your read: pnv is the *only* compositional variable, so there's no general model gap. The row cites `river_area_upstream` too, but that's a single deferred upstream value, not compositional — it belongs to its existing B5 deferral, not here. Suggested: **drop the "general fix" framing**, or narrow the row to: "Two non-standard cases only: `pnv_shares` (compositional → handled by the pnv item) and `river_area_upstream` (single deferred value → its own B5 row). No general multi-column model gap; do not build a general multi-column codebook extension on the strength of these two." Your call whether to narrow-in-place or close it.

---

## 5 — Register: two small new items

**Sequencing artifact (new row, "within step 3 — engine assembly"):**

> | `modality` emitted before the domain guard | At n=1, `cropland_extent` carries `modality='unimodal'` *and* `status='outside_active_domain'` — the distributional flag is set before the zero-domain guard nulls the score. Harmless (the score is correctly nulled), but a row can read as having a live modality verdict on a variable the engine refused to score. | Cosmetic; resolve whenever B6/guard ordering is next touched — either compute distributional flags after the domain guard, or have the guard clear them. |

**Surface-concern note (new row, near the HYDE-1950 display item, or as a locked decision — see §6):**

> | eVolv2k significance filtering is a surface concern | v0.4 returns the full unfiltered eVolv2k record in-span (`global_forcing`); v0.3's `volcanic_events` count applied a ~5 Tg S VSSI threshold. The engine serves the record; any significance cut (which events "count") is a display/use-case choice. | Display layer applies its own VSSI threshold; engine default stays unfiltered. (Instance of the resolve/serve principle — see §6.) |

---

## 6 — Optional locked-decision candidates (take or leave)

You said earlier you'd capture the resolve/serve principle "when you want it." WO13a, WO14's volcanic finding, and the modality retirement all now rest on it, so it's earning its place. If you want it in **Locked decisions** (dated 2026-06-27):

> - **The engine resolves and serves; it does not interpret.** Summarization is an analytical construct and belongs closer to the surface, with the use case. The engine may *describe* the object it returns (spreads, percentiles, distribution shape, provenance, caveats — fair game, lossless); it may not *decide what the object means* (no suppression gates, no significance filters, no verdicts that withhold data). The test is describe-vs-decide. Modality-as-gate was the first thing caught crossing the line the wrong way (retired, WO13a); eVolv2k significance filtering is the second (kept at the surface, WO14). A working default, not a law — revisable when downstream evidence (a Phase 4 correspondence need, a source whose nature breaks the line) demands it.

And the neighborhood taxonomy, if you want it locked rather than only in "You are here":

> - **Neighborhood taxonomy — meaningful vs arbitrary boundary.** Meaningful-boundary neighborhoods (`basin`, ring-expansion, polity) have boundaries that follow something real, so they can't silently clip an extreme-valued edge unit — honest even to a reader who checks no caveats; headline/dashboard-eligible. Arbitrary-boundary neighborhoods (`buffer`, bbox, arbitrary polygon) can clip an extreme edge and skew the result — trustworthy only to an analyst who reads `coverage`/`shortfall`; analyst-drawer only. The buffer was the correct build fixture (it exercises every hard path) and is demoted from a headline feature on these grounds. Support level (L6/L8) is orthogonal — any shape runs at any level.

---

*Not drafted here, by prior agreement: the "areal response object is a multivariate spatial distribution" research question stays parked in conversation, not the tracker, until a use case forces the response-object choice.*

