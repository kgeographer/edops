# Dashboard pre-design: handoff to Opus

Draft of 15 Nov 2026, by Fable for Karl's review. Covers two sessions with Karl, 14 and 15 November. Read this first, then the files listed at the end. Where anything is unclear or seems to conflict, ask Karl.

Items are marked **[Karl]** where he decided or stated them, and **[proposed]** where Fable suggested them and Karl has not ruled.

## 1. The site

- **[Karl]** The site stays named EDOPS. The research program behind it (Environmental Dimensions of Place, within Computing Place) gets a line and a link; its background lives at computingplace.org and Karl's blog.
- **[Karl]** EDOPS is infrastructure: an aggregator of environmental data from global and regional sources, some of it time-indexed, delivering raw data for computation and serving as a source for downstream tools. The splash has to say that comprehensibly to newcomers.
- **[Karl]** Terms: a **signature** is the data, something to compute over. A **profile** is prose derived from it. The current splash treats them as synonyms. (The pre-design note says "summary" for the prose; read "profile".)
- **[Karl]** Three pages under the splash, names provisional: **Dashboard**, **Using EDOPS**, **Data Explorer**.

## 2. The splash

**[Karl]** A row above three tiles. The row holds two dropdowns of examples, one for settlements and one for polities. Choosing an example runs the query and opens the Dashboard with the result. Examples only to start; a typed lookup on the splash is a later detail.

```
+--------------------------------------------------------------+
| [logo]  EDOPS                         About | Documentation  |
|  What it is: two or three sentences.                         |
|  +--------------------------------------------------------+  |
|  | See a place                                            |  |
|  | Settlements: [ example  v ]    Polities: [ example  v ] |  |
|  +--------------------------------------------------------+  |
|  +--------------+  +--------------+  +--------------+        |
|  |  DASHBOARD   |  | USING EDOPS  |  | DATA EXPLORER|        |
|  +--------------+  +--------------+  +--------------+        |
|  A product of Computing Place (link)                         |
+--------------------------------------------------------------+
```

**[proposed]** Draw the settlement examples from the ten places whose profiles Karl has reviewed, and include the places the worked examples turn on (Chaco Canyon, Santa Fe, Lviv or Poltava). A Ukrainian example also shows GEDA.

## 3. The Dashboard

- **[Karl]** It starts as a clone of `sandbox.html` on the empty `/dashboard` page and is adjusted from there. The Sandbox stays untouched, live, and out of the navigation.
- **[Karl]** Order of use: choose a place, arrive with a **Profile** tab active and the other tabs filled. A left panel changes parameters, resets, and looks up a place in WHG. This is a configurator: result first, controls adjust it.
- **[Karl]** The Profile tab shows what the WHG profile work produces for settlements.
- **[Karl]** The Profile tab's first scope is a single basin at Level 06; otherwise one line says what it covers. Dummy text may stand in so navigation works while the Day 1 source of profiles is worked out with CC.
- **[Karl]** A polity lands on the Signature tab, as now, for the first build.
- **[Karl]** No rule-written interpretation of time-varying values. Time is shown, not narrated. The profile carries no Band T.
- **[Karl]** Sources are shown, not selected. Switching sources off goes to the roadmap file delivered with v1.
- **[Karl]** Long time spans need a caution at the year inputs.
- **[proposed]** A sources statement heads Band T: fixed sentences with slots, read from the `sources` block, saying which sources apply to this place and span and which do not.
- **[proposed]** The profile's sections link to the tabs that back them (Climate to Seasonality, Water to Analysis, Surroundings to Context).
- **[proposed]** A first view for polities, taken from the Workbench's areal-signature modal: the variables furthest from the world median, then "Show all variables". It needs one line per variable (not local and upstream both), friendly names, and the "largely absent" rule applied.
- **[proposed]** An Areas tab (type "Ukraine", get an area signature) goes on the roadmap; the Ukraine worked example may pull a first version forward if it needs a country-scale signature.

A configurator needs every control to behave one way (re-run, or mark the result out of date). The pre-design note has a table of what each control does today.

## 4. Using EDOPS

- **[Karl]** Four tabs: Societies and African Regions (existing Workbench panels), Ukraine and Pueblo (new). WH Cities and Ecoregions stay live and leave the navigation for v1.
- **[Karl]** Societies and African Regions need redesign and intro material (the question, the findings) to read as worked examples. A "Show me" step-through guide is a possibility; free exploration remains.
- **[Karl]** Ukraine tests claims from Snyder's lecture; Pueblo asks whether the move from Chaco to the Rio Grande is explained in part by the environmental evidence. How these tabs are presented is entirely open.
- **[proposed]** List the WHG endpoint here once live: the only use by an outside project.
- **[proposed]** Pueblo: Chaco and Santa Fe are about two degrees apart, so LMR's 2° grid may not separate origin from destination. A quick check of the cells is a loose item for CC. LBDA would give the contrast.

## 5. The profile store

`dash_wo01` (Fable's first work order) asked what Level 08 profiles would cost. CC did item 1 and part of item 2; items 3 (the generator's wording at Level 08) and 4 (how often the levels disagree) were not run. A second Fable agent then reviewed the question against the repo.

**Findings**

- As built, Level 08 would take about 93 days: an ecoregion query that costs 35 s per basin for want of an index on `hybas_id`, and a ring call that recomputes each signature six to seven times. With both fixed, about 3.5 to 4.2 days on the one-request-at-a-time path. Level 06: about 2 days as built, 13 hours with reuse.
- Second model: Level 06's fixed cost per signature is a full-table `PERCENT_RANK`; a `basin06_scores` table, like the existing `basin08_scores`, removes it. Level 08's signature cost is the missing index. A bulk build run in-process is estimated at 30 to 40 minutes for Level 06 and about a day for Level 08, mostly the ecoregion pass. Its figures are not verified by CC, and it saw Fable's design, so it is not independent.
- A stored profile cannot be a finished paragraph: Setting mixes place and basin facts, and one ecoregion sentence depends on the point.
- Request-time lookups are milliseconds, except the external point-elevation call at 0.40 to 0.45 s.
- The ring, pair and flow tables exist for about 310 test basins only.

**Three findings that reach beyond the Dashboard**

- Nothing in `app/` serves `/whgmodal`; only `/profiles` reads the stored JSON. The endpoint is the core of v1.
- River names rest on a table holding only the 122 rivers met in the samples.
- The generator hard-codes Level 06 in several files.

**Design [proposed]** (`profile-store-design-fable.md`, in the repo): never store finished text. Store facts per basin, one table per kind of fact and per source; assemble on request. Wording changes then cost no bulk run, and a new source adds one table.

**Karl's constraints [Karl]**

- No bulk generation before Ruth and Stephen respond to the sample profiles.
- Whatever is built must not have to be done twice, including when further sources are added.
- He does not believe days of compute are necessary for 190,675 basins.

**Pending.** CC is evaluating Fable's set-wise idea against the code. Whether Level 08 profiles are in v1 or on the roadmap is undecided; Fable's lean is roadmap, with the pipeline written to take a level.

## 6. Work orders

- **dash_wo01:** done in part, as above.
- **Next [Karl]:** an estimate of what permalink capability takes (the splash hands a place to the Dashboard by URL), then a build: the new splash, the clone, the Profile tab.
- **[proposed]** One gate for the build: choose Tbilisi on the splash, arrive on the Dashboard with the Profile tab showing and the other tabs filled.
- **Later [proposed]:** a work order on time (payload size against span length; every state of the `sources` block; which route Band T comes from); the polity first view; the Using EDOPS page.
- **Loose items for CC:** the LMR cells under the Chaco and Santa Fe basins; the areal modal's Band T header says "27 basins" where the Sandbox says "cells"; the modal prints the LMR caveat text, which the Sandbox never shows.

## 7. Open questions for Karl

1. Level 08 profiles: v1 or roadmap? And the Level 08 behaviour of the Profile tab once the cost is settled.
2. The use scenarios in the pre-design note: which stand?
3. Buffer scope: keep, demote or retire?
4. Band T headline value: mean, sum or distribution first?
5. The polity first view and the Areas tab: as proposed?
6. Where the Atlas lives.
7. The form of the Ukraine and Pueblo tabs, and whether "Show me" guides are worth the state-setting work.

## 8. Known inconsistencies in the documents

Karl is clearing these with CC: the v1 plan still names OWDA as the pilot (now GEDA); the published docs describe the Dashboard as a new tool that retires Sandbox and Workbench; docs and catalog say HYDE 3.4 where the data is 3.5.

## 9. Files

| File | What it is |
| --- | --- |
| `pre-design_notes_cc.md` | The brief Fable started from |
| `dash_predesign_note_01.md` | Fable's note of 14 Nov: inventory, three shapes, costs, questions. Superseded on two points: Karl chose the configurator (its shape C), and "summary" is now "profile" |
| `dash_wo01_summary-Level08.md`, `dash_wo01_summary.md`, `dash_wo01_results.md` | The work order, and CC's summary and results with the second model's review |
| `profile-store-design-fable.md` | The store design |
| `sandbox_cheatsheet.md`, `profile_templates.md`, `worked-examples-predesign.md`, `Snyder_premises.md` | Reference, as before |