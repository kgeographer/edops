"""
EDOPS Areas Engine — promoted primitives (WO1 + WO2 + WO3) and aggregation blocks.

Bottom-of-stack pieces (WO1):
  resolve_buffer    — point + radius → weighted basin set (was inline in step1/step2)
  weighted_quantile — weighted quantile primitive (was duplicated in step3/step3b)
  diff_output       — regression harness: compare engine output to a reference

Catalog layer (WO11a):
  load_catalog      — reads codebook TSV → meta_df (build-once startup layer)
                      rows: sourced (has DB col) + derived (no DB col, branch-synthesized)

Attachment pass (WO2):
  attach_values     — basin set + meta_df → (matrix_df, class_id_df, raw_df)
                      skips derived rows (no DB col to attach)

  Private SQL builders (call via attach_values):
  _parse_zf, _val_expr, rank_expr, two_pass_sql

Dispatch (WO3):
  dispatch_variable — (typology_cluster, kind) → block label
                      caller skips derived rows before invoking
"""

import warnings
import numpy as np
import pandas as pd

# psycopg3 connections work fine with pd.read_sql; suppress the SQLAlchemy nag
warnings.filterwarnings(
    'ignore',
    message='pandas only supports SQLAlchemy connectable',
    category=UserWarning,
)


_N_HIST_BINS             = 20
_LOW_RES_CELL_THRESHOLD  = 5    # w_eff below which histogram is flagged low_resolution
_LOW_RES_BASIN_THRESHOLD = 3    # n_units below which basin histogram is flagged


def resolve_buffer(lat, lon, radius_km, level, conn, epsilon=0.001):
    """
    Buffer resolver: point + radius → weighted basin set.

    weight = fraction of buffer area covered by each basin (geography-accurate).
    Slivers below epsilon are dropped. Open-water shortfall (1 − Σweight) is
    reported by callers, not renormalized here. hybas_id is always int64.

    Parameters
    ----------
    lat, lon   : float — WGS-84 coordinates
    radius_km  : float — buffer radius in km
    level      : str   — '06' or '08'
    conn       : psycopg3 connection
    epsilon    : float — sliver threshold (fraction of buffer area)

    Returns
    -------
    DataFrame with columns [hybas_id (int64), weight], ordered by weight DESC.
    """
    radius_m = radius_km * 1000
    table    = f'public.basin{level}'

    sql = f"""
    WITH pt AS (
        SELECT ST_SetSRID(ST_MakePoint({lon}, {lat}), 4326)::geography AS pt_geog
    ),
    buf AS (
        SELECT ST_Buffer(pt_geog, {radius_m}) AS buf_geog,
               ST_Area(ST_Buffer(pt_geog, {radius_m})) AS buf_area_m2
        FROM pt
    ),
    candidates AS (
        SELECT b.hybas_id,
               ST_Area(ST_Intersection(b.geog, buf.buf_geog)) AS overlap_m2,
               buf.buf_area_m2
        FROM {table} b, buf
        WHERE ST_Intersects(b.geog, buf.buf_geog)
    )
    SELECT hybas_id,
           overlap_m2 / buf_area_m2 AS weight
    FROM candidates
    WHERE overlap_m2 / buf_area_m2 >= {epsilon}
    ORDER BY weight DESC
    """

    df = pd.read_sql(sql, conn)
    df['hybas_id'] = df['hybas_id'].astype('int64')
    return df


def resolve_polygon(geom_wkt, level, conn, epsilon=0.0):
    """
    Polygon resolver: WKT geometry → weighted basin set.

    weight = overlap_area / polity_area (geography-accurate; same convention as
    resolve_buffer's overlap/buffer_area). basin_in_polity_fraction = overlap_area
    / basin_area — records how much of each basin falls inside the polygon; used
    for the marginal-exposure diagnostic. Basins below epsilon are dropped.

    Parameters
    ----------
    geom_wkt : str   — WKT polygon (SRID 4326)
    level    : str   — '06' or '08'
    conn     : psycopg3 connection
    epsilon  : float — minimum weight threshold (fraction of polygon area)

    Returns
    -------
    DataFrame with columns [hybas_id (int64), weight,
                             basin_in_polity_fraction, overlap_area_km2],
    ordered by weight DESC.
    """
    table = f'public.basin{level}'
    sql = f"""
    WITH polity AS (
        SELECT  ST_GeomFromText(%s, 4326)                           AS geom,
                ST_Area(ST_GeomFromText(%s, 4326)::geography)       AS area_m2
    ),
    intersections AS (
        SELECT  b.hybas_id,
                ST_Area(ST_Intersection(b.geom, p.geom)::geography) AS overlap_m2,
                ST_Area(b.geog)                                       AS basin_area_m2
        FROM    {table} b, polity p
        WHERE   ST_Intersects(b.geom, p.geom)
    )
    SELECT  i.hybas_id,
            i.overlap_m2 / p.area_m2                AS weight,
            i.overlap_m2 / i.basin_area_m2          AS basin_in_polity_fraction,
            ROUND((i.overlap_m2 / 1e6)::numeric, 2) AS overlap_area_km2
    FROM    intersections i, polity p
    WHERE   i.overlap_m2 / p.area_m2 >= {epsilon}
    ORDER BY weight DESC
    """
    cur  = conn.execute(sql, (geom_wkt, geom_wkt))
    cols = [d[0] for d in cur.description]
    df   = pd.DataFrame(cur.fetchall(), columns=cols)
    df['hybas_id'] = df['hybas_id'].astype('int64')
    return df


def resolve_polity(polity_name, year, level, conn, epsilon=0.0):
    """
    Polity resolver: Cliopatria name + year → (geom_wkt, basin_set, polity_meta).

    Looks up the Cliopatria row where name = polity_name AND fromyear ≤ year ≤ toyear,
    extracts the geometry, and delegates basin resolution to resolve_polygon.

    Raises ValueError if no row matches. If multiple rows match (shouldn't happen —
    phases don't overlap), picks the narrowest temporal span.

    Parameters
    ----------
    polity_name : str  — exact Cliopatria name (gaz.clio_polities.name)
    year        : int  — year CE; must fall within fromyear..toyear of some row
    level       : int  — 6 or 8
    conn        : psycopg3 connection
    epsilon     : float — passed through to resolve_polygon

    Returns
    -------
    (geom_wkt: str, basin_set: DataFrame, polity_meta: dict)
    polity_meta keys: id, name, fromyear, toyear, year
    """
    sql = """
    SELECT id, name, fromyear, toyear, ST_AsText(geom) AS geom_wkt
    FROM gaz.clio_polities
    WHERE name = %s AND fromyear <= %s AND toyear >= %s
    """
    rows = conn.execute(sql, (polity_name, year, year)).fetchall()
    if len(rows) == 0:
        raise ValueError(f'No polity found: name={polity_name!r}, year={year}')
    if len(rows) > 1:
        rows = sorted(rows, key=lambda r: r[3] - r[2])  # narrowest span wins
    r = rows[0]
    polity_meta = {
        'id': int(r[0]), 'name': r[1],
        'fromyear': int(r[2]), 'toyear': int(r[3]), 'year': year,
    }
    geom_wkt  = r[4]
    level_str = f'{level:02d}'
    basin_set = resolve_polygon(geom_wkt, level_str, conn, epsilon=epsilon)
    return geom_wkt, basin_set, polity_meta


def weighted_quantile(scores, weights, q):
    """
    Weighted quantile via sorted cumulative weights + linear interpolation.

    Parameters
    ----------
    scores  : array-like of float
    weights : array-like of float (need not sum to 1; normalized internally)
    q       : float in [0, 1]

    Returns
    -------
    float
    """
    scores  = np.asarray(scores,  dtype=float)
    weights = np.asarray(weights, dtype=float)
    idx  = np.argsort(scores)
    sv   = scores[idx]
    sw   = weights[idx]
    cumw = np.cumsum(sw)
    cumw /= cumw[-1]
    return float(np.interp(q, cumw, sv))


def _weighted_histogram(values, raw_weights, unit_type, n_bins=_N_HIST_BINS):
    """
    Weighted histogram for the distribution detail block.

    values      : array-like float — per-unit scores (basin) or native values (cells)
    raw_weights : array-like float — fractional coverage (cells: overlap/area;
                  basins: area-weight). Normalized internally.
    unit_type   : 'basin' | 'hyde_cell' | 'lmr_cell'
    n_bins      : fixed count; keeps payload bounded regardless of unit count

    Temporal stamp fields (resolver_year, band_t_from, band_t_to) are added by
    the caller after this returns so the function stays substrate-agnostic.

    Returns None if no valid units.
    """
    v = np.asarray(values,      dtype=float)
    w = np.asarray(raw_weights, dtype=float)
    mask = np.isfinite(v) & np.isfinite(w) & (w > 0)
    v, w = v[mask], w[mask]
    if len(v) == 0:
        return None

    w_eff  = float(w.sum())
    w_norm = w / w_eff
    n      = int(len(v))
    mean_  = float(np.dot(v, w_norm))

    vmin, vmax = float(v.min()), float(v.max())
    edges = (np.linspace(vmin - 0.5, vmin + 0.5, n_bins + 1)
             if vmax == vmin else np.linspace(vmin, vmax, n_bins + 1))

    bin_idx = np.clip(np.digitize(v, edges[1:-1]), 0, n_bins - 1)
    bin_w   = np.zeros(n_bins)
    for i, ww in zip(bin_idx, w_norm):
        bin_w[i] += ww

    low_res = (w_eff < _LOW_RES_CELL_THRESHOLD) if unit_type != 'basin' \
              else (n < _LOW_RES_BASIN_THRESHOLD)

    return {
        'bins':           [round(float(e), 4) for e in edges],
        'weights':        [round(float(ww), 6) for ww in bin_w],
        'n_units':        n,
        'unit_type':      unit_type,
        'low_resolution': low_res,
        'min':            round(vmin, 4),
        'max':            round(vmax, 4),
        'p10':            round(weighted_quantile(v, w, 0.1), 4),
        'p90':            round(weighted_quantile(v, w, 0.9), 4),
        'mean':           round(mean_, 4),
    }


def diff_output(actual, reference, float_tol=0.01, id_col='hybas_id', label=''):
    """
    Regression harness: compare engine output to a reference DataFrame or TSV path.

    Reports mismatches in row count, column set, and values (float_tol for numerics).
    Returns True if all checks pass. Write it generally — attachment and each
    aggregation branch can diff against their TSVs by passing the relevant id_col.

    Parameters
    ----------
    actual    : DataFrame
    reference : DataFrame or Path/str — TSV read with sep='\\t' if not a DataFrame
    float_tol : float — absolute tolerance for numeric comparisons
    id_col    : str or None — join column; None → positional comparison
    label     : str — report header tag
    """
    if not isinstance(reference, pd.DataFrame):
        dtype = {id_col: 'int64'} if id_col else {}
        reference = pd.read_csv(reference, sep='\t', dtype=dtype)

    tag = f'[{label}] ' if label else ''
    ok  = True

    # Row count
    if len(actual) != len(reference):
        print(f'{tag}FAIL rows: got {len(actual)}, expected {len(reference)}')
        ok = False
    else:
        print(f'{tag}OK   rows: {len(actual)}')

    # Column sets
    a_cols  = set(actual.columns)
    r_cols  = set(reference.columns)
    extra   = a_cols - r_cols
    missing = r_cols - a_cols
    if extra:
        print(f'{tag}WARN extra columns in actual  : {sorted(extra)}')
    if missing:
        print(f'{tag}WARN missing columns in actual: {sorted(missing)}')

    common = sorted(a_cols & r_cols)

    # Align on id_col if present in both
    if id_col and id_col in a_cols and id_col in r_cols:
        a = actual.set_index(id_col)
        r = reference.set_index(id_col)
        only_a = set(a.index) - set(r.index)
        only_r = set(r.index) - set(a.index)
        if only_a or only_r:
            print(f'{tag}FAIL {id_col} mismatch — '
                  f'only in actual: {sorted(only_a)[:5]}, '
                  f'only in ref: {sorted(only_r)[:5]}')
            ok = False
        shared = sorted(set(a.index) & set(r.index))
        a = a.loc[shared]
        r = r.loc[shared]
        check_cols = [c for c in common if c != id_col]
    else:
        a = actual.reset_index(drop=True)
        r = reference.reset_index(drop=True)
        check_cols = common

    for col in check_cols:
        if col not in a.columns or col not in r.columns:
            continue
        try:
            a_num = pd.to_numeric(a[col], errors='raise')
            r_num = pd.to_numeric(r[col], errors='raise')
            max_diff = (a_num - r_num).abs().max()
            if max_diff > float_tol:
                print(f'{tag}FAIL {col}: max_diff={max_diff:.6f} (tol={float_tol})')
                ok = False
        except (ValueError, TypeError):
            # Treat None and NaN as equivalent nulls before string comparison
            a_null  = pd.isna(a[col])
            r_null  = pd.isna(r[col])
            n_null  = int((a_null != r_null).sum())
            mask    = ~a_null & ~r_null
            n_val   = int((a[col][mask].astype(str) != r[col][mask].astype(str)).sum())
            mismatches = n_null + n_val
            if mismatches:
                print(f'{tag}FAIL {col}: {mismatches} string mismatch(es)')
                ok = False

    if ok:
        print(f'{tag}PASS')
    return ok


# ── WO11a: catalog layer ─────────────────────────────────────────────────────

from pathlib import Path as _Path

# endorheic is type='string' in the codebook (3-class integer-coded value 0/1/2)
# but is consumed by aggregate_b4 as a raw integer flag — same as coast_flag
# (type='boolean'). A future catalog 'kind' column would make this explicit.
_FLAG_API_KEYS = frozenset({'endorheic', 'coast_flag'})
_SKIP_API_KEYS = frozenset({'gdp_avg', 'human_dev_idx'})
_SKIP_BANDS    = frozenset({'T', 'output'})

_TYPE_TO_KIND = {
    'float':    'continuous',
    'integer':  'continuous',
    'string':   'categorical',
    'boolean':  'flag',
    'fraction': 'continuous',
}

_CATALOG_PATH = (
    _Path(__file__).resolve().parents[3]
    / 'documentation' / 'EDOPS_variable_catalog_v0.3.tsv'
)


def load_catalog(level=6, codebook_path=None):
    """
    Build-once catalog layer: reads the codebook TSV → meta_df for engine use.

    Two row classes
    ---------------
    Sourced  (source != 'Derived'): have a basin08_col; flowed through
             attach_values and dispatch_variable.
    Derived  (source == 'Derived'): no DB column; synthesized by their branch
             (B4 for outlet_type / coast_fraction; future branches for
             elevation_point, relief_range_m, relief_position).
             Present in meta_df for assembly keying and provenance; attach_values
             and the dispatch loop skip them.

    Parameters
    ----------
    level         : int  — 6 or 8; selects zero_fraction_*_L{level}
    codebook_path : Path or None — defaults to EDOPS_variable_catalog_v0.3.tsv

    Returns
    -------
    DataFrame indexed by api_key; columns:
        schema_key, su, db_col, kind, band, position_method,
        typology_cluster, zero_fraction, derived (bool)

    Integrity note
    --------------
    The sourced rows exactly reproduce step2_meta.tsv (the frozen notebook output)
    modulo: (a) endorheic.schema_key = 'endorheic' (Karl's 2026-06-24 catalog edit;
    was 'outlet_type' when step2_meta was frozen); (b) the new 'derived' column.
    """
    import csv

    path = codebook_path or _CATALOG_PATH

    zf_s_col = f'zero_fraction_s_L{level}'
    zf_u_col = f'zero_fraction_u_L{level}'

    rows = []

    with open(path, newline='') as fh:
        for rec in csv.DictReader(fh, delimiter='\t'):
            band   = (rec.get('band')   or '').strip()
            status = (rec.get('status') or '').strip()
            source = (rec.get('source') or '').strip()

            if band in _SKIP_BANDS or status != 'implemented':
                continue

            raw_type = (rec.get('type') or '').strip()
            if raw_type == 'object':  # pnv_shares: multi-column variable, no single db_col
                continue

            is_derived = (source == 'Derived')
            schema_key = (rec.get('schema_key')        or '').strip() or None
            tc         = (rec.get('typology_cluster')  or '').strip() or None
            pm         = (rec.get('position_method')   or '').strip() or None
            col_s      = (rec.get('basin08_col_s')     or '').strip() or None
            col_u      = (rec.get('basin08_col_u')     or '').strip() or None

            def _emit(ak, su, col, zf_raw):
                if not ak or ak in _SKIP_API_KEYS:
                    return
                if not is_derived and not col:
                    # Upstream-only coalesce: sourced row has no _s column but _u exists.
                    # Use the upstream column so the variable still appears in the payload.
                    if su == 's' and col_u:
                        col = col_u
                    else:
                        return
                # Flags first (endorheic: type='string' but raw-integer B4 input).
                # rarity_rank → categorical: the method is chosen specifically for
                # class-membership variables (no intrinsic ordering); covers integer-
                # coded IDs like eco_id / wetland_class that map to text via lu_* views.
                if ak in _FLAG_API_KEYS:
                    kind = 'flag'
                elif pm == 'rarity_rank':
                    kind = 'categorical'
                else:
                    kind = _TYPE_TO_KIND.get(raw_type, 'continuous')
                rows.append({
                    'api_key':          ak,
                    'schema_key':       schema_key,
                    'su':               su,
                    'db_col':           col,
                    'kind':             kind,
                    'band':             band,
                    'position_method':  pm,
                    'typology_cluster': tc,
                    'zero_fraction':    _parse_zf(zf_raw),
                    'derived':          is_derived,
                })

            _emit(
                (rec.get('api_key_s') or '').strip(), 's',
                col_s, rec.get(zf_s_col),
            )
            _emit(
                (rec.get('api_key_u') or '').strip(), 'u',
                col_u, rec.get(zf_u_col),
            )

    return pd.DataFrame(rows).set_index('api_key')


# ── WO2: attachment pass ──────────────────────────────────────────────────────


def _parse_zf(v):
    """Return float zero_fraction or None if missing/NaN/non-numeric."""
    try:
        f = float(v)
        return f if not np.isnan(f) else None
    except (TypeError, ValueError):
        return None


def _val_expr(db_col, method):
    """ORDER BY expression inside PERCENT_RANK for a given position_method."""
    if method == 'log_percentile':
        return f"LN(1.0 + GREATEST(0.0, {db_col}::float))"
    return f"{db_col}::float"


def rank_expr(db_col, method, zero_fraction=None, zero_fraction_threshold=0.20):
    """
    Monolithic PERCENT_RANK SQL expression — used only when n_nodata == 0.

    The notebook version read ZERO_FRACTION_THRESHOLD from notebook scope (implicit
    closure). Here it is an explicit parameter so the function is self-contained.
    """
    nodata = f"({db_col} = -9999 OR {db_col} IS NULL)"
    val    = _val_expr(db_col, method)

    if zero_fraction is not None and zero_fraction >= zero_fraction_threshold:
        pos_val = (f"CASE WHEN {nodata} OR {db_col} <= 0 THEN NULL "
                   f"ELSE {val} END")
        return (
            f"CASE WHEN {nodata} THEN NULL "
            f"WHEN {db_col} = 0 THEN 0.0 "
            f"ELSE PERCENT_RANK() OVER ("
            f"PARTITION BY CASE WHEN {db_col} > 0 THEN 1 ELSE 0 END "
            f"ORDER BY {pos_val} NULLS LAST) * 100 END"
        )
    else:
        order_expr = f"CASE WHEN {nodata} THEN NULL ELSE {val} END"
        return (
            f"CASE WHEN {nodata} THEN NULL "
            f"ELSE PERCENT_RANK() OVER (ORDER BY {order_expr} NULLS LAST) * 100 END"
        )


def two_pass_sql(db_col, alias, method, table, ids_clause):
    """
    Filtered-CTE PERCENT_RANK for vars with nodata rows in the basin table.

    Nodata rows (-9999/NULL) are excluded from the ranking population so they
    do not compress valid percentiles. The LEFT JOIN restores the target basin
    rows; nodata values receive NULL score (same as the monolithic form).
    """
    val = _val_expr(db_col, method)
    return f"""
        WITH valid_pop AS (
            SELECT hybas_id, {db_col}
            FROM {table}
            WHERE {db_col} IS NOT NULL AND {db_col} <> -9999
        ),
        ranked AS (
            SELECT hybas_id,
                   PERCENT_RANK() OVER (ORDER BY {val}) * 100 AS score
            FROM valid_pop
        )
        SELECT b.hybas_id,
               CASE WHEN b.{db_col} IS NULL OR b.{db_col} = -9999 THEN NULL
                    ELSE r.score END AS {alias}
        FROM {table} b
        LEFT JOIN ranked r USING (hybas_id)
        WHERE b.hybas_id IN ({ids_clause})
    """


def attach_values(basin_set, meta_df, conn, table, view,
                  zero_fraction_threshold=0.20):
    """
    Attachment pass: basin set + variable metadata → values matrix.

    Produces the three DataFrames Step 3 branches consume:
      matrix_df   — continuous position scores (0–100), categorical text labels,
                    flag raw integers; index hybas_id
      class_id_df — integer class IDs for categorical variables; index hybas_id
      raw_df      — weight + raw values from the view; index hybas_id

    Parameters
    ----------
    basin_set : DataFrame — hybas_id (int64) as index OR as column; weight column
    meta_df   : DataFrame — index api_key; columns kind, db_col, position_method,
                zero_fraction, etc. (built from the catalog by load_catalog — not
                part of this function's scope)
    conn      : psycopg3 connection
    table     : str — raw basin table, e.g. 'public.basin06'
    view      : str — persist view with text labels, e.g. 'public.v_basin06_persist_rev1'
    zero_fraction_threshold : float — threshold for zero-aware PARTITION scoring (0.20)

    Returns
    -------
    (matrix_df, class_id_df, raw_df) — all indexed by hybas_id (int64)

    Locked behaviors preserved
    --------------------------
    - PERCENT_RANK population hygiene: two-pass SQL excludes -9999/NULL rows
    - Zero-aware PARTITION BY for zero_fraction >= threshold (zeros → 0.0 explicitly)
    - Flags emitted as raw integers (coast_flag bool, endorheic 0/1/2)
    - Categoricals as text labels (matrix_df) + integer IDs (class_id_df)
    - gdp_avg / human_dev_idx excluded (must be absent from meta_df at call time)
    - hybas_id always int64

    Implicit-input hazards surfaced (see WO2 report)
    -------------------------------------------------
    - ZERO_FRACTION_THRESHOLD was a notebook-scope closure in rank_expr → explicit param
    - ids_clause derived internally from basin_set.index
    - Catalog loading (_val, _zf helpers, meta_df construction) is NOT part of this
      function; meta_df is caller-supplied (startup-time product in production)
    - level is NOT a parameter: table and view encode the level; meta_df bakes in the
      level-specific zero_fraction column selection
    """
    # Normalize basin_set so hybas_id is the index
    if 'hybas_id' in basin_set.columns:
        basin_set = basin_set.set_index('hybas_id')
    basin_set.index = basin_set.index.astype('int64')

    ids_clause = ', '.join(str(h) for h in basin_set.index)

    # Derived rows have no db_col; skip the DB query pass (produced by their branch)
    if 'derived' in meta_df.columns:
        meta_df = meta_df[~meta_df['derived']]

    cont_vars = meta_df[meta_df['kind'] == 'continuous']
    cat_vars  = meta_df[meta_df['kind'] == 'categorical']
    flag_vars = meta_df[meta_df['kind'] == 'flag']

    # ── Step 1: raw values from view ─────────────────────────────────────────
    raw_all = pd.read_sql(
        f"SELECT * FROM {view} WHERE hybas_id IN ({ids_clause})", conn
    ).set_index('hybas_id')
    raw_all.index = raw_all.index.astype('int64')
    raw_all = raw_all.drop(columns=['geom'], errors='ignore')

    num_cols = raw_all.select_dtypes(include='number').columns
    raw_all[num_cols] = raw_all[num_cols].replace(-9999, np.nan)

    raw_all = basin_set[['weight']].join(raw_all)
    keep_cols = ['weight'] + [k for k in meta_df.index if k in raw_all.columns]
    raw_df = raw_all[keep_cols].copy()

    # ── Step 2: position scores for continuous variables ──────────────────────
    n_nodata_map = {}
    for api_key, row in cont_vars.iterrows():
        zf = _parse_zf(row.get('zero_fraction'))
        is_zero_aware = zf is not None and zf >= zero_fraction_threshold
        if is_zero_aware:
            n_nodata_map[api_key] = 0
        else:
            n = conn.execute(
                f"SELECT count(*) FROM {table} "
                f"WHERE {row['db_col']} = -9999 OR {row['db_col']} IS NULL"
            ).fetchone()[0]
            n_nodata_map[api_key] = int(n)

    clean_set    = {k for k, n in n_nodata_map.items() if n == 0}
    affected_set = set(n_nodata_map) - clean_set

    # Monolithic query for clean vars (no nodata in basin table)
    select_parts = ['hybas_id']
    alias_map    = {}
    for api_key, row in cont_vars.iterrows():
        if api_key not in clean_set:
            continue
        alias = f'pos_{api_key}'
        zf    = _parse_zf(row.get('zero_fraction'))
        select_parts.append(
            f"{rank_expr(row['db_col'], row['position_method'], zf, zero_fraction_threshold)} AS {alias}"
        )
        alias_map[alias] = api_key

    clean_sql = (
        f"WITH ranked AS (SELECT {', '.join(select_parts)} FROM {table}) "
        f"SELECT * FROM ranked WHERE hybas_id IN ({ids_clause})"
    )
    pos_clean = (pd.read_sql(clean_sql, conn)
                   .set_index('hybas_id')
                   .rename(columns=alias_map))
    pos_clean.index = pos_clean.index.astype('int64')

    # Two-pass queries for vars with nodata in the basin table
    nodata_frames = []
    for api_key in sorted(affected_set):
        row   = cont_vars.loc[api_key]
        alias = f'pos_{api_key}'
        sql   = two_pass_sql(row['db_col'], alias, row['position_method'],
                             table, ids_clause)
        df = (pd.read_sql(sql, conn)
                .set_index('hybas_id')
                .rename(columns={alias: api_key}))
        df.index = df.index.astype('int64')
        nodata_frames.append(df)

    if nodata_frames:
        pos_nodata = pd.concat(nodata_frames, axis=1)
    else:
        pos_nodata = pd.DataFrame(index=pos_clean.index)

    pos_df = (pd.concat([pos_clean, pos_nodata], axis=1)
                .reindex(columns=cont_vars.index))

    # ── Step 3: categorical class labels (from view) and IDs (from raw table) ─
    class_label_rows = {}
    class_id_rows    = {}

    for api_key, row in cat_vars.iterrows():
        db_col   = row['db_col']
        id_sql   = (f"SELECT hybas_id, {db_col} AS class_id "
                    f"FROM {table} WHERE hybas_id IN ({ids_clause})")
        id_series = (pd.read_sql(id_sql, conn)
                       .set_index('hybas_id')['class_id'])
        id_series.index = id_series.index.astype('int64')
        class_id_rows[api_key] = id_series

        if api_key in raw_df.columns:
            class_label_rows[api_key] = raw_df[api_key]

    class_label_df = pd.DataFrame(class_label_rows, index=raw_df.index)
    class_id_df    = pd.DataFrame(class_id_rows,    index=raw_df.index)

    # ── Step 4: flags (raw integer from view) ────────────────────────────────
    flag_cols = [k for k in flag_vars.index if k in raw_df.columns]
    flag_df   = raw_df[flag_cols].copy()

    # ── Step 5: assemble output matrix ───────────────────────────────────────
    var_cols  = [c for c in raw_df.columns if c != 'weight']
    matrix_df = (pd.concat([pos_df, class_label_df, flag_df], axis=1)
                   .reindex(columns=var_cols))

    return matrix_df, class_id_df, raw_df


# ── WO4: make_row, projector, assembler, Band T promotion ────────────────────

# Caveat texts live once here; rows carry only keys (Pin 2).
CAVEAT_TEXTS = {
    'lmr_caveat': (
        "Anomaly vs. 850–1850 CE CCSM4 reference frame; "
        "spatial structure reflects reanalysis prior. "
        "At buffer scale the collapsed value is essentially the prior at this location."
    ),
    'hyde_caveat': (
        "HYDE 3.4 cadence-transition artifact: 1950 is the last centennial/decadal "
        "epoch before annual data begins; value may not reflect real land-use change."
    ),
}

def make_row(
    variable, band, method, unit_type, n_units,
    representative_score, representative_raw, coverage, status,
    # quality flags (Pin 1, 4)
    coherence=None, modality=None, score_suppressed=False,
    distribution=None, weight_at_zero=None,
    caveat=None,          # Pin 2: list of caveat keys; empty list = no caveats
    # temporal fields (B7 only; None on basin-path rows)
    year=None, epoch_year=None,
    units=None,           # native unit label, for display
    detail=None,          # dict: method-specific distribution fields (unit-tagged)
) -> dict:
    """
    Build one complete row dict for any aggregation branch.

    Pin 1: status ∈ ok | outside_active_domain | no_data  (never old verdicts)
    Pin 2: caveat is always a list (empty, never null); text lives in CAVEAT_TEXTS
    Pin 4: score_suppressed=True when score is null because two_regime verdict makes
           a single number dishonest; score_suppressed=False + score=None means score
           is not applicable (Band T has no global-percentile ranking)

    Lean-vs-detail is a projection at serialization (project_row), not a branch here.
    make_row always returns the complete object.
    """
    return {
        # identity
        'variable':            variable,
        'band':                band,
        'method':              method,
        'unit_type':           unit_type,
        'n_units':             n_units,
        # headline
        'representative_score': representative_score,
        'representative_raw':   representative_raw,
        'score_suppressed':     score_suppressed,
        # coverage + status
        'coverage':            coverage,
        'status':              status,
        # quality flags
        'coherence':           coherence,
        'modality':            modality,
        'distribution':        distribution,
        'weight_at_zero':      weight_at_zero,
        'caveat':              caveat if caveat is not None else [],
        # temporal (None on non-B7 rows; serializer omits None fields as needed)
        'year':                year,
        'epoch_year':          epoch_year,
        'units':               units,
        # method-specific detail sub-block
        'detail':              detail if detail is not None else {},
    }


def project_row(row, include_detail=False) -> dict:
    """
    Project a complete make_row dict to lean or full form.

    Lean (default, &detail absent): every field except 'detail'.
    Full (&detail): same + the 'detail' sub-block.
    """
    out = {k: v for k, v in row.items() if k != 'detail'}
    if include_detail:
        out['detail'] = row.get('detail', {})
    return out


def assemble_payload(rows, neighborhood, shortfall, bands,
                     temporal=None, include_detail=False) -> dict:
    """
    Assemble the top-level Areas payload from a list of make_row dicts.

    Collects all caveat keys referenced by any row and emits the caveat text
    once at top level (Pin 2). Projects each row to lean or full form.

    Parameters
    ----------
    rows         : list of make_row dicts
    neighborhood : dict — resolved-query echo (type, params, n_units, unit_type)
    shortfall    : float — geographic absence fraction (open water / no basin)
    bands        : list of str — bands requested
    temporal     : dict or None — {from_year, to_year} if Band T was requested
    include_detail : bool — &detail projection flag
    """
    used_keys = set()
    for row in rows:
        used_keys.update(row.get('caveat', []))
    caveats = {k: CAVEAT_TEXTS[k] for k in sorted(used_keys) if k in CAVEAT_TEXTS}

    return {
        'neighborhood': neighborhood,
        'shortfall':    shortfall,
        'bands':        bands,
        'temporal':     temporal,
        'caveats':      caveats,
        'rows':         [project_row(r, include_detail) for r in rows],
    }


# ── Band T: promoted from step3b_band_t.ipynb, wired to make_row ─────────────

_LMR_RANGE            = (0,    1998)
_EVOLV_RANGE          = (-491, 1890)
_HYDE_1950_EPOCH_YEAR = 1950   # cadence-artifact epoch; triggers hyde_caveat


def _agg_hyde_b7(df, var_col, buf_area_m2):
    """Fractional-overlap-weighted mean + distribution for one HYDE variable.

    Weight = overlap_m2 / cell_area_m2 (fraction of each cell inside query area).
    Cells that are 10% inside contribute weight 0.1 regardless of their absolute size,
    so unequal cell areas (which vary with latitude) don't bias the mean.
    Coverage is reported as sum(overlap_m2) / buf_area_m2 (physical coverage).
    w_eff = sum of fractional coverages; honest effective-cell-count for detail block.
    """
    valid = df[df[var_col].notna()].copy()
    if len(valid) == 0:
        return {'representative_raw': None, 'p10': None, 'p90': None,
                'sd': None, 'n_units': 0, 'w_eff': 0.0,
                'coverage': 0.0, 'status': 'no_data', 'histogram': None}
    frac   = (valid['overlap_m2'] / (valid['area_km2'] * 1e6)).values
    w      = frac / frac.sum()
    v      = valid[var_col].values.astype(float)
    mean_  = float(np.dot(v, w))
    return {
        'representative_raw': mean_,
        'p10':      weighted_quantile(v, w, 0.1),
        'p90':      weighted_quantile(v, w, 0.9),
        'sd':       float(np.sqrt(np.dot(w, (v - mean_) ** 2))),
        'n_units':  len(valid),
        'w_eff':    round(float(frac.sum()), 2),
        'coverage': float(valid['overlap_m2'].sum()) / buf_area_m2,
        'status':   'ok',
        'histogram': _weighted_histogram(v, frac, unit_type='hyde_cell'),
    }


def _agg_lmr_b7(overlap_m2, values, buf_area_m2):
    """Area-weighted mean for one LMR variable (collapse path; scalar input)."""
    tot_w = float(overlap_m2.sum())
    w     = overlap_m2 / tot_w
    return {
        'representative_raw': float(np.dot(values, w)),
        'coverage':           tot_w / buf_area_m2,
        'status':             'ok',
    }


def aggregate_band_t(lat, lon, radius_km, from_year, to_year, conn,
                     geom_wkt=None, resolver_year=None):
    """
    Band T aggregator: HYDE (grid_areal_distribution) + LMR (grid_areal_collapsed) +
    eVolv2k (global_forcing) for a query area over a year span.

    Promoted from step3b_band_t.ipynb Cell 13; wired to make_row instead of _row.

    Changes vs. notebook aggregate_band_t:
    - lmr_caveat applied to every LMR row (missing from notebook's aggregate path)
    - hyde_caveat applied to HYDE rows where epoch_year == 1950
    - status uses Pin 1 vocabulary (no_data instead of no_events when eVolv2k absent)
    - coverage_weight renamed to coverage; p10/p90/sd moved to detail sub-block
    - WO15: HYDE and LMR weights changed from overlap_m2/sum(overlap_m2) to
      overlap_m2/cell_area_m2 (fractional coverage of each cell's own area), so cells
      at different latitudes are not biased by their absolute size. HYDE detail block
      gains w_eff (sum of fractional coverages; honest effective cell count).

    Parameters
    ----------
    lat, lon    : float — WGS-84 coordinates (buffer centre, or point within polygon)
    radius_km   : float — buffer radius in km; ignored when geom_wkt is provided
    from_year   : int   — start of span (CE)
    to_year     : int   — end of span (CE)
    conn        : psycopg3 connection
    geom_wkt    : str or None — WKT polygon to use instead of a circular buffer;
                  when provided, lat/lon/radius_km are not used for geometry

    Returns
    -------
    list of make_row dicts — pass to assemble_payload for the top-level payload
    """
    if geom_wkt is not None:
        buf_geom_sql = f"ST_GeomFromText('{geom_wkt}', 4326)"
        buf_geog_sql = f"({buf_geom_sql})::geography"
    else:
        radius_m     = radius_km * 1000.0
        pt_sql       = f"ST_SetSRID(ST_MakePoint({lon}, {lat}), 4326)"
        buf_geog_sql = f"ST_Buffer({pt_sql}::geography, {radius_m})"
        buf_geom_sql = f"({buf_geog_sql})::geometry"

    buf_area_m2 = float(
        conn.execute(f"SELECT ST_Area({buf_geog_sql})").fetchone()[0]
    )

    rows = []

    # ── HYDE ──────────────────────────────────────────────────────────────────
    # Spatial filter runs once (cell_overlaps CTE); CROSS JOIN with epochs
    # extracts the correct array element without re-scanning hyde_cells.
    hyde_sql = f"""
    WITH buf AS (SELECT {buf_geom_sql} AS buf_geom),
    epochs AS (
        SELECT step_idx, year_ce
        FROM temporal.hyde_times
        WHERE year_ce BETWEEN {from_year} AND {to_year}
    ),
    cell_overlaps AS (
        SELECT area_km2,
               ST_Area(ST_Intersection(hc.geom, buf.buf_geom)::geography) AS overlap_m2,
               cropland, grazing, pasture, rangeland
        FROM temporal.hyde_cells hc, buf
        WHERE ST_Intersects(hc.geom, buf.buf_geom)
    )
    SELECT
        e.year_ce, e.step_idx,
        co.area_km2, co.overlap_m2,
        co.cropland [e.step_idx + 1] AS cropland,
        co.grazing  [e.step_idx + 1] AS grazing,
        co.pasture  [e.step_idx + 1] AS pasture,
        co.rangeland[e.step_idx + 1] AS rangeland
    FROM cell_overlaps co CROSS JOIN epochs e
    WHERE co.overlap_m2 > 0
    ORDER BY e.year_ce
    """
    hyde_ts = pd.read_sql(hyde_sql, conn)

    for year_ce, grp in hyde_ts.groupby('year_ce', sort=True):
        yr     = int(year_ce)
        caveat = ['hyde_caveat'] if yr == _HYDE_1950_EPOCH_YEAR else []
        for var, units in [('cropland', 'km²'), ('grazing', 'km²'),
                           ('pasture',  'km²'), ('rangeland', 'km²')]:
            agg = _agg_hyde_b7(grp, var, buf_area_m2)
            hist_h = agg['histogram']
            if hist_h is not None:
                hist_h.update({
                    'resolver_year': resolver_year,
                    'band_t_from':   from_year,
                    'band_t_to':     to_year,
                })
            rows.append(make_row(
                variable=f'hyde_{var}', band='T',
                method='grid_areal_distribution',
                unit_type='hyde_cell', n_units=agg['n_units'],
                representative_score=None,
                representative_raw=agg['representative_raw'],
                coverage=agg['coverage'], status=agg['status'],
                caveat=caveat,
                year=yr, epoch_year=yr, units=units,
                detail={
                    'p10':          agg['p10'],
                    'p90':          agg['p90'],
                    'sd':           agg['sd'],
                    'w_eff':        agg['w_eff'],
                    'unit':         'km2_per_cell',
                    'distribution': hist_h,
                },
            ))

    # ── LMR ───────────────────────────────────────────────────────────────────
    # Array slices fetched once per footprint; expanded to annual rows in Python.
    lmr_from = max(_LMR_RANGE[0], from_year)
    lmr_to   = min(_LMR_RANGE[1], to_year)

    if lmr_from <= lmr_to:
        pg_from, pg_to = lmr_from + 1, lmr_to + 1
        lmr_sql = f"""
        WITH buf AS (SELECT {buf_geom_sql} AS buf_geom),
        footprints AS (
            SELECT
                lc.lat,
                CASE WHEN lc.lon > 180 THEN lc.lon - 360 ELSE lc.lon END AS lon_disp,
                lc.pdsi [{pg_from}:{pg_to}]  AS pdsi_slice,
                lc.air  [{pg_from}:{pg_to}]  AS air_slice,
                lc.prate[{pg_from}:{pg_to}]  AS prate_slice,
                ST_MakeEnvelope(
                    CASE WHEN lc.lon > 180 THEN lc.lon - 360 ELSE lc.lon END - 1,
                    lc.lat - 1,
                    CASE WHEN lc.lon > 180 THEN lc.lon - 360 ELSE lc.lon END + 1,
                    lc.lat + 1, 4326) AS fp
            FROM temporal.lmr_climate lc
        )
        SELECT f.pdsi_slice, f.air_slice, f.prate_slice,
               ST_Area(ST_Intersection(f.fp, buf.buf_geom)::geography) AS overlap_m2,
               ST_Area(f.fp::geography)                                 AS cell_area_m2
        FROM footprints f, buf
        WHERE ST_Intersects(f.fp, buf.buf_geom)
        ORDER BY overlap_m2 DESC
        """
        lmr_ts = pd.read_sql(lmr_sql, conn)

        ov      = lmr_ts['overlap_m2'].values.astype(float)
        ca      = lmr_ts['cell_area_m2'].values.astype(float)
        frac_l  = ov / ca
        w_lmr   = frac_l / frac_l.sum()
        cov_lmr = float(ov.sum() / buf_area_m2)
        n_fp    = len(lmr_ts)
        years_l = list(range(lmr_from, lmr_to + 1))

        pdsi_mat  = np.array(lmr_ts['pdsi_slice'].tolist(),  dtype=float)
        air_mat   = np.array(lmr_ts['air_slice'].tolist(),   dtype=float)
        prate_mat = np.array(lmr_ts['prate_slice'].tolist(), dtype=float) * 86400

        for i, year in enumerate(years_l):
            for api_name, mat, units in [
                ('pdsi',  pdsi_mat,  'dimensionless anomaly'),
                ('air',   air_mat,   'K anomaly'),
                ('prate', prate_mat, 'mm/day anomaly'),
            ]:
                col_vals = mat[:, i]
                hist_l   = _weighted_histogram(col_vals, frac_l, unit_type='lmr_cell')
                if hist_l is not None:
                    hist_l.update({
                        'resolver_year': resolver_year,
                        'band_t_from':   from_year,
                        'band_t_to':     to_year,
                    })
                rows.append(make_row(
                    variable=f'lmr_{api_name}', band='T',
                    method='grid_areal_distribution',
                    unit_type='lmr_cell', n_units=n_fp,
                    representative_score=None,
                    representative_raw=float(np.dot(col_vals, w_lmr)),
                    coverage=cov_lmr, status='ok',
                    caveat=['lmr_caveat'],
                    year=year, epoch_year=None, units=units,
                    detail={'distribution': hist_l},
                ))

    # ── eVolv2k ───────────────────────────────────────────────────────────────
    ev_from = max(_EVOLV_RANGE[0], from_year)
    ev_to   = min(_EVOLV_RANGE[1], to_year)

    if ev_from <= ev_to:
        events = pd.read_sql(f"""
            SELECT year_ad, vssi_tg
            FROM temporal.evolv2k_v4
            WHERE year_ad BETWEEN {ev_from} AND {ev_to}
            ORDER BY year_ad
        """, conn)
        for _, ev in events.iterrows():
            rows.append(make_row(
                variable='evolv2k_vssi', band='T',
                method='global_forcing',
                unit_type='global', n_units=1,
                representative_score=None,
                representative_raw=float(ev['vssi_tg']),
                coverage=None, status='ok',
                year=int(ev['year_ad']), epoch_year=None, units='Tg S',
            ))

    return rows


_BLOCK1_CLUSTERS = frozenset({'continental-gradient', 'scale-dependent'})


# ── WO3: dispatch ─────────────────────────────────────────────────────────────


def dispatch_variable(typology_cluster, kind):
    """
    Route a variable to its primary aggregation block.

    Parameters
    ----------
    typology_cluster : str or None/NaN — from meta_df['typology_cluster']
    kind             : str             — 'continuous', 'categorical', or 'flag'

    Returns
    -------
    str: one of 'B1', 'B2', 'B3', 'B4', 'B5', or 'unknown'

    Routing rules (typology_cluster is the governing axis; kind breaks ties
    for NaN-cluster variables):

        categorical  (any cluster)                        → B3  class_mixture
        flag         (any cluster)                        → B4  flag / structural
        continuous + {continental-gradient, scale-dependent} → B1  area_weighted
        continuous + network-topology                     → B2  dominant_basin
        continuous + NaN cluster                          → B5  distribution_only
        continuous + local-anomaly                        → B5  extreme

    Dropped from WO3 proposed signature:
        zero_fraction — confirmed NOT a routing input; only affects scoring within
        B1 (zero-aware PARTITION variant vs standard PERCENT_RANK). Twelve zero-
        inflated B1 vars all route to area_weighted, confirming the drop.

    Block-internal exclusions NOT handled here (by design — locked principle):
        strata_code          dispatched → B3 but excluded within B3 (opaque codes)
        ecoregion            dispatched → B3 but deduped within B3 (same col as eco_id)
        river_area_upstream  dispatched → B5 but deferred within B5 (EXTREME_VARS
                             hardcoded to ['river_area'] only in step3 Cell 21)
        endorheic/coast_flag dispatched → B4 but produce synthetic outputs (outlet_type
                             via class_mixture, coast_fraction via flag_fraction);
                             neither appears standalone in step3_results.tsv

    Band T (HYDE / LMR / eVolv2k) is a separate notebook path (step3b); none of those
    variables appear in step2_meta.tsv, so dispatch_variable never sees them.

    B6 (modality) is not a dispatch target — it is a post-B1/B5 refinement.
    """
    if kind == 'categorical':
        return 'B3'
    if kind == 'flag':
        return 'B4'
    # kind == 'continuous' from here
    tc = typology_cluster
    if pd.isna(tc) if isinstance(tc, float) else tc is None:
        return 'B5'
    if tc in ('continental-gradient', 'scale-dependent'):
        return 'B1'
    if tc == 'network-topology':
        return 'B2'
    if tc == 'local-anomaly':
        return 'B5'
    return 'unknown'


# ── WO5: B2 dominant_basin ────────────────────────────────────────────────────


def aggregate_b2(basin_set, matrix_df, raw_df, meta_df) -> list:
    """
    Block 2: network-topology dominant-basin aggregation.

    Discharge is cumulative — each basin already integrates upstream flow.
    Dominant river = basin with highest annual discharge (discharge_yr) in the
    buffer set. All three network-topology variables read from that one basin.

    n_units is the full buffer-set size (not 1): the dominant basin was *selected
    from* the full set; see WO5 report for the contract-tension note.

    discharge_min > 0 → perennial stored as detail['perennial'] on the
    discharge_min row (engine enrichment; not present in the frozen step3 TSV).

    Parameters
    ----------
    basin_set  : DataFrame — hybas_id as index (or column), weight column
    matrix_df  : DataFrame — hybas_id as index; continuous position scores
    raw_df     : DataFrame — hybas_id as index; weight + raw values from view
    meta_df    : DataFrame — api_key as index; columns include band,
                             typology_cluster, kind

    Returns
    -------
    list of make_row dicts — one per network-topology variable
    """
    if 'hybas_id' in basin_set.columns:
        basin_set = basin_set.set_index('hybas_id')
    basin_set.index = basin_set.index.astype('int64')

    nt_vars     = meta_df[meta_df['typology_cluster'] == 'network-topology']
    dominant_id = int(raw_df['discharge_yr'].idxmax())
    n_total     = len(raw_df)

    rows = []
    for api_key, vrow in nt_vars.iterrows():
        score   = round(float(matrix_df.loc[dominant_id, api_key]), 2)
        raw_val = round(float(raw_df.loc[dominant_id, api_key]),    3)
        band    = str(vrow.get('band', 'B'))

        detail = {'dominant_hybas_id': dominant_id}
        if api_key == 'discharge_min':
            detail['perennial'] = bool(raw_val > 0)

        rows.append(make_row(
            variable=api_key, band=band,
            method='dominant_basin',
            unit_type='basin', n_units=n_total,
            representative_score=score,
            representative_raw=raw_val,
            coverage=1.0, status='ok',
            units='m³/s',
            detail=detail,
        ))

    return rows


# ── WO7: B3 class_mixture ─────────────────────────────────────────────────────

# Categoricals excluded from B3: strata_code (opaque codes, see register) and
# ecoregion (deduped into eco_id — same db_col; eco_id row wins).
_B3_EXCLUDE = frozenset({'strata_code', 'ecoregion'})

# eco_id's integer column and text label column have different names in the view.
# matrix_df['eco_id'] contains integers (the view's eco_id col);
# matrix_df['ecoregion'] contains the human-readable text.
# For all other categoricals label col == api_key.
_B3_LABEL_COL = {'eco_id': 'ecoregion'}


def aggregate_b3(basin_set, matrix_df, class_id_df, meta_df,
                 plurality_threshold=0.85,
                 min_share_epsilon=1e-6,
                 low_coverage_floor=0.50) -> list:
    """
    Block 3: categorical class-mixture aggregation.

    For each categorical variable (9 vars, excluding strata_code and ecoregion):
      - class IDs come from class_id_df (integers from raw table via db_col)
      - text labels come from matrix_df (view text column; eco_id uses 'ecoregion' col)
      - NoData = class_id with no known text label; those basins drop out
      - surviving weights renormalized within the valid set → proportions per class
      - coherence: 'concentrated' if modal_share >= plurality_threshold, else 'mixed'
      - detail carries modal summary + full per-class mixture with labels

    representative_raw is always None — modal label lives in detail, not the lean row.
    n_units = valid-data basin count for that variable (not necessarily the full set).
    coverage = sum of weights over valid-data basins (unnormalized buffer fraction).

    Parameters
    ----------
    basin_set    : DataFrame — hybas_id as index (or column), weight column
    matrix_df    : DataFrame — hybas_id as index; categorical text labels (and eco_id ints)
    class_id_df  : DataFrame — hybas_id as index; integer class IDs per categorical var
    meta_df      : DataFrame — api_key as index; columns include band, kind

    Returns
    -------
    list of make_row dicts — one per B3 variable, in meta_df order
    """
    if 'hybas_id' in basin_set.columns:
        basin_set = basin_set.set_index('hybas_id')
    basin_set.index = basin_set.index.astype('int64')
    class_id_df = class_id_df.copy()
    class_id_df.index = class_id_df.index.astype('int64')
    matrix_df = matrix_df.copy()
    matrix_df.index = matrix_df.index.astype('int64')

    b3_meta = meta_df[
        (meta_df['kind'] == 'categorical') &
        (~meta_df.index.isin(_B3_EXCLUDE))
    ]
    b3_vars = [v for v in b3_meta.index if v in class_id_df.columns]

    # Build label_map: api_key → {class_id(int): label(str)}
    label_map = {}
    for var in b3_vars:
        label_col = _B3_LABEL_COL.get(var, var)
        if label_col not in matrix_df.columns:
            label_map[var] = {}
            continue
        ids    = class_id_df[var]
        labels = matrix_df[label_col]
        pairs  = pd.concat([ids, labels], axis=1)
        pairs.columns = ['class_id', 'label']
        valid = pairs.dropna(subset=['label'])
        valid = valid[valid['label'].apply(lambda x: isinstance(x, str))]
        label_map[var] = {int(r['class_id']): r['label']
                          for _, r in valid.iterrows()}

    joined = basin_set[['weight']].join(class_id_df[b3_vars], how='inner')

    rows = []
    for var in b3_vars:
        band = str(b3_meta.loc[var, 'band'])
        col  = joined[var]
        w    = joined['weight']

        valid_ids  = set(label_map.get(var, {}).keys())
        mask       = col.isin(valid_ids)
        surviving_w = w[mask]
        cov_weight  = float(surviving_w.sum())
        n_basins    = int(mask.sum())

        if cov_weight < 1e-9:
            rows.append(make_row(
                variable=var, band=band,
                method='class_mixture', unit_type='basin', n_units=0,
                representative_score=None, representative_raw=None,
                coverage=0.0, status='no_data', coherence=None,
                detail={'modal_class_id': None, 'modal_label': None,
                        'modal_share': None, 'n_classes': 0,
                        'concentration': None, 'mixture': []},
            ))
            continue

        status_val = 'low_coverage' if cov_weight < low_coverage_floor else 'ok'

        w_norm = surviving_w / cov_weight
        ids    = col[mask].astype(int)

        props = (pd.DataFrame({'class_id': ids.values, 'w': w_norm.values})
                 .groupby('class_id')['w'].sum()
                 .reset_index()
                 .rename(columns={'w': 'proportion'}))
        props = props[props['proportion'] >= min_share_epsilon].copy()
        props['label'] = props['class_id'].map(label_map[var])
        props = props.sort_values('proportion', ascending=False).reset_index(drop=True)

        modal       = props.iloc[0]
        n_classes   = len(props)
        hhi         = float((props['proportion'] ** 2).sum())
        modal_share = round(float(modal['proportion']), 4)
        coherence   = 'concentrated' if modal_share >= plurality_threshold else 'mixed'

        modal_label = str(modal['label'])

        mixture = [
            {'class_id':    int(r['class_id']),
             'class_label': str(r['label']),
             'weight':      round(float(r['proportion']), 6)}
            for _, r in props.iterrows()
        ]

        rows.append(make_row(
            variable=var, band=band,
            method='class_mixture', unit_type='basin', n_units=n_basins,
            representative_score=None,
            representative_raw=modal_label,
            coverage=round(cov_weight, 4),
            status=status_val, coherence=coherence,
            detail={
                'modal_class_id': int(modal['class_id']),
                'modal_share':    modal_share,
                'n_classes':      n_classes,
                'concentration':  round(hhi, 4),
                'mixture':        mixture,
            },
        ))

    return rows


# ── WO8: B4 flag / structural ─────────────────────────────────────────────────

_OUTLET_TYPE_LABELS = {
     0: 'Exorheic, non-coastal',
     1: 'Exorheic, coastal',
    10: 'Endorheic (drains to inland sink)',
    20: 'Terminal sink basin',
}


def aggregate_b4(basin_set, raw_df,
                 plurality_threshold=0.85,
                 min_share_epsilon=1e-6) -> list:
    """
    Block 4: flag/structural aggregation.

    Synthesizes two outputs from the raw endorheic (0/1/2) and coast_flag (0/1)
    fields; neither input is emitted as a standalone row.

    outlet_type  — method='class_mixture'; per-basin class = endo*10 + coast:
                   0=Exorheic non-coastal, 1=Exorheic coastal,
                   10=Endorheic (inland sink), 20=Terminal sink.
                   Exclusivity invariant asserted: coast=1 never co-occurs with endo>0.
                   representative_raw = modal class label (WO7b convention).
                   coherence: concentrated|mixed by plurality_threshold.

    coast_fraction — method='flag_fraction'; area-weighted fraction of basins with
                     coast_flag=1. representative_raw = the fraction (0.0–1.0).
                     coherence=None (scalar; no concentrated/mixed concept applies).

    Parameters
    ----------
    basin_set  : DataFrame — hybas_id as index (or column), weight column
    raw_df     : DataFrame — hybas_id as index; must contain endorheic, coast_flag,
                             and weight columns

    Returns
    -------
    list of two make_row dicts: [outlet_type_row, coast_fraction_row]
    """
    if 'hybas_id' in basin_set.columns:
        basin_set = basin_set.set_index('hybas_id')
    basin_set.index = basin_set.index.astype('int64')
    raw_df = raw_df.copy()
    raw_df.index = raw_df.index.astype('int64')

    w     = basin_set['weight']
    endo  = raw_df.loc[w.index, 'endorheic'].astype(int)
    coast = raw_df.loc[w.index, 'coast_flag'].astype(int)

    bad = ((coast == 1) & (endo >= 1)).sum()
    assert bad == 0, f'Exclusivity violated: {bad} basin(s) with coast=1 & endo>=1'

    ot_id = endo * 10 + coast

    # ── outlet_type class_mixture ──
    props = (pd.DataFrame({'class_id': ot_id.values, 'w': w.values})
             .groupby('class_id')['w'].sum()
             .reset_index()
             .rename(columns={'w': 'proportion'}))
    props = props[props['proportion'] >= min_share_epsilon].copy()
    props['label'] = props['class_id'].map(_OUTLET_TYPE_LABELS)
    props = props.sort_values('proportion', ascending=False).reset_index(drop=True)

    modal       = props.iloc[0]
    modal_share = round(float(modal['proportion']), 4)
    n_classes   = len(props)
    hhi         = round(float((props['proportion'] ** 2).sum()), 4)
    coherence   = 'concentrated' if modal_share >= plurality_threshold else 'mixed'
    cov_weight  = round(float(w.sum()), 4)

    mixture = [
        {'class_id':    int(r['class_id']),
         'class_label': str(r['label']),
         'weight':      round(float(r['proportion']), 6)}
        for _, r in props.iterrows()
    ]

    ot_row = make_row(
        variable='outlet_type', band='E',
        method='class_mixture', unit_type='basin', n_units=len(w),
        representative_score=None,
        representative_raw=str(modal['label']),
        coverage=cov_weight, status='ok', coherence=coherence,
        detail={
            'modal_class_id': int(modal['class_id']),
            'modal_share':    modal_share,
            'n_classes':      n_classes,
            'concentration':  hhi,
            'mixture':        mixture,
        },
    )

    # ── coast_fraction flag_fraction ──
    coast_frac = round(float((coast * w).sum()), 6)

    cf_row = make_row(
        variable='coast_fraction', band='E',
        method='flag_fraction', unit_type='basin', n_units=len(w),
        representative_score=None,
        representative_raw=coast_frac,
        coverage=cov_weight, status='ok', coherence=None,
    )

    return [ot_row, cf_row]


# ── WO9: B5 fallback + extreme ────────────────────────────────────────────────

# Only river_area takes the extreme path; river_area_upstream is deferred (register).
_B5_EXTREME_VARS    = frozenset({'river_area'})
_SPREAD_THRESHOLD   = 20.0  # concentrated if (p90-p10) < T — provisional; shared by B1 + B5


def aggregate_b5(basin_set, matrix_df, raw_df, meta_df):
    """
    Block 5: fallback aggregation — two sub-paths.

    distribution_only — untyped continuous variables (typology_cluster is NaN):
      Surfaces the weighted distribution without rendering a verdict.
      representative_score = weighted mean percentile (always populated).
      representative_raw   = None (native-unit means deferred per register).
      coherence            = 'concentrated' if spread < _SPREAD_THRESHOLD else 'spread'.
      detail               = {spread, p10, p90, unit: 'percentile'}.
      status               = 'ok' (the fallback's untyped-ness is carried by
                             method='distribution_only', not status; Pin 1
                             vocabulary is {ok, outside_active_domain, no_data}).

    extreme — local-anomaly variable (river_area only; river_area_upstream deferred):
      Selects the basin carrying the maximum score (monotone with raw value).
      representative_score = carrier basin's percentile score.
      representative_raw   = carrier basin's raw value (km²).
      coherence            = None.
      detail               = {dominant_hybas_id}.
      status               = 'ok'.

    Companion rows (second return value): one row per {variable, basin} for
    distribution_only variables — the full weighted distribution so any quantile
    is recoverable downstream.

    Parameters
    ----------
    basin_set  : DataFrame — hybas_id as index (or column), weight column
    matrix_df  : DataFrame — hybas_id as index; continuous position scores
    raw_df     : DataFrame — hybas_id as index; raw values including river_area
    meta_df    : DataFrame — api_key as index; columns include band, kind,
                             typology_cluster

    Returns
    -------
    (rows, companion_rows) where:
      rows          : list of make_row dicts
      companion_rows: list of {variable, hybas_id, weight, score} dicts
                      (one per basin for each distribution_only variable)
    """
    if 'hybas_id' in basin_set.columns:
        basin_set = basin_set.set_index('hybas_id')
    basin_set.index = basin_set.index.astype('int64')
    matrix_df = matrix_df.copy()
    matrix_df.index = matrix_df.index.astype('int64')
    raw_df = raw_df.copy()
    raw_df.index = raw_df.index.astype('int64')

    joined = basin_set[['weight']].join(matrix_df, how='inner')

    untyped_meta = meta_df[
        (meta_df['kind'] == 'continuous') &
        meta_df['typology_cluster'].isna()
    ]
    untyped_vars = [v for v in untyped_meta.index if v in joined.columns]

    extreme_meta = meta_df[meta_df['typology_cluster'] == 'local-anomaly']
    extreme_vars = [v for v in _B5_EXTREME_VARS
                    if v in joined.columns and v in extreme_meta.index]

    rows           = []
    companion_rows = []

    # ── distribution_only ──
    for var in untyped_vars:
        band = str(untyped_meta.loc[var, 'band'])
        col  = pd.to_numeric(joined[var], errors='coerce')
        w    = joined['weight']
        mask = col.notna()

        scores = col[mask].values.astype(float)
        wts    = w[mask].values.astype(float)
        n      = int(mask.sum())
        cov    = float(wts.sum())

        if n == 0 or cov == 0:
            rows.append(make_row(
                variable=var, band=band,
                method='distribution_only', unit_type='basin', n_units=n,
                representative_score=None, representative_raw=None,
                coverage=0.0, status='no_data', coherence=None,
            ))
            continue

        wts_norm = wts / cov
        wmean    = round(float(np.dot(scores, wts_norm)), 2)
        p10_raw  = weighted_quantile(scores, wts_norm, 0.10)
        p90_raw  = weighted_quantile(scores, wts_norm, 0.90)
        spread   = round(p90_raw - p10_raw, 2)
        p10      = round(p10_raw, 2)
        p90      = round(p90_raw, 2)

        coherence = 'concentrated' if spread < _SPREAD_THRESHOLD else 'spread'
        rows.append(make_row(
            variable=var, band=band,
            method='distribution_only', unit_type='basin', n_units=n,
            representative_score=wmean, representative_raw=None,
            coverage=round(cov, 4), status='ok', coherence=coherence,
            detail={'spread': spread, 'p10': p10, 'p90': p90, 'unit': 'percentile'},
        ))

        for hid, score, wt in zip(joined.index[mask], scores, w[mask].values):
            companion_rows.append({
                'variable': var,
                'hybas_id': int(hid),
                'weight':   round(float(wt), 6),
                'score':    round(float(score), 4),
            })

    # ── extreme ──
    for var in extreme_vars:
        band = str(extreme_meta.loc[var, 'band'])
        col  = pd.to_numeric(joined[var], errors='coerce')
        w    = joined['weight']
        mask = col.notna()
        n    = int(mask.sum())
        cov  = float(w[mask].sum())

        if n == 0:
            rows.append(make_row(
                variable=var, band=band,
                method='extreme', unit_type='basin', n_units=n,
                representative_score=None, representative_raw=None,
                coverage=0.0, status='no_data', coherence=None,
            ))
            continue

        carrier_id    = int(col.idxmax())
        carrier_score = round(float(col.loc[carrier_id]), 2)
        carrier_raw   = (round(float(raw_df.loc[carrier_id, var]), 3)
                         if var in raw_df.columns else None)

        rows.append(make_row(
            variable=var, band=band,
            method='extreme', unit_type='basin', n_units=n,
            representative_score=carrier_score,
            representative_raw=carrier_raw,
            coverage=round(cov, 4), status='ok', coherence=None,
            detail={'dominant_hybas_id': carrier_id},
        ))

    return rows, companion_rows


# ── WO10: B6 modality post-pass ───────────────────────────────────────────────

_MODALITY_GAP      = 0.50   # gap threshold as fraction of spread — provisional
_MIN_REGIME_WEIGHT = 0.20   # minimum weight on each side to count as a regime


def detect_modality(scores, weights_norm, spread,
                    modality_gap=_MODALITY_GAP,
                    min_regime_weight=_MIN_REGIME_WEIGHT):
    """
    Detect unimodal vs two_regime distribution.

    De-closured from step3 Cell 27 detect_modality.  Consumes only what it
    computes; the notebook's endorheic_set is used for seam-alignment reporting
    only (not detection) and is therefore not reproduced here.

    Parameters
    ----------
    scores, weights_norm : np.array — notna-filtered; weights_norm sums to 1
    spread               : float — p90 - p10 (precomputed)

    Returns
    -------
    (modality, evidence)
      modality : 'two_regime' | 'unimodal'
      evidence : dict or None
        keys: gap_size, threshold, split_between,
              left_weight, right_weight, left_center, right_center,
              n_left, n_right
    """
    if len(scores) < 2 or spread == 0.0:
        return 'unimodal', None

    idx      = np.argsort(scores)
    s_sorted = scores[idx]
    w_sorted = weights_norm[idx]

    threshold = modality_gap * spread
    best      = None
    best_gap  = 0.0

    for i in range(len(s_sorted) - 1):
        gap = float(s_sorted[i + 1] - s_sorted[i])
        if gap > threshold:
            lw = float(w_sorted[:i + 1].sum())
            rw = float(w_sorted[i + 1:].sum())
            if lw >= min_regime_weight and rw >= min_regime_weight and gap > best_gap:
                best_gap = gap
                lc = float(np.dot(s_sorted[:i + 1],     w_sorted[:i + 1]     / lw))
                rc = float(np.dot(s_sorted[i + 1:],     w_sorted[i + 1:]     / rw))
                best = {
                    'gap_size':      round(gap, 2),
                    'threshold':     round(threshold, 2),
                    'split_between': (round(float(s_sorted[i]),     2),
                                      round(float(s_sorted[i + 1]), 2)),
                    'left_weight':   round(lw, 4),
                    'right_weight':  round(rw, 4),
                    'left_center':   round(lc, 2),
                    'right_center':  round(rc, 2),
                    'n_left':        i + 1,
                    'n_right':       len(s_sorted) - i - 1,
                }

    if best is not None:
        return 'two_regime', best
    return 'unimodal', None


def apply_modality(rows, basin_set, matrix_df,
                   modality_gap=_MODALITY_GAP,
                   min_regime_weight=_MIN_REGIME_WEIGHT):
    """
    B6 post-pass: overlay modality detection on distribution-bearing rows.

    Runs after B1 (area_weighted) and B5 (distribution_only).  Mutates each row
    dict in-place; returns the same list plus the regimes companion table.

    Determination (WO10):
    - modality ∈ {unimodal, two_regime} on every distribution-bearing row
      (never null — B6 always renders a verdict for continuous rows it covers)
    - score_suppressed=True ONLY when B6 is the reason the score is null
      (concentrated row that turned out to be two_regime); not set for spread
      rows that are also two_regime (score was already null for spread)
    - suppressed value preserved in detail['suppressed_score'] (not discarded)
    - endorheic_set: seam-alignment reporting only in the notebook; not reproduced

    Parameters
    ----------
    rows      : list of make_row dicts from B1 + B5
    basin_set : DataFrame — hybas_id as index (or column), weight column
    matrix_df : DataFrame — hybas_id as index; percentile score columns

    Returns
    -------
    (rows, regimes_companion) where regimes_companion is a list of dicts:
      {variable, regime_id, regime_center, regime_weight, n_basins, coverage_weight}
    """
    if 'hybas_id' in basin_set.columns:
        basin_set = basin_set.set_index('hybas_id')
    basin_set.index = basin_set.index.astype('int64')
    matrix_df = matrix_df.copy()
    matrix_df.index = matrix_df.index.astype('int64')

    joined = basin_set[['weight']].join(matrix_df, how='inner')

    regimes_companion = []

    for row in rows:
        var    = row['variable']
        spread = float(row.get('detail', {}).get('spread') or 0.0)

        if var not in joined.columns or spread == 0.0:
            row['modality'] = 'unimodal'
            continue

        col  = pd.to_numeric(joined[var], errors='coerce')
        w    = joined['weight']
        mask = col.notna()
        n    = int(mask.sum())

        if n < 2:
            row['modality'] = 'unimodal'
            continue

        scores = col[mask].values.astype(float)
        wts    = w[mask].values.astype(float)
        cov    = float(wts.sum())
        if cov == 0.0:
            row['modality'] = 'unimodal'
            continue
        wts_norm = wts / cov

        modality, evidence = detect_modality(
            scores, wts_norm, spread,
            modality_gap=modality_gap,
            min_regime_weight=min_regime_weight,
        )
        row['modality'] = modality

        if modality == 'two_regime' and evidence is not None:
            # Suppressed-score: only when B6 is the reason (was concentrated)
            if row.get('representative_score') is not None:
                row['detail']['suppressed_score'] = row['representative_score']
                row['representative_score']        = None
                row['score_suppressed']            = True

            # Regime breakdown in detail (bounded spatial expansion, §6)
            row['detail']['regimes'] = [
                {'id': 0, 'center': evidence['left_center'],
                 'weight': evidence['left_weight']},
                {'id': 1, 'center': evidence['right_center'],
                 'weight': evidence['right_weight']},
            ]

            # Companion table
            cov_weight = float(row.get('coverage', 1.0))
            for regime_id, center_key, weight_key, n_key in [
                    (0, 'left_center',  'left_weight',  'n_left'),
                    (1, 'right_center', 'right_weight', 'n_right')]:
                regimes_companion.append({
                    'variable':        var,
                    'regime_id':       regime_id,
                    'regime_center':   evidence[center_key],
                    'regime_weight':   evidence[weight_key],
                    'n_basins':        evidence[n_key],
                    'coverage_weight': cov_weight,
                })

    return rows, regimes_companion


# ── WO6: B1 area_weighted ─────────────────────────────────────────────────────


def aggregate_b1(basin_set, matrix_df, meta_df,
                 spread_threshold=_SPREAD_THRESHOLD,
                 zero_fraction_threshold=0.20,
                 zero_coverage_threshold=0.90,
                 resolver_year=None) -> list:
    """
    Block 1: area-weighted coherence aggregation for continental-gradient and
    scale-dependent continuous variables.

    For each variable:
      - weight = basin_set weight (fraction of buffer area)
      - scores = global-percentile scores from matrix_df
      - null scores dropped; surviving weights renormalized → coverage
      - weight_at_zero = fraction of total buffer weight at score 0.0
      - coherence: 'concentrated' if weighted (p90-p10) < T, else 'spread'
      - outside_active_domain guard: if zero_fraction >= threshold AND
        weight_at_zero >= zero_coverage_threshold

    representative_raw is always None — native-unit means are deferred.

    B1 emits all rows with non-null score for 'concentrated' rows, including
    those the frozen step3 TSV marks two_regime. Those rows are correct B6
    inputs; B6 (WO10) owns the score-nulling and modality field. This function
    does NOT interact with B6 — it is the first pass only.

    Parameters
    ----------
    basin_set  : DataFrame — hybas_id as index (or column), weight column
    matrix_df  : DataFrame — hybas_id as index; continuous position scores
    meta_df    : DataFrame — api_key as index; columns include band,
                             typology_cluster, kind, zero_fraction
    spread_threshold       : float — T; coherence boundary (default 20.0, provisional)
    zero_fraction_threshold: float — catalog threshold for zero-aware vars (default 0.20)
    zero_coverage_threshold: float — outside_active_domain guard (default 0.90)

    Returns
    -------
    list of make_row dicts — one per B1 variable, in meta_df order
    """
    if 'hybas_id' in basin_set.columns:
        basin_set = basin_set.set_index('hybas_id')
    basin_set.index = basin_set.index.astype('int64')
    matrix_df = matrix_df.copy()
    matrix_df.index = matrix_df.index.astype('int64')

    joined = basin_set[['weight']].join(matrix_df, how='inner')

    b1_meta     = meta_df[
        (meta_df['kind'] == 'continuous') &
        (meta_df['typology_cluster'].isin(_BLOCK1_CLUSTERS))
    ]
    block1_vars = [v for v in b1_meta.index if v in joined.columns]

    rows = []
    for api_key in block1_vars:
        col  = pd.to_numeric(joined[api_key], errors='coerce')
        w    = joined['weight']
        mask = col.notna()

        scores = col[mask].values.astype(float)
        wts    = w[mask].values.astype(float)

        n        = int(mask.sum())
        coverage = float(wts.sum())

        band = str(b1_meta.loc[api_key, 'band'])
        zf   = _parse_zf(b1_meta.loc[api_key].get('zero_fraction'))

        if n == 0 or coverage == 0:
            rows.append(make_row(
                variable=api_key, band=band,
                method='area_weighted', unit_type='basin', n_units=n,
                representative_score=None, representative_raw=None,
                coverage=0.0, status='no_data',
            ))
            continue

        wts_norm       = wts / coverage
        weight_at_zero = round(float(wts[scores == 0.0].sum()), 4)

        wmean   = round(float(np.dot(scores, wts_norm)), 2)
        p10_raw = weighted_quantile(scores, wts_norm, 0.10)
        p90_raw = weighted_quantile(scores, wts_norm, 0.90)
        spread  = round(p90_raw - p10_raw, 2)   # from unrounded values, matching notebook
        p10     = round(p10_raw, 2)
        p90     = round(p90_raw, 2)

        if (zf is not None
                and zf >= zero_fraction_threshold
                and weight_at_zero >= zero_coverage_threshold):
            status_val = 'outside_active_domain'
            coherence  = None
            rep_score  = None
        elif spread < spread_threshold:
            status_val = 'ok'
            coherence  = 'concentrated'
            rep_score  = wmean
        else:
            status_val = 'ok'
            coherence  = 'spread'
            rep_score  = wmean

        hist_b = _weighted_histogram(scores, wts, unit_type='basin')
        if hist_b is not None:
            hist_b.update({
                'resolver_year': resolver_year,
                'band_t_from':   None,
                'band_t_to':     None,
            })
        rows.append(make_row(
            variable=api_key, band=band,
            method='area_weighted',
            unit_type='basin', n_units=n,
            representative_score=rep_score,
            representative_raw=None,
            coverage=round(coverage, 4),
            status=status_val,
            coherence=coherence,
            weight_at_zero=weight_at_zero,
            detail={
                'spread':       spread,
                'p10':          p10,
                'p90':          p90,
                'unit':         'percentile',
                'distribution': hist_b,
            },
        ))

    return rows


# ── WO11b: assembly ───────────────────────────────────────────────────────────

def _areal_signature_from_basin_set(
    basin_set, level, conn,
    *,
    neighborhood,
    shortfall,
    geom_wkt=None,
    lat=None,
    lon=None,
    radius_km=None,
    bands=None,
    from_year=None,
    to_year=None,
    include_detail=False,
    run_modality=True,
    resolver_year=None,
):
    """
    Shared aggregation pipeline for any resolver that produces a weighted basin set.

    Callers handle their own resolver step and neighborhood dict, then delegate
    here. The B1–B6 + Band T path is identical across all neighborhood types.

    For Band T: pass geom_wkt when the query area is a fixed polygon (basin or
    polity). Pass lat/lon/radius_km when it is a circular buffer.
    """
    if level not in _CATALOG_CACHE:
        _CATALOG_CACHE[level] = load_catalog(level=level)
    meta_df = _CATALOG_CACHE[level]
    table   = _LEVEL_TABLE[level]
    view    = _LEVEL_VIEW[level]

    # ── 2. Attach values ─────────────────────────────────────────────────────
    matrix_df, class_id_df, raw_df = attach_values(
        basin_set, meta_df, conn, table, view,
    )

    # ── 3. Basin path: B1–B5 ─────────────────────────────────────────────────
    b1_rows = aggregate_b1(basin_set, matrix_df, meta_df, resolver_year=resolver_year)
    b2_rows = aggregate_b2(basin_set, matrix_df, raw_df, meta_df)
    b3_rows = aggregate_b3(basin_set, matrix_df, class_id_df, meta_df)
    b4_rows = aggregate_b4(basin_set, raw_df)
    b5_rows, _ = aggregate_b5(basin_set, matrix_df, raw_df, meta_df)

    # ── 4. B6 modality post-pass (B1 + B5 distribution rows only) ────────────
    if run_modality:
        apply_modality(b1_rows + b5_rows, basin_set, matrix_df)

    basin_rows = b1_rows + b2_rows + b3_rows + b4_rows + b5_rows

    # ── 5. Band T path (gated on span presence) ───────────────────────────────
    want_t    = (bands is None or 'T' in bands)
    have_span = from_year is not None and to_year is not None
    run_t     = want_t and have_span

    t_rows = aggregate_band_t(
        lat, lon, radius_km, from_year, to_year, conn,
        geom_wkt=geom_wkt, resolver_year=resolver_year,
    ) if run_t else []

    all_rows = basin_rows + t_rows

    # ── 6. Assemble payload ───────────────────────────────────────────────────
    active_bands = bands if bands is not None else _BASIN_BANDS + (['T'] if run_t else [])
    temporal     = {'from_year': from_year, 'to_year': to_year} if run_t else None

    return assemble_payload(
        all_rows, neighborhood, shortfall,
        bands=active_bands,
        temporal=temporal,
        include_detail=include_detail,
    )


_CATALOG_CACHE = {}   # level (int) → meta_df; populated lazily on first call

_LEVEL_TABLE = {6: 'public.basin06',               8: 'public.basin08'}
_LEVEL_VIEW  = {6: 'public.v_basin06_persist_rev1', 8: 'public.v_basin08_persist_rev1'}
_BASIN_BANDS = list('ABCDE')


def areal_signature(
    lat, lon, radius_km,
    conn,
    level=6,
    bands=None,
    from_year=None,
    to_year=None,
    include_detail=False,
):
    """
    Full areal signature for a buffer neighborhood.

    Build-once catalog is loaded lazily per level on first call and cached.

    Per-query pipeline
    ------------------
    1. resolve_buffer      → weighted basin set
    2. attach_values       → matrix_df, class_id_df, raw_df
    3. B1–B5 blocks        → basin-path rows (51 for Timbuktu)
    4. apply_modality      → B6 post-pass on B1+B5 distribution rows (in-place)
    5. aggregate_band_t    → Band T rows (gated: bands contains 'T' and span given)
    6. assemble_payload    → contract-shaped payload

    Parameters
    ----------
    lat, lon       : float — WGS-84 query point
    radius_km      : float — buffer radius
    conn           : psycopg3 connection
    level          : int   — 6 or 8
    bands          : list[str] or None — band letters to include; None = all
                     ('A'–'E' always; 'T' only when from_year+to_year are given)
    from_year      : int or None — Band T span start (CE)
    to_year        : int or None — Band T span end (CE)
    include_detail : bool — include detail sub-block in projected rows

    Returns
    -------
    dict — assemble_payload output:
        {neighborhood, shortfall, bands, temporal, caveats, rows}
    """
    # ── 1. Resolve buffer ────────────────────────────────────────────────────
    level_str = f'{level:02d}'
    basin_set = resolve_buffer(lat, lon, radius_km, level_str, conn)
    shortfall = round(1.0 - float(basin_set['weight'].sum()), 6)

    neighborhood = {
        'type':      'buffer',
        'lat':       lat,
        'lon':       lon,
        'radius_km': radius_km,
        'level':     level,
        'n_units':   len(basin_set),
        'unit_type': 'basin',
    }

    return _areal_signature_from_basin_set(
        basin_set, level, conn,
        neighborhood=neighborhood,
        shortfall=shortfall,
        lat=lat, lon=lon, radius_km=radius_km,
        bands=bands,
        from_year=from_year,
        to_year=to_year,
        include_detail=include_detail,
    )


# ── WO14: single-basin resolver + entry point ─────────────────────────────────

def resolve_single_basin(lat, lon, level, conn):
    """
    Single-basin resolver: point → {hybas_id: 1.0}.

    Reuses the same ST_Contains / geom lookup the live /signature path uses,
    so the returned hybas_id is guaranteed to match v0.3's containing basin.
    Returns a one-row DataFrame with weight=1.0.
    Shortfall is 0 by definition — the query is the basin itself.
    """
    table = _LEVEL_TABLE[level]
    sql = f"""
    SELECT hybas_id
    FROM {table}
    WHERE ST_Contains(geom, ST_SetSRID(ST_MakePoint({lon}, {lat}), 4326))
    """
    df = pd.read_sql(sql, conn)
    df['hybas_id'] = df['hybas_id'].astype('int64')
    df['weight']   = 1.0
    return df


def single_basin_signature(
    lat, lon,
    conn,
    level=6,
    bands=None,
    from_year=None,
    to_year=None,
    include_detail=False,
):
    """
    Areal signature for the single containing basin at a point.

    The resolver returns {hybas_id: 1.0}; every downstream block runs unchanged.
    Shortfall is 0.0 — the query is the basin, so no geographic absence is possible.

    Band T is not yet supported: aggregate_band_t takes a circular buffer geometry;
    single-basin Band T needs the basin polygon as the query area. Deferred.

    Parameters
    ----------
    lat, lon       : float — WGS-84 query point
    conn           : psycopg3 connection
    level          : int   — 6 or 8
    bands          : list[str] or None — band letters; None = A–E only
    from_year      : int or None — reserved (Band T not yet supported here)
    to_year        : int or None — reserved
    include_detail : bool

    Returns
    -------
    dict — {neighborhood, shortfall, bands, temporal, caveats, rows}
    """
    table = _LEVEL_TABLE[level]

    # ── 1. Resolve single basin ───────────────────────────────────────────────
    basin_set = resolve_single_basin(lat, lon, level, conn)
    shortfall = 0.0
    hybas_id  = int(basin_set['hybas_id'].iloc[0])

    basin_geom_wkt = conn.execute(
        f"SELECT ST_AsText(geom) FROM {table} WHERE hybas_id = {hybas_id}"
    ).fetchone()[0]

    neighborhood = {
        'type':      'basin',
        'lat':       lat,
        'lon':       lon,
        'level':     level,
        'hybas_id':  hybas_id,
        'n_units':   1,
        'unit_type': 'basin',
    }

    return _areal_signature_from_basin_set(
        basin_set, level, conn,
        neighborhood=neighborhood,
        shortfall=shortfall,
        geom_wkt=basin_geom_wkt,
        bands=bands,
        from_year=from_year,
        to_year=to_year,
        include_detail=include_detail,
    )


# ── WO20: polygon resolver + polity entry point ───────────────────────────────

def areal_signature_polygon(
    geom_wkt,
    conn,
    level=6,
    bands=None,
    from_year=None,
    to_year=None,
    include_detail=False,
):
    """
    Full areal signature for a polygon geometry.

    The aggregation pipeline is identical to areal_signature (buffer); only the
    resolver differs. resolve_polygon returns basin_in_polity_fraction per basin;
    the marginal-exposure diagnostic is computed here and added to the neighborhood
    block so downstream consumers can assess boundary leverage without a second
    query.

    Parameters
    ----------
    geom_wkt       : str  — WKT polygon (SRID 4326)
    conn           : psycopg3 connection
    level          : int  — 6 or 8
    bands          : list[str] or None — None = A–E (+ T if span given)
    from_year      : int or None — Band T span start (CE)
    to_year        : int or None — Band T span end (CE)
    include_detail : bool

    Returns
    -------
    dict — {neighborhood, shortfall, bands, temporal, caveats, rows}
    neighborhood['marginal_exposure'] = {lt_50pct, lt_20pct}: sum of weights for
    basins where basin_in_polity_fraction < 0.5 / < 0.2 (describe, don't decide).
    """
    level_str = f'{level:02d}'
    basin_set = resolve_polygon(geom_wkt, level_str, conn)
    shortfall = round(1.0 - float(basin_set['weight'].sum()), 6)

    bif = basin_set['basin_in_polity_fraction']
    me_lt50 = float(basin_set.loc[bif < 0.5, 'weight'].sum())
    me_lt20 = float(basin_set.loc[bif < 0.2, 'weight'].sum())

    neighborhood = {
        'type':              'polygon',
        'level':             level,
        'n_units':           len(basin_set),
        'unit_type':         'basin',
        'marginal_exposure': {
            'lt_50pct': round(me_lt50, 6),
            'lt_20pct': round(me_lt20, 6),
        },
    }

    payload = _areal_signature_from_basin_set(
        basin_set, level, conn,
        neighborhood=neighborhood,
        shortfall=shortfall,
        geom_wkt=geom_wkt,
        bands=bands,
        from_year=from_year,
        to_year=to_year,
        include_detail=include_detail,
        run_modality=False,
    )
    payload['modality_post_pass'] = 'skipped — not calibrated for polygon scale'
    return payload
