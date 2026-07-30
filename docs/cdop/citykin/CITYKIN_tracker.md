# CITYKIN — Phase tracker

**This is the living source of truth** for the CITYKIN phase: current state, roadmap, and locked
decisions. If any other CITYKIN document disagrees with this one about *where things stand*, this one
wins — for CITYKIN scope only.

**How to keep this current.** Detail from notebook runs, probe scripts, correlation checks, etc. goes in
`wo{n}_findings.md` — never re-derived here. This tracker carries **top-level summary + a pointer to the
findings file**. `logs/session_log_YYYYMMDD.md` carries daily blow-by-blow and also points back to the
findings file for real detail, not a re-derivation of it. On each WO close: (1) add/replace that WO's
roadmap row and a short subsection if warranted; (2) reset the one-line *Last updated* stamp; (3) fold any
settled forward-looking note into *Locked decisions* / *Deferred* **in the same edit** — never leave a
resolved question live elsewhere. Keep *You are here* to the current WO only.

- **Location:** `docs/cdop/citykin/CITYKIN_tracker.md`
- **Last updated:** 2026-07-29 — **WO3 done: Terrain regime shipped on the sandbox Similarity panel,
  Karl-reviewed live in the browser.** The std-based knob-derivation recipe that worked for WO1a's
  point-window lens failed outright here (even a "tight" 0.5σ band admitted 24.5% of the L06 corpus —
  elevation's std sits above its own IQR, inflated by a long right tail, so a std-fraction band is far
  wider in practice than it looks on paper). Replaced with an empirical sweep of small absolute widths
  measured directly against the real conjunction code: **locked defaults elevation ±25/50/100m, relief
  ±50/100/200m** (tight/default/broad), median 0.146/0.445/1.656% of the L06 corpus matched — properly
  selective; mean is pulled up by low-elevation/low-relief queries (more company in the crowded
  lowlands, not a defect). Two-fixture generalization check passed at the locked defaults with no
  per-fixture tuning: Tbilisi (rugged, terrain-coherent, set_size 6) and a table-selected large-flat
  basin (terrain-coherent, set_size 880) share zero members, elevation ranges separated by >1,400m.
  Wired into `app/db/seasonality.py`/`routes.py`/`sandbox_v3.html` (new `elev_band`/`relief_band` API
  params, two new tight/default/broad knobs matching the panel's own convention, lens-aware hover
  popup, the existing "describes the basin, not the place" footnote extended with this lens's own
  coarse-floor caveat). Karl's browser smell tests (San Francisco, Kaifeng) both passed after two
  self-corrected misreads (a small-thumbnail misread of Kaifeng's lowland/delta match set as mountain
  ranges; and confirming — rather than assuming from Karl's description — that San Francisco's own L06
  basin is a long peninsula-ridge catchment, not a city footprint, the same HydroBASINS-drainage-
  topology mechanism as WO2a's Innsbruck case, now demonstrated live). Findings: `wo3_findings.md` (no
  exec summary). Next: wire precip/temp/aridity lenses to the WH Cities retrieval UI and delete the old
  `/api/whc-similar-env-lens` path (WO1 Part A's long-deferred half); L08 terrain knobs (named, not
  started). **Opus's WO3 tracker review, same day:** caught a stale Deferred entry (the sandbox
  Terrain regime lens WO3 just shipped was still listed as blocked on DEM acquisition — resolved by
  removing it and recording how it actually resolved, in Locked decisions, as a dissolved rather than
  cleared blocker) and a real naming collision (two distinct two-fixture rules, one per terrain lens,
  both bare "the terrain lens" — disambiguated as point-window vs. basin-scale in both rows). Both
  folded in this edit.

## Table of contents

- What CITYKIN is
- Branching / relationship to CDOP Pilot
- Roadmap
- You are here
- Locked decisions
- Deferred / out of scope

---

## What CITYKIN is

CITYKIN is the **retrieval head**: a place in, ranked environmentally-similar places out, over the WH
Cities corpus (254 of 258 basin-joined). Anchored query grammar (one origin → ranked neighbors), distinct
from the set-first cohesion grammar of the Societies/TRACE work (CDOP Pilot's WO8 arc). Retrieval has no
Galton problem — no cross-cultural inference, no hypothesis, no non-independence to control — so it
carries none of that machinery: a *distance* and a *ranking*, nothing more.

Full context and rationale: `docs/cdop/citykin/wo1_update-whcities.md`.

## Branching / relationship to CDOP Pilot

CDOP Pilot (`docs/cdop/pilot/CDOP_PILOT_tracker.md`) is now **frozen reference** — `cdop_pilot` was
fast-forward-merged into `cdop`, which holds all of WO1–WO8d pilot history. `cdop` is not pushed to
origin.

Branching convention going forward: `cdop` sits off `main`; phase-trunk branches (`cdop_citykin`, later
e.g. `cdop_trace`) cut from `cdop`, each with their own WO-child branches as needed, merged back on
accept. Per-phase directories: `docs/cdop/citykin/`, `notebooks/cdop/citykin/`, `scripts/cdop/citykin/`,
`output/cdop/citykin/`. (The pilot phase's flat layout — `docs/cdop/pilot/`, `scripts/cdop/` unprefixed —
stays as historical record, not retrofitted.)

Active branch: `cdop_citykin`, cut from `cdop`.

---

## Roadmap

| Step | Branch | Status | Notes |
|---|---|---|---|
| WO1 Part A — retire superseded similarity machinery | `cdop_pilot` (pre-merge) | **complete** | sandbox_v3's vestigial pre-WO6c panel, `/api/similarity` + `/api/similarity/lenses` routes, 4 stale tests removed. `find_similar()`/`LENS_REGISTRY` and `/api/whc-similar-env-lens` deliberately left alone — `cdop_pilot`'s WH Cities dropdown still needs them until Part B replaces them. 480 pass/0 fail/14 skip before merge, re-confirmed clean on `cdop_citykin`. |
| WO1 Part B — migrate WH Cities dropdown to the WO6b raw-curve distance; add aridity + terrain lenses | `cdop_citykin` | **terrain lens complete (via WO1a); climate/aridity lenses not yet wired** | Terrain lens design finalized and validated. Precip/temp regime (WO6b raw-curve) and aridity (`ari_log`) still need UI wiring, not yet started; unaffected by the WO1a correction. |
| WO1 Part C — terrain lens as a staged, single lens (durable design note) | — | **Tier 1 complete (as corrected by WO1a)** | Tier 2 (enclosure/containment) and Tier 3 (local DEM) remain named fidelity upgrades, not built; Kathmandu's WO1 mid-pack rank is the standing Tier-2 trigger candidate. |
| WO1 Part D — Tbilisi acceptance fixture | `cdop_citykin` | **superseded by WO1a's two-fixture gate (below), which passed** | WO1's single-fixture pass didn't generalize. Findings: `wo1_findings.md` (historical). |
| **WO1a — retire the elevation gate; query-relative tolerance core; two-fixture gate** | `cdop_citykin` | **complete — accept gate passed, 2026-07-28** | Findings: `wo1a_findings.md`; exec: `wo1a_exec_summary.md`. |
| WO1 wiring — terrain lens on `cdop_pilot` | `cdop_citykin` | **complete + polished, Karl-reviewed in browser 2026-07-28** | New route `GET /api/whc-similar-terrain` (city_id or lat/lon; `terrain_lens.py`/`terrain_grid.py`); "Terrain regime" added to the WH Cities "Similar (env)" dropdown with 3 tight/default/broad knobs (auto-apply, matching the sandbox conjunction panel's own convention). Tbilisi promoted to a real `gaz.wh_cities` row (id 259, pinned atop the dropdown, semantic-similarity hidden for it) — see Locked decisions. Three UI bugs fixed (default tab, a `d-flex`/inline-style conflict, dropdown auto-close). Detail: `logs/session_log_20260728.md`. |
| WO1 wiring — climate/aridity lenses + Part A deletion of the old path | — | **not started** | Precip/temp regime (WO6b raw-curve) and aridity (`ari_log`) still need UI wiring; only then can `/api/whc-similar-env-lens` and its harmonic-precip/Mahalanobis-temp lenses be deleted. |
| **WO2a — does basin relief-range measure terrain, or basin size?** | `cdop_citykin` | **complete — facets kept, 2026-07-29** | Diagnostic probe ahead of WO2. Findings: `wo2a_findings.md` (no exec summary this WO). |
| **WO2b — shipping-facet correlation + Kansas citation correction (Opus follow-up)** | `cdop_citykin` | **complete, 2026-07-29** | Corrected WO2a's redundancy reading to the actual shipping pair and split Kansas's excess relief into its area-explained and genuinely-distinctive components. Findings folded into `wo2a_findings.md` (no exec summary). |
| **WO3 — coarse Terrain regime lens, built + wired + reviewed** | `cdop_citykin` | **complete, 2026-07-29** | L06 only. Facets `ele_mt_sav` + `relief_range` (locked WO2a/b); tolerance-band defaults derived empirically after the std-based recipe failed (25/50/100m elev, 50/100/200m relief); two-fixture check passed; wired and Karl-reviewed live in browser. Findings: `wo3_findings.md` (no exec summary). L08 and the residual-facet idea remain named, not started. |

---

## You are here

Phase opened 2026-07-27. Branch `cdop_citykin`, cut from `cdop` (which holds all WO1–WO8d CDOP Pilot
history after the `cdop_pilot` fast-forward merge). WO1 spec: `docs/cdop/citykin/wo1_update-whcities.md`
— read in full before touching Part B; summary above.

**Current step:** WO3 — the coarse Terrain regime lens (facets locked by WO2a/b: `ele_mt_sav` +
`relief_range`) — closed 2026-07-29, built, wired, and Karl-reviewed live in the browser. The WO's
own std-based knob-derivation recipe (borrowed from WO1a's point-window lens) failed outright on this
corpus and was replaced with an empirical sweep; the two-fixture generalization check passed at the
resulting defaults with no per-fixture tuning; browser smell tests (San Francisco, Kaifeng) both
passed after two self-corrected misreads along the way. Full record: `wo3_findings.md` (no exec
summary).

**Next:** wire the remaining WH Cities retrieval lenses (precip regime, temp regime — WO6b raw-curve;
aridity, `ari_log`) to the ranked-retrieval UI and delete the old `/api/whc-similar-env-lens` path
(WO1 Part A's long-deferred half, unaffected by WO2/WO3). L08 terrain knobs and the residual-facet
idea remain named, not started.

Standing rules carried forward from CDOP Pilot: Karl runs notebooks cell-by-cell and reports output back
— never assert a number as a finding without seeing his output, never Bash-run notebook logic. Full test
suite only at merge gates; targeted tests during dev. Visual/browser review by Karl before any UI commit.
Announce what a tool call is for before running it, even quick exploratory checks.

---

## Locked decisions

| Decision | Rationale |
|---|---|
| CITYKIN is a retrieval head, not the Societies/TRACE test grammar | Anchored query, ranked neighbors, no Galton problem, no hypothesis — carries a distance and a ranking, nothing more. From WO1 Context. |
| WO6c's non-compensatory conjunction is not imported into CITYKIN | Same WO6b-validated distance core, different head: the set-query (paint-a-set) grammar stays in sandbox_v3 only; CITYKIN is ranked retrieval. From WO1 Why. |
| Terrain lens is point-window, not basin-aggregate | WO8c established point-window is materially better (211m vs 928m local relief — the container effect). The lens reads the place, not the polygon; Tbilisi (Part D) is the reason. From WO1 Part B proviso. |
| Terrain lens is one staged lens, not three separate lenses | Tier 1 (point-window: elevation, local ruggedness, landform position — all three as query-relative tolerance knobs, per WO1a below) ships this WO. Tier 2 (enclosure/containment, `ST_Touches` spatial-adjacency) and Tier 3 (local high-res DEM) are fidelity upgrades to the *same* lens — named, not built. From WO1 Part C; facet treatment finalized by WO1a. |
| No modern-only / land-use lens, ever | Those variables measure present-day human modification, not physical setting — cannot be a legitimate environmental-similarity lens. Permanently out, not deferred. From WO1 Part B. |
| Metric-within-lens is set by a correlation check, not assumed | Same lens discipline as WO8b, applied within the lens: report the correlation matrix (especially for the three terrain facets) before choosing Euclidean vs Mahalanobis/drop-to-representative. From WO1 Part B proviso. |
| Aridity kept separate from precipitation regime | Timing ("when does the rain fall") and amount ("how much water overall") are different physical questions (WO8 established this) — UI labels carry the distinction rather than collapsing it. From WO1 Part B. |
| **SUPERSEDED 2026-07-28 — Tbilisi is now a real `gaz.wh_cities` row (id 259), not a coordinate-only exception.** Karl: "I just granted it WH City status, by the power vested in me" — inserted directly (city/country/region/geom/`basin_id` via `basin08.id` lookup = 57266), terrain persisted via the normal `persist_whcities_terrain.py` run (254/255 resolve; matches the earlier live-coordinate fetch exactly: 673.0/749.0/0.410). Still pinned at the top of the city-picker dropdown, separated from the region groups by a divider — but via the normal `city_id` query path now, not the coordinate fallback. The `/api/whc-similar-terrain` route's `lat`/`lon` query mode is kept (general-purpose for any future non-corpus point), just no longer needed for Tbilisi specifically. It is **not** an actual OWHC member — the "258 World Heritage Cities" header count is left as-is (describes the real OWHC corpus); Tbilisi sits visibly apart from it, not folded into that count. | Originally decided 2026-07-27 (coordinate-only); superseded 2026-07-28. |
| Terrain point-window grid: +-10km/5km-spacing (25 pts), not WO8c's inherited +-2km/1km | A radius/density probe (Cells 7-8) found relief climbs without bound as the box widens (no natural ceiling — any radius is a judgment call) but 25 vs 81 points agree closely at 10km, so it's dense enough there without added API cost. `persist_whcities_terrain.py` and the corpus rerun at this radius. Detail: `wo1_findings.md`. |
| **SUPERSEDED by WO1a (below) — kept for history, do not build against this row.** Terrain lens: elevation as an eligibility GATE (`grid_elev_mean >= 400m`), ranking on (relief_range_m, landform_position) only | A plain 3-facet z-scored Euclidean distance failed the Part D fixture twice (named candidates ranked 174th-253rd of 254 at both 2km and 10km) because raw elevation dominated the distance. The 400m gate (a real empty histogram bin, 350-375m) fixed the Tbilisi fixture: Yerevan #1, Bhaktapur #4, Cusco #10, Sanaa #14 of 83 gate-eligible cities; Mexico City/Quito correctly excluded. **But the gate hard-codes "high" as a global constant** — a flat query city (Bruges) would be excluded by its own gate, and shape terms are meaningless for a delta city. Passing-for-Tbilisi and generalizing-to-all-254-cities turned out to be different things; WO1a replaces the gate with query-relative tolerance knobs. Detail: `wo1_findings.md`, `wo1a_terrain-lens.md`. |
| Terrain lens (WO1a): query-relative tolerance knobs anchored to the selected city, not a global elevation constant | Elevation, relief, and landform-position each become a `+-`band around the *query city's own* facet value — the same pattern already validated for the sandbox's climate-regime lenses (query-relative bands with user knobs). Bruges (~5m) asks "what's like Bruges," Tbilisi (~673m) asks "what's like Tbilisi" — same instrument, no baked-in constant. Elevation informs the ranking (it was fully discarded past WO1's gate) without dominating it (WO1's original failure), structurally, because a tolerance band constrains eligibility query-relatively rather than entering a raw z-scored Euclidean sum. From `wo1a_terrain-lens.md` Why + Part B. |
| Terrain tolerance core factored separately from its presentation head | CITYKIN wires it to a ranked-retrieval head (markers + list, WO1a); a later WO wires the *same* core to a paint-a-set head on the sandbox Similarity tab. Same "factor distance from head" discipline as WO8d's `distance_core.py` — the second consumer validates extraction, not built speculatively ahead of a real need. From `wo1a_terrain-lens.md` Part B proviso + Forward. |
| **The point-window terrain lens** (WH Cities corpus) needs two acceptance fixtures, not one (Tbilisi + a flat city) | WO1's single Tbilisi fixture is exactly how a Tbilisi-shaped (non-generalizing) instrument slipped through — it optimized for one query and nothing checked whether the design worked for a query unlike it. Both fixtures must pass at the *same* default knob settings, no per-city tuning, or the tolerance core isn't yet query-relative enough. From `wo1a_terrain-lens.md` Part D. |
| Terrain tolerance defaults locked: elevation ±500m, relief ±300m, landform-position ±0.10, `elev_weight`=1.0 | Each a **sub-one-std tolerance** on the corpus's own spread (elev std ≈698m, relief std ≈404m, position std ≈0.115) — defensible on its own terms, not fit to either fixture. (±300m elevation was tried first and excluded Yerevan, Tbilisi's best match, over a 474m gap; that's what prompted checking the std-relative basis rather than just widening until it cleared — Yerevan clearing at ±500m is confirmation, not the reason for the number. Opus's WO1a review, 2026-07-28: worth being precise about, since "widened until the motivating case cleared" is the same hazard the 400m gate itself was.) `elev_weight`=1.0 needed no adjustment — Yerevan still ranks respectably (6th) despite its elevation gap, confirming elevation informs without dominating. Both fixtures pass at these settings, no per-city tuning: Tbilisi 22/253 eligible (Yerevan #6), Bruges 35/253 eligible (Lübeck #7, a fellow flat Hanseatic port — an equally strong unprompted plausibility check). Detail: `wo1a_findings.md`. |
| **Standing rule** — any future change to **the point-window terrain lens** (WH Cities corpus) re-runs both fixtures (Tbilisi + Bruges) at shared defaults, no per-city tuning | Single-fixture validation is exactly how WO1's 400m gate slipped through. Opus's WO1a review promotes this from a one-time WO1a check to a standing guard on this lens going forward — the same way the second-seed stability check became standing after WO8b. Cheap to run, specifically targets re-de-generalizing the lens. From Opus's WO1a review, 2026-07-28. Distinct from **the basin-scale terrain lens**'s own two-fixture check below (WO3) — different corpus, different fixtures, same underlying discipline; disambiguated by name after Opus's WO3 review flagged both being called just "the terrain lens" as a real collision risk. |
| Point-window grid: drop individual points with elevation < 0 before computing relief stats | OpenTopoData's `mapzen` dataset returns real bathymetric depths (not null) for grid points landing in open water — confirmed on Willemstad (raw grid spanned -1249m to 67m). Affected 88/254 cities (35%); worst cases had relief_range inflated by >1000m and grid_elev_mean deeply negative. Fix costs a few real below-sea-level-land points too (Amsterdam-area polders, Baku) but those are shallow (0 to ~-30m) against contamination as severe as -1249m. One casualty: Aktau, Kazakhstan (2/25 points survive; confirmed by satellite view it's a peninsula genuinely mostly Caspian Sea within 10km — an honest gap, not a bug). Corpus-wide min `grid_elev_mean` went from -318m to +1.6m; 253/254 now resolve. Logic factored into `scripts/cdop/citykin/terrain_grid.py` (shared by the persist script, the notebook, and any future query-by-coordinate path). From `wo1a_findings.md`. |
| Small-corpus effect in eligible-set size: noted, not actioned | 22/253 (8.7%) and 35/253 (13.8%) eligible are both a much larger *fraction* than a comparably-tuned basin-level tolerance band would admit from the sandbox's ~16,397-basin index (two orders of magnitude larger) — structural, not a tuning error. Karl: "passes an initial smell test, we can proceed." Argues for presenting the retrieval head as ranked top-N with distances (existing `cdop_pilot` pattern) rather than leading with an "N eligible" count when wiring. From `wo1a_findings.md`. |
| Terrain knobs are tight/default/broad `<select>`s (auto-apply on change), not free-number-inputs + a button | Matches the sandbox conjunction panel's own knob convention exactly (`#v3-cj-corr` etc.) — Karl judged a raw-number version "mysterious" by comparison, having co-designed the sandbox pattern himself. Three levels per knob are round fractions of that facet's own corpus std: elevation 350/500/700 (σ≈696), relief 200/300/400 (σ≈404), position 0.05/0.10/0.15 (σ≈0.115) — the default level is the WO1a-locked, fixture-validated value in each case. 2026-07-28. |
| Landform-position knob: labeled "Landform position (±)" with a hover tooltip, not bare "Position (±)" | Karl forgot what "Position" meant despite having co-designed the facet — the bare label doesn't carry the floor/ridge meaning on its own. Tooltip (same `bootstrap.Tooltip` pattern already used for the Societies tab's variable-info icons): "0 = floor (surrounded by higher ground); 1 = ridge/peak (surrounded by lower ground)." 2026-07-28. |
| "Similar (semantic)" hidden (not disabled) when Tbilisi is selected | Tbilisi has no scraped Wikipedia summaries/embeddings, unlike the 254 true WH Cities — a dead control is worse than no control. Keyed on `city === 'Tbilisi'` in `whcSelectById`, same exception-by-name pattern already used to pin it atop the dropdown. 2026-07-28. |
| WO2's Terrain regime lens ships `ele_mt_sav` + `relief_range` as its two facets — `slp_dg_sav` does not replace `relief_range` | WO2a measured a real area confound in `relief_range` (partial corr with log-area, controlling for slope: 0.344 L06 / 0.320 L08 — weaker at L08, confirming area as the mechanism) and (WO2a's reading) high redundancy with slope (0.739 L06 / 0.809 L08, over the project's standing 0.70 Mahalanobis/drop bar) — by the WO's own decision rule, redundancy this high argues for preferring the area-invariant `slp_dg_sav`. **WO2b (Opus) corrected the redundancy reading**: `slp_dg_sav` isn't a shipping facet — the pair that actually ships correlates at 0.541 L06 / 0.566 L08, under the bar on its own terms, and the bar doesn't apply architecturally regardless (it corrects double-counting in a compensatory quadrature-sum distance; WO2's lens is a non-compensatory tolerance-band conjunction, where correlated facets cost selectivity, not distance integrity). Karl's decision stands on two independent grounds now: redundancy-threshold drop logic is a prediction-modeling import (collapse shared variance for model stability) inappropriate to EDOPS's description/characterization job, where the residual — a basin's relief relative to what its own slope predicts — is locally distinctive signal, not noise (same principle already locked for the signature itself); and, separately, the bright-line redundancy trigger for replacement doesn't survive contact with the correct pair of variables. The method was also inconsistent about applying the bar at all: WO1a kept two terrain facets at r=0.62 (under the bar) while WO2a's since-corrected 0.74–0.81 reading would have dropped one here. `wo2a_findings.md`, 2026-07-29 (updated same day per WO2b). |
| Kansas basin (hybas_id 7060622710) cited once, as a qualified keep-relief case, not a confound illustration | WO2a's first pass cited Kansas for two different conclusions from the same number. WO2b (Opus) placed it against both conditional expectations — relief expected given slope alone (206.9m) and given its own area+slope-quartile cell (382.9m) — and found a mixture: of its 435.1m excess over the slope-alone expectation, ~40% (176.0m) is attributable to its area quartile, ~60% (259.1m) is not explained by either slope or area. Cited once now, with the area contribution named rather than omitted. `wo2a_findings.md`, 2026-07-29. |
| Residual-facet design idea (relief regressed on slope, keep the residual) — named for WO2, not built | Would split `relief_range`'s slope-predictable component from its locally distinctive one explicitly, rather than leaving that signal buried in a correlated raw variable. WO2's two-facet floor doesn't require a third knob to satisfy WO2a's accept gate; adding one needs its own justification. Tension to weigh when taken up (Opus, WO2b): its value is corpus-relative (the zero point is a global-regression artifact, differing between L06/L08) while every other facet in this lens family is anchored query-relatively in physical units. Candidate for WO2's design conversation. `wo2a_findings.md` § Open, 2026-07-29. |
| WO3's terrain tolerance-band defaults are small absolute widths (elev ±25/50/100m, relief ±50/100/200m), derived empirically — NOT a round fraction of each facet's corpus std | The std-based recipe that worked for WO1a's point-window lens (a curated 254-city corpus) failed outright on the full L06 basin corpus: even a 0.5σ "tight" band admitted 24.5% of all basins on average, because elevation's std (775m) sits above its own IQR (617m) — a long right tail (max 5556m) inflates std well past the density where most basins actually live. Replaced by sweeping small absolute widths directly against the real `find_conjunction` code on a 16-basin sample stratified by elevation × relief quartile (table-sampled, not coordinate-picked): the locked defaults read 0.146/0.445/1.656% of the corpus matched at the median (tight/default/broad) — properly selective. Mean is pulled higher by low-elevation/low-relief queries (crowded lowlands, more global company there) — accepted as an honest characteristic, not squeezed away at the cost of selectivity for sparse mountain queries. `wo3_findings.md`, 2026-07-29. |
| **The basin-scale terrain lens**'s (WO3) two-fixture generalization check passed at the locked defaults, no per-fixture tuning | Rugged (Tbilisi's L06 basin, hybas_id 2060616700) and flat (hybas_id 6060269510, selected by area-quantile × relief-quantile from the table, not coordinate-picked) fixtures returned terrain-coherent, non-overlapping sets — elevation ranges separated by >1,400m. Distinct fixture pair from **the point-window terrain lens**'s Tbilisi + Bruges (above) — same city, different lens, different corpus, different actual query object (Tbilisi's L06 basin here vs. the 254-city WH Cities point-window record there); named explicitly to avoid the two being conflated. A real process trap surfaced and fixed along the way: a stale, already-imported copy of `seasonality.py` in the notebook's kernel silently ran the OLD placeholder defaults after the source file was edited — caught because the observed member ranges matched the old defaults' arithmetic exactly, not the new one. `wo3_findings.md`, 2026-07-29. |
| San Francisco's L06 basin is a long peninsula-ridge catchment, not a city footprint — confirmed live, not assumed | Karl flagged the basin extent as "odd" during browser smell-testing; confirmed via query values (`elev_m` 321.0, `relief_range_m` 1602.0 — downtown SF itself tops out ~280m) and the basin's actual geometry. Same mechanism as WO2a's Innsbruck case (HydroBASINS delineates by drainage topology, not local landscape), now demonstrated live on a real user query rather than only in a synthetic fixture — reinforces, doesn't change, the existing UI footnote's caveat. `wo3_findings.md`, 2026-07-29. |
| **RESOLVED, not by clearing the blocker — WO3's Terrain regime lens dissolved the DEM/data-acquisition question rather than answering it.** Was named Deferred (blocked on real data acquisition, not design): `note_to_opus_terrain-scale.md` argued the sandbox Similarity panel's Terrain regime needed the point-window method (to avoid container-effect smearing), which meant either a ~75min L06 batch job against a rate-limited public API or a locally-hosted DEM — impractical at L08 either way. | Opus's WO3 tracker review, 2026-07-29: that premise didn't hold. A **coarse** basin-scale lens doesn't need the point-window method at all — `ele_mt_sav`/`relief_range` are already-bulk-loaded BasinATLAS columns, the same free-SQL-reshape situation as precip/temp. The container-effect limitation this was built to avoid is disclosed honestly in the lens's own guide language instead (WO3's "describes the basin, not the place" footnote) rather than engineered around. The real DEM-acquisition question is **not moot** — it's still the path to a higher-fidelity, place-level facet (Tier-3, named not built) — but it no longer blocks *having* a Terrain regime option, which now exists. Postscript added to `note_to_opus_terrain-scale.md` rather than rewriting its historical record. |

---

## Deferred / out of scope

- **Enclosure / containment (Tier-2 terrain)** — the `ST_Touches` spatial-adjacency build. Trigger-gated,
  named in WO1 Part C, not built.
- **Local DEM (Tier-3 terrain)** — horizon, named, not built.
- **Soft-weighting elevation's tolerance-band edge** — WO1a's tolerance band already softened WO1's
  hard 400m gate considerably, but the band itself still has a hard edge. Not revisited this WO.
- **Water-fraction (`n_grid_land`/`n_grid_points`) — the first concrete crumb of the coastality lens**,
  not only a candidate fourth terrain-tolerance facet (Opus's WO1a review, sharpening Karl's original
  observation). Register entry: `docs/design/deferred_items_register.md` § CDOP — CITYKIN. Karl: "let
  it ride and see how it works out in queries" rather than adding scope now; would need its own
  correlation check first if ever promoted to a terrain facet. `wo1a_findings.md` § Open.
- **Non-compensatory conjunction head for CITYKIN** — stays in sandbox_v3 as the set-query instrument.
- **Additional lenses** (coastality, offshore topology, at-a-distance measures) — Karl's wishlist,
  demand-funded, named, not this WO. Coastality now has a real seed (the water-fraction row above) —
  not built, but no longer purely speculative.
- **The semantic (Wikipedia-text, section-sliced) similarity channel** — a separate capability on the
  same page, unaffected by this WO.
- **Any change to the Societies / TRACE surfaces.**
