# D-PLACE Society Layer: What To Do With The Markers

*Spitball, 2 September 2026 — options only, no decisions*

Given: D-PLACE society points for Africa render on the African Regions map trivially.
The question is what the layer is *for*. Roughly ordered by value, with rough cost.

---

## Status after WO04 (2026-09-03)

WO04 stood the layer up and we iterated the interaction piecemeal (skunkworks track,
merged `bee0638`). Against the six options below:

| # | idea | status |
|---|------|--------|
| 1 | society vs. its own basin, both supports | **half** — the EA card exists (`#soc-vars`: name + EA042 + EA034); the L6/L8 signature of the containing basin does **not**. The research-instrument half is still open. |
| 2 | marker colour by an EA variable over a painted variable | **partial, different mechanism** — no `circle-color`-by-trait + legend; instead the **EA-value magnifier**: click a value → ring every marker sharing it, over whatever's painted, with a count. Binary highlight, not a categorical field. |
| 3 | societies inside the selected region, listed | **not done.** The dispatcher already resolves a marker's containing region on click; the reverse (region → its societies) isn't built. |
| 4 | environmental range across a region's societies (spread + n) | **not done.** Depends on 3. The doc's intellectual core. |
| 5 | society-to-society comparison across regions | **not done.** |
| 6 | nearest environmental analogue | **not done** (doc itself: too much for now). |
| — | *resist:* region colour-by-society-aggregate | **held** — not built. |

Also built, outside the six: a **D-PLACE record modal** (society page from d-place.org in a
90 vw in-app iframe); marker **selection outline** + **hover name tip**; panel **reflow**
between region / society modes with a caret-collapsible rationale; unified click/cursor
dispatcher.

### A WO5 — `Societies_refine` would pick up

- **1** — add the containing basin's L6+L8 signature to the society card (reuse Lookup's
  signature path); show the two supports side by side, divergence visible, not narrated.
- **2 (full)** — `circle-color` by EA042 with a categorical legend; keep the magnifier as the
  "isolate one value" tool alongside it.
- **3 → 4** — region click lists its societies (point-in-polygon), then the environmental
  **spread + n** over that set — no threshold, n always shown; grey/annotate the ~17
  subregions too thin to say anything (coverage as UI, not footnote).
- **5 / 6** — parked; revisit post-Braga.
- **Skunkworks de-tag** — spec + a11y pass on the modal and the magnifier, drop the
  `SKUNKWORKS` comments.
- **Standing caveats** (ethnographic present · points-stand-for-territories · coverage) —
  surface at least the first and third *in the interface* where a claim is made.

---

## 1. Society against its own basin, both supports

Click a marker → panel shows the society's EA attributes beside the L6 **and** L8
signature of its containing basin.

This is what makes the tab a research instrument rather than a dot map. It is also the
direct expression of the Sauerian commitment: a cultural landscape described with both
kinds of thematic content at once, in one panel, for one place.

Inherits the Tbilisi finding — the two supports will sometimes disagree about what
environment the society sits in. That disagreement is not noise to be resolved; it is
the scale-conditionality argument arriving unprompted in a cultural context.

*Cost: low. Signature resolution is Lookup's existing job; the new part is the EA block.*

---

## 2. Marker colour by an EA variable, over a painted environmental variable

Two themes, one frame, no statistics. Subsistence type as marker colour over aridity as
basin paint, and the eye does the correspondence.

Probably the most persuasive thing available in a 120-second demo, precisely because it
asserts nothing. Nobody has to accept a coherence measure to see whether the colours
line up.

*Cost: low. Two existing renderings, one legend problem.*

---

## 3. Societies inside the selected region, listed

Click a region → panel lists the societies falling within it.

Areal membership in its simplest form — Phase 3 without the machinery. Turns Lovejoy's
container into something with contents, which is what a container is for. Also the
enabling step for everything below: once the list exists, dispersion over it is one
move away.

*Cost: low-moderate. Point-in-polygon, plus a list UI.*

---

## 4. Environmental range across a region's societies

Not a coherence statistic. Just the spread: *these fourteen societies span this much
aridity, and this many PNV classes.*

The honest version of "does this region hold together," and it needs no threshold —
which keeps it clear of the standing hazard about fitting cutoffs to motivating cases.
Report n alongside, always.

*Cost: moderate. Depends on (3).*

---

## 5. Society-to-society comparison across regions

Pick two societies in different Lovejoy subregions; show how alike their environments
are.

The interesting case is high similarity: the region boundary separates them but the
environment does not. That is a finding about the boundary, not about the societies.

*Cost: moderate. Uses existing similarity machinery, needs a two-selection UI.*

---

## 6. Nearest environmental analogue

Given a society, which other societies sit in the most similar basin?

The question a comparativist would actually ask, and the one that would make an
anthropologist care about EDOPS. Almost certainly too much for the current window.

*Cost: high. Similarity across a filtered set, plus ranking UI.*

---

## Resist

**Colouring regions by an aggregate of their societies.** It looks like an answer, it
hides the n, and D-PLACE coverage is uneven enough — dense in the Sahel, savanna belt,
East and southern Africa; thin in the Sahara and deep rainforest; effectively absent in
North Africa — that half the continent would be asserting something unsupported. If any
aggregate is shown at all, it belongs in text with its n attached, not in a colour ramp.

---

## Standing caveats for any of the above

- **Ethnographic present.** EA observations are twentieth-century, used here alongside a
  pre-colonial regionalization. State it; don't let it be inferred.
- **Points stand for territories.** Society locations are single coordinates
  representing areas, often approximate. A point-in-polygon membership test inherits
  that approximation.
- **Coverage before conclusions.** Roughly half the 34 subregions have enough societies
  to say anything. Name the viable subset rather than showing a table with holes.


