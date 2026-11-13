"""
app/db/hyde.py
--------------
HYDE 3.4 land-use query functions for Band T enrichment.

Returns per-epoch aggregations (cropland, grazing, pasture, rangeland) for a
given location and year window.  One row per HYDE time step that falls within
[from_year, to_year]; values in km² and as % of basin area.

Spatial method: polygon-interior (ST_Within on cell centroid).  Requires the
functional GIST index idx_hyde_cells_centroid on ST_Centroid(geom).

Resolution note (surfaced in every response):
  HYDE 3.4 time steps are millennial before 1 CE, centennial to 1700 CE,
  decadal to 1950, annual thereafter.  BCE queries typically return one epoch.
"""

from typing import Any, Optional

from psycopg.rows import dict_row

from app.db.connection import db_connect

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

HYDE_NOTE = (
    "HYDE 3.5 temporal resolution varies by era: "
    "millennial before 1 CE, centennial to 1700 CE, "
    "decadal to 1950, annual thereafter. "
    "BCE queries typically return a single epoch."
)

_HYBAS_SQL = """
SELECT hybas_id
FROM public.{table}
WHERE ST_Covers(geom, ST_SetSRID(ST_MakePoint(%(lon)s, %(lat)s), 4326))
ORDER BY sub_area ASC
LIMIT 1;
"""

_AGG_SQL = """
WITH basin_cells AS (
    SELECT hc.cropland, hc.grazing, hc.pasture, hc.rangeland, hc.area_km2
    FROM temporal.hyde_cells hc
    JOIN public.{table} b ON b.hybas_id = %(hybas_id)s
    WHERE ST_Within(ST_Centroid(hc.geom), b.geom)
),
steps AS (
    SELECT step_idx, year_ce
    FROM temporal.hyde_times
    WHERE year_ce BETWEEN %(from_year)s AND %(to_year)s
)
SELECT
    s.year_ce,
    -- totals (sum gives km² across all cells in basin)
    SUM(bc.cropland [s.step_idx + 1])::float8                          AS cropland_km2,
    SUM(bc.grazing  [s.step_idx + 1])::float8                          AS grazing_km2,
    SUM(bc.pasture  [s.step_idx + 1])::float8                          AS pasture_km2,
    SUM(bc.rangeland[s.step_idx + 1])::float8                          AS rangeland_km2,
    SUM(bc.area_km2)::float8                                           AS basin_area_km2,
    COUNT(*)::int                                                      AS n_cells,
    -- within-basin heterogeneity: std across cells (all four variables)
    STDDEV_POP(bc.cropland [s.step_idx + 1])::float8                   AS cropland_std,
    STDDEV_POP(bc.grazing  [s.step_idx + 1])::float8                   AS grazing_std,
    STDDEV_POP(bc.pasture  [s.step_idx + 1])::float8                   AS pasture_std,
    STDDEV_POP(bc.rangeland[s.step_idx + 1])::float8                   AS rangeland_std,
    -- p10/p90 for cropland and grazing (primary land-use signals)
    (percentile_cont(0.1) WITHIN GROUP (ORDER BY bc.cropland[s.step_idx + 1]))::float8  AS cropland_p10,
    (percentile_cont(0.9) WITHIN GROUP (ORDER BY bc.cropland[s.step_idx + 1]))::float8  AS cropland_p90,
    (percentile_cont(0.1) WITHIN GROUP (ORDER BY bc.grazing [s.step_idx + 1]))::float8  AS grazing_p10,
    (percentile_cont(0.9) WITHIN GROUP (ORDER BY bc.grazing [s.step_idx + 1]))::float8  AS grazing_p90
FROM basin_cells bc
CROSS JOIN steps s
GROUP BY s.year_ce
ORDER BY s.year_ce;
"""


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _build_epochs(rows: list) -> list[dict[str, Any]]:
    epochs = []
    for row in rows:
        area = float(row['basin_area_km2']) if row['basin_area_km2'] else None
        n = int(row['n_cells'])
        epoch: dict[str, Any] = {
            'year_ce':        int(row['year_ce']),
            'cropland_km2':   round(float(row['cropland_km2']),  3),
            'grazing_km2':    round(float(row['grazing_km2']),   3),
            'pasture_km2':    round(float(row['pasture_km2']),   3),
            'rangeland_km2':  round(float(row['rangeland_km2']), 3),
            'basin_area_km2': round(area, 1) if area else None,
            'n_cells':        n,
        }
        # pct = total km² as share of basin area
        if area:
            for var in ('cropland', 'grazing', 'pasture', 'rangeland'):
                epoch[f'{var}_pct'] = round(float(row[f'{var}_km2']) / area * 100, 2)

        # within-basin heterogeneity — only meaningful when n_cells > 1
        if n > 1:
            # std for all four variables (km² per cell, gives sense of patchiness)
            for var in ('cropland', 'grazing', 'pasture', 'rangeland'):
                val = row.get(f'{var}_std')
                if val is not None:
                    epoch[f'{var}_std'] = round(float(val), 3)
            # p10/p90 for cropland and grazing (primary land-use signals)
            for var in ('cropland', 'grazing'):
                for pctile in ('p10', 'p90'):
                    val = row.get(f'{var}_{pctile}')
                    if val is not None:
                        epoch[f'{var}_{pctile}'] = round(float(val), 3)

        epochs.append(epoch)
    return epochs


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_hyde_land_use(
    lat: float,
    lon: float,
    from_year: int,
    to_year: int,
    level: int = 8,
) -> dict[str, Any]:
    """Return HYDE 3.4 land-use summary for a point location and year window.

    Resolves the containing basin from (lat, lon), then aggregates HYDE cells
    within that basin for each time step in [from_year, to_year].

    Args:
        lat, lon:  WGS-84 coordinates of the query point.
        from_year: Start year (astronomical; negative = BCE).
        to_year:   End year (astronomical).
        level:     Basin level — 8 (default) or 6.

    Returns:
        {
          "epochs":   [ {year_ce, cropland_km2, grazing_km2, pasture_km2,
                         rangeland_km2, cropland_pct, grazing_pct, pasture_pct,
                         rangeland_pct, basin_area_km2, n_cells}, ... ],
          "n_epochs": int,
          "_note":    str   -- temporal resolution disclosure
        }
        Returns empty epochs list (not None) when no HYDE time steps fall in
        the requested window or no cells are found for the basin.
    """
    table = 'basin08' if level == 8 else 'basin06'

    with db_connect() as conn:
        row = conn.execute(
            _HYBAS_SQL.format(table=table),
            {'lat': lat, 'lon': lon},
        ).fetchone()

        if row is None:
            return {'epochs': [], 'n_epochs': 0, '_note': HYDE_NOTE}

        hybas_id = int(row[0])

        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                _AGG_SQL.format(table=table),
                {'hybas_id': hybas_id, 'from_year': from_year, 'to_year': to_year},
            )
            rows = cur.fetchall()

    epochs = _build_epochs(rows)
    return {
        'epochs':   epochs,
        'n_epochs': len(epochs),
        '_note':    HYDE_NOTE,
    }


def get_hyde_land_use_for_basin(
    hybas_id: int,
    from_year: int,
    to_year: int,
    level: int = 8,
) -> dict[str, Any]:
    """Same as get_hyde_land_use but accepts a known hybas_id directly.

    Useful for scripts and tests where the basin id is already resolved.
    """
    table = 'basin08' if level == 8 else 'basin06'

    with db_connect() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                _AGG_SQL.format(table=table),
                {'hybas_id': hybas_id, 'from_year': from_year, 'to_year': to_year},
            )
            rows = cur.fetchall()

    epochs = _build_epochs(rows)
    return {
        'epochs':   epochs,
        'n_epochs': len(epochs),
        '_note':    HYDE_NOTE,
    }
