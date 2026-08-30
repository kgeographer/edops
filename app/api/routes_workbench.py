"""
app/api/routes_workbench.py
------------------------------
Routes used only by the Workbench page (workbench.html). See
docs/edop/routes_audit.txt for how this classification was derived —
re-run that audit if workbench.html's calls change.
"""
import json
import re
import ssl
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional, Tuple

import certifi
from fastapi import APIRouter, HTTPException

from app.db.connection import db_connect
from app.db.seasonality import find_similar
from app.db.societies_scan import run_societies_env_scan
from app.settings import settings
from app.api.routes_common import _whg_suggest_first, _whg_entity, _extract_lonlat

router = APIRouter(prefix="/api", tags=["api"])


# -----------------------
# WHG reconcile+extend helpers — used only by /whg-reconcile. (Suggest/entity
# helpers used by /resolve live in routes_common.py, shared with Sandbox.)
# -----------------------

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


@router.get("/whc-similar-env-lens", include_in_schema=False)
def whc_similar_env_lens(city_id: int, lens_id: str = "climate.precip", limit: int = 5):
    """Return the N most similar WH cities by LENS_REGISTRY climate distance (L08, topN).

    Uses the L08 similarity index. Corpus-restricted: distances are computed only
    among the 254 cities that have an L08 basin assignment.
    FK path: gaz.wh_cities.basin_id → basin08.id → basin08.hybas_id
    """
    import numpy as np
    try:
        conn = db_connect()
        with conn.cursor() as cur:
            # Query city's L08 hybas_id
            cur.execute("""
                SELECT b.hybas_id
                FROM gaz.wh_cities c
                JOIN public.basin08 b ON b.id = c.basin_id
                WHERE c.id = %s
            """, (city_id,))
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404,
                                    detail=f"City {city_id} not found or has no L08 basin")
            q_hybas_id = int(row[0])

            # Load all other corpus cities with their hybas_ids and display info
            cur.execute("""
                SELECT c.id, c.city, c.country, c.region,
                       ST_X(c.geom) AS lon, ST_Y(c.geom) AS lat,
                       b.hybas_id
                FROM gaz.wh_cities c
                JOIN public.basin08 b ON b.id = c.basin_id
                WHERE c.id != %s AND c.basin_id IS NOT NULL
            """, (city_id,))
            corpus_rows = cur.fetchall()

        corpus_hybas = np.array([r[6] for r in corpus_rows], dtype=np.int64)

        _, ranked = find_similar(
            q_hybas_id,
            lens_id=lens_id,
            n=len(corpus_rows),
            mode="topn",
            level=8,
            filter_hybas_ids=corpus_hybas,
        )

        # Map hybas_id → corpus row for display info
        hybas_to_row = {int(r[6]): r for r in corpus_rows}

        results = []
        for r in ranked:
            city_row = hybas_to_row.get(r["hybas_id"])
            if city_row is None:
                continue
            results.append({
                "id":       city_row[0],
                "city":     city_row[1],
                "country":  city_row[2],
                "region":   city_row[3],
                "lon":      float(city_row[4]) if city_row[4] is not None else None,
                "lat":      float(city_row[5]) if city_row[5] is not None else None,
                "distance": r["distance"],
            })
            if len(results) >= limit:
                break

        return {
            "source_city_id": city_id,
            "lens_id":        lens_id,
            "corpus_size":    len(corpus_rows) + 1,
            "similar":        results,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if "conn" in locals():
            conn.close()


@router.get("/whc-similar-terrain", include_in_schema=False)
def whc_similar_terrain(
    city_id: Optional[int] = None,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    elev_tol: float = 500.0,
    relief_tol: float = 300.0,
    pos_tol: float = 0.10,
    limit: int = 8,
):
    """CITYKIN WO1a terrain lens: query-relative tolerance knobs, ranked retrieval.

    Query by `city_id` (a gaz.wh_cities row) OR by `lat`+`lon` (any point — e.g. Tbilisi, which is
    not itself a corpus city; fetched live via terrain_grid, ~1-2s). Tolerances are query-relative
    (WO1a Part B): each knob is a +/- band around the QUERY's own facet value, not a global threshold.
    Locked defaults (wo1a_findings.md): elev_tol=500, relief_tol=300, pos_tol=0.10, elev_weight=1.0.
    """
    from scripts.cdop.citykin.terrain_lens import rank_by_terrain, FACETS
    from scripts.cdop.citykin.terrain_grid import point_window_terrain
    import pandas as pd

    if city_id is None and (lat is None or lon is None):
        raise HTTPException(status_code=400, detail="Provide city_id, or both lat and lon")

    tolerances = {"grid_elev_mean": elev_tol, "relief_range_m": relief_tol, "landform_position": pos_tol}

    try:
        conn = db_connect()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT c.id, c.city, c.country, c.region, ST_X(c.geom) AS lon, ST_Y(c.geom) AS lat,
                       t.grid_elev_mean, t.relief_range_m, t.landform_position
                FROM gaz.wh_cities c JOIN gaz.wh_cities_terrain t ON t.city_id = c.id
                WHERE c.basin_id IS NOT NULL
                  AND t.grid_elev_mean IS NOT NULL AND t.relief_range_m IS NOT NULL
                  AND t.landform_position IS NOT NULL
            """)
            rows = cur.fetchall()
        corpus = pd.DataFrame(rows, columns=["id", "city", "country", "region", "lon", "lat"] + FACETS)

        exclude_idx = None
        if city_id is not None:
            match = corpus.index[corpus["id"] == city_id]
            if len(match) == 0:
                raise HTTPException(status_code=404,
                                    detail=f"City {city_id} not found, has no L08 basin, or has no resolved terrain")
            exclude_idx = match[0]
            query = {f: corpus.loc[exclude_idx, f] for f in FACETS}
            source = {"source_city_id": city_id}
        else:
            terrain = point_window_terrain(lat, lon)
            if terrain["grid_elev_mean"] is None:
                raise HTTPException(status_code=422,
                                    detail="Not enough land in this point's sampling window to characterize terrain")
            query = {f: terrain[f] for f in FACETS}
            source = {"source_lat": lat, "source_lon": lon}

        ranked = rank_by_terrain(query, corpus, tolerances, elev_weight=1.0, exclude_index=exclude_idx)

        results = []
        for _, r in ranked.head(limit).iterrows():
            results.append({
                "id":      int(r["id"]),
                "city":    r["city"],
                "country": r["country"],
                "region":  r["region"],
                "lon":     float(r["lon"]),
                "lat":     float(r["lat"]),
                "distance": round(float(r["terrain_dist"]), 4),
                "grid_elev_mean":     round(float(r["grid_elev_mean"]), 1),
                "relief_range_m":     round(float(r["relief_range_m"]), 1),
                "landform_position":  round(float(r["landform_position"]), 3),
            })

        return {
            **source,
            "lens_id":     "terrain",
            "tolerances":  tolerances,
            "query_facets": {k: round(float(v), 2) for k, v in query.items()},
            "corpus_size": len(corpus) + (1 if exclude_idx is not None else 0),
            "eligible_count": len(ranked),
            "similar":     results,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if "conn" in locals():
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


@router.get("/whc-ecoregion-wiki", include_in_schema=False)
def whc_ecoregion_wiki(city_id: int):
    """Wikipedia summary + OneEarth link for the OneEarth ecoregion a WH city's own point falls
    in. wh_cities has no ecoregion field of its own -- the "Ecoregion" row shown in its profile
    Summary table comes from BasinATLAS's own 784-class scheme (via the city's basin), a
    different taxonomy than OneEarth's 847-class Ecoregions2017, so this resolves spatially
    (point-in-polygon against the city's own geom) rather than by name match. 246/258 cities
    resolve; the rest (mostly coastal/island) fall outside any Ecoregions2017 polygon."""
    try:
        conn = db_connect()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT e.eco_id, e.eco_name, e.oneearth_slug, w.summary, w.wiki_url
                FROM gaz.wh_cities c
                JOIN gaz."Ecoregions2017" e ON ST_Contains(e.geom, c.geom)
                LEFT JOIN public.eco_wikitext w ON w.eco_id = e.eco_id
                WHERE c.id = %s
            """, (city_id,))
            row = cur.fetchone()

            if not row:
                return {"city_id": city_id, "found": False}

            return {
                "city_id": city_id,
                "found": True,
                "eco_id": row[0],
                "eco_name": row[1],
                "oneearth_slug": row[2],
                "summary": row[3],
                "wiki_url": row[4],
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


@router.get("/societies/env-scan", include_in_schema=False)
def societies_env_scan(trait: str, value: str):
    """CITYKIN WO4 -- replaces the legacy PCA 'Basin clusters' option. `(trait, value)` -> a
    composition note (top-3 language families by name, plus soc_id lists per bucket for the
    donut's map-hover linking) and the trait's hook metadata, plus either the confirmatory
    scatter (subsistence, EA042 -- has a named theoretical correlate) or per-variable strip-plot
    ticks, one per focus society (religion, EA034 -- no hook; see
    `docs/cdop/citykin/wo4_whc-grouping.md`, `docs/edop/docsv4/wo4_EA045 -viz-change.md`).

    trait: 'subsistence' (EA042) or 'religion' (EA034) -- the tab's two wired traits, not a raw
    D-PLACE variable code. No percentile/resampling language anywhere in this payload's own
    vocabulary (Karl's standing rule, 2026-07-30: that reads as a statistical claim on a GUI page,
    never acceptable) and no family-restricted resampling (Karl + Opus, same date -- that's a
    TRACE-phase analytical question, not this descriptive screen's job).
    """
    try:
        return run_societies_env_scan(trait, value)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
