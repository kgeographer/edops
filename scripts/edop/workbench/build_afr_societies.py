"""
Build app/static/workbench/afr_societies.geojson for the African Regions tab (WO04).

The D-PLACE Ethnographic Atlas societies whose point falls on the African
continent (ST_Contains vs Natural Earth admin0, continent = 'Africa') -- 528 of
the 1,291 EA societies. One Point feature each, with just enough for the eventual
map popup:

    {soc_id, name, subsistence (EA042), religion (EA034)}

subsistence / religion are null where the trait is coded missing/ambiguous (same
code-name exclusions as routes_workbench.py :: societies()).

Static artifact, committed like lovejoy_regions.geojson. Re-runnable offline;
reads the local cedop DB (dplace + gaz). The app never runs this.
"""
import json
from pathlib import Path

from scripts.shared.db_utils import db_connect

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "app" / "static" / "workbench" / "afr_societies.geojson"

SQL = """
    SELECT DISTINCT ON (s.id)
           s.id            AS soc_id,
           s.name          AS name,
           s.longitude     AS lon,
           s.latitude      AS lat,
           c.name          AS subsistence,
           rel.name        AS religion
    FROM dplace.societies s
    LEFT JOIN dplace.data d   ON d.soc_id = s.id AND d.var_id = 'EA042'
    LEFT JOIN dplace.codes c  ON c.id = d.code_id
        AND c.name NOT IN ('Missing data', '', 'Missing for at least 1 activity', 'Two or more sources')
    LEFT JOIN dplace.data rd  ON rd.soc_id = s.id AND rd.var_id = 'EA034'
    LEFT JOIN dplace.codes rel ON rel.id = rd.code_id
        AND rel.name <> 'Missing data'
    JOIN gaz.admin0 a
        ON a.geom && ST_SetSRID(ST_MakePoint(s.longitude, s.latitude), 4326)
       AND ST_Contains(a.geom, ST_SetSRID(ST_MakePoint(s.longitude, s.latitude), 4326))
       AND a.continent = 'Africa'
    WHERE s.contribution_id = 'dplace-dataset-ea'
    ORDER BY s.id
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
            "id": soc_id,
            "geometry": {"type": "Point", "coordinates": [float(lon), float(lat)]},
            "properties": {
                "soc_id": soc_id,
                "name": name,
                "subsistence": subsistence,
                "religion": religion,
            },
        }
        for soc_id, name, lon, lat, subsistence, religion in sorted(rows, key=lambda r: r[1] or "")
    ]

    fc = {
        "type": "FeatureCollection",
        "name": "afr_societies",
        "note": (
            "D-PLACE Ethnographic Atlas societies on the African continent "
            "(ST_Contains vs Natural Earth admin0). Built by "
            "scripts/edop/workbench/build_afr_societies.py."
        ),
        "features": features,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(fc))
    kb = OUT.stat().st_size / 1024
    n_sub = sum(1 for f in features if f["properties"]["subsistence"])
    n_rel = sum(1 for f in features if f["properties"]["religion"])
    print(f"wrote {OUT.relative_to(ROOT)}  ({len(features)} societies, {kb:,.0f} KB)")
    print(f"  subsistence present: {n_sub}/{len(features)}   religion present: {n_rel}/{len(features)}")


if __name__ == "__main__":
    main()
