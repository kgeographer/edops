"""WO-10: the template lines a unit chose are recorded as the profile is filled, and the stored record is built from them."""
from scripts.edop.whg import wo04_fill as W
from scripts.edop.whg import wo10_profiles as P


def test_fmt_records_lines_only_while_collecting():
    W.fmt('cmp.elev.top', {})                              # outside fill_units: nothing recorded
    assert W._take() == []
    tok = W._COLLECT.set([])
    try:
        out = W.fmt('cmp.elev.top', {})
        lines = W._take()
    finally:
        W._COLLECT.reset(tok)
    assert [ln['key'] for ln in lines] == ['cmp.elev.top'] and lines[0]['out'] == out and lines[0]['parts'] == []


def test_a_phrase_inside_a_sentence_is_its_part():
    tok = W._COLLECT.set([])
    try:
        a, b = W.fmt('cmp.elev.top', {}), W.fmt('cmp.relief.top', {})
        out = W.fmt('S6.5', dict(n='five', list=W.join_and([a, b])))
        lines = W._take()
    finally:
        W._COLLECT.reset(tok)
    assert len(lines) == 1 and lines[0]['key'] == 'S6.5' and lines[0]['out'] == out
    assert [p['key'] for p in lines[0]['parts']] == ['cmp.elev.top', 'cmp.relief.top']


def test_siblings_stay_separate_and_a_unit_that_does_not_speak_keeps_none():
    tok = W._COLLECT.set([])
    try:
        W.fmt('cmp.elev.top', {}); W.fmt('cmp.relief.top', {})
        assert [ln['key'] for ln in W._take()] == ['cmp.elev.top', 'cmp.relief.top']
        W.fmt('cmp.elev.top', {})
        assert W._drop() == [] and W._take() == []
    finally:
        W._COLLECT.reset(tok)


def test_context_is_restored_after_fill_units():
    assert W._COLLECT.get() is None


def test_slugify():
    assert [P.slugify(n) for n in ('Utqiaġvik', 'Chaco Canyon', 'Tristan da Cunha', 'Santa Fe')] == \
        ['utqiagvik', 'chaco-canyon', 'tristan-da-cunha', 'santa-fe']


def test_segments_keep_slots_unfilled_and_leave_out_what_is_not_built_or_silent():
    line = dict(key='S2.3.count', raw='raw {k}', vals={'k': 'three'}, out='raw three', parts=[])
    U = {'S2.1a': dict(ok=True, text='500', lines=[]), 'S2.3': dict(ok=True, text='raw three', lines=[line]),
         'S6.5': dict(ok=True, text='', lines=[]), 'S3.4': dict(ok=False, text=None, lines=[])}
    vals = {'S2.1a': '500', 'S2.3': 'raw three', 'S6.5': '', 'S3.4': ''}
    segs = P._segments('{name} gets {S2.1a} mm. {S2.3} {S6.5} {S3.4} {S6.2c}.', U, vals)
    kinds = [(s['type'], s.get('slot') or s.get('key') or s['text']) for s in segs]
    assert kinds[:5] == [('slot', 'name'), ('text', ' gets '), ('slot', 'S2.1a'), ('text', ' mm. '), ('line', 'S2.3.count')]
    assert segs[4]['vals'] == {'k': 'three'} and segs[4]['unit'] == 'S2.3'
    assert not any(s.get('slot') in ('S6.5', 'S3.4', 'S6.2c') or s.get('unit') in ('S6.5', 'S3.4') for s in segs)


def test_no_basin_record_has_a_message_and_no_sections():
    F = dict(pub=None, lat=-37.1, lon=-12.3, hid=None)
    r = P.build_record('Tristan da Cunha', F, {}, '2026-11-10')
    assert r['no_basin'] and r['sections'] == [] and r['slug'] == 'tristan-da-cunha' and 'No basin contains this point' in r['message']
    assert r['template_version'] == W.templates()['version']


def test_frames_without_the_unit_not_built():
    t = W.templates()['text']
    assert 'S1.2b' not in t['S1.frame.nogist'] and 'S8.1b' not in t['S8.frame.noyears']
    assert P.frame_key('S1', {}) == 'S1.frame.nogist' and P.frame_key('S8', {}) == 'S8.frame.noyears'
    built = {'S1.2b': dict(ok=True), 'S8.1b': dict(ok=True)}     # once built, the ordinary frames return
    assert P.frame_key('S1', built) == 'S1.frame' and P.frame_key('S8', built) == 'S8.frame'
    assert P.frame_key('S5', {'S5.both_none': dict(ok=True)}) == 'S5.frame.both_none' and P.frame_key('S2', {}) == 'S2.frame'
