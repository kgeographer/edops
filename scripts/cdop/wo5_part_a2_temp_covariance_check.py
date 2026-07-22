"""
WO5 Part A follow-up -- does a single global covariance matrix make sense for
climate.temp (tmp_dc_syr, tmp_seas_amp, tmp_concentration), or does the data
contain a real branching structure (e.g. "cold because high-latitude,
continental" vs "cold because high-elevation, non-high-latitude") that one
Mahalanobis ellipse can't represent?

Replicates the exact production derivation (app/db/seasonality.py
_compute_derived / _build_mahalanobis_state) against v_basin06_persist_rev2,
independently of the running server's in-memory index, so the whole L06
corpus can be inspected directly rather than just the basins admitted for
one query.

Expectation written down before running: if Tbilisi's basin (cold mean temp
at a non-high latitude, due to the L06 container swallowing Caucasus relief)
sits in a temperature band that is genuinely bimodal in amplitude globally
(maritime-cold low-amplitude vs continental-cold high-amplitude both present),
a single global covariance matrix will under-penalize amplitude mismatches in
that band -- which would mean the map is not "honestly reporting" a coherent
signal, it is reporting the output of a metric that is structurally unable to
separate two different physical regimes at Tbilisi's specific temperature.
"""
import numpy as np
import pandas as pd
import warnings
from numpy.linalg import inv

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.shared.db_utils import db_connect

warnings.filterwarnings("ignore", message="pandas only supports SQLAlchemy")

TBILISI_HYBAS = 2060616700
KAIFENG_HYBAS = 4060675920

conn = db_connect()

arr = pd.read_sql(
    "SELECT hybas_id, tmp_dc_monthly FROM public.v_basin06_persist_rev2", conn
)
geo = pd.read_sql(
    "SELECT hybas_id, ST_Y(ST_Centroid(geom)) AS lat, ST_X(ST_Centroid(geom)) AS lon "
    "FROM public.basin06", conn
)
scalars = pd.read_sql(
    "SELECT hybas_id, tmp_dc_syr FROM public.basin06", conn
)
conn.close()

hybas_ids = arr["hybas_id"].to_numpy().astype(np.int64)
TMP = np.array(arr["tmp_dc_monthly"].tolist(), dtype=float)  # already deg C

# tmp_dc_syr scalar is stored x10 in basin06 (per CLAUDE.md); divide by 10
scalars["tmp_dc_syr"] = scalars["tmp_dc_syr"].astype(float)
scalars.loc[scalars["tmp_dc_syr"] == -9999, "tmp_dc_syr"] = np.nan
scalars["tmp_dc_syr"] = scalars["tmp_dc_syr"] / 10.0

# Match production derivation exactly (app/db/seasonality.py)
_THETA = np.arange(12) * 2 * np.pi / 12  # unused here, kept for parity/documentation
TMP_shifted = TMP - TMP.min(axis=1, keepdims=True)
tmp_seas_amp = TMP.max(axis=1) - TMP.min(axis=1)

df = pd.DataFrame({"hybas_id": hybas_ids, "tmp_seas_amp": tmp_seas_amp})
df = df.merge(geo, on="hybas_id", how="left").merge(scalars, on="hybas_id", how="left")
df = df.dropna(subset=["tmp_dc_syr", "tmp_seas_amp"])

print(f"n={len(df)} L06 basins with valid tmp_dc_syr / tmp_seas_amp")

# ── Global correlation ──────────────────────────────────────────────────
r = df["tmp_dc_syr"].corr(df["tmp_seas_amp"])
print(f"\nGlobal Pearson corr(tmp_dc_syr, tmp_seas_amp) = {r:.3f}")

# ── Tbilisi / Kaifeng query values ──────────────────────────────────────
tb_row = df[df["hybas_id"] == TBILISI_HYBAS].iloc[0]
kf_row = df[df["hybas_id"] == KAIFENG_HYBAS].iloc[0]
print(f"\nTbilisi basin: tmp_dc_syr={tb_row['tmp_dc_syr']:.2f}  "
      f"tmp_seas_amp={tb_row['tmp_seas_amp']:.2f}  lat={tb_row['lat']:.2f}")
print(f"Kaifeng basin: tmp_dc_syr={kf_row['tmp_dc_syr']:.2f}  "
      f"tmp_seas_amp={kf_row['tmp_seas_amp']:.2f}  lat={kf_row['lat']:.2f}")


def band_report(center_temp, label, halfwidth=2.0):
    band = df[(df["tmp_dc_syr"] >= center_temp - halfwidth) &
              (df["tmp_dc_syr"] <= center_temp + halfwidth)]
    print(f"\n=== {label}: basins with tmp_dc_syr in [{center_temp-halfwidth:.1f}, "
          f"{center_temp+halfwidth:.1f}] deg C (n={len(band)}) ===")
    amp = band["tmp_seas_amp"]
    print(f"tmp_seas_amp in this band: min={amp.min():.1f} p10={amp.quantile(.10):.1f} "
          f"p25={amp.quantile(.25):.1f} median={amp.median():.1f} "
          f"p75={amp.quantile(.75):.1f} p90={amp.quantile(.90):.1f} max={amp.max():.1f} "
          f"std={amp.std():.1f}")
    # latitude split as a proxy for physical regime: high-lat (boreal/oceanic-influenced)
    # vs mid-lat-with-relief (mountain/continental-interior at lower latitude)
    hi = band[band["lat"].abs() >= 50]
    lo = band[band["lat"].abs() < 50]
    print(f"  |lat|>=50 (n={len(hi)}): amp median={hi['tmp_seas_amp'].median():.1f}, "
          f"range {hi['tmp_seas_amp'].min():.1f}-{hi['tmp_seas_amp'].max():.1f}")
    print(f"  |lat|<50  (n={len(lo)}): amp median={lo['tmp_seas_amp'].median():.1f}, "
          f"range {lo['tmp_seas_amp'].min():.1f}-{lo['tmp_seas_amp'].max():.1f}")
    return band


tb_band = band_report(tb_row["tmp_dc_syr"], "Tbilisi band (~5.3 C)")
kf_band = band_report(kf_row["tmp_dc_syr"], "Kaifeng band (~14.8 C)")

# ── Self-outlierness: each query's Mahalanobis distance from the corpus centroid,
#    using the same 2-variable subspace (temp, amplitude), unit-free comparison. ──
X = df[["tmp_dc_syr", "tmp_seas_amp"]].to_numpy()
mu = X.mean(axis=0)
cov = np.cov(X.T)
VI = inv(cov)


def maha_from_centroid(row):
    d = np.array([row["tmp_dc_syr"], row["tmp_seas_amp"]]) - mu
    return float(np.sqrt(d @ VI @ d))


print(f"\nGlobal centroid (tmp_dc_syr, tmp_seas_amp) = ({mu[0]:.2f}, {mu[1]:.2f})")
print(f"Tbilisi Mahalanobis distance from global centroid: {maha_from_centroid(tb_row):.3f}")
print(f"Kaifeng Mahalanobis distance from global centroid: {maha_from_centroid(kf_row):.3f}")

# percentile rank of each query's own outlierness against the whole corpus
all_d = np.sqrt(np.einsum('ij,jk,ik->i', X - mu, VI, X - mu))
tb_pct = (all_d < maha_from_centroid(tb_row)).mean() * 100
kf_pct = (all_d < maha_from_centroid(kf_row)).mean() * 100
print(f"Tbilisi self-outlier percentile (vs all L06 basins): {tb_pct:.1f}")
print(f"Kaifeng self-outlier percentile (vs all L06 basins): {kf_pct:.1f}")
