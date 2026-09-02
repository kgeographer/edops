"""
Build app/static/workbench/afr_rivers.geojson for the African Regions tab (WO04).

HydroRIVERS (gaz.rivers) clipped to the Africa bounding box, filtered to the
continental mainstems by upstream catchment area, then **dissolved to one
feature per river system** (`main_riv`) so the Nile is one line, not 400 reaches
-- keeps the file tiny.

    upland_skm >= 100000  -> 34 river systems   (~45 KB)   <- default
    upland_skm >=  50000  -> 77 river systems   (adds the medium rivers)
    upland_skm >=  30000  -> 125 river systems

`ord_clas` per feature = min over the system's reaches (in this tileset the
lower class = the larger, more-downstream channel), used for line width.
Geometry: ST_LineMerge over the reaches, ST_SimplifyPreserveTopology(0.03 deg),
coords at 4 dp. A GeoJSON source has no minzoom, so it draws at the continental
default view (unlike sandbox/rivers.pmtiles).

Static artifact, committed. Tune UPLAND_MIN by eye against the map.
"""
import json
from pathlib import Path

from scripts.shared.db_utils import db_connect

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "app" / "static" / "workbench" / "afr_rivers.geojson"

AFRICA_BBOX = (-20, -36, 55, 38)   # W, S, E, N
UPLAND_MIN = 100000                # km^2 upstream catchment
SIMPLIFY = 0.03                    # degrees (~3 km)
COORD_DP = 4                       # GeoJSON coordinate decimal places (~11 m)

SQL = f"""
    WITH reach AS (
        SELECT main_riv, ord_clas, geom
        FROM gaz.rivers
        WHERE geom && ST_MakeEnvelope({AFRICA_BBOX[0]}, {AFRICA_BBOX[1]}, {AFRICA_BBOX[2]}, {AFRICA_BBOX[3]}, 4326)
          AND upland_skm >= {UPLAND_MIN}
    )
    SELECT MIN(ord_clas) AS ord_clas,
           ST_AsGeoJSON(
               ST_SimplifyPreserveTopology(ST_LineMerge(ST_Collect(geom)), {SIMPLIFY}),
               {COORD_DP}
           ) AS gj
    FROM reach
    GROUP BY main_riv
    ORDER BY ord_clas
"""


def main():
    conn = db_connect()
    try:
        with conn.cursor() as cur:
            cur.execute(SQL)
            rows = cur.fetchall()
    finally:
        conn.close()

    features = [
        {
            "type": "Feature",
            "geometry": json.loads(gj),
            "properties": {"ord_clas": int(ord_clas) if ord_clas is not None else None},
        }
        for ord_clas, gj in rows
    ]

    fc = {
        "type": "FeatureCollection",
        "name": "afr_rivers",
        "note": (
            f"HydroRIVERS (gaz.rivers) in the Africa bbox, upland_skm >= {UPLAND_MIN:,} km^2, "
            f"dissolved by main_riv, simplified {SIMPLIFY} deg. Built by "
            f"scripts/edop/workbench/build_afr_rivers.py."
        ),
        "features": features,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(fc))
    kb = OUT.stat().st_size / 1024
    by_class = {}
    for f in features:
        oc = f["properties"]["ord_clas"]
        by_class[oc] = by_class.get(oc, 0) + 1
    print(f"wrote {OUT.relative_to(ROOT)}  ({len(features)} river systems, {kb:,.0f} KB)")
    print(f"  upland_skm >= {UPLAND_MIN:,}  ·  simplify {SIMPLIFY} deg  ·  coords {COORD_DP} dp")
    print(f"  by ord_clas: {dict(sorted(by_class.items(), key=lambda kv: (kv[0] is None, kv[0])))}")


if __name__ == "__main__":
    main()
