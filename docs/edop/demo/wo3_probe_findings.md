# WO3a — Scale-compare probe findings

**Work order:** `wo3a_scale-probe.md`
**Date:** 2026-07-13
**Status:** complete (read-only; no build)

---

## F3.1 — Level select on Polities tab: wired but broken at L08

**The wiring is there; the failure is a backend gap, not a missing event handler.**

`_onLevelChange()` (line 455) calls `_silentResig()` for both tabs unconditionally (line 462).
On the Polities tab, `_silentResig()` fires the API (`/api/areas?type=polity&...&level=lv`), reads
`nb.member_ids`, and sets `_sigMemberIds`. The event listener on `v3-polity-level` is wired at
line 1890.

**The gap:** Neither `/api/area` nor `/api/areas` includes `member_ids` in the `neighborhood`
response. Both return:

```json
{"type": "polygon", "level": 6, "n_units": 376, "unit_type": "basin", "marginal_exposure": {...}}
```

`member_ids` is absent. `_silentResig()` sets `_sigMemberIds = null`.

**Consequence at L06:** The L08 guard (`level === 8 && !_sigMemberIds?.size`) does not fire.
`applyBasinVar` paints all 16,397 L06 basins with the global choropleth. This looks functional —
the polity boundary polygon shows where the polity is; the choropleth provides global context.

**Consequence at L08:** The guard fires. `applyBasinVar` bails with "Get a signature first to use
L08 choropleth." The choropleth disappears. This is what Karl observes as "inert."

**Required fix:** Return `member_ids: [...]` in the `neighborhood` block from both `/api/area` and
`/api/areas` for polity queries. This is a backend change, not a frontend wiring fix.

**Scale numbers:**

| Polity | Level | Slice year | n\_units |
|---|---|---|---|
| Northern Song | L06 | 961 | 156 |
| Northern Song | L06 | 970 | 228 |
| Northern Song | L06 | 980 | 375 |
| Northern Song | L08 | 961 | 1,407 |
| Northern Song | L08 | 970 | 2,506 |
| Northern Song | L08 | 980 | 4,217 |

**API response time:** N Song at L08 (year=1000, bands=C, detail=true): **3.4 s**. This is the
PostGIS spatial join + area-weighted aggregation over 4,214 L08 basins — the signature computation
itself, which `_silentResig` already fires on a level-change. Adding `member_ids` to the response
adds no extra round-trip; you get a slightly larger JSON payload from the same call. The JS paint
loop (iterating 190K L08 values, filtering to 4K member IDs via a Set) would add ~100–200 ms on
top. So after the backend fix, a level switch on N Song at L08 costs ~3.5 s total. For more
extensive polities (Abbasid, Tang) the computation time would be larger; that is the real
feasibility question, not the painting.

---

## F3.2 — Tbilisi: full L06 vs L08 signature diff

**Point:** 41.694°N, 44.833°E. L06 basin 5023; L08 basin 57266. Both have `up_area` = 23,252 km²
(same Kura upstream catchment at the basin outlet; the L08 basin is the most-downstream
sub-unit within L06 5023).

**The claim that can be made in public: L06 describes the Caucasus highland system; L08 describes
the Kura valley floor where Tbilisi sits. Both answers are true — they answer different questions
about the same point.**

### Variables that flip

| Variable | L06 | L08 | Notes |
|---|---|---|---|
| aridity | **93** | **63** | 30 pp drop; most demo-legible number |
| biome | Temperate Broadleaf & Mixed Forests | **Deserts & Xeric Shrublands** | Full class flip |
| ecoregion | Caucasus mixed forests | **Azerbaijan shrub desert and steppe** | Full class flip |
| temp\_yr | 5.3 °C | **10.8 °C** | +5.5 °C |
| temp\_min | −5.9 °C | −0.5 °C | |
| temp\_max | 15.8 °C | 21.8 °C | |
| precip\_yr | 762 mm | 622 mm | −140 mm |
| runoff | 312 | 184 | −128 |
| elev\_max | 3838 m | 1975 m | Valley floor drops ceiling |
| slope\_avg | 124 | 77 | Flatter |
| stream\_gradient | 302 | 195 | |
| lith\_class | Intermediate Volcanic (VI) | Siliciclastic Sedimentary (SS) | |
| pnv\_majority | Grassland/steppe | Temperate deciduous forest | Flips to local riparian |
| river\_area | 6,788 km² | 1,085 km² | Local vs. upstream stat |
| pop\_density | 86 /km² | **607 /km²** | 7× — city vs. watershed |
| human\_footprint | 112 | 170 | |

### Variables that hold

| Variable | L06 | L08 |
|---|---|---|
| dist\_sink | 664 km | 664 km |
| endorheic / coast\_flag / karst | 0 / 0 / 0 | 0 / 0 / 0 |
| discharge (yr/min/max) | 181.7 / 29.1 / 645.2 | ≈ same (upstream stat) |
| pct\_clay / silt / sand | 22/43/35 | 23/40/37 |
| pct\_\*\_upstream | 22/43/35 | 22/43/35 |
| gw\_table\_depth | 459 | 392 |
| gdp\_avg / HDI | 8912 / 0.769 | 9119 / 0.769 |
| wetland\_class | Lake | Lake |
| permafrost\_extent | 1 | 0 |
| freshwater ecoregion | Kura - South Caspian Drainages | Kura - South Caspian Drainages |

**Summary of coverage:** Band C (bioclimate) flips entirely. Band A (terrain) sharpens.
Upstream stats (Band B discharge, Band C upstream aridity/precip/temp) hold because they
describe the same watershed above both basins. Band D urban signal intensifies 7× at L08
(city is in the valley basin). Band E holds (same drainage system).

**Demo line:** "At L06, the instrument says Tbilisi is in the Caucasus mixed forests, humid,
cold. At L08, it says Deserts & Xeric Shrublands, +5.5 °C warmer, 30 percentile points drier.
Both are correct — they measure different things."

---

## F3.3 — Northern Song gradient at L06 vs L08

**The gradient holds and very slightly sharpens at L08 — does not dissolve.**

Aridity (Band C), `representative_score` = area-weighted mean percentile; `spread` = p90 − p10:

| Year | Level | n\_units | Score | p10 | p90 | Spread |
|---|---|---|---|---|---|---|
| 961 | L06 | 156 | 48.8 | 35.8 | 66.9 | **31.1** |
| 961 | L08 | 1,407 | 47.2 | 33.9 | 67.0 | **33.1** |
| 970 | L06 | 228 | 58.8 | 38.2 | 80.4 | **42.2** |
| 970 | L08 | 2,506 | 57.3 | 35.6 | 80.5 | **44.9** |
| 980 | L06 | 375 | 69.7 | 39.6 | 88.6 | **49.0** |
| 980 | L08 | 4,217 | 68.1 | 38.5 | 87.7 | **49.2** |

Precipitation (Band C):

| Year | Level | Score | Spread |
|---|---|---|---|
| 961 | L06 | 57.2 | 28.8 |
| 961 | L08 | 56.3 | 29.8 |
| 970 | L06 | 63.5 | 30.2 |
| 970 | L08 | 62.7 | 31.1 |
| 980 | L06 | 72.7 | 40.4 |
| 980 | L08 | 71.9 | 39.9 |

**Key result:** L06 and L08 spread values are within 1–3 pp of each other at all three states for
both aridity and precipitation. The gradient sharpens as the polity expands (961→980); this
tracks the southern expansion into drier, lower terrain. L08 doesn't dissolve or contradict L06 —
it confirms the structural gradient with ~7–27× more basins.

**Implication for §6.4:** The CHAR guidance (prefer L06 for polygon queries covering few L06
basins, *unless within-polygon heterogeneity is the question*) is satisfied. For N Song, the
heterogeneity IS the question; L08 is the correct unit; and the L08 result confirms the signal.

**Implication for the demo:** the three-state expansion (961/970/980) is a clean narrative arc —
an expanding empire ingesting progressively more arid territory. The L08 number can be cited as
confirmation that the gradient is real and not an L06 artifact.

---

## F3.4 — Compare rendering: toggle carries the story

**The cheapest honest path for the Tbilisi scale-compare is the existing level toggle.**

The toggle already switches the basin layer source (`basin06.pmtiles` → `basin08.pmtiles`) and
fires `_silentResig()`. Once the L08 polity choropleth is fixed (F3.1 backend gap), the same
toggle will update the choropleth. The signature panel updates on every level change via the
settlement path (Settlements tab; verified working). On the Polities tab, after the F3.1 fix,
level-switching will repaint.

**For the Tbilisi point (Settlements tab):** the comparison is already live — switch L06/L08 and
watch biome and ecoregion labels change in the signature panel.

A genuine side-by-side (two map panes, synced viewport) would require:
- Two MapLibre instances sharing a viewport (possible but non-trivial state management)
- Separate choropleth paint paths for each pane
- Estimated 2–3 days of build
- Additional layout real estate on an already-dense surface

**Assessment:** the toggle + signature panel diff is a working demo interaction today (for
Settlements). It carries the Tbilisi story without side-by-side. For slides, screenshots at L06
and L08 are sufficient. **Do not build side-by-side for Braga.** If the Tbilisi toggle demo is
vivid enough at the conference table (it should be — biome changing from "Temperate Broadleaf
& Mixed Forests" to "Deserts & Xeric Shrublands" on a single click is striking), the case is
closed.

---

## F3.5 — Pacific Northwest (ARI.5): partial sandbox, slide-quality in Explorer

ARI.5 documents MAUP-sensitive basins in the Pacific Northwest where L06 basins averaging warm
coast + cold interior register as cold outliers in a warm neighborhood (LISA high-high / low-high
classification).

**In the sandbox:** the raw temperature and aridity choropleth IS visible — zoom into the Pacific
Northwest, select a Band C variable, and the heterogeneous pattern is apparent. The geographic
phenomenon can be pointed to.

**Not in the sandbox:** LISA classifications (`lisa_classifications.parquet`, gitignored) are only
in the Explorer paint path. The formal ARI.5 claim — "cold outlier in a warm neighborhood"
classified by local Moran's I — requires Explorer or a pre-rendered slide.

**Assessment:** ARI.5 is a slide, using Explorer screenshots. The sandbox can gesture toward the
geography but cannot render the finding. This is an acceptable answer.

---

## Open items surfaced

| Item | Where |
|---|---|
| Add `member_ids` to polity `neighborhood` response | Build task — F3.1 |
| L08 polity API latency (3.4 s for N Song) — feasibility for extensive polities | Open question pending F3.1 fix |
