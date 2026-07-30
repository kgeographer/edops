# CITYKIN WO3 — findings

Technical record for WO3: the coarse Terrain regime lens on the sandbox Similarity panel. Tracker:
`docs/cdop/citykin/CITYKIN_tracker.md` (summary + pointer only). WO: `docs/cdop/citykin/
wo3_coarse-terrain.md`. Prior: `wo2a_findings.md` (facets cleared: `ele_mt_sav` + `relief_range`,
`corr` = 0.541/0.566 — independent enough to ship both). Notebook: `notebooks/cdop/citykin/
wo2-3_terrain_basin.ipynb` (Cells 11–21, all run — same notebook as WO2a/WO2b, renamed once WO3
joined it). No exec summary for this one.

---

## Part A — the tolerance core

Extended `app/db/seasonality.py`'s existing non-compensatory conjunction machinery (the same module
backing Precipitation/Temperature/Climate regime) rather than reusing WO1a's point-window
`terrain_lens.py`, which is fed by a different data path (live grid fetches vs. basin-aggregate
columns already in the DB).

- `CONJ_CONDITIONS`/`CONJ_LENSES` gained `terrain_elev`/`terrain_relief` and `"terrain.regime"` — two
  query-relative abs-bands, no shape term.
- `load_similarity_index()` fetches `ele_mt_sav`/`ele_mt_smx`/`ele_mt_smn` straight from the scalars
  base table (`basin06`/`basin08`) — confirmed as the right path before writing it (plain base-table
  columns, not persist-view/monthly-array derived). `-9999` masked defensively; a `terrain_valid` mask
  excludes null-facet basins rather than coercing them.
- `find_conjunction()`'s single climate `valid` mask was generalized into a **per-lens-family**
  validity check — climate lenses gate on `conj["valid"]` exactly as before (confirmed by an explicit
  regression-pin test), terrain.regime gates on `conj["terrain_valid"]` alone.

Tests: registry-shape extended for the 4th lens; a structural + monotonicity contract test for
terrain.regime (no magic numbers); a regression pin confirming climate lenses are unaffected by the
family-validity generalization. Live-verified against the running server before any real defaults
existed (`/api/similarity/conjunction/lenses` listed Terrain regime generically; a live query against
Tbilisi's coordinates returned real basin-aggregate numbers under the WO1a-borrowed placeholder
defaults).

## Part B — deriving the tolerance-band defaults

**The std-based recipe (WO1a's own pattern) failed outright.** Round fractions of each facet's corpus
std (elevation ±400/600/800m, relief ±600/850/1150m) admitted **24.5–48.4% of the L06 corpus** on
average across a 16-basin sample stratified by elevation-quartile × relief-quartile (sampled from the
table, not coordinate-picked) — nowhere near the WO's own "a fraction of a percent reads as properly
selective" expectation. Cause: elevation's std (775m) sits *above* its own IQR (617m) — the long right
tail (max 5556m) inflates std well past the density where most basins actually live, so a std-fraction
band is far wider in practice than it looks on paper.

**Fix: dropped the std anchor, swept absolute widths directly.** An 8×8 grid of small elevation
(25–400m) × relief (50–600m) widths, measured against the real `find_conjunction` code on the same
sample, found selectivity crossing into the target range at far smaller numbers than any
std-fraction would suggest.

**Locked defaults** (now in `seasonality.py`, replacing the WO1a placeholders):

| Level | Elevation ± | Relief ± | % of L06 corpus matched (median across the 16-basin sample) |
|---|---|---|---|
| tight | 25m | 50m | 0.146% |
| **default** | **50m** | **100m** | **0.445%** |
| broad | 100m | 200m | 1.656% |

Mean %-matched is meaningfully higher than median at every level (e.g. default: mean 1.276% vs.
median 0.445%) — not a red flag. The gap is driven entirely by queries sitting in the low-elevation/
low-relief corner of the joint distribution, where there is genuinely far more "similar company"
worldwide (crowded lowlands) than in the sparse high-elevation/high-relief corner (mountain queries
stay selective, one sample basin even returned 0 matches at `tight` — honest scarcity, the same
convention already established for the climate lenses). Accepted as-is: squeezing the numbers smaller
to control the lowland worst-case would cost real selectivity at the sparse, arguably more
interesting, mountain end.

**WO2b's joint-vs-independence proviso, measured directly**: at the (superseded) std-based default,
actual joint admission ran almost exactly at what independence would predict (1.02× on average,
masking real per-query variation from 0.77× to 1.25×) — not the uniform "correlation makes it looser"
effect anticipated, evidence that the effect is band-width- and location-dependent rather than a fixed
multiplier. Not re-measured at the final small-width defaults; noted as a secondary, non-blocking
observation.

## Part C — the two-fixture generalization check

Rugged fixture: Tbilisi's own L06 basin (hybas_id `2060616700`, elev 1638m, relief 3583m) — the WO's
own sanctioned exception to quantile-selection, already the project's canonical terrain fixture. Flat
fixture: hybas_id `6060269510`, selected as the largest-area basin within the flattest relief quartile
— table-quantile selection, not coordinate-picked (a different basin from WO2a's coordinate-picked
Kansas fixture, `7060622710`).

At the locked defaults, no per-fixture tuning:

- **Rugged** (Tbilisi): set_size = 6. Member elevation range 1588–1685m, relief 3484–3609m. Genuinely
  clustered at high elevation/relief.
- **Flat**: set_size = 880. Member elevation range 73–173m, relief 99–299m. Genuinely low and gentle.
- **Discrimination**: zero overlap between the two sets. Elevation ranges cleanly separated by
  **>1,400m** (1588–1685m vs. 73–173m) — no leak from the flat basin's larger area into the rugged
  query's band, and vice versa.

One real process catch mid-Part-C: the notebook's first pass at these numbers ran against a **stale,
already-imported copy of `seasonality.py`** still holding the old 500m/300m placeholder defaults
(Python caches imported modules; editing the source file on disk doesn't reach a kernel that already
loaded it). Caught because the member elevation ranges matched the old placeholder's arithmetic
exactly (e.g. 1638±500 = 1138–2138m, observed 1158–2126m) rather than the newly-locked ±50m. Fixed by
restarting the kernel and rerunning from Cell 1; flagged here so a future WO doesn't rediscover the
same trap.

**Accept gate met**: both fixtures, same shared defaults, terrain-coherent and cleanly separated sets,
no per-fixture tuning.

## Part D — wiring, and the browser review

`app/api/routes.py`: `/api/similarity/conjunction` gained `elev_band`/`relief_band` optional params;
`find_conjunction`'s members gained `elev_m`/`relief_range_m` (previously climate-shaped only —
needed for a meaningful terrain hover popup). `app/templates/sandbox_v3.html`: "Terrain regime" added
to the Lens dropdown; two new tight/default/broad knobs at the locked values, matching the panel's
existing convention exactly; hover popup shows elevation/relief instead of precipitation for this
lens; the existing "this describes the basin, not the place" footnote gained one extra sentence for
this lens only (WO3's own instruction: extend the existing register, don't invent a new one); dedupe
key and fetch params extended so the new knobs trigger a refetch.

**Karl's browser review, two smell tests at `broad`:**

- **San Francisco**: 250 basins matched, spanning 20,012 km — a comparatively small, distinctive set.
- **Kaifeng**: 2,578 basins matched, reaching 19,915 km — a much larger set. First read (mine) of the
  painted regions as mountain ranges (Alps/Himalaya/Rockies) was **wrong** — corrected on inspection of
  the actual (not thumbnail) image to Eastern European plains, the Nile Delta, Mesopotamian lowlands,
  West African coastal deltas, and Orinoco/Amazon delta lowlands. Kaifeng sits on the Yellow River
  floodplain; matching other large lowland/delta terrain worldwide is terrain-coherent, and the larger
  set size (vs. SF) tracks — "large flat floodplain" is a more common global terrain type than SF's
  profile, so it should read as less distinctive, which is what showed up.
- **San Francisco's own basin, examined**: Karl flagged the L06 basin extent as "odd" — it visibly
  spans well down the peninsula's coastal-range spine, not just the city. Confirmed via the live
  query values (`elev_m: 321.0, relief_range_m: 1602.0` — downtown SF itself tops out ~280m) and the
  basin's actual geometry (a long, elongated catchment running the length of the peninsula ridge, not
  a city-sized footprint). **Same mechanism as WO2a's Innsbruck case** (HydroBASINS delineates by
  drainage topology, not local landscape) — not a bug, and exactly the caveat already sitting in the
  UI's own footnote, now demonstrated live rather than only in a synthetic fixture.

Both smell tests accepted. **Part D done, Karl's call**: "there will be lots of time for review, and
it's always good to give reviewers, first users something to critique."

## Accept gate — met

Both fixtures paint terrain-coherent, visibly different sets at shared defaults with no per-fixture
tuning; defaults were derived from the corpus distribution and an empirical selectivity sweep, not
map inspection (the map came after, for plausibility, per the WO's own order); the lens is selectable
in the panel with two auto-applying knobs; the guide language states plainly that this is basin-level
elevation level and range, not ruggedness and not within-basin position.

## Open / carried forward — unchanged from WO2a, not touched by WO3

- **L08** — same facets, same core, finer basins; `relief_range`'s area effect is weaker there
  (WO2a), so L08's knob levels need their own derivation, not inherited from L06. Named in the WO's
  own Forward section; deliberately sequenced after L06, not skipped.
- **The residual facet** (`relief_range` regressed on `slp_dg_sav`) — still named, not built. Tension
  to weigh if taken up: its zero point is corpus-relative, unlike every other facet in this lens
  family (query-relative, physical units).
- **Fine-grained ruggedness / roughness / TRI**, neighbour-relative (containment) facets — post-Braga,
  needs cell-level data the project does not yet hold. Nothing in WO3 anticipates a substrate it
  doesn't have.
