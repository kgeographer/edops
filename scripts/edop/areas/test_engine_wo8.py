"""
WO8 acceptance test: aggregate_b4 regression against frozen TSV targets.

Run from repo root:
    python scripts/edop/areas/test_engine_wo8.py

Acceptance (from WO8 work order):
  1. outlet_type mixture — strict: class_id + weight_fraction vs step3_block3_mixture.tsv
  2. outlet_type modal fields — strict: modal_class_id, modal_share, n_classes, concentration
  3. coast_fraction value — strict: representative_raw == 0.0
  4. Coherence: outlet_type='mixed' (modal_share 0.5346 < 0.85); coast_fraction=None
  5. Envelope: method, unit_type, representative_score, status (Pin 1), representative_raw
  6. Exclusivity assertion holds (coast=1 & endo>=1 → zero basins)
  7. Cross-block consistency: outlet_type endorheic fraction ≈ dist_sink weight_at_zero
  8. Sample projection: lean + full for both rows

Determinations flagged (WO8):
  - coast_fraction coherence=None — scalar flag_fraction has no concentrated/mixed concept
  - coast_fraction representative_raw=0.0 — the fraction itself (already in frozen TSV)
  - coast_fraction representative_score=None
  - outlet_type representative_raw='Exorheic, non-coastal' (modal label; WO7b convention;
    frozen TSV had NaN — re-frozen as part of WO8)

Pin 1 translation:
  frozen 'mixed'   → status='ok', coherence='mixed'   (outlet_type)
  frozen 'uniform' → status='ok', coherence=None       (coast_fraction)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

import pandas as pd
import scripts.shared.db_utils as _dbu
from scripts.edop.areas.engine import aggregate_b4, project_row, diff_output

ROOT = Path(_dbu.__file__).resolve().parents[2]
OUT  = ROOT / 'output' / 'edop' / 'areas'


def _load_inputs():
    raw_df    = _dbu.read_areas_tsv(OUT / 'step2_raw.tsv',    index_col='hybas_id')
    basin_set = raw_df[['weight']].copy()
    return basin_set, raw_df


def _run_b4():
    basin_set, raw_df = _load_inputs()
    return aggregate_b4(basin_set, raw_df)


def _rows_by_var(rows):
    return {r['variable']: r for r in rows}


def test_outlet_type_mixture():
    """Test 1: outlet_type per-class mixture strict vs step3_block3_mixture.tsv."""
    print('─' * 60)
    print('Test 1: outlet_type mixture rows')
    print('─' * 60)

    rows    = _run_b4()
    ot_row  = _rows_by_var(rows)['outlet_type']
    mixture = ot_row['detail']['mixture']

    actual = pd.DataFrame([
        {'row_id': f"outlet_type:{m['class_id']}", 'weight_fraction': m['weight']}
        for m in mixture
    ])

    ref_all = pd.read_csv(OUT / 'step3_block3_mixture.tsv', sep='\t')
    ref_ot  = ref_all[ref_all['variable'] == 'outlet_type'].copy()
    ref_ot['row_id'] = 'outlet_type:' + ref_ot['class_id'].astype(int).astype(str)

    if len(actual) != len(ref_ot):
        print(f'  FAIL  expected {len(ref_ot)} mixture rows, got {len(actual)}')
        return False
    print(f'  OK    {len(actual)} mixture rows')

    ok = diff_output(
        actual[['row_id', 'weight_fraction']],
        ref_ot[['row_id', 'weight_fraction']],
        float_tol=0.0001,
        id_col='row_id',
        label='outlet_type mixture',
    )
    return ok


def test_outlet_type_modal():
    """Test 2: outlet_type modal fields strict."""
    print()
    print('─' * 60)
    print('Test 2: outlet_type modal fields')
    print('─' * 60)

    rows   = _run_b4()
    ot_row = _rows_by_var(rows)['outlet_type']
    d      = ot_row['detail']

    actual = pd.DataFrame([{
        'variable':       'outlet_type',
        'modal_class_id': d['modal_class_id'],
        'modal_share':    d['modal_share'],
        'n_classes':      d['n_classes'],
        'concentration':  d['concentration'],
    }])

    ref_all = pd.read_csv(OUT / 'step3_results.tsv', sep='\t')
    ref     = ref_all[ref_all['variable'] == 'outlet_type'][
        ['variable', 'modal_class_id', 'modal_share', 'n_classes', 'concentration']
    ]

    ok = diff_output(actual, ref, float_tol=0.001, id_col='variable',
                     label='outlet_type modal')
    return ok


def test_coast_fraction_value():
    """Test 3: coast_fraction == 0.0 (Timbuktu: deep inland, no coastal basins)."""
    print()
    print('─' * 60)
    print('Test 3: coast_fraction value')
    print('─' * 60)

    rows   = _run_b4()
    cf_row = _rows_by_var(rows)['coast_fraction']
    val    = cf_row['representative_raw']

    ref_all = pd.read_csv(OUT / 'step3_results.tsv', sep='\t')
    ref_val = float(ref_all[ref_all['variable'] == 'coast_fraction']['representative_raw'].iloc[0])

    ok = True
    if abs(float(val) - ref_val) > 1e-6:
        print(f'  FAIL  coast_fraction={val!r}, expected {ref_val!r}')
        ok = False
    else:
        print(f'  OK    coast_fraction={val!r}  (matches frozen TSV)')

    print('  PASS  coast_fraction' if ok else '  FAIL  coast_fraction')
    return ok


def test_coherence_and_envelope():
    """Test 4+5: coherence, envelope fields (method, unit_type, status, representative_raw)."""
    print()
    print('─' * 60)
    print('Test 4+5: coherence + envelope')
    print('─' * 60)

    rows   = _run_b4()
    by_var = _rows_by_var(rows)
    ok     = True

    # outlet_type
    ot = by_var['outlet_type']
    checks = [
        ('method',              ot['method'],              'class_mixture'),
        ('unit_type',           ot['unit_type'],           'basin'),
        ('status',              ot['status'],              'ok'),
        ('coherence',           ot['coherence'],           'mixed'),
        ('representative_score',ot['representative_score'],None),
    ]
    for field, got, exp in checks:
        if got != exp:
            print(f'  FAIL  outlet_type {field}={got!r}, expected {exp!r}')
            ok = False
    if not isinstance(ot['representative_raw'], str) or not ot['representative_raw']:
        print(f"  FAIL  outlet_type representative_raw={ot['representative_raw']!r} (expected label str)")
        ok = False
    else:
        print(f"  OK    outlet_type representative_raw={ot['representative_raw']!r}")

    # coast_fraction
    cf = by_var['coast_fraction']
    cf_checks = [
        ('method',              cf['method'],              'flag_fraction'),
        ('unit_type',           cf['unit_type'],           'basin'),
        ('status',              cf['status'],              'ok'),
        ('coherence',           cf['coherence'],           None),
        ('representative_score',cf['representative_score'],None),
    ]
    for field, got, exp in cf_checks:
        if got != exp:
            print(f'  FAIL  coast_fraction {field}={got!r}, expected {exp!r}')
            ok = False

    if ok:
        print(f'  OK    all envelope fields correct for both rows')

    print('  PASS  coherence + envelope' if ok else '  FAIL  coherence + envelope')
    return ok


def test_exclusivity():
    """Test 6: exclusivity assertion — no basin has coast=1 & endo>=1."""
    print()
    print('─' * 60)
    print('Test 6: exclusivity assertion')
    print('─' * 60)

    try:
        rows = _run_b4()
        print('  OK    exclusivity assertion passed (no coast=1 & endo>=1 basins)')
        return True
    except AssertionError as e:
        print(f'  FAIL  {e}')
        return False


def test_cross_block_consistency():
    """
    Test 7: endorheic fraction (outlet_type classes 10+20) ≈ dist_sink weight_at_zero.

    Both measure the fraction of buffer weight in endorheic/terminal-sink basins.
    dist_sink score=0.0 ↔ basin at or near a terminal sink (endo>=1).
    Expect close agreement; exact match not required (different computation paths).
    """
    print()
    print('─' * 60)
    print('Test 7: cross-block consistency (endorheic fraction vs dist_sink waz)')
    print('─' * 60)

    rows   = _run_b4()
    ot_row = _rows_by_var(rows)['outlet_type']
    mixture = ot_row['detail']['mixture']

    endo_frac = sum(m['weight'] for m in mixture if m['class_id'] in (10, 20))

    ref_all   = pd.read_csv(OUT / 'step3_results.tsv', sep='\t')
    dist_sink = ref_all[ref_all['variable'] == 'dist_sink']
    if dist_sink.empty:
        print('  SKIP  dist_sink row not found in step3_results.tsv')
        return True
    waz = float(dist_sink['weight_at_zero'].iloc[0])

    gap = abs(endo_frac - waz)
    print(f'  outlet_type endorheic fraction (10+20) = {endo_frac:.4f}')
    print(f'  dist_sink weight_at_zero               = {waz:.4f}')
    print(f'  gap                                    = {gap:.4f}')

    ok = gap < 0.02
    if ok:
        print(f'  OK    gap {gap:.4f} < 0.02 — consistent')
    else:
        print(f'  FAIL  gap {gap:.4f} >= 0.02 — unexpected divergence')

    print('  PASS  cross-block consistency' if ok else '  FAIL  cross-block consistency')
    return ok


def test_sample_projection():
    """Test 8: lean + full projection for outlet_type and coast_fraction."""
    print()
    print('─' * 60)
    print('Test 8: sample projections')
    print('─' * 60)

    rows   = _run_b4()
    by_var = _rows_by_var(rows)

    for var in ('outlet_type', 'coast_fraction'):
        row  = by_var[var]
        lean = project_row(row, include_detail=False)
        full = project_row(row, include_detail=True)

        print(f'\n  variable={var}')
        for k in ('method', 'representative_score', 'representative_raw',
                  'status', 'coherence', 'n_units', 'coverage'):
            print(f'    {k:28s} = {lean.get(k)!r}')
        d = full.get('detail', {})
        if d:
            print(f'    detail.modal_class_id      = {d.get("modal_class_id")!r}')
            print(f'    detail.modal_share         = {d.get("modal_share")!r}')
            print(f'    detail.mixture             = {d.get("mixture")}')

    return True


if __name__ == '__main__':
    results = [
        test_outlet_type_mixture(),
        test_outlet_type_modal(),
        test_coast_fraction_value(),
        test_coherence_and_envelope(),
        test_exclusivity(),
        test_cross_block_consistency(),
        test_sample_projection(),
    ]

    print()
    print('=' * 60)
    n_pass = sum(r for r in results if r is True)
    print(f"WO8: {'PASS' if all(r is True for r in results) else 'FAIL'}  "
          f"({n_pass}/{len(results)} tests passed)")
    sys.exit(0 if all(r is True for r in results) else 1)
