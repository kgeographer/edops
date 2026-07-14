# WO4b — Analysis tab: port provenance to v3

**Phase:** DEMO · Track 2 (demand-driven exposure)
**Kind:** Build (port) + summary. `sandbox_v3.html` Analysis tab.
**Branch:** `demo_wo4b` → merge to `demo` on accept.
**Precondition:** WO4a complete (`wo4a_findings.md`).

---

## Goal

Port the two v1 Analysis components that earned their place — the **s/u divergence table** and the
**water provenance badge** — into `sandbox_v3.html`'s empty Analysis tab, and write an honest
summary of what the tab does and what it might become.

**This is a port, not a redesign.** Do not invent new analysis. The one thing WO4a found worth
building rather than porting (a scale-sensitivity flag) is explicitly a roadmap row, not this WO —
see *Out of scope*.

---

## Why these two

The s/u divergence panel is the surface expression of the project's core methodological claim:
**a place's environmental character can be governed by processes far outside it.** That is
Goodchild's action-at-a-distance framing, and it is what distinguishes EDOPS from a
point-enrichment service. It is currently computed, correct, and buried in a v1 alpha tab.

WO4a confirmed it fires correctly on the archetype cases (upstream ÷ local):

| Place | Level | up_area | precip ratio | aridity ratio | Badge |
|---|---|---|---|---|---|
| Cairo | L08 | 2,914,060 km² | **26.9×** | **36×** | Exogenous water supply |
| Baghdad | L08 | 134,983 km² | **3.6×** | **5.2×** | Exogenous water supply |
| Timbuktu | **L06** | 382,644 km² | **5.05×** | **5.2×** | Exogenous water supply |
| Timbuktu | L08 | 588 km² | 1.0× | 1.0× | *Small basin — undetermined* |

---

## Scope

### 1. Port `sigVal` + the divergence/provenance block

Source: `renderAnalysis()` in `sandbox.html` (≈1090–1243); accessor `sigVal()` (≈537–545).
Both compute client-side from payloads v3 already fetches (`/api/signature`,
`/api/basin-preview`). `sandbox_v3.html` has the blank Analysis stub (`v3-pane-analysis`, ~414)
and already fetches the preview for Settlements (~993). Adapt to v3 variable names.

- **s/u divergence table** — precipitation, moisture index (aridity), temperature; local /
  upstream / ratio; existing colour coding (muted <10%, warning 10–30%, red >30% off unity).
- **Water provenance badge** + gloss — existing hierarchy: Endorheic → Coastal terminal →
  Exogenous water supply (ratio > 1.5×) → Catchment-uniform → Local-dominant.

**`sandbox.html` is public and all-green — read it, do not modify it.**

### 2. The level dependency — surface it, don't bury it

**This is the substantive addition to the port, and it is guidance, not decoration.**

WO4a read the Timbuktu L06/L08 split as a scale quirk. It is more general than that.
`precip_yr_upstream` is a BasinATLAS field computed over the basin's **own** upstream catchment.
At L08 most basins are small units whose upstream catchment barely exceeds themselves, so **s/u
divergence tends to unity by construction** — which is the mechanism behind the known tail
finding (median divergence ≈ 0 across all pairs). Cairo works at L08 only because it sits at the
bottom of the Nile with 2.9M km² above it; that is the exception, not the pattern.

**s/u divergence is substantially an L06 instrument.** Reflect that:

- When the panel is shown, make the **level toggle prominent** — it is the control that changes
  the answer.
- Replace the dead-end small-basin caveat. `"Small basin — undetermined"` states a fact and gives
  no way forward. Say **why, and what to do**: *this basin's upstream catchment is too small to
  resolve distant water — try L06.* (Wording is CC's; the requirement is that the caveat be
  actionable and explain the mechanism.)

### 3. Polity tab — test, do not assume

WO4a reports the panel *may* work on polities (`/api/area` returns `profile_groups` in the same
schema) but **did not test it**. Test it.

A provenance claim at **polity** scope would be strong — *"this empire's agricultural core ran on
water that fell outside it"* — but it is an unknown, not a promise. If the schema carries and the
values are meaningful, wire it. **If aggregating s/u across a polity's basins produces something
incoherent, say so and leave the panel Settlements-only.** A negative here is a finding, not a
failure; do not force it.

### 4. Summary (the (a) deliverable)

In findings, prose: what the Analysis tab now does, and what it might do. **Prose only — do not
design or build the "might."** WO4c (similarity research) may change what this tab should become,
and designing it now means designing it twice.

---

## Accept gate

- Analysis tab renders divergence + provenance in v3 for Settlements.
- **Cairo and Baghdad** show *Exogenous water supply* with correct ratios at L08.
- **Timbuktu at L06** shows *Exogenous water supply* (5×); at L08 the caveat explains the
  mechanism and points to L06.
- Polity behaviour reported either way.
- Full suite green (zero-tolerance: no FAILs, no unexplained warnings).
- Karl reviews before merge.

---

## Out of scope

- **Scale-mismatch alert — dropped.** WO4a is right: it detects size disparity (containing vs.
  largest adjacent `up_area`, 50× threshold), not semantic divergence. It **does not fire on
  Tbilisi** (ratio 1.4×), the canonical scale case. Do not port it.
- **Scale-sensitivity flag — roadmap, not this WO.** Its replacement is a genuinely useful
  instrument and Karl wants it: a *"this location is scale-sensitive"* tag computed as the
  **L06↔L08 signature diff**. WO3 already measured exactly this on Tbilisi (biome and ecoregion
  flip, aridity −30 pp, while `dist_sink` and upstream stats hold). It turns scale-conditionality
  from something the user must remember into something the surface reports — the second half of
  the Braga scale story. **It is a build, not a port. Add the roadmap row; do not build it here.**
- **Global divergence ranking** (`ORDER BY precip_yr_upstream / precip_yr`) — roadmap row. WO4a
  confirms it is a trivial query. Same mechanic as WO1a's spread ranking, new axis: it would *find*
  the allochthonous places rather than relying on the four we guessed. A notebook, later.
- Any new analysis, any redesign of the tab, any change to `sandbox.html` or `explorer.html`.

---

## Roadmap rows to add to `DEMO_tracker.md`

| Item | What | Status |
|---|---|---|
| Scale-sensitivity flag | *"This location is scale-sensitive"* tag from the L06↔L08 signature diff; replaces the dropped v1 scale-mismatch alert | pending |
| Global divergence ranking | Notebook: rank basins by `precip_yr_upstream / precip_yr` to surface allochthonous places globally | pending |
