"""The `sources` block on the public basin path (regionality WO-04, Part D). The pinned elevation lookup keeps it offline."""
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from tests.regionality import baseline as bl


@pytest.fixture(scope="module")
def client():
    from app.main import app
    return TestClient(app)


def _get(client, elevation=None, **params):
    with patch('app.db.signature.get_elevation_point', return_value=dict(elevation or bl.PINNED_ELEVATION)):
        r = client.get('/api/signature', params=dict(scope='basin', level=6, **bl.TIMBUKTU, **params))
    assert r.status_code == 200, r.text[:200]
    return r.json()


def _used(p):
    return [e['id'] for e in p['sources']['used']]


def _not_applied(p):
    return [(e['id'], e['reason']) for e in p['sources']['not_applied']]


def test_without_band_t_basinatlas_and_the_elevation_service(client):
    p = _get(client, bands='ABCE')
    assert _used(p) == ['basinatlas_v1', 'opentopodata_mapzen'] and p['sources']['not_applied'] == []


def test_the_fallback_elevation_service_is_credited_when_it_answered(client):
    p = _get(client, elevation=dict(bl.PINNED_ELEVATION, elev_source='open-meteo'), bands='ABCE')
    assert _used(p) == ['basinatlas_v1', 'open_meteo_elevation']


def test_band_t_in_range_uses_the_three_temporal_sources(client):
    p = _get(client, bands='ABCET', from_year=1300, to_year=1400)
    assert _used(p) == ['basinatlas_v1', 'opentopodata_mapzen', 'hyde_3_5', 'lmr_v2_1', 'evolv2k_v4']
    assert p['sources']['not_applied'] == []


def test_a_span_with_no_hyde_step_reports_hyde_not_applied_with_a_note(client):
    p = _get(client, bands='ABCET', from_year=1236, to_year=1240)
    assert _used(p) == ['basinatlas_v1', 'opentopodata_mapzen', 'lmr_v2_1', 'evolv2k_v4']
    assert _not_applied(p) == [('hyde_3_5', 'outside_span')]
    assert p['sources']['not_applied'][0]['note'] == 'no step inside the span'


def test_span_past_lmr_and_evolv2k(client):
    p = _get(client, bands='ABCET', from_year=2010, to_year=2020)
    assert _used(p) == ['basinatlas_v1', 'opentopodata_mapzen', 'hyde_3_5']
    assert _not_applied(p) == [('lmr_v2_1', 'outside_span'), ('evolv2k_v4', 'outside_span')]


@pytest.mark.parametrize('years', [(1300, 1400), (1995, 2005), (2010, 2020)])
def test_lmr_in_the_block_agrees_with_the_routes_own_lmr_status(client, years):
    p = _get(client, bands='ABCET', from_year=years[0], to_year=years[1])
    available = p['signature_bands']['T']['lmr_status'] == 'available'
    assert ('lmr_v2_1' in _used(p)) == available
