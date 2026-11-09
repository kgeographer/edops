"""WO-09: template v16 loads, its new keys are known to the generator, and the flagged-link list is read."""
from scripts.edop.whg import wo04_fill as W


def test_template_v16_loads_and_has_the_new_keys():
    t = W.templates()
    for k in ('S5.1b.some_full', 'S5.both_none', 'S5.both_none.bare', 'S5.frame.both_none', 'S8.point', 'S8.osm', 'S9.frame.nowiki'):
        assert k in t['text'], k
    assert t['text']['S7.frame'] == '{S7.2}'


def test_flagged_wikipedia_links_are_read():
    ids = W.suspect_wiki_ids()
    assert len(ids) == 129 and all(isinstance(i, int) for i in ids)


def test_not_a_share_list_names_the_distance_and_the_class():
    assert W.NOT_A_SHARE == {'dist_sink', 'wetland_class'}


def test_oneearth_button_is_in_both_s9_frames():
    t = W.templates()['text']
    assert 'S9.4' in t['S9.frame'] and 'S9.4' in t['S9.frame.nowiki']
