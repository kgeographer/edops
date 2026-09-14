# EDOPS Documentation

| File | Description |
|------|-------------|
| `EDOPS_variable_catalog_v0.4.tsv` | Complete variable catalog for EDOPS signature v0.4 — all bands A–T, units, API keys, and characterization metadata; loaded at runtime by the API. Canonical, actively edited. |
| `drafts/EDOPS_variable_catalog_v0.3.tsv` | Frozen snapshot of the catalog as actually deployed in production for signature v0.3 (recovered from the live server 2026-08-06, since the v0.4 branch's copy had already diverged with no tag marking the v0.3 cutover). Historical reference only — not read by any code; moved to `drafts/` (gitignored) 2026-09-09. |
| `edops_schema_basin.json` | EDOPS signature schema v0.4, `scope=basin` (regenerated 2026-09-14 against live output) — documents the `/api/signature?scope=basin` response structure for both default and `&flat` modes, with Timbuktu example values. |
| `edops_schema_area.json` | EDOPS signature schema v0.4, `scope=area` (regenerated 2026-09-14 against live output) — documents the entirely different `/api/signature?scope=area` shape (a flat `variables` list, not `signature_bands`), with a real bbox example. `scope=buffer` shares this shape but isn't documented separately (expected to be retired soon). `/api/area` (singular) and `/api/areas` are separate, older endpoints with their own `"rows"`-based envelope — documented at `docsite/api.md` instead, not by either schema file here. |
| `BasinATLAS_Catalog_v10.pdf` | Original HydroSHEDS BasinATLAS variable catalog (external reference); source definitions for all BasinATLAS-derived signature fields. |
| `EDOP_summary_v04.md` | Current project summary (v0.4, September 2026) — scope, research phases, signature design, current status, and next steps. |
| `EDOPS_data_characterization_report.pdf` | Phase 2 characterization report — statistical and spatial analysis of the EDOPS signature dataset across all bands. |
| `EDOPS_eda_findings.md` | Accreting log of EDA findings (F1.1–F11.6) from Phase 2 — distributions, outliers, and variable-level notes. |
| `EDOPS_esda_findings.md` | Accreting log of ESDA findings from Phase 2 — spatial autocorrelation, LISA clusters, and bivariate regional patterns. |
