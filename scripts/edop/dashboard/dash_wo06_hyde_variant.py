"""WO-06 item 2 (scratch): does computing HYDE's cell overlap once per cell, not once per cell-and-step pair, remove the cost?

Reads only. Takes the SQL _band_t_hyde sends for Northern Song, 1200-1999, runs it as sent and with cell_overlaps
MATERIALIZED, under EXPLAIN (ANALYZE) and prints the execution times and the top plan lines. Usage: python dash_wo06_hyde_variant.py
"""
import re

import pandas as pd

from app.db.connection import db_connect
from scripts.edop.areas import engine


def main():
    conn = db_connect()
    geom_wkt, _, _ = engine.resolve_polity("Northern Song", 1000, 6, conn)
    captured = {}
    real = pd.read_sql

    def grab(sql, con, *a, **k):
        captured["sql"] = sql
        return real(sql, con, *a, **k)

    engine.pd.read_sql = grab
    q = engine._band_t_query(34.0, 113.0, 25, 1200, 1999, conn, geom_wkt, 1000)
    engine._band_t_hyde(q)
    base = captured["sql"]
    assert base.count("cell_overlaps AS (") == 1
    for label, sql in [("as sent", base), ("materialized", base.replace("cell_overlaps AS (", "cell_overlaps AS MATERIALIZED ("))]:
        plan = [r[0] for r in conn.execute("EXPLAIN (ANALYZE) " + sql).fetchall()]
        print(f"\n=== {label} ===")
        for line in plan:
            if "Execution Time" in line or re.match(r"^\S|^  ->  (Nested|Hash|CTE|Gather)", line):
                print(re.sub(r"'0106[0-9A-F]+'", "'<polygon>'", line)[:200])


if __name__ == "__main__":
    main()
