"""
Shared fixtures for EDOPS tests.

All tests that hit the database are skipped automatically if the DB is
unreachable, so the suite can run safely in environments without a live DB.
"""

import os
import pytest
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Reference sites used across multiple test modules
# ---------------------------------------------------------------------------
TIMBUKTU = {"lat": 16.76618535, "lon": -3.00777252}  # hyperarid, large exotic river
ROME     = {"lat": 41.8967,     "lon": 12.4822}       # Mediterranean
KAIFENG  = {"lat": 34.7972,     "lon": 114.3075}      # Yellow River lowland


@pytest.fixture(scope="session")
def db_available():
    """Return True if the DB is reachable, False otherwise."""
    try:
        import psycopg
        conn_kwargs = {
            "dbname":   os.getenv("DB_NAME") or os.getenv("PGDATABASE", "cedop"),
            "user":     os.getenv("DB_USER") or os.getenv("PGUSER"),
            "host":     os.getenv("DB_HOST") or os.getenv("PGHOST", "localhost"),
            "port":     os.getenv("DB_PORT") or os.getenv("PGPORT", "5432"),
            "connect_timeout": 3,
        }
        conn_kwargs = {k: v for k, v in conn_kwargs.items() if v}
        with psycopg.connect(**conn_kwargs):
            return True
    except Exception:
        return False


@pytest.fixture(scope="session")
def timbuktu_sig(db_available):
    if not db_available:
        pytest.skip("DB not available")
    from app.db.signature import get_signature
    sig = get_signature(**TIMBUKTU)
    assert sig is not None, "No basin found for Timbuktu reference point"
    return sig


@pytest.fixture(scope="session")
def timbuktu_temporal(db_available):
    if not db_available:
        pytest.skip("DB not available")
    from app.db.temporal import get_temporal_context
    return get_temporal_context(**TIMBUKTU, year_start=1000, year_end=1100)


@pytest.fixture(scope="session")
def athens_bce_temporal(db_available):
    """BCE query for Athens 500–400 BCE — should return volcanic events but no LMR series."""
    if not db_available:
        pytest.skip("DB not available")
    from app.db.temporal import get_temporal_context
    return get_temporal_context(lat=37.9838, lon=23.7275, year_start=-500, year_end=-400)


# ---------------------------------------------------------------------------
# Area markers, assigned by path so the suite can be run in parts: pytest -m engine, -m "not ui", ...
# ---------------------------------------------------------------------------
def _area(rel):
    if rel.startswith("engine/"):
        return "engine"
    if rel == "surface/test_sandbox_ui.py":
        return "ui"                               # Playwright, drives a browser
    if rel.startswith("surface/"):
        return "sandbox"
    if rel.startswith("cdop/"):
        return "cdop"
    if rel.startswith("regionality/"):
        return "regionality"
    if rel.startswith("dashboard/"):
        return "dashboard"
    if rel == "test_live_server.py":
        return "live"
    if rel.startswith("test_whg_") or rel == "test_profiles_page.py":
        return "whg"
    return "api"


def pytest_collection_modifyitems(config, items):
    root = os.path.dirname(__file__)
    for item in items:
        rel = os.path.relpath(str(item.fspath), root).replace(os.sep, "/")
        item.add_marker(getattr(pytest.mark, _area(rel)))
