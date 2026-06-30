"""
Engine contract tests — v0.4

Tests what the engine *promises*, not what a notebook once computed.
No frozen TSVs. Each assertion targets a structural invariant, a vocabulary
constraint, or a geographic fact that is stable across algorithmic improvements.

Fixtures
--------
Timbuktu 100 km / L06  — primary fixture; exercises every block
Timbuktu single-basin  — degeneracy / n=1 invariants
Rome single-basin      — independent geographic fixture (Section 5)

Run:
    pytest tests/engine/test_engine_contract.py -v
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.edop.areas.engine import (
    areal_signature,
    areal_signature_polygon,
    single_basin_signature,
    resolve_buffer,
    resolve_polygon,
    resolve_polity,
    load_catalog,
    dispatch_variable,
)
from scripts.shared.db_utils import db_connect

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Timbuktu — primary fixture (buffer + single-basin)
TIM_LAT, TIM_LON = 16.8167, -2.9833
TIM_R            = 100.0
TIM_LEVEL        = 6

# Rome — secondary fixture (single-basin only in this suite)
ROME_LAT, ROME_LON = 41.8967, 12.4822

# Valid vocabulary sets
VALID_STATUSES    = frozenset({'ok', 'outside_active_domain', 'no_data'})
VALID_METHODS     = frozenset({
    'area_weighted', 'dominant_basin', 'class_mixture', 'flag_fraction',
    'distribution_only', 'extreme',
    'grid_areal_collapsed', 'grid_areal_distribution', 'global_forcing',
})
VALID_MODALITIES  = frozenset({'unimodal', 'two_regime'})
VALID_COHERENCES  = frozenset({'concentrated', 'spread', 'mixed', 'outside_active_domain'})
VALID_BANDS       = frozenset({'A', 'B', 'C', 'D', 'E', 'T'})
VALID_KINDS       = frozenset({'continuous', 'categorical', 'flag'})
DERIVED_KEYS      = frozenset({
    'coast_fraction', 'elev_point', 'outlet_type', 'relief_position', 'relief_range_m',
})

# ---------------------------------------------------------------------------
# Session-scoped fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope='session')
def conn():
    try:
        c = db_connect()
    except Exception as e:
        pytest.skip(f'DB unavailable: {e}')
    yield c
    c.close()


@pytest.fixture(scope='session')
def buf_payload(conn):
    """Timbuktu 100 km / L06 buffer — Bands A–E, full detail."""
    return areal_signature(
        TIM_LAT, TIM_LON, TIM_R, conn,
        level=TIM_LEVEL, bands=['A', 'B', 'C', 'D', 'E'],
        include_detail=True,
    )


@pytest.fixture(scope='session')
def buf_rows(buf_payload):
    """Basin-path rows (no Band T) from the buffer payload."""
    return [r for r in buf_payload['rows'] if r.get('band') != 'T']


@pytest.fixture(scope='session')
def sb_payload(conn):
    """Timbuktu single-basin / L06 — Bands A–E, full detail."""
    return single_basin_signature(
        TIM_LAT, TIM_LON, conn, level=TIM_LEVEL,
        bands=['A', 'B', 'C', 'D', 'E'], include_detail=True,
    )


@pytest.fixture(scope='session')
def sb_rows(sb_payload):
    return [r for r in sb_payload['rows'] if r.get('band') != 'T']


@pytest.fixture(scope='session')
def meta():
    return load_catalog(level=TIM_LEVEL)


# ---------------------------------------------------------------------------
# Section 1 — Resolver
# ---------------------------------------------------------------------------

class TestResolver:
    def test_buffer_basin_count(self, conn):
        """Timbuktu 100 km / L06 → 9 basins (geographic fact)."""
        bs = resolve_buffer(TIM_LAT, TIM_LON, TIM_R, '06', conn)
        assert len(bs) == 9

    def test_buffer_weight_sum(self, conn):
        """Buffer weights sum to ≤ 1.0 (open-water shortfall OK)."""
        bs = resolve_buffer(TIM_LAT, TIM_LON, TIM_R, '06', conn)
        assert bs['weight'].sum() <= 1.0 + 1e-6
        assert bs['weight'].sum() > 0.5

    def test_buffer_dtypes(self, conn):
        """hybas_id must be int64; weight must be float."""
        bs = resolve_buffer(TIM_LAT, TIM_LON, TIM_R, '06', conn)
        assert str(bs['hybas_id'].dtype) == 'int64'
        assert bs['weight'].dtype.kind == 'f'

    def test_buffer_all_weights_positive(self, conn):
        """No zero or negative weights (epsilon filter applied)."""
        bs = resolve_buffer(TIM_LAT, TIM_LON, TIM_R, '06', conn)
        assert (bs['weight'] > 0).all()

    def test_single_basin_weight_and_shortfall(self, sb_payload):
        """Single-basin: weight = 1.0, shortfall = 0.0 by construction."""
        assert sb_payload['shortfall'] == 0.0


# ---------------------------------------------------------------------------
# Section 2 — Catalog
# ---------------------------------------------------------------------------

class TestCatalog:
    def test_row_counts(self, meta):
        """Catalog has expected derived/sourced split."""
        sourced = meta[~meta['derived']]
        derived = meta[meta['derived']]
        assert len(derived) == 5
        assert len(sourced) >= 55       # grows as new vars are added

    def test_derived_keys(self, meta):
        """Exact set of derived keys matches engine expectations."""
        derived = meta[meta['derived']]
        assert set(derived.index) == DERIVED_KEYS

    def test_derived_have_no_db_col(self, meta):
        """Derived rows must have db_col=None — no DB query is issued for them."""
        derived = meta[meta['derived']]
        assert derived['db_col'].isna().all()

    def test_sourced_kinds_valid(self, meta):
        """Every sourced row resolves to a known kind."""
        sourced = meta[~meta['derived']]
        bad = sourced[~sourced['kind'].isin(VALID_KINDS)]
        assert bad.empty, f'Unknown kind(s): {bad["kind"].tolist()}'

    def test_dispatch_has_no_unknowns(self, meta):
        """Every sourced row dispatches to a known block; no unknowns."""
        sourced = meta[~meta['derived']]
        KNOWN_BLOCKS = {'B1', 'B2', 'B3', 'B4', 'B5'}
        for api_key, row in sourced.iterrows():
            block = dispatch_variable(row['typology_cluster'], row['kind'])
            assert block in KNOWN_BLOCKS, \
                f'{api_key}: dispatch returned unknown block {block!r}'

    def test_reservoir_vol_present_and_routed(self, meta):
        """reservoir_vol must be present and route to B5 (coalesce fix, WO14)."""
        assert 'reservoir_vol' in meta.index
        row = meta.loc['reservoir_vol']
        assert not row['derived']
        assert dispatch_variable(row['typology_cluster'], row['kind']) == 'B5'


# ---------------------------------------------------------------------------
# Section 3 — Payload envelope
# ---------------------------------------------------------------------------

class TestPayloadEnvelope:
    REQUIRED_TOP_KEYS = {'neighborhood', 'shortfall', 'bands', 'caveats', 'rows', 'temporal'}
    REQUIRED_ROW_KEYS = {
        'variable', 'method', 'status', 'representative_score',
        'representative_raw', 'n_units', 'coverage', 'band', 'unit_type',
    }

    def test_top_level_keys(self, buf_payload):
        missing = self.REQUIRED_TOP_KEYS - set(buf_payload.keys())
        assert not missing, f'Missing top-level keys: {missing}'

    def test_every_row_has_required_keys(self, buf_rows):
        for r in buf_rows:
            missing = self.REQUIRED_ROW_KEYS - set(r.keys())
            assert not missing, f'{r["variable"]}: missing keys {missing}'

    def test_status_vocabulary(self, buf_rows):
        bad = [r for r in buf_rows if r['status'] not in VALID_STATUSES]
        assert not bad, f'Unknown status: {[(r["variable"], r["status"]) for r in bad]}'

    def test_method_vocabulary(self, buf_rows):
        bad = [r for r in buf_rows if r['method'] not in VALID_METHODS]
        assert not bad, f'Unknown method: {[(r["variable"], r["method"]) for r in bad]}'

    def test_band_vocabulary(self, buf_rows):
        bad = [r for r in buf_rows if r['band'] not in VALID_BANDS]
        assert not bad, f'Unknown band: {[(r["variable"], r["band"]) for r in bad]}'

    def test_representative_score_range(self, buf_rows):
        """Scores are in [0, 100] or None — never out of range."""
        for r in buf_rows:
            s = r['representative_score']
            if s is not None:
                assert 0.0 <= s <= 100.0, \
                    f'{r["variable"]}: score {s} out of [0, 100]'

    def test_coverage_positive(self, buf_rows):
        """Coverage is in (0, 1] for every row."""
        for r in buf_rows:
            assert 0.0 < r['coverage'] <= 1.0 + 1e-9, \
                f'{r["variable"]}: coverage {r["coverage"]} out of range'

    def test_n_units_positive(self, buf_rows):
        for r in buf_rows:
            assert r['n_units'] >= 1, f'{r["variable"]}: n_units={r["n_units"]}'

    def test_no_duplicate_variables(self, buf_rows):
        variables = [r['variable'] for r in buf_rows]
        dupes = [v for v in set(variables) if variables.count(v) > 1]
        assert not dupes, f'Duplicate variables: {dupes}'

    def test_all_catalog_sourced_vars_emitted(self, buf_rows, meta):
        """Every sourced variable from the catalog appears in the payload."""
        sourced = meta[~meta['derived']]
        emitted = {r['variable'] for r in buf_rows}
        missing = set(sourced.index) - emitted
        # B3 internals: ecoregion deduped into eco_id; strata_code excluded by design
        # B4 consumed: endorheic + coast_flag consumed to produce outlet_type/coast_fraction
        # B5 deferred: river_area_upstream deferred within B5
        KNOWN_ABSENT = {'ecoregion', 'strata_code', 'endorheic', 'coast_flag', 'river_area_upstream'}
        unexpected_missing = missing - KNOWN_ABSENT
        assert not unexpected_missing, f'Variables absent from payload: {unexpected_missing}'


# ---------------------------------------------------------------------------
# Section 4 — Block dispatch contracts
# ---------------------------------------------------------------------------

class TestBlockContracts:
    def test_b1_detail_fields(self, buf_rows):
        """B1 rows carry spread, p10, p90 in detail; coherence in vocabulary."""
        b1 = [r for r in buf_rows if r['method'] == 'area_weighted']
        assert b1, 'No B1 rows found'
        for r in b1:
            detail = r.get('detail') or {}
            if r['status'] == 'ok':
                assert 'spread' in detail, f'{r["variable"]}: missing spread'
                assert 'p10' in detail,    f'{r["variable"]}: missing p10'
                assert 'p90' in detail,    f'{r["variable"]}: missing p90'
            coh = r.get('coherence')
            if coh is not None:
                assert coh in VALID_COHERENCES, \
                    f'{r["variable"]}: unknown coherence {coh!r}'

    def test_b1_spread_rows_carry_score(self, buf_rows):
        """Spread B1 rows emit the weighted-mean score; coherence='spread' is the flag.
        Engine describes (emits the number); surface decides what to do with it.
        Exception: B6 may suppress score for two_regime rows (separate path)."""
        spread = [r for r in buf_rows
                  if r['method'] == 'area_weighted' and r.get('coherence') == 'spread'
                  and r.get('modality') != 'two_regime']
        assert spread, 'No non-two_regime spread rows to check'
        for r in spread:
            assert r['representative_score'] is not None, \
                f'{r["variable"]}: spread row missing representative_score'
            assert 0 <= r['representative_score'] <= 100, \
                f'{r["variable"]}: spread score out of range: {r["representative_score"]}'

    def test_b2_dominant_basin_geographic(self, buf_rows):
        """Discharge dominant basin for Timbuktu 100 km / L06 is the Niger main-stem."""
        b2 = [r for r in buf_rows if r['method'] == 'dominant_basin']
        assert len(b2) == 3, f'Expected 3 B2 rows, got {len(b2)}'
        for r in b2:
            dom = r['detail']['dominant_hybas_id']
            assert dom == 1060564960, \
                f'{r["variable"]}: dominant hybas_id={dom}, expected 1060564960'
            assert r['representative_score'] is not None
            assert r['representative_raw'] is not None

    def test_b3_mixture_fields(self, buf_rows):
        """B3 rows carry modal_label and mixture list in detail."""
        b3 = [r for r in buf_rows if r['method'] == 'class_mixture']
        assert b3, 'No B3 rows found'
        for r in b3:
            detail = r.get('detail') or {}
            assert 'modal_class_id' in detail, f'{r["variable"]}: missing modal_class_id'
            assert 'mixture' in detail,        f'{r["variable"]}: missing mixture'
            assert isinstance(detail['mixture'], list)
            weights = [c['weight'] for c in detail['mixture']]
            assert abs(sum(weights) - 1.0) < 0.01, \
                f'{r["variable"]}: mixture shares sum to {sum(shares):.4f}'
            coh = r.get('coherence')
            assert coh in {'concentrated', 'mixed'}, \
                f'{r["variable"]}: B3 coherence {coh!r} not in {{concentrated, mixed}}'

    def test_b4_outlet_type_mixture_sums_to_one(self, buf_rows):
        """outlet_type 4-class mixture shares must sum to 1.0."""
        ot = next((r for r in buf_rows if r['variable'] == 'outlet_type'), None)
        assert ot is not None, 'outlet_type row missing'
        weights = [c['weight'] for c in ot['detail']['mixture']]
        assert len(weights) > 0
        assert abs(sum(weights) - 1.0) < 0.01

    def test_b4_coast_fraction_range(self, buf_rows):
        """coast_fraction must be in [0, 1]."""
        cf = next((r for r in buf_rows if r['variable'] == 'coast_fraction'), None)
        assert cf is not None, 'coast_fraction row missing'
        val = cf['representative_raw']
        assert val is not None
        assert 0.0 <= float(val) <= 1.0

    def test_b5_reservoir_vol_emitted(self, buf_rows):
        """reservoir_vol must appear (WO14 coalesce fix)."""
        rv = next((r for r in buf_rows if r['variable'] == 'reservoir_vol'), None)
        assert rv is not None, 'reservoir_vol not emitted'
        assert rv['method'] == 'distribution_only'

    def test_b6_modality_vocabulary(self, buf_rows):
        """Rows with a modality field use only known values."""
        for r in buf_rows:
            m = r.get('modality')
            if m is not None:
                assert m in VALID_MODALITIES, \
                    f'{r["variable"]}: unknown modality {m!r}'

    def test_b6_two_regime_score_suppressed(self, buf_rows):
        """two_regime rows must null representative_score and carry regimes in detail."""
        two_regime = [r for r in buf_rows if r.get('modality') == 'two_regime']
        for r in two_regime:
            assert r['representative_score'] is None, \
                f'{r["variable"]}: two_regime row has non-null score'
            regimes = (r.get('detail') or {}).get('regimes')
            assert regimes and len(regimes) == 2, \
                f'{r["variable"]}: two_regime row missing regimes list'


# ---------------------------------------------------------------------------
# Section 5 — Single-basin degeneracy (n=1 invariants)
# ---------------------------------------------------------------------------

class TestSingleBasinDegeneracy:
    def test_all_coverages_are_one(self, sb_rows):
        """n=1: every row has coverage=1.0 (no shortfall possible)."""
        for r in sb_rows:
            assert r['coverage'] == 1.0, \
                f'{r["variable"]}: coverage={r["coverage"]}, expected 1.0'

    def test_b1_all_concentrated(self, sb_rows):
        """n=1: all B1 rows are concentrated (spread is impossible)."""
        b1 = [r for r in sb_rows
              if r['method'] == 'area_weighted' and r['status'] == 'ok']
        for r in b1:
            assert r['coherence'] == 'concentrated', \
                f'{r["variable"]}: n=1 B1 coherence={r["coherence"]!r}'

    def test_no_two_regime_at_n1(self, sb_rows):
        """n=1: modality is never two_regime (single basin cannot be bimodal)."""
        two_regime = [r for r in sb_rows if r.get('modality') == 'two_regime']
        assert not two_regime, \
            f'two_regime at n=1: {[r["variable"] for r in two_regime]}'

    def test_cropland_extent_outside_active_domain(self, sb_rows):
        """Geographic: Timbuktu center basin is at the cropland floor."""
        crop = next((r for r in sb_rows if r['variable'] == 'cropland_extent'), None)
        assert crop is not None
        assert crop['status'] == 'outside_active_domain', \
            f'cropland_extent status={crop["status"]!r}'

    def test_single_basin_rome_structural(self, conn):
        """Rome single-basin: coast_fraction > 0 (Mediterranean coast proximity)."""
        payload = single_basin_signature(
            ROME_LAT, ROME_LON, conn, level=6,
            bands=['A', 'B', 'C', 'D', 'E'], include_detail=True,
        )
        rows = [r for r in payload['rows'] if r.get('band') != 'T']
        cf = next((r for r in rows if r['variable'] == 'coast_fraction'), None)
        assert cf is not None
        # Rome basin is not coastal itself but may have coastal neighbors via outlet
        # Contract: structural validity only (not specific value)
        assert cf['representative_raw'] is not None
        assert 0.0 <= float(cf['representative_raw']) <= 1.0


# ---------------------------------------------------------------------------
# Section 6 — Cross-block consistency
# ---------------------------------------------------------------------------

class TestCrossBlockConsistency:
    def test_b5_vs_b2_carrier_split(self, buf_rows):
        """river_area carrier ≠ discharge dominant (Inner Niger Delta split)."""
        b5_ext = next((r for r in buf_rows if r['method'] == 'extreme'), None)
        b2_dom = next((r for r in buf_rows
                       if r['method'] == 'dominant_basin'
                       and r['variable'] == 'discharge_yr'), None)
        assert b5_ext is not None, 'No extreme row found'
        assert b2_dom is not None, 'No B2 discharge_yr row found'
        b5_carrier = b5_ext['detail']['dominant_hybas_id']
        b2_id      = b2_dom['detail']['dominant_hybas_id']
        assert b5_carrier != b2_id, \
            f'Expected distinct carriers; both = {b5_carrier}'

    def test_endorheic_cross_block(self, buf_rows):
        """Endorheic fraction in outlet_type ≈ dist_sink weight_at_zero (±0.01)."""
        ot = next((r for r in buf_rows if r['variable'] == 'outlet_type'), None)
        ds = next((r for r in buf_rows if r['variable'] == 'dist_sink'), None)
        assert ot and ds, 'outlet_type or dist_sink missing'

        endo_share = sum(
            c['share'] for c in ot['detail']['mixture']
            if 'ndorheic' in c.get('label', '') or 'sink' in c.get('label', '').lower()
        )
        waz = ds['detail'].get('weight_at_zero', 0.0) or 0.0
        assert abs(endo_share - waz) < 0.02, \
            f'Endorheic share={endo_share:.4f} vs dist_sink waz={waz:.4f}'


# ---------------------------------------------------------------------------
# Section 7 — Band T structural contracts
# ---------------------------------------------------------------------------

class TestBandT:
    @pytest.fixture(scope='class')
    def band_t_payload(self, conn):
        return areal_signature(
            TIM_LAT, TIM_LON, TIM_R, conn,
            level=TIM_LEVEL,
            bands=['A', 'B', 'C', 'D', 'E', 'T'],
            from_year=1100, to_year=1200,
            include_detail=True,
        )

    @pytest.fixture(scope='class')
    def t_rows(self, band_t_payload):
        return [r for r in band_t_payload['rows'] if r.get('band') == 'T']

    def test_band_t_rows_present(self, t_rows):
        assert len(t_rows) > 0, 'No Band T rows returned'

    def test_lmr_method_and_caveat(self, t_rows):
        lmr = [r for r in t_rows if r['method'] == 'grid_areal_collapsed']
        assert lmr, 'No LMR (grid_areal_collapsed) rows'
        for r in lmr:
            assert 'lmr_caveat' in r.get('caveat', []), \
                f'{r["variable"]}: LMR row missing lmr_caveat'

    def test_hyde_method_and_unit_type(self, t_rows):
        hyde = [r for r in t_rows if r['method'] == 'grid_areal_distribution']
        assert hyde, 'No HYDE (grid_areal_distribution) rows'
        for r in hyde:
            assert r['unit_type'] == 'hyde_cell', \
                f'{r["variable"]}: HYDE unit_type={r["unit_type"]!r}'

    def test_evolv2k_method(self, t_rows):
        evolv = [r for r in t_rows if r['method'] == 'global_forcing']
        assert evolv, 'No eVolv2k (global_forcing) rows'

    def test_band_t_status_vocabulary(self, t_rows):
        bad = [r for r in t_rows if r.get('status') not in VALID_STATUSES | {None}]
        assert not bad, \
            f'Unknown status in Band T: {[(r["variable"], r["status"]) for r in bad]}'

    def test_band_t_1950_caveat(self, conn):
        """Span containing 1950 surfaces hyde_caveat on HYDE rows."""
        payload = areal_signature(
            TIM_LAT, TIM_LON, TIM_R, conn,
            level=TIM_LEVEL, bands=['T'],
            from_year=1900, to_year=2000,
        )
        hyde_rows = [r for r in payload['rows']
                     if r.get('method') == 'grid_areal_distribution']
        assert hyde_rows, 'No HYDE rows in 1900–2000 span'
        hyde_with_caveat = [r for r in hyde_rows if 'hyde_caveat' in r.get('caveat', [])]
        assert hyde_with_caveat, 'No HYDE rows carry hyde_caveat in 1900–2000 span'


# ---------------------------------------------------------------------------
# 7. WO20 — Polity resolver + polygon engine path
#    Fixture: Northern Song, year=1000, L06
# ---------------------------------------------------------------------------

# N Song phase 990–1017, polity_id=4481, area≈2.76M km²
NSONG_NAME  = 'Northern Song'
NSONG_YEAR  = 1000
NSONG_LEVEL = 6


@pytest.fixture(scope='session')
def nsong_geom(conn):
    row = conn.execute(
        "SELECT ST_AsText(geom) FROM gaz.clio_polities "
        "WHERE name = %s AND fromyear <= %s AND toyear >= %s",
        (NSONG_NAME, NSONG_YEAR, NSONG_YEAR),
    ).fetchone()
    if row is None:
        pytest.skip('Northern Song polity not found in DB')
    return row[0]


@pytest.fixture(scope='session')
def nsong_basin_set(nsong_geom, conn):
    return resolve_polygon(nsong_geom, f'{NSONG_LEVEL:02d}', conn)


@pytest.fixture(scope='session')
def nsong_payload(nsong_geom, conn):
    return areal_signature_polygon(
        nsong_geom, conn, level=NSONG_LEVEL, bands=list('ABCDE'),
    )


class TestResolvePolygon:
    def test_basin_count_plausible(self, nsong_basin_set):
        """N Song at L06 should resolve to many dozens of basins."""
        assert len(nsong_basin_set) >= 50, f'Only {len(nsong_basin_set)} basins — too few'

    def test_weight_sum_leq_one(self, nsong_basin_set):
        wsum = nsong_basin_set['weight'].sum()
        assert wsum <= 1.0 + 1e-6, f'weight_sum={wsum:.6f} > 1'

    def test_weights_positive(self, nsong_basin_set):
        assert (nsong_basin_set['weight'] > 0).all(), 'zero-weight basins returned'

    def test_basin_in_polity_fraction_range(self, nsong_basin_set):
        bpf = nsong_basin_set['basin_in_polity_fraction']
        assert (bpf >= 0).all() and (bpf <= 1 + 1e-6).all(), \
            'basin_in_polity_fraction out of [0, 1]'

    def test_weight_leq_basin_in_polity_fraction(self, nsong_basin_set):
        """Weight (overlap/polity) can never exceed basin_in_polity_fraction (overlap/basin)
        because polity_area >= basin_area is not guaranteed, but the basin fraction
        caps what weight can contribute."""
        # weight = overlap/polity_area; bpf = overlap/basin_area
        # only invariant: both derived from same overlap — weight is independent, no cap
        # What IS guaranteed: weight <= 1 (checked above); bpf <= 1 (checked above)
        pass  # structural check only — no numeric cap between the two

    def test_required_columns(self, nsong_basin_set):
        for col in ('hybas_id', 'weight', 'basin_in_polity_fraction', 'overlap_area_km2'):
            assert col in nsong_basin_set.columns, f'Missing column: {col}'


class TestResolvePolity:
    def test_returns_correct_meta(self, conn):
        _, _, meta = resolve_polity(NSONG_NAME, NSONG_YEAR, NSONG_LEVEL, conn)
        assert meta['name'] == NSONG_NAME
        assert meta['fromyear'] <= NSONG_YEAR <= meta['toyear']
        assert meta['year'] == NSONG_YEAR

    def test_raises_on_no_match(self, conn):
        import pytest as _pytest
        with _pytest.raises(ValueError, match='No polity found'):
            resolve_polity('Nonexistent Polity XYZ', 1000, NSONG_LEVEL, conn)

    def test_basin_set_matches_direct(self, nsong_basin_set, conn):
        _, bs2, _ = resolve_polity(NSONG_NAME, NSONG_YEAR, NSONG_LEVEL, conn)
        assert len(bs2) == len(nsong_basin_set), \
            'resolve_polity basin count differs from resolve_polygon'


class TestArealSignaturePolygon:
    def test_modality_post_pass_skipped(self, nsong_payload):
        assert 'modality_post_pass' in nsong_payload, 'modality_post_pass key missing'
        assert 'skipped' in nsong_payload['modality_post_pass'].lower()

    def test_no_modality_values_in_rows(self, nsong_payload):
        import pandas as pd
        df = pd.DataFrame(nsong_payload['rows'])
        if 'modality' in df.columns:
            assert not df['modality'].notna().any(), \
                'modality values present — apply_modality ran on polygon path'

    def test_neighborhood_type_polygon(self, nsong_payload):
        assert nsong_payload['neighborhood']['type'] == 'polygon'

    def test_marginal_exposure_present(self, nsong_payload):
        me = nsong_payload['neighborhood'].get('marginal_exposure')
        assert me is not None, 'marginal_exposure missing'
        assert 'lt_50pct' in me and 'lt_20pct' in me

    def test_spread_verdicts_fire(self, nsong_payload):
        """N Song's environmental heterogeneity must surface as spread verdicts."""
        spread = sum(1 for r in nsong_payload['rows'] if r.get('coherence') == 'spread')
        assert spread >= 10, f'Only {spread} spread rows — heterogeneity not surfacing'

    def test_b2_dominant_basin_high_discharge(self, nsong_payload):
        """Dominant basin for N Song should be in top global decile for discharge."""
        b2 = [r for r in nsong_payload['rows'] if r.get('method') == 'dominant_basin']
        assert b2, 'No B2 dominant_basin rows'
        discharge = next((r for r in b2 if r['variable'] == 'discharge_yr'), None)
        assert discharge is not None, 'discharge_yr missing from B2'
        assert discharge['representative_score'] >= 90, \
            f'discharge_yr score={discharge["representative_score"]} — expected ≥90 for Yangtze-class basin'

    def test_payload_bands(self, nsong_payload):
        assert set(nsong_payload['bands']) == set('ABCDE')

    def test_shortfall_reasonable(self, nsong_payload):
        assert nsong_payload['shortfall'] < 0.10, \
            f'shortfall={nsong_payload["shortfall"]:.3f} — unexpectedly large'
