"""
Similarity lens registry — loaded once at startup, queried per request.

Two active Climate sub-lenses are precomputed from L06 and L08 monthly arrays and
BasinATLAS scalars at startup. Level is a parameter of index selection; no new
distance logic is needed to add a level.

Metric per lens:
  euclidean    — normalized Euclidean on z-scored variables (low inter-variable correlation)
  mahalanobis  — accounts for correlated variables (mandatory when |r| > ~0.3)

Derived variables (computed from monthly arrays; no DB column):
  a1, b1          — annual harmonic components (normalized by annual total)
  a2, b2          — semi-annual harmonic components (normalized by annual total)
  log_pre_mm_syr  — log1p(annual precip total)
  tmp_concentration, tmp_seas_amp

BasinATLAS scalar variables:
  tmp_dc_syr  — annual mean temp °C×10     (divide by 10)
  Sources: basin06 (level=6), basin08 (level=8) — same column names.
"""
import logging
import warnings
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from numpy.linalg import inv

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Lens registry
# ---------------------------------------------------------------------------

LENS_REGISTRY: Dict[str, Dict[str, Any]] = {
    "climate.precip": {
        "group":      "Climate",
        "label":      "Precipitation regime",
        # Continuous harmonic form: (a1,b1,a2,b2) capture modality naturally; log total
        # keeps magnitude separate from shape. Identities verified in WO2a to machine epsilon.
        "variables":  ["log_pre_mm_syr", "a1", "b1", "a2", "b2"],
        "metric":     "euclidean",
        "status":     "active",
        # Provisional thresholds — recalibrate against L06 CDFs in 5D z-score space (WO3)
        "thresholds": {"strict": 0.25, "moderate": 0.60, "loose": 1.20},
    },
    "climate.temp": {
        "group":      "Climate",
        "label":      "Temperature regime",
        "variables":  ["tmp_dc_syr", "tmp_seas_amp", "tmp_concentration"],
        "metric":     "mahalanobis",
        "status":     "active",
        "thresholds": {"strict": 0.25, "moderate": 0.75, "loose": 1.50},
    },
    "climate.phase": {
        # Retired in WO3. Was never one question: bundled modality (now in precip),
        # hemisphere-blind phase relation, and hemisphere-aware seasonal timing. Questions
        # 2 and 3 cannot share a lens. Analysis recorded in wo3_retire-phase.md.
        "group":  "Climate",
        "label":  "Seasonal phase",
        "status": "retired",
    },
    "terrain.*": {
        "group":  "Terrain",
        "label":  "Terrain (coming soon)",
        "status": "disabled",
    },
    "hydrology.*": {
        "group":  "Hydrology",
        "label":  "Hydrology (coming soon)",
        "status": "disabled",
    },
}

# Variables derived from monthly arrays (no basin column).
_DERIVED = {"a1", "b1", "a2", "b2", "log_pre_mm_syr", "tmp_concentration", "tmp_seas_amp"}

# ---------------------------------------------------------------------------
# Conjunction lens registry (WO6c) — the non-compensatory panel
# ---------------------------------------------------------------------------
# A lens is an ordered list of typed conditions. Membership is AND across every condition
# (non-compensatory): a basin is in the set or it is not. No composite distance, no threshold
# ladder. Each band is a declared parameter in its own units. Backbone: correlation on the raw
# twelve-value precipitation curve (WO6b). Temperature has no shape term — the curve saturates
# within hemisphere (WO6c Part D). Full schema + rationale: docs/cdop/pilot/wo6c_findings.md.
#
# This path is entirely separate from LENS_REGISTRY / find_similar (the shipped composite-distance
# panel), which stays reachable unchanged until the new panel is judged good.

# Arid gate for the shape condition only: below this annual total the monthly precipitation
# profile is noise-dominated and its correlation with anything is meaningless (WO6b Cell 1/Cell 7:
# `c[arid_mask] = -inf`). The one threshold in this project sitting in a genuine histogram trough,
# robust to ±25 mm (wo2_findings.md). Magnitude / cv / temperature conditions are unaffected —
# an arid basin has a valid total and temperature.
_THRESH_ARID = 100.0

CONJ_CONDITIONS: Dict[str, Dict[str, Any]] = {
    # precip_shape   — Pearson r of the mean-centred 12-value precip curve; cut is a declared bar.
    "precip_shape":        {"kind": "corr",     "default": 0.90},
    # precip_magnitude — annual total within a multiplicative ratio band (symmetric on log).
    "precip_magnitude":    {"kind": "ratio",    "default": 1.5},
    # precip_amplitude_cv — cv (sd/mean of the 12 values) within a per-query band. Band only,
    #   never a global scalar (explodes on dry-season zeros; WO6b Part D).
    "precip_amplitude_cv": {"kind": "cv_band",  "field": "cv",       "default": 0.15},
    # temp_level — mean of the 12 monthly temps within ±degrees.
    "temp_level":          {"kind": "abs_band", "field": "tmp_mean", "default": 3.0},
    # temp_range — seasonal amplitude (max-min monthly) within ±degrees.
    "temp_range":          {"kind": "abs_band", "field": "tmp_rng",  "default": 4.0},
}

CONJ_LENSES: Dict[str, Dict[str, Any]] = {
    "climate.precip": {
        "group": "Climate", "label": "Precipitation regime",
        "conditions": ["precip_shape", "precip_magnitude", "precip_amplitude_cv"],
        "shade_by": "precip_shape",
    },
    "climate.temp": {
        "group": "Climate", "label": "Temperature regime",
        # No shape term — temperature saturates within hemisphere (WO6c Part D). Weakest lens
        # standalone; exists mainly to compose the union.
        "conditions": ["temp_level", "temp_range"],
        "shade_by": None,
    },
    "climate.union": {
        "group": "Climate", "label": "Climate (precipitation + temperature)",
        # == the WO6b Part D validated five-condition conjunction. precip/temp are SUBSETS of this.
        "conditions": ["precip_shape", "precip_magnitude", "precip_amplitude_cv",
                       "temp_level", "temp_range"],
        "shade_by": "precip_shape",
    },
}

# BasinATLAS scalar variables needed by active lenses.
# Maps variable name → (column_name, scale_factor).
# scale_factor applied after load (tmp_dc_* stored ×10).
# Column names are identical in basin06 and basin08.
_SCALAR_SOURCES: Dict[str, Tuple[str, float]] = {
    "tmp_dc_syr": ("tmp_dc_syr", 0.1),
}

# Level → (monthly-arrays view, scalars table)
_LEVEL_SOURCES: Dict[int, Tuple[str, str]] = {
    6: ("public.v_basin06_persist_rev2", "public.basin06"),
    8: ("public.v_basin08_persist_rev2", "public.basin08"),
}

# ---------------------------------------------------------------------------
# Module-level state keyed by level (None until load_similarity_index called)
# ---------------------------------------------------------------------------

_TWO_PI    = 2 * np.pi
_THETA     = np.array([_TWO_PI * m / 12 for m in range(12)])   # annual
_THETA2    = np.array([_TWO_PI * m / 6  for m in range(12)])   # semi-annual

# _INDEX[level] = {"hybas_ids": ndarray | None, "lens_state": dict}
_INDEX: Dict[int, Dict[str, Any]] = {
    6: {"hybas_ids": None, "lens_state": {}},
    8: {"hybas_ids": None, "lens_state": {}},
}

# Keep legacy module-level names as aliases for backwards compatibility
# (routes.py and tests may reference _HYBAS_IDS / _LENS_STATE via import)
_HYBAS_IDS: Optional[np.ndarray] = None
_LENS_STATE: Dict[str, Dict[str, Any]] = {}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _circ_conc_angle(W: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """(N,12) weight matrix → (concentration, angle) arrays; NaN where total==0."""
    total = W.sum(axis=1, keepdims=True)
    total = np.where(total == 0, np.nan, total)
    Rx = (W * np.cos(_THETA)).sum(axis=1) / total[:, 0]
    Ry = (W * np.sin(_THETA)).sum(axis=1) / total[:, 0]
    return np.sqrt(Rx**2 + Ry**2), np.arctan2(Ry, Rx)


def _row_normalise(V: np.ndarray) -> np.ndarray:
    """Mean-centre each row, then scale to unit norm. Zero-variance rows -> NaN.

    Pearson correlation between two profiles is then a dot product of their normalised rows,
    and one profile's correlation against the whole corpus is a single matvec (WO6b Cell 4).
    """
    Vc = V - V.mean(axis=1, keepdims=True)
    with np.errstate(invalid="ignore", divide="ignore"):
        n = np.linalg.norm(Vc, axis=1, keepdims=True)
        n = np.where(n == 0, np.nan, n)
        return Vc / n


def _haversine_km(lat1: np.ndarray, lon1: np.ndarray,
                  lat2: float, lon2: float) -> np.ndarray:
    """Great-circle distance (km) from one point to arrays of points. NaN-safe."""
    R = 6371.0088
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlmb = np.radians(lon2 - lon1)
    a = np.sin(dphi / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dlmb / 2) ** 2
    return 2 * R * np.arcsin(np.sqrt(np.clip(a, 0, 1)))


def _compute_derived(PRE: np.ndarray, TMP: np.ndarray) -> Dict[str, np.ndarray]:
    """Compute all derived similarity variables from (N,12) monthly arrays.

    PRE in mm/month; TMP in °C (v_basin06_persist_rev2 already stores °C, not ×10).
    Returns dict of variable_name → (N,) array.

    Harmonic components (a1,b1,a2,b2) are normalized by annual total so they measure
    *shape* independently of *magnitude* (log_pre_mm_syr). Hyper-arid basins with zero
    annual total yield NaN — excluded from the index automatically.
    """
    total = PRE.sum(axis=1)
    # Safe denominator: zero-total basins → NaN components (excluded from index)
    with np.errstate(invalid="ignore", divide="ignore"):
        total_safe = np.where(total > 0, total, np.nan)
        # Annual harmonic (12-month period)
        a1 = (PRE * np.cos(_THETA)).sum(axis=1) / total_safe
        b1 = (PRE * np.sin(_THETA)).sum(axis=1) / total_safe
        # Semi-annual harmonic (6-month period)
        a2 = (PRE * np.cos(_THETA2)).sum(axis=1) / total_safe
        b2 = (PRE * np.sin(_THETA2)).sum(axis=1) / total_safe
        # Log total — right-skewed (range ~50–5000 mm/yr); log1p handles zeros safely
        log_pre = np.log1p(total)

    # Temperature: concentration and amplitude
    TMP_shifted = TMP - TMP.min(axis=1, keepdims=True)
    tmp_conc, _ = _circ_conc_angle(TMP_shifted)
    tmp_seas_amp = TMP.max(axis=1) - TMP.min(axis=1)

    return {
        "a1":             a1,
        "b1":             b1,
        "a2":             a2,
        "b2":             b2,
        "log_pre_mm_syr": log_pre,
        "tmp_concentration": tmp_conc,
        "tmp_seas_amp":      tmp_seas_amp,
    }


def _build_euclidean_state(X: np.ndarray) -> Dict[str, Any]:
    mask = ~np.isnan(X).any(axis=1)
    mu   = X[mask].mean(axis=0)
    sd   = X[mask].std(axis=0)
    Xz   = np.full_like(X, np.nan)
    Xz[mask] = (X[mask] - mu) / sd
    return {"metric": "euclidean", "X_raw": X, "Xz": Xz}


def _build_mahalanobis_state(X: np.ndarray) -> Dict[str, Any]:
    mask = ~np.isnan(X).any(axis=1)
    cov  = np.cov(X[mask].T)
    VI   = inv(cov)
    return {"metric": "mahalanobis", "X_raw": X, "VI": VI, "mask": mask}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_lens_registry() -> List[Dict[str, Any]]:
    """Return the public view of the lens registry (all lenses, active and disabled)."""
    return [
        {
            "lens_id":    lid,
            "group":      spec.get("group", ""),
            "label":      spec.get("label", ""),
            "status":     spec.get("status", "disabled"),
            "variables":  spec.get("variables", []),
            "metric":     spec.get("metric", ""),
            "thresholds": spec.get("thresholds", {}),
        }
        for lid, spec in LENS_REGISTRY.items()
    ]


def load_similarity_index(conn, level: int = 6) -> None:
    """Precompute all active-lens similarity state from DB for a given basin level.

    Call once per level at startup (level=6 then level=8).
    Level selects the source view and scalars table; distance logic is unchanged.
    """
    global _HYBAS_IDS, _LENS_STATE

    if level not in _LEVEL_SOURCES:
        raise ValueError(f"Unsupported level: {level}. Supported: {list(_LEVEL_SOURCES)}")

    arr_view, scalars_table = _LEVEL_SOURCES[level]

    import pandas as pd

    try:
        active = {lid: spec for lid, spec in LENS_REGISTRY.items()
                  if spec.get("status") == "active"}

        # ── Monthly arrays → derived variables ──────────────────────────────
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message="pandas only supports SQLAlchemy")
            arr = pd.read_sql(
                f"SELECT hybas_id, pre_mm_monthly, tmp_dc_monthly FROM {arr_view}",
                conn,
            )

        hybas_ids = arr["hybas_id"].to_numpy().astype(np.int64)
        PRE = np.array(arr["pre_mm_monthly"].tolist(), dtype=float)
        TMP = np.array(arr["tmp_dc_monthly"].tolist(), dtype=float)  # already °C

        derived = _compute_derived(PRE, TMP)

        # ── BasinATLAS scalars needed by any active lens ─────────────────────
        needed_scalars = {
            v for spec in active.values()
            for v in spec.get("variables", [])
            if v not in _DERIVED
        }

        scalars: Dict[str, np.ndarray] = {}
        if needed_scalars:
            col_map = {v: _SCALAR_SOURCES[v] for v in needed_scalars if v in _SCALAR_SOURCES}
            cols_sql = ", ".join(col for col, _ in col_map.values())
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", message="pandas only supports SQLAlchemy")
                sc = pd.read_sql(
                    f"SELECT hybas_id, {cols_sql} FROM {scalars_table}",
                    conn,
                )
            sc["hybas_id"] = sc["hybas_id"].astype(np.int64)

            # Align to the monthly-array row order via merge
            order = pd.DataFrame({"hybas_id": hybas_ids})
            sc = order.merge(sc, on="hybas_id", how="left")

            for var_name, (col, scale) in col_map.items():
                vals = sc[col].to_numpy(dtype=float)
                if scale != 1.0:
                    vals = vals * scale
                # Mask NoData sentinel
                vals[vals == -9999 * scale] = np.nan
                scalars[var_name] = vals

        # ── Per-lens state ───────────────────────────────────────────────────
        lens_state: Dict[str, Dict[str, Any]] = {}
        for lid, spec in active.items():
            vars_ = spec["variables"]
            cols  = []
            for v in vars_:
                if v in _DERIVED:
                    cols.append(derived[v])
                else:
                    cols.append(scalars.get(v, np.full(len(hybas_ids), np.nan)))

            X = np.column_stack(cols)    # (N, k)

            if spec["metric"] == "euclidean":
                state = _build_euclidean_state(X)
            else:
                state = _build_mahalanobis_state(X)

            n_valid = int((~np.isnan(X).any(axis=1)).sum())
            state["variables"] = vars_
            lens_state[lid]    = state
            logger.info("L%d lens %-20s ready: %d/%d valid basins",
                        level, lid, n_valid, len(hybas_ids))

        # ── Conjunction index (WO6c): raw-curve state for the non-compensatory panel ──
        # Reuses the already-loaded PRE/TMP arrays; adds one representative-point query.
        try:
            pre_total = PRE.sum(axis=1)
            with np.errstate(invalid="ignore", divide="ignore"):
                pre_mean = PRE.mean(axis=1)
                cv = PRE.std(axis=1) / np.where(pre_mean > 0, pre_mean, np.nan)
            tmp_mean = TMP.mean(axis=1)
            tmp_rng  = TMP.max(axis=1) - TMP.min(axis=1)
            Z = _row_normalise(PRE)   # mean-centred unit precip curves; flat rows -> NaN

            # Candidate universe = WO6b Cell 2 `valid`: finite curves, positive annual total,
            # and (where the temp scalar is loaded) a finite annual mean temperature.
            cvalid = (np.isfinite(PRE).all(axis=1)
                      & np.isfinite(TMP).all(axis=1)
                      & (pre_total > 0))
            if "tmp_dc_syr" in scalars:
                cvalid = cvalid & np.isfinite(scalars["tmp_dc_syr"])

            # Representative points (ST_PointOnSurface, per the WO17/18 centroid-outside precedent)
            # for spatial-spread reporting only — not basin resolution.
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", message="pandas only supports SQLAlchemy")
                pts = pd.read_sql(
                    f"SELECT hybas_id, ST_Y(ST_PointOnSurface(geom)) AS lat, "
                    f"ST_X(ST_PointOnSurface(geom)) AS lon FROM {scalars_table}", conn)
            pts["hybas_id"] = pts["hybas_id"].astype(np.int64)
            order = pd.DataFrame({"hybas_id": hybas_ids}).merge(pts, on="hybas_id", how="left")
            lat = order["lat"].to_numpy(dtype=float)
            lon = order["lon"].to_numpy(dtype=float)

            _INDEX[level]["conj"] = {
                "hybas_ids": hybas_ids, "valid": cvalid, "Z": Z,
                "arid": pre_total < _THRESH_ARID,
                "pre_total": pre_total, "cv": cv,
                "tmp_mean": tmp_mean, "tmp_rng": tmp_rng,
                "lat": lat, "lon": lon,
            }
            logger.info("L%d conjunction index ready: %d/%d valid basins",
                        level, int(cvalid.sum()), len(hybas_ids))
        except Exception:
            logger.exception("conjunction index (level=%d) failed to load", level)
            _INDEX[level]["conj"] = None

        _INDEX[level]["hybas_ids"]  = hybas_ids
        _INDEX[level]["lens_state"] = lens_state

        # Keep legacy L06 globals in sync so existing callers are unaffected
        if level == 6:
            _HYBAS_IDS  = hybas_ids
            _LENS_STATE = lens_state

    except Exception:
        logger.exception("similarity index (level=%d) failed to load", level)


def find_similar(
    query_hybas_id: int,
    lens_id: str = "climate.precip",
    n: int = 200,
    mode: str = "threshold",
    stringency: str = "moderate",
    level: int = 6,
    filter_hybas_ids: Optional[np.ndarray] = None,
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """Rank basins by distance to the query basin under the given lens.

    level: 6 (default, L06 global index) or 8 (L08, for WH Cities corpus queries).

    mode='threshold' (default): returns all basins within the calibrated radius
      for the given stringency ('strict'/'moderate'/'loose'). Count varies.
      Thresholds are calibrated on L06; use mode='topn' for level=8.
    mode='topn': returns the n nearest basins regardless of radius.

    filter_hybas_ids: if provided, only basins in this array are considered.
      Used for corpus-restricted similarity (e.g. within the 254 WH Cities).

    Returns (query_meta, ranked):
      query_meta — lens_id, lens_label, metric, mode, level, query_hybas_id, query_values;
                   in threshold mode also: stringency, radius, result_count
      ranked     — list of dicts: rank, hybas_id, distance, values

    Raises RuntimeError if index not loaded; ValueError if lens unknown/inactive,
    basin not found, or basin has no valid data for this lens.
    """
    idx_entry = _INDEX.get(level)
    if idx_entry is None or idx_entry["hybas_ids"] is None:
        raise RuntimeError(
            f"Similarity index (level={level}) not loaded — startup may have failed"
        )

    hybas_ids = idx_entry["hybas_ids"]
    lens_state = idx_entry["lens_state"]

    spec = LENS_REGISTRY.get(lens_id)
    if not spec or spec.get("status") != "active":
        raise ValueError(f"Unknown or inactive lens: {lens_id!r}")

    state = lens_state.get(lens_id)
    if state is None:
        raise RuntimeError(f"Lens {lens_id!r} state missing — startup may have failed")

    hits = np.where(hybas_ids == int(query_hybas_id))[0]
    if len(hits) == 0:
        raise ValueError(f"Basin {query_hybas_id} not in similarity index (level={level})")
    q_idx = int(hits[0])

    X_raw = state["X_raw"]
    vars_ = state["variables"]

    if state["metric"] == "euclidean":
        Xz = state["Xz"]
        if np.isnan(Xz[q_idx]).any():
            raise ValueError(f"Basin {query_hybas_id} has no valid data for lens {lens_id!r}")
        diff = Xz - Xz[q_idx]
        dist = np.sqrt(np.nansum(diff**2, axis=1))
        dist[np.isnan(Xz).any(axis=1)] = np.inf
    else:
        mask = state["mask"]
        if not mask[q_idx]:
            raise ValueError(f"Basin {query_hybas_id} has no valid data for lens {lens_id!r}")
        diff = X_raw - X_raw[q_idx]
        d2   = np.einsum("ij,jk,ik->i", diff, state["VI"], diff)
        dist = np.where(mask & (d2 >= 0), np.sqrt(d2), np.inf)

    dist[q_idx] = np.inf

    # Restrict to corpus when caller provides a filter set (e.g. WH Cities subset)
    if filter_hybas_ids is not None:
        filter_arr = np.asarray(filter_hybas_ids, dtype=np.int64)
        corpus_mask = np.isin(hybas_ids, filter_arr)
        dist = np.where(corpus_mask, dist, np.inf)

    if mode == "threshold":
        if stringency not in ("strict", "moderate", "loose"):
            raise ValueError(f"Unknown stringency: {stringency!r}")
        radius = spec["thresholds"][stringency]
        valid = np.where(np.isfinite(dist) & (dist <= radius))[0]
        top_idx = [int(i) for i in valid[np.argsort(dist[valid])]]
    else:
        top_idx = [int(i) for i in np.argsort(dist)[:n + 1] if dist[i] < np.inf][:n]

    query_meta: Dict[str, Any] = {
        "lens_id":        lens_id,
        "lens_label":     spec["label"],
        "metric":         state["metric"],
        "mode":           mode,
        "level":          level,
        "query_hybas_id": int(hybas_ids[q_idx]),
        "query_values":   {v: round(float(X_raw[q_idx, j]), 6) for j, v in enumerate(vars_)},
    }
    if mode == "threshold":
        query_meta["stringency"]   = stringency
        query_meta["radius"]       = radius
        query_meta["result_count"] = len(top_idx)

    ranked = [
        {
            "rank":     rank + 1,
            "hybas_id": int(hybas_ids[i]),
            "distance": round(float(dist[i]), 6),
            "values":   {v: round(float(X_raw[i, j]), 6) for j, v in enumerate(vars_)},
        }
        for rank, i in enumerate(top_idx)
    ]

    return query_meta, ranked


# ---------------------------------------------------------------------------
# Conjunction panel (WO6c) — public API
# ---------------------------------------------------------------------------

def get_conjunction_registry() -> List[Dict[str, Any]]:
    """Public view of the conjunction lens registry (for the panel's lens selector)."""
    out = []
    for lid, lens in CONJ_LENSES.items():
        out.append({
            "lens_id":  lid,
            "group":    lens["group"],
            "label":    lens["label"],
            "shade_by": lens["shade_by"],
            "conditions": [
                {"condition": c, "kind": CONJ_CONDITIONS[c]["kind"],
                 "default": CONJ_CONDITIONS[c]["default"]}
                for c in lens["conditions"]
            ],
        })
    return out


def find_conjunction(
    query_hybas_id: int,
    lens_id: str = "climate.precip",
    bands: Optional[Dict[str, float]] = None,
    level: int = 6,
    filter_hybas_ids: Optional[np.ndarray] = None,
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """Return the set of basins that satisfy EVERY condition of the lens (non-compensatory).

    bands: per-condition band values overriding the defaults (keys are condition names, e.g.
      {"precip_shape": 0.90, "precip_magnitude": 1.5}). Missing keys fall back to the schema default.

    Returns (query_meta, members):
      query_meta — lens_id, lens_label, level, query_hybas_id, shade_by, bands (effective),
                   set_size, query_values, per_condition (standalone counts), attrition
                   (cumulative counts in condition order), spatial (spread of the set).
      members    — list of {hybas_id, corr, lat, lon}, one per set member. `corr` is the shape
                   correlation for shading (null when the lens has no shape term).

    Membership is binary; there is no ranking and no composite distance. Empty is honest scarcity.
    Raises RuntimeError if the index is not loaded; ValueError if the lens is unknown, the basin is
    not in the index, or the basin has no valid climate data.
    """
    idx_entry = _INDEX.get(level)
    if idx_entry is None or idx_entry.get("conj") is None:
        raise RuntimeError(
            f"Conjunction index (level={level}) not loaded — startup may have failed"
        )
    conj = idx_entry["conj"]

    lens = CONJ_LENSES.get(lens_id)
    if lens is None:
        raise ValueError(f"Unknown conjunction lens: {lens_id!r}")

    hybas_ids = conj["hybas_ids"]
    valid     = conj["valid"]

    hits = np.where(hybas_ids == int(query_hybas_id))[0]
    if len(hits) == 0:
        raise ValueError(f"Basin {query_hybas_id} not in conjunction index (level={level})")
    qi = int(hits[0])
    if not valid[qi]:
        raise ValueError(f"Basin {query_hybas_id} has no valid climate data (level={level})")

    bands = bands or {}
    used_bands: Dict[str, float] = {}

    def band(cond: str) -> float:
        v = bands.get(cond)
        val = float(v) if v is not None else float(CONJ_CONDITIONS[cond]["default"])
        used_bands[cond] = val
        return val

    Z        = conj["Z"]
    pre_total = conj["pre_total"]
    cv        = conj["cv"]
    tmp_mean  = conj["tmp_mean"]
    tmp_rng   = conj["tmp_rng"]
    lat       = conj["lat"]
    lon       = conj["lon"]

    # Correlation is computed once if the lens uses it for a condition or for shading.
    need_corr = ("precip_shape" in lens["conditions"]) or (lens["shade_by"] == "precip_shape")
    corr = None
    if need_corr:
        corr = Z @ Z[qi]            # NaN where a row is flat
        corr[qi] = -np.inf          # exclude self from any shape condition
        corr[conj["arid"]] = -np.inf  # arid basins never eligible on shape (noise); WO6b Cell 7

    def condition_mask(cond: str) -> np.ndarray:
        if cond == "precip_shape":
            return np.isfinite(corr) & (corr >= band("precip_shape"))
        if cond == "precip_magnitude":
            r = band("precip_magnitude")
            q = pre_total[qi]
            return (pre_total <= q * r) & (pre_total >= q / r)
        if cond == "precip_amplitude_cv":
            return np.abs(cv - cv[qi]) <= band("precip_amplitude_cv")
        if cond == "temp_level":
            return np.abs(tmp_mean - tmp_mean[qi]) <= band("temp_level")
        if cond == "temp_range":
            return np.abs(tmp_rng - tmp_rng[qi]) <= band("temp_range")
        raise ValueError(f"Unknown condition: {cond!r}")

    # Start from the valid universe, self excluded. Optional corpus restriction.
    running = valid.copy()
    running[qi] = False
    if filter_hybas_ids is not None:
        running &= np.isin(hybas_ids, np.asarray(filter_hybas_ids, dtype=np.int64))

    per_condition: Dict[str, int] = {}   # each condition alone, over the valid universe
    attrition: List[Dict[str, Any]] = [] # cumulative in condition order
    for cond in lens["conditions"]:
        cmask = condition_mask(cond)
        per_condition[cond] = int((valid & cmask).sum())
        running &= cmask
        attrition.append({"condition": cond, "remaining": int(running.sum())})

    running[qi] = False   # defensive: never include the query itself
    member_idx = np.where(running)[0]

    # Order members by shape correlation when the lens shades by it, else by hybas_id.
    if corr is not None and lens["shade_by"] == "precip_shape":
        member_idx = member_idx[np.argsort(-corr[member_idx])]

    members = [
        {
            "hybas_id":     int(hybas_ids[i]),
            "corr":         (round(float(corr[i]), 4) if corr is not None else None),
            "pre_total_mm": round(float(pre_total[i]), 1),
            "lat":          (float(lat[i]) if np.isfinite(lat[i]) else None),
            "lon":          (float(lon[i]) if np.isfinite(lon[i]) else None),
        }
        for i in member_idx
    ]

    # Spatial spread of the set (a property of the place, not a verdict on the instrument).
    spatial: Dict[str, Any] = {"max_dist_from_query_km": None, "diameter_km": None}
    if len(member_idx) and np.isfinite(lat[qi]) and np.isfinite(lon[qi]):
        mlat, mlon = lat[member_idx], lon[member_idx]
        d_from_q = _haversine_km(mlat, mlon, float(lat[qi]), float(lon[qi]))
        if np.isfinite(d_from_q).any():
            spatial["max_dist_from_query_km"] = round(float(np.nanmax(d_from_q)), 1)
        # Diameter (max pairwise) — small sets only, to avoid an O(n^2) blowup on a loose lens.
        if 1 < len(member_idx) <= 2000:
            diam = 0.0
            for k in range(len(member_idx)):
                dk = _haversine_km(mlat, mlon, float(mlat[k]), float(mlon[k]))
                if np.isfinite(dk).any():
                    diam = max(diam, float(np.nanmax(dk)))
            spatial["diameter_km"] = round(diam, 1)

    query_values = {
        "pre_total_mm": round(float(pre_total[qi]), 1),
        "cv":           round(float(cv[qi]), 4),
        "tmp_mean_c":   round(float(tmp_mean[qi]), 2),
        "tmp_range_c":  round(float(tmp_rng[qi]), 2),
    }

    query_meta = {
        "lens_id":       lens_id,
        "lens_label":    lens["label"],
        "level":         level,
        "query_hybas_id": int(hybas_ids[qi]),
        "shade_by":      lens["shade_by"],
        "bands":         used_bands,
        "set_size":      len(members),
        "query_values":  query_values,
        "per_condition": per_condition,
        "attrition":     attrition,
        "spatial":       spatial,
    }
    return query_meta, members
