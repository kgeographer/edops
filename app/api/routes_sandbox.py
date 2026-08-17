"""
app/api/routes_sandbox.py
---------------------------
Routes used only by the Sandbox page (sandbox.html). Renamed from routes.py
(2026-08-16) once the last other page's routes were split out of it -- see
docs/edop/routes_audit.txt for the classification this split is based on.
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Any, Dict, List, Optional, Tuple
import json
import urllib.parse
import urllib.request
import ssl
import certifi
from datetime import datetime, timezone

from app.db.signature import get_signature
from app.db.temporal import get_temporal_context
from app.db.hyde import get_hyde_land_use
from app.db.narrative import get_narrative
from app.db.connection import db_connect
from app.db.seasonality import (
    find_similar, find_conjunction, get_conjunction_registry,
)
from app.db.context import get_context, get_context_population
from app.db import climate_classes as cc
from app.settings import settings
from scripts.edop.areas.engine import areal_signature, areal_signature_polygon, single_basin_signature, basin_ring_signature, resolve_basin_ring
from app.api.routes_common import _HYDE_SAFE_VARS, _whg_suggest, _whg_entity

from pathlib import Path
import re

router = APIRouter(prefix="/api", tags=["api"])

# ISO 3166-1 alpha-2 → country name; loaded once at startup from static file.
_CCODES: Dict[str, str] = json.loads(
    (Path(__file__).parent.parent / "data" / "ccodes.json").read_text(encoding="utf-8")
)


# -----------------------
# WHG API and utility helpers
# -----------------------
# _http_get_json/_whg_suggest_first/_whg_suggest/_whg_entity/_extract_lonlat moved to
# routes_common.py (2026-08-16, routes split) -- shared with /resolve (Workbench).
# _http_post_json/_whg_reconcile_query/_whg_reconcile_extend/_parse_centroid_string/
# _merge_reconcile_results moved to routes_workbench.py -- only used by /whg-reconcile.


def _whg_search_candidates(query: str, limit: int = 10) -> List[Dict]:
    """Search WHG using suggest + entity for reliable geometry.

    reconcile+extend returns child IDs (gn:, osm:) that have empty geometry
    in the extend response.  suggest returns canonical parent IDs whose entity
    record has geometry in GeoJSON Feature format.
    """
    suggest_results = _whg_suggest(query, limit=limit)
    if not suggest_results:
        return []

    results = []
    entity_calls = 0
    for r in suggest_results:
        if len(results) >= 3 or entity_calls >= 5:
            break
        place_id = r.get("id", "")
        lon, lat = None, None
        countries = []
        types = []
        fclasses = []

        # Fallback country from suggest description field ("Country: ML")
        desc = r.get("description", "") or ""
        m = re.match(r"Country:\s*(\w+)", desc)
        if m:
            countries = [{"code": m.group(1)}]

        # Fetch entity for geometry and richer metadata
        if place_id:
            try:
                entity_calls += 1
                entity = _whg_entity(place_id)
                geom = entity.get("geometry") or {}
                if geom.get("type") == "Point":
                    coords = geom.get("coordinates") or []
                    if len(coords) >= 2:
                        lon, lat = float(coords[0]), float(coords[1])
                props = entity.get("properties") or {}
                ccodes = props.get("ccodes") or []
                if ccodes:
                    countries = [{"code": c} for c in ccodes]
                types = [{"label": t.get("label", "")} for t in (entity.get("types") or [])]
                fclasses = props.get("fclasses") or []
            except Exception:
                pass  # keep suggest-only data if entity call fails

        # Drop wikidata-only noise: no GeoNames fclass means unclassified wikidata entry
        if not fclasses:
            continue

        results.append({
            "id": place_id,
            "name": r.get("name", ""),
            "score": r.get("score", 0),
            "match": r.get("match", False),
            "alt_names": r.get("alt_names", []),
            "lon": lon,
            "lat": lat,
            "countries": countries,
            "types": types,
            "fclasses": fclasses,
        })

    return results


# -----------------------
# API endpoints
# -----------------------

def _resolve_basin(conn, lat: float, lon: float, level: int = 6) -> int:
    """Return the hybas_id at the given level containing (lat, lon); raises 404 if none found."""
    table = "basin06" if level == 6 else "basin08"
    with conn.cursor() as cur:
        cur.execute(
            f"SELECT hybas_id FROM public.{table} "
            "WHERE ST_Within(ST_SetSRID(ST_MakePoint(%s, %s), 4326), geom) "
            "ORDER BY ST_Area(geom::geography) ASC LIMIT 1",
            (lon, lat),
        )
        row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="No basin found at this location")
    return int(row[0])


def _gaz_join(conn, hybas_ids: list) -> dict:
    """Return {hybas_id: (place_id, place_name, ccodes, lat, lon)} for a list of ids."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT DISTINCT ON (hybas_id_l06)
                hybas_id_l06, place_id, place_name, ccodes, lat, lon
            FROM gaz.whg_gaz
            WHERE hybas_id_l06 = ANY(%s)
            ORDER BY hybas_id_l06, place_id
            """,
            (hybas_ids,),
        )
        return {int(r[0]): r for r in cur.fetchall()}


@router.get("/similarity/conjunction/lenses", include_in_schema=False)
def similarity_conjunction_lenses():
    """Return the conjunction lens registry (WO6c) for the panel's lens selector.

    Response
    --------
    {"lenses": [{"lens_id", "group", "label", "shade_by",
                 "conditions": [{"condition", "kind", "default"}, ...]}, ...]}
    """
    return {"lenses": get_conjunction_registry()}


@router.get("/similarity/conjunction", include_in_schema=False)
def similarity_conjunction(
    lat: float,
    lon: float,
    lens: str = "climate.precip",
    level: int = 6,
    corr: Optional[float] = None,
    ratio: Optional[float] = None,
    cv: Optional[float] = None,
    t_level: Optional[float] = None,
    t_range: Optional[float] = None,
    elev_band: Optional[float] = None,
    relief_band: Optional[float] = None,
):
    """Return the set of basins that satisfy EVERY condition of the lens (WO6c; terrain.regime WO3).

    Non-compensatory conjunction on the raw twelve-value precipitation curve (WO6b backbone), or on
    basin-aggregate elevation/relief for terrain.regime (WO3). Output is a painted set, not a ranked
    list: membership is binary, empty is honest scarcity.

    Bands (all optional; per-variable units, fall back to the schema default):
      corr        — precip shape correlation cut (e.g. 0.85 / 0.90 / 0.95)
      ratio       — precip magnitude ratio band (e.g. 1.25 / 1.5 / 2.0)
      cv          — precip amplitude cv band (e.g. 0.10 / 0.15 / 0.25)
      t_level     — temperature level band, °C (e.g. 2 / 3 / 4)
      t_range     — temperature range band, °C (e.g. 2 / 4 / 6)
      elev_band   — terrain elevation band, ±m (e.g. 25 / 50 / 100 — WO3 Part B)
      relief_band — terrain relief-range band, ±m (e.g. 50 / 100 / 200 — WO3 Part B)

    Response
    --------
    {
      "lens_id", "lens_label", "level", "query_basin_id", "shade_by",
      "bands": {condition: value, ...},        # effective band values
      "set_size": int,
      "query_values": {...},
      "per_condition": {condition: count, ...}, # each condition alone
      "attrition": [{condition, remaining}, ...],
      "spatial": {"max_dist_from_query_km", "diameter_km"},
      "members": [{basin_id, corr, pre_total_mm, elev_m, relief_range_m, lat, lon,
                    place_id, place_name, ccodes}, ...]
    }
    """
    if level not in (6, 8):
        raise HTTPException(status_code=400, detail="level must be 6 or 8")
    bands = {
        "precip_shape":        corr,
        "precip_magnitude":    ratio,
        "precip_amplitude_cv": cv,
        "temp_level":          t_level,
        "temp_range":          t_range,
        "terrain_elev":        elev_band,
        "terrain_relief":      relief_band,
    }
    bands = {k: v for k, v in bands.items() if v is not None}

    conn = db_connect()
    try:
        query_hybas_id = _resolve_basin(conn, lat, lon, level=level)
        try:
            meta, members = find_conjunction(
                query_hybas_id, lens_id=lens, bands=bands, level=level,
            )
        except RuntimeError as e:
            raise HTTPException(status_code=503, detail=str(e))
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))

        gaz_by_basin = _gaz_join(conn, [m["hybas_id"] for m in members]) if members else {}
        out_members = []
        for m in members:
            place = gaz_by_basin.get(m["hybas_id"])
            out_members.append({
                "basin_id":       m["hybas_id"],
                "corr":           m["corr"],
                "pre_total_mm":   m["pre_total_mm"],
                "elev_m":         m["elev_m"],
                "relief_range_m": m["relief_range_m"],
                "lat":            m["lat"],
                "lon":            m["lon"],
                "place_id":   place[1] if place else None,
                "place_name": place[2] if place else None,
                "ccodes":     place[3] if place else None,
            })

        return {
            "lens_id":        meta["lens_id"],
            "lens_label":     meta["lens_label"],
            "level":          meta["level"],
            "query_basin_id": meta["query_hybas_id"],
            "shade_by":       meta["shade_by"],
            "bands":          meta["bands"],
            "set_size":       meta["set_size"],
            "query_values":   meta["query_values"],
            "per_condition":  meta["per_condition"],
            "attrition":      meta["attrition"],
            "spatial":        meta["spatial"],
            "members":        out_members,
        }
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# WO7 — climate classes (two discrete axes + composed cell). In-memory index
# in app/db/climate_classes.py; L06 eager at startup, L08 lazy on first use.
# ---------------------------------------------------------------------------
@router.get("/explorer/climate-class", include_in_schema=False)
def explorer_climate_class(axis: str, level: int = 6):
    """Flat {hybas_id: cat_id} + category list for one climate-class axis (WO7).

    axis: 'modality' (5 classes) or 'phase' (4 classes), each a clean choropleth. The composed
    cell is a client-side picker over the two axes (WO7a Issue 2), not a separate choropleth.
    Response: {meta: {axis, level, n_total, conventions}, categories: [...], values: {id: cat_id}}
    """
    if level not in (6, 8):
        raise HTTPException(status_code=400, detail="level must be 6 or 8")
    try:
        categories, values = cc.axis_values(level, axis)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {
        "meta": {"axis": axis, "level": level, "n_total": len(values),
                 "conventions": cc.CONVENTIONS},
        "categories": categories,
        "values": values,
    }


# /similarity/climate-class removed 2026-08-16 -- superseded by the WO6b/WO6c conjunction
# panel; not called by any live template, confirmed unrelated to Workbench's WH Cities
# similarity mechanisms (find_similar/LENS_REGISTRY in seasonality.py never referenced
# app.db.climate_classes).


# Radius options per level (WO5 Part B): 2500km excluded at L08 -- across a
# 258-city geographically diverse sample, 99.2% exceed the ~5,000-basin WebGL
# render budget at that radius/level combination (median count 13,845, vs.
# L06's max of 2,163 at the same radius). All other radius/level combinations
# stay comfortably under budget (worst case L08/1000km: 4,579 of 5,000).
_CONTEXT_RADII_BY_LEVEL: Dict[int, List[int]] = {
    6: [250, 500, 1000, 2500],
    8: [250, 500, 1000],
}


@router.get("/context", include_in_schema=False)
def context(lat: float, lon: float, level: int = 6, radius_km: int = 500):
    """Return a basin's position against two reference populations: all basins
    at the level, and basins within radius_km of (lat, lon).

    No ranking, no candidate list, no composite distance -- each variable is
    reported independently (contrast with a composite/whitened distance, which
    can let variables compensate for one another; see wo5_findings.md Part A
    Check 3).

    Parameters
    ----------
    lat, lon   : query coordinates
    level      : 6 (default) or 8
    radius_km  : one of _CONTEXT_RADII_BY_LEVEL[level] -- 2500 is excluded at
                 level=8 (see comment above)

    Response
    --------
    {
      "level": int, "query_basin_id": int, "radius_km": int, "radius_count": int,
      "rows": [
        { "variable": str, "label": str, "unit": str, "value": float|null,
          "global_percentile": float|null, "radius_percentile": float|null },
        ...
      ]
    }
    """
    if level not in (6, 8):
        raise HTTPException(status_code=400, detail="level must be 6 or 8")
    allowed_radii = _CONTEXT_RADII_BY_LEVEL[level]
    if radius_km not in allowed_radii:
        raise HTTPException(
            status_code=400,
            detail=f"radius_km must be one of {allowed_radii} for level={level}",
        )

    conn = db_connect()
    try:
        query_hybas_id = _resolve_basin(conn, lat, lon, level=level)
        try:
            result = get_context(query_hybas_id, lat, lon, level, radius_km)
        except RuntimeError as e:
            raise HTTPException(status_code=503, detail=str(e))
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))

        return {
            "level":          result["level"],
            "query_basin_id": result["query_hybas_id"],
            "radius_km":      result["radius_km"],
            "radius_count":   result["radius_count"],
            "rows":           result["rows"],
        }
    finally:
        conn.close()


@router.get("/context/population", include_in_schema=False)
def context_population(lat: float, lon: float, level: int = 6, radius_km: int = 500):
    """Return raw per-variable values for every basin within radius_km of
    (lat, lon) -- the population the Context tab's map choropleths. Pair with
    POST /api/basin-geom (same hybas_id list) for geometry.

    No basin resolution needed (unlike /api/context) -- purely an in-memory
    radius query against the query point, no DB round trip.

    Response
    --------
    {
      "level": int, "radius_km": int, "radius_count": int,
      "basins": [ { "hybas_id": int, "<variable>": float|null, ... }, ... ]
    }
    """
    if level not in (6, 8):
        raise HTTPException(status_code=400, detail="level must be 6 or 8")
    allowed_radii = _CONTEXT_RADII_BY_LEVEL[level]
    if radius_km not in allowed_radii:
        raise HTTPException(
            status_code=400,
            detail=f"radius_km must be one of {allowed_radii} for level={level}",
        )

    try:
        return get_context_population(lat, lon, level, radius_km)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


def _fetch_basin_geom(hybas_ids: list, level: int) -> dict:
    """Query basin geometries at precision 3 (~100 m). Shared by GET and POST handlers."""
    table = "basin06" if level == 6 else "basin08"
    conn = db_connect()
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"SELECT hybas_id, ST_AsGeoJSON(geom, 3) FROM public.{table} "
                "WHERE hybas_id = ANY(%s)",
                (hybas_ids,),
            )
            return {str(int(row[0])): row[1] for row in cur.fetchall()}
    finally:
        conn.close()


@router.get("/basin-geom", include_in_schema=False)
def basin_geom(ids: str, level: int = 6):
    """Return GeoJSON geometry strings for a list of basin hybas_ids (GET, max 200).

    For larger sets use POST /api/basin-geom with body {"ids": [...], "level": 6}.
    """
    if level not in (6, 8):
        raise HTTPException(status_code=400, detail="level must be 6 or 8")
    try:
        hybas_ids = [int(x.strip()) for x in ids.split(",") if x.strip()]
    except ValueError:
        raise HTTPException(status_code=400, detail="ids must be comma-separated integers")
    if not hybas_ids or len(hybas_ids) > 200:
        raise HTTPException(status_code=400, detail="ids must contain 1–200 hybas_id values")
    return _fetch_basin_geom(hybas_ids, level)


class BasinGeomRequest(BaseModel):
    ids: List[int]
    level: int = 6


@router.post("/basin-geom", include_in_schema=False)
def basin_geom_post(body: BasinGeomRequest):
    """Return GeoJSON geometry strings for a list of basin hybas_ids (POST, max 6000).

    Body: {"ids": [hybas_id, ...], "level": 6}
    Returns: {"<hybas_id>": "<GeoJSON geometry string>", ...}
    """
    if body.level not in (6, 8):
        raise HTTPException(status_code=400, detail="level must be 6 or 8")
    if not body.ids or len(body.ids) > 6000:
        raise HTTPException(status_code=400, detail="ids must contain 1–6000 hybas_id values")
    return _fetch_basin_geom(body.ids, body.level)


@router.get("/narrative", include_in_schema=False)
def narrative(
    lat: float,
    lon: float,
    name: Optional[str] = None,
    year_start: Optional[int] = None,
    year_end: Optional[int] = None,
):
    """Generate a plain-language narrative for a location using Claude.

    Fetches the signature (and optionally temporal context) then calls the
    Claude API with the rev1 narrative prompt. Returns {narrative: str}.

    Parameters
    ----------
    lat, lon   : coordinates
    name       : display name for the place (shown in the narrative)
    year_start : if provided with year_end, includes LMR PDSI temporal context
    year_end   : end year for temporal context
    """
    sig = get_signature(lat=lat, lon=lon)
    if sig is None:
        raise HTTPException(status_code=404, detail="No basin covers this point")

    temporal = None
    if year_start is not None and year_end is not None:
        temporal = get_temporal_context(lat=lat, lon=lon, year_start=year_start, year_end=year_end)
        if "error" in temporal:
            temporal = None

    text = get_narrative(sig=sig, place_name=name, temporal=temporal)
    if text.startswith("ERROR:"):
        raise HTTPException(status_code=500, detail=text)
    return {"narrative": text}


# /temporal removed 2026-08-16 -- a pre-integration standalone LMR/volcanic fetch; superseded
# once Band T was folded into /api/signature's own bands=...T... handling (routes_common.py).
# Not called by any live template.


# /resolve moved to routes_workbench.py (2026-08-16, routes split).


@router.get("/whg-suggest", include_in_schema=False)
def whg_suggest(q: str, limit: int = 5):
    """Return up to `limit` WHG suggest candidates for autocomplete.

    Each result includes: id, name, score, alt_names, description (country).
    """
    q = (q or "").strip()
    if not q:
        return {"results": []}

    if limit < 1:
        limit = 1
    elif limit > 20:
        limit = 20

    try:
        raw = _whg_suggest(q, limit=limit)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"WHG suggest failed: {e}")

    # Reshape for frontend: flatten to essentials
    results = []
    for r in raw:
        results.append({
            "id": r.get("id"),
            "name": r.get("name"),
            "score": r.get("score"),
            "description": r.get("description"),  # e.g. "Country: ML"
            "alt_names": r.get("alt_names") or [],
        })

    return {"results": results}


# /whg-reconcile moved to routes_workbench.py (2026-08-16, routes split).


@router.get("/whg/suggest", include_in_schema=False)
def whg_suggest_places(q: str, limit: int = 8, country: str = ""):
    """Settlement/site lookup via WHG suggest, filtered to fclasses P (populated) and S (site).

    Accepts an optional `country` free-text string (e.g. "Mali", "ital") which is resolved
    to an ISO-3166-1 alpha-2 code via ILIKE against gaz.ccodes, then passed to WHG as a
    countries filter. If the country hint doesn't match, the search proceeds without it.

    The frontend passes a comma-parsed country hint: "Timbuktu, Mali" → q="Timbuktu", country="Mali".
    """
    q = (q or "").strip()
    if not q or len(q) < 2:
        return {"results": []}
    limit = max(1, min(limit, 20))

    country = (country or "").strip()
    ccode = None
    if country:
        try:
            conn = db_connect()
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT iso_a2 FROM gaz.ccodes WHERE name ILIKE %s LIMIT 1",
                    (f"%{country}%",),
                )
                row = cur.fetchone()
                if row:
                    ccode = row[0]
            conn.close()
        except Exception:
            pass  # country hint is optional; never blocks search

    try:
        raw = _whg_suggest(q, limit=limit, fclasses="P,S", countries=ccode)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"WHG suggest failed: {e}")

    results = []
    for r in raw:
        pt = r.get("repr_point")
        if not pt or len(pt) < 2:
            continue
        ccs = r.get("ccodes") or []
        results.append({
            "id": r.get("id"),
            "name": r.get("name"),
            "lon": float(pt[0]),
            "lat": float(pt[1]),
            "ccodes": ccs,
            "alt_names": (r.get("alt_names") or [])[:10],
            "cname": _CCODES.get(ccs[0], "") if ccs else "",
        })

    return {"results": results}


@router.get("/similar", include_in_schema=False)
def similar(id_no: int, limit: int = 5):
    """Return most similar WH sites to the given site by id_no."""
    try:
        conn = db_connect()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    b.id_no,
                    b.name_en,
                    b.lon,
                    b.lat,
                    ROUND(sim.distance::numeric, 2) as distance,
                    c.cluster_label
                FROM edop_similarity sim
                JOIN edop_wh_sites a ON a.site_id = sim.site_a
                JOIN edop_wh_sites b ON b.site_id = sim.site_b
                LEFT JOIN edop_clusters c ON c.site_id = b.site_id
                WHERE a.id_no = %s
                ORDER BY sim.distance ASC
                LIMIT %s
            """, (id_no, limit))

            results = []
            for row in cur.fetchall():
                results.append({
                    "id_no": row[0],
                    "name_en": row[1],
                    "lon": float(row[2]),
                    "lat": float(row[3]),
                    "distance": float(row[4]),
                    "cluster_label": row[5]
                })

            return {"source_id_no": id_no, "similar": results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'conn' in locals():
            conn.close()


# WH Cities endpoints (whc-cities, whc-similar, whc-similar-env-lens,
# whc-similar-terrain, whc-similar-env-by-coord, whc-similar-text,
# whc-summaries) moved to routes_workbench.py (2026-08-16, routes split).


# -----------------------
# Basin Cluster endpoints
# -----------------------

# -----------------------
# Gazetteer endpoints
# -----------------------
# gaz-similar, gaz-suggest moved to routes_workbench.py (2026-08-16, routes split).


# Ecoregion Hierarchy endpoints (realms, subrealms, bioregions, ecoregions,
# their /geom variants, and wikitext) moved to routes_workbench.py
# (2026-08-16, routes split).


# -----------------------
# Basin neighborhood preview
# -----------------------

@router.get("/basin-preview", include_in_schema=False)
def basin_preview(lat: float, lon: float, level: int = 8):
    """Return hydro-context layers for a point: containing basin, adjacent basins, main river lines."""
    basin_table = "basin06" if level == 6 else "basin08"
    try:
        conn = db_connect()
        with conn.cursor() as cur:
            pt_geog = f"ST_SetSRID(ST_MakePoint({lon}, {lat}), 4326)::geography"

            # 1. Containing basin (smallest ST_Covers — what the signature currently picks)
            cur.execute(f"""
                SELECT hybas_id, up_area, ST_AsGeoJSON(geom, 5) AS geom
                FROM public.{basin_table}
                WHERE ST_Covers(geom, ST_SetSRID(ST_MakePoint(%s, %s), 4326))
                ORDER BY ST_Area(geom::geography) ASC
                LIMIT 1
            """, (lon, lat))
            cb = cur.fetchone()
            containing = {
                "type": "Feature",
                "properties": {"hybas_id": cb[0], "up_area": round(cb[1], 0)},
                "geometry": json.loads(cb[2])
            } if cb else None

            # 2. Adjacent basins within 50km (true metric via geog column)
            cur.execute(f"""
                SELECT hybas_id, up_area, ST_AsGeoJSON(geom, 5) AS geom
                FROM public.{basin_table}
                WHERE ST_DWithin(geog, {pt_geog}, 50000)
                ORDER BY up_area DESC
            """)
            adjacent = {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "properties": {"hybas_id": r[0], "up_area": round(r[1], 0)},
                        "geometry": json.loads(r[2])
                    }
                    for r in cur.fetchall()
                ]
            }

            # 3. Main river lines within 60km (ord_clas=1 largest, <=2 adds secondary channels)
            cur.execute(f"""
                SELECT ord_clas, dis_av_cms, ST_AsGeoJSON(geom, 5) AS geom
                FROM gaz.hydrorivers
                WHERE ST_DWithin(geog, {pt_geog}, 60000)
                AND ord_clas <= 2
            """)
            rivers = {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "properties": {"ord_clas": r[0], "dis_av_cms": round(r[1], 1)},
                        "geometry": json.loads(r[2])
                    }
                    for r in cur.fetchall()
                ]
            }

        return {
            "point": {"lat": lat, "lon": lon},
            "containing_basin": containing,
            "adjacent_basins": adjacent,
            "rivers": rivers
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/basin/geom", include_in_schema=False)
def basin_geom(ids: str, level: int = 6):
    """Return a GeoJSON FeatureCollection for a comma-separated list of hybas_ids."""
    try:
        id_list = [int(x.strip()) for x in ids.split(",") if x.strip()]
    except ValueError:
        raise HTTPException(status_code=422, detail="ids must be a comma-separated list of integers")
    if not id_list:
        raise HTTPException(status_code=422, detail="ids must not be empty")

    basin_table = "basin06" if level == 6 else "basin08"
    placeholders = ", ".join(["%s"] * len(id_list))
    try:
        conn = db_connect()
        with conn.cursor() as cur:
            cur.execute(f"""
                SELECT hybas_id, ST_AsGeoJSON(geom, 5) AS geom
                FROM public.{basin_table}
                WHERE hybas_id IN ({placeholders})
            """, id_list)
            features = [
                {
                    "type": "Feature",
                    "properties": {"hybas_id": int(row[0])},
                    "geometry": json.loads(row[1]),
                }
                for row in cur.fetchall()
            ]
        return {"type": "FeatureCollection", "features": features}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/basin/buffer", include_in_schema=False)
def basin_buffer_geom(lat: float, lon: float, radius_km: float = 100.0, level: int = 6):
    """Basin geometries intersecting a geodesic buffer — no signature computation."""
    basin_table = "basin06" if level == 6 else "basin08"
    try:
        conn = db_connect()
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT hybas_id, ST_AsGeoJSON(geom, 5)
                FROM public.{basin_table}
                WHERE ST_Intersects(
                    geom,
                    ST_Buffer(
                        ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography,
                        %s
                    )::geometry
                )
                """,
                (lon, lat, radius_km * 1000),
            )
            features = [
                {
                    "type": "Feature",
                    "properties": {"hybas_id": int(row[0])},
                    "geometry": json.loads(row[1]),
                }
                for row in cur.fetchall()
            ]
        return {"type": "FeatureCollection", "features": features}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/basin/ring", include_in_schema=False)
def basin_ring_geom(lat: float, lon: float, level: int = 6):
    """Fast ring topology: center + ring-member geometry and neighbor coords.

    Returns center and ring as GeoJSON features — no signature computation.
    neighbor_lat/lon on each ring member is ST_PointOnSurface, safe to pass
    directly to type=single_basin for per-member signature fetches.
    """
    basin_table = "basin06" if level == 6 else "basin08"
    try:
        conn = db_connect()
        center_df, ring_gdf = resolve_basin_ring(lat, lon, level, conn)
        center_id = int(center_df["hybas_id"].iloc[0])

        with conn.cursor() as cur:
            cur.execute(
                f"SELECT ST_AsGeoJSON(geom, 5) FROM public.{basin_table} WHERE hybas_id = %s",
                (center_id,),
            )
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail=f"Basin {center_id} not found")
            center_geom = json.loads(row[0])

        center_feature = {
            "type": "Feature",
            "properties": {"hybas_id": center_id},
            "geometry": center_geom,
        }

        ring_members = [
            {
                "hybas_id": int(r["hybas_id"]),
                "neighbor_lat": float(r["neighbor_lat"]),
                "neighbor_lon": float(r["neighbor_lon"]),
                "border_bearing": float(r["border_bearing"]),
                "centroid_bearing": float(r["centroid_bearing"]),
                "feature": {
                    "type": "Feature",
                    "properties": {"hybas_id": int(r["hybas_id"])},
                    "geometry": r.geometry.__geo_interface__,
                },
            }
            for _, r in ring_gdf.iterrows()
        ]

        return {"center": center_feature, "ring": ring_members}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# D-PLACE Societies (societies, societies/env-scan) moved to
# routes_workbench.py (2026-08-16, routes split).


# -----------------------
# Explorer: codebook metadata
# -----------------------
# _load_variables()/_CODEBOOK_FIELDS/_variable_cache moved to routes_common.py
# (2026-08-16, routes split) — shared with /explorer/values there.

# _CAT_LOOKUP, /explorer/variables, /explorer/lisa, /explorer/categorical,
# /explorer/evolv2k, /explorer/regions, /explorer/scatter all moved to
# routes_explorer.py (2026-08-16, routes split).


# -----------------------
# Explorer — HYDE epoch max
# -----------------------

_LMR_SAFE_VARS  = {"air", "prate"}

# _HYDE_EPOCH_RANGES/_HYDE_SAFE_VARS/_load_hyde_epoch_maxes moved to routes_common.py
# (2026-08-16, routes split) — shared with Cliopatria's /explorer/hyde-epoch-max.
# /explorer/hyde-epoch-max itself moved to routes_cliopatria.py, its only caller.


@router.get("/hyde/values", include_in_schema=False)
def hyde_values(var: str, year: int, level: int = 6):
    """Return flat {hybas_id: fraction} dict for one HYDE variable at a given CE year.

    Year is floor-snapped to the nearest available step in temporal.hyde_times.
    level=6: temporal.hyde_basin06_steps (~0.033s, 16k basins, WO18).
    level=8: temporal.hyde_basin08_steps (~0.38s, 190k basins, WO22).
    Basins with no land coverage are omitted (transparent in choropleth).
    Fractions clamped to 1.0 (sub_area/covered_km2 mismatch on a small number of basins).
    Response: {var, year, actual_year, values: {hybas_id: fraction}}
    """
    if var not in _HYDE_SAFE_VARS:
        raise HTTPException(status_code=400, detail=f"var must be one of {_HYDE_SAFE_VARS}")
    if level not in (6, 8):
        raise HTTPException(status_code=400, detail="level must be 6 or 8")

    steps_table = f"temporal.hyde_basin0{level}_steps"

    conn = db_connect()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT step_idx, year_ce
                FROM temporal.hyde_times
                WHERE year_ce <= %(year)s
                ORDER BY year_ce DESC
                LIMIT 1
                """,
                {"year": year},
            )
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=400, detail=f"No HYDE data at or before year {year}")
            step_idx, actual_year = int(row[0]), int(row[1])

            # var validated against _HYDE_SAFE_VARS; column name is server-controlled
            col = f"{var}_frac"
            cur.execute(
                f"SELECT hybas_id, {col} FROM {steps_table} WHERE step_idx = %(s)s",
                {"s": step_idx},
            )
            rows = cur.fetchall()
    finally:
        conn.close()

    values = {
        str(int(r[0])): min(round(float(r[1]), 6), 1.0) if r[1] is not None else None
        for r in rows
    }
    return {"var": var, "year": year, "actual_year": actual_year, "values": values}


@router.get("/lmr/values", include_in_schema=False)
def lmr_values(var: str, from_year: int, to_year: int):
    """Return flat {"lat,lon": mean_anomaly} dict for one LMR variable over a CE span.

    Anomalies are vs the CCSM4 model climatology 850–1850 CE (Tardif et al. 2019).
    Quality floor at 700 CE: actual_from = max(from_year, 700).
    Spans entirely below 700 CE return an empty values dict.
    Straddling spans use [700, to_year]; actual_from reflects the effective start.
    Response: {var, from_year, to_year, actual_from, values: {"lat,lon": mean_anomaly}}
    """
    if var not in _LMR_SAFE_VARS:
        raise HTTPException(status_code=400, detail=f"var must be one of {_LMR_SAFE_VARS}")

    actual_from = max(from_year, 700)
    if actual_from > to_year:
        return {"var": var, "from_year": from_year, "to_year": to_year,
                "actual_from": actual_from, "values": {}}

    conn = db_connect()
    try:
        with conn.cursor() as cur:
            # var validated against _LMR_SAFE_VARS; column name is server-controlled
            cur.execute(
                f"""
                SELECT CONCAT(lat, ',', CASE WHEN lon > 180 THEN lon - 360 ELSE lon END),
                       (SELECT AVG(v) FROM unnest({var}[%(y1)s:%(y2)s]) AS v) AS mean_val
                FROM temporal.lmr_climate
                """,
                {"y1": actual_from, "y2": to_year},
            )
            rows = cur.fetchall()
    finally:
        conn.close()

    values = {r[0]: round(float(r[1]), 6) if r[1] is not None else None for r in rows}
    return {"var": var, "from_year": from_year, "to_year": to_year,
            "actual_from": actual_from, "values": values}


# -----------------------
# /polity/search, /polity/slices, /polity/geom moved to routes_common.py;
# /polity/period, /polity/period/years, /polity/seshat moved to routes_cliopatria.py
# (2026-08-16, routes split).
# -----------------------


# -----------------------
# /area endpoint — areal signature for a named polity
# -----------------------

@router.get("/area")
def area(
    polity: str,
    year: int,
    level: int = 6,
    bands: str = "ABCDET",
    from_year: Optional[int] = None,
    to_year: Optional[int] = None,
    detail: bool = False,
):
    """Return an areal environmental signature for a named Cliopatria polity.

    Parameters
    ----------
    polity     : Cliopatria polity name (exact match, e.g. "Northern Song")
    year       : resolver year — selects the polity boundary active at this year CE
    level      : basin hierarchy level — 6 or 8 (default 6)
    bands      : which bands to compute (default ABCDET)
    from_year  : Band T span start (CE); required only when T is in bands
    to_year    : Band T span end (CE); required only when T is in bands
    detail     : if true, include per-variable histogram objects in the response

    Response
    --------
    Same profile_groups envelope as GET /api/signature, but each value is a distribution across
    the polity's member basins, not an average (see engine.py). Adds:
      "resolver": {"type": "polity", "polity", "polity_id", "fromyear", "toyear", "year"}
      "member_ids": [hybas_id, ...]
      "band_t_span": {"from_year", "to_year"}   -- present only when Band T requested
    detail=true adds a per-variable "distribution" histogram object.

    Full variable inventory: see the Codebook (/docs/codebook/).
    """
    if level not in (6, 8):
        raise HTTPException(status_code=400, detail=f"Level {level} not supported; use 6 or 8")

    requested = set(bands.upper().replace(",", "").replace(" ", ""))

    try:
        conn = db_connect()

        # Lightweight polity lookup — no basin resolution yet
        sql_lookup = """
            SELECT id, name, fromyear, toyear, ST_AsText(geom) AS geom_wkt
            FROM gaz.clio_polities
            WHERE NOT is_component AND name = %s AND fromyear <= %s AND toyear >= %s
        """
        rows = conn.execute(sql_lookup, (polity, year, year)).fetchall()

        if not rows:
            # Check whether the name exists at any other period (nice-to-have 404 detail)
            alt_rows = conn.execute(
                "SELECT fromyear, toyear FROM gaz.clio_polities "
                "WHERE NOT is_component AND name = %s ORDER BY fromyear",
                (polity,),
            ).fetchall()
            if alt_rows:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "message": f"Polity '{polity}' not active at year {year}",
                        "available_periods": [
                            {"fromyear": r[0], "toyear": r[1]} for r in alt_rows
                        ],
                    },
                )
            raise HTTPException(status_code=404, detail=f"Polity '{polity}' not found")

        # Multiple matches: pick narrowest temporal span (mirrors resolve_polity)
        if len(rows) > 1:
            rows = sorted(rows, key=lambda r: r[3] - r[2])
        polity_id, polity_name, fromyear, toyear, geom_wkt = (
            rows[0][0], rows[0][1], rows[0][2], rows[0][3], rows[0][4]
        )

        band_t_from = from_year if "T" in requested else None
        band_t_to   = to_year   if "T" in requested else None

        payload = areal_signature_polygon(
            geom_wkt,
            conn,
            level=level,
            bands=sorted(requested),
            from_year=band_t_from,
            to_year=band_t_to,
            include_detail=detail,
            resolver_year=year,
            polity_id=polity_id,
        )

        member_rows = conn.execute(
            "SELECT hybas_id FROM temporal.polity_basin08_crosswalk "
            "WHERE polity_id = %s ORDER BY weight DESC",
            (polity_id,),
        ).fetchall()
        payload["member_ids"] = [int(r[0]) for r in member_rows]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if "conn" in locals():
            conn.close()

    payload["resolver"] = {
        "type":      "polity",
        "polity":    polity_name,
        "polity_id": int(polity_id),
        "fromyear":  int(fromyear),
        "toyear":    int(toyear),
        "year":      year,
    }
    if "T" in requested and band_t_from is not None:
        payload["band_t_span"] = {"from_year": band_t_from, "to_year": band_t_to}

    return payload


# -----------------------
# /areas endpoint — type-dispatched areal signature
# -----------------------

@router.get("/areas")
def areas(
    type: str,
    lat: Optional[float] = Query(None, ge=-90, le=90),
    lon: Optional[float] = Query(None, ge=-180, le=180),
    radius_km: Optional[float] = None,
    polity: Optional[str] = None,
    year: Optional[int] = None,
    level: int = 6,
    bands: str = "ABCDE",
    from_year: Optional[int] = None,
    to_year: Optional[int] = None,
    detail: bool = False,
):
    """Areal signature dispatcher — resolves to a set of member basins by type, then
    aggregates their signature as a distribution (not an average). 'type' is confusingly
    named "area" alongside GET /api/area, but the four resolver types are not all areas
    in the geometric sense: single_basin and polity are bounded regions, buffer is an
    arbitrary radius, and basin_ring is a topological set of basins, not a shape.

    Parameters
    ----------
    type       : resolver type — 'buffer', 'single_basin', 'polity', 'basin_ring'
    lat, lon   : WGS-84 query point, decimal degrees -- lat in [-90, 90], lon in [-180, 180]
                 (required for buffer, single_basin, basin_ring)
    radius_km  : buffer radius in km (required for buffer)
    polity     : Cliopatria polity name (required for polity)
    year       : resolver year — boundary slice CE (required for polity)
    level      : basin hierarchy level — 6 or 8 (default 6)
    bands      : band letters to compute (default ABCDE; add T for temporal)
    from_year  : Band T span start CE (required when T in bands)
    to_year    : Band T span end CE (required when T in bands)
    detail     : include per-variable histogram objects in the response

    Response
    --------
    Same areal-signature envelope as GET /api/area (profile_groups as distributions across member
    basins, not averages), plus a "resolver" block whose shape depends on `type`. detail=true adds
    per-variable histogram objects. Full variable inventory: see the Codebook (/docs/codebook/).
    """
    if level not in (6, 8):
        raise HTTPException(status_code=400, detail=f"Level {level} not supported; use 6 or 8")

    requested = set(bands.upper().replace(",", "").replace(" ", ""))

    # Pass 1 — type-params
    if type == "buffer":
        missing = [p for p, v in [("lat", lat), ("lon", lon), ("radius_km", radius_km)] if v is None]
        if missing:
            raise HTTPException(
                status_code=422,
                detail=f"type=buffer requires: {', '.join(missing)}",
            )
    elif type == "single_basin":
        missing = [p for p, v in [("lat", lat), ("lon", lon)] if v is None]
        if missing:
            raise HTTPException(
                status_code=422,
                detail=f"type=single_basin requires: {', '.join(missing)}",
            )
    elif type == "polity":
        missing = [p for p, v in [("polity", polity), ("year", year)] if v is None]
        if missing:
            raise HTTPException(
                status_code=422,
                detail=f"type=polity requires: {', '.join(missing)}",
            )
    elif type == "basin_ring":
        missing = [p for p, v in [("lat", lat), ("lon", lon)] if v is None]
        if missing:
            raise HTTPException(
                status_code=422,
                detail=f"type=basin_ring requires: {', '.join(missing)}",
            )
    else:
        raise HTTPException(
            status_code=422,
            detail=f"Unsupported type '{type}'. Supported: buffer, single_basin, polity, basin_ring",
        )

    # Pass 2 — Band T span (cross-cutting)
    if "T" in requested:
        if from_year is None or to_year is None:
            raise HTTPException(
                status_code=422,
                detail="Band T requires a timespan (from_year, to_year)",
            )

    band_t_from = from_year if "T" in requested else None
    band_t_to   = to_year   if "T" in requested else None

    try:
        conn = db_connect()

        if type == "buffer":
            payload = areal_signature(
                lat, lon, radius_km,
                conn,
                level=level,
                bands=sorted(requested),
                from_year=band_t_from,
                to_year=band_t_to,
                include_detail=detail,
            )

        elif type == "single_basin":
            payload = single_basin_signature(
                lat, lon,
                conn,
                level=level,
                bands=sorted(requested),
                from_year=band_t_from,
                to_year=band_t_to,
                include_detail=detail,
            )

        elif type == "basin_ring":
            payload = basin_ring_signature(
                lat, lon,
                conn,
                level=level,
                bands=sorted(requested),
                from_year=band_t_from,
                to_year=band_t_to,
                include_detail=detail,
            )

        else:  # polity
            sql_lookup = """
                SELECT id, name, fromyear, toyear, ST_AsText(geom) AS geom_wkt
                FROM gaz.clio_polities
                WHERE NOT is_component AND name = %s AND fromyear <= %s AND toyear >= %s
            """
            rows = conn.execute(sql_lookup, (polity, year, year)).fetchall()

            if not rows:
                alt_rows = conn.execute(
                    "SELECT fromyear, toyear FROM gaz.clio_polities "
                    "WHERE NOT is_component AND name = %s ORDER BY fromyear",
                    (polity,),
                ).fetchall()
                if alt_rows:
                    raise HTTPException(
                        status_code=404,
                        detail={
                            "message": f"Polity '{polity}' not active at year {year}",
                            "available_periods": [
                                {"fromyear": r[0], "toyear": r[1]} for r in alt_rows
                            ],
                        },
                    )
                raise HTTPException(status_code=404, detail=f"Polity '{polity}' not found")

            if len(rows) > 1:
                rows = sorted(rows, key=lambda r: r[3] - r[2])
            polity_id, polity_name, fromyear, toyear, geom_wkt = (
                rows[0][0], rows[0][1], rows[0][2], rows[0][3], rows[0][4]
            )

            payload = areal_signature_polygon(
                geom_wkt,
                conn,
                level=level,
                bands=sorted(requested),
                from_year=band_t_from,
                to_year=band_t_to,
                include_detail=detail,
                resolver_year=year,
                polity_id=polity_id,
            )

            member_rows = conn.execute(
                "SELECT hybas_id FROM temporal.polity_basin08_crosswalk "
                "WHERE polity_id = %s ORDER BY weight DESC",
                (polity_id,),
            ).fetchall()
            payload["member_ids"] = [int(r[0]) for r in member_rows]

            payload["resolver"] = {
                "type":      "polity",
                "polity":    polity_name,
                "polity_id": int(polity_id),
                "fromyear":  int(fromyear),
                "toyear":    int(toyear),
                "year":      year,
            }
            if "T" in requested and band_t_from is not None:
                payload["band_t_span"] = {"from_year": band_t_from, "to_year": band_t_to}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if "conn" in locals():
            conn.close()

    return payload