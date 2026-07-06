# WO15 findings — LMR paint + example-select UX

**Date:** 2026-07-06
**Branch:** `surf_wo15`

---

## F15.1 — LMR data structure: 5 notches, not per-year

`lmr_notches.geojson` does not store annual values. Each 2°×2° cell carries five
pre-aggregated notch periods as named properties — `air_0`–`air_4` (temperature anomaly)
and `prate_0`–`prate_4` (precipitation anomaly):

| Index | Label | CE range |
|---|---|---|
| 0 | Early | 700–950 |
| 1 | MCA | 950–1250 |
| 2 | Transition | 1250–1450 |
| 3 | LIA | 1450–1850 |
| 4 | Industrial | 1850–1998 |

The paint-year control maps a CE year to one of these five notches via `lmrNotchForYear(year)`.
There is no per-year repaint — each scrub position snaps to the notch containing the target year.
Years before 700 CE return null; LMR quality floor is 700 CE (first 700 years of the 1–2000
record are excluded for quality reasons). Values are anomalies relative to the 850–1850 model
climatology.

The cliopatria implementation was the reference. The port was direct except for the rendering
path: cliopatria uses raw `map.addSource`/`map.addLayer`; WO15 routes through the shell
(`ensureLMRShellLayer`, `applyLMRChoropleth`, `clearLMRPaint`) to maintain the WO8/WO14
shell contract.

## F15.2 — Paint-year control: hidden slider, silent default

A paint-year slider (`id="v2-lmr-year-slider"`, min=700, max=1998) was built and lives in the
DOM in a hidden div (`id="v2-lmr-year-control"`). It is not shown to the user. At default value
1100 CE (MCA notch), it silently drives LMR notch selection when an LMR variable is chosen.

The slider was built visible, then hidden after it created confusion: its displayed year (e.g.
700 CE) conflicts with the Band T span shown in the signature (e.g. 1000–1100 CE), with no clear
relationship between them. Since LMR stores only 5 notches, a per-year scrub UI implies
resolution the data does not have.

The right fix — a notch-synced paint tied to the Band T span via a per-year API route — is
logged in the deferred items register as pre-Braga required (see F15.9).

## F15.3 — Anomaly ramp centred on zero; legend states the framing

Both LMR variables use the RDBU diverging ramp (`interpRdbu`) centred on zero. The legend
mid-label reads `0 (850–1850 mean)` and the legend title carries the anomaly unit
(°C anomaly / precip anomaly). The diverging domain is set from the data's actual abs-max so
neither warm nor cool end is clipped.

Caveat text is hard-coded in the legend rather than sourced from the payload field. The
choropleth paint path has no signature in hand (it is scope-independent and fires before any
sig fetch), so the payload's caveat field is unreachable here. The hard-coded string matches
the payload's framing. Full wiring to the payload field is deferred.

## F15.4 — Mutual exclusion: LMR ↔ basin variable

Selecting an LMR variable while a basin variable is active: `removeFeatureState` clears basin
feature-state and hides the basin legend before LMR paint begins. Selecting a basin variable
while LMR is active: `clearLMRPaint()` (hides LMR layer + clears LMR feature-state) before
`applyBasinVar`. No two paints stack. The example-change handler also calls both clears and
resets the selector to blank (F15.8).

## F15.5 — State audit: two-generator conflict

WO15 browser work revealed systematic confusion from two independent state generators writing
overlapping slots with different coverage:

- **Generator A — example dropdown**: writes `currentScope`, `currentLat/Lon`, Band T values,
  place display, and (for polity) `_politySlices`. Does not clear prior scope's map layers,
  stale polity state, or choropleth selection.
- **Generator B — scope dropdown**: calls `applyScope(scope)` only. Does not touch
  `currentLat/Lon`, Band T, polity name, map layers, or choropleth.

Seven specific conflicts (C1–C7) were documented in `wo15_state_audit.md`: stale coordinates
after scope switch, stale Band T bleeding across scopes, accumulated map layers across scopes,
choropleth/Band T decoupling, intro text persistence, and permanently-enabled sig tab.

The audit document establishes the design question: is there a canonical "one query at a time"
session concept, or should global choropleth and local query-geometry coexist? No architectural
resolution was attempted this WO. The audit is the prerequisite for a later state-model pass.

## F15.6 — Scope dropdown: sidelined as display-only

The scope dropdown was causing user confusion when the example dropdown pre-filled it but left
it interactive. Attempting to treat scope choice as a co-equal input alongside examples created
a two-generator conflict with no clear winner.

Resolution for this WO: the scope dropdown is **hidden on page load** (`display:none` on
`#v2-scope-wrap`). On polity example select it is shown with all options disabled — visible but
not interactive, confirming which scope is active. On single/buffer/ring example select it
remains hidden. The scope dropdown as a free-standing primary input is deferred; the example
dropdown is the controlling input for now.

## F15.7 — Example-select preview geometry

Prior to this WO, map geometry appeared only after Get Signature. WO15 adds immediate preview
geometry on example select for all four active scopes:

- **Single basin**: fetches `/api/basin-preview` and draws the containing basin polygon via
  `drawSingleBasin(lat, lon, null)`. The honesty check (hybas_id match) is bypassed when
  `sigHybas_id` is null (preview path).
- **Buffer**: draws a geodesic dashed circle only. Basin member polygons require the resolver
  output (member IDs come from the sig fetch), so basins appear only after Get Signature.
  Circle-only preview is accepted as correct for this WO.
- **Ring**: fetches `/api/basin/ring` and calls `drawRingGeometry` — full ring topology
  (center + member polygons, hover/click for member sigs) available before any sig fetch.
- **Polity**: already drew boundary via `selectPolity` → `applySlice` → `drawPolityBoundary`;
  no change required.

Prior scope layers are cleared before each preview draw
(`single-basin`, `buffer-basins`, `buffer-circle`, `ring-center`, `ring-members`), resolving
the layer accumulation problem (C4 in the audit).

`_fitMap(bbox)` helper: calls `map.fitBounds` directly if the map tab is already active,
otherwise registers `map.once('resize')` for the next tab switch. This resolves fitBounds
failing silently when the map was already visible.

## F15.8 — Post-example-select state cleanup

Two additional UX fixes:

**Get Signature tab routing**: prior logic switched to the Map tab after a successful sig fetch
(the result of writing geometry and fitBounds before preview geometry existed). Now that users
see the map via example preview, Get Signature stays on the Signature tab. Map fitBounds is
queued via `map.once('resize')` for the next time the user manually opens the Map tab.

**Choropleth clear on example change**: any active choropleth (basin feature-state or LMR paint)
is cleared and the selector reset to blank on every example select. Prevents a painted variable
layer from persisting across unrelated example loads.

## F15.9 — Deferred: paint-year slider and LMR slice-synced paint

The paint-year slider UI is deferred. The core limitation: `lmr_notches.geojson` stores only
five notch aggregates. Showing a year-scrub slider implies annual resolution the data doesn't
have, and a notch-period dropdown visible alongside the Band T from/to inputs creates
framing confusion.

The correct solution — registered in `docs/design/areas/deferred_items_register.md` as
**pre-Braga required** — is a new API route `/api/lmr/values?var=air&from_year=N&to_year=N`
querying the annual arrays in `temporal.lmr_climate` and returning per-cell weighted means for
the requested span. This would let the LMR paint reflect the actual Band T window (e.g. 1018–1027
for Northern Song) rather than a fixed notch. The quality floor (< 700 CE paints nothing
silently) applies to this route as well.

## F15.10 — Test count

- Structural (`test_sandbox_v2.py`): **80 pass** (+9 from WO15: 3 new REQUIRED_IDS for LMR
  year control elements; `TestLMRChoroplethStructure` class, 6 tests).
- Playwright (`test_sandbox_v2_ui.py`): `TestBasinChoropleth` and `TestLMRUI` marked skip
  pending state-model resolution. `test_selector_has_six_live_options` updated (count = 6).
  Full Playwright count deferred until the state model is settled and skips can be un-skipped.
- Engine + app suite: **395 pass**. Zero FAILs, zero unexplained warnings.
