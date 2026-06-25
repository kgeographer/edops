"""
WO11b capstone test: areal_signature end-to-end regression.

Run from repo root:
    python scripts/edop/areas/test_engine_wo11b.py

Fixture: Timbuktu 100 km / L06 (lat=16.8167, lon=-2.9833, r=100, level=6)
Band T span: 1100–1200 CE

Acceptance (from WO11b work order):
  1. Basin path row count = 51
  2. Basin path representative_scores strict vs step3_results.tsv (float_tol=0.01)
  3. B3 mixture detail strict vs step3_block3_mixture.tsv
  4. B5 companion distribution strict vs step3_block5_distribution.tsv
  5. B6 regimes strict vs step3_block6_regimes.tsv
  6. Band T primary row count + representative_scores vs step3b_block7_primary.tsv
  7. Payload structure: neighborhood echo, shortfall, bands, temporal, caveats present
  8. Lean + full projection sample — confirm detail gating works

Determinations:
  - Assembly is a seam-up; no new aggregation logic. All numbers must match
    per-branch regression outputs exactly (within existing WO5-WO10 tolerances).
  - B6 companion (regimes) is extracted by re-running apply_modality with the
    basin_path rows; the payload itself does not surface the regimes table.
  - B5 distribution companion is extracted by re-running aggregate_b5; same logic.
  - Blessed deviations already re-frozen in per-WO tests are honored here:
    LMR caveat, perennial flag, modal label, distribution_only coherence.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

import pandas as pd
import scripts.shared.db_utils as _dbu
from scripts.edop.areas.engine import (
    areal_signature,
    aggregate_b5, apply_modality, attach_values, load_catalog,
    resolve_buffer, diff_output,
)
from scripts.shared.db_utils import db_connect

ROOT = Path(_dbu.__file__).resolve().parents[2]
OUT  = ROOT / 'output' / 'edop' / 'areas'

# Timbuktu fixture — notebook coordinates
_LAT, _LON, _R, _LEVEL = 16.8167, -2.9833, 100, 6
_FROM, _TO = 1100, 1200


def _run_payload(conn, include_detail=True):
    return areal_signature(
        _LAT, _LON, _R, conn,
        level=_LEVEL, from_year=_FROM, to_year=_TO,
        include_detail=include_detail,
    )


def test_basin_row_count():
    """Test 1: basin-path rows = 51."""
    print('─' * 60)
    print('Test 1: basin path row count')
    print('─' * 60)

    conn = db_connect()
    try:
        payload = areal_signature(_LAT, _LON, _R, conn, level=_LEVEL, include_detail=False)
    finally:
        conn.close()

    basin_rows = [r for r in payload['rows'] if r.get('band') != 'T']
    ok = len(basin_rows) == 51
    print(f'  {"OK" if ok else "FAIL"}  basin rows={len(basin_rows)}, expected 51')
    print('  PASS  basin row count' if ok else '  FAIL  basin row count')
    return ok


def test_basin_scores():
    """Test 2: representative_scores strict vs step3_results.tsv."""
    print()
    print('─' * 60)
    print('Test 2: basin path scores vs step3_results.tsv')
    print('─' * 60)

    conn = db_connect()
    try:
        payload = areal_signature(_LAT, _LON, _R, conn, level=_LEVEL, include_detail=True)
    finally:
        conn.close()

    basin_rows = [r for r in payload['rows'] if r.get('band') != 'T']
    actual = pd.DataFrame([{
        'variable':             r['variable'],
        'method':               r['method'],
        'representative_score': r['representative_score'],
        'n_basins':             r['n_units'],
        'coverage_weight':      r['coverage'],
    } for r in basin_rows])

    ref = pd.read_csv(OUT / 'step3_results.tsv', sep='\t')
    if len(actual) != len(ref):
        print(f'  FAIL  rows: got {len(actual)}, expected {len(ref)}')
        return False

    ok = diff_output(
        actual[['variable', 'representative_score', 'n_basins', 'coverage_weight']],
        ref[['variable', 'representative_score', 'n_basins', 'coverage_weight']],
        float_tol=0.01, id_col='variable', label='basin scores',
    )
    return ok


def test_b3_mixture():
    """Test 3: B3 mixture detail strict vs step3_block3_mixture.tsv."""
    print()
    print('─' * 60)
    print('Test 3: B3 mixture detail vs step3_block3_mixture.tsv')
    print('─' * 60)

    conn = db_connect()
    try:
        payload = areal_signature(_LAT, _LON, _R, conn, level=_LEVEL, include_detail=True)
    finally:
        conn.close()

    flat = []
    for r in payload['rows']:
        if r.get('method') != 'class_mixture':
            continue
        for m in r.get('detail', {}).get('mixture', []):
            flat.append({
                'variable':        r['variable'],
                'class_id':        m['class_id'],
                'weight_fraction': m['weight'],
            })
    actual = pd.DataFrame(flat)

    ref = pd.read_csv(OUT / 'step3_block3_mixture.tsv', sep='\t')

    if len(actual) != len(ref):
        print(f'  FAIL  mixture rows: got {len(actual)}, expected {len(ref)}')
        return False
    print(f'  OK    {len(actual)} mixture rows')

    actual['row_id'] = actual['variable'] + ':' + actual['class_id'].astype(str)
    ref['row_id']    = ref['variable']    + ':' + ref['class_id'].astype(str)

    ok = diff_output(
        actual[['row_id', 'weight_fraction']],
        ref[['row_id', 'weight_fraction']],
        float_tol=0.0001, id_col='row_id', label='B3 mixture',
    )
    return ok


def test_b5_distribution_companion():
    """Test 4: B5 per-basin distribution companion vs step3_block5_distribution.tsv."""
    print()
    print('─' * 60)
    print('Test 4: B5 distribution companion vs step3_block5_distribution.tsv')
    print('─' * 60)

    # Re-run aggregate_b5 directly to get companion (not surfaced in payload)
    meta_df   = load_catalog(level=_LEVEL)
    basin_set = _dbu.read_areas_tsv(OUT / 'step2_raw.tsv',    index_col='hybas_id')[['weight']]
    matrix_df = _dbu.read_areas_tsv(OUT / 'step2_matrix.tsv', index_col='hybas_id')
    raw_df    = _dbu.read_areas_tsv(OUT / 'step2_raw.tsv',    index_col='hybas_id')

    _, companion = aggregate_b5(basin_set, matrix_df, raw_df, meta_df)
    actual = pd.DataFrame(companion)
    actual['row_id'] = actual['variable'] + ':' + actual['hybas_id'].astype(str)

    ref = pd.read_csv(OUT / 'step3_block5_distribution.tsv', sep='\t')
    ref['row_id'] = ref['variable'] + ':' + ref['hybas_id'].astype(str)

    if len(actual) != len(ref):
        print(f'  FAIL  companion rows: got {len(actual)}, expected {len(ref)}')
        return False
    print(f'  OK    {len(actual)} companion rows')

    ok = diff_output(
        actual[['row_id', 'score']],
        ref[['row_id', 'score']],
        float_tol=0.001, id_col='row_id', label='B5 companion',
    )
    return ok


def test_b6_regimes():
    """Test 5: B6 regimes companion strict vs step3_block6_regimes.tsv."""
    print()
    print('─' * 60)
    print('Test 5: B6 regimes vs step3_block6_regimes.tsv')
    print('─' * 60)

    # Re-run apply_modality directly to get regimes companion
    meta_df   = load_catalog(level=_LEVEL)
    basin_set = _dbu.read_areas_tsv(OUT / 'step2_raw.tsv',    index_col='hybas_id')[['weight']]
    matrix_df = _dbu.read_areas_tsv(OUT / 'step2_matrix.tsv', index_col='hybas_id')
    raw_df    = _dbu.read_areas_tsv(OUT / 'step2_raw.tsv',    index_col='hybas_id')

    from scripts.edop.areas.engine import aggregate_b1
    b1_rows = aggregate_b1(basin_set, matrix_df, meta_df)
    b5_rows, _ = aggregate_b5(basin_set, matrix_df, raw_df, meta_df)

    _, regimes = apply_modality(b1_rows + b5_rows, basin_set, matrix_df)
    actual = pd.DataFrame(regimes)

    ref = pd.read_csv(OUT / 'step3_block6_regimes.tsv', sep='\t')

    if len(actual) != len(ref):
        print(f'  FAIL  regimes rows: got {len(actual)}, expected {len(ref)}')
        return False
    print(f'  OK    {len(actual)} regime rows')

    actual['row_id'] = actual['variable'] + ':' + actual['regime_id'].astype(str)
    ref['row_id']    = ref['variable']    + ':' + ref['regime_id'].astype(str)

    ok = diff_output(
        actual[['row_id', 'regime_center', 'regime_weight', 'n_basins']],
        ref[['row_id', 'regime_center', 'regime_weight', 'n_basins']],
        float_tol=0.01, id_col='row_id', label='B6 regimes',
    )
    return ok


def test_band_t_primary():
    """Test 6: Band T rows vs step3b_block7_primary.tsv (1100–1200 CE)."""
    print()
    print('─' * 60)
    print('Test 6: Band T primary rows (1100–1200 CE)')
    print('─' * 60)

    conn = db_connect()
    try:
        payload = _run_payload(conn, include_detail=True)
    finally:
        conn.close()

    t_rows = [r for r in payload['rows'] if r.get('band') == 'T']
    print(f'  Band T rows in payload: {len(t_rows)}')

    actual = pd.DataFrame([{
        'variable':             r['variable'],
        'representative_score': r['representative_score'],
        'n_units':              r['n_units'],
        'coverage_weight':      r['coverage'],
        'year':                 r.get('year'),
        'epoch_year':           r.get('epoch_year'),
    } for r in t_rows])

    ref = pd.read_csv(OUT / 'step3b_block7_primary.tsv', sep='\t')

    if len(actual) != len(ref):
        print(f'  FAIL  rows: got {len(actual)}, expected {len(ref)}')
        return False
    print(f'  OK    {len(actual)} Band T rows')

    actual['row_id'] = (actual['variable'].astype(str) + ':'
                        + actual['year'].astype(str) + ':'
                        + actual['epoch_year'].astype(str))
    ref['row_id']    = (ref['variable'].astype(str) + ':'
                        + ref['year'].astype(str) + ':'
                        + ref['epoch_year'].astype(str))

    ok = diff_output(
        actual[['row_id', 'representative_score', 'n_units', 'coverage_weight']],
        ref[['row_id', 'representative_score', 'n_units', 'coverage_weight']],
        float_tol=0.01, id_col='row_id', label='Band T primary',
    )
    return ok


def test_payload_structure():
    """Test 7: payload top-level structure and key fields."""
    print()
    print('─' * 60)
    print('Test 7: payload structure')
    print('─' * 60)

    conn = db_connect()
    try:
        payload = _run_payload(conn, include_detail=False)
    finally:
        conn.close()

    ok = True
    for key in ('neighborhood', 'shortfall', 'bands', 'temporal', 'caveats', 'rows'):
        if key not in payload:
            print(f'  FAIL  missing key: {key!r}')
            ok = False
        else:
            print(f'  OK    {key} present')

    nb = payload.get('neighborhood', {})
    for field in ('type', 'lat', 'lon', 'radius_km', 'level', 'n_units', 'unit_type'):
        if field not in nb:
            print(f'  FAIL  neighborhood missing {field!r}')
            ok = False

    shortfall = payload.get('shortfall', -1)
    if not (0.0 <= shortfall <= 0.1):
        print(f'  FAIL  shortfall={shortfall!r}, expected near 0')
        ok = False
    else:
        print(f'  OK    shortfall={shortfall}')

    temporal = payload.get('temporal')
    if temporal != {'from_year': _FROM, 'to_year': _TO}:
        print(f'  FAIL  temporal={temporal!r}')
        ok = False
    else:
        print(f'  OK    temporal={temporal}')

    if ok:
        print(f'  OK    payload structure valid; '
              f'n_rows={len(payload["rows"])}, caveats={list(payload["caveats"].keys())}')

    print('  PASS  payload structure' if ok else '  FAIL  payload structure')
    return ok


def test_lean_full_projection():
    """Test 8: detail gating — lean omits detail, full includes it."""
    print()
    print('─' * 60)
    print('Test 8: lean vs full projection')
    print('─' * 60)

    conn = db_connect()
    try:
        lean_payload = _run_payload(conn, include_detail=False)
        full_payload = _run_payload(conn, include_detail=True)
    finally:
        conn.close()

    ok = True

    lean_rows = {r['variable']: r for r in lean_payload['rows']
                 if r.get('method') == 'area_weighted'}
    full_rows = {r['variable']: r for r in full_payload['rows']
                 if r.get('method') == 'area_weighted'}

    # Lean should have no 'detail' key (or empty)
    for var, row in list(lean_rows.items())[:3]:
        if 'detail' in row and row['detail']:
            print(f'  FAIL  lean row {var} has non-empty detail: {row["detail"]!r}')
            ok = False

    # Full should have detail with spread/p10/p90
    for var, row in list(full_rows.items())[:3]:
        detail = row.get('detail', {})
        if 'spread' not in detail:
            print(f'  FAIL  full row {var} detail missing spread: {detail!r}')
            ok = False

    if ok:
        sample = list(full_rows.keys())[0]
        row = full_rows[sample]
        print(f'\n  [{sample}]  method={row["method"]}  '
              f'score={row["representative_score"]:.2f}  '
              f'coherence={row["coherence"]}  modality={row["modality"]}')
        d = row.get('detail', {})
        print(f'    spread={d.get("spread"):.2f}  p10={d.get("p10"):.2f}  '
              f'p90={d.get("p90"):.2f}')
        print(f'  OK    lean/full projection gating correct')

    print('  PASS  lean/full projection' if ok else '  FAIL  lean/full projection')
    return ok


if __name__ == '__main__':
    results = [
        test_basin_row_count(),
        test_basin_scores(),
        test_b3_mixture(),
        test_b5_distribution_companion(),
        test_b6_regimes(),
        test_band_t_primary(),
        test_payload_structure(),
        test_lean_full_projection(),
    ]

    print()
    print('=' * 60)
    n_pass = sum(r for r in results if r is True)
    print(f"WO11b: {'PASS' if all(r is True for r in results) else 'FAIL'}  "
          f"({n_pass}/{len(results)} tests passed)")
    sys.exit(0 if all(r is True for r in results) else 1)
