# WO7a — Label lock and build

**Status:** draft for review.
**Prior:** `wo7_findings.md` (investigation complete; verdict Option A, labels pending).
**Type:** label decision + the build WO7 held pending it.
**Scope note:** sandbox and Explorer only. `cdop_pilot` is deliberately out of scope here.

---

## The label decision

Option A endorsed, with one change to the mechanism: **cells get no prose names of their own. They
compose from the axis names.**

The over-promise diagnosed in WO7 came from importing names — Mediterranean, monsoon — that carry
more meaning than two axes can deliver. A composed name carries exactly the axes' meaning and cannot
over-promise by construction.

**Modality axis**

| class | label |
|---|---|
| arid | Arid |
| aseasonal | Even year-round |
| 1-season | One wet season |
| 2-season | Two wet seasons |
| undetermined | Undetermined |

**Phase axis**

| class | label |
|---|---|
| warm-wet | Warm-season rain |
| cool-wet | Cool-season rain |
| weak coupling | Weak coupling |
| no thermal cycle | No temperature cycle |

**Cells compose from both**, comma-joined: *Cool-season rain, one wet season.* *Warm-season rain,
one wet season.* *One wet season, no temperature cycle.*

Wording rationale, so it is not re-litigated:

- **"Warm-season" not "Summer."** Summer reads hemisphere-specific, and the axis means *rain
  concurrent with warmth*, not *rain in summer* — Timbuktu's `weak coupling` at r = 0.38 is the
  case that distinguishes them (Sahel peak heat leads peak rain by ~2 months). Parallelism with
  "Cool-season rain" also matters more in a legend than either word alone.
- **"Even year-round" not "aseasonal."** Plainer for a non-specialist, no loss of precision.
- **"No temperature cycle" not "no thermal cycle."** Same reason.

**The classic names go in the legend as annotation, not as class names:**

> Köppen-Mediterranean, monsoon, and tropical twin-rains are subsets of these classes, not
> equivalent to them.

That is where they can be qualified. As class names they cannot.

**All four declared conventions appear in the legend as conventions, not discovered cuts:**
`THRESH_ARID` 100 mm, `CV_FLAT` 0.20, `THERMAL_FLOOR` 5 °C, `PT_CUT` 0.50.

---

## Build

Per `wo7_findings.md` § Next, unchanged in substance:

1. **Precompute-and-cache extraction.** Script writes the L06 and L08 parquets (both already
   computed in the notebook); route
   `/api/explorer/climate-class?axis=modality|phase|cell&level=6|8` serves the flat
   `{hybas_id: cat_id}` dict plus category list, mirroring `/explorer/categorical` and the
   LISA-parquet loader. Not "at index load" — the L08 Knoben grid is ~18 s.
2. **Explorer categorical** — three variables (modality, phase, cell) on `basin06.pmtiles` /
   `basin08.pmtiles`, with legend and convention note. *Show all two-wet-season basins* is a
   one-line filter.
3. **Same-cell Similarity lens** — `Climate class (same type)`. Look up the query basin's cell,
   paint all same-cell basins. Lens contract unchanged from WO6c: paint the set, report size and
   spatial spread, unpainted non-members, honest empty. No shading — there is no natural quantity
   here; flat is correct.

Provisos:

- Panel copy states the two things that distinguish this lens from the conjunction lenses: it is
  **hemisphere-blind** where they are calendar-locked, and it is **much coarser** — a conjunction
  set is ~14 basins, a class cell is hundreds. SF's conjunction set cannot contain Cape Town; its
  class cell can. Same tab, two questions, different answers.
- Container line as on the adjacent tabs: *this describes the basin the settlement sits in, not the
  settlement itself.*
- Cell counts vary enormously (45.4% for warm-season/one-season, 0.6% undetermined). Report the
  count; do not normalise the display to hide it.

---

## Accept gate

**All three Explorer variables render with composed labels and the convention note; the same-cell
lens paints and reports size and spread; no class or cell label uses a Köppen or Knoben name.**

---

## For the register

**The untested third dial is annual total, not winter temperature.** Diagnostic 2 tested a
mild-winter floor and it failed. But what excludes Anatolia–Iran–Turkmenistan from Köppen Cs is
aridity, not cold winters — Iranian summers are hot, so a hot-summer criterion would not drop them
either. Rough figures suggest the overlap is about as unfavourable (Los Angeles ~380 mm against the
Anatolian plateau ~350; Santiago ~300 against Tehran ~230), so Option A likely survives either way.
Logged as **untested**, with the reason, so that "we tested a third dial and it failed" is not read
as more general than what was actually tested.

**Phase 4 class balance, unexamined and consequential.** Modality is 77.4% one-season; the
informative contrast is 5.5% two-season against that, which is a rare-class problem with small
cells. Phase is far better balanced (50.6 / 12.3 / 19.3 / 17.8) and is the axis more likely to carry
a correspondence signal. This is an argument for cross-tabulating the **axes separately** rather
than the cell, whose 45.4% concentration is worse still. It determines what the correspondence test
can detect rather than how it is built, so it belongs in the correspondence WO's scoping, not here.

---

## Out of scope

- `precip_temp_phase` as a conjunction condition (still deferred; the class map validated the
  quantity, the lens-condition use is a separate decision)
- The D-PLACE cross-tabulation
- Option B sharpening constraints — diagnosed as not worth the cost, recorded so it is not
  re-derived
- `cdop_pilot`
- 