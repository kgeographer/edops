"""WO-07 part B: class words for the profile. Terrain (S4.1a), soil composition (S4.1b), karst and permafrost (S4.3),
land cover (S5.1c) and the aridity class (S2.4). Wording lives in profile_templates.md; the sources' own classes are here."""
import math

# FAO Guidelines for soil description (2006), Table 7, slope gradient classes: (upper limit in percent, name).
# The table's three classes under 1% (flat, level, nearly level) are merged into 'level': the words are near-synonyms and slope is stored only to 0.1 degree (0.17%)
FAO_SLOPE = [(1, 'level'), (2, 'very gently sloping'), (5, 'gently sloping'),
             (10, 'sloping'), (15, 'strongly sloping'), (30, 'moderately steep'), (60, 'steep'), (math.inf, 'very steep')]
# UNEP aridity classes on P/PET (secondary sources only; see wo07_results.md): (upper limit, name)
UNEP = [(0.05, 'hyper-arid'), (0.2, 'arid'), (0.5, 'semi-arid'), (0.65, 'dry sub-humid'), (math.inf, 'humid')]
GLC_CULTIVATED = 16   # GLC2000 "Cultivated and managed areas"
DEG_STEP = 0.05       # slope is stored to 0.1 degree

KEYS = {'S4.1a', 'S4.1b', 'S4.1b.texture', 'S4.3.karst', 'S4.3.permafrost', 'S5.1c', 'S2.4'}


def class_keys():
    return set(KEYS)


def _cls(table, v):
    return next(name for top, name in table if v < top)


def slope_pct(deg):
    return math.tan(math.radians(deg)) * 100


def slope_class(deg):
    """(class name, percent, True when the 0.1 degree storage step could put it in a neighbouring class)."""
    p = slope_pct(deg)
    lo, hi = slope_pct(max(deg - DEG_STEP, 0)), slope_pct(deg + DEG_STEP)
    return _cls(FAO_SLOPE, p), p, _cls(FAO_SLOPE, lo) != _cls(FAO_SLOPE, hi)


def aridity_class(ai100):
    """(class name, index, True when the integer storage of index x 100 could put it in a neighbouring class)."""
    ai = ai100 / 100
    return _cls(UNEP, ai), ai, _cls(UNEP, (ai100 - 0.5) / 100) != _cls(UNEP, (ai100 + 0.5) / 100)


def normalise(sand, silt, clay):
    """Shares scaled to total 100; returns (rounded shares summing to 100, raw total)."""
    tot = sand + silt + clay
    raw = [100 * v / tot for v in (sand, silt, clay)]
    out = [round(v) for v in raw]
    out[raw.index(max(raw))] += 100 - sum(out)   # absorb rounding in the largest share
    return out, tot


def texture_classes(sa, si, cl):
    """Every USDA texture class (Soil Survey Manual, ch. 3, pp. 122 to 124, fine-earth fraction) whose definition holds; exactly one should."""
    out = []
    if sa > 85 and si + 1.5 * cl < 15:
        out.append('sand')
    if 70 <= sa <= 90 and si + 1.5 * cl >= 15 and si + 2 * cl < 30:
        out.append('loamy sand')
    if (7 <= cl < 20 and sa > 52 and si + 2 * cl >= 30) or (cl < 7 and si < 50 and si + 2 * cl >= 30):
        out.append('sandy loam')
    if 7 <= cl < 27 and 28 <= si < 50 and sa <= 52:
        out.append('loam')
    if (si >= 50 and 12 <= cl < 27) or (50 <= si < 80 and cl < 12):
        out.append('silt loam')
    if si >= 80 and cl < 12:
        out.append('silt')
    if 20 <= cl < 35 and si < 28 and sa > 45:
        out.append('sandy clay loam')
    if 27 <= cl < 40 and 20 < sa <= 45:
        out.append('clay loam')
    if 27 <= cl < 40 and sa <= 20:
        out.append('silty clay loam')
    if cl >= 35 and sa > 45:
        out.append('sandy clay')
    if cl >= 40 and si >= 40:
        out.append('silty clay')
    if cl >= 40 and sa <= 45 and si < 40:
        out.append('clay')
    return out


def texture(sa, si, cl):
    """(class, True when a change of up to half a percentage point in any share, the rounding of the stored values, gives another class)."""
    c = texture_classes(sa, si, cl)
    if len(c) != 1:
        return None, True
    near = {tuple(texture_classes(sa + a, si + b, cl + d)) for a in (-.5, 0, .5) for b in (-.5, 0, .5) for d in (-.5, 0, .5)}
    return c[0], len(near) > 1


def glc_shares(conn, hid):
    """[(share %, GLC2000 label)] for the basin, largest first."""
    cols = ', '.join(f'glc_pc_s{i:02d}' for i in range(1, 23))
    row = conn.execute(f'SELECT {cols} FROM public.basin06 WHERE hybas_id = %s', (hid,)).fetchone()
    lab = dict(conn.execute('SELECT * FROM public.lu_glc').fetchall())
    return sorted(((row[i], int(i + 1), lab[str(i + 1)]) for i in range(22) if row[i]), reverse=True) if row else []


def lower(label):
    return label[0].lower() + label[1:]


def glc_other(shares):
    """The largest class other than cultivated and managed areas: (share, label) or None."""
    for sh, code, lab in shares:
        if code != GLC_CULTIVATED:
            return sh, lab
    return None


def fill_class_units(F, ok, no, sigval, fmt, tidy):
    pub = F['pub']
    U = {}
    deg = sigval(pub, 'slope_avg')
    if deg is None or deg < 0:   # BasinATLAS NoData (-9999) can arrive scaled; no real value is negative
        U['S4.1a'] = no('no mean slope')
    else:
        name, p, edge = slope_class(deg)
        shown = f'{p:.1f}' if p < 10 else f'{p:.0f}'
        U['S4.1a'] = ok(fmt('S4.1a', {'class': name, 'pct': shown}),
                        f'mean slope {deg} degrees = {p:.2f}%' + ('; the 0.1 degree storage step straddles a class boundary' if edge else ''))
    sand, silt, clay = (sigval(pub, k) for k in ('pct_sand', 'pct_silt', 'pct_clay'))
    if None in (sand, silt, clay) or min(sand, silt, clay) < 0 or sand + silt + clay == 0:
        U['S4.1b'] = no('no soil composition')
    else:
        (s, t, c), tot = normalise(sand, silt, clay)
        tx, edge = texture(s, t, c)
        note = f'raw {sand}/{silt}/{clay}, total {tot:g}' + ('; normalised to 100' if tot != 100 else '')
        if tx is None:
            U['S4.1b'] = ok(fmt('S4.1b', {'sand': s, 'silt': t, 'clay': c}), note + '; no single USDA class (' + ', '.join(texture_classes(s, t, c)) + ')')
        else:
            U['S4.1b'] = ok(fmt('S4.1b.texture', {'sand': s, 'silt': t, 'clay': c, 'texture': tx}),
                            note + f'; USDA class {tx}' + ('; a half-point change in a share gives another class' if edge else ''))
    kar, prm = (v if v is not None and v >= 0 else None for v in (sigval(pub, 'karst'), sigval(pub, 'permafrost_extent')))
    parts = []
    if kar:
        parts.append(fmt('S4.3.karst', {'k': f'{kar:.0f}'}))
    if prm:
        parts.append(fmt('S4.3.permafrost', {'p': f'{prm:.0f}'}))
    U['S4.3'] = ok(' '.join(parts), f'karst {kar}, permafrost {prm}') if parts else no('no karst and no permafrost recorded', na=True)
    o = glc_other(F['glc']) if F.get('glc') else None
    if o is None:
        U['S5.1c'] = no('no land cover other than cultivated areas', na=True)
    else:
        top = F['glc'][0]
        U['S5.1c'] = ok(fmt('S5.1c', {'label': lower(o[1]), 'share': f'{o[0]:.0f}'}),
                        f'GLC2000 largest class: {top[2]} {top[0]:.0f}%; largest other than cultivated: {o[1]} {o[0]:.0f}%')
    ai = sigval(pub, 'aridity')
    if ai is None or ai < 0:
        U['S2.4'] = no('no aridity index')
    else:
        name, idx, edge = aridity_class(ai)
        U['S2.4'] = ok(fmt('S2.4', {'ai': f'{idx:.2f}', 'class': name}),
                       f'index x 100 = {ai}' + ('; the integer storage straddles a class boundary' if edge else ''))
    return U
