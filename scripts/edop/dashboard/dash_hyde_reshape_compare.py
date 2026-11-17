"""Scratch: the reshaped _band_t_hyde (one row per cell) against the previous one (one row per cell and step).

Reads only. Runs both on a set of cases, checks every row field by field (numbers to 1e-9 relative) and times both.
The previous function is read from the file named by argv[1] (a copy of the old source). Writes nothing.
Usage: python dash_hyde_reshape_compare.py <path to the old function source>
"""
import math
import sys
import time

from app.db.connection import db_connect
from scripts.edop.areas import engine

legacy_src = open(sys.argv[1]).read()
ns = dict(vars(engine))
exec(legacy_src, ns)
legacy = ns["_band_t_hyde"]


def same(a, b, path=""):
    if isinstance(a, dict) and isinstance(b, dict):
        if set(a) != set(b):
            return f"{path}: keys {sorted(set(a) ^ set(b))}"
        for k in a:
            r = same(a[k], b[k], f"{path}.{k}")
            if r:
                return r
        return None
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        if len(a) != len(b):
            return f"{path}: length {len(a)} vs {len(b)}"
        for i, (x, y) in enumerate(zip(a, b)):
            r = same(x, y, f"{path}[{i}]")
            if r:
                return r
        return None
    if isinstance(a, float) and isinstance(b, float):
        return None if math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-12) or (math.isnan(a) and math.isnan(b)) else f"{path}: {a} vs {b}"
    return None if a == b else f"{path}: {a!r} vs {b!r}"


def main():
    conn = db_connect()
    song, _, _ = engine.resolve_polity("Northern Song", 1000, 6, conn)
    croatia, _, _ = engine.resolve_polity("Kingdom of Croatia", 1000, 6, conn)
    seljuk, _, _ = engine.resolve_polity("Seljuk Dynasty", 1000, 6, conn)
    china, _, _ = engine.resolve_polity("People's Republic of China", 1950, 6, conn)
    cases = [("Northern Song 1000-1099", song, 1000, 1000, 1099), ("Northern Song 1000-1399", song, 1000, 1000, 1399),
             ("Northern Song 1000-1799", song, 1000, 1000, 1799), ("Croatia 1000-1999", croatia, 1000, 1000, 1999),
             ("Seljuk 1200-1999", seljuk, 1000, 1200, 1999), ("Northern Song 1010-1020 (nearest step)", song, 1000, 1010, 1020),
             ("Northern Song 1040-1060 (nearest step, a tie)", song, 1000, 1040, 1060), ("China 1950-1952", china, 1950, 1950, 1952),
             ("Lviv buffer 25 km 0-1200", None, None, 0, 1200)]
    for label, wkt, ry, f, t in cases:
        q = engine._band_t_query(49.8397, 24.0297, 25, f, t, conn, wkt, ry)
        t0 = time.perf_counter(); old = legacy(q); t_old = time.perf_counter() - t0
        t0 = time.perf_counter(); new = engine._band_t_hyde(q); t_new = time.perf_counter() - t0
        diff = same(old.rows, new.rows) or same(old.note, new.note)
        print(f"{label:<48} rows {len(old.rows):>4}/{len(new.rows):<4} old {t_old:6.2f} s  new {t_new:6.2f} s  {'IDENTICAL' if not diff else 'DIFFERENT: ' + diff}", flush=True)
    for label, wkt, ry, f, t in [("Northern Song 1000-1999 (new only)", song, 1000, 1000, 1999), ("China 2000-2023 (new only)", china, 1950, 2000, 2023)]:
        q = engine._band_t_query(34.0, 113.0, 25, f, t, conn, wkt, ry)
        t0 = time.perf_counter(); new = engine._band_t_hyde(q)
        print(f"{label:<48} rows {len(new.rows):>4}  new {time.perf_counter() - t0:6.2f} s  (previous: 63.6 s and about 100 s)", flush=True)


if __name__ == "__main__":
    main()
