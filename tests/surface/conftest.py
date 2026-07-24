"""
tests/surface/conftest.py
--------------------------
Shared fixtures for surface tests.

live_server_url: starts the FastAPI app on a background thread via uvicorn so
Playwright (and any other HTTP client) can hit it on a real port.  The app is
identical to what `uvicorn app.main:app` would serve locally; the port is 8765
to avoid colliding with the dev server at 8000.

Playwright `page` and `browser` fixtures are provided automatically by
pytest-playwright once the package is installed.
"""

import threading
import time
import pytest
import httpx
import uvicorn

_TEST_HOST = "127.0.0.1"
_TEST_PORT = 8765


@pytest.fixture(scope="session")
def live_server_url():
    from app.main import app

    config = uvicorn.Config(app, host=_TEST_HOST, port=_TEST_PORT, log_level="error")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    base = f"http://{_TEST_HOST}:{_TEST_PORT}"
    # Wait generously: uvicorn accepts connections only after lifespan startup, which loads
    # five in-memory indices (similarity + context L6/L8, class L6) from 190k-basin views —
    # ~8 s cold. Too short a budget yields ERR_CONNECTION_REFUSED for every browser test.
    ready = False
    for _ in range(150):   # up to ~30 s
        try:
            httpx.get(f"{base}/api/health", timeout=1.0)
            ready = True
            break
        except Exception:
            time.sleep(0.2)
    if not ready:
        raise RuntimeError(f"test server at {base} did not become ready within ~30 s")

    yield base

    server.should_exit = True
    thread.join(timeout=5)
