# WO-10: sample profile page

Draft of 10 Nov 2026.

## Goal

A page at `edops.computingplace.org/profiles` that shows the Environmental Profile for the ten WO-09 places, for Stephen Gadd and Ruth Mostern to review before 21 November. It shows what a WHG place portal would carry and lets a reader see which parts of the text come from data.

## Background

- The profiles come from `wo04_fill.py` and its companion scripts, worded by `profile_templates.md` (v19 at WO-09). `wo09_filled_profiles.md` is the current output.
- Decision (Nov 2026): show a sample page to Stephen and Ruth instead of deploying a Summary tab, so their judgement covers the summaries' nature, quality and content, and deployment errors are deferred.
- Profiles are generated and stored ahead of time. The page reads stored profiles and does not call the engine. Today that is the ten places; later it is all L6 basins.
- The Cliopatria polity page (`/polities`) is the model for placement: a sibling of the Sandbox, Workbench and Data Explorer, not linked from them, with its own menu linking to them.

## Places

The ten WO-09 places, in this order: Timbuktu, Tbilisi, Santa Fe, Kaifeng, Lviv, Poltava, Chaco Canyon, Alexandria, Utqiagvik, Tristan da Cunha. Default: Timbuktu (Karl to confirm).

## Items

1. **Route and header.** New page at `/profiles` (Karl to confirm the path). Header and menu follow the polity page: logo, title, buttons for Sandbox, Workbench and Data Explorer. Nothing on the other pages links here. Add `<meta name="robots" content="noindex">`.
2. **Place pills.** A row of pills under the header, one per place, in the order above. The selected place is in the URL (`?place=timbuktu`), so a link opens that profile. Unknown or missing `place` falls back to the default.
3. **Intro.** A short block above the profile that stays the same for every place: that this is a sample generated ahead of time, the template version and generation date, the framing-A rule (Setting describes the place; the other sections describe its basin and say so), and the sources. Draft text only, marked for Karl to rewrite.
4. **Profile.** Below the intro, in a div that scrolls. Each section has its subtitle (Setting, Climate, Water, and so on, as generated). No accordions. Bootstrap styling, in keeping with the polity page. The Buttons section renders as real buttons: OneEarth and Wikipedia open in a new tab where present; Data as JSON opens the stored profile for that place.
5. **Template view.** A show/hide button that re-renders the whole profile as its template: the template lines the rules selected for that place, with every slot left unfilled (`{name}`, `{S2.1a}`, `{km}` and the rest, as they stand in `profile_templates.md`). Because the lines are per place, switching places in template view shows which sentences the rules chose, not only which numbers changed. The generator writes both renderings from the same selection; the page swaps them and does no parsing of its own. The template key of each line (for example `S3.2.headwater`) appears as a small muted label in template view.
6. **Tristan da Cunha.** The pill is a normal pill. Its profile is a short message that the point lies on a small island with no basin in the data, so there is no profile to show. Draft wording, marked for Karl.
7. **Unbuilt units.** The four remaining placeholders (S1.2b, S6.2c, S8.1b, S9.1) are visible in both views, styled so they read as "not yet built" and not as broken text. Karl to confirm: show them, or hide them in the filled view.
8. **Stored profiles.** The generator writes one record per place holding both renderings, the section structure, the buttons, the provenance line it already writes, and the fill notes. Use the structure the eventual store for all L6 basins would use. Fill notes are stored but not shown on the page.

## Provisos

- No wording changes. `profile_templates.md` is the source of all profile text; if something on the page needs a wording change, list it, and any edit follows the file's version and Changes rule.
- No changes to the Sandbox, Workbench, Data Explorer or polity pages, the `/whgmodal` endpoint, or the engine.
- The page works at phone width: the pills wrap, nothing scrolls sideways.
- The OSM credit appears wherever a profile shows a river name (N4), as the generator already does.
- Branch `whg-profile`. Build and check locally. No push and no deployment until Karl says.

## Out of scope

The LLM paragraph; the Summary panel in the Sandbox; precomputing all L6 basins; monthly arrays in the payload (P2); filling the four unbuilt units; the Wikipedia work on flagged ecoregion links.

## Deliverables and gate

- The page, running locally.
- Screenshots of every place in both views at desktop width, and of two places (Timbuktu and Tristan da Cunha) at phone width.
- A short `wo10_summary.md`: what was built, the route and file layout, the stored-profile structure (item 8), any wording problems found (proviso 1), and decisions waiting for Karl.
- Tests pass.

Gate: Karl reviews the screenshots and the local page before anything is pushed or deployed.
