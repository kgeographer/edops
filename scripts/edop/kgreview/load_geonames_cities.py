"""
One-time load: gaz.geonames_cities from whg_staging.geonames.places_filter1.

Source: whg_staging DB (separate Postgres database, same host/credentials as cedop),
geonames.places_filter1 (~10M rows). Filtered to populated places (fclass='P') with
population >= 15000 -- a reference/orientation layer for Sandbox's polity maps, not a
historical claim (see notebooks/edop/kgreview/chandler_modelski_wrangle.ipynb and
project memory for why modern reference data is fine here but time-filtered historical
data was ruled out).
"""
import os
import psycopg
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent.parent.parent / '.env')

PG_KWARGS = dict(
    host=os.environ.get("PGHOST", "localhost"),
    port=os.environ.get("PGPORT", "5432"),
    user=os.environ.get("PGUSER"),
    password=os.environ.get("PGPASSWORD"),
)

SELECT_SQL = """
    SELECT gnid, name, ccode, latitude, longitude, population, fclass, fcode
    FROM geonames.places_filter1
    WHERE fclass = 'P' AND population >= 15000
"""

CREATE_SQL = """
    DROP TABLE IF EXISTS gaz.geonames_cities;
    CREATE TABLE gaz.geonames_cities (
        gnid       integer PRIMARY KEY,
        name       text,
        ccode      character(2),
        lat        double precision,
        lon        double precision,
        population bigint,
        fclass     character(1),
        fcode      character varying,
        geom       geometry(Point, 4326)
    );
"""

INDEX_SQL = "CREATE INDEX geonames_cities_geom_idx ON gaz.geonames_cities USING GIST (geom);"


def main():
    with psycopg.connect(**PG_KWARGS, dbname="whg_staging") as src:
        with src.cursor() as cur:
            cur.execute(SELECT_SQL)
            rows = cur.fetchall()
    print(f"fetched {len(rows)} rows from whg_staging.geonames.places_filter1")

    with psycopg.connect(**PG_KWARGS, dbname="cedop") as dst:
        with dst.cursor() as cur:
            cur.execute(CREATE_SQL)
            with cur.copy(
                "COPY gaz.geonames_cities (gnid, name, ccode, lat, lon, population, fclass, fcode) "
                "FROM STDIN"
            ) as copy:
                for row in rows:
                    copy.write_row(row)
            cur.execute(
                "UPDATE gaz.geonames_cities SET geom = ST_SetSRID(ST_MakePoint(lon, lat), 4326);"
            )
            cur.execute(INDEX_SQL)
        dst.commit()

    with psycopg.connect(**PG_KWARGS, dbname="cedop") as dst:
        with dst.cursor() as cur:
            cur.execute("SELECT count(*) FROM gaz.geonames_cities;")
            print(f"gaz.geonames_cities loaded: {cur.fetchone()[0]} rows")


if __name__ == "__main__":
    main()
