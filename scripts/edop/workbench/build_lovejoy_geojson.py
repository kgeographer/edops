"""
Build app/static/workbench/lovejoy_regions.geojson for the African Regions Workbench tab.

The single runtime source for that tab's map. Merges, per src_id:
  - all 34 geometries + macro-region from whg_staging.lovejoy.regions (dev DB) --
    the 32 that match the published WHG dataset 1155 byte-for-byte, plus the real
    Western Sahara / Kalahari polygons that dataset's LPF/TSV export dropped (it
    picks the reconciliation-pass Wikidata point over the contributor polygon).
  - name from the published LPF (data/lovejoy/whg_dataset_1155.lpf).
  - rationale + page + ethnonyms from the curated master
    data/lovejoy/lovejoy_rationales.md (WO02.5, Karl-reviewed). This is the
    per-region article text shown in #afr-right; the old lovejoy_region_notes.json
    path is retired.

One-off / re-runnable. Reads whg_staging locally; the app never touches it.
"""
import json
import os
import re
from pathlib import Path

import psycopg
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[3]
load_dotenv(ROOT / ".env")

LPF_PATH = ROOT / "data" / "lovejoy" / "whg_dataset_1155.lpf"
RATIONALE_PATH = ROOT / "data" / "lovejoy" / "lovejoy_rationales.md"
OUT_PATH = ROOT / "app" / "static" / "workbench" / "lovejoy_regions.geojson"

PG_KWARGS = dict(
    host=os.environ.get("PGHOST", "localhost"),
    port=os.environ.get("PGPORT", "5432"),
    user=os.environ.get("PGUSER"),
    password=os.environ.get("PGPASSWORD"),
)

# Display-name corrections for typos in the WHG source (both the published dataset
# 1155 and whg_staging carry these). Flagged upstream in the WHG issue draft.
NAME_FIX = {
    "hc_10": "North Coast",   # published title is "North Coaast"
}


def load_lpf_names(path):
    """src_id -> display title."""
    lpf = json.loads(path.read_text())
    return {f["properties"]["src_id"]: f["properties"]["title"] for f in lpf["features"]}


def load_rationales(path):
    """src_id -> {"rationale": str, "page": str, "ethnonyms": str}.

    Parses the curated master. Contract (also in the file's header comment):
      section head = '## <src_id> · <name>'
      '- page:' / '- ethnonyms:' lines carry those fields
      body = the paragraph after the last '- ' line, up to a blank-line '---',
             a heading, or the next section; '_missing' body => no rationale.
    """
    text = path.read_text()
    parts = re.split(r"^## (hc_\w+) ·[^\n]*$", text, flags=re.M)
    out = {}
    for i in range(1, len(parts), 2):
        sid, body = parts[i], parts[i + 1]
        pm = re.search(r"^- page:[ \t]*(.*)$", body, re.M)
        em = re.search(r"^- ethnonyms:[ \t]*(.*)$", body, re.M)
        lines = body.splitlines()
        last_meta = max((j for j, ln in enumerate(lines) if ln.startswith("- ")), default=-1)
        para = []
        for ln in lines[last_meta + 1:]:
            if ln.strip() == "---" or ln.startswith("#"):
                break
            para.append(ln)
        rationale = re.sub(r"\s+", " ", " ".join(para)).strip()
        if rationale.startswith("_missing"):
            rationale = ""
        out[sid] = {
            "rationale": rationale,
            "page": (pm.group(1).strip() if pm else ""),
            "ethnonyms": (em.group(1).strip() if em else ""),
        }
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
    names = load_lpf_names(LPF_PATH)
    rats = load_rationales(RATIONALE_PATH)
    geoms = load_staging_geoms()

    missing_rat = sorted(set(geoms) - set(rats))
    if missing_rat:
        print(f"WARNING  no rationale entry for: {missing_rat}")
    empty_rat = sorted(s for s in geoms if not rats.get(s, {}).get("rationale"))
    if empty_rat:
        print(f"WARNING  empty rationale for: {empty_rat}")

    features = []
    for src_id in sorted(geoms):
        g = geoms[src_id]
        r = rats.get(src_id, {})
        features.append({
            "type": "Feature",
            "id": src_id,
            "properties": {
                "src_id": src_id,
                "name": NAME_FIX.get(src_id, names.get(src_id) or src_id),
                "macro": g["macro"],
                "rationale": r.get("rationale", ""),
                "page": r.get("page", ""),
                "ethnonyms": r.get("ethnonyms", ""),
            },
            "geometry": g["geometry"],
        })

    fc = {
        "type": "FeatureCollection",
        "name": "lovejoy_regions",
        "note": (
            "Pre-Colonial African Subregions (Lovejoy et al.). Geometry from a WHG "
            "working copy (whg_staging.lovejoy.regions); names from the published WHG "
            "dataset 1155 LPF; rationale/page/ethnonyms from data/lovejoy/"
            "lovejoy_rationales.md. Built by scripts/edop/workbench/build_lovejoy_geojson.py."
        ),
        "features": features,
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(fc))
    kb = OUT_PATH.stat().st_size / 1024
    n_rat = sum(1 for f in features if f["properties"]["rationale"])
    n_eth = sum(1 for f in features if f["properties"]["ethnonyms"])
    print(f"wrote {OUT_PATH.relative_to(ROOT)}  ({len(features)} features, {kb:,.0f} KB)")
    print(f"  rationale present: {n_rat}/{len(features)}   ethnonyms present: {n_eth}/{len(features)}")
    print(f"  macro regions: {sorted(set(f['properties']['macro'] for f in features))}")


if __name__ == "__main__":
    main()
