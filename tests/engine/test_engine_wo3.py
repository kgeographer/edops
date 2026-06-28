"""
WO3 coverage test: dispatch_variable full-catalog check.

Run via pytest:
    pytest tests/engine/test_engine_wo3.py

Acceptance (from WO3 work order):
  For every variable in step2_meta.tsv that appears in step3_results.tsv,
  dispatch_variable must route it to the block that produced its recorded method.
  Variables not in step3_results.tsv are reported (deferred / excluded / synthetic).
  Pass = zero mismatches, no variable unrouted, full report printed.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pandas as pd
import scripts.shared.db_utils as _dbu
from scripts.edop.areas.engine import dispatch_variable

ROOT = Path(_dbu.__file__).resolve().parents[2]
OUT  = ROOT / 'output' / 'edop' / 'areas'

# method names recorded in step3_results.tsv → block that produced them
METHOD_TO_BLOCK = {
    'area_weighted':     'B1',
    'dominant_basin':    'B2',
    'class_mixture':     'B3',  # also B4 for outlet_type, but outlet_type is synthetic
    'distribution_only': 'B5',
    'extreme':           'B5',
    'flag_fraction':     'B4',  # coast_fraction, also synthetic
}


def test_dispatch_coverage():
    meta    = pd.read_csv(OUT / 'step2_meta.tsv',    sep='\t', index_col='api_key')
    results = pd.read_csv(OUT / 'step3_results.tsv', sep='\t', index_col='variable')

    ok          = True
    mismatches  = []
    not_in_results = []   # dispatched but not in step3_results.tsv
    synthetic   = []      # in step3_results.tsv but not in meta_df

    # ── Check every meta_df variable ─────────────────────────────────────────
    for api_key, row in meta.iterrows():
        block = dispatch_variable(row['typology_cluster'], row['kind'])

        if block == 'unknown':
            mismatches.append((api_key, 'unknown', '—', row['typology_cluster'], row['kind']))
            ok = False
            continue

        if api_key not in results.index:
            not_in_results.append((api_key, block, row['typology_cluster'], row['kind']))
            continue

        recorded_method = results.loc[api_key, 'method']
        expected_block  = METHOD_TO_BLOCK.get(recorded_method, '??')

        if block != expected_block:
            mismatches.append((
                api_key, block, expected_block,
                row['typology_cluster'], row['kind']
            ))
            ok = False

    # ── Synthetic outputs (in results but not in meta_df) ────────────────────
    for var in results.index:
        if var not in meta.index:
            synthetic.append((var, results.loc[var, 'method']))

    # ── Report ───────────────────────────────────────────────────────────────
    in_both = [k for k in meta.index if k in results.index]
    print(f'Coverage check: {len(meta)} meta_df vars → '
          f'{len(in_both)} in step3_results, '
          f'{len(not_in_results)} not in results, '
          f'{len(synthetic)} synthetic outputs')
    print()

    if mismatches:
        print('MISMATCHES:')
        for api_key, got, expected, cluster, kind in mismatches:
            print(f'  {api_key:40s}  dispatched={got}  expected={expected}'
                  f'  cluster={cluster}  kind={kind}')
        print()
    else:
        print('Routing match: all dispatched vars match recorded method  ✓')
        print()

    if not_in_results:
        print('Vars dispatched but NOT in step3_results.tsv (deferred / excluded):')
        for api_key, block, cluster, kind in not_in_results:
            print(f'  {api_key:40s}  dispatch={block}  cluster={cluster}  kind={kind}')
        print()

    if synthetic:
        print('Synthetic outputs (in step3_results.tsv, NOT in meta_df):')
        for var, method in synthetic:
            print(f'  {var:40s}  method={method}')
        print()

    print('WO3:', 'PASS' if ok else 'FAIL')
    assert ok
