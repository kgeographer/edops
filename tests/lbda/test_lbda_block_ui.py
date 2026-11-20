"""LBDA block on the Dashboard's Signature tab (reg WO-07 item 5): shown wherever the payload carries lbda_pmdi rows."""
import pytest

pytestmark = pytest.mark.lbda

CHACO = "/dashboard?lat=36.06&lon=-107.96&name=Chaco%20Canyon&bands=T&from_year=1100&to_year=1200&view=signature&v=1"
CHACO_1900 = "/dashboard?lat=36.06&lon=-107.96&name=Chaco%20Canyon&bands=T&from_year=1850&to_year=1950&view=signature&v=1"
SANTA_FE = "/dashboard?lat=35.687&lon=-105.9378&name=Santa%20Fe&bands=T&from_year=150&to_year=300&view=signature&v=1"
CAHOKIA = "/dashboard?lat=38.65&lon=-90.06&name=Cahokia&bands=T&from_year=300&to_year=1000&view=signature&v=1"
LVIV = "/dashboard?lat=49.8397&lon=24.0297&name=Lviv&bands=T&from_year=1300&to_year=1400&view=signature&v=1"

T_DONE = "document.querySelector('#v3-acc-T') !== null"


def _open(page, base, url, block=True):
    page.goto(base + url, wait_until="load")
    page.wait_for_function(T_DONE, timeout=60000)
    if block:
        page.wait_for_function("document.querySelector('#v3-t-lbda') !== null", timeout=5000)


def test_chaco_shows_lbda_beside_lmr_with_its_own_slider(dashboard_server, page):
    _open(page, dashboard_server, CHACO)
    assert page.locator("#v3-t-lbda").count() == 1 and page.locator("#v3-t-geda").count() == 0
    assert page.locator("#v3-t-sl-lmr_pdsi").count() == 1 and page.locator("#v3-t-sl-lbda_pmdi").count() == 1
    text = page.inner_text("#v3-t-lbda")
    assert "Living Blended Drought Atlas" in text and "Palmer Modified Drought Index" in text and "June–August" in text
    assert "Not standardized" in text and "cannot be compared with GEDA" in text
    assert "independent reconstructions" in text                       # LMR is on the page too
    assert "reconstructed from tree rings" in text                      # the payload's caveat text
    assert "Available for this query:" in page.inner_text("#v3-t-sources") and "LBDA drought" in page.inner_text("#v3-t-sources")


def test_the_lbda_slider_moves_its_histogram_and_not_lmrs(dashboard_server, page):
    _open(page, dashboard_server, CHACO)
    lmr_before, lbda_before = page.inner_html("#v3-t-hs-lmr_pdsi"), page.inner_html("#v3-t-hs-lbda_pmdi")
    page.eval_on_selector("#v3-t-sl-lbda_pmdi", "e => { e.value = 1110; e.dispatchEvent(new Event('input')); }")
    assert page.inner_text("#v3-t-yr-lbda_pmdi") == "1110"
    assert page.inner_html("#v3-t-hs-lbda_pmdi") != lbda_before
    assert page.inner_html("#v3-t-hs-lmr_pdsi") == lmr_before


def test_instrumental_years_are_shaded_labelled_and_explained(dashboard_server, page):
    _open(page, dashboard_server, CHACO_1900)
    text = page.inner_text("#v3-t-lbda")
    assert "Shaded: instrumental years (1900 on)" in text and "Instrumental, not reconstructed" in text
    assert page.locator("#v3-t-lbda svg rect[fill='#e0a800']").count() == 1
    page.eval_on_selector("#v3-t-sl-lbda_pmdi", "e => { e.value = 1920; e.dispatchEvent(new Event('input')); }")
    assert "1920 CE · instrumental" in page.inner_text("#v3-t-hs-lbda_pmdi")
    page.eval_on_selector("#v3-t-sl-lbda_pmdi", "e => { e.value = 1880; e.dispatchEvent(new Event('input')); }")
    assert "1880 CE" in page.inner_text("#v3-t-hs-lbda_pmdi") and "instrumental" not in page.inner_text("#v3-t-hs-lbda_pmdi")


def test_a_span_that_starts_before_the_data_says_lbda_covers_part_of_it(dashboard_server, page):
    _open(page, dashboard_server, CAHOKIA)               # no data in the Cahokia cells before 920
    assert "LBDA covers 920–1000 of the 300–1000 requested" in page.inner_text("#v3-t-lbda")


def test_a_place_outside_the_footprint_has_no_lbda_block_and_the_sources_line_says_why(dashboard_server, page):
    page.goto(dashboard_server + LVIV, wait_until="load")
    page.wait_for_function(T_DONE, timeout=60000)
    page.wait_for_function("document.querySelector('#v3-t-sources') !== null", timeout=5000)
    assert page.locator("#v3-t-lbda").count() == 0 and page.locator("#v3-t-geda").count() == 1
    assert "Not applied: LBDA drought, because this place is outside its footprint" in page.inner_text("#v3-t-sources")


def test_a_basin_with_early_gaps_names_the_years_in_the_block(dashboard_server, page):
    _open(page, dashboard_server, SANTA_FE)                # the Level 6 basin: 77% of it has data before 210
    assert "early years cover less of the area: 150-209 at 77%, against 100% from 210 on" in page.inner_text("#v3-t-lbda")
    _open(page, dashboard_server, CHACO)
    assert "early years cover less" not in page.inner_text("#v3-t-lbda")
