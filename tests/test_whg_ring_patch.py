"""WO-09 item 1: the patched ring table differs from the original only in the value of flagged share rows, and those values are basin06's."""
import pandas as pd
import pytest

from scripts.edop.whg import wo09_patch_ring as P
from scripts.shared.db_utils import db_connect

pytestmark = pytest.mark.skipif(not P.BACKUP.exists(), reason='ring table not patched yet')
KEY = ['core', 'member', 'variable']


@pytest.fixture(scope='module')
def tables():
    return pd.read_csv(P.BACKUP), pd.read_csv(P.CSV)


def test_same_rows_and_columns(tables):
    old, new = tables
    assert list(old.columns) == list(new.columns) and len(old) == len(new)
    assert old[KEY + ['status', 'role', 'shared_km', 'area_km2']].fillna(-1).equals(new[KEY + ['status', 'role', 'shared_km', 'area_km2']].fillna(-1))


def test_only_flagged_share_rows_changed(tables):
    old, new = tables
    changed = ~((old['value'] == new['value']) | (old['value'].isna() & new['value'].isna()))
    flagged = (old['status'] == 'outside_active_domain') & old['variable'].isin(P.COLUMNS)
    assert not (changed & ~flagged).any()
    assert flagged.sum() == 13617 and (new.loc[flagged, 'value'].notna()).all()
    assert set(new.loc[flagged, 'value'].unique()) <= {0.0, 1.0}


def test_values_are_basin06s(tables):
    _, new = tables
    conn = db_connect()
    for var, col in P.COLUMNS.items():
        r = new[(new['status'] == 'outside_active_domain') & (new['variable'] == var)].drop_duplicates('member').head(150)
        d = dict(conn.execute(f'SELECT hybas_id, {col} FROM public.basin06 WHERE hybas_id = ANY(%s)', ([int(i) for i in r['member']],)).fetchall())
        assert all(float(d[int(m)]) == v for m, v in zip(r['member'], r['value'])), var


def test_dist_sink_left_alone(tables):
    old, new = tables
    m = old['variable'] == 'dist_sink'
    assert old.loc[m, 'value'].fillna(-1).equals(new.loc[m, 'value'].fillna(-1))


def test_member_values_uses_the_stored_value(tables):
    from scripts.edop.whg import wo06_rings
    _, new = tables
    core = new.loc[(new['status'] == 'outside_active_domain') & (new['variable'] == 'cropland_extent') & (new['value'] == 1.0), 'core'].iloc[0]
    v = wo06_rings.member_values(new[new['core'] == core])
    assert 1.0 in v['cropland_extent'].values()
