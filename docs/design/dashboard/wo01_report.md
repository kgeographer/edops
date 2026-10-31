# WO-01 report: reconcile docs and cheat sheet

2026-10-29. For Opus. Status: **complete.** The Sandbox cheat sheet, the documentation site and the running app now describe the same thing as of release v0.4.2 (commit `a673660`, live 2026-10-29). Everything v0.4.2 changed was re-verified against the running app; see Caveats for what was not.

## What was done, in numbers

- **22 of 22** reconciliation items closed, each checked against the code (cited by file and symbol).
- **40** change-log rows (app, code and docs) worked through one at a time. Every one is applied or decided, except one docs credit line (the AWMC tile server) held for a reply from its host.
- **v0.4.2 release:** 27 commits, tagged and deployed. Full suite **600 passed, 0 failed** (21 skipped: the live-server tests, run separately, 21 of 21 passing against production after one cold-start timeout on the first request). 15 tests added, 2 retired.
- **App:** 8 source files changed. **Documentation:** 14 files changed (10 pages and 4 screenshots), Codebook regenerated from the variable catalog.
- **Cheat sheet:** about 60 lines revised in a final pass against the released app. All 65 distinct code citations checked to exist; header re-stamped; the nine example captures and the docs-for-Opus concatenation regenerated.

## What changed in the app that the cheat sheet now reflects

Reconciling the three turned up real defects, not only wording drift. All are fixed:

- A–E band checkboxes filter rows (they did nothing before).
- A reversed Band T span is rejected with a clear error.
- A query that resolves to no basins returns a 404 with a message, not a 500.
- Empty values state their cause (*not present here*, *largely absent*, *no data*, "no single percentile…", *(low coverage)*) instead of a bare dash.
- Buffer and polity headings name the place, radius and BCE years; the HYDE map follows the signature's epoch rule.
- Atlas no longer drops 59 zero-precipitation basins (now Arid); the Sandbox falls back to a modern basemap if the AWMC tile server is down.

The documentation was rewritten to match, and four screenshots were re-shot.

## For the design work

- **Still open (design, not defects):** cheat sheet §7.2 items 11 to 13: how to summarise a small set of basins (ring, any buffer that stays) for divergence, seasonality and similarity; whether the buffer scope stays; surfacing the catalog's per-variable historical validity.
- **Noted for the dashboard:** why a row has low coverage is not explained on screen (the payload has what an explanation needs); the Atlas is not a signature result and sits awkwardly in the Sandbox.
- **Fixed rules are reading aids:** the badge cutoffs and other interpretive thresholds are listed in §9 with who sets each; the commitment wording was softened accordingly.

## Caveats

- Sections the v0.4.2 changes did not touch were last verified against the code on 27 Oct. Nothing known is stale there, but they were not re-read after v0.4.2. Your consistency read is the check on them.
- `file:line` citations in the cheat sheet may be off by a few lines where v0.4.2 edited a file; function and symbol names are verified.
- Map screenshots in the docs show the original terrain basemap and are unchanged; the tile server was down on 28 Oct and is being restored.
