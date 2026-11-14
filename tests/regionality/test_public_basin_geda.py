"""GEDA on the public basin route, /api/signature?scope=basin (regionality, after WO-05), against the local database.

Band T on this route returns `signature_bands.T.geda_scpdsi` (a compact series), or {status: not_applied, reason}
when the place or span is outside what GEDA can give. The route's `sources` block carries the registry's decision.
"""
import pytest
from fastapi.testclient import TestClient

from app.db.connection import db_connect
from tests.regionality import baseline as bl

SPARSE = 1060264990                                  # L6 basin: GEDA covers 0.067 of it
GEDA_EDGE = bl.GEDA_EDGE                             # a point in L6 basin 1060044120: coverage 0.498


@pytest.fixture(scope='module')
def client():
    from app.main import app
    return TestClient(app)


def sig(client, point, from_year=1150, to_year=1250, level=6, **kw):
    from unittest.mock import patch
    params = dict(scope='basin', level=level, bands='ABCET', from_year=from_year, to_year=to_year, **point, **kw)
    with patch('app.db.signature.get_elevation_point', return_value=dict(bl.PINNED_ELEVATION)):
        r = client.get('/api/signature', params=params)
    assert r.status_code == 200, r.text
    return r.json()


def block(p):
    return p['signature_bands']['T']['geda_scpdsi']


def sources(p):
    return [e['id'] for e in p['sources']['used']], [(e['id'], e['reason']) for e in p['sources']['not_applied']]


def point_in(hybas_id):
    with db_connect() as conn:
        lon, lat = conn.execute('SELECT ST_X(ST_PointOnSurface(geom)), ST_Y(ST_PointOnSurface(geom)) '
                                'FROM public.basin06 WHERE hybas_id = %s', (hybas_id,)).fetchone()
    return dict(lat=lat, lon=lon)


def test_a_place_in_the_footprint_returns_a_series(client):
    p = sig(client, bl.TBILISI)
    b = block(p)
    assert (b['status'], b['coverage']) == ('ok', pytest.approx(1.0, abs=1e-3))
    assert [s['year'] for s in b['series']] == list(range(1150, 1251)) and b['n_cells'] == 25
    assert set(b['series'][0]) == {'year', 'scpdsi', 'p10', 'p90'}
    assert b['min'] <= b['mean'] <= b['max'] and 'tree-ring' in b['caveat']
    used, not_applied = sources(p)
    assert 'geda' in used and ('geda', 'outside_footprint') not in not_applied


def test_it_matches_the_engines_single_basin_numbers(client):
    """The route runs the same GEDA block on the same polygon as /api/areas does, so the numbers agree."""
    pub = {s['year']: s for s in block(sig(client, bl.TBILISI))['series']}
    r = client.get('/api/areas', params=dict(scope='single_basin', level=6, bands='T', detail='true',
                                             from_year=1150, to_year=1250, **bl.TBILISI))
    eng = {row['year']: row for row in r.json()['rows'] if row['variable'] == 'geda_scpdsi'}
    assert set(pub) == set(eng)
    for y, s in pub.items():
        dist = eng[y]['detail']['distribution']
        assert s['scpdsi'] == pytest.approx(eng[y]['representative_raw'], abs=1e-4)
        assert (s['p10'], s['p90']) == (dist['p10'], dist['p90'])


def test_a_place_outside_the_footprint_is_not_applied(client):
    p = sig(client, bl.TIMBUKTU)
    assert block(p) == {'status': 'not_applied', 'reason': 'outside_footprint'}
    used, not_applied = sources(p)
    assert 'geda' not in used and ('geda', 'outside_footprint') in not_applied


def test_a_span_before_the_data_is_not_applied(client):
    p = sig(client, bl.TBILISI, from_year=500, to_year=900)
    assert block(p) == {'status': 'not_applied', 'reason': 'outside_span'}
    assert ('geda', 'outside_span') in sources(p)[1]


def test_a_span_straddling_the_start_returns_the_years_covered(client):
    assert [s['year'] for s in block(sig(client, bl.TBILISI, from_year=980, to_year=1010))['series']] == list(range(1000, 1011))


def test_observed_years_are_marked_from_1990(client):
    series = block(sig(client, bl.TBILISI, from_year=1985, to_year=1995))['series']
    assert [s['year'] for s in series if s.get('observed')] == list(range(1990, 1996))
    assert all('observed' not in s for s in series if s['year'] < 1990)


def test_low_coverage_is_flagged_and_noted(client):
    p = sig(client, GEDA_EDGE, from_year=1300, to_year=1400)
    assert block(p)['status'] == 'low_coverage' and block(p)['coverage'] == pytest.approx(0.498, abs=0.005)
    geda = next(e for e in p['sources']['used'] if e['id'] == 'geda')
    assert geda['note'] == 'covers 49.8% of the area'


def test_below_the_coverage_floor_is_not_applied(client):
    p = sig(client, point_in(SPARSE), from_year=1300, to_year=1400)
    assert block(p) == {'status': 'not_applied', 'reason': 'below_coverage_floor'}
    assert ('geda', 'below_coverage_floor') in sources(p)[1]


def test_level_8_works(client):
    b = block(sig(client, bl.TBILISI, level=8))
    assert b['status'] == 'ok' and len(b['series']) == 101


def test_flat_mode_carries_it_under_temporal(client):
    p = sig(client, bl.TBILISI, flat='true')
    assert p['temporal']['geda_scpdsi']['status'] == 'ok'
    assert 'T' not in p.get('signature_bands', {})


def test_without_band_t_there_is_no_geda(client):
    from unittest.mock import patch
    with patch('app.db.signature.get_elevation_point', return_value=dict(bl.PINNED_ELEVATION)):
        r = client.get('/api/signature', params=dict(scope='basin', level=6, bands='ABCE', **bl.TBILISI))
    p = r.json()
    assert 'T' not in p['signature_bands']
    assert 'geda' not in [e['id'] for e in p['sources']['used']] and p['sources']['not_applied'] == []
