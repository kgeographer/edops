# WO1 — Within-polity-variance ranking notebook

**Phase:** DEMO · Track 1 (hero-shot curation)
**Kind:** Research notebook — not a surface build. Nothing here touches sandbox_v3.
**Branch:** `demo` (no per-WO feature branch needed for a notebook; findings + TSV commit to `demo`)

## Goal

For a chosen environmental variable, rank every Cliopatria polity extent by the
**internal spread** of that variable across its member basins, producing a shortlist
of gradient-straddling polities as hero-shot candidates. Validate the mechanic
against Northern Song, which should rank high on an aridity/humidity variable.

The mechanic replaces "paint and eyeball" (doesn't scale, requires knowing the
history in advance) with "rank by spread, inspect the top of the list — the
environment points you at the polities worth a historian's attention."

## Deliverables

- `notebooks/edop/demo/wo1_within_polity_variance.ipynb`
  (notebook conventions: `# Cell N` first line each cell; `db_connect()`;
  output path derived from module location, not relative)
- `output/edop/demo/wo1_polity_spread_{variable}.tsv` — the ranked table(s)
- `docs/edop/demo/wo1_findings.md` — top ~15 per variable, the N Song validation
  result, and any met-and-deferred items the run surfaces

## Method (provisos — CC discovers particulars in the code)

1. **Base unit = rows of `gaz.clio_polities`.** Each row is a `name` +
   `fromyear`/`toyear` + `geom` slice. Compute spread per row; roll up to polity
   (`groupby name`, max spread across slices) for the shortlist. *[FORK — Q1]*

2. **Membership rule:** area-weighted overlap between polity `geom` and `basin06`
   (`ST_Area(ST_Intersection(...)) / basin_area`), inclusion at a documented overlap
   floor; `ST_Intersects` as the GIST prefilter. The ranking is **conditional on this
   rule** — the membership-rule choice is already an open row in the deferred register
   (Phase-3 design section); reference it, don't re-log. Centroid-in is the cheap
   fallback if the area-weighted join is too heavy for a first pass.

3. **Rank on the same per-basin quantity the choropleth paints.** Confirm in code
   what the Explorer values path / `basin06` serves for the chosen variable
   (global-percentile score vs native units) and compute spread on *that* quantity,
   so the ranking predicts visible colour spread **by construction**. If they diverge,
   the mechanic stops predicting visual drama — so this alignment is the point, not a
   detail. First cut leans percentile (commensurable, precomputed, maps to colour if
   the paint is percentile-based); native-unit spread is a noted refinement
   (register: "native-unit means need the raw-values table").

4. **Spread statistic:** primary rank key = interpercentile spread (p90 − p10) of the
   per-basin quantity — robust to a single outlier basin, directly legible ("spans
   10th→90th percentile of aridity"). Secondary columns: SD, min, max, median,
   **n_basins** (a 2-basin polity with huge spread is a weaker straddle story than a
   40-basin one; keep n_basins visible so the rollup isn't fooled by tiny extents).

5. **Variables, first cut: static BasinATLAS baselines only.** Aridity primary (this
   is what validates N Song). Add 1–2 more static baselines (a moisture/precip
   baseline, a terrain/relief variable). **Temporal-variable spread deferred to a
   second pass** — HYDE land-use at an epoch and LMR anomaly over a span each need a
   chosen temporal window and the temporal tables; folding them in now bloats WO1 and
   couples it to the slice/temporal question. *[FORK — Q2]*

6. **Level: L06** (16,397 basins). Spread — and therefore the ranking — is
   level-specific (MAUP); declare the level in every output. An L08 re-rank is a later
   optional pass, naturally paired with the L06↔L08 hero shot.

## Accept gate

- Ranked TSV produced for aridity; **Northern Song lands in the top tier** (say top
  ~10–15% of multi-basin polity extents). If it does not, that is a *finding*, not a
  failure to smooth over — most likely about the membership rule, the spread statistic,
  or the smooth-gradient-vs-two-regime gap (see note).
- Karl reviews the ranked table before any downstream hero-shot selection.

## The one methodological risk to watch (name it in findings)

Spread ranks *how much* the variable varies inside the extent. A hero shot wants the
polity to visibly **straddle a boundary** — which is bimodality / regime-separation,
not mere variance. A polity on a smooth continental gradient can post high variance
with no dramatic visual edge; a polity split across a sharp ecotone has the drama.
The two correlate but aren't identical. The workplan accepts spread as the first-cut
mechanic and N Song validates it, and modality detection is already a deferred-register
item — so we do **not** build modality here. We *watch*: if the top of the list is
smooth-gradient rather than boundary-straddling, that's the signal to pull the deferred
modality work forward. A cheap secondary column (e.g. a gap/dip statistic) is an
optional add if it's nearly free; otherwise leave it for the refinement pass.

## Out of scope for WO1

Candidate maps (optional WO2, using `scripts/edop/edops_polity_maps.py` as the render
reference); temporal-variable spread; L08 re-rank; any sandbox_v3 change. Research, not
build.
