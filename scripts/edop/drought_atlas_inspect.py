"""
drought_atlas_inspect.py
------------------------
Reports the structure of one or more tree-ring drought atlas files
(OWDA, MADA, NADA/LBDA, MXDA, ANZDA, SADA, ERDA, ...) so we can confirm
the actual on-disk format before designing the loader.

Download files manually from the NOAA NCEI study pages into data/drought_atlas/
(e.g. data/drought_atlas/owda/..., data/drought_atlas/mada2/...), then:

Run from repo root:
    ~/envs/_edop/bin/python3 scripts/edop/drought_atlas_inspect.py data/drought_atlas/owda/*.nc
    ~/envs/_edop/bin/python3 scripts/edop/drought_atlas_inspect.py data/drought_atlas/erda/*.txt

For netCDF: dimensions, coordinates, variables + attributes, global attributes,
per-cell first valid year distribution, and the series span at the probe
places (the five Sandbox Settlements examples).

For ASCII: first lines + a shape guess (the NOAA ASCII releases are typically a
grid-point list plus a year × grid-point matrix; this prints enough to confirm).
"""

import sys
from pathlib import Path

import numpy as np
import xarray as xr

# Sandbox Settlements examples (lat, lon) — sandbox.html #v3-example-select
PROBES = {
    "Timbuktu":      (16.8167, -2.9833),
    "Kaifeng":       (34.7975, 114.3074),
    "Tbilisi":       (41.6938, 44.8015),
    "Santa Fe":      (35.6870, -105.9378),
    "San Francisco": (37.7749, -122.4194),
}

LAT_NAMES  = ("lat", "latitude", "LAT", "Lat")
LON_NAMES  = ("lon", "longitude", "LON", "Lon")
TIME_NAMES = ("time", "year", "years", "Year", "TIME")


def _find(ds, names):
    for n in names:
        if n in ds.variables or n in ds.dims:
            return n
    return None


def inspect_nc(path):
    ds = xr.open_dataset(path, decode_times=False)

    print("\n--- Dimensions ---")
    for name, size in ds.sizes.items():
        print(f"  {name}: {size}")

    print("\n--- Coordinates ---")
    for name, coord in ds.coords.items():
        vals = coord.values
        if vals.ndim == 1 and len(vals) > 1:
            step = vals[1] - vals[0]
            print(f"  {name}: {vals[0]} → {vals[-1]}  (n={len(vals)}, step={step})")
        else:
            print(f"  {name}: {vals}")

    print("\n--- Variables ---")
    for name, var in ds.data_vars.items():
        print(f"  {name}: dims={var.dims}, shape={var.shape}, dtype={var.dtype}")
        for k, v in var.attrs.items():
            print(f"    {k}: {v}")

    print("\n--- Global attributes ---")
    for k, v in ds.attrs.items():
        print(f"  {k}: {v}")

    lat_n, lon_n, time_n = _find(ds, LAT_NAMES), _find(ds, LON_NAMES), _find(ds, TIME_NAMES)
    gridded = [v for v in ds.data_vars.values()
               if lat_n in v.dims and lon_n in v.dims and time_n in v.dims]
    if not gridded:
        print("\n(no time × lat × lon variable found — skipping coverage checks)")
        ds.close()
        return

    var = gridded[0]
    years = ds[time_n].values
    print(f"\n--- Coverage: {var.name} ---")
    print(f"  time units: {ds[time_n].attrs.get('units', '(none)')}; "
          f"first/last raw values: {years[0]} / {years[-1]}")

    data = var.transpose(time_n, lat_n, lon_n).values
    valid = ~np.isnan(data)
    any_valid = valid.any(axis=0)
    print(f"  land cells with any data: {int(any_valid.sum())} of {any_valid.size}")

    # First valid year per cell: how much does the record thin backwards in time?
    first_idx = np.where(any_valid, valid.argmax(axis=0), -1)
    firsts = years[first_idx[any_valid]]
    for q in (0, 10, 25, 50, 75, 90, 100):
        print(f"  first valid year, p{q:>3}: {np.percentile(firsts, q):.0f}")
    n_by_year = valid.sum(axis=(1, 2))
    for y in (0, 500, 1000, 1200, 1400, 1500, 1700, 1900):
        hit = np.where(years == y)[0]
        if hit.size:
            print(f"  cells with data in {y}: {int(n_by_year[hit[0]])}")

    print("\n--- Probe places (nearest cell) ---")
    lats, lons = ds[lat_n].values, ds[lon_n].values
    for place, (plat, plon) in PROBES.items():
        qlon = plon % 360 if lons.max() > 180 else plon
        if not (lats.min() - 1 <= plat <= lats.max() + 1 and lons.min() - 1 <= qlon <= lons.max() + 1):
            print(f"  {place}: outside grid extent")
            continue
        s = var.sel({lat_n: plat, lon_n: qlon}, method="nearest")
        v = s.values
        ok = ~np.isnan(v)
        if not ok.any():
            print(f"  {place}: nearest cell ({float(s[lat_n])}, {float(s[lon_n])}) is empty (outside domain / ocean)")
            continue
        print(f"  {place}: cell ({float(s[lat_n])}, {float(s[lon_n])}), "
              f"{years[ok][0]}–{years[ok][-1]}, n={int(ok.sum())}, "
              f"mean={np.nanmean(v):.2f}, sd={np.nanstd(v):.2f}")

    ds.close()


def inspect_ascii(path, n=8):
    with open(path, errors="replace") as f:
        lines = [next(f, "") for _ in range(n)]
    print("\n--- First lines ---")
    for ln in lines:
        print("  " + ln.rstrip()[:160])
    with open(path, errors="replace") as f:
        rows = sum(1 for _ in f)
    ncols = len(lines[-1].split()) if lines[-1].strip() else 0
    print(f"\n  rows: {rows}; whitespace-split columns in line {n}: {ncols}")


def main(paths):
    if not paths:
        print(__doc__)
        sys.exit(1)
    for p in map(Path, paths):
        print("=" * 78)
        print(p)
        print("=" * 78)
        if p.suffix in (".nc", ".nc4", ".cdf"):
            inspect_nc(p)
        else:
            inspect_ascii(p)


if __name__ == "__main__":
    main(sys.argv[1:])
