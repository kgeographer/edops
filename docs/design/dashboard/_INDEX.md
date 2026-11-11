# Index: docs/design/dashboard/

This folder grew past its name. Most files belong to the WHG profile and `/whgmodal` endpoint work, not the Dashboard. They stay here because code and notebooks point at these paths (`profile_templates.md` and `wo05_wikilinks.csv` are read by `scripts/edop/whg/wo04_fill.py`; the `wo0N_filled_profiles.md` files are written by the WHG notebooks). New V1 material goes under `docs/edop/_v1/`.

| Files | Belong to |
|---|---|
| `sandbox_cheatsheet*.md`, `examples/`, `wo01_*`, `wo02_*`, `main_changes_log.md`, `edops_docs_for_opus.*` | Dashboard: Sandbox cheat sheet and the statement inventory |
| `wo03_*` to `wo10a_*`, `profile_templates*.md`, `wo05_wikilinks.csv`, `modal_dummy*.md`, `whg*.md`, `WHG-profile_*.md` | WHG profile and `/whgmodal` endpoint (`docs/edop/_v1/whgmodal/`) |
| `EDOPS v1 plan *.md`, `v1_workplan_05Nov.md` | V1 planning across all three sub-phases |

Where V1 lives now:

- `docs/edop/_v1/dashboard/`: Sandbox-to-Dashboard morph (not begun)
- `docs/edop/_v1/whgmodal/`: WHG endpoint, new material only
- `docs/edop/_v1/regionality/`: regional and non-global temporal data (active)
