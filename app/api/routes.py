from fastapi import APIRouter, HTTPException
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
from app.db.seasonality import find_similar, get_lens_registry
from app.settings import settings
from scripts.edop.areas.engine import areal_signature, areal_signature_polygon, single_basin_signature, basin_ring_signature, resolve_basin_ring

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

def _http_get_json(url: str, timeout_sec: int = 20) -> Dict[str, Any]:
    ctx = ssl.create_default_context(cafile=certifi.where())
    req = urllib.request.Request(url, headers={
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://whgazetteer.org/",
    })
    with urllib.request.urlopen(req, timeout=timeout_sec, context=ctx) as resp:
        raw = resp.read().decode("utf-8")
    return json.loads(raw)


def _http_post_json(url: str, payload: Dict[str, Any], headers: Dict[str, str] = None, timeout_sec: int = 20) -> Dict[str, Any]:
    """POST JSON to URL and return parsed response."""
    ctx = ssl.create_default_context(cafile=certifi.where())
    data = json.dumps(payload).encode("utf-8")
    req_headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://whgazetteer.org/"
    }
    if headers:
        req_headers.update(headers)
    req = urllib.request.Request(url, data=data, headers=req_headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout_sec, context=ctx) as resp:
        raw = resp.read().decode("utf-8")
    return json.loads(raw)


def _whg_suggest_first(prefix: str) -> Optional[Dict[str, Any]]:
    """Call WHG suggest endpoint and return the top-ranked result, if any."""
    if not settings.WHG_API_TOKEN:
        raise HTTPException(status_code=500, detail="WHG_API_TOKEN not configured on server")

    params = {
        "prefix": prefix,
        "limit": 3,
        "cursor": 0,
        "exact": "false",
        "type": "place",
        "token": settings.WHG_API_TOKEN,
    }

    url = "https://whgazetteer.org/suggest/entity?" + urllib.parse.urlencode(params)
    data = _http_get_json(url)
    results = data.get("result") or []
    return results[0] if results else None


def _whg_suggest(prefix: str, limit: int = 5, fclasses: str = None, countries: str = None) -> List[Dict[str, Any]]:
    """Call WHG suggest endpoint and return up to `limit` results."""
    if not settings.WHG_API_TOKEN:
        raise HTTPException(status_code=500, detail="WHG_API_TOKEN not configured on server")

    params = {
        "prefix": prefix,
        "limit": limit,
        "cursor": 0,
        "type": "place",
        "token": settings.WHG_API_TOKEN,
    }
    if fclasses:
        params["fclasses"] = fclasses
    if countries:
        params["countries"] = countries

    url = "https://whgazetteer.org/suggest/entity?" + urllib.parse.urlencode(params)
    data = _http_get_json(url)
    return data.get("result") or []


def _whg_entity(place_id: str) -> Dict[str, Any]:
    """Fetch WHG entity detail for a place id (e.g. 'place:5424806')."""
    if not settings.WHG_API_TOKEN:
        raise HTTPException(status_code=500, detail="WHG_API_TOKEN not configured on server")

    encoded_id = urllib.parse.quote(place_id, safe="")
    token = urllib.parse.quote(settings.WHG_API_TOKEN)
    url = f"https://whgazetteer.org/entity/{encoded_id}/api?token={token}"
    return _http_get_json(url)


def _extract_lonlat(entity: Dict[str, Any]) -> Optional[Tuple[float, float]]:
    """Extract (lon, lat) from a WHG entity response."""
    # Current format: GeoJSON Feature with geometry.coordinates
    geom = entity.get("geometry") or {}
    if geom.get("type") == "Point":
        coords = geom.get("coordinates") or []
        if len(coords) >= 2:
            return float(coords[0]), float(coords[1])

    # Legacy format: geoms[0].geojson.coordinates
    geoms = entity.get("geoms") or []
    if geoms:
        g0 = geoms[0] or {}
        gj = g0.get("geojson")
        if isinstance(gj, dict):
            coords = gj.get("coordinates")
            if isinstance(coords, (list, tuple)) and len(coords) >= 2:
                return float(coords[0]), float(coords[1])
        coords = g0.get("coordinates")
        if isinstance(coords, (list, tuple)) and len(coords) >= 2:
            return float(coords[0]), float(coords[1])
        centroid = g0.get("centroid")
        if isinstance(centroid, (list, tuple)) and len(centroid) >= 2:
            return float(centroid[0]), float(centroid[1])

    return None


def _whg_reconcile_query(query: str, bounds: Dict = None, size: int = 10) -> Dict[str, Any]:
    """
    Call WHG /reconcile endpoint (no namespace = WHG-uploaded + tgn + pl, excludes wd/gn/osm).
    Returns candidates with id, name, score, match, alt_names, description.
    """
    if not settings.WHG_API_TOKEN:
        raise HTTPException(status_code=500, detail="WHG_API_TOKEN not configured on server")

    q_params = {
        "query": query,
        "limit": size
    }

    if bounds:
        q_params["bounds"] = bounds

    payload = {
        "queries": {
            "q1": q_params
        }
    }

    headers = {
        "Authorization": f"Bearer {settings.WHG_API_TOKEN}"
    }

    url = "https://whgazetteer.org/reconcile"
    data = _http_post_json(url, payload, headers=headers)

    # Extract results from q1
    q1_result = data.get("q1", {})
    return q1_result.get("result", [])


def _whg_reconcile_extend(place_ids: List[str]) -> Dict[str, Dict]:
    """
    Call WHG /reconcile extend to get geometry and details for place IDs.
    Returns dict keyed by place_id with geometry_wkt, countries, types, names.
    """
    if not settings.WHG_API_TOKEN:
        raise HTTPException(status_code=500, detail="WHG_API_TOKEN not configured on server")

    if not place_ids:
        return {}

    payload = {
        "extend": {
            "ids": place_ids,
            "properties": [
                {"id": "whg:geometry_centroid"}
            ]
        }
    }

    headers = {
        "Authorization": f"Bearer {settings.WHG_API_TOKEN}"
    }

    url = "https://whgazetteer.org/reconcile"
    data = _http_post_json(url, payload, headers=headers)

    return data.get("rows", {})


def _parse_centroid_string(s: str) -> Optional[Tuple[float, float]]:
    """Parse WHG geometry_centroid string 'lat, lon' to (lon, lat) tuple."""
    if not s:
        return None
    parts = s.split(",")
    if len(parts) == 2:
        try:
            lat = float(parts[0].strip())
            lon = float(parts[1].strip())
            return lon, lat
        except ValueError:
            pass
    return None


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


def _merge_reconcile_results(candidates: List[Dict], extended: Dict[str, Dict]) -> List[Dict]:
    """
    Merge reconcile query results with extend data.
    Returns list of places with all fields combined.
    """
    results = []

    for c in candidates:
        place_id = c.get("id")
        ext = extended.get(place_id, {})

        # Parse centroid — "lat, lon" string from WHG extend
        lon, lat = None, None
        centroid_list = ext.get("whg:geometry_centroid", [])
        if centroid_list and isinstance(centroid_list, list):
            coords = _parse_centroid_string(centroid_list[0].get("str", ""))
            if coords:
                lon, lat = coords

        # Country code from reconcile description field ("Country: XX")
        desc = c.get("description", "") or ""
        m = re.match(r"Country:\s*(\w+)", desc)
        country_code = m.group(1) if m else None

        result = {
            "id": place_id,
            "name": c.get("name"),
            "score": c.get("score"),
            "match": c.get("match", False),
            "alt_names": c.get("alt_names", []),
            "description": desc,
            "lon": lon,
            "lat": lat,
            "country": country_code,
        }
        results.append(result)

    return results


# -----------------------
# World Heritage seed helpers
# -----------------------

_WH_SEED_PATH = Path(__file__).resolve().parents[1] / "data" / "world_heritage_seed.json"


def _parse_wkt_point(wkt: str) -> Optional[Tuple[float, float]]:
    """Parse WKT like 'POINT (lon lat)' or 'POINT(lon lat)' into (lon, lat)."""
    if not wkt:
        return None
    m = re.match(r"^\s*POINT\s*\(\s*([-0-9.]+)\s+([-0-9.]+)\s*\)\s*$", wkt)
    if not m:
        return None
    return float(m.group(1)), float(m.group(2))


def _load_wh_seed() -> list[Dict[str, Any]]:
    """Load and normalize the WH seed JSON into a list of dicts with GeoJSON Point."""
    if not _WH_SEED_PATH.exists():
        raise FileNotFoundError(f"World Heritage seed file not found at {_WH_SEED_PATH}")

    raw = json.loads(_WH_SEED_PATH.read_text(encoding="utf-8"))
    out: list[Dict[str, Any]] = []

    if not isinstance(raw, list):
        raise ValueError("World Heritage seed file must be a JSON array")

    for row in raw:
        if not isinstance(row, dict):
            continue
        wkt = row.get("geom")
        lonlat = _parse_wkt_point(wkt) if isinstance(wkt, str) else None
        if not lonlat:
            continue
        lon, lat = lonlat
        out.append(
            {
                "id_no": row.get("id_no"),
                "name_en": row.get("name_en"),
                "states_name_en": row.get("states_name_en"),
                "short_description_en": row.get("short_description_en"),
                "location": {"type": "Point", "coordinates": [lon, lat]},
            }
        )

    return out


def _get_cluster_labels() -> Dict[int, str]:
    """Fetch cluster labels for WH sites from database."""
    try:
        conn = db_connect()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT s.id_no, c.cluster_label
                FROM edop_clusters c
                JOIN edop_wh_sites s ON s.site_id = c.site_id
            """)
            return {row[0]: row[1] for row in cur.fetchall()}
    except Exception:
        return {}
    finally:
        if 'conn' in locals():
            conn.close()


# -----------------------
# API endpoints
# -----------------------

@router.get("/health")
def health():
    return {"status": "ok"}


def _resolve_basin(conn, lat: float, lon: float) -> int:
    """Return the L06 hybas_id containing (lat, lon); raises 404 if none found."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT hybas_id FROM public.basin06 "
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


# DEPRECATED: use /api/similarity?lens=climate.phase — this wrapper exists only to keep
# WO7 callers running during transition. Do not add new callers; do not reuse as a pattern.
@router.get("/seasonality/similar")
def seasonality_similar(lat: float, lon: float, n: int = 20):
    """Deprecated backward-compat wrapper for the climate.phase lens.

    Use /api/similarity?lens=climate.phase for new callers.
    Returns the original flat shape (query_pre_concentration, query_seas_phase_offset,
    basin_rank) so existing callers are unaffected during transition.
    """
    n = min(max(1, n), 6000)
    conn = db_connect()
    try:
        query_hybas_id = _resolve_basin(conn, lat, lon)
        try:
            query_meta, ranked = find_similar(query_hybas_id, lens_id="climate.phase", n=n, mode="topn")
        except RuntimeError as e:
            raise HTTPException(status_code=503, detail=str(e))
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))

        if not ranked:
            return {
                "query_basin_id":          query_hybas_id,
                "query_pre_concentration": None,
                "query_seas_phase_offset": None,
                "metric":                  "normalized_euclidean_2idx",
                "results":                 [],
            }

        gaz_by_basin = _gaz_join(conn, [r["hybas_id"] for r in ranked])

        results = []
        for r in ranked:
            place = gaz_by_basin.get(r["hybas_id"])
            results.append({
                "basin_rank":        r["rank"],
                "basin_id":          r["hybas_id"],
                "distance":          r["distance"],
                "pre_concentration": r["values"]["pre_concentration"],
                "seas_phase_offset": r["values"]["seas_phase_offset"],
                "place_id":          place[1] if place else None,
                "place_name":        place[2] if place else None,
                "ccodes":            place[3] if place else None,
                "lat":               float(place[4]) if place else None,
                "lon":               float(place[5]) if place else None,
            })

        qv = query_meta["query_values"]
        return {
            "query_basin_id":          query_meta["query_hybas_id"],
            "query_pre_concentration": qv["pre_concentration"],
            "query_seas_phase_offset": qv["seas_phase_offset"],
            "metric":                  "normalized_euclidean_2idx",
            "results":                 results,
        }

    finally:
        conn.close()


@router.get("/similarity/lenses")
def similarity_lenses():
    """Return the full lens registry (active and disabled lenses)."""
    return {"lenses": get_lens_registry()}


@router.get("/similarity")
def similarity(
    lat: float,
    lon: float,
    lens: str = "climate.phase",
    mode: str = "threshold",
    stringency: str = "moderate",
    n: int = 200,
):
    """Return basins similar to (lat, lon) under the given similarity lens.

    Parameters
    ----------
    lat, lon    : query coordinates
    lens        : lens_id from the registry (e.g. 'climate.phase', 'climate.temp')
    mode        : 'threshold' (default) — all basins within the calibrated radius;
                  'topn' — the n nearest basins regardless of radius
    stringency  : 'strict' | 'moderate' (default) | 'loose' — used in threshold mode
    n           : top-N count used only when mode='topn' (default 200, max 2000)

    Response
    --------
    {
      "lens_id": str, "lens_label": str, "metric": str,
      "mode": str,
      "query_basin_id": int,
      "query_values": {var: value, ...},
      # threshold mode only:
      "stringency": str, "radius": float, "result_count": int,
      "results": [
        { "rank": int, "basin_id": int, "distance": float,
          "values": {var: value, ...},
          "place_id": int|null, "place_name": str|null,
          "ccodes": str|null, "lat": float|null, "lon": float|null },
        ...
      ]
    }
    """
    if mode not in ("threshold", "topn"):
        raise HTTPException(status_code=400, detail="mode must be 'threshold' or 'topn'")
    if mode == "threshold" and stringency not in ("strict", "moderate", "loose"):
        raise HTTPException(status_code=400, detail="stringency must be 'strict', 'moderate', or 'loose'")
    n = min(max(1, n), 2000)
    conn = db_connect()
    try:
        query_hybas_id = _resolve_basin(conn, lat, lon)
        try:
            query_meta, ranked = find_similar(
                query_hybas_id, lens_id=lens, n=n, mode=mode, stringency=stringency,
            )
        except RuntimeError as e:
            raise HTTPException(status_code=503, detail=str(e))
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))

        gaz_by_basin = _gaz_join(conn, [r["hybas_id"] for r in ranked]) if ranked else {}

        results = []
        for r in ranked:
            place = gaz_by_basin.get(r["hybas_id"])
            results.append({
                "rank":       r["rank"],
                "basin_id":   r["hybas_id"],
                "distance":   r["distance"],
                "values":     r["values"],
                "place_id":   place[1] if place else None,
                "place_name": place[2] if place else None,
                "ccodes":     place[3] if place else None,
                "lat":        float(place[4]) if place else None,
                "lon":        float(place[5]) if place else None,
            })

        resp = {
            "lens_id":        query_meta["lens_id"],
            "lens_label":     query_meta["lens_label"],
            "metric":         query_meta["metric"],
            "mode":           query_meta["mode"],
            "query_basin_id": query_meta["query_hybas_id"],
            "query_values":   query_meta["query_values"],
            "results":        results,
        }
        if query_meta["mode"] == "threshold":
            resp["stringency"]   = query_meta["stringency"]
            resp["radius"]       = query_meta["radius"]
            resp["result_count"] = query_meta["result_count"]
        return resp

    finally:
        conn.close()


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


@router.get("/basin-geom")
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


@router.post("/basin-geom")
def basin_geom_post(body: BasinGeomRequest):
    """Return GeoJSON geometry strings for a list of basin hybas_ids (POST, max 2000).

    Body: {"ids": [hybas_id, ...], "level": 6}
    Returns: {"<hybas_id>": "<GeoJSON geometry string>", ...}
    """
    if body.level not in (6, 8):
        raise HTTPException(status_code=400, detail="level must be 6 or 8")
    if not body.ids or len(body.ids) > 6000:
        raise HTTPException(status_code=400, detail="ids must contain 1–6000 hybas_id values")
    return _fetch_basin_geom(body.ids, body.level)


@router.get("/signature")
def signature(
    lat: float,
    lon: float,
    bands: str = "ABCDE",
    level: int = 8,
    from_year: Optional[int] = None,
    to_year: Optional[int] = None,
    flat: bool = False,
):
    """Return environmental signature for a coordinate.

    Parameters
    ----------
    lat, lon   : coordinates
    bands      : which profile groups to include, e.g. "ABCDE" or "ABCDET" (default ABCDE)
    level      : basin hierarchy level — only 8 and 6 are currently supported
    from_year  : start year CE for Band T temporal enrichment (0–1998)
    to_year    : end year CE for Band T temporal enrichment (0–1998)
    flat       : if true, return flat field values instead of nested profile_groups;
                 Band T temporal data appears at key "temporal" rather than in profile_groups
    """
    if level not in (6, 8):
        raise HTTPException(status_code=400, detail=f"Basin level {level} not available; supported levels: 6, 8")
    sig = get_signature(lat=lat, lon=lon, level=level, flat=flat)
    if sig is None:
        raise HTTPException(status_code=404, detail="No basin covers this point")

    # Filter profile_groups to requested bands
    requested = set(bands.upper().replace(",", "").replace(" ", ""))
    if sig.get("profile_groups"):
        sig["profile_groups"] = {k: v for k, v in sig["profile_groups"].items() if k in requested}

    # Band T: temporal enrichment — stored in profile_groups["T"]
    if "T" in requested:
        if from_year is None or to_year is None:
            band_t = {
                "_status": "not_requested",
                "_note": "Include from_year and to_year to retrieve Band T temporal data.",
            }
        else:
            temporal = get_temporal_context(lat=lat, lon=lon, year_start=from_year, year_end=to_year)
            if "error" in temporal:
                band_t = {"_status": "error", "_note": temporal["error"]}
            else:
                temporal["_status"] = "ok"
                band_t = temporal

            hyde = get_hyde_land_use(lat=lat, lon=lon, from_year=from_year, to_year=to_year, level=level)
            band_t["hyde_land_use"] = hyde

        if flat:
            sig["temporal"] = band_t
        else:
            sig.setdefault("profile_groups", {})["T"] = band_t

    # F8.5: Qualifying notes for BCE queries on epoch-sensitive bands.
    # Bands C and D are sourced from contemporary datasets and do not represent
    # conditions at the query epoch. The bands are returned as requested — users
    # may want contemporary baselines for comparison — but the note discloses
    # the limitation. Design principle: notes inform, they do not gatekeep.
    if from_year is not None and from_year < 0:
        band_c = sig.get("profile_groups", {}).get("C")
        if band_c is not None:
            band_c["_note"] = [
                "Band C reflects contemporary climatology (WorldClim ~1970–2000 CE). "
                "No paleoclimate reconstruction is available for BCE queries; "
                "these values describe present-day conditions at this location, "
                "not conditions at the requested epoch."
            ]
        band_d = sig.get("profile_groups", {}).get("D")
        if band_d is not None:
            band_d["_note"] = [
                "Band D reflects contemporary land use and demographic data "
                "(EarthStat ~2000 CE, human footprint 2009 CE, GDP contemporary). "
                "These values do not represent conditions at the requested epoch."
            ]

    # Inject meta block — query context, data sources, versioning
    query: Dict[str, Any] = {"lat": lat, "lon": lon, "bands": bands.upper(), "level": level}
    if from_year is not None:
        query["from_year"] = from_year
    if to_year is not None:
        query["to_year"] = to_year

    sig["meta"] = {
        "signature_version": "0.3",
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "query": query,
        "neighborhood": {
            "type": "containing_basin",
            "basin_level": level,
        },
        "data_sources": {
            "basin": f"HydroATLAS v1.0 / BasinATLAS Level 0{level}",
            "elevation_point": "OpenTopoData (mapzen DEM, ~30m) with Open-Meteo fallback",
            "temporal_climate": "LMR v2.1 (Tardif et al. 2019); 0–1998 CE; 2°×2° grid, annual",
            "volcanic": "eVolv2k v4 (Sigl & Toohey 2024)",
            "land_use_temporal": "HYDE 3.4 (Klein Goldewijk et al. 2017); 10000 BCE–2023 CE; ~10 km resolution",
        },
    }

    return sig


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


@router.get("/temporal", include_in_schema=False)
def temporal(
    lat: float,
    lon: float,
    year_start: int = 0,
    year_end: int = 1998,
    vssi_min: float = 5.0,
):
    """Return LMR v2.1 PDSI time series and significant volcanic events for a location.

    Parameters
    ----------
    lat, lon    : coordinates of the place of interest
    year_start  : first year CE (0–1998); default 0
    year_end    : last year CE (0–1998); default 1998
    vssi_min    : minimum volcanic sulfur injection in Tg to include; default 5.0
    """
    result = get_temporal_context(
        lat=lat, lon=lon,
        year_start=year_start, year_end=year_end,
        vssi_min=vssi_min,
    )
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.get("/resolve", include_in_schema=False)
def resolve(name: str):
    """Resolve a place name using WHG suggest + entity detail.

    Returns a ResolvedPlace-style payload with GeoJSON Point coordinates
    when available.
    """
    name = (name or "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="Missing required query parameter: name")

    try:
        first = _whg_suggest_first(name)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"WHG suggest failed: {e}")

    if not first:
        return {
            "label": name,
            "source": "whg",
            "meta": {"status": "not_found"},
        }

    place_id = first.get("id")
    if not place_id:
        return {
            "label": first.get("name") or name,
            "source": "whg",
            "meta": {"status": "no_id", "suggest": first},
        }

    try:
        entity = _whg_entity(str(place_id))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"WHG entity failed: {e}")

    lonlat = _extract_lonlat(entity)
    if not lonlat:
        return {
            "label": entity.get("title") or first.get("name") or name,
            "source": "whg",
            "meta": {
                "status": "no_geometry",
                "whg_id": place_id,
                "score": first.get("score"),
                "description": first.get("description"),
            },
        }

    lon, lat = lonlat
    return {
        "label": entity.get("title") or first.get("name") or name,
        "source": "whg",
        "location": {
            "type": "Point",
            "coordinates": [lon, lat],
        },
        "meta": {
            "status": "ok",
            "whg_id": place_id,
            "score": first.get("score"),
            "description": first.get("description"),
            "ccodes": entity.get("ccodes"),
            "dataset": entity.get("dataset"),
            "dataset_id": entity.get("dataset_id"),
        },
    }


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


@router.get("/whg-place", include_in_schema=False)
def whg_place(id: str):
    """Fetch WHG entity by ID and return coordinates + metadata.

    Use this after user selects from whg-suggest dropdown.
    """
    id = (id or "").strip()
    if not id:
        raise HTTPException(status_code=400, detail="Missing required query parameter: id")

    try:
        entity = _whg_entity(id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"WHG entity failed: {e}")

    lonlat = _extract_lonlat(entity)
    if not lonlat:
        return {
            "id": id,
            "label": entity.get("title"),
            "source": "whg",
            "meta": {
                "status": "no_geometry",
                "ccodes": entity.get("ccodes"),
                "fclasses": entity.get("fclasses"),
            },
        }

    lon, lat = lonlat
    return {
        "id": id,
        "label": entity.get("title"),
        "source": "whg",
        "location": {
            "type": "Point",
            "coordinates": [lon, lat],
        },
        "meta": {
            "status": "ok",
            "ccodes": entity.get("ccodes"),
            "fclasses": entity.get("fclasses"),
            "dataset": entity.get("dataset"),
        },
    }


@router.get("/whg-reconcile", include_in_schema=False)
def whg_reconcile(q: str, size: int = 10, bounds: str = None):
    """
    Search WHG using reconcile+extend pipeline.

    Args:
        q: Search query (place name)
        size: Max number of results (default 10, max 20)
        bounds: Optional GeoJSON polygon as JSON string (from map viewport)
    """
    q = (q or "").strip()
    if not q:
        return {"results": []}

    if len(q) < 3:
        return {"results": []}

    if size < 1:
        size = 1
    elif size > 20:
        size = 20

    bounds_geojson = None
    if bounds:
        try:
            bounds_geojson = json.loads(bounds)
        except Exception:
            pass

    try:
        # Fetch 50 from WHG then filter — noisy namespaces dominate top slots
        candidates = _whg_reconcile_query(q, bounds=bounds_geojson, size=50)
        if not candidates:
            return {"results": []}
        _noisy = re.compile(r'^place:(wd|osm|gn):')
        candidates = [c for c in candidates if not _noisy.match(c["id"])][:size]
        if not candidates:
            return {"results": []}
        place_ids = [c["id"] for c in candidates]
        extended = _whg_reconcile_extend(place_ids)
        results = _merge_reconcile_results(candidates, extended)
        return {"results": results}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"WHG search failed: {e}")


@router.get("/whg/suggest")
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


@router.get("/wh-sites", include_in_schema=False)
def wh_sites():
    """Return the small World Heritage seed set used by the pilot UI."""
    try:
        sites = _load_wh_seed()
        cluster_labels = _get_cluster_labels()

        # Add cluster_label to each site
        for site in sites:
            id_no = site.get("id_no")
            site["cluster_label"] = cluster_labels.get(id_no)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"count": len(sites), "sites": sites}


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


@router.get("/similar-text", include_in_schema=False)
def similar_text(id_no: int, limit: int = 5):
    """Return most similar WH sites by text/semantic similarity."""
    try:
        conn = db_connect()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    b.id_no,
                    b.name_en,
                    b.lon,
                    b.lat,
                    ROUND(sim.similarity::numeric, 3) as similarity,
                    c.cluster_label
                FROM edop_text_similarity sim
                JOIN edop_wh_sites a ON a.site_id = sim.site_a
                JOIN edop_wh_sites b ON b.site_id = sim.site_b
                LEFT JOIN edop_text_clusters c ON c.site_id = b.site_id
                WHERE a.id_no = %s
                ORDER BY sim.similarity DESC
                LIMIT %s
            """, (id_no, limit))

            results = []
            for row in cur.fetchall():
                results.append({
                    "id_no": row[0],
                    "name_en": row[1],
                    "lon": float(row[2]),
                    "lat": float(row[3]),
                    "similarity": float(row[4]),
                    "cluster_label": row[5]
                })

            return {"source_id_no": id_no, "similar": results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'conn' in locals():
            conn.close()


# -----------------------
# WH Cities (258) endpoints
# -----------------------

@router.get("/whc-cities", include_in_schema=False)
def whc_cities():
    """Return World Heritage Cities with coordinates and cluster info (excludes 4 without basin data)."""
    try:
        conn = db_connect()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    c.id,
                    c.city,
                    c.country,
                    c.region,
                    ST_X(c.geom) as lon,
                    ST_Y(c.geom) as lat,
                    ec.cluster_id as env_cluster,
                    ec.cluster_label as env_cluster_label
                FROM gaz.wh_cities c
                LEFT JOIN whc_clusters ec ON ec.city_id = c.id
                WHERE c.geom IS NOT NULL
                  AND c.basin_id IS NOT NULL
                ORDER BY c.region, c.country, c.city
            """)

            cities = []
            for row in cur.fetchall():
                cities.append({
                    "id": row[0],
                    "city": row[1],
                    "country": row[2],
                    "region": row[3],
                    "location": {
                        "type": "Point",
                        "coordinates": [float(row[4]), float(row[5])]
                    } if row[4] and row[5] else None,
                    "env_cluster": row[6],
                    "env_cluster_label": row[7]
                })

            return {"count": len(cities), "cities": cities}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'conn' in locals():
            conn.close()


@router.get("/whc-similar", include_in_schema=False)
def whc_similar(city_id: int, limit: int = 5):
    """Return most similar WH cities by environmental signature."""
    try:
        conn = db_connect()
        with conn.cursor() as cur:
            # whc_similarity stores upper triangle (city_a < city_b)
            # Need to query both directions
            cur.execute("""
                WITH similarities AS (
                    SELECT city_b as other_id, distance, similarity
                    FROM whc_similarity
                    WHERE city_a = %s
                    UNION ALL
                    SELECT city_a as other_id, distance, similarity
                    FROM whc_similarity
                    WHERE city_b = %s
                )
                SELECT
                    c.id,
                    c.city,
                    c.country,
                    c.region,
                    ST_X(c.geom) as lon,
                    ST_Y(c.geom) as lat,
                    ROUND(s.distance::numeric, 2) as distance,
                    ec.cluster_id as env_cluster,
                    ec.cluster_label as env_cluster_label
                FROM similarities s
                JOIN gaz.wh_cities c ON c.id = s.other_id
                LEFT JOIN whc_clusters ec ON ec.city_id = c.id
                ORDER BY s.distance ASC
                LIMIT %s
            """, (city_id, city_id, limit))

            results = []
            for row in cur.fetchall():
                results.append({
                    "id": row[0],
                    "city": row[1],
                    "country": row[2],
                    "region": row[3],
                    "lon": float(row[4]) if row[4] else None,
                    "lat": float(row[5]) if row[5] else None,
                    "distance": float(row[6]),
                    "env_cluster": row[7],
                    "env_cluster_label": row[8]
                })

            return {"source_city_id": city_id, "similar": results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'conn' in locals():
            conn.close()


@router.get("/whc-similar-env-by-coord", include_in_schema=False)
def whc_similar_env_by_coord(lon: float, lat: float, limit: int = 5):
    """Return most similar WH cities by environmental signature for any coordinate.

    Uses basin-level PCA vectors (pgvector) to find WH cities in environmentally
    similar basins to the input point.
    """
    try:
        conn = db_connect()
        with conn.cursor() as cur:
            # First, find which basin contains this point
            cur.execute("""
                SELECT id FROM basin08
                WHERE ST_Covers(geom, ST_SetSRID(ST_MakePoint(%s, %s), 4326))
                LIMIT 1
            """, (lon, lat))
            row = cur.fetchone()
            if not row:
                return {"error": "No basin found for coordinates", "similar": []}

            source_basin_id = row[0]

            # Check if source basin has PCA vector
            cur.execute("SELECT 1 FROM basin08_pca WHERE basin_id = %s", (source_basin_id,))
            if not cur.fetchone():
                return {"error": "Basin has no PCA vector", "similar": []}

            # Get distance distribution stats (source basin to all WH city basins)
            cur.execute("""
                WITH whc_basin_distances AS (
                    SELECT p1.pca <-> p2.pca AS distance
                    FROM basin08_pca p1, basin08_pca p2
                    JOIN gaz.wh_cities c ON c.basin_id = p2.basin_id
                    WHERE p1.basin_id = %s
                      AND p2.basin_id != %s
                      AND c.basin_id IS NOT NULL
                )
                SELECT
                    MIN(distance),
                    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY distance),
                    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY distance),
                    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY distance),
                    MAX(distance),
                    COUNT(*)
                FROM whc_basin_distances
            """, (source_basin_id, source_basin_id))
            stats_row = cur.fetchone()
            dist_stats = {
                "min": round(float(stats_row[0]), 4) if stats_row[0] else None,
                "p25": round(float(stats_row[1]), 4) if stats_row[1] else None,
                "median": round(float(stats_row[2]), 4) if stats_row[2] else None,
                "p75": round(float(stats_row[3]), 4) if stats_row[3] else None,
                "max": round(float(stats_row[4]), 4) if stats_row[4] else None,
                "count": int(stats_row[5]) if stats_row[5] else 0
            }

            # Find WH cities in the most similar basins by PCA vector distance
            # Also compute percentile rank for each result
            cur.execute("""
                WITH whc_basin_distances AS (
                    SELECT
                        c.id as city_id,
                        p1.pca <-> p2.pca AS distance
                    FROM basin08_pca p1, basin08_pca p2
                    JOIN gaz.wh_cities c ON c.basin_id = p2.basin_id
                    WHERE p1.basin_id = %s
                      AND p2.basin_id != %s
                      AND c.basin_id IS NOT NULL
                ),
                ranked AS (
                    SELECT
                        city_id,
                        distance,
                        PERCENT_RANK() OVER (ORDER BY distance) as pct_rank
                    FROM whc_basin_distances
                )
                SELECT
                    c.id,
                    c.city,
                    c.country,
                    c.region,
                    ST_X(c.geom) as lon,
                    ST_Y(c.geom) as lat,
                    ROUND(r.distance::numeric, 4) as distance,
                    ROUND((r.pct_rank * 100)::numeric, 1) as percentile,
                    ec.cluster_id as env_cluster,
                    ec.cluster_label as env_cluster_label
                FROM ranked r
                JOIN gaz.wh_cities c ON c.id = r.city_id
                LEFT JOIN whc_clusters ec ON ec.city_id = c.id
                ORDER BY r.distance ASC
                LIMIT %s
            """, (source_basin_id, source_basin_id, limit))

            results = []
            for row in cur.fetchall():
                results.append({
                    "id": row[0],
                    "city": row[1],
                    "country": row[2],
                    "region": row[3],
                    "location": {
                        "type": "Point",
                        "coordinates": [float(row[4]), float(row[5])]
                    } if row[4] and row[5] else None,
                    "distance": float(row[6]) if row[6] is not None else None,
                    "percentile": float(row[7]) if row[7] is not None else None,
                    "env_cluster": row[8],
                    "env_cluster_label": row[9]
                })

            return {
                "source_basin_id": source_basin_id,
                "count": len(results),
                "dist_stats": dist_stats,
                "similar": results
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'conn' in locals():
            conn.close()


@router.get("/whc-similar-text", include_in_schema=False)
def whc_similar_text(city_id: int, band: str = "composite", limit: int = 5):
    """Return most similar WH cities by text/semantic similarity."""
    valid_bands = ['history', 'environment', 'culture', 'modern', 'composite']
    if band not in valid_bands:
        raise HTTPException(status_code=400, detail=f"Invalid band. Must be one of: {valid_bands}")

    try:
        conn = db_connect()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    c.id,
                    c.city,
                    c.country,
                    c.region,
                    ST_X(c.geom) as lon,
                    ST_Y(c.geom) as lat,
                    ROUND(s.similarity::numeric, 3) as similarity,
                    tc.cluster_id as text_cluster
                FROM whc_band_similarity s
                JOIN gaz.wh_cities c ON c.id = s.city_b
                LEFT JOIN whc_band_clusters tc ON tc.city_id = c.id AND tc.band = %s
                WHERE s.city_a = %s AND s.band = %s
                ORDER BY s.rank ASC
                LIMIT %s
            """, (band, city_id, band, limit))

            results = []
            for row in cur.fetchall():
                results.append({
                    "id": row[0],
                    "city": row[1],
                    "country": row[2],
                    "region": row[3],
                    "lon": float(row[4]) if row[4] else None,
                    "lat": float(row[5]) if row[5] else None,
                    "similarity": float(row[6]),
                    "text_cluster": row[7]
                })

            return {"source_city_id": city_id, "band": band, "similar": results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'conn' in locals():
            conn.close()


@router.get("/whc-summaries", include_in_schema=False)
def whc_summaries(city_id: int):
    """Return band summaries for a WH city."""
    try:
        conn = db_connect()
        with conn.cursor() as cur:
            # Get city name
            cur.execute("SELECT city, country FROM gaz.wh_cities WHERE id = %s", (city_id,))
            city_row = cur.fetchone()
            if not city_row:
                raise HTTPException(status_code=404, detail="City not found")

            # Get summaries in desired order
            cur.execute("""
                SELECT band, summary
                FROM whc_band_summaries
                WHERE city_id = %s AND status = 'ok'
                ORDER BY CASE band
                    WHEN 'environment' THEN 1
                    WHEN 'history' THEN 2
                    WHEN 'culture' THEN 3
                    WHEN 'modern' THEN 4
                END
            """, (city_id,))

            summaries = []
            for row in cur.fetchall():
                summaries.append({
                    "band": row[0],
                    "summary": row[1]
                })

            return {
                "city_id": city_id,
                "city": city_row[0],
                "country": city_row[1],
                "summaries": summaries
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'conn' in locals():
            conn.close()


# -----------------------
# Basin Cluster endpoints
# -----------------------

@router.get("/basin-clusters", include_in_schema=False)
def basin_clusters():
    """Return all basin clusters with basin counts, city counts, and labels."""
    try:
        conn = db_connect()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    b.cluster_id,
                    COUNT(DISTINCT b.id) as basin_count,
                    COUNT(DISTINCT c.id) as city_count,
                    lbl.label
                FROM basin08 b
                LEFT JOIN gaz.wh_cities c ON c.basin_id = b.id
                LEFT JOIN basin_cluster_labels lbl ON lbl.cluster_id = b.cluster_id
                WHERE b.cluster_id IS NOT NULL
                GROUP BY b.cluster_id, lbl.label
                ORDER BY b.cluster_id
            """)

            clusters = []
            for row in cur.fetchall():
                clusters.append({
                    "cluster_id": row[0],
                    "basin_count": row[1],
                    "city_count": row[2],
                    "label": row[3]
                })

            return {"clusters": clusters}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'conn' in locals():
            conn.close()


@router.get("/basin-clusters/{cluster_id}/cities", include_in_schema=False)
def basin_cluster_cities(cluster_id: int):
    """Return cities in basins of a given cluster."""
    try:
        conn = db_connect()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    c.id,
                    c.city,
                    c.country,
                    c.region,
                    ST_X(c.geom) as lon,
                    ST_Y(c.geom) as lat
                FROM gaz.wh_cities c
                JOIN basin08 b ON c.basin_id = b.id
                WHERE b.cluster_id = %s
                ORDER BY c.country, c.city
            """, (cluster_id,))

            cities = []
            for row in cur.fetchall():
                cities.append({
                    "id": row[0],
                    "city": row[1],
                    "country": row[2],
                    "region": row[3],
                    "lon": float(row[4]) if row[4] else None,
                    "lat": float(row[5]) if row[5] else None
                })

            return {
                "cluster_id": cluster_id,
                "city_count": len(cities),
                "cities": cities
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'conn' in locals():
            conn.close()


# -----------------------
# Gazetteer endpoints
# -----------------------

@router.get("/gaz-similar", include_in_schema=False)
def gaz_similar(gaz_id: int, limit: int = 10):
    """Find environmentally similar gazetteer places using PCA vector distance."""
    if limit < 1:
        limit = 1
    elif limit > 25:
        limit = 25

    try:
        conn = db_connect()
        with conn.cursor() as cur:
            # Get the source place's basin
            cur.execute("""
                SELECT g.id, g.title, g.basin_id
                FROM gaz.edop_gaz g
                WHERE g.id = %s
            """, (gaz_id,))
            source = cur.fetchone()
            if not source:
                return {"error": "Place not found", "similar": []}

            source_id, source_title, source_basin_id = source

            if source_basin_id is None:
                return {"error": "Place has no basin assignment", "similar": []}

            # Check if source basin has PCA vector
            cur.execute("SELECT 1 FROM basin08_pca WHERE basin_id = %s", (source_basin_id,))
            if not cur.fetchone():
                return {"error": "Basin has no PCA vector", "similar": []}

            # Find places in the most similar basins by PCA vector distance
            # We find more similar basins than needed, then pick places from them
            cur.execute("""
                WITH similar_basins AS (
                    SELECT
                        p2.basin_id,
                        p1.pca <-> p2.pca AS distance
                    FROM basin08_pca p1, basin08_pca p2
                    WHERE p1.basin_id = %s
                      AND p2.basin_id != %s
                    ORDER BY p1.pca <-> p2.pca
                    LIMIT 500
                ),
                ranked_places AS (
                    SELECT
                        g.id, g.title, g.source, g.ccodes, g.lon, g.lat,
                        sb.distance,
                        b.cluster_id,
                        ROW_NUMBER() OVER (PARTITION BY g.basin_id ORDER BY random()) as rn
                    FROM gaz.edop_gaz g
                    JOIN similar_basins sb ON sb.basin_id = g.basin_id
                    JOIN basin08 b ON b.id = g.basin_id
                    WHERE g.id != %s
                      AND g.lon IS NOT NULL
                )
                SELECT id, title, source, ccodes, lon, lat,
                       ROUND(distance::numeric, 4) as distance, cluster_id
                FROM ranked_places
                WHERE rn = 1
                ORDER BY distance
                LIMIT %s
            """, (source_basin_id, source_basin_id, gaz_id, limit))

            results = []
            for row in cur.fetchall():
                results.append({
                    "id": row[0],
                    "title": row[1],
                    "source": row[2],
                    "ccodes": row[3],
                    "lon": float(row[4]) if row[4] else None,
                    "lat": float(row[5]) if row[5] else None,
                    "distance": float(row[6]),
                    "cluster_id": row[7]
                })

            return {
                "source_id": gaz_id,
                "source_title": source_title,
                "similar": results
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'conn' in locals():
            conn.close()


@router.get("/gaz-suggest", include_in_schema=False)
def gaz_suggest(q: str, limit: int = 10):
    """Search the edop_gaz gazetteer for autocomplete suggestions."""
    q = (q or "").strip()
    if not q or len(q) < 3:
        return {"results": []}

    if limit < 1:
        limit = 1
    elif limit > 25:
        limit = 25

    try:
        conn = db_connect()
        with conn.cursor() as cur:
            # Case-insensitive prefix search on title
            cur.execute("""
                SELECT id, source, source_id, title, ccodes, lon, lat
                FROM gaz.edop_gaz
                WHERE title ILIKE %s
                ORDER BY title
                LIMIT %s
            """, (q + '%', limit))

            results = []
            for row in cur.fetchall():
                results.append({
                    "id": row[0],
                    "source": row[1],
                    "source_id": row[2],
                    "title": row[3],
                    "ccodes": row[4],  # already an array
                    "lon": float(row[5]) if row[5] else None,
                    "lat": float(row[6]) if row[6] else None,
                })

            return {"results": results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'conn' in locals():
            conn.close()


# -----------------------
# Ecoregion Hierarchy endpoints
# -----------------------

@router.get("/eco/realms", include_in_schema=False)
def eco_realms():
    """List all realms (top level of hierarchy)."""
    try:
        conn = db_connect()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT r.realm, r.biogeorelm, COUNT(s.subrealmid) as subrealm_count
                FROM gaz."Realm2023" r
                LEFT JOIN gaz."Subrealm2023" s ON s.biogeorelm = r.biogeorelm
                GROUP BY r.realm, r.biogeorelm
                ORDER BY r.realm
            """)
            results = []
            for row in cur.fetchall():
                results.append({
                    "id": row[1],  # biogeorelm as id for drilling down
                    "name": row[0],  # realm name for display
                    "subrealm_count": row[2]
                })
            return {"count": len(results), "realms": results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'conn' in locals():
            conn.close()


@router.get("/eco/subrealms", include_in_schema=False)
def eco_subrealms(realm: str):
    """List subrealms within a realm."""
    try:
        conn = db_connect()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT s.subrealmid, s.subrealm_n, COUNT(b.bioregions) as bioregion_count
                FROM gaz."Subrealm2023" s
                LEFT JOIN gaz."Bioregions2023" b ON b.subrealm_id = s.subrealmid
                WHERE s.biogeorelm = %s
                GROUP BY s.subrealmid, s.subrealm_n
                ORDER BY s.subrealm_n
            """, (realm,))
            results = []
            for row in cur.fetchall():
                results.append({
                    "id": row[0],
                    "name": row[1],
                    "bioregion_count": row[2]
                })
            return {"realm": realm, "count": len(results), "subrealms": results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'conn' in locals():
            conn.close()


@router.get("/eco/bioregions", include_in_schema=False)
def eco_bioregions(subrealm_id: int):
    """List bioregions within a subrealm."""
    try:
        conn = db_connect()
        with conn.cursor() as cur:
            # Get subrealm name for context
            cur.execute('SELECT subrealm_n FROM gaz."Subrealm2023" WHERE subrealmid = %s', (subrealm_id,))
            sr = cur.fetchone()
            subrealm_name = sr[0] if sr else None

            # Join with bioregion_meta for titles and OneEarth links
            cur.execute("""
                SELECT b.bioregions, COUNT(e.eco_id) as ecoregion_count,
                       m.title, m.url_slug
                FROM gaz."Bioregions2023" b
                LEFT JOIN gaz."Ecoregions2017" e ON e.bioregion = b.bioregions
                LEFT JOIN gaz.bioregion_meta m ON m.bioregion_id = b.bioregions
                WHERE b.subrealm_id = %s
                GROUP BY b.bioregions, m.title, m.url_slug
                ORDER BY b.bioregions
            """, (subrealm_id,))
            results = []
            for row in cur.fetchall():
                bioregion = {
                    "id": row[0],
                    "name": row[2] if row[2] else row[0],  # Use title if available, else code
                    "code": row[0],
                    "ecoregion_count": row[1]
                }
                if row[3]:  # url_slug
                    bioregion["oneearth_url"] = f"https://www.oneearth.org/{row[3]}"
                results.append(bioregion)
            return {"subrealm_id": subrealm_id, "subrealm_name": subrealm_name, "count": len(results), "bioregions": results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'conn' in locals():
            conn.close()


@router.get("/eco/ecoregions", include_in_schema=False)
def eco_ecoregions(bioregion: str):
    """List ecoregions within a bioregion."""
    try:
        conn = db_connect()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT e.eco_id, e.eco_name, e.biome_name, e.realm
                FROM gaz."Ecoregions2017" e
                WHERE e.bioregion = %s
                ORDER BY e.eco_name
            """, (bioregion,))
            results = []
            for row in cur.fetchall():
                results.append({
                    "id": row[0],
                    "name": row[1],
                    "biome": row[2],
                    "realm": row[3]
                })
            return {"bioregion": bioregion, "count": len(results), "ecoregions": results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'conn' in locals():
            conn.close()


@router.get("/eco/realms/geom", include_in_schema=False)
def eco_realms_geom():
    """Get GeoJSON FeatureCollection of all realm geometries."""
    try:
        conn = db_connect()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT realm, biogeorelm, ST_AsGeoJSON(geom)::json
                FROM gaz."Realm2023"
                ORDER BY realm
            """)
            rows = cur.fetchall()

        features = []
        for row in rows:
            features.append({
                "type": "Feature",
                "properties": {"name": row[0], "id": row[1]},
                "geometry": row[2]
            })

        return {
            "type": "FeatureCollection",
            "features": features
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'conn' in locals():
            conn.close()


@router.get("/eco/subrealms/geom", include_in_schema=False)
def eco_subrealms_geom(realm: str):
    """Get GeoJSON FeatureCollection of subrealm geometries within a realm."""
    try:
        conn = db_connect()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT subrealmid, subrealm_n, ST_AsGeoJSON(geom)::json
                FROM gaz."Subrealm2023"
                WHERE biogeorelm = %s
                ORDER BY subrealm_n
            """, (realm,))
            rows = cur.fetchall()

        features = []
        for row in rows:
            features.append({
                "type": "Feature",
                "properties": {"id": row[0], "name": row[1]},
                "geometry": row[2]
            })

        return {
            "type": "FeatureCollection",
            "features": features
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'conn' in locals():
            conn.close()


@router.get("/eco/bioregions/geom", include_in_schema=False)
def eco_bioregions_geom(subrealm_id: int):
    """Get GeoJSON FeatureCollection of bioregion geometries within a subrealm."""
    try:
        conn = db_connect()
        with conn.cursor() as cur:
            # Join with bioregion_meta for titles
            cur.execute("""
                SELECT b.bioregions, ST_AsGeoJSON(b.geom)::json, m.title
                FROM gaz."Bioregions2023" b
                LEFT JOIN gaz.bioregion_meta m ON m.bioregion_id = b.bioregions
                WHERE b.subrealm_id = %s
                ORDER BY b.bioregions
            """, (subrealm_id,))
            rows = cur.fetchall()

        features = []
        for row in rows:
            features.append({
                "type": "Feature",
                "properties": {
                    "id": row[0],
                    "name": row[2] if row[2] else row[0],  # Title if available, else code
                    "code": row[0]
                },
                "geometry": row[1]
            })

        return {
            "type": "FeatureCollection",
            "features": features
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'conn' in locals():
            conn.close()


@router.get("/eco/ecoregions/geom", include_in_schema=False)
def eco_ecoregions_geom(bioregion: str):
    """Get GeoJSON FeatureCollection of ecoregion geometries within a bioregion."""
    try:
        conn = db_connect()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT eco_id, eco_name, ST_AsGeoJSON(geom)::json
                FROM gaz."Ecoregions2017"
                WHERE bioregion = %s
                ORDER BY eco_name
            """, (bioregion,))
            rows = cur.fetchall()

        features = []
        for row in rows:
            features.append({
                "type": "Feature",
                "properties": {"id": row[0], "name": row[1]},
                "geometry": row[2]
            })

        return {
            "type": "FeatureCollection",
            "features": features
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'conn' in locals():
            conn.close()


@router.get("/eco/geom", include_in_schema=False)
def eco_geom(level: str, id: str):
    """Get GeoJSON geometry for a hierarchy level item."""
    valid_levels = ['realm', 'subrealm', 'bioregion', 'ecoregion']
    if level not in valid_levels:
        raise HTTPException(status_code=400, detail=f"Invalid level. Must be one of: {valid_levels}")

    try:
        conn = db_connect()
        with conn.cursor() as cur:
            if level == 'realm':
                cur.execute("""
                    SELECT realm, ST_AsGeoJSON(geom)::json
                    FROM gaz."Realm2023" WHERE biogeorelm = %s
                """, (id,))
            elif level == 'subrealm':
                cur.execute("""
                    SELECT subrealm_n, ST_AsGeoJSON(geom)::json
                    FROM gaz."Subrealm2023" WHERE subrealmid = %s
                """, (int(id),))
            elif level == 'bioregion':
                cur.execute("""
                    SELECT bioregions, ST_AsGeoJSON(geom)::json
                    FROM gaz."Bioregions2023" WHERE bioregions = %s
                """, (id,))
            elif level == 'ecoregion':
                cur.execute("""
                    SELECT eco_name, ST_AsGeoJSON(geom)::json
                    FROM gaz."Ecoregions2017" WHERE eco_id = %s
                """, (int(id),))

            row = cur.fetchone()
            if not row:
                return {"error": "Not found"}

            return {
                "level": level,
                "id": id,
                "name": row[0],
                "geometry": row[1]
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'conn' in locals():
            conn.close()


@router.get("/eco/wikitext", include_in_schema=False)
def eco_wikitext(eco_id: int):
    """Get Wikipedia summary and URL for an ecoregion."""
    try:
        conn = db_connect()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT e.eco_name, w.summary, w.wiki_url
                FROM gaz."Ecoregions2017" e
                LEFT JOIN public.eco_wikitext w ON w.eco_id = e.eco_id
                WHERE e.eco_id = %s
            """, (eco_id,))
            row = cur.fetchone()

            if not row:
                return {"eco_id": eco_id, "error": "Not found"}

            return {
                "eco_id": eco_id,
                "eco_name": row[0],
                "summary": row[1],
                "wiki_url": row[2]
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'conn' in locals():
            conn.close()


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


# -----------------------
# D-PLACE Societies
# -----------------------

@router.get("/societies", include_in_schema=False)
def societies():
    """Return all D-PLACE societies with coordinates, bioregion, and cultural variables."""
    try:
        conn = db_connect()
        with conn.cursor() as cur:
            # Get societies with bioregion, ecoregion, realm, basin cluster, EA042 (subsistence), EA034 (religion)
            cur.execute("""
                SELECT s.id, s.name, s.region, ss.bioregion_id,
                       m.title as bioregion_name,
                       s.longitude as lon, s.latitude as lat,
                       c.name as subsistence,
                       ss.eco_id, e.eco_name,
                       r.realm,
                       ba.cluster_id,
                       rel.name as religion
                FROM dplace.societies s
                LEFT JOIN dplace.society_spatial ss ON ss.soc_id = s.id
                LEFT JOIN gaz.bioregion_meta m ON m.bioregion_id = ss.bioregion_id
                LEFT JOIN dplace.data d ON d.soc_id = s.id AND d.var_id = 'EA042'
                LEFT JOIN dplace.codes c ON c.id = d.code_id
                    AND c.name NOT IN ('Missing data', '', 'Missing for at least 1 activity', 'Two or more sources')
                LEFT JOIN dplace.data rd ON rd.soc_id = s.id AND rd.var_id = 'EA034'
                LEFT JOIN dplace.codes rel ON rel.id = rd.code_id
                    AND rel.name != 'Missing data'
                LEFT JOIN gaz."Ecoregions2017" e ON e.eco_id = ss.eco_id
                LEFT JOIN gaz."Bioregions2023" b ON b.bioregions = ss.bioregion_id
                LEFT JOIN gaz."Subrealm2023" sr ON sr.subrealmid = b.subrealm_id
                LEFT JOIN gaz."Realm2023" r ON r.biogeorelm = sr.biogeorelm
                LEFT JOIN dplace.society_basin sb ON sb.soc_id = s.id AND sb.basin_level = 8
                LEFT JOIN basin08 ba ON ba.hybas_id = sb.basin_id
                WHERE s.contribution_id = 'dplace-dataset-ea'
                ORDER BY ss.bioregion_id, s.name
            """)
            rows = cur.fetchall()

            societies = []
            for row in rows:
                # Strip parenthetical content from realm
                realm = row[10]
                if realm and '(' in realm:
                    realm = realm.split('(')[0].strip()
                societies.append({
                    "id": row[0],
                    "name": row[1],
                    "region": row[2],
                    "bioregion_id": row[3],
                    "bioregion_name": row[4],
                    "lon": row[5],
                    "lat": row[6],
                    "subsistence": row[7],
                    "eco_id": row[8],
                    "eco_name": row[9],
                    "realm": realm,
                    "cluster_id": row[11],
                    "religion": row[12]
                })

            # Get unique bioregions for legend
            bioregions = []
            seen = set()
            for s in societies:
                if s["bioregion_id"] and s["bioregion_id"] not in seen:
                    seen.add(s["bioregion_id"])
                    bioregions.append({
                        "id": s["bioregion_id"],
                        "name": s["bioregion_name"]
                    })
            bioregions.sort(key=lambda x: x["id"])

            # Get subsistence categories with counts
            subsistence_counts = {}
            for s in societies:
                sub = s["subsistence"]
                if sub:
                    subsistence_counts[sub] = subsistence_counts.get(sub, 0) + 1
            subsistence_categories = [
                {"name": k, "count": v}
                for k, v in sorted(subsistence_counts.items(), key=lambda x: -x[1])
            ]

            # Get religion categories with counts (ordered by conceptual progression)
            religion_order = ['Absent', 'Otiose', 'Active, but not supporting morality', 'Active, supporting morality']
            religion_counts = {}
            for s in societies:
                rel = s["religion"]
                if rel:
                    religion_counts[rel] = religion_counts.get(rel, 0) + 1
            religion_categories = [
                {"name": k, "count": religion_counts.get(k, 0)}
                for k in religion_order if k in religion_counts
            ]

            # Get variable descriptions for tooltips
            cur.execute("""
                SELECT id, name, description
                FROM dplace.variables
                WHERE id IN ('EA042', 'EA034')
            """)
            var_rows = cur.fetchall()
            variable_info = {
                row[0]: {"name": row[1], "description": row[2]}
                for row in var_rows
            }

            return {
                "count": len(societies),
                "bioregions": bioregions,
                "subsistence_categories": subsistence_categories,
                "religion_categories": religion_categories,
                "variable_info": variable_info,
                "societies": societies
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'conn' in locals():
            conn.close()


# -----------------------
# Explorer: codebook metadata
# -----------------------

_CODEBOOK_FIELDS = [
    "schema_key", "friendly_name", "band", "dimension", "type", "units",
    "s_u", "status", "typology_cluster", "basin08_col_s", "basin08_col_u",
    "high_r_partner", "position_method", "position_notes", "historical_validity",
    "informative_or_degenerate",
]

_variable_cache: List[Dict] = []

def _load_variables() -> List[Dict]:
    global _variable_cache
    if _variable_cache:
        return _variable_cache
    import csv
    cb_path = Path(__file__).resolve().parents[2] / "documentation" / "EDOPS_variable_catalog_v0.3.tsv"
    if not cb_path.exists():
        return []
    rows = []
    with cb_path.open(newline="") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            band = row.get("band", "")
            if not band or band == "output":
                continue
            rec = {k: (row.get(k) or None) for k in _CODEBOOK_FIELDS}
            col_s = rec.get("basin08_col_s") or ""
            # monthly_series: range notation ending in s01..s12 (12-month seasonal columns)
            is_monthly = col_s.endswith("s01..s12")
            rec["monthly_series"] = is_monthly
            # queryable = has a single DB column, OR is a monthly series (column resolved per month)
            # Band T subsystem: lmr | evolv2k | hyde (drives Explorer rendering mode)
            key = rec.get("schema_key") or ""
            if key.startswith("lmr_"):
                rec["t_subsystem"] = "lmr"
            elif key.startswith("evolv2k_"):
                rec["t_subsystem"] = "evolv2k"
            elif key.startswith("hyde_"):
                rec["t_subsystem"] = "hyde"
            else:
                rec["t_subsystem"] = None
            is_band_t_active = (
                rec.get("band") == "T" and
                rec.get("status") == "implemented" and
                rec.get("t_subsystem") is not None
            )
            rec["queryable"] = (bool(col_s) and (".." not in col_s or is_monthly)) or is_band_t_active
            rows.append(rec)
    # Second pass: hide _id vars whose _name or _code partner exists in the same codebook
    all_keys = {r["schema_key"] for r in rows}
    for rec in rows:
        key = rec.get("schema_key") or ""
        if key.endswith("_id"):
            base = key[:-3]
            rec["hide_in_explorer"] = (base + "_name" in all_keys) or (base + "_code" in all_keys)
        else:
            rec["hide_in_explorer"] = False
    _variable_cache = rows
    return rows


# Lookup table registry for categorical variables.
# (lu_table, id_col, name_col)  — id_col joins to basin08_col_s (cast to text both sides)
_CAT_LOOKUP: Dict[str, tuple] = {
    "lithology_name":             ("lu_lit", "id",       "class_name"),
    "climate_zone_name":          ("lu_clz", "genz_id",  "genz_name"),
    "climate_stratum_code":       ("lu_cls", "gens_id",  "gens_code"),
    "biome_name":                 ("lu_tbi", "biome_id", "biome_name"),
    "ecoregion_terrestrial_name": ("lu_tec", "eco_id",   "ecoregion_name"),
    "pnv_majority_name":          ("lu_pnv", "pnv_id",   "pnv_name"),
    "freshwater_habitat_name":    ("lu_fmh", "mht_id",   "mht_name"),
    "freshwater_ecoregion_name":  ("lu_fec", "eco_id",   "ecoregion_name"),
    "land_cover_name":            ("lu_glc", "glc_id",   "glc_name"),
}

@router.get("/explorer/variables", include_in_schema=False)
def explorer_variables():
    return _load_variables()


_lisa_df_cache = None

def _load_lisa_df():
    global _lisa_df_cache
    if _lisa_df_cache is not None:
        return _lisa_df_cache
    import pandas as pd
    p = Path(__file__).resolve().parents[2] / "output" / "edop" / "esda" / "lisa_classifications.parquet"
    if not p.exists():
        return None
    _lisa_df_cache = pd.read_parquet(p)
    return _lisa_df_cache


@router.get("/explorer/lisa", include_in_schema=False)
def explorer_lisa(var: str, level: int = 8):
    """Return per-basin LISA class assignments for one variable at one scale.

    Returns a flat dict {str(hybas_id): lisa_class} for O(1) JS lookup.
    No geometry — client reuses the already-loaded choropleth layer.
    """
    cb = _load_variables()
    row = next((r for r in cb if r["schema_key"] == var), None)
    if not row:
        raise HTTPException(status_code=404, detail=f"Variable '{var}' not found")

    col_s = row.get("basin08_col_s")
    if not col_s:
        raise HTTPException(status_code=404, detail=f"No basin column for '{var}'")
    if level not in (6, 8):
        raise HTTPException(status_code=400, detail="level must be 6 or 8")

    df = _load_lisa_df()
    if df is None:
        raise HTTPException(status_code=503, detail="LISA parquet not found")

    scale = f"L{level}"
    sub = df[(df["variable"] == col_s) & (df["scale"] == scale)][["hybas_id", "lisa_class"]]
    if sub.empty:
        raise HTTPException(
            status_code=404,
            detail=f"No LISA data for '{var}' at L{level} — run the L{level} sweep first"
        )

    counts = sub["lisa_class"].value_counts().to_dict()
    classes = dict(zip(sub["hybas_id"].astype(int).astype(str), sub["lisa_class"]))
    return {
        "meta": {"var": var, "col": col_s, "level": level, "n": len(sub), "counts": counts},
        "classes": classes,
    }


@router.get("/explorer/values", include_in_schema=False)
def explorer_values(var: str, level: int = 6, su: str = "s", month: Optional[int] = None):
    """Return flat {hybas_id: value} dict + summary stats for one variable at one level.

    su: 's' = local (basin08_col_s), 'u' = upstream (basin08_col_u),
        'delta' = s minus u (diverging render regardless of var type).
    month: 1–12 for monthly-series variables (temperature_monthly, precipitation_monthly).
    NoData (-9999) masked to null. Temperature cols (tmp_dc_*) divided by 10 (°C×10→°C).
    Response: {meta: {...}, values: {hybas_id: value|null, ...}}
    """
    cb = _load_variables()
    row = next((r for r in cb if r["schema_key"] == var), None)
    if not row:
        raise HTTPException(status_code=404, detail=f"Variable '{var}' not found")

    col_s = row.get("basin08_col_s")
    col_u = row.get("basin08_col_u")

    # Resolve monthly-series column: 'tmp_dc_s01..s12' + month=3 → 'tmp_dc_s03'
    if row.get("monthly_series"):
        if month is None:
            month = 1
        if not (1 <= month <= 12):
            raise HTTPException(status_code=400, detail="month must be 1–12")
        prefix = col_s.split("..")[0][:-2]   # 'tmp_dc_s01..s12' → 'tmp_dc_s'
        col_s = f"{prefix}{month:02d}"        # → 'tmp_dc_s03'
        su = "s"  # monthly vars have no upstream

    if su not in ("s", "u", "delta"):
        raise HTTPException(status_code=400, detail="su must be 's', 'u', or 'delta'")
    if su == "s" and not col_s:
        raise HTTPException(status_code=400, detail=f"'{var}' has no local column")
    if su == "u" and not col_u:
        raise HTTPException(status_code=400, detail=f"'{var}' has no upstream column")
    if su == "delta" and not (col_s and col_u):
        raise HTTPException(status_code=400, detail=f"'{var}' requires both s and u columns for delta")
    if level not in (6, 8):
        raise HTTPException(status_code=400, detail="level must be 6 or 8")

    basin_table = "basin06" if level == 6 else "basin08"
    tol = 0.01 if level == 6 else 0.05
    NODATA = -9999

    def _col_expr(col: str) -> str:
        # col names come from the codebook (server-controlled), not user input
        base = f"CASE WHEN {col} = {NODATA} THEN NULL ELSE {col}::float END"
        if col.startswith("tmp_dc_"):
            base = f"CASE WHEN {col} = {NODATA} THEN NULL ELSE ({col}::float / 10.0) END"
        return base

    if su == "delta":
        scale = "/ 10.0" if col_s.startswith("tmp_dc_") else ""
        val_expr = (
            f"CASE WHEN {col_s} = {NODATA} OR {col_u} = {NODATA} THEN NULL "
            f"ELSE (({col_s}::float - {col_u}::float){scale}) END"
        )
    elif su == "u":
        val_expr = _col_expr(col_u)
    else:
        val_expr = _col_expr(col_s)

    try:
        conn = db_connect()
        with conn.cursor() as cur:
            cur.execute(f"""
                SELECT hybas_id, {val_expr} AS value
                FROM public.{basin_table}
                ORDER BY hybas_id
            """)
            rows = cur.fetchall()

        valid_rows = [(r[0], r[1]) for r in rows if r[1] is not None]
        n_total = len(rows)
        n_valid = len(valid_rows)

        if valid_rows:
            import statistics
            vals = [r[1] for r in valid_rows]
            sv = sorted(vals)
            def _pct(p): return round(sv[int(p / 100 * (n_valid - 1))], 5)
            meta = {
                "var": var, "su": su, "level": level,
                "var_type": row.get("type"),
                "units": row.get("units") or "",
                "s_u": row.get("s_u"),
                "n_total": n_total,
                "n_valid": n_valid,
                "zero_fraction": round(sum(1 for v in vals if v == 0) / n_valid, 5),
                "min":    round(min(vals), 5),
                "max":    round(max(vals), 5),
                "mean":   round(statistics.mean(vals), 5),
                "median": round(statistics.median(vals), 5),
                "p10": _pct(10), "p25": _pct(25),
                "p75": _pct(75), "p90": _pct(90),
            }
        else:
            meta = {"var": var, "su": su, "level": level, "n_total": n_total, "n_valid": 0}

        values = {int(r[0]): r[1] for r in rows}
        return {"meta": meta, "values": values}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if "conn" in locals():
            conn.close()


# Qualitative palette (20 colours, Tableau-like)
_QUAL_PALETTE = [
    "#4e79a7","#f28e2b","#e15759","#76b7b2","#59a14f",
    "#edc948","#b07aa1","#ff9da7","#9c755f","#bab0ac",
    "#1f77b4","#ff7f0e","#2ca02c","#d62728","#9467bd",
    "#8c564b","#e377c2","#7f7f7f","#bcbd22","#17becf",
]
_OTHER_COLOR = "#cccccc"
_TOP_N = 20   # classes beyond this are collapsed to "Other"

@router.get("/explorer/categorical", include_in_schema=False)
def explorer_categorical(var: str, level: int = 6):
    """Return category counts + flat {hybas_id: cat_id} dict for a categorical variable.

    Categories are sorted by basin count descending; if more than _TOP_N unique
    classes exist, the tail is collapsed to an 'Other' entry (cat_id = -1).
    Response: {meta: {...}, categories: [...], values: {hybas_id: cat_id, ...}}
    """
    cb = _load_variables()
    row = next((r for r in cb if r["schema_key"] == var), None)
    if not row:
        raise HTTPException(status_code=404, detail=f"Variable '{var}' not found")
    if var not in _CAT_LOOKUP:
        raise HTTPException(status_code=400, detail=f"'{var}' has no categorical lookup")

    basin_col = row.get("basin08_col_s")
    if not basin_col:
        raise HTTPException(status_code=400, detail=f"'{var}' has no basin column")
    if level not in (6, 8):
        raise HTTPException(status_code=400, detail="level must be 6 or 8")

    basin_table = "basin06" if level == 6 else "basin08"
    lu_table, lu_id_col, lu_name_col = _CAT_LOOKUP[var]

    try:
        conn = db_connect()
        with conn.cursor() as cur:
            # 1. Category counts with names (cast both sides to text for type safety)
            cur.execute(f"""
                SELECT lu.{lu_name_col} AS cat_name,
                       b.{basin_col}    AS cat_id,
                       COUNT(*)         AS cnt
                FROM public.{basin_table} b
                LEFT JOIN public.{lu_table} lu
                    ON b.{basin_col}::text = lu.{lu_id_col}::text
                WHERE b.{basin_col} IS NOT NULL
                GROUP BY b.{basin_col}, lu.{lu_name_col}
                ORDER BY cnt DESC
            """)
            count_rows = cur.fetchall()   # (cat_name, cat_id, cnt)

            # 2. Determine top-N set; anything beyond is "Other"
            n_total_basins = sum(r[2] for r in count_rows)
            top_rows  = count_rows[:_TOP_N]
            tail_rows = count_rows[_TOP_N:]
            top_ids   = {r[1] for r in top_rows}

            categories = []
            for i, (cat_name, cat_id, cnt) in enumerate(top_rows):
                categories.append({
                    "id":    cat_id,
                    "name":  cat_name or f"Class {cat_id}",
                    "count": cnt,
                    "pct":   round(100 * cnt / n_total_basins, 2) if n_total_basins else 0,
                    "color": _QUAL_PALETTE[i % len(_QUAL_PALETTE)],
                })
            if tail_rows:
                other_cnt = sum(r[2] for r in tail_rows)
                categories.append({
                    "id":    -1,
                    "name":  f"Other ({len(tail_rows)} classes)",
                    "count": other_cnt,
                    "pct":   round(100 * other_cnt / n_total_basins, 2) if n_total_basins else 0,
                    "color": _OTHER_COLOR,
                })

            # 3. Flat values — cat_id per basin
            cur.execute(f"""
                SELECT hybas_id, {basin_col} AS cat_id
                FROM public.{basin_table}
                ORDER BY hybas_id
            """)
            val_rows = cur.fetchall()

        values = {
            int(r[0]): (r[1] if (r[1] in top_ids) else -1)
            for r in val_rows
        }
        return {
            "meta": {
                "var": var, "level": level,
                "n_classes": len(count_rows),
                "n_shown":   len(top_rows),
                "n_basins":  n_total_basins,
            },
            "categories": categories,
            "values": values,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if "conn" in locals():
            conn.close()


# ---------------------------------------------------------------------------
# Band T: Explorer endpoints
# ---------------------------------------------------------------------------

@router.get("/explorer/evolv2k", include_in_schema=False)
def explorer_evolv2k():
    """Return complete eVolv2k v4 event catalog (256 events). Client-side filtering.

    lat is approximate source latitude only; no longitude in source data.
    Events with lat=0 are equatorial; lat=±45 are unlocated NH/SH defaults.
    """
    with db_connect() as conn:
        rows = conn.execute("""
            SELECT year_ad, month, lat, vssi_tg, vssi_1sig, asymmetry, location, tephra
            FROM temporal.evolv2k_v4
            ORDER BY year_ad
        """).fetchall()
    events = [
        {
            "year":      int(r[0]),
            "month":     int(r[1]) if r[1] is not None else None,
            "lat":       float(r[2]) if r[2] is not None else None,
            "vssi_tg":   round(float(r[3]), 2),
            "vssi_1sig": round(float(r[4]), 2) if r[4] is not None else None,
            "asymmetry": round(float(r[5]), 3) if r[5] is not None else None,
            "location":  r[6],
            "tephra":    bool(r[7]) if r[7] is not None else None,
        }
        for r in rows
    ]
    return {
        "meta": {
            "count":    len(events),
            "year_min": min(e["year"] for e in events),
            "year_max": max(e["year"] for e in events),
            "note": (
                "eVolv2k v4 (Sigl & Toohey 2024). lat = approximate source latitude; "
                "no longitude in source data. lat=0 → equatorial default; "
                "lat=±45 → unlocated NH/SH default."
            ),
        },
        "events": events,
    }


# ---------------------------------------------------------------------------
# Explorer: region definitions
# ---------------------------------------------------------------------------

_REGIONS = [
    {
        "id":    "east_asia",
        "label": "East Asia",
        "bbox":  [95, 18, 145, 55],   # [west, south, east, north]
        "zoom":  4,
    },
    {
        "id":    "south_asia",
        "label": "South Asia",
        "bbox":  [60, 5, 100, 38],
        "zoom":  4,
    },
    {
        "id":    "southwest_asia",
        "label": "Southwest Asia",
        "bbox":  [25, 13, 65, 45],
        "zoom":  4,
    },
    {
        "id":    "mediterranean",
        "label": "Mediterranean & N. Africa",
        "bbox":  [-10, 15, 42, 50],
        "zoom":  4,
    },
    {
        "id":    "mesoamerica",
        "label": "Mesoamerica",
        "bbox":  [-120, 5, -65, 35],
        "zoom":  4,
    },
    {
        "id":    "pacific_northwest",
        "label": "Pacific Northwest",
        "bbox":  [-130, 40, -108, 56],
        "zoom":  5,
    },
]

@router.get("/explorer/regions", include_in_schema=False)
def explorer_regions():
    """Return the fixed set of regional bounding boxes used by the Regions tab."""
    return {"regions": _REGIONS}


# ---------------------------------------------------------------------------
# Explorer: bivariate scatter data
# ---------------------------------------------------------------------------

@router.get("/explorer/scatter", include_in_schema=False)
def explorer_scatter(x: str, y: str, level: int = 6):
    """Return paired values for a bivariate scatter plot.

    Both variables use their local ('s') column. NoData (-9999) masked;
    rows where either value is null are excluded. Temperature columns
    (tmp_dc_*) divided by 10 (°C×10 → °C).

    Response:
      {
        "x_meta": {var, label, units, n_total, n_valid},
        "y_meta": {var, label, units, n_total, n_valid},
        "n_paired": int,
        "values": [[hybas_id, x_val, y_val], ...]
      }
    """
    if level not in (6, 8):
        raise HTTPException(status_code=400, detail="level must be 6 or 8")

    cb = _load_variables()

    def _resolve(var_key: str):
        row = next((r for r in cb if r["schema_key"] == var_key), None)
        if not row:
            raise HTTPException(status_code=404, detail=f"Variable '{var_key}' not found")
        col = row.get("basin08_col_s")
        if not col:
            raise HTTPException(status_code=400, detail=f"'{var_key}' has no local column")
        if row.get("monthly_series"):
            col = col.split("..")[0][:-2] + "01"   # default to January for monthly vars
        return row, col

    x_row, x_col = _resolve(x)
    y_row, y_col = _resolve(y)

    basin_table = "basin06" if level == 6 else "basin08"
    NODATA = -9999

    def _expr(col: str, alias: str) -> str:
        if col.startswith("tmp_dc_"):
            return f"CASE WHEN {col} = {NODATA} THEN NULL ELSE ({col}::float / 10.0) END AS {alias}"
        return f"CASE WHEN {col} = {NODATA} THEN NULL ELSE {col}::float END AS {alias}"

    sql = f"""
        SELECT hybas_id,
               {_expr(x_col, 'xv')},
               {_expr(y_col, 'yv')}
        FROM public.{basin_table}
        ORDER BY hybas_id
    """

    try:
        conn = db_connect()
        with conn.cursor() as cur:
            cur.execute(sql)
            rows = cur.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if "conn" in locals():
            conn.close()

    n_total = len(rows)
    paired = [[int(r[0]), r[1], r[2]] for r in rows if r[1] is not None and r[2] is not None]

    def _meta(row, col, n_paired):
        return {
            "var":     row["schema_key"],
            "col":     col,
            "label":   row.get("friendly_name") or row["schema_key"],
            "units":   row.get("units") or "",
            "n_total": n_total,
            "n_valid": n_paired,
        }

    return {
        "x_meta":   _meta(x_row, x_col, len(paired)),
        "y_meta":   _meta(y_row, y_col, len(paired)),
        "n_paired": len(paired),
        "values":   paired,
    }


# -----------------------
# Explorer — HYDE epoch max
# -----------------------

_HYDE_EPOCH_RANGES = {
    1: (-10000, -4000),
    2: (-3000,  -1000),
    3: (0,          0),
    4: (100,     1000),
    5: (1100,    1700),
    6: (1710,    1900),
    7: (1910,    2025),
}
_HYDE_SAFE_VARS = {"cropland", "grazing", "pasture", "rangeland"}
_LMR_SAFE_VARS  = {"air", "prate"}

# Sidecar written by precompute_hyde_tiles.py; maps {var: {"epoch_N": p99_fraction}}.
# Loaded once on first request; guarantees legend values match the baked tile vmax.
_HYDE_EPOCH_MAXES_PATH = (
    Path(__file__).resolve().parents[2] / "app" / "static" / "explorer" / "hyde_epoch_maxes.json"
)
_hyde_epoch_maxes_cache: dict | None = None


def _load_hyde_epoch_maxes() -> dict:
    global _hyde_epoch_maxes_cache
    if _hyde_epoch_maxes_cache is None and _HYDE_EPOCH_MAXES_PATH.exists():
        with open(_HYDE_EPOCH_MAXES_PATH) as f:
            _hyde_epoch_maxes_cache = json.load(f)
    return _hyde_epoch_maxes_cache or {}


@router.get("/explorer/hyde-epoch-max", include_in_schema=False)
def explorer_hyde_epoch_max(var: str, epoch: int):
    """Return p99 cell-mean fraction for a HYDE variable across one epoch bin.

    Reads from hyde_epoch_maxes.json (written by precompute_hyde_tiles.py) so the
    returned value matches exactly the vmax used when the tiles were baked.
    Falls back to a live DB query (with area_km2 normalisation) if the sidecar is absent.
    """
    if var not in _HYDE_SAFE_VARS:
        raise HTTPException(status_code=400, detail=f"var must be one of {_HYDE_SAFE_VARS}")
    if epoch not in _HYDE_EPOCH_RANGES:
        raise HTTPException(status_code=400, detail="epoch must be 1–7")

    cached = _load_hyde_epoch_maxes()
    p99_cached = cached.get(var)  # one global max per variable, same scale across all epochs
    if p99_cached is not None:
        return {"var": var, "epoch": epoch, "p99_fraction": round(float(p99_cached), 4)}

    # Sidecar not yet generated — fall back to live DB query with correct normalisation.
    y0, y1 = _HYDE_EPOCH_RANGES[epoch]
    sql = f"""
        WITH epoch_steps AS (
            SELECT MIN(step_idx) AS lo, MAX(step_idx) AS hi
            FROM temporal.hyde_times
            WHERE year_ce BETWEEN %(y0)s AND %(y1)s
        ),
        cell_means AS (
            SELECT (
                SELECT AVG(v)
                FROM UNNEST(hc.{var}[
                    (SELECT lo FROM epoch_steps) + 1 :
                    (SELECT hi FROM epoch_steps) + 1
                ]) AS v
            ) / NULLIF(hc.area_km2, 0) AS mean_frac
            FROM temporal.hyde_cells hc
        )
        SELECT percentile_cont(0.99) WITHIN GROUP (ORDER BY mean_frac)
        FROM cell_means
        WHERE mean_frac > 0
    """
    try:
        conn = db_connect()
        with conn.cursor() as cur:
            cur.execute(sql, {"y0": y0, "y1": y1})
            row = cur.fetchone()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if "conn" in locals():
            conn.close()

    p99 = float(row[0]) if row and row[0] is not None else 1.0
    return {"var": var, "epoch": epoch, "p99_fraction": round(p99, 4)}


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
# Cliopatria polity endpoints
# -----------------------

@router.get("/polity/search", include_in_schema=False)
def polity_search(q: str = "", year: Optional[int] = None):
    """Autocomplete search over leaf polity names. Returns name + slice count."""
    if len(q) < 2:
        return []
    sql = """
        SELECT name, MIN(fromyear) AS first, MAX(toyear) AS last, COUNT(*) AS slices
        FROM gaz.clio_polities
        WHERE NOT is_component AND name ILIKE %(pattern)s
    """
    params: Dict[str, Any] = {"pattern": f"%{q}%"}
    if year is not None:
        sql += " AND fromyear <= %(year)s AND toyear >= %(year)s"
        params["year"] = year
    sql += " GROUP BY name ORDER BY name LIMIT 40"
    try:
        conn = db_connect()
        with conn.cursor() as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if "conn" in locals():
            conn.close()
    return [
        {"name": r[0], "first": r[1], "last": r[2], "slices": r[3]}
        for r in rows
    ]


@router.get("/polity/slices", include_in_schema=False)
def polity_slices(name: str):
    """All time slices for a named leaf polity (no geometry).
    Includes geom_hash and geom_group for client-side history tracking."""
    sql = """
        WITH base AS (
            SELECT id, fromyear, toyear, area, seshatid, invalid_source_geom,
                   memberof, components,
                   MD5(ST_AsBinary(geom)) AS geom_hash
            FROM gaz.clio_polities
            WHERE name = %(name)s AND NOT is_component
        ),
        with_prev AS (
            SELECT *, LAG(geom_hash) OVER (ORDER BY fromyear) AS prev_hash
            FROM base
        ),
        with_change AS (
            SELECT *,
                CASE WHEN geom_hash IS DISTINCT FROM prev_hash THEN 1 ELSE 0 END AS is_new
            FROM with_prev
        )
        SELECT id, fromyear, toyear, area, seshatid, invalid_source_geom,
               memberof, components, geom_hash,
               SUM(is_new) OVER (ORDER BY fromyear ROWS UNBOUNDED PRECEDING)::int AS geom_group
        FROM with_change
        ORDER BY fromyear
    """
    try:
        conn = db_connect()
        with conn.cursor() as cur:
            cur.execute(sql, {"name": name})
            rows = cur.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if "conn" in locals():
            conn.close()
    if not rows:
        raise HTTPException(status_code=404, detail=f"Polity '{name}' not found")
    return [
        {
            "id":                  r[0],
            "fromyear":            r[1],
            "toyear":              r[2],
            "area_km2":            round(r[3], 1) if r[3] else None,
            "seshatid":            r[4],
            "invalid_source_geom": r[5],
            "memberof":            r[6],
            "components":          r[7],
            "geom_hash":           r[8],
            "geom_group":          r[9],
        }
        for r in rows
    ]


@router.get("/polity/period", include_in_schema=False)
def polity_period(year: int):
    """GeoJSON FeatureCollection of all active leaf polities at a given year."""
    try:
        conn = db_connect()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT ST_AsGeoJSON(ST_Simplify(geom, 0.08), 4)::json AS geometry,
                       id, name, seshatid, fromyear, toyear
                FROM gaz.clio_polities
                WHERE fromyear <= %(year)s AND toyear >= %(year)s
                  AND NOT is_component
                  AND NOT COALESCE(invalid_source_geom, false)
                  AND geom IS NOT NULL
                ORDER BY name
            """, {"year": year})
            rows = cur.fetchall()
        features = [
            {"type": "Feature", "geometry": geom,
             "properties": {"id": id_, "name": name, "seshatid": seshatid,
                            "fromyear": fromyear, "toyear": toyear}}
            for geom, id_, name, seshatid, fromyear, toyear in rows
            if geom is not None
        ]
        return {"type": "FeatureCollection", "features": features}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


@router.get("/polity/period/years", include_in_schema=False)
def polity_period_years():
    """Sorted list of distinct fromyear values for non-component polities (for smart stepping)."""
    try:
        conn = db_connect()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT DISTINCT fromyear
                FROM gaz.clio_polities
                WHERE NOT is_component
                ORDER BY fromyear
            """)
            rows = cur.fetchall()
        return [r[0] for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


@router.get("/polity/seshat", include_in_schema=False)
def polity_seshat(seshatid: str):
    """Seshat general + social variables for a polity."""
    GENERAL_FIELDS = [
        'original_name', 'capital', 'language', 'linguistic_family',
        'religion', 'religion_family', 'religion_genus',
        'degree_of_centralization', 'duration', 'peak_years',
        'alternative_name', 'supracultural_entity',
        'preceding_entity', 'succeeding_entity',
    ]
    NUMERIC_VARS = {
        'polity_population', 'polity_territory',
        'population_of_the_largest_settlement', 'largest_communication_distance',
        'administrative_level', 'military_level', 'religious_level', 'settlement_hierarchy',
    }
    BINARY_PRESENT = {'present', 'a~p', 'p~a'}

    try:
        conn = db_connect()
        with conn.cursor() as cur:
            # General variables
            cur.execute("""
                SELECT variable_name, value_from, value_to
                FROM seshat.general
                WHERE polity_new_id = %(sid)s AND variable_name = ANY(%(fields)s)
                ORDER BY variable_name, value_from
            """, {"sid": seshatid, "fields": GENERAL_FIELDS})
            gen_rows = cur.fetchall()

            # Social variables — all for this seshatid
            cur.execute("""
                SELECT subsection, variable_name, value_from, value_to
                FROM seshat.social
                WHERE polity_new_id = %(sid)s
                ORDER BY subsection, variable_name
            """, {"sid": seshatid})
            soc_rows = cur.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if "conn" in locals():
            conn.close()

    if not gen_rows and not soc_rows:
        raise HTTPException(status_code=404, detail=f"No Seshat data for '{seshatid}'")

    # Build general dict (multi-value fields become lists)
    general: Dict[str, Any] = {}
    for var, vfrom, vto in gen_rows:
        val = vfrom if not vto else f"{vfrom} – {vto}"
        if var in general:
            if isinstance(general[var], list):
                general[var].append(val)
            else:
                general[var] = [general[var], val]
        else:
            general[var] = val

    # Build social dict grouped by subsection
    # Binary: include only if any value is present/A~P/P~A
    # Numeric: include best (non-unknown) value
    from collections import defaultdict
    soc_agg: Dict[str, Dict[str, Any]] = defaultdict(dict)  # subsection → {var → {value, type}}
    for subsection, var, vfrom, vto in soc_rows:
        if not vfrom:
            continue
        entry = soc_agg[subsection].get(var)
        if var in NUMERIC_VARS:
            if vfrom.lower() != 'unknown':
                try:
                    num = int(vfrom)
                    # Keep largest value (most informative for pop/territory)
                    if entry is None or num > entry.get('num', -1):
                        soc_agg[subsection][var] = {"type": "numeric", "value": vfrom, "num": num}
                except ValueError:
                    pass
        else:
            # Binary — record if present/transitional; don't overwrite a present with absent
            if vfrom.lower() in BINARY_PRESENT:
                soc_agg[subsection][var] = {"type": "binary", "value": vfrom}
            elif entry is None and vfrom.lower() not in {'uncoded', 'unknown'}:
                soc_agg[subsection][var] = {"type": "binary", "value": vfrom}

    # Serialise: drop internal 'num' key, filter to coded entries only
    social: Dict[str, List[Dict]] = {}
    for subsection, vars_dict in sorted(soc_agg.items()):
        entries = []
        for var, info in sorted(vars_dict.items()):
            entries.append({"var": var, "type": info["type"], "value": info["value"]})
        if entries:
            social[subsection] = entries

    return {"seshatid": seshatid, "general": general, "social": social}


@router.get("/polity/geom", include_in_schema=False)
def polity_geom(id: int):
    """GeoJSON Feature for a single polity slice by row id."""
    sql = """
        SELECT name, fromyear, toyear, area, seshatid,
               invalid_source_geom, memberof,
               ST_AsGeoJSON(geom, 6)::json AS geometry
        FROM gaz.clio_polities
        WHERE id = %(id)s
    """
    try:
        conn = db_connect()
        with conn.cursor() as cur:
            cur.execute(sql, {"id": id})
            r = cur.fetchone()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if "conn" in locals():
            conn.close()
    if not r:
        raise HTTPException(status_code=404, detail=f"Slice id {id} not found")
    return {
        "type": "Feature",
        "properties": {
            "id":                  id,
            "name":                r[0],
            "fromyear":            r[1],
            "toyear":              r[2],
            "area_km2":            round(r[3], 1) if r[3] else None,
            "seshatid":            r[4],
            "invalid_source_geom": r[5],
            "memberof":            r[6],
        },
        "geometry": r[7],
    }


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
# /areas endpoint — type-dispatched areal signature (v2 sandbox)
# -----------------------

@router.get("/areas")
def areas(
    type: str,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    radius_km: Optional[float] = None,
    polity: Optional[str] = None,
    year: Optional[int] = None,
    level: int = 6,
    bands: str = "ABCDE",
    from_year: Optional[int] = None,
    to_year: Optional[int] = None,
    detail: bool = False,
):
    """Areal signature dispatcher for the v2 sandbox.

    Parameters
    ----------
    type       : resolver type — 'buffer', 'single_basin', 'polity', 'basin_ring'
    lat, lon   : WGS-84 query point (required for buffer, single_basin, basin_ring)
    radius_km  : buffer radius in km (required for buffer)
    polity     : Cliopatria polity name (required for polity)
    year       : resolver year — boundary slice CE (required for polity)
    level      : basin hierarchy level — 6 or 8 (default 6)
    bands      : band letters to compute (default ABCDE; add T for temporal)
    from_year  : Band T span start CE (required when T in bands)
    to_year    : Band T span end CE (required when T in bands)
    detail     : include per-variable histogram objects in the response
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