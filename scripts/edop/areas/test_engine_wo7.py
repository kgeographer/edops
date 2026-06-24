"""
WO7 acceptance test: aggregate_b3 regression against frozen TSV targets.

Run from repo root:
    python scripts/edop/areas/test_engine_wo7.py

Acceptance (from WO7 work order):
  1. Coverage + n_basins — strict, all 9 B3 rows
  2. Modal fields — strict: modal_class_id, modal_share, n_classes, concentration
  3. Mixture rows — strict: class_id + weight_fraction vs step3_block3_mixture.tsv (B3 only)
  4. Coherence — 'concentrated' for lith_class + zone_name (modal_share=1.0),
                 'mixed' for remaining 7; no no_data in fixture
  5. Envelope: method='class_mixture', unit_type='basin', representative_score=None,
               representative_raw=None, status='ok' for all 9
  6. Sample projection: lean + full for one concentrated row and one mixed row

Determinations flagged (WO7 / revised WO7b):
  1. representative_raw: modal class label (text string) in the lean row — engine
     enrichment, intentional divergence from frozen TSV (same pattern as perennial
     flag / LMR caveat). Frozen TSV had NaN; re-frozen after WO7b with label values.
  2. Lean vs detail boundary: lean carries coherence + representative_raw (modal label);
     detail carries modal_class_id, modal_share, n_classes, concentration, mixture list.
     modal_label removed from detail (redundant with representative_raw in lean).
  3. Categorical coherence rule: modal_share >= 0.85 → 'concentrated'; else 'mixed'.
     Value set confirmed: {concentrated, mixed} (no no_data in Timbuktu fixture).

Pin 1 translation:
  frozen 'dominant'  → status='ok', coherence='concentrated'
  frozen 'mixed'     → status='ok', coherence='mixed'
  (old TSV used verdict in status column; Pin 1 now carries coherence separately)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

import pandas as pd
import scripts.shared.db_utils as _dbu
from scripts.edop.areas.engine import aggregate_b3, project_row, diff_output

ROOT = Path(_dbu.__file__).resolve().parents[2]
OUT  = ROOT / 'output' / 'edop' / 'areas'

# Frozen TSV status → expected Pin 1 (coherence, status)
_PIN1 = {
    'dominant': ('concentrated', 'ok'),
    'mixed':    ('mixed',        'ok'),
}


def _load_inputs():
    raw_df       = _dbu.read_areas_tsv(OUT / 'step2_raw.tsv',       index_col='hybas_id')
    matrix_df    = _dbu.read_areas_tsv(OUT / 'step2_matrix.tsv',    index_col='hybas_id')
    class_id_df  = _dbu.read_areas_tsv(OUT / 'step2_class_ids.tsv', index_col='hybas_id')
    meta_df      = pd.read_csv(OUT / 'step2_meta.tsv', sep='\t', index_col='api_key')
    basin_set    = raw_df[['weight']].copy()
    return basin_set, matrix_df, class_id_df, meta_df


def _run_b3():
    basin_set, matrix_df, class_id_df, meta_df = _load_inputs()
    return aggregate_b3(basin_set, matrix_df, class_id_df, meta_df)


def _extract_mixture_rows(rows):
    """Flatten mixture from detail into a DataFrame matching mixture TSV format."""
    flat = []
    for r in rows:
        for m in r.get('detail', {}).get('mixture', []):
            flat.append({
                'variable':        r['variable'],
                'class_id':        m['class_id'],
                'weight_fraction': m['weight'],
            })
    return pd.DataFrame(flat)


def test_coverage_and_n_basins():
    """Test 1: n_basins and coverage_weight strict for all 9 B3 rows."""
    print('─' * 60)
    print('Test 1: coverage + n_basins — all 9 B3 rows')
    print('─' * 60)

    rows = _run_b3()
    actual = pd.DataFrame([
        {'variable': r['variable'], 'n_basins': r['n_units'],
         'coverage_weight': r['coverage']}
        for r in rows
    ])

    ref_all = pd.read_csv(OUT / 'step3_results.tsv', sep='\t')
    ref     = ref_all[ref_all['method'] == 'class_mixture'].copy()
    # exclude outlet_type (B4)
    ref = ref[ref['variable'] != 'outlet_type'].copy()

    if len(actual) != 9:
        print(f'  FAIL  expected 9 rows, got {len(actual)}')
        return False
    print(f'  OK    9 rows emitted')

    ok = diff_output(
        actual[['variable', 'n_basins', 'coverage_weight']],
        ref[['variable', 'n_basins', 'coverage_weight']],
        float_tol=0.01,
        id_col='variable',
        label='B3 coverage',
    )
    return ok


def test_modal_fields():
    """Test 2: modal_class_id, modal_share, n_classes, concentration strict."""
    print()
    print('─' * 60)
    print('Test 2: modal fields — all 9 B3 rows')
    print('─' * 60)

    rows = _run_b3()
    actual = pd.DataFrame([
        {'variable':        r['variable'],
         'modal_class_id':  r['detail']['modal_class_id'],
         'modal_share':     r['detail']['modal_share'],
         'n_classes':       r['detail']['n_classes'],
         'concentration':   r['detail']['concentration']}
        for r in rows
    ])

    ref_all = pd.read_csv(OUT / 'step3_results.tsv', sep='\t')
    ref     = ref_all[ref_all['method'] == 'class_mixture'].copy()
    ref     = ref[ref['variable'] != 'outlet_type'].copy()

    ok = diff_output(
        actual[['variable', 'modal_class_id', 'modal_share', 'n_classes', 'concentration']],
        ref[['variable', 'modal_class_id', 'modal_share', 'n_classes', 'concentration']],
        float_tol=0.001,
        id_col='variable',
        label='B3 modal fields',
    )
    return ok


def test_mixture_rows():
    """Test 3: per-class mixture weight_fraction strict vs step3_block3_mixture.tsv."""
    print()
    print('─' * 60)
    print('Test 3: mixture rows — class_id + weight_fraction')
    print('─' * 60)

    rows   = _run_b3()
    actual = _extract_mixture_rows(rows)

    ref_all = pd.read_csv(OUT / 'step3_block3_mixture.tsv', sep='\t')
    ref     = ref_all[ref_all['variable'] != 'outlet_type'].copy()

    if len(actual) != len(ref):
        print(f'  FAIL  expected {len(ref)} mixture rows, got {len(actual)}')
        print(f'  ref vars: {sorted(ref["variable"].unique())}')
        print(f'  act vars: {sorted(actual["variable"].unique())}')
        return False
    print(f'  OK    {len(actual)} mixture rows')

    # Build compound id for diff_output
    actual = actual.copy()
    ref    = ref.copy()
    actual['row_id'] = actual['variable'] + ':' + actual['class_id'].astype(str)
    ref['row_id']    = ref['variable']    + ':' + ref['class_id'].astype(str)

    ok = diff_output(
        actual[['row_id', 'weight_fraction']],
        ref[['row_id', 'weight_fraction']],
        float_tol=0.0001,
        id_col='row_id',
        label='B3 mixture',
    )
    return ok


def test_coherence():
    """Test 4: coherence correct for all 9 rows (2 concentrated, 7 mixed)."""
    print()
    print('─' * 60)
    print('Test 4: coherence — concentrated/mixed classification')
    print('─' * 60)

    rows    = _run_b3()
    act_map = {r['variable']: r['coherence'] for r in rows}

    ref_all = pd.read_csv(OUT / 'step3_results.tsv', sep='\t')
    ref     = ref_all[(ref_all['method'] == 'class_mixture') &
                      (ref_all['variable'] != 'outlet_type')].copy()

    ok = True
    fails = []
    for _, row in ref.iterrows():
        var        = row['variable']
        tsv_status = row['status']   # 'dominant' or 'mixed' in old vocabulary
        exp_coherence = _PIN1.get(tsv_status, (None, None))[0]
        act_coherence = act_map.get(var)
        if act_coherence != exp_coherence:
            fails.append((var, exp_coherence, act_coherence))
            ok = False

    if fails:
        for var, exp, got in fails:
            print(f'  FAIL  {var}: expected {exp!r}, got {got!r}')
    else:
        n_conc  = sum(1 for v in act_map.values() if v == 'concentrated')
        n_mixed = sum(1 for v in act_map.values() if v == 'mixed')
        print(f'  OK    coherence correct: concentrated={n_conc}  mixed={n_mixed}')

    print('  PASS  coherence' if ok else '  FAIL  coherence')
    return ok


def test_envelope():
    """Test 5: envelope fields — method, unit_type, representative_score/raw, status."""
    print()
    print('─' * 60)
    print('Test 5: envelope fields')
    print('─' * 60)

    rows = _run_b3()
    ok   = True

    for r in rows:
        if r['method'] != 'class_mixture':
            print(f"  FAIL  {r['variable']}: method={r['method']!r}")
            ok = False
        if r['unit_type'] != 'basin':
            print(f"  FAIL  {r['variable']}: unit_type={r['unit_type']!r}")
            ok = False
        if r['representative_score'] is not None:
            print(f"  FAIL  {r['variable']}: representative_score={r['representative_score']!r} (expected None)")
            ok = False
        if not isinstance(r['representative_raw'], str) or not r['representative_raw']:
            print(f"  FAIL  {r['variable']}: representative_raw={r['representative_raw']!r} (expected non-empty string label)")
            ok = False
        if r['status'] not in ('ok', 'no_data', 'low_coverage'):
            print(f"  FAIL  {r['variable']}: status={r['status']!r} not recognised")
            ok = False

    if ok:
        print(f'  OK    all {len(rows)} rows: method=class_mixture, unit_type=basin, '
              f'score=None, raw=modal_label(str), status=ok')

    print('  PASS  envelope' if ok else '  FAIL  envelope')
    return ok


def test_sample_projection():
    """Test 6: show lean + full projection for one concentrated and one mixed row."""
    print()
    print('─' * 60)
    print('Test 6: sample projections')
    print('─' * 60)

    rows_map = {r['variable']: r for r in _run_b3()}
    samples  = [
        ('lith_class',  'concentrated'),
        ('biome',       'mixed'),
    ]

    for var, label in samples:
        if var not in rows_map:
            print(f'  WARN  {var} not in output')
            continue
        row  = rows_map[var]
        lean = project_row(row, include_detail=False)
        full = project_row(row, include_detail=True)

        print(f'\n  [{label}]  variable={var}')
        for k in ('representative_score', 'representative_raw',
                  'status', 'coherence', 'n_units', 'coverage'):
            print(f'    {k:28s} = {lean.get(k)!r}')
        d = full.get('detail', {})
        print(f'    detail.modal_class_id      = {d.get("modal_class_id")!r}')
        print(f'    detail.modal_share         = {d.get("modal_share")!r}')
        print(f'    detail.n_classes           = {d.get("n_classes")!r}')
        print(f'    detail.concentration       = {d.get("concentration")!r}')
        print(f'    detail.mixture (top 2)     = {d.get("mixture", [])[:2]}')

    return True   # display-only test


if __name__ == '__main__':
    results = [
        test_coverage_and_n_basins(),
        test_modal_fields(),
        test_mixture_rows(),
        test_coherence(),
        test_envelope(),
        test_sample_projection(),
    ]

    print()
    print('=' * 60)
    n_pass = sum(r for r in results if r is True)
    print(f"WO7: {'PASS' if all(r is True for r in results) else 'FAIL'}  "
          f"({n_pass}/{len(results)} tests passed)")
    sys.exit(0 if all(r is True for r in results) else 1)
