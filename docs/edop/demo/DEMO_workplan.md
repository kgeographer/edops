# DEMO phase — workplan

**Purpose:** the working plan for the post-SURFACE phase. SURFACE built and surfaced the
instrument; DEMO is about making it *say something to a person*. The organizing anchor is the
**Spatial Humanities 2026 conference, Braga, 21 September** (flight booked; small presentation
slot + possible demo table). Every prioritization call resolves against one question: **does this
help the 21 Sep audience?**

This is the seed document for a fresh working conversation. It carries the state, the tracks, the
sequencing, and the open decisions so the next session can pick up cold.

---

## The shift in character (why this is a new phase, not SURFACE2)

For 22 work orders the question was *does the instrument do X*. DEMO's questions —what's a good
demo, what's a second hero shot, what does a viewer need explained— are *what does the instrument
show a person who's never seen it*. That's a different kind of work: curation, framing, and
legibility, not capability-building. Conflating them is how you end up polishing controls no demo
visitor will touch. When a decision is ambiguous, "what does Braga need" resolves it faster than
"what's technically next."

---

## State at entry (SURFACE closed)

- Four scopes live off the DB: single-basin, buffer, basin-ring, polity (+ arbitrary WHG place
  lookup and Cliopatria polity search).
- Signature rendering for all method leaves + Band T; map geometry for all four scopes.
- Full choropleth: 10 variables across 4 groups (BasinATLAS, physiographic, LMR, HYDE), all
  painting honestly — HYDE area-weighted to basins (WO16–18), LMR span-mean per Band T (WO19).
- **L06 and L08 both operable** (WO22): level select wired on both tabs; L08 signatures fast via
  pre-materialized `basin08_scores`; L08 HYDE/tileset built; selective paint at L08.
- Sequenced state management (WO21): the two-tab forward-or-reset model; scope control safely back;
  one active generator; reset returns each fork to cold start.

The instrument's full range (scope, scale, variables) is built. What remains for DEMO is
**demonstration, exposure of the few unexposed pieces, and legibility** — plus the one genuinely
unbuilt scope (draw-study-area), deferred but before-Braga.

---

## Three tracks

### Track 1 — Money shots (curation + the features they need)

The center of gravity. N Song expanding into wetter territory works because it has three
properties: a **polity/region the audience recognizes**, an **environmental gradient the paint
makes obvious**, and a **historical fact the gradient illuminates**. A second and third hero shot
need the same three. This is a *curation* task, not a build task — hunting the data for the two or
three cases that land.

**The curation mechanic (demand-driven, computable):** a polity straddling a strong gradient has
high **within-polity variance** of the painted variable; one in uniform terrain has low. An offline
ranking notebook that, for a chosen variable, ranks all Clio polities by internal spread *hands you
the candidates* — top of the list = "polities most straddling an aridity (or land-use, or anomaly)
gradient." N Song surfacing near the top validates the method. This turns "paint and eyeball" (which
doesn't scale, and requires knowing the history in advance) into "rank by spread, inspect the top
ten." The environment points you at the polities worth a historian's attention. **This notebook is
the natural first work of DEMO** — it's research, not build, so it can run before feature decisions,
and it drives which features Track 2 prioritizes.

**Two demo-enabling features that are also hero shots in themselves:**

- **Continuous time slider** (replacing the polity slice dropdown). Cliopatria slices are a
  *digitization artifact* — breakpoints encode when a cartographer redrew a polygon, meaningless for
  environment. A continuous slider with **no steps and a year readout** tells the honest story: time
  flows continuously, extent holds at any instant, and the environmental variables drift underneath
  on their *own* cadence (LMR annual, HYDE epochs). Keep the geometry breakpoints as data; decouple
  the *time control* from them in the UI. The temporal hero shot: *"watch the borders hold while the
  climate moves beneath them across the polity's life."* Stepped slices would hide exactly this. This
  also fixes the real dilemma of duplicate-geometry slices producing "change slice, nothing moves"
  (misleading, because a variable value may have shifted even when extent didn't).

- **L06 ↔ L08 scale compare** (the MAUP demo). Now that L08 is operable, same region at two scales —
  regime cores holding, transition zones shifting — is a methodological show-and-tell, not a sentence
  in a paper. A future Track-1 feature; the WO22 wiring already supports a clean compare.

### Track 2 — Features (demo-driven exposure, guarded against completeness)

The pieces built but not fully exposed. **Expose only what a demo or slide uses** — the discipline
is demand-driven, not "the control is sitting there empty."

- **Analysis tab** — content exists in v1; port/review/expand *if* it carries a demo point.
- **More variables** — 10 exposed, more available in the engine; expose the ones a hero shot needs,
  not all of them for completeness.
- **Correspondence surfacing** — see the dedicated note below. This is the highest-reach Track-2
  item and it is *already substantially built*.

### Track 3 — Legibility (the demo-must-explain-itself work)

At a demo table you won't narrate over every visitor's shoulder; the surface has to carry meaning
without you. This is a higher bar than "a person could use it" (SURFACE's bar) — it's "a stranger
understands what it's showing." For Braga this may matter *more* than any new capability, because a
demo that needs explanation fails the moment you step away.

- **Basin-ring "what am I looking at"** explanation (left-column / below-map real estate exists).
- **Map legibility** when basin outlines and variable paint overlap — needs a genuine pass.
- **A minimal user guide** — the sandbox isn't self-explanatory (full dashboard guidance is out of
  scope this period).
- The slice-confusion fix, which the continuous slider (Track 1) largely resolves.

---

## Sequencing — the dependency that orders the tracks

The tracks are **not** parallel. Legibility and guide material depend on a **feature-complete-enough,
frozen surface** — you cannot write "here's what you're looking at" for controls still in flux, and
documenting a moving surface is wasted motion. So:

1. **Money-shot curation runs continuously** from day one (research, not build) and drives Track 2
   priority.
2. **Track 1 + 2 features first** (weeks ~1–6): the ranking notebook, the continuous slider, the
   MAUP compare, correspondence surfacing, whatever variables/Analysis a chosen hero shot needs.
3. **Feature freeze at the early-September UX review** — a hard calendar checkpoint. The surface is
   declared demo-frozen. This is the gate.
4. **Track 3 legibility + guide** (weeks ~7–10, to 21 Sep) over the *frozen* surface, when you know
   exactly which demos you're showing and what needs to read well.

Legibility is *last* not because it's least important (you rank it high for the table) but because it
has a prerequisite: feature-freeze.

---

## Correspondence — an existing asset, not a future build

Reassessment from the workbench Societies screen: the environment↔culture correspondence is **already
built and live**. The Computing Place Workbench "Societies" tab holds 1,291 D-PLACE societies, **87%
spatially joined to EDOPS signatures**, faceted by anthropological variable (subsistence EA042, high
gods EA034) and cross-tabulated against basin-climate clusters. "Active-morality high gods by basin
cluster: Warm Desert 38, Boreal 39, Temperate/Med 22…" *is* a computed environment-culture
correspondence. The hard part is substantially done.

So the DEMO question is not "can we build it" but "is the *claim* defensible before domain experts."
The cross-tabs are real but an anthropologist at Braga will probe: **Galton's problem** (societies
aren't independent — related cultures cluster spatially *and* share traits, inflating any
environment-culture correlation), the 13% basin-unassigned dropout, focal-year mismatch (1850–1940
ethnographic present vs. paleoclimate spans). The move is to **surface it with the caveat in the
frame** — attestation-model discipline: one dataset's answer, provenance intact, no claim to ground
truth. A screen that shows the correspondence *and* names Galton's problem is more credible than a
cleaner one that doesn't.

**Decision pending:** port the Societies screen into the sandbox/lookup surface, or demo the
workbench as a separate live thing alongside? Porting is real work; demoing as-is is nearly free and
already works — a strong argument for Braga unless there's a reason it must live in the sandbox. A
full interactive "Demo tab" with deeper correspondence exploration is a **post-Braga / CDOP-phase**
concern; for the conference, a controlled slide + the existing workbench screen is the safer reach.

---

## Explicitly deferred / out of scope

- **draw-study-area** — the one unbuilt scope. Deferred but **before-Braga**; slot into Track 2 only
  if Tracks 1–2 land with room, since it adds a scope to *explain* rather than clarifying existing
  ones.
- **Full interactive Demo/correspondence tab, CDOP correspondence work** — post-Braga phase.
- **Dashboard guidance material** — not in scope this period at all.
- Anything that builds for completeness rather than for the 21 Sep audience.

---

## Open decisions to settle early

1. **Correspondence: port vs. demo-workbench-as-is** (above). Lean: as-is for Braga.
2. **Continuous slider: no-steps-with-readout as first shot** — confirmed direction; the first
   Track-1 build candidate alongside the ranking notebook.
3. **Which hero shots** — output of the ranking notebook + Karl's own known cases (e.g. Anasazi
   geo-/enviro-history, "rise and demise" patterns). Everything demo-facing keys off this.
4. **Numbering / tracker** — DEMO gets its own `DEMO_tracker.md`, `deferred_items_register.md`
   continues cross-phase. WO numbering continues from 22 or restarts — Karl's call at directory
   setup.

---

## Immediate next

**The within-polity-variance ranking notebook** — it's research not build (can start before feature
decisions), it produces the hero-shot shortlist everything else keys off, and it exercises the
demand-driven / use-case-outward discipline. First DEMO work order. The continuous slider is the
strong second, as the temporal hero shot and the slice-confusion fix in one.
