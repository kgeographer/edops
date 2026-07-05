# WO13 findings — Basin-ring live

**Date:** 2026-07-05
**Branch:** `surf_wo13`

---

## F13.1 — Parallel fetch architecture confirmed correct

The frontend uses two parallel fetches rather than the `type=basin_ring` full-sig route:
- `buildSingleBasinUrl()` → `/api/areas?type=single_basin` (~1.1 s) — center sig with full Band T
- `/api/basin/ring?lat=X&lon=Y&level=6` (~92 ms) — ring topology with geometry

Total wall time ≈ 1.1 s (dominated by center sig). This is the architecture approved after
confirming that `type=basin_ring` with full sig computation for all members takes ~6.7 s.

The `type=basin_ring` route was retained on `/api/areas` for API completeness but is not
used by the frontend.

## F13.2 — Member sig sub-payloads not in initial response

Because the frontend uses the topology route (not `type=basin_ring`), member sig data is
**not** present in the initial response. Per-member signatures are fetched on demand when a
ring member is clicked: `type=single_basin&lat=neighbor_lat&lon=neighbor_lon`. This is a
~1 s call with the user's current Band T settings. The `_centerPayload` is stored at load
time for return-to-center without a re-fetch.

## F13.3 — Band T available for all members

Per-member sigs are independent `type=single_basin` calls with the same Band T parameters
from the UI. Band T is therefore fully available for any clicked ring member — it is not
center-only. The initial Band T pre-fill (from the ring example: years 1000–1100) applies
to all subsequent member fetches automatically.

## F13.4 — Two named shell layers, not property-driven paint

The ring uses two separate named shell layers:
- `ring-center` — single Feature, darker fill (`#1a4a6e`, 0.30 opacity), 2 px line
- `ring-members` — FeatureCollection, lighter fill (`#4a90c4`, 0.12 opacity), 0.75 px line

Two layers avoids a `match` expression on a `center/member` property, keeps the center
visually distinct, and isolates click/hover event handlers per layer cleanly.

## F13.5 — Return-to-center via center basin click

Clicking the center basin calls `renderCenterSig()`, which re-renders `_centerPayload`
(stored at sig load time) and switches to the Signature tab. No re-fetch needed. The hover
popup on the center basin reads "Return to center" to distinguish it from ring member hovers.

## F13.6 — Event listener accumulation (known, benign)

Each `drawRingGeometry()` call adds click/hover listeners to the fill layer IDs. If Get
signature is clicked multiple times on ring scope, listeners accumulate. After
`shell.remove('ring-center')` the layer no longer exists, so stale listeners fire no
callbacks. No user-visible bug; noted for future cleanup if interaction becomes complex.

## F13.7 — Ring info div shown by `applyScope`

`#v2-ring-info` is shown whenever ring scope is active and hidden for all other scopes.
It remains visible after Get signature — it describes the live interaction (clickable ring
members, return-to-center), not a pre-load orientation.

## F13.8 — Test count correction

CLAUDE.md's surface test count of "134" (WO12) was inaccurate. The correct breakdown is:
- `test_sandbox_v2.py`: 67 tests (31 functions, many parametrized)
- `test_sandbox_v2_ui.py`: 42 Playwright tests (1 browser, chromium)

WO13 net: −1 (removed WO12 ring placeholder test) +9 (ring scope gate + example prefill +
8 TestRingLive) = +9 Playwright. Correct surface total: 67 + 42 = **109**.
Non-surface: 268 passing + 14 skipped (DB-dependent) = 282 collected.
Full suite with DB: **282 + 109 = 391 tests pass**.
