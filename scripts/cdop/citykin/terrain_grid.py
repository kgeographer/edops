"""Shared point-window terrain grid: fetch + relief-statistic computation.

Factored out because it now has three real consumers: `persist_whcities_terrain.py` (the 254-city
corpus), the WO1a validation notebook (Tbilisi + a flat-city fixture, neither a `gaz.wh_cities` row),
and — once WO1a wires the retrieval head — a live "query by arbitrary coordinate" API path. One
fetch-and-compute implementation, not three copies to keep in sync.

**Negative-elevation filter.** OpenTopoData's `mapzen` dataset returns real bathymetric depths for
ocean points, not null/zero. A coastal city's +-10km grid can dip into open water and mix seafloor
depth into the same relief calculation as the city's actual land terrain — confirmed on Willemstad
(Curacao): raw grid spanned -1249m to 67m (land points cluster at 7-67m; everything below 0 is ocean),
giving a nonsense relief_range_m of ~1300m and a deeply negative mean. Fix: drop any individual grid
point with elevation < 0 before computing min/max/mean/relief/landform_position. Known tradeoff: a
handful of real places sit shallowly below sea level on land (Amsterdam-area polders, Baku, ~0 to
-30m) and would have a few valid points discarded too -- accepted, since the corpus-wide contamination
this fixes is severe (up to -1249m) and this project's specific cases are shallow enough that losing a
couple of points out of 25 doesn't starve the statistic (the existing <3-resolved-points fallback still
applies, now counting land points only, so a heavily-coastal city that ends up with too few land points
degrades to null rather than reporting a false number).
"""
from __future__ import annotations

import json
import math
import ssl
import time
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlencode
from urllib.request import Request, urlopen

try:
    import certifi
except ImportError:
    certifi = None

BATCH_SIZE = 100
REQ_INTERVAL_S = 1.05
TIMEOUT_S = 15.0
KM_PER_DEG_LAT = 111.32

# The corpus default -- +-10km box, 5km spacing, 5x5=25 points. Widened from WO8c's +-2km/1km after
# CITYKIN WO1 Cells 7-8 found 2km too small to reach the highlands that enclose a classic intermontane
# basin, and confirmed 25 vs 81 points agree closely at this radius (wo1_findings.md).
DEFAULT_RADIUS_KM = 10.0
DEFAULT_SPACING_KM = 5.0
MIN_RESOLVED_LAND_POINTS = 3


def grid_points(lat: float, lon: float, radius_km: float = DEFAULT_RADIUS_KM,
                 n: int = 5) -> List[Tuple[float, float]]:
    """n x n grid of (lat, lon), spanning +-radius_km in each direction."""
    import numpy as np
    steps = np.linspace(-radius_km, radius_km, n)
    dlat_per_km = 1.0 / KM_PER_DEG_LAT
    dlon_per_km = 1.0 / (KM_PER_DEG_LAT * max(math.cos(math.radians(lat)), 1e-6))
    return [(lat + dy * dlat_per_km, lon + dx * dlon_per_km) for dy in steps for dx in steps]


def fetch_elevations(points: List[Tuple[float, float]]) -> List[Optional[float]]:
    """points: <= BATCH_SIZE (lat, lon) pairs. Returns elevations in the same order (None on miss)."""
    locs = "|".join(f"{lat},{lon}" for lat, lon in points)
    url = f"https://api.opentopodata.org/v1/mapzen?{urlencode({'locations': locs})}"
    req = Request(url, headers={"Accept": "application/json", "User-Agent": "edop-cdop/0.1"}, method="GET")
    ctx = ssl.create_default_context(cafile=certifi.where()) if certifi else ssl.create_default_context()
    with urlopen(req, timeout=TIMEOUT_S, context=ctx) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    if payload.get("status") != "OK":
        return [None] * len(points)
    results = payload.get("results") or []
    return [r.get("elevation") for r in results] if len(results) == len(points) else [None] * len(points)


def fetch_elevations_batched(points: List[Tuple[float, float]],
                              sleep: bool = True) -> List[Optional[float]]:
    """Same as fetch_elevations but chunks to BATCH_SIZE and rate-limits -- for point counts that may
    exceed the 100/request cap (e.g. many cities' grids queued together)."""
    out: List[Optional[float]] = []
    for i in range(0, len(points), BATCH_SIZE):
        chunk = points[i:i + BATCH_SIZE]
        out.extend(fetch_elevations(chunk))
        if sleep and i + BATCH_SIZE < len(points):
            time.sleep(REQ_INTERVAL_S)
    return out


def relief_stats(elevations: List[Optional[float]]) -> Dict[str, Any]:
    """Land-only min/max/mean/relief/landform_position from a raw grid-point elevation list.

    Drops None (unresolved) and negative (bathymetric-artifact) values first -- see module docstring.
    Returns None for every stat if fewer than MIN_RESOLVED_LAND_POINTS land points survive.
    """
    resolved = [v for v in elevations if v is not None]
    land = [v for v in resolved if v >= 0]
    n_land = len(land)
    if n_land < MIN_RESOLVED_LAND_POINTS:
        return {
            "grid_elev_min": None, "grid_elev_max": None, "grid_elev_mean": None,
            "relief_range_m": None, "landform_position": None,
            "n_grid_points": len(elevations), "n_grid_resolved": len(resolved), "n_grid_land": n_land,
        }
    vmin, vmax, vmean = min(land), max(land), sum(land) / n_land
    relief = vmax - vmin
    landform = (vmean - vmin) / relief if relief > 0 else None
    return {
        "grid_elev_min": vmin, "grid_elev_max": vmax, "grid_elev_mean": vmean,
        "relief_range_m": relief, "landform_position": landform,
        "n_grid_points": len(elevations), "n_grid_resolved": len(resolved), "n_grid_land": n_land,
    }


def point_window_terrain(lat: float, lon: float, radius_km: float = DEFAULT_RADIUS_KM,
                          n: int = 5) -> Dict[str, Any]:
    """One city/point: fetch its grid and return relief_stats(), plus the grid geometry used."""
    pts = grid_points(lat, lon, radius_km=radius_km, n=n)
    vals = fetch_elevations(pts)   # single batch when n<=10 (n*n <= 100)
    stats = relief_stats(vals)
    stats["grid_radius_km"] = radius_km
    stats["grid_spacing_km"] = (2 * radius_km) / (n - 1)
    return stats
