# Notebook conventions

These are standing rules for every notebook. Consult before writing or editing any cell.

**Tooling**
- Edit notebooks with `NotebookEdit`, not the plain `Edit` tool.
- Karl runs notebooks cell by cell in PyCharm/Jupyter and reports back results. Never run notebook code via Bash to verify. Never assume a cell ran — wait for Karl to share output.

**Cell authoring**
- Every code cell must have `# Cell N` as its first line — no exceptions. Karl discusses cells by number.
- `%matplotlib inline` must be the first line of Cell 1; no rcParams or style overrides needed.
- Suppress SQLAlchemy pandas warnings at the top of any cell that makes DB calls:
  ```python
  import warnings; warnings.filterwarnings("ignore", message="pandas only supports SQLAlchemy")
  ```
  These proliferate with multiple DB calls and clutter output.

**Tabular output**
- Never output a bare DataFrame as the last expression in a cell — PyCharm renders it as an interactive table that cannot be cmd-c copied.
- Always use `print(df.to_string())` for any tabular output.

**DB and queries**
- **Connection**: `from scripts.shared.db_utils import db_connect` then `conn = db_connect()`. Default database is `cedop`.
- **Spatial queries**: `gpd.read_postgis(sql, conn, geom_col='geom').rename_geometry('geometry')` — always rename so column is `geometry` not `geom`.
- **World basemap**: `gpd.datasets` removed in geopandas 1.0; `geodatasets` not installed. Use pyogrio test fixtures: `import pyogrio; gpd.read_file(Path(pyogrio.__file__).parent / 'tests/fixtures/naturalearth_lowres/naturalearth_lowres.shp')`
- **Non-spatial queries**: `pd.read_sql(sql, conn)` — f-string SQL with values interpolated directly (no SQLAlchemy, no named params).
- **Inspect before hardcoding**: before writing city names, column names, enum values, or IDs into a cell, query the source table via `psql` to confirm exact values. Do not guess.
- `basin06` and `basin08` are verbatim BasinATLAS extractions. Derived seasonality variables (`pre_concentration`, `seas_phase_offset`, `pre_peak_month`, etc.) are NOT stored in those tables — they are computed on-the-fly by `seasonality.py:_compute_derived()` from monthly array columns. The persist views (`v_basin06_persist_rev2`, `v_basin08_persist_rev2`) expose `hybas_id`, `pre_mm_monthly`, `tmp_dc_monthly` for index-build use.

**Output path**
- Derive from module location, not relative path: `ROOT = Path(db_utils.__file__).parent.parent.parent; OUT = ROOT / 'output' / 'edop'`

**Map figure rendering**
- Do NOT rely on `plt.style.use('default')`, rcParams, or object-level helpers — PyCharm overrides them.
- Pattern: `fig.patch.set_facecolor('white')`, `ax.set_facecolor('white')`, `color='black'` on all text, `fig.savefig(..., facecolor='white')`, `plt.close(fig)`, then `display(IPImage(str(outpath)))`. This saves a PNG and displays it, bypassing PyCharm's inline renderer entirely.
- Always `print("drawing <name>...")` immediately before the `fig, axes = plt.subplots(...)` line. Figure output overwrites text output in PyCharm — an exception inside the figure-drawing block will be invisible if no text was printed before the figure rendered. The print anchors the text output above the figure.

**Extraction rule**
- Notebooks are a research record. Logic extracted to `engine.py` or other modules stays there; notebooks are never modified to call engine code. Extraction is one-directional.
