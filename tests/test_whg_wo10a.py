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


def stated(V, nbs, slugs=('precip', 'temp', 'aridity')):
    return R._stated(list(slugs), 2, 'S2.3.extreme', 'S2.3.allbutone', 'S2.3.count', 'S2.3.counts', V, 0, nbs)[0]


def test_extremes_and_counts_about_the_same_basins_are_one_sentence():
    nbs = list(range(1, 8))     # Chaco Canyon's shape: lowest rainfall, most arid, warmer than four of the seven
    V = dict(precip_yr={0: 1, **{i: 10 + i for i in nbs}},
             aridity={0: 0.1, **{i: 0.5 + i / 10 for i in nbs}},
             temp_yr={0: 5, **dict(zip(nbs, [1, 2, 3, 4, 6, 7, 8]))})
    assert stated(V, nbs) == ('Of the eight basins that meet here, it receives the least precipitation and is the most arid; '
                              'of the other seven, it is warmer than four.')


def test_several_counts_after_one_extreme():
    nbs = [1, 2, 3]             # Utqiagvik's shape: lowest rainfall; cooler than two and more arid than two of the other three
    V = dict(precip_yr={0: 1, 1: 5, 2: 6, 3: 7}, temp_yr={0: 5, 1: 4, 2: 6, 3: 7}, aridity={0: 0.5, 1: 0.4, 2: 0.6, 3: 0.7})
    assert stated(V, nbs) == ('Of the four basins that meet here, it receives the least precipitation; '
                              'of the other three, it is cooler than two and is more arid than two.')


def test_counts_alone_still_use_the_around_it_sentence():
    nbs = [1, 2, 3, 4, 5, 6, 7]
    V = dict(precip_yr={0: 5, **dict(zip(nbs, [1, 2, 3, 4, 6, 7, 8]))}, temp_yr={0: 5, **dict(zip(nbs, [1, 2, 3, 4, 6, 7, 8]))},
             aridity={0: 5, **dict(zip(nbs, [1, 2, 3, 4, 6, 7, 8]))})
    t = stated(V, nbs)
    assert t.startswith('Compared with the seven basins around it') and 'of the other' not in t


def test_a_folded_sentence_records_only_the_lines_it_uses():
    nbs = list(range(1, 8))
    V = dict(precip_yr={0: 1, **{i: 10 + i for i in nbs}}, aridity={0: 0.1, **{i: 0.5 + i / 10 for i in nbs}},
             temp_yr={0: 5, **dict(zip(nbs, [1, 2, 3, 4, 6, 7, 8]))})
    tok = W._COLLECT.set([])
    try:
        text = stated(V, nbs)
        lines = W._take()
    finally:
        W._COLLECT.reset(tok)
    assert [ln['key'] for ln in lines] == ['S2.3.extreme.counts'] and lines[0]['out'] == text
    assert sorted(p['key'] for p in lines[0]['parts']) == ['S2.3.counts.item', 'cmp.aridity.bottom', 'cmp.precip.bottom']
