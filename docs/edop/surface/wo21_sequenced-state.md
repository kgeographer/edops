# WO21 — Sequenced state management: forward-or-reset

**Branch:** `surf_wo21`
**Type:** Build — state orchestration. **No new scopes or renderers** — this wires the *sequence*
over machinery that already exists (single, buffer, ring, polity, choropleth all work). Core of
Arc A (deployability): brings the scope control back safely by making state linear instead of
combinatorial.

Goal-setting, not a spec. The **model** below is the target; the **mechanism** (how reset tears
down layers, how the reveal/gate lifecycle is implemented) is CC's to work out — flag anything
harder than it looks and consult before forcing it.

## The governing invariant

**At any moment, exactly one entry path is live and one query is resolving. The only transitions
are forward (reveal the next control) or reset (back to cold start).** No mid-path changes — the
thing that required cross-control coordination (and produced the WO15 state chaos) is simply
forbidden. If a user is bored with the path they're on, they hit reset. This collapses the state
space from combinatorial to linear; that collapse is the whole point. **Start simple. State is a
tar baby — go slowly, don't get fancy.**

## Two tabs = the top-level fork

Settlements and Polities are the two forks (labels may change later). Reflect the wireframes
(`Sandbox_v2a.pdf`) exactly — they are intentional in every detail.

### Settlements tab

- **Cold start (frame 1):** WHG resolve field + "Load an example" dropdown. **No scope select. No
  variable select.** Bands present, T unchecked by default.
- **Resolve a place (frame 2):** map paints single-basin + marker; the **scope select appears**,
  defaulted to Single basin; Get signature activates (fetches sig, lands on Signature tab). The
  **example dropdown disappears** — committing to the resolve path removes the alternate entry.
- **Broaden (frame 3):** scope → Buffer or Ring renders over the **same held point**; ring's
  core+ring are clickable (hover→tooltip→signature), which is existing WO13 behavior re-homed, not
  rebuilt. Buffer's radius is adjustable; switching lenses keeps the point fixed.
- **Example path (frames 4–5):** choosing an example paints single-basin + enables Get signature;
  the **resolve field locks** (the example is the resolved state — the alternate entry is removed,
  mirror image of the resolve path).

### Polities tab

- **Cold start (frame 6):** autocomplete polity search + "Load an example" dropdown; time-slice
  select **visible but disabled**; **band select disabled**.
- **Resolve (example or search, frame 7):** slices fetched; on slice select, Get signature
  activates; **T auto-ticks** (a polity is inherently temporal — this asymmetry with Settlements,
  where T is off by default, is intentional: polity has a mandatory span, a settlement point does
  not). The example/search alternate entry removes on commit, same as Settlements.

### Orthogonal to both (the NB)

- **Variable select appears upon any rendering of a scope** — hidden at cold start, present once a
  scope has rendered, persists as the scope-independent global-paint modifier. Choosing a variable
  paints the global choropleth (existing behavior). It rides alongside the resolved query; it is
  not part of the query's state.

## What clears what (the three clears — settled)

1. **Tab switch → the abandoned tab hard-resets to cold start.** No preserved settlement, no
   preserved polity. Flip back and it's fresh (frame 1 / frame 6). Preserving cross-tab state is
   where chaos breeds — don't.
2. **Committing to a path removes the alternate entry.** Resolve → example dropdown disappears.
   Choose example → resolve field locks. One live entry per path.
3. **Reset → this tab returns to its cold start.** The universal undo-the-whole-path. Each fork
   needs a **reset control** (there is none today) — it's the only way back to the fork's start
   once you've begun, and the escape hatch that lets the forward-only model stay simple.

## Mechanism is CC's — but start simple

The reveal/gate lifecycle (which controls appear/enable/lock at each step), how reset tears down
map layers + choropleth + resolved state cleanly, and how the hard-reset-on-tab-switch is
implemented are **CC's to settle**. Start with the simplest thing that holds the invariant;
consult Karl if a state-management possibility looks worth weighing rather than forcing the first
approach. The existing sidelined scope-dropdown, the parallel-generator handlers from WO15's
audit, and the example-plumbing all get subsumed into this one model — this is the pass that
resolves the WO15 two-generator conflict for good.

## Out of scope

- No new scopes/renderers (draw-study-area, regions — later arcs).
- No Band-T temporal-paint changes (WO19 stands); no choropleth-mechanism changes.
- Fancy state (undo history, cross-tab preservation, mid-path editing) — explicitly not now.
- `sandbox.html` (v1) untouched.

## Accept gate

- Settlements: cold start → resolve → scope appears (Single default) → broaden to buffer/ring over
  the held point; example path locks the resolve field; matches frames 1–5.
- Polities: cold start with slice/bands disabled → resolve → slices + T auto-tick → Get signature;
  matches frames 6–7.
- Variable select appears on any scope render and paints global; absent at cold start.
- The three clears hold: tab switch hard-resets the abandoned tab; committing removes the alternate
  entry; reset returns the fork to cold start.
- One active entry path, one resolving query, at all times — no mid-path control changes possible
  (forward or reset only).
- Existing scope/choropleth machinery and `sandbox.html` untouched.

## Tests

- Playwright for the sequence: cold-start control visibility per tab; reveal-on-resolve; alternate-
  entry removal; tab-switch reset; reset-to-cold-start; variable-appears-on-scope-render. This is
  the suite that was skip-pending-state-model (F15.10) — **this WO is that state model**, so those
  skips should now un-skip and pass. Report which un-skip and which remain (if any) with reason.
- Engine/app suite green — zero FAILs, zero unexplained warnings. Note counts.

## Findings

`docs/edop/surface/wo21_findings.md`. Report: the reveal/gate lifecycle as implemented; how reset
tears down state; how tab-switch reset is handled; the Settlements-vs-Polities T asymmetry as
wired; which F15.10 skips un-skipped; any state-management possibility raised with Karl and what was
settled; anything that proved harder than the simple model expected.
