"""dash WO-03 item 1: run every example in app/web/dashboard_examples.json against the local server and report.

Settlements: single basin, Level 06, bands A to E; the returned hybas_id is compared with the stored profile's.
Polities: slices fetched, then polity scope at Level 06 at the first slice with the bands the Sandbox sets by default
(A to E plus T over the slice span). Requests are tagged src=ui_aux so the query log skips them.
Usage: python -m scripts.edop.dashboard.dash_wo03_check_examples   (local server on :8000)
"""
import json
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = 'http://localhost:8000'
EX = json.loads((ROOT / 'app' / 'web' / 'dashboard_examples.json').read_text())


def get(path, **params):
    url = f'{BASE}{path}?{urllib.parse.urlencode(params)}'
    try:
        with urllib.request.urlopen(url, timeout=120) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        try:
            body = json.loads(e.read())
        except Exception:
            body = {}
        return e.code, body


print('SETTLEMENTS (single basin, Level 06, bands A-E)')
for s in EX['settlements']:
    code, d = get('/api/areas', scope='single_basin', lat=s['lat'], lon=s['lon'], level=6, bands='ABCDE', detail='false', src='ui_aux')
    prof = json.loads((ROOT / 'app' / 'static' / 'profiles' / f"{s['profile']}.json").read_text())
    if code == 200:
        hid = int(d['scope']['hybas_id'])
        print(f"  {s['name']:18} {code}  hybas_id {hid}  rows {len(d.get('rows', []))}  stored profile basin {prof['hybas_id']}  match {hid == prof['hybas_id']}")
    else:
        print(f"  {s['name']:18} {code}  {str(d.get('detail', d))[:90]}  (stored profile no_basin={prof['no_basin']})")

print('POLITIES (polity scope, Level 06, first slice)')
for p in EX['polities']:
    code, sl = get('/api/polity/slices', name=p['name'])
    if code != 200 or not sl:
        print(f"  {p['name']:18} slices {code}  {str(sl)[:80]}")
        continue
    s0 = sl[0]
    code, d = get('/api/areas', scope='polity', polity=p['name'], year=s0['fromyear'], level=6, bands='ABCDET',
                  from_year=s0['fromyear'], to_year=s0['toyear'], detail='false', src='ui_aux')
    if code == 200:
        print(f"  {p['name']:18} {code}  slices {len(sl)}  first {s0['fromyear']}..{s0['toyear']}  rows {len(d.get('rows', []))}")
    else:
        print(f"  {p['name']:18} {code}  slices {len(sl)}  first {s0['fromyear']}..{s0['toyear']}  {str(d.get('detail', d))[:90]}")
