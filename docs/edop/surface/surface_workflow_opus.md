# Surface phase — build workflow

**Purpose:** the working method for building the new sandbox page. Not a spec of the page
(that's the component inventory + `surface_state-analysis.md`); this is *how we build it* —
the sequence, the fixture discipline, the review gates. Run past CC before WO2 so the
implementation partner and the design partner share one method.

**Governing axiom:** slow and steady. Incremental, sign-off-gated, review-before-write. No
scope builds ahead of the one before it being accepted. The goal at each step is a thing that
renders real data and can be looked at, not a thing that's theoretically complete.

---

## Core method — exemplars as fixtures

The page is built **against the persisted exemplar payloads** ( confirm `docs/edop/surface/exemplars/` are what has been used in WO1),
not against a live endpoint and not against a predicted schema.

- The renderer functions consume the static exemplar JSON during development. No DB round-trip,
  no endpoint dependency, to iterate on layout.
- The exemplars are the UI's regression fixtures (confirm this makes sense; results from wo1_exemplar_inspection.ipynb were generated, not persisted?) — the analog of the engine's frozen TSVs. A
  renderer either handles the fixture or visibly doesn't; correctness is inspectable, not
  argued.
- This is the middle path between "raw-dump and eyeball" (real data, crude container) and
  "predesign from abstraction" (nice widgets, predicted data). We keep the raw-dump *philosophy*
  — design from ground truth, never from a described schema — and upgrade the *mechanism* to
  real widgets fed real fixtures from the first iteration.

Rationale, concretely: WO1 already proved prediction misses things (DN7 `raw`-is-sometimes-a-
string, DN9 histogram-trigger-is-method-not-null). Building against fixtures surfaces that
class of surprise as "the fixture doesn't render," early, instead of as a runtime break after
the endpoint is wired.

**Endpoint wiring is deferred, not required, to build the renderers.** Scopes 1/2/4 aren't
HTTP-wired yet; that's fine — the fixtures stand in. Wiring is its own step, after the
renderers are proven against fixtures.

---

## Division of labor

- **CC (implementation):** writes the renderer functions, the skeleton, the widgets. Can
  predesign the *parsing* — the method-branch dispatch, the field-presence conditionals —
  because DN1–DN10 already fixed the branch points. Works from accepted WOs.
- **Opus (design/reasoning):** the structural spec, the state-fallout logic, widget behavior,
  and review of intermediate products. Predicts payload parsing; does not author final layout.
- **Karl (critical observer, layout, UX author):** reviews every write before it lands. Owns the
  *visual* layer — proportion, hierarchy, how a dense signature reads without becoming noise —
  the part done unaided for decades and not ceded. Wireframes the two flagged spots (temporal
  controls; Signature leaf layout) as needed, but not exhaustively — the state space is near
  combinatorial and fixtures + incremental review substitute for wireframing every state.

---

## Build sequence

Ordered by confidence and shared machinery, per the state-analysis sequencing note and axiom 4
(lead with the scopes whose use cases we can already estimate; let the new cognitive territory
be informed by reactions to the simpler cases).

**Step 0 — skeleton.** Stand up the new page from the old sandbox structure: header, two-column
(1/3 · 2/3; confirm), three tabs (Map/Signature/Analysis), scope dropdown below the bands. Level frozen
L06. No rendering logic yet — just the shell and the scope gate wired to show/hide the
scope-specific input controls (left-column fallout table). Accept before proceeding.

**Step 1 — rows-renderer, single-basin first.** Build the rows-renderer with the single-basin
exemplar as the atomic fixture. **Written so a single basin's signature is the atomic case** and
the multi-unit area version is the same function over more rows — this makes the ring
deep-dive (Step 5) free and forces the atomic case to be the foundation. Method-branch the
leaves (DN7); get every method type in the fixture to render *something* before making any of
them nice. Accept.

**Step 2 — leaf widgets, one at a time.** Improve the method leaves against their fixtures,
widget by widget, each its own review gate:
  - `area_weighted` — score + coherence badge + histogram (histogram trigger = method, DN9)
  - `class_mixture` — modal class + mixture bar (`raw` is a string here — DN7, branch first)
  - `distribution_only` — range-bar p10/p90 + regime breakdown + suppressed-score caveat (DN4)
  - `dominant_basin` / `extreme` — score + carrier/dominant basin + physical `raw`
  - `flag_fraction` — plain fraction (empty detail, DN10)
Histogram widget is shared; build it once, reuse. Accept each leaf.

**Step 3 — buffer scope.** Add buffer input (radius) and run the buffer exemplar through the
same rows-renderer. This is the first true multi-unit case — confirms the renderer that was
built atomic scales to many rows, coherence/spread badges populate, marginal_exposure is
correctly *absent* (DN5, must not throw). Analysis tab: coherence/distribution story appears;
s/u divergence correctly absent. Accept.

**Step 4 — polity scope + Band T.** The new-cognitive-territory step, taken after the simpler
scopes are proven and can inform it:
  - two temporal controls, presented distinctly (resolver_year + Band T span) — the one scope
    with a moving boundary
  - `query` block echo for polity name/period/resolver_year (route-layer, DN1/DN2) — needed for
    the header; requires the endpoint or a fixture that includes the echoed block
  - Band T sub-panel, trifurcated (DN6): LMR envelope (+ local scrubber), HYDE step, eVolv2k
    timeline
  - the envelope-as-local-time-control ↔ value-histogram scrub linkage
  - marginal_exposure caution in Analysis (threshold = named adjustable constant, not literal)
  - map: boundary overlay on global tileset + choropleth slider (independent of the envelope
    scrubber)
Accept in sub-gates — this step is large; break it (temporal controls / Band T panel / map
overlay) rather than one monolithic review.

**Step 5 — basin-ring scope.** The `{center, ring[]}` exception. Ring-renderer as a wrapper:
comparison view + per-member deep-dive that **delegates to the Step 1 rows-renderer** (DN8
path 3 — free because Step 1 was built atomic). Do not weight neighbors equally in any visual
(size varies extremely). Accept.

**Step 6 — draw-study-area scope.** Map draw (rectangle first; freehand/upload later if
pulled). Routes to the same rows-renderer as polity minus name/period lookup. Analyst-drawer
caveat in Analysis. Accept.

**Endpoint wiring** slots in when a scope's renderer is proven against fixtures and needs live
data — likely folded into Steps 3/4 rather than a separate front-loaded task, since the
fixtures carry the renderers until then. (Wiring the three unwired point-rooted paths is a
known prerequisite for *live* operation; it is not a prerequisite for building the renderers.)

---

## Review gates (the "review before write" discipline)

- Every step ends at an accept gate. Karl reviews the write before it lands; nothing proceeds
  on an unaccepted step.
- Large steps (Step 4) break into sub-gates.
- A step's output is judged by whether it renders its fixture correctly and reads well — not by
  whether it's feature-complete against the eventual page.
- Regression check: a later step must not break an earlier step's fixture rendering. The
  exemplars are the standing UI regression set.

---

## What we are explicitly not doing

- Not wireframing every state — fixtures + incremental review substitute for exhaustive
  wireframes. Karl wireframes the two genuinely layout-hard spots (temporal controls, Signature
  leaf density) and no more.
- Not building lean rendering — the sandbox consumes `&detail` (settled). Lean is captured for
  contract-comparison and represented in the "show API call" feature, not rendered from.
- Not touching `sandbox.html` or `explorer.html` — new page is additive; existing public pages'
  tests stay green.
- Not front-loading the hardest scope — polity/Band T comes after the point-rooted cases inform
  it (axiom 4).

---

## Artifacts this workflow produces

- The new page (fresh template).
- Renderer functions proven against `exemplars/*.json` fixtures.
- Findings appended to `surface_findings.md` (SF.n) as build surprises emerge.
- Any missing-field or threshold decisions logged; engine-side gaps become deferred-register
  or TODO items, surface-side ones become named constants.

---

## Immediate next

Run this past CC. If the method and sequence hold, WO2 = Step 0 (skeleton) + Step 1 (atomic
rows-renderer against the single-basin exemplar), stopping at the Step 1 accept gate. Small,
reviewable, and it establishes the atomic-case foundation everything else rests on.