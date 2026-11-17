"""WO-06 items 1 and 2 (scratch): Band T cost per source, called directly on the engine's functions.

Reads only. For a place (a polity at its resolver year, or a single basin) it times _band_t_hyde, _band_t_lmr,
_band_t_evolv2k and _band_t_geda one at a time over a grid of (start year, length), REPEATS times each, and records
the rows each returns and, for HYDE, the rows its SQL pulled into pandas. Writes output/edop/dashboard/wo06_per_source.csv.
Usage: python dash_wo06_per_source.py [case ...]   (cases: song, lviv; default both)
"""
import csv
import statistics
import sys
import time
from pathlib import Path

import pandas as pd

from app.db.connection import db_connect
from scripts.edop.areas import engine

REPEATS = 3
OUT = Path(__file__).resolve().parents[3] / "output" / "edop" / "dashboard" / "wo06_per_source.csv"
# (start year, length): lengths at the WO-05 start, then fixed lengths moved across 1950 and across the data's start
GRID = [(1000, 100), (1000, 400), (1000, 800), (1000, 1000),
        (1, 800), (200, 800), (1000, 800), (1200, 800), (1100, 800), (1150, 800), (1000, 950), (1000, 951), (1000, 1000)]
GRID = list(dict.fromkeys(GRID))
SOURCES = [("hyde", engine._band_t_hyde), ("lmr", engine._band_t_lmr),
           ("evolv2k", engine._band_t_evolv2k), ("geda", engine._band_t_geda)]


def place(case, conn):
    if case == "song":
        geom_wkt, _, meta = engine.resolve_polity("Northern Song", 1000, 6, conn)
        return dict(geom_wkt=geom_wkt, lat=34.0, lon=113.0, resolver_year=1000, label="Northern Song (polity, 1000)")
    return dict(geom_wkt=None, lat=49.8397, lon=24.0297, resolver_year=None, label="Lviv (basin buffer 25 km)")


def main(cases):
    conn = db_connect()
    pulled = {}
    real_read_sql = pd.read_sql

    def spy(sql, con, *a, **k):
        t0 = time.perf_counter()
        df = real_read_sql(sql, con, *a, **k)
        pulled["rows"] = pulled.get("rows", 0) + len(df)
        pulled["sql_s"] = pulled.get("sql_s", 0.0) + (time.perf_counter() - t0)
        return df

    engine.pd.read_sql = spy
    out = []
    for case in cases:
        p = place(case, conn)
        for start, length in GRID:
            end = start + length - 1
            for src, fn in SOURCES:
                times, sqls, nrows, prow = [], [], 0, 0
                for _ in range(REPEATS):
                    pulled.clear()
                    q = engine._band_t_query(p["lat"], p["lon"], 25, start, end, conn, p["geom_wkt"], p["resolver_year"])
                    t0 = time.perf_counter()
                    res = fn(q)
                    times.append(time.perf_counter() - t0)
                    sqls.append(pulled.get("sql_s", 0.0))
                    nrows, prow = len(res.rows), pulled.get("rows", 0)
                row = dict(case=p["label"], start=start, end=end, length=length, source=src, rows_out=nrows, rows_pulled=prow,
                           seconds_median=round(statistics.median(times), 2), seconds_max=round(max(times), 2),
                           sql_seconds=round(statistics.median(sqls), 2))
                out.append(row)
                print(row, flush=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    print("wrote", OUT)


if __name__ == "__main__":
    main(sys.argv[1:] or ["song", "lviv"])
