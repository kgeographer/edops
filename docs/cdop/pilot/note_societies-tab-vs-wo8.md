# Note — the Societies tab UI and the WO8 correspondence-testing arc never intersected

Written 2026-07-28, after Karl noticed the Societies tab still shows old PCA-based clustering when
filtering on EA042/EA034, and lost track of whether any WO8 work ever reached it. Answer: it never did
— by design, not by omission. Written down here so this doesn't need re-deriving from git history again
when CDOP Pilot is next revisited.

## The two tracks

**Track 1 — the Societies tab UI is pre-CDOP-Pilot legacy.** Built in `workbench.html` on 2026-01-18
(`a0cb42c "Societies tab: D-PLACE UI with subsistence filter"`) — five-plus months before CDOP Pilot
(WO1) started. `cdop_pilot.html` was cloned from `workbench.html` for WO1 and inherited this tab
wholesale; nothing since has touched it. Its "Basin clusters" coloring option (`basin08.cluster_id`)
comes from an even older pipeline, `scripts/edop/basin08_cluster_labels.py` (2026-01-11) — a PCA
dimensionality reduction + cluster assignment over BasinATLAS basin features, predating the Areas/CHAR
phases' own later work. It is the same *style* of broken PCA-composite approach the CDOP_PILOT_tracker
itself names as the reason WO1 was commissioned in the first place (the Jerusalem/Acre/Mombasa failure
on WH Cities similarity) — just never revisited on the Societies/basin side, because WO1's fix went
into a new WH-Cities lens, not back into this tab.

**Track 2 — WO8a–d (the real correspondence-testing research) was scoped as notebook-only from the
start, not left unfinished.** Checked all four accept gates directly: WO8a states outright "descriptive
notebook only (**no engine/API/UI**)"; WO8b/8c/8d follow the identical pattern — each built a notebook
plus a standalone stats module (`dbperm.py`, `distance_core.py`) with zero `routes.py` or template
changes. This was Karl+Opus's own deliberate scope choice at WO8a's outset, not something dropped along
the way.

**The coincidence that made this hard to keep straight**: EA042 (subsistence) and EA034 (high gods) —
the exact two variables the January UI already filters on — are also the exact two variables WO8a
(positive control) and WO8d (the high-gods look) independently chose for their own, much more rigorous
analyses (PERMANOVA/PERMDISP, family-restricted permutation, whole-sample-backdrop cohesion). Same
variable names, two tracks that never touched: one a simple pre-existing filter+PCA-color UI, the other
a notebook-only statistical research arc with real findings (WO8a's environment-sets-bounds-not-
determination headline; WO8b's fixity band; WO8c's complexity null; WO8d's two-lineage story and the
still-open singleton residual) that has never been surfaced anywhere a user can see it.

## What this means for revisiting CDOP Pilot

Nothing to fix reactively — this is a genuine unspec'ed question, not a bug. When the phase is next
picked up, the first real design decision is: **what should the Societies tab actually show, now that
WO8's findings exist?** Candidates, not decided here:

- Replace the January PCA-cluster coloring with something WO8-derived (e.g., the climate-envelope
  bet from WO8a, or a cohesion-based view in the spirit of WO8d's exploratory instrument).
- Surface WO8's actual findings as a static/narrative layer (closer to how the sandbox's Context tab
  reports percentiles without a composite score) rather than trying to make an interactive instrument
  out of exploratory research that was never built with a rank/paint head in mind.
- Leave the tab as a plain D-PLACE browser and give the correspondence-testing findings their own new
  surface entirely, separate from the legacy filter UI.

All three are real options with different amounts of new build; none is assumed here. This note exists
so that conversation starts from the right premise (two disconnected tracks, not a stalled feature)
rather than re-deriving it.
