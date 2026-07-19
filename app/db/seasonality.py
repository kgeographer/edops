"""
Similarity lens registry — loaded once at startup, queried per request.

Three Climate sub-lenses are precomputed from L06 and L08 monthly arrays and
BasinATLAS scalars at startup. Level is a parameter of index selection; no new
distance logic is needed to add a level.

Metric per lens:
  euclidean    — normalized Euclidean on z-scored variables (low inter-variable correlation)
  mahalanobis  — accounts for correlated variables (mandatory when |r| > ~0.3)

Derived variables (computed from monthly arrays; no DB column):
  pre_concentration, seas_phase_offset, tmp_concentration, tmp_seas_amp

BasinATLAS scalar variables:
  pre_mm_syr  — annual precip mm/yr        (no scaling)
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
        "variables":  ["pre_mm_syr", "pre_concentration"],
        "metric":     "euclidean",
        "status":     "active",
        "thresholds": {"strict": 0.10, "moderate": 0.20, "loose": 0.50},
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
        "group":      "Climate",
        "label":      "Seasonal phase",
        "variables":  ["pre_concentration", "seas_phase_offset"],
        "metric":     "euclidean",
        "status":     "active",
        "thresholds": {"strict": 0.10, "moderate": 0.30, "loose": 0.75},
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
_DERIVED = {"pre_concentration", "seas_phase_offset", "tmp_concentration", "tmp_seas_amp"}

# BasinATLAS scalar variables needed by active lenses.
# Maps variable name → (column_name, scale_factor).
# scale_factor applied after load (tmp_dc_* stored ×10).
# Column names are identical in basin06 and basin08.
_SCALAR_SOURCES: Dict[str, Tuple[str, float]] = {
    "pre_mm_syr": ("pre_mm_syr", 1.0),
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
_THETA     = np.array([_TWO_PI * m / 12 for m in range(12)])

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


def _compute_derived(PRE: np.ndarray, TMP: np.ndarray) -> Dict[str, np.ndarray]:
    """Compute all derived similarity variables from (N,12) monthly arrays.

    PRE in mm/month; TMP in °C (v_basin06_persist_rev2 already stores °C, not ×10).
    Returns dict of variable_name → (N,) array.
    """
    pre_conc, pre_angle = _circ_conc_angle(PRE)

    TMP_shifted = TMP - TMP.min(axis=1, keepdims=True)
    tmp_conc, tmp_angle = _circ_conc_angle(TMP_shifted)

    delta          = np.abs(pre_angle - tmp_angle)
    delta          = np.minimum(delta, _TWO_PI - delta)
    seas_phase_off = delta / _TWO_PI * 12

    tmp_seas_amp = TMP.max(axis=1) - TMP.min(axis=1)

    return {
        "pre_concentration": pre_conc,
        "seas_phase_offset": seas_phase_off,
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
    lens_id: str = "climate.phase",
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
