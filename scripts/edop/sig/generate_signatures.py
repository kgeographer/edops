"""
generate_signatures.py — Generate rev1 environmental signatures for named place sets.

Queries v_basin08_persist_rev1, fetches point elevation, computes derived
fields, and writes one JSON file per place following edops_schema_basin.json structure.

Usage:
    python scripts/edop/generate_signatures.py set_personal_v1
    python scripts/edop/generate_signatures.py --list
"""
import sys
import json
import argparse
from decimal import Decimal
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from psycopg.rows import dict_row
from scripts.shared.db_utils import db_connect
from app.db.signature import get_elevation_point

PLACE_SETS_FILE = ROOT / "scripts" / "edop" / "place_sets.json"
OUTPUT_DIR      = ROOT / "output" / "edop" / "signatures"

SIGNATURE_SQL = """
SELECT
  id,
  zone_id, zone_name,
  strata_id, strata_code,
  land_cover_id, land_cover_name,

  -- A: Physiographic
  elev_min, elev_max,
  slope_avg, slope_upstream,
  stream_gradient,
  lithology, lith_class,
  karst, karst_upstream,
  permafrost_extent,

  -- B: Hydroclimatic
  discharge_yr, discharge_min, discharge_max,
  river_area, river_area_upstream,
  runoff, gw_table_depth,
  wet_pct_grp1, wet_pct_grp2,
  wet_pct_grp1_upstream, wet_pct_grp2_upstream,
  wetland_class_id, wetland_class,
  reservoir_vol,
  pct_clay, pct_silt, pct_sand,
  pct_clay_upstream, pct_silt_upstream, pct_sand_upstream,

  -- C: Bioclimatic
  temp_yr, temp_min, temp_max, temp_yr_upstream,
  precip_yr, precip_yr_upstream,
  aridity, aridity_upstream,
  biome_id, biome,
  eco_id, ecoregion,
  freshwater_type, freshwater_ecoregion_class,
  freshwater_ecoreg, freshwater_ecoregion_name,
  pnveg_id, pnv_majority, pnv_shares,

  -- D: Anthropocene
  cropland_extent, cropland_extent_upstream,
  pop_density,
  human_footprint_09, human_footprint_09_upstream,
  gdp_avg, human_dev_idx,

  -- Coastality
  dist_sink, endorheic, coast_flag,

  ST_Area(geom::geography) / 1e6 AS sub_area_km2,
  ST_AsGeoJSON(geom, 6) AS geom_geojson

FROM public.v_basin08_persist_rev1
WHERE ST_Covers(
  geom,
  ST_SetSRID(ST_MakePoint(%(lon)s, %(lat)s), 4326)
)
ORDER BY sub_area_km2 ASC
LIMIT 1;
"""


def _outlet_type(endo, coast) -> str:
    if coast:
        return "coastal"
    if endo is not None and int(endo) != 0:
        return "endorheic"
    return "exorheic"


def row_to_signature(row: dict, lat: float, lon: float, name: str, set_name: str) -> dict:
    # Point elevation + derived relief
    elev     = get_elevation_point(lat, lon)
    elev_pt  = elev.get("elev_point")
    elev_min = row.get("elev_min")
    elev_max = row.get("elev_max")

    relief_range = relief_pos = None
    if elev_pt is not None and elev_min is not None and elev_max is not None:
        r = float(elev_max) - float(elev_min)
        if r > 0:
            relief_range = r
            relief_pos   = max(0.0, min(1.0, (float(elev_pt) - float(elev_min)) / r))

    # Coastality
    endo     = row.get("endorheic")
    coast    = row.get("coast_flag")
    dist_raw = row.get("dist_sink")
    dist_km  = round(float(dist_raw), 1) if dist_raw is not None else None

    return {
        "meta": {
            "signature_version": "rev1",
            "generated": datetime.now(timezone.utc).isoformat(),
            "set": set_name,
            "query": {
                "name": name,
                "lat": lat,
                "lon": lon,
                "period": None
            },
            "neighborhood": {
                "type": "containing_basin",
                "basin_level": 8,
                "n_basins": 1
            },
            "data_sources": {
                "basin": "HydroATLAS v1.0 / BasinATLAS",
                "elevation_point": elev.get("elev_source", "unknown")
            }
        },
        "location": {
            "name": name,
            "basin": {
                "hybas_id":     row.get("id"),
                "sub_area_km2": row.get("sub_area_km2"),
                "geom_geojson": row.get("geom_geojson")
            },
            "elevation_point": {
                "value_m":      elev_pt,
                "source":       elev.get("elev_source"),
                "dataset":      elev.get("elev_dataset"),
                "resolution_m": elev.get("elev_resolution_m")
            }
        },
        "signature": {
            "A_physiographic": {
                "elevation": {
                    "min_m": {"s": row.get("elev_min")},
                    "max_m": {"s": row.get("elev_max")}
                },
                "relief_range_m":  relief_range,
                "relief_position": relief_pos,
                "slope_deg": {
                    "s": row.get("slope_avg"),
                    "u": row.get("slope_upstream")
                },
                "stream_gradient_mpm": {"s": row.get("stream_gradient")},
                "lithology": {
                    "class_id":   {"s": row.get("lithology")},
                    "class_name": {"s": row.get("lith_class")}
                },
                "karst_pct": {
                    "s": row.get("karst"),
                    "u": row.get("karst_upstream")
                },
                "permafrost_pct": {"s": row.get("permafrost_extent")}
            },
            "B_hydroclimatic": {
                "discharge_m3s": {
                    "annual":      {"s": row.get("discharge_yr")},
                    "min_monthly": {"s": row.get("discharge_min")},
                    "max_monthly": {"s": row.get("discharge_max")}
                },
                "runoff_mmyr":          {"s": row.get("runoff")},
                "groundwater_depth_cm": {"s": row.get("gw_table_depth")},
                "river_area_ha": {
                    "s": row.get("river_area"),
                    "u": row.get("river_area_upstream")
                },
                "wetland_pct": {
                    "group1": {"s": row.get("wet_pct_grp1"), "u": row.get("wet_pct_grp1_upstream")},
                    "group2": {"s": row.get("wet_pct_grp2"), "u": row.get("wet_pct_grp2_upstream")}
                },
                "wetland_class": {
                    "id":   {"s": row.get("wetland_class_id")},
                    "name": {"s": row.get("wetland_class")}
                },
                "reservoir_vol_upstream": {"u": row.get("reservoir_vol")},
                "soil_texture": {
                    "clay_pct": {"s": row.get("pct_clay"), "u": row.get("pct_clay_upstream")},
                    "silt_pct": {"s": row.get("pct_silt"), "u": row.get("pct_silt_upstream")},
                    "sand_pct": {"s": row.get("pct_sand"), "u": row.get("pct_sand_upstream")}
                }
            },
            "C_bioclimatic": {
                "climate_zone": {
                    "id":   {"s": row.get("zone_id")},
                    "name": {"s": row.get("zone_name")}
                },
                "climate_stratum": {
                    "id":   {"s": row.get("strata_id")},
                    "code": {"s": row.get("strata_code")}
                },
                "temperature_c": {
                    "annual_mean": {
                        "s": row.get("temp_yr"),
                        "u": row.get("temp_yr_upstream")
                    },
                    "min_monthly": {"s": row.get("temp_min")},
                    "max_monthly": {"s": row.get("temp_max")}
                },
                "precipitation_mmyr": {
                    "annual": {
                        "s": row.get("precip_yr"),
                        "u": row.get("precip_yr_upstream")
                    }
                },
                "aridity_index": {
                    "s": row.get("aridity"),
                    "u": row.get("aridity_upstream")
                },
                "biome": {
                    "id":   {"s": row.get("biome_id")},
                    "name": {"s": row.get("biome")}
                },
                "ecoregion_terrestrial": {
                    "id":   {"s": row.get("eco_id")},
                    "name": {"s": row.get("ecoregion")}
                },
                "ecoregion_freshwater": {
                    "class_id":    {"s": row.get("freshwater_type")},
                    "class_name":  {"s": row.get("freshwater_ecoregion_class")},
                    "region_id":   {"s": row.get("freshwater_ecoreg")},
                    "region_name": {"s": row.get("freshwater_ecoregion_name")}
                },
                "potential_natural_vegetation": {
                    "majority_id":   {"s": row.get("pnveg_id")},
                    "majority_name": {"s": row.get("pnv_majority")},
                    "shares":        {"s": row.get("pnv_shares")}
                }
            },
            "D_anthropocene": {
                "population_density_pkm2": {"s": row.get("pop_density")},
                "cropland_pct": {
                    "s": row.get("cropland_extent"),
                    "u": row.get("cropland_extent_upstream")
                },
                "human_footprint_2009": {
                    "s": row.get("human_footprint_09"),
                    "u": row.get("human_footprint_09_upstream")
                },
                "gdp_usd_km2": {"s": row.get("gdp_avg")},
                "hdi":         {"s": row.get("human_dev_idx")}
            },
            "coastality": {
                "dist_sink_km": dist_km,
                "outlet_type":  _outlet_type(endo, coast),
                "endorheic":    bool(int(endo)) if endo is not None else None,
                "coast_flag":   bool(int(coast)) if coast is not None else None
            },
            "temporal": {
                "period_ce": None,
                "lmr":       None,
                "evolv2k":   None
            }
        },
        "narrative": None
    }


def generate(set_name: str) -> None:
    sets = json.loads(PLACE_SETS_FILE.read_text())
    if set_name not in sets:
        print(f"Unknown set '{set_name}'. Available: {list(sets.keys())}")
        sys.exit(1)

    place_set = sets[set_name]
    out_dir   = OUTPUT_DIR / set_name
    out_dir.mkdir(parents=True, exist_ok=True)

    conn = db_connect()
    conn.row_factory = dict_row

    print(f"Set '{set_name}' — {place_set['label']} ({len(place_set['places'])} places)")
    for place in place_set["places"]:
        name = place["name"]
        lat  = place["lat"]
        lon  = place["lon"]
        slug = name.lower().replace(" ", "_").replace("'", "")

        with conn.cursor() as cur:
            cur.execute(SIGNATURE_SQL, {"lat": lat, "lon": lon})
            row = cur.fetchone()

        if not row:
            print(f"  {name}: no basin found — skipped")
            continue

        sig      = row_to_signature(dict(row), lat, lon, name, set_name)
        out_path = out_dir / f"{slug}.json"
        def _json_default(obj):
            if isinstance(obj, Decimal):
                return float(obj)
            return str(obj)

        out_path.write_text(json.dumps(sig, indent=2, ensure_ascii=False, default=_json_default))
        print(f"  {name} → {out_path.relative_to(ROOT)}")

    conn.close()
    print("Done.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate EDOPS rev1 signatures for a named place set."
    )
    parser.add_argument("set_name", nargs="?", help="Place set name")
    parser.add_argument("--list", action="store_true", help="List available place sets")
    args = parser.parse_args()

    sets = json.loads(PLACE_SETS_FILE.read_text())

    if args.list or not args.set_name:
        print("Available place sets:")
        for k, v in sets.items():
            n = len(v["places"])
            print(f"  {k}: {v['label']} ({n} places)")
        sys.exit(0)

    generate(args.set_name)


if __name__ == "__main__":
    main()
