"""
Database utilities for CEDOP (Computing Place) modules.

Provides centralized database connection management for both EDOP and CDOP modules.
"""
import os
import json
from pathlib import Path
from typing import Any, Dict, Optional
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

# Resolve .env from project root regardless of working directory
_ENV_FILE = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(_ENV_FILE)


def db_connect(schema: Optional[str] = None) -> psycopg.Connection:
    """
    Return a database connection using environment variables.

    Environment variables used:
        PGHOST: Database host (default: localhost)
        PGPORT: Database port (default: 5432)
        PGDATABASE: Database name (default: cedop)
        PGUSER: Database user
        PGPASSWORD: Database password

    Args:
        schema: If provided, sets search_path to this schema plus public.
                E.g., schema="cdop" sets search_path to "cdop, public".

    Returns:
        psycopg.Connection: An open database connection.

    Example:
        conn = db_connect()
        conn = db_connect(schema="cdop")
    """
    conn = psycopg.connect(
        host=os.environ.get("PGHOST", "localhost"),
        port=os.environ.get("PGPORT", "5432"),
        dbname=os.environ.get("PGDATABASE", "cedop"),
        user=os.environ.get("PGUSER"),
        password=os.environ.get("PGPASSWORD"),
    )
    if schema:
        conn.execute(f"SET search_path TO {schema}, public")
    return conn


# -----------------------
# Legacy signature query (from edop_db.py)
# -----------------------

SIGNATURE_SQL = """
SELECT
  zone_id,
  zone_name,
  strata_id,
  strata_code,
  land_cover_id,
  land_cover_name,
  pop_density,
  elev_min,
  elev_max,
  runoff,
  discharge_yr,
  -- geometry handling: return a GeoJSON string (good for Leaflet)
  ST_AsGeoJSON(geom, 6) AS geom_geojson
FROM public.v_basin08_basic
WHERE ST_Covers(
  geom,
  ST_SetSRID(ST_MakePoint(%(lon)s, %(lat)s), 4326)
)
ORDER BY area_km2 ASC
LIMIT 1;
"""


def get_signature(
    lat: float,
    lon: float,
) -> Dict[str, Any] | None:
    """Return a single basin signature dict for (lat, lon), or None if no basin covers point.

    Connection parameters are read from environment variables (typically via a .env file):
      DB_NAME, DB_USER, DB_HOST, DB_PORT, and optionally DB_PASSWORD.

    Notes:
    - Uses ST_Covers exactly as your SQL does.
    - Orders by smallest area_km2 to pick the smallest containing basin when multiple match.
    - Returns geom as a GeoJSON string in 'geom_geojson' (Leaflet-friendly).
    """

    conn_kwargs = dict(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        password=os.getenv("DB_PASSWORD") or os.getenv("PGPASSWORD") or None,
    )

    # Drop None values so psycopg/libpq can fall back to defaults / .pgpass when appropriate
    conn_kwargs = {k: v for k, v in conn_kwargs.items() if v not in (None, "")}

    with psycopg.connect(**conn_kwargs, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(SIGNATURE_SQL, {"lat": lat, "lon": lon})
            row = cur.fetchone()
            return dict(row) if row else None


# ---------------------
# Areas TSV reader
# ---------------------

# Columns that must always be integer — never let pandas coerce to float via NaN.
_AREAS_INT_COLS: Dict[str, str] = {
    'hybas_id':          'Int64',
    'dominant_hybas_id': 'Int64',
}


def read_areas_tsv(path, **kwargs) -> Any:
    """Read an Areas-phase TSV, forcing known ID columns to nullable integer.

    Pandas silently promotes integer columns to float64 when NaN is present.
    This wrapper prevents that for hybas_id and dominant_hybas_id by applying
    Int64 (pandas nullable integer) on every read.

    Extra kwargs are passed through to pd.read_csv (e.g. index_col, usecols).
    Additional dtype overrides can be passed via dtype= and will merge with
    the built-in integer overrides (caller wins on conflict).
    """
    import pandas as pd
    caller_dtype = kwargs.pop('dtype', {})
    dtype = {**_AREAS_INT_COLS, **caller_dtype}
    return pd.read_csv(path, sep='\t', dtype=dtype, **kwargs)


def main() -> None:
    # Your test coordinates (note: lon, lat order matches your SQL)
    lat = 16.76618535
    lon = -3.00777252

    sig = get_signature(lat=lat, lon=lon)

    if sig is None:
        print("No basin found covering that point.")
        return

    print(json.dumps(sig, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
