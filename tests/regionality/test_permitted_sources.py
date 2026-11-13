"""The permitted-sources option on aggregate_band_t (regionality WO-04, Part C): a source outside the set is not consulted.

Calls the engine directly against the local database. The half of the WO's test about the response's `sources` block
(LMR in neither list) is added with Part D.
"""
import pytest

from app.db.connection import db_connect
from scripts.edop.areas.engine import aggregate_band_t
from tests.regionality import baseline as bl

ALL = {'hyde_3_5', 'lmr_v2_1', 'evolv2k_v4'}


@pytest.fixture(scope='module')
def conn():
    with db_connect() as c:
        yield c


def _rows(conn, **kw):
    return aggregate_band_t(bl.TIMBUKTU['lat'], bl.TIMBUKTU['lon'], 100, 1300, 1400, conn, **kw).rows


def _sources(rows):
    return {r['variable'].split('_')[0] for r in rows}


def test_no_set_and_the_full_set_give_the_same_rows(conn):
    default, full = _rows(conn), _rows(conn, permitted=ALL)
    assert _sources(default) == {'hyde', 'lmr', 'evolv2k'}
    assert bl.compare({'rows': default}, {'rows': full}) == []
    assert bl.compare({'rows': full}, {'rows': default}) == []


def test_excluding_lmr_leaves_the_other_rows_unchanged(conn):
    default = _rows(conn)
    without = _rows(conn, permitted=ALL - {'lmr_v2_1'})
    assert _sources(without) == {'hyde', 'evolv2k'}
    kept = [r for r in default if not r['variable'].startswith('lmr_')]
    assert bl.compare({'rows': kept}, {'rows': without}) == []
    assert bl.compare({'rows': without}, {'rows': kept}) == []


def test_only_hyde_permitted(conn):
    assert _sources(_rows(conn, permitted={'hyde_3_5'})) == {'hyde'}


def test_result_carries_a_decision_per_source_and_the_hyde_note(conn):
    r = aggregate_band_t(bl.TIMBUKTU['lat'], bl.TIMBUKTU['lon'], 100, 1236, 1240, conn)   # no HYDE step inside the span
    assert [d.source_id for d in r.decisions] == ['hyde_3_5', 'lmr_v2_1', 'evolv2k_v4']
    assert all(d.applied for d in r.decisions)
    assert r.notes == {'hyde_3_5': 'nearest step: 1200'}


def test_decisions_name_the_sources_that_were_not_applied(conn):
    r = aggregate_band_t(bl.TIMBUKTU['lat'], bl.TIMBUKTU['lon'], 100, 2010, 2020, conn)
    assert [(d.source_id, d.reason) for d in r.decisions if not d.applied] == [('lmr_v2_1', 'outside_span'), ('evolv2k_v4', 'outside_span')]
    assert r.notes == {}


def test_a_source_left_out_is_in_neither_list_of_the_sources_block(conn):
    from scripts.edop.areas import source_registry
    r = aggregate_band_t(bl.TIMBUKTU['lat'], bl.TIMBUKTU['lon'], 100, 1300, 1400, conn, permitted=ALL - {'lmr_v2_1'})
    b = source_registry.sources_block(r.decisions, used=['basinatlas_v1'], notes=r.notes)
    assert [e['id'] for e in b['used']] == ['basinatlas_v1', 'hyde_3_5', 'evolv2k_v4']
    assert b['not_applied'] == []
