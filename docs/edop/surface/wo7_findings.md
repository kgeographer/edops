# WO7 findings

**WO:** wo7_polity-search  
**Phase:** Surface  
**Branch:** surf_wo7

---

## F7.1 — Band T auto-fill belongs in `applySlice`, not only in the example handler

**Context:** After WO7 wired the search → slice flow, a manually searched polity (not
selected via the example dropdown) received no Band T auto-fill: the T checkbox stayed
unchecked, `from_year`/`to_year` were empty, and the signature call omitted Band T entirely.

**Root cause:** The example handler pre-filled T before calling `selectPolity` (correct),
but the manual search path hit `selectPolity` directly with no T pre-fill. `applySlice` was
the shared terminal point for both paths and was the right place to put the fill.

**Fix:** `applySlice` now auto-ticks Band T and sets `from_year`/`to_year` if T is not
already checked. The guard `if (!tCb.checked || !fyEl.value)` preserves an explicit pre-fill
(e.g., from the example handler) and does not clobber it when `selectPolity` finishes.

---

## F7.2 — Band T span must use the full polity lifespan, not the individual slice's dates

**Context:** The first Northern Song slice is 961–961 CE (one year). `applySlice` initially
used `s.fromyear`/`s.toyear` for the Band T span, giving `from_year=961, to_year=961`.

**Consequence:** A one-year window contains no HYDE time step (nearest steps are 900 CE and
1000 CE) and typically no eVolv2k event. LMR returned 1 row/variable (which the time
marginal suppresses: `rows.length < 2 → return ''`). Result: only LMR scalar, no HYDE, no
eVolv2k — despite all three being present when a reasonable span is requested.

**Fix:** When auto-filling, `applySlice` uses the full polity lifespan:
```javascript
const polityFrom = Math.min(..._politySlices.map(s => s.fromyear));
const polityTo   = Math.max(..._politySlices.map(s => s.toyear));
```
The resolver year (which boundary to use) remains `s.fromyear` (or the `targetYear` from the
example), and is kept strictly separate from the Band T aggregation span. This is the
two-temporal-axes invariant from the Areas locked decisions.

---

## F7.3 — `resolver_year` must carry `targetYear`, not always `s.fromyear`

**Context:** The Playwright test `test_nsong_polity` asserted `#v2-resolver-year = "1000"`.
But `applySlice` always wrote `s.fromyear`, which for the matching N Song slice is 990, not
1000. The API call would have used `year=990` — still valid (990 ≤ 990 ≤ 1017 is within the
slice), but inconsistent with what the example advertised.

**Fix:** `resolverYear` threaded as an optional parameter from `selectPolity` to `applySlice`:
- Example handler passes `targetYear=1000` → `v2-resolver-year = 1000`.
- Manual search or slice-change (no targetYear) → falls back to `s.fromyear`.

The distinction matters because `resolver_year` is the year the API uses to select the
polity boundary; it should reflect what the user (or example) asked for, not silently snap
to a slice endpoint.

---

## F7.4 — UX tweaks made at WO7 close

Three small polish changes applied after the search flow was working:

1. **Accordion default** — A–E bands render collapsed; Band T renders open. For polity
   queries where T is the primary interest, this avoids scrolling past 52 rows before
   reaching the temporal charts. Users click to expand any band they want to inspect.

2. **Map tab on polity change** — `selectPolity` and the slice-change listener both switch
   to the Map tab. When a new polity is selected or a different slice is picked, the user
   sees the new boundary before looking at the signature. Anticipates a more functional
   map tab (boundary paint + choropleth) arriving later; for now the boundary outline
   makes the re-orientation worthwhile.

3. **Spinner on signature load** — button click immediately sets the Signature pane to a
   Bootstrap spinner and switches to the Signature tab. Polity signatures (A–E + T, 372+
   rows) can take 2–3 seconds; without feedback the user has no confirmation the click
   registered. Button is disabled during the fetch and re-enabled in `finally`.

---

## F7.5 — HYDE epoch density: annual resolution post-~1950 will break the table layout

**Observation (from British East Africa, 1961–1972 CE):** HYDE 3.4 shifts to annual time
steps for recent decades. A polity bounded 1961–1972 returns 12 HYDE epoch columns; the
current table is borderline readable at 12. A polity spanning 1960–2000 would return ~40
annual columns, destroying the layout entirely.

**Why it happens:** HYDE steps are coarse for pre-modern periods (100-year intervals before
~1700, 50-year intervals 1700–1900, 10-year intervals 1900–1950, then annual 1950–2023).
A span wholly in the annual regime can generate O(span_years) HYDE rows per variable.

**Current state:** Acceptable for narrow spans (≤ ~15 epochs); breaks silently for longer
ones. No action in WO7 — the current HYDE table was designed around 2–3 epoch columns.

**Deferred:** UI compensation needed before the page is used with modern polities.
Options include: chart/sparkline for dense epochs (matches the LMR visual language);
decade-binned summary with an expand toggle; or a hard cap with a "N epochs — download for
full table" note. Add to deferred register.
