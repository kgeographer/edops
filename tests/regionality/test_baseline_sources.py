"""The baseline comparison treats the `sources` lists as sets of entries matched by id: a source added later is allowed,
a removed source or a changed entry is a difference (reg WO-07)."""
import pytest

from tests.regionality import baseline as bl

pytestmark = pytest.mark.regionality

HYDE = {'id': 'hyde_3_5', 'name': 'HYDE', 'licence': 'CC BY 4.0'}
GEDA = {'id': 'geda', 'name': 'GEDA', 'licence': 'CC BY 4.0'}
LBDA = {'id': 'lbda_v3', 'name': 'LBDA', 'licence': None}


def _diff(ref_used, new_used):
    return bl.compare({'sources': {'used': ref_used}}, {'sources': {'used': new_used}})


def test_an_added_source_is_allowed():
    assert _diff([HYDE, GEDA], [HYDE, GEDA, LBDA]) == []


def test_an_added_source_in_an_empty_list_is_allowed():
    assert bl.compare({'sources': {'not_applied': []}}, {'sources': {'not_applied': [{**LBDA, 'reason': 'outside_footprint'}]}}) == []


def test_order_does_not_matter():
    assert _diff([HYDE, GEDA], [LBDA, GEDA, HYDE]) == []


def test_a_removed_source_is_a_difference():
    d = _diff([HYDE, GEDA], [HYDE, LBDA])
    assert [(path, kind) for path, kind, *_ in d] == [('.sources.used[geda]', 'removed')]


def test_a_changed_entry_is_a_difference_but_an_added_field_is_not():
    assert _diff([HYDE], [{**HYDE, 'licence': 'CC0'}])[0][:2] == ('.sources.used[hyde_3_5].licence', 'changed')
    assert _diff([HYDE], [{**HYDE, 'years': {'requested': [1, 2], 'returned': [1, 2]}}]) == []


def test_other_lists_still_compare_by_length():
    assert bl.compare({'x': [1, 2]}, {'x': [1, 2, 3]})[0][:2] == ('.x', 'changed')
