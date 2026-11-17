"""WO-06 item 1 (scratch): total cost of _band_t_hyde for a polity with cell_overlaps MATERIALIZED, against the query as sent.

Reads only; the engine is not changed (the SQL is rewritten in a spy around pd.read_sql). For each span it times the whole
function, the SQL-and-transfer part (read_sql) and the rest (grouping and row building), as sent and fixed, and checks that
the rows agree. Writes output/edop/dashboard/wo06_hyde_fixed.csv. Usage: python dash_wo06_hyde_fixed_total.py [polity name] [resolver year]   (default Northern Song, 1000)
"""
import csv
import sys
import time
from pathlib import Path

import pandas as pd

from app.db.connection import db_connect
from scripts.edop.areas import engine

SPANS = [(1000, 1099), (1000, 1799), (1200, 1999), (1000, 1999)]
NAME = sys.argv[1] if len(sys.argv) > 1 else "Northern Song"
YEAR = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
OUT = Path(__file__).resolve().parents[3] / "output" / "edop" / "dashboard" / f"wo06_hyde_fixed_{NAME.replace(' ', '_')}.csv"


def main():
    conn = db_connect()
    geom_wkt, _, _ = engine.resolve_polity(NAME, YEAR, 6, conn)
    real = pd.read_sql
    state = {"fix": False, "sql_s": 0.0, "rows": 0}

    def spy(sql, con, *a, **k):
        if state["fix"]:
            sql = sql.replace("cell_overlaps AS (", "cell_overlaps AS MATERIALIZED (")
        t0 = time.perf_counter()
        df = real(sql, con, *a, **k)
        state["sql_s"] += time.perf_counter() - t0
        state["rows"] = len(df)
        return df

    engine.pd.read_sql = spy
    out = []
    for lo, hi in SPANS:
        results = {}
        for label, fix in [("as_sent", False), ("fixed", True)]:
            state.update(fix=fix, sql_s=0.0)
            q = engine._band_t_query(34.0, 113.0, 25, lo, hi, conn, geom_wkt, YEAR)
            t0 = time.perf_counter()
            res = engine._band_t_hyde(q)
            total = time.perf_counter() - t0
            results[label] = res.rows
            out.append(dict(start=lo, end=hi, variant=label, rows_out=len(res.rows), rows_pulled=state["rows"], total_s=round(total, 2),
                            read_sql_s=round(state["sql_s"], 2), python_s=round(total - state["sql_s"], 2)))
            print(out[-1], flush=True)
        a, b = results["as_sent"], results["fixed"]
        same = len(a) == len(b) and all(x["variable"] == y["variable"] and x["year"] == y["year"]
                                        and abs((x["representative_raw"] or 0) - (y["representative_raw"] or 0)) < 1e-6 * max(1, abs(x["representative_raw"] or 0))
                                        for x, y in zip(a, b))
        print(f"  {lo}-{hi}: rows agree = {same}", flush=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
