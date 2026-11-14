"""dash WO-01: how many ecoregions does a basin have, at Level 06 and Level 08, and would the S1.4 sentence speak?

Samples N Level 08 basins (md5 order), takes a point inside each, finds the Level 06 basin containing that point, and for both
runs the generator's ecoregion-share query with the basin picked first (same result as wo08_units.eco_shares, much faster at
Level 08). S1.4 speaks when an ecoregion other than the point's and the largest by area covers at least OTHER_ECO_SHARE
(approximation: the generator also skips the signature's own eco_id, which is normally the largest). Read-only; scratch output.
Usage: python -m scripts.edop.dashboard.dash_wo01_eco_counts [N]
"""
import sys
from pathlib import Path

import pandas as pd

from scripts.edop.whg import wo08_units as U
from scripts.shared.db_utils import db_connect

OUT = Path(__file__).resolve().parents[3] / 'output' / 'edop' / 'dashboard' / 'dash_wo01'
SQL = """WITH b AS MATERIALIZED (SELECT geom FROM public.{t} WHERE hybas_id = %s)
SELECT e.eco_id::bigint, ST_Area(ST_Intersection(b.geom, ev.g)::geography) / ST_Area(b.geom::geography) AS share
FROM b JOIN gaz."Ecoregions2017" e ON e.geom && b.geom
CROSS JOIN LATERAL (SELECT CASE WHEN e.eco_id = ANY(%s) THEN ST_MakeValid(e.geom) ELSE e.geom END AS g) ev
WHERE ST_Intersects(ev.g, b.geom)"""


def shares(conn, table, hid, invalid):
    rows = conn.execute(SQL.format(t=table), (hid, invalid)).fetchall()
    return sorted(((int(e), float(s)) for e, s in rows if s and s > 0), key=lambda r: -r[1])


def main(n=300):
    OUT.mkdir(parents=True, exist_ok=True)
    conn = db_connect()
    invalid = U.invalid_ids(conn)
    ids = [int(r[0]) for r in conn.execute(
        'SELECT hybas_id FROM public.basin08 ORDER BY md5(hybas_id::text) LIMIT %s', (n,)).fetchall()]
    rows = []
    for h8 in ids:
        lat, lon = conn.execute('SELECT ST_Y(ST_PointOnSurface(geom)), ST_X(ST_PointOnSurface(geom)) '
                                'FROM public.basin08 WHERE hybas_id = %s', (h8,)).fetchone()
        h6 = conn.execute('SELECT hybas_id FROM public.basin06 WHERE ST_Contains(geom, ST_SetSRID(ST_MakePoint(%s, %s), 4326)) LIMIT 1',
                          (lon, lat)).fetchone()
        pt = conn.execute('SELECT eco_id FROM gaz."Ecoregions2017" WHERE ST_Intersects(geom, ST_SetSRID(ST_MakePoint(%s, %s), 4326)) LIMIT 1',
                          (lon, lat)).fetchone()
        pt_eco = int(pt[0]) if pt else None
        for lv, tab, hid in ((8, 'basin08', h8), (6, 'basin06', int(h6[0]) if h6 else None)):
            if hid is None:
                continue
            sh = shares(conn, tab, hid, invalid)
            ge = [e for e, s in sh if s >= U.OTHER_ECO_SHARE]
            skip = {pt_eco, sh[0][0] if sh else None}
            rows.append(dict(level=lv, hybas_id=hid, n_any=len(sh), n_ge10=len(ge),
                             s14_speaks=any(e not in skip for e in ge)))
    d = pd.DataFrame(rows)
    d.to_csv(OUT / 'eco_counts.csv', index=False)
    for lv in (6, 8):
        x = d[d.level == lv]
        print(f'Level {lv}: {len(x)} basins | ecoregions with any area: median {x.n_any.median():.0f}, mean {x.n_any.mean():.2f}, max {x.n_any.max()} '
              f'| share of basins with 1 / 2 / 3+ ecoregions at 10% or more: '
              f'{(x.n_ge10 <= 1).mean():.0%} / {(x.n_ge10 == 2).mean():.0%} / {(x.n_ge10 >= 3).mean():.0%} '
              f'| S1.4 would speak in {x.s14_speaks.mean():.0%}')


if __name__ == '__main__':
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 300)
