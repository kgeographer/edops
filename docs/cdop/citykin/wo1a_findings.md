# CITYKIN WO1a — findings

Technical record for WO1a's terrain-lens correction. Tracker: `docs/cdop/citykin/CITYKIN_tracker.md`
(summary + pointer only). WO: `docs/cdop/citykin/wo1a_terrain-lens.md`. Prior: `wo1_findings.md`
(the superseded gate design). Notebook: `notebooks/cdop/citykin/wo1_validation.ipynb` (Cells 11–14,
appended after the WO1 record; all run). Exec summary for Opus: `wo1a_exec_summary.md`.

---

## Why WO1's design needed correcting

WO1's terrain lens passed its own Tbilisi fixture (`grid_elev_mean >= 400m` eligibility gate, ranking
on relief + landform-position within the gated pool) but Karl + Opus caught, in review, that the gate
was a Tbilisi-specific artifact: it hard-codes "high" as a global constant. The WH Cities UI offers a
dropdown of *all* 254 cities — querying a flat city (Bruges, ~5m) against a `>=400m` gate excludes the
query city from its own result set, and the shape terms are meaningless for a delta city regardless.
Passing-for-Tbilisi and generalizing-to-all-254-cities turned out to be different things; WO1's single
fixture was exactly how that slipped through.

## The fix — query-relative tolerance knobs

Retired the gate. Rebuilt as three tolerance bands, each anchored to the **selected city's own** facet
value — the pattern already validated for the sandbox's climate-regime lenses (query-relative bands
with user knobs, e.g. temp level ±°C, temp range ±°C; see the WO6c panel screenshot Karl supplied for
the reference UI shape). Bruges asks "what's like Bruges," Tbilisi asks "what's like Tbilisi" — same
instrument, no baked-in constant.

**Factored core**: `scripts/cdop/citykin/terrain_lens.py` (`rank_by_terrain`, `in_tolerance`) —
separate from any presentation head, so a later WO can wire the same core to a paint-a-set head on the
sandbox Similarity tab without reimplementing the distance (same discipline as WO8d's
`distance_core.py`; CITYKIN's ranked-retrieval head is the first consumer here).

**Ranking distance**: each facet's deviation from the query is normalized by *its own* tolerance
(`d_facet / tol_facet`), not a corpus-wide z-score — the exact thing that made WO1's plain 3-facet
Euclidean distance fail (elevation dominated because its z-scored range dwarfed the others). Combined
in quadrature: `dist = sqrt(elev_weight*(d_elev/tol_elev)^2 + (d_relief/tol_relief)^2 +
(d_pos/tol_pos)^2)`. `elev_weight` is an internal parameter (not a user knob), currently `1.0` —
tested against both fixtures and found to behave correctly without adjustment: Yerevan ranks 6th for
Tbilisi despite a 474m elevation gap, because its relief and position match almost exactly, which is
the intended "informs without dominating" behavior.

## A data-quality fix discovered along the way — bathymetric contamination

While investigating why Aktau's terrain read strangely, found that OpenTopoData's `mapzen` dataset
returns real bathymetric depths (not null) for grid points that fall in open water. Any coastal city
whose ±10km point-window dips into the sea gets seafloor depth mixed into its relief statistic —
confirmed on Willemstad, Curaçao: raw grid spanned **−1249m to 67m** (land points cluster tightly at
7–67m; everything below 0 is ocean), giving a nonsense relief_range of ~1300m. **88 of 254 cities**
(35%) had at least one grid point affected.

**Fix**: drop any individual grid point with elevation < 0 before computing min/max/mean/relief/
landform_position (`scripts/cdop/citykin/terrain_grid.py`, the fetch-and-compute logic factored out of
`persist_whcities_terrain.py` since it now has three real consumers — the persist script, this
notebook's fixture queries, and eventually a live query-by-coordinate API path). Known tradeoff: a
handful of real places sit shallowly below sea level on land (Amsterdam-area polders, Baku) and lose a
couple of valid points too; accepted, since the contamination this fixes is severe (up to −1249m) and
the corpus's genuine below-sea-level land cases are shallow enough not to starve the sample.

**Effect**: corpus-wide minimum `grid_elev_mean` went from −318m to +1.6m. 253/254 cities now resolve
— **Aktau, Kazakhstan is the one casualty** (2 of 25 points left after filtering; confirmed by
satellite view it sits on a narrow peninsula genuinely mostly surrounded by the Caspian Sea within
10km — an honest "not enough land in the window" case, not a bug). Coverage distribution across the
rest of the corpus: 166/254 (65%) had zero contamination at all; only 6 cities landed in a "thin
sample" band (<10 of 25 land points: Patmos 4, Beemster 5, Dakar 5, Rhodes 6, Macau 8) — a small,
name-able population, not systemic. `n_grid_land`/`n_grid_points` is now stored per city and doubles
as a free "how much open water is in this window" signal for any future point, not just this corpus.
Karl's mid-session observation: querying a coastal city under a 4th tolerance knob on this ratio would
naturally retrieve other coastal cities. **Opus's WO1a review adds the sharper framing: this isn't only
a candidate 4th terrain facet, it's the first concrete crumb of the coastality lens already named on
the CITYKIN wishlist** (`CITYKIN_tracker.md` § Deferred; register entry: `docs/design/
deferred_items_register.md` § CDOP — CITYKIN). Not built now: "let it ride and see how it works out in
queries" rather than adding scope, and evaluate it as a coastality-lens seed when that lens is
eventually scoped, not only as terrain-facet #4.

Side effect on the correlation check: elevation-vs-relief rose from 0.43 (pre-fix) to **0.62**
(post-fix) — filtering out water tightened the relationship, since real land relief and elevation are
more genuinely coupled once bathymetric noise is removed. Still under the 0.70 Mahalanobis/drop bar,
noted for future attention if it drifts further as the lens evolves.

## Locked defaults (Part D, set jointly against both fixtures)

| Knob | Default | Basis |
|---|---|---|
| Elevation tolerance | ±500m | A sub-one-std tolerance (corpus std ≈698m) — defensible on its own terms, not fit to either fixture. ±300m was tried first and excluded Yerevan (474m elevation gap from Tbilisi, otherwise a near-perfect relief/position match); that prompted checking the std-relative basis rather than accepting a number tuned to admit one city. ±500m is the principled value; Yerevan clearing at it is a **confirmation**, not the reason for the choice (Opus's WO1a review, 2026-07-28 — the same fitting-to-the-motivating-case hazard the 400m gate itself was). |
| Relief tolerance | ±300m | Sub-one-std (corpus std ≈404m). ±200m worked but ±300m recovers a few more plausible matches (Úbeda, Baeza) without degrading Bruges's list. |
| Landform-position tolerance | ±0.10 | Corpus std ≈0.115. Left unchanged through iteration — never the binding constraint in testing. |
| `elev_weight` (internal) | 1.0 | No adjustment needed — see Ranking distance above. |

## Part D fixture results — both pass, no per-city tuning

**Tbilisi** (fresh point-window fetch, 673m/749m/0.41; 25/25 land points, no contamination): 22 of 253
eligible. Top of the list: Palazzolo Acreide (Italy), Padula (Italy, independently confirmed by
satellite/topo map earlier this session), Bardejov (Slovakia), Úbeda/Baeza (Spain), **Yerevan
(Armenia, rank 6)** — the strongest independent plausibility check in the whole WO1/WO1a arc, recovered
after the elevation-tolerance widening — Yangsan, Derbent, Ouro Preto, Granada, Oviedo, Segovia.
Terrain-coherent.

**Bruges** (corpus row: 5.8m/22m/0.22): 35 of 253 eligible. Top of the list: Island of Mozambique,
Tlacotalpan (Mexico), Bolgar (Russia), Huế (Vietnam), Santa Cruz de Mompox (Colombia), Singapore,
**Lübeck (Germany, rank 7)** — a fellow flat, low-lying Hanseatic League port city, an excellent
independent plausibility check in the same spirit as Tbilisi/Yerevan — Tunis, Galle, Pyay, Philadelphia,
Baku-Old City. Terrain-coherent, no per-city tuning from Tbilisi's settings.

**Verdict: WO1a's accept gate passes.** Both fixtures return terrain-coherent neighbors at the same
default knob settings; the 400m gate is gone; elevation informs the ranking without dominating it;
the tolerance core is factored separately from the retrieval head (not yet wired — see Forward).

## Noted, not actioned — the small-corpus effect

22/253 (8.7%) and 35/253 (13.8%) eligible are both a nontrivial share of the whole corpus — a
structurally different situation from the sandbox's basin-level similarity panel, whose reference set
(~16,397 L06 basins) is two orders of magnitude larger, so the same style of tolerance band there
admits a tiny fraction (the WO6c panel's own example: 38/16,397 = 0.23%) and reads as more selective.
Karl: "I think this passes an initial smell test, we can proceed" — not a blocker, but a reason to
prefer a top-N-with-distance presentation (the existing `cdop_pilot` "5 most similar cities in this
collection" pattern) over an admitted-count headline when wiring the retrieval head, since a raw
"N eligible" stat will read as less selective here than the equivalent basin-level number would.

## Standing rule going forward — two-fixture validation for the terrain lens

Per Opus's WO1a review: single-fixture validation is exactly how the 400m gate slipped through WO1.
**Any future change to the terrain lens re-runs both fixtures — Tbilisi (contained high valley) and a
flat city (Bruges) — at shared defaults, no per-city tuning** — not a WO1a-only artifact, a standing
check on this lens from here forward, the same way the second-seed stability check became standing
after WO8b. Logged in `CITYKIN_tracker.md` § Locked decisions.

## Open / carried forward, not pursued now

- **Water-fraction / coastality-lens seed** — `n_grid_land`/`n_grid_points` is a real, already-computed
  "proximity to open water" signal — the first concrete crumb of the coastality lens on the CITYKIN
  wishlist, not only a candidate 4th terrain facet (Opus's WO1a review). Not added as a formal knob
  this WO; register entry: `docs/design/deferred_items_register.md` § CDOP — CITYKIN.
- **Soft elevation down-weight vs. a hard band edge** — softened somewhat by moving from WO1's hard
  gate to a tolerance band, but the band still has a hard edge; not revisited this WO.
- Tier-2 (`ST_Touches` enclosure/containment) and Tier-3 (local DEM) remain named, not built (WO1
  Part C). Kathmandu's WO1 mid-pack rank is still the standing Tier-2 trigger candidate.

## Forward — not this WO

- Wire the retrieval head (WO1a Part C): query city → tolerance knobs (defaults above, user-adjustable)
  → top-N markers + ranked list with distances.
- A later WO wires the same `terrain_lens.py` core to a paint-a-set head on the sandbox Similarity tab.
