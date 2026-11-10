"""One-time load: gaz.ne_coastline_10m from data/ne_10m_coastline (Natural Earth 1:10m coastline, v5.0.0-pre9).

Additive: creates one table and a GiST index; touches nothing else. Refuses to run if the table already has rows.
Run from the repo root: python -m scripts.edop.whg.wo08_load_coastline
"""
import geopandas as gpd
from pathlib import Path
from scripts.shared.db_utils import db_connect

SHP = Path(__file__).resolve().parents[3] / 'data' / 'ne_10m_coastline' / 'ne_10m_coastline.shp'

CREATE_SQL = """
CREATE TABLE IF NOT EXISTS gaz.ne_coastline_10m (
    gid        serial PRIMARY KEY,
    featurecla text,
    scalerank  integer,
    geom       geometry(LineString, 4326) NOT NULL
);
CREATE INDEX IF NOT EXISTS ne_coastline_10m_geom_gix ON gaz.ne_coastline_10m USING gist (geom);
"""


def main():
    conn = db_connect()
    conn.execute(CREATE_SQL)
    if conn.execute('SELECT count(*) FROM gaz.ne_coastline_10m').fetchone()[0]:
        raise SystemExit('gaz.ne_coastline_10m already has rows; nothing loaded')
    g = gpd.read_file(SHP)
    with conn.cursor() as cur:
        cur.executemany('INSERT INTO gaz.ne_coastline_10m (featurecla, scalerank, geom) VALUES (%s, %s, ST_GeomFromText(%s, 4326))',
                        [(r.featurecla, int(r.scalerank), r.geometry.wkt) for r in g.itertuples()])
    conn.commit()
    conn.execute('ANALYZE gaz.ne_coastline_10m')
    conn.commit()
    print('loaded', conn.execute('SELECT count(*) FROM gaz.ne_coastline_10m').fetchone()[0], 'lines from', SHP.name)


if __name__ == '__main__':
    main()
