# Polity track — transition / approach (read me first)

**For:** the new conversation that will cut WO20.
**Phase:** Areas · **Sub-phase:** neighborhoods (final area type) · **Date:** 2026-06-27
**Read with:** current `CLAUDE.md`, `AREAS_tracker.md`, `deferred_items_register.md` (all freshly uploaded — they are the source of truth; this doc is orientation, not state).

---

## Where we are

The multi-basin work (basin-ring) is at a clean seam. The transition-character experiment (WO16–19) validated the magnitude comparator as a real, anchored, sample-stable instrument at L06-static scope, found direction mostly washes out at L06, and parked the cultural probe (no structured cultural data yet). That riff is **parked, not abandoned** — it was a speculative side-question on top of multi-basin, and the multi-basin engine work stands on its own.

**Polity is the last area type on the Areas list**, and the one the others were warming up to. Buffer / single-basin / ring all had boundaries the engine *constructs* (radius, watershed, adjacency). A polity (or a researcher-drawn study area) arrives with a **given** boundary — arbitrary in shape, crossing basins however it crosses them. That's the genuinely new resolver problem, and it's the meaningful-boundary version of what bboxes did badly.

---

## What the polity deliverable IS (settled this session)

Looking at Northern Song (dozens of L06 basins, hundreds at L08) made this concrete: **the honest polity object is not a signature scalar — it is the per-variable distribution across the constituent basins, with a geography, and it moves over time.**

- **No collapse to a polity-level number.** A single "N Song aridity" value averages desert-north and humid-south into a figure describing neither — the meaningless-mean error at its largest scale. The distribution *is* the answer; the map is its rendering. (Consistent with the locked resolve/serve + never-collapse-unless-forced principles.)
- **Membership rule — settled.** Admit every basin with any overlap; **area-weight** by fractional overlap (the WO15 principle, one level up: polygon-clips-basins is the same geometry as basin-clips-grid-cells); **no floor** (a floor would chop exactly the high-/low-value edge basins that carry the polity's environmental span — visibly destructive for N Song); **disclose marginal exposure** (a `coverage`/`shortfall`-style field: how much of the result rests on basins mostly outside the polygon). Treat the boundary as substrate for environmental purposes — no political-core weighting — unless we later decide otherwise on purpose.
- **Time-indexed.** A polity's boundary moves; membership is therefore a function of timestep (N Song's expansions annex new swaths of the gradient). The resolver returns "constituent basins **at timestep t**," and **boundary geometry and per-basin values are separable layers** — so the surface can hold one fixed and vary the other. This matters: when the slider moves, a shift could be environment-over-time *or* territory-over-time, and the engine must serve them unconfounded rather than pre-blending them.

---

## The cliopatria question — answered

`cliopatria.html` **predates the engine entirely.** So:
- It is a **throwaway preview**, not something to migrate or reconcile.
- **Inherit its interaction design** (validated, worth keeping): polity selection → timestep lookup from the cliopatria data → per-variable choropleth → time slider to "watch" the distribution and boundary move.
- **Build fresh everything that produces numbers:** the time-indexed polity resolver into the engine; area-weighted clipping; the uncollapsed per-basin distribution served through `areal_signature`; separable boundary/value layers; per-variable provenance/caveat.
- **Anticipate divergence from cliopatria's maps** — the engine-backed version will look different because it's correct (zero-aware scorer, area-weighted clipping, etc., none of which cliopatria had). That divergence is the engine correcting the preview, **not a regression** — same "blessed deviation" discipline as the frozen-TSV corrections. Flag it up front so no one compares old vs new and panics.

So **WO20 is a build, not a migration.** Make the proven surface a consumer of the real engine — closing the phase with every area type served by one resolve-and-serve contract, no bespoke side-channels.

---

## What's parked (not blocking WO20)

- **HYDE cropland trust question** — pending Ruth's reply. She reacted to the HYDE 1000 CE cropland over N Song. Diagnosis so far: HYDE's own ramp is honest (anchored at p99, ~80%); on a shared 0–100% ramp the HYDE-1000-vs-modern contrast is *real* (genuinely sparse past, not a ramp artifact). The open question is whether HYDE's *content* (likely its spatial allocation) is trustworthy for this region/period — a per-variable provenance/caveat decision on **one layer among ~50**, not an architecture blocker. Rejoins as a caveat-layer decision when she replies.
- **T as a general axis** — polity is the one neighborhood where T arrived *necessarily* (a polity without its temporal boundary is an anachronism), and cliopatria shows it's renderable. So polity isn't "deferring T"; it's where T is non-optional. Other area types' T deferral is separate.
- **Cultural probe / correspondence** — deferred to Phase 4 (needs structured cultural data, e.g. D-PLACE / Seshat). A turn to correspondence would leave the Areas phase; we're finishing Areas (polity) first.
- **Transition-character response object + L08 direction + ring-expansion** — parked outcomes of WO16–19; revisit if/when a use case pulls.

---

## Reusable part-pieces (protect from rediscovery)

- **WO15 area-weighted intersection** — the partial-unit weighting polity needs (polygon-clips-basin = basin-clips-cell, same geometry). Reuse, don't re-derive; confirm one shared weighting/quantile implementation.
- **"Bring forward neighbors' data"** — the sandbox already draws queried basin + neighbors but doesn't surface their data; that gap is the same shape as "surface a polity's constituent-basin data." Related wiring.
- **`resolve_single_basin` / `single_basin_signature`** (WO14) — the degenerate case the polity resolver generalizes.

---

## First moves for the new conversation

1. Confirm this approach still fits (membership settled, build-not-migrate, uncollapsed distribution + map, separable layers, T non-optional here).
2. Then cut **WO20**: the time-indexed polity resolver + area-weighted clipping + uncollapsed per-basin distribution through the engine, on **Northern Song** as the fixture, feeding the cliopatria-style surface. Likely first sub-step: the resolver and a single-timestep N Song run, before the time-slider/multi-timestep path.

Naming: last WO was WO19; next is WO20. Reference term for the old deployed signature path remains "v0.3 reference" (not "oracle").
