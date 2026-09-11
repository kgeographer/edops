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
import urllib.error
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
from app.api.routes_common import _HYDE_SAFE_VARS, _whg_suggest, _whg_entity, _whg_reconcile, _extract_lonlat

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
    """Return {hybas_id: (place_id, place_name, ccodes, lat, lon)} for a list of ids.

    Place-name labels are decorative — callers must tolerate an empty map. Returns {}
    if gaz.whg_gaz is absent (not deployed everywhere) rather than failing the request.
    """
    try:
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
    except Exception:
        conn.rollback()
        return {}


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


@router.get("/sandbox/cities", include_in_schema=False)
def sandbox_cities():
    """Modern reference cities (GeoNames, population >= 15,000) for the Polities map's
    Cities layer -- flat array payload (mirrors /api/explorer/values), not GeoJSON, since
    the client fetches this once and does its own point-in-polygon filtering per polity."""
    conn = db_connect()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT gnid, name, ccode, population, lon, lat FROM gaz.geonames_cities")
            return {"cities": cur.fetchall()}
    finally:
        conn.close()


@router.get("/sandbox/countries", include_in_schema=False)
def sandbox_countries():
    """Country outlines (Natural Earth admin0) for the Polities map's Countries layer --
    only 242 features, fine as a single GeoJSON FeatureCollection fetched once."""
    conn = db_connect()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT name, ST_AsGeoJSON(geom, 4) FROM gaz.admin0")
            features = [
                {"type": "Feature", "properties": {"name": name}, "geometry": json.loads(geom)}
                for name, geom in cur.fetchall()
            ]
            return {"type": "FeatureCollection", "features": features}
    finally:
        conn.close()


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


# WHG returns several AAT place types per entity; "World Heritage Sites" is often
# first and reads oddly as the primary label. Prefer a settlement-ish one.
_PLACE_TYPE_PREF = ("cities", "towns", "villages", "inhabited places",
                    "capitals (seats of government)", "archaeological sites",
                    "deserted settlements", "ancient sites")


def _whg_place_type(place_types: List[Dict]) -> Optional[str]:
    labels = [p.get("label") for p in (place_types or []) if p.get("label")]
    for pref in _PLACE_TYPE_PREF:
        if pref in labels:
            return pref
    return labels[0] if labels else None


def _ring(w: float, s: float, e: float, n: float) -> Dict:
    """A GeoJSON Polygon ring from a bbox, for a WHG /reconcile `bounds` filter."""
    return {"type": "Polygon", "coordinates": [[[w, s], [e, s], [e, n], [w, n], [w, s]]]}


def _bbox_polygon(bbox: str) -> Dict:
    """'w,s,e,n' string -> a GeoJSON Polygon ring."""
    parts = [p.strip() for p in (bbox or "").split(",")]
    if len(parts) != 4:
        raise HTTPException(
            status_code=400,
            detail="Zoom the map to your study region first — a bounding box is "
                   "required when no country is given.",
        )
    try:
        w, s, e, n = (float(x) for x in parts)
    except ValueError:
        raise HTTPException(status_code=400, detail="bbox must be four numbers: w,s,e,n")
    if not (-180 <= w < e <= 180 and -90 <= s < n <= 90):
        raise HTTPException(status_code=400, detail="bbox out of range or degenerate")
    return _ring(w, s, e, n)


# Common-name -> ISO alpha-2 for hints Natural Earth's own columns don't carry.
_COUNTRY_ALIASES = {
    "uk": "GB", "uae": "AE", "drc": "CD", "roc": "CG", "holland": "NL",
    "burma": "MM", "czechia": "CZ", "ivory coast": "CI", "east timor": "TL",
    "south korea": "KR", "north korea": "KP", "cape verde": "CV",
}


def _resolve_place_hint(hint: str) -> Optional[Dict]:
    """Resolve the free text after the comma in a Sandbox place query.

    Tiered, most-specific first:
      Tier 1 -- country: {"kind": "country", "ccode": "US"}  (ISO a2/a3, postal,
               alias map, exact name, then a >=4-char starts-with on the name)
      Tier 2 -- admin1:  {"kind": "admin1", "ccode": "US", "bbox": (w,s,e,n),
               "label": "Pennsylvania"}  (postal like "PA", iso_3166_2, or an
               exact name in gaz.admin1)
      else -> None; the caller falls back to the map viewport bbox.

    2-letter tokens that are both a country code and a US state postal (CA, GA,
    IN, LA, MO, MS, ...) currently resolve as the country (Tier 3, deferred).
    """
    h = (hint or "").strip().lower()
    if not h:
        return None
    tok = h.replace(".", "").replace(" ", "")   # "u.s.a." -> "usa"

    if h in _COUNTRY_ALIASES or tok in _COUNTRY_ALIASES:
        return {"kind": "country", "ccode": _COUNTRY_ALIASES.get(h) or _COUNTRY_ALIASES[tok]}

    try:
        conn = db_connect()
        try:
            with conn.cursor() as cur:
                # A 2-letter token that's a US state postal ("PA", "GA", "ME", ...)
                # wins over the same-letter ISO country code (Panama, Gabon,
                # Montenegro). The general country-vs-state collision (Tier 3) is
                # still deferred.
                if len(tok) == 2 and tok.isalpha():
                    cur.execute(
                        """
                        SELECT name, ST_XMin(geom), ST_YMin(geom),
                               ST_XMax(geom), ST_YMax(geom)
                        FROM gaz.admin1
                        WHERE iso_a2 = 'US' AND lower(postal) = %(tok)s
                              AND geom IS NOT NULL
                        LIMIT 1
                        """,
                        {"tok": tok},
                    )
                    row = cur.fetchone()
                    if row and all(v is not None for v in row[1:5]):
                        return {
                            "kind": "admin1", "ccode": "US", "label": row[0],
                            "bbox": (float(row[1]), float(row[2]),
                                     float(row[3]), float(row[4])),
                        }

                cur.execute(
                    """
                    SELECT iso_a2 FROM (
                      SELECT iso_a2, 1 AS pri FROM gaz.admin0
                        WHERE lower(iso_a2)=%(tok)s OR lower(iso_a3)=%(tok)s OR lower(postal)=%(tok)s
                      UNION ALL
                      SELECT iso_a2, 2 FROM gaz.admin0
                        WHERE lower(name)=%(h)s OR lower(name_long)=%(h)s
                              OR lower(formal_en)=%(h)s OR lower(brk_name)=%(h)s
                              OR replace(lower(abbrev),'.','')=%(tok)s
                      UNION ALL
                      SELECT iso_a2, 3 FROM gaz.admin0
                        WHERE length(%(h)s) >= 4 AND lower(name) LIKE %(h)s || '%%'
                    ) m
                    WHERE iso_a2 IS NOT NULL AND iso_a2 <> '-99'
                    ORDER BY pri LIMIT 1
                    """,
                    {"tok": tok, "h": h},
                )
                row = cur.fetchone()
                if row:
                    return {"kind": "country", "ccode": row[0]}

                cur.execute(
                    """
                    SELECT iso_a2, name,
                           ST_XMin(geom), ST_YMin(geom), ST_XMax(geom), ST_YMax(geom)
                    FROM gaz.admin1
                    WHERE iso_a2 IS NOT NULL AND iso_a2 <> '-99' AND geom IS NOT NULL
                      AND ( lower(postal) = %(tok)s
                            OR replace(lower(abbrev), '.', '') = %(tok)s
                            OR lower(iso_3166_2) = %(h)s
                            OR lower(iso_3166_2) LIKE '%%-' || %(tok)s
                            OR lower(name) = %(h)s OR lower(name_alt) = %(h)s
                            OR lower(name_local) = %(h)s OR lower(woe_name) = %(h)s )
                    -- 2-letter postals collide across countries (PA = Pennsylvania /
                    -- Pará / Papua); bias to the US, then to an exact name match.
                    ORDER BY (iso_a2 = 'US') DESC,
                             (lower(name) = %(h)s) DESC,
                             (lower(postal) = %(tok)s
                              OR replace(lower(abbrev), '.', '') = %(tok)s) DESC,
                             ST_Area(geom) DESC
                    LIMIT 1
                    """,
                    {"tok": tok, "h": h},
                )
                row = cur.fetchone()
                if row and all(v is not None for v in row[2:6]):
                    return {
                        "kind": "admin1", "ccode": row[0], "label": row[1],
                        "bbox": (float(row[2]), float(row[3]), float(row[4]), float(row[5])),
                    }
        finally:
            conn.close()
    except Exception:
        return None  # never block the search on a hint-resolution failure
    return None


def _reconcile_hits(data: Dict, keys) -> List[Dict]:
    """Flatten reconcile sub-query results in `keys` order, deduped by id."""
    out, seen = [], set()
    for k in keys:
        for r in (data.get(k, {}).get("result") or []):
            rid = r.get("id")
            if rid and rid in seen:
                continue
            if rid:
                seen.add(rid)
            out.append(r)
    return out


@router.get("/whg/suggest", include_in_schema=False)
def whg_suggest_places(q: str, limit: int = 8, country: str = "", bbox: str = ""):
    """Settlement/site lookup via WHG /reconcile (2026-09-09; replaced /suggest/entity).

    The text after the comma ("Venice, Italy", "Pittsburgh, PA", "Pittsburgh, US")
    goes through `_resolve_place_hint`, which yields one of:

    - **country** — `countries=[code]` + `fclasses=P,S`, `mode=exact` with a
      `mode=fuzzy` fallback only if exact is empty. No bbox, no zoom.
    - **admin1** (state/province) — `countries=[code]` + `bounds=<admin1 bbox>`
      (they compose; `fclasses` does not compose with `bounds`), exact ∪ fuzzy.
      Pins e.g. "Pittsburgh, PA" to Pennsylvania.
    - **nothing** — the request `bbox` (map viewport) is used as the `bounds`
      polygon; WHG enforces it server-side so results never fall outside. `bbox`
      is required in this case (400 otherwise). exact ∪ fuzzy.
    """
    q = (q or "").strip()
    if not q or len(q) < 2:
        return {"results": []}
    limit = max(1, min(limit, 20))

    hint = (country or "").strip()
    resolved = _resolve_place_hint(hint) if hint else None

    # whg + gn are the namespaces that carry GeoNames feature classes and the bulk
    # of the records (~15M); restricting to them drops OSM/Wikidata/TGN/Pleiades
    # cross-gazetteer noise. NB: `fclasses` still cannot compose with `bounds` at
    # WHG (probed 2026-09-09), so the bbox paths can't actually filter to P/S and
    # may surface admin areas / physical features. See the WHG issue.
    NS = ["whg", "gn"]

    if resolved and resolved["kind"] == "country":
        base = {"query": q, "countries": [resolved["ccode"]],
                "fclasses": ["P", "S"], "namespaces": NS, "limit": max(limit, 10)}
        exact_wins = True
    elif resolved and resolved["kind"] == "admin1":
        base = {"query": q, "countries": [resolved["ccode"]],
                "bounds": _ring(*resolved["bbox"]), "namespaces": NS, "limit": max(limit, 15)}
        exact_wins = False   # union exact+fuzzy; the state bbox already scopes it
    else:
        base = {"query": q, "bounds": _bbox_polygon(bbox),
                "namespaces": NS, "limit": max(limit, 15)}
        exact_wins = False

    batch = {"exact": {**base, "mode": "exact"}, "fuzzy": {**base, "mode": "fuzzy"}}

    try:
        data = _whg_reconcile(batch)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"WHG reconcile failed: {e}")

    if exact_wins and (data.get("exact", {}).get("result") or []):
        raw = _reconcile_hits(data, ("exact",))
    else:
        raw = _reconcile_hits(data, ("exact", "fuzzy"))

    results = []
    for r in raw:
        pt = r.get("repr_point")
        if not pt or len(pt) < 2:
            continue
        try:
            lon, lat = float(pt[0]), float(pt[1])
        except (TypeError, ValueError):
            continue
        ccs = r.get("ccodes") or []
        results.append({
            "id": r.get("id"),
            "name": r.get("name"),
            "lon": lon,
            "lat": lat,
            "ccodes": ccs,
            "alt_names": (r.get("alt_names") or [])[:10],
            "cname": _CCODES.get(ccs[0], "") if ccs else "",
            "score": r.get("score"),
            "place_type": _whg_place_type(r.get("place_types")),
        })
        if len(results) >= limit:
            break

    return {"results": results}


_ID_NS_PATTERN = re.compile(r"^(whg|wd|pl|gn|tgn):(\S+)$", re.IGNORECASE)


@router.get("/whg/entity", include_in_schema=False)
def whg_entity_lookup(id: str = Query(..., description="Namespaced gazetteer identifier, e.g. wd:Q220")):
    """Resolve a pasted gazetteer identifier to a point via WHG's Entity API.

    Backs the Settlements resolve field's identifier-paste path (2026-09-11).
    Accepted namespaces: whg, wd (Wikidata), pl (Pleiades), gn (GeoNames),
    tgn (Getty TGN) -- matches the resolve field's help tooltip exactly.
    Response shape matches the WHG-candidate path ({lat, lon, name, ...}) so
    the frontend can feed it straight into setResolvedPoint().
    """
    raw = (id or "").strip()
    m = _ID_NS_PATTERN.match(raw)
    if not m:
        raise HTTPException(
            status_code=400,
            detail="Expected a namespaced identifier like wd:Q220 (whg, wd, pl, gn, or tgn).",
        )
    ns, ident = m.group(1).lower(), m.group(2)

    # WHG's own native namespace has no "whg:" segment in its entity id -- e.g.
    # "place:5424806", not "place:whg:5424806" (see _whg_entity docstring).
    whg_place_id = f"place:{ident}" if ns == "whg" else f"place:{ns}:{ident}"

    try:
        entity = _whg_entity(whg_place_id)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise HTTPException(status_code=404, detail=f"No WHG record found for '{raw}'.")
        raise HTTPException(status_code=502, detail=f"WHG entity lookup failed: {e}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"WHG entity lookup failed: {e}")

    lonlat = _extract_lonlat(entity)
    if not lonlat:
        raise HTTPException(status_code=404, detail=f"No resolvable location for '{raw}'.")
    lon, lat = lonlat

    # names has been seen both under properties.names (wd-sourced records) and
    # top-level names (pl-sourced records) in probing -- check both rather than
    # assume one. types is top-level in every record seen (matches the existing
    # _whg_search_candidates convention above).
    props = entity.get("properties") or {}
    names = props.get("names") or entity.get("names") or []
    name = next(
        (n.get("toponym") for n in names
         if isinstance(n, dict) and str(n.get("lang", "")).lower() == "en" and n.get("toponym")),
        None,
    )
    if not name and names and isinstance(names[0], dict):
        name = names[0].get("toponym")
    name = name or raw

    types = [{"label": t.get("label", "")} for t in (entity.get("types") or []) if isinstance(t, dict)]

    return {
        "id": whg_place_id,
        "source_id": raw,
        "name": name,
        "lat": lat,
        "lon": lon,
        "types": types,
    }


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
    directly to scope=single_basin for per-member signature fetches.
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
# LMR's stored `air`/`prate` fields carry their native (modern) reference, so a raw
# span mean reads as uniformly cold for any pre-industrial period. Re-baseline each
# grid cell to its own last-millennium (850-1850 CE) mean so the map shows genuine
# within-millennium anomalies. Matches the legend's "0 = 850-1850 mean".
_LMR_BASELINE = (850, 1850)

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

    Each cell's span mean is re-baselined to that cell's own 850–1850 CE mean
    (_LMR_BASELINE), so values are anomalies vs the last-millennium normal — not
    vs LMR's native modern reference (which skews every historical map cold).
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
                         (SELECT AVG(v) FROM unnest({var}[%(y1)s:%(y2)s]) AS v)
                       - (SELECT AVG(v) FROM unnest({var}[%(b1)s:%(b2)s]) AS v) AS mean_val
                FROM temporal.lmr_climate
                """,
                {"y1": actual_from, "y2": to_year,
                 "b1": _LMR_BASELINE[0], "b2": _LMR_BASELINE[1]},
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

@router.get("/area", summary="Areal signature for a named historical polity")
def area(
    polity: str = Query(..., description='Cliopatria polity name, exact match (e.g. "Northern Song").'),
    year: int = Query(..., description="Resolver year CE — selects the polity boundary active at this year."),
    level: int = Query(6, description="Basin hierarchy level: 6 or 8."),
    bands: str = Query("ABCDET", description=(
        "Band letters to compute, e.g. \"ABCDET\". Add T to include Band T (requires "
        "from_year and to_year)."
    )),
    from_year: Optional[int] = Query(None, description="Band T span start, year CE. Required when T is in bands."),
    to_year: Optional[int] = Query(None, description="Band T span end, year CE. Required when T is in bands."),
    detail: bool = Query(False, description="If true, include per-variable histogram objects in the response."),
):
    """Return an areal environmental signature for a named Cliopatria polity.

    Response
    --------
    Not the GET /api/signature shape. The areal envelope is a flat "rows" list — one
    object per variable, each carrying a representative score across the polity's member
    basins (a distribution summary, not an average — see engine.py) plus coherence /
    coverage / modality metadata. Alongside "rows":
      "bands":      ["A", ...]   -- echoes the requested bands
      "resolver":   {"type": "polity", "polity", "polity_id", "fromyear", "toyear", "year"}
      "scope":      {"type": "polity", "level", "n_units", "unit_type", ...}
      "member_ids": [hybas_id, ...]
      "caveats", "shortfall", "temporal", "modality_post_pass"
      "band_t_span": {"from_year", "to_year"}   -- present only when Band T requested
    detail=true adds a per-variable "distribution" histogram object to each row.

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
# /areas endpoint — scope-dispatched areal signature
# -----------------------

@router.get("/areas", summary="Areal signature by scope — buffer, single basin, polity, or basin ring")
def areas(
    scope: str = Query(..., description=(
        "Spatial scope of the query: 'buffer', 'single_basin', 'polity', or 'basin_ring'. "
        "Determines which of lat/lon/radius_km/polity/year are required (see each param's "
        "own description) and the shape of the `scope` block in the response."
    )),
    lat: Optional[float] = Query(None, ge=-90, le=90, description=(
        "WGS-84 latitude, decimal degrees. Required for scope=buffer, single_basin, basin_ring."
    )),
    lon: Optional[float] = Query(None, ge=-180, le=180, description=(
        "WGS-84 longitude, decimal degrees. Required for scope=buffer, single_basin, basin_ring."
    )),
    radius_km: Optional[float] = Query(None, description="Buffer radius in km. Required for scope=buffer."),
    polity: Optional[str] = Query(None, description=(
        "Cliopatria polity name, exact match (e.g. \"Northern Song\"). Required for scope=polity."
    )),
    year: Optional[int] = Query(None, description=(
        "Resolver year CE — selects the polity boundary active at this year. Required for scope=polity."
    )),
    level: int = Query(6, description="Basin hierarchy level: 6 or 8."),
    bands: str = Query("ABCDE", description=(
        "Band letters to compute, e.g. \"ABCDE\" or \"ABCDET\". Add T to include Band T "
        "(requires from_year and to_year)."
    )),
    from_year: Optional[int] = Query(None, description="Band T span start, year CE. Required when T is in bands."),
    to_year: Optional[int] = Query(None, description="Band T span end, year CE. Required when T is in bands."),
    detail: bool = Query(False, description="If true, include per-variable histogram objects in the response."),
):
    """Areal signature dispatcher — resolves to a set of member basins by scope, then
    aggregates their signature as a distribution (not an average). `scope` is confusingly
    named "area" alongside GET /api/area, but the four scope kinds are not all areas
    in the geometric sense: single_basin and polity are bounded regions, buffer is an
    arbitrary radius, and basin_ring is a topological set of basins, not a shape.

    Response
    --------
    Same areal envelope as GET /api/area (a flat "rows" list of per-variable representative
    scores across the resolved member basins — not the GET /api/signature profile_groups
    shape), with a `scope` block whose fields depend on `scope`. detail=true adds a
    per-variable "distribution" histogram object to each row. Full variable inventory: see
    the Codebook (/docs/codebook/).
    """
    if level not in (6, 8):
        raise HTTPException(status_code=400, detail=f"Level {level} not supported; use 6 or 8")

    requested = set(bands.upper().replace(",", "").replace(" ", ""))

    # Pass 1 — scope-params
    if scope == "buffer":
        missing = [p for p, v in [("lat", lat), ("lon", lon), ("radius_km", radius_km)] if v is None]
        if missing:
            raise HTTPException(
                status_code=422,
                detail=f"scope=buffer requires: {', '.join(missing)}",
            )
    elif scope == "single_basin":
        missing = [p for p, v in [("lat", lat), ("lon", lon)] if v is None]
        if missing:
            raise HTTPException(
                status_code=422,
                detail=f"scope=single_basin requires: {', '.join(missing)}",
            )
    elif scope == "polity":
        missing = [p for p, v in [("polity", polity), ("year", year)] if v is None]
        if missing:
            raise HTTPException(
                status_code=422,
                detail=f"scope=polity requires: {', '.join(missing)}",
            )
    elif scope == "basin_ring":
        missing = [p for p, v in [("lat", lat), ("lon", lon)] if v is None]
        if missing:
            raise HTTPException(
                status_code=422,
                detail=f"scope=basin_ring requires: {', '.join(missing)}",
            )
    else:
        raise HTTPException(
            status_code=422,
            detail=f"Unsupported scope '{scope}'. Supported: buffer, single_basin, polity, basin_ring",
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

        if scope == "buffer":
            payload = areal_signature(
                lat, lon, radius_km,
                conn,
                level=level,
                bands=sorted(requested),
                from_year=band_t_from,
                to_year=band_t_to,
                include_detail=detail,
            )

        elif scope == "single_basin":
            payload = single_basin_signature(
                lat, lon,
                conn,
                level=level,
                bands=sorted(requested),
                from_year=band_t_from,
                to_year=band_t_to,
                include_detail=detail,
            )

        elif scope == "basin_ring":
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