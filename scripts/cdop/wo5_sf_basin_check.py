"""
WO5 Part C plausibility check -- what basin06 polygon actually gets resolved
for the San Francisco example (37.7749, -122.4194), and how well does its
mean elevation/temperature represent the city itself vs. a larger container
(the WO4 Part 0 container-problem question, applied to a new probe)?
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.shared.db_utils import db_connect

conn = db_connect()
with conn.cursor() as cur:
    cur.execute("""
        SELECT hybas_id,
               ele_mt_sav, ele_mt_smn, ele_mt_smx,
               tmp_dc_syr / 10.0 AS tmp_c,
               ST_Area(geom::geography) / 1e6 AS area_km2,
               ST_YMin(geom) AS ymin, ST_YMax(geom) AS ymax,
               ST_XMin(geom) AS xmin, ST_XMax(geom) AS xmax
        FROM public.basin06
        WHERE ST_Within(ST_SetSRID(ST_MakePoint(-122.4194, 37.7749), 4326), geom)
        ORDER BY ST_Area(geom::geography) ASC LIMIT 1
    """)
    row = cur.fetchone()
    cols = [d.name for d in cur.description]
conn.close()

print("SF basin06 record:")
for c, v in zip(cols, row):
    print(f"  {c}: {v}")

print(f"\nBasin bounding box spans roughly "
      f"{(row[7]-row[6]):.2f} deg lon x {(row[6+1]-row[6+0])} — approx size check")
