"""
WO5 Part B -- how does L08 radius-basin-count actually vary geographically?

The 4 WO4 probes were chosen for climate diversity (bimodal, temperate,
container-mismatch, etc.), not basin density. Basin density (how many small
basins pack into a given radius) is what actually drives radius_count, and it
plausibly varies a lot by region -- monsoon Asia and temperate mid-latitudes
likely subdivide more finely than deserts or high-latitude interiors. Before
deciding whether/how to offer L08 in the Context tab's radius control, this
checks a much broader, geographically diverse sample: the 254-city WH Cities
corpus (spans every inhabited continent, a real settlement-density sample
rather than 4 curated climate probes).

Uses the already-loaded context.py index directly (haversine from each city's
lat/lon against the L06/L08 basin representative-point arrays) -- no per-city
DB round trip needed, since only counts are wanted here, not per-variable
values.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import numpy as np
import pandas as pd
import warnings

from scripts.shared.db_utils import db_connect
from app.db.context import load_context_index, _INDEX, _haversine_km

warnings.filterwarnings("ignore", message="pandas only supports SQLAlchemy")

conn = db_connect()
load_context_index(conn, level=6)
load_context_index(conn, level=8)

cities = pd.read_sql(
    "SELECT id, city, country, ST_Y(geom) AS lat, ST_X(geom) AS lon "
    "FROM gaz.wh_cities WHERE geom IS NOT NULL",
    conn,
)
conn.close()

print(f"n cities = {len(cities)}")

RADII = [250, 500, 1000, 2500]
WEBGL_BUDGET = 5000

results = []
for level in (6, 8):
    idx = _INDEX[level]
    basin_lat, basin_lon = idx["lat"], idx["lon"]
    for _, row in cities.iterrows():
        for r in RADII:
            dist = _haversine_km(row["lat"], row["lon"], basin_lat, basin_lon)
            count = int((dist <= r).sum())
            results.append({"level": level, "radius_km": r, "city": row["city"],
                             "country": row["country"], "count": count})

df = pd.DataFrame(results)

print("\n=== Distribution of radius_count across all 254 WH Cities, by level/radius ===")
summary = df.groupby(["level", "radius_km"])["count"].agg(
    ["min", lambda s: s.quantile(.25), "median", lambda s: s.quantile(.75),
     lambda s: s.quantile(.90), "max"]
)
summary.columns = ["min", "p25", "median", "p75", "p90", "max"]
print(summary.to_string())

print(f"\n=== Share of cities exceeding WebGL budget ({WEBGL_BUDGET} basins), by level/radius ===")
for (level, radius), grp in df.groupby(["level", "radius_km"]):
    over = (grp["count"] > WEBGL_BUDGET).mean() * 100
    n_over = (grp["count"] > WEBGL_BUDGET).sum()
    print(f"  L{level} @ {radius}km: {over:5.1f}% of cities over budget ({n_over}/{len(grp)})")

print("\n=== Densest 5 cities at L08/1000km (worst case for that combo) ===")
sub = df[(df["level"] == 8) & (df["radius_km"] == 1000)].nlargest(5, "count")
print(sub[["city", "country", "count"]].to_string(index=False))

print("\n=== Densest 5 cities at L08/2500km ===")
sub = df[(df["level"] == 8) & (df["radius_km"] == 2500)].nlargest(5, "count")
print(sub[["city", "country", "count"]].to_string(index=False))

print("\n=== Sparsest 5 cities at L06/2500km (best case, sanity check) ===")
sub = df[(df["level"] == 6) & (df["radius_km"] == 2500)].nsmallest(5, "count")
print(sub[["city", "country", "count"]].to_string(index=False))
