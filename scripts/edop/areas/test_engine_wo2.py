"""
WO2 regression: attach_values fixture.

Run from repo root:
    python scripts/edop/areas/test_engine_wo2.py

Acceptance criteria (from WO2 work order):
  attach_values on Timbuktu 100 km / L06 basin set →
    raw_df    : 9 basins × 55 cols (weight + 54 vars); regress vs step2_raw.tsv
    matrix_df : 9 basins × 54 cols (scores, labels, flags); regress vs step2_matrix.tsv
    class_id_df: 9 basins × 11 cols (integer class IDs); regress vs step2_class_ids.tsv
"""

import sys
import warnings
warnings.filterwarnings('ignore', category=UserWarning)
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

import pandas as pd
import scripts.shared.db_utils as _dbu
from scripts.edop.areas.engine import resolve_buffer, attach_values, diff_output

ROOT  = Path(_dbu.__file__).resolve().parents[2]
OUT   = ROOT / 'output' / 'edop' / 'areas'

LEVEL = '06'
TABLE = f'public.basin{LEVEL}'
VIEW  = f'public.v_basin{LEVEL}_persist_rev1'


def load_meta():
    return pd.read_csv(OUT / 'step2_meta.tsv', sep='\t', index_col='api_key')


def test_attach_values(conn):
    basin_set = resolve_buffer(16.8167, -2.9833, 100, LEVEL, conn, epsilon=0.001)
    meta_df   = load_meta()

    matrix_df, class_id_df, raw_df = attach_values(
        basin_set, meta_df, conn, TABLE, VIEW
    )

    print(f'attach_values produced:')
    print(f'  raw_df     : {raw_df.shape}')
    print(f'  matrix_df  : {matrix_df.shape}')
    print(f'  class_id_df: {class_id_df.shape}')
    print()

    # diff_output expects hybas_id as a column, not index
    raw_r   = raw_df.reset_index()
    mat_r   = matrix_df.reset_index()
    cid_r   = class_id_df.reset_index()

    print('── raw_df vs step2_raw.tsv ──')
    ok1 = diff_output(raw_r,  OUT / 'step2_raw.tsv',      float_tol=1e-4,
                      id_col='hybas_id', label='raw')
    print()
    print('── matrix_df vs step2_matrix.tsv ──')
    ok2 = diff_output(mat_r,  OUT / 'step2_matrix.tsv',   float_tol=0.01,
                      id_col='hybas_id', label='matrix')
    print()
    print('── class_id_df vs step2_class_ids.tsv ──')
    ok3 = diff_output(cid_r,  OUT / 'step2_class_ids.tsv', float_tol=0.5,
                      id_col='hybas_id', label='class_ids')

    return ok1 and ok2 and ok3


if __name__ == '__main__':
    from scripts.shared.db_utils import db_connect
    conn = db_connect()
    try:
        ok = test_attach_values(conn)
        print()
        print('WO2:', 'PASS' if ok else 'FAIL')
    finally:
        conn.close()
