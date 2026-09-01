"""
Build app/static/workbench/lovejoy_regions.geojson for the African Regions Workbench tab.

Merges:
  - all 34 geometries + macro-region from whg_staging.lovejoy.regions (dev DB) --
    the 32 that match the published WHG dataset 1155 byte-for-byte, plus the real
    Western Sahara / Kalahari polygons that dataset's LPF/TSV export dropped (it
    picks the reconciliation-pass Wikidata point over the contributor polygon).
  - name + short blurb from the published LPF (data/lovejoy/whg_dataset_1155.lpf),
    joined on src_id -- so names are current (hc_18 = "Eastern Interior") and the
    blurbs are the citable ones shown in WHG.

Fuller per-region rationale (from the Lovejoy article PDF) is a separate pass ->
app/static/workbench/lovejoy_region_notes.json (WO02 Part B).

One-off / re-runnable. Reads whg_staging locally; the app never touches it.
"""
import json
import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[3]
load_dotenv(ROOT / ".env")

LPF_PATH = ROOT / "data" / "lovejoy" / "whg_dataset_1155.lpf"
OUT_PATH = ROOT / "app" / "static" / "workbench" / "lovejoy_regions.geojson"

PG_KWARGS = dict(
    host=os.environ.get("PGHOST", "localhost"),
    port=os.environ.get("PGPORT", "5432"),
    user=os.environ.get("PGUSER"),
    password=os.environ.get("PGPASSWORD"),
)


def load_lpf_attrs(path):
    """src_id -> {"name": title, "blurb": first description value or ""}."""
    lpf = json.loads(path.read_text())
    out = {}
    for f in lpf["features"]:
        p = f["properties"]
        descs = p.get("descriptions") or []
        blurb = (descs[0].get("value") if descs else "") or ""
        out[p["src_id"]] = {"name": p["title"], "blurb": blurb.strip()}
    return out


def load_staging_geoms():
    """src_id -> {"macro": macro_region, "geometry": <GeoJSON geometry dict>}."""
    with psycopg.connect(**PG_KWARGS, dbname="whg_staging") as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT src_id, macro_region, ST_AsGeoJSON(geom) "
                "FROM lovejoy.regions ORDER BY src_id"
            )
            rows = cur.fetchall()
    return {
        src_id: {"macro": (macro or "").strip(), "geometry": json.loads(gj)}
        for src_id, macro, gj in rows
    }


def main():
    attrs = load_lpf_attrs(LPF_PATH)
    geoms = load_staging_geoms()

    only_lpf = sorted(set(attrs) - set(geoms))
    only_stg = sorted(set(geoms) - set(attrs))
    if only_lpf or only_stg:
        print(f"WARNING  src_id mismatch  only-in-LPF={only_lpf}  only-in-staging={only_stg}")

    features = []
    for src_id in sorted(geoms):
        a = attrs.get(src_id, {})
        g = geoms[src_id]
        features.append({
            "type": "Feature",
            "id": src_id,
            "properties": {
                "src_id": src_id,
                "name": a.get("name") or src_id,
                "macro": g["macro"],
                "blurb": a.get("blurb", ""),
            },
            "geometry": g["geometry"],
        })

    fc = {
        "type": "FeatureCollection",
        "name": "lovejoy_regions",
        "note": (
            "Pre-Colonial African Subregions (Lovejoy et al.). Geometry from a WHG "
            "working copy (whg_staging.lovejoy.regions); names + blurbs from the "
            "published WHG dataset 1155 LPF. Built by "
            "scripts/edop/workbench/build_lovejoy_geojson.py."
        ),
        "features": features,
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(fc))
    kb = OUT_PATH.stat().st_size / 1024
    n_blurb = sum(1 for f in features if f["properties"]["blurb"])
    print(f"wrote {OUT_PATH.relative_to(ROOT)}  ({len(features)} features, {kb:,.0f} KB)")
    print(f"  blurbs present: {n_blurb}/{len(features)}")
    print(f"  macro regions: {sorted(set(f['properties']['macro'] for f in features))}")


if __name__ == "__main__":
    main()
