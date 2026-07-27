"""Persist point-window terrain (local relief, landform-position) for the WO8c EA analysis set.

WO8c Part D wants a "cheap terrain lens" — ruggedness / landform-position sampled around each
society's own coordinate (point-window), preferred over basin-level smx-smn because it dodges the
container problem (no basin-mean smearing across, e.g., a valley + surrounding highlands). No DEM
raster is hosted locally (checked before this WO), but OpenTopoData's public batch API (up to 100
locations/request) makes a *grid* sample around each point cheap: query a 5x5, 1km-spaced grid
(±2km box) per society, and take max-min / mean of the 25 values as the local-relief measure — a
crude but real point-window ruggedness, no raster hosting required.

Scope: the 1,133 EA societies in `output/cdop/wo8b_substrate.parquet` (WO8c's analysis universe),
not all of `dplace.societies` (that's `persist_dplace_elevation.py`, already run separately).

Writes `dplace.society_terrain` (soc_id PK, grid_elev_min/max/mean, relief_range_m,
landform_position, grid_radius_km, grid_spacing_km, n_grid_points, n_grid_resolved).

Usage:
    python scripts/cdop/persist_dplace_terrain.py
"""
from __future__ import annotations

import json
import math
import ssl
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import pandas as pd

try:
    import certifi
except ImportError:
    certifi = None

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.shared.db_utils import db_connect

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output" / "cdop"

BATCH_SIZE = 100
REQ_INTERVAL_S = 1.05
TIMEOUT_S = 15.0

GRID_STEPS_KM = [-2, -1, 0, 1, 2]   # 5x5 => 25 points, 1km spacing, +-2km box
KM_PER_DEG_LAT = 111.32

DDL = """
CREATE TABLE IF NOT EXISTS dplace.society_terrain (
    soc_id            text PRIMARY KEY REFERENCES dplace.societies(id),
    grid_elev_min     double precision,
    grid_elev_max     double precision,
    grid_elev_mean    double precision,
    relief_range_m    double precision,
    landform_position double precision,
    grid_radius_km    double precision,
    grid_spacing_km   double precision,
    n_grid_points     integer,
    n_grid_resolved   integer
);
"""


def _http_get_json(url: str) -> Dict[str, Any]:
    req = Request(url, headers={"Accept": "application/json", "User-Agent": "edop-cdop/0.1"}, method="GET")
    ctx = ssl.create_default_context(cafile=certifi.where()) if certifi else ssl.create_default_context()
    with urlopen(req, timeout=TIMEOUT_S, context=ctx) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _grid_points(lat: float, lon: float) -> List[Tuple[float, float]]:
    dlat_per_km = 1.0 / KM_PER_DEG_LAT
    dlon_per_km = 1.0 / (KM_PER_DEG_LAT * max(math.cos(math.radians(lat)), 1e-6))
    return [(lat + dy * dlat_per_km, lon + dx * dlon_per_km)
            for dy in GRID_STEPS_KM for dx in GRID_STEPS_KM]


def _batch_mapzen_elevations(points: List[Tuple[float, float]]) -> List[Optional[float]]:
    """points: <= BATCH_SIZE (lat, lon) pairs. Returns elevations in the same order (None on miss)."""
    locs = "|".join(f"{lat},{lon}" for lat, lon in points)
    url = f"https://api.opentopodata.org/v1/mapzen?{urlencode({'locations': locs})}"
    payload = _http_get_json(url)
    if payload.get("status") != "OK":
        return [None] * len(points)
    results = payload.get("results") or []
    return [r.get("elevation") for r in results] if len(results) == len(points) else [None] * len(points)


def main() -> None:
    sub = pd.read_parquet(OUT / "wo8b_substrate.parquet")[["soc_id", "lat", "lon"]].dropna()
    print(f"WO8c analysis universe: {len(sub)} EA societies with coordinates")

    # Flatten every society's 25-point grid into one queue, batch across society boundaries.
    queue: List[Tuple[str, float, float]] = []   # (soc_id, lat, lon)
    for soc_id, lat, lon in sub.itertuples(index=False):
        queue.extend((soc_id, plat, plon) for plat, plon in _grid_points(lat, lon))

    elevs: Dict[Tuple[str, int], Optional[float]] = {}
    n_batches = (len(queue) - 1) // BATCH_SIZE + 1
    idx = 0
    for b in range(n_batches):
        chunk = queue[b * BATCH_SIZE:(b + 1) * BATCH_SIZE]
        points = [(lat, lon) for _, lat, lon in chunk]
        try:
            vals = _batch_mapzen_elevations(points)
        except Exception as e:
            print(f"  batch {b + 1}/{n_batches}: request failed ({e}); all points in this batch unresolved")
            vals = [None] * len(points)
        for (soc_id, _, _), v in zip(chunk, vals):
            elevs[(soc_id, idx)] = v
            idx += 1
        if (b + 1) % 20 == 0 or b + 1 == n_batches:
            print(f"  batch {b + 1}/{n_batches} done")
        time.sleep(REQ_INTERVAL_S)

    # Reassemble per-society grids (25 slots each, in queue order) and compute relief stats.
    rows = []
    pos = 0
    for soc_id, lat, lon in sub.itertuples(index=False):
        n = len(GRID_STEPS_KM) ** 2
        vals = [elevs.get((soc_id, pos + k)) for k in range(n)]
        pos += n
        resolved = [v for v in vals if v is not None]
        if len(resolved) < 3:   # too few points to say anything about local relief
            rows.append((soc_id, None, None, None, None, None, 2.0, 1.0, n, len(resolved)))
            continue
        vmin, vmax, vmean = min(resolved), max(resolved), sum(resolved) / len(resolved)
        relief = vmax - vmin
        landform = (vmean - vmin) / relief if relief > 0 else None
        rows.append((soc_id, vmin, vmax, vmean, relief, landform, 2.0, 1.0, n, len(resolved)))

    ok = sum(1 for r in rows if r[4] is not None)
    print(f"resolved relief for {ok} / {len(rows)} societies")

    conn = db_connect()
    cur = conn.cursor()
    cur.execute(DDL)
    conn.commit()
    cur.executemany("""
        INSERT INTO dplace.society_terrain
            (soc_id, grid_elev_min, grid_elev_max, grid_elev_mean, relief_range_m,
             landform_position, grid_radius_km, grid_spacing_km, n_grid_points, n_grid_resolved)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (soc_id) DO UPDATE SET
            grid_elev_min = EXCLUDED.grid_elev_min, grid_elev_max = EXCLUDED.grid_elev_max,
            grid_elev_mean = EXCLUDED.grid_elev_mean, relief_range_m = EXCLUDED.relief_range_m,
            landform_position = EXCLUDED.landform_position, grid_radius_km = EXCLUDED.grid_radius_km,
            grid_spacing_km = EXCLUDED.grid_spacing_km, n_grid_points = EXCLUDED.n_grid_points,
            n_grid_resolved = EXCLUDED.n_grid_resolved
    """, rows)
    conn.commit()
    print(f"wrote {len(rows)} rows -> dplace.society_terrain")
    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
