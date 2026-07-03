# WO3 findings

**WO:** wo3_buffer-scope-widgets  
**Phase:** Surface  
**Branch:** surf_wo3

---

## F3.1 — Single-basin histogram spike is technically correct but meaningless

**Context:** The WO3 spec said the B1 histogram "degenerates correctly on the single-basin
fixture (n=1 → single populated bin) — verify it doesn't break there." It doesn't break.
But Karl reviewed it in the browser and noted the single spike is not a useful display.

**What happens:** For n=1, the entire basin weight lands in one bin → a single tall bar in
the middle of an otherwise empty axis. This is technically accurate but conveys nothing a
viewer couldn't read from the score and raw values already shown in the row.

**Deviation from spec:** The spec framed single-basin degeneration as a correctness gate
("doesn't break"). It is now clearer that correctness ≠ usefulness here.

**Deferred decision:** Options — suppress the histogram when `n_units === 1` (show nothing,
since there is no distribution to show); or replace with a single point/tick on the axis.
Suppression is the simpler and probably right answer: the histogram communicates spread
across units, and with one unit there is no spread. Not blocking WO3; deferred to a
polish/tuning pass.

## F3.3 — Aridity variable name is counterintuitive and needs surface-level disambiguation ⚠️

**Variable(s):** `aridity`, `aridity_upstream` (Band C — Bioclimatic)

**Issue:** The BasinATLAS aridity index is **humidity-positive**: values increase with more humid
conditions, decrease with more arid conditions (codebook: "Under this formulation, the aridity
index values increase with more humid conditions, and decrease with more arid conditions.").
A low `aridity` score therefore means *dry*, not *moist* — the opposite of what the variable
name implies to most readers.

Timbuktu buffer: `aridity` = 10.2 pct (10th global percentile = very arid ✓ — correct
geographically, but reads as "low aridity" which sounds humid). `aridity_upstream` = spread,
with basins ranging 5.8–39.2 on the humidity-positive scale.

**Risk:** Any user reading "aridity score: 10.2 pct" without the codebook context will infer
"low aridity = moist here." The variable name actively misleads.

**Recommendation:** The surface must note the index direction wherever aridity is displayed —
tooltip, label suffix, or a dedicated UI note. Minimum: label as "Aridity index (higher = wetter)"
or similar. This is not a data issue; it is a display/labelling obligation inherited from the
BasinATLAS naming convention. Elevate if the codebook variable catalog does not already carry
a direction flag that the surface can read.

## F3.4 — class_mixture bar shows modal share only; minority classes invisible ⚠️ deferred

**Context:** `detail.classes` is `null` in all buffer fixture `class_mixture` rows. The
mixture bar therefore shows only the modal class label + its area-weight share (e.g. Biome
"Tropical & Subtropical Grasslands..." at 71%). The remaining 29% of basin area-weight is in
one or more other biomes — unnamed and invisible in the current display.

**What the display says:** The bar communicates "the modal class covers this much of the
area" and implies heterogeneity via the gap to 100%. That is honest as far as it goes.

**What it can't say:** Which other classes are present, and in what proportion. A stacked
bar would solve this but categorical label lengths (e.g. "Tropical and subtropical floodplain
rivers and wetlands") make compact stacking impractical. A tooltip, modal, or secondary list
are candidates.

**Precondition:** Engine must return the full class breakdown, not just the modal entry.
Confirm whether `detail.classes` is always null or only null for certain resolver types.

**Status:** Deferred — current display works within its limits; alternative visualization
TBD in a later polish pass.

## F3.2 — Histogram x-axis bins are native units, not percentiles

**Context:** WO3 spec stated "x-axis is percentile (0–100) for these B1 rows," and the
pre-build discussion agreed on a fixed 0–100 domain. Fixture inspection before writing
showed bins are native values (aridity 6.26–18.36, elev_min 62.02–64.30, etc.).

**Decision:** Native-unit axis adopted (Option 1). Fixed 0–100 dropped. Scale varies per
variable; the shape (concentrated vs spread) is the meaningful read, and the global-percentile
`score` is already displayed in the row cell.

**Forward note (from WO spec):** Band T histogram rows will also use native units. The
`renderHistogram` function parameterises x-axis by bin values, so Band T is a no-op change.
