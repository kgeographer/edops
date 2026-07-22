# WO5 findings — Context tab; temperature lens diagnostic; hide Similarity

**Work order:** `docs/cdop/pilot/wo5_context-panel.md`
**Branch:** `cdop_pilot`
**Scripts:** `scripts/cdop/wo5_part_a_temp_lens_diagnostic.py` (live-API quartile/correlation probe),
`scripts/cdop/wo5_part_a2_temp_covariance_check.py` (direct-DB corpus-wide covariance check)
**Date:** 2026-07-21

---

## Part A — Temperature lens diagnostic

### Expectation, written down before running

Amplitude tracks rank cleanly, Q1 (nearest) high-amplitude to Q4 (farthest) low-amplitude — i.e.
the ranking itself is sound and `moderate` is simply too wide (a threshold problem). This was the
a priori guess per the WO's own framing of outcome 1; Part A exists to check it against outcome 2
(low-amplitude basins scattered through Q1/Q2, implicating `tmp_concentration`).

**Neither predicted outcome held.** The actual result is a third finding the WO didn't enumerate,
arrived at across three separate checks.

### Check 1 — Quartile / correlation probe (live API, `climate.temp`/moderate)

Tbilisi (41.6938, 44.8015) and Kaifeng (34.7986, 114.3413, control) queried via
`/api/similarity`, results binned by rank into quartiles.

Quartile medians for `tmp_seas_amp` are close to flat, not a clean gradient: Tbilisi Q1 22.4,
Q2 23.7, Q3 24.2, Q4 24.4 — drifting slightly *up* with distance, not down. Outcome 1 (threshold
problem) is out on this evidence alone.

Spearman correlation between distance and `|deviation from query|`, per variable:

| | Tbilisi | Kaifeng (control) |
|---|---|---|
| `tmp_seas_amp` | 0.402 | 0.547 |
| `tmp_dc_syr` | 0.383 | 0.646 |
| `tmp_concentration` | 0.175 | 0.316 |

`tmp_concentration` is the *weakest* correlate with distance for both probes — the opposite of
what outcome 2 predicted. What the table actually shows: **all three variables correlate with
distance more weakly for Tbilisi than for Kaifeng** — the metric is uniformly looser at Tbilisi's
location in variable space, not selectively broken on one dimension.

**A discrepancy, flagged rather than absorbed:** the original visual-review description (tracker,
WO3 section) cited "coastal Norway, 8–12°C annual range" among the false matches. Checked
directly against the full 852-basin moderate set (not just the gazetteer-linked subset): the true
minimum `tmp_seas_amp` anywhere in the set is 11.8°C, and every basin at or near that minimum is
in Yunnan, China or the Lesotho/South Africa highlands — not Norway. The ~250 high-latitude
(lat>55) basins found via gazetteer join all sit at 20–30°C amplitude, comparable to Tbilisi's own
21.7. Unable to confirm the specific "coastal Norway" claim as stated; noted as an open item below
rather than built on.

### Check 2 — Corpus-wide covariance structure (direct DB, all 16,397 L06 basins)

Replicates the production derivation (`app/db/seasonality.py` `_compute_derived` /
`_build_mahalanobis_state`) independently against `v_basin06_persist_rev2`, so the whole L06
population can be inspected, not just one query's admitted set.

- **Global correlation:** Pearson corr(`tmp_dc_syr`, `tmp_seas_amp`) = **−0.84** — a strong,
  well-known relationship (colder → bigger seasonal swing), but not deterministic.
- **Conditional spread is real and substantial at every temperature level**, not just Tbilisi's:

  | temp bin (°C) | n | mean amp | std amp |
  |---|---|---|---|
  | −15 to −10 | 718 | 42.2 | 9.1 |
  | −10 to −5 | 932 | 39.1 | 8.8 |
  | −5 to 0 | 1308 | 34.1 | 8.0 |
  | 0 to 5 | 1474 | 30.3 | 7.9 |
  | 5 to 10 (Tbilisi's bin) | 1479 | 24.8 | 8.4 |
  | 10 to 15 | 1211 | 21.7 | 7.1 |
  | 15 to 20 | 1833 | 15.6 | 6.4 |
  | 20 to 25 | 3238 | 10.3 | 7.0 |
  | 25 to 30 | 3782 | 7.5 | 6.0 |

  Standard deviation is consistently 6–9°C across the entire range — a real, substantial amount of
  natural climatic diversity (maritime vs. continental effects) at any fixed mean temperature, not
  noise specific to Tbilisi's band.
- **Tbilisi's own point is not a global outlier.** Self-Mahalanobis-distance-from-centroid (2-var
  subspace: `tmp_dc_syr`, `tmp_seas_amp`) puts Tbilisi at the **21st percentile** of outlierness
  against the full L06 corpus — *less* unusual than Kaifeng, the control, at the **54th
  percentile**. The sprawl on the map is not explained by Tbilisi being a freak combination.

**Conclusion of Check 2:** Mahalanobis distance is correctly computing whitened distance against
the real, strong-but-noisy global correlation. The metric isn't malfunctioning; the underlying
relationship between mean temperature and seasonal amplitude is genuinely this noisy everywhere,
and a single global covariance ellipse admits a wide band of real climatic diversity as
"consistent with the correlation" at any threshold wide enough to reach it.

### Check 3 — Does the composite distance let shape compensate for level? (the resolving finding)

Prompted directly by Karl: why does a lens labeled **Temperature regime** admit basins that are
obviously colder or warmer in absolute terms? Checked by comparing the admitted range of
`tmp_dc_syr` itself (not shape variables) at strict vs. moderate for Tbilisi:

| stringency | n | `tmp_dc_syr` range | `tmp_seas_amp` range |
|---|---|---|---|
| strict | 61 | [2.2, 8.1] (±3°C of query 5.3) | [19.2, 24.9] (±3°C of query 21.7) |
| moderate | 852 | **[−3.9, 14.9]** (±9–10°C of query 5.3) | [11.8, 31.5] (±10°C of query 21.7) |

At strict, "Temperature regime" behaves exactly as the label implies — absolute temperature and
amplitude both stay tight. At moderate, it doesn't: a basin nearly 10°C colder or warmer than
Tbilisi can still register as "moderately similar," because favorable agreement on `tmp_seas_amp`
and `tmp_concentration` compensates for a large mismatch on `tmp_dc_syr` inside the whitened
3-variable distance — and because temp and amplitude are strongly correlated globally (Check 2),
"colder with proportionally higher amplitude" is treated as a cheap, expected direction to move
in, not a violation.

**This is the finding that actually resolves the standoff.** The map is not lying (the arithmetic
is correctly computed) and it is not simply "honest reporting" in the sense that matters to a
user (the label promises something the composite metric doesn't deliver at moderate/loose). The
lens bundles absolute level (`tmp_dc_syr`) with shape (`tmp_seas_amp`, `tmp_concentration`) under
one name and one composite distance, and the threshold determines how much compensation between
them is tolerated — tight at strict, large at moderate. This is the same shape of problem WO3
found in `climate.phase` (one label bundling questions that don't share an answer), recurring in
`climate.temp`.

### Practical implication for WO5 Parts B–E

The Context tab as already spec'd (Part C) reports mean temperature and seasonal range as
**separate percentile rows**, not a composite distance. There is nothing for shape to compensate
against, because nothing is being blended into one number — a basin 10°C colder than the query
would show a plainly different percentile on the temperature row by itself. Shelving Similarity
and shipping Context is not a workaround for Check 3's finding; it is already the correct
structural fix, arrived at independently in the WO before this diagnostic ran. No design change
to Parts B–E indicated by Part A's results.

### Answer to the WO's two-outcome framing

Neither predicted outcome (threshold-too-wide / `tmp_concentration`-is-admitting) is what
happened. The actual mechanism has three parts: (1) the metric is uniformly looser at Tbilisi's
location than at Kaifeng's, not selectively broken on one variable; (2) that looseness reflects
real, substantial, globally-consistent climatic diversity at any fixed mean temperature, not a
Tbilisi-specific anomaly; (3) the composite "regime" distance lets shape variables compensate for
level mismatches, and how much compensation is tolerated is entirely a function of the
(uncalibrated) threshold radius.

---

## Detour — direct peak-counting vs. `R_dbl` for modality (instigated by Karl)

Not in WO5's scope; logged here as a detour rather than folded into Part A or B. Arose from a
discussion of a possible alternative similarity instrument (percentile-per-variable vector,
Euclidean, no compensation) where modality was proposed as a raw peak count (1 or 2 rainy
seasons) rather than the existing `R_dbl` harmonic-ratio measure. Prompted the question: does
direct peak-counting on the monthly curve actually do better than `R_dbl`, including on the one
case (Timbuktu) already known to be `R_dbl`-wrong?

**Method:** circular local-maxima detection over the 12-month `pre_mm_monthly` array (handling
December→January wraparound), filtered by topographic prominence — for each candidate peak, walk
outward in both directions to the lowest point reached before the curve rises above the peak's
own height again; prominence = peak height minus the higher of the two valley floors. Threshold
swept as a fraction of each basin's own annual range (10/20/30/40%), so "counts as a real second
peak" means the same thing (a dip of at least X% of the seasonal range) regardless of a basin's
absolute rainfall. Script: `scripts/cdop/wo5_modality_peak_count_probe.py`.

**Result — peak-counting beat `R_dbl` on both of `R_dbl`'s known failure directions:**

| Probe | Peak count (10–40%) | `R_dbl` verdict | Agreement |
|---|---|---|---|
| Timbuktu | 1 at every threshold | bimodal (R_dbl=0.575) — **known false positive**, Fourier artifact of a sharp single peak | Peak-counting correct; `R_dbl` wrong |
| Mombasa | 2 at 10%, 1 at 20%+ (2nd peak prominence = 18% of range) | bimodal (R_dbl=0.341) — validated, but flagged elsewhere (WO4 Part 4) as the thinnest-margin case | Both agree it's real but marginal — convergent, not just consistent |
| George Town | 2 at every threshold (2nd peak prominence = 55% of range) | "aseasonal" (R_dbl=0.187) — excluded from bimodal | Peak-counting disagreed; **checked against the sandbox Seasonality panel chart, which shows an unambiguous two-peak curve** (Apr/May bar, trough at Jun, taller Oct/Nov bar) — `R_dbl` wrong here too |
| Augsburg | 1 at every threshold | no strong prior (temperate lens probe, not a modality probe) | Consistent with expectation |

Confirmed against the live Seasonality tab's monthly bar chart for George Town: two clearly
separated bars (Apr/May and Oct/Nov) with a real trough between and a softer one in
Dec–Feb — the chart itself supports "bimodal" unambiguously, contradicting `R_dbl`'s "aseasonal"
call. Peak-counting matches the chart; `R_dbl` doesn't.

**Net:** across the four probes checked, `R_dbl` is wrong on two (Timbuktu false-positive, George
Town false-negative) in opposite directions, and peak-counting is correct on all four, including
agreeing with `R_dbl` on the one case (Mombasa) it gets right. Timbuktu's correction is by
construction, not tuning — peak-counting never touches harmonics, so it can't inherit the
Fourier-concentration artifact that produces `R_dbl`'s false positive there.

### Design direction surfaced by this result (not built) — modality as a gate, not an axis

Karl proposed, given peak-counting's better accuracy: use modality as a hard eligibility filter
rather than a weighted term in a percentile-vector similarity instrument (annual mean, amplitude,
modality) — a basin can't register as similar at all unless it matches the query's modality class
(peak count), with the continuous axes doing the ranking only *within* that matching set.

This is a different role for modality than the one WO2a's "`same_modality` dropped" locked
decision addressed — that finding was about adding same-modality as a fourth *distance term*
inside the existing continuous harmonic embedding `(a1,b1,a2,b2)`, where it was redundant because
the embedding already separates modality classes implicitly. A hard gate in a differently-built
instrument (explicit percentile axes, not fitted harmonics) is a distinct proposal; the WO2a
finding doesn't bear on it. A gate also avoids a real problem with treating modality as *any*
weighted continuous axis: it's a discrete class, not a graded quantity, so it either gets diluted
against continuous terms or degenerates as a near-constant percentile axis — gating sidesteps
both by construction.

The gate would need to run on peak-count, not `R_dbl`, given the result above — using `R_dbl`
would re-import its false positive/negative pattern into the filter itself.

**On the "zero results" objection:** a gated query can return no matches at all if nothing shares
the query's modality class. Per WO4 Part 2, that is an honest-scarcity result, not a failure mode
to design around — Karl's point: this only becomes a real problem as variable count grows large
enough that most basins become functionally unique (a curse-of-dimensionality effect), and a
3-variable vector (mean, amplitude, modality-gate) is nowhere near that regime.

**Not acted on.** Both the peak-count measure and the gating design are detour results, not WO5
deliverables — `pre_modality`'s underlying computation and any new similarity instrument are out
of WO5's scope. Noted here so neither is lost; candidates for a future WO.

---

## Part B — Context data path

**New module:** `app/db/context.py`. **Route:** `GET /api/context`. **Wired at startup** in
`app/main.py` alongside the existing similarity index. **Probe scripts:**
`scripts/cdop/wo5_part_b_schema_check.py`, `wo5_part_b_context_probe.py`,
`wo5_part_b_radius_density_check.py`.

### Variable set (locked design decision)

Seven rows, within the WO's 6–8 range: mean annual precipitation (`pre_mm_syr`), mean annual
temperature (`tmp_dc_syr`), seasonal temperature range (`tmp_seas_amp`), mean elevation
(`ele_mt_sav`), mean slope as the relief/roughness candidate (`slp_dg_sav`), aridity index
(`ari_ix_sav`, log1p-transformed before ranking per the catalog's own position_method), annual
runoff (`run_mm_syr`). All six raw scalar columns confirmed present on both `basin06`/`basin08`
before building.

Two variables needed to be computed independently rather than reused from existing
infrastructure:

- **`ele_mt_sav` (mean elevation) is not in `basin08_scores`** — the catalog's own
  `elevation_mean` row is stuck at status `"planned"` (never wired into `load_catalog` or the
  materialized-scores build), even though the raw column exists and is the same shape as
  `elevation_max`/`elevation_min`, which *are* implemented. Confirmed via the catalog's own
  position-notes field ("best-effort; not yet implemented") — no data-quality reason, just
  unpicked backlog. Logged in `docs/design/deferred_items_register.md` under "Catalog
  housekeeping" as a low-cost fix for whoever next touches the Areas/catalog pipeline; WO5 does
  not depend on that fix landing.
- **`tmp_seas_amp` (seasonal temperature range) is derived**, not a raw column — same computation
  already used by the `climate.temp` similarity lens (`TMP.max(axis=1) - TMP.min(axis=1)` from
  the monthly array), recomputed independently here rather than importing from
  `seasonality.py` to keep the two modules decoupled.

### Architecture

An in-memory index loaded once at startup, mirroring the existing similarity index pattern in
`app/db/seasonality.py`, rather than querying `basin08_scores` or running `PERCENT_RANK` per
request. `load_context_index(conn, level)` loads `hybas_id`, a basin representative point, and
the seven variable arrays per level; global percentiles are precomputed once (numpy rank,
matching Postgres `PERCENT_RANK` semantics: `rank / (n_valid - 1) * 100`, ties averaged, NoData
excluded from the ranking population). `get_context(...)` computes within-radius percentiles at
request time via vectorized haversine distance (numpy, <50ms even at 190k L08 basins) — no
spatial SQL per request, so radius stays a genuinely free parameter rather than needing a
precomputed fixed-radius fallback.

**Basin representative point: `ST_PointOnSurface`, not `ST_Centroid`** — raised by Karl during
design review. A plain geometric centroid can fall *outside* a concave or crescent-shaped basin
polygon; this is the exact mechanism behind the WO17/WO18 incident in memory
(`feedback_no_glide`) where a centroid-outside-polygon silently resolved to the wrong basin.
`ST_PointOnSurface` is guaranteed to land inside the polygon. Only used for the *other* basins
being tested for radius membership — the query origin is always the caller's exact clicked
lat/lon, never a basin representative point, since (per the same review exchange) a basin
centroid is "a not very discriminating pair of coords" for that purpose.

### Cross-validation against WO4 Part 5 — independent confirmation

WO4's notebook (different implementation, ~24 hours earlier, no shared code) computed
local-anomaly percentiles at radii not stated precisely in km. This module's L06/1000km output
matches it closely:

| Probe | WO4 Part 5 (n, precip%, temp%) | This module, L06/1000km | Agreement |
|---|---|---|---|
| Tbilisi | n=344, 63.6→91.9, 30.0→**2.6** | n=341, 63.6→92.2, 29.9→**2.6** | essentially exact |
| Kaifeng | n=343, 61.2→52.2, 45.5→65.0 | n=343, 61.2→52.3, 45.5→65.6 | essentially exact |
| Timbuktu | n=415, 17.0→47.2, 98.1→61.9 | n=417, 16.9→47.8, 98.2→63.5 | close (≤1.6pp) |
| Mombasa | n=253, 75.4→77.5, 79.1→64.0 | n=253, 75.4→77.2, 79.3→64.9 | essentially exact |

Two independently-built implementations agreeing to within ~1.6 percentage points, with basin
counts matching almost exactly (two exact, two off by 2–3). Small residual differences plausibly
trace to the `ST_PointOnSurface`-vs-`ST_Centroid` change or a different exact-radius method
(haversine vs. PostGIS `ST_DWithin`/geography). Treated as strong confirmation the module is
correct, not investigated further.

### Radius/level viability — investigated properly before committing to a design

Initial check used only the 4 WO4 climate probes and looked concerning: L08 counts ran roughly
10–11.6× L06's at every radius (matching the tracker's known L06→L08 basin-count ratio), and at
2500km, L08 hit 16,000–23,000 basins per probe against Part C's own stated ~5,000-basin WebGL
comfort ceiling. Karl's objection: 4 climate-diversity probes say nothing about basin *density*
(which drives radius count), and coding a level-dependent restriction without understanding real
behavior would be a mistake, especially given L08 has to be supported eventually regardless of
what Context ships first.

**Broader check**, `wo5_part_b_radius_density_check.py`: full 258-city WH Cities corpus (real,
geographically diverse settlement locations, not curated climate probes), radius counts computed
directly against the already-loaded index (haversine, no per-city DB round trip), at all four
radii and both levels.

| | L06 | L08 |
|---|---|---|
| 250/500/1000km | 0% of 258 cities over 5,000-basin budget at any of these | 0% of 258 cities over budget |
| 2500km | 0% over budget (max 2,163) | **99.2% over budget** (256/258 cities; median 13,845) |

Worst case in the safe zone: L08/1000km at Lijiang, China — 4,579 of 5,000 (92% of budget), real
but not over, across a geographically diverse sample. The picture is much narrower than the
4-probe check suggested: **it is specifically the 2500km radius that breaks at L08, almost
universally — not a general L08 problem.** 2500km at that radius/level covers ~13% of all land on
Earth (2500km is 12.5% of the maximum possible great-circle distance between any two points,
~20,000km) — a scale mismatch with "neighborhood," not a rendering fluke.

**Decision:** both levels offered with the same 250/500/1000km radius options; 2500km available
at L06 only. Enforced server-side — `/api/context` returns 400 for `radius_km=2500` at `level=8`.
Implemented, not just designed: `_CONTEXT_RADII_BY_LEVEL` in `app/api/routes.py`.

### Verification

`GET /api/context?lat=41.6938&lon=44.8015&level=6&radius_km=500` (Tbilisi) returns matching
values to the standalone probe script. `level=8&radius_km=2500` correctly returns HTTP 400.
`_resolve_basin` generalized to take a `level` parameter (default 6, preserving the existing
`/api/similarity` caller's behavior exactly) rather than adding a duplicate function — confirmed
via `pytest tests/test_api_examples.py -k similarity` (4 passed) and the full app suite
(`pytest tests/ --ignore=tests/engine/ --ignore=tests/surface`: 213 passed, 14 skipped, 0
failures, no new warnings).

### Open item carried from this part

- WO5's own accept-gate prose is slightly imprecise against the actual data: "near-median global
  temperature against bottom-few-percent within 500 km" for Tbilisi. Global temperature
  percentile is 29.9 (moderately below median, not "near-median" — WO4 itself said "not a global
  outlier," a more accurate framing). The striking 2.6th-percentile figure comes from ~1000km,
  not 500km (at 500km it's 11.2th — still low, just less dramatic). Not urgent; worth tightening
  before Part C's own accept-gate check cites it as more precise than it is.

---

## Part C — Context tab UI

**New tab:** `Context`, placed between Seasonality and Similarity on `sandbox_v3.html`, per spec.
Similarity left in place (hiding it is Part E, not done here). Table (7 rows: variable, value,
global percentile, within-radius percentile), a radius segmented control (250/500/1000km both
levels; 2500km L06 only, enforced client- and server-side per Part B), and a MapLibre choropleth
of the radius population colored by whichever row is selected — no refetch on row click, only on
radius/level/location change (`GET /api/context` + `GET /api/context/population`, the latter added
during this part specifically to supply per-basin raw values for the map, paired with the existing
`POST /api/basin-geom` for geometry). One row-click sets the map variable; population values are
cached client-side so switching rows repaints without a new fetch.

One small addition beyond the WO's own mockup: each table row shows the raw value+unit inline
next to the label (e.g. "Mean annual precipitation (762 mm/yr)"), not just the two percentiles —
judged worth the extra half-line for readability, not run past Karl before building, flagged
after the fact.

Left-column visibility state: `#v3-choropleth` (the Map tab's own variable selector + legend)
now only displays while the Map tab is the active right-column tab — hidden for
Signature/Analysis/Seasonality/Context/Similarity, restored on returning to Map, cleared on full
reset (`_choroplethRevealed` flag + `_syncChoroplethVisibility()`, wired to every right-column
tab's `shown.bs.tab` event). Previously this panel stayed visible regardless of which tab was
shown once first revealed — a real state-management gap Karl caught by inspection, not something
WO5's own spec mentioned.

### Plausibility check — San Francisco, second independent container-problem instance

Karl poked at the SF example (37.7749, −122.4194) and questioned the mean-annual-temperature
choropleth: Sierra Nevada basins reading much colder than the Bay Area. Checked directly
(`scripts/cdop/wo5_sf_basin_check.py`):

- **L06 basin containing the SF click point is 11,378 km²**, bounding box spanning roughly
  36.28°N–38.06°N (Monterey Bay's latitude to past Napa), elevation range **−14m to 1,588m**.
  Mean elevation 321m — the tell, since SF the city sits at ~50-60m. This is not "San Francisco,"
  it's a large Coast Range drainage basin that happens to contain the point.
- **L08 genuinely subdivides here** (unlike Mombasa's identical-L06/L08 case from WO4 Part 0):
  2,548 km² (4.5× smaller), elevation range narrows to −6m–975m, mean elevation 321m→217m,
  temperature 14.2°C→13.4°C — closer to SF's real ~13.8°C climate normal. Matches WO4 Part 0's
  corpus-wide finding exactly: L08 roughly halves the gap, doesn't eliminate it (217m mean is
  still ~4× the city's true elevation; 2,548 km² is still ~20× the city's actual area, ~121 km²).
- **The Sierra-vs-Bay-Area contrast on the map itself is real climatology**, not an artifact —
  Sierra basins sit at genuine high elevation (2,000–4,000m+), and real lapse-rate physics makes
  them much colder than coastal/valley California. That part of the map is telling the truth
  independent of any container issue.
- **Karl's sharper framing, worth keeping over my first-pass explanation**: this isn't about the
  basin extending into a *specific wrong kind* of terrain (Tbilisi's story — mountains swallowing
  a valley city). It's that **basin size itself outscales the topographic variety already present
  nearby** — the Bay Area has real hills on both the east and west sides at a scale far smaller
  than an 11,378 km² unit, so a basin this size averages over that variety regardless of which
  direction it extends. Basin size is the mechanism, not a directional bias in what got included.

### Reframe: the container effect is not a measurement problem

Karl's correction, worth recording exactly because it's the same shape of insight as the WO4
locality reframe, applied to a different topic: **the basin-scale average is a correct, direct
read of the source data — there is nothing to fix, because there is nothing wrong.** "Container
problem" names a real property (a basin is not the same object as a settlement), not a defect in
how Context computes or reports it. Context's design — no ranking, no composite score, stated
percentiles against a stated population — is the right instrument for surfacing that fact
honestly, in contrast to Similarity's composite distances, which promised more precision than
they delivered (Part A Check 3). Verdict, Karl's words: Context "does its advertised job more
effectively than Similarity," and "one can't argue with direct reads of vars from the source we
are using." The bold city-name title was flagged as a minor, non-blocking wrinkle — readable
correctly once the tab name ("Context," not "Signature") is noticed; left as-is.

### Color ramp alignment with the Map tab

Karl identified that Context's choropleth and the existing Map tab's `applyBasinVar` choropleth
are functionally overlapping (both paint basins by a variable's value) but used different,
uncoordinated color conventions — worth reconciling once flagged, not worth avoiding the overlap
retroactively, since the two answer genuinely different-scoped questions (Map's domain is the
global p10/p90; Context's is the radius population's own min/max — literally the table's two
columns). Fixed:

- **Moisture variables** (`pre_mm_syr`, `ari_ix_sav`, `run_mm_syr`): now share `RDBU_PAL` with
  Map's own `aridity_index`/`precipitation_annual` convention exactly — dry=red, wet=blue.
  Context's first pass had this backwards (low value/dry mapped to blue).
  Prompted directly by Karl reviewing an L08 SF precipitation render (screenshot) where the
  colors read as the opposite of the intended convention.
- **Temperature** (`tmp_dc_syr`): confirmed already correct — cold=blue, warm=red, matching
  Map's `temperature_annual` (`reverse: true`).
- **Elevation and slope** (`ele_mt_sav`, `slp_dg_sav`): new terrain (hypsometric) palette,
  `TERRAIN_PAL` (green→tan→brown→light gray, Google Maps terrain-layer convention) — RdBu doesn't
  apply to a non-climate axis. Still scaled to the radius population's own min/max, not a fixed
  global domain, consistent with every other row.
- **Seasonal temperature range** (`tmp_seas_amp`): initially given the same treatment as mean
  temperature (red=high), flagged as a provisional guess. Corrected on review — amplitude is a
  magnitude of swing, not a warm/cold axis, so it doesn't belong on either the moisture or
  temperature ramp. Got its own light-grey→purple sequential scale, `AMPLITUDE_PAL` (narrow
  range=grey, wide range=purple).
- Implementation: added a generic `interpPalette(pal, t)` N-stop interpolator alongside the
  existing `RDBU_PAL`/`interpRdbu` (left untouched, Map-tab-tested code), plus
  `CONTEXT_VAR_RAMP`/`_ctxColorFor`/`_ctxLegendGradientCss` to dispatch per variable. Context's
  map layer switched from a MapLibre `interpolate` paint expression to per-feature precomputed
  `fc` properties (matching Map's own `setFeatureState`-with-precomputed-color pattern) — needed
  to reuse the same JS color functions Map already uses, and incidentally fixes a real edge case
  the `interpolate` expression had: it throws when every basin in a small radius shares one value
  (e.g. slope=0 across a flat plain), since `interpolate` requires strictly increasing stops.
- **A real bug caught during this fix, before any browser test**: `CONTEXT_RAMP_PALETTES`, a
  `const` object literal, initially sat near the top of the script but eagerly evaluated
  `TERRAIN_PAL`/`AMPLITUDE_PAL`, which are declared ~2,300 lines later next to the Map tab's own
  palette constants. Unlike function bodies (hoisted, safe to forward-reference), a `const`
  literal evaluates its values immediately at its own declaration line — this would have thrown
  `ReferenceError` on every page load, breaking the entire script, not just Context. Caught by
  static reasoning about JS temporal-dead-zone semantics, not by browser testing. Fixed by moving
  the palette-dependent lookup code down next to `TERRAIN_PAL`/`AMPLITUDE_PAL`.

`tmp_seas_amp` clarified for the record: derived, not a raw BasinATLAS column — 
`max(monthly mean temp) − min(monthly mean temp)` across the 12-month array, same computation
`climate.temp`'s similarity lens uses, recomputed independently in `context.py` per that module's
own decoupling decision (Part B).

### Verification

Page renders (HTTP 200), brace/paren counts balanced pre- and post-edit (coarse JS syntax check —
no browser available to this agent; visual review is Karl's, per standing practice), full app
test suite green throughout (213 passed, 14 skipped, 0 failures) after every edit round in this
part.

### Not yet done

Part D (rule-based blurb) and Part E (hide Similarity tab — hide only, not remove markup/code/
route, per Karl's explicit correction to the WO's "retire" framing) remain open.

---

## Open items

- **"Coastal Norway, 8–12°C" claim (WO3-era visual review) does not reproduce** against a direct
  query of the full 852-basin moderate set for Tbilisi. True minimum amplitude in that set is
  11.8°C (Yunnan, China / Lesotho highlands, not Norway). Possible explanations not yet
  distinguished: different query coordinates, a different threshold, or an imprecise
  recollection from the original visual pass. Not built on; flagged for whoever wants to run it
  down.
- **Kaifeng-band-outlier wrinkle, unresolved.** Kaifeng's own `tmp_seas_amp` (27.7) sits *above
  the 90th percentile* of its own temperature band (12.8–16.8°C, p90=26.9) — Kaifeng is itself an
  outlier within its band, yet its similarity map reads as coherent and its Spearman
  distance-correlations are *stronger* than Tbilisi's across all three variables. Why an
  outlying query produces a tighter-behaved result here is not explained by anything in this WO;
  noted, not chased further.
- Threshold recalibration and any metric change remain explicitly out of scope for WO5 (per the
  WO's own "out of scope" section) — Check 3's finding motivates recalibration or a metric
  rethink as a real, evidenced case, but building it is not part of this WO.
