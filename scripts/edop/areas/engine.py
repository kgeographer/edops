"""
EDOPS Areas Engine — promoted primitives (WO1).

Bottom-of-stack pieces that are contract-independent:
  resolve_buffer    — point + radius → weighted basin set (was inline in step1/step2)
  weighted_quantile — weighted quantile primitive (was duplicated in step3/step3b)
  diff_output       — regression harness: compare engine output to a reference
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
            mismatches = (a[col].astype(str) != r[col].astype(str)).sum()
            if mismatches:
                print(f'{tag}FAIL {col}: {mismatches} string mismatch(es)')
                ok = False

    if ok:
        print(f'{tag}PASS')
    return ok
