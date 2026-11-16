"""GEDA block on the Dashboard's Signature tab (WO-05 item 1): shown wherever the payload carries geda_scpdsi rows."""
import pytest

pytestmark = pytest.mark.dashboard

LVIV = "/dashboard?lat=49.8397&lon=24.0297&name=Lviv&bands=T&from_year=1300&to_year=1400&view=signature&v=1"
SANTA_FE = "/dashboard?lat=35.687&lon=-105.9378&name=Santa%20Fe&bands=T&from_year=1300&to_year=1400&view=signature&v=1"
KYIV = "/dashboard?lat=50.4501&lon=30.5234&name=Kyiv&bands=T&from_year=1350&to_year=1350&view=signature&v=1"
OBSERVED = "/dashboard?lat=49.8397&lon=24.0297&name=Lviv&bands=T&from_year=1960&to_year=2010&view=signature&v=1"
BEFORE_GEDA = "/dashboard?lat=49.8397&lon=24.0297&name=Lviv&bands=T&from_year=900&to_year=1100&view=signature&v=1"

BLOCK_READY = "document.querySelector('#v3-t-geda') !== null"
T_DONE = "document.querySelector('#v3-acc-T') !== null"


def _open(page, base, url, want_block=True):
    page.goto(base + url, wait_until="load")
    page.wait_for_function(T_DONE, timeout=60000)
    if want_block:
        page.wait_for_function(BLOCK_READY, timeout=5000)


def test_lviv_shows_geda_beside_lmr_with_its_own_slider(dashboard_server, page):
    _open(page, dashboard_server, LVIV)
    assert page.locator("#v3-t-geda").count() == 1
    assert page.locator("#v3-t-sl-lmr_pdsi").count() == 1 and page.locator("#v3-t-sl-geda_scpdsi").count() == 1
    text = page.inner_text("#v3-t-geda")
    assert "Great Eurasian Drought Atlas" in text and "standard score" in text and "June–August" in text
    assert "Not Palmer drought categories" in text
    assert "independent reconstructions" in text                       # LMR is on the page too
    assert "reconstructed from tree rings" in text                      # the payload's caveat text


def test_the_geda_slider_moves_its_histogram_and_not_lmrs(dashboard_server, page):
    _open(page, dashboard_server, LVIV)
    lmr_before = page.inner_html("#v3-t-hs-lmr_pdsi")
    geda_before = page.inner_html("#v3-t-hs-geda_scpdsi")
    page.eval_on_selector("#v3-t-sl-geda_scpdsi", "e => { e.value = 1310; e.dispatchEvent(new Event('input')); }")
    assert page.inner_text("#v3-t-yr-geda_scpdsi") == "1310"
    assert page.inner_html("#v3-t-hs-geda_scpdsi") != geda_before
    assert page.inner_html("#v3-t-hs-lmr_pdsi") == lmr_before
    assert page.inner_text("#v3-t-yr-lmr_pdsi") != "1310"


def test_observed_years_are_shaded_labelled_and_explained(dashboard_server, page):
    _open(page, dashboard_server, OBSERVED)
    assert "Shaded: observed years" in page.inner_text("#v3-t-geda")
    assert "Observed, not reconstructed" in page.inner_text("#v3-t-geda")
    assert page.locator("#v3-t-geda svg rect[fill='#e0a800']").count() == 1
    page.eval_on_selector("#v3-t-sl-geda_scpdsi", "e => { e.value = 2000; e.dispatchEvent(new Event('input')); }")
    assert "2000 CE · observed" in page.inner_text("#v3-t-hs-geda_scpdsi")
    page.eval_on_selector("#v3-t-sl-geda_scpdsi", "e => { e.value = 1970; e.dispatchEvent(new Event('input')); }")
    assert "1970 CE" in page.inner_text("#v3-t-hs-geda_scpdsi") and "observed" not in page.inner_text("#v3-t-hs-geda_scpdsi")
    assert page.locator("#v3-t-ob-geda_scpdsi").count() == 0


def test_a_span_before_the_atlas_starts_says_geda_covers_part_of_it(dashboard_server, page):
    _open(page, dashboard_server, BEFORE_GEDA)
    assert "GEDA covers 1000–1100 of the 900–1100 requested" in page.inner_text("#v3-t-geda")


def test_a_span_with_no_observed_years_has_no_shading_and_no_observed_text(dashboard_server, page):
    _open(page, dashboard_server, LVIV)
    assert page.locator("#v3-t-geda svg rect[fill='#e0a800']").count() == 0
    text = page.inner_text("#v3-t-geda")
    assert "Shaded: observed years" not in text and "Observed, not reconstructed" not in text


def test_santa_fe_has_no_geda_block(dashboard_server, page):
    _open(page, dashboard_server, SANTA_FE, want_block=False)
    assert page.locator("#v3-t-geda").count() == 0
    assert page.locator("#v3-t-sl-lmr_pdsi").count() == 1


def test_the_kyiv_anchor_reaches_the_page_data(dashboard_server, page):
    """Kyiv basin, 1350: mean -0.408 (the regression anchor), read from the rendered histogram's source row."""
    import json
    seen = {}
    page.on("response", lambda r: seen.update(body=r.body()) if "/api/areas" in r.url and "from_year=1350" in r.url else None)
    _open(page, dashboard_server, KYIV)
    row = next(r for r in json.loads(seen["body"])["rows"] if r["variable"] == "geda_scpdsi")
    assert row["representative_raw"] == pytest.approx(-0.408, abs=6e-4)
    assert row["n_units"] == 27
    assert page.locator("#v3-t-geda").count() == 1


def test_the_slider_year_is_marked_on_the_line_chart_for_geda_and_lmr(dashboard_server, page):
    _open(page, dashboard_server, LVIV)       # span 1300-1400, 101 rows, chart 170 wide
    for var in ("geda_scpdsi", "lmr_pdsi"):
        mk = f"#v3-t-tm-{var} .v3-t-mk"
        assert float(page.get_attribute(mk, "x1")) == pytest.approx(85.0, abs=0.1)         # 1350, the middle
        page.eval_on_selector(f"#v3-t-sl-{var}", "e => { e.value = 1300; e.dispatchEvent(new Event('input')); }")
        assert float(page.get_attribute(mk, "x1")) == pytest.approx(0.0, abs=0.1)
        page.eval_on_selector(f"#v3-t-sl-{var}", "e => { e.value = 1400; e.dispatchEvent(new Event('input')); }")
        assert float(page.get_attribute(mk, "x1")) == pytest.approx(170.0, abs=0.1)


def test_the_histogram_is_stamped_with_the_slider_year(dashboard_server, page):
    _open(page, dashboard_server, OBSERVED)       # 1960-2010
    for var in ("geda_scpdsi", "lmr_pdsi"):
        mid = page.input_value(f"#v3-t-sl-{var}")                        # each variable starts at the middle of its own rows
        assert f"{mid} CE" in page.inner_text(f"#v3-t-hs-{var}")
        page.eval_on_selector(f"#v3-t-sl-{var}", "e => { e.value = 1961; e.dispatchEvent(new Event('input')); }")
        assert "1961 CE" in page.inner_text(f"#v3-t-hs-{var}") and "1960–2010" not in page.inner_text(f"#v3-t-hs-{var}")
    page.eval_on_selector("#v3-t-sl-geda_scpdsi", "e => { e.value = 2000; e.dispatchEvent(new Event('input')); }")
    assert "2000 CE · observed" in page.inner_text("#v3-t-hs-geda_scpdsi")
