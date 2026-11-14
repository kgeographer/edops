# Dashboard pre-design: brief for a new session

Draft of 2026-11-14. Opus's brief (`pre-design_notes_opus.md`) revised by Claude Code for Karl to review. The list of changes is at the end and comes out before use.

## How to use this brief

- Read this first, then the documents under "Read first". The list under "Files to have in the project" says what is available.
- You work from documents and from what Karl pastes. You have no access to the code repository. Where anything is unclear, missing or seems to conflict, **ask Karl**: he can supply detail, the Sandbox's history, screenshots and further files. Asking is better than guessing; much of what matters about the Sandbox is not written down.
- Ask one question at a time. Propose, then wait for Karl's answer before building on it.
- The first session's output is a pre-design note of options and questions, not decisions (see the last section).

## Where EDOPS stands (mid-November 2026)

- **EDOPS** (Environmental Dimensions of Place Service) is live at edops.computingplace.org as v0.4.2. It returns an environmental "signature" for a place: bands A–E (persistent environmental attributes, mostly from BasinATLAS at the scale of the containing L6 or L8 hydrological basin) and Band T (time-varying data for a chosen span: LMR climate reanalysis, HYDE land use, eVolv2k volcanic events, and now GEDA).
- **v1** is due for a meeting at Pitt (ISHI, Ruth Mostern's circle) in February 2027; its date is not yet set. The plan is `EDOPS v1 plan 09Nov.md`. After February, Karl steps back from development and others may take EDOPS on.
- **The WHG profile.** A prose profile of a place's environment, generated from its signature, for World Historical Gazetteer place pages. A sample profile page is deployed (eyes only) for review by Ruth Mostern and Stephen Gadd (WHG's current lead developer). Their feedback is awaited. Background: `whgmodal-README.md`, `wo10_sample-profile-page.md`, `profile_templates.md`.
- **Regionality is at an interim stop.** EDOPS now has a source registry (one place recording each data source's coverage, years, citation and licence), and GEDA, the first regional (non-global) dataset, is served on every public route. Each response carries a `sources` block saying which sources were used and which could not apply, with reasons. Still open and bearing on the display: on the public basin route LMR and HYDE still use older methods than the engine (LMR nearest cell, HYDE centroid rule), so one response can mix methods; every returnable variable needs a catalog entry (six payload names have none); the headline value of Band T rows (below). Background: `reg_wo05_summary.md`, `reg_wo06_summary02.md`.
- **Branches.** Nothing reaches `main` (the live site) until the v1 deploy; work happens on `v1` or branches cut from it. The Dashboard branch does not exist yet; it will be cut from `v1`. (An unlinked, noindex stub page exists at `/dashboard`; it is a placeholder, not a design.) Karl and Claude Code manage branches.
- **How work is organized.** Karl sets direction and writes final prose; Opus handles strategy, analysis and design; Claude Code (CC) implements, through work orders (goal-setting documents with provisos, one acceptance gate each). Karl reviews every write.
- **Data versions.** The stored land-use data is HYDE 3.5. The docs, the variable catalog and parts of the UI still say 3.4; read 3.4 as 3.5. (The docs get a full review before the v1 deploy.)

## The Dashboard question

Karl's framing, 2026-11-14: the "Dashboard" will be the existing **Sandbox reshaped, possibly with additions, and renamed**, not a new application. He is open to a different look or organization.

The site has three pages, and the Dashboard's relation to the other two is not settled:

- **Explorer** is a data viewer: it maps the raw data, and the results of exploratory and spatial analysis (EDA and ESDA), for all the source datasets. The regional dataset GEDA has not been added to it. Apart from that addition, Explorer will very likely remain intact as a site page.
- **Workbench** (D-PLACE societies, Isolates, Ecoregions, WH Cities; environment-culture correspondence testing) has elements that might be exposed in a different way.
- Karl is **not committed** to a Dashboard, Workbench and Explorer set that replaces the Sandbox, Workbench and Explorer one for one. The Dashboard might replace only the Sandbox, might act as a front door to all three, or might take pieces from Workbench. The first session should treat this as one of the open questions.

The cheat sheet describes the Sandbox only. For Workbench and Explorer, use `edops_docs_for_opus.md` (the Workbench and Explorer pages) and ask Karl.

What the Sandbox does today, in outline (the cheat sheet has the detail, with code citations):

- It has two tabs. **Settlements** and **Polities** each lead to a map and a signature.
- **Settlements:**
  1. **Choose a place:** a lookup of settlements and sites in World Historical Gazetteer gives a point (a pasted gazetteer identifier also works).
  2. **Set parameters:** scope (single basin, basin ring, buffer, and others), basin level, bands, a time span for Band T (with checks that the span can be honoured).
  3. **Get signature.**
  4. **View results:** on a map (choropleth, rivers, historical terrain basemap); on a page with accordions for each band; and in further analytical panels (including Analysis, Seasonality and Similarity).
- **Polities:** search for a Cliopatria polity, pick a year with a slice slider (with a play control), then the same map and signature.
- The Sandbox page itself has not changed since v0.4.2. It receives GEDA rows and does not draw them; its Band T badge counts them (cosmetic).

What is new to fit in:

- **The profile prose as a possible first view.** The engine that writes WHG profiles could give a plain summary on Get signature, before the raw numbers and graphs. The v1 plan already lists a "Summary panel at the top of the Signature tab" as a Should item (20–30 hours).
- **Rule-derived statements, and a possible prose layer.** A completed study (WO-02, `wo02_summary.md`) derived 54 types of true statement from one `/api/areas` payload by rule. Karl's plan for any prose layer: an LLM writes over those rule statements (via the API, bring-your-own-key for v1), caveats forced into the text by the rules, wording from Karl's own glossary. Findings that shape this: 18 of the 54 statements need per-variable knowledge the payload lacks (a friendly-name crosswalk is a work order not yet written); wording that needs a cutoff flips under sweeps, so most fall back to stating the number alone.
- **GEDA in the display** (see decisions below).
- **A sources view.** Possibly a modal listing all data sources, all consulted by default, with the option to choose only some. The engine already supports a permitted-sources option; nothing passes it yet.
- **Worked examples** (Ukraine from Timothy Snyder's lecture; Southwest US, Chaco to the Rio Grande) are planned for February. They show how a researcher reasons from what evidence exists for a place and period: premises sorted by how persistent the environmental feature is, with the evidence for each. How the Dashboard supports them is open. See `worked-examples-predesign.md` and `Snyder_premises.md`. One data-quality point matters to them: LMR is least reliable before about 700 CE; Karl's decision is that the worked examples expose this rather than hide it, and the app does not change (`lmr_quality_border.md`). Whether the examples restrict LMR to 700 CE onward is open: signatures themselves set no such limit (they return LMR from 0 CE with a fidelity note before 700); only the Sandbox map layer starts at 700.

## Constraints

- Karl's bandwidth and motivation are limited; scope accordingly. February is a pilot, not a finished product.
- What is owed to Pitt: a dashboard that makes the use of signatures evident, with a few worked examples.
- Keep visualization types consistent with what the Sandbox already uses where possible.
- Front end and back end are designed together: display needs can change the payload, and the reverse.
- No schedule pressure at present. Karl is away 22–30 November (Nepal), works briefly in early December, then from 29 December to early February.

## Decisions already made that bear on display

- GEDA is shown like LMR: the same panel type (histogram of cell values with a year slider, a small line with its p10–p90 band), in its own block, never on a shared axis with LMR. Each block is fully labelled: product, season, grain, units. HYDE's display is not being touched.
- GEDA values are standard scores (how unusual a summer was for that place, relative to 1000–2020), not Palmer drought categories; wording must say so.
- The observed years (1990–2020) are shaded differently from the p10–p90 band, with a legend or tooltip naming both.
- Notes appear when a basin is only partly covered (`low_coverage`) or has few cells (`low_resolution`); no new chart types for these.
- GEDA and LMR disagree over Ukraine; where both appear, the UI explains that they are independent reconstructions, not a conflict to resolve.
- Two payloads exist: the full signature (Get signature) and the curated WHG profile. The profile is precomputed and does not include Band T in v1.
- GEDA covers Eurasia only, 1000–2020 CE. Outside that, the payload says so (`sources.not_applied`, with a reason) rather than staying silent about it.

## Open questions already known

- **The headline value** for Band T rows: LMR and GEDA lead with a weighted mean, HYDE with a sum (an area, not a score), multi-basin BasinATLAS rows with a percentile. Should the display lead with the distribution instead? This would change several panels together.
- What the first view after Get signature should be: the profile, the band accordions, a map, or a combination.
- Where the sources view lives, and which sources a user may turn off (BasinATLAS underlies bands A–E, so probably not that one).
- Whether to show buffer and polity scopes prominently, given that most real use is a single place.
- Whether the Sandbox keeps a separate life or the Dashboard replaces it outright (undecided).
- How the Dashboard relates to Explorer and Workbench: replace the Sandbox only, front the whole site, or draw in Workbench pieces (undecided).

## Read first

1. `EDOPS v1 plan 09Nov.md`: scope, contract lines, schedule.
2. `sandbox_cheatsheet.md`: what the Sandbox does, with code citations. Long; use it as a reference, starting with its contents.
3. `whgmodal-README.md` and `wo10_sample-profile-page.md`: the profile. Then `profile_templates.md`.
4. `reg_wo05_summary.md` and `reg_wo06_summary02.md`: the current state of the data and payload.
5. `wo02_summary.md`: the statement inventory.
6. The three `wo02_item*.png` figures: how GEDA looks for a basin (distribution, lines, against LMR).
7. `worked-examples-predesign.md`, then `Snyder_premises.md`.
8. `edops_docs_for_opus.md`: the published documentation, for general background.

## Files to have in the project

Paths are in the repository. Where the upload name differs, use the name in the first column so the brief's references work. Tick them off as they go up.

**A. Needed**

| Upload as | Repository path |
|---|---|
| `pre-design_notes_cc.md` (this brief, final form) | `docs/edop/_v1/dashboard/` |
| `EDOPS v1 plan 09Nov.md` | `docs/design/dashboard/` |
| `sandbox_cheatsheet.md` | `docs/design/dashboard/` |
| `whgmodal-README.md` (rename from `README.md`) | `docs/edop/_v1/whgmodal/README.md` |
| `wo10_sample-profile-page.md` | `docs/edop/_v1/whgmodal/` |
| `profile_templates.md` | `docs/design/dashboard/` |
| `reg_wo05_summary.md` | `docs/edop/_v1/regionality/` |
| `reg_wo06_summary02.md` | `docs/edop/_v1/regionality/` |
| `wo02_summary.md` | `docs/design/dashboard/` |
| `wo02_item6_distribution.png`, `wo02_item7_8_lines.png`, `wo02_item11_geda_vs_lmr.png` | `output/edop/regionality/` |
| `worked-examples-predesign.md` | `docs/edop/_v1/rubrics/` |
| `Snyder_premises.md` | `docs/edop/_v1/rubrics/` |

**B. Useful**

| Upload as | Repository path |
|---|---|
| `edops_docs_for_opus.md` (regenerate first: it predates the GEDA docs) | `docs/design/dashboard/` |
| `lmr_quality_border.md` | `docs/edop/_v1/rubrics/` |
| `how_edops_works.md` (check it first: it still lists GEDA as planned) | `docs/design/dashboard/` |
| `wo02_results.md` | `docs/design/dashboard/` |
| `deferred_items_register.md` | `docs/design/` |
| `01_single_basin_timbuktu_L6.json` and `04_band_t_timbuktu_1475_1525.json` (payload shape) | `docs/design/dashboard/examples/` |
| Sandbox screenshots | from Karl |

**C. Leave out**

`SESSION_SEED.md` (defunct), `pre-design_notes_opus.md` (replaced by this file), `Snyder_Ukraine.md` (99 KB lecture transcript; the premises file is its digest), `EDOPS v1 plan 31Oct.md`, `v1_workplan_05Nov.md`, `edops_docs_for_opus.pdf`, `main_changes_log.md`, all `whgmodal/wo07`–`wo10a` records, `wo01`–`wo06` files in `docs/design/dashboard/`, `modal_dummy*.md`, `whg-profile_questions.md`, `whg_ring_profile_spec_prelim.md` (preliminary; Karl to revisit), all other `reg_wo*` files, example payload 07 (stale).

## What the first session should produce

A pre-design note, options and questions rather than decisions:

- An inventory of the Sandbox as it is (from Karl and the cheat sheet): what each part does and whether it stays, changes or goes.
- Two or three possible shapes for the Dashboard, each sketched in words (or simple wireframes): the first view, the order of things, where the new pieces fit.
- For each shape: what it needs from the payload, and what it costs roughly.
- The questions Karl needs to answer to choose.

---

## Changes from the Opus draft (delete this section before use)

1. Regionality is an interim stop, not closed; the open items that touch display are named.
2. The Sandbox outline now covers both tabs and the Sandbox page's current state (unchanged, ignores GEDA rows).
3. Branches: the Dashboard branch is not yet cut; the `/dashboard` stub is mentioned.
4. Added that the reader has no repository access, and the way of asking (one question at a time, propose then wait).
5. HYDE 3.4 vs 3.5 note.
6. Added the WO-02 statement inventory and Karl's prose-layer plan to "What is new".
7. Added the LMR 700 CE data-quality border (decided 2026-11-11) with the worked examples.
8. Added a decision on GEDA outside its footprint and span, and "HYDE's display is not being touched".
9. Added the open questions whether the Sandbox survives alongside the Dashboard, and how the Dashboard relates to Explorer and Workbench (Karl, 2026-11-14: not tied to a one-for-one replacement; Explorer is a data viewer likely to stay; Workbench has pieces that might be exposed differently). The cheat sheet is noted as Sandbox-only.
10. "Read first" now names files (the cheat sheet moved from "ask Karl" to the list; the vague "project memory" item is dropped, since the repository's memory is not part of the project).
11. New "Files to have in the project" section with tiers and upload names. The two worked-example files are in the repository (`docs/edop/_v1/rubrics/`), not outside it, and the filenames in the Opus draft were wrong (`worked-examples-predesign.md`, with hyphens; `Snyder_premises.md`).
12. Removed the empty last bullet.

Two things to settle before use:
- `worked-examples-predesign.md` says "LMR from 700 CE, everywhere" as the coverage rule. `lmr_quality_border.md` says the examples pull LMR from 0 CE and also run a version from 700. Karl: whether to restrict to 700 is an open question (signatures set no such limit). The brief states it as open.
- `Snyder_premises.md` refers to the other file as `worked_examples_predesign.md` (underscores). Harmless, but fix it if the files go up together.
