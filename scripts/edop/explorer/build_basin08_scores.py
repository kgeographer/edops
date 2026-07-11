"""Build public.basin08_scores — pre-materialized PERCENT_RANK scores for all L08 basins.

Eliminates the per-request full-table PERCENT_RANK computation in attach_values(),
reducing areal signature time at L08 from ~18-23s to ~L06 baseline.

Run from repo root:
    python scripts/edop/explorer/build_basin08_scores.py

Expected runtime: 10–30 min. Safe to re-run (DROP/CREATE).
"""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

import numpy as np
import pandas as pd
from app.db.connection import db_connect
from scripts.edop.areas.engine import load_catalog, rank_expr, _val_expr, _parse_zf

TABLE   = 'public.basin08'
OUT     = 'public.basin08_scores'
LEVEL   = 8
ZF_THRESHOLD = 0.20


def nodata_count(conn, db_col):
    row = conn.execute(
        f"SELECT COUNT(*) FROM {TABLE} WHERE {db_col} = -9999 OR {db_col} IS NULL"
    ).fetchone()
    return row[0]


def score_clean(conn, db_col, method, zero_fraction):
    """PERCENT_RANK for a variable with no nodata rows — single-pass query."""
    expr = rank_expr(db_col, method, zero_fraction, ZF_THRESHOLD)
    sql  = f"SELECT hybas_id, ({expr}) AS score FROM {TABLE}"
    return pd.read_sql(sql, conn).set_index('hybas_id')['score']


def score_affected(conn, db_col, method, zero_fraction):
    """PERCENT_RANK for a variable with nodata rows — two-pass (filtered CTE)."""
    val = _val_expr(db_col, method)

    if zero_fraction is not None and zero_fraction >= ZF_THRESHOLD:
        # Zero-aware: zeros score 0; nonzero ranked within nonzero population
        sql = f"""
            WITH valid_pop AS (
                SELECT hybas_id, {db_col}
                FROM {TABLE}
                WHERE {db_col} IS NOT NULL AND {db_col} <> -9999 AND {db_col} > 0
            ),
            ranked AS (
                SELECT hybas_id,
                       PERCENT_RANK() OVER (ORDER BY {val}) * 100 AS score
                FROM valid_pop
            )
            SELECT b.hybas_id,
                   CASE
                     WHEN b.{db_col} IS NULL OR b.{db_col} = -9999 THEN NULL
                     WHEN b.{db_col} = 0 THEN 0.0
                     ELSE r.score
                   END AS score
            FROM {TABLE} b
            LEFT JOIN ranked r USING (hybas_id)
        """
    else:
        sql = f"""
            WITH valid_pop AS (
                SELECT hybas_id, {db_col}
                FROM {TABLE}
                WHERE {db_col} IS NOT NULL AND {db_col} <> -9999
            ),
            ranked AS (
                SELECT hybas_id,
                       PERCENT_RANK() OVER (ORDER BY {val}) * 100 AS score
                FROM valid_pop
            )
            SELECT b.hybas_id,
                   CASE
                     WHEN b.{db_col} IS NULL OR b.{db_col} = -9999 THEN NULL
                     ELSE r.score
                   END AS score
            FROM {TABLE} b
            LEFT JOIN ranked r USING (hybas_id)
        """
    return pd.read_sql(sql, conn).set_index('hybas_id')['score']


def main():
    t_start = time.perf_counter()
    conn = db_connect()

    meta_df = load_catalog(level=LEVEL)
    cont_vars = meta_df[
        (meta_df['kind'] == 'continuous') &
        (~meta_df.get('derived', pd.Series(False, index=meta_df.index)))
    ]
    print(f"Continuous variables to score: {len(cont_vars)}")

    scores = {}
    for i, (api_key, row) in enumerate(cont_vars.iterrows(), 1):
        db_col = row['db_col']
        method = row['position_method'] or 'linear'
        zf     = row['zero_fraction']

        t0 = time.perf_counter()
        n_nodata = nodata_count(conn, db_col)

        if n_nodata == 0:
            s = score_clean(conn, db_col, method, zf)
        else:
            s = score_affected(conn, db_col, method, zf)

        scores[api_key] = s
        print(f"  [{i:3d}/{len(cont_vars)}] {api_key:40s}  nodata={n_nodata:6d}  "
              f"{time.perf_counter()-t0:.1f}s", flush=True)

    print("\nAssembling scores DataFrame…", flush=True)
    df = pd.DataFrame(scores)
    df.index.name = 'hybas_id'
    df = df.reset_index()
    print(f"  Shape: {df.shape[0]:,} basins × {df.shape[1]-1} variables")

    print(f"\nWriting to {OUT}…", flush=True)
    conn.execute(f"DROP TABLE IF EXISTS {OUT}")
    col_defs = ', '.join(f'"{k}" real' for k in df.columns if k != 'hybas_id')
    conn.execute(f"CREATE TABLE {OUT} (hybas_id bigint, {col_defs})")
    conn.commit()

    cols    = list(df.columns)
    col_str = ', '.join(f'"{c}"' for c in cols)
    with conn.cursor() as cur:
        with cur.copy(f"COPY {OUT} ({col_str}) FROM STDIN") as copy:
            hid_idx = cols.index('hybas_id')
            for row in df.itertuples(index=False):
                vals = list(row)
                vals[hid_idx] = int(vals[hid_idx])
                copy.write_row(tuple(None if (i != hid_idx and v is None or (isinstance(v, float) and np.isnan(v))) else v for i, v in enumerate(vals)))
    conn.commit()

    print(f"Adding primary key index on hybas_id…", flush=True)
    conn.execute(f"ALTER TABLE {OUT} ADD PRIMARY KEY (hybas_id)")
    conn.commit()

    elapsed = time.perf_counter() - t_start
    print(f"\nDone. {OUT} built in {elapsed/60:.1f} min.")
    print("Run a quick verify:")
    print(f"  SELECT COUNT(*) FROM {OUT};  -- expect ~190,675")
    print(f"  SELECT * FROM {OUT} LIMIT 3;")


if __name__ == '__main__':
    main()
