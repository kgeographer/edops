"""
Capture exemplar payloads for all five query scopes — lean and detail.

Outputs: output/edop/surface/exemplars/NN_scope_{lean|detail}.json
Run:     python scripts/edop/surface/capture_exemplar_payloads.py

See docs/edop/surface/exemplars/README.md for inspection findings.
"""

import sys
import json
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.shared.db_utils import db_connect
from scripts.edop.areas.engine import (
    single_basin_signature,
    areal_signature,
    areal_signature_polygon,
    basin_ring_signature,
    resolve_polity,
)

# ── fixtures ──────────────────────────────────────────────────────────────────

TIM_LAT, TIM_LON = 16.8167, -2.9833
TIM_RADIUS       = 100.0
LEVEL            = 6
BANDS_AE         = list('ABCDE')
BANDS_AET        = list('ABCDET')

NSONG_NAME  = 'Northern Song'
NSONG_YEAR  = 1000
NSONG_FROM  = 1000
NSONG_TO    = 1100

# 4 Corners / Santa Fe / upper Rio Grande — covers Chaco Canyon, Mesa Verde,
# the Rio Grande corridor through NM, and Santa Fe (35.69°N 105.94°W).
FOUR_CORNERS_WKT = "POLYGON((-110 35, -105.5 35, -105.5 38, -110 38, -110 35))"

OUT = ROOT / 'output' / 'edop' / 'surface' / 'exemplars'
OUT.mkdir(parents=True, exist_ok=True)


# ── serializer ────────────────────────────────────────────────────────────────

def _default(obj):
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    return str(obj)


def save(name, payload):
    p = OUT / name
    with open(p, 'w') as f:
        json.dump(payload, f, indent=2, default=_default)
    kb = p.stat().st_size / 1024
    rows = payload.get('rows') or (
        (payload.get('center') or {}).get('rows') or []
    )
    print(f'  {name:<40s}  {kb:6.1f} KB   rows={len(rows)}')


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    conn = db_connect()
    print(f'Connected: {conn.execute("SELECT current_database()").fetchone()[0]}\n')

    # ── 1. Single basin ───────────────────────────────────────────────────────
    print('Scenario 1 — single basin (Timbuktu L06)')
    save('01_single_basin_lean.json',
         single_basin_signature(TIM_LAT, TIM_LON, conn, level=LEVEL, bands=BANDS_AE))
    save('01_single_basin_detail.json',
         single_basin_signature(TIM_LAT, TIM_LON, conn, level=LEVEL, bands=BANDS_AE,
                                include_detail=True))

    # ── 2. Buffer ─────────────────────────────────────────────────────────────
    print('\nScenario 2 — buffer 100 km (Timbuktu L06)')
    save('02_buffer_lean.json',
         areal_signature(TIM_LAT, TIM_LON, TIM_RADIUS, conn, level=LEVEL, bands=BANDS_AE))
    save('02_buffer_detail.json',
         areal_signature(TIM_LAT, TIM_LON, TIM_RADIUS, conn, level=LEVEL, bands=BANDS_AE,
                         include_detail=True))

    # ── 3. Polity — Northern Song, year=1000, Band T 1000–1100 ───────────────
    print('\nScenario 3 — polity: Northern Song year=1000, Band T 1000–1100')
    geom_wkt, _, meta = resolve_polity(NSONG_NAME, NSONG_YEAR, LEVEL, conn)
    print(f'  polity: {meta["name"]}  {meta["fromyear"]}–{meta["toyear"]}')
    save('03_polity_nsong_lean.json',
         areal_signature_polygon(geom_wkt, conn, level=LEVEL, bands=BANDS_AET,
                                 from_year=NSONG_FROM, to_year=NSONG_TO,
                                 resolver_year=NSONG_YEAR))
    save('03_polity_nsong_detail.json',
         areal_signature_polygon(geom_wkt, conn, level=LEVEL, bands=BANDS_AET,
                                 from_year=NSONG_FROM, to_year=NSONG_TO,
                                 include_detail=True, resolver_year=NSONG_YEAR))

    # ── 4. Basin ring — Timbuktu L06 ─────────────────────────────────────────
    print('\nScenario 4 — basin ring (Timbuktu L06)')
    save('04_basin_ring_lean.json',
         basin_ring_signature(TIM_LAT, TIM_LON, conn, level=LEVEL, bands=BANDS_AE))
    save('04_basin_ring_detail.json',
         basin_ring_signature(TIM_LAT, TIM_LON, conn, level=LEVEL, bands=BANDS_AE,
                              include_detail=True))

    # ── 5. Arbitrary polygon — 4 Corners / Santa Fe / upper Rio Grande ────────
    print('\nScenario 5 — arbitrary polygon (4 Corners / Santa Fe / upper Rio Grande)')
    print('  bbox: lon -110 to -105.5, lat 35 to 38')
    save('05_polygon_4corners_lean.json',
         areal_signature_polygon(FOUR_CORNERS_WKT, conn, level=LEVEL, bands=BANDS_AE))
    save('05_polygon_4corners_detail.json',
         areal_signature_polygon(FOUR_CORNERS_WKT, conn, level=LEVEL, bands=BANDS_AE,
                                 include_detail=True))

    conn.close()
    print(f'\nAll files written to {OUT}')


if __name__ == '__main__':
    main()
