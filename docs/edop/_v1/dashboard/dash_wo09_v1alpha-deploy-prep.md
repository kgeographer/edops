# dash WO-(nn): v1 alpha preparation

2026-11-18, drafted by Opus after alignment with Karl. Goal-setting, not a specification. Number to be assigned by Karl (the HYDE line graphs WO comes first, and is not part of this one).

## Goal

Make the new site ready for an eyes-only v1 alpha at `edopsv1a.computingplace.org` (name to confirm), deployed the way the 0.4 preview was (`MAINTAIN_DEPLOY.md`). The alpha shows the new site only: splash, Dashboard, Using EDOPS, Data Explorer. Nothing from 0.4 is reachable from it; anyone who wants 0.4 goes to the live 0.4 site.

## Precondition

The HYDE line graphs WO is done before deployment. This WO can be built in parallel, but does not deploy without it.

## 1. A self-enclosed site

- Inventory every link, button, redirect and fallback on the new pages (splash, Dashboard and its tabs, Data Explorer, Using EDOPS, the WHG profile material), and write down where each should go.
- No route, link or fallback leads to the Sandbox, the old Workbench, or any other 0.4 page. Fix the cases where the Dashboard slips back to the Sandbox.
- On the alpha host, 0.4 routes are not served at all (404 or a short page pointing to the live 0.4 site), so a stale link cannot reach them.
- One plain link to the live 0.4 site, in the footer or the About text, for anyone who wants it.
- Permalinks and example links resolve to Dashboard pages on the alpha host.

## 2. Using EDOPS: an Overview tab and examples

Replace the dummy content with tabs:

- **Overview** (first, the landing view): a short intro saying what EDOPS is for in use (worked examples now; raw data for computational work and a source for other tools, in a sentence each), and one tile per example. Each tile has the example's name and a one-line question it asks, and switches to its tab. `?tab=` links straight to a tab.
- **Societies** and **African Regions:** the existing Workbench content, moved as it is, with one sentence at the top for each (Karl's wording; placeholders until then). A note on Societies that it is a pilot exploration with no conclusions published.
- **Pueblo:** a stub. "Coming soon" and two or three lines on the question (whether the Chaco to Rio Grande movement is explained in part by the environmental evidence EDOPS has).
- **WHG:** the sample profiles page moves into this tab (ten places, template view, response JSON), with a short intro on the WHG place-page profile. `/profiles` then redirects here or is retired. No screenshots of WHG's beta pages.

No Ukraine tab or tile.

## 3. Time series stub

A Time series tab in the Dashboard: "coming soon" and a short outline of what is planned (choose variables and a span; aligned charts; download of the raw numbers; comparison of two places), and a note that long Band T spans will point here.

## 4. Draft status and access

- A banner on every page: work in progress, not for citation, with the version (v1 alpha) and date.
- Eyes-only as for the 0.4 preview (`maintain_deploy`): noindex, and whatever access control was used then. If 0.4 used noindex only, report it; Karl decides whether to add a password.

## 5. Tidying

Anything found during item 1 that is broken, placeholder or misleading on the new pages: list it in the results, fix what is small, and leave the rest for Karl. Stubs say plainly that they are stubs.

## Provisos

- The live 0.4 site is untouched.
- No new features beyond the stubs; content moved, not redesigned.
- Karl writes the intro sentences and stub texts; placeholders are marked.
- Deployment is Karl's and CC's, following `maintain_deploy`, after the HYDE WO.

## Deliverables and gate

- `dash_wo(nn)_summary.md`: one page, read first, with the link inventory and the list of tidying items.
- A full-page screenshot of the Using EDOPS Overview tab.

**Gate:** a Playwright click-through of every nav element, tab, tile and example link on the new pages reaches only new-site pages (or the one link to live 0.4); Using EDOPS has its five tabs with the Overview first; the Time series stub is in the Dashboard; the banner is on every page.