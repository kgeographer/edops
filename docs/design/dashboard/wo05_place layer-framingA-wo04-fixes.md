# WO-05: the place layer, framing A, and the WO-04 fixes

Draft 2026-11-05, for Karl's review. Goal-setting, not a specification. Part of the two-week plan for the sample page (`sample_page_plan.md`); target finish Tuesday 10 November.

## Goal

Make the generator speak in framing A, which Karl has chosen: the Setting section speaks about the place itself; the other sections name the basin they describe. `profile_templates.md` version 2 (written by Opus) is the target wording. It introduces new units and phrases the generator does not yet supply, so it will not run until this WO is done. At the end, the ten filled_profiles regenerate from version 2 with the place layer real, the WO-04 fixes made, and two costs measured for January.

## Background to read first

`profile_templates.md` (v2, and its Changes line), `sample_page_plan.md` (the framing options and the Setting section), `wo04_summary.md` and `wo04c_results.md` (issues 1 to 9).

## 1. The place layer

- **S1.1b, elevation at the point.** Two possible sources: a DEM sampled at the point by EDOPS, or WHG's own value, which its place pages already show. For the sample page, sample a DEM in EDOPS. Say which DEM and resolution are available locally. Whether WHG supplies elevation in the endpoint is a later decision; note what each route would need.
- **S1.2a, the point's ecoregion.** A point-in-polygon lookup. Report how often it differs from the basin's majority (WO-03 found about 6% of sample basins).
- **S1.2c, the basin's majority ecoregion, when it differs.** Uses the existing lookup; the phrase appears only when the two differ. Timbuktu should show it.
- **S1.5a and S1.5b, the basin's elevation range.** From `elev_min` and `elev_max`. If the basin's mean elevation is loaded, report it; it is not in the template yet.
- **The point ecoregion for no-basin points.** The point-in-polygon lookup does not need a basin. If Tristan da Cunha falls inside an ecoregion polygon, say so; whether the no-basin profile names it is a later decision.

## 2. Water wording for all five classes

`profile_templates.md` v2 gives a phrase for each class of the Analysis tab's rule (exogenous, uniform, local, coastal, and an empty one for endorheic). The four new ones are drafts. Check each against the rule's definition of its class and its cutoffs. Report where a phrase claims more than the class means (for example "with much the same climate" for uniform, "most of the water falls locally" for local), and propose a correction in the same plain style. The phrase for a basin whose distance to the sea is 0 (`S3.5.sea_zero`) replaces "about 0 km".

## 3. Fixes from WO-04

- **Readable names in S8.2.** Replace internal field names (`wet_pct_grp1`, `cropland_extent_upstream`) with readable ones. The variable catalog (`EDOPS_variable_catalog_v0.4.tsv`) may already hold labels; use them if so, and list any that are missing.
- **Ecoregion-to-Wikipedia links.** Check all 847 rows of `public.eco_wikitext`. Ecoregion 833 (North Saharan Xeric Steppe and Woodland) links to the generic article "Woodland". Find others like it: for example, compare each article title with the ecoregion name and list those that do not match closely. List them; do not correct them.
- **Alexandria's karst at 100%.** Check the value against the source dataset, and say whether it is the source's value or an error in loading or aggregation.
- **Tbilisi "drains to the sea".** The Kura reaches the Caspian. Find how the source classes the Caspian (ocean, or inland sink). Report how many L6 basins drain to it and what their `endo` and `dist_sink` say.

## 4. Two timings for January

Measure, do not optimise. Local machine, labelled as such.

- **A DEM window around the point.** At the ten test places, read elevation in windows of 5, 20 and 50 km radius from a DEM of about 1 km resolution (30 arc-seconds). Report time per place and the min, max and mean in each window. If no such DEM is available locally, name one (for example GMTED2010 or SRTM30), its size, and how it would be loaded, and stop on this item.
- **The basin's elevation distribution.** For a few dozen L6 basins, compute an elevation histogram from the same DEM. Report the time per basin and extrapolate to all 16,397.

The window values for Tbilisi are worth showing in the summary: they are the first evidence for a "valley floor" kind of statement.

## Provisos

- Wording changes go through `profile_templates.md` with a version and a Changes line, as its header says. Rule changes stay in the script.
- No ring rules (WO-06), no class words (WO-07), no snap. The Surroundings section stays as it is.
- Read-only against the database except for anything this WO adds deliberately (for example a point ecoregion lookup); record the commit.
- Where an item needs data that is not there, name it and stop on that item.

## Deliverables and gate

- `wo05_summary.md`: one page, read first.
- `wo05_results.md`: one section per numbered item above, with issues found.
- `wo05_filled_profiles.md`: the ten filled_profiles regenerated from `profile_templates.md` v2 (or the version current at the end, if CC changed the wording under item 2).
- `wo05_wikilinks.csv`: the suspect ecoregion links.

**Gate:** the ten filled_profiles regenerate from the current template version with S1.1b, S1.2a, S1.2c, S1.5a and S1.5b filled at every place that has a basin; every water class has checked wording; each item in section 3 has an answer; both timings are reported or their missing data named.
