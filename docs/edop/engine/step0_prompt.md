CC — engine-assembly step 0: function inventory (no construction).
We're starting engine assembly for Areas. Before any refactoring, I want a complete map of what's in the notebooks, so we can see which functions become the engine and which stay behind as scaffolding. This is inventory only — do not refactor, move, or write any engine code; produce the map and stop for my review.

Read the four Areas notebooks — the step1 buffer resolver, the step2 attachment notebook, the step3 aggregator, and step3b_band_t — and list every function defined across them. For each: its real name, the notebook it lives in, and a one-line description of what it does.

Then classify each as an engine piece-part or scaffolding.
For engine piece-parts, tag the role it fills in this skeleton: resolver (basin set) · resolver (Band T grid / clipped cells) · attachment (basin values matrix) · attachment (Band T temporal indexing) · dispatch · aggregation branch — say which of the seven (coherence/B1, dominant-basin/B2, categorical-mixture/B3, flag-structural/B4, untyped-fallback+extreme/B5, modality/B6, Band T gridded/B7) · response-shaper · shared utility (db, geometry, scoring, catalog/typology, etc.).

For scaffolding, tag the kind: figure · validation/assertion · file IO (TSV writes) · reconnaissance/exploratory · fixture-specific setup.

Flag two things as you go. First, any function that touches the fields where the shared envelope has known collisions — n_basins vs n_units/unit_type, the two coverage_weight notions, the HYDE spread units. Second, any function that's dual-purpose or hard to bucket — don't force it, call it out.

Output a markdown table I can mark up, columns: function · notebook · one-line role · engine|scaffolding · role-slot or scaffolding-kind · collision flag. End with a short note on anything that surprised you, plus two specific things: skeleton roles that have no function yet (what assembly will have to write from scratch), and any function that seems to fill a role I haven't named.