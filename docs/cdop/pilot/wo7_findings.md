# WO7 findings — Climate classes: the class-relative inverse

**Work order:** `docs/cdop/pilot/wo7_climate-classes.md`
**Branch:** `cdop_pilot` (investigation), `cdop_wo7a` (WO7a label-lock + build).
**Notebook:** `notebooks/cdop/wo7_climate_classes.ipynb` (Cells 1–13, run 2026-07-23/24).
**Prior:** `wo6b_findings.md` (Knoben ΔE = Cell 12; precip×temp corr = Cell 19), `wo6c_findings.md` (Part D — temp has no shape term).
**Status:** **complete.** Investigation (Parts A–D + three diagnostics) → verdict **sound instrument, over-broad names → Option A (honest rename)**. WO7a (`wo7a_label-lock-build.md`) locked the composed labels and shipped the engine + the **Atlas** surface (2026-07-24, Karl visually signed off). Sandbox similarity/climate-class track closed here; `cdop_pilot` similarity (WH Cities) is a separate future thread with Opus.

Two independent axes, computed and painted separately (the WO's "it joins nothing"), with named cells at their cross-product (Option A cross-product variable, per Karl):
- **Modality** {arid / aseasonal / 1-season / 2-season / undetermined} — arid gate → cv gate → Knoben ΔE.
- **Phase** {warm-wet / cool-wet / weak coupling / no thermal cycle} — thermal gate → sign/strength of the direct precip×temp correlation.
- **Climate cell** = modality × phase.

## Settled with Karl before building

1. Negative correlation pole is **`cool-wet`** (Mediterranean), not "cool-dry" (which names the *warm-wet* pole). Med vs monsoon is separated by **phase sign**; the `1-season` condition separates Med/monsoon from twin-rains.
2. Thermal floor = **5 °C** `tmp_seas_amp` (WO6c Cell 7).
3. Named cells rendered via a **derived `climate_cell` cross-product variable** (Option A). Axes also ship as their own variables.
4. **All five** modality classes painted (arid ≠ aseasonal; undetermined = honest abstention).
5. Phase axis consumes a **precomputed per-basin precip×temp correlation scalar**.

## Knoben cost → vectorized grid + precompute-and-cache (resolved)

Exact Knoben (scipy Nelder-Mead, 48 fits/basin) is infeasible corpus-wide. A vectorized (δ, s) grid
evaluation of the L1 objective (`knoben_E_grid`, Cell 4) reproduces exact-Knoben verdicts **exactly**
on the WO6b synthetics (9/9) and 11 probes (11/11), and runs the L06 eligible set (13,645 basins) in
**1.5 s** and the L08 eligible set (157,407 basins) in **17.6 s** (Cell 11). A ~18 s startup cost at
L08 confirms the **LISA-parquet
precompute-and-cache** pattern as the home for the class computation (compute once, persist keyed by
hybas_id for L06+L08, serve the flat dict) — not the WO's stated "at index load." The L06 parquet is
already written (`output/cdop/wo7_climate_classes_L06.parquet`, 16,338 rows, Cell 10).

---

## Part A — Modality axis

Classifier, in order (Cell 5): **arid gate** (`pre_total < 100 mm`) → **aseasonal gate** (`cv < 0.20`)
→ **Knoben ΔE** on the eligible remainder (1-season / 2-season / undetermined). The two gates resolve
the arid and flat basins with no fit; Knoben runs only on the 13,645 modality-eligible basins.

**The vectorized Knoben is faithful (Cell 4).** Grid == exact == WO6b Cell-12 reference on all 9
synthetics and all 11 probes, including the paper's asymmetric-bimodal abstention case (4:1 →
UNDETERMINED). This is the gate that licensed corpus-wide use.

**Corpus shares (L06, N = 16,338):**

| class | n | share |
|---|---|---|
| arid | 1,434 | 8.8% |
| aseasonal | 1,259 | 7.7% |
| 1-season | 12,652 | 77.4% |
| 2-season | 899 | 5.5% |
| undetermined | 94 | 0.6% |

**Probe classes all as predicted.** Timbuktu/Augsburg/Tbilisi/Kaifeng/Santiago/Yakutsk → 1-season;
Mombasa/George Town/Nairobi → 2-season; Tennessee → aseasonal (cv 0.14). **Somalia → arid** — its
87 mm/yr basin is arid-gated, correctly overriding its Knoben BIMODAL reading. That is the WO's own
Somalia lesson working as designed (a two-monsoon *reading* on a basin too dry to have a modality).

**5.5% 2-season is already in Knoben's ~7% neighbourhood** at the corpus level; Part D tests the
*footprint*.

---

## Part B — Phase axis

Direct precip×temp correlation, one dot product per basin (Cell 6), gated: **thermal gate**
(`tmp_seas_amp < 5 °C` → `no thermal cycle`) → sign/strength cut at |r| ≥ 0.50 (`warm-wet` /
`cool-wet` / `weak coupling`).

**Reproduces WO6b Cell 19 exactly, then the gate does real work.** Without the gate: 55.0% warm-wet /
16.6% cool-wet / 28.3% weak — matching WO6b to the decimal (vectorization faithful on this axis too).
With the gate: warm-wet 50.6%, cool-wet **12.3%**, weak 19.3%, no-thermal-cycle 17.8%. **The gate
reclassified 2,900 basins (17.8%), pulling `cool-wet` down from 16.6% to 12.3%** — about a quarter of
raw cool-wet was tropical noise (negative correlation against a temperature curve that isn't a real
cycle). The WO's hypothesis, confirmed with a number.

**Nairobi is the clean demonstration of why the gate exists.** pt_corr +0.597 would read confidently
`warm-wet`; but 3.9 °C amplitude means there is no thermal year for rain to be with or against, so it
correctly reads `no thermal cycle`. Mombasa and George Town land there too — all three tropical
probes, the George Town/Nairobi confusion of WO6c Part D resolved. Santiago → `cool-wet`
(−0.894, Mediterranean); the continental probes (Augsburg/Tbilisi/Kaifeng/Yakutsk) → `warm-wet`.

**The phase map is textbook (Cell 8, bottom).** `no thermal cycle` (gold) hugs the equator exactly
(Amazon, Congo, maritime SE Asia); `cool-wet` (blue) traces the winter-rain belt (five Mediterranean
regions + the real Iran/Central-Asia western-disturbance extension); `warm-wet` (red) is
summer-concurrent rain everywhere else. The 5 °C floor is vindicated by the shape of the gold band.

**Note on Timbuktu → `weak coupling` (r 0.38).** Sahel peak *heat* leads peak *rain* by ~2 months
(pre-monsoon highs, August rains), so concurrent precip–temp correlation is only mildly positive.
Real, not a bug — and it foreshadows Part D's "summer-rain ≠ monsoon" finding: `warm-wet` measures
rain *concurrent with warmth*, not "summer rain."

---

## Part C — Surfaces (the cross-product)

**Climate cell = modality × phase (Cell 7).** The crosstab (L06):

```
phase         warm-wet  cool-wet  weak coupling  no thermal cycle
arid               449       461            521                 3
aseasonal          274       163            683               139
1-season          7422      1325           1545              2360
2-season           112        58            368               361
undetermined        15        10             32                37
```

Named-cell counts as the WO defined them: Mediterranean (`cool-wet × 1-season`) 1,325 (8.1%);
monsoon/summer-rain (`warm-wet × 1-season`) **7,422 (45.4%)**; twin-rains (`2-season`) 899 (5.5%);
arid 1,434; aseasonal 1,259. A **real unnamed cell worth surfacing:** `1-season × no thermal cycle`
= 2,360 (14.4%) — tropical single-wet-season savanna (one rainy season, flat temperature).

**The 45.4% is the headline of Part C, and it is the WO's own warning realized.** `warm-wet ×
1-season` swallows **Yakutsk, Augsburg, Tbilisi, Kaifeng**. Siberia is not a monsoon. The cell
captures *summer-concurrent single-peak rain* — the entire mid-latitude continental interior plus the
tropical monsoon as a subset; the two axes cannot separate them (that needs magnitude, deliberately
absent). The WO cautioned "a class holding 48% is carrying too much"; here it is at 45%. Not a
measurement defect — a **naming** defect. Renamed in the notebook to **"summer-rain (thermally
coupled)."** This is the template for the whole verdict.

### Surface as built (WO7a, 2026-07-24) — the Atlas tab

The WO's "Explorer categorical" framing was superseded twice, both times correctly:

- **explorer.html is frozen** — nothing new goes there. And a class distribution is **not
  place-specific**, so it does not belong on the sandbox's place-centric tabs (Map, Signature,
  Similarity, …) either. It needed its own home.
- **New `Atlas` tab in `sandbox_v3.html`** — a global-views surface (climate classes first,
  extensible). Place-independent: no Resolve, no signature; the left column swaps from the
  Settlements/Polities controls to a global-context info panel while it is active. Flush-right,
  cyan-tinted tab to signal it is the one non-place-centred feature.
- **Rendering = the Map-tab pattern, not GeoJSON.** Paints the basin PMTiles
  (`/static/explorer/basin0{6,8}.pmtiles`) via **feature-state**, fed by the flat `{hybas_id:
  class_id}` dict from `axis_values` (`GET /api/explorer/climate-class?axis=modality|phase&level=`).
  No `/basin-geom`, no 6000-id cap, no query — ~0.3 MB, instant at L06, fine at L08 (~190k
  feature-states, no place-scoping since the Atlas is global by design).
- **Views:** *Modality* (5-class choropleth), *Phase* (4-class choropleth), and two named-class
  highlights — *Two wet seasons* (`2-season`) and *One wet season, cool-season rain*
  (`1-season × cool-wet`, intersected client-side from the two axis dicts). Legend + a view-aware
  explanatory panel carrying the declared conventions and the "subsets, not Köppen" note.

**Render decision (WO7a Issue 2):** two axis choropleths + a client-side compose/highlight, **not** a
~20-colour cell choropleth (which overflows a qualitative palette). Supersedes the WO's "three
variables (modality, phase, cell)" wording. Karl visually signed off 2026-07-24. The place-anchored
`class_lens` / `GET /api/similarity/climate-class` also exist and are tested, but no UI consumes them
yet — kept as a valid "class of this place + its cohort" query for the future `cdop_pilot` thread.

---

## Part D — Validation against published climatology

The maps (Cell 9) are the acid test, checkable by looking, and the quantitative gate (Cell 10) puts
numbers on them. **The accept gate as literally worded is not met — and the reason is a finding, not a
failure.**

**Mediterranean (`cool-wet × 1-season`): all five regions present, but the class is much broader.**
All five classical regions are correctly painted (California/Pacific-NW, Med basin + Iberia + Atlas,
central Chile, the Cape, SW/SE Australia — recall is good, 484 basins inside the region boxes). But a
large blue footprint extends across **Anatolia → Caucasus → Iran → Turkmenistan/Afghanistan**, plus
the Pacific-NW north of California. Quantitatively: **484 in-region (36.5%), 841 leak (63.5%).** The
leak is *not* a box artifact — those places genuinely have single-peaked cool-season rain. What they
lack is Köppen-Med's *mild winters + hot dry summers*.

**Summer-rain (`warm-wet × 1-season`): the 45% umbrella, correctly broad.** Siberia to the Sahel to
N. Australia, all summer-concurrent rain (Cell 9, middle). Renamed from "monsoon" (see Part C).

**Twin-rains (`2-season`): tropical cores right; one L06 miss, one real superset.** East Africa,
Colombia, Sri Lanka, and the Guinea coast (a genuine Knoben feature) are all correctly purple.
Quantitatively at L06: 230 inside Knoben's regions (25.6%), 669 elsewhere (74.4%). Two causes,
separated by the L08 diagnostic below:
- **Indonesia was missing at L06 — an aggregation artifact, not a miss.** (Diagnostic 1.)
- **The SW-US and Anatolia/Central-Asia mid-latitude bimodal is real** (SW-US winter-frontal +
  summer-monsoon; Kazakh-steppe spring + autumn), so `2-season` is honestly a superset of tropical
  twin-rains. Arid-margin speckle (100–300 mm, outside twin regions): 196 basins, 21.8% of the class.

**Verdict on Part D: the two-axis instrument produces correct, climatologically-coherent broad
classes of which the Köppen/Knoben named types are subsets or cores.** The five Mediterranean regions
all appear; the tropical twin-rains cores all appear; the monsoon belt appears — each inside a
correctly broader class. The falsifiable gate returned a nuanced "no" that is itself the result.

---

## Diagnostic 1 — twin-rains at L08 (Cell 11)

L08 modality (Knoben grid, 157,407 eligible, 17.6 s). **2-season = 9,832 (5.2%)** — the same corpus
share as L06 (5.5%).

- **Indonesia returns — 8×.** The Indonesia box (95–141 °E, −10..8 °N) holds **25** twin-rains basins
  at L06 and **200** at L08. The maritime continent (Sumatra, Java, Borneo, Sulawesi, the Philippines)
  fills in at L08 where L06 had almost nothing — confirming the L06 "miss" was island-basin
  aggregation washing out the two peaks, not a method failure.
- **The broad footprint is scale-stable — the superset is real, not aggregation.** The two summary
  ratios barely move between levels: twin-rains inside Knoben's tropical regions is **24.5% at L08 vs
  25.6% at L06**, and the arid-margin speckle (100–300 mm, outside twin regions) is **21.4% at L08 vs
  21.8% at L06**. Refining the grain did *not* concentrate the class into the tropical boxes. So the
  ~75% "elsewhere" (SW-US winter-frontal + summer-monsoon; Anatolia→Central-Asia spring/autumn) is
  genuine mid-latitude bimodality at both levels — `2-season` is honestly a superset of tropical
  twin-rains, and Knoben ΔE detects bimodality wherever it occurs. Only Indonesia, a specific tropical
  *core*, was aggregation-hidden.

## Diagnostic 2 — no clean mild-winter floor for Mediterranean (Cell 12)

Coldest-month temperature, in-region vs leak: in-region median **7.0 °C** [10–90 pct: −1.1, 11.2];
leak median **2.9 °C** [−6.3, 13.0]. Directionally the leak is colder (the cold-continental
hypothesis), but the distributions **overlap heavily**. The floor sweep shows an unfavorable trade at
every setting:

| coldest-month floor | leak cut | in-region cut |
|---|---|---|
| > −2 °C | 23% | 5% |
| > 0 °C | 31% | 14% |
| > 3 °C | 51% | 23% |
| > 5 °C | 60% | 33% |
| > 8 °C | 71% | 62% |

**No floor cuts most of the leak while retaining most of the five classic regions.** The reason is
sound: winter-mildness is not what separates Köppen-Med from the Iranian/Central-Asian winter-rain
belt — the Köppen-Med regions themselves span mild-coastal to cold-continental. The real Köppen
discriminant is *hot dry summers*; the "dry summer" half is already carried by `cool-wet`, and the
"hot summer" half would require temperature-magnitude machinery (the bundling the WO avoids). So
Option B (add a mild-winter constraint) costs too much genuine Mediterranean to be worth it.

## Diagnostic 3 — no clean aridity floor either (Cell 13, per WO7a register note)

WO7a rightly flagged that Diagnostic 2 tested the *wrong* dial: what excludes the Iran/Central-Asia
winter-rain belt from Köppen-Cs is **aridity**, not cold winters (Iranian summers are hot, so a
hot-summer criterion would not drop them either). Cell 13 tests the annual-total dial. Annual precip,
in-region vs leak: in-region median **468 mm** [175, 900]; leak median **251 mm** [125, 1254].
The leak is drier — **aridity is the better discriminant of the two**, as predicted — but the trade
is still not clean:

| annual-total floor | leak cut | in-region cut |
|---|---|---|
| > 150 mm | 24% | 8% |
| > 250 mm | 50% | 18% |
| > 350 mm | 65% | 33% |
| > 450 mm | 72% | 47% |

Cutting half the leak (>250 mm) costs 18% of the genuine five regions — marginally better than the
winter-temp dial's 23% at the same leak-cut, but still a heavy price — and it degrades fast. And the
leak is not monolithic: a **wet Pacific-NW slice (75 basins, median 757 mm — wetter than the median
real Mediterranean region) is immune to any dryness floor.** So no clean aridity floor exists either.

**Both candidate third dials are now tested; both fail to isolate Köppen-Med cleanly.** Option A
holds — not "untested but probably," but tested on winter temperature *and* aridity. Register note
updated accordingly.

---

## Verdict and recommendation

**The instrument is sound; the Köppen/Knoben-specific labels over-promise. Recommendation: Option A —
rename honestly, keep the two minimal axes.** Both diagnostics point this way, and it is the
climatologically honest surface ("cool-and-cold wet winters" is a real thing the data separates;
"Köppen Mediterranean" is a narrower thing the two axes cannot isolate without bundling).

**Proposed honest labels (Opus to finalize):**

| cell | proposed label | classic name = subset/core |
|---|---|---|
| `cool-wet × 1-season` | **Cool-season rainfall (single peak)** | Köppen-Mediterranean = mild-summer-dry portion |
| `warm-wet × 1-season` | **Summer rainfall (thermally coupled)** | monsoon = heavy-tropical portion |
| `2-season` | **Bimodal rainfall (two wet seasons)** | Knoben twin-rains = low-latitude core |
| `1-season × no thermal cycle` | **Tropical single wet season** | (the 14.4% savanna cell) |
| `arid` / `aseasonal` / `undetermined` | as named | — |

All four declared conventions (`THRESH_ARID` 100 mm, `CV_FLAT` 0.20, `THERMAL_FLOOR` 5 °C, `PT_CUT`
0.50) must appear in the legend as conventions, not discovered cuts — per WO7's own proviso and the
WO6b/WO6c precedents.

## Next (the build, once labels are locked)

1. **Extraction to precompute-and-cache.** A script writes `wo7_climate_classes_L06.parquet` and an
   L08 counterpart (both computed here); a route (`/api/explorer/climate-class?axis=modality|phase|cell&level=6|8`)
   serves the flat `{hybas_id: cat_id}` dict + category list, mirroring `/explorer/categorical` and
   the LISA-parquet loader.
2. **Explorer categorical** — three new categorical "variables" (modality, phase, cell) on
   `basin06.pmtiles` / `basin08.pmtiles`, with a legend and the declared-convention note. "Show all
   bimodal" is a one-line filter on the modality variable.
3. **Same-cell Similarity lens** (`Climate class (same type)`) — look up the query basin's cell, paint
   all same-cell basins; state hemisphere-blindness and the coarser grain vs the conjunction lenses.

## Out of scope / deferred (unchanged from the WO)

- `precip_temp_phase` as a conjunction *condition* — the class map validated the quantity (this WO);
  the lens-condition use stays deferred (`wo6c_findings.md`).
- The D-PLACE cross-tabulation (next WO; this produces its input shape).
- Option B (mild-winter / low-latitude sharpening constraints) — diagnosed as not worth the cost
  (Diagnostic 2); recorded here so it is not re-derived.
