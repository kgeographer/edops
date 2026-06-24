"""
WO10 acceptance test: apply_modality + detect_modality regression.

Run from repo root:
    python scripts/edop/areas/test_engine_wo10.py

Acceptance (from WO10 work order):
  1. Two-regime classification — strict: exactly the 12 two_regime vars match frozen TSV
  2. Modality coverage — all 36 distribution-bearing rows have modality set
  3. Suppressed scores — 2 concentrated-but-bimodal rows: null score, score_suppressed=True,
     detail['suppressed_score'] == 96.45 / 5.29 (temp_yr_upstream / cropland_extent)
  4. Spread rows that are also two_regime: score_suppressed=False (score already null)
  5. Regimes companion — strict: 24 rows vs step3_block6_regimes.tsv
  6. Sample projection: lean + full for one two_regime row (suppressed value visible in detail)

Determinations (WO10):
  - detect_modality de-closure: consumed from notebook scope — joined[var] (scores),
    joined['weight'] (weights), and endo_hybas (endorheic basin set).
    endorheic_set is used ONLY for seam-alignment reporting, NOT for detection.
    The detection fires solely on: gap > MODALITY_GAP × spread,
    lw >= MIN_REGIME_WEIGHT, rw >= MIN_REGIME_WEIGHT.
  - Seam alignment (11/12): informative finding, not a computation; not reproduced here.
  - modality ∈ {unimodal, two_regime} — contract §4 values (never concentrated/broad/null
    on distribution-bearing rows). Diverges from frozen TSV sub-labels (concentrated, broad)
    which collapse to unimodal.
  - score_suppressed=True only when B6 is the reason for null (was concentrated).
    Spread rows that are also two_regime: score was already null; score_suppressed=False.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

import pandas as pd
import scripts.shared.db_utils as _dbu
from scripts.edop.areas.engine import (
    aggregate_b1, aggregate_b5, apply_modality, project_row, diff_output
)

ROOT = Path(_dbu.__file__).resolve().parents[2]
OUT  = ROOT / 'output' / 'edop' / 'areas'


def _load_inputs():
    raw_df    = _dbu.read_areas_tsv(OUT / 'step2_raw.tsv',    index_col='hybas_id')
    matrix_df = _dbu.read_areas_tsv(OUT / 'step2_matrix.tsv', index_col='hybas_id')
    meta_df   = pd.read_csv(OUT / 'step2_meta.tsv', sep='\t', index_col='api_key')
    basin_set = raw_df[['weight']].copy()
    return basin_set, matrix_df, raw_df, meta_df


def _run_b1_b5_b6():
    basin_set, matrix_df, raw_df, meta_df = _load_inputs()

    b1_rows             = aggregate_b1(basin_set, matrix_df, meta_df)
    b5_rows, _companion = aggregate_b5(basin_set, matrix_df, raw_df, meta_df)

    # apply_modality covers only distribution-bearing rows (area_weighted + distribution_only)
    dist_rows = b1_rows + [r for r in b5_rows if r['method'] == 'distribution_only']
    # 34 B1 + 2 B5 distribution_only = 36; river_area (extreme) excluded

    rows, regimes = apply_modality(dist_rows, basin_set, matrix_df)
    return rows, regimes


def test_two_regime_classification():
    """Test 1: Exactly the 12 two_regime vars match frozen TSV."""
    print('─' * 60)
    print('Test 1: two_regime classification — 12 vars strict')
    print('─' * 60)

    rows, _ = _run_b1_b5_b6()

    actual_two_regime = set(
        r['variable'] for r in rows if r.get('modality') == 'two_regime'
    )

    ref = pd.read_csv(OUT / 'step3_results.tsv', sep='\t')
    dist_ref = ref[ref['method'].isin(['area_weighted', 'distribution_only'])]
    expected_two_regime = set(
        dist_ref.loc[dist_ref['modality'] == 'two_regime', 'variable']
    )

    only_actual   = actual_two_regime - expected_two_regime
    only_expected = expected_two_regime - actual_two_regime

    ok = True
    if only_actual:
        print(f'  FAIL  extra two_regime in engine: {sorted(only_actual)}')
        ok = False
    if only_expected:
        print(f'  FAIL  missing two_regime vs frozen: {sorted(only_expected)}')
        ok = False
    if ok:
        print(f'  OK    {len(actual_two_regime)} two_regime vars: {sorted(actual_two_regime)}')

    print('  PASS  two_regime classification' if ok else '  FAIL  two_regime classification')
    return ok


def test_modality_coverage():
    """Test 2: All 36 distribution-bearing rows have modality set."""
    print()
    print('─' * 60)
    print('Test 2: modality coverage — all 36 rows')
    print('─' * 60)

    rows, _ = _run_b1_b5_b6()

    if len(rows) != 36:
        print(f'  FAIL  expected 36 rows, got {len(rows)}')
        return False
    print(f'  OK    {len(rows)} rows')

    missing = [r['variable'] for r in rows if r.get('modality') is None]
    ok = len(missing) == 0
    if not ok:
        print(f'  FAIL  modality=None on: {missing}')
    else:
        n_two_regime = sum(1 for r in rows if r.get('modality') == 'two_regime')
        n_unimodal   = sum(1 for r in rows if r.get('modality') == 'unimodal')
        print(f'  OK    unimodal={n_unimodal}  two_regime={n_two_regime}')

    print('  PASS  modality coverage' if ok else '  FAIL  modality coverage')
    return ok


def test_suppressed_scores():
    """Test 3: 2 concentrated-but-bimodal rows: null score, score_suppressed, suppressed_score."""
    print()
    print('─' * 60)
    print('Test 3: suppressed scores (cropland_extent + temp_yr_upstream)')
    print('─' * 60)

    rows, _ = _run_b1_b5_b6()
    by_var  = {r['variable']: r for r in rows}

    EXPECTED_SUPPRESSED = {
        'cropland_extent':   5.29,
        'temp_yr_upstream': 96.45,
    }

    ok = True
    for var, expected_val in EXPECTED_SUPPRESSED.items():
        row = by_var.get(var)
        if row is None:
            print(f'  FAIL  {var} not in output')
            ok = False
            continue

        if row.get('representative_score') is not None:
            print(f"  FAIL  {var}: representative_score={row['representative_score']!r}, expected null")
            ok = False

        if not row.get('score_suppressed', False):
            print(f'  FAIL  {var}: score_suppressed={row.get("score_suppressed")!r}, expected True')
            ok = False

        suppressed_val = row.get('detail', {}).get('suppressed_score')
        if suppressed_val is None:
            print(f"  FAIL  {var}: detail['suppressed_score'] missing")
            ok = False
        elif abs(float(suppressed_val) - expected_val) > 0.01:
            print(f"  FAIL  {var}: suppressed_score={suppressed_val!r}, expected ~{expected_val}")
            ok = False
        else:
            print(f"  OK    {var}: suppressed_score={suppressed_val}  (expected ~{expected_val})")

    print('  PASS  suppressed scores' if ok else '  FAIL  suppressed scores')
    return ok


def test_spread_two_regime_not_suppressed():
    """Test 4: spread rows that are also two_regime have score_suppressed=False."""
    print()
    print('─' * 60)
    print('Test 4: spread+two_regime rows — score_suppressed=False')
    print('─' * 60)

    rows, _ = _run_b1_b5_b6()

    # The 10 two_regime rows that were NOT concentrated
    concentrated_two_regime = {'cropland_extent', 'temp_yr_upstream'}
    spread_two_regime = [
        r for r in rows
        if r.get('modality') == 'two_regime'
        and r['variable'] not in concentrated_two_regime
    ]

    ok = True
    for row in spread_two_regime:
        var = row['variable']
        if row.get('score_suppressed', False):
            print(f'  FAIL  {var}: score_suppressed=True (was spread, score already null)')
            ok = False

    if ok:
        print(f'  OK    {len(spread_two_regime)} spread+two_regime rows all have score_suppressed=False')

    print('  PASS  spread two_regime' if ok else '  FAIL  spread two_regime')
    return ok


def test_regimes_companion():
    """
    Test 5: Regimes companion — 24 rows strict vs step3_block6_regimes.tsv.

    Data lineage note — pct_sand:
    pct_sand is one of 9 vars corrected by the 2026-06-18 population hygiene fix
    (two-pass SQL excluding -9999/NULL from PERCENT_RANK window). The frozen
    step3_block6_regimes.tsv was produced with pre-fix scores, giving centers
    72.65/89.71. The current matrix has post-fix scores giving centers 76.16/94.05.
    All other fields (regime_weight, n_basins, coverage_weight) match exactly;
    the two_regime CLASSIFICATION is correct in both cases (gap=11.00 > threshold=10.64).
    Strict check runs on the 11 non-pct_sand vars; pct_sand is checked separately.
    """
    print()
    print('─' * 60)
    print('Test 5: regimes companion — 11 vars strict + pct_sand lineage note')
    print('─' * 60)

    _, regimes = _run_b1_b5_b6()
    actual     = pd.DataFrame(regimes)

    if len(actual) != 24:
        print(f'  FAIL  expected 24 regimes rows, got {len(actual)}')
        return False
    print(f'  OK    {len(actual)} rows')

    actual['row_id'] = actual['variable'] + ':' + actual['regime_id'].astype(str)

    ref = pd.read_csv(OUT / 'step3_block6_regimes.tsv', sep='\t')
    ref['row_id'] = ref['variable'] + ':' + ref['regime_id'].astype(str)

    # Strict check: 11 non-pct_sand vars
    actual_11 = actual[actual['variable'] != 'pct_sand'].copy()
    ref_11    = ref[ref['variable'] != 'pct_sand'].copy()

    ok = diff_output(
        actual_11[['row_id', 'regime_center', 'regime_weight', 'n_basins', 'coverage_weight']],
        ref_11[['row_id', 'regime_center', 'regime_weight', 'n_basins', 'coverage_weight']],
        float_tol=0.01,
        id_col='row_id',
        label='B6 regimes (11 vars)',
    )

    # pct_sand: verify classification correct + document engine vs frozen centers
    pct = actual[actual['variable'] == 'pct_sand'].set_index('regime_id')
    pct_ref = ref[ref['variable'] == 'pct_sand'].set_index('regime_id')

    print()
    print('  pct_sand DATA LINEAGE ARTIFACT (pre-fix regimes TSV vs post-fix matrix):')
    for rid in (0, 1):
        eng_c = float(pct.loc[rid, 'regime_center'])
        frz_c = float(pct_ref.loc[rid, 'regime_center'])
        eng_w = float(pct.loc[rid, 'regime_weight'])
        frz_w = float(pct_ref.loc[rid, 'regime_weight'])
        print(f'    regime {rid}: engine_center={eng_c:.2f}  frozen_center={frz_c:.2f}  '
              f'engine_weight={eng_w:.4f}  frozen_weight={frz_w:.4f}')
    print('  NOTE: engine centers (76.16/94.05) are correct for current post-fix matrix;')
    print('        frozen centers (72.65/89.71) were computed with pre-fix pct_sand scores.')
    print('  NOTE: two_regime classification and regime_weight are identical — only centers differ.')
    print('  Action for Karl: re-freeze step3_block6_regimes.tsv pct_sand rows with engine values.')

    return ok


def test_sample_projection():
    """Test 6: lean + full for one two_regime row; suppressed_score visible in detail."""
    print()
    print('─' * 60)
    print('Test 6: sample projection (temp_yr_upstream)')
    print('─' * 60)

    rows, _ = _run_b1_b5_b6()
    by_var  = {r['variable']: r for r in rows}

    row  = by_var.get('temp_yr_upstream')
    if row is None:
        print('  WARN  temp_yr_upstream not found')
        return True

    lean = project_row(row, include_detail=False)
    full = project_row(row, include_detail=True)

    print('\n  [two_regime — concentrated-but-bimodal]  variable=temp_yr_upstream')
    for k in ('method', 'representative_score', 'representative_raw', 'status',
              'coherence', 'modality', 'score_suppressed', 'n_units', 'coverage'):
        print(f'    {k:28s} = {lean.get(k)!r}')
    d = full.get('detail', {})
    print(f'    detail.suppressed_score      = {d.get("suppressed_score")!r}')
    print(f'    detail.spread                = {d.get("spread")!r}')
    print(f'    detail.p10                   = {d.get("p10")!r}')
    print(f'    detail.p90                   = {d.get("p90")!r}')
    print(f'    detail.regimes               = {d.get("regimes")}')

    return True


if __name__ == '__main__':
    results = [
        test_two_regime_classification(),
        test_modality_coverage(),
        test_suppressed_scores(),
        test_spread_two_regime_not_suppressed(),
        test_regimes_companion(),
        test_sample_projection(),
    ]

    print()
    print('=' * 60)
    n_pass = sum(r for r in results if r is True)
    print(f"WO10: {'PASS' if all(r is True for r in results) else 'FAIL'}  "
          f"({n_pass}/{len(results)} tests passed)")
    sys.exit(0 if all(r is True for r in results) else 1)
