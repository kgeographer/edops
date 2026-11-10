# WO-10 summary: sample profile page

Spec: `wo10_sample-profile-page.md`. Findings and questions for Opus: `wo10_results.md`. Branch `whg-profile-page` (cut from `whg-profile`), local only: not pushed, not deployed, not merged. Commits fe5b153, e52d52c, c1095c9, ac1ae19. Template version 20.

## What was built

- **`/profiles`**: a standalone page in the manner of the polity page. Logo, title, Sandbox / Workbench / Data Explorer pills; `<meta name="robots" content="noindex">`; no other page links to it (tested).
- **Place pills** for the ten WO-09 places, in order. `?place=timbuktu` selects one; a missing or unknown value falls back to Timbuktu. Switching does not reload the page.
- **Intro block** (draft wording, marked in dark red for Karl to rewrite): sample, generated ahead of time by rules, the Setting-versus-basin rule, sources, template version and date.
- **Profile** with a subtitle per section, no accordions. Bootstrap. The page scrolls as a whole (no inner scroll box, so a full-page screenshot captures everything) and is full width. Checked at phone width by Karl: pills wrap, chart scales.
- **Ecoregion names are links** to their OneEarth pages (new tab) wherever they appear: the point's ecoregion (S1.2a), the basin's majority ecoregion (S1.2c) and the other ecoregions (S1.4).
- **Climate chart** under Climate: monthly precipitation (bars) and temperature (line) of the basin, after the Sandbox's Walter-Lieth chart, drawn from the record's `monthly` values. Text view only.
- **Buttons** under a rule, no heading: Profile as JSON (the stored record), Full signature (JSON) (`/api/signature?scope=basin&level=6&lat=…&lon=…`) and Ecoregion on Wikipedia where the link is not flagged. All open in a new tab.
- **Template view** (button, or `?view=template`): the template lines the rules chose, with `{slots}` unfilled and the line's key as a small muted label; parts the rules put inside a line are indented. The page does no parsing for wording, only for colouring the slots.
- **Tristan da Cunha** is a normal pill whose profile is the generator's no-basin message in `<h3>`, `#993333`.
- **Unbuilt units** (S1.2b, S6.2c, S8.1b, S9.1) are hidden in both views. Setting and About these figures use two frames added in v20 (`S1.frame.nogist`, `S8.frame.noyears`) so that hiding a unit leaves no hole.

## Generator change

`wo04_fill.py` now records, per unit, the template lines it chose (key, raw text, slot values, and the lines placed inside others as parts). The recording is a context variable that is active only inside `fill_units`; `fmt()` writes to it and `ok()`/`no()` collect it. The markdown output is unchanged (checked byte for byte against the committed WO-09 file before v20; since then section by section, see `wo10_results.md`). `profile_vals` was extracted from `render_filled_profile` so the record and the markdown share one set of values.

## Route and file layout

- `app/web/pages.py`: route `/profiles`; reads `app/static/profiles/index.json`.
- `app/templates/profiles.html`, `app/static/css/profiles.css`.
- `app/static/profiles/<slug>.json` (ten records) and `index.json` (place, slug, no_basin, in display order). Served as static files.
- `scripts/edop/whg/wo10_profiles.py`: `build_record`, `write_records`, `slugify`, the frame choice, buttons, ecoregion links, `monthly`.
- `scripts/edop/whg/wo04_fill.py`, `wo08_units.py` (registry entries for the two v20 frames), `docs/design/dashboard/profile_templates.md` (v20).
- `notebooks/edop/whg/wo10_profiles.ipynb`: Cell 2 checks the markdown and the recorded lines and writes the records; Cell 3 prints the template view of one place.
- Tests: `tests/test_whg_wo10.py` (8: recording, parts, silent units, context restored, slugify, segments, no-basin record, frame choice) and `tests/test_profiles_page.py` (3: page renders and is noindex; no other page links to it; every record has both renderings, no placeholder text, the button order, 12 monthly values each).

## Stored-profile structure

One JSON per place, about 29 to 36 KB (Tristan 0.8 KB):

- `place`, `slug`, `lat`, `lon`, `hybas_id`, `generated`, `template_version`, `provenance`, `no_basin`.
- `sections[]`: `id`, `title`, `filled` (plain text), `runs` (the same text as `{t}` or `{t, href}` pieces, the links being ecoregion names) and `template` (segments: `text`, `slot`, or `line` with `unit`, `key`, `raw`, `vals`, `parts`). Both renderings come from one selection of units.
- `monthly`: `scope` 'basin', `level` 6, `source`, `precip_mm[12]`, `temp_c[12]`.
- `buttons_title`, `buttons[]` (`id`, `label`, `url`, `target`).
- `units{}`: for every unit, `scope` ('point' or 'basin'), `ok`, `text`, `why`, `na`, `note`, `lines`. The point units are S1.1b, S1.2a, S1.2c, S3.1, S3.3, S8.3, S8.point, S8.osm, S9.2, S9.4.
- `notes[]`: the fill notes, stored and not shown.
- A no-basin record has `message` and empty `sections`, `buttons` and `units`.

For a future store of all L6 basins: selection is separate from rendering (a unit stores its key and slot values, so a wording edit re-renders without refilling); the `scope` tag marks what a per-basin record can carry and what needs the point (see `wo10_results.md`, C). At about 33 KB, JSON files for 16k basins would be about 500 MB, so a database table is the likelier store. Not built.

## Wording problems found

In `wo10_results.md`: the land cover percentages that can add up to more than 100% (S5), and the S8.2 sentence under About these figures, which explains percentiles the page does not show and uses catalog variable names.

## Decisions waiting

- Wording changes (v21): the S5 sentence; the S8 percentile sentence; the S9 frame, which still lists a OneEarth button; the intro text and the Tristan message are drafts for Karl.
- The shape of the `/whgmodal` response, monthly arrays in it, point versus basin units, the permalink (`wo10_results.md`, A to E). For Opus.
- Remaining placeholders in the profiles: S1.2b (One Earth reply), S6.2c (Opus), S8.1b (Karl's date range), S9.1 (WHG URL scheme).

## Not done

Full test suite (only the 55 WHG tests and the 11 WO-10 tests were run on this branch; the app suite runs before any merge); push and deploy (Karl says); screenshots (Karl).
