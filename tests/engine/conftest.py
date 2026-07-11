"""
Shared fixtures for engine unit tests (scripts/edop/areas/test_engine_wo*.py).

Tests that require a DB connection use the `conn` fixture.  If the DB is
unreachable the fixture raises pytest.skip so the suite stays green in CI or
any environment without a live database.
"""

import pytest
from scripts.shared.db_utils import db_connect


@pytest.fixture(scope='session')
def conn():
    try:
        connection = db_connect()
    except Exception as e:
        pytest.skip(f'DB unavailable: {e}')
    yield connection
    connection.close()
