# EDOPS Documentation

| File | Description |
|------|-------------|
| `EDOPS_variable_catalog_v0.4.tsv` | Complete variable catalog for EDOPS signature v0.4 — all bands A–T, units, API keys, and characterization metadata; loaded at runtime by the API. Canonical, actively edited. |
| `EDOPS_variable_catalog_v0.3.tsv` | Frozen snapshot of the catalog as actually deployed in production for signature v0.3 (recovered from the live server 2026-08-06, since the v0.4 branch's copy had already diverged with no tag marking the v0.3 cutover). Historical reference only — not read by any code. |
| `edops_schema.json` | EDOPS signature schema v0.4 (regenerated 2026-08-16 against live output) — documents the `/api/signature` response structure for both default and `&flat` modes, with Timbuktu example values. `/api/area` and `/api/areas` share the same `profile_groups` envelope (documented at `docsite/api.md` instead). |
| `BasinATLAS_Catalog_v10.pdf` | Original HydroSHEDS BasinATLAS variable catalog (external reference); source definitions for all BasinATLAS-derived signature fields. |
| `EDOP_summary_20260608.pdf` | Project summary as of June 2026 — scope, research phases, current status, and next steps. |
| `EDOPS_data_characterization_report.pdf` | Phase 2 characterization report — statistical and spatial analysis of the EDOPS signature dataset across all bands. |
| `EDOPS_eda_findings.md` | Accreting log of EDA findings (F1.1–F11.6) from Phase 2 — distributions, outliers, and variable-level notes. |
| `EDOPS_esda_findings.md` | Accreting log of ESDA findings from Phase 2 — spatial autocorrelation, LISA clusters, and bivariate regional patterns. |
