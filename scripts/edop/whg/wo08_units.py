"""WO-08 new units: S2.1b when the rain falls, S3.4 lakes and wetlands. Wording lives in profile_templates.md; each feature switches on when the
template has its trigger key (see KEYS_BY_TRIGGER, read by wo04_fill.check_keys)."""
from scripts.edop.whg import missing

# trigger key in the template -> every key the feature reads
KEYS_BY_TRIGGER = {'S3.4.lakes': {'S3.4', 'S3.4.lakes', 'S3.4.wetlands'},
                   'S2.1b.strong': {'S2.1b.even', 'S2.1b.moderate', 'S2.1b.clear', 'S2.1b.strong'}}

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
