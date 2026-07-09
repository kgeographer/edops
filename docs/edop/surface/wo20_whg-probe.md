# WO20 — WHG settlement lookup: probe + integrate as the point-resolver

**Branch:** `surf_wo20`
**Type:** Probe → integrate. **First task is investigation** (the WHG API is a moving target; the
payload is the unknown everything downstream waits on). No integration is built against a remembered
schema — only against what the current API actually returns. Opens Arc A (deployability).

This is goal-setting, not a spec. State-management mechanics are CC's to settle with Karl on the
real payload; targets and provisos below.

## Goal

Bring the WHG lookup (ported from sandbox v1) live as the **point-resolver for the settlement/site
lane**: a user picks a settlement/site, WHG returns candidates, choosing one resolves a coordinate,
and **single-basin fires immediately** for that point with Get Signature activated. This is the entry
to the point-anchor-with-lenses model — single is the entry lens; buffer and ring broaden from the
same fixed point.

## The input model this serves (context, not this WO's whole scope)

The page's first question becomes **settlement/site or area?** — plain language, not scope-type.

- **Settlement/site** → WHG lookup (this WO) → pick candidate → single-basin fires → optionally
  broaden to buffer/ring over the same point.
- **Area** → existing Cliopatria machinery, unchanged (polity is area's first member; regions and
  user-drawn come later).

WO20 builds the settlement/site lane's resolver and its immediate single-basin fire. The full
state model (scope-root return, lens-toggle persistence, example-as-tree-collapse) settles across
Arc A; WO20 lays the resolver it stands on. Don't over-reach into the area lane or the lens
machinery here beyond what's needed to fire single-basin on a resolved point.

## Task 1 — Probe the current WHG API (do this first, report before integrating)

The WHG API has been a moving target; treat its payload as **discovered, not assumed**. Establish,
against the live API:

- What endpoint(s) and params yield settlement/site candidates, and what the response actually looks
  like now (fields, coordinate shape, feature-type markers, IDs, any period/name metadata).
- **How to filter candidates to point locations.** WHG carries mostly populated places but some
  places have areal extents. We want to investigate filtering candidate results to point/settlement
  types. Report what the payload exposes that supports such a filter (a feature-type field? a
  geometry-type discriminator?) — and if the API can filter server-side vs. whether we filter
  client-side on returned candidates.
- **The areal-extent case:** how does a candidate that *has* an extent (not a point) appear in the
  payload, and — noted, not necessarily solved here — does it still resolve to a point for the core
  basin, or is that a later wrinkle? See what the payload shows rather than deciding in advance.

Report the probe findings (`wo20_findings.md`, plus a short payload sample) **before** wiring
integration, so you and Karl settle the resolution model on real data. This is the review gate that
matters most in this WO.

## Task 2 — Integrate as the point-resolver (after the probe settles)

Port the v1 WHG lookup UI (candidate list + map markers, as it works now) into the settlement/site
lane. On the resolved payload:

- Candidate results appear with map markers (v1 behavior).
- Label the lookup as **settlement lookup** — it's a settlement-lookup service, and saying so is
  honest about what WHG resolves.
- Apply the point-location filter established in Task 1.
- **Choosing a candidate → single-basin fires** for its coordinate (existing single-basin path, WO10/
  WO11 — the basin outline draws, the signature is resolvable), and **Get Signature activates**.
- From a resolved point, the user can broaden to buffer or ring over the **same** point (switchable,
  radius adjustable for buffer). Wire only what's needed for the lens toggle to operate over the
  fixed point; the full anchor-persistence state model is CC's to settle across Arc A.

## Provisos

- **Probe before integrate** — no integration against an assumed schema; the payload is the unknown.
- The WHG lookup feeds the **point-rooted lane only** — it is not the polity/area search (that's the
  separate Cliopatria lane, unchanged).
- If the current WHG API differs materially from v1's (params, payload shape, auth), that's a probe
  finding to surface with Karl, not to work around silently.
- State-management specifics (how the anchor persists across lens toggles, how a resolved point
  clears on crossing to the area lane) are **CC's to work out** — the goal is a working point-resolver
  that fires single-basin; the state model is settled with Karl, not dictated here.
- Don't touch `sandbox.html` (v1) or the existing Cliopatria/area path.

## Accept gate

- Probe findings reported and reviewed **before** integration: params → payload, point-filter
  approach, areal-extent behavior.
- WHG lookup live in the settlement/site lane, labeled as settlement lookup, candidates filtered to
  point locations, markers on the map.
- Choosing a candidate fires single-basin and activates Get Signature.
- Buffer/ring reachable as lenses over the resolved point (radius adjustable); the point holds across
  the lens toggle.
- Area (Cliopatria) lane and `sandbox.html` untouched.

## Tests

- Probe is investigative (no assertions on a live external API in the suite — mock or fixture the
  payload shape once known, and test the client-side filter + candidate→single-basin fire against
  that fixture).
- Playwright to the extent the choropleth-suite skip-pending-state-model status allows; match that
  honesty (write it, skip under the same trigger if others are). Note status.
- Engine/app suite green — zero FAILs, zero unexplained warnings. Note counts.

## Findings

`docs/edop/surface/wo20_findings.md`. Report: the WHG probe (endpoint/params → payload, with a
sample); the point-location filter approach (server-side vs client-side) and what payload field
supports it; how areal-extent candidates appear; how the current API differs from v1 if it does; the
candidate→single-basin fire; what state-model decisions you and Karl settled on the real payload.
