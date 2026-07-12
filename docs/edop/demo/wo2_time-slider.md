# WO2 — Polity time control + slice-synced variable paint

**Phase:** DEMO · Track 1
**Kind:** Diagnosis, then build. `sandbox_v3.html` / Polities tab only.
**Branch:** `demo_wo2` → merge to `demo` on accept.
**Precondition:** WO1a complete.
**Read first:** `DEMO_tracker.md` (locked decisions), `deferred_items_register.md`
(*"LMR choropleth — slice-synced per-year paint"*, tagged **pre-Braga required** — this WO is
where it comes due), `wo1a_findings.md` F1a.6.

---

## The model this WO is built on

**A Cliopatria polity is a sequence of space-time slices.** The atom is *(geometry, span)* —
inseparable. There is no "the border in year Y" independent of the slice that asserts it, and no
legitimate way to pair a variable value with a border that did not hold over the value's span.

Consequences, and they are not negotiable in this WO:

- The **span is the slice's own span**, whatever it is. Slices are frequently **zero-width**
  (`Slice 18 of 38 · 875 CE – 875 CE` — a cartographic instant, the year someone drew the border),
  and sometimes decades (`990–1017`). Both are handled by the same rule.
- **Band T span = active slice span.** This is already locked (2026-07-11, `applySlice()`); the
  work here is making the *paint* honour it.
- The time control may be **continuous as an affordance** but the **data is stepped**. Nothing is
  interpolated; no border is invented; no value is ever shown against a border that did not hold.

**Standing-constraint correction (for the tracker, not a build item):** CLAUDE.md and
DEMO_tracker carry *"two temporal axes remain independent — do not collapse them into one
control."* That holds on the **Settlements** tab, where a point has no span of its own and the
user must supply one. On the **Polities** tab it does not: `resolver_year` and the Band T span are
the same fact, delivered by the slice. Record the scoping correction rather than working around it.

---

## Step 1 — Diagnosis (read-only; findings gate the build)

No changes. Findings → `docs/edop/demo/wo2_findings.md`. Karl reviews before Step 2.

**Note on the gate:** diagnosis shapes *how* the LMR work is done, not *whether*. Slice-synced
LMR is going in. Step 1 exists to find the right path to it and to surface what else is broken on
the way.

1. **The notch problem — confirm the mechanism.** The sandbox_v3 panel reports LMR as
   `LMR v2.1 · 2°×2° native grid · Early (700–950 CE)`. That is a **250-year notch period, not the
   slice span**. If so, the LMR layer answers *"climate during the Early period"* — returning
   identical paint for every slice from 700 to 950 — rather than *"climate during this slice."*
   Confirm in code.
   This is the mechanism behind the observed confound (Karl, Abbasid slices 32→33, LMR temp:
   borders moved *and* values moved, nothing attributable): the values changed because a **notch**
   boundary was crossed, not a slice boundary. Two misaligned grids both moving. State plainly
   whether this is what is happening.

2. **Making the sandbox notch-less — the path.** `temporal.lmr_climate` holds annual arrays
   (1–2001 CE), so a per-slice span-mean is computable directly. Establish what it takes to paint
   LMR at **arbitrary slice spans** instead of fixed notch periods: query cost, response time,
   whether the values API can carry it, what else depends on the notch periods.
   **Report the path and its cost.** This is a design question, not a go/no-go.

3. **The LMR data floor — establish the number, do not assume.** The register carries 700 CE as
   the floor of the *pre-aggregated notch file*; `temporal.lmr_climate` runs from 1 CE. The
   effective floor depends on which path the paint uses, and going notch-less will move it.
   State the actual number, before and after.

4. **Zero-width slices.** How does the current code handle `875 CE – 875 CE` on the Band T path?
   A single-year span is legitimate and must not be a special case that silently fails.

5. **Band T inputs.** Trace `applySlice()`. Are the inputs ever anything but a mirror of the active
   slice? Can a user set them independently, and does the map honour it if they do?

6. **Period vs. slice discrepancy.** sandbox_v3 shows polity period *"Northern Song (1000–1100
   CE)"* with active slice *"990 CE – 1017 CE"* — a slice starting before its own period. WO1a has
   N Song slices at 961–1027. Labelling artifact or real defect?

7. **BCE / Qin.** The API accepts 0–1998 CE; BCE is unhandled (`CLAUDE.md`). Is a BCE polity
   queryable at all in the running app? If not, **Qin (−750 to −222)** and Greco-Bactrian are not
   demoable candidates, and that is a finding — a met-and-deferred register row (met in curation),
   not a prediction.

8. **Where slice-synced LMR pays off — test on the polities where it can.**
   **LMR spread requires spatial extent.** A compact polity gives a paleoclimate anomaly field no
   room to vary across it. **N Song is compact — a null result there says nothing about LMR** and
   is not evidence about this work. Do not test on N Song.
   Test on **extensive** polities: **Abbasid Caliphate** (5.1M km²; already in hand from the
   cliopatria demonstrator), **Tibetan Empire**, **Tang**, **Roman Empire**.
   Question: over a single slice's span, does the LMR field vary visibly **across the polity's own
   extent**?
   Note that the 2°×2° cell scale — coarse and unconvincing against basin polygons for a compact
   polity — is **adequate at continental extent**. Support and story match at that scale.
   **This is a hero-shot hunt in its own right, not a check on N Song.** Report what it finds.

---

## Step 2 — Build

### 2a. Time control

Replace the slice dropdown on the Polities tab with a **slider + VCR controls**, modelled on
`cliopatria.html`'s control.

- **Draggable, no detents.** The handle moves continuously; the year readout moves with it. State
  changes when the handle **crosses a slice threshold** — the widget is continuous, the data is
  stepped, and neither misrepresents the other.
- **VCR controls** — first / prev / play / next, stepping slice to slice deterministically.
- **Readout** carries slice ordinal, span, and (as in cliopatria) area: *"Slice 18 of 38 · 875 CE
  – 875 CE."* The ordinal is the honest signal that the unit is a slice, not a year.
- **Reuse the mechanism, not the model.** `cliopatria.html` is an **interim demonstrator — do not
  modify it.** Take its slider wiring, VCR handling, debounce, and repaint plumbing; take nothing
  that assumes notch-period variable paint.
- **Debounce the repaint.** Dragging must not fire a request per pixel.
- **Band T inputs become a readout, not controls** — they can only ever mirror the slice.

**What this fixes (WO1a F1a.6):** N Song has six slices but three distinct states (961 / 970 /
980; slices 980–989, 990–1017, 1018–1027 are identical). Today three of six dropdown selections
change nothing visible, which reads as a bug. Under the slider the border simply **holds** while
the year advances — the artifact becomes the truth.

### 2b. Slice-synced LMR paint

Replace notch-period LMR paint with **span-mean over the active slice's span**, so the climate
layer answers the question the border poses. Path and cost per Step 1 item 2.

**Why this matters on its own terms:** the LMR layer is currently painting at the **wrong
support** — answering a question about a 250-year notch while the border asks about a slice. That
is a correctness defect regardless of what any given polity shows, and it is the register's
pre-Braga item.

**And it opens a third hero-shot class.** WO1a established two: **static spread** (a sharp gradient
edge — N Song, aridity) and **trajectory** (directional expansion over slices). LMR suggests a
third: **extent** — *"this empire was large enough that the climate anomaly of its era hit its
provinces differently."* That claim needs no gradient edge and no expansion, only reach. It
rehabilitates polities the aridity ranking correctly rejected (the extensive, continental, and
colonial cases), and it is a strong claim for a spatial-humanities audience. Precipitation is the
more likely LMR variable to carry it; temperature anomaly less so — but that is for Step 1 item 8
to report, not for this WO to assume.

### 2c. Coverage guards

- **No LMR overlap** (polity lifespan entirely outside the LMR window): **disable LMR variables in
  the variable select**, reason surfaced. Do not offer a variable that cannot paint. HYDE (to
  10,000 BCE) and BasinATLAS remain available, so the polity stays demoable.
- **Partial overlap** (e.g. **Tibetan Empire, 623–840**, starting below the floor): LMR available;
  the slider **marks where LMR data begins**; scrubbing below it **explains itself rather than
  blanking**. Under a draggable control a user *will* land in the dead zone — silence is not
  acceptable.
- **Full overlap** (N Song, Songhai, Pagan, Inca): no guard fires.
- Guards key off the floor established in Step 1 item 3. **Do not hardcode 700.**

---

## Accept gate

- **Scrub Northern Song 961 → 1027:** the border grows at **961→970** and **970→980**, then
  **holds** while the year advances — three real transitions, not six phantom ones.
- VCR controls step slice-to-slice; the readout names the slice ordinal and span.
- A zero-width slice (875–875) renders correctly.
- Dragging is smooth; repaint is debounced.
- **LMR paint changes at slice boundaries, not notch boundaries.**
- Scrubbing below the LMR floor produces an **explanation, not a blank map**; a polity with no LMR
  overlap shows LMR variables **disabled with a reason**.
- Full suite green (zero-tolerance rule: no FAILs, no unexplained warnings).
- Karl reviews before merge.

---

## Deliverables

- Slider + VCR control on `sandbox_v3.html` Polities tab; dropdown demoted or removed.
- Slice-synced LMR paint (2b) and coverage guards (2c).
- `docs/edop/demo/wo2_findings.md` — Step 1 diagnosis in full: notch mechanism, notch-less path and
  cost, established LMR floor (before/after), zero-width handling, period/slice discrepancy,
  BCE/Qin result, and the **extensive-polity LMR hero-shot test** (item 8).
- `DEMO_tracker.md` — the two-axis scoping correction (independent on Settlements, slice-determined
  on Polities) recorded as a dated locked decision; slider roadmap row updated.
- `deferred_items_register.md` — the LMR slice-synced row resolved. New rows only for issues
  **actually met and deferred**. Not predictions.

---

## Out of scope

**`cliopatria.html` — read for reuse, do not modify.** Interim demonstrator; it stays as it is.
`sandbox.html` and `explorer.html` (public, all-green, untouched). L06↔L08 compare; Analysis tab;
correspondence surfacing; HYDE annual-resolution table layout (register row — bites only on a
post-1950 polity, and no candidate is one); any change to the Settlements tab.

**Notebook candidate maps are retired.** WO1a's median-drift test did the triage numerically, and
the sandbox is both the inspection surface and the demo asset. A second rendering path is wasted
motion.

**Not in this WO, but implied by it:** nobody has ranked polities by **LMR spread within a slice** —
the WO1a mechanic run on a paleoclimate variable. That would *hand* you the extent-class hero-shot
candidates instead of guessing at four. Natural WO3 if Step 1 item 8 finds the field varies.