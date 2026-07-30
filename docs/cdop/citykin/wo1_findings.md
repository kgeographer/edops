# CITYKIN WO1 — findings

Technical record for WO1 Part B's terrain lens (Tier 1: point-window facets) and its Part D
acceptance fixture. Tracker: `docs/cdop/citykin/CITYKIN_tracker.md` (summary + pointer only). WO:
`docs/cdop/citykin/wo1_update-whcities.md`. Notebook: `notebooks/cdop/citykin/wo1_validation.ipynb`
(Cells 1–10, all run). Exec summary for Opus: `wo1_exec_summary.md`.

---

## Part B step 1 — substrate: terrain persist + coverage

New table `gaz.wh_cities_terrain` (`scripts/cdop/citykin/persist_whcities_terrain.py`), a direct
analogue of WO8c's `persist_dplace_terrain.py`: OpenTopoData `mapzen` batch API, a 5×5 point grid per
city, `relief_range_m` = max−min elevation over the grid, `landform_position` = (mean−min)/relief
(0 = floor, 1 = ridge). Universe: the 254 `gaz.wh_cities` rows with a resolved `basin_id` (not all
258). `gaz.wh_cities.basin_id` references `basin08.id` (a serial PK), **not** `basin08.hybas_id`
directly — confirmed by inspection before the substrate query was written; getting this wrong would
have silently joined the wrong basins.

First run (grid radius ±2km, 1km spacing, unchanged from WO8c's society-terrain default): **254/254
resolved**, no fallback rows. Substrate assembled in the validation notebook (Cell 2): raw monthly
curves from `v_basin08_persist_rev2`, `ari_log = log1p(ari_ix_sav)` (carried from WO8b/8c), and the
three terrain facets — zero NaNs across all 254 rows on every column.

## Part B step 2 — terrain-facet correlation check

Cell 3, on the full 254: `grid_elev_mean` / `relief_range_m` / `landform_position` pairwise
correlation. No pair reached the WO8-standard |r| ≥ 0.70 Mahalanobis-or-drop bar (max |r| = 0.35,
elevation vs relief, at the original 2km radius). **Decision: plain Euclidean on z-scored facets, no
Mahalanobis, no drop-to-representative** — the three facets are near-independent on this corpus.

## Part D fixture, attempt 1 (±2km radius, 3-facet z-scored Euclidean) — failed

Tbilisi (41.6938, 44.8015 — canonical project coordinates since WO5; **not** a `gaz.wh_cities` row,
confirmed by query) fetched fresh via the same grid method, then ranked against the 254-city corpus.

The WO's own named "high valley floor" candidates (Kathmandu, Mexico City, Sanaa, Quito, Cusco —
Bogotá is not in the corpus) ranked **174th, 239th, 243rd, 248th, 252nd of 254** — nearly the bottom
of the whole corpus, the opposite of the intended result. Root cause, confirmed by inspecting their
raw facet values: their point-window read as **near-flat** (relief_range_m 17–73m) because a ±2km box
does not reach the highlands that actually enclose a classic intermontane basin (they sit many km
away from city center). Tbilisi's own ±2km box happened to catch real local relief (410m) close to
the point. Not a bug — the lens was measuring exactly what a ±2km window can see, which is a
different thing from "sits in a basin ringed by distant highlands." This is the Tier-1/Tier-2
boundary WO1 Part C already names (enclosure/containment is a relational, `ST_Touches`-based
facet the point-window structurally cannot see).

## Radius + density probes (Cells 7–8) — targeted, 6 cities only, not the full 254

Karl: "2km is not far at all." Probed box radii 2/5/10/20km (still 5×5=25 points, wider spacing) on
Tbilisi + the 5 named candidates:

- **`relief_range_m` climbs with radius indefinitely** (e.g. Kathmandu 73→260→987→2005m) — no natural
  ceiling; picking a radius is a judgment call, not a discovery.
- **`landform_position` is genuinely non-monotonic for some cities** (Kathmandu: 0.45→0.18→0.27→0.50;
  Quito: 0.23→0.31→0.32→0.48) — not obviously converging toward "floor" as the box widens.
- Mexico City is the clean exception: floor-like at every radius (0.29→0.19→0.16→0.15), sharpening
  with distance.

A density check (25 vs 81 points at 10/20km, same 6 cities) found the two grids agree closely at
10km for every city; only at 20km did the sparse grid miss something real (Quito's relief 1619 vs
2581m at 81 points — a genuine aliasing miss, not signal). **Decision: 25 points at ±10km/5km
spacing** — no added API cost over the original ±2km grid, and dense enough at that radius that
25 vs 81 points don't materially disagree.

`persist_whcities_terrain.py` updated to the new grid and rerun for the full corpus: **254/254
resolved** again.

## Part D fixture, attempt 2 (±10km radius, 3-facet z-scored Euclidean) — still failed

Named-candidate ranks improved only partially: Kathmandu 174→121, but Mexico City 239→242, Sanaa
243→227, Quito 248→253 (now *worse*, dead last), Cusco 252→252 (unchanged). Diagnosed directly: the
blocker was never the window size — it's that **elevation dominates a z-scored 3-facet Euclidean
distance**. Tbilisi's point-window mean elevation (673m at 10km) sits 500–3000m below the named
candidates' (1147–3756m); that gap alone swamps however well relief/position agree. One genuine
positive signal survived this attempt: **Yerevan ranked 7th** unprompted — same South Caucasus
basin-and-highlands geography as Tbilisi, comparable elevation — an independent plausibility check in
the same spirit as WO8d's Hopi/Hano/Navajo result.

## Karl's redesign — elevation as an eligibility gate, not a magnitude to compare

> "the valley/basin floor elevation doesn't matter much - it should be above some 'high' threshold...
> the idea is a settlement 'contained' by elevation"

A 500m valley floor and a 3000m valley floor can both be genuinely "high, contained" places; what a
raw z-scored elevation term was actually measuring is how far apart their absolute heights are, which
is a different (and not obviously relevant) question. Redesign: **elevation gates eligibility; the
ranking distance runs only on `relief_range_m` + `landform_position`** once a city clears the gate.

**Threshold derivation, not asserted:** the corpus's `grid_elev_mean` histogram (±10km radius data,
`gaz.wh_cities` joined to `gaz.wh_cities_terrain`, confirmed not the WHG gazetteer) is heavily
right-skewed — 55% of the 254 cities sit under 300m. A fine-grained scan (25m bins, 150–550m) found a
genuinely **empty bin at 350–375m** (0 cities), between a thin tail below (1 city, 325–350m) and a
thin tail above (2 cities, 375–400m: Notodden, Cáceres) — the same "real histogram trough, not a
fitted line" shape as the WO2 aridity gate. **`ELEV_HIGH_THRESHOLD = 400.0`** — sits just above the
trough, robust to a ±25m shift (only Notodden/Cáceres would flip), comfortably below Tbilisi (673m)
and every named candidate (1147–3756m).

83 of 254 cities clear the gate. Ranking distance: Euclidean on z-scored `(relief_range_m,
landform_position)`, mean/sd fit on the 83-city eligible pool (not the full 254) — their own
correlation is negligible (|r| = 0.01 at this radius), so no Mahalanobis needed here either.

## Part D fixture, attempt 3 (gate + 2-facet distance) — passed

| rank | city | country | dist | elev_mean | relief_range_m | landform_position |
|---|---|---|---|---|---|---|
| 1 | Yerevan | Armenia | 0.096 | 1148 | 749 | 0.421 |
| 2 | Palazzolo Acreide | Italy | 0.306 | 562 | 596 | 0.410 |
| 3 | Lijiang | China | 0.340 | 2737 | 912 | 0.398 |
| 4 | Bhaktapur | Nepal | 0.365 | 1539 | 634 | 0.376 |
| 5 | Guanajuato | Mexico | 0.466 | 2247 | 828 | 0.462 |
| 6 | Padula | Italy | 0.533 | 792 | 944 | 0.367 |
| 9 | Sucre | Bolivia | 0.603 | 2836 | 777 | 0.481 |
| 10 | **Cusco** | Peru | 0.626 | 3756 | 890 | 0.476 |
| 14 | **Sanaa** | Yemen | 0.709 | 2401 | 521 | 0.345 |
| 18 | **Shibam** | Yemen | 0.766 | 815 | 375 | 0.430 |
| 46 | **Kathmandu** | Nepal | 1.232 | 1570 | 987 | 0.275 |
| 77 | **Mexico City** | Mexico | 2.300 | 2276 | 270 | 0.161 |
| 83 (last) | **Quito** | Ecuador | 3.377 | 3067 | 2397 | 0.321 |

**Yerevan #1** (dist 0.096, effectively the tightest possible match) — same South Caucasus terrain
context, confirmed geographically plausible, unprompted twice now (also 7th in attempt 2). **Bhaktapur
#4** sits in the Kathmandu Valley itself. **Padula** confirmed by satellite/topo map (Karl): genuine
valley floor with steep, high terrain (600–1370m contours) close around it to the east. Four of five
named candidates now land at meaningfully better ranks: Cusco #10, Sanaa #14, Kathmandu #46 (was
174→121→46). **Mexico City (#77) and Quito (#83, dead last) remain excluded — for a principled reason,
not an artifact.** Mexico City's landform_position (0.161) is far more extreme-flat than Tbilisi's
(0.410) — a former lakebed, about as pure a "floor" as exists. Quito's relief_range (2397m) is ~3× 
Tbilisi's — a narrow shelf against an active volcano, far more extreme than a moderate valley. Both
are genuinely "high" (they clear the gate) but neither shares Tbilisi's specific containment *shape* —
which is exactly WO1 Part D's own acceptance language: "exclude high-flat and high-peak cities that
share only elevation." Mexico City is the flat case; Quito is the peak-adjacent case.

**Verdict: the Part D fixture passes**, on Karl + Opus's confirmed reading (2026-07-28). The named
candidates in the WO text were Opus's a priori guesses at what might show up, not independently
verified exemplars — several (Mexico City, Quito) are *correctly* excluded once the instrument
measures containment shape rather than raw magnitude, which is a more physically faithful result than
forcing all five into the top ranks would have been. Karl: "these are the WH Cities most similar to
Tbilisi wrt terrain… it is what it is" — an honest measure, not a fit to a preconceived expectation.

## Locked parameters (for Part B build)

- Grid: 5×5 = 25 points, ±10km box, 5km spacing (`persist_whcities_terrain.py`,
  `gaz.wh_cities_terrain`).
- Eligibility gate: `grid_elev_mean >= 400.0` (histogram-trough-derived, not arbitrary).
- Ranking metric: Euclidean on z-scored `(relief_range_m, landform_position)`, fit on the eligible
  subset only (not the full 254).
- Tbilisi queries by coordinate (not a corpus row) and needs the same gate check applied before
  ranking — it clears comfortably (673m ≥ 400m).

## Open / carried forward, not pursued now

- **Soft-weighting elevation instead of a hard gate** — Karl's own follow-on idea ("downweighting
  city elev might have a positive effect also"); not tried this WO. A continuous down-weight (rather
  than binary in/out at 400m) might smooth the Notodden/Cáceres edge case and let cities just under
  the gate compete on shape terms with reduced elevation influence rather than being excluded
  outright. Worth a look before or after UI wiring, not blocking it.
- **Kathmandu's mid-pack rank (#46)** may still reflect a Tier-2 (enclosure/containment) gap rather
  than anything fixable within Tier 1 — its own relief/position values are plausible but not
  standout; a bigger circumscribing ring than 10km can see might matter here specifically.
- Tier 2 (`ST_Touches` enclosure/containment) and Tier 3 (local DEM) remain named, not built, per
  WO1 Part C.
