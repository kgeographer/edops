"""Dashboard page stub: /dashboard renders and carries the shared header and GA tag."""
from fastapi.testclient import TestClient


def test_dashboard_page_renders():
    from app.main import app
    r = TestClient(app).get("/dashboard")
    assert r.status_code == 200
    assert "EDOPS Dashboard" in r.text
    assert "gtag/js?id=G-5K56B8BCD9" in r.text
