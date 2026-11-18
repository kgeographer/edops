# dash WO-09 results: v1 alpha preparation

2026-11-18. Spec `dash_wo09_v1alpha-deploy-prep.md`; summary `dash_wo09_summary.md`. Branch `dashboard`. Commits: `dffe448` (site mode), `8ff85bc` (no analytics, no query log), `a0b6f46` (v0.4 tags), `afefde2` and `9f173a3` (Using EDOPS), `3fffa70` (Time series stub), `5d1928e` (Atlas to Explorer, permalink button). Nothing deployed.

## Link inventory (item 1)

Found by reading the rendered pages and by a click-through; the click-through test is `tests/dashboard/test_alpha_click_through_ui.py`.

| Page | Internal links and where they go |
| --- | --- |
| Splash `/edops` | tiles to `/dashboard`, `/using`, `/explorer`; two example dropdowns to `/dashboard?...` (17 examples); Documentation modal (`/docs`, the 0.4 docs); banner link to live 0.4 |
| Dashboard `/dashboard` | header pills to `/edops`, `/dashboard`, `/using`, `/explorer`; help modals to `/docs/sandbox/reading-a-signature/`, `/docs/codebook/`, `/docs/similarity/` (0.4 docs); the permalink button builds `/dashboard?...` on the page's own origin |
| Using `/using` | header pills; left tiles are tabs on the page; frames `/using/societies`, `/using/africa`; WHG tab links are `?place=` on the same page |
| Explorer `/explorer` | header pills; modals to `/docs/data-sources/`, `/docs/explorer/overview/` (0.4 docs) |
| Embedded Workbench | no internal links apart from the favicon |
| External | Computing Place and project links in the splash's About text; the live 0.4 site (banner and pointer page) |

- **No page on the new site links to a 0.4 page.** The leaks were Explorer's header (Sandbox and Workbench pills, from the shared header) and the old profiles page's own nav; both fixed.
- **Docs.** `/docs` is the 0.4 documentation and is still served; in the alpha its link reads "Documentation (v0.4)" with a red tag, and so does the modal title. A banner inside the docs pages would need a separate docs build and was left out.
- **0.4 routes in the alpha.** 404 with a pointer page for `/sandbox`, `/sandbox/*` (including the old `lookup`, `lookup3` and `explorer` aliases), `/workbench`, `/polities`, `/about`. `/` renders the splash on any host in the alpha. The API routes stay: the Dashboard and Explorer need them.

## Isolation

- Analytics: `_ga.html` renders nothing in the alpha (every page includes it).
- Query log: the logging middleware skips the write in the alpha (a test counts rows before and after a request with the setting on, and the same request with it off adds one).
- The test suite runs in normal mode whatever `.env` says (an autouse fixture in `tests/conftest.py`); tests that need the alpha switch it on. This was needed after the alpha setting in a developer's `.env` made unrelated tests fail.

## Using EDOPS

- Layout and content as in the summary. Societies and African Regions are `workbench.html` in embed mode (no header, no tab bar, one tab selected after the page's own `DOMContentLoaded` handler has registered its tab listeners; selecting the tab earlier left the African Regions map unpainted). Frames load on first view and grow to their page's height. `workbench.html` therefore cannot be retired at the v1 deploy without moving that content into the Using page, which means untangling its roughly 4,400-line shared script: a work order of its own.
- The sample profiles page is now a partial (`_profiles_panel.html`); `/profiles` redirects (307) to `/using?tab=whg`, keeping `place` and `view`.
- Both column widths were tried (`using_2of10.png`, `using_3of9.png` in the scratchpad); 2/10 was kept.

## Time series stub

A tab with "Coming soon", the planned outline (variables and a span, aligned charts, download of raw numbers, comparison of two places) and the note that long Band T spans will point here. Always enabled, not a result tab, not part of the tab reset.

## Atlas to Explorer and other changes made along the way

- The Atlas script moved unchanged (ids renamed) to `app/static/js/edops_atlas.js`; while the tab is active the Explorer's variable selector and control strip give way to the Atlas text. Removed from the Dashboard: the tab, pane, left panel, script and the `view=atlas` link value.
- **Bug found:** `#ex-pane-compare { display: flex; }` in `explorer.css` kept the hidden Compare pane laid out (about 500 px) below whichever tab was active. Removed; the active pane is still shown by `.tab-pane.show.active`.
- The permalink button moved into the left column beside Reset ("Permalink", copy icon); the link box appears under the strip on click and goes away on a second click. Karl's note: the usual pattern is a short "copied" message; refine in the review stage.

## Deployment prerequisites (not part of this WO's build)

From `MAINTAIN_DEPLOY.md` and CLAUDE.md, for the alpha service: a new hostname (A record, nginx block, certbot; name to confirm), a new port (8002 to 8004 are taken), a new service, tree (`/var/www/edops-v1a`, tracking `v1`) and venv; the alpha service's environment needs `EDOPS_SITE_MODE=v1alpha` (and `EDOPS_LIVE_V04_URL` if different); `temporal.geda_climate` must be loaded in the server database first; the gitignored assets (PMTiles, `explorer/`, `hyde_tiles/`, `basinatlas_pages/`) are rsynced. The alpha shares the live `cedop` database, so it must not write to `public.query_log` (done) and uses only additive objects.

## Needs attention

1. Placeholder wording (yellow): the Overview intro, the tile questions, the Societies, African Regions, Pueblo and WHG lines, the Time series outline, and the time-limit message from WO-08.
2. `[More]` in each Using tile loading a short essay (Karl's idea; not built).
3. The splash's About EDOPS modal and the Computing Place tile still say v0.4.
4. `workbench.html` stays as the source for two Using tabs (above).
5. How the 0.4 preview was kept eyes-only is not recorded in `MAINTAIN_DEPLOY.md`; the alpha relies on an undistributed address, noindex and robots.
6. The full suite was run at the end of this WO; its result is in the log of 18 Nov.
