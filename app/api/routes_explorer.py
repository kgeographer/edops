"""
app/api/routes_explorer.py
----------------------------
Routes used only by the Data Explorer page (explorer.html). See
docs/edop/routes_audit.txt for how this classification was derived —
re-run that audit if explorer.html's calls change. /explorer/values itself
is shared (sandbox.html, cliopatria.html too) and lives in routes_common.py.
"""
from pathlib import Path
from typing import Dict

from fastapi import APIRouter, HTTPException

from app.db.connection import db_connect
from app.api.routes_common import _load_variables

router = APIRouter(prefix="/api", tags=["api"])


@router.get("/explorer/variables", include_in_schema=False)
def explorer_variables():
    return _load_variables()


_lisa_df_cache = None

def _load_lisa_df():
    global _lisa_df_cache
    if _lisa_df_cache is not None:
        return _lisa_df_cache
    import pandas as pd
    p = Path(__file__).resolve().parents[2] / "output" / "edop" / "esda" / "lisa_classifications.parquet"
    if not p.exists():
        return None
    _lisa_df_cache = pd.read_parquet(p)
    return _lisa_df_cache


@router.get("/explorer/lisa", include_in_schema=False)
def explorer_lisa(var: str, level: int = 8):
    """Return per-basin LISA class assignments for one variable at one scale.

    Returns a flat dict {str(hybas_id): lisa_class} for O(1) JS lookup.
    No geometry — client reuses the already-loaded choropleth layer.
    """
    cb = _load_variables()
    row = next((r for r in cb if r["schema_key"] == var), None)
    if not row:
        raise HTTPException(status_code=404, detail=f"Variable '{var}' not found")

    col_s = row.get("basin08_col_s")
    if not col_s:
        raise HTTPException(status_code=404, detail=f"No basin column for '{var}'")
    if level not in (6, 8):
        raise HTTPException(status_code=400, detail="level must be 6 or 8")

    df = _load_lisa_df()
    if df is None:
        raise HTTPException(status_code=503, detail="LISA parquet not found")

    scale = f"L{level}"
    sub = df[(df["variable"] == col_s) & (df["scale"] == scale)][["hybas_id", "lisa_class"]]
    if sub.empty:
        raise HTTPException(
            status_code=404,
            detail=f"No LISA data for '{var}' at L{level} — run the L{level} sweep first"
        )

    counts = sub["lisa_class"].value_counts().to_dict()
    classes = dict(zip(sub["hybas_id"].astype(int).astype(str), sub["lisa_class"]))
    return {
        "meta": {"var": var, "col": col_s, "level": level, "n": len(sub), "counts": counts},
        "classes": classes,
    }


# Lookup table registry for categorical variables.
# (lu_table, id_col, name_col)  — id_col joins to basin08_col_s (cast to text both sides)
_CAT_LOOKUP: Dict[str, tuple] = {
    "lithology_name":             ("lu_lit", "id",       "class_name"),
    "climate_zone_name":          ("lu_clz", "genz_id",  "genz_name"),
    "climate_stratum_code":       ("lu_cls", "gens_id",  "gens_code"),
    "biome_name":                 ("lu_tbi", "biome_id", "biome_name"),
    "ecoregion_terrestrial_name": ("lu_tec", "eco_id",   "ecoregion_name"),
    "pnv_majority_name":          ("lu_pnv", "pnv_id",   "pnv_name"),
    "freshwater_habitat_name":    ("lu_fmh", "mht_id",   "mht_name"),
    "freshwater_ecoregion_name":  ("lu_fec", "eco_id",   "ecoregion_name"),
    "land_cover_name":            ("lu_glc", "glc_id",   "glc_name"),
}

# Qualitative palette (20 colours, Tableau-like)
_QUAL_PALETTE = [
    "#4e79a7","#f28e2b","#e15759","#76b7b2","#59a14f",
    "#edc948","#b07aa1","#ff9da7","#9c755f","#bab0ac",
    "#1f77b4","#ff7f0e","#2ca02c","#d62728","#9467bd",
    "#8c564b","#e377c2","#7f7f7f","#bcbd22","#17becf",
]
_OTHER_COLOR = "#cccccc"
_TOP_N = 20   # classes beyond this are collapsed to "Other"

@router.get("/explorer/categorical", include_in_schema=False)
def explorer_categorical(var: str, level: int = 6):
    """Return category counts + flat {hybas_id: cat_id} dict for a categorical variable.

    Categories are sorted by basin count descending; if more than _TOP_N unique
    classes exist, the tail is collapsed to an 'Other' entry (cat_id = -1).
    Response: {meta: {...}, categories: [...], values: {hybas_id: cat_id, ...}}
    """
    cb = _load_variables()
    row = next((r for r in cb if r["schema_key"] == var), None)
    if not row:
        raise HTTPException(status_code=404, detail=f"Variable '{var}' not found")
    if var not in _CAT_LOOKUP:
        raise HTTPException(status_code=400, detail=f"'{var}' has no categorical lookup")

    basin_col = row.get("basin08_col_s")
    if not basin_col:
        raise HTTPException(status_code=400, detail=f"'{var}' has no basin column")
    if level not in (6, 8):
        raise HTTPException(status_code=400, detail="level must be 6 or 8")

    basin_table = "basin06" if level == 6 else "basin08"
    lu_table, lu_id_col, lu_name_col = _CAT_LOOKUP[var]

    try:
        conn = db_connect()
        with conn.cursor() as cur:
            # 1. Category counts with names (cast both sides to text for type safety)
            cur.execute(f"""
                SELECT lu.{lu_name_col} AS cat_name,
                       b.{basin_col}    AS cat_id,
                       COUNT(*)         AS cnt
                FROM public.{basin_table} b
                LEFT JOIN public.{lu_table} lu
                    ON b.{basin_col}::text = lu.{lu_id_col}::text
                WHERE b.{basin_col} IS NOT NULL
                GROUP BY b.{basin_col}, lu.{lu_name_col}
                ORDER BY cnt DESC
            """)
            count_rows = cur.fetchall()   # (cat_name, cat_id, cnt)

            # 2. Determine top-N set; anything beyond is "Other"
            n_total_basins = sum(r[2] for r in count_rows)
            top_rows  = count_rows[:_TOP_N]
            tail_rows = count_rows[_TOP_N:]
            top_ids   = {r[1] for r in top_rows}

            categories = []
            for i, (cat_name, cat_id, cnt) in enumerate(top_rows):
                categories.append({
                    "id":    cat_id,
                    "name":  cat_name or f"Class {cat_id}",
                    "count": cnt,
                    "pct":   round(100 * cnt / n_total_basins, 2) if n_total_basins else 0,
                    "color": _QUAL_PALETTE[i % len(_QUAL_PALETTE)],
                })
            if tail_rows:
                other_cnt = sum(r[2] for r in tail_rows)
                categories.append({
                    "id":    -1,
                    "name":  f"Other ({len(tail_rows)} classes)",
                    "count": other_cnt,
                    "pct":   round(100 * other_cnt / n_total_basins, 2) if n_total_basins else 0,
                    "color": _OTHER_COLOR,
                })

            # 3. Flat values — cat_id per basin
            cur.execute(f"""
                SELECT hybas_id, {basin_col} AS cat_id
                FROM public.{basin_table}
                ORDER BY hybas_id
            """)
            val_rows = cur.fetchall()

        values = {
            int(r[0]): (r[1] if (r[1] in top_ids) else -1)
            for r in val_rows
        }
        return {
            "meta": {
                "var": var, "level": level,
                "n_classes": len(count_rows),
                "n_shown":   len(top_rows),
                "n_basins":  n_total_basins,
            },
            "categories": categories,
            "values": values,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if "conn" in locals():
            conn.close()


# ---------------------------------------------------------------------------
# Band T: Explorer endpoints
# ---------------------------------------------------------------------------

@router.get("/explorer/evolv2k", include_in_schema=False)
def explorer_evolv2k():
    """Return complete eVolv2k v4 event catalog (256 events). Client-side filtering.

    lat is approximate source latitude only; no longitude in source data.
    Events with lat=0 are equatorial; lat=±45 are unlocated NH/SH defaults.
    """
    with db_connect() as conn:
        rows = conn.execute("""
            SELECT year_ad, month, lat, vssi_tg, vssi_1sig, asymmetry, location, tephra
            FROM temporal.evolv2k_v4
            ORDER BY year_ad
        """).fetchall()
    events = [
        {
            "year":      int(r[0]),
            "month":     int(r[1]) if r[1] is not None else None,
            "lat":       float(r[2]) if r[2] is not None else None,
            "vssi_tg":   round(float(r[3]), 2),
            "vssi_1sig": round(float(r[4]), 2) if r[4] is not None else None,
            "asymmetry": round(float(r[5]), 3) if r[5] is not None else None,
            "location":  r[6],
            "tephra":    bool(r[7]) if r[7] is not None else None,
        }
        for r in rows
    ]
    return {
        "meta": {
            "count":    len(events),
            "year_min": min(e["year"] for e in events),
            "year_max": max(e["year"] for e in events),
            "note": (
                "eVolv2k v4 (Sigl & Toohey 2024). lat = approximate source latitude; "
                "no longitude in source data. lat=0 → equatorial default; "
                "lat=±45 → unlocated NH/SH default."
            ),
        },
        "events": events,
    }


# ---------------------------------------------------------------------------
# Explorer: region definitions
# ---------------------------------------------------------------------------

_REGIONS = [
    {
        "id":    "east_asia",
        "label": "East Asia",
        "bbox":  [95, 18, 145, 55],   # [west, south, east, north]
        "zoom":  4,
    },
    {
        "id":    "south_asia",
        "label": "South Asia",
        "bbox":  [60, 5, 100, 38],
        "zoom":  4,
    },
    {
        "id":    "southwest_asia",
        "label": "Southwest Asia",
        "bbox":  [25, 13, 65, 45],
        "zoom":  4,
    },
    {
        "id":    "mediterranean",
        "label": "Mediterranean & N. Africa",
        "bbox":  [-10, 15, 42, 50],
        "zoom":  4,
    },
    {
        "id":    "mesoamerica",
        "label": "Mesoamerica",
        "bbox":  [-120, 5, -65, 35],
        "zoom":  4,
    },
    {
        "id":    "pacific_northwest",
        "label": "Pacific Northwest",
        "bbox":  [-130, 40, -108, 56],
        "zoom":  5,
    },
]

@router.get("/explorer/regions", include_in_schema=False)
def explorer_regions():
    """Return the fixed set of regional bounding boxes used by the Regions tab."""
    return {"regions": _REGIONS}


# ---------------------------------------------------------------------------
# Explorer: bivariate scatter data
# ---------------------------------------------------------------------------

@router.get("/explorer/scatter", include_in_schema=False)
def explorer_scatter(x: str, y: str, level: int = 6):
    """Return paired values for a bivariate scatter plot.

    Both variables use their local ('s') column. NoData (-9999) masked;
    rows where either value is null are excluded. Temperature columns
    (tmp_dc_*) divided by 10 (°C×10 → °C).

    Response:
      {
        "x_meta": {var, label, units, n_total, n_valid},
        "y_meta": {var, label, units, n_total, n_valid},
        "n_paired": int,
        "values": [[hybas_id, x_val, y_val], ...]
      }
    """
    if level not in (6, 8):
        raise HTTPException(status_code=400, detail="level must be 6 or 8")

    cb = _load_variables()

    def _resolve(var_key: str):
        row = next((r for r in cb if r["schema_key"] == var_key), None)
        if not row:
            raise HTTPException(status_code=404, detail=f"Variable '{var_key}' not found")
        col = row.get("basin08_col_s")
        if not col:
            raise HTTPException(status_code=400, detail=f"'{var_key}' has no local column")
        if row.get("monthly_series"):
            col = col.split("..")[0][:-2] + "01"   # default to January for monthly vars
        return row, col

    x_row, x_col = _resolve(x)
    y_row, y_col = _resolve(y)

    basin_table = "basin06" if level == 6 else "basin08"
    NODATA = -9999

    def _expr(col: str, alias: str) -> str:
        if col.startswith("tmp_dc_"):
            return f"CASE WHEN {col} = {NODATA} THEN NULL ELSE ({col}::float / 10.0) END AS {alias}"
        return f"CASE WHEN {col} = {NODATA} THEN NULL ELSE {col}::float END AS {alias}"

    sql = f"""
        SELECT hybas_id,
               {_expr(x_col, 'xv')},
               {_expr(y_col, 'yv')}
        FROM public.{basin_table}
        ORDER BY hybas_id
    """

    try:
        conn = db_connect()
        with conn.cursor() as cur:
            cur.execute(sql)
            rows = cur.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if "conn" in locals():
            conn.close()

    n_total = len(rows)
    paired = [[int(r[0]), r[1], r[2]] for r in rows if r[1] is not None and r[2] is not None]

    def _meta(row, col, n_paired):
        return {
            "var":     row["schema_key"],
            "col":     col,
            "label":   row.get("friendly_name") or row["schema_key"],
            "units":   row.get("units") or "",
            "n_total": n_total,
            "n_valid": n_paired,
        }

    return {
        "x_meta":   _meta(x_row, x_col, len(paired)),
        "y_meta":   _meta(y_row, y_col, len(paired)),
        "n_paired": len(paired),
        "values":   paired,
    }
