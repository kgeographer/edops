# Reading a signature

*Placeholder — content in development. Scoped 2026-08-06; see `logs/session_log_20260806.md`
for the working session this was scoped in.*

This page explains how to read the Signature tab's output — the accordion of bands, numbers,
badges, and small charts — not how to operate the Sandbox UI (that's the Overview page) and not
what each variable means (that's the [Codebook](../codebook.md)). Everything here is specific to
`/api/area`'s output (both Sandbox forks go through the Areas engine, even a single-basin
Settlement query); it does not apply to Workbench's environmental-profile panel, which reads
`/api/signature` directly and displays flat values with none of this machinery.

## Settlement vs. polity: the structural fork

- [ ] `[prose]` One basin (n=1) vs. many basins (n-basin, area-weighted aggregation) is the single
      idea everything else depends on. A settlement's histogram degenerates to one bar; a
      polity's histogram shows the real spread across its constituent basins.

## The row forms

- [ ] `[prose]` Not every row renders the same way — `row.method` in the payload selects one of
      six forms. Grounded in `sandbox_v3.html`'s `renderLeaf()` (~line 3119):
    - `area_weighted` — pct + concentrated/spread badge + real per-basin histogram
    - `distribution_only` — pct, **no badge**, single solid range bar (p10–p90) instead of a
      histogram — easy to mistake for a degenerate histogram; it's a different renderer
    - `extreme` — pct + raw value + the carrying basin's ID, no chart (basin picked by extremum,
      not averaged)
    - `dominant_basin` — same text-only shape as `extreme`, different selection logic
    - `class_mixture` — categorical: dominant class name as text + a modal-share bar
    - `flag_fraction` — plain percentage, no bar

## Reading the pieces

- [ ] `[prose]` `pct` = global percentile. Each basin's raw value is ranked via SQL
      `PERCENT_RANK()` against every basin worldwide at the query's resolution level (all of
      `basin06` or `basin08`), not a regional or neighborhood percentile. For a polity, the
      displayed score is the area-weighted mean of each contributing basin's own percentile.
- [ ] `[prose]` Concentrated vs. spread — badge driven by `p90 − p10` against a fixed 20
      percentile-point threshold (`_SPREAD_THRESHOLD` in `engine.py`). Under 20 points →
      concentrated (the polity's basins agree); 20+ → spread (real internal heterogeneity).
      Only `area_weighted` rows show this badge.
- [ ] `[prose]` The two numbers flanking a histogram/range bar are p10/p90 of the per-basin
      percentile distribution — the middle-80% range — not the raw variable's min/max in its own
      units.
- [ ] `[prose]` `boundary NNN` — the polity slice/boundary ID the query resolved to; same for
      every row in one query.

## Band T is its own thing

- [ ] `[prose]` Band T doesn't use any of the above — `renderTBand()` is a separate code path
      with its own widgets per source: LMR (line chart + year slider), HYDE (land-use series),
      eVolv2k (event list). Keyed to `from_year`/`to_year`, not percentile/badge logic.

## Worked example

- [ ] `[wire]` One fully annotated screenshot walking through a complete readout end to end —
      absorbs what would otherwise be a generic "how to read an entry" stub. Candidate source
      screenshots already exist from the scoping conversation; decide whether to reuse the
      canonical example places/polities used elsewhere in the docs (Timbuktu, etc.) for
      consistency, or the ones already captured.

## Format decision

Follows the same screenshot + caption pattern already settled for the Sandbox walkthroughs
(`docs/design/DOCSv4 — TODO.md` §7) rather than prose-only, given how visual this content is.
