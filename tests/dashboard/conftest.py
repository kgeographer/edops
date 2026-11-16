"""Fixtures for the Dashboard's browser tests: the app on a background uvicorn thread (port 8766, so it does not
collide with the dev server on 8000 or the surface tests' 8765). Playwright's `page` comes from pytest-playwright."""
import threading
import time

import httpx
import pytest
import uvicorn

_HOST, _PORT = "127.0.0.1", 8766


@pytest.fixture(scope="session")
def dashboard_server():
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
