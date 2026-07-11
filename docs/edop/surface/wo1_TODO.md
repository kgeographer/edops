# WO1 TODO — engine / API fixes arising from payload inspection

Source: `docs/edop/surface/wo1_findings.md` (F1.1–F1.13)
These are contract violations or misleading fields that should not survive a test.
Fix each with a corresponding contract test in `tests/engine/test_engine_contract.py`.

---

## TODO 1 — Clamp shortfall to zero in engine

**Finding:** F1.2, F1.12
**Location:** aggregator / wherever `shortfall` is computed before payload assembly
**Problem:** shortfall represents the fraction of area not covered by resolved basins.
It is a ratio and can never be negative. The aggregator returns -5.9e-05 due to
floating-point arithmetic in the area summation.
**Fix:** `shortfall = max(0.0, shortfall)` before the value is placed in the payload.
**Test:** add assertion `shortfall >= 0` to contract test suite; verify with S5 4-corners.

Status: **done** (commit 3a8f177)

---

## TODO 2 — Remove always-null `row["distribution"]` field

**Finding:** F1.9
**Location:** `engine.py` — row construction (wherever `_build_row` or equivalent assembles
the row dict)
**Problem:** every row carries a top-level `distribution` key that is always null, even in
detail mode. The histogram lives at `row["detail"]["distribution"]`. A developer reading
the row will attempt `row["distribution"]` and get null, missing the histogram entirely.
The field serves no purpose as currently populated.
**Fix:** remove `distribution` from the row-level keys entirely. Confirm nothing in
`app/`, `tests/`, or the UI reads `row["distribution"]`.
**Test:** add assertion that `"distribution" not in row` for a representative set of rows
(area_weighted lean, area_weighted detail, grid_areal_distribution detail).

Status: **done** (commit 3a8f177)

---

## TODO 3 — Document basin-ring top-level keys in contract tests

**Finding:** F1.2, F1.11
**Location:** `tests/engine/test_engine_contract.py` — `TestBasinRingSignature`
**Problem:** basin-ring top-level keys (`center, lat, level, lon, ring, type`) differ from
all other scopes — no `caveats`, no `shortfall`, no `rows`. This is correct by design
(composite of single-basin payloads, each with its own caveats), but there is no contract
test that asserts the exact key set. Without it, accidental addition or removal of
top-level keys would go undetected.
**Fix:** add assertion `set(payload.keys()) == {"center", "lat", "level", "lon", "ring", "type"}`
in `TestBasinRingSignature`.
**Test:** is the fix (no engine change needed — test only).

Status: **done** (commit 3a8f177)
