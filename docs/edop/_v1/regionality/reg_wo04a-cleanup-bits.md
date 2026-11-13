# WO-04a (regionality): stage boundary before GEDA

Draft of 2026-11-13.

## Goal

Close stage 2 cleanly before GEDA is added, so that when WO-05 changes the payload the only differences are GEDA's. Fix the payload strings WO-04 deferred, bump the signature version for the `sources` block, and re-capture the reference payloads once, deliberately.

## Context

- WO-04 is complete on branch `registry` (head 4c0c8e2; 710 passed, 21 skipped). Its open items 2, 3, 5, 11 and 16 are handled here.
- This WO stays on `registry`, and so does the work after it (WO-05). There is no merge back to `regionality` at this point; it happens when a stage needs it.

## Items

1. **Payload strings.** Change only the strings that appear in responses:
   - "HYDE 3.4" to "HYDE 3.5" in the HYDE caveat text and in `meta.data_sources` (`routes_common.py`), and any other string the three affected reference payloads show.
   - LMR "0-1998 CE" to "0-2000 CE" in `meta.data_sources` (`routes_common.py:51`), with its copies in `documentation/edops_schema_area.json`, `edops_schema_basin.json` and the cheat-sheet example `07_public_signature...json`.
   - The remaining "HYDE 3.4" occurrences in docs and frozen records stay for the pre-v1 docs check.
2. **Signature version** "0.4" to "0.5" (the `sources` block is an additive change).
3. **HYDE's registry entry** lists every table the code reads: `temporal.hyde_cells`, `temporal.hyde_times`, `hyde_basin06_steps`, `hyde_basin08_steps` (WO-04 item 5).
4. **Registry table (Karl's decision; do only what he chooses):**
   - (a) Drop `public.source_registry`, its loader and its YAML-versus-table test; the YAML stays the single source the module reads. Or
   - (b) Keep it as it is, and note it in the deploy steps.
5. **Re-capture.** Before re-capturing, run the comparison and produce the diff: it should show only the changes from items 1 and 2. Karl reviews it. After his approval, re-capture all 13 reference payloads (`capture_baseline.py --force`) and record the capture in `MANIFEST.json`.
6. **Record for the unification WO** (no code change): on a span with no HYDE step inside it, the engine path reports HYDE as `used` with a nearest-step note while the public basin path reports it as `not_applied`, `outside_span`. Each is true of its own path; the difference comes from the two paths' different methods.

## Provisos

- No engine, method or row-level change. Only the strings, version, registry entry and (if chosen) the table.
- If the pre-re-capture diff shows anything beyond items 1 and 2, stop and report.

## Deliverables

- Commits for items 1 to 4; the diff for item 5 (for review); the re-captured references.
- `reg_wo04a_summary.md` (short): what changed, the reviewed diff, test state.

## Acceptance gate

The diff before re-capture shows only the intended changes; after re-capture the baseline passes; the full suite passes (zero failures).
