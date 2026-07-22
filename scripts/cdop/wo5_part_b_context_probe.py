"""
WO5 Part B -- verify app/db/context.py directly (load_context_index + get_context)
against the DB, before wiring into app startup or a route.

Checks:
  - Sane values/percentiles for known probes (Tbilisi, Kaifeng, Timbuktu, Mombasa)
  - Tbilisi shows near-median global temperature, bottom-few-percent within
    500km -- the accept-gate example from the WO itself
  - Timbuktu shows the documented precipitation inversion (~17th globally,
    ~47th locally) -- cross-check against WO4's independently-computed figures
  - Radius basin counts at 250/500/1000/2500 km, L06 and L08 -- Part B's own
    proviso, informs whether both levels are offered in the UI
"""
import sys
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.shared.db_utils import db_connect
from app.db.context import load_context_index, get_context
from app.api.routes import _resolve_basin  # same basin-containment lookup the route will use

PROBES = {
    "Tbilisi":     (41.6938,   44.8015),
    "Kaifeng":     (34.7986,  114.3413),
    "Timbuktu":    (16.8167,  -2.9833),
    "Mombasa":     (-4.0435,   39.6682),
}

conn = db_connect()

print("Loading L06 context index...")
t0 = time.time()
load_context_index(conn, level=6)
print(f"  done in {time.time()-t0:.1f}s")

print("Loading L08 context index...")
t0 = time.time()
load_context_index(conn, level=8)
print(f"  done in {time.time()-t0:.1f}s")

for name, (lat, lon) in PROBES.items():
    print(f"\n{'='*70}\n{name} ({lat}, {lon})\n{'='*70}")
    for level in (6, 8):
        hybas_id = _resolve_basin(conn, lat, lon) if level == 6 else None
        if level == 8:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT hybas_id FROM public.basin08 "
                    "WHERE ST_Within(ST_SetSRID(ST_MakePoint(%s, %s), 4326), geom) "
                    "ORDER BY ST_Area(geom::geography) ASC LIMIT 1",
                    (lon, lat),
                )
                row = cur.fetchone()
                hybas_id = int(row[0]) if row else None
        if hybas_id is None:
            print(f"  L{level}: no basin resolved")
            continue

        print(f"\n  --- L{level} (hybas_id={hybas_id}) ---")
        for radius in (250, 500, 1000, 2500):
            ctx = get_context(hybas_id, lat, lon, level, radius)
            print(f"  radius={radius}km  count={ctx['radius_count']}")

        # full row detail at 500km and 1000km for eyeballing / cross-check against
        # WO4 Part 5's independently-computed local-anomaly percentiles (n~344 for
        # Tbilisi, n~415 for Timbuktu -- close to this module's L6 1000km counts)
        for radius in (500, 1000):
            ctx = get_context(hybas_id, lat, lon, level, radius)
            print(f"\n  Detail @ {radius}km (n={ctx['radius_count']}):")
            for r in ctx["rows"]:
                print(f"    {r['label']:<28} value={str(r['value']):>10} {r['unit']:<10} "
                      f"global={r['global_percentile']!s:>6}  within{radius}km={r['radius_percentile']!s:>6}")

conn.close()
