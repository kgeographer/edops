"""WO-05 item 3: payload size and response time of /api/areas against Band T span length.

Local server only (default http://localhost:8000). Asks as the Dashboard does (detail=true, Band T) for a single basin
inside GEDA's footprint (Lviv), one outside it (Santa Fe) and a polity, at increasing spans, REPEATS times each.
Writes output/edop/dashboard/wo05_span_timing.csv and prints a table. Usage: python dash_wo05_span_timing.py [base_url]
"""
import csv
import gzip
import statistics
import sys
import time
from pathlib import Path

import requests

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
REPEATS = 3
SPANS = [10, 25, 50, 100, 200, 400, 800, 1000]           # years, starting at 1000 CE (GEDA's first year)
CASES = {
    "Lviv (inside GEDA)":    dict(scope="single_basin", lat=49.8397, lon=24.0297, level=6),
    "Santa Fe (no GEDA)":    dict(scope="single_basin", lat=35.687, lon=-105.9378, level=6),
    "Northern Song (polity)": dict(scope="polity", polity="Northern Song", year=1000, level=6),
}
OUT = Path(__file__).resolve().parents[3] / "output" / "edop" / "dashboard" / "wo05_span_timing.csv"


def one(params, years):
    q = dict(params, bands="T", detail="true", from_year=1000, to_year=1000 + years - 1, src="ui_aux")
    t0 = time.perf_counter()
    r = requests.get(f"{BASE}/api/areas", params=q, timeout=600, headers={"Accept-Encoding": "identity"})
    dt = time.perf_counter() - t0
    r.raise_for_status()
    rows = r.json()["rows"]
    return dt, len(r.content), len(gzip.compress(r.content)), len(rows)


def main():
    out = []
    for name, params in CASES.items():
        for years in SPANS:
            times, sizes = [], None
            for _ in range(REPEATS):
                dt, raw, gz, n = one(params, years)
                times.append(dt)
                sizes = (raw, gz, n)
            row = dict(case=name, years=years, rows=sizes[2], raw_kb=round(sizes[0] / 1024), gzip_kb=round(sizes[1] / 1024),
                       seconds_median=round(statistics.median(times), 2), seconds_max=round(max(times), 2))
            out.append(row)
            print(row, flush=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
