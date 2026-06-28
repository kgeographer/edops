"""
WO6 acceptance test: aggregate_b1 regression against step3_results.tsv B1 rows.

Run via pytest:
    pytest tests/engine/test_engine_wo6.py

Acceptance (from WO6 work order):
  1. Distribution fields — strict, all 34 B1 rows:
       spread, p10, p90 (from detail), weight_at_zero, n_units, coverage
  2. Score / coherence — strict, 32 of 34 rows (excludes 2 concentrated-two_regime):
       representative_score, coherence matches expected from frozen status
  3. Two concentrated-two_regime rows (temp_yr_upstream, cropland_extent):
       B1 produces non-null score ≈ frozen representative_score_suppressed
  4. Envelope: method, unit_type, status (Pin 1), representative_raw=None
  5. Sample projection: lean + full for one concentrated, one spread, one outside_active_domain row

B1 vs B6 field ownership:
  B1 owns (tested here): representative_score (pre-B6), coherence, spread/p10/p90,
      weight_at_zero, n_units, coverage, status (ok|outside_active_domain).
  B6 owns (deferred to WO10): modality, score_suppressed, score-nulling on two_regime rows.

representative_raw determination: always None — native-unit means deferred per locked
decision (register, 'native-unit means' row); confirmed from frozen TSV (all B1 rows NaN).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import numpy as np
import pandas as pd
import scripts.shared.db_utils as _dbu
from scripts.edop.areas.engine import aggregate_b1, project_row, diff_output

ROOT = Path(_dbu.__file__).resolve().parents[2]
OUT  = ROOT / 'output' / 'edop' / 'areas'

VALID_STATUSES = {'ok', 'no_data', 'outside_active_domain'}

# Two_regime rows where B1 produced a concentrated score that B6 later suppressed.
# Identified from frozen TSV: representative_score_suppressed is non-null.
CONCENTRATED_TWO_REGIME = {'temp_yr_upstream', 'cropland_extent'}


def _load_inputs():
    raw_df    = _dbu.read_areas_tsv(OUT / 'step2_raw.tsv',    index_col='hybas_id')
    matrix_df = _dbu.read_areas_tsv(OUT / 'step2_matrix.tsv', index_col='hybas_id')
    meta_df   = pd.read_csv(OUT / 'step2_meta.tsv', sep='\t', index_col='api_key')
    basin_set = raw_df[['weight']].copy()
    return basin_set, matrix_df, meta_df


def _run_b1():
    basin_set, matrix_df, meta_df = _load_inputs()
    return aggregate_b1(basin_set, matrix_df, meta_df)


def _flatten_b1(rows):
    """
    Flatten make_row list → DataFrame for comparison.
    Extracts spread/p10/p90 from detail sub-block.
    Renames n_units→n_basins, coverage→coverage_weight to match frozen TSV columns.
    """
    flat = []
    for r in rows:
        d = {k: v for k, v in r.items() if k != 'detail'}
        d['n_basins']        = d.pop('n_units')
        d['coverage_weight'] = d.pop('coverage')
        d['spread'] = r.get('detail', {}).get('spread')
        d['p10']    = r.get('detail', {}).get('p10')
        d['p90']    = r.get('detail', {}).get('p90')
        flat.append(d)
    return pd.DataFrame(flat)


def _expected_coherence(tsv_status, spread):
    """
    Derive expected B1 coherence from the frozen row.

    For non-two_regime rows the status directly encodes the verdict.
    For two_regime rows the status was overwritten by B6; re-derive from spread.
    outside_active_domain rows have no coherence flag.
    """
    if tsv_status == 'outside_active_domain':
        return None
    # All other rows (concentrated, spread, two_regime): coherence from spread
    return 'concentrated' if float(spread) < 20.0 else 'spread'


def test_distribution_fields():
    """
    Test 1: distribution fields strict, all 34 B1 rows.
    Compares spread, p10, p90, weight_at_zero, n_basins, coverage_weight.
    """
    print('─' * 60)
    print('Test 1: distribution fields — all 34 B1 rows')
    print('─' * 60)

    rows   = _run_b1()
    actual = _flatten_b1(rows)

    ref_all = pd.read_csv(OUT / 'step3_results.tsv', sep='\t')
    ref     = ref_all[ref_all['method'] == 'area_weighted'].copy()

    if len(actual) != 34:
        print(f'  FAIL  expected 34 rows, got {len(actual)}')
        assert False
    print(f'  OK    34 rows emitted')

    compare_cols = ['variable', 'spread', 'p10', 'p90',
                    'weight_at_zero', 'n_basins', 'coverage_weight']

    ok = diff_output(
        actual[compare_cols],
        ref[compare_cols],
        float_tol=0.01,
        id_col='variable',
        label='B1 distribution',
    )
    assert ok


def test_score_and_coherence():
    """
    Test 2: representative_score + coherence strict for 32 rows.
    Skips the 2 concentrated-two_regime rows (their scores were suppressed by B6).
    """
    print()
    print('─' * 60)
    print('Test 2: score + coherence — 32 non-concentrated-two_regime rows')
    print('─' * 60)

    rows   = _run_b1()
    actual = _flatten_b1(rows)

    ref_all = pd.read_csv(OUT / 'step3_results.tsv', sep='\t')
    ref     = ref_all[ref_all['method'] == 'area_weighted'].copy()

    # Exclude concentrated-two_regime rows from score comparison
    compare_vars = ref[~ref['variable'].isin(CONCENTRATED_TWO_REGIME)]['variable'].tolist()
    act32 = actual[actual['variable'].isin(compare_vars)].copy()
    ref32 = ref[ref['variable'].isin(compare_vars)].copy()

    # Pin 1 translation for expected status
    def expected_status(s):
        return 'outside_active_domain' if s == 'outside_active_domain' else 'ok'

    ref32 = ref32.copy()
    ref32['expected_status'] = ref32['status'].map(expected_status)

    ok = True

    # Score comparison
    score_ok = diff_output(
        act32[['variable', 'representative_score']],
        ref32[['variable', 'representative_score']],
        float_tol=0.01,
        id_col='variable',
        label='B1 score (32 rows)',
    )
    if not score_ok:
        ok = False

    # Coherence check
    act_indexed = actual.set_index('variable')
    ref_indexed = ref.set_index('variable')
    coherence_fails = []
    for var in compare_vars:
        tsv_status = ref_indexed.loc[var, 'status']
        tsv_spread = ref_indexed.loc[var, 'spread']
        expected_c = _expected_coherence(tsv_status, tsv_spread)
        actual_c   = act_indexed.loc[var, 'coherence']
        if actual_c != expected_c:
            coherence_fails.append((var, expected_c, actual_c))

    if coherence_fails:
        for var, exp, got in coherence_fails:
            print(f'  FAIL  coherence {var}: expected {exp!r}, got {got!r}')
        ok = False
    else:
        print(f'  OK    coherence matches for all {len(compare_vars)} rows')

    # Status vocabulary check (32 non-skipped rows)
    for var in compare_vars:
        tsv_status = ref_indexed.loc[var, 'status']
        act_status = act_indexed.loc[var, 'status']
        exp_status = expected_status(tsv_status)
        if act_status != exp_status:
            print(f'  FAIL  status {var}: expected {exp_status!r}, got {act_status!r}')
            ok = False

    if ok:
        print(f'  OK    status translations correct for {len(compare_vars)} rows')

    print('  PASS  score + coherence (32 rows)' if ok else '  FAIL  score + coherence')
    assert ok


def test_two_regime_b1_inputs():
    """
    Test 3: B1 inputs for concentrated-two_regime rows.
    B1 must produce non-null score ≈ frozen representative_score_suppressed.
    """
    print()
    print('─' * 60)
    print('Test 3: concentrated-two_regime rows — B1 produces correct B6 input')
    print('─' * 60)

    rows   = _run_b1()
    actual = {r['variable']: r for r in rows}

    ref_all = pd.read_csv(OUT / 'step3_results.tsv', sep='\t')
    ref     = ref_all[ref_all['method'] == 'area_weighted'].set_index('variable')

    ok = True
    for var in CONCENTRATED_TWO_REGIME:
        if var not in actual:
            print(f'  FAIL  {var}: row missing from B1 output')
            ok = False
            continue

        row          = actual[var]
        b1_score     = row['representative_score']
        tsv_suppressed = float(ref.loc[var, 'representative_score_suppressed'])

        if b1_score is None or np.isnan(float(b1_score if b1_score is not None else float('nan'))):
            print(f'  FAIL  {var}: B1 score is null; expected ≈ {tsv_suppressed:.2f}')
            ok = False
        elif abs(float(b1_score) - tsv_suppressed) > 0.01:
            print(f'  FAIL  {var}: B1 score={b1_score:.2f} vs suppressed={tsv_suppressed:.2f} (diff > 0.01)')
            ok = False
        else:
            print(f'  OK    {var}: B1 score={b1_score:.2f} ≈ frozen suppressed={tsv_suppressed:.2f}  '
                  f'(coherence={row["coherence"]!r})')

    # Also verify these rows have coherence='concentrated' (spread < 20)
    for var in CONCENTRATED_TWO_REGIME:
        if var in actual:
            spread = actual[var].get('detail', {}).get('spread', float('nan'))
            coh    = actual[var].get('coherence')
            if spread < 20.0 and coh != 'concentrated':
                print(f'  FAIL  {var}: spread={spread:.2f} < 20 but coherence={coh!r}')
                ok = False

    print('  PASS  concentrated-two_regime B6 inputs' if ok
          else '  FAIL  concentrated-two_regime B6 inputs')
    assert ok


def test_envelope():
    """
    Test 4: envelope correctness — method, unit_type, representative_raw, status vocabulary.
    """
    print()
    print('─' * 60)
    print('Test 4: envelope fields')
    print('─' * 60)

    rows = _run_b1()
    ok   = True

    for r in rows:
        if r['method'] != 'area_weighted':
            print(f"  FAIL  {r['variable']}: method={r['method']!r}")
            ok = False
        if r['unit_type'] != 'basin':
            print(f"  FAIL  {r['variable']}: unit_type={r['unit_type']!r}")
            ok = False
        if r['representative_raw'] is not None:
            print(f"  FAIL  {r['variable']}: representative_raw={r['representative_raw']!r} (expected None)")
            ok = False
        if r['status'] not in VALID_STATUSES:
            print(f"  FAIL  {r['variable']}: status={r['status']!r} not in Pin 1 vocabulary")
            ok = False

    if ok:
        print(f'  OK    all {len(rows)} rows: method=area_weighted, unit_type=basin, '
              f'representative_raw=None, status∈Pin1')

    # Counts
    n_outside = sum(1 for r in rows if r['status'] == 'outside_active_domain')
    n_ok      = sum(1 for r in rows if r['status'] == 'ok')
    n_conc    = sum(1 for r in rows if r['coherence'] == 'concentrated')
    n_spread  = sum(1 for r in rows if r['coherence'] == 'spread')
    print(f'  Status:   outside_active_domain={n_outside}  ok={n_ok}')
    print(f'  Coherence: concentrated={n_conc}  spread={n_spread}  none={len(rows)-n_conc-n_spread}')

    # Verify counts match expectations from frozen TSV
    # (outside=3, concentrated=7 direct + 2 two_regime = 9, spread=12 direct + 10 two_regime = 22)
    if n_outside != 3:
        print(f'  FAIL  outside_active_domain count: expected 3, got {n_outside}')
        ok = False
    if n_conc != 9:
        print(f'  FAIL  concentrated count: expected 9 (7 direct + 2 two_regime), got {n_conc}')
        ok = False
    if n_spread != 22:
        print(f'  FAIL  spread count: expected 22 (12 direct + 10 two_regime), got {n_spread}')
        ok = False

    print('  PASS  envelope' if ok else '  FAIL  envelope')
    assert ok


def test_sample_projection():
    """
    Test 5: show lean + full projection for one concentrated, spread, outside_active_domain row.
    """
    print()
    print('─' * 60)
    print('Test 5: sample projections')
    print('─' * 60)

    rows    = {r['variable']: r for r in _run_b1()}
    samples = [
        ('temp_yr',           'concentrated'),
        ('runoff',            'spread'),
        ('karst',             'outside_active_domain'),
    ]

    for var, label in samples:
        if var not in rows:
            print(f'  WARN  {var} not in output')
            continue
        row  = rows[var]
        lean = project_row(row, include_detail=False)
        full = project_row(row, include_detail=True)

        print(f'\n  [{label}]  variable={var}')
        for k in ('representative_score', 'representative_raw', 'status',
                  'coherence', 'weight_at_zero', 'coverage', 'n_units'):
            print(f'    {k:28s} = {lean.get(k)!r}')
        print(f'    detail                       = {full.get("detail")}')

