# Status after WO-05 (Claude Code, 2026-11-14)

Written for Opus. The registry and GEDA work is done on the engine path only; it is not complete.

## What is done

WO-04, WO-04a and WO-05 are finished and tested. The registry harness and GEDA work end to end on the engine path, which serves the Sandbox's `/api/areas` and the public `/api/signature` routes `scope=buffer` and `scope=area`.

- The full suite passes (755 passed, 21 skipped).
- Branches: `registry` (WO-04 and WO-04a) and `geda` (WO-05, cut from `registry`), both pushed. `regionality` and `main` are untouched. Nothing is merged and nothing is deployed.
- `signature_version` is "0.5".

What exists:

- A YAML source registry, the only copy, with nine sources.
- `check()` judges years, footprint and coverage rule for a regional source.
- GEDA is served in Band T through it.
- A `sources` block on responses lists what was used and what was not applied, with reasons.
- A permitted-sources option exists; nothing passes it yet.
- The baseline has 16 reference payloads, including GEDA cases.

## What is not done (so "registry done" and "GEDA done" would be wrong)

1. **Public API, `scope=basin`: no GEDA.**
   - `/api/signature?scope=basin` runs on separate code (`signature.py`, `temporal.py`, `hyde.py`) that never consults the registry for GEDA.
   - It is silent, not just absent: for Tbilisi 1150-1250 the response lists LMR and eVolv2k in `sources` but has no GEDA entry, in neither `used` nor `not_applied`. A caller gets no hint that GEDA exists.
   - This is part of the regionality remit. It needs a work order: unify the basin path's Band T onto the engine's blocks, or add a GEDA block to it.
2. **Public API, `scope=buffer` and `scope=area`:** GEDA is returned, but Band T there takes a single year only. Without `detail=true` the rows carry only the weighted mean, because the lean form drops `detail`, where the distribution lives.
3. **Display.** The Sandbox ignores GEDA rows: they are in the payload and the page does not draw them. WO-05 was scoped as no display work. Karl's direction: GEDA should read like LMR in the UI (a panel mirroring LMR's). The only visible change today is that the Band T badge counts the extra rows (cosmetic).
4. **Catalog as the single truth of every variable.** Not done, and Karl treats it as a core principle. The check showed 6 payload variables with no catalog key. `geda_scpdsi` has a catalog row whose key equals its payload name, so it joins cleanly.
5. **Docs.** The API guide (`api.md`), the two schema JSONs and the Sandbox pages do not mention GEDA or the `sources` block, and HYDE 3.4 mentions remain. These are on the pre-v1 docs check.

## Open decisions and findings

All are in `reg_wo05_results.md`, "Needs attention".

- **Band T headline is inconsistent across sources.** LMR and GEDA lead with a weighted mean, HYDE with a sum, BasinATLAS multi-basin rows with a percentile and no native value. Whether the headline should be the distribution is a display question, deferred; it would change LMR, HYDE and GEDA together.
- **SQL built from polygon text.** The existing HYDE, LMR and eVolv2k blocks put the polygon text into the SQL string, and the public `scope=area` route checks only the first word. The basin-resolution step parses the text first through a parameterized call, so it is probably contained, but production v0.4.2 has the same code. GEDA's block is parameterized. Needs a decision on timing.
- **Deploy.** `temporal.geda_climate` must be loaded to the server database before code that serves GEDA runs there.
- **Versioning.** 0.5 holds through GEDA; the number moves to 1.0 at the deploy. The earlier "minor bump per additive change" rule no longer applies before 1.0.

## Departures from the WO's wording in WO-05

- "Observed" is a second caveat key, `geda_observed`, not an `observed: true` field. A new row field would add a key to every row of every payload, and the lean projection drops `detail`.
- The effective cell count is `detail.w_eff`, as for HYDE.
- `check()` carries the footprint test and the coverage rule, as agreed.

## Suggested next work orders (for Opus to sequence)

- (a) Public basin-path integration, to close the regionality remit.
- (b) Catalog completeness.
- (c) GEDA display.
- (d) The SQL hardening, possibly ahead of the others given it is in prod.
- (e) The pre-v1 docs check.

Until (a) is done, "registry implemented" should read "implemented on the engine path, provisionally".
