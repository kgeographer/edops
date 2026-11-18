"""Server time limit on Band T's HYDE query (WO-08 item 2): the engine stops it, the routes answer 504 with a plain message,
the Dashboard shows it. The test server runs in this process, so lowering the engine's limit forces a real timeout."""
import pytest
from fastapi.testclient import TestClient

from .test_handoff_ui import _arrive

pytestmark = pytest.mark.dashboard

SONG_T = dict(scope="polity", polity="Northern Song", year=1000, level=6, bands="T", from_year=1000, to_year=1999)
LVIV = "/dashboard?lat=49.8397&lon=24.0297&name=Lviv&from_year=1300&to_year=1400&bands=ABCDET&view=signature&v=1"


@pytest.fixture
def tiny_limit(monkeypatch):
    from scripts.edop.areas import engine
    monkeypatch.setattr(engine, "BAND_T_TIME_LIMIT_S", 0.001)
    return engine


def test_the_engine_stops_hyde_past_the_limit(tiny_limit):
    from app.db.connection import db_connect
    conn = db_connect()
    try:
        wkt, _, _ = tiny_limit.resolve_polity("Northern Song", 1000, 6, conn)
        q = tiny_limit._band_t_query(34.0, 113.0, 25, 1000, 1999, conn, wkt, 1000)
        with pytest.raises(tiny_limit.BandTTimeLimit) as e:
            tiny_limit._band_t_hyde(q)
        assert "time limit" in e.value.message and "Untick T" in e.value.message
    finally:
        conn.close()


def test_areas_answers_504_with_the_message(tiny_limit):
    from app.main import app
    r = TestClient(app).get("/api/areas", params=SONG_T)
    assert r.status_code == 504
    assert r.json()["detail"].startswith("Band T stopped at the server's time limit")


def test_the_public_buffer_answers_504_too(tiny_limit):
    from app.main import app
    r = TestClient(app).get("/api/signature", params=dict(scope="buffer", lat=49.8397, lon=24.0297, radius_km=50,
                                                           bands="T", from_year=1000, to_year=1000))    # the public buffer takes one year
    assert r.status_code == 504 and "time limit" in r.json()["detail"]


def test_a_query_inside_the_limit_is_unaffected():
    from app.main import app
    r = TestClient(app).get("/api/areas", params=dict(SONG_T, from_year=1000, to_year=1099))
    assert r.status_code == 200 and any(row["variable"] == "hyde_cropland" for row in r.json()["rows"])


def test_the_dashboard_shows_the_message_plainly(dashboard_server, page, tiny_limit):
    page.goto(dashboard_server + LVIV, wait_until="load")
    page.wait_for_selector("#v3-sig-content .ph-inline", timeout=60000)
    text = page.inner_text("#v3-sig-content")
    assert "Band T stopped at the server's time limit" in text and "Untick T" in text
