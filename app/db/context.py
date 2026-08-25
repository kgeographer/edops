"""
Context index — loaded once at startup, queried per request.

Supports WO5's Context tab: a basin's position against a stated reference
population, reported two ways per variable — percentile against all basins at
the level, and percentile against basins within a chosen radius of the query
point. No ranking, no candidate list, no compensating composite distance
(contrast with the similarity lenses in seasonality.py).

Variable set (locked WO5 Part B design decision, 2026-07-21): seven rows,
chosen to be readable by a historian without a glossary and to cover the
dimensions WO4/WO5 diagnostics actually exercised (container problem →
elevation; composite-metric bundling → temperature split into level + range).

  pre_mm_syr    — mean annual precipitation (mm/yr)
  tmp_dc_syr    — mean annual temperature (°C; stored ×10, divide by 10)
  tmp_seas_amp  — seasonal temperature range (°C; derived from monthly array,
                  same computation as seasonality.py)
  ele_mt_sav    — mean elevation (m). Catalog status is "planned" (never wired
                  into load_catalog / basin08_scores) — computed independently
                  here; see docs/design/deferred_items_register.md "Catalog
                  housekeeping" for the catalog-side gap.
  slp_dg_sav    — mean slope (degrees; stored ×10, divide by 10) — relief/roughness proxy
  ari_ix_sav    — aridity index (P/PET ×100); log1p-transformed before ranking
                  per the catalog's position_method for this variable
  run_mm_syr    — annual runoff (mm/yr)

Percentile method mirrors scripts/edop/areas/engine.py's rank_expr/PERCENT_RANK
semantics (percentile = rank / (n-1) * 100, ties averaged, NoData excluded from
the ranking population) but computed in numpy at startup/request time rather
than via SQL, so a within-radius percentile costs no DB round-trip.

Basin representative point for radius membership: ST_PointOnSurface, not
ST_Centroid — a plain centroid can fall outside a concave/crescent-shaped
basin polygon (the exact WO17/WO18 failure mode: centroid-outside-polygon
silently resolving to the wrong basin). The query point itself is always the
caller's exact lat/lon, never a basin representative point.
"""
import logging
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Variable registry
# ---------------------------------------------------------------------------

# variable_key -> (label, unit, transform)
# transform: None (plain percentile) or "log1p" (log1p before ranking, per
# the catalog's position_method for skewed variables).
CONTEXT_VARIABLES: Dict[str, Dict[str, Any]] = {
    "pre_mm_syr":   {"label": "Mean annual precipitation", "unit": "mm/yr", "transform": None},
    "tmp_dc_syr":   {"label": "Mean annual temperature",   "unit": "°C",    "transform": None},
    "tmp_seas_amp": {"label": "Seasonal temperature range", "unit": "°C",   "transform": None},
    "ele_mt_sav":   {"label": "Mean elevation",            "unit": "m",     "transform": None},
    "slp_dg_sav":   {"label": "Mean slope",                "unit": "°",     "transform": None},
    "ari_ix_sav":   {"label": "Aridity index",              "unit": "P/PET ×100", "transform": "log1p"},
    "run_mm_syr":   {"label": "Annual runoff",              "unit": "mm/yr", "transform": None},
}

# Raw BasinATLAS scalar columns needed (same names on basin06/basin08).
# scale: applied after load (tmp_dc_syr stored ×10).
_SCALAR_COLS: Dict[str, float] = {
    "pre_mm_syr": 1.0,
    "tmp_dc_syr": 0.1,
    "ele_mt_sav": 1.0,
    "slp_dg_sav": 0.1,
    "ari_ix_sav": 1.0,
    "run_mm_syr": 1.0,
}

_LEVEL_SOURCES: Dict[int, Tuple[str, str]] = {
    6: ("public.v_basin06_persist_rev2", "public.basin06"),
    8: ("public.v_basin08_persist_rev2", "public.basin08"),
}

_EARTH_RADIUS_KM = 6371.0088

# _INDEX[level] = {"hybas_ids", "lat", "lon", "values": {var: raw_array},
#                   "global_pctl": {var: pctl_array}}
_INDEX: Dict[int, Dict[str, Any]] = {6: {}, 8: {}}


def _rank_percentile(values: np.ndarray, transform: Optional[str]) -> np.ndarray:
    """PERCENT_RANK-equivalent: percentile = rank / (n_valid - 1) * 100, ties
    averaged, NaN excluded from both the ranking population and the output."""
    valid_mask = ~np.isnan(values)
    n_valid = int(valid_mask.sum())
    pctl = np.full(values.shape, np.nan)
    if n_valid < 2:
        return pctl

    v = values[valid_mask].astype(float)
    if transform == "log1p":
        v = np.log1p(np.clip(v, 0, None))

    # average rank under ties, then normalize to 0-100 over n_valid-1
    order = np.argsort(v, kind="mergesort")
    ranks = np.empty(n_valid, dtype=float)
    ranks[order] = np.arange(n_valid, dtype=float)
    # tie-average: for each unique value, assign the mean rank of its group
    sorted_v = v[order]
    sorted_ranks = ranks[order]
    i = 0
    while i < n_valid:
        j = i
        while j + 1 < n_valid and sorted_v[j + 1] == sorted_v[i]:
            j += 1
        if j > i:
            sorted_ranks[i:j + 1] = sorted_ranks[i:j + 1].mean()
        i = j + 1
    ranks[order] = sorted_ranks

    pctl[valid_mask] = ranks / (n_valid - 1) * 100.0
    return pctl


def load_context_index(conn, level: int = 6) -> None:
    """Load basin positions, raw variable values, and precomputed global
    percentiles for a given level. Call once per level at startup."""
    if level not in _LEVEL_SOURCES:
        raise ValueError(f"Unsupported level: {level}. Supported: {list(_LEVEL_SOURCES)}")

    arr_view, scalars_table = _LEVEL_SOURCES[level]

    import pandas as pd
    import warnings
    warnings.filterwarnings("ignore", message="pandas only supports SQLAlchemy")

    try:
        cols_sql = ", ".join(_SCALAR_COLS)
        with conn.cursor() as cur:
            cur.execute(
                f"SELECT hybas_id, {cols_sql}, "
                f"ST_Y(ST_PointOnSurface(geom)) AS lat, "
                f"ST_X(ST_PointOnSurface(geom)) AS lon "
                f"FROM {scalars_table}"
            )
            rows = cur.fetchall()
            colnames = [d.name for d in cur.description]

        df = pd.DataFrame(rows, columns=colnames)
        df["hybas_id"] = df["hybas_id"].astype(np.int64)

        arr = pd.read_sql(f"SELECT hybas_id, tmp_dc_monthly FROM {arr_view}", conn)
        arr["hybas_id"] = arr["hybas_id"].astype(np.int64)
        df = df.merge(arr, on="hybas_id", how="left")

        hybas_ids = df["hybas_id"].to_numpy()
        lat = df["lat"].to_numpy(dtype=float)
        lon = df["lon"].to_numpy(dtype=float)

        values: Dict[str, np.ndarray] = {}
        for col, scale in _SCALAR_COLS.items():
            v = df[col].to_numpy(dtype=float)
            v[v == -9999 * scale] = np.nan
            v = v * scale
            values[col] = v

        TMP = np.array(df["tmp_dc_monthly"].tolist(), dtype=float)
        values["tmp_seas_amp"] = TMP.max(axis=1) - TMP.min(axis=1)

        global_pctl = {
            var: _rank_percentile(values[var], spec["transform"])
            for var, spec in CONTEXT_VARIABLES.items()
        }

        _INDEX[level] = {
            "hybas_ids": hybas_ids,
            "lat": lat,
            "lon": lon,
            "values": values,
            "global_pctl": global_pctl,
        }
        logger.info("L%d context index ready: %d basins, %d variables",
                    level, len(hybas_ids), len(CONTEXT_VARIABLES))

    except Exception:
        logger.exception("context index (level=%d) failed to load", level)


def _haversine_km(lat1, lon1, lat2, lon2) -> np.ndarray:
    lat1, lon1, lat2, lon2 = map(np.radians, (lat1, lon1, lat2, lon2))
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    return 2 * _EARTH_RADIUS_KM * np.arcsin(np.sqrt(np.clip(a, 0, 1)))


def _load_level(level: int) -> Dict[str, Any]:
    idx = _INDEX.get(level)
    if not idx or idx.get("hybas_ids") is None:
        raise RuntimeError(f"Context index (level={level}) not loaded — startup may have failed")
    return idx


def _radius_mask(idx: Dict[str, Any], query_lat: float, query_lon: float,
                  radius_km: float) -> np.ndarray:
    """Boolean mask over idx['hybas_ids']: basins within radius_km of the query
    point (caller's exact coordinates, not a basin representative point)."""
    dist = _haversine_km(query_lat, query_lon, idx["lat"], idx["lon"])
    return dist <= radius_km


def get_context(query_hybas_id: int, query_lat: float, query_lon: float,
                 level: int, radius_km: float) -> Dict[str, Any]:
    """Per-variable value, global percentile, within-radius percentile, and
    the radius basin count, for the basin containing (query_lat, query_lon).

    query_lat/query_lon are the caller's exact coordinates — not a basin
    representative point — used as the radius origin. Other basins use
    ST_PointOnSurface (see module docstring) to decide radius membership.

    Raises RuntimeError if index not loaded; ValueError if the basin isn't
    in the index.
    """
    idx = _load_level(level)

    hybas_ids = idx["hybas_ids"]
    hits = np.where(hybas_ids == int(query_hybas_id))[0]
    if len(hits) == 0:
        raise ValueError(f"Basin {query_hybas_id} not in context index (level={level})")
    q_idx = int(hits[0])

    in_radius = _radius_mask(idx, query_lat, query_lon, radius_km)
    radius_count = int(in_radius.sum())

    rows = []
    for var, spec in CONTEXT_VARIABLES.items():
        raw = idx["values"][var]
        value = raw[q_idx]
        global_pctl = idx["global_pctl"][var][q_idx]

        radius_vals = np.where(in_radius, raw, np.nan)
        radius_pctl_all = _rank_percentile(radius_vals, spec["transform"])
        radius_pctl = radius_pctl_all[q_idx]

        rows.append({
            "variable":         var,
            "label":            spec["label"],
            "unit":             spec["unit"],
            "value":            None if np.isnan(value) else round(float(value), 3),
            "global_percentile": None if np.isnan(global_pctl) else round(float(global_pctl), 1),
            "radius_percentile": None if np.isnan(radius_pctl) else round(float(radius_pctl), 1),
        })

    return {
        "level":         level,
        "query_hybas_id": int(hybas_ids[q_idx]),
        "radius_km":      radius_km,
        "radius_count":   radius_count,
        "rows":           rows,
    }


def get_context_population(query_lat: float, query_lon: float,
                            level: int, radius_km: float) -> Dict[str, Any]:
    """Raw per-basin values for every CONTEXT_VARIABLE, for every basin within
    radius_km of the query point — the population the Context tab's map
    choropleths. Fetched once per radius/level/location change; the caller
    switches which variable is painted locally without refetching (WO5 Part C:
    "selecting a table row sets the map variable" — no separate refetch).

    Values are raw, not percentiles — the map's own color ramp is scaled to
    this population's min/max client-side, per WO5's "the variable's own
    distribution within the shown population, not a global ramp" proviso.
    """
    idx = _load_level(level)
    in_radius = _radius_mask(idx, query_lat, query_lon, radius_km)
    hybas_ids = idx["hybas_ids"][in_radius]

    # Mask each variable's array once (not per-basin) before assembling rows.
    masked = {var: idx["values"][var][in_radius] for var in CONTEXT_VARIABLES}

    basins = []
    for i, hid in enumerate(hybas_ids):
        row = {"hybas_id": int(hid)}
        for var in CONTEXT_VARIABLES:
            v = masked[var][i]
            row[var] = None if np.isnan(v) else round(float(v), 3)
        basins.append(row)

    return {
        "level":       level,
        "radius_km":   radius_km,
        "radius_count": len(basins),
        "basins":      basins,
    }
