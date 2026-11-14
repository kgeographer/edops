"""GEDA in the response's `sources` block (regionality WO-05), through the real routes against the local database."""
import pytest
from fastapi.testclient import TestClient

from app.db.connection import db_connect
from scripts.edop.areas.engine import aggregate_band_t
from scripts.edop.areas import source_registry
from tests.regionality import baseline as bl

EDGE, SPARSE = 1060044120, 1060264990        # L6 basins: coverage 0.498 and 0.067 (see test_source_registry_footprint)


@pytest.fixture(scope='module')
def client():
    from app.main import app
    return TestClient(app)


def point_in(hybas_id):
    with db_connect() as conn:
        lon, lat = conn.execute('SELECT ST_X(ST_PointOnSurface(geom)), ST_Y(ST_PointOnSurface(geom)) '
                                'FROM public.basin06 WHERE hybas_id = %s', (hybas_id,)).fetchone()
    return dict(lat=lat, lon=lon)


def signature(client, point, from_year=1300, to_year=1400):
    r = client.get('/api/areas', params=dict(scope='single_basin', level=6, bands='T', detail='true',
                                             from_year=from_year, to_year=to_year, **point))
    assert r.status_code == 200, r.text
    return r.json()


def ids(entries):
    return [e['id'] for e in entries]


def not_applied(block):
    return [(e['id'], e['reason']) for e in block['not_applied']]


def test_a_place_inside_the_footprint_lists_geda_as_used_with_its_credits(client):
    p = signature(client, bl.KYIV)
    assert ids(p['sources']['used']) == ['basinatlas_v1', 'hyde_3_5', 'lmr_v2_1', 'evolv2k_v4', 'geda']
    assert p['sources']['not_applied'] == []
    geda = p['sources']['used'][-1]
    assert geda['name'] == 'Great Eurasian Drought Atlas'
    assert geda['citation'] == 'Cook et al. 2024, Journal of Climate' and geda['licence'] == 'CC BY 4.0'
    assert geda['version'].startswith('Zenodo deposit') and 'note' not in geda
    assert any(r['variable'] == 'geda_scpdsi' for r in p['rows'])


def test_a_low_coverage_basin_lists_geda_as_used_with_the_coverage_note(client):
    p = signature(client, point_in(EDGE))
    geda = next(e for e in p['sources']['used'] if e['id'] == 'geda')
    assert geda['note'] == 'covers 49.8% of the area'
    assert {r['status'] for r in p['rows'] if r['variable'] == 'geda_scpdsi'} == {'low_coverage'}


def test_a_basin_below_the_coverage_floor_lists_geda_as_not_applied(client):
    p = signature(client, point_in(SPARSE))
    assert 'geda' not in ids(p['sources']['used'])
    assert ('geda', 'below_coverage_floor') in not_applied(p['sources'])
    assert not any(r['variable'] == 'geda_scpdsi' for r in p['rows'])


def test_a_span_before_the_data_lists_geda_as_not_applied_for_the_span(client):
    p = signature(client, bl.KYIV, from_year=500, to_year=900)
    assert ('geda', 'outside_span') in not_applied(p['sources'])


def test_without_band_t_geda_is_in_neither_list(client):
    r = client.get('/api/areas', params=dict(scope='single_basin', level=6, bands='ABCDE', **bl.KYIV))
    assert r.status_code == 200
    block = r.json()['sources']
    assert 'geda' not in ids(block['used']) and block['not_applied'] == []


def test_a_source_not_permitted_is_in_neither_list():
    with db_connect() as conn:
        r = aggregate_band_t(bl.KYIV['lat'], bl.KYIV['lon'], 100, 1300, 1400, conn,
                             permitted={'hyde_3_5', 'lmr_v2_1', 'evolv2k_v4'})
    block = source_registry.sources_block(r.decisions, used=['basinatlas_v1'], notes=r.notes)
    assert 'geda' not in ids(block['used']) and block['not_applied'] == []
    assert not any(row['variable'] == 'geda_scpdsi' for row in r.rows)


def test_the_public_buffer_route_carries_geda_rows_and_the_sources_entry(client):
    # The public buffer/area routes pass the engine's payload through; Band T takes a single year there.
    r = client.get('/api/signature', params=dict(scope='buffer', radius_km=100, level=6, bands='ABCET',
                                                 from_year=1300, to_year=1300, **bl.KYIV))
    assert r.status_code == 200
    p = r.json()
    assert 'geda' in ids(p['sources']['used']) and 'sources' not in p['meta']
    geda = [v for v in p['variables'] if v['variable'] == 'geda_scpdsi']
    assert [v['year'] for v in geda] == [1300]
