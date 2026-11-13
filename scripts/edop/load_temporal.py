"""
load_temporal.py
----------------
Creates the temporal schema and loads paleoclimate datasets into cedop:

  1. LMR v2.1 PDSI  — data/lmr_v2.1/pdsi_MCruns_ensemble_mean_LMRv2.1.nc
     16,380 rows (one per 2° grid cell); pdsi[] array of 2001 annual means (0–2000 CE).

  2. eVolv2k v4     — data/volcano/evolv2k_v4.csv
     256 volcanic eruption events, ~500 BCE – 1890 CE.

  3. LMR v2.1 air   — data/lmr_v2.1/air_MCruns_ensemble_mean_LMRv2.1.nc
     2m air temperature; stored as air[] column in temporal.lmr_climate.

  4. LMR v2.1 prate — data/lmr_v2.1/prate_MCruns_ensemble_mean_LMRv2.1.nc
     Precipitation rate; stored as prate[] column in temporal.lmr_climate.

Run from repo root:
    ~/envs/_edop/bin/python3 scripts/edop/load_temporal.py [--lmr] [--evolv2k] [--air] [--prate] [--dry-run]

With no flags, loads all datasets. Use individual flags to load one at a time.
"""

import argparse
import csv
import sys
from pathlib import Path

import netCDF4 as nc
import numpy as np
import psycopg

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.shared.db_utils import db_connect

LMR_NC    = Path("data/lmr_v2.1/pdsi_MCruns_ensemble_mean_LMRv2.1.nc")
AIR_NC    = Path("data/lmr_v2.1/air_MCruns_ensemble_mean_LMRv2.1.nc")
PRATE_NC  = Path("data/lmr_v2.1/prate_MCruns_ensemble_mean_LMRv2.1.nc")
EVOLV_CSV = Path("data/volcano/evolv2k_v4.csv")
SQL_DDL   = Path("sql/temporal/create_temporal.sql")

BATCH_SIZE = 500   # rows per executemany batch for LMR


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

def create_schema(conn):
    ddl = SQL_DDL.read_text()
    conn.execute(ddl)
    conn.commit()
    print("Schema ready (temporal.lmr_climate, temporal.evolv2k_v4).")


def add_lmr_column(conn, col_name):
    """Add a real[] column to lmr_climate if it doesn't already exist."""
    conn.execute(f"""
        ALTER TABLE temporal.lmr_climate
        ADD COLUMN IF NOT EXISTS {col_name} real[]
    """)
    conn.commit()
    print(f"Column {col_name} ready in temporal.lmr_climate.")


# ---------------------------------------------------------------------------
# LMR PDSI loader (initial load — inserts all rows)
# ---------------------------------------------------------------------------

def load_lmr(conn, dry_run=False):
    print(f"\nOpening {LMR_NC} ...")
    ds = nc.Dataset(LMR_NC)

    lat_vals = ds.variables["lat"][:]    # shape (91,)
    lon_vals = ds.variables["lon"][:]    # shape (180,)  0–358
    pdsi_var = ds.variables["pdsi"]      # shape (2001, 20, 91, 180)

    n_lat = len(lat_vals)
    n_lon = len(lon_vals)
    total = n_lat * n_lon
    print(f"Grid: {n_lat} lat × {n_lon} lon = {total:,} cells")
    print(f"Collapsing 20 MC runs to ensemble mean ...")

    if dry_run:
        print(f"[dry-run] Would insert {total:,} rows into temporal.lmr_climate — skipping.")
        ds.close()
        return

    # Load full array into memory: (2001, 20, 91, 180) → mean over axis 1 → (2001, 91, 180)
    print("Loading full PDSI array (this may take ~30s) ...")
    pdsi_all = pdsi_var[:].data          # (2001, 20, 91, 180), fill→nan already masked
    pdsi_mean = pdsi_all.mean(axis=1)    # (2001, 91, 180)
    ds.close()
    print("Array loaded.")

    insert_sql = """
        INSERT INTO temporal.lmr_climate (lat, lon, pdsi, geom)
        VALUES (%s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326))
    """

    # Truncate first so re-runs are safe
    conn.execute("TRUNCATE temporal.lmr_climate RESTART IDENTITY")
    conn.commit()

    rows = []
    inserted = 0

    for i_lat in range(n_lat):
        for i_lon in range(n_lon):
            lat = float(lat_vals[i_lat])
            lon_native = float(lon_vals[i_lon])   # 0–358
            # Convert to -180/180 for the PostGIS point
            lon_geom = lon_native if lon_native <= 180 else lon_native - 360

            pdsi_arr = pdsi_mean[:, i_lat, i_lon].tolist()
            rows.append((lat, lon_native, pdsi_arr, lon_geom, lat))

            if len(rows) >= BATCH_SIZE:
                conn.cursor().executemany(insert_sql, rows)
                conn.commit()
                inserted += len(rows)
                rows = []
                print(f"  {inserted:,} / {total:,} rows inserted", end="\r")

    if rows:
        conn.cursor().executemany(insert_sql, rows)
        conn.commit()
        inserted += len(rows)

    print(f"\nLMR PDSI: {inserted:,} rows inserted into temporal.lmr_climate.")


# ---------------------------------------------------------------------------
# Generic LMR variable loader (updates existing rows by lat/lon)
# ---------------------------------------------------------------------------

def load_lmr_var(conn, nc_path: Path, var_name: str, col_name: str, dry_run=False):
    """
    Load an additional LMR variable into an existing column of temporal.lmr_climate.
    Updates rows matched by (lat, lon) — grid must be identical to PDSI grid.

    Parameters
    ----------
    nc_path  : path to the _ensemble_mean NC file
    var_name : name of the variable inside the NC file (e.g. 'air', 'prate')
    col_name : target column in temporal.lmr_climate (e.g. 'air', 'prate')
    """
    print(f"\nOpening {nc_path} ...")
    ds = nc.Dataset(nc_path)

    lat_vals = ds.variables["lat"][:]
    lon_vals = ds.variables["lon"][:]
    var      = ds.variables[var_name]     # shape (2001, 20, 91, 180)

    n_lat = len(lat_vals)
    n_lon = len(lon_vals)
    total = n_lat * n_lon
    print(f"Grid: {n_lat} lat × {n_lon} lon = {total:,} cells")
    print(f"Collapsing MC runs to ensemble mean for '{var_name}' ...")

    if dry_run:
        print(f"[dry-run] Would update {total:,} rows — skipping.")
        ds.close()
        return

    print(f"Loading full {var_name} array ...")
    arr_all  = var[:].data               # (2001, n_mc, 91, 180)
    arr_mean = arr_all.mean(axis=1)      # (2001, 91, 180)
    ds.close()
    print("Array loaded.")

    update_sql = f"""
        UPDATE temporal.lmr_climate
        SET {col_name} = %s
        WHERE lat = %s AND lon = %s
    """

    rows = []
    updated = 0

    for i_lat in range(n_lat):
        for i_lon in range(n_lon):
            lat        = float(lat_vals[i_lat])
            lon_native = float(lon_vals[i_lon])
            arr        = arr_mean[:, i_lat, i_lon].tolist()
            rows.append((arr, lat, lon_native))

            if len(rows) >= BATCH_SIZE:
                conn.cursor().executemany(update_sql, rows)
                conn.commit()
                updated += len(rows)
                rows = []
                print(f"  {updated:,} / {total:,} rows updated", end="\r")

    if rows:
        conn.cursor().executemany(update_sql, rows)
        conn.commit()
        updated += len(rows)

    print(f"\nLMR {var_name}: {updated:,} rows updated in temporal.lmr_climate (column: {col_name}).")


# ---------------------------------------------------------------------------
# eVolv2k loader
# ---------------------------------------------------------------------------

def load_evolv2k(conn, dry_run=False):
    print(f"\nReading {EVOLV_CSV} ...")

    rows = []
    with open(EVOLV_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            tephra = r["tephra"].strip().upper() == "Y" if r["tephra"].strip() else None
            rows.append((
                int(r["year_ad"]),
                int(r["month"])   if r["month"].strip()   else None,
                int(r["day"])     if r["day"].strip()     else None,
                float(r["lat"])   if r["lat"].strip()     else None,
                float(r["so4_grl"])  if r["so4_grl"].strip()  else None,
                float(r["so4_ant"])  if r["so4_ant"].strip()  else None,
                float(r["vssi_tg"]),
                float(r["vssi_1sig"]) if r["vssi_1sig"].strip() else None,
                float(r["asymmetry"]) if r["asymmetry"].strip() else None,
                r["location"].strip() or None,
                tephra,
                r["reference"].strip() or None,
            ))

    print(f"Parsed {len(rows)} eruption records.")

    if dry_run:
        print("[dry-run] Would insert rows into temporal.evolv2k_v4 — skipping.")
        return

    insert_sql = """
        INSERT INTO temporal.evolv2k_v4
            (year_ad, month, day, lat, so4_grl, so4_ant, vssi_tg,
             vssi_1sig, asymmetry, location, tephra, reference)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """

    conn.execute("TRUNCATE temporal.evolv2k_v4 RESTART IDENTITY")
    conn.commit()
    conn.cursor().executemany(insert_sql, rows)
    conn.commit()
    print(f"eVolv2k: {len(rows)} rows inserted into temporal.evolv2k_v4.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Load temporal datasets into cedop db.")
    parser.add_argument("--lmr",     action="store_true", help="Load LMR PDSI only")
    parser.add_argument("--evolv2k", action="store_true", help="Load eVolv2k only")
    parser.add_argument("--air",     action="store_true", help="Load LMR air temperature")
    parser.add_argument("--prate",   action="store_true", help="Load LMR precipitation rate")
    parser.add_argument("--dry-run", action="store_true", help="Parse only; no db writes")
    args = parser.parse_args()

    any_flag = args.lmr or args.evolv2k or args.air or args.prate
    do_lmr     = args.lmr     or not any_flag
    do_evolv2k = args.evolv2k or not any_flag
    do_air     = args.air     or not any_flag
    do_prate   = args.prate   or not any_flag

    conn = db_connect()

    create_schema(conn)

    if do_lmr:
        load_lmr(conn, dry_run=args.dry_run)

    if do_evolv2k:
        load_evolv2k(conn, dry_run=args.dry_run)

    if do_air:
        add_lmr_column(conn, "air")
        load_lmr_var(conn, AIR_NC, "air", "air", dry_run=args.dry_run)

    if do_prate:
        add_lmr_column(conn, "prate")
        load_lmr_var(conn, PRATE_NC, "prate", "prate", dry_run=args.dry_run)

    conn.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
