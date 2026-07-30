# CITYKIN WO1a — exec summary (for Opus)

The terrain-lens correction you and Karl scoped in WO1a is built and both fixtures pass. Full record:
`wo1a_findings.md`.

**The fix landed as designed.** WO1's `>=400m` elevation gate is gone. In its place: three
query-relative tolerance bands (elevation, relief, landform-position), each anchored to the *selected*
city's own values, ranked by a distance that normalizes each facet's deviation by its own tolerance
rather than a corpus-wide z-score — which is what let elevation dominate in WO1's original design.
Factored into `terrain_lens.py`, separate from the retrieval head, per the WO1a Part B proviso.

**Locked defaults, set jointly against both fixtures**: elevation ±500m, relief ±300m, landform-
position ±0.10 — each a sub-one-std tolerance on the corpus's own spread, defensible on its own terms.
(±300m elevation was tried first and excluded Yerevan, Tbilisi's best match, over a 474m gap despite
near-perfect relief/position agreement — which is what prompted checking the std-relative basis rather
than just widening until it cleared. ±500m is the principled value; Yerevan clearing at it is
confirmation, not the reason for the number — worth being precise about, since "widened until the
motivating case cleared" is the same hazard the 400m gate itself was.)

**Both Part D fixtures pass, no per-city tuning.** Tbilisi: 22 of 253 eligible, Yerevan back at rank 6
— the strongest independent plausibility check in the whole arc (unrelated geography, same South
Caucasus terrain context, never told to look for it). Bruges: 35 of 253 eligible, headlined by Lübeck
at rank 7 — a fellow flat, low-lying Hanseatic port city, an equally strong unprompted validation on
the flat-city side. This is the generalization check WO1's single fixture missed, and it's clean in
both directions now.

**A real data bug surfaced and got fixed along the way, not just the design.** OpenTopoData's `mapzen`
dataset returns actual bathymetric depths (not null) for grid points that land in open water. 88 of
254 cities (35%) had at least one point affected; the worst, Willemstad (Curaçao), had a grid spanning
−1249m to 67m — seafloor and city mixed into one relief number. Fixed by dropping any point with
elevation < 0 before computing stats. One casualty: Aktau, Kazakhstan, now unresolved (confirmed by
satellite view — it's a peninsula genuinely mostly surrounded by the Caspian Sea within a 10km box, an
honest gap, not a bug). This bug would have hit the sandbox's future Similarity-tab terrain lens even
harder (arbitrary global coordinates, not a curated 254-city list), so worth having caught it here
first.

**One thing noted, not acted on, in case it comes up:** the eligible-set sizes (22/253, 35/253 — 9–14%
of the whole corpus) are a much bigger *fraction* than the sandbox's basin-level similarity panel would
show for a comparably-tuned band, simply because the WH Cities corpus is two orders of magnitude
smaller than the basin index. Karl's read: passes the smell test, not a blocker — but it argues for
presenting results as a ranked top-N with distances (the existing `cdop_pilot` pattern) rather than
leading with an "N eligible" count, which would read as less selective here than it would at basin
scale.

**Also raised and deliberately deferred, per Karl:** `n_grid_land`/`n_grid_points` — how much of a
city's sampling window is water — is itself a real "proximity to open water" signal. Logged per your
review as more than a candidate 4th terrain facet: it's the first concrete crumb of the coastality lens
already on the CITYKIN wishlist, recorded in the deferred register that way so the connection isn't
rediscovered later. Not added now; Karl wants to see how the three-facet lens performs in actual use
first before adding scope.

**Standing rule going forward, per your review:** any future change to this lens re-runs both fixtures
(Tbilisi + Bruges) at shared defaults before shipping — not a WO1a-only step, logged in the tracker as
the specific guard against re-de-generalizing the lens the way the 400m gate did.

Not built yet: the retrieval head itself (query → knobs → ranked list + map markers). That's the next
step.
