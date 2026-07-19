# WO3a · Scale-compare probe (read-only; no build)

Do not summarize the CHAR MAUP findings — they are written up and we have them
(`EDOPS_data_characterization_report.docx` §6.1–6.5; `esda_findings.md` ARI.3, ARI.4, ARI.5).
The gap is between those findings and the live instrument. Report only on that.

Findings → `docs/edop/demo/wo3_probe_findings.md`.

1. **Level select on the Polities tab — is it working?** Karl reports it operates on
   Settlements but appears inert on Polities. WO22 findings claim both tabs wired
   (`_onLevelChange()` → `_drawScopePreview()` + `_silentResig()` → `_repaintChoropleth()`).
   Determine which is true, and if it is inert, *why*: not wired, or wired but failing?
   Candidate cause: selective paint at L08 keys off `_sigMemberIds`, and an extensive polity's
   L08 member set is very large — the repaint may be silently failing, timing out, or exceeding
   a feature-state limit rather than simply not firing. **The distinction matters:** one is a
   wiring bug, the other constrains whether an L08 polity view is feasible at all.
   Report request time and member-set size for a polity at L08 (use N Song; then an extensive
   one — Abbasid or Tang — for the worst case).

2. **Tbilisi is the confirmed demo case — characterize it.** The L06 containing basin reads
   humid; the L08 basin reads arid (Karl's screenshots). This is the ARI.5 mechanism inverted:
   the coarse basin averages the wet Caucasus flank across the dry Kura valley floor.
   Report, for the Tbilisi point at both levels: containing basin id, area, aridity raw value
   and percentile score, and the full Band A–E signature diff. **Which variables flip, which
   hold?** The claim we will make in public is that L06 and L08 give different *true* answers —
   we should know exactly which parts of the signature the claim covers.

3. **Northern Song at L06 vs L08** (contingent on item 1). Does the aridity gradient hold,
   sharpen, or dissolve at L08? Report per-basin spread (p90−p10) at each level for the three
   distinct states (961 / 970 / 980). Note §6.4's guidance cuts both ways here: it prefers L06
   for polygon queries covering few L06 basins, *"unless within-polygon heterogeneity is itself
   the question"* — and for N Song it **is** the question. So L08 may be the correct unit for our
   own hero shot. Any of hold / sharpen / dissolve is a usable result; not knowing is not.

4. **Compare rendering — what would it cost?** Given the Tbilisi case, is a genuine side-by-side
   (two panes, or a swipe/split) needed, or do two screenshots at different levels carry it?
   `basin06.pmtiles` and `basin08.pmtiles` are separate sources. Report the cheapest honest path.
   **Do not build.** If the story is carried by a toggle plus a steady hand, say so — that is a
   good outcome, not a failure.

5. **Pacific Northwest (ARI.5)** — reproducible in the sandbox, or notebook-only? It depends on
   LISA classifications, which may not be in the sandbox paint path. If notebook-only, it is a
   slide, and that is an acceptable answer.
   