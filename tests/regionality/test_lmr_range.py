"""LMR v2.1 covers 0-2000 CE (regionality WO-04, Part 0): a span reaching 2000 returns rows for 1999 and 2000."""
import pytest
from fastapi.testclient import TestClient

from tests.regionality.baseline import TIMBUKTU


@pytest.fixture(scope="module")
def client():
    from app.main import app
    return TestClient(app)


def _lmr_years(payload):
    years = set()

    def walk(x):
        if isinstance(x, dict):
            if str(x.get('variable', '')).startswith('lmr_') and x.get('year') is not None:
                years.add(x['year'])
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
    walk(payload)
    return years


def _fetch(client, to_year):
    r = client.get('/api/areas', params=dict(scope='single_basin', **TIMBUKTU, level=6, bands='T',
                                             from_year=1995, to_year=to_year, detail='true'))
    assert r.status_code == 200, r.text[:200]
    return r.json()


def test_span_to_2000_returns_1999_and_2000(client):
    years = _lmr_years(_fetch(client, 2000))
    assert {1999, 2000} <= years
    assert max(years) == 2000


def test_span_past_2000_stops_at_2000(client):
    years = _lmr_years(_fetch(client, 2005))
    assert max(years) == 2000
