# Surface page — state fallout from "Select a scope"

**Purpose:** map what the scope choice actually changes downstream, so the page is built
around the axes that vary rather than an enumerated grid of scope × tab states. The claim is
that the apparent combinatorial explosion collapses to **two renderers plus a small set of
conditional sections that switch on what the payload contains at runtime.**

**Source of truth:** WO1 findings (F1.1–F1.13) and design notes (DN1–DN10), against the five
persisted exemplar payloads. Everything below is keyed to observed payload structure, not
predicted schema.

---

## The two axes that actually drive variation

Not five scopes × three tabs. Two axes:

**Axis 1 — payload shape.** Two values:
- `{rows[], neighborhood}` — single-basin, buffer, polity, polygon (four scopes)
- `{center, ring[]}` — basin-ring (one scope, the exception)

**Axis 2 — Band T present.** Boolean, orthogonal to scope. Any `{rows[]}` scope may or may not
include Band T depending on whether T was ticked (and, per DN3, whether the call was
`&detail`).

Everything else is a **conditional section** whose presence is readable from the payload:
- `marginal_exposure` present ⇔ polygon-path (polity, polygon) — DN5
- s/u divergence present ⇔ single-basin (and the `center` of a ring) — Analysis tab
- histogram present ⇔ row method ∈ {`area_weighted`, `grid_areal_distribution`} — DN9
- per-method leaf widget ⇔ `row['method']` — DN7

So the design surface is: **two renderers** (rows-table, ring) × **conditional sections keyed
to field/method presence**. The page reads the payload and shows what's there; it does not
switch on "which scope" beyond selecting the renderer.

---

## Left column fallout (scope → input controls)

The scope dropdown gates which input controls appear. This part *is* scope-keyed (it's the
input side, before any payload exists):

| Scope | Point input | Extra control | Temporal controls (if T ticked) |
|---|---|---|---|
| Single basin | WHG lookup / lat,lon | — | Band T span (from/to) |
| Buffer | WHG lookup / lat,lon | radius_km | Band T span |
| Basin ring | WHG lookup / lat,lon | — | Band T span |
| Polity | polity search | period picker → resolver_year | Band T span **and** resolver_year (two axes, DN1) |
| Draw study area | (none — map draw / upload) | draw affordance on Map tab | Band T span |

Note the temporal-control asymmetry: only **polity** shows two temporal controls (resolver_year
+ Band T span), because it's the only scope with a moving boundary. All others show at most the
Band T span. This is the locked "two axes must present distinctly" constraint — and it only
bites for one scope, which bounds the UI problem.

---

## Right column — Map tab fallout

| Scope | Map behavior |
|---|---|
| Single basin | containing basin highlighted + ring preview (existing behavior) |
| Buffer | buffer circle + intersected basins |
| Basin ring | center + ring members drawn (existing preview already does this) |
| Polity | boundary overlay (from `/api/polity/geom`) on the global tileset; variable choropleth + time slider |
| Draw study area | draw rectangle/freehand → polygon; then intersected basins |

The map is bidirectional for draw-study-area (input capture) and for polity (the slider picks
the choropleth year — a *different* year-control than the Signature-tab envelope cursor; keep
them independent per the temporal-axis discussion).

---

## Right column — Signature tab fallout (the core)

**Renderer selection (Axis 1):**
- `{rows[]}` → **rows-renderer** (shared by four scopes)
- `{center, ring[]}` → **ring-renderer** (DN8; its own thing, no shared rows table)

### Rows-renderer — one function, method-branched leaves

Band accordion (A–E, T) as container, unchanged. Each row's leaf dispatches on `row['method']`
(DN7, DN9). The leaf types, from the exemplars:

| `method` | Leaf widget | `raw` (DN7) | Histogram? (DN9) |
|---|---|---|---|
| `area_weighted` | score + coherence badge; histogram in detail | None | yes |
| `dominant_basin` | score + which basin carried it | physical value | no |
| `class_mixture` | modal class label + mixture bar | **string label** ⚠ | no |
| `flag_fraction` | plain fraction / binary indicator | fraction 0–1 | no (DN10: empty detail) |
| `distribution_only` | **range-bar** p10–p90 + regime breakdown (DN4) | None | no — range-bar, not histogram |
| `extreme` | carrier-basin score | physical value | no |
| `grid_areal_distribution` | Band T time-series (see Band T sub-panel) | — | yes |
| `global_forcing` | eVolv2k event row (DN10) | — | no |

⚠ `class_mixture.raw` is a string, not a number — the leaf must branch before formatting or it
throws. This is the sharpest DN7 case.

**Conditional within the rows-renderer:**
- Histogram widget appears iff method ∈ {`area_weighted`, `grid_areal_distribution`} — trigger
  on method, not on detail-null-check (DN9).
- `distribution_only` gets a range-bar + `suppressed_score` shown with a "score suppressed —
  bimodal" caveat, never as headline (DN4).

### Band T sub-panel (Axis 2) — trifurcated (DN6)

Present only when T is in `bands` and the call was `&detail` (DN3 — lean has `score=None,
detail=None` for Band T rows, so the panel *must* trigger a detail request). Three substrates,
three widgets, shared time axis:

| Substrate | Method | Widget | Notes |
|---|---|---|---|
| LMR (3 vars, annual) | `grid_areal_distribution` | envelope: mean line + p10/p90 band | p10/p90 = spatial spread across polity, meaningful; dimensionless |
| HYDE (4 vars, epochs) | `grid_areal_distribution` | step/bar per variable | values in km² — unit label required |
| eVolv2k (events) | `global_forcing` | spike/event timeline | primary field `vssi` (Tg SO₂); `location` labels events |

The LMR envelope doubles as the local time scrubber: scrub a year on the envelope → the value
histogram at that year updates. This is the Signature tab's own year-control, independent of
the Map tab's choropleth slider.

For single-cell scopes (single-basin) the envelope band collapses to a line — the same widget
degenerates to the old single-cell chart. One widget, both cases.

### Ring-renderer (Axis 1, the exception)

No top-level `rows` (DN8). Its own display, three viable paths (combinable):
1. comparison table — center + N ring members as columns, one row per variable; `border_bearing`
   gives clockwise column order.
2. schematic compass — center + neighbors at bearing; `shared_km` → edge weight; `sub_area_km²`
   → glyph size. **Do not weight neighbors equally** — size varies extremely (921 vs 24,966 km²).
3. per-member deep-dive — select a member → render its full signature via the single-basin
   rows-renderer (all data present in `member.signature`).

Path 3 means the ring-renderer *reuses* the rows-renderer for the per-member view — so ring
isn't wholly separate; it's a wrapper that can delegate to rows-renderer per member.

---

## Right column — Analysis tab fallout

Auto-interpretation from payload values (surface owns interpretation). Scope-conditional:

| Content | Present when | Source |
|---|---|---|
| Basin context (upstream area, dist-to-outlet, drainage type) | single-basin; ring center | single-basin fields |
| s/u divergence + water-provenance verdict | single-basin only | s/u fields (no single s/u pair for areas) |
| marginal_exposure caution | polygon-path (polity, polygon) — DN5 | `neighborhood.marginal_exposure`; threshold a **named adjustable constant**, not inline literal |
| coherence / distribution story | any multi-unit `{rows[]}` | coherence + histogram stats |
| analyst-drawer caveat | draw-study-area (arbitrary boundary) | scope flag |

Analysis must branch on what's in the payload, not on a remembered scope label — same
principle as the Signature renderer.

---

## What this buys the build

- **Two renderers to design, not fifteen states.** rows-renderer (method-branched) and
  ring-renderer (which delegates to rows-renderer for deep-dives).
- **Conditional sections are payload-driven** — the page inspects field/method presence and
  shows what's there; absence is never an error (DN5).
- **The combinatorics that remain are real and small:** the temporal two-axis control (polity
  only), the Band T trifurcation (three widgets), and the ring exception. Everything else is
  one method-branch table.
- **Sequencing implication:** the rows-renderer + method leaves + histogram/range-bar widgets
  are shared by four scopes and carry no temporal or marginal-exposure complexity for the
  point-rooted ones. Building single-basin + buffer first exercises the whole rows-renderer and
  both non-Band-T widget families, with the least new cognitive territory — then polity adds the
  two-axis controls + Band T envelope, and ring adds its wrapper. (Feeds WO2 scoping.)

---

## Open threshold/config note

Any significance threshold the page carries (e.g. DN5's `lt_50pct > 0.10` caution) is a
**surface interpretation decision** (locked principle) and must be a named, adjustable constant
with a comment pointing at that principle — never an inline literal. Use cases will correct
these; they should be one-line changes.
