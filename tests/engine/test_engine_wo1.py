"""
WO1 regression: resolver fixture + weighted_quantile spot-check.

Run from repo root:
    python scripts/edop/areas/test_engine_wo1.py

Acceptance criteria (from WO1 work order):
  resolver  — Timbuktu 100 km / L06 → 9 basins, weight sum 1.0000, weights
               match step2_raw.tsv (the canonical reference) within 1e-4.
  quantile  — spot-checked against known equal-weight and skewed-weight cases.
"""

import sys
import warnings
warnings.filterwarnings('ignore', category=UserWarning)
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import numpy as np
import pandas as pd
import scripts.shared.db_utils as _dbu
from scripts.edop.areas.engine import resolve_buffer, weighted_quantile, diff_output

ROOT = Path(_dbu.__file__).resolve().parents[2]
OUT  = ROOT / 'output' / 'edop' / 'areas'


def test_resolve_buffer(conn):
    result = resolve_buffer(16.8167, -2.9833, 100, '06', conn, epsilon=0.001)

    assert len(result) == 9,                   f'Expected 9 basins, got {len(result)}'
    assert result['hybas_id'].dtype == 'int64', 'hybas_id must be int64'

    total_w = result['weight'].sum()
    assert abs(total_w - 1.0) < 1e-4,          f'Weight sum {total_w:.6f} ≠ 1.0'

    ref = _dbu.read_areas_tsv(OUT / 'step2_raw.tsv', index_col='hybas_id')
    ref_weights = ref[['weight']].reset_index()

    print('resolve_buffer vs step2_raw.tsv:')
    return diff_output(result, ref_weights, float_tol=1e-4,
                       id_col='hybas_id', label='resolver')


def test_weighted_quantile():
    scores  = np.array([10.0, 20.0, 30.0, 40.0])
    weights = np.array([0.25, 0.25, 0.25, 0.25])

    # cumw = [0.25, 0.50, 0.75, 1.00]; interp hits sv[1]=20 at q=0.5 exactly
    assert abs(weighted_quantile(scores, weights, 0.5)  - 20.0) < 1e-6
    assert abs(weighted_quantile(scores, weights, 0.75) - 30.0) < 1e-6
    assert abs(weighted_quantile(scores, weights, 0.0)  - 10.0) < 1e-9
    assert abs(weighted_quantile(scores, weights, 1.0)  - 40.0) < 1e-9

    # Heavy mass on third value — p50 shifts into the 20–30 interval
    weights2 = np.array([0.1, 0.1, 0.7, 0.1])
    median2  = weighted_quantile(scores, weights2, 0.5)
    assert 20.0 <= median2 < 30.0, f'Median {median2:.4f} not in [20, 30)'

    # Unnormalized weights — function must normalize internally
    weights3 = np.array([2.5, 2.5, 2.5, 2.5])
    assert abs(weighted_quantile(scores, weights3, 0.5) - 20.0) < 1e-6

    print('[quantile] PASS')
    return True


if __name__ == '__main__':
    from scripts.shared.db_utils import db_connect
    conn = db_connect()
    try:
        r1 = test_resolve_buffer(conn)
        r2 = test_weighted_quantile()
        print()
        print('WO1:', 'PASS' if r1 and r2 else 'FAIL')
    finally:
        conn.close()
