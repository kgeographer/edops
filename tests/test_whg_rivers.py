"""WO-08 A5: a river is named only when Natural Earth names it near the reach AND the OpenStreetMap line of that river passes
within OSM_GATE_KM of the reach (wo07_rivers._name)."""
import pytest

from scripts.edop.whg import wo07_rivers as R

ROW = dict(r4_name='Kura', r4_name_km=0.4, r4_qid='Q156557', r4_name2='', r4_name2_km=None, r4_qid2='', r4_cx=44.79, r4_cy=41.72)


@pytest.fixture(autouse=True)
def labels(monkeypatch):
    monkeypatch.setattr(R, 'labels', lambda: {'Q156557': 'Kura River'})


def test_named_when_osm_line_is_close(monkeypatch):
    monkeypatch.setattr(R, 'osm_km', lambda q, lon, lat: R.OSM_GATE_KM - 0.01)
    assert R._name(ROW, 'r4') == 'Kura River'


@pytest.mark.parametrize('osm', [R.OSM_GATE_KM + 0.01, 9.4, None])
def test_unnamed_when_osm_line_is_far_or_missing(monkeypatch, osm):
    monkeypatch.setattr(R, 'osm_km', lambda q, lon, lat: osm)
    assert R._name(ROW, 'r4') == ''


def test_gate_is_three_km():
    assert R.OSM_GATE_KM == 3.0
