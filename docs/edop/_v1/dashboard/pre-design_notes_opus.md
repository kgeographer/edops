# Dashboard pre-design: brief for a new session

Draft of 2026-11-14, by Opus for Karl to review and extend. Written to start a new chat in the CEDOP project with enough context to work from the first message.

## How to use this brief

- Read this first, then the documents listed under "Read first".
- Where anything is unclear, missing or seems to conflict, **ask Karl**. He can supply detail, background on the Sandbox's history, screenshots and further files. Asking is better than guessing; much of what matters about the Sandbox is not written down in the project.
- The first session's output is a pre-design note of options and questions, not decisions (see the last section).

## Where EDOPS stands (mid-November 2026)

- **EDOPS** (Environmental Dimensions of Place Service) is live at edops.computingplace.org as v0.4.2. It returns an environmental "signature" for a place: bands A–E (persistent environmental attributes, mostly from BasinATLAS at the scale of the containing L6 or L8 hydrological basin) and Band T (time-varying data for a chosen span: LMR climate reanalysis, HYDE land use, eVolv2k volcanic events, and now GEDA).
- **v1** is due for a meeting at Pitt (ISHI, Ruth Mostern's circle) in February 2027; its date is not yet set. The plan is `EDOPS v1 plan 09Nov.md`. After February, Karl steps back from development and others may take EDOPS on.
- **The WHG profile.** A prose profile of a place's environment, generated from its signature, for World Historical Gazetteer place pages. A sample profile page is deployed (eyes only) for review by Ruth Mostern and Stephen Gadd (WHG's current lead developer). Their feedback is awaited. Background: the `whgmodal/` folder, especially `wo10_sample-profile-page.md` and `README.md`; `profile_templates.md`.
- **Regionality is closed.** EDOPS now has a source registry (one place recording each data source's coverage, years, citation and licence), and GEDA, the first regional (non-global) dataset, is served on every public route. Each response carries a `sources` block saying which sources were used and which could not apply, with reasons. Background: the `reg_wo*` summaries, `reg_wo05_summary.md` and `reg_wo06_summary02.md` above all.
- **Branches.** Nothing reaches `main` (the live site) until the v1 deploy; work happens on `v1` or branches from it. Karl and Claude Code manage branches.
- **How work is organized.** Karl sets direction and writes final prose; Opus (this role) handles strategy, analysis and design; Claude Code (CC) implements, through work orders (goal-setting documents with provisos, one acceptance gate each). Karl reviews every write. See the project memory file on ways of working.

## The Dashboard question

Karl's framing, 2026-11-14: the "Dashboard" will be the existing **Sandbox reshaped, possibly with additions, and renamed**, not a new application. He is open to a different look or organization.

What the Sandbox does today, in outline (Karl can fill in the detail):

1. **Choose a place:** a lookup of settlements and sites in World Historical Gazetteer gives a point.
2. **Set parameters:** scope (single basin, buffer, polity from Cliopatria, and others), basin level, bands, a time span for Band T (with checks that the span can be honoured).
3. **Get signature.**
4. **View results:** on a map; on a page with accordions for each band; and in further analytical panels (including Analysis and Seasonality tabs).

What is new to fit in:

- **The profile prose as a possible first view.** The engine that writes WHG profiles could give a plain summary on Get signature, before the raw numbers and graphs. The v1 plan already lists a "Summary panel at the top of the Signature tab" as a Should item (20–30 hours).
- **GEDA in the display.** GEDA rows are returned but the Sandbox does not draw them yet; the Band T badge counts them, though (cosmetic).
- **A sources view.** Possibly a modal listing all data sources, all consulted by default, with the option to choose only some. The engine already supports a permitted-sources option; nothing passes it yet.
- **Worked examples** (Ukraine from Timothy Snyder's lecture; Southwest US, Chaco to the Rio Grande) are planned for February. They show how a researcher reasons from what evidence exists for a place and period. How the Dashboard supports them is open. Notes exist outside the project (`worked_examples_predesign.md`, `snyder_premises.md`); ask Karl for them if needed.

## Constraints

- Karl's bandwidth and motivation are limited; scope accordingly. February is a pilot, not a finished product.
- What is owed to Pitt: a dashboard that makes the use of signatures evident, with a few worked examples.
- Keep visualization types consistent with what the Sandbox already uses where possible.
- Front end and back end are designed together: display needs can change the payload, and the reverse.
- No schedule pressure at present. Karl is away 22–30 November (Nepal), works briefly in early December, then from 29 December to early February.

## Decisions already made that bear on display

- GEDA is shown like LMR: the same panel type (histogram of cell values with a year slider, a small line with its p10–p90 band), in its own block, never on a shared axis with LMR. Each block is fully labelled: product, season, grain, units.
- GEDA values are standard scores (how unusual a summer was for that place, relative to 1000–2020), not Palmer drought categories; wording must say so.
- The observed years (1990–2020) are shaded differently from the p10–p90 band, with a legend or tooltip naming both.
- Notes appear when a basin is only partly covered (`low_coverage`) or has few cells (`low_resolution`); no new chart types for these.
- GEDA and LMR disagree over Ukraine; where both appear, the UI explains that they are independent reconstructions, not a conflict to resolve.
- Two payloads exist: the full signature (Get signature) and the curated WHG profile. The profile is precomputed and does not include Band T in v1.

## Open questions already known

- **The headline value** for Band T rows: LMR and GEDA lead with a weighted mean, HYDE with a sum, multi-basin BasinATLAS rows with a percentile. Should the display lead with the distribution instead? This would change several panels together.
- What the first view after Get signature should be: the profile, the band accordions, a map, or a combination.
- Where the sources view lives, and which sources a user may turn off (BasinATLAS underlies bands A–E, so probably not that one).
- Whether to show buffer and polity scopes prominently, given that most real use is a single place.

## Read first

1. `EDOPS v1 plan 09Nov.md`: scope, contract lines, schedule.
2. `whgmodal/README.md` and `whgmodal/wo10_sample-profile-page.md`: the profile.
3. `profile_templates.md`.
4. `reg_wo05_summary.md` and `reg_wo06_summary02.md`: the current state of the data and payload.
5. The three `wo02_*.png` figures: how GEDA looks for a basin (distribution, lines, against LMR).
6. `edops_docs_for_opus.md`: general background.
7. Project memory: overview, decisions and principles, ways of working.

**Ask Karl for,** as needed: the Sandbox cheat sheet (`docs/design/dashboard/sandbox_cheatsheet.md` in the repo); screenshots of the current Sandbox; the deferred items register; the worked-example notes.

## What the first session should produce

A pre-design note, options and questions rather than decisions:

- An inventory of the Sandbox as it is (from Karl and the cheat sheet): what each part does and whether it stays, changes or goes.
- Two or three possible shapes for the Dashboard, each sketched in words (or simple wireframes): the first view, the order of things, where the new pieces fit.
- For each shape: what it needs from the payload, and what it costs roughly.
- The questions Karl needs to answer to choose.
- 