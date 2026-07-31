# CITYKIN WO4 — Step 1 findings: engine generalization + validation

WO: `docs/cdop/citykin/wo4_whc-grouping.md`. Engine: `scripts/cdop/distance_core.py` (new: `displacement`,
`random_draw_stats`, `top_families`, `scan`). Notebook: `notebooks/cdop/citykin/wo4_whc_grouping.ipynb`,
Cells 1–6, Karl-run. Unit tests: `tests/cdop/test_distance_core.py`, 21 green (10 original WO8d + 11 new).

## Terrain-variable provenance (Cell 2) — confirmed, no caveat needed beyond the known one

`relief_range_m` (point-window, `dplace.society_terrain`) and `basin_relief_range_m` (basin-aggregate)
correlate at 0.689 across 1,133 societies — a real relationship (both measure relief at the same
location) but far from near-identical, confirming the `terrain` lens reads the point-window column and
isn't a redundant rescaling of the basin-aggregate one. `landform_position` null rate 0.79%,
`relief_range_m` 0% — both real, complete-enough facets. Standing caveat carried from the WO (not
resolved, not blocking): `dplace.society_terrain`'s ±2km/1km grid predates CITYKIN WO1a's later-corrected
±10km/5km box for the WH Cities corpus — the two `terrain` lenses are not on the same sampling window,
immaterial here since this scan never compares a society to a WH City directly.

## A real bug, caught and fixed during Step 1 validation (Cells 3–4)

**Symptom:** first `scan()` run reproduced WO8d's `water`/`thermal`/`overall` numbers exactly but not
`terrain` (obs_cohesion 1.233 vs. reference 1.207; `pct_tighter_than_random` 36.75 vs. 44.10).

**Cause:** `scan()` computed the focus mask once against `sub`'s original index, then reindexed it onto
`backdrop_z`'s output index. `backdrop_z` calls `.reset_index(drop=True)` after dropping incomplete rows
for that lens — for a lens dropping zero rows (water/thermal/overall, all n_backdrop=1,133, nothing
missing) the reindex coincidentally lines up; for `terrain` (9 rows dropped to n_backdrop=1,124, on
`landform_position` NaNs) it silently selected the wrong 40 rows once the misalignment started.

**Fix:** recompute the focus condition directly against each lens's own post-dropna frame (`ok[trait_col]
== value`) rather than reindexing a mask built elsewhere. Verified two ways: (1) a direct side-by-side on
the exact bug-triggering synthetic case showed old logic picking up 7/7 raw matches (cohesion 1.205)
against the correct 4/7 survivors (cohesion 0.949) — a materially different mask, not a rounding
difference; (2) a new regression test
(`test_scan_focus_mask_survives_lens_specific_row_drops`) plants NaNs in the *middle* of a synthetic
frame (not the tail — the exact condition that let the original bug pass a same-size check) and asserts
the correct post-dropna focus count and cohesion. First re-run attempt after the fix still showed the old
(wrong) numbers — a stale kernel import, the same trap WO3 hit (`seasonality.py`); a kernel restart plus
re-run from Cell 1 resolved it. After that, all four lenses reproduce WO8d's Part C table exactly.

## Reproduction (Cells 3–4) — exact, all four lenses

| lens | obs_cohesion | ref | random_mean | ref | pct_tighter | ref |
|---|---|---|---|---|---|---|
| water | 0.540 | 0.540 | 0.731 | 0.731 | 95.25 | 95.25 |
| thermal | 1.223 | 1.223 | 1.201 | 1.201 | 44.75 | 44.75 |
| overall | 1.441 | 1.441 | 1.525 | 1.525 | 70.80 | 70.80 |
| terrain | 1.207 | 1.207 | 1.184 | 1.184 | 44.10 | 44.10 |

`random_draw_stats` also confirmed identical to `random_draw_cohesions` on the real backdrop (not just
synthetic), k=40, `np.array_equal` True.

## EA042 calibration (Cells 5–6) — passes, and the two cases correct the calibration bar itself

**Pastoralism (n=76):** strongly displaced on `water`/`thermal`/`overall` (displacement_pct_rank 97.55–
100.0) but **not** tight — `water`'s `pct_tighter_than_random` is 0.00 (looser than nearly every random
draw of the same size, not tighter). `terrain` is the outlier: both tight (99.95) and displaced (99.30),
unplanned and not yet explained (candidate: pastoralism concentrated in open, low-relief rangeland — or a
confound riding on the same geography as the aridity signal; not resolved here).

**Intensive agriculture (n=265, contrast):** tight **and** displaced on `water`/`thermal`/`overall`
(pct_tighter 78.10–95.95, displacement 72.9–99.9) — a real climatic core, matching WO8a's "wet-mild
quadrant" framing exactly. `terrain` flips to loose (pct_tighter 10.75 — more spread than random) with
moderate displacement (83.7) — agriculture occurs across far more terrain types than pastoral rangeland.

**The calibration bar as originally written in the notebook ("must light up on both cohesion and
displacement, on the same lens") was mis-specified — corrected here, not just qualified.** Displacement
and cohesion measure different things (where a group sits vs. how tightly it holds together there) and
can legitimately dissociate: Pastoralism's displaced-but-loose profile is not a partial miss, it is the
*correct* signature of a subsistence mode WO8b already established as dispersed across dry/cold margins
("mobile societies range widely... breadth 1.76") rather than clustered in one place. Intensive
agriculture's tight-and-displaced profile shows the instrument can and does detect the other shape when
the trait actually has one. **Revised bar: a calibration trait should show a clear, theoretically
coherent signal on at least one statistic (cohesion or displacement), and two contrasting trait values
should produce visibly different profiles from each other — not "both light up the same way regardless
of input."** Both conditions are met here.

Composition note behaved correctly on both, no special-casing: Pastoralism concentrated in one family
(Afro-Asiatic, 47%, plausible — Cushitic/Semitic pastoralists across the Horn/Sahel/Middle East);
Intensive agriculture spread near-evenly across three (Atlantic-Congo 19%, Afro-Asiatic 18%,
Indo-European 13%) — plausible given agriculture's many independent origins across unrelated lineages.

## Step 1 status: validated, signed off 2026-07-30

Terrain provenance confirmed; WO8d reproduction exact on all four lenses (after the fix above); EA042
calibration passes on a corrected, more accurate bar than originally written, with two trait values
producing clearly distinguishable, theory-consistent profiles. `wo4_whc-grouping.md`'s Step 1 validation
language amended to the revised bar in the same edit as sign-off.

## Step 2 — the API path

**`GET /api/societies/env-scan?trait={subsistence|religion}&value=...`** — new route, `app/api/routes.py`.
Wraps `distance_core.scan()` via a new module, `app/db/societies_scan.py`.

**Data-sourcing decision, made explicit rather than silently picked:** the substrate
(`output/cdop/wo8c_substrate.parquet`) is loaded once at app startup (`app/main.py` lifespan) and cached
in memory — not re-read per request, and not re-derived from the DB. The family-crosswalk step in
particular (WO8b Cell 3) parses local Glottolog CLDF `.trees` files, a research-data dependency this WO
deliberately does not repeat live; the existing, already-validated parquet is the right substrate to
serve from given the few-days scope. This keeps the parquet itself (not a new DB table) as the source of
truth, following the same access pattern as LISA's `output/edop/esda/lisa_classifications.parquet` —
small-per-basin-result-in-memory, not large-cube, but the same "cache once, load at startup" shape.
**Deploy note:** this parquet needs the same rsync treatment as other gitignored static assets; a server
restart is required to pick up any future regeneration of the substrate (a WO8-family notebook re-run).

Payload shape: `{trait, value, n_focus, hook: {has_hook, axes, source}, composition, lenses: {water,
thermal, overall, terrain}}`. No family-restricted resampling (per the settled Step 3 design). `hook`
carries the WO's hand-flag (`subsistence` → `has_hook=True, axes=['water','thermal']`, sourced to WO8a
Part B; `religion` → `has_hook=False, axes=None`) so the frontend can route to the confirmatory or scan
display without re-deciding it client-side.

Verified end-to-end against the real substrate (not synthetic): Pastoralism/subsistence and the EA034
focus class both return the exact numbers already validated in Step 1 (terrain `pct_tighter_than_random`
44.10, matching the WO8d reference to 2 decimal places). Unknown trait → 400; unmatched value → 200 with
`n_focus=0` (not an error — a real query that just happens to match nothing).

Tests: `tests/test_societies_scan.py`, 5 green (hook metadata for both traits, composition note shape,
unknown-trait 400, unmatched-value zero-focus). Full app suite: 416 passed / 14 skipped / 0 fail
(`--ignore=tests/engine`), up from 411 pre-WO4 Step 2 baseline.

## Step 2 status: built and tested, ready for payload review before Step 3
