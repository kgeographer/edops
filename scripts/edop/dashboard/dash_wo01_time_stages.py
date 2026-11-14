"""dash WO-01, item 1: time the basin stages of profile generation, at Level 06 and Level 08, in one process.

Samples N Level 08 basins (fixed order by md5 of the id), takes a point inside each, and times per point and level:
the ring resolver, the single-basin signature, the basin-ring signature (the call that built wo06_ring_values.csv), and the per-basin
database lookups the generator makes (land cover, zone, lake share, ecoregion shares, coast, wiki and OneEarth links).
Level 08 lookups run the generator's own helpers through a connection that rewrites public.basin06 to public.basin08; the
generator files are not changed. Then times the template fill (build_facts + fill_units) at Level 06 for a few test places.

Scratch output: output/edop/dashboard/dash_wo01/stage_timings.csv. Usage: python -m scripts.edop.dashboard.dash_wo01_time_stages [N]
"""
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

from scripts.edop.areas import engine as E
from scripts.edop.whg import wo03_common as C
from scripts.edop.whg import wo04_fill as W
from scripts.edop.whg import wo06_rings as R
from scripts.edop.whg import wo07_classes as K
from scripts.edop.whg import wo08_units as U
from scripts.shared.db_utils import db_connect

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'output' / 'edop' / 'dashboard' / 'dash_wo01'
BANDS = list('ABCDE')


class Level8Conn:
    """Passes everything to a real connection, rewriting the Level 06 table name in SQL text."""

    def __init__(self, conn, old='public.basin06', new='public.basin08'):
        self._c, self._old, self._new = conn, old, new

    def execute(self, sql, *a, **k):
        if isinstance(sql, str):
            sql = sql.replace(self._old, self._new)
        return self._c.execute(sql, *a, **k)

    def __getattr__(self, name):
        return getattr(self._c, name)


def timed(fn, *a, **k):
    t = time.perf_counter()
    out = fn(*a, **k)
    return out, time.perf_counter() - t


def lookups(conn, level, hid, lat, lon):
    """The generator's per-basin database reads, one by one; returns seconds per helper."""
    c = Level8Conn(conn) if level == 8 else conn
    t = {}
    _, t['glc_shares'] = timed(K.glc_shares, c, hid)
    _, t['zone'] = timed(K.zone, c, hid)
    _, t['lake_pct'] = timed(U.lake_pct, c, hid)
    _, t['eco_shares'] = timed(U.eco_shares, c, hid)
    _, t['basin_coast'] = timed(U.basin_coast, c, hid, lat, lon)
    _, t['wiki_slug'] = timed(
        lambda: (conn.execute('SELECT wiki_url FROM public.eco_wikitext WHERE eco_id = %s', (1,)).fetchone(),
                 conn.execute('SELECT oneearth_slug FROM gaz."Ecoregions2017" WHERE eco_id = %s LIMIT 1', (1,)).fetchone()))
    return t


def sample_points(conn, n):
    ids = [r[0] for r in conn.execute(
        'SELECT hybas_id FROM public.basin08 ORDER BY md5(hybas_id::text) LIMIT %s', (n,)).fetchall()]
    pts = []
    for h in ids:
        la, lo = conn.execute(
            'SELECT ST_Y(ST_PointOnSurface(geom)), ST_X(ST_PointOnSurface(geom)) FROM public.basin08 WHERE hybas_id = %s',
            (h,)).fetchone()
        pts.append((int(h), float(la), float(lo)))
    return pts


def main(n=20):
    OUT.mkdir(parents=True, exist_ok=True)
    conn = db_connect()
    pts = sample_points(conn, n)
    # warm-up, untimed: first calls load catalogs and caches
    h0, la0, lo0 = pts[0]
    for lv in (6, 8):
        E.single_basin_signature(la0, lo0, conn, level=lv, bands=BANDS)
    rows = []
    for i, (h8, lat, lon) in enumerate(pts, 1):
        for lv in (6, 8):
            r = dict(sample_hybas8=h8, lat=lat, lon=lon, level=lv)
            try:
                res, r['t_ring_resolve'] = timed(E.resolve_basin_ring, lat, lon, lv, conn)
                r['n_neighbours'] = len(res[1])
                sig, r['t_signature'] = timed(E.single_basin_signature, lat, lon, conn, level=lv, bands=BANDS)
                hid = int(sig['scope']['hybas_id'])
                _, r['t_ring_signature'] = timed(E.basin_ring_signature, lat, lon, conn, level=lv, bands=BANDS)
                for k, v in lookups(conn, lv, hid, lat, lon).items():
                    r['t_' + k] = v
                r['hybas_id'] = hid
            except Exception as ex:
                r['error'] = f'{type(ex).__name__}: {ex}'
                conn.rollback()
            rows.append(r)
        print(f'{i}/{n}', flush=True)
        pd.DataFrame(rows).to_csv(OUT / 'stage_timings.csv', index=False)

    # template fill at Level 06 (saved pair, flow and ring tables exist for the test places only)
    PAIRS = pd.read_csv(C.OUT / 'q1_pairs.csv', dtype={'tag': str})
    FLOW = pd.read_csv(C.OUT / 'q2_flow_pairs.csv', dtype={'tag': str})
    RING = R.load_table()
    fill = []
    for name, (lat, lon) in list(C.PLACES.items())[:6]:
        F, tf = timed(W.build_facts, lat, lon, conn, PAIRS, FLOW, ring=RING)
        if F.get('hid') is None:
            continue
        _, tu = timed(W.fill_units, F)
        fill.append(dict(place=name, t_build_facts_http=tf, t_fill_units=tu))
    pd.DataFrame(fill).to_csv(OUT / 'fill_timings_l6.csv', index=False)
    print(pd.DataFrame(fill).round(3).to_string())


if __name__ == '__main__':
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 20)
