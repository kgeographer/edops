# WO5 — Polity slice: A–E rendered, Band T raw-exposed

**Branch:** Surface / sandbox v2 (new branch off WO4)
**Phase:** Surface · **Step:** 4 (polity scope — first live render)
**Depends on:** WO4 (`/api/areas`, buffer live) — done.
**Type:** front-end + finding. No engine change (unless the finding says we need one — that's WO6+).
**Stance:** baby step. WO5 makes the polity payload **visible** so downstream decisions
(map destination, Sig-tab fate, engine changes, spanned-vs-slice Band T) can be made against
real data instead of in the abstract. It decides none of those.

## What WO5 does NOT decide

- Whether the Sig tab eventually "goes dark" for polity (map as destination).
- Whether Band T should be a single slice's snapshot or a span across slices.
- Whether the engine needs to serve something different for polity Band T.
- Any Band T *visualization* design.

These are downstream. WO5 generates the evidence they need. Committing to any of them now is
the overthinking we're avoiding.

## Goal

For a selected Clio polity slice: render Bands A–E through the existing renderer, and
**raw-expose** what Band T actually contains, so we can see the material before designing its
display. The deliverable is as much the **finding** (what Band T holds) as the render.

## Part A — polity slice selection + A–E render

- Polity scope resolves via `/api/areas?type=polity` (WO4). The `polity` search resolves a
  name; on resolution, the polity's available **slices** (Cliopatria geometries + their
  timespans) become known.
- Present the slices as a picker (constrained to the polity's actual slices — not a free year
  field). Selecting a slice fixes `resolver_year` (the boundary) and labels it.
- Selected slice's outline renders to the Map tab (boundary only — no paint; user may not even
  see it, that's fine).
- Lead to the Signature tab. Bands **A–E** render through the **existing `renderSignature` +
  widgets** (WO2/WO3) — polity returns the same `{rows[], neighborhood}` shape as buffer, so
  this is the proven renderer over polity rows. No new rendering logic for A–E.
- This is polity `&detail` meeting the renderer at its **largest payload** for the first time
  (52 rows, heavier detail, `marginal_exposure` present). Note anything that strains — render
  cost, layout density, a widget choking on polity-scale data. That strain is part of the finding.

## Part B — Band T raw-exposed (the actual point)

- Do **not** design a Band T visualization. Render Band T **raw** — a structured inspection
  view of exactly what the T rows contain for this call. Think "readable dump," not "chart":
  per T variable, show what the payload holds (values, time points, whatever fields are present),
  in a form we can read and reason about.
- The purpose is to see the material. A designed chart would silently commit to a temporal model
  (slice snapshot vs span, envelope vs steps) we have NOT settled. Raw exposure commits to nothing.
- Keep it in the T accordion, clearly marked as a diagnostic/inspection view, not a finished
  display.

## Deliverable — the finding (`wo5_findings.md`)

The finding is the product. Report, for a representative polity slice (N Song, a chosen slice):

1. **What Band T variables are present** (LMR set, HYDE set, eVolv2k) and their methods.
2. **Temporal extent** — the critical question: does the payload contain a **single slice's
   snapshot**, or a **span**? How many time points per variable? What years/epochs?
   This is what tells us whether we must go back to the engine for spanned-over-fixed-boundary
   data (the thing we suspect but haven't confirmed).
3. **Shape and size** — row count, per-row detail weight, total payload size. How the renderer
   coped at polity scale (Part A strain notes).
4. **What's missing for an eventual map** — first read on the gap between what Band T returns
   and what a Cliopatria-style paint would need.

## Explicitly out of scope

- Band T visualization (envelope, stepped chart, event overlay) — deferred until the finding
  tells us what we're rendering.
- Map paint / variable selector / slice slider — the map is a later, larger build.
- Any engine change — if the finding shows the engine returns the wrong temporal extent, that
  becomes WO6+, decided against the finding.
- Analysis tab.
- Ring / polygon / draw scopes.
- Deciding the Sig tab's long-term fate.

## Accept gate

- Polity slice selectable; selecting one fixes + labels the boundary and renders A–E via the
  existing renderer.
- Band T raw-exposed in a readable inspection view (not a designed chart).
- `wo5_findings.md` answers the four finding questions — especially #2 (single slice vs span),
  which is the decision-driving one.
- Existing suites green; live Lookup untouched.
- Karl reviews each write before it lands.

## Note on what "more will be revealed" means here

The finding may show one of:
- Band T already carries a usable span over the fixed boundary → later WO charts it.
- Band T carries only the slice's snapshot → engine WO to serve spanned-over-fixed-boundary,
  then a charting WO.
- Something else we haven't anticipated.
Any of these is a good WO5 outcome, because it replaces a guess with a fact. WO5 succeeds by
making the choice concrete, not by making it.

