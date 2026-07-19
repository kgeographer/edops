import os
import csv
import json
import math
import ssl
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

try:
    import certifi  # type: ignore
except Exception:  # pragma: no cover
    certifi = None

load_dotenv()  # reads .env from project root

# -----------------------
# Field lookup: built once at import from edops_codebook.tsv.
# Keyed by api_key_s and api_key_u; value is {schema_key, friendly_name, source, units}.
# Used in profile_groups to generate human-readable labels.
# -----------------------

def _load_field_lookup() -> Dict[str, Dict[str, str]]:
    lookup: Dict[str, Dict[str, str]] = {}
    codebook = Path(__file__).parent.parent.parent / "documentation" / "EDOPS_variable_catalog_v0.3.tsv"
    if not codebook.exists():
        return lookup
    with codebook.open(newline="") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            source_s = row.get("basin08_col_s", "")
            source_u = row.get("basin08_col_u", "")
            meta = {
                "schema_key":    row.get("schema_key", ""),
                "friendly_name": row.get("friendly_name", ""),
                "units":         row.get("units", ""),
                "notes":         row.get("notes", ""),
            }
            api_s = (row.get("api_key_s") or "").strip()
            api_u = (row.get("api_key_u") or "").strip()
            if api_s:
                lookup[api_s] = {**meta, "source": source_s or source_u or "derived"}
            if api_u:
                lookup[api_u] = {**meta, "source": source_u or "derived",
                                 "schema_key": meta["schema_key"] + "_u",
                                 "friendly_name": meta["friendly_name"] + " (upstream)"}
    return lookup

FIELD_LOOKUP: Dict[str, Dict[str, str]] = _load_field_lookup()

_TWO_PI = 2 * math.pi
_THETA  = [_TWO_PI * m / 12 for m in range(12)]   # Jan=0 … Dec=11π/6


def _circ_stats(weights):
    """Circular mean resultant for a 12-month weight vector.
    Returns (concentration, peak_angle_rad, peak_month_continuous) or (None,None,None).
    """
    total = sum(weights)
    if total == 0:
        return None, None, None
    Rx = sum(w * math.cos(t) for w, t in zip(weights, _THETA)) / total
    Ry = sum(w * math.sin(t) for w, t in zip(weights, _THETA)) / total
    concentration = math.sqrt(Rx ** 2 + Ry ** 2)
    angle         = math.atan2(Ry, Rx)
    peak_month    = (angle / _TWO_PI * 12) % 12
    return concentration, angle, peak_month


def _seasonality_indices(pre_monthly, tmp_monthly):
    """Compute six scalar seasonality indices from monthly precip and temp arrays.
    Returns a dict; all values None if inputs are missing or malformed.
    """
    _none = {k: None for k in (
        "pre_concentration", "pre_peak_month",
        "tmp_concentration", "tmp_peak_month",
        "seas_phase_offset", "tmp_seas_amp",
    )}
    if not pre_monthly or not tmp_monthly:
        return _none
    pre = [float(v) for v in pre_monthly]
    tmp = [float(v) for v in tmp_monthly]
    if len(pre) != 12 or len(tmp) != 12:
        return _none

    pre_conc, pre_angle, pre_peak = _circ_stats(pre)

    tmp_min = min(tmp)
    tmp_conc, tmp_angle, tmp_peak = _circ_stats([v - tmp_min for v in tmp])

    if pre_angle is not None and tmp_angle is not None:
        delta  = abs(pre_angle - tmp_angle)
        delta  = min(delta, _TWO_PI - delta)
        offset = delta / _TWO_PI * 12
    else:
        offset = None

    return {
        "pre_concentration": pre_conc,
        "pre_peak_month":    pre_peak,
        "tmp_concentration": tmp_conc,
        "tmp_peak_month":    tmp_peak,
        "seas_phase_offset": offset,
        "tmp_seas_amp":      max(tmp) - min(tmp),
    }

_VIEW_FOR_LEVEL = {
    8: "v_basin08_persist_rev2",
    6: "v_basin06_persist_rev2",
}

SIGNATURE_SQL_TMPL = """
SELECT
  id,
  zone_id,
  zone_name,
  strata_id,
  strata_code,
  land_cover_id,
  land_cover_name,

  -- A: Physiographic bedrock
  elev_min,
  elev_max,
  slope_avg,
  slope_upstream,
  stream_gradient,
  lithology,
  lith_class,
  karst,
  karst_upstream,

  -- B: Hydro-climatic baselines
  discharge_yr,
  discharge_min,
  discharge_max,
  river_area,
  river_area_upstream,
  runoff,
  gw_table_depth,
  pnveg_id,
  pnv_majority,
  pnv_shares,
  pct_clay,
  pct_silt,
  pct_sand,
  pct_clay_upstream,
  pct_silt_upstream,
  pct_sand_upstream,
  wet_pct_grp1,
  wet_pct_grp2,
  wet_pct_grp1_upstream,
  wet_pct_grp2_upstream,
  wetland_class,

  -- C: Bioclimatic proxies
  pre_mm_monthly,
  tmp_dc_monthly,
  temp_yr,
  temp_min,
  temp_max,
  temp_yr_upstream,
  precip_yr,
  precip_yr_upstream,
  aridity,
  aridity_upstream,
  permafrost_extent,
  biome_id,
  biome,
  eco_id,
  ecoregion,
  freshwater_type,
  freshwater_ecoregion_class,
  freshwater_ecoregion_name,

  -- D: Anthropocene markers
  reservoir_vol,
  cropland_extent,
  cropland_extent_upstream,
  pasture_extent,
  pasture_extent_upstream,
  pop_density,
  human_footprint_09,
  human_footprint_09_upstream,
  gdp_avg,
  human_dev_idx,

  -- E: Coastality
  dist_sink,
  endorheic,
  coast_flag,

  -- Scale context
  up_area,

  -- geometry handling: return a GeoJSON string (good for Leaflet)
  ST_AsGeoJSON(geom, 6) AS geom_geojson
FROM public.{view}
WHERE ST_Covers(
  geom,
  ST_SetSRID(ST_MakePoint(%(lon)s, %(lat)s), 4326)
)
ORDER BY ST_Area(geom::geography) ASC
LIMIT 1;
"""

# -----------------------
# Profile presentation metadata (pilot)
# -----------------------

PROFILE_GROUPS: Dict[str, Dict[str, Any]] = {
    "A": {
        "label": "Physiographic bedrock",
        "fields": [
            "elev_min",
            "elev_max",
            "slope_avg",
            "slope_upstream",
            "stream_gradient",
            "lith_class",
            "karst",
            "karst_upstream",
        ],
    },
    "B": {
        "label": "Hydro-climatic baselines",
        "fields": [
            "runoff",
            "discharge_yr",
            "discharge_min",
            "discharge_max",
            "river_area",
            "river_area_upstream",
            "gw_table_depth",
            "pnv_majority",
            "pnv_shares",
            "pct_clay",
            "pct_silt",
            "pct_sand",
            "pct_clay_upstream",
            "pct_silt_upstream",
            "pct_sand_upstream",
            "wet_pct_grp1",
            "wet_pct_grp2",
            "wet_pct_grp1_upstream",
            "wet_pct_grp2_upstream",
            "wetland_class",
        ],
    },
    "C": {
        "label": "Bioclimatic proxies",
        "fields": [
            "temp_yr",
            "temp_min",
            "temp_max",
            "temp_yr_upstream",
            "precip_yr",
            "precip_yr_upstream",
            "aridity",
            "aridity_upstream",
            "permafrost_extent",
            "biome",
            "ecoregion",
            "freshwater_ecoregion_class",
            "freshwater_ecoregion_name",
        ],
    },
    "D": {
        "label": "Anthropocene markers",
        "fields": [
            "pop_density",
            "human_footprint_09",
            "human_footprint_09_upstream",
            "cropland_extent",
            "cropland_extent_upstream",
            "pasture_extent",
            "pasture_extent_upstream",
            "reservoir_vol",
            "gdp_avg",
            "human_dev_idx",
        ],
    },
    "E": {
        "label": "Coastality",
        "fields": [
            "dist_sink",
            "endorheic",
            "coast_flag",
        ],
    },
}

# Proposed “top summary” (pilot): quick-read fields that usually explain the setting best.
# UI can render this as a compact list above accordions.
PROFILE_SUMMARY: list[Dict[str, str]] = [
    {"key": "ecoregion", "label": "Ecoregion"},
    {"key": "zone_name", "label": "Bioclimate zone"},
    {"key": "strata_code", "label": "Bioclimate stratum"},
    {"key": "land_cover_name", "label": "Land cover"},
    {"key": "elev_point", "label": "Elevation (point, m)"},
    {"key": "elev_min", "label": "Elevation min (basin, m)"},
    {"key": "elev_max", "label": "Elevation max (basin, m)"},
    {"key": "relief_position", "label": "Relief position (0–1)"},
    {"key": "runoff", "label": "Runoff (mm/yr)"},
    {"key": "discharge_yr", "label": "Discharge (m³/s, yr)"},
    {"key": "pop_density", "label": "Population density"},
]

# -----------------------
# Elevation provider (external, swappable)
# Pattern B: try OpenTopoData (mapzen) first, then Open-Meteo elevation API.
# -----------------------

# Very small in-process cache (per worker) to avoid repeated lookups.
# Key is rounded (lat, lon) to 5 decimals (~1m-2m at equator in lat; good enough for caching).
_ELEV_CACHE: Dict[Tuple[float, float], Dict[str, Any]] = {}
_ELEV_CACHE_MAX = 512


def _cache_get(lat: float, lon: float) -> Optional[Dict[str, Any]]:
    key = (round(float(lat), 5), round(float(lon), 5))
    return _ELEV_CACHE.get(key)


def _cache_set(lat: float, lon: float, val: Dict[str, Any]) -> None:
    key = (round(float(lat), 5), round(float(lon), 5))
    if key in _ELEV_CACHE:
        _ELEV_CACHE[key] = val
        return
    if len(_ELEV_CACHE) >= _ELEV_CACHE_MAX:
        # Drop an arbitrary item (good enough for a pilot)
        _ELEV_CACHE.pop(next(iter(_ELEV_CACHE)))
    _ELEV_CACHE[key] = val


def _http_get_json(url: str, timeout_s: float = 4.0) -> Dict[str, Any]:
    req = Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "edop-pilot/0.1",
        },
        method="GET",
    )

    # Some environments (notably minimal Linux images) lack CA certificates,
    # causing CERTIFICATE_VERIFY_FAILED. Prefer certifi's bundle when available.
    # For local/dev emergency only, set EDOP_SSL_NO_VERIFY=1 to bypass verification.
    no_verify = os.getenv("EDOP_SSL_NO_VERIFY", "0") in ("1", "true", "True", "yes", "YES")

    if no_verify:
        ctx = ssl._create_unverified_context()
    else:
        if certifi is not None:
            ctx = ssl.create_default_context(cafile=certifi.where())
        else:
            ctx = ssl.create_default_context()

    with urlopen(req, timeout=timeout_s, context=ctx) as resp:
        data = resp.read().decode("utf-8")
        return json.loads(data)


def _elev_opentopodata_mapzen(lat: float, lon: float) -> Dict[str, Any]:
    # OpenTopoData uses locations=lat,lon
    qs = urlencode({"locations": f"{lat},{lon}"})
    url = f"https://api.opentopodata.org/v1/mapzen?{qs}"
    payload = _http_get_json(url)

    if payload.get("status") != "OK":
        raise RuntimeError(payload.get("error") or f"OpenTopoData status={payload.get('status')}")

    results = payload.get("results") or []
    if not results:
        raise RuntimeError("OpenTopoData returned no results")

    elev = results[0].get("elevation")
    if elev is None:
        raise RuntimeError("OpenTopoData result missing elevation")

    return {
        "elev_point": float(elev),
        "elev_source": "opentopodata",
        "elev_dataset": "mapzen",
        "elev_resolution_m": 30,
    }


def _elev_open_meteo(lat: float, lon: float) -> Dict[str, Any]:
    # Open-Meteo Elevation API uses latitude=..&longitude=..
    qs = urlencode({"latitude": str(lat), "longitude": str(lon)})
    url = f"https://api.open-meteo.com/v1/elevation?{qs}"
    payload = _http_get_json(url)

    elev = None
    # API commonly returns: {"elevation": [..], "latitude": [..], "longitude": [..]}
    if isinstance(payload.get("elevation"), list) and payload["elevation"]:
        elev = payload["elevation"][0]
    elif payload.get("elevation") is not None:
        elev = payload.get("elevation")

    if elev is None:
        raise RuntimeError("Open-Meteo elevation missing in response")

    return {
        "elev_point": float(elev),
        "elev_source": "open-meteo",
        "elev_dataset": "copernicus-dem-glo-90-2021",
        "elev_resolution_m": 90,
    }


def get_elevation_point(lat: float, lon: float) -> Dict[str, Any]:
    """Return elevation metadata dict.

    Always returns a dict with keys:
      - elev_point (float) when available else None
      - elev_source, elev_dataset, elev_resolution_m when available
      - elev_error when both providers fail

    Pattern B fallback: OpenTopoData(mapzen) -> Open-Meteo elevation.
    """
    cached = _cache_get(lat, lon)
    if cached is not None:
        return cached

    last_err: Optional[str] = None

    # Provider 1: OpenTopoData /mapzen (~30m)
    try:
        val = _elev_opentopodata_mapzen(lat, lon)
        _cache_set(lat, lon, val)
        return val
    except (HTTPError, URLError, TimeoutError, ValueError, RuntimeError) as e:
        last_err = f"opentopodata: {e}"

    # Provider 2: Open-Meteo elevation (Copernicus GLO-90)
    try:
        val = _elev_open_meteo(lat, lon)
        _cache_set(lat, lon, val)
        return val
    except (HTTPError, URLError, TimeoutError, ValueError, RuntimeError) as e:
        last_err = (last_err + "; " if last_err else "") + f"open-meteo: {e}"

    val = {
        "elev_point": None,
        "elev_error": last_err or "elevation lookup failed",
    }
    _cache_set(lat, lon, val)
    return val


def get_signature(
    lat: float,
    lon: float,
    level: int = 8,
    flat: bool = False,
) -> Dict[str, Any] | None:
    """Return a single basin signature dict for (lat, lon), or None if no basin covers point.

    When flat=False (default): response includes profile_groups (nested band structure)
    but not raw flat field values. When flat=True: response includes flat field values
    but omits profile_groups; Band T temporal data appears at key "temporal" instead.

    Connection parameters are read from environment variables (typically via a .env file):
      DB_NAME, DB_USER, DB_HOST, DB_PORT, and optionally DB_PASSWORD.

    Notes:
    - Uses ST_Covers exactly as your SQL does.
    - Orders by smallest area_km2 to pick the smallest containing basin when multiple match.
    - Returns geom as a GeoJSON string in 'geom_geojson' (Leaflet-friendly).
    """

    conn_kwargs = dict(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        password=os.getenv("DB_PASSWORD") or os.getenv("PGPASSWORD") or None,
    )

    # Drop None values so psycopg/libpq can fall back to defaults / .pgpass when appropriate
    conn_kwargs = {k: v for k, v in conn_kwargs.items() if v not in (None, "")}

    view = _VIEW_FOR_LEVEL.get(level, "v_basin08_persist_rev1")
    sql = SIGNATURE_SQL_TMPL.format(view=view)

    with psycopg.connect(**conn_kwargs, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, {"lat": lat, "lon": lon})
            row = cur.fetchone()
            if not row:
                return None
            sig = dict(row)

            # Add point elevation via external providers (fallback chain)
            try:
                elev = get_elevation_point(lat=lat, lon=lon)
            except Exception as e:
                elev = {"elev_point": None, "elev_error": str(e)}
            sig.update(elev)

            # Derived relief metrics (requires elev_point + basin elev_min/elev_max)
            try:
                elev_point = sig.get("elev_point")
                elev_min = sig.get("elev_min")
                elev_max = sig.get("elev_max")

                if elev_point is None or elev_min is None or elev_max is None:
                    sig["relief_range_m"] = None
                    sig["relief_position"] = None
                else:
                    elev_point_f = float(elev_point)
                    elev_min_f = float(elev_min)
                    elev_max_f = float(elev_max)
                    relief_range = elev_max_f - elev_min_f

                    sig["relief_range_m"] = relief_range if relief_range > 0 else None

                    if relief_range > 0:
                        pos = (elev_point_f - elev_min_f) / relief_range
                        # Clamp to [0, 1] to absorb minor inconsistencies across datasets/resolution
                        if pos < 0:
                            pos = 0.0
                        elif pos > 1:
                            pos = 1.0
                        sig["relief_position"] = pos
                    else:
                        sig["relief_position"] = None
            except Exception:
                sig["relief_range_m"] = None
                sig["relief_position"] = None

            # -----------------------
            # Seasonality indices (derived from monthly arrays in rev2 views)
            # -----------------------
            pre_monthly = sig.get("pre_mm_monthly")
            tmp_monthly = sig.get("tmp_dc_monthly")
            if pre_monthly is not None:
                pre_monthly = list(pre_monthly)
            if tmp_monthly is not None:
                tmp_monthly = list(tmp_monthly)
            seas = _seasonality_indices(pre_monthly, tmp_monthly)
            sig.update(seas)

            # -----------------------
            # Pilot payload helpers for UI rendering (no UI changes required yet)
            # -----------------------

            # profile_summary: ordered list of {key,label,value} using PROFILE_SUMMARY
            summary_items: list[Dict[str, Any]] = []
            for spec in PROFILE_SUMMARY:
                k = spec["key"]
                if k in sig:
                    summary_items.append({
                        "key": k,
                        "label": spec["label"],
                        "value": sig.get(k),
                    })

            # profile_groups: {A:{label,items:[{key,label,value}...]}, ...}
            grouped: Dict[str, Any] = {}
            for gcode, gspec in PROFILE_GROUPS.items():
                items: list[Dict[str, Any]] = []
                for k in gspec["fields"]:
                    if k in sig:
                        meta = FIELD_LOOKUP.get(k, {})
                        sk = meta.get("schema_key") or k
                        src = meta.get("source", "")
                        label = f"{sk} ({src})" if src else sk
                        items.append({
                            "key": k,
                            "label": label,
                            "value": sig.get(k),
                        })
                grouped[gcode] = {
                    "label": gspec["label"],
                    "items": items,
                }

            out: Dict[str, Any] = {
                # Seasonality arrays + derived scalar indices (Band C; top-level only)
                "pre_mm_monthly":    pre_monthly,
                "tmp_dc_monthly":    tmp_monthly,
                "pre_concentration": seas.get("pre_concentration"),
                "pre_peak_month":    seas.get("pre_peak_month"),
                "tmp_concentration": seas.get("tmp_concentration"),
                "tmp_peak_month":    seas.get("tmp_peak_month"),
                "seas_phase_offset": seas.get("seas_phase_offset"),
                "tmp_seas_amp":      seas.get("tmp_seas_amp"),
                # Core fields
                "id":           sig.get("id"),
                "eco_id":       sig.get("eco_id"),
                "up_area":      sig.get("up_area"),
                "geom_geojson": sig.get("geom_geojson"),
                "elev_point":        sig.get("elev_point"),
                "elev_source":       sig.get("elev_source"),
                "elev_dataset":      sig.get("elev_dataset"),
                "elev_resolution_m": sig.get("elev_resolution_m"),
                "relief_range_m":  sig.get("relief_range_m"),
                "relief_position": sig.get("relief_position"),
                "profile_summary": summary_items,
            }
            if "elev_error" in sig:
                out["elev_error"] = sig["elev_error"]

            if flat:
                for _gcode, gdata in grouped.items():
                    for item in gdata.get("items", []):
                        out[item["key"]] = item["value"]
            else:
                out["profile_groups"] = grouped

            return out


def main() -> None:
    # Your test coordinates (note: lon, lat order matches your SQL)
    lat = 16.76618535
    lon = -3.00777252

    sig = get_signature(lat=lat, lon=lon)

    if sig is None:
        print("No basin found covering that point.")
        return

    print(json.dumps(sig, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
