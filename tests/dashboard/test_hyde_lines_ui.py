"""HYDE land use on the Signature tab as one line chart (WO-08 item 1): a dot at each step, grazing not drawn."""
import pytest

pytestmark = pytest.mark.dashboard

T = "bands=T&view=signature&v=1"
LVIV = "/dashboard?lat=49.8397&lon=24.0297&name=Lviv"
CHART = "#v3-t-hyde-chart"


def _open(page, base, from_year, to_year):
    page.goto(f"{base}{LVIV}&from_year={from_year}&to_year={to_year}&{T}", wait_until="load")
    page.wait_for_selector("#v3-t-sources", timeout=90000)


def _lines_and_dots(page):
    return page.evaluate(f"""() => {{
        const c = document.querySelector('{CHART}');
        return c ? [c.querySelectorAll('polyline').length, c.querySelectorAll('circle').length] : null;
    }}""")


def test_a_short_span_draws_three_lines_with_a_dot_per_step(dashboard_server, page):
    _open(page, dashboard_server, 1000, 1300)                 # 1000, 1100, 1200, 1300
    assert _lines_and_dots(page) == [3, 12]
    legend = page.inner_text("#v3-acc-T")
    assert "Cropland" in legend and "Pasture" in legend and "Rangeland" in legend and "Grazing" not in legend


def test_a_span_crossing_1950_keeps_decadal_then_annual_steps(dashboard_server, page):
    _open(page, dashboard_server, 1940, 1960)                 # 1940, 1950, 1951 ... 1960
    assert _lines_and_dots(page) == [3, 36]


def test_a_long_annual_span_is_one_chart_not_a_wide_table(dashboard_server, page):
    _open(page, dashboard_server, 1900, 2000)                 # 56 steps
    assert _lines_and_dots(page) == [3, 168]
    width = page.evaluate(f"document.querySelector('{CHART}').getBoundingClientRect().width")
    assert width < 400


def test_a_span_with_no_step_shows_the_nearest_step_as_text(dashboard_server, page):
    _open(page, dashboard_server, 1301, 1302)
    assert _lines_and_dots(page) is None
    text = page.inner_text("#v3-acc-T")
    assert "nearest available HYDE epoch" in text and "Cropland" in text
