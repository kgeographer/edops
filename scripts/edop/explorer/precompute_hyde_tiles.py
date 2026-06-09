"""
scripts/edop/explorer/precompute_hyde_tiles.py
----------------------------------------------
Pre-compute XYZ tile pyramids (zoom 0–6) for HYDE 3.4 derived views.

Derived views per variable (cropland, grazing, pasture, rangeland):
  first_epoch  — first of 7 epoch bins where fraction > 0 (categorical, 1–7; 0=never)
  persistence  — count of 7 epoch bins where fraction > 0 (ordinal, 0–7)
  epoch_N      — mean fraction across all time steps in epoch bin N (continuous, N=1..7)

7 epoch bins (step_idx → array index [step_idx+1] in PostgreSQL 1-indexed arrays):
  Epoch 1: step_idx 0-6   → years -10000 to -4000 BCE  arr[1:7]
  Epoch 2: step_idx 7-9   → years -3000 to -1000 BCE   arr[8:10]
  Epoch 3: step_idx 10    → year  0 CE                 arr[11]
  Epoch 4: step_idx 11-20 → years 100-1000 CE          arr[12:21]
  Epoch 5: step_idx 21-27 → years 1100-1700 CE         arr[22:28]
  Epoch 6: step_idx 28-47 → years 1710-1900 CE         arr[29:48]
  Epoch 7: step_idx 48-127→ years 1910-2025 CE         arr[49:128]

Tile output: app/static/explorer/hyde_tiles/{var}/{view}/{z}/{x}/{y}.png
  var:  cropland | grazing | pasture | rangeland
  view: first_epoch | persistence | epoch_1..epoch_7

Performance strategy:
  1. Query derived features from PostgreSQL via SQL (one query per var×view = 9 queries
     repeated across 4 vars = 36 queries; each returns lat, lon, value for 2.2M cells).
  2. Build 4320×2160 equirectangular numpy float32 raster (5-arcmin grid).
  3. Generate Mercator XYZ tile pyramid at zoom 0–6 using per-pixel inverse projection.
  4. Apply colormap and write PNG tiles; skip all-transparent tiles.

Usage:
    python scripts/edop/explorer/precompute_hyde_tiles.py [--var cropland] [--zoom-max 6]
"""

import argparse
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from app.db.connection import db_connect

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
GRID_ROWS = 2160   # 180° / (5/60°)
GRID_COLS = 4320   # 360° / (5/60°)
ARCMIN    = 5      # cell size in arcminutes
DEG_PER_CELL = ARCMIN / 60.0   # = 0.0833...°

VARIABLES = ["cropland", "grazing", "pasture", "rangeland"]

# 7 epoch bins: (epoch_label, pg_slice_start, pg_slice_end, n_steps)
# PostgreSQL array slice: arr[start:end] inclusive, 1-indexed
EPOCH_BINS = [
    (1, "10000–4000 BCE", 1,   7,   7),
    (2, "3000–1000 BCE",  8,  10,   3),
    (3, "0 CE",          11,  11,   1),
    (4, "100–1000 CE",   12,  21,  10),
    (5, "1100–1700 CE",  22,  28,   7),
    (6, "1710–1900 CE",  29,  48,  20),
    (7, "1910–2025 CE",  49, 128,  80),
]

OUT_BASE = Path(__file__).resolve().parents[3] / "app" / "static" / "explorer" / "hyde_tiles"

# ---------------------------------------------------------------------------
# Colormaps (RGBA tuples)
# ---------------------------------------------------------------------------

def _lerp_color(c0, c1, t):
    return tuple(int(c0[i] + (c1[i] - c0[i]) * t) for i in range(4))


def _make_first_epoch_cmap():
    """7 discrete colors (epoch 1–7) + transparent for 0/NaN."""
    # Blue → purple → magenta → red-orange → orange → yellow-green → yellow
    colors = {
        0: (0, 0, 0, 0),          # never — transparent
        1: (8,  48, 107, 255),    # dark blue  (pre-4000 BCE)
        2: (63, 0,  125, 255),    # purple     (3000-1000 BCE)
        3: (152, 0, 136, 255),    # magenta    (0 CE)
        4: (217, 72, 1,  255),    # orange-red (100-1000 CE)
        5: (239, 138, 7, 255),    # amber      (1100-1700 CE)
        6: (166, 217, 106, 255),  # yellow-green (1710-1900 CE)
        7: (255, 255, 153, 255),  # light yellow (1910-2025 CE)
    }
    lut = np.zeros((256, 4), dtype=np.uint8)
    for k, rgba in colors.items():
        lut[k] = rgba
    return lut


def _make_persistence_cmap():
    """8 steps (0–7): light yellow → dark blue; 0=transparent."""
    stops = [
        (0, (0, 0, 0, 0)),
        (1, (255, 255, 204, 255)),
        (2, (199, 233, 180, 255)),
        (3, (127, 205, 187, 255)),
        (4, (65,  182, 196, 255)),
        (5, (29,  145, 192, 255)),
        (6, (34,   94, 168, 255)),
        (7, (12,   44, 132, 255)),
    ]
    lut = np.zeros((256, 4), dtype=np.uint8)
    for k, rgba in stops:
        lut[k] = rgba
    return lut


def _make_value_cmap(var: str, steps: int = 128):
    """Sequential colormap for current-value view (fraction 0–1).
    Crops: greens; Graz/Past/Range: brown-tan.
    Value 0 → transparent; >0 → full color range.
    """
    if var == "cropland":
        lo = (229, 245, 224, 200)
        hi = (0,   109, 44,  255)
    else:
        lo = (255, 247, 236, 200)
        hi = (127, 39,  4,   255)

    lut = np.zeros((256, 4), dtype=np.uint8)
    lut[0] = (0, 0, 0, 0)   # 0 = transparent
    for i in range(1, 256):
        t = i / 255.0
        lut[i] = _lerp_color(lo, hi, t)
    return lut


# ---------------------------------------------------------------------------
# SQL query builders
# ---------------------------------------------------------------------------

def _sql_first_epoch(var: str) -> str:
    cases = []
    for epoch, _, pg0, pg1, _ in EPOCH_BINS:
        if pg0 == pg1:
            check = f"{var}[{pg0}] > 0"
        else:
            checks = " OR ".join(f"{var}[{i}] > 0" for i in range(pg0, pg1 + 1))
            check = f"({checks})"
        cases.append(f"WHEN {check} THEN {epoch}")
    return f"""
        SELECT
            ST_Y(ST_Centroid(geom)) AS lat,
            ST_X(ST_Centroid(geom)) AS lon,
            CASE {' '.join(cases)} ELSE 0 END AS value
        FROM temporal.hyde_cells
    """


def _sql_persistence(var: str) -> str:
    terms = []
    for _, _, pg0, pg1, _ in EPOCH_BINS:
        if pg0 == pg1:
            check = f"{var}[{pg0}] > 0"
        else:
            checks = " OR ".join(f"{var}[{i}] > 0" for i in range(pg0, pg1 + 1))
            check = f"({checks})"
        terms.append(f"(CASE WHEN {check} THEN 1 ELSE 0 END)")
    return f"""
        SELECT
            ST_Y(ST_Centroid(geom)) AS lat,
            ST_X(ST_Centroid(geom)) AS lon,
            ({' + '.join(terms)}) AS value
        FROM temporal.hyde_cells
    """


def _sql_epoch_value(var: str, pg0: int, pg1: int, n_steps: int) -> str:
    if pg0 == pg1:
        expr = f"{var}[{pg0}]::float4 / NULLIF(area_km2, 0)"
    else:
        terms = " + ".join(f"COALESCE({var}[{i}], 0)" for i in range(pg0, pg1 + 1))
        expr = f"({terms}) / {n_steps}.0 / NULLIF(area_km2, 0)"
    return f"""
        SELECT
            ST_Y(ST_Centroid(geom)) AS lat,
            ST_X(ST_Centroid(geom)) AS lon,
            {expr} AS value
        FROM temporal.hyde_cells
    """


def _sql_epoch_p99(var: str, pg0: int, pg1: int, n_steps: int) -> str:
    """p99 of per-cell mean fractions (> 0) for one epoch bin."""
    if pg0 == pg1:
        expr = f"{var}[{pg0}]::float4 / NULLIF(area_km2, 0)"
    else:
        terms = " + ".join(f"COALESCE({var}[{i}], 0)" for i in range(pg0, pg1 + 1))
        expr = f"({terms}) / {n_steps}.0 / NULLIF(area_km2, 0)"
    return f"""
        WITH fracs AS (
            SELECT {expr} AS frac FROM temporal.hyde_cells
        )
        SELECT percentile_cont(0.99) WITHIN GROUP (ORDER BY frac)
        FROM fracs WHERE frac > 0
    """


# ---------------------------------------------------------------------------
# Raster building
# ---------------------------------------------------------------------------

def build_raster(rows) -> np.ndarray:
    """Build a 4320×2160 float32 raster from (lat, lon, value) rows.
    NaN = no data / ocean cell.
    """
    raster = np.full((GRID_ROWS, GRID_COLS), np.nan, dtype=np.float32)
    for lat, lon, val in rows:
        if val is None:
            continue
        row = int((90.0 - float(lat)) / DEG_PER_CELL)
        col = int((float(lon) + 180.0) / DEG_PER_CELL)
        if 0 <= row < GRID_ROWS and 0 <= col < GRID_COLS:
            raster[row, col] = float(val)
    return raster


# ---------------------------------------------------------------------------
# Tile generation
# ---------------------------------------------------------------------------

def lat_from_tile_y(tile_y: float, n: int) -> float:
    """Inverse Mercator: tile y-fraction → latitude degrees."""
    return math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * tile_y / n))))


def generate_tile(z: int, tx: int, ty: int, raster: np.ndarray,
                  lut: np.ndarray, vmin: float, vmax: float,
                  discrete: bool = False) -> Image.Image | None:
    """
    Generate a 256×256 RGBA PNG tile from an equirectangular raster.

    discrete: if True, values in raster are integer indices into lut directly.
    continuous: vmin/vmax scale float raster to 1–255; 0 kept transparent.
    Returns None if the tile is fully transparent (no data).
    """
    n = 1 << z  # 2^z
    size = 256

    # Pixel column fractions within tile → lon
    px = (tx + np.arange(size, dtype=np.float64) / size)
    lon = px / n * 360.0 - 180.0         # shape (size,)

    # Pixel row fractions within tile → lat via inverse Mercator
    py = (ty + np.arange(size, dtype=np.float64) / size)
    lat = np.degrees(np.arctan(np.sinh(np.pi * (1 - 2 * py / n))))  # shape (size,)

    # Grid indices (broadcast to 256×256)
    row_idx = np.clip(((90.0 - lat[:, None]) / DEG_PER_CELL).astype(np.int32), 0, GRID_ROWS - 1)
    col_idx = np.clip(((lon[None, :] + 180.0) / DEG_PER_CELL).astype(np.int32), 0, GRID_COLS - 1)

    values = raster[row_idx, col_idx]   # shape (256, 256)

    nan_mask = np.isnan(values)
    if nan_mask.all():
        return None

    if discrete:
        # Integer indices directly into LUT (values are already 0–7)
        safe = np.where(nan_mask, 0, np.nan_to_num(values, nan=0.0))
        idx = np.clip(safe, 0, 255).astype(np.uint8)
    else:
        # Normalise 0–1 float to 1–255 LUT index (0 = transparent for 0-value cells)
        norm = np.where(nan_mask, np.nan,
               np.where(values <= 0, 0,
               np.clip((values - vmin) / (vmax - vmin), 0, 1) * 254 + 1))
        idx = np.where(np.isnan(norm), 0, norm).astype(np.uint8)

    rgba = lut[idx]  # shape (256, 256, 4)
    rgba[nan_mask] = (0, 0, 0, 0)  # ocean / no-data → transparent

    img = Image.fromarray(rgba, mode="RGBA")
    return img


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def render_view(var: str, view_name: str, sql: str,
                lut: np.ndarray, vmin: float, vmax: float,
                discrete: bool, zoom_max: int):
    t0 = time.time()
    print(f"  [{var}/{view_name}] querying …", flush=True)
    with db_connect() as conn:
        cur = conn.execute(sql)
        rows = cur.fetchall()
    print(f"  [{var}/{view_name}] {len(rows)} cells in {time.time()-t0:.1f}s — building raster …", flush=True)

    t1 = time.time()
    raster = build_raster(rows)
    del rows
    print(f"  [{var}/{view_name}] raster built in {time.time()-t1:.1f}s — generating tiles …", flush=True)

    tile_dir_base = OUT_BASE / var / view_name
    total = sum(4**z for z in range(zoom_max + 1))
    written = skipped = 0

    t2 = time.time()
    for z in range(zoom_max + 1):
        n = 1 << z
        for tx in range(n):
            for ty in range(n):
                img = generate_tile(z, tx, ty, raster, lut, vmin, vmax, discrete=discrete)
                if img is None:
                    skipped += 1
                    continue
                tile_path = tile_dir_base / str(z) / str(tx) / f"{ty}.png"
                tile_path.parent.mkdir(parents=True, exist_ok=True)
                img.save(tile_path, format="PNG", optimize=False)
                written += 1

    elapsed = time.time() - t2
    print(f"  [{var}/{view_name}] {written} tiles written, {skipped} skipped "
          f"(all-transparent) in {elapsed:.0f}s", flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--var",      default=None,
                        help="Limit to one variable (cropland|grazing|pasture|rangeland)")
    parser.add_argument("--view",     default=None,
                        help="Limit to one view (first_epoch|persistence|epoch_1..epoch_7)")
    parser.add_argument("--zoom-max", type=int, default=6,
                        help="Maximum zoom level to generate (default 6)")
    args = parser.parse_args()

    vars_to_run = [args.var] if args.var else VARIABLES

    # Epoch views need a per-var/epoch p99 as vmax so tiles saturate at the real
    # distribution top, not at 100%.  Skip this phase for non-epoch --view targets.
    running_epoch_views = not args.view or args.view.startswith("epoch_")

    epoch_maxes_new: dict = {}  # {var: global_vmax}  — single float, max p99 across all epochs
    if running_epoch_views:
        for var in vars_to_run:
            print(f"\n=== Variable: {var} — computing epoch p99 ===")
            all_p99s = []
            for epoch, label, pg0, pg1, n_steps in EPOCH_BINS:
                # Always scan ALL epochs so global max is correct even on partial --view runs
                sql = _sql_epoch_p99(var, pg0, pg1, n_steps)
                with db_connect() as conn:
                    row = conn.execute(sql).fetchone()
                p99 = float(row[0]) if row and row[0] is not None else 0.0
                all_p99s.append(p99)
                print(f"  epoch_{epoch} ({label}): {p99 * 100:.1f}%", flush=True)
            global_vmax = round(max(all_p99s), 4)
            print(f"  → global vmax: {global_vmax * 100:.1f}%", flush=True)
            epoch_maxes_new[var] = global_vmax

    for var in vars_to_run:
        print(f"\n=== Variable: {var} ===")

        views = []

        # first_epoch
        if not args.view or args.view == "first_epoch":
            views.append({
                "name":     "first_epoch",
                "sql":      _sql_first_epoch(var),
                "lut":      _make_first_epoch_cmap(),
                "vmin":     0, "vmax": 7,
                "discrete": True,
            })

        # persistence
        if not args.view or args.view == "persistence":
            views.append({
                "name":     "persistence",
                "sql":      _sql_persistence(var),
                "lut":      _make_persistence_cmap(),
                "vmin":     0, "vmax": 7,
                "discrete": True,
            })

        # epoch_1..epoch_7 — same global vmax for all epochs of this variable
        if running_epoch_views:
            for epoch, label, pg0, pg1, n_steps in EPOCH_BINS:
                vname = f"epoch_{epoch}"
                if args.view and args.view != vname:
                    continue
                vmax = epoch_maxes_new[var]
                views.append({
                    "name":     vname,
                    "sql":      _sql_epoch_value(var, pg0, pg1, n_steps),
                    "lut":      _make_value_cmap(var),
                    "vmin":     0.0,
                    "vmax":     vmax,
                    "discrete": False,
                })

        for v in views:
            render_view(var, v["name"], v["sql"], v["lut"],
                        v["vmin"], v["vmax"], v["discrete"], args.zoom_max)

    # Write / merge p99 sidecar JSON so the legend endpoint can read it without a DB query.
    # Merges into any existing file so partial runs (--var or --view) don't wipe other entries.
    if running_epoch_views and epoch_maxes_new:
        json_path = OUT_BASE.parent / "hyde_epoch_maxes.json"
        existing: dict = {}
        if json_path.exists():
            with open(json_path) as f:
                existing = json.load(f)
        existing.update(epoch_maxes_new)
        with open(json_path, "w") as f:
            json.dump(existing, f, indent=2)
        print(f"\nWrote p99 sidecar → {json_path}")

    print("\nAll done.")


if __name__ == "__main__":
    main()
