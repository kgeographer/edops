"""Export basin08 geometry to GeoJSON, then invoke tippecanoe to build basin08.pmtiles.

Output: app/static/explorer/basin08.pmtiles
Run from the repo root: python scripts/edop/explorer/export_basin08_pmtiles.py
"""

import json
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from app.db.connection import db_connect

TIPPECANOE = '/opt/homebrew/bin/tippecanoe'
OUT_PMTILES = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'app', 'static', 'explorer', 'basin08.pmtiles')


def export_geojson(conn, path):
    print("Querying basin08 geometry…", flush=True)
    with conn.cursor() as cur:
        cur.execute("""
            SELECT hybas_id, ST_AsGeoJSON(geom, 5) AS geom
            FROM public.basin08
            ORDER BY hybas_id
        """)
        rows = cur.fetchall()

    print(f"  {len(rows):,} basins fetched — building GeoJSON…", flush=True)
    features = [
        {
            "type": "Feature",
            "id": row[0],
            "properties": {"hybas_id": row[0]},
            "geometry": json.loads(row[1]),
        }
        for row in rows
    ]
    fc = {"type": "FeatureCollection", "features": features}
    with open(path, 'w') as f:
        json.dump(fc, f)
    print(f"  Written: {path}  ({os.path.getsize(path) / 1e6:.1f} MB)", flush=True)


def run_tippecanoe(geojson_path, pmtiles_path):
    print("Running tippecanoe…", flush=True)
    cmd = [
        TIPPECANOE,
        '--output',                   pmtiles_path,
        '--force',
        '--layer',                    'basin08',
        '--use-attribute-for-id',     'hybas_id',
        '--minimum-zoom',             '0',
        '--maximum-zoom',             '7',
        '--no-feature-limit',
        '--no-tile-size-limit',
        '--simplification',           '10',
        geojson_path,
    ]
    print('  ' + ' '.join(cmd), flush=True)
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("STDERR:", result.stderr[-2000:])
        raise RuntimeError(f"tippecanoe failed (exit {result.returncode})")
    print(result.stderr[-500:] if result.stderr else '  (no stderr)')
    size = os.path.getsize(pmtiles_path)
    print(f"  Written: {pmtiles_path}  ({size / 1e6:.1f} MB)", flush=True)


def main():
    conn = db_connect()
    try:
        with tempfile.NamedTemporaryFile(suffix='.geojson', delete=False) as tf:
            geojson_path = tf.name

        export_geojson(conn, geojson_path)
        run_tippecanoe(geojson_path, os.path.abspath(OUT_PMTILES))
    finally:
        conn.close()
        if os.path.exists(geojson_path):
            os.unlink(geojson_path)
            print("  Cleaned up temp GeoJSON.", flush=True)

    print("Done. Add basin08.pmtiles to your rsync list for server deploy.")


if __name__ == '__main__':
    main()
