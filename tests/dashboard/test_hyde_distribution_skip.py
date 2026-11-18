"""HYDE histograms are left out on request (WO-08 item 4): skip_hyde_distribution on /api/areas; every other number is unchanged."""
import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.dashboard

SONG = dict(scope="polity", polity="Northern Song", year=1000, level=6, bands="T", from_year=1000, to_year=1099, detail="true")
LVIV = dict(scope="single_basin", lat=49.8397, lon=24.0297, level=6, bands="T", from_year=1000, to_year=1300, detail="true")


def _rows(params, **extra):
    from app.main import app
    r = TestClient(app).get("/api/areas", params=dict(params, **extra))
    assert r.status_code == 200
    return [x for x in r.json()["rows"] if x["variable"].startswith("hyde_")]


@pytest.mark.parametrize("params", [SONG, LVIV])
def test_by_default_hyde_rows_keep_their_histograms(params):
    rows = _rows(params)
    assert rows and all(r["detail"]["distribution"]["bins"] and r["detail"]["distribution"]["weights"] for r in rows)


@pytest.mark.parametrize("params", [SONG, LVIV])
def test_skipping_drops_only_the_histogram(params):
    full, lean = _rows(params), _rows(params, skip_hyde_distribution="true")
    assert len(full) == len(lean)
    for a, b in zip(full, lean):
        assert b["detail"]["distribution"] is None
        top = lambda r: {k: v for k, v in r.items() if k != "detail"}
        assert top(a) == pytest.approx(top(b), rel=1e-9)         # cell order varies between calls: last-digit differences
        for key in ("p10", "p90", "sd", "w_eff"):
            assert a["detail"][key] == pytest.approx(b["detail"][key], rel=1e-9)


def test_lmr_and_geda_histograms_are_still_built_when_hyde_is_skipped():
    from app.main import app
    rows = TestClient(app).get("/api/areas", params=dict(LVIV, skip_hyde_distribution="true")).json()["rows"]
    lmr = [r for r in rows if r["variable"].startswith("lmr_")]
    assert lmr and all(r["detail"]["distribution"]["bins"] for r in lmr)


def test_the_dashboard_asks_for_it(dashboard_server, page):
    seen = []
    page.on("request", lambda r: seen.append(r.url) if "/api/areas" in r.url and "detail=true" in r.url else None)
    page.goto(dashboard_server + "/dashboard?lat=49.8397&lon=24.0297&name=Lviv&from_year=1300&to_year=1400&bands=ABCDET&v=1", wait_until="load")
    page.wait_for_selector("#v3-t-hyde-chart", state="attached", timeout=90000)
    assert seen and all("skip_hyde_distribution=true" in u for u in seen)
