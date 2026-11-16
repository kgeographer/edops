"""One setting (EDOPS_VERSION_LABEL, default v1.0 alpha) feeds the version pill on the splash and in every page header."""
from fastapi.testclient import TestClient

PAGES = ("/edops", "/dashboard", "/using", "/sandbox", "/explorer", "/workbench")


def _get(path):
    from app.main import app
    r = TestClient(app).get(path)
    assert r.status_code == 200
    return r.text


def test_the_default_is_v1_0_alpha():
    from app.settings import settings
    assert settings.EDOPS_VERSION_LABEL == "v1.0 alpha"
    for path in PAGES:
        assert ">v1.0 alpha</span>" in _get(path), path


def test_every_page_reads_the_setting(monkeypatch):
    from app.web.pages import templates
    monkeypatch.setitem(templates.env.globals, "version_label", "v9.9 test")
    for path in PAGES:
        html = _get(path)
        assert ">v9.9 test</span>" in html and ">v0.4</span>" not in html, path
