# WO2 findings — Step 1 diagnosis

Source: `notebooks/edop/demo/wo2_diagnosis.ipynb` (Cells 1–11)

---

## D1 — LMR paint mechanism: slice-synced, not notch-period

**Finding:** The `/api/lmr/values` endpoint already aggregates per arbitrary span:
`AVG(v) FROM unnest(var[from_year:to_year])`. The WO1 fix wired `applySlice()` →
Band T inputs → `_activeBandTYears()` → `applyLMRChoropleth()` → `/api/lmr/values`,
so the paint is already slice-synced at the data level.

The panel header label "LMR v2.1 · 2°×2° native grid · Early (700–950 CE)" is a stale
notch-period string — it does not reflect what the query actually computes.
The data is correct; the label needs updating in Step 2.

**Consequence for Step 2b:** the paint path does not need to be rewritten. What remains
is hiding the Band T inputs (so the user cannot override the slice-sourced values) and
fixing the panel label. The full notch-less path is already operational.

---

## D2 — LMR floor: 700 CE, hardcoded in the route

`/api/lmr/values` (routes.py): `actual_from = max(from_year, 700)`. If `actual_from > to_year`
the endpoint returns `{"values": {}}` immediately.

`temporal.lmr_climate` holds arrays of length 2001 (1–2001 CE, 1-indexed). The 700 CE floor
is a quality threshold in the route, not a data boundary. A notch-less query could in principle
reach back to 1 CE, but the current route enforces 700.

**Before the fix:** notch periods started at 700 CE (the pre-aggregated file's floor).
**After the fix:** same effective floor — 700 CE, enforced by the route. The floor moves only
if the route is changed. Do not change the route for this WO; record it as a deferred item if
earlier coverage is wanted.

---

## D3 — Zero-width slices: work correctly

`875 CE – 875 CE` (a cartographic instant): PostgreSQL `array[875:875]` returns a
single-element array; `AVG` of one value is valid and returns that value. Spot-check confirmed
correct output. Zero-width slices are not a special case and require no guard.

---

## D4 — Band T inputs: already hidden by default; revealed at two points

Cell 11 audit of `sandbox_v3.html`:

| ID | Occurrences | Role |
|---|---|---|
| `v3-polity-from-year` | 6 | L278 def · L454/1692 read (areas request builder) · L1535 clear · L1655 write (applySlice) · L2026 read (_activeBandTYears) |
| `v3-polity-to-year` | 6 | Same pattern |
| `v3-polity-t-year-row` | 4 | L275 def (starts `d-none`) · L1514 toggle (Band T checkbox) · L1537 hide · L1624 show |

**The row already starts hidden** (`class="d-none mb-2"`). It is revealed at:
- **L1514** — `classList.toggle('d-none', !tChecked)` when the Band T band checkbox is ticked
- **L1624** — `classList.remove('d-none')` explicitly

The inputs themselves hold values (written by `applySlice()`, read by the areas request builders
and `_activeBandTYears()`) whether or not the row is visible. Hiding permanently on the
Polities tab is safe — the values flow correctly through hidden DOM elements.

**Step 2 action:** condition L1514 and L1624 on current tab. On Polities tab, never reveal the
row. The Band T checkbox can still gate Band T variable selection; the year inputs just become
read-only plumbing that mirrors the slice.

**Current user-override risk:** while the row is visible a user can type a different year range
and the choropleth will honour it. Hiding eliminates this; it is the correct behaviour on the
Polities tab (the span is the slice, not a user choice).

---

## D5 — Period vs. slice discrepancy: labelling artifact

The `v3-polity-period` label (e.g. "Northern Song 1000–1100 CE") comes from
`/api/polity/period`, which returns a rounded historical period name. The active slice span
comes from `gaz.clio_polities` directly. A slice can start before or after the period label.

**Not a defect.** The slice bounds are authoritative; the period is a display convenience.
No code change required; document it as a known labelling artifact.

---

## D6 — BCE polities (Qin): not LMR-demoable

All Qin Dynasty slices are BCE (−750 to −209 CE). The `/api/lmr/values` floor check
(`actual_from = max(from_year, 700)`) means any BCE polity → `actual_from > to_year` →
empty dict → no LMR paint.

HYDE (10,000 BCE coverage) and BasinATLAS are unaffected. Qin is demoable on those variables.
Qin is confirmed on the shortlist by WO1a median-drift ranking and remains a Tier 1 aridity
candidate; it simply cannot be an LMR hero shot.

**Coverage guard required (Step 2c):** disable LMR variables in the variable selector for
polities whose entire lifespan is below the LMR floor. Reason string surfaced in UI.

---

## D7 — LMR spatial spread across extensive polities

### `prate` (precipitation anomaly): spatially flat

| Polity | Slice | n_cells | prate spread |
|---|---|---|---|
| Abbasid | 751–799 | 197 | ~1×10⁻⁶ |
| Tang | peak slice | ~180 | ~6.7×10⁻⁷ |

Near-zero variation. `prate` carries no useful choropleth signal at polity scale.

### `air` (temperature anomaly): real signal

| Polity | Slice | n_cells | air range |
|---|---|---|---|
| Abbasid 751–799 | 197 cells | 14–42°N, 2–72°E | −0.175 to +0.040 K (spread 0.215 K) |
| Tang | varies by slice | — | varies (0.118–0.171 K at peak extents) |

`air` shows genuine spatial variation across large polities. The 2°×2° cell granularity, coarse
for compact polities, is adequate at continental extent — the signal justifies the resolution.

**Hero-shot class confirmed:** the "extent" class — *"this empire was large enough that the
climate anomaly of its era hit its provinces differently"* — is real for continental-scale
polities painting `lmr_temp_anomaly`. This rehabilitates Abbasid, Tang (in its LMR-reachable
slices), and similar continental cases that scored poorly on aridity gradient.

### Tibetan Empire floor classification

| Slice range | CE span | Count | LMR status |
|---|---|---|---|
| 623–691 | below floor | 11 | EMPTY |
| 692–704 | straddle | 1 | partial (clips to 700) |
| 705–849 | full | 13 | LMR-available |

~44% of the polity's lifespan has no LMR paint. A slider will land users in the empty zone.
**Partial-overlap guard required (Step 2c):** the slider marks where LMR data begins; scrubbing
below the floor explains itself rather than silently blanking.

### Tang floor asymmetry

Tang's territorial peak (661–665 CE, 1075 basins) is entirely below the 700 CE LMR floor.
The LMR-reachable peak is 751–754 CE — only 562 basins, post-An Lushan contraction.
Tang as an LMR hero shot requires narrating around this: the empire at its painted maximum
is smaller than its historical maximum.

---

## D8 — Step 1 summary: what Step 2 inherits

| Item | Status | Step 2 action |
|---|---|---|
| LMR paint notch vs. slice-synced | Already slice-synced (WO1 fix) | Fix stale panel label only |
| LMR floor | 700 CE, route-hardcoded | Coverage guards key off 700 |
| Zero-width slices | Work correctly | No action |
| Band T inputs | Row hidden by default; revealed at L1514, L1624 | Condition reveal on tab; never show on Polities |
| Period/slice label | Known labelling artifact | Document, no code change |
| BCE polities | Empty LMR; HYDE/BA still work | Disable LMR selector + reason string |
| `prate` spatial signal | Flat (1e-6 range) | Do not offer as LMR hero variable |
| `air` spatial signal | Real (0.1–0.2 K range) | Confirmed hero variable for continental polities |
| Tibetan Empire partial overlap | 44% below floor | Partial-overlap guard: explain, don't blank |
| Tang territorial peak | Below floor; LMR-reachable peak is smaller | Narration note; no code change |

---

## Status

Step 1 complete. All eight diagnosis items answered. Findings gate the build.
Step 2 may begin: 2a (slider + VCR), 2b (hide Band T inputs + fix label), 2c (coverage guards).
