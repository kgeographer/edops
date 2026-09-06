# WHG dataset export drops contributor polygons for places with multiple geometries

**Draft — for Karl to file against World Historical Gazetteer. Not filed.**

## Summary

For a place that has more than one `place_geom` row, WHG's **dataset downloads (both
LPF and TSV)** emit a single geometry and choose the reconciliation-pass point
(e.g. a Wikidata representative point) instead of the contributor's drawn polygon.
The dataset's own map view renders the polygon, so the loss is silent — only
visible on download.

## Where it bites

Dataset **1155 — *Pre-Colonial African Subregions*** (Henry B. Lovejoy et al.).
34 subregions; 32 export with their contributor `MULTIPOLYGON`/`POLYGON`. Two do not:

| region | WHG place id | export geometry | `geo_source` in TSV |
|---|---|---|---|
| Western Sahara (`hc_02`) | 7130907 | `MULTIPOINT` @ ~(-13, 25) | `wd:Q6250` |
| Kalahari (`hc_25`) | 7130908 | `MULTIPOINT` @ ~(23.4, -22.75) | `wd:Q14202768` |

Both the `.lpf` and `.tsv` exports for dataset 1155 give these two as the single
Wikidata point; the TSV `geo_source` / `geo_id` columns name the Wikidata id, i.e.
the export picked the reconciliation geometry over the contributor one.

## Expected

Dataset export should prefer the contributor-supplied geometry when a place has
several, or (better) emit all geometries — e.g. LPF `geometry` as a
`GeometryCollection`, or one feature per geometry, or a documented precedence rule.

## Repro

1. Download dataset 1155 as LPF and as TSV from WHG.
2. Inspect the features / rows for *Western Sahara* and *Kalahari* — both carry a
   single `MULTIPOINT`; every other subregion carries a polygon.
3. Compare to the dataset map view, which shows polygons for all 34.

## Secondary (same dataset, trivial)

Subregion `hc_10` has the title **"North Coaast"** (double-a typo) in the published
dataset. Should be **"North Coast"**.

## Impact / workaround here

The EDOPS *African Regions* Workbench tab needs the polygons. Worked around by
sourcing all 34 geometries from a WHG working copy (`whg_staging.lovejoy.regions`,
which still has the drawn polygons) and joining names + descriptions from the
published LPF on `src_id`
(`scripts/edop/workbench/build_lovejoy_geojson.py`). The typo is corrected for
display via a `NAME_FIX` map in that script.
