# Sandbox cheat sheet — spec (agreed 2026-10-26)

Purpose: factual, code-cited map of everything the **Sandbox** produces for a signature call (values, tables,
badges, charts, maps), for Opus, who lacks Sandbox context. No design opinions. **Workbench is out of scope.**

- Output: `sandbox_cheatsheet.md`, header "Last verified against commit X". ~4 pages; link out to docsite/engine docstrings.
- Every claim tagged `[code file:symbol]`, `[doc path §]` or `[inferred]`; symbol first, line number second.
- Built one section at a time, code read fresh each time; Karl reviews each before the next.
- Final pass: re-check every `[code]` citation, stamp the commit, list `[inferred]` items under "Open questions".

Sections: 0 Parameter space · 1 Query types (UI → engine → what the signature describes) · 2 Signature
structure (bands, row fields, method taxonomy, dash taxonomy, percentile reference set) · 3 Aggregation by
scope · 4 What the UI shows and where it collapses information (**includes every chart/graph/map**) ·
5 Date handling · 6 Other results of a signature call (companion endpoints, maps, context, similarity) ·
7 Known gaps and quirks · 8 Appendix: captured example responses (GET only, local server).
