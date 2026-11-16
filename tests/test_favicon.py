"""Favicon and touch icon: the files, the /favicon.ico route, and the link tags on every page."""
from pathlib import Path

from fastapi.testclient import TestClient
from PIL import Image

IMAGES = Path(__file__).resolve().parents[1] / "app" / "static" / "images"
PAGES = ("/", "/edops", "/about", "/dashboard", "/using", "/sandbox", "/explorer", "/workbench", "/polities", "/profiles")


def test_the_icon_files():
    ico = Image.open(IMAGES / "favicon.ico")
    assert {(16, 16), (32, 32), (48, 48)} <= set(ico.info["sizes"])
    assert Image.open(IMAGES / "favicon-32.png").size == (32, 32)
    assert Image.open(IMAGES / "apple-touch-icon.png").size == (180, 180)


def test_the_favicon_route():
    from app.main import app
    r = TestClient(app).get("/favicon.ico")
    assert r.status_code == 200 and r.headers["content-type"] == "image/x-icon" and r.content[:4] == b"\x00\x00\x01\x00"


def test_every_page_links_the_icons():
    from app.main import app
    c = TestClient(app)
    for path in PAGES:
        r = c.get(path)
        assert r.status_code == 200, path
        assert 'rel="icon"' in r.text and "favicon-32.png" in r.text and 'rel="apple-touch-icon"' in r.text, path
