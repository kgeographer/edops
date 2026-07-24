# WO7 — Climate classes: the class-relative inverse

**Status:** draft for review.
**Prior:** `wo6b_findings.md` (Parts B, C, E, Cell 18b, Cell 19), `wo6c_findings.md` (Part D),
`CDOP_PILOT_tracker.md` § Proposed next instrument.
**Type:** index computation + Explorer categorical + one Similarity lens.

Goal-setting with provisos. CC discovers implementation particulars; Karl reviews every write.

---

## Why

Every similarity instrument so far is **query-relative**: here is a place, paint its kin. This
builds the **class-relative** inverse: here is a climate type, paint its global footprint, no query
point.

Three reasons it goes next:

**It joins nothing.** Every failure in the WO1–WO6 sequence came from bundling — three questions
in the phase lens, level and shape in one composite distance, and most recently an attempt to graft
a hemisphere fix onto a calendar-locked shape term. Two independent axes, computed separately and
painted separately, is the opposite move.

**It validates the phase quantity in public before that quantity is wired into anything.** WO6b
Cell 19 verified direct precip×temp correlation against `s_d` on eleven probes. A global map is a
far stronger test at similar cost, and it is checkable against published climatology by looking.
The deferred `precip_temp_phase` conjunction condition (`wo6c_findings.md` § Candidate next lens
condition) stays deferred until this map says the quantity is sound.

**It is the input Phase 4 needs.** *Are moralising high gods associated with any particular
environmental setting* is a cross-tabulation. That wants classes, not ranked sets. This is the
first instrument in the sequence producing that shape of output.

It also dissolves the SF/Kalahari problem rather than patching it. Calendar-locked shape cannot
separate SF's January cool-season rain from the Kalahari's January warm-season rain. The phase axis
is hemisphere-blind by construction, so if what you want is Mediterranean basins, you ask for the
class — and you get Cape Town and central Chile too, which calendar-locked shape can never return.

---

## Part A — Modality axis

Computed per basin at index load, from curves already retained in the conjunction index.

Classifier, in order:

1. **Arid gate** — `pre_mm_syr < THRESH_ARID` (100 mm) → class `arid`. Not "aseasonal": too little
   rain to have a season is a different fact from rain spread evenly. This is the one threshold in
   the project sitting in a genuine histogram trough, robust to ±25 mm. WO6b's Somalia correction
   showed what happens when it is skipped — an 87 mm/yr basin was classified for modality and
   became a flagship example it had no business being.
2. **Aseasonal gate** — `cv` below a declared cut → class `aseasonal`.
3. **Modality** — Knoben ΔE decides 1-season vs 2-season, with `undetermined` retained as a real
   class where both sine models fit badly (|ΔE| ≈ 0).

Provisos:

- **Use Knoben ΔE, not peak-counting and not `R_dbl`.** ΔE has no free parameter in the modality
  decision — the entire point. WO6b Part C validated it: agrees with peak-counting on 9 of 11
  probes, both disagreements informative, and it gets right the two cases `R_dbl` got wrong in
  opposite directions (Timbuktu unimodal, George Town bimodal). The equal-amplitude breakdown lands
  between 2:1 and 4:1 asymmetry; Mombasa at 2.1:1 and George Town at 1.35:1 sit on the good side.
- **`undetermined` is not a failure class.** It is the method abstaining where neither model
  describes the basin, and it must be painted and labelled as such, not folded into a neighbour.
- **The `cv` cut is a declared convention with no data-driven support.** WO6b Cell 18 found the
  corpus histogram is a flat plateau from ≈0.15 to ≈0.65 with no trough. `CV_FLAT = 0.20` separates
  the probes correctly (Tennessee 0.144 below, George Town 0.296 above), and that is the whole of
  its justification. State it as a convention in the legend, not as a discovered boundary.
- Do not expose `cv` as a displayed score. It explodes on dry-season zeros; it is safe as a gate
  and as a per-query band, and nowhere else.

## Part B — Phase axis

Direct correlation of the twelve-value precipitation curve against the twelve-value temperature
curve — one dot product per basin (WO6b Cell 19).

1. **Thermal-cycle gate** — `tmp_seas_amp` below a declared floor → class `no thermal cycle`.
2. Above the gate: `warm-wet` (strongly positive, rain with heat), `cool-wet` (strongly negative,
   rain against heat), `weak coupling` (near zero).

Provisos:

- **The thermal gate is required and WO6c Part D supplies its evidence.** Below roughly 5 °C
  seasonal amplitude the temperature curve is noise — Cell 7 found same-hemisphere pairs in the
  2–5 °C band correlating at median −0.027, sd 0.64. Correlating precipitation against noise
  produces noise. Without the gate, `no thermal cycle` and `weak coupling` are indistinguishable in
  the output and distinguishable in the world: George Town's −0.25 should read *this basin has no
  thermal year for rain to be in or out of phase with*, not *the coupling is weak*.
- Recommend the floor value against the Cell 7 bins; ~11% of basins sit under 3 °C. Declare it.
- The `warm-wet` / `cool-wet` cuts are also declared conventions. WO6b Cell 19 reported corpus
  shares of 55% warm-wet, 17% Mediterranean, 28% weak/none under some cut — report what cut
  produced those and whether it survives the thermal gate being added.
- Hemisphere-blind by construction. That is the point, not a side effect.

## Part C — Surfaces

**Explorer — two categorical variables, each axis separately.** This is the existing pattern
verbatim: `/api/explorer/categorical?var=…` returning `{hybas_id: cat_id}` plus a category list,
painted on `basin06.pmtiles`. *Show all bimodal* is a one-line MapLibre filter. New work is the
per-basin class computation plus a legend.

**Similarity tab — one new lens, the grid cell.** Karl's question was whether these can be lenses
despite a different underlying algorithm. Yes, with one design constraint: on a surface that has a
query basin, a *single-axis* class paints half the world and is not a similarity answer. The lens
should be the query's **cell** — same modality class **and** same phase class.

Provisos:

- Label it plainly: `Climate class (same type)`. It answers a different question from the
  conjunction lenses — *what shares this basin's climate type* rather than *what closely resembles
  this basin* — and sits beside them at a coarser grain. A conjunction set is ~14 basins; a class
  cell is hundreds. Both are legitimate; the labels must not imply they are the same instrument at
  different settings.
- The lens contract is unchanged even though the algorithm is: paint the set, report size and
  spatial spread, unpainted non-members, honest empty. Shading has no natural quantity here — leave
  it flat rather than inventing one.
- **State the complementarity in the panel copy**: the class lens is hemisphere-blind, the
  conjunction lenses are calendar-locked. SF's conjunction set cannot contain Cape Town; its class
  cell can. That is the clearest available demonstration that these are different questions.
- Report class at both L06 and L08. Expect disagreement for mountain basins — the container problem
  again, and the level toggle already makes it legible on the conjunction panel (WO6c review).

## Part D — Validation against published climatology

The acid test, and the reason this WO has an external gate rather than an internal one.

- **`cool-wet` × `unimodal`** should paint the five classical Mediterranean-climate regions —
  California, central Chile, the Cape, southwest and south Australia, the Mediterranean basin — and
  little else.
- **`bimodal`** should reproduce Knoben's published footprint: ~7% of the global land surface,
  concentrated in East Africa, Colombia, Sri Lanka, Indonesia. The paper is on disk
  (`articles/`); Figure 1c is the comparison.
- **`warm-wet` × `unimodal`** should paint the monsoon belt.

Report the corpus share of every class and every occupied cell. A class holding 48% of basins is
carrying too much, and the WO4 Part 4 finding — Mombasa and George Town landing in the identical
bioclimate bucket — is what that looks like when it goes unexamined.

---

## Accept gate

**The `cool-wet` × `unimodal` cell paints the five Mediterranean regions and little else, and the
`bimodal` class reproduces Knoben's published ~7% footprint in the documented regions.**

Both are checkable by looking, against published sources, and both can fail.

Supporting: per-class corpus shares reported; both declared conventions (`cv` cut, thermal floor)
stated in the legend as conventions; Explorer categorical renders sub-second; class lens paints,
reports size and spread, and states its hemisphere-blindness.

---

## Out of scope

- `precip_temp_phase` as a conjunction condition — deferred until this map validates the quantity.
  Same quantity, two uses; this is the cheaper and more legible use and it should report first.
- The D-PLACE cross-tabulation (next WO; this produces its input).
- Terrain lens conditions (WO6c Part C).
- The circular-shift mode. WO6b Part E killed it as a ranking refinement, correctly — the maximiser
  is always 0. Whether it survives as a *set* mode is a separate question and the class lens may
  make it unnecessary, since hemisphere-blind matching is what it was wanted for.
- Any fix to the container problem.

---

## Note for the register

The WO6b reasoning that killed the circular-shift trick applies to correlation-maximising rankings.
WO6c changed the output shape to binary set membership, where "same shape, six months displaced" is
a different query rather than a worse-ranked one. The original reason for dropping it does not
transfer cleanly. Recording so it is not re-derived; not proposing it be built.