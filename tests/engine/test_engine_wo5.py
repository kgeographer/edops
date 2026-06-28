"""
WO5 acceptance test: aggregate_b2 regression against step3_results.tsv B2 rows.

Run via pytest:
    pytest tests/engine/test_engine_wo5.py

Acceptance (from WO5 work order):
  1. Numeric regression: representative_score, representative_raw, dominant_hybas_id
     match frozen step3_results.tsv B2 rows within float_tol=0.01.
  2. Envelope: method='dominant_basin', unit_type='basin', n_units=9, coverage=1.0,
     status='ok' (Pin 1: 'dominant' → 'ok').
  3. Projection: lean row has no 'detail'; full row includes dominant_hybas_id.
  4. Status vocabulary: all rows status ∈ {ok, outside_active_domain, no_data}.

Three flagged determinations (WO5 spec §3):
  1. Score: B2 rows carry BOTH representative_score (dominant basin percentile from
     matrix_df) and representative_raw (m³/s from raw_df). Confirmed from TSV.
  2. Perennial: discharge_min > 0 → perennial stored as detail['perennial'] on the
     discharge_min row only. Engine enrichment; not in frozen step3 TSV.
  3. n_units: frozen TSV has n_basins=9 (full buffer set, not the 1 dominant basin).
     Engine reproduces 9. The dominant basin is identified via detail['dominant_hybas_id'].
     Contract tension: n_units = "units in the selection pool," not "units contributing
     the value." Proposal: preserve n_units=9 (selection pool size) and carry
     n_contributing=1 implicitly via the dominant_hybas_id detail field.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pandas as pd
import scripts.shared.db_utils as _dbu
from scripts.edop.areas.engine import aggregate_b2, project_row, diff_output

ROOT = Path(_dbu.__file__).resolve().parents[2]
OUT  = ROOT / 'output' / 'edop' / 'areas'

VALID_STATUSES = {'ok', 'no_data', 'outside_active_domain'}


def _load_inputs():
    """Load frozen step2 TSVs; return (basin_set, matrix_df, raw_df, meta_df)."""
    raw_df    = _dbu.read_areas_tsv(OUT / 'step2_raw.tsv',    index_col='hybas_id')
    matrix_df = _dbu.read_areas_tsv(OUT / 'step2_matrix.tsv', index_col='hybas_id')
    meta_df   = pd.read_csv(OUT / 'step2_meta.tsv', sep='\t', index_col='api_key')
    basin_set = raw_df[['weight']].copy()
    return basin_set, matrix_df, raw_df, meta_df


def _run_b2():
    basin_set, matrix_df, raw_df, meta_df = _load_inputs()
    return aggregate_b2(basin_set, matrix_df, raw_df, meta_df)


def _flatten_b2(rows):
    """Flatten make_row list → DataFrame; extract dominant_hybas_id from detail."""
    flat = []
    for r in rows:
        d = {k: v for k, v in r.items() if k != 'detail'}
        d['dominant_hybas_id'] = r.get('detail', {}).get('dominant_hybas_id')
        flat.append(d)
    return pd.DataFrame(flat)


def test_regression():
    """Test 1: strict numeric regression against frozen step3_results.tsv B2 rows."""
    print('─' * 60)
    print('Test 1: numeric regression vs. step3_results.tsv B2 rows')
    print('─' * 60)

    rows   = _run_b2()
    actual = _flatten_b2(rows)
    actual = actual.rename(columns={'n_units': 'n_basins', 'coverage': 'coverage_weight'})

    ref_all = _dbu.read_areas_tsv(OUT / 'step3_results.tsv')
    ref     = ref_all[ref_all['method'] == 'dominant_basin'].copy()
    # Pin 1 translation: old status 'dominant' → 'ok'
    ref['status'] = 'ok'

    compare_cols = [
        'variable', 'method', 'status',
        'representative_score', 'representative_raw',
        'n_basins', 'coverage_weight', 'dominant_hybas_id',
    ]

    ok = diff_output(
        actual[compare_cols],
        ref[compare_cols],
        float_tol=0.01,
        id_col='variable',
        label='B2 regression',
    )
    assert ok


def test_envelope():
    """Test 2: verify make_row envelope fields."""
    print()
    print('─' * 60)
    print('Test 2: envelope fields')
    print('─' * 60)

    rows = _run_b2()
    ok   = True

    if len(rows) != 3:
        print(f'  FAIL  expected 3 rows, got {len(rows)}')
        assert False
    print(f'  OK    3 rows emitted')

    for r in rows:
        if r['method'] != 'dominant_basin':
            print(f"  FAIL  {r['variable']}: method={r['method']!r}, expected 'dominant_basin'")
            ok = False
        if r['unit_type'] != 'basin':
            print(f"  FAIL  {r['variable']}: unit_type={r['unit_type']!r}, expected 'basin'")
            ok = False
        if r['n_units'] != 9:
            print(f"  FAIL  {r['variable']}: n_units={r['n_units']}, expected 9 (full set)")
            ok = False
        if r['coverage'] != 1.0:
            print(f"  FAIL  {r['variable']}: coverage={r['coverage']}, expected 1.0")
            ok = False
        if r['status'] != 'ok':
            print(f"  FAIL  {r['variable']}: status={r['status']!r}, expected 'ok'")
            ok = False
        if r.get('detail', {}).get('dominant_hybas_id') != 1060564960:
            print(f"  FAIL  {r['variable']}: dominant_hybas_id mismatch")
            ok = False

    if ok:
        print('  OK    method, unit_type, n_units, coverage, status, dominant_hybas_id all correct')

    # Verify perennial flag on discharge_min only
    disc_min = next((r for r in rows if r['variable'] == 'discharge_min'), None)
    disc_yr  = next((r for r in rows if r['variable'] == 'discharge_yr'),  None)
    if disc_min is None:
        print('  FAIL  discharge_min row missing')
        ok = False
    else:
        perennial = disc_min.get('detail', {}).get('perennial')
        if perennial is not True:
            print(f'  FAIL  discharge_min detail.perennial={perennial!r}, expected True')
            ok = False
        else:
            print(f'  OK    discharge_min detail.perennial=True  (discharge_min 301.82 m³/s > 0)')

    if disc_yr is not None and 'perennial' in disc_yr.get('detail', {}):
        print('  FAIL  discharge_yr should NOT carry perennial flag in detail')
        ok = False
    else:
        print('  OK    perennial absent from discharge_yr detail (correct)')

    print('  PASS  envelope' if ok else '  FAIL  envelope')
    assert ok


def test_projection():
    """Test 3: lean projection strips detail; full includes dominant_hybas_id."""
    print()
    print('─' * 60)
    print('Test 3: lean vs. full projection')
    print('─' * 60)

    rows     = _run_b2()
    disc_yr  = next(r for r in rows if r['variable'] == 'discharge_yr')

    lean = project_row(disc_yr, include_detail=False)
    full = project_row(disc_yr, include_detail=True)

    print(f'\n  Lean ({len(lean)} fields — no detail):')
    for k, v in lean.items():
        print(f'    {k:30s} = {v!r}')

    print(f'\n  Full (detail block):')
    print(f'    detail = {full.get("detail")}')

    ok = ('detail' not in lean
          and 'detail' in full
          and full['detail'].get('dominant_hybas_id') == 1060564960)
    print()
    print('  PASS  lean omits detail; full carries dominant_hybas_id' if ok
          else '  FAIL  projection error')
    assert ok


def test_status_vocabulary():
    """Test 4: all rows status ∈ Pin 1 vocabulary."""
    print()
    print('─' * 60)
    print('Test 4: status vocabulary (Pin 1)')
    print('─' * 60)

    rows = _run_b2()
    bad  = [r for r in rows if r['status'] not in VALID_STATUSES]
    if bad:
        vals = {r['status'] for r in bad}
        print(f'  FAIL  unexpected status values: {vals}')
        assert False
    print(f'  OK    all {len(rows)} rows status ∈ {VALID_STATUSES}')
    print('  PASS  status vocabulary')
