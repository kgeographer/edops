"""
WO11a acceptance test: load_catalog integrity + derived/sourced fork.

Run from repo root:
    python scripts/edop/areas/test_engine_wo11a.py

Acceptance (from WO11a work order):
  1. Row counts — sourced=54, derived=5, total=59
  2. Sourced rows == step2_meta.tsv — all shared columns; one expected diff:
       endorheic.schema_key='endorheic' (Karl's 2026-06-24 edit; frozen='outlet_type')
  3. Derived rows present and correctly marked — 5 rows, all derived=True,
       db_col=None; api_keys: coast_fraction, elev_point, outlet_type,
       relief_position, relief_range_m
  4. attach_values skips derived rows — matrix/raw shapes unchanged from
       step2 frozen outputs (9 basins × 54 sourced vars)
  5. dispatch_variable routes every sourced var correctly — no derived var
       misrouted; B4-consumed flags (endorheic, coast_flag) routed to B4
  6. B1 regression with load_catalog meta_df — strict vs step3_results.tsv
  7. B4 regression with load_catalog meta_df — strict vs step3_results.tsv

Determinations flagged (WO11a):
  1. endorheic.schema_key: expected diff vs frozen (Karl's catalog edit).
  2. kind derivation: flags detected by _FLAG_API_KEYS override; categoricals
     by position_method='rarity_rank' (logically coherent, not just empirical —
     rarity_rank is chosen specifically for class-membership variables).
  3. WO expected 2 derived rows; actual 5 (elevation_point, relief_range_m,
     relief_position were already status='implemented' when load_catalog was
     written). All 5 correctly marked derived=True, db_col=None.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pandas as pd
import scripts.shared.db_utils as _dbu
from scripts.edop.areas.engine import (
    load_catalog, attach_values, aggregate_b1, aggregate_b4,
    dispatch_variable, diff_output,
)
from scripts.shared.db_utils import db_connect

ROOT = Path(_dbu.__file__).resolve().parents[2]
OUT  = ROOT / 'output' / 'edop' / 'areas'

_EXPECTED_DERIVED = frozenset({
    'coast_fraction', 'elev_point', 'outlet_type',
    'relief_position', 'relief_range_m',
})


def test_row_counts():
    """Test 1: sourced=54, derived=5, total=59."""
    print('─' * 60)
    print('Test 1: row counts')
    print('─' * 60)

    meta = load_catalog(level=6)
    sourced = meta[~meta['derived']]
    derived = meta[meta['derived']]

    ok = True
    for label, got, exp in [
        ('total',   len(meta),    59),
        ('sourced', len(sourced), 54),
        ('derived', len(derived), 5),
    ]:
        if got == exp:
            print(f'  OK    {label}={got}')
        else:
            print(f'  FAIL  {label}={got}, expected {exp}')
            ok = False

    print('  PASS  row counts' if ok else '  FAIL  row counts')
    return ok


def test_sourced_vs_frozen():
    """Test 2: sourced rows match step2_meta.tsv; one expected diff (endorheic.schema_key)."""
    print()
    print('─' * 60)
    print('Test 2: sourced rows vs frozen step2_meta.tsv')
    print('─' * 60)

    meta   = load_catalog(level=6)
    sourced = meta[~meta['derived']]
    frozen  = pd.read_csv(OUT / 'step2_meta.tsv', sep='\t', index_col='api_key')

    ok = True

    # api_key sets must match exactly
    only_sourced = set(sourced.index) - set(frozen.index)
    only_frozen  = set(frozen.index)  - set(sourced.index)
    if only_sourced or only_frozen:
        print(f'  FAIL  api_key mismatch — only sourced: {sorted(only_sourced)}, '
              f'only frozen: {sorted(only_frozen)}')
        ok = False
    else:
        print(f'  OK    api_key sets identical (54 rows)')

    # Value diff on shared rows
    common_cols = [c for c in frozen.columns if c in sourced.columns]
    shared = sorted(set(sourced.index) & set(frozen.index))

    diffs = []
    for col in common_cols:
        a = sourced.loc[shared, col]
        b = frozen.loc[shared, col]
        try:
            diff = (pd.to_numeric(a, errors='raise')
                    - pd.to_numeric(b, errors='raise')).abs().max()
            if diff > 1e-6:
                diffs.append((col, f'max_diff={diff:.6f}'))
        except (ValueError, TypeError):
            a_null, b_null = pd.isna(a), pd.isna(b)
            null_mm = int((a_null != b_null).sum())
            mask    = ~a_null & ~b_null
            str_mm  = int((a[mask].astype(str) != b[mask].astype(str)).sum())
            if null_mm or str_mm:
                examples = [
                    (i, a.get(i), b.get(i)) for i in shared
                    if str(a.get(i, '')) != str(b.get(i, ''))
                    or (pd.isna(a.get(i)) != pd.isna(b.get(i)))
                ][:3]
                diffs.append((col, f'{null_mm} null / {str_mm} str; e.g. {examples}'))

    expected_diffs = {'schema_key'}   # endorheic: 'endorheic' vs frozen 'outlet_type'
    unexpected = [d for d in diffs if d[0] not in expected_diffs]
    expected_seen = [d for d in diffs if d[0] in expected_diffs]

    for col, msg in expected_seen:
        print(f'  OK    expected diff  {col}: {msg}')
    for col, msg in unexpected:
        print(f'  FAIL  unexpected diff {col}: {msg}')
        ok = False

    if not diffs:
        print('  OK    no diffs (zero delta from frozen)')
    elif not unexpected:
        print(f'  OK    only expected diff(s): {[d[0] for d in expected_seen]}')

    print('  PASS  sourced vs frozen' if ok else '  FAIL  sourced vs frozen')
    return ok


def test_derived_rows():
    """Test 3: derived rows present, marked, db_col=None."""
    print()
    print('─' * 60)
    print('Test 3: derived rows')
    print('─' * 60)

    meta    = load_catalog(level=6)
    derived = meta[meta['derived']]
    ok      = True

    got_keys = set(derived.index)
    if got_keys != _EXPECTED_DERIVED:
        print(f'  FAIL  derived api_keys={sorted(got_keys)}, '
              f'expected={sorted(_EXPECTED_DERIVED)}')
        ok = False
    else:
        print(f'  OK    derived api_keys: {sorted(got_keys)}')

    for ak, row in derived.iterrows():
        if row['db_col'] is not None:
            print(f'  FAIL  {ak}: db_col={row["db_col"]!r}, expected None')
            ok = False
        if row['derived'] is not True:
            print(f'  FAIL  {ak}: derived={row["derived"]!r}, expected True')
            ok = False

    if ok:
        print(f'  OK    all {len(derived)} derived rows: derived=True, db_col=None')

    print('  PASS  derived rows' if ok else '  FAIL  derived rows')
    return ok


def test_attach_skips_derived():
    """Test 4: attach_values matrix/raw shapes unchanged (9×54) with load_catalog meta_df."""
    print()
    print('─' * 60)
    print('Test 4: attach_values skips derived rows')
    print('─' * 60)

    meta      = load_catalog(level=6)
    basin_set = _dbu.read_areas_tsv(OUT / 'step2_raw.tsv', index_col='hybas_id')[['weight']]
    conn      = db_connect()

    try:
        matrix_df, class_id_df, raw_df = attach_values(
            basin_set, meta, conn,
            table='public.basin06',
            view='public.v_basin06_persist_rev1',
        )
    finally:
        conn.close()

    ok = True
    for label, got, exp in [
        ('matrix rows', matrix_df.shape[0],  9),
        ('matrix cols', matrix_df.shape[1],  54),
        ('raw rows',    raw_df.shape[0],      9),
    ]:
        if got == exp:
            print(f'  OK    {label}={got}')
        else:
            print(f'  FAIL  {label}={got}, expected {exp}')
            ok = False

    # Confirm no derived api_key leaked into matrix
    meta_derived = set(load_catalog(level=6).loc[load_catalog(level=6)['derived']].index)
    leaked = meta_derived & set(matrix_df.columns)
    if leaked:
        print(f'  FAIL  derived keys in matrix: {sorted(leaked)}')
        ok = False
    else:
        print(f'  OK    no derived keys in matrix columns')

    print('  PASS  attach skips derived' if ok else '  FAIL  attach skips derived')
    return ok


def test_dispatch_routing():
    """Test 5: dispatch_variable routes all sourced vars; no derived var misrouted."""
    print()
    print('─' * 60)
    print('Test 5: dispatch_variable routing')
    print('─' * 60)

    meta    = load_catalog(level=6)
    sourced = meta[~meta['derived']]
    derived = meta[meta['derived']]
    ok      = True

    route_counts = {}
    unknown = []
    for ak, row in sourced.iterrows():
        label = dispatch_variable(row['typology_cluster'], row['kind'])
        route_counts[label] = route_counts.get(label, 0) + 1
        if label == 'unknown':
            unknown.append(ak)

    print(f'  Routing distribution: {dict(sorted(route_counts.items()))}')

    if unknown:
        print(f'  FAIL  unknown routes: {unknown}')
        ok = False

    # Flags must route to B4
    for ak in ('endorheic', 'coast_flag'):
        label = dispatch_variable(
            sourced.loc[ak, 'typology_cluster'],
            sourced.loc[ak, 'kind'],
        )
        if label != 'B4':
            print(f'  FAIL  {ak} routed to {label!r}, expected B4')
            ok = False
        else:
            print(f'  OK    {ak} → B4')

    # Derived rows: not routed (caller responsibility; confirm they'd route to 'unknown'
    # or a valid block IF accidentally fed — derived kind='categorical'/'continuous' with
    # no typology_cluster would give B3/B5, not B4. Not a correctness concern since the
    # assembly skips them.)
    for ak, row in derived.iterrows():
        if row['kind'] in ('continuous', 'categorical', 'flag'):
            label = dispatch_variable(row['typology_cluster'], row['kind'])
            print(f'  NOTE  derived {ak} would route to {label!r} if not skipped')

    if ok:
        print(f'  OK    all {len(sourced)} sourced vars routed; no unknowns')

    print('  PASS  dispatch routing' if ok else '  FAIL  dispatch routing')
    return ok


def test_b1_regression():
    """Test 6: B1 area_weighted regression with load_catalog meta_df."""
    print()
    print('─' * 60)
    print('Test 6: B1 regression (area_weighted)')
    print('─' * 60)

    meta      = load_catalog(level=6)
    basin_set = _dbu.read_areas_tsv(OUT / 'step2_raw.tsv', index_col='hybas_id')[['weight']]
    conn      = db_connect()

    try:
        matrix_df, _, _ = attach_values(
            basin_set, meta, conn,
            table='public.basin06',
            view='public.v_basin06_persist_rev1',
        )
    finally:
        conn.close()

    rows    = aggregate_b1(basin_set, matrix_df, meta)
    ref_all = pd.read_csv(OUT / 'step3_results.tsv', sep='\t')
    ref     = ref_all[ref_all['method'] == 'area_weighted'].copy()

    actual = pd.DataFrame([{
        'variable':             r['variable'],
        'representative_score': r['representative_score'],
        'n_basins':             r['n_units'],
        'coverage_weight':      r['coverage'],
    } for r in rows])

    ok = diff_output(
        actual[['variable', 'representative_score', 'n_basins', 'coverage_weight']],
        ref[['variable', 'representative_score', 'n_basins', 'coverage_weight']],
        float_tol=0.01, id_col='variable', label='B1',
    )
    return ok


def test_b4_regression():
    """Test 7: B4 flag/structural regression with load_catalog meta_df."""
    print()
    print('─' * 60)
    print('Test 7: B4 regression (flag/structural)')
    print('─' * 60)

    meta      = load_catalog(level=6)
    basin_set = _dbu.read_areas_tsv(OUT / 'step2_raw.tsv', index_col='hybas_id')[['weight']]
    conn      = db_connect()

    try:
        _, _, raw_df = attach_values(
            basin_set, meta, conn,
            table='public.basin06',
            view='public.v_basin06_persist_rev1',
        )
    finally:
        conn.close()

    rows    = aggregate_b4(basin_set, raw_df)
    ref_all = pd.read_csv(OUT / 'step3_results.tsv', sep='\t')
    ref     = ref_all[
        ref_all['method'].isin(['class_mixture', 'flag_fraction'])
        & ref_all['variable'].isin(['outlet_type', 'coast_fraction'])
    ].copy()

    actual = pd.DataFrame([{
        'variable':             r['variable'],
        'representative_score': r['representative_score'],
        'n_basins':             r['n_units'],
        'coverage_weight':      r['coverage'],
    } for r in rows])

    ok = diff_output(
        actual[['variable', 'representative_score', 'n_basins', 'coverage_weight']],
        ref[['variable', 'representative_score', 'n_basins', 'coverage_weight']],
        float_tol=0.01, id_col='variable', label='B4',
    )
    return ok


if __name__ == '__main__':
    results = [
        test_row_counts(),
        test_sourced_vs_frozen(),
        test_derived_rows(),
        test_attach_skips_derived(),
        test_dispatch_routing(),
        test_b1_regression(),
        test_b4_regression(),
    ]

    print()
    print('=' * 60)
    n_pass = sum(r for r in results if r is True)
    print(f"WO11a: {'PASS' if all(r is True for r in results) else 'FAIL'}  "
          f"({n_pass}/{len(results)} tests passed)")
    sys.exit(0 if all(r is True for r in results) else 1)
