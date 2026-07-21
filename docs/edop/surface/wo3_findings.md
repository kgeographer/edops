# WO3 findings

**WO:** wo3_buffer-scope-widgets  
**Phase:** Surface  
**Branch:** surf_wo3

---

## F3.1 — n=1 suppresses cross-unit widgets; generalises beyond histogram

**Context:** The WO3 spec said the B1 histogram "degenerates correctly on the single-basin
fixture (n=1 → single populated bin) — verify it doesn't break there." It doesn't break,
but Karl reviewed the single-spike in the browser and noted it is not a useful display.

**General rule:** Widgets that express cross-unit variation — histogram, coherence badge,
spread indicators — should render **nothing** when `n_units === 1`, not a degenerate
something. The principle: histogram communicates spread across units; coherence communicates
agreement across units. With one unit there is neither spread nor agreement to show. This
is the same logic as the `coherence: null` no-badge path already built in B2.

**What single-basin should show:** score, raw value, class label — the things that are real
at n=1. Omit histogram, coherence badge, and any cross-unit summary.

**Status:** Deferred — suppress `n_units === 1` in a polish pass. Applies to histogram (B1)
and coherence badge (B2) at minimum; audit other cross-unit displays when implementing.

---

## F3.2 — Histogram x-axis is native units; chosen tradeoff, not an oversight ⚠️

**Context:** WO3 spec stated "x-axis is percentile (0–100) for these B1 rows," and the
pre-build discussion agreed on a fixed 0–100 domain. Fixture inspection before writing
showed bins are native values (aridity 6.26–18.36, elev_min 62.02–64.30, etc.).

**Decision:** Native-unit axis adopted. Fixed 0–100 dropped. Scale varies per variable;
the within-variable shape (concentrated vs spread) is the meaningful read, and the
global-percentile `score` is already in the row cell.

**Tradeoff to preserve:** Native-unit axes mean **no two histograms share a domain.** A
viewer cannot compare spread *across* variables by eye — a wide-looking bar in aridity and
a narrow one in elev_min are on different scales. This forecloses cross-variable visual
comparison that a percentile domain would have allowed. That tradeoff is **intentional**:
within-variable shape is the intent of the histogram; cross-variable comparison is not.
Do not revert to 0–100 thinking it was an oversight — it was explicitly considered and
rejected because the underlying bins are native values the renderer cannot remap without
a global percentile lookup that isn't in the payload.

**Forward note:** Band T histogram rows also use native units. `renderHistogram` is already
parameterised on bin values, so Band T is a no-op change on the widget.

---

## F3.3 — Surface needs per-variable direction metadata; aridity is the first case ⚠️

**Variable(s):** `aridity`, `aridity_upstream` (Band C — Bioclimatic); likely others.

**Issue:** The BasinATLAS aridity index is **humidity-positive**: values increase with more
humid conditions, decrease with more arid conditions. A low `aridity` score means *dry* —
the opposite of what the name implies. Timbuktu buffer: `aridity` = 10.2 pct (10th global
percentile = very arid ✓, but reads as "low aridity = moist").

**This is the semantic-inversion class of error, and aridity is unlikely to be the only
member.** Any variable whose name implies a direction its scale doesn't follow is a
landmine: `gw_table_depth` (high value = deep water table = dry, or high water table =
wet?), anything `_depth`, any index where "more of the named thing" and "higher score"
diverge. A per-variable aridity tooltip is the wrong fix — it will be rediscovered at
`gw_table_depth` in a later session.

**Recommendation:** The surface needs a **per-variable direction annotation** read from the
codebook/variable catalog. If `EDOPS_variable_catalog_v0.3.tsv` carries a direction flag
(or can be enriched with one), the surface reads it and appends "(higher = wetter)" or
"(higher = deeper)" generically at the variable label — one renderer path, all ambiguous
variables. If the catalog does not carry this flag, adding it is a small catalog-enrichment
task with payoff across every semantically inverted variable, not just aridity.

**Action:** Audit the variable catalog for a direction or polarity field. If absent, add
a `direction_note` column (free text, shown as label suffix or tooltip). This is a
semantics problem, not a rendering problem — the fix lives in the catalog, not in
per-variable JS.

---

## F3.4 — class_mixture minority classes invisible; engine gap, not surface gap ⚠️ deferred register

**Context:** `detail.classes` is `null` in all `class_mixture` rows — confirmed across
both buffer and polity fixtures. The engine never emits the class breakdown for any
resolver type. The mixture bar therefore shows only the modal class label and its
area-weight share (e.g. Biome "Tropical & Subtropical Grasslands..." at 71%); the
remaining 29% in other biomes is unnamed.

**What the display says:** Honest as far as it goes — modal class + how dominant it is;
the gap to 100% implies heterogeneity without naming the minority classes.

**Engine gap confirmed:** A stacked bar or tooltip showing minority classes is blocked on
an engine change to populate `detail.classes`. This is not a surface rendering task.
**Move to `docs/design/deferred_items_register.md`**: engine to emit full class
breakdown in `detail.classes` for `class_mixture` rows, across all resolver types.

**Display note:** Long categorical labels (e.g. "Tropical and subtropical floodplain
rivers and wetlands") make compact stacking impractical regardless. A tooltip or secondary
list is the likely surface form once the engine provides the data.

**Status:** Current display deferred as-is; engine task logged in deferred register.
