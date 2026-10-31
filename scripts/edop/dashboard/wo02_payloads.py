"""WO-02 shared helpers: load the saved payloads, weight the population sample, write master-table rows.

Read-only. The payloads under output/edop/dashboard/wo02/ are never edited and the API is never called.
Used by the Step 3 family notebooks in notebooks/edop/dashboard/.
"""
import csv, json, collections
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "output/edop/dashboard/wo02"
MASTER = ROOT / "notebooks/edop/dashboard/wo02_master_table.csv"
MASTER_COLS = ["id", "family", "name", "inputs", "rule", "applies_to", "does_not_apply_when", "template",
               "in_ui_today", "needs_new_data", "fixture_result", "population_result", "sweep_result"]


def load_set(name):
    """List of dicts: id, set, kind, params, http, bytes, seconds, body, plus climate_zone/hybas_id_l6 for population."""
    man = json.loads((OUT / f"manifest_{name}.json").read_text())
    items = []
    for e in man["entries"]:
        r = e["result"]
        items.append(dict(id=e["id"], set=name, kind=e["id"][-1] if name == "population" else "f",
                          params=e["params"], condition=e.get("condition"), http=r["http"], bytes=r["bytes"],
                          seconds=r["seconds"], body=json.loads((OUT / r["file"]).read_text()),
                          climate_zone=e.get("climate_zone"), hybas_id_l6=e.get("hybas_id_l6")))
    return man, items


def load_all():
    """(fixtures, population, provenance): only queries that returned 200 are kept."""
    mf, fx = load_set("fixtures")
    mp, pop = load_set("population")
    return [q for q in fx if q["http"] == 200], [q for q in pop if q["http"] == 200], mf["provenance"]


def load_bandt():
    """The Band T-only fixtures (F35 to F45, manifest_bandt.json); those that returned 200."""
    _, items = load_set("bandt")
    return [q for q in items if q["http"] == 200]


def population_weights(pop):
    """Query id -> weight so that each climate zone counts in proportion to its number of L6 basins worldwide.

    The sample draws the same number of basins per zone, so rare zones are over-represented. Within each
    kind of query (s = single basin L6, b = 100 km buffer, t = single basin L8) a query's weight is
    zone_size / (queries of that kind in its zone), normalised to sum to 1 per kind.
    """
    man = json.loads((OUT / "manifest_population.json").read_text())
    size = {int(k): v for k, v in man["zone_sizes"].items()}
    cnt = collections.Counter((q["kind"], int(q["climate_zone"])) for q in pop)
    raw = {q["id"]: size[int(q["climate_zone"])] / cnt[(q["kind"], int(q["climate_zone"]))] for q in pop}
    tot = collections.Counter()
    for q in pop:
        tot[q["kind"]] += raw[q["id"]]
    return {q["id"]: raw[q["id"]] / tot[q["kind"]] for q in pop}


def ae_rows(q):
    """Band A-E rows of one query with the query-level context a rule needs."""
    b = q["body"]
    ctx = dict(qid=q["id"], scope=b["scope"]["type"], level=q["params"]["level"],
               n_units=b["scope"].get("n_units"), shortfall=b.get("shortfall"))
    return [(ctx, r) for r in b["rows"] if r["band"] != "T"]


_CATALOG = {}


def catalog(level):
    """The engine's own catalog table (indexed by payload variable name; has zero_fraction, kind, units).

    Read-only use of engine.load_catalog, so the zero fractions are the ones the percentiles were built from.
    """
    if level not in _CATALOG:
        import sys
        sys.path.insert(0, str(ROOT))
        from scripts.edop.areas import engine
        _CATALOG[level] = engine.load_catalog(level)
    return _CATALOG[level]


def zero_fraction(variable, level):
    cat = catalog(level)
    if variable not in cat.index:
        return None
    zf = cat.loc[variable, "zero_fraction"]
    return None if zf is None or zf != zf else float(zf)


def wquantile(values, weights, q):
    v = np.asarray(values, float)
    w = np.asarray(weights, float)
    o = np.argsort(v)
    v, w = v[o], w[o]
    c = np.cumsum(w) - 0.5 * w
    c /= w.sum()
    return float(np.interp(q, c, v))


def upsert_master(family, rows):
    """Replace this family's rows in the master table with `rows` (list of dicts keyed by MASTER_COLS)."""
    existing = []
    if MASTER.exists():
        with open(MASTER, newline="") as fh:
            existing = [r for r in csv.DictReader(fh) if r["family"] != family]
    out = existing + [{c: r.get(c, "") for c in MASTER_COLS} for r in rows]
    out.sort(key=lambda r: r["id"])
    with open(MASTER, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=MASTER_COLS)
        w.writeheader()
        w.writerows(out)
    return len(out)
