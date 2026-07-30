# CITYKIN WO1 — exec summary (for Opus)

Terrain lens Tier 1 is built and the Part D acceptance fixture (query Tbilisi, expect back
"high valley floor" cities) **passes** — but the path there is worth reading, because it changed the
lens's design partway through, not just its parameters. Full technical record: `wo1_findings.md`.

**The naive version failed badly, twice.** First pass used a point-window grid (±2km box around each
city, following WO8c's society-terrain precedent) and a plain 3-facet z-scored Euclidean distance
(elevation, local relief, landform position). The WO's own named "high valley floor" candidates
(Kathmandu, Mexico City, Sanaa, Quito, Cusco) ranked 174th–252nd of 254 against Tbilisi — nearly last.
Diagnosis: 2km is too small a window to see the highlands that actually enclose those cities (they
read as artificially flat). Widening the box to 10km (empirically chosen — a radius/density probe
confirmed relief keeps growing without bound as the box widens, so *some* radius has to be a judgment
call, and 10km was where a sparser and denser grid stopped disagreeing) helped only a little — the
real blocker turned out to be that **raw elevation, z-scored and compared like any other facet, was
measuring how far apart two cities' absolute heights are** — and Tbilisi (673m) sits 500–3000m below
every named candidate. No amount of relief/position agreement could overcome that gap in a plain
Euclidean sum.

**Karl's fix: elevation isn't a magnitude to compare, it's a threshold to clear.** A 500m valley floor
and a 3000m valley floor can both be genuinely "a settlement contained by elevation" — what matters is
*whether* a place is high enough to have that character, not *how* high. Rebuilt as: elevation gates
eligibility (`grid_elev_mean >= 400m`, chosen from a real empty bin in the corpus's own elevation
histogram — the same kind of evidence-based threshold as the WO2 aridity gate, not a fitted number);
ranking runs only on the two shape facets (local relief, landform position) among cities that clear
the gate.

**That fixed it, and better than expected.** Yerevan comes back #1 (dist 0.096 — essentially the
tightest match in the whole 83-city eligible pool), unprompted, and it's a genuinely strong
independent plausibility check — same South Caucasus terrain context as Tbilisi. Bhaktapur (#4) sits
literally in the Kathmandu Valley. Cusco moved from 252nd to 10th; Sanaa from 243rd to 14th. **Mexico
City (#77) and Quito (#83, dead last) are still excluded — and that turns out to be correct, not a
failure**: Mexico City's landform_position is far more extreme-flat than Tbilisi's (a former lakebed);
Quito's local relief is ~3× Tbilisi's (a shelf against an active volcano). Both are "high" but neither
shares Tbilisi's specific containment shape — which is exactly the WO's own stated exclusion
criterion ("exclude high-flat and high-peak cities that share only elevation"), just applied to two of
the WO's own five *positive* examples. Reading, confirmed by Karl: the named candidates were informed
guesses at what might show up, not verified exemplars, and the instrument doing its job (measuring
shape) rather than confirming the guesses is the more honest outcome.

**Not pursued this WO, worth a look:** a soft down-weight on elevation instead of the hard 400m gate
(Karl's own follow-on idea — might smooth the one edge case, cities just under the gate that could
otherwise compete on shape). Kathmandu's own rank (#46, mid-pack) may point at a genuine Tier-2
(enclosure/containment, `ST_Touches`-based, still unbuilt) gap rather than anything fixable within
Tier 1.

Locked parameters, ready for Part B's UI wiring: ±10km/5km-spacing 25-point grid
(`persist_whcities_terrain.py` → `gaz.wh_cities_terrain`); `grid_elev_mean >= 400` eligibility gate;
Euclidean on z-scored `(relief_range_m, landform_position)` fit on the eligible subset.
