"""WO-08 A5: a river line from OpenStreetMap for every river Natural Earth can name in the profile (S3.1 and S3.3).

One Overpass query per river, by its Wikidata Q-id (the relation tagged with it), stored as a simplified line under
output/edop/whg/wo08_osm/<qid>.json; `load_table` then writes them to gaz.osm_river_lines. The profile shows a river's
name only when this line passes within GATE_KM of the reach (wo07_rivers). OSM data are under the ODbL: attribute them.
Run from the repo root: python -m scripts.edop.whg.wo08_osm_rivers   (resumable; about 35 s per river)
"""
import json
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import certifi
import pandas as pd
from shapely.geometry import LineString, MultiLineString

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'output' / 'edop' / 'whg' / 'wo08_osm'
RIVERS_CSV = ROOT / 'output' / 'edop' / 'whg' / 'wo07_rivers.csv'
URL = 'https://overpass-api.de/api/interpreter'
UA = 'EDOPS-research/0.1 (WHG profile river names)'
GATE_KM = 3.0          # the OSM line must pass within this distance of the reach (sample: passes <= 2.89 km, blocks >= 8.7 km)
SIMPLIFY_DEG = 0.0005  # about 50 m
RETRY_PAUSES = (20, 40, 80)


def qids():
    """Every Q-id the profile can name: S3.1 (class 4+ reach within 25 km) and S3.3 (a much larger river nearby)."""
    d = pd.read_csv(RIVERS_CSV, dtype={'key': str})
    a = d[d.r4_name.notna() & d.r4_qid.notna() & (d.r4_km <= 25)][['r4_qid', 'r4_name']].rename(columns={'r4_qid': 'qid', 'r4_name': 'name'})
    b = d[d.big_name.notna() & d.big_qid.notna()][['big_qid', 'big_name']].rename(columns={'big_qid': 'qid', 'big_name': 'name'})
    return pd.concat([a, b]).drop_duplicates('qid').reset_index(drop=True)


def fetch(qid):
    query = f'[out:json][timeout:240];rel["wikidata"="{qid}"]["waterway"];out geom;'
    req = urllib.request.Request(URL, data=urllib.parse.urlencode({'data': query}).encode(), headers={'User-Agent': UA})
    ctx = ssl.create_default_context(cafile=certifi.where())
    for pause in (*RETRY_PAUSES, None):
        try:
            with urllib.request.urlopen(req, timeout=280, context=ctx) as f:
                raw = f.read()
            break
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as e:
            if pause is None:
                raise
            time.sleep(pause)
    els = json.loads(raw)['elements']
    lines = [LineString([(p['lon'], p['lat']) for p in m['geometry']]) for e in els for m in e.get('members', [])
             if m.get('type') == 'way' and m.get('geometry') and len(m['geometry']) >= 2]
    return len(raw), len(els), lines


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    todo = qids()
    for k, r in enumerate(todo.itertuples(), 1):
        fp = OUT / f'{r.qid}.json'
        if fp.exists() and json.loads(fp.read_text()).get('status') in ('ok', 'none'):
            continue
        t0 = time.perf_counter()
        rec = dict(qid=r.qid, ne_name=r.name)
        try:
            nbytes, nrel, lines = fetch(r.qid)
            rec.update(status='ok' if lines else 'none', bytes=nbytes, n_rel=nrel, n_ways=len(lines),
                       wkt=MultiLineString(lines).simplify(SIMPLIFY_DEG).wkt if lines else None)
        except Exception as e:
            rec.update(status='error', error=str(e)[:200])
        rec['secs'] = round(time.perf_counter() - t0, 1)
        fp.write_text(json.dumps(rec))
        print(f"{k}/{len(todo)} {r.qid} {r.name}: {rec['status']} in {rec['secs']}s", {x: rec.get(x) for x in ('n_ways', 'bytes')}, flush=True)
        time.sleep(5)


CREATE_SQL = """
CREATE TABLE IF NOT EXISTS gaz.osm_river_lines (
    qid     text PRIMARY KEY,
    ne_name text,
    n_ways  integer,
    geom    geometry(MultiLineString, 4326) NOT NULL
);
CREATE INDEX IF NOT EXISTS osm_river_lines_geom_gix ON gaz.osm_river_lines USING gist (geom);
"""


def load_table(conn):
    """Write every stored river that has a line to gaz.osm_river_lines (replaces the rows; additive table)."""
    conn.execute(CREATE_SQL)
    conn.execute('DELETE FROM gaz.osm_river_lines')
    n = 0
    for fp in sorted(OUT.glob('Q*.json')):
        r = json.loads(fp.read_text())
        if r.get('status') == 'ok':
            conn.execute('INSERT INTO gaz.osm_river_lines (qid, ne_name, n_ways, geom) VALUES (%s, %s, %s, ST_Multi(ST_GeomFromText(%s, 4326)))',
                         (r['qid'], r['ne_name'], r['n_ways'], r['wkt']))
            n += 1
    conn.commit()
    conn.execute('ANALYZE gaz.osm_river_lines')
    conn.commit()
    return n


if __name__ == '__main__':
    build()
    recs = [json.loads(fp.read_text()) for fp in OUT.glob('Q*.json')]
    print('status:', pd.Series([r['status'] for r in recs]).value_counts().to_dict(), '| rivers wanted:', len(qids()))
