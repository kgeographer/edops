# Dashboard pre-design: brief for a new session

Draft of 2026-11-14. Opus's brief (`pre-design_notes_opus.md`) revised by Claude Code for my review. This project is team-built to date, with me leading, Opus in design and conceptual discussions and drafting work orders (WOs), and Claude Code (CC) executing in step with me in PyCharm. I am consulting Fable for this pre-design work and will return to Opus in a few days.

## How to use this brief

- Read this first, then the documents under "Read first". The section "Files in the desktop project under _xfer/" lists what is available.

- You work from documents and from what I paste. You have no access to the code repository. Where anything is unclear, missing or seems to conflict, **ask me**: I can supply detail, the Sandbox's history, screenshots and further files. Asking is better than guessing; much of what matters about the Sandbox is not written down.

- Ask one question at a time. Propose, then wait for my answer before building on it.

- The first session's output is a pre-design note of options and questions, not decisions (see the last section).

## Where EDOPS stands (14 November 2026)

- **EDOPS** (Environmental Dimensions of Place Service) is live at edops.computingplace.org as v0.4.2. In its Sandbox page it returns an environmental "signature" for a place (settlements, polities): bands A–E (persistent environmental attributes, mostly from BasinATLAS at the scale of the containing L6 or L8 hydrological basin) and Band T (time-varying data for a chosen span: LMR climate reanalysis, HYDE land use, eVolv2k volcanic events, and now Great Eurasian Drought Atlas (GEDA)). 

- **v1** is due for a meeting at Pitt (ISHI, Ruth Mostern's circle) in mid-February 2027; its date is not yet set. The plan is `EDOPS v1 plan 09Nov.md`. After February, I step back from development and others may take EDOPS on.

- **The WHG profile.** A prose profile of a place's environment, generated from its signature, for World Historical Gazetteer place pages. A sample profile page is deployed (eyes only) for review by Ruth Mostern and Stephen Gadd (WHG's current lead developer). Their feedback is awaited. Background: `whgmodal-README.md`, `wo10_sample-profile-page.md`, `profile_templates.md`. The plan is to generate persisted profiles for all 16k Level 06 basins.

- **Regionality is at an interim stop.** EDOPS now has a source registry (YAML recording each data source's coverage, years, citation and licence), and GEDA, the first regional (non-global) dataset, is served on every public route. Each response carries a `sources` block saying which sources were used and which could not apply, with reasons. Still open and bearing on the display: on the public basin route LMR and HYDE still use older methods than the engine (LMR nearest cell, HYDE centroid rule), so one response can mix methods; every returnable variable needs a catalog entry (six payload names have none); the headline value of Band T rows (below). Background: `reg_wo05_summary.md`, `reg_wo06_summary02.md`.

- **Branches.** Nothing reaches `main` (the live site) until the v1 deploy; work happens on `v1` or branches cut from it. The Dashboard branch does not exist yet; it will be cut from `v1`. (An unlinked, noindex stub page exists at `/dashboard`; it is a placeholder, not a design.) Claude Code and I manage branches.

- **How work is organized.** I set direction and write final prose; Opus (and now Fable for a while) handles strategy, analysis and design; Claude Code (CC) implements, through work orders (goal-setting documents with provisos, one acceptance gate each). I review every write.

- **Data versions.** The stored land-use data is HYDE 3.5. The docs, the variable catalog and parts of the UI still say 3.4; read 3.4 as 3.5. (The docs get a full review before the v1 deploy.)

## The Dashboard question

My framing, 2026-11-14: the "Dashboard" will be the existing **Sandbox reshaped, possibly with additions, and renamed**, not a new application. I am open to different components, look, and organization.

The site has three pages, and the Dashboard's relation to the other two is not settled:

- **Explorer** is a data viewer: it maps the raw data, and the results of exploratory and spatial analysis (EDA and ESDA), for all the source datasets. The regional dataset GEDA has not been added to it. Apart from that addition, Explorer will very likely remain intact as a site page.

- **Workbench** (D-PLACE societies, Isolates, Ecoregions, WH Cities; environment-culture correspondence testing) has elements that might be exposed in a different way.

- I am **not committed** to a Dashboard, Workbench and Explorer set that replaces the Sandbox, Workbench and Explorer one for one. The Dashboard might replace only the Sandbox, might act as a front door to all three, or might take pieces from Workbench. The first session should treat this as one of the open questions.

The cheat sheet describes the Sandbox only. For Workbench and Explorer, use `edops_docs_for_opus.md` (the Workbench and Explorer pages) and ask me.

What the Sandbox does today, in outline (the cheat sheet has the detail, with code citations):

- It has two tabs. **Settlements** and **Polities** each lead to a map and a signature.

- **Settlements:**

  1. **Choose a place:** a lookup of settlements and sites in World Historical Gazetteer gives a point (a pasted gazetteer identifier also works).

  2. **Set parameters:** scope (single basin, basin ring, buffer, and others), basin level, bands, a time span for Band T (with checks that the span can be honoured).

  3. **Get signature.**

  4. **View results:** on a map (choropleth, rivers, historical terrain basemap); on a page with accordions for each band; and in further analytical panels (including Analysis, Seasonality and Similarity).

- **Polities:** search for a Cliopatria polity, pick a year with a slice slider (with a play control), then the same map and signature.

- The Sandbox page itself has not changed since v0.4.2. It now receives GEDA rows but does not yet draw them; its Band T badge counts them (cosmetic).

What is new to fit in:

- **The profile prose as a possible first view.** The engine that writes WHG profiles could give a plain summary on Get signature, before the raw numbers and graphs. The v1 plan already lists a "Summary panel at the top of the Signature tab" as a Should item (20–30 hours).

- **A possible LLM-generated prose layer.** i.e. an LLM either summarizes the 16k Level 06 pre-generated profile statements, or uses the rules system used to generate profiles

- **GEDA in the display** (see decisions below).

- **A sources view.** Possibly a modal listing all data sources, all consulted by default, with the option to choose only some. The engine already supports a permitted-sources option; nothing passes it yet.

- **Worked examples** (Ukraine’s extraordinary environment, from Timothy Snyder's lecture; Southwest US, Pueblo migration from Chaco to the Rio Grande) are planned for February. They would show how a researcher reasons from what evidence exists for a place and period: premises sorted by how persistent the environmental feature is, with the evidence for each. How the Dashboard supports them is open. See `worked-examples-predesign.md` and `Snyder_premises.md`. One data-quality point matters to them: LMR is least reliable before about 700 CE; my decision is that the worked examples expose this rather than hide it, and the app does not change (`lmr_quality_border.md`). Whether the examples restrict LMR to 700 CE onward is open: signatures themselves set no such limit (they return LMR from 0 CE with a fidelity note before 700); only the Sandbox map layer starts at 700.

## Constraints

- My bandwidth and motivation are limited; scope accordingly. February is a pilot, not a finished product.

- What is owed to Pitt: a dashboard that makes the use of signatures evident, with a few worked examples.

- Keep visualization types consistent with what the Sandbox already uses where possible.

- Front end and back end are designed together: display needs can change the payload, and the reverse.

- No schedule pressure at present. I am away 22–30 November (Nepal), work briefly in early December, then from 29 December to early February.

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

## Files in the desktop project under _xfer/

The files are in a folder called `_xfer/` in the project, with a subfolder per phase (`dashboard/`, `whgmodal/`, `regionality/`, `rubrics/`). They are copies of files from the repository, gathered there so that file names do not clash. The references in this brief use the bare file name; find it in the subfolder shown. If something listed is missing, or you need a file not listed, ask me.

**A. Needed**

| File | Subfolder of _xfer/ |
| - | - |
| `pre-design_notes_cc.md` (this brief, final form) | `dashboard/` |
| `EDOPS v1 plan 09Nov.md` | `dashboard/` |
| `sandbox_cheatsheet.md` | `dashboard/` |
| `whgmodal-README.md` | `whgmodal/` |
| `wo10_sample-profile-page.md` | `whgmodal/` |
| `profile_templates.md` | `dashboard/` |
| `reg_wo05_summary.md` | `regionality/` |
| `reg_wo06_summary02.md` | `regionality/` |
| `wo02_summary.md` | `dashboard/` |
| `wo02_item6_distribution.png`, `wo02_item7_8_lines.png`, `wo02_item11_geda_vs_lmr.png` | `regionality/` |
| `worked-examples-predesign.md` | `rubrics/` |
| `Snyder_premises.md` | `rubrics/` |


**B. Useful**

| File | Subfolder of _xfer/ |
| - | - |
| `edops_docs_for_opus.md` | `dashboard/` |
| `lmr_quality_border.md` | `rubrics/` |
| `how_edops_works.md` | `dashboard/` |
| `wo02_results.md` | `dashboard/` |
| `deferred_items_register.md` | `_xfer/` itself (no subfolder) |
| `01_single_basin_timbuktu_L6.json` and `04_band_t_timbuktu_1475_1525.json` (payload shape) | `dashboard/` |
| Sandbox screenshots | from me as needed |


## What the first session should produce

A pre-design note, options and questions rather than decisions:

- An inventory of the Sandbox as it is (from me and the cheat sheet): what each part does and whether it stays, changes or goes.

- Two or three possible shapes for the Dashboard, each sketched in words (or simple wireframes): the first view, the order of things, where the new pieces fit.

- For each shape: what it needs from the payload, and what it costs roughly.

- The questions I need to answer to choose.

