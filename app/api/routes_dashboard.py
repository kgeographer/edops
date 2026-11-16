"""
app/api/routes_dashboard.py
---------------------------
Routes used only by the Dashboard page (dashboard.html).

/api/profile returns the stored profile of a basin, keyed by (level, hybas_id). For now the store is the ten sample
records in app/static/profiles (each names its own place and coordinates); the page reads this route, not the files,
so a later store (a database table of per-basin profiles) changes nothing in the page.

The place is part of the contract: optional lat and lon (both or neither) say where the profile is for. Profile text
also depends on the point (its elevation and ecoregion, the river distances), so a store that serves any place will use
them to assemble those statements. Today's sample records each describe one place, so with lat and lon the route
returns a record only when that place is within PLACE_MATCH_KM of the point asked about; without them it returns the
basin's record as it is.
"""
import json
import math
from functools import lru_cache
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

router = APIRouter(prefix="/api", tags=["api"])

PROFILES_DIR = Path(__file__).resolve().parents[1] / "static" / "profiles"
PLACE_MATCH_KM = 10   # a sample record describes its own place: the point asked about must be this close


def _km(lat1, lon1, lat2, lon2) -> float:
    r = math.pi / 180
    a = math.sin((lat2 - lat1) * r / 2) ** 2 + math.cos(lat1 * r) * math.cos(lat2 * r) * math.sin((lon2 - lon1) * r / 2) ** 2
    return 2 * 6371 * math.asin(math.sqrt(a))


@lru_cache(maxsize=2)
def _by_basin(stamp: int) -> dict:
    """{hybas_id: record} for the stored records that have a basin; `stamp` (index.json's mtime) refreshes the cache."""
    out = {}
    for p in json.loads((PROFILES_DIR / "index.json").read_text(encoding="utf-8")):
        rec = json.loads((PROFILES_DIR / f"{p['slug']}.json").read_text(encoding="utf-8"))
        if not rec.get("no_basin") and rec.get("hybas_id") is not None:
            out[int(rec["hybas_id"])] = rec
    return out


@router.get("/profile", include_in_schema=False)
def get_profile(level: int = Query(..., description="Basin level; stored profiles exist for 6 only"),
                hybas_id: int = Query(..., description="BasinATLAS basin id"),
                lat: Optional[float] = Query(None, ge=-90, le=90, description="Latitude of the place the profile is for"),
                lon: Optional[float] = Query(None, ge=-180, le=180, description="Longitude of the place the profile is for")):
    if (lat is None) != (lon is None):
        raise HTTPException(status_code=422, detail="lat and lon go together.")
    if level != 6:
        raise HTTPException(status_code=404, detail="Stored profiles exist for Level 06 only.")
    rec = _by_basin((PROFILES_DIR / "index.json").stat().st_mtime_ns).get(hybas_id)
    if rec is None:
        raise HTTPException(status_code=404, detail="No stored profile for this basin.")
    if lat is not None and _km(lat, lon, rec["lat"], rec["lon"]) > PLACE_MATCH_KM:
        raise HTTPException(status_code=404, detail="No stored profile for this place.")
    return rec
