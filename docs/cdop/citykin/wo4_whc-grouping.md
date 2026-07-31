# CITYKIN WO4 — replacing the Societies-tab PCA cluster option

**Status:** accepted 2026-07-30 (Karl + Opus settled the Step 3 family-restricted question, see the
superseded/revised provisos below); building.
**Prior:** `note_to_opus_societies-dataviz.md` (the hook/no-hook framing this WO builds on),
`note_societies-tab-vs-wo8.md` (why the legacy PCA option exists and is hidden), `wo8a_findings.md`
Part B (the Climate envelope — the validated aridity × temperature separator for subsistence),
`wo8d_findings.md` (the cohesion mechanic, hand-scoped to 40 EA034 societies).
Register entry: `docs/design/deferred_items_register.md` § CDOP — Societies tab (pilot legacy).
**Type:** engine generalization + two display modes. Notebook validation first, then wiring.
**Scope:** CITYKIN (Karl, 2026-07-30). This is the phase's last feature item before documentation.

Goal-setting with provisos. CC discovers implementation particulars; Karl reviews every write and runs
every cell.

---

## What this replaces

`cdop_pilot.html`'s `#panel-soc` Societies tab currently carries a hidden legacy "Basin clusters" option
built on the suspect-provenance PCA clustering. This WO replaces it with a targeted dataviz — and the
replacement is **two displays, not one**, because the two wired traits are different kinds of question:

- **EA042 (subsistence) has a theoretical hook.** Environment sets outer bounds on subsistence strategy;
  WO8a validated aridity × temperature as the cleanest separator. Showing that scatter is a
  **confirmatory** illustration of an established relationship.
- **EA034 (high gods) has no hook.** WO8d could not test a predicted axis because there isn't one — it
  asked instead whether *any* environmental thread shows more than shared ancestry explains. That needs
  an **exploratory scan** across lenses, not a specific plot.

The design has to work for both kinds, because the tab will likely always show one of each. Different
traits get different endpoints and different payloads.

## Step 1 — the engine: parameterize, and add displacement

`scripts/cdop/distance_core.py` currently hardcodes WO8d's 40-society group. Generalize it to take
`(trait, value)` → filtered society set, and return per-lens statistics against the existing
`LENSES` dict (`water`, `thermal`, `overall`, `terrain`).

**Two statistics per lens, not one.** WO8d computes cohesion only — mean distance from each society to
*its own group's* centroid. That measures **spread**, and it is computed relative to the group centroid,
so the centroid's location cancels out of the arithmetic entirely. A group of societies all living in
unusually dry places, but with ordinary spread, returns an unremarkable cohesion number. That is a real
environmental association the current instrument cannot see, and it is probably the most common form
such an association takes.

Add **displacement**: the distance from the filtered group's centroid to the backdrop centroid, in the
same z-scored lens space. Where the group sits, as against how tightly it holds together there.

Provisos:

- **Same resampling loop.** For each draw already generated — random and family-restricted — compute the
  drawn group's centroid displacement alongside its cohesion, and percentile-rank both. The expensive
  part (generating the draws) is already happening; this is one more quantity per iteration, not a
  second pass.
- **Standardize once on the whole backdrop**, never refit per subgroup — the existing WO8d discipline,
  which is what makes numbers comparable across groups. Unchanged.
- **Return per-society distances too**, not just the aggregate. Cohesion is the mean of them; Step 4's
  map paints them. Computing the mean and discarding the parts would mean recomputing later, and would
  risk the chart and the map disagreeing.
- **Confirm what `relief_range_m` and `landform_position` actually are in the `terrain` lens** before
  trusting its output — for *both* variables, not just `relief_range_m`. If they are point-window values
  at society coordinates, fine. If `relief_range_m` is basin-derived (`ele_mt_smx − ele_mt_smn`), WO2a's
  area confound transfers directly — the lens would partly be measuring "these societies live in
  similarly-sized basins," which is not a terrain fact and needs a caveat. Separately: confirm
  `landform_position` was actually computed and stored for D-PLACE societies at all — WO8c's own writeup
  documents point-window local *relief* for the 1,133 EA societies but doesn't clearly establish that
  landform position (floor vs. ridge) was ever built for the society table, as opposed to only for the WH
  Cities corpus. If it's missing, the `terrain` lens's second facet is silently wrong or absent, not just
  differently-scoped. One check, early, because the answer changes what the scan's terrain row means, or
  whether it can ship at all this WO.

**Validation, in this order:**

1. **Reproduce WO8d's EA034 numbers** through the parameterized path. Cohesion should match the hand-run
   values. If it doesn't, the generalization changed something.
2. **Calibration run on EA042.** Filter to a subsistence value with a strong expected environmental
   association and confirm it lights up on `water` and `thermal`, as WO8a predicts — checking **both
   cohesion and displacement**, not cohesion alone (displacement is the new, unvalidated statistic; a
   calibration pass that only checks cohesion never actually validates it). **This is a build-time check,
   not a shipped path** — but it is the check that the instrument detects real signal at all.
   **SUPERSEDED, 2026-07-30 (Cells 5–6, `wo4_findings.md`) — the original bar below was mis-specified,
   not just informal:** ~~If EA042 does not light up on both statistics, stop and report — the scan is not
   measuring what it claims to.~~ Cohesion and displacement measure different things (how tightly a group
   holds together vs. where it sits) and can legitimately dissociate — Pastoralism calibrated as strongly
   displaced but *not* tight on `water` (matching WO8b's own established "mobile societies range widely
   across dry/cold margins" finding), while the Intensive-agriculture contrast case came back tight *and*
   displaced (a real climatic core, matching WO8a's "wet-mild quadrant"). **Revised bar: a calibration
   trait must show a clear, theoretically coherent signal on at least one statistic, and two contrasting
   trait values must produce visibly different profiles from each other — not both statistics lighting up
   identically regardless of input.** Both conditions were met; a scan with no known-positive, or one
   where every trait value produces the same generic profile, is what would actually indicate "no signal"
   or "no instrument."

Numbers to `wo4_findings.md`. Karl's sign-off before Step 2.

## Step 2 — the API path

One route: `(trait, value)` → per-lens cohesion and displacement with percentiles against the random-draw
baseline, plus the top-3 language-family composition note and per-society lens distances for the map.
Family-restricted resampling is not part of this payload (see Step 3 revision above) — the endpoint has
nothing to compute or serve for it.

Provisos:

- **Report group size prominently in the payload.** EA034's filter was 40 societies; some trait-value
  filters will return far fewer, and small groups are *more* likely to produce extreme-looking
  percentiles, not less. Karl decides at review what the display does below some size — likely show the
  numbers without the baseline framing rather than suppress the row.
- **NULLs are excluded from the filtered set, never imputed.** Standing rule.

## Step 3 — the two displays

**Confirmatory (EA042).** The Climate envelope scatter: filtered societies plotted in aridity ×
temperature, against the backdrop. The axes come from the trait's declared hook, not from a global
constant.

**Scan (EA034) — SUPERSEDED, 2026-07-30, see `wo4_findings.md` § "Step 3, redesigned: meter bars +
donut" for the full reasoning and the actual shipped design.** ~~One row per lens — `water`,
`thermal`, `overall`, `terrain` — each showing the group's displacement and cohesion against their
baseline distributions. A small-multiple dot or bar layout; the visualization is straightforward once
the numbers exist.~~ Karl's browser review found this unnarratable (two of the four lenses bundle two
physical variables into one number, so no plain-language gloss could give a single direction) and its
"tighter than X% of random draws" language impossible on a GUI page. Replaced by five meter bars, one
per raw physical variable (aridity, temperature, seasonality, ruggedness, landform), each a
deterministic percentile-of-global-range with plain-word poles and a qualifier (typical/somewhat/very)
— no resampling, no cohesion. The composition note (both displays) is now a donut with hover-to-map
linking, not a bullet list.

Provisos:

- **The hand-flag records *what* the hook is, not that one exists.** `EA042 → water + thermal, per WO8a
  Part B`. That both routes to the confirmatory mode and names the axes it needs to plot. A boolean
  carries neither. Two traits are wired, so hand-flagging is cheap — do not build a general rule for a
  two-trait tab.
- **Never surface a winning lens alone.** All four rows always visible together, so "three of four are
  unremarkable" reads in the same glance as the fourth. Four lenses × every selectable trait value
  means something will look tight somewhere by chance. This is a display rule, not a significance floor
  — the engine still doesn't interpret; the surface just refuses to show a winner without its context.
- **SUPERSEDED, 2026-07-30 — settled between Karl and Opus, see below.** ~~Family-restricted is the
  headline reading; random is context. WO8d's own finding is the argument: water looked tight against
  random and dissolved once ancestry was controlled. Shown side by side with equal weight, a reader takes
  the more impressive number. The Galton control should be visible in the layout, not explained in a
  caption.~~
- **Plain cohesion and displacement against random draws lead; a composition note sits beneath, no
  baseline.** Karl's correction: "environmental similarity *net family*" is an analytical move, not a
  description — it belongs to TRACE (its own sandbox output, later), not to this descriptive screen.
  Opus's concession sharpened it further, via the project's own standing principle (the 0.70 redundancy-
  bar critique — an inferential guard misapplied to a description job displaces the thing the surface
  exists to show; same error, same direction, here): **the composition note is better description than a
  family-restricted percentile, not just better-scoped.** "14 of 40 are Bantu" is a fact about the group,
  directly legible; a percentile against restricted permutation is a compressed, harder-to-read proxy for
  the same fact. WO8d's own write-up already did it this way — led with the plain pattern, explained the
  ancestry read after, never suppressed the plain pattern for the controlled one.
- **Composition note: top 3 language families by count/share, always shown, no dominance threshold.**
  Not "the dominant family, if any" — a single-family framing needs a threshold decision (how big a share
  counts as dominant?) that's exactly the kind of provisional, set-by-eye cutoff this project keeps having
  to revisit (coherence threshold `T`, `plurality_threshold`, etc. — deferred register). A fixed top-3-by-
  count rule needs no such judgment call and reads correctly whichever shape the group takes: one dominant
  family (15/40 Atlantic-Congo, 4/40 Nilo-Saharan — WO8d's own case), or several small ones with no
  dominant lineage at all (WO8d's Siberian trio — three unrelated families, the single tightest sub-group
  in the set — is exactly the pattern a single-dominant-family note would have missed entirely). Data
  dependency already exists — same `glottocode`/family field `distance_core.py`'s family-restricted
  resampling already reads; a `groupby(family).size()` on the filtered set, no new query.
- **Family-restricted resampling (`family_restricted_draw_cohesions`) is not called by this WO's engine
  path.** It stays in `distance_core.py`, unremoved, for TRACE, which will need it properly. One fewer
  statistic to compute, display, and label in this WO — worth taking given the few-days scope. The
  multiple-comparisons concern the original proviso was also guarding against (four lenses, many trait
  values, the eye landing on whatever looks tightest) is unaffected — still handled by the
  never-show-a-winning-lens-alone rule below, not by the family-restricted baseline.
- **Label what displacement and cohesion each mean, in the display.** Two statistics per row is more
  than a reader will infer correctly from position alone.

## Step 4 — link the map to the lens

Selecting a lens repaints the map: each society's marker encodes its distance to the group centroid in
that lens's z-space — the per-society quantity cohesion averages. The four lenses are genuinely
different physical questions (which is why `terrain` was kept out of `overall`), so flipping between
them shows *which* environmental dimension a group coheres on, geographically rather than numerically.

Provisos:

- **Marker colour encodes one thing.** If the tab already spends that channel on trait-value membership,
  decide deliberately: membership as the filter (which societies appear), lens distance as the ramp.
  Check the tab's existing behaviour before choosing.
- **The map shows cohesion only.** Displacement is a property of the group, not of any society, and has
  no per-marker analogue. Say so in the label or the map will be read as showing both.

## Accept gate

**SUPERSEDED, 2026-07-30 — the gate below described the lens-based scan; see `wo4_findings.md` for
the actual shipped gate (meter bars, no cohesion, donut composition).** ~~The engine takes `(trait,
value)` and returns cohesion and displacement per lens with percentiles against the random-draw
baseline, plus a top-3 language-family composition note; WO8d's EA034 numbers reproduce; EA042 lights
up on `water`/`thermal` on both statistics in the calibration run; EA042 renders its confirmatory
scatter and EA034 its four-lens scan; and the legacy PCA "Basin clusters" option is removed rather than
left hidden.~~ **Actual gate, met:** the engine returns a per-variable percentile-of-global-range (no
resampling) for the five raw variables, plus a composition note with family names and per-bucket
`soc_ids`; WO8d's Step 1 reproduction numbers still stand (unaffected — a separate code path); EA042
renders its confirmatory scatter, EA034 its five-variable meter scan, both with a donut composition
(hover-linked to the map); and the legacy PCA "Basin clusters" option is removed, not hidden.

Step 4 (map linkage) turned out not to be a separate step — the donut's hover-to-map linking absorbed
it, built alongside Step 3 rather than after. Both are done.

## Validation order

1. Engine parameterized, displacement added, terrain-variable provenance confirmed (Step 1).
2. EA034 reproduction + EA042 calibration reported to Karl. **Sign-off gate.**
3. Endpoint (Step 2); payload reviewed.
4. Both displays (Step 3); Karl reviews in the browser. **Sign-off gate.**
5. Map linkage (Step 4) if time allows.
6. `wo4_findings.md`; tracker roadmap row, *Last updated* stamp, and the Deferred entry for the legacy
   PCA option folded into *Locked decisions* in the same edit.

## Notebook conventions

New WO4 notebook. `# Cell N` first line of every cell; SQLAlchemy warning suppressed in DB cells;
`print(df.to_string())` for tabular output; standing figure-render pattern. Karl runs cell by cell and
reports output — no number asserted as a finding before Karl has shared it.

## Forward — not this WO

- **Traits beyond EA042/EA034** (D-PLACE enrichment). The hand-flag is deliberately not generalized; if
  a third trait is wired, revisit whether a rule is needed then.
- **Any significance floor or verdict gate.** The tracker's "no floor" decision stands; the
  never-show-a-winner-alone display rule is the containment instead.
- **Phase 4 correspondence testing** (PERMANOVA with restricted permutation). This WO's displacement
  statistic is a descriptive cousin of that machinery, not a substitute for it, and does not open it.