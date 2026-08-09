# Similarity instruments

*Placeholder — content in development. Scoped 2026-08-08; see `logs/session_log_20260808.md`
for the working session this was scoped in.*

This page covers the app's similarity-search features: Sandbox's Similarity panel and
Workbench's WH Cities similarity dropdowns. They share vocabulary ("regime," "similar") but are
**not** the same mechanism — that's the reason this page exists, rather than folding a paragraph
into each surface's own overview. It does not cover Workbench's Societies-tab environment↔culture
correspondence testing (PERMANOVA, family-restricted permutation) — a statistical-correlation
question, not a nearest-neighbor retrieval one; out of scope here, see [Out of scope](#out-of-scope).

## Comparison at a glance

- [ ] `[wire]` Table: surface/lens, mechanism (conjunction / distance-rank / gate+rank / text),
      output shape (unranked set vs. ranked top-N), data source, level.

## Sandbox's Similarity panel — one method

- [ ] `[prose]` Non-compensatory **conjunction** (`find_conjunction`,
      `GET /api/similarity/conjunction`, `app/db/seasonality.py:CONJ_LENSES`). Four lenses:
      `climate.precip` (raw monthly-curve shape correlation + magnitude ratio + amplitude CV),
      `climate.temp` (level + seasonal range), `climate.union` (both combined, 5 conditions),
      `terrain.regime` (basin-aggregate `ele_mt_sav`/`relief_range` from precomputed BasinATLAS
      columns). Every condition is a query-relative ± band; membership is AND across all of them.
      Output is the **full unranked set** of matching basins — no limit, no distance sort ("a
      painted set, not a ranked list," per the route's own docstring). Level toggles L06/L08.

## Workbench WH Cities — three separate mechanisms

### Precipitation / Temperature regime ("Similar (env)" dropdown)

- [ ] `[prose]` Despite the "regime" label matching Sandbox, this is a **different, older**
      mechanism: `find_similar`/`LENS_REGISTRY` (`GET /api/whc-similar-env-lens`) — composite
      distance (Euclidean for precip, Mahalanobis for temp) on z-scored **derived/compressed**
      variables (harmonic components a1/b1/a2/b2 + log-total for precip; seasonal amplitude +
      concentration for temp), ranked, top-5. Corpus fixed to the 254 L08-assigned WH cities.
      CLAUDE.md flags `/api/whc-similar-env-lens` as deprecated-pending-deletion, but it's
      confirmed still the live wired path as of this scoping (`workbench.html`'s own comment:
      "Climate lenses via LENS_REGISTRY (L08, topN=5)") — the conjunction rewrite implied by
      CITYKIN's original plan never happened for cities. Worth a decision, not just a doc note:
      retire the deprecation label (nothing is replacing it) or actually do the rewrite.

### Terrain regime

- [ ] `[prose]` A third, distinct mechanism (`GET /api/whc-similar-terrain`,
      `scripts/cdop/citykin/terrain_lens.py` + `terrain_grid.py`). Query-relative tolerance bands
      (elev/relief/landform-position — "the three dials") act as an eligibility gate, then
      results are **ranked by a weighted distance score within the eligible set**, top-8 default
      — a gate+rank hybrid, not a pure membership set. Data source also differs in kind from
      Sandbox's terrain lens: a **live external elevation-grid fetch** (OpenTopoData, 5×5 points
      over ±10km around the literal coordinate) rather than precomputed BasinATLAS aggregates.

### Semantic similarity ("Similar (semantic)" dropdown)

- [ ] `[prose]` Wikipedia-discourse text similarity by band (Composite/Environment/History/
      Culture/Modern) — `GET /api/whc-similar-text`. No numeric-environmental content at all; a
      different paradigm (text/NLP) from every lens above. No Sandbox equivalent.

## Out of scope

- [ ] `[prose]` Workbench Societies tab's environment↔culture correspondence testing (PERMANOVA,
      family-restricted permutation, necessary-not-sufficient floor) — a different question from
      similarity retrieval. Belongs on its own page or folded into Workbench's overview; not
      decided yet.
