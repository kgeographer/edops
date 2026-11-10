"""WO-03 shared helpers: test places, the WO-02 population sample, a DB connection.

Read-only. Used by the notebooks in notebooks/edop/whg/. Nothing here changes app behaviour.
"""
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "output/edop/whg"
WO02 = ROOT / "output/edop/dashboard/wo02"

# Approximate coordinates from the WO-03 table; each is resolved to a hybas_id in the notebooks.
PLACES = {
    "Timbuktu":      (16.77, -3.01),
    "Tbilisi":       (41.72, 44.79),
    "Santa Fe":      (35.69, -105.94),
    "Kaifeng":       (34.80, 114.31),
    "Lviv":          (49.84, 24.03),
    "Poltava":       (49.59, 34.55),
    "Chaco Canyon":  (36.06, -107.96),
    "Alexandria":    (31.20, 29.92),
    "Utqiagvik":     (71.29, -156.79),
    # island: my choice (WO leaves it to CC); Edinburgh of the Seven Seas, Tristan da Cunha
    "Tristan da Cunha": (-37.068, -12.312),
}


def commit():
    return subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"],
                          capture_output=True, text=True).stdout.strip()


def population_points():
    """The WO-02 stratified sample: one row per distinct L6 basin (the single-basin queries).

    Returns a list of dicts: hybas_id_l6, climate_zone, lat, lon.
    """
    man = json.loads((WO02 / "manifest_population.json").read_text())
    seen, rows = set(), []
    for e in man["entries"]:
        p = e["params"]
        if p["scope"] != "single_basin" or p["level"] != 6:
            continue
        h = int(e["hybas_id_l6"])
        if h in seen:
            continue
        seen.add(h)
        rows.append(dict(hybas_id_l6=h, climate_zone=e["climate_zone"], lat=p["lat"], lon=p["lon"]))
    return rows
