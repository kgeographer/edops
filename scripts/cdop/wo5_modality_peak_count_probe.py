"""
WO5 detour -- direct peak-counting as an alternative to the existing R_dbl
(harmonic-ratio) modality measure.

Question: does counting local maxima in the 12-month precipitation curve,
using topographic prominence (not a fixed height) as the "is this a real
second peak" threshold, correctly classify the known probe cases -- including
the one case (Timbuktu) where the existing R_dbl measure is known to be wrong?

Ground truth, from wo2_findings.md / wo2a_findings.md:
  Mombasa      -> bimodal (2 peaks). R_dbl=0.341, correctly above threshold.
  Timbuktu     -> single monsoon (1 peak). R_dbl=0.575 -- WRONGLY above the
                  0.30 threshold; "an artifact of a sharp single monsoon peak:
                  Fourier decomposition places energy at all harmonics when
                  the signal is sharply concentrated" (wo2a_findings.md).
  George Town  -> "aseasonal" -- near-flat year-round rain, R_dbl=0.187,
                  correctly excluded from bimodal. Not a clean 1-or-2 case;
                  the interesting question is whether peak-counting produces
                  a low-prominence single peak (consistent) or something
                  spurious.
  Augsburg     -> temperate, distributed rainfall (the WO1 false-match probe
                  for a different lens); included here as an additional
                  general-purpose check, no strong prior on peak count.

Circular peak-finding with prominence, implemented directly (12 points is
small enough that a hand-rolled version is clearer than pulling in scipy's
linear-sequence find_peaks and working around the wraparound).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import warnings

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.shared.db_utils import db_connect

warnings.filterwarnings("ignore", message="pandas only supports SQLAlchemy")

PROBES = {
    "Mombasa":     (-4.0435,   39.6682),
    "Timbuktu":    (16.8167,   -2.9833),
    "George Town": (5.4141,   100.3288),
    "Augsburg":    (48.3705,   10.8978),
}


def resolve_basin(conn, lat, lon):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT hybas_id FROM public.basin06 "
            "WHERE ST_Within(ST_SetSRID(ST_MakePoint(%s, %s), 4326), geom) "
            "ORDER BY ST_Area(geom::geography) ASC LIMIT 1",
            (lon, lat),
        )
        row = cur.fetchone()
    if not row:
        raise RuntimeError(f"no basin found at ({lat}, {lon})")
    return int(row[0])


def circular_peaks(values, min_prominence):
    """Local maxima of a circular 12-point sequence, filtered by topographic
    prominence >= min_prominence. Returns list of (month_idx, value, prominence).

    Prominence of a peak = peak height minus the higher of the two "key col"
    (valley floor) elevations reached by walking outward in each direction
    until the curve rises above the peak's own height again (wrapping around
    the circle). A tall isolated peak has high prominence; a small bump on
    the shoulder of a bigger peak has low prominence.
    """
    n = len(values)
    v = np.asarray(values, dtype=float)

    # Candidate local maxima (circular neighbors), ties broken by requiring
    # strict inequality on at least one side to avoid double-counting a flat top.
    candidates = []
    for i in range(n):
        left, right = v[(i - 1) % n], v[(i + 1) % n]
        if v[i] >= left and v[i] >= right and (v[i] > left or v[i] > right):
            candidates.append(i)

    def walk_to_col(start, step):
        """From `start`, walk in direction `step` (+1 or -1) around the
        circle; return the lowest value seen before the curve exceeds
        v[start]'s height again (or after a full loop, the global min seen)."""
        floor = np.inf
        i = (start + step) % n
        for _ in range(n):
            if v[i] > v[start]:
                break
            floor = min(floor, v[i])
            i = (i + step) % n
        return floor

    peaks = []
    for i in candidates:
        left_col = walk_to_col(i, -1)
        right_col = walk_to_col(i, +1)
        prominence = v[i] - max(left_col, right_col)
        if prominence >= min_prominence:
            peaks.append((i, float(v[i]), float(prominence)))

    return peaks


conn = db_connect()
rows = []
for name, (lat, lon) in PROBES.items():
    hybas_id = resolve_basin(conn, lat, lon)
    arr = pd.read_sql(
        "SELECT pre_mm_monthly FROM public.v_basin06_persist_rev2 WHERE hybas_id = %s",
        conn, params=(hybas_id,),
    )
    monthly = np.array(arr.iloc[0]["pre_mm_monthly"], dtype=float)
    rows.append((name, hybas_id, monthly))
conn.close()

MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# Sweep a few prominence thresholds, expressed as a fraction of the basin's
# own annual range (max - min), so the threshold means the same thing
# ("the dip must erase at least X% of the seasonal range") across places
# with very different absolute rainfall.
FRACTIONS = [0.10, 0.20, 0.30, 0.40]

for name, hybas_id, monthly in rows:
    total = monthly.sum()
    rng = monthly.max() - monthly.min()
    print(f"\n=== {name} (hybas_id={hybas_id}) ===")
    print(f"monthly mm: " + ", ".join(f"{m}={v:.0f}" for m, v in zip(MONTH_NAMES, monthly)))
    print(f"annual total={total:.0f}mm  range={rng:.0f}mm")

    for frac in FRACTIONS:
        min_prom = frac * rng
        peaks = circular_peaks(monthly, min_prom)
        peak_desc = ", ".join(
            f"{MONTH_NAMES[i]}({val:.0f}mm, prom={prom:.0f})" for i, val, prom in peaks
        )
        print(f"  prominence >= {frac:.0%} of range ({min_prom:.0f}mm): "
              f"{len(peaks)} peak(s) -- {peak_desc}")
