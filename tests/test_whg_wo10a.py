"""WO-10a: template v21 wording, the S6.2 chain rule, and the proposed /whgmodal response made from a stored record."""
import json

import pytest

from scripts.edop.whg import wo04_fill as W, wo06_rings as R, wo10_profiles as P

PROFILES = W.ROOT / 'app' / 'static' / 'profiles'
ok = lambda text, note=None: dict(ok=True, text=text, note=note, why=None, lines=[])
no = lambda why, na=False: dict(ok=False, text=None, why=why, na=na, lines=[])


def s62(dn1, dnN, up1=0, upN=0):
    F = dict(n_nb=7, flow=dict(up1=up1, upN=upN, dn1=dn1, dnN=dnN), ring=None)
    return R.fill_ring_units(F, ok, no)['S6.2']['text']


def test_v21_wording():
    t = W.templates()
    assert t['version'] >= 21
    assert 'GLC2000' in t['text']['S5.1c'] and 'GLC2000' in t['text']['S5.both_none']
    assert '{S8.2}' not in t['text']['S8.frame'] and '{S8.2}' not in t['text']['S8.frame.noyears']
    assert 'S8.2.zero' in t['text']   # the unit is still filled; only the frames dropped it


@pytest.mark.parametrize('dn1, dnN, expect', [
    (1, 0, 'It drains into one of them.'),
    (1, 1, 'It drains into one of them, and its water then passes through one more.'),
    (1, 2, 'It drains into one of them, and its water then passes through two more.'),
    (2, 0, 'Its water flows on through two of them.'),
    (0, 2, 'Its water flows on through two of them.'),
    (0, 0, 'It drains into none of them.'),
])
def test_downstream_chain_wording(dn1, dnN, expect):
    assert s62(dn1, dnN).endswith(expect)


def test_response_leaves_out_the_generators_working():
    rec = json.loads((PROFILES / 'kaifeng.json').read_text())
    out = P.to_response(rec)
    assert not {'units', 'notes', 'provenance', 'buttons', 'slug'} & set(out)
    assert all(set(s) == {'id', 'title', 'text', 'runs'} for s in out['sections'])
    assert all('template' not in s and 'vals' not in json.dumps(s) for s in out['sections'])
    assert out['links']['signature'].startswith(P.SITE + '/api/signature?scope=basin&level=6&lat=')
    assert all(e['url'].startswith('https://www.oneearth.org/ecoregions/') for e in out['links']['ecoregions'])
    m = out['monthly']
    assert m['scope'] == 'basin' and len(m['precip_mm']) == 12 and len(m['temp_c']) == 12 and m['units'] and m['note']
    assert m['precip_mm'] == rec['monthly']['precip_mm']   # the values the chart draws


def test_response_for_a_place_with_no_basin():
    rec = json.loads((PROFILES / 'tristan-da-cunha.json').read_text())
    out = P.to_response(rec)
    assert out['no_basin'] is True and out['message'] and 'sections' not in out
