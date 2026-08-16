"""
app/api/routes_cliopatria.py
------------------------------
Routes used only by the Cliopatria polity viewer (/polities, eyes-only for ISHI,
no nav link). See docs/edop/routes_audit.txt for how this classification was
derived — re-run that audit if cliopatria.html's calls change.
"""
from collections import defaultdict
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException

from app.db.connection import db_connect
from app.api.routes_common import (
    _HYDE_SAFE_VARS, _HYDE_EPOCH_RANGES, _load_hyde_epoch_maxes,
)

router = APIRouter(prefix="/api", tags=["api"])


@router.get("/polity/period", include_in_schema=False)
def polity_period(year: int):
    """GeoJSON FeatureCollection of all active leaf polities at a given year."""
    try:
        conn = db_connect()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT ST_AsGeoJSON(ST_Simplify(geom, 0.08), 4)::json AS geometry,
                       id, name, seshatid, fromyear, toyear
                FROM gaz.clio_polities
                WHERE fromyear <= %(year)s AND toyear >= %(year)s
                  AND NOT is_component
                  AND NOT COALESCE(invalid_source_geom, false)
                  AND geom IS NOT NULL
                ORDER BY name
            """, {"year": year})
            rows = cur.fetchall()
        features = [
            {"type": "Feature", "geometry": geom,
             "properties": {"id": id_, "name": name, "seshatid": seshatid,
                            "fromyear": fromyear, "toyear": toyear}}
            for geom, id_, name, seshatid, fromyear, toyear in rows
            if geom is not None
        ]
        return {"type": "FeatureCollection", "features": features}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


@router.get("/polity/period/years", include_in_schema=False)
def polity_period_years():
    """Sorted list of distinct fromyear values for non-component polities (for smart stepping)."""
    try:
        conn = db_connect()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT DISTINCT fromyear
                FROM gaz.clio_polities
                WHERE NOT is_component
                ORDER BY fromyear
            """)
            rows = cur.fetchall()
        return [r[0] for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


@router.get("/polity/seshat", include_in_schema=False)
def polity_seshat(seshatid: str):
    """Seshat general + social variables for a polity."""
    GENERAL_FIELDS = [
        'original_name', 'capital', 'language', 'linguistic_family',
        'religion', 'religion_family', 'religion_genus',
        'degree_of_centralization', 'duration', 'peak_years',
        'alternative_name', 'supracultural_entity',
        'preceding_entity', 'succeeding_entity',
    ]
    NUMERIC_VARS = {
        'polity_population', 'polity_territory',
        'population_of_the_largest_settlement', 'largest_communication_distance',
        'administrative_level', 'military_level', 'religious_level', 'settlement_hierarchy',
    }
    BINARY_PRESENT = {'present', 'a~p', 'p~a'}

    try:
        conn = db_connect()
        with conn.cursor() as cur:
            # General variables
            cur.execute("""
                SELECT variable_name, value_from, value_to
                FROM seshat.general
                WHERE polity_new_id = %(sid)s AND variable_name = ANY(%(fields)s)
                ORDER BY variable_name, value_from
            """, {"sid": seshatid, "fields": GENERAL_FIELDS})
            gen_rows = cur.fetchall()

            # Social variables — all for this seshatid
            cur.execute("""
                SELECT subsection, variable_name, value_from, value_to
                FROM seshat.social
                WHERE polity_new_id = %(sid)s
                ORDER BY subsection, variable_name
            """, {"sid": seshatid})
            soc_rows = cur.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if "conn" in locals():
            conn.close()

    if not gen_rows and not soc_rows:
        raise HTTPException(status_code=404, detail=f"No Seshat data for '{seshatid}'")

    # Build general dict (multi-value fields become lists)
    general: Dict[str, Any] = {}
    for var, vfrom, vto in gen_rows:
        val = vfrom if not vto else f"{vfrom} – {vto}"
        if var in general:
            if isinstance(general[var], list):
                general[var].append(val)
            else:
                general[var] = [general[var], val]
        else:
            general[var] = val

    # Build social dict grouped by subsection
    # Binary: include only if any value is present/A~P/P~A
    # Numeric: include best (non-unknown) value
    soc_agg: Dict[str, Dict[str, Any]] = defaultdict(dict)  # subsection → {var → {value, type}}
    for subsection, var, vfrom, vto in soc_rows:
        if not vfrom:
            continue
        entry = soc_agg[subsection].get(var)
        if var in NUMERIC_VARS:
            if vfrom.lower() != 'unknown':
                try:
                    num = int(vfrom)
                    # Keep largest value (most informative for pop/territory)
                    if entry is None or num > entry.get('num', -1):
                        soc_agg[subsection][var] = {"type": "numeric", "value": vfrom, "num": num}
                except ValueError:
                    pass
        else:
            # Binary — record if present/transitional; don't overwrite a present with absent
            if vfrom.lower() in BINARY_PRESENT:
                soc_agg[subsection][var] = {"type": "binary", "value": vfrom}
            elif entry is None and vfrom.lower() not in {'uncoded', 'unknown'}:
                soc_agg[subsection][var] = {"type": "binary", "value": vfrom}

    # Serialise: drop internal 'num' key, filter to coded entries only
    social: Dict[str, List[Dict]] = {}
    for subsection, vars_dict in sorted(soc_agg.items()):
        entries = []
        for var, info in sorted(vars_dict.items()):
            entries.append({"var": var, "type": info["type"], "value": info["value"]})
        if entries:
            social[subsection] = entries

    return {"seshatid": seshatid, "general": general, "social": social}


@router.get("/explorer/hyde-epoch-max", include_in_schema=False)
def explorer_hyde_epoch_max(var: str, epoch: int):
    """Return p99 cell-mean fraction for a HYDE variable across one epoch bin.

    Reads from hyde_epoch_maxes.json (written by precompute_hyde_tiles.py) so the
    returned value matches exactly the vmax used when the tiles were baked.
    Falls back to a live DB query (with area_km2 normalisation) if the sidecar is absent.
    """
    if var not in _HYDE_SAFE_VARS:
        raise HTTPException(status_code=400, detail=f"var must be one of {_HYDE_SAFE_VARS}")
    if epoch not in _HYDE_EPOCH_RANGES:
        raise HTTPException(status_code=400, detail="epoch must be 1–7")

    cached = _load_hyde_epoch_maxes()
    p99_cached = cached.get(var)  # one global max per variable, same scale across all epochs
    if p99_cached is not None:
        return {"var": var, "epoch": epoch, "p99_fraction": round(float(p99_cached), 4)}

    # Sidecar not yet generated — fall back to live DB query with correct normalisation.
    y0, y1 = _HYDE_EPOCH_RANGES[epoch]
    sql = f"""
        WITH epoch_steps AS (
            SELECT MIN(step_idx) AS lo, MAX(step_idx) AS hi
            FROM temporal.hyde_times
            WHERE year_ce BETWEEN %(y0)s AND %(y1)s
        ),
        cell_means AS (
            SELECT (
                SELECT AVG(v)
                FROM UNNEST(hc.{var}[
                    (SELECT lo FROM epoch_steps) + 1 :
                    (SELECT hi FROM epoch_steps) + 1
                ]) AS v
            ) / NULLIF(hc.area_km2, 0) AS mean_frac
            FROM temporal.hyde_cells hc
        )
        SELECT percentile_cont(0.99) WITHIN GROUP (ORDER BY mean_frac)
        FROM cell_means
        WHERE mean_frac > 0
    """
    try:
        conn = db_connect()
        with conn.cursor() as cur:
            cur.execute(sql, {"y0": y0, "y1": y1})
            row = cur.fetchone()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if "conn" in locals():
            conn.close()

    p99 = float(row[0]) if row and row[0] is not None else 1.0
    return {"var": var, "epoch": epoch, "p99_fraction": round(p99, 4)}
