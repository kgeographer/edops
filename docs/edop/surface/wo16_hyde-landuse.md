# WO16 — HYDE land-use raster overlay

**Branch:** `surf_wo16` → merge to `surface` at accept gate.
**Type:** Build — the raster-overlay mechanism. Last of the four selector groups goes live.

This WO is goal-setting, not a spec: exact reuse (which existing sandbox code ports, how the
epoch logic is structured) is discovered in implementation, where it's actually knowable. Targets
and provisos below; particulars to CC's read of the code.

## Goal

Bring the two HYDE variables live in the selector — cropland fraction, grazing fraction — as a
**raster tile overlay** (`/static/explorer/hyde_tiles/…/{z}/{x}/{y}.png`), opacity-controlled,
driven by the WO15 paint-year control snapping to HYDE's epoch steps. This completes the four-group
menu; every variable in the dropdown paints.

## The new mechanism

HYDE is unlike both prior paints. Not feature-state (basin), not static-vector (LMR) — a
semi-transparent **raster overlay** on the basemap. No values route, no p10–p90 domain, no
per-feature colour: pre-baked PNG tiles per epoch, added as a raster source/layer through the
shell, with an opacity control. The colour encoding is baked into the tiles. That's the one
genuinely new thing in WO16; the rest inherits.

## Reuse, don't reinvent

- **Epoch-resolution logic already exists in the current sandbox.** HYDE's temporal resolution
  shifts (coarse steps early, annual post-~1950 — the F7.5 observation). The sandbox already has
  logic that sorts out which HYDE epoch/tile-set applies for a given year. Resurface it and reuse
  it; do not rebuild epoch handling. Report where it lived and how it maps a year → epoch/tileset.
- **Year control inherits from WO15.** The paint-year control built in WO15 drives HYDE too — the
  target year snaps to the nearest HYDE epoch (as it snaps to an LMR notch). Same control, same
  hidden-default interim state; WO16 adds HYDE as a consumer of it, doesn't touch its UI status.

## Temporal honesty — match LMR's interim treatment, don't reopen it

HYDE has the same span-vs-epoch temporality LMR had: fixed time steps, the year control snaps to
one, not a true span-synced paint. This was already settled for LMR (F15.2/F15.9): paint the step,
label the step, defer the span-synced version to the later temporal pass (the `/api/lmr/values`-style
route, pre-Braga-required). **Apply the same treatment to HYDE — no new decision.** The HYDE
overlay's legend/label states the epoch it's showing (e.g. "cropland fraction, 1000 CE" or the
epoch range the tileset represents), so the encoding states its own time even while the control to
change it stays deferred. Consistent with LMR; recorded as **for now**.

## Left as live refinement (not a WO16 gate)

Layer stacking and legibility — HYDE is a raster over the basemap and possibly over/under vector
paints — is an acknowledged soft spot Karl is working through with CC directly, same as LMR's
legibility (F15.x). WO16 should make a reasonable default z-order and opacity, but **stacking
legibility is not an acceptance condition** here; it's a known refinement pass, not a bug to close
in this WO. Report the default chosen so the refinement pass has a starting point.

## Coexist vs. exclusive — default exclusive, flag if it fights the mechanism

Basin↔LMR are mutually exclusive paints (F15.4). Default HYDE into that same one-paint-at-a-time
model — selecting HYDE clears any active basin/LMR paint, and vice versa — keeping WO16 inside the
state model WO15 stabilized. **Proviso:** HYDE being a raster overlay rather than feature-state may
make coexistence trivially easy (a raster layer and a vector paint don't contend for feature-state
the way two vector paints would). If, in implementation, exclusive turns out to be *more* work than
letting the raster coexist, surface that — it's a case where the mechanism might argue for
coexistence and it's worth Karl knowing rather than forcing exclusivity against the grain. Don't
decide it silently either way; report which and why.

## Deliberately not in this WO

- Span-synced temporal paint (the values-route fix) — the later temporal pass, for LMR and HYDE
  together.
- Paint-year control UI (still the WO15 hidden/deferred state).
- Stacking/legibility refinement — Karl + CC, separate pass.
- L8 — L6 only (HYDE tiles are their own grid regardless).

## Accept gate

- Both HYDE variables paint as a raster overlay from the tile path, opacity-controlled.
- The year control drives HYDE via the existing epoch-resolution logic (reused, not rebuilt);
  changing the year moves HYDE to the corresponding epoch tileset.
- Epoch label in the legend states the time the overlay shows.
- HYDE clears/coexists with basin/LMR paint per the reported decision — no silently-stacked
  confusion.
- Basin (WO14), LMR (WO15), scope geometry, and `sandbox.html` untouched.

## Tests

- Given the Playwright choropleth suite is currently skip-pending-state-model (F15.10), match that
  status honestly: add HYDE UI coverage in the same suite, skipped under the same trigger if the
  others still are, so HYDE isn't the one interactive surface with *no* test written (even if
  parked). Don't leave it uncovered silently — a written-but-skipped test is a recorded debt; no
  test is an invisible gap. Note it in findings.
- Any non-UI structural coverage (REQUIRED_IDS for HYDE controls, epoch-mapping unit test if the
  resurfaced logic is unit-testable) that *can* run, should.
- Engine/app suite stays green — zero FAILs, zero unexplained warnings. Note counts.

## Constraints

- Review before write — Karl signs off each write.
- Shell API for the raster source; keep the shell contract intact.
- Reuse the existing HYDE tiles and epoch logic read-only; don't modify shared paths.
- `sandbox.html` untouched.

## Findings

`docs/edop/surface/wo16_findings.md`. Report: where the epoch-resolution logic lived and how it
maps year→tileset; how much HYDE code ported from the current sandbox vs. adapted; the exclusive-vs-coexist
decision and why the mechanism pointed that way; the default z-order/opacity chosen (starting point
for the legibility pass); the epoch-label form; test status (which HYDE tests run vs. skip-pending).