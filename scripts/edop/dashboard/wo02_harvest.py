"""WO-02 payload harvest: persist full /api/areas payloads for the fixture and population sets.

Local server only (uvicorn app.main:app on :8000); GET requests only. Payloads are saved
exactly as received (detail=true), one file per query, under output/edop/dashboard/wo02/.

    python scripts/edop/dashboard/wo02_harvest.py plan-fixtures      # write manifest_fixtures.json
    python scripts/edop/dashboard/wo02_harvest.py plan-population    # draw sample, write manifest_population.json
    python scripts/edop/dashboard/wo02_harvest.py plan-bandt         # Band T-only fixtures F35-F45, own manifest
    python scripts/edop/dashboard/wo02_harvest.py fetch fixtures     # fetch every query in the manifest
    python scripts/edop/dashboard/wo02_harvest.py fetch population   # (add --only ID ... to refetch some)
    python scripts/edop/dashboard/wo02_harvest.py pretty fixtures    # re-indent saved payloads (whitespace only)
Payloads are saved indented (values untouched; `bytes` in the manifest is the size as received).
"""
import argparse, datetime, json, random, subprocess, sys, time, urllib.error, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "output/edop/dashboard/wo02"
BASE = "http://localhost:8000/api/areas"
SEED = 20261030
PER_ZONE = 17            # basins per climate zone (cap); zones with fewer keep all
N_BUFFER, N_L8 = 100, 100

TIMBUKTU = (16.8167, -2.9833)
ROME = (41.90, 12.50)
KAIFENG = (34.80, 114.30)


def q(id, scope, level, lat=None, lon=None, bands="ABCDE", span=None, radius_km=None,
      polity=None, year=None, why=""):
    p = dict(scope=scope, level=level, bands=bands, detail="true")
    if lat is not None: p.update(lat=lat, lon=lon)
    if radius_km: p["radius_km"] = radius_km
    if polity: p.update(polity=polity, year=year)
    if span: p.update(from_year=span[0], to_year=span[1])
    return dict(id=id, params=p, condition=why)


def fixtures():
    S, B, P = "single_basin", "buffer", "polity"
    return [
        q("F01", S, 6, *TIMBUKTU, why="arid; exogenous water (Niger); outside_active_domain"),
        q("F02", S, 8, *TIMBUKTU, why="L6 vs L8 pair"),
        q("F03", B, 6, *TIMBUKTU, radius_km=25, why="small buffer (fewer than 5 basins)"),
        q("F04", B, 6, *TIMBUKTU, radius_km=100, why="large buffer; suppressed scores; section 2.6 reference counts"),
        q("F05", S, 6, -22.46, -68.93, why="Calama: hyper-arid (endo flag 0)"),
        q("F06", S, 6, -3.12, -60.02, why="Manaus: humid"),
        q("F07", S, 6, -13.53, -71.97, why="Cusco: mountain"),
        q("F08", S, 6, 29.65, 91.12, why="Lhasa: mountain plateau; permafrost spread"),
        q("F09", S, 6, 62.03, 129.73, why="Yakutsk: permafrost concentrated; cold"),
        q("F10", S, 6, 30.04, 31.24, why="Cairo: exogenous water (Nile)"),
        q("F11", S, 6, 40.76, -111.89, why="Salt Lake City: endorheic"),
        q("F12", S, 6, 39.47, 75.99, why="Kashgar: endorheic, arid, mountain-ringed"),
        q("F13", S, 6, 38.72, -9.14, why="Lisbon: coastal"),
        q("F14", S, 6, *KAIFENG, why="Kaifeng: inland, temperate"),
        q("F15", S, 8, *KAIFENG, why="L6 vs L8 pair"),
        q("F16", S, 6, *ROME, why="Rome: coastal-ish"),
        q("F17", S, 8, *ROME, why="L6 vs L8 pair"),
        q("F18", B, 6, *ROME, radius_km=200, why="low_coverage by sea (about 50% sea)"),
        q("F19", B, 6, 43.0, 51.0, radius_km=150, why="Caspian shore: low_coverage, shortfall about 0.75"),
        q("F20", B, 6, 72.0, -40.0, radius_km=300, why="Greenland: no_data slope rows; low_coverage wetland_class"),
        q("F21", S, 6, 35.69, -105.94, why="Santa Fe: mountain, semi-arid"),
        q("F22", P, 6, polity="Northern Song", year=961, why="one-year slice (961-961); not_areal discharge; modality skipped"),
        q("F23", P, 8, polity="Northern Song", year=961, why="polity at L8 (crosswalk path)"),
        q("F24", P, 6, polity="Roman Republic", year=-100, why="long slice; marginal_exposure"),
        q("F25", P, 6, polity="Northern Song", year=1000, why="medium slice (990-1017)"),
        q("F26", S, 6, *TIMBUKTU, bands="ABCDET", span=(1475, 1525), why="CE span with LMR and HYDE; 7 eVolv2k events"),
        q("F27", S, 6, *TIMBUKTU, bands="ABCDET", span=(1250, 1300), why="CE span with an eVolv2k event (1257)"),
        q("F28", S, 6, *ROME, bands="ABCDET", span=(-200, -100), why="BCE span: HYDE nearest-epoch; no LMR"),
        q("F29", P, 6, bands="T", polity="Northern Song", year=961, span=(961, 1027), why="Band T on a polity"),
        q("F30", S, 6, *KAIFENG, bands="ABCDET", span=(1000, 1100), why="CE span, other region"),
        q("F31", S, 6, 0.0, -30.0, why="open Atlantic: expected 404 NoBasinsError"),
        q("F32", S, 6, 35.01, 135.77, why="Kyoto: humid temperate, Japan"),
        q("F33", S, 6, *TIMBUKTU, bands="ABCDET", span=(1140, 1170), why="CE span with no eVolv2k event (gap 1137-1171)"),
        q("F34", S, 6, *TIMBUKTU, bands="ABCDET", span=(1940, 1960), why="span containing the 1950 HYDE epoch (hyde_caveat)"),
    ]


def bandt_fixtures():
    """Band T-only fixtures added for the Band T family (Step 3). Kept in their own manifest so the main fixture set,
    and the earlier families' results, are unchanged."""
    S, B, P = "single_basin", "buffer", "polity"
    return [
        q("F35", B, 6, *TIMBUKTU, radius_km=100, bands="T", span=(1475, 1525), why="Band T over a buffer footprint"),
        q("F36", B, 6, *ROME, radius_km=200, bands="T", span=(1000, 1100), why="Band T over a buffer with sea (about half the circle)"),
        q("F37", S, 8, *TIMBUKTU, bands="T", span=(1475, 1525), why="Band T at L8: the LMR cell count at the smaller scale"),
        q("F38", P, 8, bands="T", polity="Northern Song", year=961, span=(961, 1027), why="Band T on a polity at L8 (crosswalk path)"),
        q("F39", P, 6, bands="T", polity="Roman Republic", year=-100, span=(-200, -100), why="BCE polity: no LMR, HYDE nearest epoch, eVolv2k events"),
        q("F40", S, 6, *TIMBUKTU, bands="T", span=(1257, 1257), why="single-year span (the Samalas event year)"),
        q("F41", S, 6, *TIMBUKTU, bands="T", span=(1980, 2020), why="span crossing the end of the LMR coverage (1998) and HYDE's annual epochs"),
        q("F42", S, 6, *ROME, bands="T", span=(-50, 50), why="span crossing the BCE and CE boundary (LMR starts at 1 CE)"),
        q("F43", S, 6, -13.96, -61.69, bands="T", span=(1475, 1525), why="the largest L6 basin (216,379 km2, Bolivia and Brazil): the most LMR cells a single basin can have"),
        q("F44", S, 6, *TIMBUKTU, bands="T", span=(800, 1200), why="a long span (401 years): row counts and payload size"),
        q("F45", B, 6, *TIMBUKTU, radius_km=500, bands="T", span=(1475, 1525), why="a 500 km buffer: a large footprint, many LMR cells (low_resolution expected false)"),
    ]


def provenance():
    git = lambda *a: subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    return dict(app_version="0.4", git_commit=git("rev-parse", "--short", "HEAD"),
                git_describe=git("describe", "--tags", "--always"), branch=git("branch", "--show-current"),
                planned=str(datetime.date.today()))


def write_manifest(name, entries, extra=None):
    OUT.mkdir(parents=True, exist_ok=True)
    m = dict(set=name, base=BASE, provenance=provenance(), entries=entries, **(extra or {}))
    (OUT / f"manifest_{name}.json").write_text(json.dumps(m, indent=1, ensure_ascii=False))
    print(f"manifest_{name}.json: {len(entries)} queries")


def plan_population():
    sys.path.insert(0, str(ROOT))
    from app.db.connection import db_connect
    rng = random.Random(SEED)
    with db_connect() as c, c.cursor() as cur:
        cur.execute("""select clz_cl_smj, hybas_id,
                              ST_Y(ST_PointOnSurface(geom)), ST_X(ST_PointOnSurface(geom))
                       from public.basin06 where clz_cl_smj is not null and clz_cl_smj > 0
                       order by hybas_id""")
        rows = cur.fetchall()
    zones = {}
    for z, h, la, lo in rows: zones.setdefault(z, []).append((h, la, lo))
    picked = []
    for z in sorted(zones):
        picked += [(z, *r) for r in rng.sample(zones[z], min(PER_ZONE, len(zones[z])))]
    idx = list(range(len(picked)))
    buf = set(rng.sample(idx, min(N_BUFFER, len(idx))))
    l8 = set(rng.sample(idx, min(N_L8, len(idx))))
    entries = []
    for i, (z, h, la, lo) in enumerate(picked):
        la, lo = round(la, 5), round(lo, 5)
        base = f"P{i:03d}"
        why = f"climate zone {z}; L6 basin {h}"
        entries.append(q(base + "s", "single_basin", 6, la, lo, why=why))
        if i in buf: entries.append(q(base + "b", "buffer", 6, la, lo, radius_km=100, why=why))
        if i in l8: entries.append(q(base + "t", "single_basin", 8, la, lo, why=why + " (L8 at same point)"))
        for e in entries:
            if e["id"].startswith(base): e["hybas_id_l6"], e["climate_zone"] = h, z
    write_manifest("population", entries, dict(
        method=f"basin unit; stratified by clz_cl_smj; up to {PER_ZONE} L6 basins per zone; query point = ST_PointOnSurface; "
               f"{len(buf)} also get a 100 km buffer, {len(l8)} also get an L8 single-basin query; seed {SEED}",
        zone_sizes={str(z): len(v) for z, v in sorted(zones.items())}))


def pretty(body):
    """Indent a JSON body; values are unchanged. Non-JSON bodies are returned as received."""
    try: return json.dumps(json.loads(body), indent=1, ensure_ascii=False).encode()
    except ValueError: return body


def pretty_set(name):
    n = 0
    for f in sorted((OUT / "payloads" / name).glob("*.json")):
        f.write_bytes(pretty(f.read_bytes())); n += 1
    print("reformatted", n)


def fetch(name, only=None):
    m = json.loads((OUT / f"manifest_{name}.json").read_text())
    pdir = OUT / "payloads" / name
    pdir.mkdir(parents=True, exist_ok=True)
    m["provenance"]["captured"] = str(datetime.date.today())
    done = 0
    for e in m["entries"]:
        if only and e["id"] not in only: continue
        url = BASE + "?" + urllib.parse.urlencode(e["params"])
        t0 = time.time()
        try:
            with urllib.request.urlopen(url, timeout=600) as r: body, code = r.read(), r.status
        except urllib.error.HTTPError as ex: body, code = ex.read(), ex.code
        e["result"] = dict(http=code, bytes=len(body), seconds=round(time.time() - t0, 1), file=f"payloads/{name}/{e['id']}.json")
        (pdir / f"{e['id']}.json").write_bytes(pretty(body))
        done += 1
        print(e["id"], code, len(body), e["result"]["seconds"], "s", flush=True)
    (OUT / f"manifest_{name}.json").write_text(json.dumps(m, indent=1, ensure_ascii=False))
    print("fetched", done)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["plan-fixtures", "plan-population", "plan-bandt", "fetch", "pretty"])
    ap.add_argument("which", nargs="?", choices=["fixtures", "population", "bandt"])
    ap.add_argument("--only", nargs="*")
    a = ap.parse_args()
    if a.cmd == "plan-fixtures": write_manifest("fixtures", fixtures())
    elif a.cmd == "plan-bandt": write_manifest("bandt", bandt_fixtures())
    elif a.cmd == "plan-population": plan_population()
    elif a.cmd == "pretty": pretty_set(a.which)
    else: fetch(a.which, a.only)
