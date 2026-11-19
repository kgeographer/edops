"""Sources line at the top of Band T (WO-05 item 2): which sources answered, and why any did not."""
import pytest

pytestmark = pytest.mark.dashboard

T = "bands=T&view=signature&v=1"
LVIV = f"/dashboard?lat=49.8397&lon=24.0297&name=Lviv&from_year=1300&to_year=1400&{T}"
SANTA_FE = f"/dashboard?lat=35.687&lon=-105.9378&name=Santa%20Fe&from_year=1300&to_year=1400&{T}"
AFTER_THE_ATLAS = f"/dashboard?lat=49.8397&lon=24.0297&name=Lviv&from_year=2021&to_year=2025&{T}"
NO_HYDE_STEP = f"/dashboard?lat=49.8397&lon=24.0297&name=Lviv&from_year=1301&to_year=1302&{T}"
EDGE = f"/dashboard?lat=28.8214&lon=20.0173&name=Edge&from_year=1300&to_year=1400&{T}"      # GEDA covers 0.498 of the basin
SPARSE_ID = 1060264990                                                                         # GEDA covers 0.067 of it


def _sparse_url():
    from app.db.connection import db_connect
    with db_connect() as conn:
        lon, lat = conn.execute("SELECT ST_X(ST_PointOnSurface(geom)), ST_Y(ST_PointOnSurface(geom)) "
                                "FROM public.basin06 WHERE hybas_id = %s", (SPARSE_ID,)).fetchone()
    return f"/dashboard?lat={lat}&lon={lon}&name=Sparse&from_year=1300&to_year=1400&{T}"


def _text(page, base, url):
    page.goto(base + url, wait_until="load")
    page.wait_for_selector("#v3-t-sources", timeout=90000)
    return page.inner_text("#v3-t-sources")


ORIGINAL_LABELS = ["HYDE land use", "LMR climate", "eVolv2k volcanic events", "GEDA drought"]   # sources added since are not under test here


def test_every_source_applies(dashboard_server, page):
    t = _text(page, dashboard_server, LVIV)
    assert "Available for this query: HYDE land use, LMR climate, eVolv2k volcanic events, GEDA drought" in t   # sources added later may follow
    assert not any(f"Not applied: {label}" in t for label in ORIGINAL_LABELS)


def test_geda_outside_its_footprint(dashboard_server, page):
    t = _text(page, dashboard_server, SANTA_FE)
    assert "Available for this query: HYDE land use, LMR climate, eVolv2k volcanic events" in t
    assert "GEDA drought" not in t.split("Not applied")[0]
    assert "Not applied: GEDA drought, because this place is outside its footprint." in t


def test_span_after_the_data_ends(dashboard_server, page):
    t = _text(page, dashboard_server, AFTER_THE_ATLAS)
    assert "Not applied: GEDA drought, because its years do not overlap this span." in t
    assert "GEDA drought" not in t.split("Not applied")[0]


def test_hyde_with_no_step_in_the_span_shows_its_nearest(dashboard_server, page):
    t = _text(page, dashboard_server, NO_HYDE_STEP)
    assert "No HYDE step falls in this span; the nearest (" in t
    assert "HYDE land use" in t.split("\n")[0]                        # still available


def test_geda_with_low_coverage_is_available_and_says_how_much(dashboard_server, page):
    t = _text(page, dashboard_server, EDGE)
    assert "GEDA drought" in t.split("\n")[0]
    assert "GEDA drought: covers 49.8% of the area." in t


def test_geda_below_the_coverage_floor_is_not_applied(dashboard_server, page):
    t = _text(page, dashboard_server, _sparse_url())
    assert "Not applied: GEDA drought, because its cells cover too little of this area." in t
    assert "GEDA drought" not in t.split("Not applied")[0]


def test_a_polity_has_the_line_too(dashboard_server, page):
    t = _text(page, dashboard_server, "/dashboard?scope=polity&polity=Inca%20Empire&view=signature&v=1")
    assert "Available for this query: HYDE land use, LMR climate, eVolv2k volcanic events." in t
    assert "Not applied: GEDA drought, because this place is outside its footprint." in t
