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
    return aggregate_band_t(bl.TIMBUKTU['lat'], bl.TIMBUKTU['lon'], 100, 1300, 1400, conn, **kw)


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
