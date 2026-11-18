"""Span gate (WO-07 items 1 and 2, Settlements side): a warning under the Band T year inputs above a buffer's HYDE step limit (single basin and ring have none)."""
from .test_handoff_ui import _arrive

TBILISI_T = "/dashboard?lat=41.6938&lon=44.8015&name=Tbilisi&bands=ABCDET&from_year=1150&to_year=1250&v=1"
WARN = "#v3-t-span-warn"


def _set_span(page, lo, hi):
    page.fill("#v3-from-year", str(lo))
    page.fill("#v3-to-year", str(hi))
    page.dispatch_event("#v3-to-year", "change")           # what leaving the field does


def _warned(page):
    return page.evaluate(f"!document.querySelector('{WARN}').classList.contains('d-none')")


def test_the_step_table_is_the_database_table(dashboard_server, page):
    from app.db.connection import db_connect
    with db_connect() as conn:
        years = [r[0] for r in conn.execute("SELECT year_ce FROM temporal.hyde_times ORDER BY year_ce").fetchall()]
    page.goto(dashboard_server + "/dashboard", wait_until="load")
    assert page.evaluate("EdopsSpanGate.steps()") == years


def test_a_single_basin_or_ring_has_no_step_limit(dashboard_server, page):
    """HYDE is drawn as lines, so width no longer limits a basin or a ring."""
    _arrive(page, dashboard_server, TBILISI_T, "v3-tab-map-btn")
    _set_span(page, 1900, 2000)                                # 56 steps
    assert not _warned(page)
    page.select_option("#v3-scope-select", "ring")
    assert not _warned(page)


def test_a_buffer_has_the_polity_limit_of_nine(dashboard_server, page):
    _arrive(page, dashboard_server, TBILISI_T, "v3-tab-map-btn")
    page.select_option("#v3-scope-select", "buffer")
    _set_span(page, 0, 800)                                    # 9 steps
    assert not _warned(page)
    _set_span(page, 0, 900)                                    # 10
    assert _warned(page)
    assert "long time" in page.inner_text(WARN)


def test_a_scope_change_rechecks_the_same_span(dashboard_server, page):
    _arrive(page, dashboard_server, TBILISI_T, "v3-tab-map-btn")
    _set_span(page, 0, 1100)                                   # 12 steps: fine for a basin
    assert not _warned(page)
    page.select_option("#v3-scope-select", "buffer")           # over a buffer's nine
    assert _warned(page)
    page.select_option("#v3-scope-select", "single")
    assert not _warned(page)


def test_the_warning_does_not_block_getting_the_signature(dashboard_server, page):
    _arrive(page, dashboard_server, TBILISI_T, "v3-tab-map-btn")
    page.select_option("#v3-scope-select", "buffer")
    _set_span(page, 0, 1200)
    assert _warned(page)
    assert not page.evaluate("document.getElementById('v3-sig-btn').disabled")


def test_no_warning_without_band_t_or_with_a_reversed_span(dashboard_server, page):
    _arrive(page, dashboard_server, TBILISI_T, "v3-tab-map-btn")
    page.select_option("#v3-scope-select", "buffer")
    _set_span(page, 0, 1200)
    assert _warned(page)
    _set_span(page, 1200, 0)
    assert not _warned(page)
    _set_span(page, 0, 1200)
    page.uncheck("#v3-band-T")
    assert not _warned(page)
    page.check("#v3-band-T")
    assert _warned(page)


def test_the_cost_follows_the_years_asked_for(dashboard_server, page):
    _arrive(page, dashboard_server, TBILISI_T, "v3-tab-map-btn")
    page.select_option("#v3-scope-select", "buffer")
    _set_span(page, 1000, 1400)                                # 400 years, 5 steps
    assert not _warned(page)
    _set_span(page, 1700, 2100)                                # 400 years, but decadal then annual steps
    assert _warned(page)
