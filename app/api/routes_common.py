"""
app/api/routes_common.py
-------------------------
Routes and helpers shared by more than one page (Sandbox, Workbench, Explorer,
Cliopatria viewer). See docs/edop/routes_audit.txt for the classification this
split is based on — re-run that audit after adding/removing/renaming any route
before assuming a helper is still page-scoped.
"""
import json
import ssl
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import certifi
from fastapi import APIRouter, HTTPException

from app.db.signature import get_signature
from app.db.temporal import get_temporal_context
from app.db.hyde import get_hyde_land_use
from app.db.connection import db_connect
from app.settings import settings

router = APIRouter(prefix="/api", tags=["api"])


@router.get("/health")
def health():
    return {"status": "ok"}


# -----------------------
# WHG suggest/entity helpers — shared by Sandbox's /whg/suggest and
# Workbench's /resolve. (WHG reconcile+extend helpers, used only by
# /whg-reconcile, live in routes_workbench.py instead.)
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

    Response
    --------
    Default (flat=False): basin identity/geometry fields (id, hybas_id, geom_geojson, ...) plus
    "profile_groups": {"<band letter>": {"label": str, "items": [{"key", "label", "value"}, ...]}}
    for each requested band. Band T (if requested) nests under profile_groups["T"] instead, with
    its own "_status" ("ok" | "not_requested" | "error").

    flat=True: the same identity/geometry fields plus every variable as a top-level key (no
    profile_groups nesting); Band T appears at top-level key "temporal" instead.

    Full variable inventory (what each band/key means): see the Codebook (/docs/codebook/).
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


# -----------------------
# Explorer: codebook metadata — shared by /explorer/values (here) and the
# Explorer-only routes (variables/categorical/lisa/scatter) still in routes.py
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
    cb_path = Path(__file__).resolve().parents[2] / "documentation" / "EDOPS_variable_catalog_v0.4.tsv"
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


# -----------------------
# HYDE epoch-max metadata — shared by Cliopatria's /explorer/hyde-epoch-max
# and Sandbox's /hyde/values (still in routes.py)
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


# -----------------------
# Cliopatria polities — shared search/slices/geom (period/period-years/seshat
# are Cliopatria-viewer-only, see routes_cliopatria.py)
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
