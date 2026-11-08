"""The profile scripts' one rule for missing values (scripts/edop/whg/missing.py)."""
from scripts.edop.whg import missing, wo04_fill as W


def test_is_missing():
    assert missing.is_missing(None) and missing.is_missing(-9999) and missing.is_missing(-9999.0)
    assert not missing.is_missing(0) and not missing.is_missing(-22.1) and not missing.is_missing(12)


def test_clean_and_class_label():
    assert missing.clean(-9999) is None and missing.clean(7) == 7
    assert missing.class_label(-9999, {1: 'Lake'}) is None and missing.class_label(1, {1: 'Lake'}) == 'Lake'


def test_row_value_follows_the_engine_status():
    rows = {'slope_avg': {'status': 'no_data'}, 'temp_yr': {'status': 'ok'}}
    assert missing.row_value(rows, 'slope_avg', -999.9) is None          # the marker, scaled
    assert missing.row_value(rows, 'temp_yr', -22.1) == -22.1            # a real negative stays
    assert missing.row_value(rows, 'not_listed', 5) == 5 and missing.row_value(None, 'x', 5) == 5


def test_val_masks_a_no_data_row():
    pub = {'signature_bands': {'A': {'items': [{'key': 'slope_avg', 'value': -999.9}, {'key': 'temp_yr', 'value': -22.1}]}}}
    F = dict(pub=pub, rows={'slope_avg': {'status': 'no_data'}, 'temp_yr': {'status': 'ok'}})
    assert W.val(F, 'slope_avg') is None and W.val(F, 'temp_yr') == -22.1
