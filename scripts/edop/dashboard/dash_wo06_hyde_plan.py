"""WO-06 item 2 (scratch): EXPLAIN ANALYZE of the HYDE Band T query for a polity, at a short and a long step count.

Reads only. Captures the SQL _band_t_hyde sends, runs it under EXPLAIN (ANALYZE, BUFFERS) and prints the plan
without the polygon text. Usage: python dash_wo06_hyde_plan.py
"""
import re
import time

import pandas as pd

from app.db.connection import db_connect
from scripts.edop.areas import engine

SPANS = [(1000, 1099), (1000, 1799), (1200, 1999)]


def main():
    conn = db_connect()
    geom_wkt, _, _ = engine.resolve_polity("Northern Song", 1000, 6, conn)
    captured = {}
    real = pd.read_sql

    def grab(sql, con, *a, **k):
        captured["sql"] = sql
        return real(sql, con, *a, **k)

    engine.pd.read_sql = grab
    for lo, hi in SPANS:
        q = engine._band_t_query(34.0, 113.0, 25, lo, hi, conn, geom_wkt, 1000)
        engine._band_t_hyde(q)
        sql = captured["sql"]
        t0 = time.perf_counter()
        plan = conn.execute("EXPLAIN (ANALYZE, BUFFERS) " + sql).fetchall()
        dt = time.perf_counter() - t0
        print(f"\n=== {lo}-{hi}  EXPLAIN ANALYZE {dt:.1f} s ===")
        for (line,) in plan:
            print(re.sub(r"ST_GeomFromText\('[^']{200,}'", "ST_GeomFromText('<polygon>'", line)[:230])


if __name__ == "__main__":
    main()
