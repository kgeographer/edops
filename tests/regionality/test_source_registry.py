"""check() in scripts/edop/areas/source_registry.py (regionality WO-04, Part C): no database needed."""
import pytest

from scripts.edop.areas import source_registry as sr


def test_span_inside_the_years_is_unchanged():
    d = sr.check('lmr_v2_1', span=(1300, 1400))
    assert (d.applied, d.reason, d.span) == (True, None, (1300, 1400))


@pytest.mark.parametrize('source, span, clipped', [
    ('lmr_v2_1', (1990, 2010), (1990, 2000)),
    ('lmr_v2_1', (-50, 10), (0, 10)),
    ('evolv2k_v4', (1800, 1950), (1800, 1890)),
    ('evolv2k_v4', (-600, -400), (-491, -400)),
])
def test_span_is_clipped_to_the_years_covered(source, span, clipped):
    d = sr.check(source, span=span)
    assert d.applied and d.span == clipped


@pytest.mark.parametrize('source, span', [
    ('lmr_v2_1', (2001, 2010)),
    ('lmr_v2_1', (-300, -10)),
    ('evolv2k_v4', (1891, 2000)),
])
def test_span_outside_the_years_is_outside_span(source, span):
    d = sr.check(source, span=span)
    assert (d.applied, d.reason, d.span) == (False, 'outside_span', None)


def test_hyde_is_not_suppressed_for_a_span_outside_its_years():
    d = sr.check('hyde_3_5', span=(2100, 2200))
    assert (d.applied, d.span) == (True, (2100, 2200))


def test_permitted_set_excludes_a_source_before_any_other_test():
    d = sr.check('lmr_v2_1', span=(2100, 2200), permitted={'hyde_3_5'})   # span is also outside; permission wins
    assert (d.applied, d.reason) == (False, 'not_permitted')
    assert sr.check('lmr_v2_1', span=(1300, 1400), permitted={'lmr_v2_1'}).applied
    assert sr.check('lmr_v2_1', span=(1300, 1400), permitted=None).applied


def test_stored_source_is_not_served():
    d = sr.check('geda', span=(1300, 1400))
    assert (d.applied, d.reason) == (False, 'not_served')


def test_source_without_a_time_axis_applies():
    assert sr.check('basinatlas_v1').applied
    assert sr.check('basinatlas_v1', span=(1300, 1400)).span == (1300, 1400)


def test_years_covered_and_unknown_source():
    assert sr.years_covered('lmr_v2_1') == (0, 2000)
    assert sr.years_covered('evolv2k_v4') == (-491, 1890)
    assert sr.years_covered('basinatlas_v1') is None
    with pytest.raises(KeyError, match='unknown source'):
        sr.check('nonesuch')
