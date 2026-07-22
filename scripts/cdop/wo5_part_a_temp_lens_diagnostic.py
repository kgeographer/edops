"""
WO5 Part A -- temperature lens diagnostic.

Expectation written down before running (per WO5 proviso):
  Amplitude tracks rank cleanly, Q1 (nearest) high-amplitude to Q4 (farthest)
  low-amplitude -- i.e. the ranking itself is sound and 'moderate' is simply
  too wide (a threshold problem). This is the a priori guess; Part A exists
  to check it against the alternative (low-amplitude basins scattered through
  Q1/Q2, implicating tmp_concentration as the admitting variable).

Query: GET /api/similarity, lens=climate.temp, mode=threshold, stringency=moderate.
Probes: Tbilisi (41.6938, 44.8015) -- the WO1 false-match case.
        Kaifeng (34.7986, 114.3413) -- control, map reads coherent.
Coordinates match notebooks/cdop/wo4_similarity-studies.ipynb probe table.

Run against the live dev server (assumes `uvicorn app.main:app --reload` already running).
"""
import requests
import pandas as pd

BASE = "http://localhost:8000"

PROBES = {
    "Tbilisi": (41.6938, 44.8015),
    "Kaifeng": (34.7986, 114.3413),
}


def fetch(lat, lon):
    r = requests.get(
        f"{BASE}/api/similarity",
        params={"lat": lat, "lon": lon, "lens": "climate.temp",
                "mode": "threshold", "stringency": "moderate"},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()


def quartile_report(name, data):
    results = data["results"]
    n = len(results)
    print(f"\n=== {name} ===")
    print(f"query_basin_id={data['query_basin_id']}  query_values={data['query_values']}")
    print(f"metric={data['metric']}  stringency={data['stringency']}  "
          f"radius={data['radius']}  result_count={data['result_count']}")

    df = pd.DataFrame([
        {
            "rank": r["rank"],
            "distance": r["distance"],
            "basin_id": r["basin_id"],
            "place_name": r["place_name"],
            "lat": r["lat"],
            "lon": r["lon"],
            "tmp_dc_syr": r["values"]["tmp_dc_syr"],
            "tmp_seas_amp": r["values"]["tmp_seas_amp"],
            "tmp_concentration": r["values"]["tmp_concentration"],
        }
        for r in results
    ])

    df["quartile"] = pd.qcut(df["rank"], 4, labels=["Q1", "Q2", "Q3", "Q4"])

    print(f"\nn={n}")
    print(df.groupby("quartile", observed=True)[["tmp_seas_amp", "tmp_dc_syr"]]
          .agg(["min", "median", "max"]).to_string())

    print("\ntmp_concentration by quartile:")
    print(df.groupby("quartile", observed=True)["tmp_concentration"]
          .agg(["min", "median", "max"]).to_string())

    qv = data["query_values"]
    print(f"\nquery tmp_concentration={qv.get('tmp_concentration')}  "
          f"tmp_seas_amp={qv.get('tmp_seas_amp')}  tmp_dc_syr={qv.get('tmp_dc_syr')}")

    # Does |value - query_value| grow with distance? Spearman rank correlation,
    # deviation from query vs. Mahalanobis distance -- a direct test of whether
    # each variable is actually being "spent" by the metric or is nearly free.
    df["abs_dev_amp"]  = (df["tmp_seas_amp"] - qv["tmp_seas_amp"]).abs()
    df["abs_dev_temp"] = (df["tmp_dc_syr"] - qv["tmp_dc_syr"]).abs()
    df["abs_dev_conc"] = (df["tmp_concentration"] - qv["tmp_concentration"]).abs()
    corr = df[["distance", "abs_dev_amp", "abs_dev_temp", "abs_dev_conc"]].corr(method="spearman")["distance"]
    print("\nSpearman corr(distance, |deviation from query|):")
    print(f"  tmp_seas_amp:      {corr['abs_dev_amp']:.3f}")
    print(f"  tmp_dc_syr:        {corr['abs_dev_temp']:.3f}")
    print(f"  tmp_concentration: {corr['abs_dev_conc']:.3f}")

    return df


if __name__ == "__main__":
    dfs = {}
    for name, (lat, lon) in PROBES.items():
        data = fetch(lat, lon)
        dfs[name] = quartile_report(name, data)

    # Explicit Norway / high-latitude maritime check for Tbilisi (proviso: "Norway's
    # presence needs explaining even if it ranks last").
    tb = dfs["Tbilisi"]
    maritime = tb[(tb["lat"].notna()) & (tb["lat"] > 55)]
    print("\n=== Tbilisi: high-latitude (lat>55) admitted basins ===")
    if len(maritime):
        print(maritime[["rank", "distance", "place_name", "lat", "lon",
                         "tmp_seas_amp", "tmp_dc_syr", "tmp_concentration"]].to_string())
    else:
        print("none with lat>55 among gazetteer-linked results (place_name may be null for many)")

    print("\n=== Tbilisi: lowest tmp_seas_amp basins in the full moderate set (any rank) ===")
    print(tb.nsmallest(10, "tmp_seas_amp")[["rank", "distance", "place_name", "lat", "lon",
                                            "tmp_seas_amp", "tmp_dc_syr", "tmp_concentration"]]
          .to_string())
