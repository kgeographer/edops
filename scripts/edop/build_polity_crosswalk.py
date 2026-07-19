#!/usr/bin/env python3
"""Build temporal.polity_basin08_crosswalk.

Pre-materialises the ST_Intersection spatial join between every Cliopatria polity
slice and the L08 basin grid. Geometry never leaves the DB — SQL joins directly to
gaz.clio_polities by id.

Run time: ~5 h. Resumable: re-running skips already-processed polity ids.
Usage: python scripts/edop/build_polity_crosswalk.py
"""
import sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from scripts.shared.db_utils import db_connect

EPSILON    = 0.0001
BATCH_SIZE = 100

DDL = """
CREATE TABLE IF NOT EXISTS temporal.polity_basin08_crosswalk (
    polity_id            integer          NOT NULL,
    hybas_id             bigint           NOT NULL,
    weight               double precision NOT NULL,
    basin_in_polity_frac double precision NOT NULL,
    overlap_km2          real             NOT NULL,
    PRIMARY KEY (polity_id, hybas_id)
);
CREATE INDEX IF NOT EXISTS pol_xwalk_polity_idx
    ON temporal.polity_basin08_crosswalk (polity_id);
"""

FETCH_POLITIES = """
SELECT id, name, ST_Area(geog) AS area_m2
FROM   gaz.clio_polities
WHERE  NOT is_component
ORDER  BY area_m2 ASC
"""

ALREADY_DONE = """
SELECT DISTINCT polity_id FROM temporal.polity_basin08_crosswalk
"""

INSERT_SQL = """
INSERT INTO temporal.polity_basin08_crosswalk
       (polity_id, hybas_id, weight, basin_in_polity_frac, overlap_km2)
WITH polity AS (
    SELECT ST_Buffer(ST_MakeValid(geom), 0)             AS geom,
           ST_Buffer(ST_MakeValid(geom), 0)::geography  AS geog,
           ST_Area(ST_Buffer(ST_MakeValid(geom), 0)::geography) AS polity_m2
    FROM   gaz.clio_polities
    WHERE  id = %(polity_id)s
),
inter AS (
    SELECT b.hybas_id,
           ST_Area(ST_Intersection(b.geom, p.geom)::geography) AS overlap_m2,
           ST_Area(b.geog)                          AS basin_m2
    FROM   public.basin08 b, polity p
    WHERE  ST_Intersects(b.geom, p.geom)
)
SELECT %(polity_id)s,
       i.hybas_id,
       i.overlap_m2 / p.polity_m2,
       i.overlap_m2 / i.basin_m2,
       ROUND((i.overlap_m2 / 1e6)::numeric, 2)
FROM   inter i, polity p
WHERE  i.overlap_m2 / p.polity_m2 >= %(epsilon)s
ON CONFLICT (polity_id, hybas_id) DO NOTHING
"""


def main():
    conn = db_connect()
    conn.autocommit = False

    conn.execute(DDL)
    conn.commit()

    polities = conn.execute(FETCH_POLITIES).fetchall()
    done_ids = {r[0] for r in conn.execute(ALREADY_DONE).fetchall()}
    todo     = [(r[0], r[1], float(r[2])) for r in polities if r[0] not in done_ids]

    print(f"Slices total: {len(polities)}  done: {len(done_ids)}  remaining: {len(todo)}", flush=True)

    t0         = time.time()
    t_batch    = time.time()
    batch_rows = 0
    bad        = []   # (polity_id, name, area_km2, error)

    for i, (pid, name, area_m2) in enumerate(todo, 1):
        try:
            cur = conn.execute(INSERT_SQL, {"polity_id": pid, "epsilon": EPSILON})
            n   = cur.rowcount
            batch_rows += n
        except Exception as e:
            try:
                conn.rollback()
            except Exception:
                try: conn.close()
                except Exception: pass
                conn = db_connect()
                conn.autocommit = False
            bad.append((pid, name, round(area_m2 / 1e6), str(e)[:120]))
            print(f"  BAD  id={pid} {name[:40]:<40} {area_m2/1e6:>9.0f} km²  {str(e)[:80]}", flush=True)
            continue

        if i % BATCH_SIZE == 0:
            conn.commit()
            batch_sec  = time.time() - t_batch
            total_sec  = time.time() - t0
            print(f"  [{i:>5}/{len(todo)}] batch {i//BATCH_SIZE} committed  "
                  f"rows: {batch_rows}  bad so far: {len(bad)}  "
                  f"last 100: {batch_sec:.0f}s  elapsed: {total_sec/3600:.2f}h", flush=True)
            batch_rows = 0
            t_batch    = time.time()

    conn.commit()
    elapsed_total = time.time() - t0
    print(f"\nDone in {elapsed_total/3600:.2f} h", flush=True)

    row = conn.execute(
        "SELECT COUNT(*), COUNT(DISTINCT polity_id) FROM temporal.polity_basin08_crosswalk"
    ).fetchone()
    print(f"Rows: {row[0]:,}  polities covered: {row[1]:,}  bad geometry: {len(bad)}")

    if bad:
        print(f"\nBad geometry ({len(bad)} slices) — need ST_MakeValid or manual fix:")
        for pid, name, area_km2, err in bad:
            print(f"  id={pid:<6} {name[:40]:<40} {area_km2:>9} km²  {err}")

    conn.close()


if __name__ == "__main__":
    main()
