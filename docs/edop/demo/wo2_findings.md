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

Step 1 complete. All eight diagnosis items answered.

---

# WO2 findings — Step 2 build

---

## S1 — No-detents slider: label snaps, handle does not

The WO spec said "draggable, no detents." Implementation separates two concerns:
- **Label**: updates on every `input` event (drag) to nearest slice — gives live feedback
- **Data**: commits on `change` event (release) to nearest slice
- **Handle position**: never moved programmatically after initial load — stays where user released

This means the handle position does not snap to slice positions; users feel smooth drag.
VCR buttons (`⏮ ◀ ▶ ▶|`) do move the handle (they set `slider.value` explicitly before
calling `applySlice`), giving crisp single-step movement.

`_polityCurrentIdx` tracks the committed slice index; `updatePolityButton()` gates on
`_polityCurrentIdx >= 0` (not on the old select value).

---

## S2 — Hidden select retained for test compatibility

`#v3-slice-select` is kept in the DOM as `class="d-none"` and is still populated with
slice options and enabled/disabled correctly. Playwright tests that reference it by ID
(`select_option`, `is_disabled`) continue to work without modification. The hidden select
is not user-facing.

---

## S3 — Band T year row: permanently hidden on Polities tab

`v3-polity-t-year-row` starts `d-none` and is never revealed. The reveal logic that
previously fired on Band T checkbox click (`updatePolityBandT`) is removed entirely.
Hidden inputs still hold values written by `applySlice()` and read by the sig button
and `_activeBandTYears()`. The DOM element approach allows full test coverage without
exposing the controls to users.

---

## S4 — Coverage guard: two tiers

**Polity-level** (`selectPolity`): `hasLMR = slices.some(s => s.toyear >= 700)`. If all
slices are BCE, LMR options in `#v3-basin-var` are disabled immediately on polity load
with the message "LMR data begins 700 CE — this polity predates the record."

**Slice-level** (`applyLMRChoropleth`): fires when a straddle polity (e.g. Tibetan
Empire, hasLMR=true) is on a sub-700 CE slice. `/api/lmr/values` returns `n=0`;
the guard message is "LMR data begins 700 CE — this slice (FROM–TO) predates the record."

The two guards are independent and additive. A straddle polity starts with LMR enabled
(polity guard passes), then shows the slice guard when scrubbed below the floor.

---

## S5 — HYDE in signature: nearest-year fallback (engine fix)

**Finding:** `aggregate_band_t` used `WHERE year_ce BETWEEN from_year AND to_year`.
HYDE's centennial cadence means any narrow polity slice (e.g. 961–961, –318 to –316)
has zero matching epochs. Band T was therefore absent or HYDE-free for the majority of
polity slices, regardless of HYDE's actual historical coverage.

Confirmed via Maurya Empire screenshot: 318–316 BCE slice returned Bands A–E only.

**Fix:** `epochs` CTE split into `in_span` + fallback. When `in_span` is empty, the
nearest HYDE step is selected with `ORDER BY ABS(year_ce - mid) LIMIT 1`. Fallback rows
carry `hyde_nearest_year` caveat. `renderTBand` marks fallback epochs `~YEAR CE` and
adds a footnote.

**Invariant preserved:** wide spans that already straddled exact HYDE steps are unchanged
(fallback's `WHERE NOT EXISTS (SELECT 1 FROM in_span)` prevents duplication).

---

## Status

WO2 complete. 4 commits on `wo2`. 580 tests pass, 50 skipped.
Accept gate: Karl browser review → merge `wo2 → demo`.
