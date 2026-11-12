# WO-03 summary: registry harness, stage 1

2026-11-12. Spec: `reg_wo03_registry-harness-stage1.md`. Full detail: `reg_wo03_results.md`. Branch `registry`. No engine, API or Sandbox behaviour was changed. The work stops at the schema proposal for Karl's approval.

## The short version

A safety net is in place: ten signature payloads are saved and a test compares today's responses with them, so later engine changes cannot quietly alter existing output. The audit of where source facts live shows they are scattered and in places wrong, which is the case for a registry. A schema is proposed but not built.

## What was done

- **Baseline.** Ten requests (Timbuktu, Tbilisi, Bruges, Northern Song 961, Band T for Timbuktu and Kyiv, and the public signature) are saved. The test allows added fields and fails on any changed or removed field. Numbers match to six digits; a timestamp is ignored; one live elevation lookup is pinned so the test runs offline. 17 new tests pass.
- **Test partitions.** Tests now carry area markers, so a run can be limited to one area (`-m engine` takes 26 seconds; the whole suite takes about three minutes).
- **Audit of the sources.** For LMR, HYDE, eVolv2k, Cliopatria, BasinATLAS and GEDA: where the extent, years, grain, units, citation, licence, caveats and checks live, with file and line.
- **Papers.** The papers for the sources the signature uses are in `articles/sources/`, prefixed by source.
- **Docsite.** The two HYDE links were corrected.

## What we found

1. **LMR covers 0 to 2000, not 0 to 1998.** The data holds 2,001 years in every cell. About fourteen lines of code and docs say 1998, and the engine cuts the data off there. Nothing explains why.
2. **The HYDE data is version 3.5, not 3.4.** A byte-for-byte check of one file against the 3.5 download settled it; the "3.4" inside the files is a stale label. Docs, the catalog and the UI say 3.4, and two places give the end year as 2023 when the data ends at 2025.
3. **Licences are known for HYDE (CC BY 3.0), eVolv2k and Cliopatria (CC BY 4.0) and GEDA (CC BY 4.0).** BasinATLAS is CC BY 4.0 overall but some columns may be ODbL. LMR's licence was not found.
4. **Source facts are repeated by hand in many places:** the 700 CE floor in seven, the LMR range in two constants, and two separate caveat systems.
5. **The variable catalog is a file read in four places,** with no database form.

## Decision for Karl and Opus

**Approve, or change, the registry schema.** The draft is `reg_wo03_registry_draft.yaml`: one entry per source, each with a block the engine reads to decide whether and how to query it, and a block that describes it (citation, licence). Karl's decisions while shaping it are listed in the results file, "Design decisions made with Karl (for Opus)": the registry judges source availability, not which variables a route returns; a location gate that tests the query against the source's own cells; a per-source coverage rule (GEDA: ok from 0.5, low_coverage from 0.1); a `sources` block in every response listing what was used and what could not be; nothing about same-concept sources carried in the signature; BasinATLAS as the default input of derived variables. No questions remain open in the draft. After approval: the YAML file, loader, table and test.

## Needs attention going forward

A full list is at the end of the results file: the LMR and HYDE corrections, the missing licences, the missing papers, the two caveat systems, and the stage-2 and stage-3 items.
