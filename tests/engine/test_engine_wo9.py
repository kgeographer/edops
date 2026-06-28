"""
WO9 acceptance test: aggregate_b5 regression against frozen TSV targets.

Run from repo root:
    python scripts/edop/areas/test_engine_wo9.py

Acceptance (from WO9 work order):
  1. distribution_only headline — strict: representative_score, spread, p10, p90,
     n_basins, coverage_weight vs step3_results.tsv (temp_min, temp_max)
  2. distribution_only companion — strict: hybas_id + score vs step3_block5_distribution.tsv
  3. extreme (river_area) headline — strict: representative_score, representative_raw,
     n_basins, coverage_weight; carrier basin = 1060582960 at 4273 km²
  4. Envelope: method, unit_type, status, coherence for all 3 B5 rows
  5. extreme/B2 carrier split confirmed (river_area carrier ≠ B2 discharge dominant)
  6. Sample projection: lean + full for one distribution_only row and river_area

Determinations flagged (WO9 / amended WO10b):
  1. distribution_only coherence — WO10b blessed deviation: coherence now emitted as
     'concentrated' (spread < 20) or 'spread'; engine adds the trust flag the frozen TSV
     lacked. temp_min spread=5.65, temp_max spread=3.23 → both 'concentrated'.
     Amended from WO9 original (coherence=None); re-freeze signed off 2026-06-24.
  2. distribution_only representative_score = weighted mean percentile (always populated,
     unlike B1 which nulls it for spread rows); confirmed from frozen TSV (78.98, 95.56).
  3. extreme envelope: representative_raw=raw km² value; representative_score=carrier
     percentile; dominant_hybas_id in detail; coherence=None.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pandas as pd
import scripts.shared.db_utils as _dbu
from scripts.edop.areas.engine import aggregate_b5, project_row, diff_output

ROOT = Path(_dbu.__file__).resolve().parents[2]
OUT  = ROOT / 'output' / 'edop' / 'areas'


def _load_inputs():
    raw_df    = _dbu.read_areas_tsv(OUT / 'step2_raw.tsv',    index_col='hybas_id')
    matrix_df = _dbu.read_areas_tsv(OUT / 'step2_matrix.tsv', index_col='hybas_id')
    meta_df   = pd.read_csv(OUT / 'step2_meta.tsv', sep='\t', index_col='api_key')
    basin_set = raw_df[['weight']].copy()
    return basin_set, matrix_df, raw_df, meta_df


def _run_b5():
    basin_set, matrix_df, raw_df, meta_df = _load_inputs()
    return aggregate_b5(basin_set, matrix_df, raw_df, meta_df)


def test_distribution_only_headline():
    """Test 1: distribution_only representative_score + distribution fields strict."""
    print('─' * 60)
    print('Test 1: distribution_only headline — temp_min + temp_max')
    print('─' * 60)

    rows, _ = _run_b5()
    dist_rows = [r for r in rows if r['method'] == 'distribution_only']

    actual = pd.DataFrame([{
        'variable':             r['variable'],
        'representative_score': r['representative_score'],
        'n_basins':             r['n_units'],
        'coverage_weight':      r['coverage'],
        'spread':               r.get('detail', {}).get('spread'),
        'p10':                  r.get('detail', {}).get('p10'),
        'p90':                  r.get('detail', {}).get('p90'),
    } for r in dist_rows])

    ref_all = pd.read_csv(OUT / 'step3_results.tsv', sep='\t')
    ref     = ref_all[ref_all['method'] == 'distribution_only'].copy()
    ref['n_basins'] = ref['n_basins'].astype(int)

    if len(actual) != 2:
        print(f'  FAIL  expected 2 distribution_only rows, got {len(actual)}')
        return False
    print(f'  OK    {len(actual)} distribution_only rows')

    ok = diff_output(
        actual[['variable', 'representative_score', 'n_basins', 'coverage_weight',
                'spread', 'p10', 'p90']],
        ref[['variable', 'representative_score', 'n_basins', 'coverage_weight',
             'spread', 'p10', 'p90']],
        float_tol=0.01,
        id_col='variable',
        label='B5 distribution_only',
    )
    return ok


def test_companion_rows():
    """Test 2: companion distribution rows strict vs step3_block5_distribution.tsv."""
    print()
    print('─' * 60)
    print('Test 2: companion distribution rows')
    print('─' * 60)

    _, companion = _run_b5()
    actual = pd.DataFrame(companion)
    actual['row_id'] = actual['variable'] + ':' + actual['hybas_id'].astype(str)

    ref = pd.read_csv(OUT / 'step3_block5_distribution.tsv', sep='\t')
    ref['row_id'] = ref['variable'] + ':' + ref['hybas_id'].astype(str)

    if len(actual) != len(ref):
        print(f'  FAIL  expected {len(ref)} companion rows, got {len(actual)}')
        return False
    print(f'  OK    {len(actual)} companion rows')

    ok = diff_output(
        actual[['row_id', 'score']],
        ref[['row_id', 'score']],
        float_tol=0.001,
        id_col='row_id',
        label='B5 companion scores',
    )
    return ok


def test_extreme_headline():
    """Test 3: river_area extreme row strict."""
    print()
    print('─' * 60)
    print('Test 3: river_area extreme row')
    print('─' * 60)

    rows, _ = _run_b5()
    ext = next((r for r in rows if r['method'] == 'extreme'), None)
    if ext is None:
        print('  FAIL  no extreme row emitted')
        return False

    actual = pd.DataFrame([{
        'variable':             ext['variable'],
        'representative_score': ext['representative_score'],
        'representative_raw':   ext['representative_raw'],
        'n_basins':             ext['n_units'],
        'coverage_weight':      ext['coverage'],
    }])

    ref_all = pd.read_csv(OUT / 'step3_results.tsv', sep='\t')
    ref     = ref_all[ref_all['method'] == 'extreme'].copy()
    ref['n_basins'] = ref['n_basins'].astype(int)

    ok = diff_output(
        actual[['variable', 'representative_score', 'representative_raw',
                'n_basins', 'coverage_weight']],
        ref[['variable', 'representative_score', 'representative_raw',
             'n_basins', 'coverage_weight']],
        float_tol=0.01,
        id_col='variable',
        label='B5 extreme',
    )

    # Carrier basin check
    carrier = ext['detail'].get('dominant_hybas_id')
    if carrier != 1060582960:
        print(f'  FAIL  carrier={carrier!r}, expected 1060582960')
        ok = False
    else:
        print(f'  OK    carrier basin = {carrier}')

    return ok


def test_envelope():
    """Test 4: method, unit_type, status, coherence for all 3 B5 rows."""
    print()
    print('─' * 60)
    print('Test 4: envelope fields')
    print('─' * 60)

    rows, _ = _run_b5()
    ok = True

    expected = {
        'temp_min':   ('distribution_only', 'ok', 'concentrated'),  # spread=5.65 < 20; WO10b; status normalized untyped→ok (assembly review)
        'temp_max':   ('distribution_only', 'ok', 'concentrated'),  # spread=3.23 < 20; WO10b; status normalized untyped→ok (assembly review)
        'river_area': ('extreme',           'ok',       None),
    }

    for r in rows:
        var = r['variable']
        exp = expected.get(var)
        if exp is None:
            print(f'  WARN  unexpected variable {var!r}')
            continue
        exp_method, exp_status, exp_coherence = exp
        for field, got, exp_val in [
            ('method',    r['method'],    exp_method),
            ('unit_type', r['unit_type'], 'basin'),
            ('status',    r['status'],    exp_status),
            ('coherence', r['coherence'], exp_coherence),
        ]:
            if got != exp_val:
                print(f'  FAIL  {var}.{field}={got!r}, expected {exp_val!r}')
                ok = False

    if ok:
        print(f'  OK    all {len(rows)} rows: method/unit_type/status/coherence correct')

    print('  PASS  envelope' if ok else '  FAIL  envelope')
    return ok


def test_carrier_split():
    """Test 5: river_area carrier ≠ B2 discharge dominant (Inner Niger Delta split)."""
    print()
    print('─' * 60)
    print('Test 5: extreme/B2 carrier split (Inner Niger Delta finding)')
    print('─' * 60)

    rows, _ = _run_b5()
    ext = next((r for r in rows if r['method'] == 'extreme'), None)
    if ext is None:
        print('  SKIP  no extreme row')
        return True

    b5_carrier = ext['detail'].get('dominant_hybas_id')

    ref_all = pd.read_csv(OUT / 'step3_results.tsv', sep='\t')
    b2_rows = ref_all[ref_all['method'] == 'dominant_basin']
    if b2_rows.empty:
        print('  SKIP  no B2 rows in frozen TSV')
        return True

    b2_dom = _dbu.read_areas_tsv(OUT / 'step3_results.tsv')
    b2_dom = b2_dom[b2_dom['method'] == 'dominant_basin']['dominant_hybas_id'].dropna()
    b2_id  = int(b2_dom.iloc[0]) if len(b2_dom) else None

    ok = (b5_carrier != b2_id)
    print(f'  river_area carrier (B5) : {b5_carrier}')
    print(f'  discharge dominant (B2) : {b2_id}')
    if ok:
        print(f'  OK    distinct basins — Inner Niger Delta split preserved')
    else:
        print(f'  FAIL  same basin — expected different carriers')

    print('  PASS  carrier split' if ok else '  FAIL  carrier split')
    return ok


def test_sample_projection():
    """Test 6: lean + full projection for temp_min and river_area."""
    print()
    print('─' * 60)
    print('Test 6: sample projections')
    print('─' * 60)

    rows, _ = _run_b5()
    by_var  = {r['variable']: r for r in rows}

    for var, label in [('temp_min', 'distribution_only'), ('river_area', 'extreme')]:
        if var not in by_var:
            print(f'  WARN  {var} not in output')
            continue
        row  = by_var[var]
        lean = project_row(row, include_detail=False)
        full = project_row(row, include_detail=True)

        print(f'\n  [{label}]  variable={var}')
        for k in ('method', 'representative_score', 'representative_raw',
                  'status', 'coherence', 'n_units', 'coverage'):
            print(f'    {k:28s} = {lean.get(k)!r}')
        print(f'    detail                       = {full.get("detail")}')

    return True


if __name__ == '__main__':
    results = [
        test_distribution_only_headline(),
        test_companion_rows(),
        test_extreme_headline(),
        test_envelope(),
        test_carrier_split(),
        test_sample_projection(),
    ]

    print()
    print('=' * 60)
    n_pass = sum(r for r in results if r is True)
    print(f"WO9: {'PASS' if all(r is True for r in results) else 'FAIL'}  "
          f"({n_pass}/{len(results)} tests passed)")
    sys.exit(0 if all(r is True for r in results) else 1)
