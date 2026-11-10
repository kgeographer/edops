# Work order: reconcile docs and cheat sheet

Prepared 2026-10-27 from a read-through of `sandbox_cheatsheet.md` (verified against commit `b44aa01`, 2026-10-26) and `edops_docs_for_opus.md` (concatenation of `docsite/`).

## Purpose

Settle every inconsistency below before the dashboard-design experiments start, so that the rule-based summarizer is specified against one consistent description of the app.

## Instructions for CC

1. **Authority rule.** Code is authoritative for what the app does. Where the docs and code disagree, fix the docs. Where the cheat sheet and code disagree, fix the cheat sheet. Exceptions are marked "Decision (Karl)": do not resolve those, report what the code does and stop.
2. For each item: verify against the code (cite file and symbol), apply the fix named under **Action**, then tick **Status** and add a one-line note of what changed and where.
3. Do not fix app defects here. Defects belong in `main_changes_log.md`; if an item turns out to be a defect, log it there and mark the item "logged" here.
4. Append any new inconsistency you find at the end under "Found during this pass", using the same format.
5. When done, update the cheat sheet's "Last verified against commit" line.

## What this read-through did not cover

- Cheat sheet vs code (only cheat sheet vs docs was compared).
- The eight example JSON files other than `06_ring_topology_timbuktu_L6.json`.
- The variable catalog TSV vs the Codebook and cheat sheet counts.
  - **Done 2026-10-27 (CC):** the Codebook is generated from the catalog (`generate_codebook.py`). Regenerating to a temp file gave a byte-identical copy of `docsite/codebook.md` (102 variable rows = 102 catalog rows), and the per-band counts are computed in the generator (`:133-146`), so catalog and Codebook cannot disagree. Wording faults in the generator (the "implemented" footnote, the duplicate "Outlet type" title) are logged in `main_changes_log.md`. Cheat sheet counts vs catalog: item 11, cheat sheet 2.9.
- Docs screenshots (the concatenation has alt-text placeholders only).
- The cheat sheet's docs line citations (`reading-a-signature.md:32`, `:49`, `:54`); the concatenation does not preserve line numbers.
  - **Done 2026-10-27 (CC):** all three hold against `docsite/sandbox/reading-a-signature.md`. `:32` says the percentile is global and ranked at the resolution level queried (so the page does name the level); `:49` says the headline is the area-weighted mean of member-basin percentiles; `:54` is the stale p10/p90 badge rule. (`:49-50` also calls the histogram's flanking numbers p10 and p90, which is wrong: logged with the coherence-rule row.)

---

## A. Contradictions that bear on the dashboard design

### 1. Buffer and the other tabs — DECIDED
- **Docs:** `sandbox/overview.md` says a buffer "changes what 'the basin' means for every tab that follows." `project.md` lists basin ring among areal queries whose results are "returned as distributions."
- **Cheat sheet / code:** Analysis, Seasonality, Context and Similarity describe the containing basin for single, ring (centre or selected neighbour) and buffer scopes (§4.8, §6.1, §6.2). Ring has no set-level summary. `similarity.md` already says this correctly.
- **Karl's finding (2026-10-27):** The buffer's Signature heading reads "N basins, L06"; the other tabs' headings read "Containing basin for {place}". So the UI does report what is being shown, and the docs sentence is simply wrong: a buffer result never claims the signature is for one basin, only that the following tabs are.
- **Action (docs):** Reword the `overview.md` sentence to say that the Signature tab summarizes the buffer set while the other tabs describe the containing basin. In `project.md`, stop grouping basin ring with the aggregated areal queries.
- **Action (cheat sheet):** §4.7 item 9 says Analysis and Seasonality carry "no label saying so for a buffer." Per Karl they carry a "Containing basin for {place}" heading. Verify in code which tabs carry it (Analysis, Seasonality, Context, Similarity), then correct §4.7.9 and the note in §4.8.
- **Status:** [x] docs fixed (logged: 2 rows in `main_changes_log.md`, to apply on `main`)  [x] cheat sheet fixed (§4.7.9, §4.8). Note: the four tabs verified in `sandbox.html:_basinTitleHtml` callers; Atlas heading not checked.

### 2. What a dash means
- **Docs:** `sandbox/reading-a-signature.md`: a dash "does not mean zero"; for a single basin a dash means the variable "isn't coded" (karst, permafrost, wetland groups). For multi-basin it lists three meanings (bare dash with empty histogram, "score suppressed — bimodal", "outside active range").
- **Cheat sheet:** §2.6 lists five states plus `low_coverage`. For Timbuktu single basin, four rows are `outside_active_domain` (karst, permafrost, cropland and similar, i.e. about zero). §4.2 does not say how a single-basin `outside_active_domain` row renders.
- **Question:** What does the single-basin UI show for `outside_active_domain`? If it is a dash, the docs are wrong and a dash can mean "about zero."
- **Also:** the polity text "network measure, not meaningful for areas" (`not_areal`) is not in the docs; `no_data` vs `low_coverage` are indistinguishable on screen (cheat sheet §4.7.1).
- **Authority:** code.
- **Action:** Verify rendering per state and per scope (single, multi, polity); add the full state-to-display table to the cheat sheet §4.2 if it is not complete; rewrite the "When a value is missing" section of `reading-a-signature.md` to match.
- **Status:** [x] Answer: single-basin `outside_active_domain` renders "—" (so a dash can mean about zero); docs wrong. Cheat sheet §4.2 now has the full state-to-display table. Logged for `main`: UI row (state the cause, no bare dash), docs rewrite row, `low_coverage` note added to the status-vocabulary row.

### 3. Thresholds vs the "no thresholds" commitment — DECISION (Karl)
- **Docs:** `design/commitments.md`: "no thresholds encoding what counts as a meaningful difference"; where the interface applies a threshold, "the value is exposed as a control the user sets."
- **Cheat sheet:** fixed, non-adjustable thresholds exist in the UI and engine: concentrated/spread/split badge rules (core share ≥ 0.65, ±15-point window, split rule), `outside_active_domain` (zero fraction and weight-at-zero ≥ 0.90), Context blurb cutoffs (≤15/≥85 regional, ≤10/≥90 global, ≥25 difference), Seasonality sentence cutoffs, Analysis rules (1.5× exogenous, upstream area under 500 km² at L6 / 5,000 km² at L8 = Undetermined).
- **Action (CC):** produce a single table of every fixed interpretive threshold in `engine.py` and `sandbox.html` (value, location, what it governs, whether user-adjustable). Do not change the docs yet.
- **Decision (Karl):** soften the commitment wording, or expose or retire thresholds. This also governs what the rule-based prose layer may say.
- **Status:** [x] table produced (cheat sheet §9, 13 engine + 16 UI rows; no docs or code changed)  [x] decision recorded (Karl, 2026-10-27): soften the commitment; do not expose or retire thresholds. The prose layer may use the fixed rules, described as reading aids. Logged for `main` (commitments.md row).

### 4. The concentrated/spread badge rule and the histogram's flanking numbers
- **Docs:** `reading-a-signature.md`: "concentrated" if p10–p90 spans under 20 percentile points, otherwise "spread"; the two numbers flanking the histogram are p10 and p90; only two badges.
- **Cheat sheet:** §2.7: core share (largest share of weight in any ±15-point window) ≥ 0.65 is concentrated; "split" when one tied score holds ≥ 50% of weight and ≥ 10% sits outside the core window; otherwise spread; the 0.65 cutoff is provisional; the cheat sheet calls the flanking labels "low and high axis values." The docs' rule is noted as stale (§2.7, §7.2 #8).
- **Test case:** In a Band B screenshot, Pct Clay shows 18.6 and 51.5 as flanking numbers, a 33-point span, and carries the "concentrated" badge. If those numbers are p10 and p90, the docs rule would call it "spread."
- **Question:** What exactly are the flanking numbers (p10/p90, min/max, window edges)?
- **Authority:** code.
- **Action:** Identify the flanking values in `renderLeaf` / the histogram widget; rewrite the badge section of `reading-a-signature.md` (include "split"); record the threshold in the item 3 table. Note that the threshold design is itself an open problem (no cutoff works for all distributions); prose generation will depend on the outcome.
- **Status:** [x] Flanking numbers are min and max of member-basin percentiles (not p10/p90); the range bar uses p10/p90. Cheat sheet §4.2 and §2.7 corrected. Docs fix folded into the existing coherence-rule row in `main_changes_log.md` (also covers item 22). Threshold already in the §9 table.

---

## B. Docs vs cheat sheet, or docs vs docs

### 5. Example counts
- **Polities:** 6 (`sandbox/overview.md`, `walkthrough-polity.md`) vs 8 (cheat sheet §1.4).
- **Settlements:** `overview.md` says "four worked examples" then lists five; the walkthrough and cheat sheet say five.
- **Action:** count the examples in `sandbox.html`; fix whichever side is wrong.
- **Status:** [x] Code: 5 settlement examples, 8 polity examples. Cheat sheet right. Docs wrong at `overview.md:12` (four) and `:33` (six; Tang Dynasty not an option; Inca, Mali, Poland missing), logged for `main`. The `walkthrough-polity.md` "six" is Northern Song's slices, not examples: no error.

### 6. Coverage ranges for the temporal datasets
| Source | Docs | Cheat sheet / code |
|---|---|---|
| LMR | 1–2000 CE (`data-sources.md`); "1 CE" (`overview.md`) | 0–1998 CE in signature (engine clamp, API `from_year` limit); 700 CE floor in the map layer and the Polities "LMR data begins 700 CE" message |
| eVolv2k | 500 BCE–1900 CE (`data-sources.md`) | 491 BCE–1890 CE (`explorer/overview.md`, cheat sheet) |
| HYDE end year | 2023 CE (`data-sources.md`; cheat sheet §5.5 UI entry limit) | 2025 CE (`explorer/overview.md`, Codebook, cheat sheet §5.3) |
- **Action:** take the ranges from the data and engine constants; make `data-sources.md`, `overview.md` (the Qin "no LMR" note) and cheat sheet §5.5 agree, stating the signature range and the map-layer floor separately.
- **Status:** [x] Ranges from data/engine: LMR 0–1998 (arrays 2001), eVolv2k −491 to 1890, HYDE −10000 to 2025 (Karl: the table is the data). Cheat sheet was right; §5.5 and §5.3 clarified. Logged for `main`: docs ranges row; Band T year inputs cap at 2023 row.

### 7. HYDE cadence boundaries
- **Cheat sheet §5.3:** "every 100 yr 0–1700; every 10 yr 1700–1950; annual 1950–2025" (overlaps at 1700 and 1950).
- **Codebook:** centennial 0–1700, decadal 1710–1950, annual 1951–2025, millennial before 0. These boundaries sum to the 128 steps the cheat sheet cites.
- **Action:** align cheat sheet §5.3 to the Codebook boundaries after checking `temporal.hyde_times`.
- **Status:** [x] Checked `temporal.hyde_times`: 10 + 18 + 25 + 75 = 128 steps. Codebook right; cheat sheet §5.3 wording changed to non-overlapping ranges. Nothing for `main`.

### 8. LMR anomaly reference period
- **Docs:** Codebook Band C intro: "LMR anomalies relative to a 20th-century reference." `walkthrough-polity.md`: compared to "modeled norms for climatology for 850–1850."
- **Cheat sheet:** the map layer is "anomaly vs the cell's own 850–1850 CE mean."
- **Question:** are signature Band T rows (source anomalies) and the map layer (recomputed) different quantities? Which reference applies to each?
- **Action:** state the reference for each display in the cheat sheet §5.3/§6.4 and make the Codebook and walkthrough match.
- **Status:** [x] Settled by Tardif et al. 2019 s2.3: native reference = mean over the CCSM4 850-1850 CE simulation (not 20th century); signature rows show stored values, the map layer re-baselines to their 850-1850 mean. Measured offset: air avg -0.21 K (range -1.8 to +0.3), Timbuktu 1475-1525 table -0.17 vs map -0.02 K. Cheat sheet 5.3, 6.4, 7.3 updated. Logged for `main`: docs/comment reference-period row; possible 1-year offset in `lmr_values`.

### 9. BCE year convention
- **Docs:** `design/caveats.md`: HYDE and eVolv2k use astronomical year numbering (year 0 = 1 BCE, year -1 = 2 BCE).
- **Cheat sheet:** does not state the convention; examples use "300–200 BCE" and "-1000" without saying what a user types. The polity slider shows "750 BCE – 222 BCE"; the Signature heading shows raw negative years.
- **Question:** which convention do (a) the From/To inputs, (b) polity slice years, (c) the slider labels use? Are they consistent?
- **Action:** document the convention for each in the cheat sheet §5.5; flag any mismatch as a defect for `main_changes_log.md`.
- **Status:** [x] Signed years everywhere (negative = BCE); inputs and Band T payload pass through unchanged; labels use no-year-zero (`formatYear`); docs say astronomical for HYDE/eVolv2k: one-year disagreement, immaterial. Cliopatria numbering unverified. Cheat sheet 5.5 updated; one low-priority row logged for `main` (the polity heading was already logged).

### 10. "Render variable" count
- **Docs:** `walkthrough-polity.md`: "offers ten variables."
- **Cheat sheet §6.4:** table lists eleven (5 BasinATLAS + 2 LMR + 4 HYDE).
- **Action:** count the options in `BASIN_VARS` and the LMR/HYDE lists on the Polities tab; fix the wrong side. Check whether Settlements and Polities differ.
- **Status:** [x] Eleven options, one dropdown shared by both tabs (`sandbox.html:388`). Cheat sheet right (clarified §6.4); docs wrong (`walkthrough-polity.md:22`), logged for `main`.

### 11. What "implemented" means, and variable counts
- **Docs:** Codebook footnote: "[implemented]: Live in the current API and signature payload." Catalog implemented counts for A–E total 61 (A 9, B 14, C 26, D 7, E 5). `index.md` says "around 100 variables."
- **Cheat sheet:** 52 rows at L6 (A 8, B 18, C 15, D 8, E 3), with exclusions (`gdp_avg`, `human_dev_idx`, `river_area_upstream`, `strata_code`, `pnv_shares`) and local/upstream pairs counted as separate rows. Several "implemented" variables appear elsewhere (Seasonality, Analysis, Atlas) but not in the Signature tab.
- **Also:** the Codebook has two entries titled "Outlet type" (`endorheic` and `outlet_type`).
- **Action:** add a reconciliation table (catalog implemented → emitted in `/api/areas` → shown on Signature tab → shown elsewhere → not emitted) to the cheat sheet; reword the Codebook footnote and the "around 100" claim; retitle the duplicate "Outlet type" entry.
- **Status:** [x] Reconciliation table added (cheat sheet 2.9). Catalog 102 rows (74 implemented + 28 planned); A-E 61 implemented; 38 fully on the Signature tab, 1 partly, 17 public-API only, 5 in neither payload. Three docs rows logged for `main` (footnote, "around 100", duplicate "Outlet type"). UI use of eight variables not checked (listed in 2.9).

### 12. Band selection
- **Docs:** `design/commitments.md`: bands are parameters in signature requests in both the interface and the API.
- **Cheat sheet §2.1 / §7.2 #1:** the A–E checkboxes do not filter rows (known bug, `main` fix).
- **Action:** none for the docs unless the bug fix slips; add a note to the docs checklist to re-verify after the fix.
- **Status:** [x] logged (existing 2026-10-26 row, amended 2026-10-27: names the `commitments.md` sentence to re-verify after the fix). Karl: fix on `main` with the docs tweaks.

---

## C. Inside the cheat sheet

### 13. Which tabs the Polities page shows
- **Cheat sheet:** §0.1 says Analysis, Seasonality, Context and Similarity are hidden on Polities. §4 intro says Polities shows "the Signature tab only"; §7.1.4 says "Only the Signature tab and the map." The docs `walkthrough-polity.md` uses the Atlas tab on Polities.
- **Action:** read `_setPolitiesTabVisibility`; state the exact visible set once (expected: Map, Signature, Atlas) and make §0.1, §4, §6 and §7.1.4 agree.
- **Status:** [x] `_setPolitiesTabVisibility` hides Analysis, Seasonality, Context, Similarity; Polities shows Map, Signature, Atlas (Atlas global, stays per Karl). Cheat sheet 4 intro and 7.1.4 corrected; nothing for `main`.

### 14. Polity Band T span vs example 05
- **Cheat sheet §1.4:** on Polities the Band T span is the slice's own `fromyear`–`toyear`.
- **Example 05:** `from_year=961&to_year=1027`. The walkthrough has six slices, with the last at 1018–1027, so 961–1027 looks like the whole polity span, not one slice.
- **Action:** check how example 05 was captured and what the first slice's `toyear` is; correct the example's `_query` note or §1.4.
- **Status:** [x] Cheat sheet 1.4 right: Sandbox sends the slice's own years (Northern Song slice 1 is 961-961). Example 05 used the polity's whole span 961-1027; its `_note` (JSON and generator string) and the cheat sheet 8 row now say so. Generator script edited, not committed. Nothing for `main`.

### 15. Atlas totals
- **Cheat sheet §6.3:** L6 classes total 16,338 basins; L6 has 16,397.
- **Action:** identify the 59-basin gap (nodata or unclassified) and state it in §6.3.
- **Status:** [x] The 59-basin gap = basins with zero precipitation in all 12 months, dropped by `climate_classes.py:build_level` (`pre_total > 0`); `basin06` and the persist view both have 16,397. Cheat sheet 6.3 states it; map rendering of the 59 unchecked. One low-priority row logged for `main`.

---

## D. Minor wording

16. `sandbox/overview.md` calls the Seasonality chart a "histogram" (the cheat sheet describes precipitation bars plus a temperature line, a Walter-Lieth chart).
17. `sandbox/overview.md` says Context paints "the mean value of a chosen variable across that radius"; the cheat sheet says each basin is painted with its own value. Verify, fix whichever is wrong.
18. `walkthrough-settlement.md` says Similarity finds "most similar" basins; elsewhere it is a membership test, not a ranking.
19. `walkthrough-polity.md` says "climate modularity"; should be "modality."
20. `index.md`'s tab description lists six tabs and omits Atlas.
21. `design/commitments.md` refers to "seven instrument measures" without saying what the seven are.
22. The docs describe only two coherence badges; "split" is not mentioned (covered by item 4).

**Status for 16–22:** [x] 16 (docs loose: Walter-Lieth, not histogram), [x] 17 (docs wrong: each basin painted with its own value), [x] 18 (docs wrong: membership test, not ranking), [x] 19 (typo), [x] 20 (index.md omits Atlas), [x] 21 (phrase to be deleted; Karl: no idea what the seven are), [x] 22 (covered by item 4 row). All logged for `main` as 5 rows; cheat sheet already correct on all of them.

---

## Found during this pass

(CC: append new items here.)

- **(a) LMR baseline window in the project summary.** `documentation/EDOP_summary_v04.md:126` names 1000-1850 CE as the Band T LMR baseline "stated in API documentation"; the map uses 850-1850; signature rows use stored values (item 8). Not yet checked against `docsite/api.md`. Logged for `main`. Status: [x] logged

**Closing note (2026-10-27).** Items 1 to 22 closed; instruction 5 done (cheat sheet header now `7152eee`, with a change note). Docs fixes were logged, not applied, per Karl: see `main_changes_log.md` (35 rows).

**Closing note 2026-10-29: the "logged for `main`" items are applied.** v0.4.2 (tag at `a673660`, live 2026-10-29, merged into `dashboard` as `3156342`) applied the app, docs and code-comment rows from `main_changes_log.md`. Cheat sheet follow-up, item by item: 1 (buffer heading, §4.1), 2 (dash wording and `low_coverage`, §2.6, §4.2, §4.7), 4 (docs rule rewritten, notes in §2.7 and §7.2), 6 (year inputs to 2025, §5.5), 9 (polity heading BCE-aware, tooltip, `caveats.md`, §5.5), 12 (band checkboxes filter, §2.1) and 15 (59 basins now Arid, §6.3) changed the cheat sheet text; 3, 5, 7, 8, 10, 11, 13, 14 and 16 to 22 needed no change. Outside the 22 items, §7.2 (defects) and §5.5, §6.4, §6.6, §7.1, §7.4 were updated for the reversed-span 422, the HYDE map epoch rule, `/api/area` removal, the settled status vocabulary, the 404 for no-basin queries and the AWMC fallback basemap. Header re-stamped to v0.4.2; all 65 distinct `file:symbol` citations were checked to exist (line numbers not re-counted; the header says so). `edops_docs_for_opus.md` and the nine example files were regenerated; example 05 now returns only Band T rows because the band filter works.

Decisions still open (design questions, not defects): cheat sheet §7.2 items 11 to 13.
