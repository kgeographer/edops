# Note to Opus — terrain at basin scale: what WO1a's build reveals about the sandbox goal

Not a WO. A situation report, drafted at Karl's request, to ground a conversation about timing and
data acquisition for full basin-level terrain — the piece of EDOPS that's been deferred the longest
and that Karl considers essential, not optional, for the sandbox Similarity panel.

**Postscript, 2026-07-29 (Opus's WO3 tracker review):** this report's premise — that a Similarity-
panel Terrain regime lens requires the point-window method, and therefore either the ~75min L06 batch
job or a hosted DEM described below — turned out not to hold. WO3 shipped a coarse basin-scale
Terrain regime lens (`ele_mt_sav` + `relief_range`, already bulk-loaded BasinATLAS columns) without
either. The scale problem wasn't solved, it was **dissolved**: a coarse floor doesn't need the
point-window method at all, container-effect smearing and all, disclosed honestly in the lens's own
guide language rather than engineered around. The DEM-acquisition question below is **not moot** — it's
still the real path to a higher-fidelity, place-level basin-scale facet (this report's Tier-3 upgrade,
WO1 Part C's named-but-unbuilt horizon) — but it no longer blocks *having* a Terrain regime option on
the panel, which already exists. Findings: `wo3_findings.md`; tracker: `CITYKIN_tracker.md`.

## Where terrain currently stands

`app/db/seasonality.py`'s `LENS_REGISTRY` has carried a placeholder since early in the similarity
work: `"terrain.*": {"group": "Terrain", "label": "Terrain (coming soon)", "status": "disabled"}`.
CITYKIN WO1/WO1a just built the first real terrain instrument — but scoped to the 254-city WH Cities
corpus only, and it's worth being explicit about *why* that scope, because the reason is the same
thing that's been blocking basin-level terrain all along.

**The method**: for each city, sample a 5×5 grid of points (±10km box) via OpenTopoData's public
elevation API, compute local relief (max−min) and landform position (floor vs. ridge) from the grid.
Point-window, not basin-aggregate — WO8c already established that basin-aggregate elevation smears
container-scale terrain (a mountain-valley settlement averaged with the surrounding highlands loses
its own character entirely; Tbilisi is the canonical case). Validated end-to-end: two acceptance
fixtures (a contained high valley, a flat coastal city), both passing at shared query-relative
tolerance defaults, no per-city tuning (`wo1a_findings.md`). A real data bug was caught and fixed
along the way (OpenTopoData returns actual bathymetric depths, not null, for grid points landing in
open water — affected 88 of 254 cities before the fix).

**Why 254 cities and not all basins**: the precip/temp regime lenses already on the sandbox Similarity
panel work at basin scale because their raw ingredient — twelve monthly scalar columns per basin — was
already bulk-loaded into `basin06`/`basin08` during the original BasinATLAS import. The persist views
that expose them as arrays are a free, instant SQL reshape of data that was already sitting in the
table; no live computation happens per query. Terrain has no equivalent ingredient. BasinATLAS's own
basin-level elevation columns (`ele_mt_sav`/`smn`/`smx`) exist, but they're basin-*aggregate* — the
exact container-effect problem the point-window method exists to avoid. The point-window method itself
has only ever been run against 254 named coordinates, one live API call at a time.

## The scale problem, in numbers

Extending point-window terrain to basins means running the same acquisition step — not per query, but
once, as a batch backfill, the same way `persist_whcities_terrain.py` did for the 254 cities:

- **L06** (~16,397 basins × 25 grid points/basin ≈ 410,000 elevation lookups): roughly 75 minutes at
  the batch/rate-limit pace already in use (100 points/request, ~1 request/second) — plausible as a
  one-time job against the free public API.
- **L08** (~190,675 basins × 25 ≈ 4.77 million lookups): many hours at the same pace — not realistic
  against a free, rate-limited third-party API, and fragile even if run (network failures, API
  availability, no SLA on a free public service for a production dependency).

There is no way to make this "on the fly" per query the way the precip/temp views are — a live query
would need to fetch terrain for every candidate basin before it could even test membership, which is
the same hours-long cost paid at request time instead of once up front.

## What this means for priority

Karl's read, from prior discussion with you: **terrain deserves a full-throated per-basin
representation in EDOPS, not a permanently-scoped-down instrument** — this has been deferred since
early in the similarity work (the `LENS_REGISTRY` placeholder, WO1 Part C's own named-but-unbuilt Tier
3 "local high-resolution DEM" horizon item) and a "Terrain regime" option on the sandbox Similarity
panel is considered essential, alongside Precipitation/Temperature/Climate-union, not a nice-to-have
fourth option added when convenient.

The real fix is almost certainly **hosting a proper DEM raster locally** rather than depending on a
rate-limited public elevation API — the same category of decision as the project's other "no local
raster hosted, checked before building on a substitute" moments (WO8c's terrain module has the
identical note). A local DEM would let terrain characterization run as a real batch/zonal-stats
pipeline against `basin06`/`basin08` geometries directly (no per-basin live HTTP calls, no rate limit,
repeatable), and would also unlock WO1's own named Tier-3 upgrade path (richer point-window facets:
viewshed, aspect, hydrological position) for the WH Cities lens at the same time.

## What's not blocked by this

The WH Cities retrieval head (cdop_pilot) doesn't need any of this — its 254-city terrain data is
already acquired, validated, and sitting in `gaz.wh_cities_terrain`. That wiring proceeds now,
independent of this conversation.

## The question for you and Karl

Given terrain's priority, is it time to scope DEM acquisition (source, hosting, licensing, storage
footprint, integration into the basin06/08 pipeline) as its own work order — likely starting at L06
scale, matching how most of the similarity/conjunction/climate-class instruments already default to
L06 first — or is there a reason to hold further, and if so what would change that? Not answered here;
this is the situation, for the two of you to take from here.
