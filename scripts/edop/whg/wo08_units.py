"""WO-08 new units: S2.1b when the rain falls, S3.4 lakes and wetlands, S1.4 the basin's other ecoregions, S8.3 the snap, S7.3 the seacoast. Wording lives in profile_templates.md; each feature switches on when the
template has its trigger key (see KEYS_BY_TRIGGER, read by wo04_fill.check_keys)."""
from scripts.edop.whg import missing

# trigger key in the template -> every key the feature reads
KEYS_BY_TRIGGER = {'S3.4.lakes': {'S3.4', 'S3.4.lakes', 'S3.4.wetlands'},
                   'S2.1b.strong': {'S2.1b.even', 'S2.1b.moderate', 'S2.1b.clear', 'S2.1b.strong'},
                   'S1.4.one': {'S1.4.one', 'S1.4.many'},
                   'S8.3': {'S8.3'},
                   'S7.3': {'S7.3'}}

MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
SEASON_CUTS = (0.15, 0.35, 0.60)   # precipitation concentration classes of the Seasonality tab (sandbox.html, renderSeasonality)


def unit_keys(text):
    """Required keys of every WO-08 feature whose trigger key the template has."""
    out = set()
    for trigger, keys in KEYS_BY_TRIGGER.items():
        if trigger in text:
            out |= keys
    return out


def all_keys():
    return set().union(*KEYS_BY_TRIGGER.values())


def lake_pct(conn, hid):
    """Lake share of the basin in percent (HydroLAKES limnicity, stored x 10), or None where missing."""
    v = missing.clean(conn.execute('SELECT lka_pc_sse FROM public.basin06 WHERE hybas_id = %s', (hid,)).fetchone()[0])
    return None if v is None else v / 10


def pct(v):
    """A share for prose: whole above 10, else one decimal with a trailing .0 dropped (lakes are stored to 0.1%)."""
    return f'{v:.0f}' if v >= 10 else f'{v:.1f}'.removesuffix('.0')


def fill_water_units(F, ok, no, val, fmt):
    """S3.4. Lakes: HydroLAKES limnicity (`lka_pc_sse`, in basin06 but not in a payload). Wetlands: the source's own
    group 2 (`wet_pc_sg2`: GLWD classes 4 to 12, excluding lakes, reservoirs and rivers, so no lake is counted twice).
    A part is stated when its share is above zero, by its value (the engine's outside_active_domain flag is about
    percentiles, not about the value being zero); silent when both are zero."""
    U = {}
    lake, wet = F.get('lake_pct'), val(F, 'wet_pct_grp2')
    parts = {}
    if lake:
        parts['lakes'] = pct(lake)
    if wet:
        parts['wetlands'] = pct(wet)
    note = f'lakes {lake}% (HydroLAKES), wetlands {wet}% (GLWD group 2: classes 4 to 12)'
    if lake is None and wet is None:
        U['S3.4'] = no('no lake or wetland value', na=True)
    elif not parts:
        U['S3.4'] = no(f'no lakes and no wetlands recorded ({note})', na=True)
    elif len(parts) == 2:
        U['S3.4'] = ok(fmt('S3.4', {'l': parts['lakes'], 'w': parts['wetlands']}), note)
    elif 'lakes' in parts:
        U['S3.4'] = ok(fmt('S3.4.lakes', {'l': parts['lakes']}), note)
    else:
        U['S3.4'] = ok(fmt('S3.4.wetlands', {'w': parts['wetlands']}), note)
    return U


def season_class(conc):
    """The Seasonality tab's four classes on precipitation concentration (0 even to 1 all in one month)."""
    return 'even' if conc < SEASON_CUTS[0] else 'moderate' if conc < SEASON_CUTS[1] else 'clear' if conc < SEASON_CUTS[2] else 'strong'


def fill_season_unit(F, ok, no, val, fmt):
    """S2.1b: the tab's concentration class, and the wettest month where the rain is not even. The wettest month, not the
    tab's circular "peak month", which differs from it by a month or more in about half the basins and by two or more in
    about one in eight, and would contradict the bars of a chart drawn from the monthly values."""
    conc, pre = val(F, 'pre_concentration'), val(F, 'pre_mm_monthly')
    if conc is None or not pre or len(pre) != 12:
        return {'S2.1b': no('no monthly precipitation')}
    k = season_class(conc)
    wet = max(range(12), key=lambda i: pre[i])      # the first of equals
    return {'S2.1b': ok(fmt('S2.1b.' + k, {'month': MONTHS[wet]}), f'concentration {conc:.2f} ({k}); wettest month {MONTHS[wet]} ({pre[wet]:.0f} mm)')}


# ---- S1.4: ecoregions (gaz."Ecoregions2017": eco_id, eco_name, geom) --------------------------------------
_INVALID = []


def invalid_ids(conn):
    """eco_ids whose geometry is not valid (69 of 847); they go through ST_MakeValid before any measuring."""
    if not _INVALID:
        _INVALID.extend(int(r[0]) for r in conn.execute('SELECT eco_id FROM gaz."Ecoregions2017" WHERE NOT ST_IsValid(geom)').fetchall())
    return _INVALID


NEXT_SQL = """
SELECT e.eco_id::bigint, e.eco_name, ST_Distance(ev.g::geography, p.g::geography) / 1000.0 AS km
FROM gaz."Ecoregions2017" e
CROSS JOIN LATERAL (SELECT CASE WHEN e.eco_id = ANY(%(inv)s) THEN ST_MakeValid(e.geom) ELSE e.geom END AS g) ev
CROSS JOIN (SELECT ST_SetSRID(ST_MakePoint(%(lon)s, %(lat)s), 4326) AS g) p
WHERE ST_DWithin(e.geom, p.g, %(deg)s) AND e.eco_id <> %(own)s
ORDER BY km LIMIT 1"""
SEARCH_DEG = 4.0   # prefilter in degrees (about 440 km of latitude; 150 km of longitude at 70 degrees north)


# S1.3 was dropped (Karl, 8 Nov); kept only for the evidence cells of wo08_new_units.ipynb.
def next_ecoregion(conn, lat, lon, own_eco_id):
    """(eco_id, name, km) of the nearest ecoregion polygon other than `own_eco_id`, measured from the point; None when
    there is none within the search window. Distance to the polygon, so an ecoregion that adjoins the point's is 0 km."""
    r = conn.execute(NEXT_SQL, dict(inv=invalid_ids(conn), lon=lon, lat=lat, deg=SEARCH_DEG, own=own_eco_id)).fetchone()
    return (int(r[0]), r[1], float(r[2])) if r else None


SHARES_SQL = """
SELECT e.eco_id::bigint, e.eco_name, ST_Area(ST_Intersection(b.geom, ev.g)::geography) / ST_Area(b.geom::geography) AS share
FROM public.basin06 b
JOIN gaz."Ecoregions2017" e ON e.geom && b.geom
CROSS JOIN LATERAL (SELECT CASE WHEN e.eco_id = ANY(%s) THEN ST_MakeValid(e.geom) ELSE e.geom END AS g) ev
WHERE b.hybas_id = %s AND ST_Intersects(ev.g, b.geom)"""


def eco_shares(conn, hid):
    """[(eco_id, name, share of the basin's area)] for every ecoregion that has area in the basin, largest first. The
    shares do not sum to 1 where part of the basin lies outside every ecoregion polygon (coasts, lakes)."""
    rows = conn.execute(SHARES_SQL, (invalid_ids(conn), int(hid))).fetchall()
    return sorted(((int(a), b, float(c)) for a, b, c in rows if c and c > 0), key=lambda r: -r[2])


# Share of the basin an ecoregion must cover to be named (Karl chose 10% after the 5, 10 and 20% results, wo08_results.md).
OTHER_ECO_SHARE = 0.10


def fill_ecoregion_units(F, ok, no, val, fmt):
    """S1.4: the ecoregions other than the point's, the signature's and the largest by area that cover at least
    OTHER_ECO_SHARE of the basin. Silent where there are none."""
    U = {}
    own = F['pt_eco_id'] if F['pt_eco_id'] is not None else (None if val(F, 'eco_id') is None else int(val(F, 'eco_id')))
    sh = F.get('eco_shares') or []
    skip = {own, F['pt_eco_id'], (None if val(F, 'eco_id') is None else int(val(F, 'eco_id'))), sh[0][0] if sh else None}
    other = [(n, v) for e, n, v in sh if e not in skip and v >= OTHER_ECO_SHARE]
    if not sh:
        U['S1.4'] = no('no ecoregion area in the basin', na=True)
    elif not other:
        U['S1.4'] = no(f'no other ecoregion covers {OTHER_ECO_SHARE:.0%} of the basin or more', na=True)
    else:
        note = ', '.join(f'{n} {v:.0%}' for n, v in other)
        U['S1.4'] = ok(fmt('S1.4.one', {'eco1': other[0][0]}) if len(other) == 1 else fmt('S1.4.many', {'list': join_and([n for n, _ in other])}), note)
    return U


def join_and(items):
    """'a', 'a and b', 'a, b and c'"""
    return items[0] if len(items) == 1 else ', '.join(items[:-1]) + ' and ' + items[-1]


# ---- S8.3: the snap (profile scripts only; the engine and the public API still answer no_basin) ---------------------
SNAP_M = 1000.0   # a point this close to a basin and inside none is moved to it (WO-03 D10)
SNAP_NUDGES_M = (3.0, 30.0, 300.0)   # how far inside the edge the moved point is put, so that ST_Contains holds

SNAP_SQL = """
WITH p AS (SELECT ST_SetSRID(ST_MakePoint(%(lon)s, %(lat)s), 4326) AS g),
n AS (SELECT b.hybas_id, b.geom, p.g, ST_Distance(b.geom::geography, p.g::geography) AS d
      FROM public.basin06 b, p WHERE ST_DWithin(b.geom::geography, p.g::geography, %(m)s)
      ORDER BY b.geom <-> p.g LIMIT 1),
c AS (SELECT hybas_id, geom, d, ST_ClosestPoint(geom, g) AS e, ST_PointOnSurface(geom) AS i FROM n)
SELECT hybas_id, d,
       ST_Y(ST_LineInterpolatePoint(ST_MakeLine(e, i), LEAST(1.0, %(nudge)s / NULLIF(ST_Length(ST_MakeLine(e, i)::geography), 0)))),
       ST_X(ST_LineInterpolatePoint(ST_MakeLine(e, i), LEAST(1.0, %(nudge)s / NULLIF(ST_Length(ST_MakeLine(e, i)::geography), 0)))),
       ST_Contains(geom, ST_LineInterpolatePoint(ST_MakeLine(e, i), LEAST(1.0, %(nudge)s / NULLIF(ST_Length(ST_MakeLine(e, i)::geography), 0))))
FROM c"""


def snap_point(conn, lat, lon):
    """(hybas_id, metres moved, lat, lon of a point just inside that basin) for a point that lies in no basin but within
    SNAP_M of one; None otherwise (the point is inside a basin, or nothing is near: no_basin stays no_basin)."""
    for nudge in SNAP_NUDGES_M:
        r = conn.execute(SNAP_SQL, dict(lat=lat, lon=lon, m=SNAP_M, nudge=nudge)).fetchone()
        if r is None or r[1] == 0:
            return None
        if r[4]:
            return int(r[0]), float(r[1]), float(r[2]), float(r[3])
    return None


# ---- S7.3: the coastline (gaz.ne_coastline_10m, Natural Earth 1:10m; loaded by wo08_load_coastline.py) ----
# The Caspian is gid 958 (a closed ring) plus the island rings inside it. Natural Earth treats it as coast; whether a
# profile does is a switch (CASPIAN_IS_COAST); Karl decided it does (8 Nov).
CASPIAN_IS_COAST = True
CASPIAN_SQL = "(k.gid = 958 OR ST_Within(k.geom, (SELECT ST_MakePolygon(geom) FROM gaz.ne_coastline_10m WHERE gid = 958)))"
COAST_WHERE = {True: 'TRUE', False: 'NOT ' + CASPIAN_SQL}
COAST_NEAR_DEG = 5.0   # prefilter for the outline tests below (they only ask 'within COAST_TOUCH_KM?')
COAST_TOUCH_KM = 2.0   # the basin's outline (S7.2) or its edge nearest the point (S7.3) counts as the seacoast within this (Karl, 8 Nov)


# S7.1a (distance to the seacoast) was dropped, Karl 8 Nov; coast_km stays for the evidence cells of wo08_new_units.ipynb.
def coast_km(conn, lat, lon, caspian=None):
    """Distance in km from the point to the nearest coastline, however far; None only if the table is empty. The five
    nearest lines by planar distance are measured on the sphere, which is enough to find the nearest."""
    caspian = CASPIAN_IS_COAST if caspian is None else caspian
    r = conn.execute(f"""SELECT min(ST_Distance(t.geom::geography, t.g::geography)) / 1000.0 FROM (
        SELECT k.geom, p.g FROM gaz.ne_coastline_10m k, (SELECT ST_SetSRID(ST_MakePoint(%s, %s), 4326) AS g) p
        WHERE {COAST_WHERE[caspian]} ORDER BY k.geom <-> p.g LIMIT 5) t""", (lon, lat)).fetchone()
    return None if r[0] is None else float(r[0])


def basin_coast(conn, hid, lat, lon, caspian=None):
    """(km from the basin's outline to the nearest coastline, km from the point's nearest outline spot to the nearest
    coastline); each None when the coastline is further than COAST_NEAR_DEG. The first says the basin touches the coast
    (S7.2); the second that the edge of the basin nearest the point is the coast (S7.3)."""
    caspian = CASPIAN_IS_COAST if caspian is None else caspian
    r = conn.execute(f"""WITH b AS (SELECT ST_Boundary(geom) AS o FROM public.basin06 WHERE hybas_id = %s),
        n AS (SELECT ST_ClosestPoint(b.o, ST_SetSRID(ST_MakePoint(%s, %s), 4326)) AS g, b.o FROM b)
        SELECT (SELECT min(ST_Distance(k.geom::geography, n.o::geography)) / 1000.0 FROM gaz.ne_coastline_10m k WHERE ST_DWithin(k.geom, n.o, %s) AND {COAST_WHERE[caspian]}),
               (SELECT min(ST_Distance(k.geom::geography, n.g::geography)) / 1000.0 FROM gaz.ne_coastline_10m k WHERE ST_DWithin(k.geom, n.g, %s) AND {COAST_WHERE[caspian]})
        FROM n""", (int(hid), lon, lat, COAST_NEAR_DEG, COAST_NEAR_DEG)).fetchone()
    return tuple(None if v is None else float(v) for v in r)


def fill_coast_units(F, ok, no, val, fmt):
    """S7.3: the edge of the basin nearest the point is the seacoast (Natural Earth 1:10m, the Caspian counted), within
    COAST_TOUCH_KM. S7.2 (in wo04_fill) speaks for the signature's coast flag or an outline within COAST_TOUCH_KM, so S7.3
    never speaks where S7.2 is silent."""
    c = F.get('coast')
    if c is not None and c['s'] is not None and c['s'] <= COAST_TOUCH_KM:
        return {'S7.3': ok(fmt('S7.3', {}), f"nearest edge {c['s']:.1f} km from the coastline")}
    return {'S7.3': no('the nearest edge of the basin is not the seacoast (optional part not stated)', na=True)}
