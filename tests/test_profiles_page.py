"""WO-10: the sample profiles page and its stored records."""
import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app

PROFILES = Path(__file__).resolve().parents[1] / 'app' / 'static' / 'profiles'
client = TestClient(app)   # no lifespan: only renders the template


def test_page_renders_noindex_and_lists_the_places():
    r = client.get('/profiles')
    assert r.status_code == 200
    assert '<meta name="robots" content="noindex">' in r.text
    index = json.loads((PROFILES / 'index.json').read_text())
    assert [p['place'] for p in index][:2] == ['Timbuktu', 'Tbilisi'] and len(index) == 10
    assert all(p['slug'] in r.text for p in index)


def test_no_other_page_links_to_profiles():
    for name in ('sandbox', 'workbench', 'explorer', 'polities'):
        assert 'href="/profiles' not in client.get('/' + name).text


def test_every_record_has_both_renderings_and_hides_what_is_not_built():
    for p in json.loads((PROFILES / 'index.json').read_text()):
        rec = json.loads((PROFILES / f'{p["slug"]}.json').read_text())
        seen = [s['filled'] for s in rec['sections']] + [seg.get('text') or seg.get('raw') or '' for s in rec['sections'] for seg in s['template']]
        assert not any('⟦' in t for t in seen) and rec['template_version'] >= 20      # what a reader sees: no placeholder
        if rec['no_basin']:
            assert rec['message'] and rec['sections'] == []
            continue
        assert rec['sections'] and all(s['filled'].strip() and s['template'] for s in rec['sections'])
        assert all(''.join(r['t'] for r in s['runs']) == s['filled'] for s in rec['sections'])
        assert len(rec['monthly']['precip_mm']) == 12 and len(rec['monthly']['temp_c']) == 12 and rec['monthly']['scope'] == 'basin'
        sig = next(b for b in rec['buttons'] if b['id'] == 'signature')
        assert sig['url'] == f'/api/signature?scope=basin&level=6&lat={rec["lat"]}&lon={rec["lon"]}'
        assert rec['buttons'][0]['id'] == 'S9.3' and rec['buttons'][0]['label'] == 'Profile as JSON' and rec['buttons'][1]['id'] == 'signature' and all(b['target'] == '_blank' for b in rec['buttons'])
        assert {u['scope'] for u in rec['units'].values()} == {'basin', 'point'}
