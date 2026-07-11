# WO1 findings — within-polity-variance ranking

Source: `notebooks/edop/demo/wo1_within_polity_variance.ipynb`
Output: `output/edop/demo/wo1_polity_spread_{aridity|precip|elev}_L06_centroid.tsv`

Findings recorded as cells run and results discussed. Accept gate: Northern Song in top 15%
by aridity spread.

---

## F1.1 — Variable audit (Cell 2)

All three BasinATLAS columns confirmed in `public.basin06`. Zero NoData across all 16,397
basins for all three variables — no masking required.

| Variable | Column | Range | Mean |
|---|---|---|---|
| `aridity_index` | `ari_ix_sav` | 0 – 2101 (P/PET × 100) | 84 |
| `precipitation_annual` | `pre_mm_syr` | 0 – 6872 mm/yr | 772 |
| `elevation_mean` | `ele_mt_sav` | -30 – 5556 m | 613 |

---

## F1.2 — Basin scores (Cell 3)

`PERCENT_RANK` over 16,397 basins produces near-uniform distributions on all three
variables (mean ≈ 50, std ≈ 29; theoretical uniform std = 28.87). Scores are well-behaved
and commensurable across variables — spread in percentile space predicts visible colour
spread on the choropleth by construction.

---

## F1.3 — Polity-basin membership (Cell 4)

**Method:** centroid-in (`ST_Within(ST_Centroid(basin.geom), polity.geom)`). Excludes
component polities and invalid source geometries.

- 10,607 polity slices joined (from ~15,690 total rows minus components/invalid)
- 1,327 unique polity names
- 15,142 / 16,397 basins (92%) assigned to at least one polity — unassigned basins are
  predominantly ocean/polar with no historical polity coverage

Basin distribution per polity slice: median 20, mean 115, max 3,334. Distribution is
heavily right-skewed — most polities are small, a handful of empires are very large.
`MIN_BASINS = 5` (the p25) is the documented inclusion threshold throughout.

---

## F1.4 — Spread statistics overview (Cell 5)

9,670 of 10,607 slices have computable spread (≥ 2 basins); 937 are 1-basin slices
(spread undefined by construction, filtered by MIN_BASINS anyway).

| Variable | Mean spread | Median spread | Max spread |
|---|---|---|---|
| Aridity | 24.8 | 20.7 | 96.8 |
| Precipitation | 22.2 | 16.5 | 95.1 |
| Elevation | 40.4 | 40.3 | 97.2 |

Elevation spread is consistently higher (~40 mean vs ~23 for climate variables) because
terrain varies sharply within polity extents while climate gradients are smoother.

---

## F1.5 — Aridity spread rollup: top-tier observations (Cell 6)

**Accept gate: PASS.** Northern Song ranks 132 / 1,012 (top 13%) with aridity spread 49.69
pct-pts. Gate threshold was top 15%.

**Top of the list is dominated by two classes that require curation:**

1. **Colonial / discontinuous empires** — British Colonial Empire, German Africa, French
   Africa, Spanish Empire rank high because they include disconnected territories that happen
   to span multiple climate zones (Sahara + rainforest + temperate). High spread, but no
   single continuous gradient edge visible on the map. These are not N Song analogs.
   *However*, expansion of these empires into resource-rich territory (cropland %, HYDE
   land-use variables) is a distinct and valid hero-shot story — just a different class.
   Defer to a HYDE-variable spread pass.

2. **Large modern nation-states** — Chile, Peru, USA rank high by the same geometric logic
   (large latitudinal extent crosses climate zones). Not historical polities; lower value for
   Braga.

**After culling these two classes, the strongest static-spread candidates are:**

- **Tang Dynasty** (82.2, 506 basins, 705–749 CE) — spans the Gobi Desert to subtropical
  South China; high and culturally recognizable
- **Han Dynasty** (82.0, 566 basins, 106–116 CE) — similar northwest-to-southeast gradient;
  foundational Chinese polity
- **Roman Empire** (79.5, 395 basins, 6–8 CE) — Sahara to Britain; continuous territory;
  recognizable to any humanities audience
- **Maurya Empire** (75.7, 245 basins, -315 to -302 CE) — Indus valley (arid) to wet Deccan
  coast; strongest South Asia candidate
- **Turks** (75.5, 22 basins, 755–756 CE) — small but high spread per basin; sharp ecotone
  rather than smooth gradient; worth inspecting visually

---

## F1.6 — Trajectory analysis: expansion-into-gradient (Cell 6b)

**N Song trajectory confirmed.** Rank 66 / 744 by spread delta (+14.48). Monotone
increasing over 6 slices (961–1018 CE): spread grew 35.2 → 45.5 → 49.7 pct-pts as
territory expanded southward into wetter basins.

**Key methodological note:** N Song is the confirmed hero shot because the expansion story
runs over 6 slices, each one adding wetter (higher aridity-index) territory. The *trajectory*
— not the peak spread — is what makes it narratively compelling. The continuous time slider
(WO2 or later) is the feature that tells this story properly.

**A display bug was caught and fixed:** `str.contains('Song')` captured Songhai Empire (rank
55) and Liu Song–era slices (426–479 CE) alongside Northern Song. All subsequent name lookups
use exact matching via `NSONG_NAME = 'Northern Song'`.

### Top candidates from spread-delta ranking

| Polity | Delta | Slices | Years | Notes |
|---|---|---|---|---|
| Empire of Japan | +58.9 | 25 | 1868–1945 | Geographically discontinuous; sensitive for some audiences |
| Tibetan Empire | +48.4 | 25 | 623–840 CE | Dramatic: plateau → Tarim Basin + Ganges lowlands; visually striking |
| Liao Dynasty | +46.0 | 10 | 911–1111 CE | Khitan; contemporaneous with N Song on the opposite side of the gradient |
| Turks | +42.5 | 7 | 666–755 CE | Less well-known but strong arc |
| Later Jin Dynasty | +41.1 | 8 | 1619–1642 CE | Manchu conquest prelude; rapid expansion |
| Qin | +40.8 | 13 | -750 to -222 CE | **Unification of China**; most significant political event; strong trajectory |
| Inca Empire | +39.1 | 5 | 1450–1534 CE | Iconic geography; 5 clean slices; Atacama-to-Amazon gradient |

### Top candidates from monotone-increasing ranking

| Polity | Delta | Slices | Years | Notes |
|---|---|---|---|---|
| Cao Cao | +24.1 | 3 | 197–215 CE | Opening act of Three Kingdoms; culturally resonant; minimal slices |
| Adal Sultanate | +20.4 | 4 | 1415–1540 CE | Somalia coast (arid) → Ethiopian highlands; less-known but geographically clean |
| Sukhothai Kingdom | +18.0 | 5 | 1241–1363 CE | Early Thai state; Southeast Asian candidate |
| Songhai Empire | +17.0 | 5 | 1463–1564 CE | **Timbuktu connection** — EDOPS canonical exemplar is within Songhai core territory; expansion across Niger bend; strong narrative anchor |
| Northern Song | +14.5 | 6 | 961–1018 CE | **Confirmed hero shot** — benchmark case; rank 14 / 744 monotone polities |
| Greco-Bactrian Kingdom | +13.2 | 4 | -247 to -144 CE | Hellenistic Central Asia; starts already high (52.9); niche but interesting |

---

## F1.7a — N Song is not a static-spread standout (Cell 7 histogram)

The aridity spread distribution (1,012 polities, ≥ 5 basins) is right-skewed: mode ~10
pct-pts, long tail to 97. N Song at 49.7 pct-pts sits in the upper third — good enough to
pass the acceptance gate (top 13%) but not visually exceptional. Roughly 130 polities have
higher static aridity spread.

**This sharpens the finding:** N Song's hero-shot value is *trajectory-based*, not
*spread-based*. A single-slice choropleth of N Song at peak spread would not be more dramatic
than Tang or Han at spread 82. What makes it compelling is the movement — spread climbing
35 → 50 over 6 slices as the territory absorbs wetter southern basins. That story only exists
with the continuous time slider, not with a static snapshot.

This distinguishes two structurally different hero-shot classes:

- **Static spread** (Tang, Han, Roman, Maurya — spread 75–82) — pick the peak slice, paint
  it, point at the gradient edge. No time control needed; works as a still image.
- **Trajectory** (N Song pattern, Qin, Tibetan Empire) — the story is the change over time.
  Requires the continuous slider. More distinctive as a demo because no static map tells the
  same story.

For Braga: a static hero shot is the fallback if the slider isn't ready; a trajectory hero
shot is the reason to build it.

---

## F1.7 — Hero-shot shortlist (synthesis)

**Tier 1 — strong candidates for visual demo:**

- **Qin** (unification of China, -750 to -222) — high delta, many slices, maximum historical
  significance, pre-colonial
- **Songhai Empire** (1463–1564) — monotone, Timbuktu tie-in, West African story, clean
  5-slice arc
- **Tibetan Empire** (623–840) — dramatic gradient, visually striking map, less familiar to
  Western audiences (a virtue for Braga)
- **Inca Empire** (1450–1534) — iconic geography, globally recognizable, clean 5-slice arc

**Tier 2 — worth inspecting visually before deciding:**

- Roman Empire (already high spread, not a trajectory story but a static hero shot)
- Liao Dynasty (N Song's contemporary adversary; tells a paired story)
- Tang Dynasty (high absolute spread; foundational Chinese polity)
- Cao Cao (short but vivid; Three Kingdoms opener)

**Deferred — different story class (not N Song analogs):**

- Colonial empires (British, French, Spanish, German Africa): expand into resource-rich
  territory; potentially compelling for HYDE land-use variable spread; revisit in a
  HYDE-variable pass
- Modern nation-states (Chile, Peru, USA): geometric artifacts, not historical polities

---

## F1.8 — Open questions carried forward

**On the temporal framing of hero shots:**
The N Song hero shot was always plural — either interactive time-scrubbing or a triptych of
maps showing the territory at three moments. A single map showing a polity straddling an
aridity gradient may or may not be interesting without the historical context of a political
process unfolding over time. This holds for all trajectory candidates: the story is the
*change*, not the snapshot. Moisture/aridity is one factor; terrain, land use, and volcanic
forcing are others.

Implication: the continuous time slider (replacing the slice dropdown) is not a polish item
— it's the feature that makes the trajectory hero-shot class possible at all. A static map
tells the static-spread story; the slider tells the trajectory story.

**On the sandbox and example list:**
The Polities tab already has the controls needed to explore these candidates. Adding 4–5
curated examples alongside N Song (Songhai, Qin, Tibetan Empire, Inca at minimum) would
let Karl scrub and screenshot triptychs without any new feature work. Low-effort, high demo
value.

**On precipitation and elevation spread (amended by WO1a F1a.1):**
Spearman ρ values from Cell 9 (n=1,012 polities):
- aridity ↔ precipitation: ρ = +0.827 — near-redundant; precipitation is not a separate hero-shot axis
- aridity ↔ elevation: ρ = +0.456 — genuinely distinct; different story class (terrain control, vertical ecology)
- precipitation ↔ elevation: ρ = +0.452

Precipitation as an independent hero-shot axis is closed. Elevation is a future pass, framed
differently: terrain and altitude stories, not climate-gradient stories.

**On Band T variables — the key open question:**
WO1 uses BasinATLAS modern climate data painted onto historical extents. This measures
*environmental potential* — what the environment is capable of — not *what the polity
actually experienced*. Band T changes this:

- **LMR**: compute mean PDSI/temperature/precipitation anomaly per basin over each polity
  slice's fromyear–toyear span, then compute spread across member basins. Measures actual
  historical climate variation experienced by the polity.
- **HYDE**: land-use spread (cropland, grazing) across a polity's basins at its period.
  Answers "how much land-use heterogeneity did this polity govern" — a political economy
  question rather than a climate one.

Both require matching each polity slice's temporal window to per-basin temporal arrays —
more complex than WO1's static join, but conceptually cleaner for historical research.
Natural candidate for a follow-on WO. LMR quality floor (700 CE) limits the analysis to the
medieval and modern period; HYDE covers back to 10,000 BCE.

---

## Open / next steps

- **Cell 7** — precipitation and elevation rankings not yet run
- **WO2 (candidate)** — visual inspection maps for Tier 1 shortlist; use
  `scripts/edop/edops_polity_maps.py` as render reference
- **HYDE-variable pass** — re-run trajectory analysis on cropland spread to find the
  resource-expansion story class; natural second hero-shot axis
- **Contiguity filter** — a future refinement; for now, curation by eye removes the
  obvious discontinuous cases
