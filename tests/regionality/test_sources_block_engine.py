"""The `sources` block on the engine path (regionality WO-04, Part D): what each baseline request says it drew on."""
import pytest
from fastapi.testclient import TestClient

from tests.regionality import baseline as bl


@pytest.fixture(scope="module")
def client():
    from app.main import app
    return TestClient(app)


def _block(client, name):
    return bl.fetch(client, name)['sources']


def _used(b):
    return [e['id'] for e in b['used']]


def _not_applied(b):
    return [(e['id'], e['reason']) for e in b['not_applied']]


def test_basin_request_without_band_t_uses_only_basinatlas(client):
    b = _block(client, 'timbuktu_single_basin_L6')
    assert _used(b) == ['basinatlas_v1'] and b['not_applied'] == []


def test_polity_request_also_names_cliopatria(client):
    assert _used(_block(client, 'northern_song_961_L6')) == ['basinatlas_v1', 'cliopatria']


def test_band_t_in_range_uses_all_three_temporal_sources(client):
    b = _block(client, 'timbuktu_bandT_1300_1400')
    assert _used(b) == ['basinatlas_v1', 'hyde_3_5', 'lmr_v2_1', 'evolv2k_v4']
    assert _not_applied(b) == [('geda', 'outside_footprint')]        # Timbuktu is outside GEDA's cells
    assert all('note' not in e for e in b['used'])


def test_hyde_nearest_step_is_used_with_a_note(client):
    b = _block(client, 'timbuktu_bandT_1236_1240')
    hyde = next(e for e in b['used'] if e['id'] == 'hyde_3_5')
    assert hyde['note'] == 'nearest step: 1200' and hyde['version'] == '3.5'


def test_band_t_past_lmr_and_evolv2k_lists_them_as_not_applied(client):
    b = _block(client, 'timbuktu_bandT_2010_2020')
    assert _used(b) == ['basinatlas_v1', 'hyde_3_5']
    assert _not_applied(b) == [('lmr_v2_1', 'outside_span'), ('evolv2k_v4', 'outside_span'), ('geda', 'outside_footprint')]


def test_polity_with_band_t(client):
    b = _block(client, 'northern_song_bandT_950_970')
    assert _used(b) == ['basinatlas_v1', 'cliopatria', 'hyde_3_5', 'lmr_v2_1', 'evolv2k_v4']
    assert next(e for e in b['used'] if e['id'] == 'hyde_3_5')['note'] == 'nearest step: 1000'
    assert _not_applied(b) == [('geda', 'outside_span')]             # the span (950-970) starts before GEDA's 1000


def test_entries_carry_citation_and_licence_and_a_missing_licence_is_null(client):
    b = _block(client, 'timbuktu_bandT_1300_1400')
    by_id = {e['id']: e for e in b['used']}
    assert by_id['basinatlas_v1']['citation'] and by_id['evolv2k_v4']['licence'] == 'CC BY 4.0'
    assert by_id['lmr_v2_1']['licence'] is None


def test_public_buffer_response_carries_the_block_at_top_level(client):
    # The public buffer/area routes pass the engine's payload through; Band T takes a single year there.
    r = client.get('/api/signature', params=dict(scope='buffer', radius_km=100, level=6, bands='ABCET',
                                                 from_year=1300, to_year=1300, **bl.TIMBUKTU))
    assert r.status_code == 200
    p = r.json()
    assert 'sources' in p and 'sources' not in p['meta']
    assert _used(p['sources']) == ['basinatlas_v1', 'hyde_3_5', 'lmr_v2_1', 'evolv2k_v4']
    assert _not_applied(p['sources']) == [('geda', 'outside_footprint')]
