"""Persist point-window terrain (local relief, landform-position) for the WH Cities corpus.

CITYKIN WO1 Part B wants a terrain lens for the 254 basin-joined WH Cities, sampled at each city's
own coordinate (point-window) rather than basin-aggregate — WO8c established point-window is
materially better (211m vs 928m local relief, the container effect), and Tbilisi (the WO1 Part D
acceptance fixture) is exactly the case an aggregate would smear. `gaz.wh_cities` currently has zero
elevation/terrain columns (confirmed before this script was written).

Direct analogue of `scripts/cdop/persist_dplace_terrain.py` (WO8c, `dplace.society_terrain`): same
OpenTopoData public batch API, same 5x5-point grid, same max-min / mean relief statistic. Universe
here is `gaz.wh_cities` restricted to the 254 rows with a resolved `basin_id` (the CITYKIN corpus),
not all 258. Fetch + relief-statistic logic is factored into `terrain_grid.py` (shared with the WO1a
validation notebook and, eventually, a live query-by-coordinate API path) — see that module's
docstring for the grid radius (+-10km/5km-spacing, widened from WO8c's +-2km/1km; `wo1_findings.md`)
and the negative-elevation (bathymetric-artifact) filter (WO1a, `wo1_findings.md` follow-up).

Writes `gaz.wh_cities_terrain` (city_id PK, grid_elev_min/max/mean, relief_range_m,
landform_position, grid_radius_km, grid_spacing_km, n_grid_points, n_grid_resolved, n_grid_land).

Usage:
    python scripts/cdop/citykin/persist_whcities_terrain.py
"""
from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.shared.db_utils import db_connect
from scripts.cdop.citykin.terrain_grid import (
    DEFAULT_RADIUS_KM, DEFAULT_SPACING_KM, fetch_elevations, grid_points, relief_stats,
)

BATCH_SIZE = 100
REQ_INTERVAL_S = 1.05

DDL = """
CREATE TABLE IF NOT EXISTS gaz.wh_cities_terrain (
    city_id           integer PRIMARY KEY REFERENCES gaz.wh_cities(id),
    grid_elev_min     double precision,
    grid_elev_max     double precision,
    grid_elev_mean    double precision,
    relief_range_m    double precision,
    landform_position double precision,
    grid_radius_km    double precision,
    grid_spacing_km   double precision,
    n_grid_points     integer,
    n_grid_resolved   integer,
    n_grid_land       integer
);
"""
ADD_COL_SQL = """
ALTER TABLE gaz.wh_cities_terrain ADD COLUMN IF NOT EXISTS n_grid_land integer;
"""


def main() -> None:
    conn = db_connect()

    import warnings
    warnings.filterwarnings("ignore", message="pandas only supports SQLAlchemy")
    cities = pd.read_sql(
        "SELECT id AS city_id, city, country, ST_Y(geom) AS lat, ST_X(geom) AS lon "
        "FROM gaz.wh_cities WHERE basin_id IS NOT NULL ORDER BY id",
        conn,
    )
    print(f"CITYKIN corpus: {len(cities)} basin-joined WH Cities with coordinates")

    # Flatten every city's 25-point grid into one queue, batch across city boundaries.
    queue: List[Tuple[int, float, float]] = []   # (city_id, lat, lon)
    for city_id, _city, _country, lat, lon in cities.itertuples(index=False):
        queue.extend((city_id, plat, plon) for plat, plon in grid_points(lat, lon))

    elevs: Dict[Tuple[int, int], Optional[float]] = {}
    n_batches = (len(queue) - 1) // BATCH_SIZE + 1
    idx = 0
    for b in range(n_batches):
        chunk = queue[b * BATCH_SIZE:(b + 1) * BATCH_SIZE]
        points = [(lat, lon) for _, lat, lon in chunk]
        try:
            vals = fetch_elevations(points)
        except Exception as e:
            print(f"  batch {b + 1}/{n_batches}: request failed ({e}); all points in this batch unresolved")
            vals = [None] * len(points)
        for (city_id, _, _), v in zip(chunk, vals):
            elevs[(city_id, idx)] = v
            idx += 1
        if (b + 1) % 20 == 0 or b + 1 == n_batches:
            print(f"  batch {b + 1}/{n_batches} done")
        time.sleep(REQ_INTERVAL_S)

    # Reassemble per-city grids (25 slots each, in queue order) and compute land-only relief stats.
    rows = []
    pos = 0
    n = 25
    for city_id, _city, _country, lat, lon in cities.itertuples(index=False):
        vals = [elevs.get((city_id, pos + k)) for k in range(n)]
        pos += n
        stats = relief_stats(vals)
        rows.append((
            city_id, stats["grid_elev_min"], stats["grid_elev_max"], stats["grid_elev_mean"],
            stats["relief_range_m"], stats["landform_position"], DEFAULT_RADIUS_KM, DEFAULT_SPACING_KM,
            stats["n_grid_points"], stats["n_grid_resolved"], stats["n_grid_land"],
        ))

    ok = sum(1 for r in rows if r[3] is not None)
    contaminated = sum(1 for r in rows if r[9] > r[10])   # n_grid_resolved > n_grid_land: some point(s) filtered
    print(f"resolved relief for {ok} / {len(rows)} cities  |  "
          f"{contaminated} cities had >=1 grid point filtered as bathymetric (elevation < 0)")

    cur = conn.cursor()
    cur.execute(DDL)
    cur.execute(ADD_COL_SQL)
    conn.commit()
    cur.executemany("""
        INSERT INTO gaz.wh_cities_terrain
            (city_id, grid_elev_min, grid_elev_max, grid_elev_mean, relief_range_m,
             landform_position, grid_radius_km, grid_spacing_km, n_grid_points, n_grid_resolved,
             n_grid_land)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (city_id) DO UPDATE SET
            grid_elev_min = EXCLUDED.grid_elev_min, grid_elev_max = EXCLUDED.grid_elev_max,
            grid_elev_mean = EXCLUDED.grid_elev_mean, relief_range_m = EXCLUDED.relief_range_m,
            landform_position = EXCLUDED.landform_position, grid_radius_km = EXCLUDED.grid_radius_km,
            grid_spacing_km = EXCLUDED.grid_spacing_km, n_grid_points = EXCLUDED.n_grid_points,
            n_grid_resolved = EXCLUDED.n_grid_resolved, n_grid_land = EXCLUDED.n_grid_land
    """, rows)
    conn.commit()
    print(f"wrote {len(rows)} rows -> gaz.wh_cities_terrain")
    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
