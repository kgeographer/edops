# WO2 — Atomic rows-renderer against the single-basin fixture

**Branch:** Surface / sandbox v2 page
**Phase:** Surface · **Step:** 1 (of the build sequence in `surface_workflow.md`)
**Depends on:** skeleton (done); WO1 exemplar fixtures (done)
**Type:** front-end renderer, pure-fixture. No endpoint call. No engine change. Touches only
the new v2 page's own code.

## Hard constraint

**Nothing in this WO touches the live Lookup page (`sandbox.html`) or anything it uses** —
not its JS, not its routes, not its templates. Sandbox v2 is a separate page with its own
code. All work here is additive to v2.

## Goal

Build the **atomic rows-renderer**: the function that renders a `{rows[], neighborhood}`
signature payload into the Signature-tab band accordion, method-branching each row's leaf.
Prove it against the single-basin exemplar. This is the foundation every other `{rows[]}`
scope reuses, and (per DN8 path 3) the function the basin-ring deep-dive will delegate to — so
it is written **single-basin-atomic first**, with the multi-unit area case being the same
function over more rows.

Scope of "render" here: every method type in the fixture renders *something* correct and
non-throwing. Leaf-widget polish (nice histograms, range-bars, badges) is Step 2 / a later WO.
The accept gate is "renders without throwing, values land in the right band/row," not "looks
finished."

## Fixture source

`output/edop/surface/exemplars/` — the WO1-persisted payloads (verbatim engine output, real
DB, real entry points). Primary fixture for this WO: the **single-basin `&detail`** dump
(e.g. `01_single_basin_detail.json` — confirm exact filename in the dir).

**Why fixture is a valid proxy:** the exemplars are the unmodified return of the engine
callables the live `get_signature()` will invoke. Fixture and live differ only in transport
(a route serializing the same output), not in payload shape. Building against the fixture
builds against ground truth.

**Forward constraint (record for the later wiring WO):** when single-basin is HTTP-wired, the
route must return the callable's payload **unmodified** — serialize, do not transform (no
wrapping, renaming, or added envelope). If the route reshapes the payload, the fixture silently
goes stale and ceases to be a valid proxy. Serialize, don't transform.

## Build

**1 — fixture loader (dev harness).** A way to load a chosen exemplar JSON into the page
without an endpoint. Simplest: fetch the static file from `output/edop/surface/exemplars/` (or
import/hardcode for now). Wire the existing "Get signature" button to the loader for
single-basin scope, as a stand-in for the eventual live fetch. This is a harness, not the
final data path — keep it isolated so repointing at the live route later is a one-line change.

**2 — rows-renderer, atomic.** A function `renderSignature(payload)` that:
- reads `payload.rows[]` and groups by `row.band` into the A–E (and T, later) accordion
  (accordion shell already exists in the skeleton / carries the current sandbox pattern).
- for each row, dispatches on `row.method` to a leaf renderer.
- is written so a **single basin** (every row is one unit) is the natural atomic case; the
  multi-unit version is the identical path over rows with more units behind them. Do not build
  in an assumption of multi-unit area data.

**3 — method-branch leaf dispatch.** One branch per method present in the single-basin fixture.
Render each correctly but minimally (Step 2 makes them nice). Branch table (from DN7/DN9/DN10):

| `method` | Minimal render this WO | `raw` handling (DN7) |
|---|---|---|
| `area_weighted` | score + coherence text; histogram → placeholder slot (widget in Step 2) | `raw` is None — don't render it |
| `dominant_basin` | score + `raw` as physical value + carrier basin id | `raw` numeric |
| `class_mixture` | modal class label (from `raw`) | ⚠ `raw` is a **string label** — render as text, never format as number |
| `flag_fraction` | the fraction as-is | `raw` is fraction 0–1 |
| `distribution_only` | p10–p90 as text + suppressed-score with caveat label (DN4) | `raw` is None |
| `extreme` | score + `raw` physical value + carrier basin | `raw` numeric |

(Band T methods `grid_areal_distribution` / `global_forcing` are **out of scope this WO** —
single-basin fixture with A–E only. They arrive with the polity/Band-T step.)

**4 — header.** Basin title + level from the payload (`neighborhood` + whatever the
single-basin payload carries). JSON/API link can stub for now.

## Explicitly out of scope

- Any endpoint call or wiring. Fixture only.
- Leaf-widget polish — histogram SVG, range-bar, coherence badges as styled elements (Step 2).
- Band T (needs the polity fixture + trifurcated panel — later step).
- Multi-unit scopes (buffer/polity/polygon) — same renderer, later steps, not exercised here.
- Basin-ring — its own renderer (delegates back to this one), later step.
- Analysis tab content — later.
- `marginal_exposure` — absent on single-basin (DN5); nothing to render, must not throw on its
  absence.

## DN references honored

- DN7 — `raw` semantics branch by method; `class_mixture.raw` is a string (the throw risk).
- DN9 — histogram trigger is `row.method`, not a detail null-check (matters once the widget
  lands in Step 2; the dispatch built here is where that check lives).
- DN10 — `flag_fraction` has empty detail; render from row fields, don't look for a sub-dict.
- DN5 — `marginal_exposure` absence is normal for single-basin; guard, don't throw.

## Accept gate

- Single-basin `&detail` fixture loads via the harness and renders in the Signature accordion.
- Every `method` present in that fixture renders without throwing, in the correct band/row.
- `class_mixture` renders its string label as text (the DN7 throw case is handled).
- No reference to or effect on the live Lookup page.
- Karl reviews the write before it lands (review-before-write).

## Note on numbering

WO1 was the exemplar capture. This is WO2 (build Step 1). WO/step numbering need not be 1:1
going forward — steps may span multiple WOs or combine; the workflow sequence is the spine,
WO numbers just increment.
