"""Regenerate docs/design/dashboard/examples/*.json for the Sandbox cheat sheet.

Needs the local server running (uvicorn app.main:app, http://localhost:8000). GET requests only.
Trims each response (geometry dropped, long lists capped, one representative row per
method/status/score-state) and stamps the capture date. Run from anywhere:
    python scripts/edop/dashboard/make_cheatsheet_examples.py
"""
import json, urllib.request, urllib.parse, collections, copy, os, datetime
from pathlib import Path
B="http://localhost:8000/api/"
OUT=str(Path(__file__).resolve().parents[3] / "docs/design/dashboard/examples")
def get(path, **kw):
    q=urllib.parse.urlencode(kw)
    with urllib.request.urlopen(B+path+("?"+q if q else ""),timeout=180) as r:
        return json.load(r)
def save(name, obj):
    with open(os.path.join(OUT,name),"w") as f: json.dump(obj,f,indent=1,ensure_ascii=False)
    print(name, os.path.getsize(os.path.join(OUT,name)),"bytes")

def state(r):
    return (r['method'], r['status'],
            'score' if r['representative_score'] is not None else 'noscore',
            'raw' if r['representative_raw'] is not None else 'noraw',
            'suppressed' if r['score_suppressed'] else '')

def compact(r):
    return {k:r[k] for k in ('variable','band','method','status','representative_score','representative_raw','units','n_units','coherence','modality','score_suppressed') if k in r}

def shrink_dist(d):
    """cap long arrays inside a detail block"""
    d=copy.deepcopy(d)
    dist=d.get('distribution')
    if isinstance(dist,dict):
        for k in ('bins','weights'):
            if isinstance(dist.get(k),list) and len(dist[k])>12: dist[k]=dist[k][:12]+['...%d more'%(len(dist[k])-12)]
    return d

def areal_example(payload, note, query):
    rows=payload['rows']
    basin=[r for r in rows if r['band']!='T']
    tt=[r for r in rows if r['band']=='T']
    reps={}
    for r in basin:
        reps.setdefault(state(r), r)
    rep_rows=[]
    for k,r in reps.items():
        rr=copy.deepcopy(r); rr['detail']=shrink_dist(r.get('detail',{})); rep_rows.append(rr)
    out={"_note":note,"_query":query,"_captured":str(datetime.date.today()),
         "_trimmed":"geometry omitted; rows reduced to (a) a compact one-line summary of EVERY A-E row and (b) the full row for one representative of each distinct method/status/score-state; histogram arrays capped at 12 entries; Band T rows reduced to first/middle/last per variable.",
         "scope":payload['scope'],"shortfall":payload['shortfall'],"bands":payload['bands'],"temporal":payload.get('temporal'),
         "caveats":payload.get('caveats'),
         "extra_top_level_keys":{k:payload[k] for k in payload if k not in ('scope','shortfall','bands','temporal','caveats','rows')} if any(k not in ('scope','shortfall','bands','temporal','caveats','rows') for k in payload) else {},
         "row_counts":{"A-E rows":len(basin),"T rows":len(tt),"by_method":dict(collections.Counter(r['method'] for r in basin)),"by_status":dict(collections.Counter(r['status'] for r in basin))},
         "rows_summary_all_A_to_E":[compact(r) for r in basin],
         "representative_rows_full":rep_rows}
    if tt:
        byv=collections.defaultdict(list)
        for r in tt: byv[r['variable']].append(r)
        sel=[]
        for v,lst in byv.items():
            picks=[lst[0]] if len(lst)==1 else [lst[0],lst[len(lst)//2],lst[-1]]
            for r in picks:
                rr=copy.deepcopy(r); rr['detail']=shrink_dist(r.get('detail',{})); sel.append(rr)
        out["band_t_rows_selected"]=sel
        out["band_t_counts_by_variable"]={v:len(l) for v,l in byv.items()}
    return out

lat,lon=16.8167,-2.9833
common=dict(level=6,detail="true")
# 1 single basin (A-E)
p=get("areas",scope="single_basin",lat=lat,lon=lon,bands="ABCDE",**common)
save("01_single_basin_timbuktu_L6.json", areal_example(p,"Single containing basin. n_units=1: rows carry raw value + percentile; no coherence badge. Compare with 02 and 03.",
     "/api/areas?scope=single_basin&lat=16.8167&lon=-2.9833&level=6&bands=ABCDE&detail=true"))
# 2 buffer
p=get("areas",scope="buffer",lat=lat,lon=lon,radius_km=100,bands="ABCDE",**common)
save("02_buffer_100km_timbuktu_L6.json", areal_example(p,"100 km buffer, 9 basins. Distribution over member basins; no raw values on continuous rows; two-regime rows have the score suppressed. Compare with 01.",
     "/api/areas?scope=buffer&lat=16.8167&lon=-2.9833&radius_km=100&level=6&bands=ABCDE&detail=true"))
# 3 polity
p=get("areas",scope="polity",polity="Northern Song",year=961,bands="ABCDE",level=6,detail="true")
save("03_polity_northern_song_961_L6.json", areal_example(p,"Polity slice (Northern Song, year 961), 156 member basins. Discharge rows are not_areal; modality pass skipped. No Band T here (see 04).",
     "/api/areas?scope=polity&polity=Northern Song&year=961&level=6&bands=ABCDE&detail=true"))
# 4 band T single basin
p=get("areas",scope="single_basin",lat=lat,lon=lon,bands="ABCDET",from_year=1475,to_year=1525,**common)
ex=areal_example(p,"Single basin with Band T over 1475-1525 CE. Shows HYDE (one epoch), LMR (one row per year), eVolv2k (event years).",
     "/api/areas?scope=single_basin&lat=16.8167&lon=-2.9833&level=6&bands=ABCDET&detail=true&from_year=1475&to_year=1525")
ex.pop("rows_summary_all_A_to_E"); ex.pop("representative_rows_full")
ex["_trimmed"]="A-E rows omitted (identical to 01); Band T rows reduced to first/middle/last per variable; histogram arrays capped at 12 entries."
save("04_band_t_timbuktu_1475_1525.json", ex)
# 5 band T polity
p=get("areas",scope="polity",polity="Northern Song",year=961,bands="T",level=6,detail="true",from_year=961,to_year=1027)
ex=areal_example(p,"Polity with Band T over the polity's whole span 961-1027 (not a single slice: the Sandbox itself sends the selected slice's own years, e.g. 990-1017 for slice 5). NB bands=T still returned all A-E rows (known bug); only the T rows are shown here.",
     "/api/areas?scope=polity&polity=Northern Song&year=961&level=6&bands=T&detail=true&from_year=961&to_year=1027")
ex.pop("rows_summary_all_A_to_E"); ex.pop("representative_rows_full")
ex["_trimmed"]="A-E rows omitted; Band T rows reduced to first/middle/last per variable; histogram arrays capped at 12 entries."
save("05_band_t_polity_northern_song.json", ex)
# 6 ring topology
rg=get("basin/ring",lat=lat,lon=lon,level=6)
ring={"_note":"Ring topology as the Sandbox receives it from /api/basin/ring: centre id and per-neighbour interior point and bearing. Geometry omitted. The ring's signature is the CENTRE basin's single_basin signature (01); each neighbour is fetched separately with scope=single_basin at its neighbor_lat/lon.",
      "_query":"/api/basin/ring?lat=16.8167&lon=-2.9833&level=6","_captured":str(datetime.date.today()),
      "center_hybas_id":rg['center']['properties']['hybas_id'],
      "n_neighbours":len(rg['ring']),
      "ring":[{k:m[k] for k in ('hybas_id','neighbor_lat','neighbor_lon','border_bearing','centroid_bearing')} for m in rg['ring']]}
save("06_ring_topology_timbuktu_L6.json", ring)
# 7 public basin signature (parallel call)
s=get("signature",lat=lat,lon=lon,level=6,bands="ABCE",scope="basin")
s2=copy.deepcopy(s)
if 'geom_geojson' in s2: s2['geom_geojson']="<omitted>"
for b,v in s2.get('signature_bands',{}).items():
    items=v.get('items',[])
    v['items_total']=len(items)
    # keep monthly arrays (Seasonality uses them) + first 4 other items
    keep=[i for i in items if str(i.get('key','')).endswith('_monthly')] + [i for i in items if not str(i.get('key','')).endswith('_monthly')][:4]
    v['items']=keep
s2={"_note":"The parallel public call (/api/signature?scope=basin&bands=ABCE) that feeds the Analysis and Seasonality tabs: raw values per variable, no percentiles. Items trimmed per band (monthly arrays kept).",
    "_query":"/api/signature?lat=16.8167&lon=-2.9833&level=6&bands=ABCE&scope=basin","_captured":str(datetime.date.today()),**s2}
save("07_public_signature_basin_timbuktu_L6.json", s2)
# 8 context
c=get("context",lat=lat,lon=lon,level=6,radius_km=500)
c["_note"]="Context tab: 7 variables, each value with its percentile against all basins and against basins within the radius."
c["_query"]="/api/context?lat=16.8167&lon=-2.9833&level=6&radius_km=500"
save("08_context_timbuktu_500km.json", c)
# 9 similarity
j=get("similarity/conjunction",lat=lat,lon=lon,lens="climate.precip",level=6,corr=0.9,ratio=1.5,cv=0.15)
j2={k:v for k,v in j.items() if k!='members'}
j2["members_total"]=len(j['members']); j2["members_first_5"]=j['members'][:5]
j2["_note"]="Similarity tab, Precipitation lens, default thresholds: the set of matching basins (only 5 of 119 shown), how far they reach, the query basin's own values."
j2["_query"]="/api/similarity/conjunction?lat=16.8167&lon=-2.9833&lens=climate.precip&level=6&corr=0.9&ratio=1.5&cv=0.15"
save("09_similarity_precip_timbuktu.json", j2)
