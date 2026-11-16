"""
app/api/routes_dashboard.py
---------------------------
Routes used only by the Dashboard page (dashboard.html).

/api/profile returns the stored profile of a basin, keyed by (level, hybas_id). For now the store is the ten sample
records in app/static/profiles (each names its own place and coordinates); the page reads this route, not the files,
so a later store (a database table of per-basin profiles) changes nothing in the page.
"""
import json
from functools import lru_cache
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query

router = APIRouter(prefix="/api", tags=["api"])

PROFILES_DIR = Path(__file__).resolve().parents[1] / "static" / "profiles"


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
                hybas_id: int = Query(..., description="BasinATLAS basin id")):
    if level != 6:
        raise HTTPException(status_code=404, detail="Stored profiles exist for Level 06 only.")
    rec = _by_basin((PROFILES_DIR / "index.json").stat().st_mtime_ns).get(hybas_id)
    if rec is None:
        raise HTTPException(status_code=404, detail="No stored profile for this basin.")
    return rec
