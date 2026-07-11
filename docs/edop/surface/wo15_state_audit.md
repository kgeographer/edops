# Sandbox v2 — State Audit
**Date:** 2026-07-06  
**Purpose:** Inventory every piece of state in sandbox_v2.html — what it is, what writes it, what reads it, whether it is ever cleared. Written so a reader can reason about conflicts without reading the code.

---

## JS state variables (declared at top of IIFE)

| Variable | Type | Default | Set by | Read by | Ever cleared? |
|---|---|---|---|---|---|
| `currentScope` | string | `''` | scope dropdown → `applyScope()`; example handler → `applyScope()` | sig button click; `updateSigButton()`; URL builders | No — overwritten only |
| `currentLat` | float\|null | null | Example handler (from the encoded `lat,lon` in option value) | URL builders; `drawSingleBasin`; `drawBufferGeometry`; ring fetch | No |
| `currentLon` | float\|null | null | Same as `currentLat` | Same as `currentLat` | No |
| `_politySlices` | array | `[]` | `selectPolity()` ← example handler or manual polity search | `applySlice()` (Band T auto-fill); `sliceSelect` options render | No |
| `_ringData` | null\|object | null | Sig button click (ring scope only) | `drawRingGeometry()`; ring hover/click handlers | No |
| `_centerPayload` | null\|object | null | Sig button click (ring scope only) | `renderCenterSig()` | No |
| `_lmrData` | null\|GeoJSON | null | `loadLMRData()` on first LMR select | `applyLMRChoropleth()`; `ensureLMRShellLayer()` | No — one-time cache |
| `_lmrPainting` | bool | false | `applyLMRChoropleth()` (concurrency guard) | `applyLMRChoropleth()` | Yes — reset in finally block |
| `_basinLayerLoaded` | bool | false | `loadBasinLayer()` | `loadBasinLayer()` | No |

---

## DOM state

These are values that live in form elements or element visibility/content rather than JS variables. They are set and read through the DOM; they persist across scope changes unless something explicitly clears them.

### Scope dropdown (`#v2-scope-select`)
- **Written by:** scope dropdown `change` listener → `applyScope()`; example handler (sets `.value` then calls `applyScope()` directly — does not fire the `change` event)
- **Read by:** nothing reads the DOM value at fetch time; `currentScope` (the JS var) is what drives the fetch
- **Cleared:** No. Changing examples overwrites it; manual scope change overwrites it.

### Band T checkbox and year inputs (`#v2-band-T`, `#v2-from-year`, `#v2-to-year`)
- **Written by:** example handler (ring, polity); `applySlice()` (polity — auto-fills from full lifespan)
- **Read by:** `updateBandT()` (controls row visibility); all URL builders (`buildSingleBasinUrl`, `buildBufferUrl`, `buildPolityUrl`); `fetchMemberSig()`
- **Cleared:** No. Once filled by an example or polity selection, these persist unchanged when scope changes to single/buffer/ring or a new scope is chosen.

### Polity input (`#v2-polity-input`)
- **Written by:** example handler; `selectPolity()`
- **Read by:** `buildPolityUrl()`
- **Cleared:** No.

### Resolver year (`#v2-resolver-year`)
- **Written by:** `applySlice()` (sets the year from the selected slice's fromyear)
- **Read by:** `buildPolityUrl()`
- **Cleared:** No.

### Slice select (`#v2-slice-select`)
- **Written by:** `selectPolity()` (populates options and selects idx)
- **Read by:** `applySlice()` on `change`; `applySlice()` called from sig button (polity scope)
- **Cleared:** No — overwritten on next `selectPolity()` call.

### Slice row visibility (`#v2-slice-row`)
- **Shown:** `selectPolity()` (sets `display = ''`)
- **Hidden:** implicitly by `applyScope()` which hides `#scope-extra-polity` (the parent); but the data inside remains intact

### Place input (`#v2-place-input`)
- **Written by:** example handler (display label only)
- **Read by:** nothing — it's display-only; `currentLat/Lon` drive actual fetches
- **Cleared:** No.

### Radius (`#v2-radius`)
- **Written by:** example handler
- **Read by:** `buildBufferUrl()`
- **Cleared:** No.

### Sig tab button (`#v2-tab-sig-btn`)
- **Disabled on load:** yes (has class `disabled`)
- **Enabled:** sig button click (removed before fetch, regardless of outcome)
- **Re-disabled:** never

### Intro text (`#v2-intro-text`)
- **Visible on load:** yes
- **Hidden:** sig button click (on success or draw-placeholder path)
- **Re-shown:** never

### Choropleth selector (`#v2-basin-var`)
- **Written by:** user selection
- **Read by:** change listener → `applyBasinVar()` or LMR paint
- **Cleared:** No — persists across scope changes, sig loads, scope switches, everything.

---

## Map layers (shell registry)

The shell (`_layers`) maps a name to `{ sourceId, layerIds }`. `shell.add(name, ...)` removes any prior layer with the same name before adding. Different names accumulate.

| Layer name | Added by | Removed by | Persists across scope change? |
|---|---|---|---|
| `single-basin` | `drawSingleBasin()` | `shell.add('single-basin', ...)` (next call replaces) | Yes — not cleaned up on scope change |
| `buffer-basins` | `drawBufferGeometry()` | Next `shell.add('buffer-basins', ...)` | Yes |
| `buffer-circle` | `drawBufferGeometry()` | Next `shell.add('buffer-circle', ...)` | Yes |
| `polity-boundary` | `drawPolityBoundary()` | Next `shell.add('polity-boundary', ...)` | Yes |
| `ring-center` | `drawRingGeometry()` | Next `shell.add('ring-center', ...)` | Yes |
| `ring-members` | `drawRingGeometry()` | Next `shell.add('ring-members', ...)` | Yes |
| `basin-choropleth` | `loadBasinLayer()` (lazy) | Never | Yes — permanent once loaded |
| `lmr-choropleth` | `ensureLMRShellLayer()` (lazy) | Never (only hidden/shown) | Yes — permanent once loaded |

**Key finding:** No cross-scope cleanup exists. After polity → ring, the polity boundary layer remains on the map simultaneously with the ring geometry. Same for any other sequence. Each call to the same scope overwrites its own layers but leaves other scopes' layers untouched.

---

## The two state generators

### Generator A — Example dropdown
Fires a batch update: sets `currentScope`, `currentLat/Lon`, place input display, Band T values. For polity scope, also calls `selectPolity()` which fetches slices and populates `_politySlices` and the slice select. Resets the dropdown to `''` after.

**What it does NOT reset:** prior scope's map layers; prior scope's stale slice/polity state if switching from polity to something else; `#v2-basin-var` choropleth selection.

### Generator B — Scope dropdown
Calls `applyScope(scope)` only. Updates: `currentScope`; shows/hides scope-extra panels and point section; calls `updateSigButton()`.

**What it does NOT touch:** `currentLat/Lon`; Band T values; polity name; slice options; map layers; choropleth selector.

---

## Conflict map

These are the specific state collisions that produce misleading UI.

### C1 — Stale coordinates after scope switch via dropdown
**Sequence:** Load Timbuktu buffer example → manually change scope to "ring" via dropdown.  
**Result:** `currentScope = 'ring'`, but `currentLat/Lon` still hold Timbuktu buffer coords from the example. Get Signature fires a ring fetch at Timbuktu — which happens to be correct, but only by accident. If you had typed a different place name into the input, `currentLat/Lon` would still be the example's coords.

### C2 — Stale Band T after scope switch
**Sequence:** Load Northern Song polity example (sets from=1000, to=1100) → switch to single-basin scope via dropdown → Get Signature.  
**Result:** single-basin fetch fires with `&from_year=1000&to_year=1100&bands=ABCDET` because `#v2-from-year` and `#v2-to-year` still hold polity values. The user sees Band T in the signature for a scope where it was not intentionally requested.

### C3 — Stale polity state after scope switch
**Sequence:** Load Northern Song → switch to ring via dropdown → Get Signature (ring) → switch back to polity via dropdown.  
**Result:** `_politySlices` still has Northern Song slices; `#v2-polity-input` still shows "Northern Song"; `#v2-resolver-year` still has the Song year. The polity scope appears pre-filled correctly, but if the user had changed the polity name in the input without selecting from the dropdown (i.e., typed something and pressed Enter), `buildPolityUrl()` uses the stale `_politySlices` year.

### C4 — Accumulated map layers across scopes
**Sequence:** Get signature for polity (draws polity boundary) → Get signature for ring (draws ring layers).  
**Result:** polity boundary + ring center + ring members all visible simultaneously. No visual collision between them, but the polity outline for a completely different query is shown alongside the ring result. There is no "clear previous scope geometry" step.

### C5 — Choropleth time/context mismatch
**Sequence:** Load Northern Song example (Band T 1000–1100) → select LMR temperature anomaly.  
**Result:** LMR paints using default year 1100 → notch MCA (950–1250 CE). Status reads "16,380 cells · MCA (950–1250 CE)". Band T row reads "1000–1100". These are numerically compatible by coincidence (1100 is in the MCA notch), but the choropleth is not actually reading from the Band T span. Change Band T to 500–600 and the choropleth does not update. The two are fully independent.

### C6 — Intro text persists through active map use
**Sequence:** Open page → select LMR variable → choropleth paints globally.  
**Result:** `#v2-intro-text` (which says "Select a scope, enter a location, choose bands, and click Get signature") remains visible below the choropleth controls while the map is actively showing data. The intro text is only hidden on sig button click, not on any choropleth interaction.

### C7 — Sig tab permanently enabled after first fetch
**Sequence:** Get signature for polity → switch to ring → change lat/lon → Get signature for ring.  
**Result:** Sig tab is permanently enabled after the first fetch and shows whatever the last rendered signature was. If Get Signature fails for the ring, the tab still shows the previous polity result. There is no "sig tab shows stale result" warning.

---

## What has no state at all

- **Whether a signature has been successfully loaded** — no flag. `_centerPayload !== null` is a proxy for "ring sig was loaded" but there is no general "last successful payload" variable.
- **What scope the last successful fetch used** — `currentScope` reflects the current UI selection, not the scope of what's displayed. These can diverge if the user changes scope after a fetch.
- **What the current map extent shows** — no state tracks what's in view. `fitBounds` fires on fetch but the map can be panned anywhere after.
- **Whether the choropleth is active** — `#v2-basin-var` value is the only record; there is no `_choroActive` flag or similar.

---

## Summary for design

The page has grown one WO at a time, adding state each round without a clearing strategy. The result is a page where:

1. **Two generators write the same state slots** (scope, Band T, coords) through different code paths with different coverage — the example handler writes a coherent bundle; the scope dropdown writes only scope.
2. **No scope change clears anything** — map layers, coordinates, polity data, Band T values all persist until explicitly overwritten by the next operation on that exact slot.
3. **The choropleth is fully decoupled from every other state dimension** — it has its own independent rendering loop that does not read or write any of the above.
4. **"Last fetched" state is not tracked** — the page cannot distinguish "params match what's displayed" from "params are stale relative to what's displayed."

Any fix needs to decide: is there a canonical "session" concept (one query at a time, scope change resets everything) or is mixing intentional (choropleth is global context, scope geometry is query result, these coexist)? Right now the code aspires to the second model but the clearing logic of the first model is missing — which is why sequences feel tangled.
