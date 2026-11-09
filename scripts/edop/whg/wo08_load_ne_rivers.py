"""One-time load: gaz.ne_rivers_10m from data/ne_10m_rivers_lake_centerlines_scale_rank (Natural Earth 1:10m rivers).

The shapefile is never edited. The table is a copy with FIXES applied; `wikidataid_src` keeps the shapefile's own value and
`fixed` marks the lines that differ. Additive: creates one table and a GiST index. Refuses to run if the table has rows.
Run from the repo root: python -m scripts.edop.whg.wo08_load_ne_rivers
"""
import geopandas as gpd
from pathlib import Path
from scripts.shared.db_utils import db_connect

SHP = Path(__file__).resolve().parents[3] / 'data' / 'ne_10m_rivers_lake_centerlines_scale_rank' / 'ne_10m_rivers_lake_centerlines_scale_rank.shp'

# (name, id in the shapefile, id it should have, test on the line): Natural Earth gives its Colorado lines in the USA the
# Argentine river's id (Q270627); the USA river is Q1265. The four Argentine lines (south of the equator) are right.
FIXES = [('Colorado', 'Q270627', 'Q1265', 'north')]

CREATE_SQL = """
CREATE TABLE IF NOT EXISTS gaz.ne_rivers_10m (
    gid            serial PRIMARY KEY,
    featurecla     text,
    scalerank      integer,
    name           text,
    name_en        text,
    wikidataid     text,
    wikidataid_src text,
    fixed          boolean NOT NULL DEFAULT false,
    geom           geometry(Geometry, 4326) NOT NULL
);
CREATE INDEX IF NOT EXISTS ne_rivers_10m_geom_gix ON gaz.ne_rivers_10m USING gist (geom);
"""


def main():
    conn = db_connect()
    conn.execute(CREATE_SQL)
    if conn.execute('SELECT count(*) FROM gaz.ne_rivers_10m').fetchone()[0]:
        raise SystemExit('gaz.ne_rivers_10m already has rows; nothing loaded')
    g = gpd.read_file(SHP)
    rows = []
    for r in g.itertuples():
        q = r.wikidataid if isinstance(r.wikidataid, str) and r.wikidataid else None
        new = q
        for name, old, fixed_q, where in FIXES:
            if r.name == name and q == old and where == 'north' and r.geometry.representative_point().y > 0:
                new = fixed_q
        rows.append((r.featurecla, int(r.scalerank), r.name, r.name_en, new, q, new != q, r.geometry.wkt))
    with conn.cursor() as cur:
        cur.executemany('INSERT INTO gaz.ne_rivers_10m (featurecla, scalerank, name, name_en, wikidataid, wikidataid_src, fixed, geom) '
                        'VALUES (%s, %s, %s, %s, %s, %s, %s, ST_GeomFromText(%s, 4326))', rows)
    conn.commit()
    conn.execute('ANALYZE gaz.ne_rivers_10m')
    conn.commit()
    print('loaded', conn.execute('SELECT count(*) FROM gaz.ne_rivers_10m').fetchone()[0], 'lines from', SHP.name,
          '|', conn.execute('SELECT count(*) FROM gaz.ne_rivers_10m WHERE fixed').fetchone()[0], 'with a corrected id')


if __name__ == '__main__':
    main()
