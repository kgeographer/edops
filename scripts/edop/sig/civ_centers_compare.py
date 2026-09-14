"""
civ_centers_compare.py

Compare EDOPS signatures for 10 major civilizational centers at Level 06.
Fetches bands A, B, C, E from the local API, extracts numeric fields,
normalizes (z-score), and outputs a pairwise Euclidean distance matrix.

Usage:
    python3 scripts/edop/sig/civ_centers_compare.py
"""

import urllib.request
import json
import math
import sys

API_BASE = "http://localhost:8000/api/signature"
LEVEL = 6
BANDS = "ABCE"

SITES = [
    ("Babylon",        32.54,   44.42),
    ("Memphis (Egypt)", 29.85,  31.25),
    ("Mohenjo-daro",   27.33,   68.14),
    ("Anyang",         36.10,  114.35),
    ("Athens",         37.97,   23.73),
    ("Rome",           41.90,   12.50),
    ("Teotihuacan",    19.69,  -98.84),
    ("Tiwanaku",      -16.55,  -68.67),
    ("Angkor",         13.41,  103.87),
    ("Aksum",          14.13,   38.72),
]

# Numeric fields to include in comparison (excludes categorical/ID fields)
NUMERIC_FIELDS = [
    "elev_min", "elev_max", "slope_avg", "slope_upstream", "stream_gradient",
    "karst", "karst_upstream",
    "discharge_yr", "discharge_min", "discharge_max",
    "river_area", "river_area_upstream", "runoff",
    "gw_table_depth",
    "pct_clay", "pct_silt", "pct_sand",
    "pct_clay_upstream", "pct_silt_upstream", "pct_sand_upstream",
    "wet_pct_grp1", "wet_pct_grp2", "wet_pct_grp1_upstream", "wet_pct_grp2_upstream",
    "temp_yr", "temp_min", "temp_max", "temp_yr_upstream",
    "precip_yr", "precip_yr_upstream",
    "aridity", "aridity_upstream",
    "dist_sink", "endorheic", "coast_flag",
]


def fetch_sig(lat, lon):
    url = f"{API_BASE}?lat={lat}&lon={lon}&bands={BANDS}&level={LEVEL}&scope=basin"
    with urllib.request.urlopen(url, timeout=20) as r:
        return json.loads(r.read().decode())


def extract_numeric(sig):
    return {f: sig.get(f) for f in NUMERIC_FIELDS if sig.get(f) is not None}


def zscore_normalize(rows):
    """rows: list of dicts. Returns list of dicts with z-scored values, plus stats."""
    all_fields = sorted({k for r in rows for k in r})
    stats = {}
    for f in all_fields:
        vals = [r[f] for r in rows if f in r]
        if len(vals) < 2:
            stats[f] = (0, 1)
            continue
        mean = sum(vals) / len(vals)
        std = math.sqrt(sum((v - mean) ** 2 for v in vals) / len(vals))
        stats[f] = (mean, std if std > 0 else 1)

    normed = []
    for r in rows:
        normed.append({f: (r[f] - stats[f][0]) / stats[f][1] for f in all_fields if f in r})
    return normed, stats


def euclidean(a, b):
    common = set(a) & set(b)
    return math.sqrt(sum((a[k] - b[k]) ** 2 for k in common))


def field_std(rows):
    """Per-field std deviation across sites (pre-normalization) — shows which fields drive variation."""
    all_fields = sorted({k for r in rows for k in r})
    result = []
    for f in all_fields:
        vals = [r[f] for r in rows if f in r]
        if len(vals) < 2:
            continue
        mean = sum(vals) / len(vals)
        std = math.sqrt(sum((v - mean) ** 2 for v in vals) / len(vals))
        cv = abs(std / mean) if mean != 0 else 0
        result.append((f, round(std, 3), round(cv, 3), round(mean, 3)))
    return sorted(result, key=lambda x: -x[2])  # sort by CV descending


def main():
    print(f"Fetching signatures at Level {LEVEL}, Bands {BANDS}...\n")
    raw_rows = []
    for name, lat, lon in SITES:
        print(f"  {name} ({lat}, {lon})")
        try:
            sig = fetch_sig(lat, lon)
            raw_rows.append((name, extract_numeric(sig)))
        except Exception as e:
            print(f"    ERROR: {e}", file=sys.stderr)
            raw_rows.append((name, {}))

    names = [r[0] for r in raw_rows]
    dicts = [r[1] for r in raw_rows]

    # --- Field variation (pre-normalization) ---
    print("\n── Top 15 fields by coefficient of variation (CV = std/mean) ──")
    print(f"{'Field':<30} {'Std':>10} {'CV':>8} {'Mean':>10}")
    for f, std, cv, mean in field_std(dicts)[:15]:
        print(f"{f:<30} {std:>10} {cv:>8} {mean:>10}")

    # --- Normalize and compute distance matrix ---
    normed, _ = zscore_normalize(dicts)

    print("\n── Pairwise Euclidean distance matrix (z-scored) ──\n")
    col_w = 14
    header = " " * 20 + "".join(n[:col_w].rjust(col_w) for n in names)
    print(header)
    for i, ni in enumerate(names):
        row = ni[:20].ljust(20)
        for j, _ in enumerate(names):
            if i == j:
                row += "-".rjust(col_w)
            else:
                d = euclidean(normed[i], normed[j])
                row += f"{d:.2f}".rjust(col_w)
        print(row)

    # --- Closest / most distant pairs ---
    pairs = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            d = euclidean(normed[i], normed[j])
            pairs.append((d, names[i], names[j]))
    pairs.sort()

    print("\n── 5 most similar pairs ──")
    for d, a, b in pairs[:5]:
        print(f"  {a} ↔ {b}: {d:.2f}")

    print("\n── 5 most distant pairs ──")
    for d, a, b in pairs[-5:][::-1]:
        print(f"  {a} ↔ {b}: {d:.2f}")


if __name__ == "__main__":
    main()
