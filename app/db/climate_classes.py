"""WO7 climate classes — two discrete axes + a composed cell label.

Two independent axes, computed per basin from the monthly precip/temp curves:

  * modality  {arid, aseasonal, 1-season, 2-season, undetermined}
      arid gate (annual total < THRESH_ARID) -> cv gate (cv < CV_FLAT) -> Knoben ΔE
  * phase     {warm-wet, cool-wet, weak coupling, no thermal cycle}
      thermal gate (tmp_seas_amp < THERMAL_FLOOR) -> sign/strength of the direct
      precip x temp correlation (|r| >= PT_CUT)

The cell is the (modality, phase) pair; its display label composes from the axis labels
(modality-first), with the phase term dropped for `aseasonal` basins (flat rainfall -> the
timing of the rain is meaningless). See docs/cdop/pilot/wo7_findings.md and wo7a_label-lock-build.md.

Runtime home is an **in-memory startup index** (the similarity/context family), sourced from the
persist views — not a parquet or a table. `load_class_index(conn, level)` computes and holds the
class arrays in `_INDEX[level]`; `main.py` lifespan loads L06 eagerly, and L08 is computed lazily on
first use (so the ~18 s L08 Knoben never hits boot). Routes read `axis_values` / `class_lens` from
memory. `build_and_save` remains only as an OFFLINE parquet export for analysis — it is not the
runtime source.

Knoben ΔE here is the *vectorized grid* validated in notebooks/cdop/wo7_climate_classes.ipynb Cell 4
(grid == exact Nelder-Mead == WO6b reference on 9/9 synthetics and 11/11 probes).
"""
from __future__ import annotations

import warnings
from typing import Dict

import numpy as np
import pandas as pd

# ── Declared conventions (stated in the legend as conventions, not discovered cuts) ──────────
THRESH_ARID   = 100.0   # mm/yr — the one threshold in a genuine histogram trough (wo2 Cell 12)
CV_FLAT       = 0.20    # aseasonal gate (WO6b Cell 18 plateau)
THERMAL_FLOOR = 5.0     # deg C tmp_seas_amp — below this the temp curve is noise (WO6c Cell 7)
PT_CUT        = 0.50    # |precip x temp corr| cut for warm/cool-season vs weak coupling (WO6b Cell 19)
# Knoben verdict thresholds (WO6b Cell 12):
POOR_E        = 0.25
NEGLIGIBLE_D  = 0.02

_t = np.arange(12)

MOD_ORDER   = ['arid', 'aseasonal', '1-season', '2-season', 'undetermined']
PHASE_ORDER = ['warm-wet', 'cool-wet', 'weak coupling', 'no thermal cycle']

MOD_LABEL = {
    'arid': 'Arid', 'aseasonal': 'Even year-round', '1-season': 'One wet season',
    '2-season': 'Two wet seasons', 'undetermined': 'Undetermined',
}
PHASE_LABEL = {
    'warm-wet': 'Warm-season rain', 'cool-wet': 'Cool-season rain',
    'weak coupling': 'Weak coupling', 'no thermal cycle': 'No temperature cycle',
}

# Fixed per-class colours (the notebook's darkened palette), so legend and paint agree everywhere.
MOD_COLORS = {'arid': '#D9B879', 'aseasonal': '#8A8A8A', '1-season': '#2E8B57',
              '2-season': '#8E44AD', 'undetermined': '#C879B0'}
PHASE_COLORS = {'warm-wet': '#D7301F', 'cool-wet': '#2166AC',
                'weak coupling': '#9E9E9E', 'no thermal cycle': '#E8C34A'}

# Declared conventions, for the legend note (stated as conventions, not discovered cuts).
CONVENTIONS = (f"Conventions (declared, not discovered cuts): arid < {THRESH_ARID:.0f} mm/yr · "
               f"even year-round cv < {CV_FLAT} · no temperature cycle < {THERMAL_FLOOR:.0f} °C "
               f"seasonal amplitude · warm/cool-season |precip×temp r| ≥ {PT_CUT}. "
               "Köppen-Mediterranean, monsoon, and tropical twin-rains are subsets of these "
               "classes, not equivalent to them.")


def axis_meta(axis: str):
    """(order, label_map, color_map) for an axis; raises on unknown axis."""
    if axis == 'modality':
        return MOD_ORDER, MOD_LABEL, MOD_COLORS
    if axis == 'phase':
        return PHASE_ORDER, PHASE_LABEL, PHASE_COLORS
    raise ValueError(f"axis must be 'modality' or 'phase', got {axis!r}")


def axis_categories(df: pd.DataFrame, axis: str):
    """Category list [{id,key,label,count,pct,color}] + {key: id} map for a class axis."""
    order, label, color = axis_meta(axis)
    n = len(df)
    vc = df[axis].value_counts()
    cats, idmap = [], {}
    for i, k in enumerate(order):
        idmap[k] = i
        c = int(vc.get(k, 0))
        cats.append({'id': i, 'key': k, 'label': label[k], 'count': c,
                     'pct': round(100 * c / n, 2) if n else 0.0, 'color': color[k]})
    return cats, idmap

_LEVEL_TABLES = {6: ('v_basin06_persist_rev2', 'basin06'),
                 8: ('v_basin08_persist_rev2', 'basin08')}


# ── Knoben ΔE, vectorized grid (Cell 4) ─────────────────────────────────────────────────────
def _cr(delta):
    """B&W eq 4 truncation-correction factor; zero below delta=1. Scalar or array."""
    d = np.asarray(delta, dtype=float)
    poly = -0.001*d**4 + 0.026*d**3 - 0.245*d**2 + 0.2432*d - 0.038
    return np.where(d > 1, poly, 0.0)


def knoben_E_grid(P, tau, d_step=0.05, s_per_month=4):
    """Best Knoben fit error E per row of P (M,12) over a (delta, s) grid. Returns E (M,)."""
    P = np.atleast_2d(P).astype(float)
    pbar = P.mean(axis=1)
    ok = pbar > 0
    grid_delta = np.arange(0.0, 4.0 + 1e-9, d_step)
    grid_s = np.linspace(0.0, tau, int(round(tau*s_per_month)), endpoint=False)
    sin_tab = np.sin(2*np.pi*(_t[None, :] - grid_s[:, None]) / tau)   # (n_s, 12)
    bestE = np.full(P.shape[0], np.inf)
    safe_pbar = np.where(ok, pbar, 1.0)
    for d in grid_delta:
        cr = float(_cr(d))
        for row in sin_tab:
            sim = np.maximum(0.0, safe_pbar[:, None] * (1.0 + cr + d * row[None, :]))
            obj = np.abs(sim - P).mean(axis=1) / safe_pbar
            bestE = np.minimum(bestE, obj)
    bestE[~ok] = np.nan
    return bestE


# ── Axis classifiers ─────────────────────────────────────────────────────────────────────────
def classify_modality(PRE: np.ndarray, pre_total: np.ndarray) -> np.ndarray:
    """Modality label per basin. PRE (N,12) monthly precip; pre_total (N,) annual total."""
    n = len(PRE)
    with np.errstate(invalid="ignore", divide="ignore"):
        mean = PRE.mean(axis=1)
        cv = PRE.std(axis=1) / np.where(mean > 0, mean, np.nan)
    out = np.full(n, 'undetermined', dtype=object)
    arid = pre_total < THRESH_ARID
    asea = (~arid) & np.isfinite(cv) & (cv < CV_FLAT)
    elig = (~arid) & (~asea) & np.isfinite(cv)
    out[arid] = 'arid'
    out[asea] = 'aseasonal'
    if elig.any():
        e12 = knoben_E_grid(PRE[elig], 12.0)
        e6 = knoben_E_grid(PRE[elig], 6.0)
        dE = e12 - e6
        sub = np.full(int(elig.sum()), '1-season', dtype='<U12')
        sub[dE > 0] = '2-season'
        sub[(np.minimum(e12, e6) > POOR_E) & (np.abs(dE) < NEGLIGIBLE_D)] = 'undetermined'
        out[np.where(elig)[0]] = sub
    return out


def _pearson_rows(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    Ac = A - A.mean(axis=1, keepdims=True)
    Bc = B - B.mean(axis=1, keepdims=True)
    num = (Ac * Bc).sum(axis=1)
    den = np.sqrt((Ac**2).sum(axis=1) * (Bc**2).sum(axis=1))
    return np.where(den > 0, num / den, np.nan)


def classify_phase(PRE: np.ndarray, TMP: np.ndarray, tmp_seas_amp: np.ndarray) -> np.ndarray:
    """Phase label per basin. Direct precip x temp correlation + thermal gate."""
    pt = _pearson_rows(PRE, TMP)
    out = np.full(len(PRE), 'weak coupling', dtype=object)
    out[pt >= PT_CUT] = 'warm-wet'
    out[pt <= -PT_CUT] = 'cool-wet'
    out[tmp_seas_amp < THERMAL_FLOOR] = 'no thermal cycle'   # gate wins
    return out, pt


def cell_key(modality: str, phase: str) -> str:
    """Cell identity for lens/picker grouping. Aseasonal groups by modality alone (its label
    drops the phase term), so two aseasonal basins are the same cell regardless of phase."""
    if modality == 'aseasonal':
        return 'aseasonal'
    return f'{modality}|{phase}'


def cell_label(modality: str, phase: str) -> str:
    """Composed display label, modality-first. Phase term dropped for aseasonal (Issue 1)."""
    if modality == 'aseasonal':
        return MOD_LABEL['aseasonal']
    return f'{MOD_LABEL[modality]}, {PHASE_LABEL[phase].lower()}'


# ── Build (offline) ────────────────────────────────────────────────────────────────────────
def build_level(conn, level: int) -> pd.DataFrame:
    """Compute the class table for one level from the persist view + basin rep points."""
    if level not in _LEVEL_TABLES:
        raise ValueError(f"level must be 6 or 8, got {level}")
    view, basin = _LEVEL_TABLES[level]
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="pandas only supports SQLAlchemy")
        arr = pd.read_sql(
            f"SELECT hybas_id, pre_mm_monthly, tmp_dc_monthly FROM public.{view}", conn)
        pts = pd.read_sql(
            f"SELECT hybas_id, ST_Y(ST_PointOnSurface(geom)) AS lat, "
            f"ST_X(ST_PointOnSurface(geom)) AS lon FROM public.{basin}", conn)
    arr['hybas_id'] = arr['hybas_id'].astype(np.int64)
    pts['hybas_id'] = pts['hybas_id'].astype(np.int64)
    d = arr.merge(pts, on='hybas_id', how='left')

    PRE = np.array(d['pre_mm_monthly'].tolist(), dtype=float)
    TMP = np.array(d['tmp_dc_monthly'].tolist(), dtype=float)   # already deg C (persist view)
    pre_total = PRE.sum(axis=1)
    tmp_amp = TMP.max(axis=1) - TMP.min(axis=1)

    valid = (np.isfinite(PRE).all(axis=1) & np.isfinite(TMP).all(axis=1) & (pre_total > 0))
    d = d[valid].reset_index(drop=True)
    PRE, TMP, pre_total, tmp_amp = PRE[valid], TMP[valid], pre_total[valid], tmp_amp[valid]

    modality = classify_modality(PRE, pre_total)
    phase, pt = classify_phase(PRE, TMP, tmp_amp)

    d['modality'] = modality
    d['phase'] = phase
    d['cell'] = [cell_key(m, p) for m, p in zip(modality, phase)]
    d['label'] = [cell_label(m, p) for m, p in zip(modality, phase)]
    d['pre_total'] = pre_total
    d['tmp_seas_amp'] = tmp_amp
    d['pt_corr'] = pt
    return d[['hybas_id', 'modality', 'phase', 'cell', 'label',
              'pre_total', 'tmp_seas_amp', 'pt_corr', 'lat', 'lon']]


# ── Runtime: in-memory startup index (similarity/context family) ────────────────────────────
# _INDEX[level] holds the class arrays + precomputed choropleth dicts for one level. L06 is loaded
# eagerly at startup (main.py lifespan); L08 is computed lazily on first use (its ~18 s Knoben grid
# never hits boot). Sourced from the persist views — no parquet, no table, no rsync.
_INDEX: Dict[int, dict] = {}


def _haversine_km(lat1, lon1, lat2, lon2):
    """Great-circle distance, km. lat1/lon1 may be arrays; lat2/lon2 scalars (broadcasts)."""
    R = 6371.0088
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(np.asarray(lat2) - np.asarray(lat1))
    dlmb = np.radians(np.asarray(lon2) - np.asarray(lon1))
    a = np.sin(dphi / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dlmb / 2) ** 2
    return 2 * R * np.arcsin(np.sqrt(a))


def _axis_choropleth(hybas_ids, arr, axis):
    """Precompute (categories, {str(hybas_id): cat_id}) for one axis at index-load time."""
    order, label, color = axis_meta(axis)
    idmap = {k: i for i, k in enumerate(order)}
    counts = {k: 0 for k in order}
    values = {}
    for h, k in zip(hybas_ids, arr):
        values[str(int(h))] = idmap[k]
        counts[k] += 1
    n = len(arr)
    cats = [{'id': i, 'key': k, 'label': label[k], 'count': counts[k],
             'pct': round(100 * counts[k] / n, 2) if n else 0.0, 'color': color[k]}
            for i, k in enumerate(order)]
    return cats, values


def load_class_index(conn, level: int) -> int:
    """Compute the class arrays for a level from the persist view and hold them in memory.
    Returns the basin count. Idempotent-ish: recomputes and replaces on each call."""
    df = build_level(conn, level)
    hy = df['hybas_id'].to_numpy(np.int64)
    idx = {
        'hybas_ids': hy,
        'modality':  df['modality'].to_numpy(object),
        'phase':     df['phase'].to_numpy(object),
        'cell':      df['cell'].to_numpy(object),
        'label':     df['label'].to_numpy(object),
        'lat':       df['lat'].to_numpy(float),
        'lon':       df['lon'].to_numpy(float),
        'id_to_pos': {int(h): i for i, h in enumerate(hy)},
    }
    for axis in ('modality', 'phase'):
        cats, values = _axis_choropleth(hy, idx[axis], axis)
        idx[f'cat_{axis}'] = cats
        idx[f'val_{axis}'] = values
    _INDEX[level] = idx
    return len(hy)


def _ensure_level(level: int, conn=None) -> dict:
    """Return the in-memory index for a level, computing it lazily (L08) if absent."""
    if level not in _LEVEL_TABLES:
        raise ValueError(f"level must be 6 or 8, got {level}")
    if level not in _INDEX:
        if conn is None:
            from app.db.connection import db_connect
            conn = db_connect()
            try:
                load_class_index(conn, level)
            finally:
                conn.close()
        else:
            load_class_index(conn, level)
    return _INDEX[level]


def axis_values(level: int, axis: str, conn=None):
    """(categories, {str(hybas_id): cat_id}) for one axis — the Explorer choropleth payload."""
    axis_meta(axis)  # validates axis, raises ValueError on unknown
    idx = _ensure_level(level, conn)
    return idx[f'cat_{axis}'], idx[f'val_{axis}']


def class_lens(level: int, query_hybas_id: int, conn=None) -> dict:
    """Same-cell set for a query basin: members, size, spatial spread (the Similarity lens)."""
    idx = _ensure_level(level, conn)
    pos = idx['id_to_pos'].get(int(query_hybas_id))
    if pos is None:
        raise ValueError(f"basin {query_hybas_id} not in class index (level {level})")

    qcell = idx['cell'][pos]
    qmod, qphase = idx['modality'][pos], idx['phase'][pos]
    member_pos = np.where(idx['cell'] == qcell)[0]
    lat, lon = idx['lat'], idx['lon']
    members = [int(h) for h in idx['hybas_ids'][member_pos]]

    spatial = {'max_dist_from_query_km': None, 'diameter_km': None}
    qlat, qlon = float(lat[pos]), float(lon[pos])
    if np.isfinite(qlat) and np.isfinite(qlon) and len(member_pos):
        mlat, mlon = lat[member_pos], lon[member_pos]
        d = _haversine_km(mlat, mlon, qlat, qlon)
        if np.isfinite(d).any():
            spatial['max_dist_from_query_km'] = round(float(np.nanmax(d)), 1)
        if 1 < len(member_pos) <= 2000:   # O(n^2) diameter only for small sets
            diam = 0.0
            for k in range(len(member_pos)):
                dk = _haversine_km(mlat, mlon, float(mlat[k]), float(mlon[k]))
                if np.isfinite(dk).any():
                    diam = max(diam, float(np.nanmax(dk)))
            spatial['diameter_km'] = round(diam, 1)

    aseasonal = (qmod == 'aseasonal')
    return {
        'level': level,
        'query_hybas_id': int(query_hybas_id),
        'cell': qcell,
        'label': idx['label'][pos],
        'modality': qmod, 'modality_label': MOD_LABEL[qmod],
        'phase': (None if aseasonal else qphase),
        'phase_label': (None if aseasonal else PHASE_LABEL[qphase]),
        'set_size': len(members),
        'members': members,
        'spatial': spatial,
    }
