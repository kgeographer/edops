# WO4a findings — Analysis tab inventory + demo assessment

**Date:** 2026-07-13  
**Kind:** Read-only probe. No changes to any file.

---

## Part 1 — Inventory

### What exists

The Analysis α tab in `sandbox.html` (v1 Lookup) contains three components, all rendered by
`renderAnalysis()` (sandbox.html:1090–1243). All three are **pure client-side JS** — no dedicated
engine endpoint. They compute from two already-fetched payloads:

- `/api/signature` — provides all s/u values, `up_area`, drainage fields
- `/api/basin-preview` — provides containing + adjacent basin geometries with `up_area`

The key accessor is `sigVal(sig, key)` (sandbox.html:537–545), which walks `profile_groups[band].items[]`
matching on `item.key`. The keys used: `dist_sink`, `coast_flag`, `endorheic`, `precip_yr`,
`precip_yr_upstream`, `aridity`, `aridity_upstream`, `temp_yr`, `temp_yr_upstream`.

### Scale-mismatch alert

Compares `containing_basin.up_area` vs `max(adjacent_basins[].up_area)` from the preview payload.
Fires only at L08, only if the ratio exceeds 50×. Displays a Bootstrap warning alert.

- **Engine-backed?** No — client arithmetic on preview data.
- **Works at L08?** Yes (L06 branch is suppressed by design).
- **Works on polities?** No — preview is point-only; polity tab has no `basin-preview` call.

### s/u divergence table

Three-row table: precipitation, moisture index (aridity), temperature — local value, upstream value,
ratio. Ratio cells are color-coded (muted <10%, warning 10–30%, red >30% from unity).
Small-basin caveat shown when `up_area` < 5,000 km² at L08 (< 500 km² at L06).

- **Engine-backed?** Values are precomputed BasinATLAS fields returned by `/api/signature`. Ratios
  are client-side division.
- **Works at L08?** Yes — upstream fields present at both levels.
- **Works on polities?** Potentially — `/api/area` returns `profile_groups` in the same schema;
  not tested here.

### Water provenance badge

Single badge + one-sentence gloss, derived from the same inputs as the divergence table.
Classification hierarchy: Endorheic → Coastal terminal → Exogenous water supply (precip or aridity
ratio > 1.5×) → Catchment-uniform → Local-dominant.

- **Engine-backed?** Client rule logic only.
- **Works at both levels?** Yes.
- **Works on polities?** Same as divergence table.

### Porting cost to sandbox_v3

`sandbox_v3.html` already has a blank Analysis tab stub (v3-pane-analysis, line 414) and already
fetches `/api/basin-preview` for Settlements (line 993). It does **not** have `sigVal()`. Cost
of porting the full divergence + provenance section: add `sigVal` (8 lines), adapt `renderAnalysis`
divergence block (~80 lines of JS) to v3's variable names, call it from the v3 signature handler.
**Porting cost: low.** The scale-mismatch section would need separate handling (L06 path suppressed
in v1; v3 has explicit level state).

---

## Part 2 — Demo assessment

### 1. Scale-mismatch alert — does it fire on Tbilisi?

Tbilisi at L08:
- Containing basin `up_area`: 23,252 km²
- Largest adjacent basin `up_area`: 33,467 km²
- Ratio: **1.4×** — well below 50× threshold.

**The alert does not fire on Tbilisi.** This is the right result for the wrong reason: the alert
detects when a microbasin is dwarfed by a neighbor, not when L06 and L08 give semantically different
answers. Tbilisi's scale story (biome flip, −30 pp aridity between levels) is a MAUP effect, not a
size-disparity effect. The alert as designed is orthogonal to that story; it would fire on a small
coastal basin adjacent to the main Nile — not on a mid-sized highland basin like Tbilisi's.

### 2. Water provenance / s/u divergence — which places light up?

All queries at L08 except Timbuktu (also checked at L06). Ratios computed: upstream ÷ local.

| Place | Level | up_area km² | precip local | precip upstream | ratio | aridity local | aridity upstream | ratio | Badge |
|---|---|---|---|---|---|---|---|---|---|
| Tbilisi | L8 | 23,252 | 622 mm | 761 mm | 1.22× | 63 | 93 | 1.48× | Local-dominant |
| Timbuktu | **L8** | **588** | 172 mm | 172 mm | 1.0× | 8 | 8 | 1.0× | **Small basin — undetermined** |
| Timbuktu | **L6** | **382,644** | 189 mm | 955 mm | **5.05×** | 9 | 47 | **5.2×** | **Exogenous water supply** |
| Cairo | L8 | 2,914,060 | 25 mm | 672 mm | **26.9×** | 1 | 36 | **36×** | **Exogenous water supply** |
| Baghdad | L8 | 134,983 | 161 mm | 583 mm | **3.6×** | 9 | 47 | **5.2×** | **Exogenous water supply** |
| Lima | L8 | 3,304 | 508 mm | 508 mm | 1.0× | 56 | 56 | 1.0× | Coastal terminal (dist_sink=0) |

**Does the instrument support the claim "a place's environmental character can be governed by
processes far outside it"?**

Yes, on Cairo and Baghdad, unambiguously. Cairo's local basin receives 25 mm/yr precipitation;
its upstream catchment averages 672 mm/yr (26.9×). Baghdad's local basin is semi-arid (161 mm/yr);
the Tigris-Euphrates headwaters deliver 583 mm/yr upstream (3.6×). These are the exact cases the
project summary uses as archetypes (Ur/Tigris-Euphrates). The panel fires correctly and the gloss
it would generate is the right one.

Timbuktu is a partial story. At L08, the assigned basin is 588 km² — a small unit within the
inland Niger delta that does not reach the Niger's headwaters. The small-basin caveat fires and
the provenance is "undetermined." At L06 the Niger upstream signal is fully resolved: 5× precipitation
ratio, clear "Exogenous" classification. This is itself a demo point: *the scale at which you ask
the question changes what the instrument sees.* But it means Timbuktu requires L06 for this panel.

Lima shows "Coastal terminal" (the basin terminates at the Pacific) rather than an orographic story.
The L08 basin is small and uniform — the Andean precipitation gradient would require a larger
upstream unit to appear. Lima is not a strong case for this panel.

**Best demo cases for the provenance panel: Cairo and Baghdad (L8). Timbuktu viable at L6.**

### 3. Global divergence ranking — feasibility

`precip_yr_upstream` and `precip_yr` are precomputed BasinATLAS columns in both `basin06` and
`basin08`. A global ranking by `precip_yr_upstream / precip_yr` (or aridity equivalent) is a
single SQL `ORDER BY` on a computed ratio — no aggregation, no join, no new data required.
**Feasibility: high; cost: trivial query.** A notebook using this ranking would immediately surface
allochthonous basins globally and is the right mechanic for extending the demo fixture set beyond
Cairo/Baghdad.

---

## Part 3 — Recommendation

| Component | Verdict | Reason |
|---|---|---|
| **Scale-mismatch alert** | **Drop from v3** | Does not fire on the canonical scale case (Tbilisi). MAUP story is already told by the level toggle (WO3). A redesigned version comparing L06 vs L08 values would be meaningful but is a Track-2 build, not a port. |
| **s/u divergence table** | **Port to v3** | Cairo and Baghdad produce compelling, correct results. Data arrives free with the existing signature fetch. Porting cost is low. Directly demonstrates "conditions at a distance" — the instrument's core methodological claim — in a form visible to a non-specialist. |
| **Water provenance badge** | **Port to v3** alongside divergence | Computed from the same inputs; adds the interpretive label the table alone doesn't provide. Together, divergence + badge make the allochthonous story readable without narration. |

**Note on v1:** `sandbox.html` can remain the demo vehicle for the provenance panel until v3 port
is done — it is public, all-green, and accessible. For a Braga demo at a table, v1 is viable for
this specific panel.

**Standing note:** The Timbuktu L08 / L06 divergence difference is itself a demo point worth
surfacing — at L08 the basin is too small to see the Niger; at L06 the signal is clear. This argues
for making the level toggle prominent when the provenance panel is displayed.
