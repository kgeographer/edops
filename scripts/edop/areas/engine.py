"""
EDOPS Areas Engine — promoted primitives (WO1 + WO2 + WO3).

Bottom-of-stack pieces (WO1):
  resolve_buffer    — point + radius → weighted basin set (was inline in step1/step2)
  weighted_quantile — weighted quantile primitive (was duplicated in step3/step3b)
  diff_output       — regression harness: compare engine output to a reference

Attachment pass (WO2):
  attach_values     — basin set + meta_df → (matrix_df, class_id_df, raw_df)

  Private SQL builders (call via attach_values):
  _parse_zf, _val_expr, rank_expr, two_pass_sql

Dispatch (WO3):
  dispatch_variable — (typology_cluster, kind) → block label
"""

import numpy as np
import pandas as pd


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
