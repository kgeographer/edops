"""Persist point elevation for every dplace.societies row with coordinates.

Standing infrastructure move (Karl, WO8c pre-work): elevation is going to matter increasingly
across CDOP, so it is fetched once for the whole D-PLACE society table (6,684 rows, not just the
EA slice WO8c needs) rather than re-derived per-WO. Same two-provider fallback chain as
`app/db/signature.py:get_elevation_point` (OpenTopoData mapzen -> Open-Meteo/Copernicus GLO-90),
but batched: OpenTopoData's public API takes up to 100 locations per request (1 req/sec, 1000
req/day), so the whole table costs ~70 requests, not 6,684 round trips.

Writes `dplace.society_elevation` (soc_id PK, elev_point, elev_source, elev_dataset,
elev_resolution_m), the same shape as the per-point fields `signature.py` already returns, and the
same "small derived table keyed by soc_id" convention as `dplace.society_basin` /
`dplace.society_spatial` (WO4). `dplace.societies` itself is left untouched (schema comment: no
modifications to source data).

Usage:
    python scripts/cdop/persist_dplace_elevation.py
"""
from __future__ import annotations

import json
import ssl
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlencode
from urllib.request import Request, urlopen

try:
    import certifi
except ImportError:
    certifi = None

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.shared.db_utils import db_connect

BATCH_SIZE = 100          # OpenTopoData public API cap
REQ_INTERVAL_S = 1.05     # stay under the 1 req/sec cap with margin
TIMEOUT_S = 15.0

DDL = """
CREATE TABLE IF NOT EXISTS dplace.society_elevation (
    soc_id            text PRIMARY KEY REFERENCES dplace.societies(id),
    elev_point        double precision,
    elev_source       text,
    elev_dataset      text,
    elev_resolution_m integer,
    elev_error        text
);
"""


def _http_get_json(url: str) -> Dict[str, Any]:
    req = Request(url, headers={"Accept": "application/json", "User-Agent": "edop-cdop/0.1"}, method="GET")
    ctx = ssl.create_default_context(cafile=certifi.where()) if certifi else ssl.create_default_context()
    with urlopen(req, timeout=TIMEOUT_S, context=ctx) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _batch_mapzen(coords: List[Tuple[str, float, float]]) -> Dict[str, Dict[str, Any]]:
    """coords: [(soc_id, lat, lon), ...], len <= BATCH_SIZE. Returns {soc_id: result_dict}."""
    locs = "|".join(f"{lat},{lon}" for _, lat, lon in coords)
    url = f"https://api.opentopodata.org/v1/mapzen?{urlencode({'locations': locs})}"
    payload = _http_get_json(url)
    out: Dict[str, Dict[str, Any]] = {}
    if payload.get("status") != "OK":
        return out
    results = payload.get("results") or []
    for (soc_id, _, _), r in zip(coords, results):
        elev = r.get("elevation")
        if elev is not None:
            out[soc_id] = {
                "elev_point": float(elev),
                "elev_source": "opentopodata",
                "elev_dataset": "mapzen",
                "elev_resolution_m": 30,
            }
    return out


def _single_open_meteo(lat: float, lon: float) -> Optional[Dict[str, Any]]:
    url = f"https://api.open-meteo.com/v1/elevation?{urlencode({'latitude': str(lat), 'longitude': str(lon)})}"
    try:
        payload = _http_get_json(url)
    except Exception:
        return None
    elev = None
    if isinstance(payload.get("elevation"), list) and payload["elevation"]:
        elev = payload["elevation"][0]
    elif payload.get("elevation") is not None:
        elev = payload.get("elevation")
    if elev is None:
        return None
    return {
        "elev_point": float(elev),
        "elev_source": "open-meteo",
        "elev_dataset": "copernicus-dem-glo-90-2021",
        "elev_resolution_m": 90,
    }


def main() -> None:
    conn = db_connect()
    cur = conn.cursor()
    cur.execute(DDL)
    conn.commit()

    cur.execute("""
        SELECT id, latitude, longitude FROM dplace.societies
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
    """)
    rows = cur.fetchall()
    print(f"societies with coordinates: {len(rows)}")

    results: Dict[str, Dict[str, Any]] = {}
    misses: List[Tuple[str, float, float]] = []

    for i in range(0, len(rows), BATCH_SIZE):
        batch = rows[i:i + BATCH_SIZE]
        coords = [(soc_id, lat, lon) for soc_id, lat, lon in batch]
        try:
            got = _batch_mapzen(coords)
        except Exception as e:
            print(f"  batch {i}-{i + len(batch)}: mapzen request failed ({e}); all fall through to Open-Meteo")
            got = {}
        results.update(got)
        for soc_id, lat, lon in coords:
            if soc_id not in got:
                misses.append((soc_id, lat, lon))
        print(f"  batch {i // BATCH_SIZE + 1}/{(len(rows) - 1) // BATCH_SIZE + 1}: "
              f"{len(got)}/{len(coords)} via mapzen, {len(coords) - len(got)} pending fallback")
        time.sleep(REQ_INTERVAL_S)

    print(f"mapzen misses requiring Open-Meteo fallback: {len(misses)}")
    for soc_id, lat, lon in misses:
        r = _single_open_meteo(lat, lon)
        if r is not None:
            results[soc_id] = r
        time.sleep(0.2)

    all_ids = [r[0] for r in rows]
    failed = [sid for sid in all_ids if sid not in results]
    print(f"resolved: {len(results)} / {len(all_ids)}  |  failed both providers: {len(failed)}")

    write_rows = []
    for soc_id in all_ids:
        r = results.get(soc_id)
        if r is not None:
            write_rows.append((soc_id, r["elev_point"], r["elev_source"], r["elev_dataset"],
                               r["elev_resolution_m"], None))
        else:
            write_rows.append((soc_id, None, None, None, None, "both providers failed"))

    cur.executemany("""
        INSERT INTO dplace.society_elevation (soc_id, elev_point, elev_source, elev_dataset, elev_resolution_m, elev_error)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (soc_id) DO UPDATE SET
            elev_point = EXCLUDED.elev_point, elev_source = EXCLUDED.elev_source,
            elev_dataset = EXCLUDED.elev_dataset, elev_resolution_m = EXCLUDED.elev_resolution_m,
            elev_error = EXCLUDED.elev_error
    """, write_rows)
    conn.commit()
    print(f"wrote {len(write_rows)} rows -> dplace.society_elevation")
    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
