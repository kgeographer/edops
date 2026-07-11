# WO21 (scoping run) — Surface the polity `detail` payload and the hidden per-basin vector

**Branch:** `engine_v0.4b`
**Phase:** Areas · **Sub-phase:** neighborhoods (polity — response-shape design)
**Fixture:** Northern Song, year=1000, L06 (the WO20 fixture, unchanged)

## Goal

Produce a readable dump of an actual `areal_signature_polygon` response with `include_detail=True`, so Karl and Opus can decide the polity `detail` contract against real numbers rather than a reconstructed envelope. This is a **scoping/inspection run, not an engine change** — no new code in the response path, only a dump harness. The design decision it feeds (does `detail` carry the per-basin score vector, or does that live behind a separate endpoint) is WO21 proper and out of scope here.

## Scope

In: one `include_detail=True` run on the N Song fixture; a two-panel dump; verification of top-level key spellings.

Out: any change to `areal_signature_polygon` output, the per-basin matrix surfacing decision itself, choropleth/endpoint wiring, multi-timestep.

## Deliverable — a two-panel dump (TSV or JSON, implementer's call)

**Panel A — distribution summary as the payload returns it today.**
For each of the 35 spread B1 rows: `variable`, `representative_score`, and the full detail block (`spread`, `p10`, `p90`, `weight_at_zero`). This is the aspatial summary `&detail` currently carries.

**Panel B — the per-basin vector the payload currently hides.**
For two spread variables — `aridity_index` and one precipitation/moisture variable expected to show the NW/SE gradient cleanly (implementer picks; note the choice) — emit the per-basin `{hybas_id: score}` vector that the pipeline already computes internally as the B1 aggregation input. This vector is **not** a new computation; it exists upstream of the area-weighted collapse. Surface it read-only into the dump, alongside each basin's `weight` and `basin_in_polity_fraction` from the resolver, so the gradient can be read against the geography.

The two panels side by side are the whole point: Panel A is what the scalar consumer gets; Panel B is what the map consumer needs and the payload currently drops. Seeing them together is what lets us decide the WO21 contract.

## Also verify

Confirm the top-level payload key spellings against `assemble_payload` (reconstructed from the locked spec, not trusted from memory): `coverage`, `marginal_exposure` (and its `lt_50pct` / `lt_20pct` sub-keys), `modality_post_pass`, and the row envelope fields (`variable`, `method`, `status`, `coherence`, `representative_score`, `representative_raw`, `n_basins`, `coverage_weight`). Flag any mismatch.

## Out of scope (restated for the record)

- No surfacing decision is made here — Panel B is for inspection only, not a payload change.
- No new endpoint, no multi-timestep, no choropleth.
- Do not touch `areal_signature` (buffer path) or the engine response shape.

## Return

The dump file plus a one-paragraph note on which moisture variable was chosen for Panel B and why, and any key-spelling mismatches found. Karl runs it and pastes the result back for joint review.
