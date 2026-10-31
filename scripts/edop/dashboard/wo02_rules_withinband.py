"""WO-02 Step 3, family 7: Within-band families (variables that belong together and constrain each other).

Families found through the catalog's `dimension` field and checked against the payloads: soil texture (clay, silt, sand), river
discharge (annual mean, monthly maximum and minimum), wetlands (class and the two extent groups), temperature (annual, maximum,
minimum), elevation (minimum, maximum) and land use (cropland, pasture). Each statement runs on its own items (a family and a
side, local or upstream), so rates are shares of those items. Rules describe and never judge (WO constraint 1).
"""
from scripts.edop.dashboard import wo02_payloads as P
from scripts.edop.dashboard.wo02_rules_position import ordinal, fmt_num

SOIL = ("clay", "silt", "sand")

STATEMENTS = [
    dict(id="WB-01", name="Soil texture as one composition (one basin)",
         inputs="representative_raw of pct_clay, pct_silt, pct_sand (local, and the _upstream versions)",
         rule="One basin, all three raw values present: state the three shares together, and the sum when it is more than 1.5 points from 100 (the upstream triples often are).",
         applies_to="single basin and one-basin buffer; local and upstream; L6, L8",
         does_not_apply_when="several basins (no native-unit value); any of the three empty (Empty cells)",
         template="Soil texture{ (upstream)}: {n}% clay, {n}% silt, {n}% sand{ (these sum to {n}%, not 100%)}.",
         in_ui_today="no: the three are separate rows",
         needs_new_data="no"),
    dict(id="WB-02", name="Soil texture ranks are not independent",
         inputs="representative_score of the three soil rows, status, score_suppressed",
         rule="All three rows have a usable percentile (single basin or area): state the three ranks and that the three shares are parts of one whole, so the ranks are not independent.",
         applies_to="all scopes with the three rows usable; local and upstream; L6, L8",
         does_not_apply_when="any of the three has no usable percentile",
         template="Soil texture{ (upstream)}: clay ranks at the {ord} percentile, silt at the {ord} and sand at the {ord}; the three shares are parts of one whole, so these ranks are not independent.",
         in_ui_today="no: each is listed separately with no mention of the dependence",
         needs_new_data="no"),
    dict(id="WB-03", name="River discharge: mean, lowest and highest month",
         inputs="representative_raw and units of discharge_yr, discharge_max, discharge_min; detail.perennial",
         rule="Dominant-basin discharge rows present: state the annual mean and the lowest and highest monthly values; the ratio of highest to lowest when the lowest is above zero, or that at least one month has no flow when it is zero. For an area the values are those of the basin with the highest annual discharge.",
         applies_to="single basin, buffer; L6, L8",
         does_not_apply_when="polity (discharge is not_areal); any row empty",
         template="River discharge{ in the basin with the highest annual discharge}: annual mean {n} m3/s, from {n} m3/s in the lowest month to {n} m3/s in the highest ({n} times | ; at least one month has no flow).",
         in_ui_today="partly: three separate rows with the dominant basin's id",
         needs_new_data="no"),
    dict(id="WB-04", name="Wetland extent: wetland and open water, and the part that is open water",
         inputs="representative_raw of wet_pct_grp1 and wet_pct_grp2 (local, upstream)",
         rule="One basin, both extents present and positive: state group 1 (all wetland classes including lakes, reservoirs and rivers), group 2 (wetland excluding lakes, reservoirs and rivers) and the difference (lakes, reservoirs and rivers). Group 2 is part of group 1 by the provider's definition and was at most group 1 in every payload.",
         applies_to="single basin and one-basin buffer; local and upstream; L6, L8",
         does_not_apply_when="several basins; either extent zero or empty (zero is EMP-01)",
         template="Wetland extent: {n}% of the basin | Wetland extent (upstream): {n}% of the area upstream is wetland or open water (wetland classes including lakes, reservoirs and rivers), {n}% is wetland excluding lakes, reservoirs and rivers; the other {n}% is lakes, reservoirs and rivers.",
         in_ui_today="no: the two extents are separate rows and their relation is not stated",
         needs_new_data="the group definitions come from the provider's page (L06), not the payload"),
    dict(id="WB-05", name="Wetland class present while both extents are zero",
         inputs="wetland_class (status ok, class label), wet_pct_grp1 and wet_pct_grp2 status outside_active_domain",
         rule="One basin, a wetland class is present but both local extents read zero (whole percents): state the class and that both extents read zero percent.",
         applies_to="single basin and one-basin buffer; local; L6, L8",
         does_not_apply_when="class absent (no_data: the source records no wetlands, EMP-03); either extent positive",
         template="Wetland class: {label} is the dominant wetland class, while both extent figures read zero percent (extents are whole percents).",
         in_ui_today="no: the class and the extents are separate rows",
         needs_new_data="why the two disagree is not established; small extents stored as zero is a likely reason, not verified"),
    dict(id="WB-06", name="Temperature: annual, maximum and minimum",
         inputs="representative_raw and units of temp_yr, temp_max, temp_min",
         rule="One basin, all three raw values present: state them with the range between maximum and minimum. The payload names say 'monthly maximum' and 'monthly minimum'; whether these are the warmest and coldest month's mean is not stated, and the rule does not claim it.",
         applies_to="single basin and one-basin buffer; local; L6, L8",
         does_not_apply_when="several basins; any value empty",
         template="Temperature: annual mean {n} C; monthly maximum {n} C; monthly minimum {n} C; the range between maximum and minimum is {n} C.",
         in_ui_today="no: three separate rows",
         needs_new_data="whether monthly maximum and minimum are the warmest and coldest month's mean is not stated in the payload"),
    dict(id="WB-07", name="Elevation span",
         inputs="representative_raw and units of elev_min, elev_max",
         rule="One basin, both raw values present: state the lowest and highest elevation and the difference.",
         applies_to="single basin and one-basin buffer; L6, L8",
         does_not_apply_when="several basins; either value empty",
         template="Elevation runs from {n} m to {n} m, a difference of {n} m.",
         in_ui_today="no: two separate rows",
         needs_new_data="no"),
    dict(id="WB-08", name="Land use: cropland and pasture",
         inputs="cropland_extent and pasture_extent (local, upstream): raw, or zero when outside_active_domain",
         rule="One basin, each of the two extents known (a raw value, or zero where the status is outside_active_domain): state both. Their sum was at most 100 in every payload.",
         applies_to="single basin and one-basin buffer; local and upstream; L6, L8",
         does_not_apply_when="several basins; either extent empty (no data)",
         template="Land use{ (upstream)}: cropland covers {n}% and pasture {n}% of the area.",
         in_ui_today="no: two separate rows",
         needs_new_data="no"),
]


def _ctx_rows(q):
    pairs = P.ae_rows(q)
    if not pairs:
        return None, {}
    return pairs[0][0], {r["variable"]: r for _, r in pairs}


def _raw(row):
    return row["representative_raw"] if row and row["status"] == "ok" and row.get("representative_raw") is not None else None


def _val(row):
    """Raw value, or zero where the extent is outside the active domain; None otherwise."""
    if row is None:
        return None
    if row["status"] == "ok" and row.get("representative_raw") is not None:
        return row["representative_raw"]
    return 0.0 if row["status"] == "outside_active_domain" else None


def _usable(row):
    return bool(row and row["status"] == "ok" and not row.get("score_suppressed") and row.get("representative_score") is not None)


def _units(row):
    return f" {row['units']}" if row and row.get("units") else ""


def evaluate_query(q):
    ctx, rows = _ctx_rows(q)
    out = []
    if ctx is None:
        return out
    single = ctx["n_units"] == 1
    base = dict(qid=ctx["qid"], scope=ctx["scope"], level=ctx["level"], n_units=ctx["n_units"], method=None, status=None)

    def rec(i, item, applies, reason=None, text=None, stat=None):
        out.append(dict(base, id=i, variable=item, applies=applies, reason=reason, text=text, stat=stat))

    for side, suf in (("local", ""), ("upstream", "_upstream")):
        tag = " (upstream)" if suf else ""
        item = f"soil_{side}"
        rs = [rows.get(f"pct_{c}{suf}") for c in SOIL]
        # WB-01
        if not single:
            rec("WB-01", item, False, "multi_unit")
        else:
            v = [_raw(r) for r in rs]
            if None in v:
                rec("WB-01", item, False, "side_not_usable")
            else:
                s = sum(v)
                t = f"Soil texture{tag}: {fmt_num(v[0])}% clay, {fmt_num(v[1])}% silt, {fmt_num(v[2])}% sand"
                t += f" (these sum to {s:.0f}%, not 100%)." if abs(s - 100) > 1.5 else "."
                rec("WB-01", item, True, text=t, stat=s)
        # WB-02
        if not all(_usable(r) for r in rs):
            rec("WB-02", item, False, "side_not_usable")
        else:
            sc = [r["representative_score"] for r in rs]
            rec("WB-02", item, True, text=f"Soil texture{tag}: clay ranks at the {ordinal(sc[0])} percentile, silt at the {ordinal(sc[1])} and sand at "
                                           f"the {ordinal(sc[2])}; the three shares are parts of one whole, so these ranks are not independent.", stat=max(sc) - min(sc))
        # WB-04
        item = f"wetland_extent_{side}"
        g1, g2 = rows.get(f"wet_pct_grp1{suf}"), rows.get(f"wet_pct_grp2{suf}")
        if not single:
            rec("WB-04", item, False, "multi_unit")
        else:
            a, b = _raw(g1), _raw(g2)
            if a is None or b is None:
                rec("WB-04", item, False, "extent_zero_or_empty")
            else:
                d = a - b
                rest = "none of it is lakes, reservoirs or rivers" if d == 0 else f"the other {fmt_num(d)}% is lakes, reservoirs and rivers"
                where = "the area upstream" if suf else "the basin"
                rec("WB-04", item, True, text=f"Wetland extent{tag}: {fmt_num(a)}% of {where} is wetland or open water (wetland classes including lakes, "
                                               f"reservoirs and rivers), {fmt_num(b)}% is wetland excluding lakes, reservoirs and rivers; {rest}.", stat=d)
        # WB-08
        item = f"landuse_{side}"
        cr, pa = rows.get(f"cropland_extent{suf}"), rows.get(f"pasture_extent{suf}")
        if not single:
            rec("WB-08", item, False, "multi_unit")
        else:
            a, b = _val(cr), _val(pa)
            if a is None or b is None:
                rec("WB-08", item, False, "extent_empty")
            else:
                rec("WB-08", item, True, text=f"Land use{tag}: cropland covers {fmt_num(a)}% and pasture {fmt_num(b)}% of the area.", stat=a + b)

    # WB-03 discharge
    dy, dx, dn = rows.get("discharge_yr"), rows.get("discharge_max"), rows.get("discharge_min")
    if ctx["scope"] == "polity":
        rec("WB-03", "discharge", False, "not_areal")
    else:
        y, x, n = _raw(dy), _raw(dx), _raw(dn)
        if None in (y, x, n):
            rec("WB-03", "discharge", False, "row_empty")
        else:
            u = _units(dy)
            who = "River discharge" if single else "River discharge in the basin with the highest annual discharge"
            tail = f" ({x / n:.1f} times)." if n > 0 else "; at least one month has no flow."
            rec("WB-03", "discharge", True, text=f"{who}: annual mean {fmt_num(y)}{u}, from {fmt_num(n)}{u} in the lowest month to {fmt_num(x)}{u} in the highest{tail}",
                stat=(x / n if n > 0 else None))

    # WB-05 wetland class with zero extents
    wc, g1, g2 = rows.get("wetland_class"), rows.get("wet_pct_grp1"), rows.get("wet_pct_grp2")
    if not single:
        rec("WB-05", "wetland_class", False, "multi_unit")
    elif wc is None or wc["status"] != "ok":
        rec("WB-05", "wetland_class", False, "class_absent")
    elif not (g1 and g2 and g1["status"] == "outside_active_domain" and g2["status"] == "outside_active_domain"):
        rec("WB-05", "wetland_class", False, "extent_positive_or_empty")
    else:
        rec("WB-05", "wetland_class", True, text=f"Wetland class: {wc['representative_raw']} is the dominant wetland class, while both extent figures "
                                                   "read zero percent (extents are whole percents).")

    # WB-06 temperature
    ty, tx, tn = rows.get("temp_yr"), rows.get("temp_max"), rows.get("temp_min")
    if not single:
        rec("WB-06", "temperature", False, "multi_unit")
    else:
        y, x, n = _raw(ty), _raw(tx), _raw(tn)
        if None in (y, x, n):
            rec("WB-06", "temperature", False, "row_empty")
        else:
            u = _units(ty)
            nm = lambda r: (r.get("friendly_name") or r["variable"]).removeprefix("Temperature ").strip()
            rec("WB-06", "temperature", True, text=f"Temperature: {nm(ty)} {fmt_num(y)}{u}; {nm(tx)} {fmt_num(x)}{u}; {nm(tn)} {fmt_num(n)}{u}; "
                                                    f"the range between maximum and minimum is {fmt_num(x - n)}{u}.", stat=x - n)

    # WB-07 elevation
    el, eh = rows.get("elev_min"), rows.get("elev_max")
    if not single:
        rec("WB-07", "elevation", False, "multi_unit")
    else:
        lo, hi = _raw(el), _raw(eh)
        if lo is None or hi is None:
            rec("WB-07", "elevation", False, "row_empty")
        else:
            u = _units(el)
            rec("WB-07", "elevation", True, text=f"Elevation runs from {fmt_num(lo)}{u} to {fmt_num(hi)}{u}, a difference of {fmt_num(hi - lo)}{u}.", stat=hi - lo)
    return out


def relations(queries):
    """Counter of the relations each family should obey, over single-basin queries (fixtures and population)."""
    import collections
    c = collections.Counter()
    sums = {"local": [], "upstream": []}
    for q in queries:
        ctx, rows = _ctx_rows(q)
        if ctx is None or ctx["scope"] != "single_basin":
            continue
        for side, suf in (("local", ""), ("upstream", "_upstream")):
            v = [_raw(rows.get(f"pct_{k}{suf}")) for k in SOIL]
            if None not in v:
                sums[side].append(sum(v))
        y, x, n = _raw(rows.get("discharge_yr")), _raw(rows.get("discharge_max")), _raw(rows.get("discharge_min"))
        if None not in (y, x, n):
            c["discharge: triples"] += 1
            c["discharge: lowest <= mean <= highest"] += n <= y <= x
        ty, tx, tn = _raw(rows.get("temp_yr")), _raw(rows.get("temp_max")), _raw(rows.get("temp_min"))
        if None not in (ty, tx, tn):
            c["temperature: triples"] += 1
            c["temperature: min <= annual <= max"] += tn <= ty <= tx
        lo, hi = _raw(rows.get("elev_min")), _raw(rows.get("elev_max"))
        if None not in (lo, hi):
            c["elevation: pairs"] += 1
            c["elevation: min <= max"] += lo <= hi
        a, b = _raw(rows.get("wet_pct_grp1")), _raw(rows.get("wet_pct_grp2"))
        if None not in (a, b):
            c["wetland groups: pairs"] += 1
            c["wetland groups: group 1 >= group 2"] += a >= b
        for suf in ("", "_upstream"):
            cr, pa = _val(rows.get(f"cropland_extent{suf}")), _val(rows.get(f"pasture_extent{suf}"))
            if None not in (cr, pa):
                c["land use: cropland + pasture known"] += 1
                c["land use: cropland + pasture <= 100"] += cr + pa <= 100.001
        wc = rows.get("wetland_class")
        g1, g2 = rows.get("wet_pct_grp1"), rows.get("wet_pct_grp2")
        if wc and g1 and g2:
            zero = g1["status"] == "outside_active_domain" and g2["status"] == "outside_active_domain"
            if wc["status"] == "no_data":
                c["wetland class no_data rows"] += 1
                c["   ... of which both extents zero"] += zero
            elif wc["status"] == "ok":
                c["wetland class present rows"] += 1
                c["   ... of which both extents zero (present class, zero extents)"] += zero
    return c, sums


def wetland_zero_by_class(queries):
    """Counter of wetland class labels where a class is present but both local extents read zero, and where an extent is positive."""
    import collections
    zero, pos = collections.Counter(), collections.Counter()
    for q in queries:
        ctx, rows = _ctx_rows(q)
        if ctx is None or ctx["scope"] != "single_basin":
            continue
        wc, g1, g2 = rows.get("wetland_class"), rows.get("wet_pct_grp1"), rows.get("wet_pct_grp2")
        if wc and wc["status"] == "ok" and g1 and g2:
            if g1["status"] == "outside_active_domain" and g2["status"] == "outside_active_domain":
                zero[wc["representative_raw"]] += 1
            elif g1["status"] == "ok":
                pos[wc["representative_raw"]] += 1
    return zero, pos


def upstream_soil_anomalies(queries, tol=1.5):
    """Upstream triples (single basin) whose sum is more than tol from 100, split into all zero, partly zero and short or over."""
    import collections
    c = collections.Counter()
    sums = []
    for q in queries:
        ctx, rows = _ctx_rows(q)
        if ctx is None or ctx["scope"] != "single_basin":
            continue
        v = [_raw(rows.get(f"pct_{k}_upstream")) for k in SOIL]
        if None in v:
            continue
        c["upstream triples"] += 1
        sm = sum(v)
        if abs(sm - 100) > tol:
            sums.append(sm)
            c["sum more than %.1f from 100" % tol] += 1
            c["   all three zero" if sm == 0 else "   some component zero" if 0 in v else "   no zero component (short or over)"] += 1
    return c, sums
