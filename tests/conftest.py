"""
Shared fixtures for EDOPS tests.

All tests that hit the database are skipped automatically if the DB is
unreachable, so the suite can run safely in environments without a live DB.
"""

import os
import time
import threading
import pytest
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Reference sites used across multiple test modules
# ---------------------------------------------------------------------------
TIMBUKTU = {"lat": 16.76618535, "lon": -3.00777252}  # hyperarid, large exotic river
ROME     = {"lat": 41.8967,     "lon": 12.4822}       # Mediterranean
KAIFENG  = {"lat": 34.7972,     "lon": 114.3075}      # Yellow River lowland


@pytest.fixture(autouse=True, scope="session")
def normal_site_mode():
    """Tests run in the normal site mode whatever .env says (session scope: module and session fixtures build their clients
    first); the ones that need the v1 alpha switch it on themselves with monkeypatch."""
    from app.settings import settings
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(settings, "EDOPS_SITE_MODE", "")
        yield


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
    if rel in ("surface/test_sandbox_ui.py", "dashboard/test_handoff_ui.py", "dashboard/test_permalink_ui.py", "dashboard/test_get_signature_ui.py"):
        return "ui"                               # Playwright, drives a browser
    if rel.startswith("surface/"):
        return "sandbox"
    if rel.startswith("cdop/"):
        return "cdop"
    if rel.startswith("lbda/"):
        return "lbda"                             # reg WO-07, run alone with -m lbda
    if rel.startswith("regionality/"):
        return "regionality"
    if rel.startswith("dashboard/"):
        return "dashboard"
    if rel in ("test_live_server.py", "test_live_alpha.py"):
        return "live"
    if rel.startswith("test_whg_") or rel == "test_profiles_page.py":
        return "whg"
    return "api"


def pytest_collection_modifyitems(config, items):
    root = os.path.dirname(__file__)
    for item in items:
        rel = os.path.relpath(str(item.fspath), root).replace(os.sep, "/")
        item.add_marker(getattr(pytest.mark, _area(rel)))


# ---------------------------------------------------------------------------
# The app on a background uvicorn thread for the Dashboard's and LBDA's browser tests (port 8766, so it does not collide with
# the dev server on 8000 or the surface tests' 8765). Playwright's `page` comes from pytest-playwright.
# ---------------------------------------------------------------------------
_HOST, _PORT = "127.0.0.1", 8766


@pytest.fixture(scope="session")
def dashboard_server():
    import httpx
    import uvicorn
    from app.main import app
    server = uvicorn.Server(uvicorn.Config(app, host=_HOST, port=_PORT, log_level="error"))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    base = f"http://{_HOST}:{_PORT}"
    for _ in range(150):   # startup loads the in-memory indices, about 8 s cold
        try:
            httpx.get(f"{base}/api/health", timeout=1.0)
            break
        except Exception:
            time.sleep(0.2)
    else:
        raise RuntimeError(f"test server at {base} did not become ready")
    yield base
    server.should_exit = True
    thread.join(timeout=5)
