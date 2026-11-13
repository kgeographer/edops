"""
app/db/temporal.py
------------------
Temporal enrichment lookups for the EDOP signature API.

Functions:
  get_temporal_context(lat, lon, year_start, year_end, vssi_min)
    Returns LMR v2.1 climate time series (PDSI, air temperature, precipitation rate)
    and significant volcanic events (eVolv2k v4) for a given location and year range.

Array indexing note:
  PostgreSQL arrays are 1-indexed. Year Y CE is stored at arr[Y+1].
  Slice year_start–year_end → arr[year_start+1 : year_end+1].

Units (all LMR variables are anomalies relative to a reference period):
  pdsi  : Palmer Drought Severity Index anomaly (dimensionless)
  air   : 2m air temperature anomaly (K)
  prate : precipitation rate anomaly (kg/m²/s) — multiply by 86400 for mm/day anomaly
"""

from typing import Any, Dict, List, Optional
from app.db.connection import db_connect



# Coverage constants for each temporal layer
LMR_MIN, LMR_MAX         = 0, 2000      # LMR v2.1 proxy reanalysis window
EVOLV2K_MIN, EVOLV2K_MAX = -491, 1890   # eVolv2k v4 actual DB range


def get_temporal_context(
    lat: float,
    lon: float,
    year_start: int = 0,
    year_end: int = 2000,
    vssi_min: float = 5.0,
) -> Dict[str, Any]:
    """
    Return PDSI time series and volcanic events for a location and year range.

    LMR and eVolv2k are handled independently:
      - LMR covers 0–2000 CE; queries outside this range return empty series
        with lmr_status = "out_of_range".
      - eVolv2k covers −491–1890 CE; volcanic events are returned for any
        requested window within that range, even when LMR is unavailable.

    Parameters
    ----------
    lat, lon      : query coordinates (used to find nearest 2° LMR grid cell)
    year_start    : first year to include (negative = BCE); default 0
    year_end      : last year to include; default 2000
    vssi_min      : minimum VSSI (Tg) to include a volcanic event; default 5.0

    Returns
    -------
    dict with keys:
      lmr_status              : "available" | "out_of_range"
      grid_cell               : {lat, lon} of nearest LMR 2° cell (None if out_of_range)
      year_start              : requested start year
      year_end                : requested end year
      pdsi_series             : list of {year, pdsi} dicts (empty if LMR out of range)
      pdsi_mean / pdsi_min / pdsi_max
      air_series              : list of {year, air_anom_k} dicts
      air_mean_anom_k
      prate_series            : list of {year, prate_anom_mm_day} dicts
      prate_mean_anom_mm_day
      volcanic_events         : list of eruption dicts with vssi_tg >= vssi_min
      volcanic_event_count    : count of events in window
      volcanic_vssi_sum_tg    : total VSSI in window
      years_since_last_major  : years from last event >= 10 Tg to year_end (None if none)
      volcanic_events_note    : coverage warning when year_end > EVOLV2K_MAX
    """
    # Determine LMR availability for the requested window
    lmr_available = (year_end >= LMR_MIN and year_start <= LMR_MAX)

    # LMR array bounds — clamped to valid range (PostgreSQL arrays are 1-indexed)
    lmr_start = max(LMR_MIN, min(year_start, LMR_MAX))
    lmr_end   = max(lmr_start, min(year_end, LMR_MAX))
    pg_start  = lmr_start + 1
    pg_end    = lmr_end + 1

    # eVolv2k query bounds — clamped to catalog range, independent of LMR
    volc_start = max(EVOLV2K_MIN, year_start)
    volc_end   = min(EVOLV2K_MAX, year_end)

    # lon for PostGIS must be −180/180
    lon_geom = lon

    with db_connect() as conn:
        with conn.cursor() as cur:

            # --- LMR nearest-cell lookup ---
            grid_lat = grid_lon_display = None
            series = []
            pdsi_mean = pdsi_min = pdsi_max = None
            air_series, air_mean = [], None
            prate_series, prate_mean = [], None

            if lmr_available:
                cur.execute("""
                    SELECT
                        lat,
                        lon,
                        pdsi[%(pg_start)s  : %(pg_end)s] AS pdsi_slice,
                        air[%(pg_start)s   : %(pg_end)s] AS air_slice,
                        prate[%(pg_start)s : %(pg_end)s] AS prate_slice
                    FROM temporal.lmr_climate
                    ORDER BY geom <-> ST_SetSRID(ST_MakePoint(%(lon)s, %(lat)s), 4326)
                    LIMIT 1
                """, {"lat": lat, "lon": lon_geom, "pg_start": pg_start, "pg_end": pg_end})

                row = cur.fetchone()
                if row is None:
                    return {"error": "No LMR grid cell found"}

                grid_lat, grid_lon, pdsi_slice, air_slice, prate_slice = row

                years = list(range(lmr_start, lmr_end + 1))

                series = [
                    {"year": y, "pdsi": round(float(v), 4)}
                    for y, v in zip(years, pdsi_slice) if v is not None
                ]
                values = [s["pdsi"] for s in series]
                pdsi_mean = round(sum(values) / len(values), 4) if values else None
                pdsi_min  = round(min(values), 4) if values else None
                pdsi_max  = round(max(values), 4) if values else None

                air_series = [
                    {"year": y, "air_anom_k": round(float(v), 4)}
                    for y, v in zip(years, air_slice) if v is not None
                ]
                air_vals = [s["air_anom_k"] for s in air_series]
                air_mean = round(sum(air_vals) / len(air_vals), 4) if air_vals else None

                prate_series = [
                    {"year": y, "prate_anom_mm_day": round(float(v) * 86400, 4)}
                    for y, v in zip(years, prate_slice) if v is not None
                ]
                prate_vals = [s["prate_anom_mm_day"] for s in prate_series]
                prate_mean = round(sum(prate_vals) / len(prate_vals), 4) if prate_vals else None

                # Convert native LMR lon (0–358) to −180/180 for display
                grid_lon_display = float(grid_lon) if float(grid_lon) <= 180 else float(grid_lon) - 360

            # --- eVolv2k volcanic events (independent of LMR availability) ---
            cur.execute("""
                SELECT year_ad, month, vssi_tg, vssi_1sig, asymmetry, location, tephra
                FROM temporal.evolv2k_v4
                WHERE year_ad BETWEEN %(y0)s AND %(y1)s
                  AND vssi_tg >= %(vssi_min)s
                ORDER BY year_ad
            """, {"y0": volc_start, "y1": volc_end, "vssi_min": vssi_min})

            events = [
                {
                    "year_ad":   r[0],
                    "month":     r[1],
                    "vssi_tg":   round(float(r[2]), 2),
                    "vssi_1sig": round(float(r[3]), 2) if r[3] is not None else None,
                    "asymmetry": round(float(r[4]), 3) if r[4] is not None else None,
                    "location":  r[5],
                    "tephra":    r[6],
                }
                for r in cur.fetchall()
            ]

    return {
        "lmr_status":      "available" if lmr_available else "out_of_range",
        "grid_cell":       {"lat": float(grid_lat), "lon": grid_lon_display} if lmr_available else None,
        "year_start":      year_start,
        "year_end":        year_end,
        "pdsi_series":     series,
        "pdsi_mean":       pdsi_mean,
        "pdsi_min":        pdsi_min,
        "pdsi_max":        pdsi_max,
        "air_series":           air_series,
        "air_mean_anom_k":      air_mean,
        "prate_series":         prate_series,
        "prate_mean_anom_mm_day": prate_mean,
        "volcanic_events":      events,
        "volcanic_event_count": len(events),
        "volcanic_vssi_sum_tg": round(sum(e["vssi_tg"] for e in events), 2),
        "years_since_last_major": (
            year_end - max((e["year_ad"] for e in events if e["vssi_tg"] >= 10.0), default=None)
            if any(e["vssi_tg"] >= 10.0 for e in events) else None
        ),
        "volcanic_events_note": (
            f"eVolv2k v4 catalog covers {EVOLV2K_MIN}–{EVOLV2K_MAX} CE; "
            "this period falls outside that range — no volcanic record is available."
            if year_end < EVOLV2K_MIN or year_start > EVOLV2K_MAX else
            f"eVolv2k v4 catalog covers {EVOLV2K_MIN}–{EVOLV2K_MAX} CE; "
            "events after 1890 (e.g. Pinatubo, Agung, El Chichón) are not in the record."
            if year_end > EVOLV2K_MAX else None
        ),
        "lmr_out_of_range_note": (
            f"LMR v2.1 covers 0–2000 CE; climate reconstruction is not available for this period."
            if not lmr_available else None
        ),
        "lmr_fidelity_note": (
            "Climate reconstructions before 700 CE carry greater uncertainty "
            "due to sparser proxy records for this period; treat values as indicative."
            if lmr_available and year_start < 700 else None
        ),
        "lmr_proxy_bias_note": (
            "LMR reconstruction quality is strongest for Europe and North America, "
            "where proxy records are densest; results for East Asia, South Asia, "
            "and the Southern Hemisphere carry greater uncertainty."
            if lmr_available else None
        ),
    }
