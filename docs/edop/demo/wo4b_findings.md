# WO4b findings — Analysis tab: port provenance to v3

**Date:** 2026-07-13
**Branch:** `demo_wo4b`

---

## What was built

The s/u divergence table and water provenance badge from v1's Analysis α tab are now live in
`sandbox_v3.html`'s Analysis tab, Settlements path only.

### Implementation notes

**Data source mismatch discovered:** `/api/areas` (v3's signature endpoint) returns
`representative_score` (0–100 normalized) with `representative_raw: None` for all
divergence-relevant fields. Raw values (mm/yr precipitation, P/PET aridity index, °C temperature)
required for meaningful ratios are only available from `/api/signature`. Solution: a parallel fetch
to `/api/signature?lat=X&lon=Y&level=N&bands=ABCE` is kicked off at the top of the Settlements
"Get Signature" handler alongside the existing `/api/areas` call. Zero added latency; stored in
`_pointSig`.

**`sigVal(sig, key)`** ported from v1 — traverses `sig.profile_groups[band].items[].key`; works
on the `/api/signature` response format.

**`renderAnalysis(sig, level)`** ported from v1 with two substantive changes:
- Scale-mismatch alert **dropped** per WO4a recommendation and spec.
- Small-basin caveat made **actionable**: instead of "undetermined," now explains the mechanism
  ("upstream catchment too small to resolve distant water sources by construction") and directs
  the user to switch to L06.
- Level note added at top of panel: reminds the user that s/u divergence is substantially an
  L06 instrument and points to the Level selector.

**Reset behaviour fixed:** example-select `change` handler now calls `_resetRightColumn()` before
updating coords — previously the analysis pane would linger when switching between examples.

**`_resetRightColumn()`** extended to null `_pointSig` and restore the analysis pane placeholder.

---

## Accept-gate verification

### Cairo at L08 — Exogenous water supply

- `precip_yr`: 25 mm/yr local, 672 mm/yr upstream → **26.9×** (red, fw-semibold)
- `aridity`: 1 local, 36 upstream → **36×**
- Badge: **Exogenous water supply** ✓

### Baghdad at L08 — Exogenous water supply

- `precip_yr`: 161 mm/yr local, 583 mm/yr upstream → **3.62×**
- `aridity`: 9 local, 47 upstream → **5.22×**
- Badge: **Exogenous water supply** ✓

### Timbuktu at L06 — Exogenous water supply

- `precip_yr`: 189 mm/yr local, 955 mm/yr upstream → **5.05×**
- `aridity`: 9 local, 47 upstream → **5.22×**
- Badge: **Exogenous water supply** ✓

### Timbuktu at L08 — actionable small-basin caveat

- `up_area`: 588 km² (below 5,000 km² L08 threshold)
- Badge: **Undetermined**
- Caveat: explains small-catchment mechanism; directs user to L06 ✓

---

## Polity tab — Analysis is an open design question

The polity signature (`/api/areas?type=polity`) does return `precip_yr_upstream`,
`aridity_upstream`, `temp_yr_upstream` — but these are **area-weighted means of each member
basin's own upstream value**, not a measure of "how much of this polity's water fell outside its
borders." Those are different questions. A polity whose interior basins all have high upstream
values might be well-watered throughout; or it might straddle a drainage divide. The naive ratio
would be misleading.

What the Analysis tab should show for a polity — and whether the upstream fields are useful at all
at polity scope — is an open design question, tracked in DEMO_tracker.md. The Polities tab Analysis
pane is left with the default "Run Get Signature to populate analysis" placeholder.

---

## Roadmap rows added to DEMO_tracker.md

- Analysis tab polity scope — pending design
- Scale-sensitivity flag (L06↔L08 diff) — pending
- Global divergence ranking notebook — pending
