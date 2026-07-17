"""
Seasonal similarity index — loaded once at startup, queried per request.

Precomputes normalized Euclidean distance state for all L06 basins using
two seasonality indices: pre_concentration and seas_phase_offset.
"""
import logging
import warnings
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)

_TWO_PI = 2 * np.pi
_THETA  = np.array([_TWO_PI * m / 12 for m in range(12)])

# Module-level state; None until load_similarity_index() is called
_HYBAS_IDS: Optional[np.ndarray] = None   # (N,)  int64
_X_RAW:     Optional[np.ndarray] = None   # (N,2) [pre_concentration, seas_phase_offset]
_X2Z:       Optional[np.ndarray] = None   # (N,2) z-scored


def _circ_concentration_batch(W: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """(N,12) weight matrix → (concentration, angle) each (N,); NaN where total==0."""
    total = W.sum(axis=1, keepdims=True)
    total = np.where(total == 0, np.nan, total)
    Rx = (W * np.cos(_THETA)).sum(axis=1) / total[:, 0]
    Ry = (W * np.sin(_THETA)).sum(axis=1) / total[:, 0]
    return np.sqrt(Rx**2 + Ry**2), np.arctan2(Ry, Rx)


def load_similarity_index(conn) -> None:
    """Compute and cache L06 seasonal similarity state. Call once at startup."""
    global _HYBAS_IDS, _X_RAW, _X2Z

    import pandas as pd

    try:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message="pandas only supports SQLAlchemy")
            raw = pd.read_sql(
                "SELECT hybas_id, pre_mm_monthly, tmp_dc_monthly "
                "FROM public.v_basin06_persist_rev2",
                conn,
            )

        PRE = np.array(raw["pre_mm_monthly"].tolist(), dtype=float)
        TMP = np.array(raw["tmp_dc_monthly"].tolist(), dtype=float)

        pre_conc, pre_angle = _circ_concentration_batch(PRE)

        TMP_shifted = TMP - TMP.min(axis=1, keepdims=True)
        _, tmp_angle = _circ_concentration_batch(TMP_shifted)

        delta  = np.abs(pre_angle - tmp_angle)
        delta  = np.minimum(delta, _TWO_PI - delta)
        offset = delta / _TWO_PI * 12

        X    = np.column_stack([pre_conc, offset])   # (N, 2)
        mask = ~np.isnan(X).any(axis=1)
        mu   = X[mask].mean(axis=0)
        sd   = X[mask].std(axis=0)

        X2z        = np.full_like(X, np.nan)
        X2z[mask]  = (X[mask] - mu) / sd

        _HYBAS_IDS = raw["hybas_id"].to_numpy()
        _X_RAW     = X
        _X2Z       = X2z

        logger.info("seasonality index ready: %d basins (%d valid)", len(raw), int(mask.sum()))

    except Exception:
        logger.exception("seasonality index failed to load — /api/seasonality/similar unavailable")


def find_similar(
    query_hybas_id: int,
    n: int = 20,
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """Rank all L06 basins by normalized Euclidean distance to query basin.

    Returns (query_info, results):
      query_info  — {hybas_id, pre_concentration, seas_phase_offset}
      results     — list of n dicts with rank, hybas_id, distance, and both indices

    Raises RuntimeError if index not loaded; ValueError if basin missing or has no data.
    """
    if _HYBAS_IDS is None:
        raise RuntimeError("Similarity index not loaded — startup may have failed")

    hits = np.where(_HYBAS_IDS == int(query_hybas_id))[0]
    if len(hits) == 0:
        raise ValueError(f"Basin {query_hybas_id} not in similarity index")

    q_idx = int(hits[0])
    if np.isnan(_X2Z[q_idx]).any():
        raise ValueError(f"Basin {query_hybas_id} has no valid seasonal data")

    diff = _X2Z - _X2Z[q_idx]
    dist = np.sqrt(np.nansum(diff**2, axis=1))
    dist[q_idx] = np.inf                              # exclude self
    dist[np.isnan(_X2Z).any(axis=1)] = np.inf        # exclude NaN-index basins from ranking

    top_idx = np.argsort(dist)[:n + 1]
    top_idx = [int(i) for i in top_idx if dist[i] < np.inf][:n]

    query_info = {
        "hybas_id":          int(_HYBAS_IDS[q_idx]),
        "pre_concentration": float(_X_RAW[q_idx, 0]),
        "seas_phase_offset": float(_X_RAW[q_idx, 1]),
    }

    results = [
        {
            "rank":              rank + 1,
            "hybas_id":          int(_HYBAS_IDS[i]),
            "distance":          round(float(dist[i]), 6),
            "pre_concentration": round(float(_X_RAW[i, 0]), 6),
            "seas_phase_offset": round(float(_X_RAW[i, 1]), 6),
        }
        for rank, i in enumerate(top_idx)
    ]

    return query_info, results
